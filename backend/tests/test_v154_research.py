"""Independent geometry projection / symbolic integration answer oracles."""
import json
from pathlib import Path
from collections import Counter
from fractions import Fraction
import sympy as sp

ROOT=Path(__file__).resolve().parents[2]
RESEARCH=ROOT/'V154_RESEARCH'

def read(name):
    return [json.loads(line) for line in (RESEARCH/name).read_text(encoding='utf8').splitlines()]

def independent_oracle(q):
    p=q['params']
    if q['id'].startswith('v154_geo_'):
        a,b,c,x,y=(p[key] for key in ('a','b','c','x','y'))
        # Construct the perpendicular foot and use squared Euclidean distance.
        t=Fraction(a*x+b*y+c, a*a+b*b)
        hx=Fraction(x)-a*t;hy=Fraction(y)-b*t
        squared=(Fraction(x)-hx)**2+(Fraction(y)-hy)**2
        return sp.sqrt(sp.Rational(squared.numerator,squared.denominator))
    x=sp.symbols('x', real=True)
    k,upper=p['k'],p['upper']
    # Different route from the substitution used in the explanations:
    # symbolic primitive with differentiation and independently evaluated limits.
    f=x*sp.exp(k*x*x)
    primitive=sp.integrate(f,x)
    assert sp.simplify(sp.diff(primitive,x)-f)==0
    return sp.simplify(primitive.subs(x,upper)-primitive.subs(x,0))

def test_v154_answer_oracles_and_no_auto_certification():
    methods=read('V154_CANDIDATE_METHODS.jsonl')
    questions=read('V154_VERIFIED_ANSWERS_PENDING_REVIEW.jsonl')
    assert len(methods)==2 and len(questions)==20
    assert len({m['method_id'] for m in methods})==2
    assert len({q['question'] for q in questions})==20
    assert len({q['id'] for q in questions})==20
    assert Counter(q['method_id'] for q in questions)=={m['method_id']:10 for m in methods}
    assert Counter(q['format'] for q in questions)=={'trac_nghiem':14,'tu_luan':4,'dung_sai':2}
    assert all(m['independence_certified'] is False and not m['published'] for m in methods)
    for q in questions:
        actual=independent_oracle(q)
        answer=sp.sympify(q['canonical_answer'])
        assert sp.simplify(actual-answer)==0
        assert len(q['solution'])>=120
        assert q['independence_certified'] is False and q['published'] is False
        if q['format']=='trac_nghiem':
            values=[sp.sympify(v) for v in q['options'].values()]
            assert len(values)==4
            assert len({sp.simplify(v) for v in values})==4
            assert sum(sp.simplify(v-actual)==0 for v in values)==1
            assert sp.simplify(sp.sympify(q['options'][q['answer']])-actual)==0
        elif q['format']=='tu_luan':
            assert sp.simplify(sp.sympify(q['answer'])-actual)==0
        else:
            assert q['answer']=='Sai'
            assert sp.simplify(sp.sympify(q['asserted_answer'])-actual)!=0
