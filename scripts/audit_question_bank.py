"""Audit JSON/JSONL question-bank exports without silently accepting invalid items.

Usage: python scripts/audit_question_bank.py path/to/questions.json
Accepts a list or {"questions": [...]}. Does not modify the source file.
This checks structure and duplicate text, NOT mathematical correctness.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path


def normalize(value):
    return re.sub(r"\s+", " ", str(value).strip().casefold())


def audit(items):
    errors = []
    seen = {}
    topics = {}
    for index, q in enumerate(items, 1):
        if not isinstance(q, dict):
            errors.append(f"#{index}: not a question object")
            continue
        topic = str(q.get("topic", "")).strip()
        question = str(q.get("question", "")).strip()
        answer = str(q.get("answer", q.get("correct_answer", ""))).strip()
        if not topic or not question or not answer:
            errors.append(f"#{index}: missing topic/question/answer")
            continue
        topics[topic] = topics.get(topic, 0) + 1
        key = hashlib.sha256(normalize(question).encode()).hexdigest()
        if key in seen:
            errors.append(f"#{index}: duplicate question text of #{seen[key]}")
        else:
            seen[key] = index
        kind = q.get("question_type", "multiple_choice")
        if kind == "multiple_choice":
            choices = q.get("options", q.get("choices", []))
            if not isinstance(choices, list) or len(choices) != 4:
                errors.append(f"#{index}: expected four options")
                continue
            normalized_choices = [normalize(x) for x in choices]
            if len(set(normalized_choices)) != 4:
                errors.append(f"#{index}: duplicate answer options")
            if normalize(answer) not in normalized_choices:
                errors.append(f"#{index}: correct answer does not match an option")
    return {"total": len(items), "topics": topics, "errors": errors, "structurally_valid": not errors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    with args.file.open(encoding="utf-8") as handle:
        if args.file.suffix.lower() == ".jsonl":
            questions = [json.loads(line) for line in handle if line.strip()]
        else:
            questions = json.load(handle)
    if isinstance(questions, dict):
        questions = questions["questions"]
    if not isinstance(questions, list):
        raise ValueError("Expected list of questions")
    result = audit(questions)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["structurally_valid"] else 1)

if __name__ == "__main__":
    main()
