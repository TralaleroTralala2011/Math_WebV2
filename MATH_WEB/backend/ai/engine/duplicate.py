from .validator import fingerprint


def is_duplicate(question, seen):
    return fingerprint(question) in seen
