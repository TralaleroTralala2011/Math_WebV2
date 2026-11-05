import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from app.ai.engine.validator import validate, ValidationError
from app.ai.engine.service import AIQuestionService


def question(options, answer):
    return {"id": "test", "topic": "topic", "grade": 10, "difficulty": "easy", "question_type": "multiple_choice", "question": "Tính 1/2", "answer": answer, "solution": "1/2 = 0.5", "options": options}


def test_reject_equivalent_options():
    with pytest.raises(ValidationError, match="mcq_equivalent_options"):
        validate(question(["1/2", "0.5", "2", "3"], "1/2"))


def test_valid_distinct_choices():
    q=question(["1/2", "1", "2", "3"], "1/2")
    validate(q)
    assert q.get("fingerprint")


def test_check_browser_answer_formats():
    service=AIQuestionService.__new__(AIQuestionService)
    q=question(["1", "1/2", "2", "3"], "1/2")
    for value in ["B", "b", 1, "1/2", "0.5", {"index": 1}, {"answer": "B"}]:
        assert service._check(q, value), repr(value)
    for value in ["A", 0, "3", {"index": 3}]:
        assert not service._check(q, value), repr(value)
