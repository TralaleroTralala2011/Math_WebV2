import json
import tempfile
import unittest
from pathlib import Path
from audit_research_method_collisions import audit

class CandidateIdentityTests(unittest.TestCase):
    def audit_items(self, items):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            folder = root / 'V149_RESEARCH'
            folder.mkdir()
            (folder / 'V149_CANDIDATE_METHODS.jsonl').write_text('\n'.join(json.dumps(x) for x in items), encoding='utf-8')
            return audit(root)

    def test_duplicate_id_across_methods_detected(self):
        result = self.audit_items([{'id':'same','topic':'T','method':'A'}, {'id':'same','topic':'T','method':'B'}])
        self.assertEqual(result['duplicate_candidate_id_groups'], 1)

    def test_missing_method_is_unsafe(self):
        result = self.audit_items([{'id':'x','topic':'T'}])
        self.assertEqual(result['invalid_or_unsafe_count'], 1)

    def test_missing_id_count_separate_from_certification(self):
        result = self.audit_items([{'topic':'T','method':'A'}])
        self.assertEqual(result['missing_candidate_ids'], 1)
        self.assertEqual(result['invalid_or_unsafe_count'], 0)

if __name__ == '__main__':
    unittest.main()
