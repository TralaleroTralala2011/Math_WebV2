import json
import tempfile
import unittest
from pathlib import Path
from audit_practice_coverage import inspect


class CoverageTests(unittest.TestCase):
    def test_duplicates_do_not_inflate_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bank.jsonl'
            row = dict(topic_id='t', type_id='a', structure_signature='s', question='Q', answer='A', solution='Step: A', answer_reviewed=True, solution_reviewed=True, topic_alignment_reviewed=True, reviewed_topic_id='t')
            p.write_text('\n'.join(json.dumps(row) for _ in range(10)), encoding='utf-8')
            r = inspect(p, ['t'], min_types=1, min_questions=10)
            self.assertEqual(r['metadata_qualified_topics'], 0)
            self.assertEqual(r['counts']['duplicate_within_type'], 9)

    def test_signature_conflict_fails_type(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bank.jsonl'
            rows = [dict(topic_id='t', type_id='a', structure_signature=str(i), question='Q'+str(i), answer='A', solution='Explanation', answer_reviewed=True, solution_reviewed=True, topic_alignment_reviewed=True, reviewed_topic_id='t') for i in range(2)]
            p.write_text('\n'.join(map(json.dumps, rows)), encoding='utf-8')
            self.assertEqual(inspect(p, ['t'], 1, 2)['metadata_qualified_topics'], 0)

    def test_cross_type_question_reuse_fails_both_types(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bank.jsonl'
            rows = [dict(topic_id='t', type_id=k, structure_signature=k, question='Same question', answer='1', solution='Compute 1', answer_reviewed=True, solution_reviewed=True, topic_alignment_reviewed=True, reviewed_topic_id='t') for k in ('a', 'b')]
            p.write_text('\n'.join(map(json.dumps, rows)), encoding='utf-8')
            result = inspect(p, ['t'], 2, 1)
            self.assertEqual(result['topics']['t']['metadata_qualified_types'], 0)
            self.assertEqual(result['counts']['cross_type_duplicate_questions'], 1)

    def test_same_signature_different_type_ids_not_independent(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bank.jsonl'
            rows = [dict(topic_id='t', type_id=k, structure_signature='identical', question='Q'+k, answer='1', solution='Compute 1', answer_reviewed=True, solution_reviewed=True, topic_alignment_reviewed=True, reviewed_topic_id='t') for k in ('a', 'b')]
            p.write_text('\n'.join(map(json.dumps, rows)), encoding='utf-8')
            result = inspect(p, ['t'], 2, 1)
            self.assertEqual(result['topics']['t']['metadata_qualified_types'], 0)
            self.assertEqual(result['counts']['shared_structure_signatures'], 1)

    def test_complete_metadata_and_missing_topic(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bank.jsonl'
            rows = [dict(topic_id='t', type_id='a', structure_signature='s', question='Q'+str(i), answer='A', solution='Explanation', answer_reviewed=True, solution_reviewed=True, topic_alignment_reviewed=True, reviewed_topic_id='t') for i in range(2)]
            p.write_text('\n'.join(map(json.dumps, rows)), encoding='utf-8')
            r = inspect(p, ['t', 'missing'], 1, 2)
            self.assertEqual(r['metadata_qualified_topics'], 1)
            self.assertEqual(r['topics']['missing']['missing_qualified_types'], 1)
            self.assertFalse(r['mathematical_correctness_verified'])

if __name__ == '__main__':
    unittest.main()
