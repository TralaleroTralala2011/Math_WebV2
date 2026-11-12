"""V120: 150 authored, topic-specific candidate objectives with 10 worked items each.

The precise mathematical OBJECTIVE for each topic is authored in v120_specs.txt.
These are 150 candidate archetypes, not 150 certified globally novel methods.
Unlike a numeric-ID expansion, each has its own prompt, mathematical expression,
and explanatory rule. The generator never approves or publishes them.

The verifier checks record integrity, exact symbolic answer and MCQ/true-false
semantics. It does NOT demonstrate that narrative statements or all solution
steps are pedagogically sound; those require further review.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
from hashlib import sha256
import json, re
from sympy import (Integer, Rational, pi, sqrt, exp, floor, ceiling, Abs, Max, Min,
                   binomial, factorial, simplify, sympify, Symbol, latex)

FIELDS=('a','b','c','d','n','N','r')
FUNCTIONS={'pi':pi,'sqrt':sqrt,'exp':exp,'floor':floor,'ceiling':ceiling,'Abs':Abs,
           'Max':Max,'Min':Min,'binomial':binomial,'factorial':factorial,'Rational':Rational}

@dataclass(frozen=True)
class Method:
    family:str
    topic:str
    title:str
    signature:str
    skill:str
    grade:int
    difficulty:str='trung cấp'
    real_world:bool=False

SPEC_BY_FAMILY={}
METHODS=[]


def _load():
    topics=json.loads(Path(__file__).with_name('catalog_150.json').read_text(encoding='utf8'))
    lines=Path(__file__).with_name('v120_specs.txt').read_text(encoding='utf8').splitlines()
    found=set()
    for line in lines:
        if not line.strip() or line.startswith('#'):continue
        parts=[x.strip() for x in line.split('§')]
        if len(parts)!=5:raise ValueError('bad specification columns: '+line[:150])
        num=int(parts[0]);title,stem,formula,reason=parts[1:]
        if not 1<=num<=len(topics) or num in found:raise ValueError('bad/duplicate row index')
        found.add(num)
        topic=topics[num-1]
        family='v120_topic_'+topic['id']
        if family in SPEC_BY_FAMILY:raise ValueError('duplicate topic '+family)
        # Treat authored formula as code, NEVER parse an arbitrary answer from a user.
        syms={f:Symbol(f, positive=True) for f in FIELDS}
        symbolic=sympify(formula, locals={**FUNCTIONS,**syms})
        if symbolic.free_symbols-set(syms.values()):raise ValueError('unknown symbols '+family)
        if any(f not in (*FIELDS,'twice_a') for f in re.findall(r'(?<!\{)\{(\w+)\}',stem)):
            raise ValueError('unknown prompt parameter '+family)
        m=Method(family,topic['id'],title,'v120:'+topic['id']+':'+re.sub(r'\W+','-',title.lower()),
            reason,topic['grade'],'nâng cao' if 'advanced' in topic['id'] or 'nang_cao' in topic['id'] else 'trung cấp',
            any(x in stem.lower() for x in ('tiền','hộp','xưởng','cửa hàng','tài sản','hàng rào','thử','sản phẩm','viên')))
        METHODS.append(m)
        SPEC_BY_FAMILY[family]=(stem,formula,reason,symbolic)
    if len(METHODS)!=150 or len(found)!=150:raise ValueError('incomplete V120 topic catalog')

_load()
BY_ID={m.family:m for m in METHODS}
FAMILIES=frozenset(BY_ID)
FORMATS=('tra_loi_ngan','trac_nghiem','dung_sai','tu_luan_ngan','van_dung')


def params_for(ordinal):
    if type(ordinal) is not int or not 0<=ordinal<10:raise ValueError('ordinal 0..9 required')
    k=ordinal+2
    a=k+2;b=a+1;c=a+2+(k%3);d=c+1+(k%4);n=k+5;r=2+(k%4);N=a*b*(k+2)+k
    return dict(a=a,b=b,c=c,d=d,n=n,N=N,r=r,twice_a=2*a) # deterministic per ordinal


def numeric_value(family,p):
    if family not in FAMILIES:raise ValueError('unknown family')
    symbols={f:Symbol(f,positive=True) for f in FIELDS}
    expr=SPEC_BY_FAMILY[family][3]
    return simplify(expr.subs({symbols[f]:Integer(p[f]) for f in FIELDS}))


def _fingerprint(s):
    return sha256(re.sub(r'\s+',' ',s.strip().casefold()).encode('utf8')).hexdigest()


def _is_prob(v):
    return v.is_real is True and v.is_nonnegative is True and (v-1).is_nonpositive is True


def _alternatives(value):
    v=simplify(value)
    if _is_prob(v):
        cand=[v/2,(v+1)/2,1-v,(v+2)/3,v/3,(2*v+1)/3,(3*v+1)/4]
    else:
        cand=[v+1,v-1,v+2,v-2,2*v,v/2,v+3,v-3,3*v/2]
    opts=[]
    for x in cand:
        x=simplify(x)
        if simplify(x-v)==0 or any(simplify(x-y)==0 for y in opts):continue
        if _is_prob(v) and not _is_prob(x):continue
        opts.append(x)
        if len(opts)==3:break
    if len(opts)!=3:raise ValueError('could not construct options')
    return opts


def generate(family,ordinal,difficulty=None,seed_key=None):
    if family not in FAMILIES:raise ValueError('unknown V120 family')
    p=params_for(ordinal)
    stem_pattern,formula,why,_=SPEC_BY_FAMILY[family]
    m=BY_ID[family]
    stem=stem_pattern.format(**p)
    val=numeric_value(family,p)
    if val.has(Symbol) or val.is_real is False or val.is_finite is False:
        raise ValueError('undefined or non-real answer')
    ans=str(val)
    fmt=FORMATS[ordinal%5]
    # Numerical substitution is provided explicitly, in addition to human-authored method.
    shown=', '.join(f'{x}={p[x]}' for x in FIELDS if re.search(r'\b'+x+r'\b',formula))
    solution=f'{why} Thay {shown} vào biểu thức tính được kết quả chính xác là {ans}.'
    extra={}
    if fmt=='trac_nghiem':
        opts=_alternatives(val)
        index=(ordinal//5+ordinal)%4
        opts.insert(index,val)
        extra={'options':[str(x) for x in opts], 'correct_index':index}
        stem+=' Chọn một đáp án đúng trong bốn phương án.'
        solution+=f' Phương án đúng là {"ABCD"[index]}.'
    elif fmt=='dung_sai':
        assertion=val if ordinal%2==0 else (val/2 if val!=0 and _is_prob(val) else val+1)
        assertion=simplify(assertion)
        truth=bool(simplify(assertion-val)==0)
        extra={'assertion_value':str(assertion),'truth':truth}
        ans='Đúng' if truth else 'Sai'
        stem+=f' Nhận định "Đáp số là {assertion}" đúng hay sai?'
        solution+=f' Vì kết quả tính là {val}, nhận định này {"đúng" if truth else "sai"}.'
    elif fmt=='tu_luan_ngan':
        stem+=' Trình bày các bước lập luận và ghi đáp án chính xác.'
    elif fmt=='van_dung':
        fmt='toan_thuc_te' if m.real_world else 'van_dung'
        stem+=' Giải thích cách áp dụng kiến thức để có kết quả.'
    else:
        stem+=' Ghi đáp án ở dạng chính xác.'
    return {
        'family':family,'ordinal':ordinal,'params':p,'stem':stem,'answer':ans,
        'solution':solution,'difficulty':difficulty or m.difficulty,'question_type':fmt,
        'numeric_result':str(val),'topic_id':m.topic,'method_signature':m.signature,
        'skill':m.skill,'method_review_status':'pending-expert-review','independence_certified':False,
        'seed_key':str(seed_key or ''),'fingerprint':_fingerprint(stem),**extra
    }


def verify(data):
    """Reconstruct entire authored record; recompute exact symbolic value.

    This detects mutation and arithmetic mistakes within the recorded formula,
    but DOES NOT prove mathematical correctness of the narrative prompt itself.
    """
    try:
        f=data.get('family');i=data.get('ordinal')
        if f not in FAMILIES or type(i) is not int or i not in range(10):
            return False,{'error':'invalid family or ordinal'}
        regenerated=generate(f,i,data.get('difficulty'),data.get('seed_key'))
        if regenerated!=data:return False,{'error':'record tampering or answer mismatch'}
        val=numeric_value(f,data['params'])
        if data['numeric_result']!=str(val):return False,{'error':'numeric mismatch'}
        if data['question_type']=='trac_nghiem':
            opts=[sympify(x) for x in data['options']]
            if len(opts)!=4 or sum(simplify(x-val)==0 for x in opts)!=1:
                return False,{'error':'invalid MCQ uniqueness'}
            if simplify(opts[data['correct_index']]-val)!=0:
                return False,{'error':'wrong MCQ answer position'}
        if data['question_type']=='dung_sai':
            truth=bool(simplify(sympify(data['assertion_value'])-val)==0)
            if truth!=data['truth'] or data['answer']!=('Đúng' if truth else 'Sai'):
                return False,{'error':'wrong truth value'}
        if len(data['solution'])<65:return False,{'error':'insufficient explanation'}
        return True,{'symbolic_arithmetic_check':True,'record_integrity':True,
            'pedagogical_review':'pending','independent_method_review':'pending',
            'publication_blocked':True}
    except Exception as e:
        return False,{'error':type(e).__name__+': '+str(e)}


def export(folder):
    target=Path(folder);target.mkdir(parents=True,exist_ok=True)
    forms=target/'V120_150_NEW_CANDIDATE_FORMS.jsonl'
    questions=target/'V120_1500_NEW_QUESTIONS.jsonl'
    fingerprints=set();counts=Counter();by_topic=Counter()
    with forms.open('w',encoding='utf8') as fp, questions.open('w',encoding='utf8') as fq:
        for method in METHODS:
            fp.write(json.dumps({**method.__dict__,'status':'pending-expert-review','independence_certified':False},ensure_ascii=False)+'\n')
            for ordinal in range(10):
                question=generate(method.family,ordinal)
                yes,proof=verify(question)
                if not yes:raise AssertionError((method.family,ordinal,proof))
                if question['fingerprint'] in fingerprints:raise ValueError('duplicate V120 stem '+method.family)
                fingerprints.add(question['fingerprint']);counts[question['question_type']]+=1
                by_topic[method.topic]+=1
                fq.write(json.dumps({**question,'verification':proof},ensure_ascii=False)+'\n')
    return {'topic_count':len(by_topic),'new_candidate_methods':len(METHODS),
        'new_questions_checked_arithmetically':len(fingerprints),
        'question_formats':dict(counts),'method_independence_certified':0,
        'pedagogical_accuracy_expert_certified':0}
