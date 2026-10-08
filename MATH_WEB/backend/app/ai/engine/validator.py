import hashlib, re

class ValidationError(ValueError): pass

def fingerprint(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def validate(q: dict) -> None:
    required = ("id", "topic", "grade", "difficulty", "question_type", "question", "answer", "solution")
    for key in required:
        if key not in q or q[key] in (None, ""):
            raise ValidationError(f"missing:{key}")
    if q["question_type"] == "multiple_choice":
        opts=q.get("options") or []
        if len(opts) != 4 or len({str(x).strip() for x in opts}) != 4:
            raise ValidationError("mcq_options")
        if q["answer"] not in opts:
            raise ValidationError("mcq_answer")
    elif q["question_type"] == "true_false":
        if not isinstance(q.get("statements"), list) or len(q["statements"]) != 4:
            raise ValidationError("tf_statements")
    q["fingerprint"] = fingerprint(q["question"])
    return None
