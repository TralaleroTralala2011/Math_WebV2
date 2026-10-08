from .difficulty import adaptive, normalize


def next_difficulty(history=None, current="medium"):
    if not history:
        return normalize(current)
    recent = history[-10:]
    values = [bool(x.get("correct")) for x in recent if isinstance(x, dict)]
    if not values:
        return normalize(current)
    return adaptive(sum(values) / len(values), current)
