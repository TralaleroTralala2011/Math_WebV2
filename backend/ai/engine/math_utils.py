import math
from fractions import Fraction


def fmt(value):
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def comb(n, k):
    return math.comb(n, k) if 0 <= k <= n else 0


def perm(n, k=None):
    return math.factorial(n) if k is None else math.factorial(n) // math.factorial(n - k)
