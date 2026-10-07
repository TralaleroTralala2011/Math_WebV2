DIFFICULTY_ORDER = {"easy": 1, "medium": 2, "hard": 3}

ALIASES = {
    "de": "easy",
    "dễ": "easy",
    "easy": "easy",
    "khá": "medium",
    "kha": "medium",
    "vừa": "medium",
    "medium": "medium",
    "khó": "hard",
    "hard": "hard",
    "chuyên": "hard",
    "expert": "hard",
}

def normalize(value: str | None) -> str:
    return ALIASES.get((value or "medium").strip().lower(), "medium")

def adaptive(accuracy: float | None, current: str = "medium") -> str:
    current = normalize(current)
    if accuracy is None:
        return current
    n = DIFFICULTY_ORDER[current]
    if accuracy >= .85:
        n += 1
    elif accuracy <= .45:
        n -= 1
    n = max(1, min(3, n))
    return next(k for k, v in DIFFICULTY_ORDER.items() if v == n)
