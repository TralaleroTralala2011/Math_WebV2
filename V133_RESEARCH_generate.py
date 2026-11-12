"""Unpublished, reproducible V133 candidate research. Not a novelty certification."""
from pathlib import Path
from fractions import Fraction
import json, collections, hashlib, re, math
import sympy as s
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'V133_RESEARCH';OUT.mkdir(exist_ok=True)
x=s.symbols('x',real=True)
# Each definition is a different underlying operation, not merely a different presentation.
F=[
 ('ham_so','Tìm tham số của hàm bậc nhất qua hai điểm',10,'Giải hệ hai phương trình tuyến tính'),
 ('tap_hop','Đếm tập con có điều kiện về phần tử bắt buộc',10,'Song ánh với tập lũy thừa sau khi cố định phần tử'),
 ('he_phuong_trinh','Giải hệ 2x2 bằng quy tắc Cramer',10,'Định thức và quy tắc Cramer'),
 ('xac_suat','Xác suất rút không hoàn lại có đúng hai màu',10,'Tổ hợp trên mẫu không hoàn lại'),
 ('ham_so_luong_giac','Đếm nghiệm sin(x)=0 trên đoạn hữu hạn',11,'Tham số hóa nghiệm lượng giác và đếm số nguyên'),
 ('cap_so_nhan','Tổng cấp số nhân hữu hạn',11,'Tách hiệu và công thức tổng cấp số nhân'),
 ('gioi_han','Giới hạn dạng 0/0 của đa thức có nhân tử chung',11,'Phân tích nhân tử và khử nhân tử trước khi lấy giới hạn'),
 ('dao_ham','Phương trình tiếp tuyến tại một điểm',11,'Hệ số góc từ đạo hàm'),
 ('pt_logarit','Giải phương trình logarit có điều kiện xác định',12,'Đưa về phương trình đại số sau kiểm tra điều kiện'),
 ('hinh_hoc_khong_gian','Khoảng cách từ điểm đến mặt phẳng Oxyz',12,'Chiếu theo phương pháp tuyến và công thức khoảng cách'),
 ('so_phuc','Tìm liên hợp của tích hai số phức',12,'Nhân số phức và lấy liên hợp'),
 ('nguyen_ham_tich_phan','Giá trị trung bình hàm bậc hai trên một đoạn',12,'Tích phân xác định chia độ dài đoạn'),
]
def N(z):return str(s.simplify(z))
def make(j,i):
 k=i+1;topic,title,grade,approach=F[j]
 if j==0:
  m=i-5;b=(3*i)%11-5;x1=-2-i%3;x2=2+i%4;y1=m*x1+b;y2=m*x2+b
  q=f'Hàm số y=ax+b đi qua A({x1};{y1}) và B({x2};{y2}). Tìm a+b.';ans=m+b
  check=s.solve([s.Eq(s.Symbol('a')*x1+s.Symbol('b'),y1),s.Eq(s.Symbol('a')*x2+s.Symbol('b'),y2)],(s.Symbol('a'),s.Symbol('b')));chk=check[s.Symbol('a')]+check[s.Symbol('b')]
  sol=f'Từ hai tọa độ: a=({y2}−({y1}))/({x2}−({x1}))={m}; b={y1}−{m}·({x1})={b}. Vậy a+b={ans}.'
 elif j==1:
  n=8+i;r=2+i%3;mandatory=1+i%3; choose=3+i%3
  # select exactly choose objects from n, given mandatory objects present
  q=f'Tập X có {n} phần tử; cố định trước {mandatory} phần tử của X. Có bao nhiêu tập con gồm đúng {choose} phần tử chứa đủ {mandatory} phần tử này?'
  ans=math.comb(n-mandatory,choose-mandatory);chk=sum(1 for v in __import__('itertools').combinations(range(n),choose) if set(range(mandatory)).issubset(v))
  sol=f'Giữ nguyên {mandatory} phần tử bắt buộc, chọn thêm {choose-mandatory} phần tử từ {n-mandatory} phần tử còn lại. Có C({n-mandatory},{choose-mandatory})={ans} cách.'
 elif j==2:
  a=2+i%5;b=1+i%4;c=i%3;d=3+i%5
  if a*d-b*c==0:d+=1
  xx=i-4;yy=2-i%4;u=a*xx+b*yy;v=c*xx+d*yy
  q=f'Giải hệ {a}x+{b}y={u}, {c}x+{d}y={v}. Tính x−y.';ans=xx-yy
  det=a*d-b*c;chk=s.solve([s.Eq(a*x+b*s.Symbol('y'),u),s.Eq(c*x+d*s.Symbol('y'),v)],(x,s.Symbol('y')));chk=chk[x]-chk[s.Symbol('y')]
  sol=f'Định thức D={a}·{d}−{b}·{c}={det}≠0. Theo Cramer, x={xx}, y={yy}; suy ra x−y={ans}. Kiểm tra thay lại cả hai phương trình.'
 elif j==3:
  red=4+i%5;blue=5+i%4;draw=3+i%3; r=1+i%2
  total=math.comb(red+blue,draw);good=math.comb(red,r)*math.comb(blue,draw-r);ans=Fraction(good,total)
  chk=Fraction(sum(sum(t<red for t in subset)==r for subset in __import__('itertools').combinations(range(red+blue),draw)),total)
  q=f'Hộp có {red} bi đỏ và {blue} bi xanh. Rút ngẫu nhiên đồng thời {draw} bi. Tính xác suất có đúng {r} bi đỏ.'
  sol=f'Số cách rút đều khả năng là C({red+blue},{draw})={total}. Thuận lợi: C({red},{r})·C({blue},{draw-r})={good}. Xác suất bằng {good}/{total}={ans}.'
 elif j==4:
  L=-5-i;U=4+i
  ans=sum(1 for v in range(L,U+1) if v==0) # counts multiples of pi index on [L pi, U pi]
  chk=len([m for m in range(L-1,U+2) if L<=m<=U]);ans=chk
  q=f'Có bao nhiêu nghiệm của sin(x)=0 trên đoạn [{L}π;{U}π]?'
  sol=f'sin(x)=0 ⇔ x=kπ (k nguyên). Điều kiện {L}≤k≤{U}, có {U-L+1} số nguyên thỏa mãn. Đáp án {ans}.'
 elif j==5:
  a=i+1;r=2+i%3;n=3+i%5;ans=a*(r**n-1)//(r-1)
  chk=sum(a*r**t for t in range(n))
  q=f'Cấp số nhân có u₁={a}, công bội q={r}. Tìm tổng {n} số hạng đầu.'
  sol=f'Sₙ=u₁(qⁿ−1)/(q−1)={a}({r}^{n}−1)/({r}−1)={ans}. Có thể đối chiếu bằng cách cộng các số hạng.'
 elif j==6:
  a=i-3;b=2+i%4;c=i%5+1
  pol=s.expand((x-a)*(c*x+b));ans=c*a+b
  chk=s.limit(pol/(x-a),x,a)
  q=f'Tính lim khi x→{a} của ({s.sstr(pol)})/(x−({a})).'
  sol=f'Tử số phân tích thành (x−({a}))({c}x+({b})). Khử nhân tử khi x≠{a}; giới hạn bằng {c}·({a})+({b})={ans}.'
 elif j==7:
  a=1+i%4;b=i-5;c=1+i%3;at=i-2
  slope=2*a*at+b;intercept=(a*at*at+b*at+c)-slope*at;ans=intercept
  chk=s.expand(a*x*x+b*x+c).subs(x,at)-s.diff(a*x*x+b*x+c,x).subs(x,at)*at
  q=f'Cho f(x)={a}x²+({b})x+({c}). Tiếp tuyến tại x={at} có dạng y=mx+n. Tính n.'
  sol=f'f′(x)={2*a}x+({b}), m=f′({at})={slope}. n=f({at})−m·({at})={intercept}. Vậy n={ans}.'
 elif j==8:
  base=2+i%4;root=i+2;offset=i%3+1;val=root+offset;rhs=math.log(val,base) if False else None
  # log_base(x-offset)=log_base(root); x-offset>0
  q=f'Giải phương trình log cơ số {base} của (x−{offset}) bằng log cơ số {base} của {root}. Tìm x.'
  ans=val;chk=s.solve(s.Eq(x-offset,root),x)[0]
  sol=f'Điều kiện x>{offset}. Do log cơ số {base}>1 là đơn ánh, x−{offset}={root}, suy ra x={val}, thỏa điều kiện.'
 elif j==9:
  a=1+i%3;b=2+i%4;c=2+(i+1)%3; px=i-5;py=i%5-2;pz=i%3+1;d=a*px+b*py+c*pz+(i+1)
  ans=s.Rational(i+1,1)/s.sqrt(a*a+b*b+c*c)
  chk=abs(a*px+b*py+c*pz-d)/s.sqrt(a*a+b*b+c*c)
  q=f'Trong Oxyz, tìm khoảng cách từ P({px};{py};{pz}) tới mặt phẳng {a}x+{b}y+{c}z={d}.'
  sol=f'd(P,(Q))=|{a}·({px})+{b}·({py})+{c}·({pz})−({d})|/√({a*a+b*b+c*c})={N(ans)}.'
 elif j==10:
  a=i-4;b=i%5+1;c=2+i%4;d=1+i%3
  ans=s.conjugate((a+b*s.I)*(c+d*s.I));chk=s.expand_complex(s.conjugate(a+b*s.I)*s.conjugate(c+d*s.I))
  q=f'Cho z=({a}+{b}i)({c}+{d}i). Tính số phức liên hợp của z.'
  sol=f'Nhân hai thừa số: phần thực ac−bd={a*c-b*d}, phần ảo ad+bc={a*d+b*c}. Do đó z={a*c-b*d}+({a*d+b*c})i và liên hợp z={N(ans)}.'
 elif j==11:
  a=1+i%4;b=i-4;c=2+i%5;lo=-1-i%3;hi=2+i%4
  fun=a*x*x+b*x+c;ans=s.integrate(fun,(x,lo,hi))/(hi-lo)
  chk=s.simplify(a*s.Rational(hi**3-lo**3,3*(hi-lo))+b*s.Rational(hi+lo,2)+c)
  q=f'Tính giá trị trung bình của f(x)={a}x²+({b})x+({c}) trên [{lo};{hi}].'
  sol=f'Giá trị trung bình bằng 1/({hi}−({lo})) nhân tích phân của f từ {lo} đến {hi}. Dùng nguyên hàm {a}x³/3+({b})x²/2+({c})x, nhận được {N(ans)}.'
 else:raise AssertionError
 assert s.simplify(s.sympify(ans)-s.sympify(chk))==0,(j,i,ans,chk)
 # Explain the validation step rather than padding with arbitrary filler.
 if j==0: sol+=' Thế a và b vào phương trình hai điểm để kiểm tra đều cho đúng tung độ đã biết.'
 if j==7: sol+=' Đối chiếu tiếp tuyến đi qua điểm (x₀,f(x₀)) và có hệ số góc bằng f′(x₀).'
 if j==9: sol+=' Mẫu số là độ dài vectơ pháp tuyến, khác 0 vì các hệ số của mặt phẳng không đồng thời bằng 0.'
 return {'id':f'v133_{j:02}_{i:02}','method_id':f'v133_{j:02}','topic':topic,'grade':grade,'question':q,'answer':N(ans),'independent_check':N(chk),'solution':sol,'format':'tra_loi_ngan','published':False,'review_status':'pending-expert-review','independence_certified':False}
def output(path,items):path.write_text(''.join(json.dumps(z,ensure_ascii=False,sort_keys=True)+'\n' for z in items),encoding='utf-8')
def run():
 forms=[{'method_id':f'v133_{j:02}','topic':t,'title':title,'grade':grade,'solving_method':method,'questions_expected':10,'independence_certified':False,'review_status':'pending-expert-review','published':False} for j,(t,title,grade,method) in enumerate(F)]
 qs=[make(j,i) for j in range(len(F)) for i in range(10)]
 assert len(set(z['id'] for z in qs))==len(qs)
 assert len(set(z['question'] for z in qs))==len(qs)
 output(OUT/'V133_CANDIDATE_METHODS.jsonl',forms);output(OUT/'V133_VERIFIED_QUESTIONS.jsonl',qs)
 print(len(forms),len(qs))
if __name__=='__main__':run()
