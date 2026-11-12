import unittest
from fractions import Fraction
from question_factory.v127_independent_oracle import verify
class TestV127(unittest.TestCase):
 def sample(self,family,result):
  return {'topic_id':'menh_de_tap_hop','family':'v123_'+family+'_menh_de_tap_hop','stem':('A. Trong các số nguyên từ 1 đến 10, có bao nhiêu số chia hết cho 2 nhưng không chia hết cho 3? '
  'B. Trong các số nguyên từ 1 đến 12, có bao nhiêu số chia hết cho 3 nhưng không chia hết cho 4? '
  'C. Trong các số nguyên từ 1 đến 20, có bao nhiêu số chia hết cho 4 nhưng không chia hết cho 5? '
  'D. Trong các số nguyên từ 1 đến 30, có bao nhiêu số chia hết cho 5 nhưng không chia hết cho 6?'), 'numeric_result':str(result)}
 def test_seven_operations(self):
  vals=[4,3,4,5]
  cases={'delta':-1,'total':11,'maximum':4,'median':4,'curvature':2,'threshold':1,'variance':Fraction(2,9)}
  for f,r in cases.items():
   with self.subTest(f=f):self.assertEqual(verify(self.sample(f,r))['status'],'pass')
 def test_tampered_answer_detected(self):
  self.assertEqual(verify(self.sample('total',999))['status'],'mismatch')
 def test_unparseable_rejected(self):
  q=self.sample('total',11);q['stem']='bad';self.assertEqual(verify(q)['status'],'unparsed-scenarios')
 def test_unsupported_not_certified(self):
  q=self.sample('total',11);q['topic_id']='other';self.assertEqual(verify(q)['status'],'unsupported-topic')
if __name__=='__main__':unittest.main()
