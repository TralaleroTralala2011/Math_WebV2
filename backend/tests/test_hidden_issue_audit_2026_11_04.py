from app.ai.engine.knowledge_service import KnowledgeService
from app.ai.engine.solver import equivalent
from app.ai.engine.validator import validate, ValidationError
import pytest


def test_quadratic_alias_not_system_equation():
    knowledge = KnowledgeService()
    assert knowledge.normalize_topics(10, ["quadratic-equation"]) == ["ham_so_bac_hai"]
    assert knowledge.normalize_topics(10, ["QUADRATIC_EQUATION"]) == ["ham_so_bac_hai"]
    assert knowledge.normalize_topics(10, ["SYSTEM_EQUATION"]) == ["phuong_trinh_he"]


def test_pi_equivalent_math_answers():
    assert equivalent("2π", "2*pi") is False  # Unicode multiplication is not silently guessed
    assert equivalent("2*pi", "6.283185307179586")
    assert equivalent("pi", "3.141592653589793")


def test_duplicate_pi_options_rejected():
    q = {"id":"audit","topic":"ham_so_bac_hai","grade":10,"difficulty":"easy", "question_type":"multiple_choice", "question":"Giá trị của pi là bao nhiêu?", "answer":"pi", "solution":"π là hằng số.", "options":["pi", "3.141592653589793", "2", "4"]}
    with pytest.raises(ValidationError, match="mcq_equivalent_options"):
        validate(q)
