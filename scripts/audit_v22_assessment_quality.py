"""Offline structural audit of assessment; NOT an independent maths/pedagogy review."""
from __future__ import annotations
import collections, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'learn-assets'/'assessment-matrix-questions.json'
TOPICS=ROOT/'learn-assets'/'topics.json'
SLOTS=[('nen_tang','ly_thuyet','trac_nghiem'),('nen_tang','ly_thuyet','dung_sai'),('trung_cap','ly_thuyet','trac_nghiem'),('trung_cap','thuc_te','trac_nghiem'),('kho','ly_thuyet','dung_sai'),('kho','thuc_te','tra_loi_ngan')]

def audit():
    rows=json.loads(DATA.read_text(encoding='utf-8'))
    topics=json.loads(TOPICS.read_text(encoding='utf-8'))
    valid_topic={(int(x['grade']),x['id']) for x in topics}
    err=[];by=collections.defaultdict(list); ids=set();texts=set()
    for i,q in enumerate(rows):
        context=f'row {i+1} ({q.get("id")})'
        key=(q.get('grade'),q.get('topic_id'))
        if key not in valid_topic:err.append(context+': topic mismatch')
        by[key].append(q)
        if q.get('id') in ids:err.append(context+': duplicate ID')
        ids.add(q.get('id'))
        txt=re.sub(r'\s+',' ',q.get('question','').strip().casefold())
        if txt in texts:err.append(context+': duplicate normalized question')
        texts.add(txt)
        if not txt or not str(q.get('solution','')).strip():err.append(context+': blank question/solution')
        slot=q.get('slot')
        if not isinstance(slot,int) or not 1<=slot<=6:err.append(context+': invalid slot');continue
        if (q.get('difficulty'),q.get('context'),q.get('format'))!=SLOTS[slot-1]:err.append(context+': slot matrix mismatch')
        typ=q.get('format')
        if typ=='trac_nghiem':
            ch=q.get('choices',[]);ind=q.get('correct')
            if len(ch)!=4 or len({str(x).strip().casefold() for x in ch})!=4:err.append(context+': invalid MCQ choices')
            elif not isinstance(ind,int) or ind not in range(4) or ch[ind]!=q.get('answer'):err.append(context+': wrong MCQ answer index')
        elif typ=='dung_sai' and q.get('answer') not in ('true','false'):err.append(context+': invalid true/false answer')
        elif typ=='tra_loi_ngan' and not str(q.get('answer','')).strip():err.append(context+': blank short answer')
    for key in sorted(valid_topic):
        slots=collections.Counter(x.get('slot') for x in by.get(key,[]))
        if slots != collections.Counter({i:1 for i in range(1,7)}):err.append(f'{key}: does not have exactly slots 1..6')
    truth=collections.Counter(x['answer'] for x in rows if x.get('format')=='dung_sai')
    grades=collections.Counter(x.get('grade') for x in rows)
    report={
     'scope':'Structural and consistency audit only; NO independent mathematical or pedagogical certification',
     'total_questions':len(rows),'expected_questions':900,'covered_topics':len(by), 'curriculum_topics':len(valid_topic),
     'by_grade':dict(sorted(grades.items())),'formats':dict(collections.Counter(x.get('format') for x in rows)),
     'true_false_distribution':dict(truth),
     'warnings':['True/false answers are imbalanced. Do not invert answers without rewriting and verifying the propositions.','Difficulty and real-world relevance require independent subject-matter review.','30-question rounds cannot establish proficiency in all 150 topics.'],
     'structural_errors':err[:250], 'structural_error_count':len(err),
     'unreviewed_count':sum('independent' in str(q.get('review_status','')) or 'pending' in str(q.get('review_status','')) for q in rows),
    }
    return report
if __name__=='__main__':
    report=audit();print(json.dumps(report,ensure_ascii=False,indent=2));
    raise SystemExit(0 if report['structural_error_count']==0 else 1)
