"""Read-only audit for MATH_WEB topic counts and the 45-topic geometry expansion.

Run from backend/: python scripts/audit_ai_geometry_catalog.py
This checks catalogue metadata only; it does not claim that every browser flow was manually tested.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "app/ai/knowledge/index.json"
index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
all_topics = [topic for grade in ("10", "11", "12") for topic in index.get(grade, [])]
ids = [str(topic.get("id", "")) for topic in all_topics]
if len(ids) != len(set(ids)):
    duplicates = [topic_id for topic_id, count in Counter(ids).items() if count > 1]
    raise SystemExit(f"FAIL duplicate topic IDs: {duplicates}")

prefix = {"10": "g10_geom_", "11": "g11_geom_", "12": "g12_geom_"}
levels = ("Nền tảng", "Trung cấp", "Nâng cao")
errors = []
new_topics = []
for grade in ("10", "11", "12"):
    grade_topics = index.get(grade, [])
    found = [t for t in grade_topics if str(t.get("id", "")).startswith(prefix[grade])]
    new_topics.extend(found)
    if len(found) != 15:
        errors.append(f"Grade {grade}: expected 15 added geometry topics, found {len(found)}")
    for level in levels:
        count = sum(1 for t in found if t.get("difficulty_level") == level)
        if count != 5:
            errors.append(f"Grade {grade}, {level}: expected 5, found {count}")
    for topic in found:
        if not topic.get("subtopics"):
            errors.append(f"{topic.get('id')}: missing subtopics")
        if topic.get("geometry") is not True:
            errors.append(f"{topic.get('id')}: geometry flag is not true")

print("MATH_WEB topic audit")
print(f"Grade 10 records: {len(index.get('10', []))}")
print(f"Grade 11 records: {len(index.get('11', []))}")
print(f"Grade 12 records: {len(index.get('12', []))}")
print(f"Total index records: {len(all_topics)}")
print(f"Unique topic IDs: {len(set(ids))}")
print(f"Added geometry topics: {len(new_topics)}")
print("Geometry additions by grade/level:")
for grade in ("10", "11", "12"):
    found = [t for t in index.get(grade, []) if str(t.get("id", "")).startswith(prefix[grade])]
    print(f"  Grade {grade}: " + ", ".join(f"{level}={sum(t.get('difficulty_level') == level for t in found)}" for level in levels))
print("Baseline discrepancy: target says 102 existing topics; current index has 94 non-expansion records.")
print("147 is a target only; current index count is not 147.")
if errors:
    print("FAIL")
    print("\n".join(f"- {e}" for e in errors))
    raise SystemExit(1)
print("PASS: unique IDs and required 45-topic distribution")
