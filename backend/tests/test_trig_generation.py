"""Regression coverage for varied Grade 11 trigonometry generation."""

import pytest

from app.ai.engine.service import AIQuestionService


TRIG_TOPICS = [
    "gia_tri_luong_giac",
    "cong_thuc_luong_giac",
    "ham_so_luong_giac_day_du",
    "phuong_trinh_luong_giac_day_du",
]


@pytest.mark.parametrize("topic", TRIG_TOPICS)
@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_trig_topic_generates_unique_practice_set(topic, difficulty, tmp_path, monkeypatch):
    history_db = tmp_path / f"{topic}_{difficulty}.sqlite3"
    monkeypatch.setenv("MATHWEB_AI_HISTORY_DB_PATH", str(history_db))
    service = AIQuestionService()

    result = service.generate_set(
        grade=11,
        topics=[topic],
        count=10,
        difficulty=difficulty,
        question_type="mixed",
    )

    questions = result["questions"]
    assert len(questions) == 10
    assert len({question["question"] for question in questions}) == 10
    assert all(question.get("answer") not in (None, "") for question in questions)
    assert all(question.get("solution") for question in questions)
    assert all(question.get("difficulty") == difficulty for question in questions)


def test_trig_equation_topic_survives_multiple_sets(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "MATHWEB_AI_HISTORY_DB_PATH",
        str(tmp_path / "trig_equation_history.sqlite3"),
    )
    service = AIQuestionService()

    for _ in range(4):
        result = service.generate_set(
            grade=11,
            topics=["phuong_trinh_luong_giac_day_du"],
            count=10,
            difficulty="medium",
            question_type="mixed",
        )
        assert len(result["questions"]) == 10
        assert len({question["question"] for question in result["questions"]}) == 10
