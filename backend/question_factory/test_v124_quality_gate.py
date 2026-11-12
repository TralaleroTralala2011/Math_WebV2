import unittest
from question_factory.v124_quality_gate import count_direct, independent_check_delta
class QualityGateTests(unittest.TestCase):
    def test_direct_count(self): self.assertEqual(count_direct(82,4,5),16)
    def test_zero_range(self): self.assertEqual(count_direct(0,4,5),0)
    def test_delta_oracle(self):
        r={'family':'v123_delta_menh_de_tap_hop','stem':'Trong các số nguyên từ 1 đến 82, có bao nhiêu số chia hết cho 4 nhưng không chia hết cho 5? Trong các số nguyên từ 1 đến 153, có bao nhiêu số chia hết cho 5 nhưng không chia hết cho 6?', 'numeric_result':'9'}
        self.assertTrue(independent_check_delta(r))
        r['numeric_result']='10'
        self.assertFalse(independent_check_delta(r))
    def test_unrecognized_is_not_verified(self):
        self.assertIsNone(independent_check_delta({'family':'other','stem':'','numeric_result':'9'}))
if __name__=='__main__': unittest.main()
