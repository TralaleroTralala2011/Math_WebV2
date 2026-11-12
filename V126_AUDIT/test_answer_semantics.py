import unittest
from audit_answer_semantics import audit

class GateTests(unittest.TestCase):
    def base(self,**kw):
        return {'topic_id':'t','question_type':'tra_loi_ngan','answer':'3','numeric_result':'3',**kw}
    def test_direct_good(self): self.assertEqual(audit([self.base()])['issues_count'],0)
    def test_direct_bad(self): self.assertEqual(audit([self.base(answer='4')])['issues_count'],1)
    def test_true_false_good(self): self.assertEqual(audit([self.base(question_type='dung_sai',answer='Sai',truth=False,assertion_value='4')])['issues_count'],0)
    def test_true_false_bad(self): self.assertGreater(audit([self.base(question_type='dung_sai',answer='Đúng',truth=False,assertion_value='3')])['issues_count'],0)
    def test_mcq_good(self): self.assertEqual(audit([self.base(question_type='trac_nghiem',options=['1','2','3','4'],correct_index=2)])['issues_count'],0)
    def test_mcq_bad(self): self.assertGreater(audit([self.base(question_type='trac_nghiem',options=['1','2','3','3'],correct_index=2)])['issues_count'],0)

if __name__=='__main__':unittest.main()
