import unittest
from v129_integrity_gate import audit

F={'family':'f','source_family':'core','topic':'t','published':False,'independence_certified':False}
def question(i):
 return {'family':'f','topic_id':'t','stem':f'Question {i}','answer':str(i),'solution':f'Solution {i}','question_type':'tra_loi_ngan','method_signature':'core','fingerprint':str(i),'independence_certified':False,'verification':{'publication_blocked':True}}
class GateTests(unittest.TestCase):
 def test_valid_family(self):self.assertEqual(audit([F],[question(i) for i in range(10)])['status'],'PASS_STRUCTURE_ONLY')
 def test_duplicate(self):
  q=[question(i) for i in range(10)];q[1]['stem']=q[0]['stem'];self.assertIn('repeated_stem_within_family',audit([F],q)['issues'])
 def test_wrong_topic(self):
  q=[question(i) for i in range(10)];q[1]['topic_id']='wrong';self.assertIn('topic_mismatch',audit([F],q)['issues'])
 def test_publication(self):
  q=[question(i) for i in range(10)];q[1]['verification']['publication_blocked']=False;self.assertIn('unsafe_publication',audit([F],q)['issues'])
 def test_missing(self):self.assertIn('family_not_ten_questions',audit([F],[question(0)])['issues'])
 def test_orphan(self):self.assertIn('orphan_question',audit([], [question(0)])['issues'])
if __name__=='__main__':unittest.main()
