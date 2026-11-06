import json
import tempfile
import unittest
from pathlib import Path
from audit_question_quality import audit

class QualityAuditTests(unittest.TestCase):
    def run_rows(self, rows):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bank.jsonl'
            path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
            return audit(path)

    def row(self, question='Giải phương trình x+2=5'):
        return dict(topic_id='t1', type_id='linear', skill_id='solve', structure_signature='isolate-linear', question=question, answer='3', solution='Chuyển số hạng 2 sang vế phải, suy ra x = 5 - 2 = 3. Thử lại 3 + 2 = 5.', topic_alignment_reviewed=True, reviewed_topic_id='t1', solution_reviewed=True, answer_reviewed=True)

    def test_valid(self):
        r=self.run_rows([self.row()]); self.assertEqual(r['issues'], {})
    def test_duplicate(self):
        r=self.run_rows([self.row(), self.row()]); self.assertEqual(r['issues']['duplicate_question_text'],1)
    def test_short_solution(self):
        row=self.row(); row['solution']='3'; self.assertIn('solution_too_short_for_detailed_explanation',self.run_rows([row])['issues'])
    def test_missing_review(self):
        row=self.row(); row['answer_reviewed']=False; self.assertIn('answer_not_reviewed',self.run_rows([row])['issues'])
    def test_signature_conflict(self):
        a=self.row(); b=self.row('Giải x+3=6'); b['structure_signature']='different'; self.assertIn('inconsistent_type_signature',self.run_rows([a,b])['issues'])

if __name__=='__main__': unittest.main()
