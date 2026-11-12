"""V121 candidate problem objectives: two authored specifications per official topic.

CAVEATS: A stable family ID, different numeric prompts, successful SymPy evaluation,
non-identical stems and an independent recomputation of the expression DO NOT
establish globally independent mathematical methods or expert-level validity.
All 300 are permanently quarantined until explicitly reviewed in the existing DB.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json, re
from sympy import (Abs, Integer, Symbol, Rational, sqrt, pi, Max, Min, ceiling,
                   floor, binomial, factorial, fibonacci, exp, log, simplify, sympify)
from .v120_research import _alternatives, _is_prob

FIELDS=('a','b','c','d','n','N','r')
FUNCTIONS={'Abs':Abs,'sqrt':sqrt,'pi':pi,'Max':Max,'Min':Min,'ceiling':ceiling,
           'floor':floor,'binomial':binomial,'factorial':factorial,
           'fibonacci':fibonacci,'exp':exp,'log':log,'Rational':Rational}
FORMATS=('tra_loi_ngan','trac_nghiem','dung_sai','tu_luan_ngan','van_dung')

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

METHODS=[]
SPEC_BY_FAMILY={}

def load():
    topics=json.loads(Path(__file__).with_name('catalog_150.json').read_text(encoding='utf8'))
    specs=Path(__file__).with_name('v121_specs.txt').read_text(encoding='utf8').splitlines()
    symbols={f:Symbol(f,positive=True,integer=True) for f in FIELDS}
    found=set()
    for line in specs:
        if not line.strip() or line.lstrip().startswith('#'):continue
        parts=[s.strip() for s in line.split('§')]
        if len(parts)!=9:raise ValueError('Expected 9 columns in V121 specification: '+line[:140])
        row=int(parts[0]);
        if row<1 or row>len(topics) or row in found:raise ValueError('bad/duplicate official index')
        found.add(row)
        topic=topics[row-1]
        for label,offset in [('a',1),('b',5)]:
            title,stem,formula,reason=parts[offset:offset+4]
            if min(len(title),len(stem),len(reason))<8 or not formula:raise ValueError('missing method content')
            if any(f not in (*FIELDS,'twice_a') for f in re.findall(r'\{(\w+)\}',stem)):
                raise ValueError('bad placeholder '+str(row))
            expression=sympify(formula,locals={**FUNCTIONS,**symbols},evaluate=True)
            if expression.free_symbols-set(symbols.values()):raise ValueError('unknown symbol '+str(row))
            family=f'v121_{label}_{topic["id"]}'
            if family in SPEC_BY_FAMILY:raise ValueError('duplicate family')
            signature=f'v121:{topic["id"]}:{label}:' + re.sub(r'\W+','-',title.casefold())
            real_world=any(s in stem.casefold() for s in ('triệu','nghìn','xưởng','cửa hàng','học sinh','lãi','sản phẩm','hộp','viên','phép thử','tài sản','chuyển động','chi phí','dân số','doanh thu'))
            method=Method(family,topic['id'],title,signature,reason,topic['grade'],
                'nâng cao' if 'advanced' in topic['id'] or 'nang_cao' in topic['id'] else 'trung cấp',real_world)
            METHODS.append(method)
            SPEC_BY_FAMILY[family]=(stem,formula,reason,expression)
    if len(found)!=150 or len(METHODS)!=300:raise ValueError('V121 must have 2 methods in every topic')

load()
BY_ID={m.family:m for m in METHODS}
FAMILIES=frozenset(BY_ID)


def params_for(ordinal):
    if type(ordinal) is not int or ordinal not in range(10):
        raise ValueError('ordinal 0..9')
    k=ordinal+2
    a=k+2;b=a+1;c=a+2+(k%3);d=c+1+(k%4);n=k+5;r=k+2
    N=a*b*(k+2)+k
    return dict(a=a,b=b,c=c,d=d,n=n,r=r,N=N,twice_a=2*a)


def numeric_value(family,params):
    if family not in FAMILIES:raise ValueError('unknown V121 family')
    syms={f:Symbol(f,positive=True,integer=True) for f in FIELDS}
    value=SPEC_BY_FAMILY[family][3].subs({syms[f]:Integer(params[f]) for f in FIELDS})
    return simplify(value)


def fingerprint(stem):
    return sha256(re.sub(r'\s+',' ',stem.strip().casefold()).encode('utf8')).hexdigest()


def generate(family,ordinal,difficulty=None,seed_key=None):
    if family not in FAMILIES:raise ValueError('unknown family')
    p=params_for(ordinal)
    template,formula,reason,_=SPEC_BY_FAMILY[family]
    m=BY_ID[family]
    stem=template.format(**p)
    val=numeric_value(family,p)
    if val.is_finite is False or val.is_real is False or val.has(Symbol):
        raise ValueError(f'undefined value {family} {ordinal}: {val}')
    fmt=FORMATS[ordinal%5]
    vals=', '.join(f'{f}={p[f]}' for f in FIELDS if re.search(r'\b'+f+r'\b',formula))
    # Show the actual substitution in addition to the conceptual method.
    substituted=re.sub(r'\b(?:a|b|c|d|n|N|r)\b',lambda match:str(p[match.group(0)]),formula)
    pretty=lambda text:text.replace('**','^').replace('*','×').replace('pi','π')
    solution=(f'Bước 1. {reason} '
              f'Bước 2. Lập biểu thức toán học: {pretty(formula)}. '
              f'Bước 3. Thay các dữ kiện {vals}, ta có: {pretty(substituted)}. '
              f'Bước 4. Tính toán và rút gọn được kết quả chính xác: {val}.')
    answer=str(val)
    extra={}
    if fmt=='trac_nghiem':
        choices=_alternatives(val)
        ix=(ordinal//5+ordinal)%4
        choices.insert(ix,val)
        extra={'options':[str(c) for c in choices],'correct_index':ix}
        stem+=' Chọn đúng một đáp án trong bốn phương án.'
        solution+=f' Đáp án đúng là {"ABCD"[ix]}.'
    elif fmt=='dung_sai':
        assertion=val if ordinal%2==0 else (val/2 if val!=0 and _is_prob(val) else val+1)
        assertion=simplify(assertion)
        truth=simplify(assertion-val)==0
        extra={'assertion_value':str(assertion),'truth':bool(truth)}
        answer='Đúng' if truth else 'Sai'
        stem+=f' Nhận định "Kết quả là {assertion}" đúng hay sai?'
        solution+=f' Kiểm tra với kết quả {val}: nhận định {"đúng" if truth else "sai"}.'
    elif fmt=='tu_luan_ngan':
        stem+=' Trình bày phương pháp và đáp số chính xác.'
    elif fmt=='van_dung':
        fmt='toan_thuc_te' if m.real_world else 'van_dung'
        stem+=' Nêu cách áp dụng kiến thức để giải.'
    else:stem+=' Viết kết quả chính xác, không làm tròn.'
    return dict(family=family,ordinal=ordinal,params=p,stem=stem,answer=answer,
        solution=solution,difficulty=difficulty or m.difficulty,question_type=fmt,
        numeric_result=str(val),topic_id=m.topic,method_signature=m.signature,
        skill=m.skill,method_review_status='pending-expert-review',
        independence_certified=False,seed_key=str(seed_key or ''),fingerprint=fingerprint(stem),**extra)


def verify(record):
    """Checks arithmetic, MCQ/TF semantics, record integrity; not expert mathematics."""
    try:
        family=record.get('family');i=record.get('ordinal')
        if family not in FAMILIES or type(i) is not int or i not in range(10):
            return False,{'error':'invalid family or ordinal'}
        expected=generate(family,i,record.get('difficulty'),record.get('seed_key'))
        if expected!=record:return False,{'error':'record integrity or answer mismatch'}
        val=numeric_value(family,record['params'])
        if val.is_real is False or val.is_finite is False:
            return False,{'error':'nonreal or undefined numeric value'}
        if record['question_type']=='trac_nghiem':
            opts=[sympify(s,locals=FUNCTIONS) for s in record['options']]
            if len(opts)!=4 or len({str(simplify(o)) for o in opts})!=4 or sum(simplify(o-val)==0 for o in opts)!=1:
                return False,{'error':'nonunique MCQ'}
            if simplify(opts[record['correct_index']]-val)!=0:return False,{'error':'wrong correct index'}
        if record['question_type']=='dung_sai':
            assertion=sympify(record['assertion_value'],locals=FUNCTIONS)
            truth=simplify(assertion-val)==0
            if record['truth']!=bool(truth) or record['answer']!=('Đúng' if truth else 'Sai'):
                return False,{'error':'incorrect truth assertion'}
        if len(record['solution'])<75:return False,{'error':'too short explanation'}
        return True,dict(symbolic_arithmetic_check=True,record_integrity=True,
            method_independence='pending',pedagogical_accuracy='pending',publication_blocked=True)
    except Exception as exc:
        return False,{'error':f'{type(exc).__name__}: {exc}'}


def export(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    forms_file=folder/'V121_300_CANDIDATE_FORMS.jsonl'
    qs_file=folder/'V121_3000_NEW_QUESTIONS.jsonl'
    unique_stems=set();formats=Counter();topic_counts=Counter()
    with forms_file.open('w',encoding='utf8') as forms, qs_file.open('w',encoding='utf8') as qs:
        for m in METHODS:
            forms.write(json.dumps({**m.__dict__,'status':'pending-expert-review','independence_certified':False},ensure_ascii=False)+'\n')
            for i in range(10):
                row=generate(m.family,i)
                valid,proof=verify(row)
                if not valid:raise ValueError(f'failed {m.family}#{i}: {proof}')
                if row['fingerprint'] in unique_stems:
                    raise ValueError('duplicate question stem '+m.family)
                unique_stems.add(row['fingerprint']);formats[row['question_type']]+=1;topic_counts[m.topic]+=1
                qs.write(json.dumps({**row,'verification':proof},ensure_ascii=False)+'\n')
    if len(unique_stems)!=3000 or len(topic_counts)!=150 or set(topic_counts.values())!={20}:
        raise AssertionError('insufficient topic coverage')
    return dict(covered_topics=len(topic_counts),candidate_forms=len(METHODS),
                questions_with_arithmetic_checks=len(unique_stems),question_formats=dict(formats),
                certified_independent_forms=0,expert_verified_questions=0)
