"""Mutation/regeneration/corpus tests for V135 research quarantine."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'V135_RESEARCH'

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 return mod

gen=load('v135_source',ROOT/'V135_RESEARCH_generate.py')
audit=load('v135_gate',D/'audit.py')

class QualityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.forms=list(audit.read(D/'V135_CANDIDATE_METHODS.jsonl'))
  cls.qs=list(audit.read(D/'V135_VERIFIED_QUESTIONS.jsonl'))
  cls.catalog=json.loads((ROOT/'backend/question_factory/catalog_150.json').read_text(encoding='utf8'))
  cls.recomputed={gen.question(j,i)['id']:gen.question(j,i) for j in range(13) for i in range(10)}
 def run_gate(self,forms=None,qs=None):
  return audit.check(forms if forms is not None else self.forms,qs if qs is not None else self.qs,self.catalog,source_regeneration=self.recomputed)[0]
 def test_all_130_oracles_recomputed(self):
  self.assertEqual(len(self.qs),130)
  self.assertEqual({q['id']:q for q in self.qs},self.recomputed)
 def test_full_release_audit(self):
  r=audit.run();self.assertEqual(r['fatal_errors'],[]);self.assertEqual(r['prior_question_records_scanned'],302513);self.assertEqual(r['historical_normalized_duplicate_occurrences'],1)
 def test_canonical_catalog(self):self.assertFalse(self.run_gate())
 def test_wrong_answer_detected(self):
  qs=copy.deepcopy(self.qs);qs[0]['answer']='-999'
  self.assertTrue(self.run_gate(qs=qs))
 def test_both_answer_and_checker_modified_detected(self):
  qs=copy.deepcopy(self.qs);qs[0]['answer']=qs[0]['independent_check']='-999'
  self.assertTrue(any('regeneration' in e for e in self.run_gate(qs=qs)))
 def test_missing_exercise_detected(self):
  self.assertTrue(any('ten exercises' in e for e in self.run_gate(qs=self.qs[1:])))
 def test_wrong_topic_detected(self):
  qs=copy.deepcopy(self.qs);qs[0]['topic']='fake'
  self.assertTrue(any('wrong topic' in e for e in self.run_gate(qs=qs)))
 def test_duplicate_question_detected(self):
  qs=copy.deepcopy(self.qs);qs[1]['question']=qs[0]['question']
  self.assertTrue(any('duplicate stem' in e for e in self.run_gate(qs=qs)))
 def test_wrong_grade_detected(self):
  forms=copy.deepcopy(self.forms);forms[0]['grade']=12
  self.assertTrue(any('wrong topic/grade' in e for e in self.run_gate(forms=forms)))
 def test_publication_leak_detected(self):
  qs=copy.deepcopy(self.qs);qs[0]['published']=True
  self.assertTrue(any('publication' in e for e in self.run_gate(qs=qs)))
 def test_false_method_certification_detected(self):
  forms=copy.deepcopy(self.forms);forms[0]['independence_certified']=True
  self.assertTrue(any('certification leak' in e for e in self.run_gate(forms=forms)))
 def test_source_regeneration_does_not_modify_banks(self):
  self.assertTrue(all(q['published'] is False for q in self.qs))
  self.assertTrue(all(m['published'] is False for m in self.forms))
 def test_ten_different_questions_each_method(self):
  for m in self.forms:
   qs=[q for q in self.qs if q['method_id']==m['method_id']]
   self.assertEqual(len(set(q['question'] for q in qs)),10)

if __name__=='__main__':unittest.main()
