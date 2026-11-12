"""Roadmap V2: per-user diagnostic, server-graded exams, staged 3-topic unlock.

No assessment key is transmitted before submission. The pre-existing reviewed
lesson library is a *source*, not proof of independent certification. Coverage
shortages are reported explicitly rather than inventing questions.
"""
import json
import hashlib
import random
import re
import secrets
import sqlite3
from collections import Counter, defaultdict
from fractions import Fraction
from datetime import datetime, timezone
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from database.database import get_connection
from .auth.routes import get_current_user
from .fixed_placement import (load_blueprint, assemble_fixed_paper, digest, evidence_profile, validate_frozen_paper)
from . import learner_online

router = APIRouter(prefix='/api/roadmap-v2', tags=['Roadmap V2'])
ROOT = Path(__file__).resolve().parents[2]
DIFFICULTY = ('nền tảng', 'trung cấp', 'nâng cao')

@lru_cache(maxsize=1)
def _data():
    topics = json.loads((ROOT / 'learn-assets/topics.json').read_text(encoding='utf-8'))
    lessons = json.loads((ROOT / 'learn-assets/verified-lessons.json').read_text(encoding='utf-8'))
    return topics, lessons


def now(): return datetime.now(timezone.utc).isoformat()


def student(auth): return int(get_current_user(auth)['id'])


@contextmanager
def db():
    c = get_connection()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS roadmap_v2_attempts (
        attempt_id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, grade INTEGER NOT NULL,
        mode TEXT NOT NULL, topic_id TEXT, questions_json TEXT NOT NULL,
        submitted_at TEXT, responses_json TEXT, result_json TEXT, created_at TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS idx_roadmap_user ON roadmap_v2_attempts(user_id,grade,mode,submitted_at);
    CREATE TABLE IF NOT EXISTS roadmap_v2_skill_state (
        user_id INTEGER NOT NULL, grade INTEGER NOT NULL, topic_id TEXT NOT NULL, tier TEXT NOT NULL,
        mastery REAL NOT NULL DEFAULT 0.35, observations INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL, PRIMARY KEY(user_id,grade,topic_id,tier));
    CREATE TABLE IF NOT EXISTS roadmap_v2_fixed_papers (
        paper_id TEXT PRIMARY KEY, grade INTEGER NOT NULL, paper_hash TEXT NOT NULL,
        blueprint_hash TEXT NOT NULL, questions_json TEXT NOT NULL,
        published_at TEXT NOT NULL, published_by INTEGER NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1);
    CREATE INDEX IF NOT EXISTS idx_roadmap_fixed_grade ON roadmap_v2_fixed_papers(grade,is_active);
    CREATE TABLE IF NOT EXISTS roadmap_v2_mastery (
        user_id INTEGER NOT NULL, grade INTEGER NOT NULL, topic_id TEXT NOT NULL,
        best_score INTEGER NOT NULL DEFAULT 0, attempts INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL, PRIMARY KEY(user_id,grade,topic_id));
    -- Private, per-student evidence. Raw answers/solutions do not enter this table.
    CREATE TABLE IF NOT EXISTS roadmap_v2_learning_events (
        user_id INTEGER NOT NULL, grade INTEGER NOT NULL, attempt_id TEXT NOT NULL,
        qid TEXT NOT NULL, topic_id TEXT NOT NULL, tier TEXT NOT NULL,
        verdict TEXT NOT NULL CHECK(verdict IN ('correct','wrong','skipped')),
        source TEXT NOT NULL, created_at TEXT NOT NULL,
        PRIMARY KEY(user_id,attempt_id,qid));
    CREATE INDEX IF NOT EXISTS idx_roadmap_learning_events
      ON roadmap_v2_learning_events(user_id,grade,topic_id,created_at);
    ''')
    try:yield c
    finally:c.close()


def _bkt_next(prior, correct, tier):
    """Incremental probabilistic knowledge tracing, never an LLM retrain.

    Guess/slip parameters are provisional engineering defaults, NOT calibrated
    psychometric parameters. Only evidence from reviewed questions is used.
    """
    # Harder questions have a lower chance of correct guessing, but success on
    # just one question never certifies true mastery.
    prob_correct_known, prob_correct_unknown = {
        'nền tảng': (0.90, 0.25),
        'trung cấp': (0.86, 0.18),
        'nâng cao': (0.82, 0.12),
    }.get(tier,(0.86,0.18))
    prior=max(0.02,min(0.98,float(prior)))
    a=prob_correct_known if correct else (1-prob_correct_known)
    b=prob_correct_unknown if correct else (1-prob_correct_unknown)
    posterior=(prior*a)/(prior*a+(1-prior)*b)
    return max(0.02,min(0.98,posterior+(1-posterior)*0.035))


def _tier(q, index):
    value = str(q.get('difficulty', '')).strip().lower()
    mapping = {'easy':'nền tảng','medium':'trung cấp','hard':'nâng cao','basic':'nền tảng',
               'intermediate':'trung cấp','advanced':'nâng cao','foundation':'nền tảng'}
    return mapping.get(value, value if value in DIFFICULTY else None)


def _key(q):
    return re.sub(r'\s+', ' ', str(q.get('q','')).strip()).casefold()


def _valid(q):
    if not isinstance(q,dict) or len(str(q.get('q','')).strip())<6:
        return False
    choices=q.get('choices')
    kind=str(q.get('type','')).lower()
    if isinstance(choices,list) and len(choices)==4 and isinstance(q.get('correct'),int) and not isinstance(q.get('correct'),bool):
        from .ai.engine.validator import options_equivalent
        return (0<=q['correct']<4 and len(set(map(str,choices)))==4
                and not any(options_equivalent(a,b) for i,a in enumerate(choices) for b in choices[i+1:])
                and bool(str(q.get('why','')).strip()))
    if kind in ('short_answer','written','fill','tu_luan'):
        return bool(str(q.get('answer',q.get('correct',''))).strip()) and bool(str(q.get('why','')).strip())
    if kind in ('true_false','dung_sai'):
        return str(q.get('answer',q.get('correct',''))).lower() in ('true','false','đúng','sai') and bool(str(q.get('why','')).strip())
    return False


def _approved_bank_for_grade(grade):
    """Fetch reviewed rows once per grade to avoid 50 SQLite opens per status."""
    by_topic=defaultdict(list)
    c=get_connection()
    try:
        try:
            rows=c.execute("""SELECT id,topic,question,question_type,difficulty,choices_json,correct_answer,explanation,tags_json
                FROM admin_question_bank WHERE grade=?
                AND source='Question Factory 2.0 · independently reviewed' ORDER BY id""",(grade,)).fetchall()
        except sqlite3.OperationalError:
            rows=[]
        # A source string alone is forgeable. Require an approved QF2 form
        # with a real form ID before a bank row becomes exam evidence.
        try:
            approved_forms={int(r['id']):(r['topic_id'],json.loads(r['questions_json']))
                            for r in c.execute(
                "SELECT id,topic_id,questions_json FROM qf2_forms WHERE grade=? AND status='approved'",
                (grade,)).fetchall()}
        except (sqlite3.OperationalError,ValueError,TypeError):
            approved_forms={}
        for row in rows:
            try:
                tags=json.loads(row['tags_json'] or '[]')
                form_ids={int(tag.split(':',1)[1]) for tag in tags
                          if isinstance(tag,str) and re.fullmatch(r'form:[0-9]+',tag)}
                if len(form_ids)!=1:continue
                form=approved_forms.get(next(iter(form_ids)))
                if not form or form[0]!=row['topic']:continue
                row_choices=json.loads(row['choices_json'] or '[]')
                # Verify exact correspondence to the reviewed, frozen form;
                # source labels and form tags alone are not certification.
                matching=[q for q in form[1]
                          if q.get('question')==row['question']
                          and q.get('difficulty')==row['difficulty']
                          and ('short_answer' if q.get('question_type')=='written' else q.get('question_type'))==row['question_type']
                          and q.get('choices',[])==row_choices
                          and q.get('answer')==row['correct_answer']
                          and q.get('explanation')==row['explanation']]
                if len(matching)!=1:continue
            except (TypeError,ValueError,KeyError):
                continue
            by_topic[row['topic']].append(row)
    finally:c.close()
    return by_topic


def _lesson_fingerprint(question):
    """Invalidate manual review if any statement, answer or explanation changes."""
    return hashlib.sha256(json.dumps(question,ensure_ascii=False,sort_keys=True).encode()).hexdigest()


def _lesson_reviews_for_grade(grade):
    c=get_connection()
    try:
        try:
            rows=c.execute('SELECT topic_id,question_index,question_hash,difficulty,status FROM qf2_lesson_reviews WHERE grade=?',(grade,)).fetchall()
        except sqlite3.OperationalError:
            rows=[]
        return {(r['topic_id'],r['question_index']):dict(r) for r in rows}
    finally:c.close()


def pool(topic, approved_bank=None, lesson_reviews=None):
    _, lessons = _data()
    out=[]; seen=set()
    if lesson_reviews is None:lesson_reviews=_lesson_reviews_for_grade(topic['grade'])
    for ix,q in enumerate(lessons.get(topic['id'],{}).get('quiz',[])):
        if not _valid(q): continue
        reviewed=lesson_reviews.get((topic['id'],ix))
        if reviewed and reviewed['question_hash']!=_lesson_fingerprint(q):reviewed=None
        if reviewed and reviewed['status']=='rejected':continue
        # An author's proposed difficulty is not an independently reviewed tier.
        # Keep it separately for Admin auditing; only approved labels may be
        # counted as diagnostic evidence or enter tier-based exam sampling.
        tier=reviewed['difficulty'] if reviewed and reviewed['status']=='approved' else None
        signature=_key(q)
        if signature in seen: continue
        seen.add(signature)
        out.append({'qid':f"{topic['id']}:{ix}", 'topic_id':topic['id'], 'title':topic['title'],
                    'grade':topic['grade'], 'difficulty':tier, 'question':q['q'],
                    'choices':q.get('choices',[]),'correct':q.get('correct',q.get('answer')),'question_type':('multiple_choice' if q.get('choices') else ('true_false' if str(q.get('type','')).lower() in ('true_false','dung_sai') else 'written')),'explanation':q['why'],
                    'source':'lesson-reviewed' if reviewed and reviewed['status']=='approved' else 'lesson-candidate',
                    'proposed_difficulty': _tier(q,ix)})
    # Only formally approved QF2 rows are eligible for new placement/topic tests.
    # Runtime AI archives are NOT assumed to have independently verified answers.
    rows=(approved_bank if approved_bank is not None else _approved_bank_for_grade(topic['grade'])).get(topic['id'],[])
    for r in rows:
        if not r['explanation'] or len(r['question'].strip())<6:continue
        text_key=re.sub(r'\s+', ' ', r['question'].strip()).casefold()
        if text_key in seen:continue
        try:choices=json.loads(r['choices_json'])
        except (TypeError, ValueError):continue
        kind='written' if r['question_type'] in ('short_answer','written') else r['question_type']
        if kind=='multiple_choice':
            if not isinstance(choices,list) or len(choices)!=4 or r['correct_answer'] not in choices:continue
            correct=choices.index(r['correct_answer'])
        elif kind in ('written','true_false'):
            correct=r['correct_answer'];choices=[]
        else:continue
        # Recheck reviewed bank rows before they enter an actual exam.
        validation_kind = 'short_answer' if kind == 'written' else kind
        if not _valid({'q':r['question'],
                       'choices':choices if kind=='multiple_choice' else None,
                       'correct':correct, 'why':r['explanation'],
                       'type':validation_kind}):
            continue
        if _tier({'difficulty':r['difficulty']},0) is None:
            continue
        tags=json.loads(r['tags_json'] or '[]') if 'tags_json' in r.keys() else []
        form_ids=[int(tag[5:]) for tag in tags if isinstance(tag,str) and re.fullmatch(r'form:[0-9]+',tag)]
        if len(form_ids)!=1:continue
        seen.add(text_key)
        out.append({'form_id':form_ids[0],'qid':f"qf2:{r['id']}",'topic_id':topic['id'],'title':topic['title'],
                    'grade':topic['grade'],'difficulty':_tier({'difficulty':r['difficulty']},0),
                    'question':r['question'],'choices':choices,'correct':correct,
                    'question_type':kind,'explanation':r['explanation'],
                    'source':'qf2-approved'})
    return out


def public(q):
    return {k:q[k] for k in ('qid','topic_id','title','grade','difficulty','question','choices','question_type')}


def coverage(grade):
    topics=[t for t in _data()[0] if t['grade']==grade]
    details=[]
    approved=_approved_bank_for_grade(grade)
    reviews=_lesson_reviews_for_grade(grade)
    for t in topics:
        qs=pool(t,approved,reviews); counts=Counter(q['difficulty'] for q in qs if q['difficulty'])
        certified=sum(q['source'] in ('lesson-reviewed','qf2-approved') for q in qs)
        details.append({'id':t['id'],'title':t['title'],'available':len(qs),
                        'certified':certified,'eligible_for_30_question_exam':certified>=30,
                        'by_difficulty':{d:counts[d] for d in DIFFICULTY},
                        'minimum_met':all(counts[d]>=3 for d in DIFFICULTY),
                        'unlabeled':len(qs)-sum(counts.values())})
    return {'grade':grade,'topic_count':len(topics),'topics_with_questions':sum(d['available']>0 for d in details),
            'topics_with_30_certified':sum(d['eligible_for_30_question_exam'] for d in details),
            'topics_meeting_3_per_tier':sum(d['minimum_met'] for d in details),
            'requirements_fully_met':all(d['minimum_met'] for d in details), 'topics':details}


class StartRequest(BaseModel):
    grade: int = Field(ge=10,le=12)
    mode: str = Field(default='placement', pattern='^(placement|fixed_placement|topic)$')
    topic_id: str | None = Field(default=None,max_length=120)


class SubmitRequest(BaseModel):
    answers: dict[str, object] = Field(default_factory=dict)


class DraftRequest(BaseModel):
    answers: dict[str, object] = Field(default_factory=dict)


def assessment_quality(questions, topics):
    """Recalculate diagnostic coverage for both new and resumed attempts.

    Coverage is a per-topic, per-tier requirement, not a grade-wide total.
    Candidate questions are visible as practice, never certified evidence.
    """
    reviewed_sources = ('lesson-reviewed', 'qf2-approved')
    tier_counts = Counter(q.get('difficulty') for q in questions if q.get('source') in reviewed_sources)
    missing = []
    for topic in topics:
        counts = Counter(q.get('difficulty') for q in questions
                         if q.get('topic_id') == topic['id'] and q.get('source') in reviewed_sources)
        gaps = {tier: max(0, 3-counts[tier]) for tier in DIFFICULTY}
        if any(gaps.values()):
            missing.append({'topic_id': topic['id'], 'title': topic['title'], 'missing_by_tier': gaps})
    # A score without sufficient verified questions must not be advertised as
    # a reliable placement diagnosis. Publish per-topic evidence to the UI.
    per_topic_evidence = []
    for topic in topics:
        evidence = {}
        for tier in DIFFICULTY:
            matching = [q for q in questions
                        if q.get('topic_id') == topic['id']
                        and q.get('difficulty') == tier
                        and q.get('source') in reviewed_sources]
            evidence[tier] = {
                'verified_questions': len(matching),
                'minimum_required': 3,
                'sufficient': len(matching) >= 3,
            }
        per_topic_evidence.append({
            'topic_id': topic['id'], 'title': topic['title'],
            'tiers': evidence,
            'ready': all(e['sufficient'] for e in evidence.values()),
        })
    return {
        'complete_three_tier_coverage': not missing,
        'per_topic_evidence': per_topic_evidence,
        'confidence_label': 'Đủ dữ liệu kiểm chứng' if not missing else 'Chưa đủ dữ liệu để đánh giá năng lực toàn diện',
        'reviewed_items': sum(q.get('source') in reviewed_sources for q in questions),
        'unreviewed_items': sum(q.get('source') not in reviewed_sources for q in questions),
        'three_tier_counts': {tier: tier_counts[tier] for tier in DIFFICULTY},
        'requested_minimum': len(topics)*3*3,
        'topics_missing_verified_tiers': len(missing),
        'missing_topic_details': missing,
        'note': 'Các câu chưa được duyệt chỉ phục vụ tham khảo, không chứng minh độ chính xác của bài đánh giá.'
    }



def select_placement_questions(topics, approved, reviews, *, rng=None):
    """Three or four verified items per tier/topic when available.

    Unreviewed lesson candidates are shown only when a tier is short; they
    never make the placement certified. Each topic is kept in the paper so
    coverage shortages are visible instead of silently omitting a topic.
    """
    rng = rng or random
    result = []
    for topic in topics:
        available = pool(topic, approved, reviews)
        used = set()
        for tier in DIFFICULTY:
            eligible = [q for q in available if q['difficulty'] == tier
                        and q['source'] in ('lesson-reviewed', 'qf2-approved')]
            rng.shuffle(eligible)
            for q in eligible[:4]:
                if q['qid'] not in used:
                    result.append(q)
                    used.add(q['qid'])
        # Only provisional, never counted as diagnostic evidence. Do not add
        # unverified filler when all three tiers already have >=3 questions.
        chosen = [q for q in result if q['topic_id'] == topic['id']]
        if not all(sum(q['difficulty'] == tier for q in chosen) >= 3 for tier in DIFFICULTY):
            candidates = [q for q in available if q['source'] not in ('lesson-reviewed','qf2-approved')
                          and q['qid'] not in used]
            rng.shuffle(candidates)
            # Cap at nine provisional items per topic, with an explicit label.
            for q in candidates[:max(1, 9-len(chosen))]:
                result.append(q)
                used.add(q['qid'])
        if not any(q['topic_id'] == topic['id'] for q in result) and available:
            result.append(available[0])
    rng.shuffle(result)
    return result



def _placement_topic_priority(counts, curriculum_index):
    """Rank observed weaknesses without treating skipped questions as errors.

    Prefer topics with sufficient answered evidence. Topics with only skips
    need re-assessment, not a fictional zero-percent mastery estimate.
    """
    answered = counts['correct'] + counts['wrong']
    if answered >= 3:
        evidence_bucket = 0
    elif answered:
        evidence_bucket = 1
    else:
        evidence_bucket = 2
    accuracy = counts['correct'] / answered if answered else 1.0
    return (evidence_bucket, accuracy, -answered, curriculum_index)


def _fixed_blueprint(grade):
    blueprint=load_blueprint(ROOT,grade)
    grade_topics=[t for t in _data()[0] if t['grade']==grade]
    if [(t['id'],t['title']) for t in grade_topics] != [
            (t['topic_id'],t['title']) for t in blueprint['topics']]:
        raise HTTPException(503,'Đề cương cố định không đồng bộ với danh mục chủ đề.')
    return blueprint,grade_topics


def _fixed_build(grade):
    blueprint,grade_topics=_fixed_blueprint(grade)
    approved=_approved_bank_for_grade(grade)
    reviews=_lesson_reviews_for_grade(grade)
    by_topic={t['id']:pool(t,approved,reviews) for t in grade_topics}
    return assemble_fixed_paper(blueprint,by_topic)


def _active_fixed_paper(c,grade):
    return c.execute('SELECT * FROM roadmap_v2_fixed_papers WHERE grade=? AND is_active=1 '
                     'ORDER BY published_at DESC LIMIT 1',(grade,)).fetchone()


def _paper_valid_now(grade,paper):
    """Review revocations or changed lesson content invalidate an old paper."""
    if paper is None:
        return False
    try:
        stored=json.loads(paper['questions_json'])
        blueprint, grade_topics = _fixed_blueprint(grade)
        if (int(paper['grade']) != grade
                or digest(stored) != paper['paper_hash']
                or paper['blueprint_hash'] != digest(blueprint)
                or not validate_frozen_paper(blueprint, stored)):
            return False
        approved=_approved_bank_for_grade(grade)
        reviews=_lesson_reviews_for_grade(grade)
        by_topic={q['topic_id'] for q in stored}
        current={q['qid']:q for t in grade_topics if t['id'] in by_topic
                 for q in pool(t,approved,reviews)}
        return all(q['qid'] in current and digest(q)==digest(current[q['qid']])
                   and q.get('source') == 'qf2-approved'
                   for q in stored)
    except (ValueError, KeyError, TypeError):
        return False


def _fixed_status(grade):
    if grade not in (10,11,12):raise HTTPException(422,'Lớp không hợp lệ')
    paper_status=_fixed_build(grade)
    with db() as c:
        paper=_active_fixed_paper(c,grade)
    published_valid=_paper_valid_now(grade,paper)
    return {k:v for k,v in paper_status.items() if k!='questions'} | {
        'candidate_paper_hash':paper_status['paper_hash'],
        'paper_hash':paper['paper_hash'] if paper and published_valid else None,
        'has_new_candidate':bool(paper and published_valid and paper_status['ready']
                                 and paper_status['paper_hash']!=paper['paper_hash']),
        'published':paper is not None,
        'published_valid':published_valid,
        'paper_id':paper['paper_id'] if paper and published_valid else None,
        'published_at':paper['published_at'] if paper and published_valid else None,
        'official_exam_available':published_valid,
        # Sufficient content coverage is not evidence of psychometric validity.
        # An independently piloted, calibrated form is a separate milestone.
        'psychometric_validated':False,
        'validation_stage':('content_reviewed_not_empirically_validated'
                            if published_valid else 'not_published'),
        'note':('Đề chỉ được mở khi đã kiểm duyệt và xuất bản. '
                'Đủ số câu KHÔNG đồng nghĩa đã chứng minh độ tin cậy, '
                'độ phân biệt hay tính công bằng trên học sinh thực tế.')}



@router.get('/fixed/status/{grade}')
def fixed_exam_status(grade:int,authorization:str|None=Header(default=None)):
    student(authorization)
    return _fixed_status(grade)


@router.get('/fixed/admin-status/{grade}')
def admin_fixed_status(grade:int,authorization:str|None=Header(default=None)):
    from .admin_routes import require_admin
    require_admin(authorization)
    return _fixed_status(grade)


@router.post('/fixed/publish/{grade}')
def publish_fixed_exam(grade:int,authorization:str|None=Header(default=None)):
    from .admin_routes import require_admin
    admin=require_admin(authorization)
    if grade not in (10,11,12):raise HTTPException(422,'Lớp không hợp lệ')
    result=_fixed_build(grade)
    if not result['ready']:
        raise HTTPException(409,detail={
            'reason':'paper_not_ready','required':result['required'],
            'selected':result['selected'],'gaps':result['gaps'],
            'format_warnings':result['format_warnings'],
            'distinct_form_gaps':result['distinct_form_gaps'],
            'message':'Không thể xuất bản đề chưa đủ câu đã duyệt và đa dạng hình thức.'})
    questions=result['questions']
    paper_id=f"fixed-{grade}-{digest([result['paper_hash'],result['blueprint_hash']])[:20]}"
    admin_id=int(admin['id'])
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        current=_active_fixed_paper(c,grade)
        if (current and current['paper_hash']==result['paper_hash']
                and current['blueprint_hash']==result['blueprint_hash']):
            c.commit()
            return {'published':True,'paper_id':current['paper_id'],
                    'paper_hash':current['paper_hash'],'total':len(questions),'unchanged':True}
        c.execute('UPDATE roadmap_v2_fixed_papers SET is_active=0 WHERE grade=?',(grade,))
        c.execute('INSERT INTO roadmap_v2_fixed_papers '
                  '(paper_id,grade,paper_hash,blueprint_hash,questions_json,published_at,published_by,is_active) '
                  'VALUES(?,?,?,?,?,?,?,1)',
                  (paper_id,grade,result['paper_hash'],result['blueprint_hash'],
                   json.dumps(questions,ensure_ascii=False),now(),admin_id))
        c.commit()
    return {'published':True,'paper_id':paper_id,'paper_hash':result['paper_hash'],
            'total':len(questions),'unchanged':False}




@router.get('/fixed/calibration/{grade}')
def fixed_calibration(grade:int,authorization:str|None=Header(default=None)):
    """Admin-only, aggregate psychometric pilot metrics for one frozen form."""
    from .admin_routes import require_admin
    from .placement_psychometrics import evaluate_fixed_paper
    require_admin(authorization)
    if grade not in (10,11,12):raise HTTPException(422,'Lớp không hợp lệ')
    with db() as c:
        paper=_active_fixed_paper(c,grade)
        if not paper:raise HTTPException(409,'Chưa có đề đầu vào cố định được công bố.')
        expected=json.loads(paper['questions_json'])
        rows=c.execute("SELECT user_id,result_json FROM roadmap_v2_attempts "
                       "WHERE grade=? AND mode='fixed_placement' AND submitted_at IS NOT NULL "
                       "ORDER BY submitted_at DESC",(grade,)).fetchall()
    # One result per student, only for the current immutable form.
    seen=set();results=[]
    for row in rows:
        if row['user_id'] in seen:continue
        result=json.loads(row['result_json'])
        if result.get('fixed_paper_hash')!=paper['paper_hash']:continue
        seen.add(row['user_id']);results.append(result)
    return {'grade':grade,'paper_id':paper['paper_id'],
            'analysis':evaluate_fixed_paper(results,[q['qid'] for q in expected])}

def _new_attempt(c,user,grade,mode,topic,questions):
    aid=secrets.token_urlsafe(18)
    c.execute('INSERT INTO roadmap_v2_attempts VALUES (?,?,?,?,?,?,?,?,?,?)',
              (aid,user,grade,mode,topic,json.dumps(questions,ensure_ascii=False),None,None,None,now()))
    c.commit()
    return {'attempt_id':aid,'grade':grade,'mode':mode,'topic_id':topic,'total':len(questions),
            'questions':[public(q) for q in questions]}



def public_result(summary):
    """Keep the official *fixed* paper's answer key private.

    The student still sees totals, per-topic/tier diagnosis, and suggested
    topics. Per-item solutions stay on the trusted server because the same
    published fixed form is administered to many learners. Ordinary practice
    and 30-question topic tests keep their complete worked review.
    """
    if not summary or summary.get('mode') != 'fixed_placement':
        return summary
    safe = dict(summary)
    safe['review'] = []
    safe['review_release_policy'] = 'fixed_paper_protected'
    safe['review_notice'] = ('Đề đầu vào cố định dùng chung cho nhiều học sinh. '
        'Hệ thống chỉ công bố điểm, kết quả theo chủ đề/mức độ và gợi ý ôn tập; '
        'đáp án chi tiết được bảo mật để hạn chế học tủ và truyền đáp án.')
    return safe


@router.get('/catalog')
def catalog(authorization: str | None=Header(default=None)):
    student(authorization)
    return {'grades':[coverage(g) for g in (10,11,12)],
            'note':'Độ khó chỉ được tính khi câu có nhãn đã kiểm tra; câu không có nhãn không được tự gán vào 3 mức.'}


@router.get('/status/{grade}')
def status(grade:int,authorization:str|None=Header(default=None)):
    user=student(authorization)
    if grade not in (10,11,12): raise HTTPException(422,'Lớp không hợp lệ')
    with db() as c:
        p=c.execute("SELECT result_json,mode FROM roadmap_v2_attempts WHERE user_id=? AND grade=? AND mode IN ('fixed_placement','placement') AND submitted_at IS NOT NULL ORDER BY CASE WHEN mode='fixed_placement' THEN 0 ELSE 1 END, submitted_at DESC LIMIT 1",(user,grade)).fetchone()
        rows=c.execute('SELECT topic_id,best_score,attempts FROM roadmap_v2_mastery WHERE user_id=? AND grade=?',(user,grade)).fetchall()
    diagnostic=public_result(json.loads(p['result_json'])) if p else None
    fixed=fixed_exam_status(grade,authorization)
    validated=bool(p and p['mode']=='fixed_placement' and diagnostic
                   and diagnostic.get('diagnostic_completeness',{}).get('reliable_for_placement')
                   and fixed['published_valid'] and diagnostic.get('fixed_paper_hash')==fixed['paper_hash'])
    return {'grade':grade,'placement_complete':bool(p),
            'official_placement_complete':validated,
            'fixed_exam':fixed, 'placement_validated':validated,
            'placement_state':'validated' if validated else ('provisional' if p else 'not_started'),
            'diagnostic':diagnostic,'mastery':[dict(r) for r in rows], 'coverage':coverage(grade)}


@router.post('/start')
def start(req:StartRequest,authorization:str|None=Header(default=None)):
    user=student(authorization)
    topics=[t for t in _data()[0] if t['grade']==req.grade]
    with db() as c:
        existing=c.execute('SELECT attempt_id,questions_json,topic_id,mode,responses_json FROM roadmap_v2_attempts WHERE user_id=? AND grade=? AND mode=? AND submitted_at IS NULL ORDER BY created_at DESC LIMIT 1',(user,req.grade,req.mode)).fetchone()
        if existing and req.mode=='fixed_placement':
            current_paper=_active_fixed_paper(c,req.grade)
            if not current_paper or not _paper_valid_now(req.grade,current_paper) or digest(json.loads(existing['questions_json']))!=current_paper['paper_hash']:
                # An invalidated paper may not be resumed. The learner can
                # start the newly published form; no old answer key is used.
                c.execute('DELETE FROM roadmap_v2_attempts WHERE attempt_id=? AND user_id=? AND submitted_at IS NULL',
                          (existing['attempt_id'],user))
                c.commit()
                existing=None
        if existing and (req.mode in ('placement','fixed_placement') or existing['topic_id']==req.topic_id):
            qs=json.loads(existing['questions_json'])
            resumed={'attempt_id':existing['attempt_id'],'grade':req.grade,'mode':req.mode,'topic_id':existing['topic_id'],
                    'total':len(qs),'questions':[public(q) for q in qs], 'resumed':True,
                    'draft_answers':json.loads(existing['responses_json']) if existing['responses_json'] else {}}
            if req.mode in ('placement','fixed_placement'):
                resumed['assessment_quality']=assessment_quality(qs,topics)
            if req.mode=='fixed_placement':
                resumed['paper_hash']=digest(qs)
            return resumed
        if req.mode=='fixed_placement':
            paper=_active_fixed_paper(c,req.grade)
            if not paper or not _paper_valid_now(req.grade,paper):
                raise HTTPException(409,detail={
                    'reason':'fixed_paper_not_published',
                    'message':'Đề đầu vào cố định của lớp này chưa được kiểm chứng và xuất bản.',
                    'grade':req.grade,'blueprint':_fixed_build(req.grade)['selected']})
            last=c.execute("SELECT result_json FROM roadmap_v2_attempts WHERE user_id=? AND grade=? AND mode='fixed_placement' AND submitted_at IS NOT NULL ORDER BY submitted_at DESC LIMIT 1",(user,req.grade)).fetchone()
            if last and json.loads(last['result_json']).get('fixed_paper_hash')==paper['paper_hash']:
                raise HTTPException(409,detail={'reason':'already_completed',
                    'message':'Bạn đã hoàn thành phiên bản đề cố định này. Có thể xem lại kết quả, không được thi lại cùng đáp án.'})
            qs=json.loads(paper['questions_json'])
            result=_new_attempt(c,user,req.grade,'fixed_placement',None,qs)
            result['paper_id']=paper['paper_id']
            result['paper_hash']=paper['paper_hash']
            result['assessment_quality']=assessment_quality(qs,topics)
            return result
        if req.mode=='placement':
            approved=_approved_bank_for_grade(req.grade)
            reviews=_lesson_reviews_for_grade(req.grade)
            questions=select_placement_questions(topics,approved,reviews)
            if len(set(q['topic_id'] for q in questions))!=len(topics):
                raise HTTPException(503,'Thiếu câu hỏi cho một hoặc nhiều chủ đề. Cần bổ sung ngân hàng trước khi kiểm tra.')
            random.shuffle(questions)
            result=_new_attempt(c,user,req.grade,'placement',None,questions)
            result['assessment_quality']=assessment_quality(questions,topics)
            return result
        current=c.execute("SELECT 1 FROM roadmap_v2_attempts WHERE user_id=? AND grade=? AND mode='fixed_placement' AND submitted_at IS NOT NULL LIMIT 1",(user,req.grade)).fetchone()
        if not current:
            legacy=c.execute("SELECT 1 FROM roadmap_v2_attempts WHERE user_id=? AND grade=? AND mode='placement' AND submitted_at IS NOT NULL LIMIT 1",(user,req.grade)).fetchone()
            if not legacy:
                raise HTTPException(403,'Bạn phải hoàn tất kiểm tra đầu vào trước.')
            raise HTTPException(409,detail={
                'reason':'placement_not_validated', 'message':'Bài thử không thay thế đề đầu vào cố định đã được kiểm chứng.',
                'available':0,'required':30})
        completed=c.execute("SELECT result_json FROM roadmap_v2_attempts WHERE user_id=? AND grade=? AND mode='fixed_placement' AND submitted_at IS NOT NULL ORDER BY submitted_at DESC LIMIT 1",(user,req.grade)).fetchone()
        active_paper=_active_fixed_paper(c,req.grade)
        completed_result=json.loads(completed['result_json']) if completed else {}
        reliable=bool(completed and active_paper and _paper_valid_now(req.grade,active_paper)
                      and completed_result.get('diagnostic_completeness',{}).get('reliable_for_placement')
                      and completed_result.get('fixed_paper_hash')==active_paper['paper_hash'])
        if not reliable:
            # Fail closed: a provisional test must not open an official exam.
            # The existing client understands the available/required fields.
            raise HTTPException(409,detail={
                'message':'Bài đầu vào chưa đủ câu đã kiểm chứng ở cả ba mức cho từng chủ đề. Chưa thể mở kiểm tra chính thức.',
                'reason':'placement_not_validated','available':0,'required':30,
                'coverage':coverage(req.grade)['topics_meeting_3_per_tier'],
                'topics_required':len(topics)})
        index=next((i for i,t in enumerate(topics) if t['id']==req.topic_id),-1)
        if index<0:raise HTTPException(404,'Chủ đề không thuộc lớp đã chọn')
        done={r[0] for r in c.execute('SELECT topic_id FROM roadmap_v2_mastery WHERE user_id=? AND grade=? AND best_score>=25',(user,req.grade))}
        placement=c.execute("SELECT result_json FROM roadmap_v2_attempts WHERE user_id=? AND grade=? AND mode='fixed_placement' AND submitted_at IS NOT NULL ORDER BY submitted_at DESC LIMIT 1",(user,req.grade)).fetchone()
        ordering=json.loads(placement['result_json']).get('roadmap_order',[]) if placement else []
        ordered=[next(t for t in topics if t['id']==tid) for tid in ordering if any(t['id']==tid for t in topics)]
        ordered.extend(t for t in topics if t['id'] not in set(ordering))
        index=next((i for i,t in enumerate(ordered) if t['id']==req.topic_id),-1)
        # Only reveal one group of 3 after previous groups all passed.
        if index >= 3 and not all(t['id'] in done for t in ordered[(index//3-1)*3:(index//3)*3]):
            raise HTTPException(403,'Hãy hoàn thành nhóm 3 chủ đề trước để mở khóa')
        # A practice bank candidate can help with exploration, but may not be
        # used as a pass/fail exam question. The 25/30 unlock is based only on
        # content that was explicitly reviewed and approved by Admin.
        all_questions=pool(ordered[index])
        qs=[q for q in all_questions if q['source'] in ('lesson-reviewed','qf2-approved')]
        random.shuffle(qs)
        if len(qs)<30:
            raise HTTPException(409,detail={
                'message':'Chủ đề chưa đủ 30 câu đã kiểm chứng độc lập; chưa thể mở bài kiểm tra chính thức.',
                'available':len(qs),'candidate_count':len(all_questions),'required':30})
        return _new_attempt(c,user,req.grade,'topic',req.topic_id,qs[:30])


@router.post('/draft/{attempt_id}')
def save_draft(attempt_id:str,req:DraftRequest,authorization:str|None=Header(default=None)):
    """Persist a long placement test safely; never reveal answer keys."""
    user=student(authorization)
    if len(attempt_id)>100:raise HTTPException(404,'Không tìm thấy bài thi')
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT questions_json,submitted_at FROM roadmap_v2_attempts WHERE attempt_id=? AND user_id=?',
                      (attempt_id,user)).fetchone()
        if not row:raise HTTPException(404,'Không tìm thấy bài thi')
        if row['submitted_at']:raise HTTPException(409,'Bài thi đã nộp')
        valid_ids={q['qid'] for q in json.loads(row['questions_json'])}
        serialized=_check_answer_payload(req.answers,valid_ids)
        c.execute('UPDATE roadmap_v2_attempts SET responses_json=? WHERE attempt_id=?',(serialized,attempt_id))
        c.commit()
    return {'saved':True,'answered':len(req.answers)}


MAX_ANSWER_PAYLOAD_BYTES = 150_000
MAX_SINGLE_ANSWER_CHARS = 2_000


def _check_answer_payload(answers, valid_ids):
    if (len(answers) > len(valid_ids) or any(key not in valid_ids for key in answers)):
        raise HTTPException(422, 'Danh sách câu trả lời không hợp lệ')
    for given in answers.values():
        if (given is not None and (not isinstance(given, (str, int, float, bool))
                                   or len(str(given)) > MAX_SINGLE_ANSWER_CHARS)):
            raise HTTPException(422, 'Một câu trả lời quá dài hoặc sai định dạng')
    encoded = json.dumps(answers, ensure_ascii=False, allow_nan=False)
    if len(encoded.encode('utf-8')) > MAX_ANSWER_PAYLOAD_BYTES:
        raise HTTPException(413, 'Dữ liệu câu trả lời vượt giới hạn')
    return encoded


def grade_question(q,answer):
    if answer is None or (isinstance(answer,str) and not answer.strip()):
        return 'skipped'
    if q['question_type']=='multiple_choice':
        # The roadmap stores 0-based indices, while the front end may submit
        # a letter or the visible choice text. Grade all forms consistently.
        from .questions.answer_checker import grade_answer
        options=q.get('choices') or []
        expected=options[q['correct']] if isinstance(q.get('correct'),int) and 0<=q['correct']<len(options) else None
        if expected is None:
            return 'wrong'
        return 'correct' if grade_answer({'question_type':'multiple_choice','options':options},answer,expected) else 'wrong'
    if q['question_type']=='true_false':
        from .questions.answer_checker import grade_answer
        return 'correct' if grade_answer({'question_type':'true_false'},answer,q['correct']) else 'wrong'
    from .questions.answer_checker import grade_answer
    return 'correct' if grade_answer({'question_type':'short_answer'},answer,q['correct']) else 'wrong'


@router.post('/submit/{attempt_id}')
def submit(attempt_id:str,req:SubmitRequest,authorization:str|None=Header(default=None)):
    user=student(authorization)
    if len(attempt_id)>100:raise HTTPException(404,'Không tìm thấy bài thi')
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT * FROM roadmap_v2_attempts WHERE attempt_id=? AND user_id=?',(attempt_id,user)).fetchone()
        if not row:raise HTTPException(404,'Không tìm thấy bài thi')
        if row['submitted_at']:raise HTTPException(409,'Bài này đã nộp; không thể chấm thêm.')
        qs=json.loads(row['questions_json']); valid_ids={q['qid'] for q in qs}
        if row['mode']=='fixed_placement':
            paper=_active_fixed_paper(c,row['grade'])
            if not paper or not _paper_valid_now(row['grade'],paper) or digest(qs)!=paper['paper_hash']:
                raise HTTPException(409,'Đề đầu vào cố định đã bị thay đổi hoặc thu hồi. Hãy liên hệ quản trị viên.')
        serialized_answers=_check_answer_payload(req.answers,valid_ids)
        counts=Counter();tiers=defaultdict(Counter);topics=defaultdict(Counter);review=[]
        for i,q in enumerate(qs,1):
            given=req.answers.get(q['qid']); verdict=grade_question(q,given)
            counts[verdict]+=1; topics[q['topic_id']][verdict]+=1
            tiers[q['difficulty'] or 'chưa phân loại'][verdict]+=1
            review.append({'number':i,'qid':q['qid'],'topic_id':q['topic_id'],'topic':q['title'],
                           'difficulty':q['difficulty'],'source':q.get('source','unknown'),
                           'verified_for_diagnostic':q.get('source') in ('lesson-reviewed','qf2-approved'),
                           'question':q['question'],'choices':q['choices'],
                           'answer':given,'expected':(q['choices'][q['correct']] if q['question_type']=='multiple_choice' else str(q['correct'])), 'verdict':verdict,
                           'explanation':q['explanation']})
        verified_review=[x for x in review if x['verified_for_diagnostic']]
        verified_counts=Counter(x['verdict'] for x in verified_review)
        summary={'grade':row['grade'],'topic_id':row['topic_id'],'mode':row['mode'],'total':len(qs),
                 'verified_score':{'total':len(verified_review),'correct':verified_counts['correct'],
                                   'wrong':verified_counts['wrong'],'skipped':verified_counts['skipped']},
                 'correct':counts['correct'],'wrong':counts['wrong'],'skipped':counts['skipped'],
                 'by_topic':{k:dict(v) for k,v in topics.items()},
                 'by_difficulty':{k:dict(v) for k,v in tiers.items()},
                 'review':review,'passed':row['mode']=='topic' and counts['correct']>=25,
                 'coverage_note':'Phân loại còn thiếu ở các câu chưa có nhãn độ khó được kiểm chứng.',
                 'verified_question_count':sum(q['source'] in ('lesson-reviewed','qf2-approved') for q in qs),
                 'candidate_question_count':sum(q['source'] not in ('lesson-reviewed','qf2-approved') for q in qs),
                 'skill_update_policy':'Only independently approved correct/wrong answers update the skill model; skipped answers are logged but not penalized.',
                 'training_evidence':{
                   'verified_answered':sum(x['verified_for_diagnostic'] and x['verdict'] in ('correct','wrong') for x in review),
                   'verified_skipped':sum(x['verified_for_diagnostic'] and x['verdict']=='skipped' for x in review),
                   'candidate_ignored':sum(not x['verified_for_diagnostic'] for x in review),
                   'method':'Online Bayesian Knowledge Tracing; manually chosen parameters, not calibrated'}}
        if row['mode'] in ('placement','fixed_placement'):
            per_topic_tiers={tid:Counter(q['difficulty'] for q in qs if q['topic_id']==tid) for tid in topics}
            # Candidate questions cannot certify placement reliability.
            grade_topics=[t for t in _data()[0] if t['grade']==row['grade']]
            quality=assessment_quality(qs,grade_topics)
            summary['assessment_quality']=quality
            summary['diagnostic_completeness']={
                'three_tiers_complete':quality['complete_three_tier_coverage'],
                'topics_sampled':len(per_topic_tiers),
                'topics_with_3_per_tier':sum(
                    all(sum(q['topic_id']==tid and q.get('difficulty')==tier
                            and q.get('source') in ('lesson-reviewed','qf2-approved')
                            for q in qs)>=3 for tier in DIFFICULTY)
                    for tid in per_topic_tiers),
                'verified_items':quality['reviewed_items'],
                'candidate_items':quality['unreviewed_items'],
                # This flag is a structural coverage gate. 3 questions per
                # tier do not establish reliability on a population of learners.
                'reliable_for_placement':quality['complete_three_tier_coverage'],  # structural gate, not population reliability
                'content_coverage_complete':quality['complete_three_tier_coverage'],
                'psychometric_validated':False,
                'disclaimer':('Đủ 3 câu đã duyệt mỗi mức chỉ xác nhận ĐỘ PHỦ NỘI DUNG. '
                    'Chưa chứng minh độ tin cậy hoặc tính công bằng của đề; '
                    'cần thử nghiệm với học sinh thực tế và hiệu chuẩn câu hỏi.')}

            # A skipped item is an unanswered item, not proof of weakness.
            # Prefer weaknesses supported by actual answers, then topics with
            # few answers; unassessed topics remain in curricular order.
            topic_map={t['id']:t for t in _data()[0] if t['grade']==row['grade']}
            trusted=defaultdict(Counter)
            for item in verified_review:
                trusted[item['topic_id']][item['verdict']]+=1
            positions={k:i for i,k in enumerate(topic_map)}
            ranking=sorted(topic_map,key=lambda k:_placement_topic_priority(trusted[k],positions[k]))
            def topic_reason(k):
                c=trusted[k]
                answered=c['correct']+c['wrong']
                if not answered:
                    return 'Chưa có câu trả lời được duyệt; nên làm bài ngắn để xác định kiến thức.'
                if answered<3:
                    return 'Mới có ít câu đã trả lời; cần đánh giá bổ sung trước khi kết luận.'
                return ('Ưu tiên ôn những câu đã trả lời sai' if c['wrong'] else
                        'Tiếp tục luyện vận dụng và kiểm tra lại')
            summary['suggested_topics']=[{'id':k,'title':topic_map[k]['title'],
                'reason':topic_reason(k),
                'verified_evidence':trusted[k]['correct']+trusted[k]['wrong'],
                'verified_skipped':trusted[k]['skipped']} for k in ranking[:3]]
            summary['roadmap_order'] = ranking
            summary['roadmap_is_provisional'] = (row['mode']!='fixed_placement'
                                                 or not quality['complete_three_tier_coverage'])
            if row['mode']=='fixed_placement':
                blueprint,_=_fixed_blueprint(row['grade'])
                summary['fixed_paper_hash']=digest(qs)
                summary['objective_evidence']=evidence_profile(review,blueprint)
        # Rebuild any existing V23 history first; subsequently update the
        # fitted predictor only with distinct, verified answered questions.
        personal_predictor = learner_online.ensure(c, user, row['grade'])
        # Record every attempt for transparent history, but learn from a
        # given approved question only once per learner and grade. Repeating
        # the same fixed or topic item is practice, not independent evidence.
        unique_learned=0
        repeated_ignored=0
        for item in review:
            if not item['verified_for_diagnostic']:
                continue
            tier=item['difficulty'] or 'chưa phân loại'
            previously_answered = bool(item['verdict'] != 'skipped' and c.execute(
                "SELECT 1 FROM roadmap_v2_learning_events WHERE user_id=? AND grade=? "
                "AND qid=? AND attempt_id<>? AND verdict IN ('correct','wrong') LIMIT 1",
                (user,row['grade'],item['qid'],attempt_id)).fetchone())
            inserted=c.execute('INSERT OR IGNORE INTO roadmap_v2_learning_events(user_id,grade,attempt_id,qid,topic_id,tier,verdict,source,created_at) VALUES (?,?,?,?,?,?,?,?,?)',
                (user,row['grade'],attempt_id,item['qid'],item['topic_id'],tier,item['verdict'],item['source'],now()))
            if inserted.rowcount != 1 or item['verdict']=='skipped':
                continue
            if previously_answered:
                repeated_ignored+=1
                continue
            old=c.execute('SELECT mastery,observations FROM roadmap_v2_skill_state WHERE user_id=? AND grade=? AND topic_id=? AND tier=?',(user,row['grade'],item['topic_id'],tier)).fetchone()
            prior=float(old['mastery']) if old else 0.35
            updated=_bkt_next(prior,item['verdict']=='correct',tier)
            c.execute('INSERT INTO roadmap_v2_skill_state VALUES (?,?,?,?,?,?,?) ON CONFLICT(user_id,grade,topic_id,tier) DO UPDATE SET mastery=excluded.mastery, observations=excluded.observations, updated_at=excluded.updated_at',
                      (user,row['grade'],item['topic_id'],tier,updated,(int(old['observations']) if old else 0)+1,now()))
            # Actual SGD training uses the outcome of the authenticated,
            # server-graded item, never the student's untrusted correctness.
            learner_online.learn(personal_predictor,item['topic_id'],tier,item['verdict'])
            unique_learned+=1
        learner_online.save(c,user,row['grade'],personal_predictor)
        summary['training_evidence']['trained_predictor']=learner_online.public_report(personal_predictor)
        summary['training_evidence']['unique_new_answers']=unique_learned
        summary['training_evidence']['repeated_answers_excluded']=repeated_ignored
        summary['training_evidence']['repeat_policy']='Một câu hỏi đã dùng để cập nhật năng lực sẽ không được cộng lại trong lần làm sau.'
        # Save after completing the evidence update so the returned report and
        # persisted report always agree; the transaction remains atomic.
        c.execute('UPDATE roadmap_v2_attempts SET submitted_at=?,responses_json=?,result_json=? WHERE attempt_id=?',
                  (now(),serialized_answers,json.dumps(summary,ensure_ascii=False),attempt_id))
        if row['mode']=='topic':
            c.execute('INSERT INTO roadmap_v2_mastery(user_id,grade,topic_id,best_score,attempts,updated_at) VALUES(?,?,?,?,1,?) ON CONFLICT(user_id,grade,topic_id) DO UPDATE SET best_score=max(best_score,excluded.best_score),attempts=attempts+1,updated_at=excluded.updated_at',(user,row['grade'],row['topic_id'],counts['correct'],now()))
        c.commit()
    return public_result(summary)


@router.get('/latest/{grade}')
def latest(grade:int,authorization:str|None=Header(default=None)):
    user=student(authorization)
    if grade not in (10,11,12):raise HTTPException(422,'Lớp không hợp lệ')
    with db() as c:
        row=c.execute("SELECT result_json FROM roadmap_v2_attempts WHERE user_id=? AND grade=? AND mode IN ('fixed_placement','placement') AND submitted_at IS NOT NULL ORDER BY CASE WHEN mode='fixed_placement' THEN 0 ELSE 1 END, submitted_at DESC LIMIT 1",(user,grade)).fetchone()
    return {'result':public_result(json.loads(row['result_json'])) if row else None}


def _effective_training_evidence(events):
    """One training observation per approved question, even across retakes.

    A skip is not a failure. If the learner later answers that question,
    the first actual answer becomes evidence. Later attempts are history only.
    This is also used for user-visible statistics, not just BKT updates.
    """
    first={}
    for event in events:
        qid=event['qid']
        if qid not in first or (first[qid]['verdict']=='skipped' and event['verdict'] in ('correct','wrong')):
            first[qid]={'qid':qid,'topic_id':event['topic_id'],
                        'tier':event['tier'],'verdict':event['verdict']}
    return list(first.values())


@router.get('/tutor/{grade}')
def tutor_profile(grade:int,authorization:str|None=Header(default=None), include_all:bool=False):
    """Per-student incremental knowledge tracing from independently reviewed items."""
    user=student(authorization)
    if grade not in (10,11,12):raise HTTPException(422,'Lớp không hợp lệ')
    with db() as c:
        rows=c.execute('SELECT topic_id,tier,mastery,observations FROM roadmap_v2_skill_state WHERE user_id=? AND grade=?',(user,grade)).fetchall()
        events=c.execute('SELECT topic_id,tier,qid,verdict,created_at FROM roadmap_v2_learning_events WHERE user_id=? AND grade=? ORDER BY created_at, rowid',(user,grade)).fetchall()
        completed={r['topic_id'] for r in c.execute('SELECT topic_id FROM roadmap_v2_mastery WHERE user_id=? AND grade=? AND best_score>=25',(user,grade)).fetchall()}
        # One-time, deterministic backfill for V23 accounts. Same user/grade.
        fitted_predictor=learner_online.ensure(c,user,grade)
        c.commit()
    topics={t['id']:t for t in _data()[0] if t['grade']==grade}
    stats=defaultdict(Counter)
    tier_stats=defaultdict(lambda:defaultdict(Counter))
    total_events=len(events)
    effective=_effective_training_evidence(events)
    for e in effective:
        if e['topic_id'] in topics:
            stats[e['topic_id']][e['verdict']]+=1
            tier_stats[e['topic_id']][e['tier']][e['verdict']]+=1
    agg=defaultdict(lambda:{'weighted':0.0,'observations':0,'tiers':{}})
    for r in rows:
        if r['topic_id'] not in topics:continue
        state=agg[r['topic_id']];n=int(r['observations'])
        state['weighted']+=float(r['mastery'])*n
        state['observations']+=n
        state['tiers'][r['tier']]={'mastery_percent':round(100*float(r['mastery'])),'observations':n}
    recommendations=[]
    for topic_id,state in agg.items():
        if not state['observations']:continue
        evidence=stats[topic_id]
        # Do not present an accurate-looking 0-100% as certified measurement.
        n=state['observations']
        confidence='rất ít bằng chứng' if n<3 else 'bằng chứng còn hạn chế' if n<10 else 'ước lượng đang tích lũy'
        tiers=state['tiers']
        focus=min(tiers, key=lambda t:(tiers[t]['mastery_percent'], -tiers[t]['observations']))
        mastery=round(100*state['weighted']/n)
        if n<3:
            reason=f'Mới có {n} câu được xác minh. Cần thêm bài tập trước khi kết luận năng lực.'
        elif evidence['wrong']>evidence['correct']:
            reason=f'Đã ghi nhận {evidence["wrong"]} câu sai trên nội dung được duyệt; ưu tiên xem lý thuyết và luyện lại.'
        else:
            reason=f'Ước lượng theo {n} câu đã được duyệt; nên củng cố mức {focus}.'
        observed_tiers={tier:{'correct':tier_stats[topic_id][tier]['correct'],
                              'wrong':tier_stats[topic_id][tier]['wrong'],
                              'skipped':tier_stats[topic_id][tier]['skipped'],
                              'answered':(tier_stats[topic_id][tier]['correct']+
                                          tier_stats[topic_id][tier]['wrong'])}
                        for tier in DIFFICULTY}
        fitted=learner_online.suggestions_for_topic(fitted_predictor,topic_id)
        # Model predictions are probabilities of a correct *future answer*,
        # distinct from BKT's uncalibrated estimated knowledge mastery.
        recommendations.append({'topic_id':topic_id,'title':topics[topic_id]['title'],
                'estimated_mastery':mastery,'observations':n,'tiers':tiers,
                'next_answer_prediction':fitted['predicted_correct'],
                'online_prediction_ready':fitted['predictive_ready'],
                'online_focus_tier':fitted['focus_tier'],
                'right':evidence['correct'],'wrong':evidence['wrong'],'skipped':evidence['skipped'],
                'observed_by_tier':observed_tiers,
                'confidence':confidence,'reason':reason,'focus_tier':focus,
                'suggestion':'Ôn lý thuyết → xem ví dụ → luyện bài theo mức độ → kiểm tra lại',
                'completed':topic_id in completed})
    # Priority: unfinished subjects with multiple verified answers and lower
    # mastery, but a low-confidence single answer cannot dominate the plan.
    recommendations.sort(key=lambda x:(x['completed'],x['observations']<3,
                                       x['estimated_mastery'],-x['observations']))
    return {'grade':grade,'recommendations':recommendations if include_all else recommendations[:6],
            'topics_assessed':len(recommendations),'training_events':total_events,
            'trained_answers':sum(int(x['observations']) for x in rows),
            'unique_question_evidence':len(effective),
            'model':'bkt_v23_plus_online_logistic_v24',
            'online_training':learner_online.public_report(fitted_predictor),
            'training_policy':'Chỉ câu được kiểm chứng độc lập và đã chấm trên máy chủ mới cập nhật ước lượng; bỏ qua chỉ ghi nhận.',
            'limitations':('Các tham số BKT vẫn là giả định kỹ thuật, chưa hiệu chuẩn trên dữ liệu học sinh thật. '
                           'Kết quả không phải kết luận năng lực toàn diện, không phải mô hình ngôn ngữ tự huấn luyện.')}


@router.get('/tutor-plan/{grade}')
def tutor_adaptive_plan(grade:int,authorization:str|None=Header(default=None)):
    """Learner-specific next three topics, respecting official 3-topic gates.

    The online learner updates on every *unique verified answered item* in
    submit(). This endpoint consumes the resulting state, never trusts client
    claims of correctness, never unveils answer keys, and never bypasses the
    fixed placement test or the 25/30 rule.
    """
    user=student(authorization)
    if grade not in (10,11,12):raise HTTPException(422,'Lớp không hợp lệ')
    all_topics=[t for t in _data()[0] if t['grade']==grade]
    by_id={t['id']:t for t in all_topics}
    with db() as c:
        placement=c.execute("SELECT result_json FROM roadmap_v2_attempts "
            "WHERE user_id=? AND grade=? AND mode='fixed_placement' AND submitted_at IS NOT NULL "
            "ORDER BY submitted_at DESC LIMIT 1",(user,grade)).fetchone()
        paper=_active_fixed_paper(c,grade)
        done={r['topic_id']:int(r['best_score']) for r in c.execute(
            'SELECT topic_id,best_score FROM roadmap_v2_mastery WHERE user_id=? AND grade=? AND best_score>=25',
            (user,grade)).fetchall()}
    base={'grade':grade,'model':'bkt_v23_plus_online_logistic_v24',
          'calibrated':False,
          'notice':'Các ước lượng được cập nhật theo câu đã duyệt, nhưng chưa hiệu chuẩn thống kê trên học sinh thực tế.'}
    if not placement or not paper:
        return {**base,'status':'placement_required','current_stage':None,'topics':[],
                'message':'Chưa có đề đầu vào cố định hợp lệ. Cần hoàn thành bài đầu vào đã kiểm chứng trước khi mở lộ trình.'}
    result=json.loads(placement['result_json'])
    if (not result.get('diagnostic_completeness',{}).get('content_coverage_complete')
            or result.get('fixed_paper_hash')!=paper['paper_hash']
            or not _paper_valid_now(grade,paper)):
        return {**base,'status':'placement_not_validated','current_stage':None,'topics':[],
                'message':'Đề đầu vào chưa đủ nội dung đã duyệt hoặc đã bị thay đổi; chưa thể dùng để mở lộ trình.'}
    ordering=result.get('roadmap_order') or []
    ordered=[by_id[tid] for tid in ordering if tid in by_id]
    used={t['id'] for t in ordered}
    ordered.extend(t for t in all_topics if t['id'] not in used)
    current=0
    for start in range(3,len(ordered),3):
        if all(t['id'] in done for t in ordered[start-3:start]):
            current=start
        else:
            break
    group=ordered[current:current+3]
    profile=tutor_profile(grade,authorization,True)
    estimates={t['topic_id']:t for t in profile['recommendations']}
    items=[]
    for pos,t in enumerate(group):
        tid=t['id'];r=estimates.get(tid)
        score=done.get(tid)
        n=r['observations'] if r else 0
        wrong=r['wrong'] if r else 0
        right=r['right'] if r else 0
        skipped=r['skipped'] if r else 0
        focus=(r['focus_tier'] if r and n>=3 else 'nền tảng')
        focus_basis='Bắt đầu từ nền tảng hoặc mức ít bằng chứng; không coi bỏ qua là sai.'
        fitted_ready=bool(r and r.get('online_prediction_ready'))
        if fitted_ready and r['online_focus_tier'] in DIFFICULTY:
            # Soft skill selection only; never influences the 25/30 gate.
            focus=r['online_focus_tier']
            focus_basis='Mức luyện gợi ý bởi mô hình dự đoán chưa hiệu chuẩn.'
        # A demonstrated error pattern is more actionable than a speculative
        # probability. Use one observation per distinct approved answered item.
        observed=(r or {}).get('observed_by_tier',{})
        weak=[(tier,details) for tier,details in observed.items()
              if details['answered']>=2 and details['wrong']>=1]
        if weak:
            weak.sort(key=lambda x:(-x[1]['wrong']/x[1]['answered'],
                                    -x[1]['wrong'],DIFFICULTY.index(x[0])))
            focus,detail=weak[0]
            focus_basis=(f'{detail["wrong"]}/{detail["answered"]} câu đã được duyệt '
                         f'ở mức {focus} trả lời sai. Đây là tín hiệu cần luyện thêm, '
                         'chưa phải kết luận năng lực.')
        if score is not None:
            action='review_or_advance'
            reason='Đã vượt bài kiểm tra chủ đề với ít nhất 25/30; có thể ôn lại hoặc học chủ đề còn lại.'
        elif n<3:
            action='gather_evidence'
            reason=(f'Mới có {n} câu trả lời được kiểm chứng. Ưu tiên ví dụ nền tảng và bài ngắn để đánh giá thêm.'
                    if n else 'Chưa có câu đã trả lời được kiểm chứng. Nên bắt đầu từ lý thuyết và bài luyện nền tảng.')
        elif wrong>right:
            action='remediate'
            reason=f'{wrong}/{right+wrong} câu đã kiểm chứng trả lời sai. Cần ôn phần {focus}, luyện lại bằng câu khác.'
        else:
            action='practice_and_check'
            reason=f'{right}/{right+wrong} câu đã kiểm chứng làm đúng. Tiếp tục luyện và kiểm tra mức {focus}.'
        items.append({'topic_id':tid,'title':t['title'],'grade':grade,
                      'completed':score is not None,'best_score':score,
                      'action':action,'reason':reason,'focus_tier':focus,
                      'focus_basis':focus_basis,
                      'verified_answered':n,'correct':right,'wrong':wrong,'skipped':skipped,
                      'mastery_estimate':(r['estimated_mastery'] if r and n>=3 else None),
                      'confidence':(r['confidence'] if r else 'chưa có bằng chứng'),
                      'online_prediction_ready':fitted_ready,
                      'predicted_correct_by_tier':(r['next_answer_prediction'] if fitted_ready else {}),
                      'learning_steps':[
                        {'kind':'theory','label':'Đọc lý thuyết và ví dụ phù hợp'},
                        {'kind':'video','label':'Xem bài giảng và ghi chú điểm chưa rõ'},
                        {'kind':'practice','label':f'Luyện câu mới ở mức {focus}'},
                        {'kind':'reflection','label':'Xem giải thích các bước sai và thử lại'},
                        {'kind':'exam','label':'Kiểm tra 30 câu; đạt 25/30 để hoàn thành'}],
                      'learning_url':'learn.html?grade='+str(grade)+'&topic='+tid})
    # Prioritize demonstrated weakness, with an explicit insufficient-evidence
    # bucket. Do not move topics between stages or unlock a fourth topic.
    def priority(item):
        if item['completed']:return (3,0)
        if item['verified_answered']<3:return (1,0)
        return (0, -(item['wrong']/max(1,item['correct']+item['wrong'])))
    items.sort(key=priority)
    remaining=sum(not x['completed'] for x in items)
    return {**base,'status':'ready','current_stage':current//3+1,
            'total_stages':(len(ordered)+2)//3,
            'completed_topics':len(done),'stage_remaining':remaining,
            'unlock_condition':'Chỉ mở nhóm tiếp theo khi cả 3 chủ đề đạt >=25/30.',
            'topics':items,'next_topic':next((x['topic_id'] for x in items if not x['completed']),None),
            'training_events':profile['training_events'],
            'trained_predictor':profile['online_training'],
            'trained_answers':profile['trained_answers'],
            'unique_question_evidence':profile['unique_question_evidence'],
            'personalization_policy':'Cập nhật sau mỗi lần nộp bài; chỉ học từ câu đã duyệt và lần trả lời đầu tiên.'}


@router.get('/tutor-data/{grade}')
def tutor_training_data(grade:int,authorization:str|None=Header(default=None)):
    """Allow a logged-in learner to export only their own anonymized training evidence."""
    user=student(authorization)
    if grade not in (10,11,12):raise HTTPException(422,'Lớp không hợp lệ')
    with db() as c:
        total=c.execute('SELECT COUNT(*) FROM roadmap_v2_learning_events WHERE user_id=? AND grade=?',(user,grade)).fetchone()[0]
        events=c.execute('SELECT topic_id,tier,verdict,created_at FROM roadmap_v2_learning_events WHERE user_id=? AND grade=? ORDER BY created_at DESC LIMIT 2500',(user,grade)).fetchall()
        skills=c.execute('SELECT topic_id,tier,mastery,observations,updated_at FROM roadmap_v2_skill_state WHERE user_id=? AND grade=? ORDER BY topic_id,tier',(user,grade)).fetchall()
        fitted_predictor=learner_online.ensure(c,user,grade)
        c.commit()
    return {'grade':grade,'online_training':learner_online.public_report(fitted_predictor),
            'total_events':total,'exported_events':len(events),
            'model':'incremental_bayesian_knowledge_tracing_v23',
            'trained_answers':sum(int(r['observations']) for r in skills),
            'events':[dict(e) for e in events],
            'skill_state':[{'topic_id':r['topic_id'],'tier':r['tier'],
                            'estimated_mastery':round(float(r['mastery']),4),
                            'observations':r['observations'],'updated_at':r['updated_at']} for r in skills],
            'policy':'Chỉ kết quả câu đã được duyệt. Không xuất câu hỏi, đáp án, định danh người dùng hay dữ liệu người khác.',
            'note':('Bản xuất giới hạn 2500 sự kiện gần nhất; dữ liệu đầy đủ được lưu trong SQLite của tài khoản. '
                    'Ước lượng xác suất chưa được hiệu chuẩn trên nhóm học sinh đại diện.') }


@router.post('/tutor/retrain/{grade}')
def tutor_retrain(grade:int,authorization:str|None=Header(default=None)):
    """Recreate this student's online weights from their verified evidence only.

    This also allows backfilling older V23 profiles and testing reproducibility.
    Never changes grades, placement, unlock status or other learners' data.
    """
    user=student(authorization)
    if grade not in (10,11,12):raise HTTPException(422,'Lớp không hợp lệ')
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        predictor=learner_online.rebuild(c,user,grade)
        c.commit()
    return {'grade':grade,'training':learner_online.public_report(predictor),
            'note':'Đã huấn luyện lại từ các câu đã duyệt, trả lời lần đầu; không học từ câu bỏ qua.'}
