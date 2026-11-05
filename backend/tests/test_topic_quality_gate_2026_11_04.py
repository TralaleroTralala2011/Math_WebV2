import pytest
from app.ai.engine.validator import validate, ValidationError


def question(topic, text, kind="multiple_choice"):
    return {"id":"x", "topic":topic, "knowledge_name":topic,
            "grade":12, "difficulty":"easy", "question_type":kind,
            "question":text, "answer":"53", "solution":"23+30=53",
            "options":["53","87","79","40"]}


@pytest.mark.parametrize("text", ["Tính 23 + 30.", "Hãy tính: 10 + 28?", "Tính 20 × 4."])
def test_geometry_rejects_unrelated_arithmetic(text):
    with pytest.raises(ValidationError, match="topic_mismatch"):
        validate(question("g12_geom_3d_optimization", text))


def test_algebra_does_not_incorrectly_block_arithmetic():
    validate(question("g10_arithmetic", "Tính 23 + 30."))


def test_geometry_allows_real_geometry_problem():
    validate(question("g12_geom_3d_optimization", "Một hình hộp chữ nhật có ba cạnh 2, 3, 4 cm. Tính thể tích."))


def test_equivalent_mcq_options_are_rejected():
    q=question("g10_arithmetic", "Tính 1/2 + 1/2.")
    q["options"]=["1/2","0.5","1","2"]
    q["answer"]="1"
    with pytest.raises(ValidationError, match="equivalent"):
        validate(q)
