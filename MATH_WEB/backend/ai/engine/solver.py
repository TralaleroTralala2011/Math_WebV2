import re
from fractions import Fraction


def normalize_answer(value):
    s = str(value).strip().lower().replace(" ", "").replace("−", "-")
    # Accept simple fractions such as 3/4 and ordinary integers/decimals.
    try:
        return Fraction(s)
    except Exception:
        pass
    return re.sub(r"[{}()\[\]]", "", s)


def equivalent(a, b):
    return normalize_answer(a) == normalize_answer(b)
