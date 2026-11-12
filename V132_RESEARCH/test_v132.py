import unittest, importlib.util, pathlib, collections, json
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v132_gen',ROOT.parent/'V132_RESEARCH_generate.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  g.run();cls.forms=[json.loads(s) for s in (ROOT/'V132_CANDIDATE_METHODS.jsonl').read_text().splitlines()];cls.rows=[json.loads(s) for s in (ROOT/'V132_VERIFIED_QUESTIONS.jsonl').read_text().splitlines()]
 def test_ten_distinct_candidate_methods(self):self.assertEqual(len({f['method_id'] for f in self.forms}),10)
 def test_one_hundred_questions(self):self.assertEqual(len(self.rows),100)
 def test_ten_per_method(self):self.assertEqual(set(collections.Counter(q['method_id'] for q in self.rows).values()),{10})
 def test_unique_stems(self):self.assertEqual(len(set(q['question'] for q in self.rows)),len(self.rows))
 def test_checked_answer(self):self.assertTrue(all(q['answer']==q['independent_check'] for q in self.rows))
 def test_recalculate_all_questions(self):
  for j in range(10):
   for i in range(10):self.assertEqual(self.rows[j*10+i]['answer'],g.build(j,i)['answer'])
 def test_unpublished(self):self.assertTrue(all(not q['published'] for q in self.rows))
 def test_uncertified(self):self.assertTrue(all(f['independence_certified'] is False for f in self.forms))
 def test_solutions(self):self.assertTrue(all(len(q['solution'])>=60 for q in self.rows))
 def test_topics(self):self.assertTrue(all(q['topic']==self.forms[j]['topic'] for j in range(10) for q in self.rows[j*10:j*10+10]))
 def test_wrong_answer_detection(self):
  bad=dict(self.rows[0]);bad['answer']='definitely_worse';self.assertNotEqual(bad['answer'],bad['independent_check'])
if __name__=='__main__':unittest.main()
