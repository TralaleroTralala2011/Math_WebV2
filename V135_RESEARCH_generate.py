"""V135 mathematics research candidates, quarantined pending semantic novelty review.

Each objective represents a different *authored learning task* within this batch;
we do NOT certify independence from older historical method families.
Each answer is recomputed by a separate oracle (exact enumeration or SymPy).
"""
from __future__ import annotations
from fractions import Fraction
from itertools import combinations
from math import comb, cos, factorial, gcd, lcm, pi
from pathlib import Path
import json
import sympy as sp

ROOT=Path(__file__).resolve().parent
DEST=ROOT/'V135_RESEARCH'
DEST.mkdir(exist_ok=True)
x=sp.symbols('x',real=True)

SPECS=[
 ('g10_combinatorics_olympiad',10,'Đếm nghiệm nguyên không âm của ax+by=N','đồng dư và bước nghiệm của phương trình Diophantine'),
 ('g10_geom_circle_tangent_chord',10,'Độ dài tiếp tuyến từ điểm ngoài đường tròn','tam giác vuông tạo bởi bán kính tới tiếp điểm'),
 ('g10_symmetric_systems',10,'Tổng hai ẩn từ x²+y² và xy','hằng đẳng thức đối xứng và xét dấu'),
 ('g10_advanced_inequalities',10,'Cực tiểu biểu thức x+A/x với x dương','AM–GM với điều kiện đạt dấu bằng'),
 ('cap_so_nhan',11,'Tổng n số hạng đầu cấp số nhân','công thức tổng hình học hữu hạn'),
 ('g11_binomial_advanced',11,'Hệ số tích hai nhị thức','tích chập hệ số nhị thức Newton'),
 ('g11_advanced_trig_equations',11,'Đếm nghiệm cos(nx)=cos(mx) trên chu kỳ','hai nhánh của đẳng thức cos và khử nghiệm trùng'),
 ('bien_co_doc_lap_11',11,'Xác suất siêu bội khi lấy không hoàn lại','đếm tổ hợp theo số phần tử từng loại'),
 ('tiep_tuyen',12,'Hệ số góc tiếp tuyến hàm logarit','đạo hàm hàm hợp logarit'),
 ('ung_dung_tich_phan',12,'Diện tích miền giới hạn bởi một parabol và trục hoành','tích phân xác định hàm không âm giữa hai nghiệm'),
 ('g12_geom_point_plane_distance',12,'Khoảng cách từ điểm tới mặt phẳng trong Oxyz','hình chiếu vuông góc lên véc-tơ pháp tuyến'),
 ('g12_complex_plane_geometry',12,'Điểm trên trục thực cách đều hai điểm phức','đường trung trực và khai triển bình phương môđun'),
 ('bpt_logarit',12,'Số nghiệm nguyên dương của bất phương trình log cơ số nhỏ hơn 1','đảo chiều bất đẳng thức khi cơ số thuộc (0,1)'),
]
TRIPLES=[(5,3,4),(13,5,12),(17,8,15),(25,7,24),(29,20,21),(37,12,35),(41,9,40),(53,28,45),(61,11,60),(65,16,63)]
AB=[(3,7),(4,9),(5,8),(6,11),(7,9),(8,13),(9,11),(10,13),(11,14),(12,17)]

def canon(z):return str(sp.simplify(z))
def question(j,i):
    assert 0<=i<10 and 0<=j<len(SPECS)
    if j==0:
        a,b=AB[i]; N=(i+2)*a*b
        x0=(pow(a,-1,b)*N)%b
        ymax=N//a
        ans=sp.Integer(1+(ymax-x0)//b if x0<=ymax else 0)
        chk=sp.Integer(sum((N-a*k)%b==0 for k in range(ymax+1)))
        prompt=f'Có hai loại phiếu giá {a} và {b} điểm. Có bao nhiêu cặp số nguyên không âm (u,v) thỏa {a}u+{b}v={N}?'
        solution=(f'Vì gcd({a},{b})=1, điều kiện chia hết cho {b} cho u≡{x0} (mod {b}). '
                  f'Mọi nghiệm không âm có u={x0}+{b}t≤⌊{N}/{a}⌋={ymax} và v=({N}−{a}u)/{b}. '
                  f'Số t nguyên không âm thỏa điều kiện là {ans}.')
    elif j==1:
        dist,r,tangent=TRIPLES[i]
        ans=sp.Integer(tangent)
        T=sp.Point(sp.Rational(r*r,dist),sp.Rational(r*tangent,dist))
        chk=sp.simplify(T.distance(sp.Point(dist,0)))
        prompt=f'Từ điểm P ở ngoài đường tròn tâm O bán kính {r} cm, biết OP={dist} cm. Tiếp tuyến PT có độ dài bao nhiêu?'
        solution=f'Bán kính OT vuông góc tiếp tuyến PT. Tam giác OPT vuông tại T, nên PT²=OP²−OT²={dist}²−{r}²={tangent*tangent}; PT={ans} cm.'
    elif j==2:
        p=i+2; q=2*i+3; A=p*p+q*q; B=p*q
        ans=sp.Integer(p+q)
        z=sp.symbols('z',real=True)
        values=sp.solve(z*z-(A+2*B),z)
        chk=next(zv for zv in values if zv>0)
        prompt=f'Biết x²+y²={A}, xy={B} và x+y>0. Tìm x+y.'
        solution=f'Từ (x+y)²=x²+y²+2xy={A}+2·{B}={int(ans)**2}. Do x+y>0 theo giả thiết, ta lấy căn bậc hai dương: x+y=√{int(ans)**2}={ans}; nghiệm âm không được chọn.'
    elif j==3:
        k=i+2; A=k*k
        ans=sp.Integer(2*k)
        derivative=sp.diff(x+sp.Rational(A,1)/x,x)
        critical=[v for v in sp.solve(derivative,x) if v.is_positive]
        chk=(x+sp.Rational(A,1)/x).subs(x,critical[0])
        prompt=f'Cho x>0. Tìm giá trị nhỏ nhất của P=x+{A}/x.'
        solution=f'AM–GM: x+{A}/x≥2√(x·{A}/x)=2√{A}={ans}. Dấu bằng khi x={A}/x, tức x={k}>0, nên min P={ans}.'
    elif j==4:
        u=2+i; r=2+i%3;n=4+i
        ans=sp.Integer(u*(r**n-1)//(r-1))
        chk=sp.Integer(sum(u*r**j for j in range(n)))
        prompt=f'Cấp số nhân có u₁={u} và công bội q={r}. Tính tổng {n} số hạng đầu.'
        solution=f'Viết Sₙ=u₁+u₁q+⋯+u₁q^(n−1). Lấy qSₙ−Sₙ=u₁(qⁿ−1), do q={r}≠1 nên Sₙ=u₁(qⁿ−1)/(q−1)={u}·({r}^{n}−1)/({r}−1)={ans}.'
    elif j==5:
        a=4+i;b=3+(i%4);k=2+(i%4)
        ans=sp.Integer(sum(comb(a,t)*comb(b,k-t)*2**(k-t) for t in range(k+1) if t<=a and k-t<=b))
        chk=sp.Poly(sp.expand((1+x)**a*(1+2*x)**b),x).coeff_monomial(x**k)
        prompt=f'Tìm hệ số của x^{k} trong khai triển (1+x)^{a}·(1+2x)^{b}.'
        solution=f'Khi lấy x^t từ (1+x)^{a} và x^({k}−t) từ (1+2x)^{b}, hệ số đóng góp là C({a},t)C({b},{k}−t)2^({k}−t). Cộng theo t hợp lệ thu được {ans}.'
    elif j==6:
        n=5+i;m=1+(i%3);D=lcm(n-m,n+m)
        ans=sp.Integer((n-m)+(n+m)-gcd(n-m,n+m))
        chk=sp.Integer(sum(abs(cos(n*2*pi*k/D)-cos(m*2*pi*k/D))<1e-9 for k in range(D)))
        prompt=f'Có bao nhiêu nghiệm khác nhau của cos({n}x)=cos({m}x) trong khoảng 0≤x<2π?'
        solution=(f'cos A=cos B ⇔ A=±B+2kπ. Hai nhánh cho lần lượt {n-m} và {n+m} nghiệm trong [0,2π). '
                  f'Số nghiệm chung là gcd({n-m},{n+m})={gcd(n-m,n+m)}. Theo nguyên lý bù trừ có {ans} nghiệm phân biệt.')
    elif j==7:
        red=4+i;blue=3+i%5;pick=3
        ans=sp.Rational(comb(red,2)*comb(blue,1),comb(red+blue,pick))
        groups=combinations(range(red+blue),pick)
        favorable=sum(sum(y<red for y in c)==2 for c in groups)
        chk=sp.Rational(favorable,comb(red+blue,pick))
        prompt=f'Hộp có {red} bi đỏ, {blue} bi xanh phân biệt. Rút cùng lúc 3 bi, xác suất có đúng 2 bi đỏ là bao nhiêu?'
        solution=f'Số cách chọn đồng khả năng: C({red+blue},3). Số cách có đúng 2 đỏ và 1 xanh: C({red},2)·C({blue},1). Xác suất={canon(ans)}.'
    elif j==8:
        a=2+i;b=3+(i%4);x0=i%4
        ans=sp.Rational(a,a*x0+b)
        chk=sp.limit((sp.log(a*(x0+x)+b)-sp.log(a*x0+b))/x,x,0)
        prompt=f'Với y=ln({a}x+{b}), tính hệ số góc tiếp tuyến của đồ thị tại điểm có hoành độ x={x0}.'
        solution=f'Hàm số xác định khi {a}x+{b}>0. Ta có y′={a}/({a}x+{b}). Thay x={x0} vào đạo hàm, hệ số góc tiếp tuyến bằng {canon(ans)}.'
    elif j==9:
        a=i-4;b=a+3+i
        ans=sp.Rational((b-a)**3,6)
        chk=sp.integrate((x-a)*(b-x),(x,a,b))
        prompt=f'Tính diện tích hình phẳng giới hạn bởi y=(x−({a}))({b}−x) và trục Ox trên đoạn [{a};{b}].'
        solution=f'Trên [{a};{b}], hai thừa số x−({a}) và {b}−x không âm. Diện tích bằng ∫ từ {a} đến {b} của (x−({a}))({b}−x) dx=({b-a})³/6={canon(ans)}.'
    elif j==10:
        normal=sp.Matrix([2+i%4,1+i%3,3+i%5]);P=sp.Matrix([1+i,3-i,2+i%4]);constant=i-7
        numerator=normal.dot(P)-constant
        ans=sp.Abs(numerator)/sp.sqrt(normal.dot(normal))
        H=P-normal*sp.Rational(numerator,normal.dot(normal))
        chk=sp.sqrt((P-H).dot(P-H))
        A,B,C=tuple(normal)
        prompt=f'Trong Oxyz, tính khoảng cách từ P{tuple(P)} đến mặt phẳng ({A})x+({B})y+({C})z={constant}.'
        solution=f'Pháp tuyến n=({A},{B},{C}); n·P−d={numerator}; |n|=√({normal.dot(normal)}). Khoảng cách |n·P−d|/|n|={canon(ans)}.'
    elif j==11:
        a=i+1;b=2+i%3;c=a+3+(i%4);d=4+i%5
        ans=sp.Rational(c*c+d*d-a*a-b*b,2*(c-a))
        chk=sp.solve((x-a)**2+b*b-((x-c)**2+d*d),x)[0]
        prompt=f'Tìm số thực t để |t−({a}+{b}i)|=|t−({c}+{d}i)| (i là đơn vị ảo).'
        solution=f'Bình phương hai vế: (t−{a})²+{b}²=(t−{c})²+{d}². Thu gọn 2({c}−{a})t={c*c+d*d-a*a-b*b}, nên t={canon(ans)}.'
    elif j==12:
        base_den=i+2;offset=i%4
        ans=sp.Integer(base_den**2-offset)
        chk=sp.Integer(sum((v+offset)>0 and float(sp.log(v+offset,sp.Rational(1,base_den)))>=-2-1e-10 for v in range(1,base_den**2+1)))
        prompt=f'Có bao nhiêu số nguyên x>0 thỏa log_(1/{base_den})(x+{offset})≥−2?'
        solution=f'Vì 0<1/{base_den}<1, log cơ số này nghịch biến. Với x+{offset}>0, bất phương trình tương đương x+{offset}≤(1/{base_den})^(−2)={base_den**2}; do đó 1≤x≤{base_den**2-offset}. Có {ans} số.'
    else:raise ValueError(j)
    assert sp.simplify(ans-chk)==0,(j,i,ans,chk)
    if len(solution)<65:raise ValueError((j,i,'short solution',solution))
    return {'id':f'v135_{j:02}_{i:02}','method_id':f'v135_{j:02}',
            'topic':SPECS[j][0],'grade':SPECS[j][1],
            'question':prompt,'answer':canon(ans),'independent_check':canon(chk),
            'solution':solution,'format':'tra_loi_ngan','review_status':'pending-expert-review',
            'independence_certified':False,'published':False}

def dump(path,records):
    with path.open('w',encoding='utf8') as fout:
        for r in records:fout.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')

def generate():
    catalog={c['id']:c for c in json.loads((ROOT/'backend/question_factory/catalog_150.json').read_text(encoding='utf8'))}
    methods=[];items=[]
    for j,(topic,grade,title,approach) in enumerate(SPECS):
        assert catalog[topic]['grade']==grade,(topic,grade)
        methods.append({'method_id':f'v135_{j:02}','topic':topic,'grade':grade,
                        'title':title,'solving_method':approach,'questions_expected':10,
                        'review_status':'pending-expert-review','independence_certified':False,'published':False})
        items.extend(question(j,i) for i in range(10))
    assert len({x['question'] for x in items})==len(items)
    dump(DEST/'V135_CANDIDATE_METHODS.jsonl',methods)
    dump(DEST/'V135_VERIFIED_QUESTIONS.jsonl',items)
    print(f'V135: {len(methods)} quarantined candidates, {len(items)} independently oracle-checked exercises, 0 certified')
    return methods,items

if __name__=='__main__':generate()
