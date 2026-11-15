"""Conservative MCQ distractor repair for one audited, obvious-answer pattern.

Does NOT change the question, correct answer, solution or source database.
Only replaces choices when the exact correct value is a scalar fraction over a
square root and the alternatives visibly reveal the right answer by notation.
"""
from __future__ import annotations

import math
import random
import re
from .validator import options_equivalent

_RADICAL = re.compile(r'^\s*([+-]?\d+)\s*/\s*√\s*(?:\(\s*(\d+)\s*\)|(\d+))\s*$')


def improve_mcq(q: dict) -> dict:
    if q.get('question_type') != 'multiple_choice':
        return q
    choices = q.get('options')
    if not isinstance(choices,list) or len(choices)!=4:
        return q
    answer = str(q.get('answer','')).strip()
    match = _RADICAL.fullmatch(answer)
    if not match or answer not in choices:
        return q
    numerator=int(match.group(1))
    denominator=int(match.group(2) or match.group(3))
    if denominator<=1 or numerator==0:
        return q
    # A valid mixed-format set may intentionally require equivalence
    # reasoning. Replace only when the radical answer is the conspicuous
    # *only* radically formatted choice.
    candidates=[str(x) for x in choices if x != answer]
    matching=sum(bool(_RADICAL.fullmatch(x)) for x in candidates)
    if matching>=2:
        return q
    # Keep trig ratios in [-1,1] and all choices sharing the same kind of
    # denominator, without assuming an arbitrary wrong number is correct.
    bound=math.sqrt(denominator)
    sign = 1 if numerator>0 else -1
    wrong=[]
    for delta in (1,-1,2,-2,3,-3,4,-4):
        n=numerator+delta
        if n==numerator or n==0:
            continue
        if ('sin' in str(q.get('question','')).casefold() or 'cos' in str(q.get('question','')).casefold()) and abs(n)>=bound:
            continue
        val=f'{n}/√({denominator})'
        if not any(options_equivalent(val,other) for other in [answer,*wrong]):
            wrong.append(val)
        if len(wrong)==3:
            break
    if len(wrong)<3:
        return q  # Keep original intact if the safe repair pool is too small.
    repaired=[answer,*wrong]
    random.shuffle(repaired)
    q['options']=repaired
    q['distractors_refined']='same_form_radical'
    return q
