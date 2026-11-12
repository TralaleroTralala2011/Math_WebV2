import importlib.util
import pathlib
import unittest

p = pathlib.Path(__file__).with_name('v122_independent_audit.py')
spec = importlib.util.spec_from_file_location('v122_audit',p)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class AuditTests(unittest.TestCase):
    def test_all_records(self):
        self.assertEqual(audit.audit()['issues_total'],0)
    def test_coverage(self):
        r=audit.audit()
        self.assertEqual((r['topics'],r['families'],r['questions']),(150,300,3000))
    def test_independent_oracle(self):
        qs=audit.load(audit.DATA)
        tested=[q for q in qs if audit.independent_oracle(q) is not None]
        self.assertEqual(len(tested),20)
        self.assertTrue(all(str(audit.independent_oracle(q))==str(q['numeric_result']) for q in tested))
    def test_oracle_detects_wrong_result(self):
        q=next(q for q in audit.load(audit.DATA) if audit.independent_oracle(q) is not None)
        altered=dict(q,numeric_result=str(int(q['numeric_result'])+1))
        self.assertNotEqual(str(audit.independent_oracle(altered)),altered['numeric_result'])
    def test_publication_guard(self):
        self.assertTrue(all(q['verification']['publication_blocked'] for q in audit.load(audit.DATA)))

if __name__=='__main__': unittest.main()
