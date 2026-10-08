from .validator import fingerprint

def is_duplicate(question: str, seen: set[str]) -> bool:
    return fingerprint(question) in seen
