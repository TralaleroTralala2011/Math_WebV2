"""Independent oracle checks: brute-force enumeration / recurrence, not copy of formula."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'V153_RESEARCH'

def load(file):
    return [json.loads(x) for x in (DATA/file).read_text(encoding='utf-8').splitlines()]

def brute(method, p):
    if method=='v153_00':
        n,r,f,k=(p[t] for t in ('n','r','f','k'))
        return Fraction(sum(1 for sample in combinations(range(1,n+1),k)
                            if set(range(1,r+1))<=set(sample)
                            and not set(range(r+1,r+f+1))&set(sample)))
    if method=='v153_01':
        N,a,b=(p[t] for t in ('N','a','b'))
        return Fraction(sum(i%a==0 or i%b==0 for i in range(1,N+1)))
    if method=='v153_02':
        x=p['u0']
        for _ in range(p['n']): x=p['a']*x+p['b']
        return Fraction(x)
    if method=='v153_03':
        red,blue,draws,target=(p[t] for t in ('red','blue','draws','target'))
        good=total=0
        for picks in combinations(range(red+blue),draws):
            total+=1
            good+=sum(v<red for v in picks)==target
        return Fraction(good,total)
    raise AssertionError(method)


def test_candidate_count_schema_and_independent_answers():
    methods=load('V153_CANDIDATE_METHODS.jsonl')
    questions=load('V153_REVIEW_QUESTIONS.jsonl')
    assert len(methods)==4 and len(questions)==40
    assert all(not m['independence_certified'] and not m['published'] for m in methods)
    assert len({m['method_id'] for m in methods})==4
    assert len({q['id'] for q in questions})==40
    assert len({q['question'] for q in questions})==40
    assert Counter(q['method_id'] for q in questions)=={m['method_id']:10 for m in methods}
    assert Counter(q['format'] for q in questions)=={'trac_nghiem':28,'tu_luan':8,'dung_sai':4}
    for q in questions:
        actual=brute(q['method_id'],q['parameters'])
        assert Fraction(q['canonical_answer'])==actual
        assert q['solution'] and len(q['solution'])>=100
        assert not q['published'] and not q['independence_certified']
        if q['format']=='trac_nghiem':
            values=[Fraction(v) for v in q['options'].values()]
            assert len(set(values))==4
            assert sum(value==actual for value in values)==1
            assert Fraction(q['options'][q['answer']])==actual
        elif q['format']=='tu_luan':
            assert Fraction(q['answer'])==actual
        else:
            assert q['answer']=='Sai' and Fraction(q['asserted_answer'])!=actual
