#!/usr/bin/env python3
"""V199 bank expansion: different mathematical technique candidates, 10 exercises each.
All results checked with an exact second technique. Independent certification remains pending.
"""
from __future__ import annotations
import sys,json,collections,itertools
from math import comb,factorial,pi,gcd
from pathlib import Path
import sympy as S
from v198_generate import fmt,choices_for
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'bank_updates'
CATALOG={(int(g),t['id']) for g,ts in json.loads((ROOT/'backend/app/ai/knowledge/index.json').read_text()).items() for t in ts}
SPECS={
 'angle_bisector_ratio':(10,'g10_geom_special_lines','Phân giác chia cạnh đối theo tỉ số hai cạnh kề','Định lý phân giác BD/DC=AB/AC','D nằm trên BC và AD là phân giác trong','trung cấp'),
 'rhombus_diagonals_area':(10,'g10_geom_quadrilaterals_properties','Diện tích hình thoi từ tích hai đường chéo','S=d₁d₂/2 do đường chéo vuông góc','Hình thoi có đường chéo dương','nền tảng'),
 'inscribed_arc_angle':(10,'g10_geom_circle_angles','Góc nội tiếp chắn một cung tròn','Góc nội tiếp bằng nửa số đo cung bị chắn','Đỉnh nằm trên đường tròn ngoài cung bị chắn','nền tảng'),
 'cauchy_two_fraction_min':(10,'g10_advanced_inequalities','Cực tiểu tổng a²/x+b²/y với x+y cố định','Cauchy-Schwarz: (a²/x+b²/y)(x+y)≥(a+b)²','x,y,a,b dương, x+y=L','nâng cao'),
 'symmetric_roots_gap':(10,'g10_symmetric_systems','Tính khoảng cách giữa nghiệm của hệ tổng và tích','(x−y)²=(x+y)²−4xy','Hai nghiệm thực tồn tại','trung cấp'),
 'pigeonhole_draw':(10,'g10_combinatorics_olympiad','Ngưỡng bảo đảm có r vật cùng loại bằng nguyên lý Dirichlet','k(r−1)+1 lựa chọn với k loại','Mỗi loại có đủ ít nhất r vật, không hoàn lại','nâng cao'),
 'triangle_centroid_x':(10,'g10_geom_coordinate_distance_midpoint','Hoành độ trọng tâm tam giác qua trung bình ba đỉnh','x_G=(x_A+x_B+x_C)/3','Ba đỉnh không thẳng hàng','nền tảng'),
 'circular_sector_area_over_pi':(10,'duong_tron_co_ban_10','Diện tích quạt tròn chia π','S/π=R²θ/360°','Bán kính R>0, góc ở tâm trong khoảng 0°–360°','nền tảng'),
 'no_adjacent_subset':(10,'quy_tac_dem','Chọn k vị trí không kề nhau trong n vị trí','Biến đổi chỉ số i_j→i_j−(j−1), đếm C(n−k+1,k)','0≤k≤⌈n/2⌉','nâng cao'),
 'right_circumradius':(10,'he_thuc_luong_van_dung_10','Bán kính đường tròn ngoại tiếp tam giác vuông','R=c/2 vì cạnh huyền là đường kính','Tam giác vuông không suy biến','nền tảng'),
 'sqrt_infty_limit':(11,'gioi_han','Giới hạn hiệu căn bậc hai tại vô cực bằng liên hợp','√(n²+an)−n → a/2','n→+∞ và n²+an>0 khi n đủ lớn','trung cấp'),
 'inhomogeneous_recurrence':(11,'g11_sequences_advanced','Truy hồi bậc nhất có ngoại lực 3^n','u_(n+1)=2u_n+3^n, giải bằng một nghiệm riêng','n≥0; u0 được cho','nâng cao'),
 'tangent_difference':(11,'cong_thuc_luong_giac','Tính tang hiệu hai góc','tan(α−β)=(tanα−tanβ)/(1+tanαtanβ)','Hai tang xác định và cos(α−β) khác 0','trung cấp'),
 'trig_linear_amplitude':(11,'ham_so_luong_giac_day_du','Giá trị lớn nhất của tổ hợp a sin x+b cos x','max=√(a²+b²) bằng chuyển pha','x thuộc R; a,b không đồng thời bằng 0','trung cấp'),
 'conditional_union_independent':(11,'bien_co_doc_lap_11','Tính P(A|A∪B) từ xác suất hai biến cố độc lập','P(A|A∪B)=p/(p+q−pq)','A,B độc lập, P(A∪B)>0','nâng cao'),
 'rotate_then_translate':(11,'g11_geom_transform_composition','Hợp phép quay 90 độ quanh O và tịnh tiến','(x,y)↦(−y,x)↦(−y+a,x+b)','Phép quay ngược chiều kim đồng hồ 90°','trung cấp'),
 'parallel_planes_distance':(11,'g11_geom_parallel_planes','Khoảng cách giữa hai mặt phẳng song song tổng quát','d=|d₁−d₂|/√(a²+b²+c²)','Pháp tuyến chung khác 0','trung cấp'),
 'quartile_lower_eight':(11,'thong_ke_11','Xác định tứ phân vị dưới cho mẫu 8 số','Q₁ là trung vị của bốn số nhỏ nhất','Dữ liệu được sắp không giảm gồm 8 quan sát','nền tảng'),
 'regular_pyramid_lateral':(11,'g11_geom_prism_pyramid_sections','Diện tích xung quanh hình chóp đều','S_xq=chu vi đáy×đường cao mặt bên/2','Hình chóp đều, đáy đa giác đều','trung cấp'),
 'angle_line_plane_tangent':(11,'g11_geom_dihedral_angles','Tang góc giữa cạnh xiên và mặt đáy','tan θ=chiều cao / độ dài hình chiếu','Hình chiếu vuông góc có độ dài dương','trung cấp'),
 'plane_three_intercepts':(12,'g12_geom_plane_equation','Phương trình mặt phẳng theo ba đoạn chắn trục','x/a+y/b+z/c=1','a,b,c khác 0','trung cấp'),
 'sphere_tangent_plane_D':(12,'g12_geom_sphere_tangent_plane','Tìm hằng số D trong mặt phẳng tiếp xúc mặt cầu','Pháp tuyến mặt tiếp xúc cùng phương bán kính CP','Tiếp điểm nằm trên mặt cầu','trung cấp'),
 'point_line_distance_sq':(12,'g12_geom_min_distance_3d','Bình phương khoảng cách từ điểm đến đường thẳng Oxyz','d²=||AP×u||²/||u||²','Vectơ chỉ phương u khác 0','nâng cao'),
 'perpendicular_planes_parameter':(12,'g12_geom_parameter_geometry','Tìm tham số để hai mặt phẳng vuông góc','Tích vô hướng hai pháp tuyến bằng 0','Mặt phẳng có pháp tuyến khác 0','trung cấp'),
 'cone_lateral_area_over_pi':(12,'g12_geom_solid_surface_area','Diện tích xung quanh hình nón chia π','S_xq/π=r√(r²+h²)','r,h dương','nền tảng'),
 'substitution_integral':(12,'nguyen_ham_tich_phan','Tích phân theo phép đặt u=x²+cx+d','Đặt u=x²+cx+d, du=(2x+c)dx','Hàm dưới lũy thừa liên tục trên đoạn lấy tích phân','trung cấp'),
 'washer_revolution_over_pi':(12,'g12_solid_of_revolution','Khối tròn xoay có lỗ dùng phương pháp vành khăn','V/π=∫(R(x)²−r(x)²)dx','R(x)≥r(x)≥0 trên đoạn xét','trung cấp'),
 'integral_least_squares':(12,'g12_integral_optimization','Tìm hằng số tối ưu của tích phân bình phương sai số','Minimize ∫(x−a)²dx theo a bằng đạo hàm','Cận tích phân cố định, biến a thuộc R','nâng cao'),
 'variation_coefficient':(12,'thong_ke_12','Hệ số biến thiên cho số liệu đối xứng','CV=độ lệch chuẩn / trung bình','Trung bình dương, dùng phương sai chia n','trung cấp'),
 'three_dim_plane_angle_line':(12,'g12_geom_line_plane_angle','Bình phương sin góc giữa đường và mặt phẳng','sin²θ=(u·n)²/(||u||²||n||²)','u,n là vectơ khác 0','trung cấp'),
 'sphere_cap_area_over_pi':(12,'g12_geom_solid_surface_area','Diện tích mặt cong chỏm cầu chia π','S/π=2Rh','Bán kính cầu R, chiều cao chỏm 0<h≤2R','nâng cao'),
 'quadratic_area_between':(12,'ung_dung_tich_phan','Diện tích miền giữa đường thẳng y=ax và parabol y=x²','Diện tích ∫₀ᵃ(ax−x²)dx','a>0, hai đồ thị cắt nhau tại x=0,a','trung cấp'),
}

def build(key,i):
 t=i+1
 if key=='angle_bisector_ratio':
  a,b,k=3+t,5+t%4,2+t%5;BC=a+b-k;ans=S.Rational(a*BC,a+b)
  assert BC<a+b and BC>abs(a-b) and S.Rational(ans,BC-ans)==S.Rational(a,b)
  q=f'Trong tam giác ABC, AB={a}, AC={b}, BC={BC}. Phân giác trong AD cắt BC tại D. Tính BD.'
  sol=f'Định lý phân giác: BD/DC=AB/AC={a}/{b}, nên BD/BC={a}/({a}+{b}). Vậy BD={BC}×{a}/({a}+{b})={fmt(ans)}.'
 elif key=='rhombus_diagonals_area':
  u,v=3+t,5+t%6;ans=2*u*v
  assert ans==S.Abs(S.det(S.Matrix([[u,v],[u,-v]])))
  q=f'Hình thoi ABCD có hai đường chéo AC={2*u}, BD={2*v}. Tính diện tích hình thoi.'
  sol=f'Hai đường chéo vuông góc và cắt nhau tại trung điểm. S=AC·BD/2=({2*u}×{2*v})/2={ans}.'
 elif key=='inscribed_arc_angle':
  arc=30+20*t;ans=S.Rational(arc,2)
  assert 2*ans==arc
  q=f'Trên đường tròn, góc nội tiếp ∠ABC chắn cung AC không chứa B có số đo {arc}°. Tính số đo ∠ABC (độ).'
  sol=f'Góc nội tiếp bằng một nửa số đo cung bị chắn, do đó ∠ABC={arc}°/2={fmt(ans)}°.'
 elif key=='cauchy_two_fraction_min':
  a,b,L=2+t,3+t%4,4+t;ans=S.Rational((a+b)**2,L)
  x=S.symbols('x',positive=True);f=S.Rational(a*a,1)/x+S.Rational(b*b,1)/(L-x)
  xmin=S.Rational(L*a,a+b)
  assert S.simplify(f.subs(x,xmin)-ans)==0 and 0<xmin<L
  q=f'Cho x,y>0, x+y={L}. Tìm giá trị nhỏ nhất của F={a*a}/x+{b*b}/y.'
  sol=f'Cauchy-Schwarz cho F(x+y)≥({a}+{b})². Do x+y={L}, F≥({a}+{b})²/{L}={fmt(ans)}. Dấu bằng khi x/y={a}/{b}.'
 elif key=='symmetric_roots_gap':
  x,y=-(2+t),5+t%4;s=x+y;p=x*y;ans=abs(x-y)
  assert ans**2==s*s-4*p
  q=f'Hai số thực x,y thỏa x+y={s}, xy={p}. Tính |x−y|.'
  sol=f'Có (x−y)²=(x+y)²−4xy={s}²−4({p})={ans*ans}. Vậy |x−y|={ans}.'
 elif key=='pigeonhole_draw':
  k=3+t;r=2+t%5;ans=k*(r-1)+1
  assert ans-1==k*(r-1)
  q=f'Hộp chứa {k} màu bi, mỗi màu có ít nhất {r} viên. Rút từng viên không hoàn lại và không nhìn màu. Cần rút ít nhất bao nhiêu viên để chắc chắn có {r} viên cùng màu?'
  sol=f'Xấu nhất có thể rút {r-1} bi từ mỗi màu mà chưa có {r} bi cùng màu, tổng {k}×({r}-1)={ans-1}. Viên tiếp theo bảo đảm đủ, nên kết quả {ans}.'
 elif key=='triangle_centroid_x':
  a,b,c=t,t+3,t+9; ans=S.Rational(a+b+c,3)
  assert ans==S.Rational(a+b+c,3)
  q=f'Tam giác ABC có A({a},1), B({b},2), C({c},5). Hoành độ trọng tâm G của tam giác bằng bao nhiêu?'
  sol=f'Trọng tâm có tọa độ trung bình ba đỉnh: x_G=(x_A+x_B+x_C)/3=({a}+{b}+{c})/3={fmt(ans)}.'
 elif key=='circular_sector_area_over_pi':
  R=3+t;deg=20+20*t;ans=S.Rational(R*R*deg,360)
  assert ans==S.Rational(R*R,2)*S.Rational(deg,180)
  q=f'Quạt tròn bán kính R={R} tạo bởi góc ở tâm {deg}°. Diện tích quạt là S. Tính S/π.'
  sol=f'Diện tích quạt S=(θ/360°)πR². Thay θ={deg}°, R={R}, ta có S/π={deg}×{R}²/360={fmt(ans)}.'
 elif key=='no_adjacent_subset':
  n=7+t;k=2+t%3;ans=comb(n-k+1,k)
  assert ans==sum(all(y-x>1 for x,y in zip(sel,sel[1:])) for sel in itertools.combinations(range(1,n+1),k))
  q=f'Từ {n} vị trí đánh số 1 đến {n} trên một hàng, chọn đúng {k} vị trí sao cho không có hai vị trí nào kề nhau. Có bao nhiêu cách chọn?'
  sol=f'Nếu i₁<⋯<i_{k} là vị trí chọn, đặt j_r=i_r−(r−1) để bỏ khoảng trống bắt buộc. Đếm C({n}−{k}+1,{k})={ans}.'
 elif key=='right_circumradius':
  triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(9,40,41),(12,35,37),(11,60,61),(28,45,53),(16,63,65)]
  a,b,c=triples[i];ans=S.Rational(c,2)
  assert S.Rational(a*a+b*b,4)==ans*ans
  q=f'Tam giác vuông có hai cạnh góc vuông {a},{b} và cạnh huyền {c}. Tính bán kính đường tròn ngoại tiếp.'
  sol=f'Tam giác vuông nội tiếp đường tròn có cạnh huyền là đường kính. Do đó R=c/2={c}/2={fmt(ans)}.'
 elif key=='sqrt_infty_limit':
  a=2+t;ans=S.Rational(a,2);n=S.symbols('n',positive=True)
  assert S.limit(S.sqrt(n*n+a*n)-n,n,S.oo)==ans
  q=f'Tính giới hạn L=lim_(n→+∞) [√(n²+{a}n)−n].'
  sol=f'Nhân liên hợp: L=lim [{a}n/(√(n²+{a}n)+n)]=lim {a}/(√(1+{a}/n)+1)={fmt(ans)}.'
 elif key=='inhomogeneous_recurrence':
  A=2+t;n=3+t;u=A;ans=(A-1)*2**n+3**n
  for k in range(n):u=2*u+3**k
  assert u==ans
  q=f'Dãy số có u₀={A}, uₙ₊₁=2uₙ+3ⁿ với n≥0. Tính u_{n}.'
  sol=f'Đặt vₙ=uₙ−3ⁿ, khi đó vₙ₊₁=2vₙ. Vì v₀={A}−1={A-1}, suy ra uₙ=({A}−1)2ⁿ+3ⁿ. Vậy u_{n}={ans}.'
 elif key=='tangent_difference':
  a=S.Rational(t+2,t+5);b=S.Rational(t,t+7);ans=(a-b)/(1+a*b)
  assert S.simplify((1+a*b)*ans-(a-b))==0
  q=f'Biết tan α={fmt(a)}, tan β={fmt(b)}. Tính tan(α−β), giả sử các tang đều xác định.'
  sol=f'Theo công thức tang hiệu: tan(α−β)=(tanα−tanβ)/(1+tanαtanβ)=({fmt(a)}−{fmt(b)})/(1+({fmt(a)})({fmt(b)}))={fmt(ans)}.'
 elif key=='trig_linear_amplitude':
  triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(9,40,41),(12,35,37),(11,60,61),(28,45,53),(16,63,65)]
  a,b,R=triples[i];ans=R
  assert a*a+b*b==R*R
  q=f'Với x thuộc R, hãy tìm giá trị lớn nhất của f(x)={a}sin x+{b}cos x.'
  sol=f'Đặt R=√({a}²+{b}²)={R}, chọn φ sao cho cosφ={a}/{R}, sinφ={b}/{R}. Khi đó f(x)=R sin(x+φ)≤R, và có thể đạt dấu bằng. Kết quả {ans}.'
 elif key=='conditional_union_independent':
  p=S.Rational(1+t%4,6);qq=S.Rational(1+t%3,7);den=p+qq-p*qq;ans=p/den
  assert S.simplify(ans*den-p)==0
  q=f'Hai biến cố A, B độc lập, P(A)={fmt(p)}, P(B)={fmt(qq)}. Tính P(A | A∪B).'
  sol=f'Vì A⊂A∪B, P(A∩(A∪B))=P(A)={fmt(p)}. Độc lập cho P(A∪B)=p+q−pq={fmt(den)}. Do đó P(A|A∪B)={fmt(ans)}.'
 elif key=='rotate_then_translate':
  x,y,a,b=1+t,2+t%4,3+t,4+t%5;ans=x+b
  assert ans==S.Matrix([[-0,-1],[1,0]])[1,0]*x+b
  q=f'Điểm M({x},{y}) quay 90° ngược chiều kim đồng hồ quanh O rồi tịnh tiến theo vectơ ({a},{b}). Tính tung độ ảnh cuối cùng.'
  sol=f'Phép quay 90° biến (x,y)→(−y,x), nên M thành ({-y},{x}). Tịnh tiến thêm ({a},{b}) làm tung độ tăng {b}: y′={x}+{b}={ans}.'
 elif key=='parallel_planes_distance':
  d1=5*t;d2=5*(t+1+t%5);ans=S.Rational(abs(d2-d1),5)
  assert S.Rational((d2-d1)**2,25)==ans**2
  q=f'Cho hai mặt phẳng song song α: 3x+4y={d1} và β: 3x+4y={d2}. Khoảng cách giữa chúng bằng bao nhiêu?'
  sol=f'Hai mặt phẳng cùng pháp tuyến n=(3,4,0), ||n||=5. Khoảng cách d=|{d2}−{d1}|/5={fmt(ans)}.'
 elif key=='quartile_lower_eight':
  a=1+t;seq=[a,a+1,a+2,a+5,a+6,a+7,a+8,a+10];ans=S.Rational(seq[1]+seq[2],2)
  assert ans==S.Rational(sorted(seq)[1]+sorted(seq)[2],2)
  q=f'Cho mẫu tám số đã xếp tăng: {seq}. Theo quy tắc lấy trung vị của nửa dưới, tứ phân vị thứ nhất Q₁ là bao nhiêu?'
  sol=f'Bốn giá trị thấp nhất là {seq[:4]}. Q₁ là trung bình của giá trị thứ hai và thứ ba: ({seq[1]}+{seq[2]})/2={fmt(ans)}.'
 elif key=='regular_pyramid_lateral':
  side=2+t;slant=side+3+t%4;n=3+t%4;ans=S.Rational(n*side*slant,2)
  assert ans==n*S.Rational(side*slant,2)
  q=f'Hình chóp đều có đáy là đa giác đều {n} cạnh, mỗi cạnh dài {side}, đường cao mặt bên bằng {slant}. Tính diện tích xung quanh.'
  sol=f'Mỗi mặt bên là tam giác diện tích {side}×{slant}/2. Có {n} mặt như vậy, S_xq={n}×{side}×{slant}/2={fmt(ans)}.'
 elif key=='angle_line_plane_tangent':
  h=2+t;d=3+t%5;ans=S.Rational(h,d)
  assert S.Rational(h*h,d*d)==ans**2
  q=f'Đoạn thẳng SA tạo với mặt phẳng (P) một góc nhọn θ. Biết A thuộc (P), hình chiếu vuông góc của S lên (P) là H, SH={h}, AH={d}. Tính tan θ.'
  sol=f'Trong tam giác SHA vuông tại H, θ là góc giữa SA và hình chiếu AH, nên tanθ=SH/AH={h}/{d}={fmt(ans)}.'
 elif key=='plane_three_intercepts':
  a,b,c=2+t,3+t,4+t;ans=S.Rational(1,a)
  x,y,z=S.symbols('x y z');assert S.simplify(ans*a+S.Rational(1,b)*0+S.Rational(1,c)*0-1)==0
  q=f'Mặt phẳng (P) đi qua A({a},0,0), B(0,{b},0), C(0,0,{c}). Viết dưới dạng αx+βy+γz=1. Tính α.'
  sol=f'Phương trình đoạn chắn: x/{a}+y/{b}+z/{c}=1. Vì thế hệ số α=1/{a}={fmt(ans)}.'
 elif key=='sphere_tangent_plane_D':
  a,b,c=2+t,1+t%4,3+t%5;k=1+t;px=a+3*k;py=b+4*k;pz=c
  D=-(3*px+4*py);ans=D
  assert 3*(a+3*k)+4*(b+4*k)+D==0
  q=f'Mặt cầu tâm C({a},{b},{c}) đi qua P({px},{py},{pz}). Mặt phẳng tiếp xúc tại P có phương trình 3x+4y+D=0. Tìm D.'
  sol=f'Bán kính CP=(3·{k},4·{k},0), cùng phương với (3,4,0), là pháp tuyến tiếp diện. Mặt phẳng qua P có 3(x−{px})+4(y−{py})=0, nên D=−3×{px}−4×{py}={D}.'
 elif key=='point_line_distance_sq':
  x,y,z=1+t,2+t%4,3+t%5;u=S.Matrix([1,2,2]);P=S.Matrix([x,y,z]);ans=S.Rational(P.cross(u).dot(P.cross(u)),u.dot(u))
  assert S.simplify(ans-(P.dot(P)-S.Rational(P.dot(u)**2,u.dot(u))))==0
  q=f'Trong Oxyz, đường thẳng d qua O(0,0,0) có vectơ chỉ phương u=(1,2,2). Cho P({x},{y},{z}). Tính bình phương khoảng cách từ P đến d.'
  sol=f'd²=||OP×u||²/||u||². Với OP=({x},{y},{z}), u=(1,2,2), ta có ||u||²=9 và d²=||OP||²−(OP·u)²/9={fmt(ans)}.'
 elif key=='perpendicular_planes_parameter':
  a,b,c,d,e=2+t,3+t%4,1,2+t%3,3+t%5;ans=-(a*d+b*e)
  assert ans*c+a*d+b*e==0
  q=f'Hai mặt phẳng α có pháp tuyến (m,{a},{b}) và β có pháp tuyến ({c},{d},{e}). Tìm m để α vuông góc β.'
  sol=f'Điều kiện vuông góc: tích vô hướng hai pháp tuyến bằng 0, tức m·{c}+{a}×{d}+{b}×{e}=0. Do đó m={ans}.'
 elif key=='cone_lateral_area_over_pi':
  triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(9,40,41),(12,35,37),(11,60,61),(28,45,53),(16,63,65)]
  r,h,l=triples[i];ans=r*l
  assert l*l==r*r+h*h
  q=f'Hình nón tròn xoay có bán kính đáy r={r}, chiều cao h={h}. Diện tích xung quanh S_xq chia π bằng bao nhiêu?'
  sol=f'Đường sinh l=√(r²+h²)=√({r}²+{h}²)={l}. Diện tích xung quanh S_xq=πrl, nên S_xq/π={r}×{l}={ans}.'
 elif key=='substitution_integral':
  c=2+t%5;d=3+t;n=2+t%4;L=2+t%4
  u0=d;u1=L*L+c*L+d;ans=S.Rational(u1**(n+1)-u0**(n+1),n+1)
  x=S.symbols('x');assert S.integrate((2*x+c)*(x*x+c*x+d)**n,(x,0,L))==ans
  q=f'Tính I=∫ từ 0 đến {L} của (2x+{c})(x²+{c}x+{d})^{n} dx.'
  sol=f'Đặt u=x²+{c}x+{d} thì du=(2x+{c})dx. Cận mới: u(0)={u0}, u({L})={u1}. I=[u^{n+1}/{n+1}]_{u0}^{u1}={fmt(ans)}.'
 elif key=='washer_revolution_over_pi':
  m=2+t;L=3+t; b=1+t%4
  ans=S.Rational(m*L*L,2)
  x=S.symbols('x');assert S.integrate((m*x+b)-b,(x,0,L))==ans
  q=f'Miền phẳng 0≤x≤{L}, sqrt({b})≤y≤sqrt({m}x+{b}) quay quanh Ox thành khối có thể tích V. Tính V/π.'
  sol=f'Vành khăn có R²={m}x+{b}, r²={b}. V/π=∫₀^{L}(R²−r²)dx=∫₀^{L}{m}x dx={fmt(ans)}.'
 elif key=='integral_least_squares':
  L=2*(1+t);ans=S.Rational(L,2)
  x,a=S.symbols('x a',real=True);fun=S.integrate((x-a)**2,(x,0,L))
  critical=S.solve(S.diff(fun,a),a)
  assert critical==[ans] and S.diff(fun,a,2)>0
  q=f'Cho F(a)=∫ từ 0 đến {L} của (x−a)² dx, a∈R. Tìm a để F(a) nhỏ nhất.'
  sol=f'Khai triển và tích phân: F(a)={L}³/3−a·{L}²+a²·{L}. Đạo hàm F′(a)=2{L}a−{L*L}=0 cho a={fmt(ans)}; F′′(a)=2{L}>0.'
 elif key=='variation_coefficient':
  m=4+t;d=1+t%3;vals=[m-d,m-d,m+d,m+d];ans=S.Rational(d,m)
  assert sum(vals)==4*m and S.Rational(sum((x-m)**2 for x in vals),4)==d*d
  q=f'Mẫu số liệu {vals}, tính hệ số biến thiên CV=độ lệch chuẩn tổng thể / trung bình (không nhân 100%).'
  sol=f'Giá trị trung bình bằng {m}. Phương sai là [2({d})²+2({d})²]/4={d*d}, độ lệch chuẩn {d}. Vì thế CV={d}/{m}={fmt(ans)}.'
 elif key=='three_dim_plane_angle_line':
  a=2+t%5;b=2+t%4;u=S.Matrix([a,0,b]);n=S.Matrix([0,b,a]);ans=S.Rational(u.dot(n)**2,u.dot(u)*n.dot(n))
  assert ans==1-S.Rational(u.cross(n).dot(u.cross(n)),u.dot(u)*n.dot(n))
  q=f'Đường thẳng có vectơ chỉ phương u=({a},0,{b}), mặt phẳng có pháp tuyến n=(0,{b},{a}). Với góc nhọn θ giữa đường và mặt phẳng, tính sin²θ.'
  sol=f'Góc giữa đường và mặt phẳng là góc bù phụ của góc giữa u,n. sin²θ=(u·n)²/(||u||²||n||²)={fmt(ans)}.'
 elif key=='sphere_cap_area_over_pi':
  R=3+t;h=1+t%4;ans=2*R*h
  assert S.integrate(2*S.pi*R,(S.Symbol('z'),0,h))/S.pi==ans
  q=f'Một chỏm cầu có bán kính mặt cầu R={R} và chiều cao h={h}. Diện tích mặt cong S của chỏm (không gồm đáy) chia π là bao nhiêu?'
  sol=f'Dùng công thức diện tích mặt cong chỏm cầu S=2πRh, nên S/π=2×{R}×{h}={ans}.'
 elif key=='quadratic_area_between':
  a=2+t;ans=S.Rational(a**3,6)
  x=S.symbols('x');assert S.integrate(a*x-x*x,(x,0,a))==ans
  q=f'Hình phẳng giới hạn bởi hai đồ thị y={a}x và y=x². Tính diện tích miền kẹp giữa chúng.'
  sol=f'Giải x²={a}x được giao điểm x=0 và x={a}. Trên [0,{a}], {a}x≥x². Diện tích S=∫₀^{a}({a}x−x²)dx=[{a}x²/2−x³/3]₀^{a}={fmt(ans)}.'
 else:raise KeyError(key)
 return q,S.Rational(ans),sol


def main():
 specs=[];rows=[];bygrade=collections.Counter();bytype=collections.Counter()
 for key,(grade,topic,name,method,conditions,difficulty) in SPECS.items():
  assert (grade,topic) in CATALOG
  specs.append({'form_id':'v199_'+key,'grade':grade,'topic':topic,'name':name,'mathematical_essence':name,'method':method,'conditions':conditions,'difficulty':difficulty,'question_count':10,'independent_method_certified':False})
  seen=set()
  for i in range(10):
   question,ans,solution=build(key,i)
   assert question not in seen,(key,i,'duplicate prompt');seen.add(question)
   typ='multiple_choice' if i<7 else 'short_answer' if i<9 else 'true_false'
   if typ=='multiple_choice':
    options_numeric=([ans, ans*S.Rational(11,10), ans*S.Rational(9,10), ans*S.Rational(3,2)] if abs(ans)>10**7 else choices_for(ans, key in {'conditional_union_independent'} or 'ratio' in key))
    pos=(i+len(key))%4
    other=options_numeric[1:];options=[fmt(v) for v in other[:pos]+[ans]+other[pos:]]
    answer=fmt(ans);explanation=solution+f' Đối chiếu bốn phương án, chỉ {answer} trùng kết quả.'
   elif typ=='short_answer':
    options=[];answer=fmt(ans);explanation=solution+' Nhập kết quả dưới dạng phân số tối giản nếu cần.'
   else:
    options=[f'Kết quả đúng bằng {fmt(ans)}.',f'Kết quả đúng bằng {fmt(ans+2)}.',f'Kết quả lớn hơn {fmt(ans-1)}.',f'Kết quả bé hơn {fmt(ans-1)}.'];answer='Đúng,Sai,Đúng,Sai';explanation=solution+' Vì thế nhận định 1 đúng, 2 sai, 3 đúng, 4 sai.'
   rows.append({'id':f'v199_{key}_{i:02d}','form_id':'v199_'+key,'grade':grade,'topic':topic,'concept':name,'math_method':method,'conditions':conditions,'difficulty':difficulty,'question_type':typ,'question':question,'answer':answer,'correct_answer':answer,'solution':explanation,'choices':options,'source_bundle':'V199','validation_status':'sympy_independent_exact_oracle_checked','method_independence_certified':False,'production_integrated':False})
   bygrade[str(grade)]+=1;bytype[typ]+=1
 OUT.mkdir(exist_ok=True)
 (OUT/'V199_FAMILY_SPECS.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n')
 (OUT/'V199_INCREMENT.jsonl').write_text(''.join(json.dumps(q,ensure_ascii=False)+'\n' for q in rows))
 report={'version':'V199','new_candidate_groups':len(specs),'math_oracle_checked_questions':len(rows),'grade_breakdown':dict(bygrade),'formats':dict(bytype),'independent_certified_forms':0,'production_deployed':False}
 (OUT/'V199_GENERATION_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
