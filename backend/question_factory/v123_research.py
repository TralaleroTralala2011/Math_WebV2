"""V123: research backlog of cross-scenario candidate *objectives*, NOT 1050 new mathematical methods.

All seven objective operators perform nontrivial operations on the answers of a
previously authored, topic-specific V121 problem. They are candidate *composite*
problems. They share a core solving method and MUST NOT count as globally
independent archetypes; explicit flags prevent publishing without expert review.
The module is deterministic and does not use untrusted sympify/eval input.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from sympy import Add, Integer, Max, Min, Rational, simplify, sqrt, sstr
import json, re

from . import v121_research as source

OPERATIONS = {
    'delta': ('Biến thiên tuyệt đối giữa hai bộ dữ kiện', 'difference-of-two-scenario-results'),
    'total': ('Tổng kết quả từ ba tình huống', 'aggregation-sum-three-scenarios'),
    'maximum': ('Tối ưu kết quả trong ba phương án', 'finite-optimization-max-three-scenarios'),
    'median': ('Trung vị của ba kết quả', 'order-statistic-median-three-scenarios'),
    'curvature': ('Đánh giá độ biến thiên bậc hai', 'second-finite-difference-three-scenarios'),
    'threshold': ('Đếm phương án vượt mức chuẩn', 'count-strict-inequality-four-scenarios'),
    'variance': ('Phương sai của ba kết quả', 'dispersion-mean-square-three-scenarios'),
    'range': ('Độ rộng khoảng biến thiên của ba kết quả', 'finite-range-max-minus-min'),
}
FORMATS=('tra_loi_ngan','trac_nghiem','dung_sai','tu_luan_ngan','van_dung')

@dataclass(frozen=True)
class Method:
    family:str
    topic:str
    title:str
    signature:str
    skill:str
    grade:int
    difficulty:str='nâng cao'
    real_world:bool=False
    source_family:str=''
    operator:str=''
    shared_core_method:bool=True
    independence_certified:bool=False

CATALOG=json.loads(Path(__file__).with_name('catalog_150.json').read_text(encoding='utf8'))
METHODS=[];BY_ID={}
for topic in CATALOG:
    tid=topic['id']
    # Avoid two source formulas whose answer is constant for all ten cases.
    anchor='b' if tid in ('g10_geom_circle_angles','g11_geom_space_proof') else 'a'
    original=source.BY_ID['v121_'+anchor+'_'+tid]
    for op,(name,concept) in OPERATIONS.items():
        if tid=='ham_logarit' and op=='variance':continue
        if tid!='ham_logarit' and op=='range':continue
        family=f'v123_{op}_{tid}'
        m=Method(family,tid,f'{name}: {original.title}',
                 f'v123:{concept}:{original.signature}',
                 f'Kiến thức nguồn: {original.title}. Phương pháp bổ sung: {name.lower()}.',
                 topic['grade'], 'nâng cao', original.real_world,
                 original.family,op)
        METHODS.append(m);BY_ID[family]=m
FAMILIES=frozenset(BY_ID)
assert len(METHODS)==1050 and len(FAMILIES)==1050

@lru_cache(maxsize=1500)
def _base(family, i):
    if not isinstance(i,int) or i not in range(10):raise ValueError('invalid case index')
    p=source.params_for(i)
    q=source.SPEC_BY_FAMILY[family]
    stem=q[0].format(**p).strip()
    val=simplify(source.numeric_value(family,p))
    if val.is_real is False or val.is_finite is False:
        raise ValueError('invalid source answer')
    return stem,val,q[2],q[1]

def _equals(a,b):return simplify(a-b)==0

def _sort(vals):
    """Exact original expressions, numeric key used only for comparisons."""
    return sorted(vals, key=lambda v:float(v.evalf(40)))

def _pairwise_var(vals):
    n=len(vals)
    return simplify(sum((vals[i]-vals[j])**2 for i in range(n) for j in range(i+1,n))/Integer(n*n))

def _solve(op, vals):
    if op=='delta':
        return simplify(vals[1]-vals[0]),f'Độ thay đổi Δ = {vals[1]} − ({vals[0]}).',simplify(vals[1]+(-vals[0]))
    if op=='total':
        return simplify(sum(vals)),f'Cộng các kết quả: S = '+ ' + '.join(f'({v})' for v in vals)+'.',simplify(Add(*vals))
    if op=='maximum':
        return _sort(vals)[-1],f'So sánh chính xác {", ".join(map(str, vals))} và lấy số lớn nhất.',simplify(Max(*vals))
    if op=='median':
        ordered=_sort(vals)
        return ordered[1],f'Xếp ba kết quả theo thứ tự tăng dần: {", ".join(map(str, ordered))}, chọn số ở vị trí giữa.',simplify(sum(vals)-Min(*vals)-Max(*vals))
    if op=='curvature':
        return simplify(vals[2]-2*vals[1]+vals[0]),f'Hiệu sai phân bậc hai Δ² = ({vals[2]}) − 2×({vals[1]}) + ({vals[0]}).',simplify((vals[2]-vals[1])-(vals[1]-vals[0]))
    if op=='threshold':
        base=vals[0]
        num=sum(int(float((v-base).evalf(40))>1e-18) for v in vals[1:])
        ordered=_sort(vals[1:])
        second=sum(1 for v in ordered if v.is_real is True and v.compare(base)>0) if False else sum(1 for v in ordered if float((v-base).evalf(40))>1e-18)
        return Integer(num),f'Lấy kết quả A={base} làm ngưỡng. So lần lượt các phương án B, C, D và đếm số trường hợp lớn hơn A: {num}.',Integer(second)
    if op=='range':
        maximum=_sort(vals)[-1];minimum=_sort(vals)[0]
        return simplify(maximum-minimum),f'Độ rộng khoảng biến thiên = {maximum} − ({minimum}).',simplify(Max(*vals)-Min(*vals))
    if op=='variance':
        mean=simplify(sum(vals)/3)
        direct=simplify(sum((v-mean)**2 for v in vals)/3)
        return direct,f'Đặt trung bình m=({" + ".join(map(str, vals))})/3={mean}; phương sai σ²=∑(xᵢ−m)²/3={direct}.',_pairwise_var(vals)
    raise ValueError('unsupported operator')

def _indices(op, i):
    n=2 if op=='delta' else 4 if op=='threshold' else 3
    return tuple((i+j)%10 for j in range(n))

def _instruction(op):
    return {
        'delta':'Tính kết quả B trừ kết quả A. Không làm tròn.',
        'total':'Tính tổng ba đáp số A, B, C.',
        'maximum':'Tìm GIÁ TRỊ LỚN NHẤT trong ba kết quả A, B, C (không hỏi phương án nào).',
        'median':'Tìm TRUNG VỊ của ba kết quả A, B, C.',
        'curvature':'Tính sai phân bậc hai: C − 2B + A.',
        'threshold':'Dùng đáp số A làm ngưỡng. Có bao nhiêu đáp số trong B, C, D LỚN HƠN NGHIÊM NGẶT A?',
        'variance':'Tính PHƯƠNG SAI TỔNG THỂ của ba đáp số A, B, C (chia cho 3, không chia cho 2).',
        'range':'Tính hiệu giữa kết quả lớn nhất và nhỏ nhất trong ba tình huống A, B, C.',
    }[op]

def _distractors(value):
    result=[]
    for x in (value+1,value-1,value+2,2*value,value/2,value+3,value-2):
        x=simplify(x)
        if _equals(x,value) or any(_equals(x,v) for v in result):continue
        result.append(x)
        if len(result)==3:break
    assert len(result)==3
    return result

def _fingerprint(s):return sha256(re.sub(r'\s+',' ',s.strip().casefold()).encode('utf8')).hexdigest()

def generate(family,ordinal,difficulty=None,seed_key=None):
    if family not in FAMILIES or type(ordinal) is not int or ordinal not in range(10):
        raise ValueError('unknown family or invalid ordinal')
    m=BY_ID[family]
    ids=_indices(m.operator,ordinal)
    data=[_base(m.source_family,i) for i in ids]
    vals=[x[1] for x in data]
    val,explanation,oracle=_solve(m.operator,vals)
    if not _equals(val,oracle):raise ValueError('operator oracle mismatch')
    labels='ABCD'
    lines=[f'{labels[j]}. {item[0]}' for j,item in enumerate(data)]
    question=(f'Chuyên đề: {next(t["name"] for t in CATALOG if t["id"]==m.topic)}. '
              f'Cho các tình huống TOÁN HỌC ĐỘC LẬP sau, đều giải bằng cùng kiến thức nguồn. '
              + ' '.join(lines)+' '+_instruction(m.operator))
    why=data[0][2]
    solution=('Bước 1. Mỗi tình huống phải giải theo kiến thức nền: '+why+' '
        'Bước 2. Kết quả chính xác của từng tình huống: '
        +'; '.join(f'{labels[j]} = {vals[j]}' for j in range(len(vals)))+'. '
        'Bước 3. Áp dụng phép xử lý bổ sung của dạng này: '+explanation+
        f' Bước 4. Đáp số chính xác là {val}.')
    fmt=FORMATS[ordinal%5];extra={};answer=str(val)
    if fmt=='trac_nghiem':
        opts=_distractors(val);correct=(ordinal+ordinal//5)%4;opts.insert(correct,val)
        extra={'options':[str(x) for x in opts],'correct_index':correct}
        question+=' Chọn một đáp án đúng trong bốn phương án.'
        solution+=f' Trong trắc nghiệm, phương án đúng là {"ABCD"[correct]}.'
    elif fmt=='dung_sai':
        assertion=val if ordinal<5 else val+1
        truth=_equals(assertion,val)
        extra={'assertion_value':str(assertion),'truth':bool(truth)}
        answer='Đúng' if truth else 'Sai'
        question+=f' Xác định đúng/sai cho nhận định: đáp số bằng {assertion}.'
        solution+=f' Nhận định {"đúng" if truth else "sai"}.'
    elif fmt=='tu_luan_ngan':question+=' Trình bày lời giải theo các bước.'
    elif fmt=='van_dung':question+=' Giải thích ý nghĩa và thao tác so sánh/tổng hợp được sử dụng.'
    return dict(family=family,topic_id=m.topic,ordinal=ordinal,
        params={'scenario_indices':list(ids),'anchor_family':m.source_family},
        stem=question,answer=answer,solution=solution,numeric_result=str(val),
        question_type=fmt,difficulty=difficulty or m.difficulty,
        skill=m.skill,method_signature=m.signature,
        method_review_status='pending-expert-review',independence_certified=False,
        shared_core_method=True,concept_reuse_risk='high',
        seed_key=str(seed_key or ''),fingerprint=_fingerprint(question),
        operator_arithmetic_checked=True,**extra)

def verify(record):
    try:
        fam=record.get('family');i=record.get('ordinal')
        if fam not in FAMILIES or type(i) is not int or i not in range(10):
            return False,{'error':'unknown family or invalid ordinal'}
        expected=generate(fam,i,record.get('difficulty'),record.get('seed_key'))
        if record!=expected:return False,{'error':'record differs from recomputed question'}
        ids=_indices(BY_ID[fam].operator,i)
        vals=[_base(BY_ID[fam].source_family,j)[1] for j in ids]
        result,_,oracle=_solve(BY_ID[fam].operator,vals)
        if not _equals(result,oracle) or record['numeric_result']!=str(result):
            return False,{'error':'arithmetic or oracle mismatch'}
        if len(record['solution'])<180:return False,{'error':'solution too short'}
        if record['question_type']=='trac_nghiem':
            options=record['options'];idx=record['correct_index']
            if len(options)!=4 or len(set(options))!=4 or options[idx]!=str(result):
                return False,{'error':'multiple choice verification failed'}
        if record['question_type']=='dung_sai' and record['answer']!=('Đúng' if record['truth'] else 'Sai'):
            return False,{'error':'true-false verification failed'}
        return True,{'arithmetic_checked':True,'oracle_checked':True,
                     'global_independence':'unverified-shared-core-method',
                     'pedagogical_review':'required','publication_blocked':True}
    except Exception as ex:return False,{'error':f'{type(ex).__name__}: {ex}'}

def export(out):
    folder=Path(out);folder.mkdir(parents=True,exist_ok=True)
    forms=folder/'V123_1050_CANDIDATE_OBJECTIVES.jsonl'
    questions=folder/'V123_10500_WORKED_QUESTIONS.jsonl'
    by_topic=Counter();by_format=Counter();unique=set();bad=[]
    with forms.open('w',encoding='utf8') as f,questions.open('w',encoding='utf8') as q:
        for m in METHODS:
            f.write(json.dumps({**m.__dict__,'review_status':'pending-expert-review',
                'novelty_warning':'Composite objective sharing source method; may duplicate reasoning',
                'published':False},ensure_ascii=False)+'\n')
            for i in range(10):
                item=generate(m.family,i)
                ok,detail=verify(item)
                if not ok:bad.append((m.family,i,detail));raise ValueError(str(bad[-1]))
                if item['fingerprint'] in unique:raise ValueError('duplicate V123 prompt '+m.family)
                unique.add(item['fingerprint']);by_topic[m.topic]+=1;by_format[item['question_type']]+=1
                q.write(json.dumps({**item,'verification':detail},ensure_ascii=False)+'\n')
    assert len(unique)==10500 and len(by_topic)==150 and set(by_topic.values())=={70}
    return {'candidate_composite_objectives':len(METHODS),
        'source_parent_methods':150,'topics_covered':len(by_topic),
        'worked_questions_arithmetic_checked':len(unique),
        'formats':dict(by_format), 'globally_certified_independent_forms':0,
        'near_method_risk':'all 1050 share parent method; require expert review',
        'published_forms':0}
