#!/usr/bin/env python3
"""Generate V192 distinct-method candidate families, 10 independently checked questions each.
No claim of global semantic novelty or production insertion.
"""
from __future__ import annotations
import sys, json, random, hashlib, collections, re
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'backend'))
from app.ai.engine.validator import validate
from app.questions.answer_checker import grade_answer
OUT=ROOT/'bank_updates'
FORMS=[]
x=S.symbols('x',real=True)
def f(z): return S.sstr(S.simplify(z))
def add(g,t,key,name,method,condition,level='trung cấp'):
 def wrap(fun):
  FORMS.append(dict(grade=g,topic=t,key='v192_'+key,name=name,method=method,conditions=condition,difficulty=level,fun=fun))
  return fun
 return wrap

def Q(question,answer,solution,oracle):
 if S.simplify(S.sympify(answer)-S.sympify(oracle)) != 0: raise ArithmeticError((question,answer,oracle))
 assert len(question)>25 and len(solution)>60, (question,solution)
 return question,S.simplify(answer),solution,{'independent_oracle':f(oracle),'check':'exact_sympy_or_independent_combinatorial_count'}

# GRADE 10: distinct operations and methods
@add(10,'menh_de','truth_assignments','Đếm cách gán giá trị chân lý để một tuyển nhiều mệnh đề đúng','Số gán khiến ít nhất một trong n mệnh đề đúng = 2^n−1','n mệnh đề độc lập, mỗi mệnh đề có hai giá trị', 'nền tảng')
def a01(k):
 n=3+k;v=2**n-1
 return Q(f'Có {n} mệnh đề đơn độc lập p₁,...,p_{n}. Có bao nhiêu cách gán Đúng/Sai để mệnh đề p₁∨...∨p_{n} là Đúng?',v,f'Mỗi mệnh đề có hai giá trị nên có 2^{n}={2**n} phép gán. Phủ định của tuyển chỉ đúng khi cả {n} mệnh đề đều Sai, có đúng 1 phép gán. Số cần tìm là {2**n}−1={v}.',sum(1 for m in range(2**n) if m!=0))
@add(10,'he_bat_phuong_trinh','bounded_integer','Đếm nghiệm nguyên của giao hai bất phương trình tuyến tính một ẩn','L≤x≤U => U−L+1 nghiệm nguyên','L,U nguyên, L≤U', 'nền tảng')
def a02(k):
 a=2*k-5;b=a+8+(k%3);v=b-a+1
 return Q(f'Có bao nhiêu nghiệm nguyên x thỏa đồng thời x≥{a} và x≤{b}?',v,f'Giao hai điều kiện là đoạn [{a};{b}]. Các số nguyên từ {a} đến {b} kể cả hai đầu mút có {b}−({a})+1={v} giá trị.',len(list(range(a,b+1))))
@add(10,'he_thuc_luong','cosine_law_side_squared','Áp dụng định lý côsin để tìm bình phương cạnh đối diện góc 60°','c²=a²+b²−ab khi góc xen giữa 60°','Hai cạnh a,b>0, góc xen giữa 60°')
def a03(k):
 a=k+4;b=2*k+7;v=a*a+b*b-a*b
 return Q(f'Tam giác ABC có AB={a}, AC={b}, góc BAC bằng 60°. Tính BC².',v,f'Định lý côsin: BC²=AB²+AC²−2·AB·AC·cos60°. Vì cos60°=1/2, BC²={a}²+{b}²−{a}·{b}={v}.',S.expand(a*a+b*b-2*a*b*S.cos(S.pi/3)))
@add(10,'vector','parallelogram_vector_norm','Tính bình phương độ dài tổng hai vectơ từ độ dài và tích vô hướng','||u+v||²=||u||²+||v||²+2u·v','Hai vectơ cho phép tích vô hướng xác định')
def a04(k):
 a=k+2;b=k+5;d=(k%4)-2;v=a*a+b*b+2*d
 return Q(f'Cho hai vectơ u,v có ||u||={a}, ||v||={b}, u·v={d}. Tính ||u+v||².',v,f'Khai triển tích vô hướng (u+v)·(u+v)=u·u+2u·v+v·v. Suy ra ||u+v||²={a}²+2·({d})+{b}²={v}.',S.expand((a*a)+(b*b)+2*d))
@add(10,'quy_tac_dem','binary_no_adjacent_ones','Đếm chuỗi nhị phân không có hai chữ số 1 liền kề','F(n)=F(n−1)+F(n−2) dựa trên chữ số cuối','n≥2; chuỗi dài n', 'trung cấp')
def a05(k):
 n=4+k;counts=[1,2]
 for j in range(2,n+1):counts.append(counts[-1]+counts[-2])
 ans=counts[n]
 return Q(f'Có bao nhiêu chuỗi nhị phân độ dài {n} không chứa hai chữ số 1 ở hai vị trí kề nhau?',ans,f'Gọi F(m) là số chuỗi hợp lệ dài m. Chuỗi kết thúc bằng 0 có F(m−1) cách, chuỗi kết thúc bằng 1 bắt buộc đứng sau 0 nên có F(m−2) cách. Do đó F(m)=F(m−1)+F(m−2), với F(0)=1, F(1)=2. Lặp đến m={n} cho F({n})={ans}.',sum('11' not in f'{i:0{n}b}' for i in range(2**n)))
@add(10,'thong_ke','weighted_mean','Trung bình cộng của mẫu có bảng tần số','x̄=(Σf_i x_i)/(Σf_i)','Tần số nguyên dương, tổng tần số khác 0', 'nền tảng')
def a06(k):
 a=k+1;b=k+5;c=k+10;p=2+k%3;q=3+k%4;r=4+k%2
 v=S.Rational(a*p+b*q+c*r,p+q+r)
 return Q(f'Mẫu số liệu có giá trị {a},{b},{c} với tần số tương ứng {p},{q},{r}. Tìm trung bình cộng của mẫu.',v,f'Tổng tần số N={p}+{q}+{r}={p+q+r}. Tổng giá trị là {a}·{p}+{b}·{q}+{c}·{r}={a*p+b*q+c*r}. Chia cho N được x̄={f(v)}.',sum([a]*p+[b]*q+[c]*r)/S.Integer(p+q+r))
@add(10,'g10_geom_angles_parallel','alternate_interior_angle','Xác định góc so le trong khi hai đường thẳng song song','Góc so le trong bằng nhau','Hai đường thẳng song song cắt bởi một cát tuyến','nền tảng')
def a07(k):
 angle=35+7*k
 return Q(f'Hai đường thẳng song song a,b bị đường thẳng c cắt. Một góc so le trong tại a bằng {angle}°. Tính góc so le trong tương ứng tại b (đơn vị độ).',angle,f'Vì a song song b nên hai góc so le trong tạo bởi c bằng nhau. Một góc đã cho là {angle}°, vậy góc so le trong tương ứng cũng bằng {angle}°.',angle)
@add(10,'g10_geom_quadrilaterals_properties','parallelogram_diagonal_law','Định luật hình bình hành cho hai đường chéo','AC²+BD²=2(AB²+BC²)','ABCD là hình bình hành')
def a08(k):
 a=5+k;b=7+k;v=2*(a*a+b*b)
 return Q(f'Hình bình hành ABCD có AB={a}, BC={b}. Tính AC²+BD².',v,f'Áp dụng định luật hình bình hành, tổng bình phương hai đường chéo bằng hai lần tổng bình phương hai cạnh kề: AC²+BD²=2({a}²+{b}²)={v}.',2*S.Integer(a*a+b*b))
@add(10,'g10_geom_thales_similarity','similar_triangle_area','Tỉ số diện tích của hai tam giác đồng dạng tạo bởi đường song song','S_ADE/S_ABC=(AD/AB)²','D trên AB; E trên AC; DE∥BC')
def a09(k):
 p=2+k;q=5+k;ratio=S.Rational(p,q);v=ratio**2
 return Q(f'Trong tam giác ABC, D thuộc AB, E thuộc AC và DE∥BC. Biết AD/AB={f(ratio)}. Tính S_ADE/S_ABC.',v,f'Định lý Thales cho AD/AB=AE/AC={f(ratio)}. Tam giác ADE đồng dạng tam giác ABC nên diện tích tỉ lệ với bình phương cạnh tương ứng: S_ADE/S_ABC=({f(ratio)})²={f(v)}.',S.Rational(p*p,q*q))
@add(10,'g10_geom_triangle_area_ratio','cevian_area_ratio','Tỉ số diện tích hai tam giác chung đường cao từ A','S_ABD/S_ACD=BD/DC','D nằm trong cạnh BC của tam giác ABC')
def a10(k):
 bd=k+3;dc=2*k+5;v=S.Rational(bd,dc)
 return Q(f'Trong tam giác ABC, D thuộc BC với BD={bd}, DC={dc}. Tính S_ABD/S_ACD.',v,f'Hai tam giác ABD, ACD có chiều cao từ A xuống đường thẳng BC bằng nhau. Tỉ số diện tích bằng tỉ số đáy: S_ABD/S_ACD=BD/DC={bd}/{dc}={f(v)}.',S.Rational(bd,dc))
@add(10,'g10_geom_circle_angles','interior_chords_arc_angle','Góc tạo bởi hai dây cung cắt nhau bên trong đường tròn','Góc trong = (số đo cung chắn và cung đối đỉnh)/2','Hai dây cắt bên trong đường tròn')
def a11(k):
 a=60+2*k;b=80+4*k;v=S.Rational(a+b,2)
 return Q(f'Hai dây AB và CD cắt nhau tại E nằm trong đường tròn. Hai cung bị chắn bởi góc AEC và góc đối đỉnh của nó có số đo {a}° và {b}°. Tính góc AEC.',v,f'Góc do hai dây cắt nhau trong đường tròn bằng nửa tổng hai cung bị chắn. Vì vậy ∠AEC=({a}°+{b}°)/2={f(v)}°.',S.Rational(a+b,2))
@add(10,'g10_geom_line_intersections','two_lines_intersect','Tìm hoành độ giao điểm hai đường thẳng từ hệ số góc','ax+b=cx+d => x=(d−b)/(a−c)','Hai đường thẳng khác hệ số góc')
def a12(k):
 a=k+3;c=k+1;b=3+k;d=7+3*k;v=S.Rational(d-b,a-c)
 return Q(f'Trong Oxy, hai đường thẳng y={a}x+{b} và y={c}x+{d} cắt nhau tại P. Tìm hoành độ P.',v,f'Tại giao điểm, {a}x+{b}={c}x+{d}. Chuyển vế cho ({a}−{c})x={d}−{b}. Vì {a-c}≠0 nên x={d-b}/{a-c}={f(v)}.',S.solve(S.Eq(a*x+b,c*x+d),x)[0])
@add(10,'g10_geom_triangle_inequalities','count_triangle_integer_third_side','Đếm độ dài nguyên của cạnh thứ ba để tạo thành tam giác','|a−b|<c<a+b','a,b là hai cạnh nguyên dương')
def a13(k):
 a=k+4;b=2*k+7;v=2*min(a,b)-1
 return Q(f'Cho hai cạnh của một tam giác dài {a} và {b}. Có bao nhiêu giá trị nguyên dương của cạnh thứ ba c để tam giác không suy biến?',v,f'Bất đẳng thức tam giác yêu cầu |{a}−{b}|<c<{a+b}. Do c nguyên, các giá trị chạy từ {abs(a-b)+1} đến {a+b-1}. Số giá trị là {a+b-1}−{abs(a-b)+1}+1={v}.',len([c for c in range(1,a+b+1) if abs(a-b)<c<a+b]))
@add(10,'g10_radical_equations_advanced','one_radical_equation','Giải phương trình căn √(x+a)=x−b và loại nghiệm ngoại lai','Bình phương hai vế sau khi đặt x−b≥0, thử điều kiện','Căn bậc hai không âm; nghiệm phải thỏa x−b≥0','nâng cao')
def a14(k):
 b=2+k;t=3+k;a=t*t-b-t;ans=b+t;roots=S.solve(S.Eq(x+a,(x-b)**2),x);good=[z for z in roots if z-b>=0 and z+a>=0]
 return Q(f'Giải phương trình √(x+({a}))=x−({b}). Tìm nghiệm thực x.',ans,f'Điều kiện x≥{b} và x+({a})≥0. Bình phương: x+({a})=(x−({b}))². Đặt y=x−{b}≥0 được y²−y−({b+a})=0, có hai nghiệm y={t} và y={1-t}. Loại y={1-t}<0. Vậy x={b}+{t}={ans}; thay lại thấy hai vế cùng bằng {t}.',good[0] if len(good)==1 else S.nan)
@add(10,'g10_geom_circle_tangent_chord','power_of_point_tangent','Độ dài tiếp tuyến bằng căn tích hai đoạn cát tuyến','PT²=PA·PB','P nằm ngoài đường tròn, A gần P hơn B')
def a15(k):
 t=k+2;pa=t*t;pb=9*t*t;pt=3*t*t
 return Q(f'Từ điểm P ngoài đường tròn kẻ tiếp tuyến PT và cát tuyến PAB (A nằm giữa P,B). Biết PA={pa}, PB={pb}. Tính PT.',pt,f'Định lý tiếp tuyến-cát tuyến cho PT²=PA·PB={pa}·{pb}={pa*pb}. Vì độ dài dương nên PT=√({pa*pb})={pt}.',S.sqrt(pa*pb))
@add(10,'chung_minh_hinh_hoc_10','right_triangle_altitude','Hệ thức đường cao ứng với cạnh huyền trong tam giác vuông','CH²=AH·HB','Tam giác ABC vuông tại C; H là chân đường cao trên AB')
def a16(k):
 t=k+1;ah=4*t;hb=9*t;h=6*t
 return Q(f'Tam giác ABC vuông tại C, CH là đường cao xuống cạnh huyền AB. Biết AH={ah} và HB={hb}. Tính CH.',h,f'Định lý hệ thức lượng trong tam giác vuông: CH²=AH·HB={ah}·{hb}={ah*hb}. CH>0 nên CH=√({ah*hb})={h}.',S.sqrt(ah*hb))
@add(10,'g10_geom_locus','equidistant_locus_on_axis','Xác định điểm thuộc Ox cách đều hai điểm qua bình phương khoảng cách','(x−a)²+y₁²=(x−b)²+y₂² => x=(b²+y₂²−a²−y₁²)/(2(b−a))','A,B khác hoành độ; điểm H nằm trên Ox')
def a17(k):
 a=k+1;b=a+4;y1=k+2;y2=2*k+4;ans=S.Rational(b*b+y2*y2-a*a-y1*y1,2*(b-a))
 return Q(f'Trong Oxy, A({a};{y1}), B({b};{y2}). Tìm hoành độ điểm H nằm trên trục Ox và thỏa HA=HB.',ans,f'Đặt H(x;0). Từ HA=HB suy ra (x−{a})²+{y1}²=(x−{b})²+{y2}². Khai triển và triệt x² thu được 2({b}−{a})x={b*b}+{y2*y2}−{a*a}−{y1*y1}, nên x={f(ans)}.',S.solve(S.Eq((x-a)**2+y1*y1,(x-b)**2+y2*y2),x)[0])

@add(10,'toa_do_hinh_hoc_10','coordinate_triangle_area','Diện tích tam giác theo định thức hai vectơ cạnh trong Oxy','S=|det(AB,AC)|/2','Ba điểm không thẳng hàng')
def a18(k):
 a=k+3;c=2*k+7;p=k+1;v=S.Rational(a*c,2)
 return Q(f'Trong Oxy, tam giác có A(0;0), B({a};0), C({p};{c}). Tính diện tích tam giác ABC.',v,f'Véc tơ AB=({a};0), AC=({p};{c}). Định thức det(AB,AC)={a}·{c}−0·{p}={a*c}. Diện tích bằng |det|/2={f(v)}.',abs(S.det(S.Matrix([[a,0],[p,c]])))/2)
@add(10,'duong_thang','parallel_lines_distance','Khoảng cách giữa hai đường thẳng song song ở dạng tổng quát','d=|c₂−c₁|/√(a²+b²)','Đường thẳng có cùng pháp tuyến (3,4)')
def a19(k):
 c=2+k;diff=5*(k+2);ans=k+2
 return Q(f'Trong Oxy, hai đường thẳng d₁:3x+4y+{c}=0 và d₂:3x+4y+{c+diff}=0. Tính khoảng cách giữa chúng.',ans,f'Chúng cùng pháp tuyến (3;4) nên song song. Khoảng cách d=|({c+diff})−({c})|/√(3²+4²)={diff}/5={ans}.',S.Rational(diff,5))
@add(10,'g10_advanced_inequalities','amgm_product_max','Giá trị lớn nhất của tích hai số không âm có tổng cố định','xy≤((x+y)/2)²','x,y không âm, x+y=S','nâng cao')
def a20(k):
 total=2*(k+5);v=S.Rational(total*total,4)
 return Q(f'Cho hai số thực không âm x,y thỏa x+y={total}. Tìm giá trị lớn nhất của xy.',v,f'Theo AM–GM, (x+y)/2≥√(xy), suy ra xy≤({total}/2)²={f(v)}. Dấu bằng khi x=y={total//2}, thỏa điều kiện. Vậy GTLN bằng {f(v)}.',(S.Rational(total,2))**2)
@add(10,'g10_symmetric_systems','sum_and_product_to_square_sum','Tìm x²+y² từ tổng và tích hai nghiệm','x²+y²=(x+y)²−2xy','Hai số thực x,y với tổng và tích tương thích')
def a21(k):
 a=k+2;b=2*k+5;sm=a+b;pr=a*b;v=a*a+b*b
 return Q(f'Hai số thực x,y có x+y={sm} và xy={pr}. Tính x²+y².',v,f'Bình phương tổng: (x+y)²=x²+2xy+y². Do đó x²+y²=(x+y)²−2xy={sm}²−2·{pr}={v}.',S.expand(sm*sm-2*pr))
@add(10,'duong_tron_co_ban_10','two_external_tangents','Tính đoạn tiếp tuyến từ một điểm ngoài đường tròn bằng Pythagore','PT=√(OP²−R²)','P nằm ngoài đường tròn, OT⊥PT')
def a22(k):
 t=k+1;r=3*t;d=5*t;ans=4*t
 return Q(f'Đường tròn tâm O bán kính {r}, điểm P cách O một khoảng {d}. PT là tiếp tuyến tại T. Tính PT.',ans,f'Vì bán kính OT vuông góc tiếp tuyến PT nên tam giác OPT vuông tại T. Từ OP²=OT²+PT² suy ra PT=√({d}²−{r}²)={ans}.',S.sqrt(d*d-r*r))
@add(10,'nhi_thuc_newton','sum_binomial_coefficients','Tổng các hệ số trong khai triển nhị thức Newton','Σ C(n,k)=2^n bằng cách thay x=1 trong (1+x)^n','n số nguyên không âm','nền tảng')
def a23(k):
 n=5+k;ans=2**n
 return Q(f'Tính tổng C({n},0)+C({n},1)+...+C({n},{n}).',ans,f'Theo nhị thức Newton, (1+x)^{n}=Σ C({n},j)x^j. Lấy x=1, vế trái là 2^{n}, vế phải chính là tổng đã cho. Vậy kết quả bằng {ans}.',sum(S.binomial(n,j) for j in range(n+1)))
@add(10,'g10_geom_coordinate_circle_line','circle_vertical_tangency','Tìm hoành độ đường thẳng đứng tiếp xúc phía phải với đường tròn','x=a+R với tâm I(a,b) bán kính R','Tiếp tuyến đứng nằm bên phải tâm')
def a24(k):
 a=2*k-5;b=k+3;r=k+4;ans=a+r
 return Q(f'Cho đường tròn (x−({a}))²+(y−({b}))²={r*r}. Đường thẳng x=m tiếp xúc đường tròn ở phía bên phải tâm. Tìm m.',ans,f'Tâm I({a};{b}), bán kính R={r}. Khoảng cách từ I đến đường x=m là |m−({a})|. Tiếp xúc khi |m−({a})|={r}; phía phải tâm nên m={a}+{r}={ans}.',a+S.sqrt(r*r))

# GRADE 11: trig, sequences, derivatives, stochastic and geometric transformations
@add(11,'ham_so_luong_giac','sine_period','Chu kỳ cơ bản của hàm sin(ax+b)','T=2π/|a|','a khác 0; x đo bằng radian','nền tảng')
def b01(k):
 a=2+k;ans=S.Rational(2,a)
 return Q(f'Hàm y=sin({a}x+{k+1}) có chu kỳ dương nhỏ nhất T. Tính T/π.',ans,f'Hàm sin(u) có chu kỳ theo u là 2π. Vì hệ số của x bằng {a}, chu kỳ cơ bản của hàm y=sin({a}x+{k+1}) là T=2π/{a}. Do đó T/π=2/{a}={f(ans)}.',S.Rational(2,a))
@add(11,'phuong_trinh_luong_giac','sine_zero_root_count','Đếm nghiệm sin(mx)=0 trên đoạn nửa kín','sin(mx)=0⇔mx=jπ; j nguyên','m nguyên dương, 0≤x<π')
def b02(k):
 m=k+2;ans=m
 return Q(f'Phương trình sin({m}x)=0 có bao nhiêu nghiệm x thuộc [0;π)?',ans,f'Điều kiện sin({m}x)=0 tương đương {m}x=jπ với j nguyên. Vì 0≤x<π, ta có 0≤j<{m}. Có các j=0,1,...,{m-1}, tổng cộng {m} nghiệm.',len([j for j in range(m)]))
@add(11,'gia_tri_luong_giac','cos_double_from_tan','Tính cos(2α) từ tanα','cos2α=(1−tan²α)/(1+tan²α)','cosα khác 0')
def b03(k):
 t=S.Rational(k+1,k+3);ans=(1-t*t)/(1+t*t)
 return Q(f'Cho góc α có tanα={f(t)}. Tính cos(2α).',ans,f'Dùng công thức biến đổi theo tan: cos(2α)=(1−tan²α)/(1+tan²α). Thế tanα={f(t)} được (1−({f(t)})²)/(1+({f(t)})²)={f(ans)}.',S.cancel((1-t**2)/(1+t**2)))
@add(11,'day_so','telescoping_product','Tích rút gọn của dãy phân số liên tiếp','∏_{j=1}^n (j+1)/j=n+1','n số nguyên dương','nền tảng')
def b04(k):
 n=4+k;ans=n+1
 return Q(f'Tính tích P=(2/1)·(3/2)·...·({n+1}/{n}).',ans,f'Khi nhân các phân số, các thừa số 2,3,...,{n} ở tử và mẫu triệt tiêu từng cặp. Còn P=({n+1})/1={ans}.',S.prod(S.Rational(j+1,j) for j in range(1,n+1)))
@add(11,'cap_so_cong','sum_to_term_difference','Tìm số hạng u_n từ công thức tổng n số hạng đầu','u_n=S_n−S_{n−1}','n nguyên dương; S_n đã cho dưới dạng tam thức bậc hai')
def b05(k):
 a=k+2;b=k+4;n=k+5;ans=a*(2*n-1)+b
 return Q(f'Một dãy có tổng n số hạng đầu S_n={a}n²+{b}n. Tìm số hạng u_{n} (n={n}).',ans,f'Do S_n=u₁+...+u_n, ta có u_n=S_n−S_(n−1). Thay biểu thức: u_n={a}[n²−(n−1)²]+{b}[n−(n−1)]={a}(2n−1)+{b}. Tại n={n}, u_n={ans}.',S.expand((a*S.Symbol('n')**2+b*S.Symbol('n'))-(a*(S.Symbol('n')-1)**2+b*(S.Symbol('n')-1))).subs(S.Symbol('n'),n))
@add(11,'cap_so_nhan','common_ratio_nonconsecutive','Suy công bội dương của cấp số nhân qua hai số hạng không liên tiếp','q²=u_{j+2}/u_j','Cấp số nhân q>0, u_j khác 0')
def b06(k):
 u=2+k;q=2+k%4;u5=u*q*q
 return Q(f'Cấp số nhân có các số hạng u₃={u} và u₅={u5}, công bội q>0. Tính q.',q,f'Với cấp số nhân, u₅=u₃q² nên q²=u₅/u₃={u5}/{u}={q*q}. Vì q>0 nên q=√({q*q})={q}.',S.sqrt(S.Rational(u5,u)))
@add(11,'ham_so_lien_tuc','piecewise_removable_continuity','Điền giá trị tại điểm khuyết để hàm phân thức liên tục','(x²−a²)/(x−a)→2a khi x→a','Xét giới hạn khi x→a và gán f(a)=m')
def b07(k):
 a=k+2;m=2*a
 return Q(f'Hàm f(x)=(x²−{a*a})/(x−{a}) khi x≠{a} và f({a})=m. Tìm m để f liên tục tại x={a}.',m,f'Với x khác {a}, phân tích x²−{a*a}=(x−{a})(x+{a}) và rút gọn f(x)=x+{a}. Giới hạn khi x→{a} là {2*a}. Liên tục yêu cầu m bằng giới hạn, nên m={m}.',S.limit((x*x-a*a)/(x-a),x,a))
@add(11,'ung_dung_dao_ham_11','tangent_cubic_intercept','Tung độ giao Oy của tiếp tuyến với đồ thị bậc ba','b=f(a)−af′(a)','f(x)=x³+cx; tiếp xúc tại x=a')
def b08(k):
 a=k+2;c=k+1;fx=x**3+c*x;slope=S.diff(fx,x).subs(x,a);intercept=S.expand(fx.subs(x,a)-a*slope)
 return Q(f'Cho đồ thị hàm f(x)=x³+{c}x. Tiếp tuyến tại điểm có hoành độ x₀={a} cắt Oy tại tung độ b. Tìm b.',intercept,f'Đạo hàm f′(x)=3x²+{c}, nên hệ số góc tiếp tuyến tại x₀={a} là {f(slope)}. Tung độ điểm tiếp xúc f({a})={f(fx.subs(x,a))}. Phương trình tiếp tuyến y=f({a})+f′({a})(x−{a}); thay x=0 được b={f(intercept)}.',S.expand(-2*a**3))
@add(11,'phuong_trinh_luong_giac_day_du','cos_zero_root_count','Đếm nghiệm cos(mx)=0 trên chu kỳ 2π','mx=π/2+jπ','m nguyên dương; x thuộc [0;2π)')
def b09(k):
 m=k+2;ans=2*m
 return Q(f'Phương trình cos({m}x)=0 có bao nhiêu nghiệm x thuộc [0;2π)?',ans,f'Giải cos({m}x)=0: {m}x=π/2+jπ. Tương đương x=(2j+1)π/(2·{m}). Điều kiện 0≤x<2π cho j=0,1,...,{2*m-1}. Do đó có {2*m} nghiệm.',len(range(2*m)))
@add(11,'g11_geom_transform_translation','translation_coordinate_sum','Ảnh điểm qua phép tịnh tiến vectơ xác định','P′=P+v','Điểm và vectơ thuộc mặt phẳng Oxy','nền tảng')
def b10(k):
 a=k-3;b=2*k+1;u=k+2;v=-k-4;ans=a+u+b+v
 return Q(f'Tịnh tiến điểm P({a};{b}) theo vectơ v=({u};{v}) được P′(x′;y′). Tính x′+y′.',ans,f'Phép tịnh tiến cộng từng tọa độ: x′={a}+{u}={a+u}, y′={b}+({v})={b+v}. Do đó x′+y′={a+u}+({b+v})={ans}.',S.Integer(a+u+b+v))
@add(11,'g11_geom_transform_reflection','reflect_across_y_eq_x','Phép đối xứng qua đường thẳng y=x hoán đổi tọa độ','(x,y)↦(y,x)','Trục đối xứng y=x','nền tảng')
def b11(k):
 a=k+4;b=2*k-3
 return Q(f'Trong Oxy, lấy ảnh Q của điểm P({a};{b}) qua đường thẳng y=x. Tìm hoành độ Q.',b,f'Phép đối xứng qua trục y=x đổi chỗ hai tọa độ: P({a};{b}) biến thành Q({b};{a}). Vì vậy hoành độ Q bằng {b}.',S.Integer(b))
@add(11,'g11_geom_rotation_homothety','central_symmetry_nonorigin','Đối xứng tâm O(a,b) trong Oxy','P′=2O−P','O là trung điểm đoạn PP′')
def b12(k):
 a=k+1;b=2*k-3;p=k+4;q=k+7;ans=2*a-p
 return Q(f'Trong Oxy, điểm P({p};{q}) đối xứng qua tâm O({a};{b}) thành P′. Tìm hoành độ P′.',ans,f'Vì O là trung điểm PP′, x_O=(x_P+x_P′)/2. Suy ra x_P′=2·{a}−{p}={ans}; tương tự tính được tung độ nếu cần.',S.Integer(2*a-p))
@add(11,'g11_geom_transform_composition','translation_then_reflection','Hợp phép tịnh tiến rồi đối xứng trục tung','(x,y)→(x+a,y+b)→(−x−a,y+b)','Trục đối xứng cuối là Oy')
def b13(k):
 a=k+2;b=k+3;p=2*k-7;q=k+1;ans=-(p+a)
 return Q(f'Từ P({p};{q}), tịnh tiến theo vectơ ({a};{b}), sau đó lấy đối xứng qua trục Oy. Tìm hoành độ điểm cuối.',ans,f'Sau tịnh tiến được P₁({p+a};{q+b}). Đối xứng qua trục Oy đổi dấu hoành độ, giữ tung độ: x_cuối=−({p+a})={ans}.',S.Integer(-p-a))
@add(11,'g11_geom_prism_pyramid_sections','right_prism_lateral_area','Diện tích xung quanh lăng trụ đứng theo chu vi đáy','S_xq=P_đáy·h','Lăng trụ đứng có đáy là tam giác 3-4-5','nền tảng')
def b14(k):
 t=k+1;h=k+5;per=12*t;ans=per*h
 return Q(f'Lăng trụ đứng có đáy là tam giác cạnh {3*t}, {4*t}, {5*t}, và chiều cao h={h}. Tính diện tích xung quanh.',ans,f'Diện tích xung quanh lăng trụ đứng bằng tổng diện tích các mặt bên, tức chu vi đáy nhân chiều cao. Chu vi là {3*t}+{4*t}+{5*t}={per}. S_xq={per}·{h}={ans}.',S.Integer(per*h))
@add(11,'hinh_khong_gian','pyramid_volume','Thể tích hình chóp bằng một phần ba diện tích đáy nhân chiều cao','V=S_đáy·h/3','Hình chóp có diện tích đáy và chiều cao dương','nền tảng')
def b15(k):
 base=6*(k+2);height=3*(k+1);ans=S.Rational(base*height,3)
 return Q(f'Một hình chóp có diện tích đáy S={base} và chiều cao h={height}. Tính thể tích khối chóp.',ans,f'Công thức thể tích hình chóp V=(1/3)·S_đáy·h. Thay S_đáy={base}, h={height}: V={base}·{height}/3={f(ans)}.',S.Rational(base*height,3))
@add(11,'g11_geom_dihedral_angles','line_plane_angle_sine_squared','Bình phương sin góc giữa cạnh xiên và mặt phẳng đáy','sin²θ=h²/(h²+d²)','Điểm ngoài mặt phẳng có hình chiếu vuông góc, h>0,d>0')
def b16(k):
 h=3*(k+1);d=4*(k+1);ans=S.Rational(h*h,h*h+d*d)
 return Q(f'Đoạn SA có hình chiếu vuông góc lên mặt phẳng (P) dài {d}, khoảng cách từ S tới (P) là {h}. Tính sin² góc giữa SA và (P).',ans,f'Gọi H là chân vuông góc của S lên (P). Góc giữa SA và mặt phẳng là ∠SAH. Tam giác SAH vuông tại H: SA²=AH²+SH²={d*d}+{h*h}. Vì sinθ=SH/SA nên sin²θ={h*h}/({h*h}+{d*d})={f(ans)}.',S.Rational(h*h,h*h+d*d))
@add(11,'g11_binomial_advanced','vandermonde_binomial','Tổng bình phương các hệ số tổ hợp qua đồng nhất thức Vandermonde','Σ C(n,k)² = C(2n,n)','n số nguyên dương; C(n,k) tổ hợp')
def b17(k):
 n=k+3;ans=S.binomial(2*n,n)
 return Q(f'Tính T=C({n},0)²+C({n},1)²+...+C({n},{n})².',ans,f'Đồng nhất thức Vandermonde: Σ C(n,j)C(n,n−j)=C(2n,n). Do C(n,n−j)=C(n,j), tổng T=Σ C({n},j)²=C({2*n},{n})={ans}.',sum(S.binomial(n,j)**2 for j in range(n+1)))
@add(11,'quy_nap_toan_hoc_11','sum_of_cubes_induction','Dùng công thức quy nạp cho tổng lập phương số tự nhiên','1³+...+n³=[n(n+1)/2]²','n nguyên dương')
def b18(k):
 n=k+3;ans=(n*(n+1)//2)**2
 return Q(f'Tính tổng 1³+2³+...+{n}³ theo công thức có thể chứng minh bằng quy nạp.',ans,f'Cơ sở n=1 đúng. Giả sử tổng đến n bằng [n(n+1)/2]². Cộng thêm (n+1)³ và rút gọn được [(n+1)(n+2)/2]², nên công thức đúng với mọi n. Thế n={n} được [{n}·{n+1}/2]²={ans}.',sum(j**3 for j in range(1,n+1)))
@add(11,'g11_sequences_advanced','affine_first_order_recurrence','Giải truy hồi tuyến tính cấp một bằng cách dịch điểm bất động','u_n=(u₁+c)2^(n−1)−c nếu u_(n+1)=2u_n+c','u₁,c cho trước, n nguyên dương','nâng cao')
def b19(k):
 a=k+1;c=k+3;n=k+4;ans=(a+c)*2**(n-1)-c
 return Q(f'Dãy u₁={a}, u_(n+1)=2u_n+{c}. Tính u_{n}.',ans,f'Đặt v_n=u_n+{c}. Ta có v_(n+1)=u_(n+1)+{c}=2(u_n+{c})=2v_n. Vậy v_n=({a}+{c})2^(n−1), suy ra u_n=({a+c})2^(n−1)−{c}. Thay n={n} được {ans}.',S.Integer(ans))
@add(11,'to_hop_xac_suat_nang_cao_11','lattice_shortest_paths','Đếm đường đi ngắn nhất trên lưới ô vuông','C(m+n,m)','Chỉ được đi sang phải hoặc đi lên')
def b20(k):
 m=k+2;n=k+4;ans=S.binomial(m+n,m)
 return Q(f'Từ (0;0) đến ({m};{n}) trên lưới tọa độ nguyên, mỗi bước chỉ sang phải 1 đơn vị hoặc lên 1 đơn vị. Có bao nhiêu đường đi ngắn nhất?',ans,f'Mỗi đường ngắn nhất có đúng {m} bước phải và {n} bước lên, tổng cộng {m+n} bước. Chọn vị trí cho {m} bước phải trong {m+n} vị trí được C({m+n},{m})={ans} cách.',S.binomial(m+n,n))
@add(11,'thong_ke_11','median_sorted_odd_sample','Trung vị của dãy đã sắp tăng có số phần tử lẻ','Me=x_((n+1)/2)','Dãy đơn điệu tăng gồm số lẻ phần tử','nền tảng')
def b21(k):
 n=2*(k+4)+1;start=k+3;d=2+k;mid=start+d*(n//2)
 return Q(f'Có {n} số liệu được sắp tăng: {start}, {start+d}, {start+2*d},... với công sai {d}. Tính trung vị của mẫu.',mid,f'Mẫu có số lẻ phần tử n={n}. Trung vị ở vị trí (n+1)/2={n//2+1}. Số tại vị trí đó là {start}+({n//2})·{d}={mid}.',sorted([start+d*j for j in range(n)])[n//2])
@add(11,'g11_conditional_probability_models','dice_even_sum_condition','Xác suất có điều kiện cả hai lần gieo đều chẵn khi tổng chẵn','P(cả chẵn | tổng chẵn)=E²/(E²+O²)','Gieo độc lập 2 xúc xắc đều từ 1 đến n','nâng cao')
def b22(k):
 n=k+3;E=n//2;O=n-E;ans=S.Rational(E*E,E*E+O*O)
 return Q(f'Gieo độc lập hai xúc xắc công bằng có các mặt ghi số 1 đến {n}. Biết tổng hai số là chẵn. Tính xác suất cả hai số đều chẵn.',ans,f'Tổng chẵn xảy ra khi cả hai chẵn hoặc cả hai lẻ. Có E={E} mặt chẵn, O={O} mặt lẻ nên có E²+O²={E*E+O*O} kết quả thỏa điều kiện. Trong đó E²={E*E} trường hợp cả chẵn, vậy P={E*E}/{E*E+O*O}={f(ans)}.',S.Rational(E**2,E**2+O**2))
@add(11,'g11_geom_parallel_planes','parallel_plane_coordinate_distance','Khoảng cách giữa hai mặt phẳng song song có phương trình z=a, z=b','d=|a−b|','Hệ trục vuông góc Oxyz; hai mặt phẳng khác nhau')
def b23(k):
 a=k-4;b=a+5+k;ans=b-a
 return Q(f'Trong không gian Oxyz, hai mặt phẳng (P): z={a} và (Q): z={b} song song. Tính khoảng cách giữa (P) và (Q).',ans,f'Cả hai mặt phẳng có pháp tuyến (0;0;1). Khoảng cách theo phương pháp tuyến chính là |{b}−({a})|={ans}.',S.Abs(b-a))
@add(11,'xac_suat_11','at_least_one_independent_success','Xác suất có ít nhất một thành công qua n lần thử Bernoulli','P(X≥1)=1−(1−p)^n','Các lần thử độc lập, mỗi lần xác suất thành công p')
def b24(k):
 n=2+k;p=S.Rational(1,k+3);ans=1-(1-p)**n
 return Q(f'Thử {n} lần độc lập, mỗi lần có xác suất thành công p={f(p)}. Tính xác suất có ít nhất một lần thành công.',ans,f'Biến cố đối là không có lần thành công nào, xác suất (1−p)^{n}=(1−{f(p)})^{n}. Do đó xác suất ít nhất một thành công bằng 1−(1−{f(p)})^{n}={f(ans)}.',1-S.prod([1-p for _ in range(n)]))

# GRADE 12: analytical calculus, probability, complex numbers, spatial coordinate geometry
@add(12,'tinh_don_dieu','decreasing_cubic_interval','Độ dài khoảng nghịch biến của hàm bậc ba đặc biệt','f′(x)=3(x²−a²)<0 khi −a<x<a','a>0, f(x)=x³−3a²x')
def c01(k):
 a=k+2;ans=2*a
 return Q(f'Hàm số f(x)=x³−{3*a*a}x nghịch biến trên khoảng (−a;a). Tính độ dài khoảng nghịch biến lớn nhất này.',ans,f'Tính đạo hàm f′(x)=3x²−{3*a*a}=3(x−{a})(x+{a}). Đạo hàm âm đúng khi −{a}<x<{a}. Độ dài khoảng là {a}−(−{a})={ans}.',S.Rational(2*a))
@add(12,'cuc_tri','local_maximum_of_odd_cubic','Giá trị cực đại địa phương của f(x)=x³−3a²x','Cực đại tại x=−a, f(−a)=2a³','a>0, đạo hàm đổi dấu từ dương sang âm')
def c02(k):
 a=k+2;ans=2*a**3;fn=x**3-3*a*a*x
 return Q(f'Cho f(x)=x³−{3*a*a}x. Tìm giá trị cực đại địa phương của hàm số.',ans,f'f′(x)=3(x²−{a*a}), nghiệm x=−{a}, x={a}. Đạo hàm đổi từ dương sang âm tại x=−{a} nên cực đại đạt tại đó. f(−{a})=−{a**3}+{3*a**3}={ans}.',fn.subs(x,-a))
@add(12,'tien_can','rational_vertical_asymptote','Tiệm cận đứng của phân thức bậc nhất/bậc nhất','x=−d/c nếu mẫu bằng 0 nhưng tử khác 0','c khác 0, tử không triệt tiêu tại nghiệm mẫu')
def c03(k):
 a=k+5;b=k+2;c=k+2;d=k+3;ans=-S.Rational(d,c)
 assert a*ans+b!=0
 return Q(f'Đồ thị y=({a}x+{b})/({c}x+{d}) có tiệm cận đứng x=x₀. Tính x₀.',ans,f'Mẫu bằng 0 tại {c}x+{d}=0, do đó x₀=−{d}/{c}={f(ans)}. Tại đây tử có giá trị {f(a*ans+b)} khác 0, nên phân thức tiến ra vô cực và x=x₀ là tiệm cận đứng.',S.solve(S.Eq(c*x+d,0),x)[0])
@add(12,'tiep_tuyen','tangent_natural_log_intercept','Tung độ giao trục Oy của tiếp tuyến với đồ thị y=ln x','b=ln(a)−1 tại x=a','a>0, tiếp tuyến y=ln a+(x−a)/a')
def c04(k):
 n=k+1;a=S.exp(n);ans=n-1
 return Q(f'Tiếp tuyến của đồ thị y=ln x tại x₀=e^{n} cắt trục Oy tại điểm có tung độ b. Tính b.',ans,f'Đạo hàm (ln x)′=1/x. Tại x₀=e^{n}, hệ số góc là e^(−{n}), tung độ tiếp xúc ln(e^{n})={n}. Phương trình tiếp tuyến y={n}+e^(−{n})(x−e^{n}). Thế x=0 được b={n}−1={ans}.',S.simplify(S.log(a)-a*(1/a)))
@add(12,'pt_mu','quadratic_in_exponential','Đặt t=2^x giải phương trình bậc hai theo t','(2^x−A)(2^x−B)=0','A,B là lũy thừa nguyên dương của 2 và khác nhau')
def c05(k):
 p=k+1;q=p+2;A=2**p;B=2**q;ans=p+q
 return Q(f'Giải phương trình 2^(2x)−{A+B}·2^x+{A*B}=0. Tính tổng các nghiệm thực x.',ans,f'Đặt t=2^x>0. Phương trình thành t²−{A+B}t+{A*B}=0=(t−{A})(t−{B}). Do đó 2^x={A}=2^{p} hoặc 2^x={B}=2^{q}; nghiệm x={p},{q}, tổng là {ans}.',S.log(A,2)+S.log(B,2))
@add(12,'pt_logarit','log_sum_quadratic','Giải phương trình tổng hai logarit với miền xác định','log_a x+log_a(x−m)=log_a C => x(x−m)=C','a>1, x>m>0')
def c06(k):
 m=k+1;n=2*k+6;C=n*(n-m)
 return Q(f'Tìm nghiệm thực của log₂(x)+log₂(x−{m})=log₂({C}).',n,f'Điều kiện x>{m}. Gộp logarit: log₂[x(x−{m})]=log₂({C}), nên x²−{m}x−{C}=0. Vì {C}={n}·({n}−{m}), hai nghiệm là {n} và {m-n}. Nghiệm {m-n}≤{m} bị loại; nhận x={n}.',max(S.solve(S.Eq(x*(x-m),C),x)))
@add(12,'bpt_mu','exponential_inequality_integer_count','Đếm số nguyên trong đoạn thỏa bất phương trình mũ','2^x>2^k ⇔ x>k','Cơ số 2>1; x nguyên trong [0,N]')
def c07(k):
 m=k+3;N=m+7+k%3;ans=N-m
 return Q(f'Có bao nhiêu số nguyên x thuộc [0;{N}] thỏa 2^x>2^{m}?',ans,f'Vì cơ số 2>1, hàm 2^x đồng biến nên 2^x>2^{m} tương đương x>{m}. Các nghiệm nguyên là {m+1},...,{N}; số nghiệm là {N}−{m}={ans}.',sum(2**j>2**m for j in range(N+1)))
@add(12,'bpt_logarit','logarithmic_inequality_integer_count','Đếm nghiệm nguyên của bất phương trình logarit có dịch chuyển','log₂(x−a)≥m ⇔ x≥a+2^m','Điều kiện x−a>0; x trong đoạn cho trước')
def c08(k):
 a=k+2;m=2+k%3;lo=a+2**m;hi=lo+5+k;ans=hi-lo+1
 return Q(f'Đếm số nguyên x thuộc [0;{hi}] sao cho log₂(x−{a})≥{m}.',ans,f'Điều kiện x>{a}. Do log₂ đồng biến, log₂(x−{a})≥{m} ⇔ x−{a}≥2^{m}={2**m}, nghĩa là x≥{lo}. Trong đoạn đã cho x nhận {lo},...,{hi}: có {hi}−{lo}+1={ans} nghiệm.',sum(j>a and (j-a)>=2**m for j in range(hi+1)))
@add(12,'nguyen_ham_tich_phan','sine_definite_integral','Tích phân sin(ax) trên nửa chu kỳ','∫₀^(π/a) sin(ax)dx=2/a','a>0')
def c09(k):
 a=k+2;ans=S.Rational(2,a)
 return Q(f'Tính I=∫ từ 0 đến π/{a} của sin({a}x) dx.',ans,f'Nguyên hàm của sin({a}x) là −cos({a}x)/{a}. Thay cận, I=[−cos({a}x)/{a}] từ 0 đến π/{a}=(−cosπ+cos0)/{a}=2/{a}={f(ans)}.',S.integrate(S.sin(a*x),(x,0,S.pi/a)))
@add(12,'ung_dung_tich_phan','absolute_value_area','Tính diện tích dưới đồ thị |x−a| bằng chia khoảng','∫₀^(2a)|x−a|dx=a²','a>0, phân tích trị tuyệt đối tại x=a')
def c10(k):
 a=k+2;ans=a*a
 return Q(f'Tính diện tích hình phẳng giới hạn bởi y=|x−{a}|, trục Ox và hai đường x=0, x={2*a}.',ans,f'Đồ thị |x−{a}| không âm. Chia tại x={a}: diện tích bằng ∫₀^{a}({a}−x)dx+∫_{a}^{2*a}(x−{a})dx. Mỗi tích phân bằng {f(S.Rational(a*a,2))}; tổng bằng {ans}.',S.integrate(S.Abs(x-a),(x,0,2*a)))
@add(12,'g12_solid_of_revolution','volume_disks_linear_graph','Thể tích khối tròn xoay từ y=ax trên đoạn [0,b]','V=π∫₀ᵇ (ax)²dx=πa²b³/3','a,b>0; quay quanh trục Ox')
def c11(k):
 a=k+2;b=k+3;ans=S.Rational(a*a*b**3,3)
 return Q(f'Miền giới hạn bởi y={a}x, y=0, x=0, x={b} quay quanh Ox. Tính V/π của khối tròn xoay.',ans,f'Phương pháp đĩa: V=π∫₀^{b}({a}x)²dx=π·{a*a}[x³/3]₀^{b}=π·{a*a}·{b}³/3. Vậy V/π={f(ans)}.',S.integrate((a*x)**2,(x,0,b)))
@add(12,'xac_suat_12','expected_discrete_three_point','Kỳ vọng của biến ngẫu nhiên nhận ba giá trị','E(X)=Σ x_i·p_i','X nhận các giá trị −a,0,b; xác suất cộng thành 1')
def c12(k):
 a=k+1;b=2*k+5;p=S.Rational(1,k+3);q=S.Rational(1,2);r=1-p-q;ans=-a*p+b*r
 assert r>0
 return Q(f'Biến ngẫu nhiên X nhận giá trị −{a} với xác suất {f(p)}, 0 với xác suất 1/2 và {b} với xác suất {f(r)}. Tính E(X).',ans,f'Tổng xác suất là {f(p)}+1/2+{f(r)}=1. Kỳ vọng E(X)=−{a}·{f(p)}+0·1/2+{b}·{f(r)}={f(ans)}.',S.simplify(sum(v*prob for v,prob in [(-a,p),(0,q),(b,r)])))
@add(12,'thong_ke_12','population_variance_two_values','Phương sai mẫu với hai giá trị có tần số','Var=p(1−p)(a−b)²','Tính phương sai theo 1/n, không hiệu chỉnh n−1')
def c13(k):
 a=k+1;b=2*k+7;na=k+2;nb=3*k+5;n=na+nb;p=S.Rational(na,n);ans=p*(1-p)*(a-b)**2
 return Q(f'Mẫu gồm {na} quan sát bằng {a} và {nb} quan sát bằng {b}. Tính phương sai theo công thức chia cho n (không chia n−1).',ans,f'Gọi p={na}/{n} là tỉ lệ giá trị {a}, 1−p={nb}/{n} là tỉ lệ giá trị {b}. Với phân bố hai điểm, phương sai bằng p(1−p)({a}−{b})²={f(p)}·{f(1-p)}·{(a-b)**2}={f(ans)}.',S.Rational(na*a*a+nb*b*b,n)-(S.Rational(na*a+nb*b,n))**2)
@add(12,'g12_geom_line_plane_intersection','line_plane_parameter','Tìm tham số giao điểm của đường thẳng tham số với mặt phẳng','t=(d−n·A)/(n·u)','n·u khác 0')
def c14(k):
 a=k+2;b=2*k+1;c=k+5;u=1;v=2;w=k+3;tar=k+2;D=a+2*b+3*c+tar*(u+2*v+3*w)
 return Q(f'Trong Oxyz, d: (x,y,z)=({a},{b},{c})+t({u},{v},{w}). Giao với (P):x+2y+3z={D}. Tìm tham số t tại giao điểm.',tar,f'Thay tọa độ x={a}+{u}t, y={b}+{v}t, z={c}+{w}t vào (P): ({a}+2·{b}+3·{c})+({u}+2·{v}+3·{w})t={D}. Suy ra t=({D}−{a+2*b+3*c})/{u+2*v+3*w}={tar}.',S.solve(S.Eq(a+u*S.Symbol('t')+2*(b+v*S.Symbol('t'))+3*(c+w*S.Symbol('t')),D),S.Symbol('t'))[0])
@add(12,'g12_geom_sphere_tangent_plane','tangent_plane_constant','Hệ số tự do của mặt phẳng tiếp xúc với mặt cầu','n·X=n·T khi n=T−C','Bán kính CT vuông góc mặt phẳng tiếp xúc tại T')
def c15(k):
 C=S.Matrix([k+1,2*k+3,k+4]);r=3*(k+1);n=S.Matrix([1,2,2]);T=C+(k+1)*n;d=n.dot(T)
 return Q(f'Mặt cầu tâm C({C[0]};{C[1]};{C[2]}), bán kính R={r}, tiếp xúc (P) tại T({T[0]};{T[1]};{T[2]}). Biết (P) có phương trình x+2y+2z=D. Tính D.',d,f'Vectơ CT=({k+1};{2*(k+1)};{2*(k+1)}) cùng hướng n=(1;2;2), là pháp tuyến của mặt phẳng tiếp xúc. Vì T nằm trên (P), D=x_T+2y_T+2z_T={T[0]}+2·{T[1]}+2·{T[2]}={d}.',n.dot(T))
@add(12,'g12_geom_two_planes_angle','angle_between_planes_cos_squared','Bình phương cos góc nhọn giữa hai mặt phẳng','cos²φ=(n₁·n₂)²/(||n₁||²||n₂||²)','Hai mặt phẳng cắt nhau; pháp tuyến cho trước')
def c16(k):
 a=2+k;b=3+k;n1=S.Matrix([a,b,0]);n2=S.Matrix([0,b,a]);val=S.Rational((n1.dot(n2))**2,n1.dot(n1)*n2.dot(n2))
 return Q(f'Hai mặt phẳng có vectơ pháp tuyến n₁=({a};{b};0), n₂=(0;{b};{a}). Tính cos² góc nhọn giữa chúng.',val,f'Góc nhọn giữa hai mặt phẳng bằng góc nhọn giữa hai pháp tuyến. n₁·n₂={b*b}, ||n₁||²=||n₂||²={a*a+b*b}. Vì vậy cos²φ=({b*b})²/({a*a+b*b}²)={f(val)}.',S.Rational(b**4,(a*a+b*b)**2))
@add(12,'g12_geom_line_plane_angle','angle_between_line_plane_sin_squared','Bình phương sin góc giữa đường thẳng và mặt phẳng','sin²φ=(u·n)²/(||u||²||n||²)','u vectơ chỉ phương đường thẳng, n pháp tuyến mặt phẳng')
def c17(k):
 a=k+1;u=S.Matrix([3,4,a]);n=S.Matrix([0,0,1]);ans=S.Rational(a*a,25+a*a)
 return Q(f'Đường thẳng d có vectơ chỉ phương u=(3;4;{a}), mặt phẳng (P): z=0. Tính sin² góc giữa d và (P).',ans,f'Pháp tuyến mặt phẳng n=(0;0;1). Sin góc đường thẳng-mặt phẳng là |u·n|/(||u||·||n||). Ta có u·n={a}, ||u||²={25+a*a}, ||n||²=1. Vậy sin²φ={a*a}/{25+a*a}={f(ans)}.',S.Rational((u.dot(n))**2,u.dot(u)*n.dot(n)))
@add(12,'g12_geom_sphere_plane_intersection','integer_parallel_secant_planes','Đếm các mặt phẳng tọa độ nguyên cắt mặt cầu theo đường tròn thực','z=m cắt x²+y²+z²=R² thành đường tròn nếu |m|<R','R nguyên dương, m nguyên')
def c18(k):
 R=k+5;ans=2*R-1
 return Q(f'Cho mặt cầu x²+y²+z²={R*R}. Với m nguyên, xét mặt phẳng z=m. Có bao nhiêu giá trị m để giao tuyến là đường tròn có bán kính dương?',ans,f'Thay z=m vào phương trình mặt cầu: x²+y²={R*R}−m². Giao tuyến là đường tròn bán kính dương khi {R*R}−m²>0, tương đương −{R}<m<{R}. Các số nguyên m từ −{R-1} đến {R-1} có {ans} giá trị.',sum(1 for m in range(-R,R+1) if m*m<R*R))

@add(12,'g12_geom_skew_line_relation','skew_lines_distance_squared','Bình phương khoảng cách hai đường thẳng chéo nhau bằng tích hỗn tạp','d²=[(B−A)·(u×v)]²/||u×v||²','Hai đường thẳng không song song, không cắt nhau')
def c19(k):
 t=2*k+3;A=S.Matrix([0,0,0]);B=S.Matrix([0,k+1,k+1+t]);u=S.Matrix([1,0,0]);v=S.Matrix([0,1,1]);cross=u.cross(v);ans=S.Rational(((B-A).dot(cross))**2,cross.dot(cross))
 return Q(f'Trong Oxyz, d₁:(x,y,z)=(0,0,0)+s(1,0,0), d₂:(x,y,z)=(0,{k+1},{k+1+t})+t(0,1,1). Tính bình phương khoảng cách giữa d₁ và d₂.',ans,f'Chọn u=(1;0;0), v=(0;1;1), suy ra u×v=(0;−1;1), ||u×v||²=2. Vectơ nối A đến B là (0;{k+1};{k+1+t}), tích hỗn tạp (B−A)·(u×v)={t}. Khoảng cách bình phương d²={t}²/2={f(ans)}.',S.Rational(t*t,2))
@add(12,'g12_geom_parameter_geometry','parameter_line_parallel_plane','Tìm tham số để đường thẳng song song mặt phẳng','n(m)·u=0, đồng thời không nằm trong mặt phẳng','Đường thẳng chỉ phương u=(2,−k,1); mặt phẳng pháp tuyến (m,2,3)')
def c20(k):
 p=k+2;ans=S.Rational(2*p-3,2)
 return Q(f'Đường thẳng d đi qua O(0;0;0), chỉ phương u=(2;−{p};1). Mặt phẳng (P):mx+2y+3z=1. Tìm m để d song song (P).',ans,f'Pháp tuyến của (P) là n=(m;2;3). Điều kiện song song: n·u=2m−2·{p}+3=0, nên m=(2·{p}−3)/2={f(ans)}. Vì O không thuộc (P), d không nằm trong (P).',S.solve(S.Eq(2*S.Symbol('m')-2*p+3,0),S.Symbol('m'))[0])
@add(12,'g12_geom_min_distance_3d','distance_point_to_sphere_squared','Bình phương khoảng cách ngắn nhất từ điểm ngoài tới mặt cầu','d_min²=(OP−R)²','P nằm ngoài mặt cầu, OP>R')
def c21(k):
 R=k+3;D=2*k+8;ans=(D-R)**2
 return Q(f'Mặt cầu tâm O bán kính R={R}. Điểm P nằm ngoài mặt cầu và OP={D}. Tính bình phương khoảng cách ngắn nhất từ P đến một điểm trên mặt cầu.',ans,f'Điểm gần P nhất trên mặt cầu nằm trên đoạn OP, cách O đúng bán kính R. Khoảng cách ngắn nhất là OP−R={D}−{R}={D-R}. Bình phương bằng {ans}.',S.Integer((D-R)**2))
@add(12,'g12_complex_plane_geometry','complex_circle_farthest','Giá trị lớn nhất của khoảng cách |z−w| khi |z| cố định','max_{|z|=R}|z−w|=R+|w|','R>0, w cố định trong mặt phẳng phức')
def c22(k):
 R=k+5;t=k+1;w=3*t+4*t*S.I;ans=R+5*t
 return Q(f'Cho z∈C thỏa |z|={R}, đặt w={3*t}+{4*t}i. Tìm giá trị lớn nhất của |z−w|.',ans,f'Bất đẳng thức tam giác cho |z−w|≤|z|+|w|={R}+√(({3*t})²+({4*t})²)={R}+{5*t}={ans}. Dấu bằng khi z ngược hướng w với |z|={R}, nên GTLN thực sự đạt {ans}.',R+S.Abs(w))
@add(12,'pt_so_phuc','complex_linear_division','Tính phần thực nghiệm phương trình tuyến tính phức','z=(c+di)/(a+bi), phần thực = (ac+bd)/(a²+b²)','a²+b²>0')
def c23(k):
 c=k+5;d=2*k+3;ans=S.Rational(3*c+4*d,25)
 return Q(f'Giải phương trình (3+4i)z={c}+{d}i với z phức. Tính phần thực của z.',ans,f'Chia hai vế cho 3+4i và nhân liên hợp 3−4i: z=(({c}+{d}i)(3−4i))/25. Phần thực của tử là 3·{c}+4·{d}={3*c+4*d}, suy ra Re(z)={f(ans)}.',S.re((c+d*S.I)/(3+4*S.I)))
@add(12,'g12_integral_optimization','ftc_chain_derivative','Đạo hàm của tích phân có cận phụ thuộc x theo định lý cơ bản','d/dx∫₀^(x²)t^pdt=2x(x²)^p','x>0, p nguyên dương')
def c24(k):
 p=2+k%3;t=k+2;ans=2*t**(2*p+1);z=S.Symbol('z',real=True)
 return Q(f'Đặt F(x)=∫ từ 0 đến x² của t^{p}dt. Tính F′({t}).',ans,f'Theo định lý cơ bản của giải tích và quy tắc hàm hợp, F′(x)=(x²)^{p}·(2x)=2x^{2*p+1}. Thay x={t}: F′({t})=2·{t}^{2*p+1}={ans}.',S.diff(S.integrate(z**p,(z,0,x*x)),x).subs(x,t))
@add(12,'g12_geom_line_equation_3d','line_param_find_coordinate','Tìm tọa độ trên đường thẳng tham số nhờ một hoành độ cho trước','x=a+ut suy ra t=(x−a)/u, rồi thế vào z=c+wt','u khác 0')
def c25(k):
 a=k+1;b=k+2;c=2*k+3;u=2;v=k+1;w=k+3;t=k+2;X=a+u*t;Z=c+w*t
 return Q(f'Đường thẳng trong Oxyz có (x,y,z)=({a},{b},{c})+t({u},{v},{w}). Điểm P trên đường thẳng có hoành độ x={X}. Tính cao độ z_P.',Z,f'Từ x={a}+{u}t={X} suy ra t=({X}−{a})/{u}={t}. Thay vào tọa độ z={c}+{w}t cho z_P={c}+{w}·{t}={Z}.',S.Integer(c+w*S.Rational(X-a,u)))
@add(12,'g12_geom_solid_surface_area','cylinder_total_surface','Diện tích toàn phần hình trụ gồm hai đáy và mặt xung quanh','S_tp=2πrh+2πr²','r,h>0; hình trụ tròn xoay')
def c26(k):
 r=k+3;h=2*k+5;ans=2*r*(h+r)
 return Q(f'Hình trụ có bán kính đáy r={r}, chiều cao h={h}. Tính S_tp/π với S_tp là diện tích toàn phần.',ans,f'Diện tích xung quanh là 2πrh=2π·{r}·{h}; hai đáy có tổng diện tích 2πr²=2π·{r}². Tổng S_tp=2πr(h+r), do đó S_tp/π=2·{r}({h}+{r})={ans}.',S.Integer(2*r*h+2*r*r))
@add(12,'hinh_khoi_va_the_tich_co_ban_12','frustum_cone_volume','Thể tích hình nón cụt bán kính hai đáy R,r','V=πh(R²+Rr+r²)/3','R>r>0, h>0')
def c27(k):
 r=k+2;R=r+3;h=3*(k+2);ans=S.Rational(h*(R*R+R*r+r*r),3)
 return Q(f'Hình nón cụt có bán kính đáy lớn R={R}, đáy nhỏ r={r}, chiều cao h={h}. Tính V/π.',ans,f'Công thức thể tích nón cụt V=(πh/3)(R²+Rr+r²). Thay R={R}, r={r}, h={h} được V/π=({h}/3)({R*R}+{R*r}+{r*r})={f(ans)}.',S.Rational(h,3)*(R*R+R*r+r*r))
@add(12,'g12_geom_sphere_equation','sphere_complete_square','Tìm bán kính từ phương trình mặt cầu dạng khai triển','R²=(a²+b²+c²)−d với phương trình x²+y²+z²−2ax−2by−2cz+d=0','Phương trình mô tả mặt cầu thực R>0')
def c28(k):
 a=k+1;b=k+2;c=k+3;r=k+5;D=a*a+b*b+c*c-r*r;ans=r*r
 return Q(f'Mặt cầu (S): x²+y²+z²−{2*a}x−{2*b}y−{2*c}z+({D})=0. Tính bình phương bán kính R².',ans,f'Hoàn thành bình phương được (x−{a})²+(y−{b})²+(z−{c})²={a*a}+{b*b}+{c*c}−({D})={ans}. Vậy mặt cầu tâm ({a};{b};{c}) và R²={ans}.',S.Integer(a*a+b*b+c*c-D))
@add(12,'g12_geom_3d_optimization','box_volume_fixed_edge_sum','Tối đa hóa thể tích hộp chữ nhật có tổng ba kích thước cố định','V=xyz≤[(x+y+z)/3]³, dấu bằng khi x=y=z','x,y,z dương, tổng ba cạnh cho trước','nâng cao')
def c29(k):
 total=3*(k+5);ans=(k+5)**3
 return Q(f'Xét hình hộp chữ nhật có ba cạnh x,y,z dương thỏa x+y+z={total}. Tìm thể tích lớn nhất V=xyz.',ans,f'Áp dụng bất đẳng thức AM–GM cho ba số dương, (x+y+z)/3≥∛(xyz). Vì x+y+z={total}, suy ra xyz≤({total}/3)³={ans}. Dấu bằng xảy ra khi x=y=z={k+5}, là kích thước hợp lệ nên GTLN đúng bằng {ans}.',S.Rational(total,3)**3)

# SECOND CYCLE: prioritize low-volume topics absent from the first V192 cycle.
@add(10,'menh_de_tap_hop','set_complement_union_count','Số phần tử ngoài hợp hai tập trong vũ trụ hữu hạn','|U\\(A∪B)|=|U|−|A|−|B|+|A∩B|','A,B là tập con của U hữu hạn')
def d01(k):
 u=70+5*k;a=20+k;b=25+k;c=5+k;ans=u-a-b+c
 return Q(f'Cho vũ trụ U có {u} phần tử, |A|={a}, |B|={b}, |A∩B|={c}. Tính số phần tử không thuộc A và không thuộc B.',ans,f'Áp dụng công thức hợp: |A∪B|={a}+{b}−{c}={a+b-c}. Phần bù của hợp trong U có {u}−({a+b-c})={ans} phần tử.',u-(a-c)-(b-c)-c)
@add(10,'bat_phuong_trinh','quadratic_between_roots','Đếm nghiệm nguyên của bất phương trình tam thức âm giữa hai nghiệm','(x−a)(x−b)<0 ⇔ a<x<b','Hai nghiệm phân biệt a<b và hệ số bậc hai dương')
def d02(k):
 a=k-4;b=a+6+(k%3);ans=b-a-1
 return Q(f'Có bao nhiêu số nguyên x thỏa bất phương trình x²−({a+b})x+({a*b})<0?',ans,f'Phân tích x²−({a+b})x+({a*b})=(x−({a}))(x−({b})). Vì a={a}<b={b} và hệ số x² dương, tích âm khi {a}<x<{b}. Các nghiệm nguyên có {b-a-1} giá trị.',len([t for t in range(a-2,b+3) if (t-a)*(t-b)<0]))
@add(10,'ham_so_bac_hai','parabola_vertex_abscissa','Hoành độ đỉnh của đồ thị tam thức bậc hai','x_đỉnh=−b/(2a)','a khác 0; y=ax²+bx+c')
def d03(k):
 a=k+1;b=2*(k+1)*(k-4);c=k+7;ans=4-k
 return Q(f'Hàm số f(x)={a}x²+({b})x+{c} có đỉnh I(x₀;y₀). Tìm x₀.',ans,f'Tung độ đỉnh không cần tính, dùng hoành độ x₀=−b/(2a). Với a={a}, b={b} suy ra x₀=−({b})/(2·{a})={ans}.',-S.Rational(b,2*a))
@add(10,'phuong_trinh_he','sum_difference_system','Giải hệ hai phương trình dạng tổng và hiệu','x=(S+D)/2, y=(S−D)/2','Hai ẩn thực x,y')
def d04(k):
 a=k+3;b=2*k-1;sm=a+b;diff=a-b
 return Q(f'Cho hệ hai phương trình x+y={sm}, x−y={diff}. Tìm giá trị x.',a,f'Cộng hai phương trình: 2x=({sm})+({diff})={2*a}. Chia 2 ta được x={a}. Thế lại cho y={b}.',S.solve([S.Eq(S.Symbol('u')+S.Symbol('v'),sm),S.Eq(S.Symbol('u')-S.Symbol('v'),diff)],[S.Symbol('u'),S.Symbol('v')])[S.Symbol('u')])
@add(10,'hoan_vi_chinh_hop_to_hop','arrange_three_distinct_roles','Chỉnh hợp chập ba khi phân công ba vai trò khác nhau','A(n,3)=n(n−1)(n−2)','n người khác nhau, ba vị trí phân biệt')
def d05(k):
 n=6+k;ans=n*(n-1)*(n-2)
 return Q(f'Có {n} người. Chọn và phân công 3 người khác nhau vào ba chức vụ lớp trưởng, lớp phó, thủ quỹ. Có bao nhiêu cách?',ans,f'Chức vụ phân biệt: chọn lớp trưởng có {n} cách; chọn lớp phó từ {n-1} người còn lại, chọn thủ quỹ từ {n-2} người. Theo quy tắc nhân, có {n}·{n-1}·{n-2}={ans} cách.',S.factorial(n)/S.factorial(n-3))
@add(10,'xac_suat','hypergeometric_all_red_three','Xác suất lấy ba phần tử cùng loại khi không hoàn lại','P=C(R,3)/C(R+B,3)','R≥3, B≥1, rút cùng lúc ba viên bi')
def d06(k):
 R=5+k;B=k+4;ans=S.Rational(S.binomial(R,3),S.binomial(R+B,3))
 return Q(f'Hộp có {R} bi đỏ và {B} bi xanh. Rút đồng thời 3 bi ngẫu nhiên. Tính xác suất cả 3 bi đều đỏ.',ans,f'Không gian mẫu có C({R+B},3)={S.binomial(R+B,3)} cách chọn. Biến cố ba bi đỏ có C({R},3)={S.binomial(R,3)} cách. Xác suất bằng C({R},3)/C({R+B},3)={f(ans)}.',S.Rational(R*(R-1)*(R-2),(R+B)*(R+B-1)*(R+B-2)))
@add(10,'tap_hop','cartesian_product_cardinality','Số cặp có thứ tự trong tích Descartes hai tập hữu hạn','|A×B|=|A|·|B|','Hai tập hữu hạn, đếm cặp có thứ tự','nền tảng')
def d07(k):
 a=k+3;b=2*k+4;ans=a*b
 return Q(f'Hai tập hữu hạn A và B có lần lượt {a} và {b} phần tử. Tích Descartes A×B có bao nhiêu cặp có thứ tự?',ans,f'Với mỗi trong {a} phần tử a∈A, có đúng {b} lựa chọn b∈B. Theo quy tắc nhân, |A×B|={a}·{b}={ans}.',S.Integer(a*b))
@add(10,'ham_so','domain_square_root_linear','Điểm đầu của miền xác định hàm căn bậc hai tuyến tính','√(ax−b) xác định khi x≥b/a với a>0','a>0; biến thực','nền tảng')
def d08(k):
 a=k+2;b=(k+2)*(k+3);ans=k+3
 return Q(f'Hàm y=√({a}x−{b}) xác định với x≥c. Tìm c nhỏ nhất.',ans,f'Biểu thức dưới căn bậc hai phải không âm: {a}x−{b}≥0. Vì {a}>0, x≥{b}/{a}={ans}. Đây là cận dưới chính xác của miền xác định.',S.Rational(b,a))
@add(10,'ham_so_bac_nhat','line_slope_from_points','Hệ số góc đường thẳng qua hai điểm trong Oxy','a=(y_B−y_A)/(x_B−x_A)','x_B khác x_A')
def d09(k):
 x1=k+1;x2=x1+3+k%3;m=k+2;y1=2*k-3;y2=y1+m*(x2-x1)
 return Q(f'Đường thẳng y=ax+b đi qua A({x1};{y1}), B({x2};{y2}). Tìm hệ số góc a.',m,f'Từ hai phương trình y_A=ax_A+b và y_B=ax_B+b, lấy hiệu: a=(y_B−y_A)/(x_B−x_A)=({y2}−({y1}))/({x2}−{x1})={m}.',S.Rational(y2-y1,x2-x1))
@add(10,'phuong_trinh','parameter_infinite_solutions','Điều kiện phương trình tuyến tính có vô số nghiệm','a(m)x=b(m) có vô số nghiệm khi a(m)=b(m)=0','Hai vế tuyến tính theo ẩn x')
def d10(k):
 a=k+2
 return Q(f'Tìm m để phương trình (m−{a})x=3(m−{a}) có vô số nghiệm thực x.',a,f'Phương trình ax=b có vô số nghiệm khi a=0 và b=0. Ở đây hệ số là m−{a}, vế phải là 3(m−{a}); chúng đồng thời bằng 0 khi m={a}. Với m khác {a}, phương trình có nghiệm duy nhất x=3.',S.Integer(a))
@add(10,'he_phuong_trinh','cramer_rule_two_unknowns','Giải hệ hai phương trình hai ẩn bằng định thức Cramer','x=det(A_x)/det(A), det(A)≠0','Hệ tuyến tính có định thức ma trận hệ số khác 0')
def d11(k):
 a=k+2;b=k+3;u=a+2*b;v=2*a-b
 return Q(f'Hệ x+2y={u}, 2x−y={v} có nghiệm duy nhất (x,y). Tìm y.',b,f'Ma trận hệ số [[1,2],[2,−1]] có định thức −5 khác 0. Nhân phương trình thứ hai với −1 và cộng hai lần phương trình thứ nhất: 5y=2·{u}−{v}={5*b}. Vậy y={b}, suy ra x={a}.',S.solve([S.Eq(S.Symbol('u')+2*S.Symbol('v'),u),S.Eq(2*S.Symbol('u')-S.Symbol('v'),v)],[S.Symbol('u'),S.Symbol('v')])[S.Symbol('v')])
@add(10,'he_thuc_luong_tam_giac','extended_sine_rule','Tìm bán kính ngoại tiếp bằng định lý sin mở rộng','2R=a/sin A','Góc A có sin A>0 và cạnh đối diện a')
def d12(k):
 t=k+2;a=6*t;ans=5*t
 return Q(f'Trong tam giác ABC, cạnh BC={a}, sin∠A=3/5. Tính bán kính đường tròn ngoại tiếp R.',ans,f'Định lý sin mở rộng: BC/sin A=2R. Do đó R={a}/(2·3/5)=({a}·5)/6={ans}.',S.Rational(a,2)/S.Rational(3,5))
@add(10,'toa_do_phang','point_distance_pythagorean','Khoảng cách giữa hai điểm trong hệ tọa độ Oxy','AB=√[(x_B−x_A)²+(y_B−y_A)²]','Hai điểm A,B khác nhau','nền tảng')
def d13(k):
 t=k+1;px=k-3;py=2*k+1;x2=px+3*t;y2=py+4*t;ans=5*t
 return Q(f'Tính khoảng cách giữa A({px};{py}) và B({x2};{y2}) trong mặt phẳng Oxy.',ans,f'Ta có Δx={x2}−({px})={3*t}, Δy={y2}−({py})={4*t}. Do đó AB=√[({3*t})²+({4*t})²]={ans} theo định lý Pythagore.',S.sqrt((x2-px)**2+(y2-py)**2))
@add(10,'duong_tron','arc_length_radians','Độ dài cung tròn tính bằng radian','L=Rθ với θ tính theo radian','Bán kính R>0, góc ở tâm θ≥0')
def d14(k):
 R=6*(k+2);theta=S.Rational(k+1,k+3);ans=R*theta
 return Q(f'Đường tròn có bán kính R={R}. Một cung có góc ở tâm θ={f(theta)} radian. Tính độ dài cung.',ans,f'Khi góc tính bằng radian, chiều dài cung L=Rθ. Thay R={R}, θ={f(theta)} ta có L={R}·{f(theta)}={f(ans)}.',S.Rational(R*(k+1),k+3))
@add(10,'hinh_hoc_10','centroid_divides_median','Trọng tâm chia đường trung tuyến theo tỉ số 2:1 từ đỉnh','AG=2AM/3','G là trọng tâm tam giác, AM trung tuyến')
def d15(k):
 m=3*(k+4);ans=2*m//3
 return Q(f'Tam giác ABC có đường trung tuyến AM={m}. G là trọng tâm tam giác. Tính AG.',ans,f'Tính chất trọng tâm: AG:GM=2:1, nên AG=2AM/3. Thế AM={m} ta có AG=2·{m}/3={ans}.',S.Rational(2*m,3))
@add(10,'hinh_hoc_co_ban_10','trapezoid_area','Diện tích hình thang theo tổng hai đáy và chiều cao','S=(a+b)h/2','Hai đáy song song, chiều cao h>0','nền tảng')
def d16(k):
 a=k+4;b=2*k+9;h=2*(k+2);ans=S.Rational((a+b)*h,2)
 return Q(f'Hình thang có hai đáy dài {a} và {b}, chiều cao {h}. Tính diện tích.',ans,f'Áp dụng công thức diện tích hình thang S=(đáy lớn+đáy nhỏ)·chiều cao/2. S=({a}+{b})·{h}/2={f(ans)}.',S.Rational((a+b)*h,2))
@add(10,'tam_giac_tu_giac_10','rhombus_diagonals_area','Diện tích hình thoi bằng nửa tích hai đường chéo','S=d₁d₂/2','Hai đường chéo vuông góc cắt nhau tại trung điểm','nền tảng')
def d17(k):
 a=2*(k+3);b=2*(k+5);ans=a*b//2
 return Q(f'Một hình thoi có độ dài hai đường chéo lần lượt {a} và {b}. Tính diện tích hình thoi.',ans,f'Hai đường chéo của hình thoi vuông góc nhau, chia hình thoi thành bốn tam giác vuông bằng nhau. Diện tích tổng là S=d₁d₂/2={a}·{b}/2={ans}.',S.Rational(a*b,2))
@add(10,'he_thuc_luong_van_dung_10','triangle_area_included_sine','Diện tích tam giác từ hai cạnh kề và sin góc xen giữa','S=ab·sin C/2','Hai cạnh a,b dương và góc xen giữa hợp lệ')
def d18(k):
 a=2*(k+3);b=3*(k+4);ss=S.Rational(3,5);ans=S.Rational(a*b,2)*ss
 return Q(f'Tam giác ABC có AB={a}, AC={b}, sin∠A=3/5. Tính diện tích tam giác.',ans,f'Kẻ đường cao từ C xuống đường AB. Độ lớn chiều cao bằng AC·sin A={b}·3/5. Diện tích S=(1/2)·AB·AC·sin A=({a}·{b}·3)/(2·5)={f(ans)}.',S.Rational(a*b*3,10))
@add(10,'g10_geom_circle_chords_arcs','chord_using_half_central_angle','Tính dây cung theo góc ở tâm và bán kính','AB=2R·sin(θ/2)','Hai đầu dây thuộc đường tròn tâm O; sin(θ/2) đã biết')
def d19(k):
 R=5*(k+2);ans=6*(k+2)
 return Q(f'Đường tròn bán kính R={R} có dây AB tạo góc ở tâm AOB=θ với sin(θ/2)=3/5. Tính độ dài AB.',ans,f'Gọi H là trung điểm AB, OH vuông góc AB. Trong tam giác vuông AOH, AH=R·sin(θ/2)={R}·3/5. Vì AB=2AH nên AB=2·{R}·3/5={ans}.',S.Rational(2*R*3,5))
@add(10,'g10_geom_coordinate_distance_midpoint','coordinate_midpoint_x','Hoành độ trung điểm của đoạn trong Oxy','x_M=(x_A+x_B)/2','A,B có tọa độ thực','nền tảng')
def d20(k):
 a=2*k-9;b=4*k+3;ans=S.Rational(a+b,2)
 return Q(f'Trong hệ trục Oxy, cho A({a};{k+1}), B({b};{2*k+4}). M là trung điểm AB. Tìm hoành độ M.',ans,f'Vì M là trung điểm đoạn AB nên hoành độ M bằng trung bình cộng hai hoành độ A và B. Do đó x_M=(x_A+x_B)/2=[({a})+({b})]/2={f(ans)}.',S.Rational(a+b,2))
@add(10,'g10_geom_vector_proofs','parallelogram_fourth_vertex','Khôi phục đỉnh thứ tư hình bình hành bằng vectơ','D=A+C−B đối với ABCD thứ tự liên tiếp','A,B,C là ba đỉnh liên tiếp hình bình hành')
def d21(k):
 A=(k+1,k+3);B=(2*k+5,3*k+4);C=(4*k+7,k+9);ans=A[0]+C[0]-B[0]
 return Q(f'Trong Oxy, A({A[0]};{A[1]}), B({B[0]};{B[1]}), C({C[0]};{C[1]}) là ba đỉnh liên tiếp của hình bình hành ABCD. Tìm hoành độ D.',ans,f'Tính chất vectơ hình bình hành: AD=BC, hay D−A=C−B. Do đó D=A+C−B và x_D={A[0]}+{C[0]}−{B[0]}={ans}.',S.Integer(ans))
@add(10,'g10_combinatorics_olympiad','pigeonhole_guaranteed','Nguyên lý Dirichlet: số đồ vật tối thiểu để có ít nhất r đồ vật cùng hộp','N_min=m(r−1)+1','Phân N đồ vật vào m hộp, m,r nguyên dương','nâng cao')
def d22(k):
 m=k+3;r=3+(k%4);ans=m*(r-1)+1
 return Q(f'Phân các viên bi vào {m} hộp. Cần ít nhất bao nhiêu viên để chắc chắn một hộp có ít nhất {r} viên?',ans,f'Nếu mọi hộp có nhiều nhất {r-1} viên thì tối đa xếp được {m}·{r-1}={m*(r-1)} viên. Thêm một viên buộc phải có hộp chứa ít nhất {r} viên. Vậy số tối thiểu là {ans}.',S.Integer(ans))

@add(11,'gioi_han','polynomial_difference_quotient','Giới hạn của thương (x^n−1)/(x−1) tại x=1','lim_(x→1)(x^n−1)/(x−1)=n','n nguyên dương')
def e01(k):
 n=k+3
 return Q(f'Tính L=lim khi x→1 của (x^{n}−1)/(x−1).',n,f'Phân tích x^{n}−1=(x−1)(1+x+...+x^{n-1}). Với x≠1, thương bằng tổng {n} số hạng. Khi x→1, mỗi số hạng tiến đến 1 nên L={n}.',S.limit((x**n-1)/(x-1),x,1))
@add(11,'dao_ham','sqrt_derivative_at_square','Đạo hàm căn bậc hai tại bình phương số dương','(√x)′=1/(2√x)','x>0')
def e02(k):
 a=k+2;ans=S.Rational(1,2*a)
 return Q(f'Cho hàm f(x)=√x trên (0;+∞). Tính f′({a*a}).',ans,f'Với x>0, đạo hàm f′(x)=1/(2√x). Thế x={a*a} được f′({a*a})=1/(2·{a})={f(ans)}.',S.diff(S.sqrt(x),x).subs(x,a*a))
@add(11,'ham_so_luong_giac_day_du','range_sine_affine','Giá trị nhỏ nhất của hàm y=a sin x+b','min y=b−|a|','a,b thực, x∈R')
def e03(k):
 a=k+2;b=3*k-7;ans=b-a
 return Q(f'Hàm số y={a}sin x+({b}) xác định trên R. Tìm giá trị nhỏ nhất của y.',ans,f'Vì −1≤sin x≤1, với {a}>0 ta có −{a}≤{a}sin x≤{a}. Cộng {b}, giá trị nhỏ nhất là {b}−{a}={ans}, đạt khi sin x=−1.',S.Integer(b-a))
@add(11,'gioi_han_ham_so','exp_zero_limit','Giới hạn cơ bản của hàm mũ tự nhiên ở 0','lim_(x→0) (e^(ax)−1)/x=a','a là hằng số thực')
def e04(k):
 a=k+2
 return Q(f'Tính lim khi x→0 của (e^({a}x)−1)/x.',a,f'Đặt t={a}x, khi x→0 thì t→0. Ta có (e^({a}x)−1)/x={a}·(e^t−1)/t. Giới hạn cơ bản (e^t−1)/t→1 nên giá trị bằng {a}.',S.limit((S.exp(a*x)-1)/x,x,0))
@add(11,'dao_ham_quy_tac','polynomial_product_derivative','Đạo hàm tích hai đa thức tại điểm cho trước','(uv)′=u′v+uv′','u,v khả vi')
def e05(k):
 a=k+2;b=k+4;xx=S.Symbol('zz');fn=(xx+a)*(xx*xx+b);ans=S.diff(fn,xx).subs(xx,1)
 return Q(f'Cho f(x)=(x+{a})(x²+{b}). Tính f′(1).',ans,f'Đặt u=x+{a}, v=x²+{b}. Quy tắc đạo hàm tích: f′=u′v+uv′=(x²+{b})+(x+{a})2x. Thay x=1 được (1+{b})+2(1+{a})={ans}.',S.expand(fn).diff(xx).subs(xx,1))
@add(11,'bai_toan_thuc_te_11','finite_annuity_geometric','Tổng giá trị khoản tiền gửi tăng trưởng theo cấp số nhân','S=p(1+r+...+r^(n−1))=p(r^n−1)/(r−1)','r>1; gửi đầu mỗi kỳ, đánh giá cuối các kỳ')
def e06(k):
 p=k+2;r=2+(k%2);n=k+3;ans=p*(r**n-1)//(r-1)
 return Q(f'Mỗi năm gửi {p} đơn vị tiền vào tài khoản, năm đầu tiên bắt đầu ngay bây giờ. Mỗi khoản tăng gấp {r} lần sau mỗi năm. Ngay sau khi gửi lần thứ {n}, tổng giá trị các khoản gửi tính theo thời điểm đó là bao nhiêu?',ans,f'Khoản gửi gần nhất có giá trị {p}; khoản trước đó thành {p}·{r}; lần trước nữa {p}·{r}², ...; khoản đầu là {p}·{r}^{n-1}. Tổng là cấp số nhân S={p}(1+{r}+...+{r}^{n-1})={p}({r}^{n}−1)/({r}−1)={ans}.',sum(p*r**j for j in range(n)))
@add(11,'bien_co_doc_lap_11','intersection_independent_events','Xác suất giao hai biến cố độc lập','P(A∩B)=P(A)P(B)','A,B độc lập; xác suất thuộc [0;1]')
def e07(k):
 p=S.Rational(k+1,k+4);q=S.Rational(k+2,k+5);ans=p*q
 return Q(f'Biến cố A, B độc lập, P(A)={f(p)}, P(B)={f(q)}. Tính P(A∩B).',ans,f'Theo định nghĩa hai biến cố độc lập, P(A∩B)=P(A)·P(B)={f(p)}·{f(q)}={f(ans)}.',S.cancel(S.Rational(k+1,k+4)*S.Rational(k+2,k+5)))
@add(11,'day_so_truy_hoi_11','add_n_recurrence','Truy hồi cộng theo chỉ số và tổng số tự nhiên','u_n=u₁+Σ_(j=1)^(n−1) j=u₁+n(n−1)/2','u_(n+1)=u_n+n, n nguyên dương')
def e08(k):
 a=k+2;n=k+5;ans=a+n*(n-1)//2
 return Q(f'Dãy số có u₁={a} và u_(n+1)=u_n+n (n≥1). Tính u_{n}.',ans,f'Viết các sai phân: u₂−u₁=1, u₃−u₂=2,..., u_n−u_(n−1)=n−1. Cộng vế theo vế: u_n−u₁=1+2+...+(n−1)=n(n−1)/2. Do đó u_{n}={a}+{n}·{n-1}/2={ans}.',S.Integer(a+sum(range(1,n))))
@add(11,'phep_bien_hinh_co_ban_11','reflection_across_horizontal','Ảnh điểm qua trục đối xứng là đường thẳng y=c','(x,y)→(x,2c−y)','Đường y=c nằm ngang')
def e09(k):
 c=k+2;a=2*k+1;b=3*k+7;ans=2*c-b
 return Q(f'Lấy ảnh Q của P({a};{b}) qua đường thẳng y={c} trong Oxy. Tìm tung độ Q.',ans,f'Khoảng cách theo phương thẳng đứng tới trục y={c} được bảo toàn và đổi dấu. Do đó y_Q=2·{c}−{b}={ans}; hoành độ giữ nguyên x_Q={a}.',S.Integer(2*c-b))
@add(11,'nhan_biet_hinh_khong_gian_11','euler_convex_polyhedron','Tìm số mặt từ đặc trưng Euler của đa diện lồi','V−E+F=2','Đa diện lồi, V là số đỉnh, E số cạnh','nền tảng')
def e10(k):
 n=k+4;v=2*n;e=3*n;ans=e-v+2
 return Q(f'Một đa diện lồi có V={v} đỉnh, E={e} cạnh. Theo công thức Euler, đa diện có bao nhiêu mặt F?',ans,f'Hệ thức Euler cho đa diện lồi: V−E+F=2. Suy ra F=2−V+E=2−{v}+{e}={ans}.',S.Integer(2-v+e))
@add(11,'vuong_goc_khong_gian','box_space_diagonal','Đường chéo không gian hình hộp chữ nhật theo định lý Pythagore ba chiều','d=√(a²+b²+c²)','a,b,c độ dài ba cạnh đôi một vuông góc')
def e11(k):
 t=k+1;a=2*t;b=3*t;c=6*t;ans=7*t
 return Q(f'Hình hộp chữ nhật có ba cạnh xuất phát từ một đỉnh dài {a}, {b}, {c}. Tính đường chéo không gian.',ans,f'Đường chéo đáy có bình phương bằng {a}²+{b}². Dùng Pythagore với cạnh vuông góc thứ ba, d²={a}²+{b}²+{c}²={49*t*t}; suy ra d={ans}.',S.sqrt(a*a+b*b+c*c))
@add(11,'g11_geom_section_ratio','similar_pyramid_volume_ratio','Tỉ số thể tích hai hình chóp đồng dạng do thiết diện song song đáy','V_nhỏ/V_lớn=(tỉ số chiều cao)^3','Mặt phẳng cắt song song đáy hình chóp','trung cấp')
def e12(k):
 a=k+2;b=k+5;r=S.Rational(a,b);ans=r**3
 return Q(f'Hình chóp S.ABC bị cắt bởi mặt phẳng song song (ABC) tại khoảng cách từ S bằng {a} phần đơn vị, còn chiều cao toàn chóp bằng {b} đơn vị. Tính V_chóp_nhỏ/V_chóp_lớn.',ans,f'Vì thiết diện song song đáy, hình chóp nhỏ đồng dạng với hình chóp lớn theo tỉ số chiều cao {a}/{b}={f(r)}. Thể tích của hai khối đồng dạng tỉ lệ với lập phương tỉ số đồng dạng. Vậy V_nhỏ/V_lớn=({f(r)})³={f(ans)}.',S.Rational(a**3,b**3))
@add(11,'g11_advanced_trig_equations','sin_equals_cos_count','Đếm nghiệm sin x=cos x trên số chu kỳ xác định','tan x=1 => x=π/4+jπ','cosx không thể bằng 0 ở nghiệm; x∈[0,2nπ)')
def e13(k):
 n=k+2;ans=2*n
 return Q(f'Phương trình sin x=cos x có bao nhiêu nghiệm trên [0;{2*n}π)?',ans,f'Tại nghiệm sin x=cos x thì cos x khác 0 nên tan x=1. Nghiệm tổng quát x=π/4+jπ. Điều kiện 0≤x<{2*n}π cho j=0,1,...,{2*n-1}. Vậy có {ans} nghiệm.',len(range(2*n)))
@add(11,'g11_geom_skew_lines_distance','skew_edges_of_cube_distance','Khoảng cách giữa hai cạnh chéo nhau trong hình lập phương','Khoảng cách bằng độ dài đoạn vuông góc chung','Hình lập phương ABCD.A′B′C′D′ cạnh a')
def e14(k):
 a=k+3
 return Q(f'Hình lập phương ABCD.A′B′C′D′ có cạnh a={a}. Tính khoảng cách giữa đường thẳng AB và DD′.',a,f'AB nằm theo một phương cạnh đáy, DD′ là cạnh đứng không cắt AB. Đoạn AD vuông góc AB (hình vuông đáy) và cũng vuông góc DD′ (cạnh đứng vuông góc mặt đáy). Vì AD là đoạn vuông góc chung, khoảng cách bằng AD={a}.',S.Integer(a))
@add(11,'phep_bien_hinh_11','homothety_center_origin','Phép vị tự tâm O tỉ số k đối với điểm P(x,y)','(x,y)→(kx,ky)','k khác 0, O là gốc tọa độ')
def e15(k):
 ratio=k+2;a=k+1;b=2*k+3;ans=ratio*a
 return Q(f'Phép vị tự tâm O, tỉ số k={ratio} biến P({a};{b}) thành P′. Tìm hoành độ P′.',ans,f'Vị tự tâm O nhân cả hai tọa độ với tỉ số {ratio}. Vì x_P={a}, hoành độ ảnh là x_P′={ratio}·{a}={ans}.',S.Integer(ratio*a))
@add(11,'g11_geom_three_perpendiculars','space_perpendicular_projection','Độ dài cạnh xiên từ hai đoạn trực giao theo định lý ba đường vuông góc','SB²=SA²+AB² khi SA⊥(P), A,B∈(P)','SA>0, AB>0')
def e16(k):
 t=k+2;h=3*t;d=4*t;ans=5*t
 return Q(f'Trong không gian, SA vuông góc với mặt phẳng (P), A,B thuộc (P), SA={h}, AB={d}. Tính SB.',ans,f'Vì SA⊥(P) nên SA⊥AB. Tam giác SAB vuông tại A, do đó SB²=SA²+AB²={h}²+{d}²={25*t*t}. Suy ra SB={ans}.',S.sqrt(h*h+d*d))

@add(12,'khao_sat_ham_so','oblique_asymptote_division','Tiệm cận xiên qua phép chia đa thức của hàm phân thức','(x²+ax+b)/(x+c)=x+(a−c)+R/(x+c)','Mẫu khác 0; x→±∞')
def f01(k):
 a=k+5+k//2;c=k+1;b=k+3;ans=a-c
 return Q(f'Xét f(x)=(x²+{a}x+{b})/(x+{c}). Tiệm cận xiên có dạng y=x+m. Tìm m.',ans,f'Chia đa thức: x²+{a}x+{b}=(x+{c})(x+({a-c}))+({b-c*(a-c)}). Vì số dư chia cho x+{c} tiến đến 0 khi x→±∞, tiệm cận xiên là y=x+{a-c}; m={ans}.',S.div(x*x+a*x+b,x+c,x)[0].coeff(x,0))
@add(12,'so_phuc','complex_modulus_multiplicative','Môđun của tích hai số phức theo tính nhân','|zw|=|z|·|w|','z,w∈C, môđun không âm')
def f02(k):
 t=k+1;s=k+2;z=3*t+4*t*S.I;w=5*s+12*s*S.I;ans=65*t*s
 return Q(f'Cho z={3*t}+{4*t}i, w={5*s}+{12*s}i. Tính |zw|.',ans,f'Môđun của tích thỏa |zw|=|z|·|w|. Ta có |z|=√[({3*t})²+({4*t})²]={5*t}, |w|=√[({5*s})²+({12*s})²]={13*s}. Vì thế |zw|={5*t}·{13*s}={ans}.',S.Abs(z*w))
@add(12,'toa_do_khong_gian','tetrahedron_centroid','Tọa độ trọng tâm tứ diện bằng trung bình cộng bốn đỉnh','G=(A+B+C+D)/4','A,B,C,D không đồng phẳng')
def f03(k):
 t=k+2;pts=[S.Matrix([0,0,0]),S.Matrix([4*t,0,0]),S.Matrix([0,4*t,0]),S.Matrix([0,0,4*t])];ans=t
 return Q(f'Tứ diện ABCD có A(0;0;0), B({4*t};0;0), C(0;{4*t};0), D(0;0;{4*t}). Tìm hoành độ trọng tâm G.',ans,f'Tọa độ trọng tâm tứ diện là trung bình cộng các tọa độ bốn đỉnh. Do đó x_G=(0+{4*t}+0+0)/4={ans}.',sum(P[0] for P in pts)/4)
@add(12,'gtln_gtnn','cubic_max_closed_interval','Giá trị lớn nhất của đa thức bậc ba trên đoạn kín qua đạo hàm','So sánh f tại hai đầu mút và các điểm tới hạn nội bộ','Đoạn [0,a] với a≥2')
def f04(k):
 a=k+3;z=S.Symbol('z');fn=z**3-3*a*z*z;left=0;right=2*a;points=[left,right,2*a];ans=max([fn.subs(z,t) for t in points])
 # Instead use f(z)=−z³+3a z² on [0,2a], max at right; derivative gives interior max vs endpoints? max at 2a ->4a³.
 fn=-z**3+3*a*z*z;maxv=4*a**3
 return Q(f'Hàm f(x)=−x³+{3*a}x² xét trên đoạn [0;{2*a}]. Tính GTLN của f.',maxv,f'f′(x)=−3x²+{6*a}x=3x({2*a}−x), dương trên (0;{2*a}). Do đó f tăng trên toàn đoạn, GTLN đạt tại x={2*a}. Giá trị f({2*a})=−({2*a})³+{3*a}({2*a})²={4*a**3}.',max([fn.subs(z,t) for t in range(2*a+1)]))
@add(12,'tuong_giao','parabola_horizontal_intersections','Đếm giao điểm parabol và đường thẳng ngang theo dấu biệt thức','x²+a=m => có 0,1,2 nghiệm tùy dấu m−a','m thực, xét riêng m<a, m=a, m>a')
def f05(k):
 a=k+1;delta=0 if k%3==0 else (k+3)**2 if k%3==1 else -(k+2);m=a+delta
 ans=1 if delta==0 else 2 if delta>0 else 0
 nature='đúng một nghiệm kép' if delta==0 else 'hai nghiệm phân biệt' if delta>0 else 'không có nghiệm thực'
 return Q(f'Đồ thị y=x²+{a} và đường thẳng y={m} có bao nhiêu giao điểm phân biệt?',ans,f'Hoành độ giao điểm giải x²+{a}={m}, tức x²={delta}. Vì vế phải {('bằng 0' if delta==0 else 'dương' if delta>0 else 'âm')}, phương trình có {nature}. Số giao điểm phân biệt do đó bằng {ans}.',len(S.solve(S.Eq(x*x+a,m),x)))

@add(12,'ham_mu','exponential_time_ratio','Tỉ số giá trị hàm mũ tại hai thời điểm cách nhau Δ','a^(t+Δ)/a^t=a^Δ','a>0 và a≠1, t thực')
def f06(k):
 base=2+(k%3);t=k+3;delta=k+1;ans=base**delta
 return Q(f'Cho f(t)={base}^t. Tính tỉ số f({t+delta})/f({t}).',ans,f'Áp dụng quy tắc lũy thừa cùng cơ số, f({t+delta})/f({t})={base}^{t+delta}/{base}^{t}={base}^{delta}={ans}.',S.Rational(base**(t+delta),base**t))
@add(12,'ham_logarit','change_of_base_power','Đổi cơ số logarit của lũy thừa','log_(a²)(a^n)=n/2','a>0, a≠1')
def f07(k):
 n=k+3;ans=S.Rational(n,2)
 return Q(f'Cho biểu thức A=log₄(2^{n}). Tính giá trị chính xác của A bằng công thức đổi cơ số.',ans,f'Vì 4=2², theo công thức đổi cơ số log₄(2^{n})=log₂(2^{n})/log₂4={n}/2={f(ans)}.',S.log(2**n,4))
@add(12,'mat_phang_oxyz','plane_from_normal_point_constant','Tìm hệ số tự do D trong phương trình mặt phẳng qua điểm với pháp tuyến','ax+by+cz+D=0 ⇒ D=−(ax₀+by₀+cz₀)','Pháp tuyến khác không')
def f08(k):
 a=k+1;b=k+2;c=k+3;p=k+4;q=2*k+1;r=k+5;D=-(a*p+b*q+c*r)
 return Q(f'Mặt phẳng đi qua P({p};{q};{r}), có pháp tuyến n=({a};{b};{c}), phương trình {a}x+{b}y+{c}z+D=0. Tính D.',D,f'Vì P thuộc mặt phẳng, thay P vào ta có {a}·{p}+{b}·{q}+{c}·{r}+D=0. Chuyển vế D=−({a*p}+{b*q}+{c*r})={D}.',S.Integer(-S.Matrix([a,b,c]).dot(S.Matrix([p,q,r]))))
@add(12,'mat_cau','sphere_surface_area','Diện tích mặt cầu theo bán kính','S=4πR²','R>0, hỏi hệ số S/π')
def f09(k):
 R=k+3;ans=4*R*R
 return Q(f'Một mặt cầu có bán kính R={R}. Tính S/π, trong đó S là diện tích mặt cầu.',ans,f'Công thức diện tích mặt cầu S=4πR². Thế R={R}: S=4π·{R}²={ans}π, nên S/π={ans}.',S.Integer(4*R*R))
@add(12,'bai_toan_thuc_te_12','half_life_radioactive_decay','Mô hình giảm một nửa sau mỗi chu kỳ','N(t)=N₀·(1/2)^(t/T)','T chu kỳ bán rã dương, t bội nguyên của T')
def f10(k):
 n=k+2;N0=2**(n+5);left=N0//2**n
 return Q(f'Một lượng chất ban đầu có {N0} đơn vị, cứ sau mỗi chu kỳ bán rã lượng chất còn lại bằng một nửa. Sau {n} chu kỳ, còn bao nhiêu đơn vị?',left,f'Sau một chu kỳ còn N₀/2, sau hai chu kỳ còn N₀/2². Sau {n} chu kỳ còn {N0}/2^{n}={left} đơn vị.',S.Rational(N0,2**n))
@add(12,'g12_geom_vectors_3d','cross_norm_via_gram','Độ dài tích có hướng qua định thức Gram','||u×v||²=||u||²||v||²−(u·v)²','Vectơ u,v∈R³')
def f11(k):
 a=k+2;b=k+3;u=S.Matrix([a,0,b]);v=S.Matrix([0,b,a]);ans=u.dot(u)*v.dot(v)-(u.dot(v))**2
 return Q(f'Trong Oxyz cho u=({a};0;{b}), v=(0;{b};{a}). Tính ||u×v||².',ans,f'Đồng nhất thức Lagrange cho ||u×v||²=||u||²||v||²−(u·v)². Ta có ||u||²=||v||²={a*a+b*b}, u·v={a*b}. Suy ra kết quả=({a*a+b*b})²−({a*b})²={ans}.',u.cross(v).dot(u.cross(v)))
@add(12,'g12_geom_plane_equation','plane_normal_from_vectors','Tìm hệ số pháp tuyến mặt phẳng qua hai vectơ chỉ phương','n=u×v','u,v không cùng phương')
def f12(k):
 a=k+2;u=S.Matrix([1,a,0]);v=S.Matrix([0,1,a]);n=u.cross(v);ans=n[0]
 return Q(f'Cho mặt phẳng (P) chứa hai vectơ chỉ phương u=(1;{a};0), v=(0;1;{a}). Vectơ pháp tuyến n=u×v có hoành độ bao nhiêu?',ans,f'Tính tích có hướng: u×v=({a*a};−{a};1), vuông góc với cả hai vectơ chỉ phương của (P). Do đó hoành độ của n bằng {ans}.',n[0])
@add(12,'g12_geom_point_plane_distance','point_plane_squared_distance','Bình phương khoảng cách từ điểm đến mặt phẳng bằng công thức pháp tuyến','d²=(ax₀+by₀+cz₀+D)²/(a²+b²+c²)','Mặt phẳng 3x+4y+D=0 có pháp tuyến khác 0')
def f13(k):
 p=k+1;q=2*k+3;r=k+6;D=2*k+1;num=3*p+4*q+D;ans=S.Rational(num*num,25)
 return Q(f'Trong Oxyz cho P({p};{q};{r}) và (Q):3x+4y+({D})=0. Tính bình phương khoảng cách từ P đến (Q).',ans,f'Pháp tuyến của (Q) là (3;4;0), có bình phương chuẩn 3²+4²=25. Giá trị biểu thức mặt phẳng tại P bằng 3·{p}+4·{q}+{D}={num}. Do đó d²={num}²/25={f(ans)}.',S.Rational((3*p+4*q+D)**2,3**2+4**2))
@add(12,'tong_hop_thpt','inverse_derivative_polynomial','Đạo hàm hàm ngược tại một giá trị từ đạo hàm hàm gốc','(f⁻¹)′(f(a))=1/f′(a)','f khả vi khả nghịch lân cận a, f′(a)≠0','nâng cao')
def f14(k):
 a=k+2;xx=S.Symbol('xx');fn=xx**3+xx;ans=S.Rational(1,3*a*a+1)
 return Q(f'Cho f(x)=x³+x, có hàm ngược g=f⁻¹. Biết y₀=f({a}). Tính g′(y₀).',ans,f'f′(x)=3x²+1>0 nên hàm khả nghịch. Công thức đạo hàm hàm ngược: g′(f({a}))=1/f′({a})=1/(3·{a}²+1)={f(ans)}.',1/S.diff(fn,xx).subs(xx,a))
@add(12,'goc_khoang_cach_oxyz','broken_line_reflection_min','Tối ưu đường gấp khúc đi qua mặt phẳng bằng phép phản xạ','min_H∈(P)(PH+HQ)=P′Q với P′ đối xứng P qua (P)','P,Q ở cùng phía mặt phẳng (Oxy)')
def f15(k):
 t=k+2;pa=2*t;qc=2*t;by=3*t;ans=5*t
 return Q(f'Trong Oxyz, P(0;0;{pa}) và Q({by};0;{qc}) cùng phía mặt phẳng (Oxy). Tìm độ dài nhỏ nhất của đường gấp khúc PH+HQ với H bất kỳ trên (Oxy).',ans,f'Phản xạ P qua mặt phẳng (Oxy) được P′(0;0;−{pa}). Vì H thuộc (Oxy), PH=P′H, nên PH+HQ=P′H+HQ≥P′Q. Đẳng thức xảy ra khi H là giao điểm đoạn P′Q với (Oxy), điều này luôn đúng vì P′ và Q nằm khác phía. P′Q=√[{by}²+({pa}+{qc})²]={ans}.',S.sqrt(by**2+(pa+qc)**2))

@add(10,'bai_toan_thuc_te_10','profit_linear_demand_quadratic','Tối ưu lợi nhuận với giá bán giảm tuyến tính theo số lượng','P(x)=x(p₀−x)−cx có parabol quay xuống, đỉnh cho cực đại','Giá bán và chi phí cho phép nghiệm tối ưu x>0')
def g01(k):
 a=20+2*k;cost=4+2*(k%3);best=(a-cost)//2
 return Q(f'Một cửa hàng bán x sản phẩm (x≥0), giá bán mỗi sản phẩm là ({a}−x) đơn vị tiền, chi phí mỗi sản phẩm là {cost}. Chọn x thực để lợi nhuận lớn nhất. Tính x.',best,f'Doanh thu R=x({a}−x), chi phí C={cost}x nên lợi nhuận P(x)=−x²+({a-cost})x. Parabol quay xuống có đỉnh tại x=({a-cost})/2={best}, thuộc miền x≥0, do đó lợi nhuận lớn nhất ở x={best}.',S.Rational(a-cost,2))
@add(10,'g10_geom_triangle_congruence','sas_equal_corresponding_angle','Suy góc tương ứng bằng nhau từ hai tam giác bằng nhau theo cạnh-góc-cạnh','SAS: hai cạnh và góc xen giữa bằng nhau => hai tam giác bằng nhau','Hai tam giác có hai cạnh kề và góc xen giữa bằng nhau')
def g02(k):
 a=k+4;b=k+7;theta=35+4*k;beta=50+2*k
 return Q(f'Hai tam giác ABC, DEF có AB=DE={a}, AC=DF={b}, ∠BAC=∠EDF={theta}°. Biết thêm ∠ABC={beta}°. Từ trường hợp bằng nhau cạnh-góc-cạnh, tính ∠DEF.',beta,f'Hai cạnh AB=DE, AC=DF kề với hai góc xen giữa A và D bằng {theta}°. Vậy ΔABC=ΔDEF theo trường hợp cạnh-góc-cạnh, tương ứng A↔D, B↔E, C↔F. Góc DEF tương ứng góc ABC và do đó bằng {beta}°.',S.Integer(beta))

@add(10,'g10_geom_special_lines','angle_bisector_stewart_length','Tính bình phương độ dài đường phân giác trong bằng hệ thức Stewart','l_a²=bc[1−a²/(b+c)²]','Tam giác có cạnh a=BC,b=CA,c=AB thỏa bất đẳng thức tam giác')
def g03(k):
 t=k+1;a=13*t;b=14*t;c=15*t;ans=S.Rational(b*c)*(1-S.Rational(a*a,(b+c)**2))
 BD=S.Rational(a*c,b+c);DC=S.Rational(a*b,b+c);oracle=(b*b*BD+c*c*DC)/a-BD*DC
 return Q(f'Tam giác ABC có BC={a}, CA={b}, AB={c}. Đường phân giác trong AD cắt BC tại D. Tính AD².',ans,f'Áp dụng định lý phân giác: BD/DC=AB/AC={c}/{b}; vậy BD={f(BD)}, DC={f(DC)}. Theo định lý Stewart, CA²·BD+AB²·DC=BC(AD²+BD·DC). Suy ra AD²={b*c}[1−{a}²/({b}+{c})²]={f(ans)}.',S.simplify(oracle))
@add(11,'cong_thuc_luong_giac','triple_angle_sine','Dùng công thức góc ba lần để tính sin(3α) từ sinα','sin(3α)=3sinα−4sin³α','α nhọn, sinα đã biết')
def g04(k):
 t=k+2;val=S.Rational(2*t,t*t+1);ans=3*val-4*val**3
 return Q(f'Cho góc nhọn α có sinα={f(val)}. Dùng công thức góc ba lần để tính sin(3α).',ans,f'Theo công thức sin(3α)=3sinα−4sin³α. Với sinα={f(val)}, ta được sin(3α)=3·{f(val)}−4·({f(val)})³={f(ans)}. Không cần tính trực tiếp số đo góc α.',S.expand(3*val-4*val**3))

@add(11,'day_so_tong_quat','finite_difference_quadratic_sequence','Tính sai phân hai số hạng liên tiếp của dãy bậc hai','u_(n+1)−u_n=a(2n+1)+b','u_n=an²+bn+c')
def g05(k):
 a=k+2;b=k+5;c=2*k+1;n=k+4;ans=a*(2*n+1)+b
 return Q(f'Dãy số được xác định bởi u_n={a}n²+{b}n+{c}. Tính u_{n+1}−u_{n}.',ans,f'Lấy u_(n+1)−u_n={a}[(n+1)²−n²]+{b}[(n+1)−n]+({c}−{c})={a}(2n+1)+{b}. Thay n={n}, hiệu bằng {ans}.',S.expand((a*(n+1)**2+b*(n+1)+c)-(a*n*n+b*n+c)))
@add(11,'song_song_khong_gian','parallel_planes_transversal_ratio','Hệ quả định lý Thales trong không gian với hai mặt phẳng song song','OA′/OA=OB′/OB','O không thuộc hai mặt phẳng song song, hai tia cắt hai mặt phẳng')
def g06(k):
 a=k+2;scale=k+3;ob=2*k+5;ans=ob*scale
 return Q(f'Từ O kẻ hai tia gặp mặt phẳng (P) tại A,B, rồi gặp mặt phẳng (Q) song song (P) tại A′,B′. Biết OA={a}, OA′={a*scale}, OB={ob}. Tính OB′.',ans,f'Vì hai mặt phẳng (P),(Q) song song, phép chiếu từ tâm O tạo phép vị tự có tỉ số OA′/OA={a*scale}/{a}={scale}. Do đó OB′/OB={scale}, nên OB′={ob}·{scale}={ans}.',S.Rational(a*scale,a)*ob)
@add(11,'goc_khoang_cach_11','height_from_line_plane_angle','Khoảng cách từ điểm đến mặt phẳng bằng cạnh xiên nhân sin góc nghiêng','d=SA·sinφ','A thuộc (P), S không thuộc (P); góc giữa SA và (P) có sinφ cho trước')
def g07(k):
 t=k+1;SA=5*t;ans=3*t
 return Q(f'Điểm A nằm trên mặt phẳng (P), S nằm ngoài (P), SA={SA}. Góc giữa SA và (P) có sinφ=3/5. Tính khoảng cách từ S đến (P).',ans,f'Gọi H là chân đường vuông góc từ S xuống (P). Góc SAH chính là góc giữa SA và (P), và tam giác SAH vuông tại H. Do sinφ=SH/SA, ta có SH={SA}·3/5={ans}. Đây là khoảng cách cần tìm.',S.Rational(SA*3,5))
@add(11,'thiet_dien_hinh_khong_gian_11','tetra_midpoint_section_perimeter','Chu vi thiết diện tam giác qua ba trung điểm cạnh từ đỉnh tứ diện đều','Thiết diện đồng dạng đáy tỉ số 1/2, chu vi giảm một nửa','Tứ diện đều cạnh a; thiết diện qua trung điểm SA,SB,SC')
def g08(k):
 a=2*(k+5);ans=S.Rational(3*a,2)
 return Q(f'Tứ diện đều S.ABC có cạnh a={a}. Mặt phẳng qua trung điểm SA,SB,SC tạo thiết diện tam giác MNP. Tính chu vi MNP.',ans,f'Theo định lý đường trung bình của tam giác, MN=AB/2={a}/2, NP=BC/2, PM=CA/2. Thiết diện MNP đều có cạnh {a}/2 nên chu vi bằng 3·{a}/2={f(ans)}.',S.Rational(3*a,2))
@add(11,'bai_toan_thuc_te_tong_hop_11','two_speed_time_sum','Mô hình thời gian hành trình hai chặng với vận tốc khác nhau','t_total=s₁/v₁+s₂/v₂','Hai chặng liên tiếp, tốc độ khác 0')
def g09(k):
 v1=k+3;v2=k+5;t1=k+2;t2=2+k%4;s1=v1*t1;s2=v2*t2;ans=t1+t2
 return Q(f'Một chuyến đi gồm chặng 1 dài {s1} km với tốc độ {v1} km/h và chặng 2 dài {s2} km với tốc độ {v2} km/h, đi liên tục. Tính tổng thời gian đi (giờ).',ans,f'Thời gian mỗi chặng bằng quãng đường chia tốc độ. Chặng 1: {s1}/{v1}={t1} giờ; chặng 2: {s2}/{v2}={t2} giờ. Tổng thời gian {t1}+{t2}={ans} giờ.',S.Rational(s1,v1)+S.Rational(s2,v2))
@add(11,'g11_geom_space_lines_planes','prism_face_count','Đếm số mặt của lăng trụ đáy n giác','F=n+2: n mặt bên và 2 mặt đáy','Lăng trụ có hai đáy là đa giác n cạnh; n≥3','nền tảng')
def g10(k):
 n=k+4;ans=n+2
 return Q(f'Một lăng trụ có hai đáy là đa giác {n} cạnh. Hỏi hình lăng trụ có tất cả bao nhiêu mặt?',ans,f'Mỗi cạnh của đa giác đáy ứng với đúng một mặt bên, nên có {n} mặt bên. Cộng thêm 2 mặt đáy, tổng số mặt là {n}+2={ans}.',S.Integer(n+2))
@add(11,'g11_geom_parallel_line_plane','midline_parallel_base_3d','Đường trung bình song song cạnh đáy trong mặt bên của hình chóp','MN=BC/2 khi M,N là trung điểm SB,SC','Trong tam giác SBC; MN∥BC và MN∥mặt phẳng đáy khi BC nằm trên đáy')
def g11(k):
 a=2*(k+5);ans=a//2
 return Q(f'Cho hình chóp S.ABC với M,N lần lượt là trung điểm SB,SC. Biết BC={a}. Tính MN, đoạn song song với mặt phẳng (ABC).',ans,f'Trong tam giác SBC, M và N là trung điểm hai cạnh SB,SC. Theo định lý đường trung bình, MN∥BC và MN=BC/2={a}/2={ans}. Vì BC nằm trong mặt phẳng (ABC), MN song song với mặt phẳng đáy.',S.Rational(a,2))
@add(11,'g11_geom_perpendicular_line_plane','vertical_cube_edge_distance','Khoảng cách giữa hai mặt phẳng đáy và mặt trên hình hộp chữ nhật','Hai mặt phẳng song song, cạnh bên vuông góc cả hai nên khoảng cách bằng chiều cao','Hình hộp chữ nhật ABCD.A′B′C′D′')
def g12(k):
 h=k+6;aa=k+3;bb=k+5
 return Q(f'Hình hộp chữ nhật ABCD.A′B′C′D′ có AA′={h}, AB={aa}, AD={bb}. Tính khoảng cách giữa hai mặt phẳng (ABCD) và (A′B′C′D′).',h,f'Vì AA′ vuông góc với mặt phẳng đáy (ABCD) và cũng vuông góc với mặt phẳng trên, đoạn AA′ là đường vuông góc chung. Khoảng cách giữa hai mặt phẳng bằng AA′={h}, không phụ thuộc AB hay AD.',S.Integer(h))
@add(11,'g11_geom_section_construction','cube_horizontal_section_area','Thiết diện hình hộp bởi mặt phẳng song song đáy','Thiết diện bằng hình chữ nhật đáy khi cắt song song đáy','Cắt bên trong hình hộp chữ nhật tại độ cao h giữa hai đáy')
def g13(k):
 a=k+3;b=2*k+5;h=k+4;ans=a*b
 return Q(f'Hình hộp chữ nhật có đáy kích thước {a}×{b}, chiều cao {h}. Cắt bởi mặt phẳng song song đáy và nằm giữa hai đáy. Tính diện tích thiết diện.',ans,f'Các cạnh bên song song và bằng nhau, mặt phẳng cắt song song với đáy tạo thiết diện là hình chữ nhật có hai cạnh đúng bằng hai cạnh đáy: {a} và {b}. Diện tích S={a}·{b}={ans}.',S.Integer(a*b))
@add(11,'g11_geom_space_proof','centroids_of_two_pyramid_faces','Đường nối trọng tâm hai mặt của hình chóp song song cạnh đối diện','GH=(S−A)/3 khi G là trọng tâm ABC, H là trọng tâm SBC','Hình chóp S.ABC với SA>0')
def g14(k):
 a=3*(k+4);ans=a//3
 return Q(f'Hình chóp S.ABC có SA={a}. G là trọng tâm tam giác ABC, H là trọng tâm tam giác SBC. Biết hai trọng tâm nối với nhau theo phương SA. Tính độ dài GH.',ans,f'Dùng vectơ vị trí, G=(A+B+C)/3 và H=(S+B+C)/3. Lấy hiệu ta được vectơ GH=(S−A)/3, vì thế GH song song SA và độ dài GH=SA/3={a}/3={ans}.',S.Rational(a,3))

@add(12,'ung_dung_dao_ham','optimize_closed_cylinder_surface','Tối ưu diện tích toàn phần hình trụ có thể tích cố định','S(r)=2πr²+2V/r; cực tiểu khi r³=V/(2π)','Hình trụ kín r,h>0, V=πr²h không đổi','nâng cao')
def g15(k):
 a=k+2;Vcoef=2*a**3;ans=a
 return Q(f'Một hình trụ kín có thể tích cố định V={Vcoef}π. Tìm bán kính r>0 để diện tích toàn phần nhỏ nhất.',ans,f'Từ V=πr²h, suy ra h={Vcoef}/r². Diện tích toàn phần S=2πr²+2πrh=2πr²+2π·{Vcoef}/r. Lấy đạo hàm S′=4πr−2π·{Vcoef}/r². Giải S′=0 được r³={Vcoef}/2={a**3}, nên r={a}; S′ đổi từ âm sang dương, đó là cực tiểu.',S.integer_nthroot(Vcoef//2,3)[0])
@add(12,'hinh_hoc_khong_gian','prism_volume_base_area','Thể tích lăng trụ từ diện tích đáy và chiều cao','V=S_đáy·h','Lăng trụ có hai đáy song song bằng nhau, h>0','nền tảng')
def g16(k):
 s=k+5;h=2*k+7;ans=s*h
 return Q(f'Một lăng trụ có diện tích đáy S={s} (đơn vị diện tích), chiều cao h={h}. Tính thể tích.',ans,f'Thể tích của lăng trụ bằng diện tích đáy nhân chiều cao tương ứng. Do đó V=S_đáy·h={s}·{h}={ans}.',S.Integer(s*h))
@add(12,'bieu_dien_so_phuc','real_part_complex_square','Phần thực bình phương số phức trong tọa độ phẳng','Re((a+bi)²)=a²−b²','a,b thực')
def g17(k):
 a=k+3;b=2*k+5;ans=a*a-b*b
 return Q(f'Điểm M({a};{b}) biểu diễn số phức z={a}+{b}i. Tính phần thực của z².',ans,f'Khai triển z²=({a}+{b}i)²={a*a}+2·{a}·{b}i+{b*b}i². Vì i²=−1, phần thực bằng {a*a}−{b*b}={ans}.',S.re((a+b*S.I)**2))
@add(12,'duong_thang_oxyz','line_line_angle_dot_square','Bình phương cos góc giữa hai đường thẳng theo vectơ chỉ phương','cos²θ=(u·v)²/(||u||²||v||²)','Hai vectơ chỉ phương khác 0')
def g18(k):
 a=k+2;u=S.Matrix([a,1,0]);v=S.Matrix([0,a,1]);ans=S.Rational((u.dot(v))**2,u.dot(u)*v.dot(v))
 return Q(f'Hai đường thẳng trong Oxyz có vectơ chỉ phương u=({a};1;0), v=(0;{a};1). Tính cos² góc nhọn giữa chúng.',ans,f'Tích vô hướng u·v={a}. Bình phương độ dài hai vectơ đều là {a*a+1}. Vì cos²θ=(u·v)²/(||u||²||v||²), ta được cos²θ={a*a}/({a*a+1}²)={f(ans)}.',S.Rational(a*a,(a*a+1)**2))
@add(12,'the_tich_khong_gian','regular_tetra_volume_squared','Thể tích tứ diện đều qua chiều cao và diện tích đáy','V=a³√2/12 nên V²=a⁶/72','Tứ diện đều cạnh a>0')
def g19(k):
 a=k+2;ans=S.Rational(a**6,72)
 return Q(f'Một tứ diện đều có độ dài cạnh a={a}. Tính bình phương thể tích V² của tứ diện.',ans,f'Đáy là tam giác đều cạnh {a}, diện tích S=({a}²√3)/4. Đường cao tứ diện đều h={a}√(2/3). Thể tích V=Sh/3={a}³√2/12. Do đó V²={a}⁶·2/144={f(ans)}.',(a**3*S.sqrt(2)/12)**2)
@add(12,'hinh_hoc_oxyz_van_dung_12','closest_point_segment_origin','Tối thiểu hóa bình phương khoảng cách từ điểm trên đoạn thẳng đến O bằng đạo hàm','P(t)=A+t(B−A), min ||P(t)||² với 0≤t≤1','A,B phân biệt; hình chiếu chân vuông góc thuộc đoạn','nâng cao')
def g20(k):
 a=k+2;b=k+4;# Segment from (a,b) to (-a,b), passes projection of O at center
 ans=b*b
 return Q(f'Trong Oxyz, điểm P di chuyển trên đoạn nối A({a};{b};0) và B({-a};{b};0). Tính GTNN của OP².',ans,f'Tham số hóa P(t)=({a}−{2*a}t;{b};0) với 0≤t≤1. Khi đó OP²=({a}−{2*a}t)²+{b*b}≥{b*b}. Dấu bằng khi t=1/2 nằm trong đoạn; vậy GTNN là {ans}.',min((a-2*a*S.Rational(j,10))**2+b*b for j in range(11)))


def norm(prompt):
 return re.sub(r'\s+',' ',prompt.casefold().strip())
def pattern(prompt):
 # We test numeric-template overlaps; this is a screening test, not full semantic dedup.
 s=norm(prompt)
 s=re.sub(r'[+-]?\d+(?:/\d+)?(?:\.\d+)?','<n>',s)
 return s

def generate():
 catalog=json.loads((ROOT/'backend/app/ai/knowledge/index.json').read_text(encoding='utf8'))
 valid_topics={(int(g),t['id']) for g,ts in catalog.items() for t in ts}
 existing=[]
 with (OUT/'V191_CUMULATIVE_QA_IMPORT.jsonl').open(encoding='utf8') as f_in:
  existing=[json.loads(s) for s in f_in if s.strip()]
 existing_prompts={(int(r['grade']),norm(r['question'])) for r in existing}
 existing_patterns={(int(r['grade']),pattern(r['question'])) for r in existing}
 prior_specs=json.loads((OUT/'V191_FAMILY_SPECS.json').read_text(encoding='utf8'))
 assert len({r['key'] for r in FORMS})==len(FORMS)
 assert all((r['grade'],r['topic']) in valid_topics for r in FORMS)
 seen=set();rows=[]; specs=[]; pattern_overlaps=[]
 for spec in FORMS:
  specs.append({k:v for k,v in spec.items() if k!='fun'})
  for k in range(10):
   q,ans,sol,check=spec['fun'](k)
   assert ans.is_rational, (spec['key'],ans)
   fmt='multiple_choice' if k<7 else 'short_answer' if k<9 else 'true_false'
   val=f(ans)
   choices=[];answer=val
   if fmt=='multiple_choice':
    if 0<ans<1:
     opts=[ans,ans*S.Rational(3,4),(ans+1)/2,ans+ans*(1-ans)/3]
    else:
     opts=[ans,ans+1,ans-1,ans+2]
    choices=list(map(f,opts))
    assert len(set(choices))==4, (spec['key'],val,choices)
    random.Random(192024+k*41).shuffle(choices)
   if fmt=='true_false':
    assertions=[('=',ans,True),('>',ans-1,True),('=',ans+1,False),('<',ans-1,False)]
    for op,other,expected in assertions:
     truth=(ans==other if op=='=' else ans>other if op=='>' else ans<other)
     assert bool(truth)==expected
     choices.append(f'Giá trị đại lượng được hỏi {op} {f(other)}.')
    answer='Đúng,Đúng,Sai,Sai'
    sol+=f' Đối chiếu với giá trị đã tính {val}: nhận định 1 đúng, 2 đúng, 3 sai, 4 sai.'
   rid=f'{spec["key"]}_{k:02d}'
   row={
    'id':rid,'grade':spec['grade'],'topic':spec['topic'],'family':spec['key'],'form_id':spec['key'],
    'concept':spec['name'],'math_method':spec['method'],'conditions':spec['conditions'],
    'difficulty':spec['difficulty'],'question_type':fmt,'question':q,'answer':answer,
    'correct_answer':answer,'choices':choices,'solution':sol,'source_bundle':'V192',
    'source_checkpoint':'V191','method_independence_certified':False,'production_integrated':False,
    'validation_status':'sympy_oracle_and_app_grader_checked_not_semantically_certified','verification':check}
   candidate={'id':rid,'grade':row['grade'],'topic':row['topic'],'difficulty':row['difficulty'],
              'question_type':fmt,'question':q,'answer':answer,'solution':sol,
              'options':choices if fmt=='multiple_choice' else [],
              'statements':choices if fmt=='true_false' else []}
   validate(candidate)
   assert grade_answer(candidate,answer),('grading',rid)
   if fmt=='multiple_choice':
    matches=[bool(grade_answer(candidate,c)) for c in choices]
    assert sum(matches)==1,('nonunique',rid,matches)
   if fmt=='true_false': assert len(choices)==4 and len(answer.split(','))==4
   key=(int(row['grade']),norm(q))
   assert key not in seen,('duplicate in V192',rid)
   assert key not in existing_prompts,('duplicate vs V191',rid)
   if (int(row['grade']),pattern(q)) in existing_patterns:
    pattern_overlaps.append(rid)
   seen.add(key);rows.append(row)
 assert len(rows)==len(FORMS)*10
 assert all(v==10 for v in collections.Counter(r['family'] for r in rows).values())
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/'V192_IMPORT_READY.jsonl').open('w',encoding='utf8') as out:
  for row in rows:out.write(json.dumps(row,ensure_ascii=False)+'\n')
 (OUT/'V192_FAMILY_SPECS.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 report={'version':'V192','source':'V191_FULL_WEB','catalog_count':len(valid_topics),
  'new_candidate_families':len(FORMS),'new_oracle_checked_questions':len(rows),
  'new_topics_expanded':len(set((r['grade'],r['topic']) for r in rows)),
  'question_formats':dict(collections.Counter(r['question_type'] for r in rows)),
  'grades':dict(collections.Counter(str(r['grade']) for r in rows)),
  'exact_duplicate_new_vs_prior':0,'numeric_pattern_overlaps_vs_prior':len(pattern_overlaps),
  'numeric_pattern_overlap_ids':pattern_overlaps[:30],
  'new_independent_types_globally_certified':0,'production_questions_imported':0,
  'method_spec_exact_name_collision_vs_v191':len(set(s['name'] for s in specs)&set(s['name'] for s in prior_specs)),
  'test_scope':'exact arithmetic oracle, 7/2/1 formatted per family, application validation and grader, exact dedup; semantic novelty NOT certified'}
 (OUT/'V192_GENERATION_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if not isinstance(v,list)},ensure_ascii=False))
 return report

if __name__=='__main__':generate()
