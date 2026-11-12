"""Regression: truncated shuffled mixed blocks must retain all answer modes."""
import random
from app.ai.engine.service import AIQuestionService


def test_mixed_mode_distribution_minimum_three(monkeypatch):
    # Inspect the type schedule without invoking the expensive generator.
    # Service constructor is intentionally bypassed; the generation call's
    # dependent collaborators are stubbed at their interface boundaries.
    service = object.__new__(AIQuestionService)
    class Knowledge:
        def normalize_topics(self, grade, topics): return topics
    service.knowledge = Knowledge()
    service.recent_families = {}
    calls = []
    def fake_one(grade, topic, level, qtype, *args):
        calls.append(qtype)
        n = len(calls)
        return {'question': f'Question {n}', 'answer':'1', 'fingerprint':str(n), 'question_type':qtype}
    service.generate_one = fake_one
    monkeypatch.setattr('app.ai.engine.service.geometry_diagram', lambda *args: None)
    for count in (3, 4, 5, 7, 9, 10, 11, 20):
        for seed in range(20):
            random.seed(seed)
            calls.clear()
            result = service.generate_set(11, ['xac_suat_11'], count, question_type='mixed')
            assert len(result['questions']) == count
            assert {'multiple_choice','short_answer','true_false'} <= set(calls)
