"""Focused V134 regression: independent math, curriculum, quarantine, malformed inputs."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'V134_RESEARCH'
spec=importlib.util.spec_from_file_location('v134gen',ROOT/'V134_RESEARCH_generate.py')
gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
spec2=importlib.util.spec_from_file_location('v134audit',D/'audit.py')
audit=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(audit)

class V134QualityGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.forms=list(audit.rows(D/'V134_CANDIDATE_METHODS.jsonl'))
  cls.qs=list(audit.rows(D/'V134_VERIFIED_QUESTIONS.jsonl'))
  cls.catalog=json.loads((ROOT/'backend/question_factory/catalog_150.json').read_text('utf8'))
  cls.known,cls.prior_count,cls.missing=audit.older_stems()
 def test_180_oracle_recomputed(self):
  for j in range(18):
   for i in range(10):
    with self.subTest(form=j,item=i):
     q=gen.task(j,i)
     old=self.qs[j*10+i]
     self.assertEqual(q,old)
 def test_catalog_and_all_question_counts(self):
  errors,_=audit.check(self.forms,self.qs,self.catalog,self.known)
  self.assertFalse(errors,errors[:8]);self.assertFalse(self.missing)
  self.assertEqual(self.prior_count,13870)
 def test_incorrect_topic_detected(self):
  qs=copy.deepcopy(self.qs);qs[0]['topic']='fake_topic'
  errors,_=audit.check(self.forms,qs,self.catalog)
  self.assertTrue(any('incorrect curriculum topic' in e for e in errors))
 def test_wrong_grade_detected(self):
  forms=copy.deepcopy(self.forms);forms[0]['grade']=12
  errors,_=audit.check(forms,self.qs,self.catalog)
  self.assertTrue(any('grade mismatch' in e for e in errors))
 def test_tampered_answer_detected(self):
  qs=copy.deepcopy(self.qs);qs[0]['answer']='999999'
  errors,_=audit.check(self.forms,qs,self.catalog)
  self.assertTrue(any('answer/check mismatch' in e for e in errors))
 def test_duplicate_question_detected(self):
  qs=copy.deepcopy(self.qs);qs[1]['question']=qs[0]['question']
  errors,_=audit.check(self.forms,qs,self.catalog)
  self.assertTrue(any('normalized duplicate' in e for e in errors))
 def test_leakage_detected(self):
  qs=copy.deepcopy(self.qs);qs[2]['published']=True
  errors,_=audit.check(self.forms,qs,self.catalog)
  self.assertTrue(any('incorrectly published' in e for e in errors))
 def test_disallowed_certification_detected(self):
  forms=copy.deepcopy(self.forms);forms[0]['independence_certified']=True
  errors,_=audit.check(forms,self.qs,self.catalog)
  self.assertTrue(any('incorrectly published/certified' in e for e in errors))
 def test_earlier_topics_repaired(self):
  official={c['id']:c['grade'] for c in self.catalog}
  for version in ('V131','V132','V133'):
   for tag in ('CANDIDATE_METHODS','VERIFIED_QUESTIONS'):
    for obj in audit.rows(ROOT/f'{version}_RESEARCH/{version}_{tag}.jsonl'):
     self.assertEqual(official[obj['topic']],obj['grade'])
 def test_no_unreviewed_publications(self):
  self.assertEqual(sum(q['published'] or q['independence_certified'] for q in self.qs),0)
  self.assertEqual(sum(m['published'] or m['independence_certified'] for m in self.forms),0)
 def test_number_variants_are_not_new_methods(self):
  self.assertEqual(len({z['method_id'] for z in self.qs}),18)
  self.assertEqual(len(self.qs),180)

if __name__=='__main__':unittest.main()
