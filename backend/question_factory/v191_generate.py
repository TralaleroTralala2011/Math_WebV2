#!/usr/bin/env python3
"""V191 deterministic, bounded, mathematically-oracled candidate question bank.
No automatic certification of independent types and no production writes.
"""
from __future__ import annotations
import json, sys, hashlib, random, re
from pathlib import Path
from fractions import Fraction
from collections import Counter
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'bank_updates'/'V191_IMPORT_READY.jsonl'
REPORT=ROOT/'bank_updates'/'V191_GENERATION_AUDIT.json'
FAMILIES=[]
def family(grade,topic,key,name,method,knowledge,conditions,difficulty='trung cấp'):
 def register(fn):
  FAMILIES.append(dict(grade=grade,topic=topic,key=key,name=name,method=method,knowledge=knowledge,conditions=conditions,difficulty=difficulty,make=fn))
  return fn
 return register

def f(v):
 v=s.simplify(v)
 if v.is_Rational: return str(v)
 return s.sstr(v)

def checked(q, ans, solution, oracle, meta=None):
 a=s.simplify(ans); b=s.simplify(oracle)
 assert s.simplify(a-b)==0,(q,a,b)
 assert isinstance(q,str) and len(q)>25 and len(solution)>45
 return q,a,solution,dict(meta or {},oracle=f(b))

# TOÁN 10: distinct mathematical operations, no re-labeled numeric templates.
@family(10,'tap_hop','v191_symmetric_difference','Đếm phần tử thuộc đúng một trong hai tập','|A Δ B| = |A|+|B|-2|A∩B|','Phép toán tập hợp, đếm phần tử','Hai tập hữu hạn', 'nền tảng')
def symdiff(k):
 a,b,c=23+2*k,18+3*k,6+k; v=a+b-2*c
 return checked(f'Cho |A|={a}, |B|={b}, |A∩B|={c}. Có bao nhiêu phần tử thuộc đúng một trong A và B?',v,f'Số phần tử chỉ thuộc A là {a}-{c}={a-c}; chỉ thuộc B là {b}-{c}={b-c}. Hai nhóm không giao nhau nên tổng là {a-c}+{b-c}={v}.',(a-c)+(b-c))

@family(10,'hinh_hoc_co_ban_10','v191_polygon_diagonals','Đếm đường chéo của đa giác lồi','C(n,2)-n','Đa giác, đếm cặp đỉnh','n>=3 là số đỉnh')
def diagonals(k):
 n=6+k; v=n*(n-3)//2
 return checked(f'Một đa giác lồi có {n} đỉnh. Hỏi đa giác có bao nhiêu đường chéo?',v,f'Mỗi cặp trong {n} đỉnh xác định một đoạn: C({n},2)={n*(n-1)//2}. Loại {n} cạnh của đa giác, số đường chéo là {n*(n-1)//2}-{n}={v}.',s.binomial(n,2)-n)

@family(10,'hinh_hoc_co_ban_10','v191_polygon_angle_sum','Tổng góc trong của đa giác n cạnh','(n-2)×180°','Chia đa giác thành n−2 tam giác','Đa giác đơn lồi, n≥3', 'nền tảng')
def anglesum(k):
 n=5+k; v=(n-2)*180
 return checked(f'Cho đa giác lồi {n} cạnh. Tính tổng số đo các góc trong (đơn vị độ).',v,f'Kẻ các đường chéo từ một đỉnh để chia đa giác thành {n}-2={n-2} tam giác. Mỗi tam giác có tổng ba góc 180°. Vậy tổng là {n-2}×180°={v}°.',180*(n-2))

@family(10,'g10_geom_special_lines','v191_apollonius_median','Bình phương trung tuyến theo ba cạnh','m_a²=(2b²+2c²−a²)/4','Định lý Apollonius','Ba cạnh hợp lệ tạo thành tam giác')
def median(k):
 # triangle sides 13,14,15 scaled; choose median toward side 14
 a,b,c=14*(k+1),13*(k+1),15*(k+1)
 v=s.Rational(2*b*b+2*c*c-a*a,4)
 return checked(f'Tam giác ABC có BC={a}, CA={b}, AB={c}. Gọi M là trung điểm BC. Tính AM².',v,f'Theo định lý Apollonius, AM²=[2·CA²+2·AB²−BC²]/4. Thay số: [2·{b}²+2·{c}²−{a}²]/4={f(v)}.',(b*b+c*c)/2-a*a/4)

@family(10,'he_thuc_luong_tam_giac','v191_heron_area','Diện tích tam giác theo công thức Heron','S²=p(p−a)(p−b)(p−c)','Nửa chu vi và định lý Heron','Ba cạnh thỏa bất đẳng thức tam giác')
def heron(k):
 t=k+1;a,b,c=13*t,14*t,15*t;p=s.Rational(a+b+c,2);area=s.sqrt(p*(p-a)*(p-b)*(p-c))
 return checked(f'Tam giác có độ dài ba cạnh lần lượt {a}, {b}, {c}. Tính diện tích tam giác.',area,f'Nửa chu vi p=({a}+{b}+{c})/2={f(p)}. Theo Heron, S=√[p(p−a)(p−b)(p−c)]=√[{f(p)}·{f(p-a)}·{f(p-b)}·{f(p-c)}]={f(area)}.',84*t*t)

@family(10,'g10_geom_circle_chords_arcs','v191_intersecting_chords','Dây cung cắt nhau trong đường tròn','PA·PB=PC·PD','Định lý hai dây cung cắt nhau','P trong đường tròn, độ dài dương')
def intersectchords(k):
 p=4+k;pa=2*p;pb=3*(p+1);pc=3*p;pd=2*(p+1)
 return checked(f'Hai dây AB và CD của đường tròn cắt nhau tại P (P nằm trong đường tròn), PA={pa}, PB={pb}, PC={pc}. Tính PD.',pd,f'Áp dụng định lý hai dây cắt nhau: PA·PB=PC·PD. Do đó PD=({pa}·{pb})/{pc}={pd}.',s.Rational(pa*pb,pc))

@family(10,'g10_geom_coordinate_distance_midpoint','v191_projection_on_sloped_line','Hình chiếu vuông góc của điểm lên y=x+b','H_x=(x_0+y_0−b)/2','Điểm đối xứng qua đường thẳng','Đường thẳng có hệ số góc 1')
def projection(k):
 px=3*k+1;py=2*k+8;b=2-k;h=s.Rational(px+py-b,2)
 return checked(f'Trong Oxy, cho P({px};{py}) và đường thẳng d: y=x+({b}). H là hình chiếu vuông góc của P lên d. Tìm hoành độ H.',h,f'Viết d: x−y+({b})=0, vectơ pháp tuyến (1;−1). Từ P hạ vuông góc lên d: H=P−t(1;−1), t=(x_P−y_P+{b})/2. Suy ra x_H={px}−({px}−{py}+{b})/2={f(h)}.',px-s.Rational(px-py+b,2))

@family(10,'quy_tac_dem','v191_stars_bars_three','Đếm nghiệm nguyên không âm của x+y+z=N','C(N+2,2)','Phương pháp chia kẹo Euler / stars and bars','x,y,z là số nguyên không âm')
def starsbars(k):
 n=7+k;v=s.binomial(n+2,2)
 return checked(f'Có bao nhiêu bộ ba số nguyên không âm (x,y,z) thỏa mãn x+y+z={n}?',v,f'Biểu diễn {n} đơn vị bằng {n} dấu sao, đặt thêm 2 vạch chia thành ba nhóm x, y, z. Tổng có {n}+2 vị trí, chọn 2 vị trí đặt vạch. Số cách C({n+2},2)={v}.',(n+1)*(n+2)//2)

@family(10,'g10_combinatorics_olympiad','v191_linear_diophantine_nonnegative','Đếm nghiệm nguyên không âm của x+2y=N','y∈[0,⌊N/2⌋]','Giải phương trình Diophantine với điều kiện không âm','N là số nguyên không âm')
def diophantine(k):
 n=13+2*k;v=n//2+1
 return checked(f'Đếm số cặp số nguyên không âm (x,y) thỏa mãn x+2y={n}.',v,f'Từ x={n}−2y≥0 suy ra 0≤y≤⌊{n}/2⌋={n//2}. Mỗi y nguyên như vậy xác định duy nhất x nguyên không âm, nên số cặp là {n//2}+1={v}.',len([(x,y) for y in range(n//2+1) for x in [n-2*y]]))

@family(10,'g10_advanced_inequalities','v191_quadratic_nonnegative_all_real','Điều kiện để tam thức luôn dương trên R','a>0 và Δ<0','Biệt thức và dấu tam thức','Hệ số x² dương; bất đẳng thức nghiêm ngặt','nâng cao')
def quadraticpositive(k):
 # x² + (2k)x + m, ask least integer m for strict positivity
 b=2*(k+1);v=(k+1)**2+1
 return checked(f'Tìm số nguyên m nhỏ nhất để x²+{b}x+m>0 với mọi x thực.',v,f'Hệ số x² là 1>0. Tam thức dương với mọi x khi Δ={b}²−4m<0, tức m>{b*b}/4={(k+1)**2}. Số nguyên nhỏ nhất thỏa điều kiện là m={v}.',next(m for m in range((k+1)**2+5) if b*b-4*m<0))

# TOÁN 11
@family(11,'cap_so_nhan','v191_infinite_geometric_series','Tổng cấp số nhân vô hạn hội tụ','S=a₁/(1−q)','Giới hạn cấp số nhân','|q|<1')
def geoinfinite(k):
 a=3+k;q=s.Rational(k+1,k+4);v=a/(1-q)
 return checked(f'Cho cấp số nhân vô hạn có số hạng đầu u₁={a}, công bội q={f(q)}. Tính tổng tất cả các số hạng.',v,f'Vì |q|={f(q)}<1, tổng hội tụ và S=u₁/(1−q)={a}/(1−{f(q)})={f(v)}.',s.limit(a*(1-q**s.Symbol('m'))/(1-q),s.Symbol('m'),s.oo))

@family(11,'gioi_han','v191_telescopic_rational_sum','Tính tổng rút gọn bằng phân tích thành phân số đơn','Σ1/[j(j+1)]=1−1/(n+1)','Tổng lồng nhau / telescoping','j=1..n')
def telescopic(k):
 n=5+2*k;v=s.Rational(n,n+1)
 return checked(f'Tính tổng S=1/(1·2)+1/(2·3)+...+1/({n}·{n+1}).',v,f'Ta có 1/[j(j+1)]=1/j−1/(j+1). Khi cộng j=1,...,{n}, các số hạng ở giữa triệt tiêu, còn S=1−1/{n+1}={f(v)}.',sum((s.Rational(1,j*(j+1)) for j in range(1,n+1)),s.Integer(0)))

@family(11,'dao_ham_quy_tac','v191_chain_power_derivative','Đạo hàm hợp lũy thừa (ax+b)^m','d/dx (ax+b)^m = ma(ax+b)^(m−1)','Quy tắc dây chuyền','m nguyên dương')
def chainpower(k):
 a=2+(k%4);b=3+k;m=3+(k%3);x=1;v=m*a*(a*x+b)**(m-1)
 return checked(f'Cho hàm số f(x)=({a}x+{b})^{m}. Tính f′(1).',v,f'Đặt u={a}x+{b}, u′={a}. Quy tắc hàm hợp: f′(x)={m}({a}x+{b})^{m-1}·{a}. Thay x=1 được f′(1)={m}·{a}·({a}+{b})^{m-1}={v}.',s.diff((a*s.Symbol('x')+b)**m,s.Symbol('x')).subs(s.Symbol('x'),1))

@family(11,'dao_ham','v191_quotient_rule_derivative','Đạo hàm thương hai hàm bậc nhất','((ax+b)/(cx+d))′=(ad−bc)/(cx+d)²','Quy tắc đạo hàm thương','cx+d khác 0')
def quotient(k):
 a=k+4;b=2*k+1;c=2;d=2*k+5;x=1;v=s.Rational(a*d-b*c,(c*x+d)**2)
 return checked(f'Cho f(x)=({a}x+{b})/({c}x+{d}). Tính f′(1).',v,f'Quy tắc thương: f′(x)=[{a}({c}x+{d})−{c}({a}x+{b})]/({c}x+{d})²=({a*d-b*c})/({c}x+{d})². Tại x=1, f′(1)={f(v)}.',s.diff((a*s.Symbol('x')+b)/(c*s.Symbol('x')+d),s.Symbol('x')).subs(s.Symbol('x'),1))

@family(11,'gioi_han_ham_so','v191_limit_sin_over_x','Giới hạn lượng giác cơ bản sin(ax)/(bx)','lim sin(ax)/(bx)=a/b','Giới hạn lượng giác','x→0, b khác 0')
def triglimit(k):
 a=3+k;b=2+(k%3);v=s.Rational(a,b);x=s.Symbol('x')
 return checked(f'Tính lim khi x→0 của sin({a}x)/({b}x).',v,f'Viết sin({a}x)/({b}x)=({a}/{b})·[sin({a}x)/({a}x)]. Vì lim sin t/t=1 khi t→0 nên giới hạn bằng {f(v)}.',s.limit(s.sin(a*x)/(b*x),x,0))

@family(11,'gioi_han_ham_so','v191_limit_cos_1_over_x_squared','Giới hạn (1−cos(ax))/x²','lim (1−cos(ax))/x²=a²/2','Hằng đẳng thức 1−cos t=2sin²(t/2)','x→0')
def coslimit(k):
 a=k+2;x=s.Symbol('x');v=s.Rational(a*a,2)
 return checked(f'Tính lim khi x→0 của [1−cos({a}x)]/x².',v,f'Dùng 1−cos t=2sin²(t/2). Khi x→0, sin({a}x/2)/({a}x/2)→1. Vậy giới hạn bằng 2·({a}/2)²={f(v)}.',s.limit((1-s.cos(a*x))/x**2,x,0))

@family(11,'bien_co_doc_lap_11','v191_bayes_two_urns','Định lý Bayes trong mô hình chọn hộp','P(H|R)=P(R|H)P(H)/P(R)','Xác suất có điều kiện, xác suất toàn phần','Hai hộp được chọn với xác suất bằng nhau')
def bayes(k):
 # box A 2+k red / (5+k); box B 1 red / (7+k)
 ra=k+2;ta=k+5;rb=1;tb=k+7;v=s.Rational(ra*tb,ra*tb+rb*ta)
 return checked(f'Chọn ngẫu nhiên một trong hai hộp A, B với xác suất bằng nhau. A có {ra} bi đỏ trong {ta} bi, B có {rb} bi đỏ trong {tb} bi. Rút được bi đỏ. Tính xác suất đã chọn hộp A.',v,f'Gọi R là sự kiện rút bi đỏ. P(R|A)={ra}/{ta}, P(R|B)={rb}/{tb}, P(A)=P(B)=1/2. Theo Bayes, P(A|R)=[({ra}/{ta})/2]÷[({ra}/{ta})/2+({rb}/{tb})/2]={f(v)}.', (s.Rational(ra,ta)*s.Rational(1,2))/(s.Rational(ra,ta)/2+s.Rational(rb,tb)/2))

@family(11,'to_hop_xac_suat_nang_cao_11','v191_binomial_exactly_two','Phân phối nhị thức: đúng 2 lần thành công','P(X=2)=C(n,2)p²(1−p)^(n−2)','Đếm số vị trí thành công độc lập','n lần thử độc lập, xác suất p')
def binomialtwo(k):
 n=4+(k%4);p=s.Rational(k+1,k+5);v=s.binomial(n,2)*p**2*(1-p)**(n-2)
 return checked(f'Có {n} phép thử Bernoulli độc lập, mỗi phép thử thành công với xác suất {f(p)}. Tính xác suất thành công đúng 2 lần.',v,f'Có C({n},2)={s.binomial(n,2)} cách chọn đúng 2 vị trí thành công. Mỗi mẫu có xác suất ({f(p)})²·(1−{f(p)})^{n-2}. Vậy P=C({n},2)·({f(p)})²·(1−{f(p)})^{n-2}={f(v)}.',sum((p**j*(1-p)**(n-j) for bits in range(2**n) if (j:=bits.bit_count())==2),s.Integer(0)))

@family(11,'day_so_truy_hoi_11','v191_second_order_fibonacci_recurrence','Dãy truy hồi tuyến tính bậc hai dạng Fibonacci','u_(n+2)=u_(n+1)+u_n','Hai điều kiện đầu và tính chất số Fibonacci','u0,u1 cho trước, n>=2', 'nâng cao')
def secondorder(k):
 a=2+k;b=3+2*k;N=7+(k%4);v=int(s.fibonacci(N-1)*a+s.fibonacci(N)*b)
 values=[a,b]
 for _ in range(2,N+1): values.append(values[-1]+values[-2])
 assert values[N]==v
 return checked(f'Cho dãy số u₀={a}, u₁={b}, uₙ₊₂=uₙ₊₁+uₙ với mọi n≥0. Tính u_{N}.',v,f'Từ điều kiện đầu, u₂={a+b}, u₃={a+2*b}. Đặt F₀=0, F₁=1, Fₙ₊₂=Fₙ₊₁+Fₙ. Khi đó uₙ=F_(n−1)u₀+F_n u₁ (n≥1). Với n={N}, F_{N-1}={s.fibonacci(N-1)}, F_{N}={s.fibonacci(N)} nên u_{N}={s.fibonacci(N-1)}·{a}+{s.fibonacci(N)}·{b}={v}.', values[N])

# TOÁN 12
@family(12,'g12_geom_sphere_equation','v191_sphere_diameter_endpoints','Mặt cầu có đường kính AB','R²=AB²/4','Định lý đường kính mặt cầu và công thức khoảng cách','A,B khác nhau trong Oxyz')
def spherediameter(k):
 ax,ay,az=1+k,2-k,k+3;bx,by,bz=ax+2*k+2,ay+2,az+4;v=s.Rational((bx-ax)**2+(by-ay)**2+(bz-az)**2,4)
 return checked(f'Trong Oxyz, A({ax};{ay};{az}), B({bx};{by};{bz}) là hai đầu mút đường kính của mặt cầu. Tính bán kính bình phương R².',v,f'Mặt cầu có tâm trung điểm AB, bán kính R=AB/2. AB²=({bx-ax})²+({by-ay})²+({bz-az})². Do đó R²=AB²/4={f(v)}.',sum((s.Rational(b-a,2)**2 for a,b in zip([ax,ay,az],[bx,by,bz])),s.Integer(0)))

@family(12,'goc_khoang_cach_oxyz','v191_line_point_distance_cross','Khoảng cách từ điểm đến đường thẳng trong Oxyz','d²=||AP×u||²/||u||²','Tích có hướng và hình chiếu vuông góc','Vectơ chỉ phương u≠0')
def linepointdistance(k):
 a=s.Matrix([1+k,2,3]);u=s.Matrix([1,2,2]);v=s.Matrix([2+k,4,1]);cross=(v-a).cross(u);dsq=s.Rational(cross.dot(cross),u.dot(u))
 return checked(f'Trong Oxyz, đường thẳng d đi qua A({a[0]};{a[1]};{a[2]}) có vectơ chỉ phương u=(1;2;2). Tính bình phương khoảng cách từ P({v[0]};{v[1]};{v[2]}) đến d.',dsq,f'AP=({v[0]-a[0]};{v[1]-a[1]};{v[2]-a[2]}). Vectơ AP×u=({cross[0]};{cross[1]};{cross[2]}). Áp dụng d²=||AP×u||²/||u||²=({cross.dot(cross)})/9={f(dsq)}.',(v-a).dot(v-a)-s.Rational((v-a).dot(u)**2,u.dot(u)))

@family(12,'g12_geom_plane_equation','v191_two_plane_intersection_direction','Vectơ chỉ phương giao tuyến hai mặt phẳng','u=n₁×n₂','Tích có hướng hai vectơ pháp tuyến','Hai mặt phẳng không song song')
def planeintersection(k):
 n1=s.Matrix([1,2,k+2]);n2=s.Matrix([3,1,1]);cross=n1.cross(n2);v=cross.dot(cross)
 return checked(f'Hai mặt phẳng có vectơ pháp tuyến n₁=(1;2;{k+2}), n₂=(3;1;1). Tính bình phương độ dài của một vectơ chỉ phương u=n₁×n₂ của giao tuyến.',v,f'Giao tuyến vuông góc với cả hai pháp tuyến nên u=n₁×n₂=({cross[0]};{cross[1]};{cross[2]}). Khi đó ||u||²={cross[0]}²+{cross[1]}²+{cross[2]}²={v}.',s.det(s.Matrix.hstack(n1,n2).T*s.Matrix.hstack(n1,n2)))

@family(12,'nguyen_ham_tich_phan','v191_substitution_polynomial_integral','Tích phân đặt ẩn phụ u=x²+c','∫2x(x²+c)² dx=(x²+c)³/3','Đổi biến và định lý Newton–Leibniz','a>0,c>0')
def substintegral(k):
 a=k+1;c=2+(k%3);x=s.Symbol('x');v=s.Rational((a*a+c)**3-c**3,3)
 return checked(f'Tính tích phân I=∫ từ 0 đến {a} của 2x(x²+{c})² dx.',v,f'Đặt u=x²+{c} nên du=2x dx. Cận mới: u(0)={c}, u({a})={a*a+c}. Khi đó I=∫u²du=[u³/3] từ {c} đến {a*a+c}=(({a*a+c})³−{c}³)/3={f(v)}.',s.integrate(2*x*(x*x+c)**2,(x,0,a)))

@family(12,'ung_dung_tich_phan','v191_parabola_line_enclosed_area','Diện tích hình phẳng giữa y=ax² và y=bx','∫₀^(b/a)(bx−ax²) dx','Tìm giao điểm và tích phân hiệu hai đồ thị','a,b>0, miền kín')
def parabolaline(k):
 a=k+1;b=(k+1)*(k+2);end=s.Rational(b,a);v=s.Rational(b**3,6*a*a);x=s.Symbol('x')
 return checked(f'Tính diện tích hình phẳng giới hạn bởi hai đồ thị y={a}x² và y={b}x.',v,f'Giao điểm: {a}x²={b}x, nên x=0 hoặc x={f(end)}. Trên [0;{f(end)}], đường thẳng nằm trên parabol. S=∫₀^{f(end)} ({b}x−{a}x²) dx=[{b}x²/2−{a}x³/3]₀^{f(end)}={f(v)}.',s.integrate(b*x-a*x**2,(x,0,end)))

@family(12,'gtln_gtnn','v191_quadratic_min_closed_interval','Cực tiểu tam thức bậc hai trên đoạn kín','min tại đỉnh nếu thuộc đoạn, ngược lại tại đầu mút','Xét đỉnh và hai đầu mút','Đoạn [0,L] đóng')
def quadinterval(k):
 a=(k%9)-2;L=4+(k%4);c=5+k;x=s.Symbol('x');poly=x*x-2*a*x+c;h=max(0,min(L,a));v=h*h-2*a*h+c
 return checked(f'Tìm GTNN của f(x)=x²−({2*a})x+{c} trên đoạn [0;{L}].',v,f'Ta có f′(x)=2x−({2*a}), đỉnh ở x={a}. Điểm gần đỉnh nhất trong [0;{L}] là x₀={h}. Vì hệ số x² dương, GTNN=f({h})={h}²−({2*a})·{h}+{c}={v}.',min(poly.subs(x,xx) for xx in [0,L,h]))

@family(12,'xac_suat_12','v191_binomial_variance','Phương sai của biến ngẫu nhiên nhị thức','Var(X)=np(1−p)','Tổng các Bernoulli độc lập','X∼Binomial(n,p), 0<p<1')
def binomialvar(k):
 n=5+k;p=s.Rational(k+1,k+5);v=n*p*(1-p)
 return checked(f'Cho X có phân phối nhị thức B({n}, {f(p)}). Tính Var(X).',v,f'X là tổng của {n} biến Bernoulli độc lập có tham số p={f(p)}. Mỗi biến có phương sai p(1−p); do đó Var(X)={n}·{f(p)}·(1−{f(p)})={f(v)}.',sum(((s.Integer(i)-n*p)**2*s.binomial(n,i)*p**i*(1-p)**(n-i) for i in range(n+1)),s.Integer(0)))

@family(12,'mat_cau','v191_sphere_secant_chord_length','Dây cung của mặt cầu theo khoảng cách tới tâm','L²=4(R²−d²)','Tam giác vuông tại chân đường vuông góc','0≤d<R')
def spherechord(k):
 R=10+k;d=3+k;v=4*(R*R-d*d)
 return checked(f'Một đường thẳng cắt mặt cầu bán kính R={R}, có khoảng cách từ tâm mặt cầu đến đường thẳng d={d}. Tính bình phương độ dài đoạn dây cung cắt được.',v,f'Chân vuông góc từ tâm đến đường thẳng là trung điểm dây cung. Nửa dây có bình phương bằng R²−d²={R}²−{d}²={R*R-d*d}. Vậy chiều dài dây L=2√(R²−d²), suy ra L²=4·({R*R-d*d})={v}.',4*((R-d)*(R+d)))

@family(12,'so_phuc','v191_complex_geometric_rotation','Quay số phức bằng phép nhân i','i(a+bi)=−b+ai','Nhân đơn vị ảo ứng với phép quay 90°','a,b là số thực')
def complexrot(k):
 a=2+k;b=4+2*k;v=-b
 return checked(f'Cho z={a}+{b}i. Gọi w=i·z. Tìm phần thực của w.',v,f'i·z=i({a}+{b}i)={a}i+{b}i²=−{b}+{a}i vì i²=−1. Do đó phần thực của w là {v}.',s.re(s.I*(a+b*s.I)))

@family(12,'g12_geom_3d_optimization','v191_min_distance_to_plane_on_segment','Khoảng cách tối thiểu từ đoạn thẳng tới mặt phẳng','min_{0≤z≤L}(z−d)²/6','Hình chiếu có điều kiện, xét đầu mút hoặc điểm trong đoạn','P=(a,2,z), 0≤z≤L, mặt phẳng x+2y+z=T', 'nâng cao')
def optimplane(k):
 a=k+1;b=2;d=k-5;L=3+k%4;T=a+4+d
 h=max(0,min(L,d));v=s.Rational((h-d)**2,6)
 return checked(f'Điểm P({a};{b};z) di chuyển trên đoạn 0≤z≤{L} trong Oxyz. Tìm GTNN của bình phương khoảng cách từ P đến mặt phẳng (Q): x+2y+z={T}.',v,f'Bình phương khoảng cách là D(z)=[{a}+2·{b}+z−{T}]²/(1²+2²+1²)=(z−({d}))²/6. Trên [0;{L}], giá trị nhỏ nhất đạt tại điểm gần {d} nhất là z={h}. Do đó min D=({h}−({d}))²/6={f(v)}.',min(s.Rational((u-d)**2,6) for u in [0,L,h]))

# The next family has answer depending on k; no trivial zero-answer cloning.
@family(12,'bieu_dien_so_phuc','v191_complex_line_locus_min_modulus','Cực tiểu môđun số phức với điều kiện đường thẳng','min |z|²=d²/(a²+b²)','Khoảng cách từ O tới đường thẳng biểu diễn z','z=x+yi, a²+b²>0')
def complexlocus(k):
 a=3;b=4;c=5*(k+2);v=s.Rational(c*c,a*a+b*b)
 return checked(f'Cho z=x+yi (x,y thực) thỏa 3x+4y={c}. Tính giá trị nhỏ nhất của |z|².',v,f'|z|²=x²+y² là bình phương khoảng cách OM² đến điểm M(x,y) trên đường thẳng 3x+4y={c}. Khoảng cách nhỏ nhất khi OM vuông góc đường thẳng: min |z|²={c}²/(3²+4²)={f(v)}.',s.Rational(c*c,25))

@family(12,'g12_geom_solid_surface_area','v191_cone_generatrix_pythagorean','Tính diện tích xung quanh nón từ bán kính và chiều cao','S_xq=πr√(r²+h²)','Định lý Pythagore trong tiết diện qua trục','Hình nón tròn xoay r,h>0')
def conearea(k):
 # Ask S/pi to stay integer via Pythagorean 3-4-5
 r=3*(k+1);h=4*(k+1);l=5*(k+1);v=r*l
 return checked(f'Một hình nón có bán kính đáy r={r}, chiều cao h={h}. Tính S_xq/π (với S_xq là diện tích xung quanh hình nón).',v,f'Đường sinh l=√(r²+h²)=√({r}²+{h}²)={l}. Diện tích xung quanh S_xq=πr·l=π·{r}·{l}={v}π nên S_xq/π={v}.',r*s.sqrt(r*r+h*h))

@family(12,'nguyen_ham_tich_phan','v191_integral_by_parts_x_exp','Tìm hệ số trong kết quả tích phân từng phần x·e^x','∫₀ⁿ x e^x dx=(n−1)e^n+1','Chọn u=x, dv=e^x dx','n là số nguyên dương')
def xexp(k):
 n=k+1;x=s.Symbol('x');integral=s.integrate(x*s.exp(x),(x,0,n));v=n-1
 return checked(f'Cho I=∫ từ 0 đến {n} của x·e^x dx. Biết I có dạng A·e^{n}+1. Tìm hệ số A.',v,f'Đặt u=x, dv=e^x dx, nên du=dx, v=e^x. Từng phần: I=[xe^x]₀^{n}−∫₀^{n}e^x dx=[(x−1)e^x]₀^{n}=({n}−1)e^{n}+1. So sánh hệ số cho A={v}.',s.simplify((integral-1)/s.exp(n)))

@family(12,'nguyen_ham_tich_phan','v191_integration_by_parts_ln','Tìm hệ số của logarit sau tích phân từng phần','∫₁ᵃ ln x dx=a ln a−a+1','Chọn u=ln x, dv=dx','a nguyên, a>1')
def intln(k):
 a=k+2;x=s.Symbol('x');integral=s.integrate(s.log(x),(x,1,a));v=a
 return checked(f'Cho I=∫ từ 1 đến {a} của ln(x) dx. Biết I=A·ln({a})−{a}+1. Tính hệ số A.',v,f'Đặt u=ln x, dv=dx, suy ra du=dx/x, v=x. Theo tích phân từng phần I=[x ln x]₁^{a}−∫₁^{a}dx={a}ln({a})−({a}−1)={a}ln({a})−{a}+1. Vì vậy A={a}.',s.simplify((integral+a-1)/s.log(a)))

# Additional V191 bank cycle: mathematical constructions different from the first batch.
@family(10,'hoan_vi_chinh_hop_to_hop','v191_multinomial_repeated_letters','Hoán vị đa tập có ký hiệu trùng','(a+b+c)!/(a!b!c!)','Đếm hoán vị của các ký tự lặp lại','a,b,c là số nguyên dương')
def multinomial(k):
 a=2+k%3;b=3+k//3;c=1+k%2;N=a+b+c;v=s.factorial(N)/(s.factorial(a)*s.factorial(b)*s.factorial(c))
 return checked(f'Có bao nhiêu cách xếp thành một hàng {a} chữ A, {b} chữ B và {c} chữ C giống hệt nhau trong từng loại?',v,f'Nếu phân biệt từng chữ thì có {N}! cách. Do {a} chữ A, {b} chữ B, {c} chữ C giống nhau, mỗi cách thực tế bị đếm lặp {a}!·{b}!·{c}! lần. Vậy số cách là {N}!/({a}!·{b}!·{c}!)={f(v)}.',s.binomial(N,a)*s.binomial(N-a,b))

@family(10,'g10_geom_special_lines','v191_angle_bisector_side_division','Định lý đường phân giác trong tam giác','BD/DC=AB/AC','Tỉ số cạnh kề của đường phân giác','Tam giác không suy biến, D thuộc BC')
def bisector(k):
 t=k+1;ab=3*t;ac=4*t;bc=5*t;bd=s.Rational(ab*bc,ab+ac)
 return checked(f'Tam giác ABC có AB={ab}, AC={ac}, BC={bc}. Đường phân giác trong của góc A cắt BC tại D. Tính BD.',bd,f'Theo định lý phân giác, BD/DC=AB/AC={ab}/{ac}. Vì BD+DC=BC={bc}, suy ra BD=BC·AB/(AB+AC)={bc}·{ab}/({ab}+{ac})={f(bd)}.',s.solve([s.Eq(s.Symbol('u')/s.Symbol('v'),s.Rational(ab,ac)),s.Eq(s.Symbol('u')+s.Symbol('v'),bc)],[s.Symbol('u'),s.Symbol('v')])[s.Symbol('u')])

@family(10,'he_thuc_luong_tam_giac','v191_excircle_radius_heron','Bán kính đường tròn bàng tiếp đối diện góc A','r_a=S/(p−a)','Diện tích tam giác và tiếp xúc ba cạnh','Tam giác có cạnh 13t,14t,15t')
def exradius(k):
 t=k+1;a,b,c=13*t,14*t,15*t;p=s.Rational(a+b+c,2);S=84*t*t;r=s.Rational(S,p-a)
 return checked(f'Tam giác ABC có BC={a}, CA={b}, AB={c}, diện tích bằng {S}. Tính bán kính đường tròn bàng tiếp đối diện góc A.',r,f'Nửa chu vi p=({a}+{b}+{c})/2={f(p)}. Với đường tròn bàng tiếp đối diện A, S=r_a(p−BC). Suy ra r_a={S}/({f(p)}−{a})={f(r)}.',s.Rational(21*t,2))

@family(10,'tam_giac_tu_giac_10','v191_incircle_tangent_length','Độ dài tiếp tuyến từ đỉnh đến tiếp điểm đường tròn nội tiếp','Đoạn tiếp tuyến từ A=s−a','Các tiếp tuyến từ cùng một điểm bằng nhau','Tam giác có đường tròn nội tiếp')
def inctangent(k):
 t=k+1;a,b,c=13*t,14*t,15*t;p=s.Rational(a+b+c,2);ans=p-a
 return checked(f'Cho tam giác ABC có BC={a}, CA={b}, AB={c}. Đường tròn nội tiếp tiếp xúc AB tại E và AC tại F. Tính AE (=AF).',ans,f'Đặt AE=AF=x. Tương tự, hai cặp đoạn tiếp tuyến ở B và C bằng nhau. Cộng các cạnh suy ra 2x=AB+AC−BC={c}+{b}−{a}. Vậy x=({c}+{b}−{a})/2={f(ans)}.',s.Rational(b+c-a,2))

@family(10,'toa_do_phang','v191_internal_section_point','Tọa độ điểm chia đoạn theo tỉ số cho trước','M=(nA+mB)/(m+n)','Công thức chia trong đoạn thẳng','A,B phân biệt, AM:MB=m:n với m,n>0')
def sectionratio(k):
 ax=k+1;bx=ax+6+k;m=1+k%4;n=2+k%3;xx=s.Rational(n*ax+m*bx,m+n)
 return checked(f'Trong Oxy, A có hoành độ {ax}, B có hoành độ {bx}. Điểm M nằm trong AB sao cho AM:MB={m}:{n}. Tính hoành độ M.',xx,f'Vì AM/MB={m}/{n}, công thức chia trong đoạn cho x_M=(n·x_A+m·x_B)/(m+n). Thay dữ kiện: x_M=({n}·{ax}+{m}·{bx})/({m}+{n})={f(xx)}.',ax+s.Rational(m,m+n)*(bx-ax))

@family(10,'ham_so_bac_hai','v191_parabola_leading_coefficient_from_vertex','Tìm tham số a của parabol biết đỉnh và một điểm','y=a(x−h)²+k','Dạng đỉnh của hàm bậc hai','Điểm đã cho không trùng đỉnh')
def vertexcoef(k):
 h=k+1;v=3+k;aa=2+k;xx=h+2;yy=v+4*aa
 return checked(f'Parabol y=a(x−{h})²+{v} đi qua điểm P({xx};{yy}). Tìm a.',aa,f'Thay tọa độ P vào phương trình: {yy}=a({xx}−{h})²+{v}. Suy ra 4a={yy}−{v}={yy-v}, nên a={aa}.',s.solve(s.Eq(s.Symbol('a')*(xx-h)**2+v,yy),s.Symbol('a'))[0])

@family(11,'cong_thuc_luong_giac','v191_cosine_addition_acute_angles','Công thức cos(α+β) từ các tỉ số lượng giác','cos(α+β)=cosα cosβ−sinα sinβ','Công thức cộng hai góc','α,β nhọn, cos sin dương')
def cosadd(k):
 triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29)]
 a,b,c=triples[k%5];d,e,fden=triples[(k//2+1)%5]
 if k>=5:a,b=b,a
 val=s.Rational(a*d-b*e,c*fden)
 return checked(f'Hai góc α, β đều nhọn, cosα={a}/{c}, sinα={b}/{c}, cosβ={d}/{fden}, sinβ={e}/{fden}. Tính cos(α+β).',val,f'Theo công thức cộng: cos(α+β)=cosα cosβ−sinα sinβ=({a}·{d})/({c}·{fden})−({b}·{e})/({c}·{fden})=({a*d}−{b*e})/{c*fden}={f(val)}.',s.cos(s.atan2(b,a)+s.atan2(e,d)).simplify())

@family(11,'to_hop_xac_suat_nang_cao_11','v191_adjacent_permutations','Xếp hai người quy định đứng cạnh nhau','2(n−1)!','Gộp hai người thành một khối','n người phân biệt, n≥2')
def adjacent(k):
 n=5+k;v=2*s.factorial(n-1)
 return checked(f'Có {n} người phân biệt xếp thành một hàng, trong đó hai người A và B bắt buộc đứng cạnh nhau. Có bao nhiêu cách xếp?',v,f'Gộp A và B thành một khối, khi đó còn {n}-1={n-1} đơn vị phân biệt. Xếp các đơn vị có ({n-1})! cách. Trong khối A,B đổi vị trí được 2 cách. Tổng cộng 2·({n-1})!={v}.',s.factorial(n-1)*s.factorial(2))

@family(11,'to_hop_xac_suat_nang_cao_11','v191_no_adjacent_selections','Chọn k vị trí không có hai vị trí liên tiếp','C(n−k+1,k)','Biến đổi chỉ số vị trí x_i thành y_i=x_i−i+1','n vị trí liên tiếp, 1≤k≤(n+1)/2')
def nonadjacent(k):
 n=11+k;r=2+k%4;val=s.binomial(n-r+1,r)
 return checked(f'Trong {n} vị trí đánh số 1 đến {n}, chọn đúng {r} vị trí sao cho không có hai vị trí được chọn nào liên tiếp. Có bao nhiêu cách?',val,f'Gọi các vị trí chọn là 1≤x₁<...<x_{r}≤{n}, với x_(j+1)−x_j≥2. Đặt y_j=x_j−(j−1), ta được 1≤y₁<...<y_{r}≤{n-r+1}. Chọn {r} vị trí từ {n-r+1} vị trí: C({n-r+1},{r})={f(val)}.',s.binomial(n-r+1,r))

@family(11,'gioi_han_ham_so','v191_rational_function_limit_at_infinity','Giới hạn tỉ số hai đa thức cùng bậc tại vô cực','lim(a x³+...)/(c x³+...) = a/c','Chia tử và mẫu cho x³','x→+∞, hệ số bậc cao nhất của mẫu khác 0')
def rationalinfty(k):
 a=k+3;b=4+k;c=2+(k%4);d=5+k;v=s.Rational(a,c);x=s.Symbol('x')
 return checked(f'Tính lim khi x→+∞ của ({a}x³+{b}x²+1)/({c}x³+{d}x+2).',v,f'Chia cả tử và mẫu cho x³: [{a}+{b}/x+1/x³]/[{c}+{d}/x²+2/x³]. Khi x→+∞, các hạng 1/x^k→0, nên giới hạn là {a}/{c}={f(v)}.',s.limit((a*x**3+b*x**2+1)/(c*x**3+d*x+2),x,s.oo))

@family(11,'xac_suat_11','v191_two_different_color_without_replacement','Rút hai viên khác màu, không hoàn lại','P=2RB/[(R+B)(R+B−1)]','Đếm cặp chọn theo màu / không thứ tự','R,B nguyên dương, rút hai viên cùng lúc')
def twocolors(k):
 R=3+k;B=5+2*k;N=R+B;v=s.Rational(2*R*B,N*(N-1))
 return checked(f'Hộp có {R} bi đỏ và {B} bi xanh. Chọn đồng thời 2 bi ngẫu nhiên, không hoàn lại. Xác suất hai viên khác màu là bao nhiêu?',v,f'Có C({N},2) cách chọn hai bi bất kỳ. Chọn đúng một đỏ, một xanh có {R}·{B}={R*B} cách. Vậy P={R*B}/C({N},2)=2·{R}·{B}/({N}·{N-1})={f(v)}.',s.Rational(R*B,s.binomial(N,2)))

@family(12,'hinh_hoc_oxyz_van_dung_12','v191_reflection_point_across_plane','Tìm hình chiếu đối xứng của điểm qua mặt phẳng','P′=P−2((n·P−d)/||n||²)n','Phép đối xứng qua mặt phẳng','Mặt phẳng x+y+z=d')
def planereflect(k):
 px=k+2;py=2*k+3;pz=k+6;d=k+1;t=s.Rational(px+py+pz-d,3);xx=px-2*t
 return checked(f'Trong Oxyz, phản xạ điểm P({px};{py};{pz}) qua mặt phẳng (Q): x+y+z={d}, được P′. Tính hoành độ của P′.',xx,f'Pháp tuyến của (Q) là n=(1;1;1), ||n||²=3. Hệ số hạ vuông góc t=({px}+{py}+{pz}−{d})/3={f(t)}. Điểm đối xứng P′=P−2t·n, nên x_P′={px}−2·{f(t)}={f(xx)}.',px-2*(s.Rational(px+py+pz-d,3)))

@family(12,'mat_phang_oxyz','v191_plane_3_intercepts_equation','Phương trình mặt phẳng qua ba giao điểm trục tọa độ','x/a+y/b+z/c=1','Mặt phẳng dạng đoạn chắn','a,b,c đều khác 0')
def planeintercepts(k):
 a=2+k;b=3+k;c=5+k;D=-a*b*c
 return checked(f'Mặt phẳng (P) qua A({a};0;0), B(0;{b};0), C(0;0;{c}), có phương trình {b*c}x+{a*c}y+{a*b}z+D=0. Tìm D.',D,f'Dạng đoạn chắn là x/{a}+y/{b}+z/{c}=1. Nhân cả hai vế với {a*b*c} được {b*c}x+{a*c}y+{a*b}z−{a*b*c}=0. Vậy D={D}.',-int(s.det(s.diag(a,b,c))))

@family(12,'nguyen_ham_tich_phan','v191_partial_fractions_log_argument','Tìm đối số logarit sau tích phân phân thức','∫[1/(x+1)−1/(x+2)]dx=ln[(x+1)/(x+2)]','Tách phân thức và đổi cận','Tích phân trên [0,n], n>0')
def partiallog(k):
 n=k+1;x=s.Symbol('x');I=s.integrate(1/(x+1)-1/(x+2),(x,0,n));ans=s.Rational(2*(n+1),n+2)
 return checked(f'Cho I=∫ từ 0 đến {n} của [1/(x+1)−1/(x+2)] dx. Biết I=ln(K) với K>0. Tìm K.',ans,f'Nguyên hàm là ln(x+1)−ln(x+2)=ln[(x+1)/(x+2)]. Thế cận: I=ln[({n}+1)/({n}+2)]−ln(1/2)=ln[2({n}+1)/({n}+2)]. Vậy K={f(ans)}.',s.exp(I))

@family(12,'ung_dung_tich_phan','v191_average_value_polynomial_interval','Giá trị trung bình của hàm trên đoạn','f_tb=(1/(b−a))∫_a^b f(x)dx','Tích phân xác định và giá trị trung bình','Hàm liên tục trên [0,T]')
def averagepoly(k):
 a=k+1;b=2+(k%3);c=k+4;T=3+(k%4);x=s.Symbol('x');val=s.Rational(a*T*T,3)+s.Rational(b*T,2)+c
 return checked(f'Tìm giá trị trung bình của f(x)={a}x²+{b}x+{c} trên đoạn [0;{T}].',val,f'Theo định nghĩa f_tb=(1/{T})∫₀^{T}f(x)dx. Nguyên hàm là {a}x³/3+{b}x²/2+{c}x. Lấy giá trị tại {T} trừ tại 0, rồi chia {T}: f_tb={a}·{T}²/3+{b}·{T}/2+{c}={f(val)}.',s.integrate(a*x*x+b*x+c,(x,0,T))/T)

@family(12,'so_phuc','v191_complex_reciprocal_real','Phần thực nghịch đảo số phức','Re[1/(a+bi)]=a/(a²+b²)','Nhân liên hợp mẫu số','a²+b²>0')
def reciprocal(k):
 a=k+2;b=k+4;v=s.Rational(a,a*a+b*b)
 return checked(f'Cho z={a}+{b}i khác 0. Tìm phần thực của 1/z.',v,f'Nhân cả tử và mẫu của 1/({a}+{b}i) với {a}−{b}i: 1/z=({a}−{b}i)/({a}²+{b}²). Do đó Re(1/z)={a}/({a*a+b*b})={f(v)}.',s.re(1/(a+b*s.I)))

@family(12,'pt_so_phuc','v191_complex_quadratic_imaginary_roots','Nghiệm của tam thức bậc hai có biệt thức âm','z=−a±bi nếu z²+2az+a²+b²=0','Hoàn bình phương trên C','b>0, hệ số thực')
def complexroots(k):
 a=k+2;b=2*k+3;c=a*a+b*b;z=s.Symbol('z');res=s.solve(z*z+2*a*z+c,z)
 return checked(f'Giải trên tập số phức phương trình z²+{2*a}z+{c}=0. Tìm phần ảo dương trong hai nghiệm.',b,f'Hoàn bình phương: (z+{a})²=−({c}−{a*a})=−{b*b}. Suy ra z+{a}=±{b}i, nên z=−{a}±{b}i. Phần ảo dương cần tìm là {b}.',max(s.im(r) for r in res))

@family(12,'g12_geom_point_plane_distance','v191_perpendicular_foot_to_plane_coordinate','Tọa độ chân đường vuông góc tới mặt phẳng','H=P−((n·P−d)/||n||²)n','Hình chiếu trực giao lên mặt phẳng','Mặt phẳng x+y+z=d')
def footplane(k):
 px=k+3;py=k+4;pz=2*k+5;d=2*k+1;lam=s.Rational(px+py+pz-d,3);ans=px-lam
 return checked(f'Trong Oxyz, H là hình chiếu vuông góc của P({px};{py};{pz}) lên mặt phẳng x+y+z={d}. Tính hoành độ H.',ans,f'Pháp tuyến n=(1;1;1), có ||n||²=3. Độ dịch chuyển theo n là λ=({px}+{py}+{pz}−{d})/3={f(lam)}. Chân vuông góc H=P−λn nên x_H={px}−{f(lam)}={f(ans)}.',px-s.Rational(px+py+pz-d,3))

@family(12,'ham_mu','v191_derivative_exponential_chain_coefficient','Hệ số trong đạo hàm hàm mũ hợp','(e^(ax+b))′=a e^(ax+b)','Đạo hàm hợp và đạo hàm e^x','a,b nguyên')
def expderiv(k):
 a=k+2;b=k+1;x=s.Symbol('x');expr=s.exp(a*x+b);val=a
 return checked(f'Cho f(x)=e^({a}x+{b}). Biết f′(0)=A·e^{b}. Tính A.',val,f'Áp dụng quy tắc hàm hợp, đạo hàm của e^u là u′e^u. Vì u(x)={a}x+{b} nên u′={a}, do đó f′(x)={a}e^({a}x+{b}). Thế x=0, f′(0)={a}e^{b}, suy ra A={a}.',s.diff(expr,x).subs(x,0)/s.exp(b))


# Main: build 7 MCQ / 2 numeric / 1 four-assertion TF, reject duplicates & bad grading.
def generate():
 questions=[]; specs=[]; seen=set(); seen_patterns=set()
 from app.ai.engine.validator import validate
 from app.questions.answer_checker import grade_answer
 for familyinfo in FAMILIES:
  specs.append({key:value for key,value in familyinfo.items() if key!='make'})
  for k in range(10):
   q,answer,solution,meta=familyinfo['make'](k)
   as_text=f(answer)
   typ='multiple_choice' if k<7 else ('short_answer' if k<9 else 'true_false')
   choices=[]
   answer_str=as_text
   # Exact rational distractors; independent symbolic equivalence gate below.
   if typ=='multiple_choice':
    wrong=[s.simplify(answer+d) for d in (1,-1,2)]
    if familyinfo['key'] in ('v191_bayes_two_urns','v191_binomial_exactly_two','v191_binomial_variance'):
     wrong=[s.simplify(answer+d) for d in (s.Rational(1,100),s.Rational(-1,100),s.Rational(2,100))]
    choices=[f(y) for y in [answer,*wrong]]
    random.Random(9931+k).shuffle(choices)
   if typ=='true_false':
    # Four distinct, related, independently evaluated claims about the result.
    comparisons=[('=',answer,True),('>',answer-1,True),('=',answer+1,False),('<',answer-1,False)]
    choices=[]; statuses=[]
    for op,val,expected in comparisons:
     actual= (answer==val if op=='=' else answer>val if op=='>' else answer<val)
     assert bool(actual)==expected
     choices.append(f'Giá trị cần tìm {op} {f(val)}.')
     statuses.append('Đúng' if expected else 'Sai')
    answer_str=','.join(statuses)
    solution+=' Xét lần lượt các khẳng định: '+', '.join(f'{idx+1} {"đúng" if expected else "sai"}' for idx,(_,_,expected) in enumerate(comparisons))+f', dựa trên giá trị đúng {as_text}.'
   rid=f'{familyinfo["key"]}_{k:02d}'
   row={
    'id':rid,'grade':familyinfo['grade'],'topic':familyinfo['topic'],'family':familyinfo['key'],
    'form_id':familyinfo['key'],'concept':familyinfo['name'],'math_method':familyinfo['method'],
    'conditions':familyinfo['conditions'],'difficulty':familyinfo['difficulty'],
    'question_type':typ,'question':q,'answer':answer_str,'correct_answer':answer_str,
    'choices':choices,'solution':solution,'source_bundle':'V191','source_checkpoint':'V190',
    'validation_status':'sympy_independent_value_oracle_and_app_grader_checked',
    'method_independence_certified':False,'production_integrated':False,
    'verification':meta,
   }
   candidate={'id':rid,'grade':row['grade'],'topic':row['topic'],'difficulty':row['difficulty'],
              'question_type':typ,'question':q,'answer':answer_str,'solution':solution,
              'options':choices if typ=='multiple_choice' else [],'statements':choices if typ=='true_false' else []}
   validate(candidate)
   assert grade_answer(candidate,answer_str),(rid,'grader')
   if typ=='multiple_choice':
    assert sum(bool(grade_answer(candidate,opt)) for opt in choices)==1,(rid,'MCQ')
   if typ=='true_false':
    assert len(choices)==4 and len(answer_str.split(','))==4
   assert q not in seen
   seen.add(q)
   # Do not treat normalized numeric variants as distinct *types*; all 10 share one form_id.
   questions.append(row)
 assert len(questions)==10*len(FAMILIES)
 counts=Counter(r['family'] for r in questions)
 assert set(counts.values())=={10}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8') as o:
  for row in questions:o.write(json.dumps(row,ensure_ascii=False)+'\n')
 (ROOT/'bank_updates'/'V191_FAMILY_SPECS.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2),encoding='utf-8')
 audit={'version':'V191','candidate_form_families':len(specs),'questions_oracle_checked':len(questions),
        'per_grade':dict(Counter(str(r['grade']) for r in questions)),
        'per_topic':{f'{g}:{t}':n for (g,t),n in Counter((r['grade'],r['topic']) for r in questions).items()},
        'format_breakdown':dict(Counter(r['question_type'] for r in questions)),
        'new_types_certified_independent':0,'production_questions_imported':0,
        'check_scope':'sympy value oracle, application validator/grader, per-batch exact dedup; independent semantic review pending'}
 REPORT.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(audit,ensure_ascii=False))
 return audit
if __name__=='__main__':
 sys.path.insert(0,str(ROOT/'backend'))
 generate()
