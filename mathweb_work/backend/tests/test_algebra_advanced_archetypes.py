"""Regression tests for higher-reasoning algebra archetypes added to game bank."""
from types import SimpleNamespace

from app.ai.engine.game_bank import GameQuestionBank


def _fake_generator():
    def base(question, answer, solution, options=None, hint="", **meta):
        return {"question": question, "answer": answer, "solution": solution,
                "options": options or [], "hint": hint, **meta}
    return SimpleNamespace(_base=base)


def test_advanced_algebra_builders_return_complete_questions():
    bank = GameQuestionBank(_fake_generator())
    for game_id, builder in bank._advanced.items():
        for _ in range(25):
            q = builder(bank, "expert")
            assert q["question"].strip(), game_id
            assert q["answer"] is not None, game_id
            assert q["solution"].strip(), game_id
            assert str(q["answer"]).strip() not in {"None", ""}, game_id


def test_advanced_algebra_bank_is_attached_to_existing_game_ids():
    bank = GameQuestionBank(_fake_generator())
    assert set(bank._advanced).issubset(set(bank._builders))
    assert len(bank._advanced) >= 8


def test_true_false_numeric_statements_are_logically_consistent():
    from app.ai.engine.generator import QuestionGenerator

    knowledge = {1: {"name": "Hàm số"}}
    generator = QuestionGenerator(knowledge)
    q = {"question": "Tính 2+3", "answer": 5, "solution": "2+3=5", "options": []}
    out = generator._convert(q, "true_false")
    assert out["statement_answers"] == [True, False, False, True]
    assert "Đáp án lớn hơn 6" in out["statements"][1]


def test_expert_geometry_tasks_are_distinct_and_diagrams_validate():
    from app.ai.engine.geometry_curriculum import generate
    from app.ai.engine.geometry_diagrams import validate_geometry_diagram

    cases = [
        (10, "duong_tron", "expert", "olympic_circle_power"),
        (10, "he_thuc_luong_tam_giac", "expert", "olympic_triangle_heron"),
        (10, "toa_do_phang", "hell", "olympic_circle_tangent_parameter"),
        (10, "ham_so_bac_hai", "expert", "olympic_parameter_quadratic"),
        (12, "toa_do_khong_gian", "expert", "olympic_space_distance"),
    ]
    for grade, topic, difficulty, family in cases:
        q = generate(grade, topic, difficulty)
        assert q["archetype"] == family
        assert q["question"] and q["solution"] and q["answer"] is not None
        if q.get("diagram"):
            assert not validate_geometry_diagram(q["diagram"])
