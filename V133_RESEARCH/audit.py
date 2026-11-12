from pathlib import Path
from collections import Counter
from importlib.machinery import SourceFileLoader
import json,re,unittest
import sympy as sp
ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'V133_RESEARCH'
def load(p):
 if not p.exists():return []
 with p.open(encoding='utf-8') as f:return [json.loads(l) for l in f if l.strip()]
def norm(t):return re.sub(r'\s+',' ',t.casefold().strip())
def verify():
 from importlib.util import spec_from_file_location,module_from_spec
 spec=spec_from_file_location('v133gen',ROOT/'V133_RESEARCH_generate.py');m=module_from_spec(spec);spec.loader.exec_module(m)
 forms=load(D/'V133_CANDIDATE_METHODS.jsonl');qs=load(D/'V133_VERIFIED_QUESTIONS.jsonl')
 errors=[];counter=Counter(q['method_id'] for q in qs)
 for i,form in enumerate(forms):
  if counter[form['method_id']]!=10:errors.append('question count '+form['method_id'])
  if form['published'] or form['independence_certified']:errors.append('unreviewed publication')
 for j in range(len(forms)):
  for i in range(10):
   expected=m.make(j,i)
   stored=next((q for q in qs if q['id']==expected['id']),None)
   if stored is None or stored!=expected:errors.append('incorrect generated payload '+expected['id'])
   elif sp.simplify(sp.sympify(stored['answer'])-sp.sympify(stored['independent_check']))!=0:errors.append('answer mismatch '+expected['id'])
 for q in qs:
  if q['published'] or q['independence_certified'] or q['review_status']!='pending-expert-review':errors.append('review bypass '+q['id'])
  if len(q['solution'])<65:errors.append('solution too short '+q['id'])
  if q['topic']!=next(f['topic'] for f in forms if f['method_id']==q['method_id']):errors.append('topic mismatch '+q['id'])
 prior={};inputs=[ROOT/'V123_RESEARCH/V123_10500_WORKED_QUESTIONS.jsonl',ROOT/'V131_RESEARCH/V131_VERIFIED_QUESTIONS.jsonl',ROOT/'V132_RESEARCH/V132_VERIFIED_QUESTIONS.jsonl']
 for p in inputs:
  for q in load(p):
   stem=q.get('question') or q.get('stem') or ''
   if stem:prior[norm(stem)]=True
 duplicate=[q['id'] for q in qs if norm(q['question']) in prior]
 if duplicate:errors+=['exact duplicate '+d for d in duplicate]
 if len(set(norm(q['question']) for q in qs))!=len(qs):errors.append('internal exact duplicate')
 res=dict(version='V133',new_candidate_methods=len(forms),new_questions=len(qs),answer_checks_matching=len(qs)-len([e for e in errors if e.startswith('incorrect') or e.startswith('answer')]),new_certified_independent_methods=0,prior_records_indexed=len(prior),normalized_exact_duplicate_hits=len(duplicate),errors=errors,published_questions=0,semantic_method_uniqueness='NOT CERTIFIED',full_stack_regression='NOT RUN',answer_diversity_by_method={fid:len(set(q['answer'] for q in qs if q['method_id']==fid)) for fid in counter})
 (D/'V133_RESULTS.json').write_text(json.dumps(res,indent=2,ensure_ascii=False),encoding='utf-8')
 return res
class QA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=verify()
 def test_no_errors(self):self.assertEqual(self.data['errors'],[])
 def test_new_questions(self):self.assertEqual(self.data['new_questions'],120)
 def test_new_candidates(self):self.assertEqual(self.data['new_candidate_methods'],12)
 def test_not_certified(self):self.assertEqual(self.data['new_certified_independent_methods'],0)
 def test_not_published(self):self.assertEqual(self.data['published_questions'],0)
 def test_old_exact_collision(self):self.assertEqual(self.data['normalized_exact_duplicate_hits'],0)
 def test_math_arithmetic(self):self.assertEqual(self.data['answer_checks_matching'],120)
 def test_tamper_detected(self):
  z=load(D/'V133_VERIFIED_QUESTIONS.jsonl')[0].copy();z['answer']='100000000'
  self.assertNotEqual(sp.simplify(sp.sympify(z['answer'])-sp.sympify(z['independent_check'])),0)
 def test_per_method_10(self):
  counts=Counter(q['method_id'] for q in load(D/'V133_VERIFIED_QUESTIONS.jsonl'))
  self.assertEqual(set(counts.values()),{10})
 def test_no_id_collision(self):
  q=load(D/'V133_VERIFIED_QUESTIONS.jsonl');self.assertEqual(len({v['id'] for v in q}),len(q))
if __name__=='__main__':unittest.main()
