import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_research_method_collisions import audit, norm

class TestMethodAudit(unittest.TestCase):
    def test_unicode_normalization(self):
        self.assertEqual(norm('  PHÉP  CỘNG  '), norm('phép cộng'))

    def test_detect_same_method_same_topic(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'V999_RESEARCH' / 'TEST_CANDIDATE.jsonl'
            p.parent.mkdir()
            p.write_text('\n'.join(json.dumps(x) for x in [
                {'topic':'tap_hop','solving_method':'Đếm tập hợp','title':'A'},
                {'topic':'tap_hop','solving_method':'đếm tập hợp','title':'B'},
            ]), encoding='utf-8')
            self.assertEqual(audit(Path(td))['exact_topic_method_collision_groups'], 1)

    def test_reject_premature_publication(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'V999_RESEARCH' / 'TEST_CANDIDATE.jsonl'
            p.parent.mkdir()
            p.write_text(json.dumps({'topic':'tap_hop','solving_method':'x','published':True}), encoding='utf-8')
            self.assertTrue(audit(Path(td))['invalid_or_unsafe'])

if __name__ == '__main__':
    unittest.main()
