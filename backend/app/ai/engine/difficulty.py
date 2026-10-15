DIFFICULTY_ORDER = {"easy": 1, "medium": 2, "hard": 3, "expert": 4, "hell": 5}

ALIASES = {
    "de": "easy", "dễ": "easy", "nền tảng": "easy", "nen tang": "easy", "easy": "easy",
    "vừa": "medium", "vua": "medium", "trung cấp": "medium", "trung cap": "medium", "medium": "medium",
    "khó": "hard", "kho": "hard", "nâng cao": "hard", "nang cao": "hard", "hard": "hard",
    "chuyên": "expert", "chuyen": "expert", "học sinh giỏi": "expert", "hsg": "expert", "expert": "expert",
    "địa ngục": "hell", "dia nguc": "hell", "cực khó": "hell", "hell": "hell", "nightmare": "hell",
}

def normalize(value: str | None) -> str:
    raw = (value or "medium").strip().lower()
    return ALIASES.get(raw, raw if raw in DIFFICULTY_ORDER else "medium")

def adaptive(accuracy: float | None, current: str = "medium") -> str:
    current = normalize(current)
    if accuracy is None: return current
    n = DIFFICULTY_ORDER[current]
    if accuracy >= .85: n += 1
    elif accuracy <= .45: n -= 1
    n = max(1, min(5, n))
    return next(k for k, v in DIFFICULTY_ORDER.items() if v == n)
