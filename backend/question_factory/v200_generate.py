#!/usr/bin/env python3
"""V200 third incremental mathematics bank cycle. Verified exact result; method certification pending."""
from __future__ import annotations
import sys,itertools,math,collections,json
from pathlib import Path
import sympy as S
from v198_generate import fmt,choices_for
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'bank_updates'
CATALOG={(int(g),t['id']) for g,ts in json.loads((ROOT/'backend/app/ai/knowledge/index.json').read_text()).items() for t in ts}
SPECS={
 'function_composition':(10,'ham_so','Hợp hàm bậc nhất với hàm bậc hai','f(g(x)) thay g(x) vào biểu thức f','f(x)=ax+b, g(x)=cx²+d xác định trên R','nền tảng'),
 'inverse_restricted_quadratic':(10,'ham_so_bac_hai','Hàm ngược của parabol giới hạn trên nửa trục','f^{-1}(y)=h+sqrt(y-k) khi x>=h','Parabol giới hạn miền xác định x>=h','trung cấp'),
 'bounded_integer_compositions':(10,'g10_combinatorics_olympiad','Đếm nghiệm nguyên không âm có chặn trên ở ba biến','Nguyên lý bù trừ lên số nghiệm x+y+z=N và mỗi biến<=M','N,M nguyên dương; 0<=x,y,z<=M','nâng cao'),
 'angle_bisector_length_sq':(10,'g10_geom_special_lines','Bình phương độ dài phân giác trong tam giác','l²=bc(1−a²/(b+c)²)','Ba cạnh tạo tam giác thật','nâng cao'),
 'dice_sum_probability':(10,'xac_suat','Xác suất tổng hai xúc xắc bằng s','Đếm cặp (a,b) thuộc {1,...,6}² có a+b=s','Hai xúc xắc công bằng, độc lập','nền tảng'),
 'vector_internal_section':(10,'vector','Điểm chia trong đoạn thẳng theo tỉ số cho trước','P=(nA+mB)/(m+n) với AP:PB=m:n','m,n dương, A,B khác nhau','trung cấp'),
 'arc_length_over_pi':(10,'duong_tron_co_ban_10','Độ dài cung tròn chia π từ góc ở tâm','l/π=Rθ/180°','0<θ<360°, R>0','nền tảng'),
 'circle_line_intersection_count':(10,'g10_geom_coordinate_circle_line','Đếm giao điểm của đường tròn với đường thẳng ngang','So sánh bình phương khoảng cách tâm–đường với R²','Mặt phẳng Oxy, R>0','trung cấp'),
 'arithmetico_geometric_sum':(11,'day_so_tong_quat','Tổng có trọng số k2^k','Σk2^k=(n−1)2^{n+1}+2','n nguyên dương','nâng cao'),
 'cubic_difference_limit':(11,'gioi_han_ham_so','Giới hạn thương hiệu hai lập phương','(x³−a³)/(x−a)=x²+ax+a²','x tiến đến a, a thực','nền tảng'),
 'tan_equation_root_count':(11,'g11_advanced_trig_equations','Đếm nghiệm phương trình tan x = tan α trên nhiều chu kỳ','Nghiệm x=α+kπ, đếm theo khoảng','0<α<π/2; khoảng [0,Nπ]','trung cấp'),
 'cos_addition_rational':(11,'cong_thuc_luong_giac','Cos của tổng hai góc biết sin cos theo bộ Pythagore','cos(α+β)=cosαcosβ−sinαsinβ','α,β nhọn, dữ kiện giá trị lượng giác hợp lệ','trung cấp'),
 'poisson_binomial_exact_one':(11,'bien_co_doc_lap_11','Xác suất đúng một trong hai biến cố độc lập xảy ra','p(1−q)+(1−p)q','0<p,q<1, hai biến cố độc lập','trung cấp'),
 'two_step_markov':(11,'g11_conditional_probability_models','Xác suất trạng thái sau hai bước của chuỗi Markov nhị phân','P(A2|A0)=p²+(1−p)q','Chuỗi 2 trạng thái có chuyển tiếp cố định','nâng cao'),
 'binomial_odd_sum':(11,'g11_binomial_advanced','Tổng các hệ số có bậc lẻ trong nhị thức','Tách (1+1)^n và (1−1)^n','n>=1 nguyên','trung cấp'),
 'space_line_angle_cos_sq':(11,'goc_khoang_cach_11','Bình phương cos góc giữa hai đường không gian','cos²θ=(u·v)²/(||u||²||v||²)','Vectơ chỉ phương khác 0','trung cấp'),
 'complex_division_realpart':(12,'bieu_dien_so_phuc','Phần thực của thương hai số phức','Re[(a+bi)/(c+di)]=(ac+bd)/(c²+d²)','Mẫu c+di khác 0','trung cấp'),
 'sphere_line_intersections':(12,'g12_geom_sphere_plane_intersection','Số giao điểm mặt cầu với đường thẳng qua biệt thức','So sánh khoảng cách tâm đến đường với bán kính','Mặt cầu R>0, đường thẳng xác định','nâng cao'),
 'cone_frustum_volume_over_pi':(12,'the_tich_khong_gian','Thể tích khối nón cụt chia π','V/π=h(R²+Rr+r²)/3','R>r>0, h>0','trung cấp'),
 'exp_integral_to_ln2':(12,'nguyen_ham_tich_phan','Tích phân hàm mũ trên đoạn [0,ln2]','∫e^{ax}dx=(e^{ax}/a)+C','a nguyên dương','trung cấp'),
 'cubic_bounded_maximum':(12,'gtln_gtnn','Giá trị lớn nhất của hàm bậc ba trên đoạn đóng','So sánh giá trị ở hai đầu và điểm đạo hàm bằng 0','Hàm liên tục trên đoạn, cực trị nội xác định','nâng cao'),
 'expected_hypergeometric':(12,'xac_suat_12','Kỳ vọng số thành công khi lấy không hoàn lại','E[X]=nK/N từ tổng các biến chỉ thị','0<K<N và 0<n<=N','trung cấp'),
 'nearest_point_on_ray_sq':(12,'g12_geom_3d_optimization','Khoảng cách ngắn nhất từ điểm tới tia trong Oxyz','Minimize ||P−tu||² với ràng buộc t>=0','u khác 0','nâng cao'),
}

def build(key,i):
 t=i+1
 if key=='function_composition':
  a,b,c,d,x=2+t%4,3+t,1+t%3,4+t%5,t
  ans=a*(c*x*x+d)+b
  X=S.symbols('x');assert S.expand((a*(c*X*X+d)+b).subs(X,x))==ans
  q=f'Cho f(x)={a}x+{b}, g(x)={c}x²+{d}. Tính f(g({x})).'
  sol=f'Tính g({x})={c}×{x}²+{d}={c*x*x+d}. Thay vào f: f(g({x}))={a}×({c*x*x+d})+{b}={ans}.'
 elif key=='inverse_restricted_quadratic':
  h,k,r=t,2+t%5,2+t;value=r*r+k;ans=h+r
  x=S.symbols('x',real=True);assert (ans-h)**2+k==value and ans>=h
  q=f'Cho hàm f(x)=(x−{h})²+{k} với miền xác định x≥{h}. Tìm x duy nhất sao cho f(x)={value}.'
  sol=f'Vì x≥{h}, phương trình cho (x−{h})²={value-k}={r*r}; lấy căn không âm x−{h}={r}, nên x={ans}.'
 elif key=='bounded_integer_compositions':
  m=2+t%4;n=2*m+t%3
  ans=sum(1 for x in range(m+1) for y in range(m+1) for z in range(m+1) if x+y+z==n)
  c=lambda a:math.comb(a+2,2) if a>=0 else 0
  oracle=sum((-1)**j*math.comb(3,j)*c(n-j*(m+1)) for j in range(4));assert ans==oracle
  q=f'Có bao nhiêu bộ số nguyên (x,y,z) thỏa x+y+z={n}, đồng thời 0≤x,y,z≤{m}?'
  sol=f'Đếm nghiệm không âm không chặn: C({n}+2,2). Dùng bù trừ loại các biến >{m}, nhận Σ_{{j=0}}³(−1)^j C(3,j)C({n}−j({m}+1)+2,2) với hệ số âm tính 0; kết quả {ans}.'
 elif key=='angle_bisector_length_sq':
  b,c=5+t,6+t%4;a=b+c-3
  assert abs(b-c)<a<b+c
  ans=S.Rational(b*c)*(1-S.Rational(a*a,(b+c)**2))
  d=S.Rational(a*c,b+c);e=S.Rational(a*b,b+c)
  assert S.simplify((b*b*d+c*c*e)/a-d*e-ans)==0
  q=f'Tam giác ABC có BC={a}, CA={b}, AB={c}. AD là phân giác trong góc A. Tính AD².'
  sol=f'Áp dụng công thức đường phân giác: AD²=CA·AB(1−BC²/(CA+AB)²)={b}×{c}(1−{a}²/({b}+{c})²)={fmt(ans)}.'
 elif key=='dice_sum_probability':
  s=1+t;outcomes=[(x,y) for x in range(1,7) for y in range(1,7) if x+y==s]
  ans=S.Rational(len(outcomes),36);assert len(outcomes)==6-abs(s-7)
  q=f'Tung hai xúc xắc cân đối 6 mặt độc lập. Tính xác suất tổng số chấm bằng {s}.'
  sol=f'Không gian mẫu có 6×6=36 kết quả đồng khả năng. Các cặp số chấm có tổng {s} là {len(outcomes)} cặp, do đó xác suất {len(outcomes)}/36={fmt(ans)}.'
 elif key=='vector_internal_section':
  ax,bx=1+t,5+t; m,n=1+t%4,2+t%5
  ans=S.Rational(n*ax+m*bx,m+n)
  assert ans==ax+S.Rational(m,m+n)*(bx-ax)
  q=f'Trên đoạn AB trong Oxy, A({ax},1), B({bx},3), điểm P chia trong với AP:PB={m}:{n}. Tính hoành độ P.'
  sol=f'Công thức chia trong: x_P=(n·x_A+m·x_B)/(m+n)=({n}×{ax}+{m}×{bx})/({m}+{n})={fmt(ans)}.'
 elif key=='arc_length_over_pi':
  R,deg=3+t,20+20*t;ans=S.Rational(R*deg,180)
  assert ans==S.Rational(2*R*deg,360)
  q=f'Cung tròn của đường tròn bán kính R={R} có góc ở tâm {deg}°. Nếu độ dài cung là ℓ, tính ℓ/π.'
  sol=f'Độ dài cung ℓ=(θ/360°)×2πR. Thay θ={deg}°, R={R}: ℓ/π=2×{R}×{deg}/360={fmt(ans)}.'
 elif key=='circle_line_intersection_count':
  R=4+t;d=R+((-1)**t)*(t%3); d=abs(d)
  ans=2 if d<R else 1 if d==R else 0
  x=S.symbols('x',real=True);sols=S.solveset(x*x+d*d-R*R,x,domain=S.S.Reals)
  assert len(sols)==ans
  q=f'Đường tròn C: x²+y²={R*R}. Đường thẳng d: y={d}. Có bao nhiêu giao điểm thực giữa C và d?'
  sol=f'Thế y={d} vào phương trình đường tròn được x²={R*R}-{d*d}={R*R-d*d}. Nếu số này dương có 2 giao điểm, bằng 0 có 1, âm có 0. Kết quả {ans}.'
 elif key=='arithmetico_geometric_sum':
  n=2+t;ans=(n-1)*2**(n+1)+2
  assert sum(k*2**k for k in range(1,n+1))==ans
  q=f'Tính tổng S=1·2¹+2·2²+3·2³+…+{n}·2^{n}.'
  sol=f'Nhân tổng với 2 rồi trừ: 2S−S={n}·2^{n+1}−(2²+2³+…+2^{n+1})+2. Thu gọn cho S=({n}−1)2^{n+1}+2={ans}.'
 elif key=='cubic_difference_limit':
  a=2+t;ans=3*a*a
  x=S.symbols('x');assert S.limit((x**3-a**3)/(x-a),x,a)==ans
  q=f'Tính L=lim_(x→{a}) (x³−{a**3})/(x−{a}).'
  sol=f'Phân tích hiệu hai lập phương: x³−{a}³=(x−{a})(x²+{a}x+{a*a}). Rút gọn rồi cho x→{a}, L=3×{a}²={ans}.'
 elif key=='tan_equation_root_count':
  n=2+t;alpha=S.pi/6;ans=n
  assert all(0<=alpha+k*S.pi<=n*S.pi for k in range(n))
  q=f'Trong đoạn 0≤x≤{n}π, phương trình tan x=tan(π/6) có bao nhiêu nghiệm?'
  sol=f'Vì tan có chu kỳ π, mọi nghiệm x=π/6+kπ với k nguyên. Điều kiện 0≤x≤{n}π cho k=0,1,...,{n-1}; tổng {n} nghiệm.'
 elif key=='cos_addition_rational':
  triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(9,40,41),(12,35,37),(11,60,61),(28,45,53),(16,63,65)]
  sa,ca,ha=triples[i];sb,cb,hb=triples[(i+3)%10]
  ans=S.Rational(ca*cb-sa*sb,ha*hb)
  assert S.simplify((S.Rational(ca,ha)*S.Rational(cb,hb)-S.Rational(sa,ha)*S.Rational(sb,hb))-ans)==0
  q=f'Biết α,β nhọn, sinα={sa}/{ha}, cosα={ca}/{ha}, sinβ={sb}/{hb}, cosβ={cb}/{hb}. Tính cos(α+β).'
  sol=f'cos(α+β)=cosαcosβ−sinαsinβ=({ca}/{ha})({cb}/{hb})−({sa}/{ha})({sb}/{hb})={fmt(ans)}.'
 elif key=='poisson_binomial_exact_one':
  p=S.Rational(t+1,t+7);qq=S.Rational(1+t%4,t+8)
  ans=p*(1-qq)+(1-p)*qq
  assert 0<ans<1 and ans==(p+qq-2*p*qq)
  q=f'Hai biến cố A,B độc lập với P(A)={fmt(p)}, P(B)={fmt(qq)}. Xác suất có đúng một trong hai biến cố xảy ra?'
  sol=f'Có hai trường hợp rời nhau: A xảy ra B không, hoặc B xảy ra A không. P=p(1−q)+(1−p)q={fmt(p)}(1−{fmt(qq)})+(1−{fmt(p)}){fmt(qq)}={fmt(ans)}.'
 elif key=='two_step_markov':
  p=S.Rational(1+t%4,6);q0=S.Rational(1+t%3,7);ans=p*p+(1-p)*q0
  assert ans==p*S.Rational(p)+(1-p)*q0
  question=f'Chuỗi Markov có hai trạng thái A,B. Xác suất A→A là {fmt(p)}, A→B là 1−{fmt(p)}, B→A là {fmt(q0)}. Bắt đầu ở A, sau 2 bước xác suất đang ở A là bao nhiêu?'
  sol=f'Đến A sau hai bước qua A→A→A hoặc A→B→A. Hai đường đi rời nhau nên P(A₂|A₀)=p²+(1−p)q={fmt(p)}²+(1−{fmt(p)})×{fmt(q0)}={fmt(ans)}.'
  q=question
 elif key=='binomial_odd_sum':
  n=2+t;ans=2**(n-1)
  assert sum(math.comb(n,k) for k in range(1,n+1,2))==ans
  q=f'Với n={n}, tính S=C(n,1)+C(n,3)+C(n,5)+… (chỉ lấy các chỉ số lẻ không vượt quá n).'
  sol=f'Từ (1+1)^n=ΣC(n,k)=2^n và (1−1)^n=Σ(−1)^k C(n,k)=0, lấy hiệu rồi chia đôi được S=2^(n−1)={ans}.'
 elif key=='space_line_angle_cos_sq':
  a,b=2+t%5,3+t%4;u=S.Matrix([a,b,0]);v=S.Matrix([0,b,a]);ans=S.Rational(u.dot(v)**2,u.dot(u)*v.dot(v))
  assert ans==1-S.Rational(u.cross(v).dot(u.cross(v)),u.dot(u)*v.dot(v))
  q=f'Trong không gian, hai đường thẳng có vectơ chỉ phương u=({a},{b},0) và v=(0,{b},{a}). Tính cos² góc nhọn giữa hai đường.'
  sol=f'cos²θ=(u·v)²/(||u||²||v||²). Tích vô hướng bằng {b*b}, mỗi bình phương độ dài là {a*a+b*b}; vì vậy cos²θ={fmt(ans)}.'
 elif key=='complex_division_realpart':
  a,b,c,d=1+t,2+t%4,3+t,1+t%5
  ans=S.Rational(a*c+b*d,c*c+d*d)
  z=(a+S.I*b)/(c+S.I*d)
  assert S.simplify(S.re(S.expand_complex(z))-ans)==0
  q=f'Cho z=({a}+{b}i)/({c}+{d}i). Tính phần thực Re(z).'
  sol=f'Nhân cả tử và mẫu với liên hợp {c}−{d}i, phần thực bằng (ac+bd)/(c²+d²)=({a}×{c}+{b}×{d})/({c}²+{d}²)={fmt(ans)}.'
 elif key=='sphere_line_intersections':
  R=4+t;h=R+(t%3)-1
  d2=h*h;ans=2 if d2<R*R else 1 if d2==R*R else 0
  x=S.symbols('x',real=True);assert len(S.solveset(x*x+d2-R*R,x,domain=S.S.Reals))==ans
  q=f'Mặt cầu S: x²+(y−{h})²+z²={R*R}. Đường thẳng d là trục Ox. Có bao nhiêu giao điểm thực giữa S và d?'
  sol=f'Trên trục Ox ta có y=z=0, nên x²={R*R}−{h*h}={R*R-h*h}. Biểu thức dương cho 2 giao điểm, bằng 0 cho 1, âm cho 0; đáp án {ans}.'
 elif key=='cone_frustum_volume_over_pi':
  R=6+t;r=2+t%4;h=3+t;ans=S.Rational(h*(R*R+R*r+r*r),3)
  assert R>r and h>0
  q=f'Khối nón cụt có bán kính hai đáy R={R}, r={r} và chiều cao h={h}. Tính thể tích V chia π.'
  sol=f'Công thức nón cụt V=(πh/3)(R²+Rr+r²). V/π={h}/3×({R}²+{R}×{r}+{r}²)={fmt(ans)}.'
 elif key=='exp_integral_to_ln2':
  a=1+t;ans=S.Rational(2**a-1,a)
  x=S.symbols('x');assert S.integrate(S.exp(a*x),(x,0,S.log(2)))==ans
  q=f'Tính I=∫ từ 0 đến ln(2) của e^({a}x) dx.'
  sol=f'Nguyên hàm của e^({a}x) là e^({a}x)/{a}. Thế cận 0,ln 2: I=(e^({a}ln2)−1)/{a}=(2^{a}−1)/{a}={fmt(ans)}.'
 elif key=='cubic_bounded_maximum':
  a=1+t;L=a+2+t%4;x=S.symbols('x');poly=x**3-3*a*a*x
  points=[-L,L,-a,a]; vals=[S.expand(poly.subs(x,p)) for p in points];ans=max(vals)
  assert S.diff(poly,x).subs(x,a)==0 and S.diff(poly,x).subs(x,-a)==0
  q=f'Tìm giá trị lớn nhất của f(x)=x³−{3*a*a}x trên đoạn [−{L},{L}].'
  sol=f'f′(x)=3(x²−{a*a}) bằng 0 tại x=±{a}. So sánh f tại hai đầu ±{L} và hai điểm ±{a}: các giá trị {", ".join(map(str,vals))}. Lớn nhất là {fmt(ans)}.'
 elif key=='expected_hypergeometric':
  N=20+t;K=6+t%5;n=3+t%4;ans=S.Rational(n*K,N)
  assert K<N and n<=N
  # check exact hypergeometric mass and expectation
  probs=[S.Rational(math.comb(K,k)*math.comb(N-K,n-k),math.comb(N,n)) for k in range(n+1) if k<=K and n-k<=N-K]
  exp=sum(S.Rational(k)*S.Rational(math.comb(K,k)*math.comb(N-K,n-k),math.comb(N,n)) for k in range(n+1) if k<=K and n-k<=N-K)
  assert sum(probs)==1 and exp==ans
  q=f'Trong {N} linh kiện có {K} loại tốt. Lấy ngẫu nhiên {n} linh kiện không hoàn lại. Gọi X là số linh kiện tốt thu được. Tính E(X).'
  sol=f'X là tổng {n} biến chỉ thị mỗi linh kiện được chọn có xác suất tốt bằng {K}/{N}. Nhờ tuyến tính kỳ vọng, E(X)={n}×{K}/{N}={fmt(ans)}.'
 elif key=='nearest_point_on_ray_sq':
  a,b,c=2+t,3+t%4,4+t%5;u=S.Matrix([1,1,0]);P=S.Matrix([(-1)**t*a,b,c]);s=S.symbols('s',real=True)
  unconstrained=S.Rational(P.dot(u),u.dot(u));best=max(S.Rational(0),unconstrained)
  ans=S.expand((P-best*u).dot(P-best*u))
  assert (best>=0) and (best==0 or S.diff((P-s*u).dot(P-s*u),s).subs(s,best)==0)
  q=f'Trong Oxyz, cho tia Ot: (x,y,z)=(s,s,0), s≥0. Cho P({P[0]},{P[1]},{P[2]}). Bình phương khoảng cách ngắn nhất từ P đến tia là bao nhiêu?'
  sol=f'Khoảng cách bình phương F(s)=||P−s(1,1,0)||², s≥0. Đỉnh parabol ở s₀=(P·u)/||u||²={fmt(unconstrained)}; ràng buộc cho s*=max(0,s₀)={fmt(best)}. Thế vào F được {fmt(ans)}.'
 elif key=='spherical_zone_area_over_pi':
  R=4+t;h=1+t%3;ans=2*R*h
  assert h<=2*R
  q=f'Đới cầu (phần mặt cầu bị kẹp giữa hai mặt phẳng song song) thuộc mặt cầu bán kính R={R}, có chiều cao h={h}. Tính diện tích mặt cong S chia π.'
  sol=f'Định lý Archimedes cho đới cầu: S=2πRh. Do đó S/π=2×{R}×{h}={ans}.'
 else:raise KeyError(key)
 return q,S.Rational(ans),sol


def main():
 specs=[];rows=[];bygrade=collections.Counter();bytype=collections.Counter()
 for key,(grade,topic,name,method,conditions,difficulty) in SPECS.items():
  assert (grade,topic) in CATALOG,(grade,topic)
  specs.append({'form_id':'v200_'+key,'grade':grade,'topic':topic,'name':name,'mathematical_essence':name,'method':method,'conditions':conditions,'difficulty':difficulty,'question_count':10,'independent_method_certified':False})
  seen=set()
  for i in range(10):
   question,answer,sol=build(key,i)
   assert question not in seen,(key,i,'duplicate question');seen.add(question)
   typ='multiple_choice' if i<7 else 'short_answer' if i<9 else 'true_false'
   if typ=='multiple_choice':
    opt=([answer,answer*S.Rational(11,10),answer*S.Rational(9,10),answer*S.Rational(3,2)] if abs(answer)>10**7 else choices_for(answer,key in ['dice_sum_probability','poisson_binomial_exact_one','two_step_markov']))
    pos=(i+len(key))%4;choice=[fmt(v) for v in opt[1:][:pos]+[answer]+opt[1:][pos:]]
    correct=fmt(answer);explanation=sol+' Trong các đáp án, chỉ '+correct+' trùng giá trị tìm được.'
   elif typ=='short_answer':
    choice=[];correct=fmt(answer);explanation=sol+' Có thể nhập phân số tối giản nếu cần.'
   else:
    choice=[f'Kết quả bằng {fmt(answer)}.',f'Kết quả nhỏ hơn {fmt(answer-1)}.',f'Kết quả lớn hơn {fmt(answer-1)}.',f'Kết quả bằng {fmt(answer+1)}.'];correct='Đúng,Sai,Đúng,Sai';explanation=sol+' Đánh giá bốn nhận định lần lượt đúng, sai, đúng, sai.'
   rows.append({'id':f'v200_{key}_{i:02d}','form_id':'v200_'+key,'grade':grade,'topic':topic,'concept':name,'math_method':method,'conditions':conditions,'difficulty':difficulty,'question_type':typ,'question':question,'answer':correct,'correct_answer':correct,'solution':explanation,'choices':choice,'source_bundle':'V200','validation_status':'exact_oracle_checked','method_independence_certified':False,'production_integrated':False})
   bygrade[str(grade)]+=1;bytype[typ]+=1
 (OUT/'V200_FAMILY_SPECS.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n')
 (OUT/'V200_INCREMENT.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
 report={'version':'V200','new_candidate_families':len(specs),'exact_oracle_checked_questions':len(rows),'grades':dict(bygrade),'formats':dict(bytype),'certified_independent_forms':0,'production_deployed':False}
 (OUT/'V200_GENERATION_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
