"""Question Factory V2: isolated staging, conservative quality gates, admin approval.

Candidates never count as certified and are never served to students. Semantic
independence and mathematical proofs require independent human review.
"""
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from contextlib import contextmanager
from difflib import SequenceMatcher
from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field
from database.database import get_connection
from .admin_routes import require_admin
from .roadmap_v2_routes import _data, coverage, _valid, _lesson_fingerprint
from .qf2_verified_generators import GENERATORS, PLACEMENT_GENERATORS
from .placement_v20_original_forms import GENERATORS as V20_PLACEMENT_GENERATORS
from .ai.engine.validator import options_equivalent

router = APIRouter(prefix='/api/admin/qf2', tags=['Question Factory V2'])


def time_now():return datetime.now(timezone.utc).isoformat()


@contextmanager
def conn():
    c=get_connection()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS qf2_forms (
      id INTEGER PRIMARY KEY AUTOINCREMENT, grade INTEGER NOT NULL, topic_id TEXT NOT NULL,
      title TEXT NOT NULL, concept TEXT NOT NULL, method TEXT NOT NULL, conditions TEXT NOT NULL,
      distinguishing TEXT NOT NULL, signature TEXT NOT NULL, questions_json TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending_review', warnings_json TEXT NOT NULL DEFAULT '[]',
      reviewer_notes TEXT, reviewed_by INTEGER, created_at TEXT NOT NULL, reviewed_at TEXT);
    CREATE INDEX IF NOT EXISTS qf2_form_status ON qf2_forms(status,grade,topic_id);
    CREATE INDEX IF NOT EXISTS qf2_form_signature ON qf2_forms(grade,topic_id,signature);
    CREATE TABLE IF NOT EXISTS qf2_lesson_reviews (
      topic_id TEXT NOT NULL,question_index INTEGER NOT NULL,grade INTEGER NOT NULL,
      question_hash TEXT NOT NULL,difficulty TEXT NOT NULL,status TEXT NOT NULL,
      notes TEXT NOT NULL,reviewed_by INTEGER NOT NULL,reviewed_at TEXT NOT NULL,
      PRIMARY KEY(topic_id,question_index));
    CREATE INDEX IF NOT EXISTS qf2_lesson_grade ON qf2_lesson_reviews(grade,status);

    ''')
    try:yield c
    finally:c.close()


def norm(text):
    raw=unicodedata.normalize('NFKC',str(text)).casefold()
    raw=re.sub(r'[-+]?\d+(?:[.,]\d+)?',' # ',raw)
    return re.sub(r'\s+',' ',raw).strip()

def norm_exact(text):
    """Normalize display wording without erasing numbers in answer options."""
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(text)).casefold()).strip()


class QualityQuestion(BaseModel):
    question: str=Field(min_length=12,max_length=5000)
    question_type:str=Field(pattern='^(multiple_choice|written|true_false)$')
    difficulty:str=Field(pattern='^(nền tảng|trung cấp|nâng cao)$')
    choices:list[str]=Field(default_factory=list,max_length=4)
    correct_index:int|None=Field(default=None,ge=0,le=3)
    answer:str=Field(min_length=1,max_length=1000)
    explanation:str=Field(min_length=24,max_length=10000)


class Candidate(BaseModel):
    grade:int=Field(ge=10,le=12)
    topic_id:str=Field(min_length=2,max_length=150)
    title:str=Field(min_length=10,max_length=240)
    concept:str=Field(min_length=8,max_length=1000)
    method:str=Field(min_length=15,max_length=2000)
    conditions:str=Field(min_length=8,max_length=1500)
    distinguishing:str=Field(min_length=15,max_length=1500)
    questions:list[QualityQuestion]=Field(min_length=10,max_length=100)


class LessonDecision(BaseModel):
    approved:bool
    difficulty:str=Field(pattern='^(nền tảng|trung cấp|nâng cao)$')
    independently_checked:bool=False
    notes:str=Field(min_length=20,max_length=3000)


class Decision(BaseModel):
    approved:bool
    notes:str=Field(min_length=20,max_length=3000)
    independently_checked:bool=False


def validate_candidate(c,data):
    topics,_=_data()
    if not any(t['id']==data.topic_id and t['grade']==data.grade for t in topics):
        raise HTTPException(422,'Chủ đề không thuộc khối lớp đã chọn')
    warnings=[];seen=set()
    for i,q in enumerate(data.questions):
        if q.question_type=='multiple_choice':
            if len(q.choices)!=4 or q.correct_index is None or len({norm_exact(x) for x in q.choices})!=4:
                raise HTTPException(422,f'Câu {i+1}: trắc nghiệm phải có 4 lựa chọn khác nhau và một đáp án hợp lệ')
            if norm_exact(q.answer)!=norm_exact(q.choices[q.correct_index]):
                raise HTTPException(422,f'Câu {i+1}: đáp án không khớp lựa chọn đúng')
            # Four distinct strings are not necessarily four distinct answers:
            # 1/2 == 0,5; (x+1)^2 == x^2+2x+1.
            for left in range(4):
                for right in range(left+1,4):
                    if options_equivalent(q.choices[left],q.choices[right]):
                        raise HTTPException(422,f'Câu {i+1}: lựa chọn {left+1} và {right+1} tương đương toán học')
        elif q.question_type!='multiple_choice' and q.choices:
            raise HTTPException(422,f'Câu {i+1}: không được có lựa chọn trắc nghiệm')
        if q.question_type=='true_false' and norm_exact(q.answer) not in ('đúng','sai','true','false'):
            raise HTTPException(422,f'Câu {i+1}: đáp án Đúng/Sai không hợp lệ')
        # Within ONE type, distinct numerical instances are legitimate exercises.
        # Numeric substitutions must never count as a NEW type, but should not
        # be rejected as duplicate QUESTIONS when their givens differ.
        k=norm_exact(q.question)
        if k in seen:raise HTTPException(422,f'Câu {i+1}: đề trùng hệt câu đã có')
        seen.add(k)
    signature=hashlib.sha256(norm(data.concept+' '+data.method+' '+data.conditions).encode()).hexdigest()
    duplicate=c.execute('SELECT id FROM qf2_forms WHERE grade=? AND topic_id=? AND signature=? LIMIT 1',(data.grade,data.topic_id,signature)).fetchone()
    if duplicate:raise HTTPException(409,f'Dạng tương tự dạng #{duplicate[0]} đã tồn tại trong hệ thống')
    recent=c.execute("SELECT id,method,concept FROM qf2_forms WHERE grade=? AND topic_id=? ORDER BY id DESC LIMIT 150",(data.grade,data.topic_id)).fetchall()
    for r in recent:
        if SequenceMatcher(None,norm(data.method+' '+data.concept),norm(r['method']+' '+r['concept'])).ratio()>=0.84:
            warnings.append(f'Cần đối chiếu bản chất với dạng #{r["id"]}')
    return signature,warnings




def build_parabola_vertex_candidate() -> Candidate:
    """Generate exactly ONE candidate form, with ten independently calculated items.

    The coefficient changes are ten exercises of the SAME mathematical type,
    not ten independent types. All answers are checked by substitution.
    """
    parameters = [
        (1, -3, 2), (2, -2, 1), (-1, 3, -2), (3, 1, 4),
        (-2, -1, 3), (1, 2, -4), (2, 3, 1), (-3, -2, -3),
        (3, -1, 2), (-1, 1, -5),
    ]
    questions=[]
    for index,(a,h,k) in enumerate(parameters):
        b=-2*a*h
        c=a*h*h+k
        correct=f'({h}; {k})'
        candidates=[correct,f'({-h}; {k+1})',f'({h+1}; {k-1})',f'({h-2}; {k+2})']
        assert len(set(candidates))==4
        shift=index%4
        options=candidates[shift:]+candidates[:shift]
        correct_index=options.index(correct)
        assert -b/(2*a)==h and a*h*h+b*h+c==k
        explanation=(
            f'Với y = ax² + bx + c, ta có a = {a}, b = {b}, c = {c}. '
            f'Hoành độ đỉnh là x₀ = −b/(2a) = −({b})/(2×({a})) = {h}. '
            f'Thay x₀ = {h} vào hàm số: y₀ = {a}×({h})² + ({b})×({h}) + ({c}) = {k}. '
            f'Vì vậy đỉnh của parabol là I({h}; {k}).'
        )
        questions.append(QualityQuestion(
            question=f'Cho hàm số y = {a}x² + ({b})x + ({c}). Tọa độ đỉnh của parabol là gì?',
            question_type='multiple_choice',difficulty=['nền tảng','trung cấp','nâng cao'][index%3],
            choices=options,correct_index=correct_index,answer=correct,explanation=explanation
        ))
    return Candidate(
        grade=10,topic_id='ham_so_bac_hai',
        title='Xác định tọa độ đỉnh của đồ thị hàm số bậc hai',
        concept='Tọa độ đỉnh của parabol y = ax² + bx + c với a khác 0',
        method='Sử dụng x₀ = −b/(2a), sau đó tính y₀ = f(x₀) để tìm tọa độ đỉnh',
        conditions='Hàm số bậc hai với a khác 0, hệ số nguyên đã kiểm tra',
        distinguishing='Bài toán xác định đỉnh parabol, không phải tìm nghiệm hoặc giao điểm trục',
        questions=questions,
    )


@router.post('/generate/parabola-vertex')
def generate_parabola_vertex(authorization:str|None=Header(default=None)):
    """A narrow, deterministic and algebraically verified candidate generator.

    Admin-only, never auto-approves or claims a new type from changing numbers.
    """
    require_admin(authorization)
    candidate=build_parabola_vertex_candidate()
    result=create(candidate,authorization)
    return {**result,'generated_questions':len(candidate.questions),
            'generated_types':1,
            'note':'Đã tạo 1 dạng ứng viên với 10 câu khác nhau. Chờ Admin kiểm chứng độc lập trước khi xuất bản.'}


@router.get('/generate/catalog')
def generator_catalog(authorization:str|None=Header(default=None)):
    """List only mathematically constrained generators, never unreviewed AI claims."""
    require_admin(authorization)
    rows=[]
    for slug,fn in [('parabola-vertex',build_parabola_vertex_candidate),*GENERATORS.items()]:
        form=fn()
        rows.append({'slug':slug,'grade':form.grade if isinstance(form,Candidate) else form['grade'],
                     'topic_id':form.topic_id if isinstance(form,Candidate) else form['topic_id'],
                     'title':form.title if isinstance(form,Candidate) else form['title'],
                     'questions':len(form.questions if isinstance(form,Candidate) else form['questions']),
                     'status':'generator available; candidates require independent review'})
    return {'generators':rows,'note':'Mỗi bộ sinh là một phương pháp toán, 10 câu số liệu khác nhau chỉ là 10 bài tập.'}


@router.post('/generate/verified-batch')
def generate_verified_batch(authorization:str|None=Header(default=None)):
    """Create nine pending candidate forms spanning three grades; idempotent.

    Arithmetic is checked inside each generator. This is NOT an automated proof
    of semantic independence and cannot publish to the official question bank.
    """
    require_admin(authorization)
    candidates=[build_parabola_vertex_candidate(),*[Candidate.model_validate(fn()) for fn in GENERATORS.values()]]
    result={'created_forms':0,'created_questions':0,'already_present':0,'errors':[],
            'topics':sorted({c.topic_id for c in candidates}), 'grades':[10,11,12]}
    for form in candidates:
        try:
            create(form,authorization)
            result['created_forms']+=1
            result['created_questions']+=len(form.questions)
        except HTTPException as exc:
            if exc.status_code==409:
                result['already_present']+=1
            else:
                result['errors'].append({'title':form.title,'error':str(exc.detail)})
    result['note']='Chỉ sinh ứng viên. 10 câu/dạng; tất cả cần quản trị viên đối chiếu và duyệt riêng.'
    return result


@router.post('/generate/placement-expansion')
def generate_placement_expansion(authorization:str|None=Header(default=None)):
    """Stage six new, arithmetic-checked candidate forms; never auto-approve.

    Keep the legacy verified-batch endpoint stable for existing integrations.
    """
    require_admin(authorization)
    candidates=[Candidate.model_validate(fn()) for fn in PLACEMENT_GENERATORS.values()]
    result={'created_forms':0,'created_questions':0,'already_present':0,'errors':[],
            'topics':sorted({c.topic_id for c in candidates}), 'grades':[10,11,12]}
    for form in candidates:
        try:
            create(form,authorization)
            result['created_forms']+=1
            result['created_questions']+=len(form.questions)
        except HTTPException as exc:
            if exc.status_code==409:result['already_present']+=1
            else:result['errors'].append({'title':form.title,'error':str(exc.detail)})
    result['note']='Sáu dạng mới, 60 câu ứng viên; cần giáo viên kiểm chứng và duyệt trước khi dùng trong đề chính thức.'
    return result


@router.get('/generate/placement-v20-catalog')
def placement_v20_catalog(authorization:str|None=Header(default=None)):
    """Separated from the legacy 9-generator catalog for API compatibility."""
    require_admin(authorization)
    return {'generators':[{'slug':slug,'grade':form['grade'],'topic_id':form['topic_id'],
                            'title':form['title'],'questions':len(form['questions']),
                            'status':'candidate_not_approved'}
                           for slug,fn in V20_PLACEMENT_GENERATORS.items() for form in [fn()]],
            'note':'Tất cả 31 dạng phải được giáo viên duyệt; không phải đề chính thức.'}


@router.post('/generate/placement-v20-review-batch')
def generate_placement_v20_review_batch(authorization:str|None=Header(default=None)):
    """Stage 31 original mathematical-method candidates, all pending teacher review.

    Never auto-approves or publishes any candidate to a student's exam.
    Duplicate method signatures return an idempotent already_present count.
    """
    require_admin(authorization)
    candidates=[Candidate.model_validate(fn()) for fn in V20_PLACEMENT_GENERATORS.values()]
    result={'candidate_forms':len(candidates),'candidate_questions':sum(len(x.questions) for x in candidates),
            'created_forms':0,'created_questions':0,'already_present':0,'errors':[],
            'grades':[10,11,12],'status':'pending_independent_teacher_review'}
    for form in candidates:
        try:
            create(form,authorization)
            result['created_forms']+=1
            result['created_questions']+=len(form.questions)
        except HTTPException as exc:
            if exc.status_code==409:
                result['already_present']+=1
            else:
                result['errors'].append({'topic_id':form.topic_id,'error':str(exc.detail)})
    result['note']=('Mỗi phương pháp gồm 10 bài tập gốc. Nhãn độ khó chỉ là ứng viên; '
                    'phải có giáo viên kiểm định độc lập và thử nghiệm học sinh trước khi dùng làm đề chuẩn.')
    return result


@router.post('/candidates')
def create(data:Candidate,authorization:str|None=Header(default=None)):
    admin=require_admin(authorization)
    with conn() as c:
        signature,warnings=validate_candidate(c,data)
        cur=c.execute('''INSERT INTO qf2_forms (grade,topic_id,title,concept,method,conditions,distinguishing,signature,questions_json,status,warnings_json,created_at)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',(data.grade,data.topic_id,data.title,data.concept,data.method,data.conditions,data.distinguishing,signature,
          json.dumps([q.model_dump() for q in data.questions],ensure_ascii=False),'pending_review',json.dumps(warnings,ensure_ascii=False),time_now()))
        c.commit()
    return {'id':cur.lastrowid,'status':'pending_review','warnings':warnings,
            'note':'Chỉ là ứng viên, chưa chứng nhận đúng toán hoặc độc lập về bản chất.'}


@router.get('/summary')
def summary(authorization:str|None=Header(default=None)):
    require_admin(authorization)
    with conn() as c:
        rows=c.execute('SELECT status,COUNT(*) AS count,COALESCE(SUM(json_array_length(questions_json)),0) AS questions FROM qf2_forms GROUP BY status').fetchall()
        recent=c.execute('SELECT id,title,topic_id,grade,status,warnings_json,created_at FROM qf2_forms ORDER BY id DESC LIMIT 40').fetchall()
    return {'status':[dict(r) for r in rows], 'recent':[{**dict(r),'warnings':json.loads(r['warnings_json'])} for r in recent],
            'certified_definition':'Chỉ approved sau 10 câu đạt định dạng, đối chiếu trùng và quản trị viên xác nhận kiểm tra toán học độc lập.'}


@router.get('/lesson-queue')
def lesson_review_queue(grade:int=Query(ge=10,le=12),offset:int=Query(default=0,ge=0),
                        limit:int=Query(default=20,ge=1,le=100),authorization:str|None=Header(default=None)):
    """Admin review queue for the existing lesson bank, no automatic tier claims."""
    require_admin(authorization)
    topics,lessons=_data()
    entries=[]
    with conn() as c:
        existing={(r['topic_id'],r['question_index']):dict(r) for r in c.execute(
            'SELECT topic_id,question_index,question_hash,difficulty,status FROM qf2_lesson_reviews WHERE grade=?',(grade,)).fetchall()}
    for t in topics:
        if t['grade']!=grade:continue
        for i,q in enumerate(lessons.get(t['id'],{}).get('quiz',[])):
            if not _valid(q):continue
            review=existing.get((t['id'],i))
            if review and review['question_hash']!=_lesson_fingerprint(q):review=None
            entries.append({'topic_id':t['id'],'title':t['title'],'index':i,
                            'question':q['q'],'choices':q.get('choices',[]),'answer':q.get('correct',q.get('answer')),
                            'explanation':q['why'],'status':review['status'] if review else 'unreviewed',
                            'difficulty':review['difficulty'] if review else None})
    return {'grade':grade,'total':len(entries),'reviewed':sum(x['status']!='unreviewed' for x in entries),
            'questions':entries[offset:offset+limit], 'offset':offset,'limit':limit}


@router.post('/lesson-questions/{topic_id}/{index}/review')
def review_lesson_question(topic_id:str,index:int,decision:LessonDecision,
                           authorization:str|None=Header(default=None)):
    admin=require_admin(authorization)
    topics,lessons=_data()
    topic=next((t for t in topics if t['id']==topic_id),None)
    questions=lessons.get(topic_id,{}).get('quiz',[])
    if not topic or index<0 or index>=len(questions):raise HTTPException(404,'Không tìm thấy câu học liệu')
    q=questions[index]
    if not _valid(q):raise HTTPException(422,'Câu học liệu chưa đạt điều kiện tối thiểu')
    if decision.approved and not decision.independently_checked:
        raise HTTPException(409,'Phải xác nhận đã kiểm tra đáp án và lời giải độc lập')
    status='approved' if decision.approved else 'rejected'
    with conn() as c:
        c.execute('''INSERT INTO qf2_lesson_reviews(topic_id,question_index,grade,question_hash,difficulty,status,notes,reviewed_by,reviewed_at)
          VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(topic_id,question_index) DO UPDATE SET
          grade=excluded.grade,question_hash=excluded.question_hash,difficulty=excluded.difficulty,
          status=excluded.status,notes=excluded.notes,reviewed_by=excluded.reviewed_by,reviewed_at=excluded.reviewed_at''',
          (topic_id,index,topic['grade'],_lesson_fingerprint(q),decision.difficulty,status,
           decision.notes,admin['id'],time_now()))
        c.commit()
    return {'topic_id':topic_id,'index':index,'status':status,'difficulty':decision.difficulty,
            'note':'Chỉ câu được duyệt mới có nhãn độ khó đã kiểm chứng.'}


@router.get('/coverage')
def admin_coverage(authorization:str|None=Header(default=None)):
    """Evidence-based coverage, not synthetic percentages from a mockup."""
    require_admin(authorization)
    result=[]
    for grade in (10,11,12):
        data=coverage(grade)
        result.append({'grade':grade,'topic_count':data['topic_count'],
                       'topics_with_questions':data['topics_with_questions'],
                       'topics_meeting_3_per_tier':data['topics_meeting_3_per_tier'],
                       'topics_with_30_questions':sum(x['certified']>=30 for x in data['topics']),
                       'most_incomplete':sorted(data['topics'],key=lambda x:(x['minimum_met'],-x['available']))[:10]})
    return {'grades':result,'note':'Đủ 30 câu: chỉ đếm câu đã được duyệt độc lập. Câu chưa kiểm định có thể xuất hiện trong kho học liệu, nhưng không được tính để mở khóa.'}


@router.get('/coverage-detail')
def coverage_detail(grade: int | None=Query(default=None,ge=10,le=12),
                    authorization: str | None=Header(default=None)):
    """Export evidence-based 150-topic deficits, never inflate new-type totals."""
    require_admin(authorization)
    if grade is not None and grade not in (10,11,12):
        raise HTTPException(422,'Lớp không hợp lệ')
    grades=[grade] if grade is not None else [10,11,12]
    details=[]
    for g in grades:
        for t in coverage(g)['topics']:
            missing={tier:max(0,3-t['by_difficulty'][tier]) for tier in ('nền tảng','trung cấp','nâng cao')}
            details.append({'grade':g,'topic_id':t['id'],'title':t['title'],
                            'candidates':t['available']-t['certified'],
                            'approved_questions':t['certified'],
                            'missing_to_30':max(0,30-t['certified']),
                            'missing_by_difficulty':missing,
                            'complete':t['certified']>=30 and not any(missing.values())})
    return {'topic_count':len(details), 'certified_topic_exams':sum(t['complete'] for t in details),
            'total_missing_certified_questions':sum(t['missing_to_30'] for t in details),
            'total_tier_gaps':sum(sum(t['missing_by_difficulty'].values()) for t in details),
            'topics':details,
            'note':'Số lượng thiếu được tính trên câu đã kiểm chứng và duyệt, không phải bộ câu hỏi ứng viên.'}


@router.get('/candidates/{form_id}')
def candidate_detail(form_id:int,authorization:str|None=Header(default=None)):
    require_admin(authorization)
    with conn() as c:
        row=c.execute('SELECT * FROM qf2_forms WHERE id=?',(form_id,)).fetchone()
    if not row:raise HTTPException(404,'Không tìm thấy dạng ứng viên')
    obj=dict(row)
    obj['questions']=json.loads(obj.pop('questions_json'))
    obj['warnings']=json.loads(obj.pop('warnings_json'))
    return obj


@router.post('/candidates/{form_id}/review')
def review(form_id:int,decision:Decision,authorization:str|None=Header(default=None)):
    admin=require_admin(authorization)
    with conn() as c:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT * FROM qf2_forms WHERE id=?',(form_id,)).fetchone()
        if not row:raise HTTPException(404,'Không tìm thấy dạng ứng viên')
        if row['status']!='pending_review':raise HTTPException(409,'Dạng đã được xử lý')
        if decision.approved and (not decision.independently_checked or json.loads(row['warnings_json'])):
            raise HTTPException(409,'Dạng còn nghi vấn trùng hoặc chưa xác nhận kiểm chứng toán học độc lập.')
        status='approved' if decision.approved else 'rejected'
        approved_questions = json.loads(row['questions_json']) if decision.approved else []
        if decision.approved:
            # Publish only after explicit verification by an authorized admin.
            # The existing practice/question services already read admin_question_bank.
            if len(approved_questions)<10:raise HTTPException(409,'Không đủ 10 câu để duyệt')
            try:
                snapshot=Candidate.model_validate({
                    'grade':row['grade'],'topic_id':row['topic_id'],'title':row['title'],
                    'concept':row['concept'],'method':row['method'],
                    'conditions':row['conditions'],'distinguishing':row['distinguishing'],
                    'questions':approved_questions})
                for ix,question in enumerate(snapshot.questions):
                    if question.question_type=='multiple_choice':
                        if any(options_equivalent(a,b) for i,a in enumerate(question.choices)
                               for b in question.choices[i+1:]):
                            raise HTTPException(409,f'Câu {ix+1} có các lựa chọn tương đương; từ chối xuất bản.')
            except (ValueError, TypeError) as exc:
                raise HTTPException(409,'Ứng viên không còn đạt cấu trúc bắt buộc') from exc
            for question in approved_questions:
                duplicate=c.execute('SELECT id FROM admin_question_bank WHERE grade=? AND topic=? AND lower(trim(question))=lower(trim(?)) LIMIT 1',
                    (row['grade'],row['topic_id'],question['question'])).fetchone()
                if duplicate:raise HTTPException(409,'Có câu trùng trong ngân hàng chính thức. Cần xử lý trước khi duyệt.')
            for question in approved_questions:
                timestamp=time_now()
                c.execute('INSERT INTO admin_question_bank (grade,topic,difficulty,question_type,game_id,question,choices_json,correct_answer,explanation,source,tags_json,created_by,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (row['grade'],row['topic_id'],question['difficulty'],
                     'short_answer' if question['question_type']=='written' else question['question_type'],
                     '',question['question'],json.dumps(question['choices'],ensure_ascii=False),
                     question['answer'],question['explanation'],'Question Factory 2.0 · independently reviewed',
                     json.dumps(['qf2','reviewed',f'form:{form_id}'],ensure_ascii=False),admin['id'],timestamp,timestamp))
        c.execute('UPDATE qf2_forms SET status=?,reviewer_notes=?,reviewed_by=?,reviewed_at=? WHERE id=?',
                  (status,decision.notes,admin['id'],time_now(),form_id));c.commit()
    return {'id':form_id,'status':status,'published_questions':len(approved_questions),
            'note':'Chỉ những câu thuộc dạng được duyệt mới đưa vào ngân hàng chính thức.'}
