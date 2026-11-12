"""Deterministic worked examples and a separate symbolic verifier.

These nine families demonstrate a safe pipeline, not an AI capable of
inventing 300,000 independent mathematical methods.
"""
from __future__ import annotations
import hashlib
import json
import random
import re
from sympy import Integer, Rational, Symbol, diff, integrate, sqrt, simplify, sympify


class VerificationError(ValueError):
    pass


def _rng(family, ordinal, seed_key=None):
    stable_key = str(seed_key or family)
    seed = int(hashlib.sha256(f'{family}:{stable_key}:{ordinal}:v2'.encode()).hexdigest()[:16],16)
    return random.Random(seed)


def generate(family, ordinal, difficulty, seed_key=None):
    from . import v123_research
    if family in v123_research.FAMILIES:
        return v123_research.generate(family, ordinal, difficulty, seed_key=seed_key)
    # Optional V122 generator may be absent in audit-only distributions.
    from importlib.util import find_spec
    if find_spec('question_factory.v122_research') is not None:
        from . import v122_research
        if family in v122_research.FAMILIES:
            return v122_research.generate(family, ordinal, difficulty, seed_key=seed_key)
    from . import v121_research
    if family in v121_research.FAMILIES:
        return v121_research.generate(family, ordinal, difficulty, seed_key=seed_key)
    from . import v120_research
    if family in v120_research.FAMILIES:
        return v120_research.generate(family, ordinal, difficulty, seed_key=seed_key)
    from . import v119_research
    if family in v119_research.FAMILIES:
        return v119_research.generate(family, ordinal, difficulty, seed_key=seed_key)
    from . import v118_research
    if family in v118_research.FAMILIES:
        return v118_research.generate(family, ordinal, difficulty, seed_key=seed_key)
    from . import v117_research
    if family in v117_research.FAMILIES:
        return v117_research.generate(family, ordinal, difficulty, seed_key=seed_key)
    from . import v116_research
    if family in v116_research.FAMILIES:
        return v116_research.generate(family, ordinal, difficulty, seed_key=seed_key)
    from . import v114_engine
    if family in v114_engine.FAMILIES:
        return v114_engine.generate(family, ordinal, difficulty, seed_key=seed_key)
    from . import expanded_engine
    if family in expanded_engine.FAMILIES:
        return expanded_engine.generate(family, ordinal, difficulty, seed_key=seed_key)
    if not isinstance(ordinal,int) or ordinal<0 or ordinal>9:
        raise ValueError('pilot permits ordinal 0..9')
    rng=_rng(family,ordinal,seed_key=seed_key)
    p={}
    if family=='set_union':
        p=dict(a=12+ordinal*2,b=rng.randint(9,17)+ordinal,i=rng.randint(2,7))
        expected=p['a']+p['b']-p['i']
        stem=f"Cho hai tập hữu hạn A, B với |A|={p['a']}, |B|={p['b']} và |A∩B|={p['i']}. Tính |A∪B|."
        solution=f"Dùng nguyên lý cộng trừ: |A∪B|=|A|+|B|-|A∩B|={p['a']}+{p['b']}-{p['i']}={expected}."
    elif family=='linear_equation':
        x=ordinal-4; a=rng.randint(2,9); b=rng.randint(-12,12); c=a*x+b
        p=dict(a=a,b=b,c=c)
        expected=Integer(x)
        stem=f"Giải phương trình {a}x + ({b}) = {c}."
        solution=f"Chuyển vế: {a}x={c}-{b}={c-b}; chia cho {a}, được x={x}."
    elif family=='vieta_sum':
        a=rng.randint(1,5); r1=ordinal+1; r2=rng.randint(-7,-1)
        b=-a*(r1+r2);c=a*r1*r2
        p=dict(a=a,b=b,c=c)
        expected=Integer(-b)/a
        stem=f"Không giải trực tiếp, tính tổng hai nghiệm của phương trình {a}x² + ({b})x + ({c}) = 0."
        solution=f"Phương trình có hai nghiệm thực vì Δ≥0. Theo Viète: x₁+x₂=-b/a={-b}/{a}={expected}."
    elif family=='triangle_area':
        base=2*(ordinal+3);h=rng.randint(3,13)
        p=dict(base=base,h=h)
        expected=Rational(base*h,2)
        stem=f"Một tam giác có cạnh đáy {base} cm và đường cao tương ứng {h} cm. Tính diện tích (cm²)."
        solution=f"S=1/2×đáy×chiều cao=1/2×{base}×{h}={expected} cm²."
    elif family=='ap_term':
        a1=rng.randint(-9,9);d=ordinal+2;n=rng.randint(5,14)
        p=dict(a1=a1,d=d,n=n)
        expected=Integer(a1+(n-1)*d)
        stem=f"Cấp số cộng có u₁={a1}, công sai d={d}. Tính u{n}."
        solution=f"uₙ=u₁+(n-1)d={a1}+({n}-1)×{d}={expected}."
    elif family=='ap_sum':
        a1=rng.randint(-8,12);d=ordinal+1;n=rng.randint(6,15)
        p=dict(a1=a1,d=d,n=n)
        expected=Rational(n*(2*a1+(n-1)*d),2)
        stem=f"Cấp số cộng có u₁={a1}, công sai d={d}. Tính S{n}, tổng {n} số hạng đầu."
        solution=f"Sₙ=n[2u₁+(n-1)d]/2={n}[2×{a1}+({n}-1)×{d}]/2={expected}."
    elif family=='derivative_at':
        a=ordinal+1;b=rng.randint(-9,8);c=rng.randint(-9,9);t=rng.randint(-4,5)
        p=dict(a=a,b=b,c=c,t=t)
        expected=Integer(2*a*t+b)
        stem=f"Cho f(x)={a}x²+({b})x+({c}). Tính f'({t})."
        solution=f"f'(x)=2×{a}x+({b}). Thay x={t}: f'({t})=2×{a}×({t})+({b})={expected}."
    elif family=='definite_integral':
        a=ordinal+1;b=rng.randint(-5,8);upper=rng.randint(2,10)
        p=dict(a=a,b=b,upper=upper)
        expected=Rational(a*upper**2,2)+b*upper
        stem=f"Tính tích phân I=∫₀^{upper} ({a}x+({b})) dx."
        solution=f"Nguyên hàm là {a}x²/2+({b})x. Thay cận 0 và {upper}, I={a}×{upper}²/2+({b})×{upper}={expected}."
    elif family=='space_distance':
        x=ordinal+1;y=rng.randint(2,7);z=rng.randint(3,8)
        p=dict(x1=0,y1=0,z1=0,x2=x,y2=y,z2=z)
        expected=sqrt(x*x+y*y+z*z)
        stem=f"Trong Oxyz, cho A(0;0;0) và B({x};{y};{z}). Tính độ dài AB."
        solution=f"AB=√[({x}-0)²+({y}-0)²+({z}-0)²]=√({x*x+y*y+z*z})={expected}."
    else:
        raise ValueError(f'unknown family: {family}')
    data=dict(family=family,ordinal=ordinal,params=p,stem=stem,
              answer=str(expected),solution=solution,difficulty=difficulty)
    normalized=re.sub(r'\s+',' ',stem.strip().casefold())
    data['fingerprint']=hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    return data


def independently_verify(data):
    from . import v123_research
    if data.get('family') in v123_research.FAMILIES:
        return v123_research.verify(data)
    # V122 was an audit-only release; some distributed ZIPs contain no
    # v122_research module.  Continue checking registered families instead
    # of aborting verification for all subsequent versions.
    from importlib.util import find_spec
    if find_spec('question_factory.v122_research') is not None:
        from . import v122_research
        if data.get('family') in v122_research.FAMILIES:
            return v122_research.verify(data)
    from . import v121_research
    if data.get('family') in v121_research.FAMILIES:
        return v121_research.verify(data)
    from . import v120_research
    if data.get('family') in v120_research.FAMILIES:
        return v120_research.verify(data)
    from . import v119_research
    if data.get('family') in v119_research.FAMILIES:
        return v119_research.verify(data)
    from . import v118_research
    if data.get('family') in v118_research.FAMILIES:
        return v118_research.verify(data)
    from . import v117_research
    if data.get('family') in v117_research.FAMILIES:
        return v117_research.verify(data)
    from . import v116_research
    if data.get('family') in v116_research.FAMILIES:
        return v116_research.verify(data)
    from . import v114_engine
    if data.get('family') in v114_engine.FAMILIES:
        return v114_engine.verify(data)
    from . import expanded_engine
    if data.get('family') in expanded_engine.FAMILIES:
        return expanded_engine.verify(data)
    """Recompute from recorded parameters, not from the provided solution text."""
    fam=data['family']; p=data['params']; x=Symbol('x')
    try:
        if fam=='set_union':
            value=Integer(p['a']+p['b']-p['i'])
            if not 0<=p['i']<=min(p['a'],p['b']):
                raise VerificationError('invalid set cardinalities')
        elif fam=='linear_equation':
            if p['a']==0: raise VerificationError('a=0')
            value=Rational(p['c']-p['b'],p['a'])
        elif fam=='vieta_sum':
            if p['a']==0 or p['b']**2-4*p['a']*p['c']<0:
                raise VerificationError('invalid real quadratic')
            value=Rational(-p['b'],p['a'])
        elif fam=='triangle_area':
            if min(p['base'],p['h'])<=0: raise VerificationError('nonpositive length')
            value=Rational(p['base']*p['h'],2)
        elif fam=='ap_term':
            if p['n']<1: raise VerificationError('invalid n')
            value=Integer(p['a1']+(p['n']-1)*p['d'])
        elif fam=='ap_sum':
            if p['n']<1: raise VerificationError('invalid n')
            value=Rational(p['n']*(2*p['a1']+(p['n']-1)*p['d']),2)
        elif fam=='derivative_at':
            value=diff(p['a']*x*x+p['b']*x+p['c'],x).subs(x,p['t'])
        elif fam=='definite_integral':
            if p['upper']<=0: raise VerificationError('invalid interval')
            value=integrate(p['a']*x+p['b'],(x,0,p['upper']))
        elif fam=='space_distance':
            value=sqrt((p['x2']-p['x1'])**2+(p['y2']-p['y1'])**2+(p['z2']-p['z1'])**2)
        else:
            raise VerificationError(f'unknown verifier family {fam}')
        # The answer comes from our own generator only, not arbitrary user input.
        if simplify(sympify(data['answer'])-value)!=0:
            raise VerificationError(f"expected {value}, received {data['answer']}")
        if len(data['solution'].strip()) < 25 or len(data['stem'].strip()) < 20:
            raise VerificationError('missing question or worked solution')
        return True, dict(engine='sympy-recomputation',equivalent=True,
                          answer=str(value),type_independence='requires-human-review')
    except VerificationError as ex:
        return False, dict(engine='sympy-recomputation',equivalent=False,error=str(ex))
    except Exception as ex:
        return False, dict(engine='sympy-recomputation',equivalent=False,error=f'{type(ex).__name__}: {ex}')
