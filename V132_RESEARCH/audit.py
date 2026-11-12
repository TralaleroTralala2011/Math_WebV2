"""Independent structural/duplication audit. Does not certify pedagogical novelty."""
import collections, json, pathlib, re, importlib.util, hashlib
ROOT=pathlib.Path(__file__).resolve().parent.parent;D=ROOT/'V132_RESEARCH'
def readjsonl(p):
 with p.open(encoding='utf8') as f:
  for line in f:
   if line.strip():yield json.loads(line)
def normalize(s):return ' '.join(s.casefold().split())
def run():
 forms=list(readjsonl(D/'V132_CANDIDATE_METHODS.jsonl')); questions=list(readjsonl(D/'V132_VERIFIED_QUESTIONS.jsonl'))
 prior_paths=[ROOT/'V131_RESEARCH/V131_VERIFIED_QUESTIONS.jsonl',ROOT/'V123_RESEARCH/V123_10500_WORKED_QUESTIONS.jsonl', ROOT/'V121_RESEARCH/V121_3000_WORKED_QUESTIONS.jsonl']
 prior_counts={};known=set()
 for p in prior_paths:
  if not p.exists():continue
  n=0
  for row in readjsonl(p):
   stem=row.get('question') or row.get('question_text') or row.get('stem') or row.get('problem')
   if stem:known.add(normalize(stem))
   n+=1
  prior_counts[str(p.relative_to(ROOT))]=n
 hits=[q['id'] for q in questions if normalize(q['question']) in known]
 counts=collections.Counter(q['method_id'] for q in questions)
 answer_diversity={m['method_id']:len(set(q['answer'] for q in questions if q['method_id']==m['method_id'])) for m in forms}
 # Critical checks are reproducible, not semantic correctness certification
 flags=[]
 if hits:flags.append('exact-normalized overlap with prior data')
 if len({normalize(q['question']) for q in questions})!=len(questions):flags.append('within-batch duplicate questions')
 if set(counts.values())!={10} or len(counts)!=len(forms):flags.append('incorrect number of questions per method')
 if any(q['answer']!=q['independent_check'] for q in questions):flags.append('answer differs from independent check')
 if any(q.get('published') or q.get('review_status')!='pending-expert-review' for q in questions):flags.append('unreviewed question published')
 if any(f.get('independence_certified') or f.get('published') for f in forms):flags.append('unreviewed method certified or published')
 # quality warning: multiple questions share patterns, not a novelty proof
 alerts=[{'method_id':mid,'reason':'same answer repeated in at least 8/10 items','distinct_answers':n} for mid,n in answer_diversity.items() if n<=2]
 result={'version':'V132','new_candidate_methods':len(forms),'new_questions':len(questions),'math_answer_checks_matching':sum(q['answer']==q['independent_check'] for q in questions),'certified_independent_methods':0,'normalized_exact_duplicate_hits':len(hits),'prior_banks_scanned':prior_counts,'critical_flags':flags,'answer_diversity_by_method':answer_diversity,'quality_alerts':alerts,'method_novelty_semantic_review':'NOT PERFORMED','full_backend_frontend_regression':'NOT PERFORMED','release_status':'RESEARCH_ONLY_PENDING_REVIEW'}
 (D/'V132_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':run()
