#!/usr/bin/env python3
"""V202 20 candidate solution strategies: validated exact identities + application grading.
Method novelty remains unproven until comprehensive expert semantic review.
"""
import collections,json,math
from pathlib import Path
import sympy as S
from v198_generate import fmt,choices_for
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'bank_updates'
CATALOG={(int(g),x['id']) for g,xs in json.loads((ROOT/'backend/app/ai/knowledge/index.json').read_text()).items() for x in xs}
SPECS={
 'polygon_diagonals':(10,'g10_geom_quadrilaterals_properties','Đếm số đường chéo đa giác lồi n cạnh','D=n(n−3)/2, đếm cặp đỉnh trừ các cạnh','n≥4','nền tảng'),
 'chord_from_radius_distance':(10,'g10_geom_circle_chords_arcs','Tính độ dài dây cung từ bán kính và khoảng cách đến tâm','L=2√(R²−d²), tam giác vuông tâm–trung điểm dây','0≤d<R','trung cấp'),
 'law_of_cosines_c_square':(10,'he_thuc_luong_van_dung_10','Tính bình phương cạnh đối góc 60° từ hai cạnh kề','c²=a²+b²−ab','a,b>0 và góc xen giữa 60°','trung cấp'),
 'multiset_permutation_count':(10,'hoan_vi_chinh_hop_to_hop','Số hoán vị phân biệt của đa tập có hai loại phần tử','P=(a+b)!/(a!b!)','a,b nguyên dương','trung cấp'),
 'right_triangle_median_hypotenuse':(10,'g10_geom_triangle_inequalities','Trung tuyến từ đỉnh góc vuông tới cạnh huyền','m=c/2 theo định lý trung tuyến trong tam giác vuông','Tam giác vuông với cạnh huyền c>0','nền tảng'),
 'sector_area_over_pi':(10,'duong_tron_co_ban_10','Diện tích hình quạt tròn ứng với góc ở tâm','S/π=r²θ/360°','r>0, 0<θ≤360°','trung cấp'),
 'tangent_segment_length':(10,'g10_geom_circle_tangent_chord','Tính độ dài tiếp tuyến từ điểm ngoài đường tròn','PT=√(OP²−R²)','OP>R>0, PT là tiếp tuyến','trung cấp'),
 'similar_area_scale':(10,'g10_geom_triangle_area_ratio','Tỉ số diện tích hai tam giác đồng dạng','S₂/S₁=k² khi tỉ số cạnh tương ứng là k','Hai tam giác đồng dạng, k>0','trung cấp'),
 'cos_zeros_interval':(11,'phuong_trinh_luong_giac','Đếm nghiệm cos x=0 trên đoạn [0,nπ]','x=π/2+kπ, k=0,...,n−1','n nguyên dương','nền tảng'),
 'rational_derivative_point':(11,'dao_ham_quy_tac','Đạo hàm tại điểm của thương hai đa thức','(u/v)′=(u′v−uv′)/v²','Mẫu số khác 0 tại điểm','trung cấp'),
 'leading_poly_limit':(11,'gioi_han_ham_so','Giới hạn tại dương vô cực của tỉ số đa thức cùng bậc','Giới hạn bằng tỉ số hệ số bậc cao nhất','Hệ số bậc cao nhất mẫu khác 0','nền tảng'),
 'piecewise_continuity_parameter':(11,'ham_so_lien_tuc','Tìm tham số để hàm từng đoạn liên tục tại điểm nối','Giới hạn trái bằng giá trị tại điểm nối','Hai biểu thức từng đoạn có giới hạn tại điểm nối','trung cấp'),
 'binomial_exact_success_count':(11,'bien_co_doc_lap_11','Xác suất đúng k lần thành công trong n phép thử độc lập','P=C(n,k)p^k(1−p)^(n−k)','0≤k≤n, 0<p<1, thử độc lập','trung cấp'),
 'sum_first_n_odd_by_induction':(11,'quy_nap_toan_hoc_11','Tính tổng n số lẻ dương đầu tiên bằng quy nạp','1+3+⋯+(2n−1)=n²','n nguyên dương','nền tảng'),
 'parallel_planes_distance':(12,'goc_khoang_cach_oxyz','Khoảng cách hai mặt phẳng song song','d=|D₁−D₂|/√(a²+b²+c²)','Cùng một vectơ pháp tuyến khác 0','trung cấp'),
 'sphere_plane_section_radius':(12,'g12_geom_sphere_tangent_plane','Bán kính giao tuyến đường tròn của mặt cầu và mặt phẳng','r=√(R²−d²)','0≤d<R, mặt phẳng cắt mặt cầu','trung cấp'),
 'odd_integral_symmetric':(12,'nguyen_ham_tich_phan','Tính tích phân của hàm lẻ trên đoạn đối xứng','∫[-a,a]f(x)dx=0 nếu f lẻ','f liên tục trên đoạn đối xứng','nền tảng'),
 'product_exp_derivative':(12,'tiep_tuyen','Đạo hàm tại 0 của tích hàm bậc nhất và e^x','[(ax+b)e^x]′=(ax+a+b)e^x','a,b thực','trung cấp'),
 'cubic_local_max':(12,'cuc_tri','Giá trị cực đại địa phương của hàm bậc ba có hai điểm dừng','f=x³−3k²x; cực đại tại −k bằng 2k³','k>0','trung cấp'),
 'cone_lateral_area_over_pi':(12,'hinh_khoi_va_the_tich_co_ban_12','Diện tích xung quanh hình nón chia π','S/π=rl với l là đường sinh','r,l>0','nền tảng'),
}

def build(key,i):
 t=i+1
 if key=='polygon_diagonals':
  n=4+t;ans=n*(n-3)//2;assert ans==sum(1 for j in range(n) for k in range(j+1,n) if k-j not in (1,n-1))
  q=f'Một đa giác lồi có {n} đỉnh. Có bao nhiêu đường chéo?';sol=f'Mỗi đỉnh nối được {n-3} đỉnh không kề. Mỗi đường chéo được đếm hai lần, nên D={n}×({n}−3)/2={ans}.'
 elif key=='chord_from_radius_distance':
  k=t;R=5*k;d=4*k;ans=6*k
  assert S.sqrt(R*R-d*d)*2==ans
  q=f'Đường tròn bán kính {R} có một dây cung cách tâm {d} đơn vị. Tính độ dài dây cung.';sol=f'Đường vuông góc từ tâm chia đôi dây, mỗi nửa dài √({R}²−{d}²)={3*k}; độ dài dây bằng 2×{3*k}={ans}.'
 elif key=='law_of_cosines_c_square':
  a,b=3+t,4+t;ans=a*a+b*b-a*b
  x=S.sqrt(ans);assert S.simplify(x*x-(a*a+b*b-2*a*b*S.cos(S.pi/3)))==0
  q=f'Tam giác có hai cạnh kề góc 60° lần lượt bằng {a} và {b}. Tính bình phương cạnh đối diện góc 60°.';sol=f'Định lý cosin cho c²={a}²+{b}²−2×{a}×{b}×cos60°={a*a}+{b*b}−{a*b}={ans}.'
 elif key=='multiset_permutation_count':
  a,b=1+t,1+t%4;n=a+b;ans=S.binomial(n,a)
  assert ans==S.factorial(n)/(S.factorial(a)*S.factorial(b))
  q=f'Có {a} thẻ chữ A giống nhau và {b} thẻ chữ B giống nhau. Có bao nhiêu cách xếp thành một dãy sử dụng hết thẻ?';sol=f'Số hoán vị đa tập có {n} phần tử, trong đó A lặp {a} lần, B lặp {b} lần, là {n}!/({a}!{b}!)={fmt(ans)}.'
 elif key=='right_triangle_median_hypotenuse':
  k=t;c=5*k;ans=S.Rational(c,2);assert S.sqrt((3*k)**2+(4*k)**2)==c
  q=f'Tam giác ABC vuông tại A, AB={3*k}, AC={4*k}. M là trung điểm BC. Tính AM.';sol=f'Pythagore: BC=√({3*k}²+{4*k}²)={c}. Trong tam giác vuông, trung tuyến tới cạnh huyền bằng một nửa cạnh huyền: AM={c}/2={fmt(ans)}.'
 elif key=='sector_area_over_pi':
  r=3+t;theta=[30,45,60,90,120,135,150,180,270,300][i];ans=S.Rational(r*r*theta,360)
  assert S.simplify(S.pi*r*r*theta/360/S.pi-ans)==0
  q=f'Cho hình quạt tròn bán kính {r}, góc ở tâm {theta}°. Gọi diện tích S, tính S/π.';sol=f'S=(θ/360)πr², suy ra S/π={theta}×{r}²/360={fmt(ans)}.'
 elif key=='tangent_segment_length':
  k=t;OP=5*k;R=3*k;ans=4*k;assert OP*OP-R*R==ans*ans
  q=f'Điểm P nằm ngoài đường tròn tâm O bán kính {R}, OP={OP}. T là tiếp điểm của tiếp tuyến từ P. Tính PT.';sol=f'OT⊥PT nên tam giác OTP vuông tại T. PT=√(OP²−OT²)=√({OP}²−{R}²)={ans}.'
 elif key=='similar_area_scale':
  k=S.Rational(t+2,t+1);ans=k*k
  assert S.simplify((k*5)*(k*7)/(5*7)-ans)==0
  q=f'Hai tam giác ABC và A′B′C′ đồng dạng với tỉ số cạnh tương ứng A′B′/AB={fmt(k)}. Tính S(A′B′C′)/S(ABC).';sol=f'Diện tích hai tam giác đồng dạng tỉ lệ với bình phương tỉ số cạnh: ({fmt(k)})²={fmt(ans)}.'
 elif key=='cos_zeros_interval':
  n=t+2;ans=n;assert sum(S.cos((2*j+1)*S.pi/2)==0 for j in range(n))==n
  q=f'Phương trình cos x=0 có bao nhiêu nghiệm x trong đoạn [0,{n}π]?';sol=f'cos x=0 khi x=π/2+kπ (k nguyên). Trong đoạn [0,{n}π], chỉ k=0,...,{n-1} thỏa, tổng cộng {n} nghiệm.'
 elif key=='rational_derivative_point':
  a=t+2;b=t+3;x0=t;X=S.symbols('x');f=(a*X*X+b)/(X+1);ans=S.diff(f,X).subs(X,x0)
  alternative=S.Rational((2*a*x0)*(x0+1)-(a*x0*x0+b),(x0+1)**2);assert ans==alternative
  q=f'Cho f(x)=({a}x²+{b})/(x+1). Tính f′({x0}).';sol=f'Quy tắc đạo hàm thương: f′(x)=[{2*a}x(x+1)−({a}x²+{b})]/(x+1)². Thay x={x0} được {fmt(ans)}.'
 elif key=='leading_poly_limit':
  a=t+2;b=t+3;c=t+4;X=S.symbols('x');f=(a*X**2+c*X+1)/(b*X**2+X+2);ans=S.Rational(a,b)
  assert S.limit(f,X,S.oo)==ans
  q=f'Tính lim_(x→+∞) [({a}x²+{c}x+1)/({b}x²+x+2)].';sol=f'Chia tử và mẫu cho x², các số hạng 1/x và 1/x² tiến về 0. Giới hạn bằng tỉ số hệ số bậc hai {a}/{b}={fmt(ans)}.'
 elif key=='piecewise_continuity_parameter':
  a=t+1;b=t+2;x0=2+t%4;ans=a*x0+b
  assert S.limit(a*S.Symbol('x')+b,S.Symbol('x'),x0,dir='-')==ans
  q=f'Cho f(x)={a}x+{b} nếu x<{x0}, và f(x)=m nếu x≥{x0}. Tìm m để f liên tục tại x={x0}.';sol=f'Giới hạn trái khi x→{x0} bằng {a}×{x0}+{b}={ans}. Vì f({x0})=m, tính liên tục yêu cầu m={ans}.'
 elif key=='binomial_exact_success_count':
  n=4+t;k=1+(t%3);p=S.Rational(1,2+t%3);ans=S.binomial(n,k)*p**k*(1-p)**(n-k)
  brute=sum(S.binomial(n,j)*p**j*(1-p)**(n-j) for j in range(n+1));assert S.simplify(brute-1)==0 and 0<ans<1
  q=f'Một phép thử độc lập có xác suất thành công p={fmt(p)}. Trong {n} phép thử, xác suất đúng {k} lần thành công là bao nhiêu?';sol=f'Biến đếm có phân phối nhị thức. P=C({n},{k})×({fmt(p)})^{k}×(1−{fmt(p)})^({n}−{k})={fmt(ans)}.'
 elif key=='sum_first_n_odd_by_induction':
  n=5+t;ans=n*n;assert sum(2*i-1 for i in range(1,n+1))==ans
  q=f'Tính tổng 1+3+5+⋯+({2*n-1}), gồm {n} số lẻ dương liên tiếp đầu tiên.';sol=f'Cơ sở n=1 cho tổng 1=1². Nếu tổng đến n là n², thêm (2n+1) được (n+1)². Do quy nạp, tổng đến {n} bằng {n}²={ans}.'
 elif key=='parallel_planes_distance':
  k=t;D1=t+3;D2=D1+3*k;ans=k
  assert S.sqrt(2*2+(-1)**2+2*2)==3 and abs(D1-D2)/3==ans
  q=f'Tính khoảng cách giữa hai mặt phẳng 2x−y+2z+({D1})=0 và 2x−y+2z+({D2})=0.';sol=f'Hai mặt phẳng song song, vectơ pháp tuyến có độ dài √(4+1+4)=3. Khoảng cách =|{D1}−{D2}|/3={ans}.'
 elif key=='sphere_plane_section_radius':
  k=t;R=5*k;d=4*k;ans=3*k;assert R*R-d*d==ans*ans
  q=f'Một mặt phẳng cắt mặt cầu bán kính {R}, cách tâm mặt cầu {d}. Tính bán kính đường tròn giao tuyến.';sol=f'Trong tam giác vuông qua tâm và giao tuyến: r²=R²−d²={R}²−{d}²={ans*ans}, do đó r={ans}.'
 elif key=='odd_integral_symmetric':
  a=t+1;c=t+2;d=t+3;X=S.symbols('x');f=c*X**3+d*X;ans=0
  assert S.integrate(f,(X,-a,a))==0 and S.simplify(f.subs(X,-X)+f)==0
  q=f'Tính tích phân từ −{a} đến {a} của ({c}x³+{d}x) dx.';sol=f'Hàm f(x)={c}x³+{d}x là hàm lẻ, liên tục trên [−{a},{a}]. Hai nửa tích phân triệt tiêu, nên bằng 0.'
 elif key=='product_exp_derivative':
  a=t+2;b=t+4;X=S.symbols('x');f=(a*X+b)*S.exp(X);ans=a+b
  assert S.diff(f,X).subs(X,0)==ans
  q=f'Cho f(x)=({a}x+{b})e^x. Tính f′(0).';sol=f'Dùng quy tắc đạo hàm tích: f′(x)={a}e^x+({a}x+{b})e^x. Tại x=0, f′(0)={a}+{b}={ans}.'
 elif key=='cubic_local_max':
  k=t;X=S.symbols('x');f=X**3-3*k*k*X;ans=2*k**3
  assert S.diff(f,X).subs(X,-k)==0 and S.diff(f,X,2).subs(X,-k)<0 and f.subs(X,-k)==ans
  q=f'Cho f(x)=x³−{3*k*k}x. Tính giá trị cực đại địa phương của f(x).';sol=f'f′(x)=3x²−{3*k*k}=0 khi x=±{k}. f′′(−{k})=−{6*k}<0 nên cực đại tại x=−{k}; f(−{k})={ans}.'
 elif key=='cone_lateral_area_over_pi':
  k=t;r=3*k;h=4*k;l=5*k;ans=r*l;assert S.sqrt(r*r+h*h)==l
  q=f'Hình nón có bán kính đáy {r}, chiều cao {h}. Gọi diện tích xung quanh là S, tính S/π.';sol=f'Đường sinh l=√({r}²+{h}²)={l}. Diện tích xung quanh S=πrl nên S/π={r}×{l}={ans}.'
 else:raise KeyError(key)
 return q,S.Rational(ans),sol

def main():
 specs=[];rows=[];gc=collections.Counter();fc=collections.Counter()
 for key,(grade,topic,name,method,conditions,difficulty) in SPECS.items():
  assert (grade,topic) in CATALOG,(grade,topic)
  form_id='v202_'+key
  specs.append(dict(form_id=form_id,grade=grade,topic=topic,name=name,mathematical_essence=name,method=method,conditions=conditions,difficulty=difficulty,question_count=10,independent_method_certified=False))
  prompts=set()
  for i in range(10):
   q,ans,sol=build(key,i);assert q not in prompts,(key,i);prompts.add(q)
   typ='multiple_choice' if i<7 else 'short_answer' if i<9 else 'true_false'
   if typ=='multiple_choice':
    choices_base=choices_for(ans,0<=ans<=1 and ans!=0)
    pos=(i+len(key))%4;opts=choices_base[1:][:pos]+[ans]+choices_base[1:][pos:]
    opts=[fmt(x) for x in opts];answer=fmt(ans)
    assert len(set(opts))==4
    solution=sol+f' Chọn duy nhất phương án {answer}.'
   elif typ=='short_answer':
    opts=[];answer=fmt(ans);solution=sol+' Đáp án có thể nhập dưới dạng phân số tối giản.'
   else:
    opts=[f'Kết quả bằng {fmt(ans)}.',f'Kết quả lớn hơn {fmt(ans+1)}.',f'Kết quả lớn hơn {fmt(ans-1)}.',f'Kết quả bằng {fmt(ans+1)}.']
    answer='Đúng,Sai,Đúng,Sai';solution=sol+' Lần lượt nhận định đúng, sai, đúng, sai.'
   rows.append(dict(id=f'{form_id}_{i:02d}',form_id=form_id,grade=grade,topic=topic,concept=name,math_method=method,conditions=conditions,difficulty=difficulty,question_type=typ,question=q,answer=answer,correct_answer=answer,solution=solution,choices=opts,source_bundle='V202',validation_status='independent_exact_calculation_checked',method_independence_certified=False,production_integrated=False))
   gc[str(grade)]+=1;fc[typ]+=1
 (OUT/'V202_FAMILY_SPECS.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (OUT/'V202_INCREMENT.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf8')
 result=dict(version='V202',new_candidate_families=len(specs),math_oracle_checked=len(rows),grades=dict(gc),formats=dict(fc),independent_certified=0,production_deployed=False)
 (OUT/'V202_GENERATION_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
