import json
import tempfile
import unittest
from pathlib import Path
from question_factory.v125_quality_gate import audit, canonical_stem

class V125GateTests(unittest.TestCase):
    def run_audit(self, candidates, questions):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'c.jsonl',Path(d)/'q.jsonl'
            a.write_text(''.join(json.dumps(x)+'\n' for x in candidates),encoding='utf8')
            b.write_text(''.join(json.dumps(x)+'\n' for x in questions),encoding='utf8')
            return audit(a,b)
    def fixture(self):
        c=[{'family':'f','topic':'t','source_family':'base','published':False,'independence_certified':False}]
        q=[{'family':'f','stem':f'Question {i}','answer':str(i),'numeric_result':str(i),'solution':'Verified solution','independence_certified':False} for i in range(10)]
        return c,q
    def test_normalization(self):
        self.assertEqual(canonical_stem(' A   B\n'),canonical_stem('a b'))
    def test_clean_structure(self):
        self.assertTrue(self.run_audit(*self.fixture())['structural_gate_pass'])
    def test_duplicate_text(self):
        c,q=self.fixture();q[1]['stem']=q[0]['stem'].upper()
        self.assertEqual(self.run_audit(c,q)['discrepancies']['duplicate_normalized_stems'],1)
    def test_missing_solution(self):
        c,q=self.fixture();q[0]['solution']=''
        self.assertFalse(self.run_audit(c,q)['structural_gate_pass'])
    def test_unreviewed_cannot_publish(self):
        c,q=self.fixture();c[0]['published']=True
        self.assertFalse(self.run_audit(c,q)['structural_gate_pass'])
    def test_wrong_count(self):
        c,q=self.fixture();q.pop()
        self.assertFalse(self.run_audit(c,q)['structural_gate_pass'])
    def test_no_auto_certification(self):
        self.assertFalse(self.run_audit(*self.fixture())['mathematical_independence_gate_pass'])
if __name__=='__main__':unittest.main()
