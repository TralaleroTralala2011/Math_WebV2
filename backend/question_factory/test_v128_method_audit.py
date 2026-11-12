import unittest,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from v128_method_audit import analyze
ZIP=Path(__file__).parents[1]/'MATH_WEB_GITHUB_READY_V127_INDEPENDENT_ENUMERATION_AUDIT.zip'
class AuditTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  project_root=Path(__file__).resolve().parents[2]
  # Prefer the exact historical archive, falling back to its preserved inputs.
  source=ZIP if ZIP.is_file() else project_root
  cls.r=analyze(source)
 def test_counts(self):self.assertEqual((self.r['forms'],self.r['questions'],self.r['topics']),(1050,10500,150))
 def test_exactly_ten_per_form(self):self.assertFalse(self.r['families_not_ten_questions'])
 def test_method_reuse(self):self.assertEqual(self.r['source_reuse_distribution'],{7:150})
 def test_review_safety(self):self.assertEqual(self.r['publication_and_review_flags'],{})
 def test_no_certification(self):self.assertEqual(self.r['certified_independent_forms'],0)
 def test_consistency(self):self.assertEqual(self.r['status'],'PASS')
if __name__=='__main__':unittest.main()
