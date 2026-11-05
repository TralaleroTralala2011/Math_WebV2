import hashlib, re
from .solver import equivalent

class ValidationError(ValueError): pass

def fingerprint(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def validate(q: dict) -> None:
    required = ("id", "topic", "grade", "difficulty", "question_type", "question", "answer", "solution")
    for key in required:
        if key not in q or q[key] in (None, ""):
            raise ValidationError(f"missing:{key}")
    # Reject elementary arithmetic substituted for geometry topics. Topic IDs
    # alone are not evidence that the actual question belongs to that topic.
    topic_label = " ".join(str(q.get(k, "")) for k in ("topic", "knowledge_name", "topic_group")).casefold()
    prompt = re.sub(r"\s+", " ", str(q["question"]).strip().casefold())
    is_geometry = any(token in topic_label for token in (
        "geom", "hình học", "hinh hoc", "tam giác", "đường tròn", "không gian",
        "mặt phẳng", "tọa độ", "hình chóp", "hình trụ", "hình cầu",
    ))
    elementary_arithmetic = bool(re.fullmatch(
        r"(?:tính|tinh|hãy tính|hay tinh|calculate)\s*[:：]?\s*"
        r"[-+]?\d+(?:[.,]\d+)?\s*[+\-×*÷/]\s*[-+]?\d+(?:[.,]\d+)?\s*[.?!]?",
        prompt,
    ))
    if is_geometry and elementary_arithmetic:
        raise ValidationError("topic_mismatch_geometry_arithmetic")
    # A calculation question must not silently turn into a true/false prompt.
    if q["question_type"] == "true_false" and elementary_arithmetic:
        raise ValidationError("question_type_mismatch")
    if q["question_type"] == "multiple_choice":
        opts=q.get("options") or []
        if len(opts) != 4 or len({re.sub(r"\s+", " ", str(x).strip().casefold()) for x in opts}) != 4:
            raise ValidationError("mcq_options")
        if q["answer"] not in opts:
            raise ValidationError("mcq_answer")
        # Reject numerical duplicates such as 1/2 vs 0.5, not only identical text.
        # This is a conservative arithmetic check, not a proof of symbolic uniqueness.
        for i, left in enumerate(opts):
            for right in opts[i+1:]:
                if equivalent(left, right):
                    raise ValidationError("mcq_equivalent_options")
    elif q["question_type"] == "true_false":
        if not isinstance(q.get("statements"), list) or len(q["statements"]) != 4:
            raise ValidationError("tf_statements")
    q["fingerprint"] = fingerprint(q["question"])
    normalized = re.sub(r"(?<![A-Za-z])[-+]?\d+(?:[\.,/]\d+)?", "#", str(q["question"]).lower())
    normalized = re.sub(r"^trong [^,]+, ", "", normalized)
    normalized = re.sub(r"^sau khi phân tích dữ kiện, ", "", normalized)
    normalized = re.sub(r"^kiểm tra kiến thức: ", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    q["structure_fingerprint"] = fingerprint(normalized)
    return None
