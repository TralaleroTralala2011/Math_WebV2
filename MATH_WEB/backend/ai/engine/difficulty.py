ORDER = {"easy": 1, "medium": 2, "hard": 3, "expert": 4}
ALIASES = {
    "de": "easy", "dễ": "easy", "easy": "easy",
    "vua": "medium", "vừa": "medium", "medium": "medium",
    "kho": "hard", "khó": "hard", "hard": "hard",
    "chuyen": "expert", "chuyên": "expert", "rat_kho": "expert",
    "rất khó": "expert", "expert": "expert",
}


def normalize(value):
    return ALIASES.get(str(value or "medium").strip().lower(), "medium")


def shift(level, delta):
    level = normalize(level)
    n = max(1, min(4, ORDER[level] + delta))
    return next(k for k, v in ORDER.items() if v == n)


def adaptive(accuracy, current="medium"):
    if accuracy is None:
        return normalize(current)
    if accuracy >= 0.85:
        return shift(current, 1)
    if accuracy <= 0.45:
        return shift(current, -1)
    return normalize(current)
