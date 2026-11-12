import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.verified_bank_routes import audit_records, load_bank, quality, normalized_question

def test_bank_quality_report():
    result = quality()
    assert result["question_count"] >= 1510
    assert result["form_count"] >= 145
    assert result["forms_with_ten_questions"] >= 145
    assert not any(i["issue"] == "invalid_linear_proof" for i in result["issues"])
    assert result["fully_mathematically_verified"] is False

def test_normalization():
    assert normalized_question("  A   B ") == normalized_question("a b")

def test_detect_duplicate_and_bad_proof():
    row = dict(load_bank()[0]); row["proof"] = dict(row["proof"], x=999)
    report = audit_records([row, dict(row)])
    assert {x["issue"] for x in report["issues"]} >= {"duplicate_question", "invalid_linear_proof"}
