"""Reproducible four-method research pilot. All content remains pending expert review.

The enumerative oracle lives separately in backend/tests/test_v153_research.py.
"""
from fractions import Fraction
from itertools import combinations
from math import comb, gcd
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
METHODS = [
    ('v153_00', 10, 'tap_hop', 'Đếm tập con có nhóm bắt buộc và nhóm bị loại',
     'chọn k-r phần tử từ n-r-f phần tử còn lại sau khi ép r phần tử có mặt và loại f phần tử'),
    ('v153_01', 10, 'menh_de_tap_hop', 'Đếm hợp hai tập bội số bằng nguyên lý bù trừ',
     'đếm bội số của a và b trong đoạn nguyên rồi trừ bội số chung của BCNN(a,b)'),
    ('v153_02', 11, 'day_so_truy_hoi_11', 'Giải truy hồi tuyến tính cấp một có hằng số',
     'khử hằng số bằng điểm bất động của truy hồi u(n+1)=a*u(n)+b rồi tìm công thức tường minh'),
    ('v153_03', 12, 'xac_suat_12', 'Xác suất siêu bội khi chọn ngẫu nhiên không hoàn lại',
     'đếm số tổ hợp chọn đúng k phần tử thành công và d-k phần tử không thành công trên tổng số tổ hợp'),
]


def items():
    for i in range(10):
        # A: arbitrary labels A={1,...,n}, R={1,...,r}, F={r+1,...,r+f}.
        n=8+i%4; r=1+i%3; f=1+(i//2)%2; k=r+2+(i//3)%2
        total=comb(n-r-f,k-r)
        q=(f'Cho A={{1,2,...,{n}}}. Hỏi có bao nhiêu tập con B của A có đúng {k} phần tử, '
           f'bắt buộc chứa mọi phần tử của R={{1,...,{r}}} và không chứa phần tử nào của '
           f'F={{{", ".join(map(str,range(r+1,r+f+1)))}}}?')
        s=(f'Tập R có {r} phần tử đã chọn, còn {k-r} vị trí cần điền. '
           f'Loại {f} phần tử F và {r} phần tử R đã cố định, còn {n-r-f} phần tử tự do. '
           f'Áp dụng công thức tổ hợp C({n-r-f},{k-r}) = {total}.')
        yield 0,i, {'n':n,'r':r,'f':f,'k':k},q,s,Fraction(total), 'enumerate_subsets'
        # B: avoid a|b so all three disjoint classes are nonempty.
        a,b=[(4,6),(5,8),(6,9),(4,7),(6,10)][i%5]
        N=60+9*i
        lcm=a*b//gcd(a,b)
        result=N//a+N//b-N//lcm
        q=f'Trong các số nguyên từ 1 đến {N}, có bao nhiêu số chia hết cho {a} hoặc {b}?'
        s=(f'Có ⌊{N}/{a}⌋={N//a} số chia hết cho {a}; '
           f'⌊{N}/{b}⌋={N//b} số chia hết cho {b}. '
           f'Bội chung là bội BCNN({a},{b})={lcm}, có ⌊{N}/{lcm}⌋={N//lcm} số. '
           f'Nguyên lý bù trừ: {N//a}+{N//b}−{N//lcm}={result}.')
        yield 1,i, {'N':N,'a':a,'b':b},q,s,Fraction(result),'enumerate_divisible'
        # C: positive integer coefficients, fixed initial term.
        a=2+i%3; b=1+(i*2)%7; nterm=3+i%4; u0=i%5
        value=a**nterm*u0+b*(a**nterm-1)//(a-1)
        q=(f'Dãy số xác định bởi u₀={u0} và uₙ₊₁={a}uₙ+{b} với n≥0. '
           f'Tính u_{nterm}.')
        s=(f'Tìm điểm bất động c thỏa c={a}c+{b}, suy ra c=−{b}/({a}−1). '
           f'Đặt vₙ=uₙ−c thì vₙ₊₁={a}vₙ. '
           f'Vậy uₙ={a}^n×{u0}+{b}×({a}^n−1)/({a}−1). '
           f'Thay n={nterm}, được u_{nterm}={value}.')
        yield 2,i, {'a':a,'b':b,'n':nterm,'u0':u0},q,s,Fraction(value),'iterate_recurrence'
        # D: hypergeometric, exact rational answer.
        red=5+i%4; blue=5+(i//2)%4; draws=3+i%3; target=1+i%3
        favorable=comb(red,target)*comb(blue,draws-target)
        all_samples=comb(red+blue,draws)
        prob=Fraction(favorable,all_samples)
        q=(f'Một hộp có {red} bi đỏ và {blue} bi xanh, rút đồng thời {draws} bi ngẫu nhiên '
           f'(không hoàn lại). Xác suất rút đúng {target} bi đỏ là bao nhiêu?')
        s=(f'Số cách rút {draws} bi từ {red+blue} bi là C({red+blue},{draws})={all_samples}. '
           f'Số cách rút đúng {target} bi đỏ và {draws-target} bi xanh là '
           f'C({red},{target})×C({blue},{draws-target})={favorable}. '
           f'Xác suất bằng {favorable}/{all_samples}={prob}.')
        yield 3,i, {'red':red,'blue':blue,'draws':draws,'target':target},q,s,prob,'enumerate_color_selections'


def fmt(x):
    return str(x) if x.denominator==1 else f'{x.numerator}/{x.denominator}'


def build():
    ms=[];qs=[]
    for mid,grade,topic,title,method in METHODS:
        ms.append({'grade':grade,'topic':topic,'method_id':mid,'title':title,'solving_method':method,
                   'shared_core_method':False,'questions_expected':10,'independence_certified':False,
                   'published':False,'review_status':'pending-expert-review',
                   'novelty_note':'Unverified against historical mathematical methods. Candidate only.'})
    for index,i,params,q,s,answer,oracle in items():
        mid=METHODS[index][0]
        mode='trac_nghiem' if i<7 else 'tu_luan' if i<9 else 'dung_sai'
        rec={'id':f'{mid}_{i:02d}','method_id':mid,'topic':METHODS[index][2],
             'grade':METHODS[index][1],'question':q,'solution':s,'canonical_answer':fmt(answer),
             'answer_oracle_match':None,'format':mode,'published':False,
             'independence_certified':False,'review_status':'pending-expert-review',
             'oracle_method':oracle,'parameters':params}
        if mode=='trac_nghiem':
            if answer.denominator==1:
                choices=[answer, answer+1,answer+2,answer-1]
            else:
                # Closely-spaced but different probabilities; all remain in [0,1].
                choices=[answer, Fraction(answer.numerator+1,answer.denominator),
                         Fraction(max(0,answer.numerator-1),answer.denominator),
                         Fraction(answer.numerator+2,answer.denominator)]
                if len(set(choices))!=4 or any(c<0 or c>1 for c in choices):
                    choices=[answer,Fraction(1,2),Fraction(1,3),Fraction(2,3)]
            if len(set(choices))!=4 or any(c<0 for c in choices):
                raise ValueError('invalid MCQ distractors')
            options={key:fmt(value) for key,value in zip('ABCD',choices[i%4:]+choices[:i%4])}
            assert list(options.values()).count(fmt(answer))==1
            correct=next(key for key,v in options.items() if v==fmt(answer))
            rec.update({'options':options,'answer':correct,'correct_option':correct})
        elif mode=='tu_luan':
            rec['answer']=fmt(answer)
        else:
            asserted=answer+1
            # explicit false proposition validated against independent oracle in tests.
            rec['question']=q+' Khẳng định: kết quả bằng '+fmt(asserted)+'. Đúng hay sai?'
            rec.update({'answer':'Sai','asserted_answer':fmt(asserted)})
            rec['solution']+=' Vì '+fmt(asserted)+' khác '+fmt(answer)+', khẳng định đã cho sai.'
        qs.append(rec)
    assert len(ms)==4 and len(qs)==40
    (HERE/'V153_CANDIDATE_METHODS.jsonl').write_text(''.join(json.dumps(m,ensure_ascii=False,sort_keys=True)+'\n' for m in ms),encoding='utf8')
    (HERE/'V153_REVIEW_QUESTIONS.jsonl').write_text(''.join(json.dumps(q,ensure_ascii=False,sort_keys=True)+'\n' for q in qs),encoding='utf8')
    return ms,qs


if __name__=='__main__':
    ms,qs=build()
    print(len(ms), 'pending method candidates;',len(qs),'pending questions')
