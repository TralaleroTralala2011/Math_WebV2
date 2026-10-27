import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = json.loads((ROOT / "app/ai/knowledge/index.json").read_text(encoding="utf-8"))
CATALOG = json.loads((ROOT / "app/ai/knowledge/geometry_curriculum_catalog.json").read_text(encoding="utf-8"))

def test_45_new_geometry_topics_have_required_distribution():
    added = [t for grade in ("10", "11", "12") for t in INDEX[grade] if t.get("source") == "geometry_45_expansion_2026-10-16"]
    # Source metadata lives in the geometry catalog; index records use the explicit ID prefix.
    ids = {x["id"] for grade in ("10", "11", "12") for x in INDEX[grade] if x["id"].startswith(("g10_geom_", "g11_geom_", "g12_geom_"))}
    assert len(ids) == 45
    for grade in ("10", "11", "12"):
        grade_ids = [x["id"] for x in INDEX[grade] if x["id"].startswith(f"g{grade}_geom_")]
        assert len(grade_ids) == 15
        for level in ("Nền tảng", "Trung cấp", "Nâng cao"):
            assert sum(1 for x in INDEX[grade] if x.get("difficulty_level") == level and x["id"].startswith(f"g{grade}_geom_")) == 5

def test_new_topic_ids_are_unique_and_have_skills():
    all_topics = [t for topics in INDEX.values() for t in topics]
    all_ids = [t["id"] for t in all_topics]
    assert len(all_ids) == len(set(all_ids))
    for t in all_topics:
        if t["id"].startswith(("g10_geom_", "g11_geom_", "g12_geom_")):
            assert t.get("subtopics") and t.get("geometry") is True
