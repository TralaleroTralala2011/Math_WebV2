import math
from fractions import Fraction

def clean_num(x):
    if isinstance(x, float) and x.is_integer(): return int(x)
    return x

def fmt(x):
    if isinstance(x, Fraction):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(clean_num(x))

def gcd(a,b): return math.gcd(int(a), int(b))

def lcm(a,b): return abs(int(a*b)) // gcd(a,b) if a and b else 0

def quadratic_roots(a,b,c):
    d=b*b-4*a*c
    if d < 0: return []
    if d == 0: return [Fraction(-b,2*a)]
    s=math.isqrt(d)
    if s*s==d:
        return [Fraction(-b-s,2*a), Fraction(-b+s,2*a)]
    return None

def perm(n): return math.factorial(n)

def comb(n,k):
    if k<0 or k>n: return 0
    return math.comb(n,k)
