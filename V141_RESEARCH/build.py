"""V141: deterministic, topic-scoped research candidates. No method is certified/published.

Ten mathematically different parameterizations per candidate method. Independent
oracles inspect each answer, while novelty is deliberately left for expert review.
"""
from __future__ import annotations
import itertools
import json
import math
import random
from pathlib import Path
import sympy as S

OUT = Path(__file__).resolve().parent
CATALOG = OUT.parent/'backend/question_factory/catalog_150.json'
TOPICS = {entry['id']:entry['grade'] for entry in json.loads(CATALOG.read_text(encoding='utf-8'))}
METHODS = [
 ('ham_so_bac_hai',10,'GT lớn nhất của parabol trên đoạn','so sánh giá trị tại biên và điểm đỉnh trong đoạn'),
 ('duong_tron',10,'Xác định tâm đường tròn qua ba điểm không thẳng hàng','lấy hiệu phương trình khoảng cách để giải hệ tuyến tính'),
 ('gioi_han',11,'Giới hạn dạng (1-cos(ax))/x²','giới hạn lượng giác chuẩn hoặc khai triển Taylor cấp hai'),
 ('dao_ham',11,'Đạo hàm của hàm phân thức bậc nhất tại một điểm','quy tắc đạo hàm thương và rút gọn'),
 ('cap_so_cong',11,'Tổng các số hạng vị trí lẻ của cấp số cộng','nhận diện cấp số cộng con có công sai gấp đôi'),
 ('xac_suat_11',11,'Xác suất đúng hai thành công trong ba phép thử Bernoulli khác xác suất','cộng xác suất ba trường hợp loại trừ nhau'),
 ('bpt_mu',12,'Bất phương trình bậc hai theo ẩn phụ 2^x','đặt t=2^x rồi giải bất phương trình tích các nhân tử'),
 ('mat_phang_oxyz',12,'Tìm tham số để hai mặt phẳng vuông góc','tích vô hướng của hai vectơ pháp tuyến bằng không'),
 ('nguyen_ham_tich_phan',12,'Tích phân phân thức tuyến tính bằng logarit','đổi biến tuyến tính và định lý cơ bản của giải tích'),
 ('g12_solid_of_revolution',12,'Thể tích vành khăn của miền giữa hai đường thẳng quay quanh Ox','lấy hiệu bình phương hai bán kính và tích phân'),
 ('quy_tac_dem',10,'Số ánh xạ toàn ánh từ tập n phần tử lên tập ba phần tử','nguyên lý bù trừ kết hợp số Stirling loại hai'),
]


def oracle(m, i):
    """Return (statement, exact answer, independent answer, detailed worked solution)."""
    x=S.symbols('x',real=True)
    if m==0:
        a=-(i%4+1); h=(i%7)-3; c=5+3*i; l=-5+i//2; r=l+5+i%4
        f=lambda t: a*(t-h)**2+c
        cand=[(l,f(l)),(r,f(r))]+ ([(h,f(h))] if l<=h<=r else [])
        v=max(y for _,y in cand)
        independent=max(f(l),f(r),f(min(max(h,l),r)))
        q=f'Cho hàm số y={S.expand(a*(x-h)**2+c)} trên đoạn [{l};{r}]. Giá trị lớn nhất là bao nhiêu?'
        sol=f'Viết hàm dưới dạng y={a}(x-({h}))²+{c}, đỉnh tại x={h}. Xét hai đầu đoạn x={l}, {r}' + (f' và đỉnh x={h}' if l<=h<=r else '; đỉnh nằm ngoài đoạn') + f'. Các giá trị cần so sánh là {[(t,y) for t,y in cand]}. Vậy giá trị lớn nhất bằng {v}.'
    elif m==1:
        h=i-5;k=2-(i%6); r5=5 if i%2==0 else 13
        pts=((3,4),(4,3),(-3,4)) if r5==5 else ((5,12),(12,5),(-5,12))
        A,B,C=[(h+u,k+v) for u,v in pts]
        X,Y=S.symbols('X Y')
        eq1=S.expand((X-A[0])**2+(Y-A[1])**2-((X-B[0])**2+(Y-B[1])**2))
        eq2=S.expand((X-A[0])**2+(Y-A[1])**2-((X-C[0])**2+(Y-C[1])**2))
        center=S.solve((eq1,eq2),(X,Y), dict=True)
        assert len(center)==1
        v=(S.Integer(h),S.Integer(k))
        independent=(center[0][X],center[0][Y])
        q=f'Đường tròn đi qua ba điểm A{A}, B{B}, C{C}. Tọa độ tâm đường tròn là gì? (Viết dạng (x;y)).'
        sol=f'Gọi tâm I(X;Y). Điều kiện IA²=IB² và IA²=IC² cho hệ tuyến tính {eq1}=0; {eq2}=0 sau khi khử X²+Y². Giải hệ được X={h}, Y={k}. Kiểm tra IA²=IB²=IC²={r5*r5}. Vậy I=({h};{k}).'
    elif m==2:
        t=i+1
        v=S.Rational(t*t,2)
        independent=S.limit((1-S.cos(t*x))/x**2,x,0)
        q=f'Tính lim khi x→0 của (1−cos({t}x))/x².'
        sol=f'Đặt u={t}x, ta có (1−cos({t}x))/x² = {t*t}·(1−cos u)/u². Vì lim(u→0)(1−cos u)/u²=1/2 nên giới hạn là {v}.'
    elif m==3:
        a=1+i%5; b=2+i; c=1+(i*2)%4; d=5+i*2; t=(i%5)-2
        if c*t+d==0:d+=7
        if a*d-b*c==0:b+=1
        v=S.Rational(a*d-b*c,(c*t+d)**2)
        independent=S.diff((a*x+b)/(c*x+d),x).subs(x,t).simplify()
        q=f'Cho f(x)=({a}x+{b})/({c}x+{d}). Tính f′({t}).'
        sol=f'Quy tắc đạo hàm thương: f′(x)=({a}({c}x+{d})−{c}({a}x+{b}))/({c}x+{d})²=({a*d-b*c})/({c}x+{d})². Thay x={t}, mẫu khác 0, suy ra f′({t})={v}.'
    elif m==4:
        a=-4+i; d=(i%7)+1; n=i+3
        v=n*a+d*n*(n-1)
        independent=sum(a+2*j*d for j in range(n))
        q=f'Một cấp số cộng có u₁={a}, công sai d={d}. Tính S=u₁+u₃+...+u_({2*n-1}).'
        sol=f'Các chỉ số lẻ tạo cấp số cộng con gồm n={n} số hạng, số đầu {a}, công sai 2d={2*d}. Do đó S=n[2u₁+(n−1)2d]/2={n}({a}+({n}−1){d})={v}.'
    elif m==5:
        p=S.Rational(i+1,13);q=S.Rational((i*2)%11+1,13);r=S.Rational((i*3+2)%11+1,13)
        v=p*q*(1-r)+p*r*(1-q)+q*r*(1-p)
        probs=[p,q,r]
        independent=sum(S.prod((probs[j] if outcomes[j] else 1-probs[j]) for j in range(3)) for outcomes in itertools.product([0,1],repeat=3) if sum(outcomes)==2)
        s=lambda z: str(z)
        statement=f'Ba phép thử độc lập có xác suất thành công lần lượt {p}, {q}, {r}. Xác suất có đúng hai phép thử thành công là bao nhiêu?'
        sol=f'Đúng hai thành công có ba trường hợp rời nhau: (1,2), (1,3), (2,3). P={p}·{q}·(1−{r})+{p}·(1−{q})·{r}+(1−{p})·{q}·{r}={v}.'
        q=statement
    elif m==6:
        a=i%4; b=a+i+2; N=b+2
        count=sum((2**z-2**a)*(2**z-2**b)<0 for z in range(N+1))
        v=S.Integer(b-a-1)
        independent=S.Integer(count)
        q=f'Có bao nhiêu số nguyên x, 0≤x≤{N}, thỏa (2^x−2^{a})(2^x−2^{b})<0?'
        sol=f'Đặt t=2^x>0. Bất phương trình (t−2^{a})(t−2^{b})<0 tương đương 2^{a}<t<2^{b}. Do hàm 2^x đồng biến, suy ra {a}<x<{b}. Kết hợp x nguyên, 0≤x≤{N}, nhận x={a+1},...,{b-1}, tổng cộng {v} giá trị.'
    elif m==7:
        a=i%3+1;b=2+i%4;c=1+i%5;p=2*a;qv=3*a
        v=S.Integer(-2*b-3*c)
        independent=S.solve(a*S.Symbol('m')+b*p+c*qv, S.Symbol('m'))[0]
        q=f'Cho hai mặt phẳng có vectơ pháp tuyến n₁=({a};{b};{c}) và n₂=(m;{p};{qv}). Tìm m để hai mặt phẳng vuông góc.'
        sol=f'Hai mặt phẳng vuông góc khi tích vô hướng hai pháp tuyến bằng 0. Suy ra {a}m+{b}·{p}+{c}·{qv}=0, tức {a}m={-(b*p+c*qv)}, nên m={v}.'
    elif m==8:
        k=1+i%4;mult=1+i%5;Q=i+2;L=k*(Q-1)
        v=S.log(Q)
        independent=S.integrate(S.Rational(mult,mult)*(1/(x+k)), (x,0,L))
        q=f'Tính tích phân xác định ∫ từ 0 đến {L} của {mult}/({mult}x+{mult*k}) dx.'
        sol=f'Vì {mult}/({mult}x+{mult*k})=1/(x+{k}), một nguyên hàm trên [0;{L}] là ln(x+{k}). Thay cận: ln({L}+{k})−ln({k})=ln({Q}).'
    elif m==9:
        a=1+i%4;b=1+i%5;extra=1+(i*2)%5;L=1+i%6
        # R(x)=(a+1)x+b+extra and r(x)=ax+b, always R>r>=0 for 0<=x<=L.
        r=lambda t: a*t+b
        R=lambda t:(a+1)*t+b+extra
        # Exact manual polynomial integration of (R-r)(R+r).
        v=S.pi*(S.Rational(2*a+1,3)*L**3+S.Rational(2*b+(2*a+2)*extra,2)*L**2+extra*(2*b+extra)*L)
        independent=S.pi*S.integrate(R(x)**2-r(x)**2,(x,0,L))
        q=f'Quay miền giữa y={a}x+{b} và y={a+1}x+{b+extra} trên 0≤x≤{L} quanh trục Ox. Tính thể tích khối tròn xoay.'
        sol=f'Vì R(x)=({a+1})x+{b+extra} lớn hơn r(x)={a}x+{b}>0, mỗi mặt cắt vuông góc Ox là một vành khăn, diện tích π(R²−r²). Thể tích V=π∫₀^{L}[R(x)²−r(x)²]dx=π∫₀^{L}(x+{extra})(({2*a+1})x+{2*b+extra})dx={S.sstr(v)}.'
    elif m==10:
        n=i+3
        v=S.Integer(3**n-3*2**n+3)
        independent=S.Integer(6*S.functions.combinatorial.numbers.stirling(n,3))
        q=f'Có bao nhiêu hàm số toàn ánh từ tập A gồm {n} phần tử sang tập B gồm đúng 3 phần tử?'
        sol=f'Có 3^{n} hàm bất kỳ. Trừ 3·2^{n} hàm bỏ sót ít nhất một giá trị, cộng lại 3·1^{n} hàm chỉ nhận một giá trị. Theo nguyên lý bao hàm–loại trừ, số toàn ánh =3^{n}−3·2^{n}+3={v}.'
    else: raise AssertionError(m)
    return q, v, independent, sol


def same(a,b):
    if isinstance(a,tuple) or isinstance(b,tuple):
        return isinstance(a,tuple) and isinstance(b,tuple) and len(a)==len(b) and all(S.simplify(x-y)==0 for x,y in zip(a,b))
    return S.simplify(a-b)==0


def pretty(value):
    if isinstance(value,tuple): return '('+';'.join(str(S.simplify(x)) for x in value)+')'
    return str(S.simplify(value)).replace('log(', 'ln(').replace('pi','π')


def distractors(value):
    if isinstance(value,tuple):
        x,y=value
        return [(x+1,y),(x,y+1),(x+1,y+2)]
    return [value+1, value-1, value+2]


def build():
    rng=random.Random(141)
    methods=[];questions=[]
    for m,(topic,grade,title,signature) in enumerate(METHODS):
        assert TOPICS[topic]==grade,(topic,grade)
        mid=f'v141_{m:02d}'
        methods.append({'method_id':mid,'topic':topic,'grade':grade,'title':title,
                        'solving_method':signature,'questions_expected':10,'review_status':'pending-expert-review',
                        'independence_certified':False,'published':False,
                        'novelty_note':'Not independently assessed against all prior mathematical methods.'})
        for i in range(10):
            stem,value,other,solution=oracle(m,i)
            assert same(value,other),(m,i,value,other)
            answer_val=pretty(value)
            record={'id':f'{mid}_{i:02d}','method_id':mid,'topic':topic,'grade':grade,
                    'question':stem,'solution':solution,'canonical_answer':answer_val,
                    'review_status':'pending-expert-review','independence_certified':False,
                    'published':False,'mathematical_oracle':'independent symbolic/combinatorial check',
                    'answer_oracle_match':True}
            if i<7:
                choices=[value]+distractors(value)
                assert all(not same(choices[j],choices[k]) for j in range(4) for k in range(j+1,4))
                rng.shuffle(choices)
                options={key:pretty(x) for key,x in zip('ABCD',choices)}
                correct=next(letter for letter,x in zip('ABCD',choices) if same(x,value))
                record.update({'format':'trac_nghiem','options':options,'correct_option':correct,
                               'answer':correct,'independent_check':correct})
            elif i<9:
                record.update({'format':'tra_loi_ngan','answer':answer_val,'independent_check':pretty(other)})
            else:
                proposed=value if m%2==0 else distractors(value)[0]
                correct='Đúng' if same(proposed,value) else 'Sai'
                record['question']=stem+' Nhận định: kết quả bằng '+pretty(proposed)+'. Đúng hay sai?'
                record.update({'format':'dung_sai','assertion':pretty(proposed),
                               'answer':correct,'independent_check':correct})
            questions.append(record)
    assert len(methods)==11 and len(questions)==110
    assert len({q['question'] for q in questions})==110
    for name, items in [('V141_CANDIDATE_METHODS.jsonl',methods),('V141_VERIFIED_QUESTIONS.jsonl',questions)]:
        (OUT/name).write_text(''.join(json.dumps(item,ensure_ascii=False,sort_keys=True)+'\n' for item in items), encoding='utf-8')
    print('V141:',len(methods),'candidate methods;',len(questions),'questions; formats:',{t:sum(q['format']==t for q in questions) for t in ['trac_nghiem','tra_loi_ngan','dung_sai']})
    return methods,questions

if __name__=='__main__': build()
