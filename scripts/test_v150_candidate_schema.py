import json
import tempfile
import unittest
from pathlib import Path
from audit_research_method_collisions import audit

class CandidateSchemaTests(unittest.TestCase):
    def run_items(self, items):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'V150_RESEARCH'
            folder.mkdir()
            (folder / 'V150_CANDIDATE_METHODS.jsonl').write_text('\n'.join(json.dumps(i) for i in items), encoding='utf-8')
            return audit(Path(tmp))

    def test_signature_is_valid_candidate_identity(self):
        a = self.run_items([{'topic':'tap_hop','signature':'v121:alpha','skill':'dem boi'}])
        self.assertEqual(a['missing_candidate_ids'], 0)
        self.assertEqual(a['identity_source_counts']['signature'], 1)

    def test_duplicate_signature_is_detected(self):
        a = self.run_items([{'topic':'A','signature':'same','skill':'one'}, {'topic':'B','signature':'same','skill':'two'}])
        self.assertEqual(a['duplicate_candidate_id_groups'], 1)

    def test_explicit_id_takes_priority_over_signature(self):
        a = self.run_items([{'topic':'A','method_id':'x','signature':'old','skill':'one'}])
        self.assertEqual(a['identity_source_counts']['method_id'], 1)

    def test_shared_core_method_remains_uncertified(self):
        a = self.run_items([{'topic':'A','signature':'x','skill':'delta','shared_core_method':True,'independence_certified':False}])
        self.assertEqual(a['shared_core_method_candidates'], 1)
        self.assertEqual(a['invalid_or_unsafe_count'], 0)

if __name__ == '__main__':
    unittest.main()
