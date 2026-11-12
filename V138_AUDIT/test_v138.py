import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_research_linkage_v137 import answer_equivalent
class Check(unittest.TestCase):
 def test_complex_equal(self): self.assertTrue(answer_equivalent('10*I*(-1 + I)','-10 - 10*I'))
 def test_incorrect(self): self.assertFalse(answer_equivalent('2+I','2-I'))
 def test_symbolic(self): self.assertTrue(answer_equivalent('(x+1)**2','x**2+2*x+1'))
 def test_unsupported(self): self.assertIsNone(answer_equivalent('văn bản không phân tích được','1'))
if __name__=='__main__':unittest.main()
