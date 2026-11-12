"""V158 research batch regression tests: never mark forms independent."""
import unittest, json, sys
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import build
P=Path(__file__).parent
class ResearchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  build.main()
  cls.rows=[json.loads(x) for x in (P/'V158_VERIFIED_ANSWERS_PENDING_REVIEW.jsonl').read_text().splitlines()]
  cls.methods=[json.loads(x) for x in (P/'V158_CANDIDATE_METHODS.jsonl').read_text().splitlines()]
 def test_candidate_status(self):
  self.assertEqual(len(self.methods),6)
  self.assertTrue(all(x['review_status']=='pending-expert-review' and not x['independence_certified'] and not x['published'] for x in self.rows+self.methods))
 def test_count(self):
  self.assertEqual(len(self.rows),60)
  self.assertEqual(Counter(x['format'] for x in self.rows),{'trac_nghiem':42,'tu_luan':12,'dung_sai':6})
  self.assertEqual(Counter(x['method_id'] for x in self.rows),{x['method_id']:10 for x in self.methods})
 def test_unique(self):
  for field in ('id','question'):
   self.assertEqual(len({x[field] for x in self.rows}),60)
 def test_oracles(self):
  for row in self.rows:
   kind=row['method_id'].removeprefix('v158_');i=int(row['id'][-2:])
   q,answer,solution,params,oracle=build.mk(kind,i)
   self.assertEqual(build.val(answer),row['canonical_answer'])
   self.assertEqual(params,row['parameters'])
   self.assertTrue(row['answer_oracle_match'])
   self.assertTrue(row['solution'].strip())
 def test_multiple_choice(self):
  for x in self.rows:
   if x['format']!='trac_nghiem':continue
   self.assertEqual(set(x['options']),set('ABCD'))
   self.assertEqual(len(set(x['options'].values())),4)
   self.assertEqual(x['options'][x['answer']],x['canonical_answer'])
 def test_true_false(self):
  rows=[x for x in self.rows if x['format']=='dung_sai']
  self.assertEqual(Counter(x['answer'] for x in rows),{'Đúng':3,'Sai':3})
if __name__=='__main__':unittest.main()
