"""V154: two ORIGINAL research candidates, 10 worked questions each.

These are NOT certified independent from the historical bank, NOT published.
Exact answers are checked separately by backend/tests/test_v154_research.py.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import json
import sympy as sp

HERE=Path(__file__).resolve().parent
METHODS=[
    {'method_id':'v154_point_to_line_distance','grade':10,'topic':'toa_do_hinh_hoc_10',
     'title':'Khoảng cách điểm đến đường thẳng trong Oxy bằng hình chiếu trực giao',
     'solving_method':'Lập hình chiếu vuông góc theo pháp tuyến (a,b), tính tọa độ chân đường vuông góc rồi dùng định lý Pythagoras.',
     'independence_certified':False,'shared_core_method':'unknown','review_status':'pending-expert-review','published':False,
     'questions_expected':10,'novelty_note':'Phải đối chiếu các dạng hình học tọa độ cũ trước khi chứng nhận.'},
    {'method_id':'v154_exponential_substitution_integral','grade':12,'topic':'nguyen_ham_tich_phan',
     'title':'Tích phân xác định hàm x·exp(kx²) bằng đổi biến',
     'solving_method':'Đặt u=kx² để đổi biến tích phân x·e^(kx²) thành e^u du/(2k), rồi tính tại hai cận.',
     'independence_certified':False,'shared_core_method':'unknown','review_status':'pending-expert-review','published':False,
     'questions_expected':10,'novelty_note':'Phải đối chiếu những dạng đổi biến tích phân cũ trước khi chứng nhận.'},
]

def make():
    qs=[]
    normals=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29)]
    for i in range(10):
        a,b,normal=normals[i%5]
        x=i-4;y=3-i;distance=1+i%6
        c=normal*distance-a*x-b*y
        prompt=(f'Trong mặt phẳng Oxy, cho điểm P({x}; {y}) và đường thẳng '
                f'Δ: {a}x + {b}y + ({c}) = 0. Tính khoảng cách từ P đến Δ.')
        numerator=abs(a*x+b*y+c)
        solution=(f'Vectơ pháp tuyến của Δ là n=({a}; {b}), có độ dài '
                  f'√({a}²+{b}²)={normal}. Từ P, hạ đường vuông góc đến Δ. '
                  f'Tọa độ chân H=P−t·n, với t=({a}×{x}+{b}×{y}+{c})/'
                  f'({a}²+{b}²)={a*x+b*y+c}/{normal**2}. '
                  f'Suy ra PH=|t|·|n|={numerator}/{normal}={distance}.')
        q={'id':f'v154_geo_{i:02d}','method_id':METHODS[0]['method_id'],'grade':10,
           'topic':METHODS[0]['topic'],'question':prompt,'solution':solution,
           'canonical_answer':str(distance),'params':{'a':a,'b':b,'c':c,'x':x,'y':y},
           'published':False,'independence_certified':False,'review_status':'pending-expert-review'}
        if i<7:
            choices=[distance,distance+1,distance+2,Fraction(distance*normal,normal*normal)]
            assert len(set(choices))==4
            choices=choices[i%4:]+choices[:i%4]
            q.update(format='trac_nghiem',options={k:str(v) for k,v in zip('ABCD',choices)})
            q['answer']='ABCD'[choices.index(distance)]
        elif i<9:
            q.update(format='tu_luan',answer=str(distance))
        else:
            q['question']=prompt+f' Khẳng định: khoảng cách bằng {distance+1}. Đúng hay sai?'
            q.update(format='dung_sai',answer='Sai',asserted_answer=str(distance+1))
            q['solution']+=f' Vì {distance+1} khác {distance}, mệnh đề là sai.'
        qs.append(q)
    # Integral of x*exp(kx^2) from 0 to a, with k=1..5, a=2 or 3.
    for i in range(10):
        k=1+i%5; upper=2+i//5
        exponent=k*upper*upper
        exact=(sp.exp(exponent)-1)/(2*k)
        opts=[exact, (sp.exp(exponent)-1)/k,
              (sp.exp(exponent)+1)/(2*k),
              (sp.exp(exponent)-1)/(2*k*upper)]
        assert len({sp.simplify(x) for x in opts})==4
        expr=lambda x:sp.sstr(sp.expand(x))
        prompt=f'Tính tích phân I = ∫ từ 0 đến {upper} của x·e^({k}x²) dx.'
        solution=(f'Đặt u={k}x², khi đó du={2*k}x dx, hay x dx=du/{2*k}. '
                  f'Khi x=0 thì u=0, khi x={upper} thì u={exponent}. '
                  f'Vì vậy I=(1/{2*k})∫ từ 0 đến {exponent} e^u du '
                  f'=(e^{exponent}−1)/{2*k}. Đây là giá trị chính xác của tích phân.')
        q={'id':f'v154_int_{i:02d}','method_id':METHODS[1]['method_id'],'grade':12,
           'topic':METHODS[1]['topic'],'question':prompt,'solution':solution,
           'canonical_answer':expr(exact),'params':{'k':k,'upper':upper},
           'published':False,'independence_certified':False,'review_status':'pending-expert-review'}
        if i<7:
            options=opts[i%4:]+opts[:i%4]
            q.update(format='trac_nghiem',options={key:expr(v) for key,v in zip('ABCD',options)},
                     answer='ABCD'[next(j for j,v in enumerate(options) if sp.simplify(v-exact)==0)])
        elif i<9:
            q.update(format='tu_luan',answer=expr(exact))
        else:
            q['question']=prompt+f' Khẳng định I = {expr(opts[1])}. Đúng hay sai?'
            q.update(format='dung_sai',answer='Sai',asserted_answer=expr(opts[1]))
            q['solution']+=' Khẳng định đã cho thiếu hệ số 1/2 nên sai.'
        qs.append(q)
    assert Counter(q['method_id'] for q in qs)=={m['method_id']:10 for m in METHODS}
    for file,values in [('V154_CANDIDATE_METHODS.jsonl',METHODS),('V154_VERIFIED_ANSWERS_PENDING_REVIEW.jsonl',qs)]:
        (HERE/file).write_text(''.join(json.dumps(v,ensure_ascii=False,sort_keys=True)+'\n' for v in values),encoding='utf8')
    return METHODS,qs

if __name__=='__main__':
    print('Pending methods/questions:',tuple(map(len,make())))
