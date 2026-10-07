import hashlib
import re


class ValidationError(ValueError):
    pass


def fingerprint(text):
    text = re.sub(r"\s+", " ", str(text).strip().lower())
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate(q):
    required = (
        "id", "grade", "topic", "difficulty", "question_type",
        "question", "answer", "solution"
    )
    for key in required:
        if key not in q or q[key] in (None, ""):
            raise ValidationError(f"missing:{key}")

    t = q["question_type"]
    if t == "multiple_choice":
        options = q.get("options") or []
        if len(options) != 4 or len({str(x) for x in options}) != 4:
            raise ValidationError("mcq_options")
        if str(q["answer"]) not in {str(x) for x in options}:
            raise ValidationError("mcq_answer")
    elif t == "true_false":
        if len(q.get("statements") or []) != 4:
            raise ValidationError("tf_statements")
        if len(q.get("statement_answers") or []) != 4:
            raise ValidationError("tf_answers")
    elif t != "short_answer":
        raise ValidationError("question_type")

    q["fingerprint"] = fingerprint(q["question"])
    return q
