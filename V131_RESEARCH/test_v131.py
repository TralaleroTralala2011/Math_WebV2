import importlib.util, json, pathlib, unittest, collections
BASE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v131_gen', BASE/'generate.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
class V131Test(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.forms,cls.questions=g.build()
 def test_fifteen_methods(self):self.assertEqual(len(self.forms),15)
 def test_ten_per_method(self):self.assertEqual(set(collections.Counter(q['method_id'] for q in self.questions).values()),{10})
 def test_150_questions(self):self.assertEqual(len(self.questions),150)
 def test_exact_duplicate_stems(self):self.assertEqual(len({q['question'] for q in self.questions}),150)
 def test_all_answers_independently_checked(self):
  for j in range(15):
   for i in range(10):
    q=g.make(j,i)
    self.assertEqual(q['answer'],q['independent_check'])
 def test_unpublished(self):self.assertTrue(all(not q['published'] for q in self.questions))
 def test_pending_expert_review(self):self.assertTrue(all(f['review_status']=='pending-expert-review' and not f['independence_certified'] for f in self.forms))
 def test_solving_text_present(self):self.assertTrue(all(len(q['solution'])>30 for q in self.questions))
 def test_topic_grade_match(self):
  for m in self.forms:
   self.assertEqual(next(z for z in g.METHODS if z[0]==m['topic'])[2],m['grade'])
 def test_detect_deliberate_wrong_answer(self):
  q=dict(self.questions[0]);q['answer']='123456789'
  self.assertNotEqual(q['answer'],q['independent_check'])
if __name__=='__main__':unittest.main()
