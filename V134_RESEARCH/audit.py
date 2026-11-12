"""Quality gate for V134 research candidates; no semantic novelty certification."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import importlib.util
import json
import re
import unicodedata

ROOT=Path(__file__).resolve().parent.parent
RESEARCH=ROOT/'V134_RESEARCH'


def rows(path):
 with path.open(encoding='utf8') as f:
  for line in f:
   if line.strip():yield json.loads(line)


def normalize(stem):
 text=unicodedata.normalize('NFKC',stem).casefold()
 text=text.translate(str.maketrans({'−':'-','–':'-','—':'-','²':'2','³':'3'}))
 return re.sub(r'\s+',' ',text.strip())


def older_stems():
 files=[
   ROOT/'V121_RESEARCH/V121_3000_NEW_QUESTIONS.jsonl',
   ROOT/'V123_RESEARCH/V123_10500_WORKED_QUESTIONS.jsonl',
   ROOT/'V131_RESEARCH/V131_VERIFIED_QUESTIONS.jsonl',
   ROOT/'V132_RESEARCH/V132_VERIFIED_QUESTIONS.jsonl',
   ROOT/'V133_RESEARCH/V133_VERIFIED_QUESTIONS.jsonl',
 ]
 known=set();count=0;missing=[]
 for path in files:
  if not path.is_file():
   missing.append(str(path.relative_to(ROOT)));continue
  for q in rows(path):
   stem=q.get('question') or q.get('question_text') or q.get('stem') or q.get('problem')
   if stem:known.add(normalize(stem))
   count+=1
 return known,count,missing


def check(forms,questions,catalog,known=None):
 errors=[];warnings=[]
 official={c['id']:c['grade'] for c in catalog}
 fids=[m['method_id'] for m in forms]
 qids=[q['id'] for q in questions]
 freq=Counter(q.get('method_id') for q in questions)
 if len(fids)!=len(set(fids)):errors.append('duplicate form IDs')
 if len(qids)!=len(set(qids)):errors.append('duplicate question IDs')
 seen=set()
 for m in forms:
  mid=m['method_id'];topic=m.get('topic')
  if official.get(topic)!=m.get('grade'):errors.append(f'{mid} not in curriculum/grade mismatch: {topic}')
  if m.get('questions_expected')!=10 or freq[mid]!=10:errors.append(f'{mid} has {freq[mid]} items, expected 10')
  if m.get('published') or m.get('independence_certified') or m.get('review_status')!='pending-expert-review':errors.append(f'{mid} incorrectly published/certified')
 for q in questions:
  qid=q.get('id','');topic=q.get('topic')
  if official.get(topic)!=q.get('grade'):errors.append(f'{qid} incorrect curriculum topic')
  if q.get('method_id') not in fids:errors.append(f'{qid} references absent method')
  if q.get('published') or q.get('independence_certified') or q.get('review_status')!='pending-expert-review':errors.append(f'{qid} incorrectly published/certified')
  if not q.get('solution') or len(q['solution'].strip())<60:errors.append(f'{qid} missing/short solution')
  if not q.get('answer') or not q.get('independent_check'):errors.append(f'{qid} missing answer or checker')
  if q.get('answer')!=q.get('independent_check'):errors.append(f'{qid} answer/check mismatch')
  stem=normalize(q.get('question',''))
  if not stem:errors.append(f'{qid} empty question')
  if stem in seen:errors.append(f'{qid} normalized duplicate within V134')
  seen.add(stem)
  if known is not None and stem in known:errors.append(f'{qid} exact normalized collision with previous releases')
 for m in forms:
  qset=[q for q in questions if q.get('method_id')==m['method_id']]
  if any(q['topic']!=m['topic'] or q['grade']!=m['grade'] for q in qset):errors.append(f'{m["method_id"]} question topic/grade disagrees with form')
  n=len({q['answer'] for q in qset})
  if n<5:warnings.append(f'{m["method_id"]}: only {n} unique answers among 10')
 return errors,warnings


def run():
 forms=list(rows(RESEARCH/'V134_CANDIDATE_METHODS.jsonl'))
 questions=list(rows(RESEARCH/'V134_VERIFIED_QUESTIONS.jsonl'))
 catalog=json.loads((ROOT/'backend/question_factory/catalog_150.json').read_text(encoding='utf8'))
 known,prior_count,missing=older_stems()
 errors,warnings=check(forms,questions,catalog,known)
 if missing:errors.append('prior banks missing: '+', '.join(missing))
 # Explicit check also covers the previously incorrect curriculum codes in V132 and V133.
 correction_errors=[]
 for v in ('V131','V132','V133'):
  old_forms=list(rows(ROOT/f'{v}_RESEARCH/{v}_CANDIDATE_METHODS.jsonl'))
  old_qs=list(rows(ROOT/f'{v}_RESEARCH/{v}_VERIFIED_QUESTIONS.jsonl'))
  e,_=check(old_forms,old_qs,catalog,known=None)
  # Older batches differ in their solution length; this gate is about curricula and statuses only
  correction_errors.extend(x for x in e if 'not in curriculum' in x or 'incorrect curriculum topic' in x or 'question topic/grade disagrees' in x or 'incorrectly published' in x or 'incorrectly' in x)
 errors+=correction_errors
 result={
  'version':'V134',
  'topic_catalog_count':len(catalog),
  'new_candidate_methods':len(forms),
  'new_questions':len(questions),
  'questions_mathematically_crosschecked_at_generation':sum(q['answer']==q['independent_check'] for q in questions),
  'new_independent_methods_certified':0,
  'published_questions':sum(q['published'] for q in questions),
  'prior_questions_scanned':prior_count,
  'unique_prior_normalized_stems':len(known),
  'normalized_duplicate_hits':sum(normalize(q['question']) in known for q in questions),
  'curriculum_topic_repairs_in_previous_versions':{'V132_methods':3,'V132_questions':30,'V133_methods':1,'V133_questions':10},
  'critical_errors':errors,
  'quality_warnings':warnings,
  'method_independence_and_global_semantic_duplicate_review':'NOT CERTIFIED',
  'full_end_to_end_regression':'NOT RUN',
  'publication_status':'RESEARCH_QUARANTINED'
 }
 (RESEARCH/'V134_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 return result

if __name__=='__main__':
 result=run();print(json.dumps(result,ensure_ascii=False,indent=2));
 if result['critical_errors']:raise SystemExit(1)
