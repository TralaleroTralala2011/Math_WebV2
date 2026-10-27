from app.ai.engine.geometry_curriculum import generate
from app.ai.engine.solver import equivalent

def test_midpoint_topic_stays_on_topic_across_tiers():
    for tier in ("easy", "medium", "hard", "expert", "hell"):
        for _ in range(12):
            q = generate(10, "g10_geom_coordinate_distance_midpoint", tier)
            text = q["question"].lower()
            assert any(k in text for k in ("trung điểm", "độ dài ab", "khoảng cách", "chia đoạn", "tập hợp các điểm", "tổng ma²", "so sánh ca", "hình bình hành", "chứng minh trung điểm"))
            assert q.get("answer") not in (None, "")
            assert q.get("solution")
            assert q.get("diagram") is not None

def test_symbolic_answer_equivalence():
    assert equivalent("(2; -3.5)", "(2; -7/2)")
    assert equivalent("√50", "5*sqrt(2)")
    assert equivalent("3/6", "0.5")
    assert not equivalent("(2; 3)", "(3; 2)")
