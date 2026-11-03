from .difficulty import adaptive

def next_difficulty(history: list[dict] | None, current="medium"):
    if not history:
        return current
    recent=history[-10:]
    accuracy=sum(bool(x.get("correct")) for x in recent)/len(recent)
    return adaptive(accuracy,current)
