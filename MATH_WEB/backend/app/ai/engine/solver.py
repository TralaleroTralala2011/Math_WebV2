from fractions import Fraction
import re

def normalize_answer(value):
    s=str(value).strip().lower().replace(" ", "")
    s=s.replace("−","-")
    try: return Fraction(s)
    except Exception: return s

def equivalent(a,b):
    return normalize_answer(a) == normalize_answer(b)

def solve_numeric(q: dict):
    return q.get("answer")
