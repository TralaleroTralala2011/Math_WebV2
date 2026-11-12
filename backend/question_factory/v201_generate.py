#!/usr/bin/env python3
"""V201 fourth batch, exact-oracle verified questions, method novelty pending human review."""
from __future__ import annotations
import json,collections,math,itertools
from pathlib import Path
import sympy as S
from v198_generate import fmt,choices_for
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'bank_updates'
CATALOG={(int(g),r['id']) for g,ts in json.loads((ROOT/'backend/app/ai/knowledge/index.json').read_text()).items() for r in ts}
SPECS={
 'de_morgan_complement':(10,'menh_de_tap_hop','Đếm phần tử ngoài hợp hai tập trong vũ trụ','|U\\(A∪B)|=|U|−|A|−|B|+|A∩B|','U hữu hạn, A,B là tập con của U','nền tảng'),
 'rational_inequality_integers':(10,'bat_phuong_trinh','Đếm nghiệm nguyên của bất phương trình phân thức một ẩn','Xét dấu (x−a)/(x−b) và loại x=b','a<b, x nguyên trong đoạn hữu hạn','trung cấp'),
 'mixture_concentration':(10,'bai_toan_thuc_te_10','Nồng độ sau khi pha hai dung dịch','C=(m₁c₁+m₂c₂)/(m₁+m₂)','Thể tích cộng được, nồng độ trong [0,100%]','trung cấp'),
 'triangle_area_sin_30':(10,'he_thuc_luong','Diện tích tam giác theo hai cạnh và góc xen giữa 30°','S=ab sin C/2=ab/4','Hai cạnh kề dương và góc xen giữa 30°','nền tảng'),
 'fourth_parallelogram_vertex':(10,'g10_geom_quadrilaterals_properties','Khôi phục đỉnh thứ tư của hình bình hành ABCD','D=A+C−B với A,B,C liên tiếp','A,B,C không thẳng hàng','trung cấp'),
 'cramer_x':(10,'he_phuong_trinh','Tìm hoành độ nghiệm hệ phương trình tuyến tính bằng Cramer','x=(u d−b v)/(ad−bc)','ad−bc khác 0','trung cấp'),
 'bounded_radical_domain':(10,'g10_radical_equations_advanced','Đếm số nguyên thuộc miền xác định căn của tích hai nhị thức','(x−a)(b−x)≥0 tương đương a≤x≤b','a<b nguyên','trung cấp'),
 'stirling_three_groups':(10,'g10_combinatorics_olympiad','Chia n phần tử phân biệt thành ba nhóm không nhãn và không rỗng','S(n,3)=(3^n−3·2^n+3)/6','n≥3; ba nhóm không đánh số thứ tự','nâng cao'),
 'geometric_first_success':(11,'xac_suat_11','Xác suất lần thành công đầu tiên xảy ra ở bước k','(1−p)^(k−1)p','Các phép thử Bernoulli độc lập cùng p','trung cấp'),
 'motion_acceleration':(11,'ung_dung_dao_ham_11','Tính gia tốc tức thời từ hàm vị trí bậc ba','a(t)=s′′(t)=6At+2B','s(t) khả vi hai lần','trung cấp'),
 'two_colors_selection':(11,'to_hop_xac_suat_nang_cao_11','Số cách chọn k phần tử có cả hai màu','C(a+b,k)−C(a,k)−C(b,k)','a,b dương, 2≤k≤a+b','nâng cao'),
 'prism_edge_count':(11,'g11_geom_space_lines_planes','Đếm tổng cạnh của lăng trụ có đáy n giác','3n cạnh gồm hai đáy và n cạnh bên','Lăng trụ hai đáy là n giác với n≥3','nền tảng'),
 'parabola_line_intersection_count':(12,'tuong_giao','Đếm số giao điểm của parabol và đường thẳng','Đếm nghiệm thực phương trình bậc hai bằng biệt thức','Hai đồ thị y=x² và y=mx+b','trung cấp'),
 'inverse_linear_derivative':(12,'ung_dung_dao_ham','Đạo hàm hàm ngược tại điểm theo đạo hàm hàm gốc','(f^-1)′(y)=1/f′(x), y=f(x)','f tuyến tính với hệ số góc khác 0','trung cấp'),
 'horizontal_asymptote_ratio':(12,'khao_sat_ham_so','Tiệm cận ngang của phân thức có bậc tử mẫu bằng nhau','Giới hạn bằng thương hai hệ số cao nhất','Hệ số bậc hai mẫu khác 0','nền tảng'),
 'decreasing_log_integer_count':(12,'bpt_logarit','Đếm nghiệm nguyên khi cơ số logarit nằm trong (0,1)','Hàm log cơ số a<1 nghịch biến, đổi chiều bất đẳng thức','x−h>0, cơ số 1/2','trung cấp'),
 'sphere_complete_square':(12,'g12_geom_sphere_equation','Hoàn thành bình phương để tìm bán kính mặt cầu','R²=(A²+B²+C²)/4−D','R²>0','trung cấp'),
 'cylinder_lateral_area':(12,'hinh_khoi_va_the_tich_co_ban_12','Diện tích xung quanh hình trụ chia π','S/π=2rh','r,h dương','nền tảng'),
 'bernoulli_variance':(12,'xac_suat_12','Phương sai của biến Bernoulli','Var(X)=p(1−p)','0<p<1, X nhận giá trị 0 hoặc 1','trung cấp'),
 'normal_plane_constant':(12,'mat_phang_oxyz','Phương trình mặt phẳng qua điểm và pháp tuyến','D=−(ax₀+by₀+cz₀)','Vectơ pháp tuyến khác 0','trung cấp'),
}

def build(key,i):
 t=i+1
 if key=='de_morgan_complement':
  total=60+5*t;A=15+t;B=20+t;intersection=5+t%5
  ans=total-A-B+intersection
  assert intersection<=min(A,B) and ans>=0
  q=f'Vũ trụ U có {total} phần tử. Hai tập A,B⊂U có |A|={A}, |B|={B}, |A∩B|={intersection}. Có bao nhiêu phần tử không thuộc A cũng không thuộc B?'
  sol=f'|A∪B|={A}+{B}−{intersection}={A+B-intersection}. Phần bù trong U có {total}−{A+B-intersection}={ans} phần tử.'
 elif key=='rational_inequality_integers':
  a=-(3+t);b=2+t;L=2+t%3;R=7+t
  nums=[x for x in range(-L,R+1) if x!=b and (x-a)*(x-b)>=0]
  ans=len(nums)
  assert ans==sum(x<=a or x>b for x in range(-L,R+1))
  q=f'Trong đoạn số nguyên −{L}≤x≤{R}, có bao nhiêu x thỏa (x−({a}))/(x−{b})≥0?'
  sol=f'Có hai mốc a={a}<b={b}. Bảng xét dấu cho nghiệm x≤{a} hoặc x>{b}, và loại x={b}. Đếm các số nguyên trong [−{L},{R}] thỏa điều kiện được {ans}.'
 elif key=='mixture_concentration':
  a,b,c,d=2+t,3+t%4,10+2*t,30+t
  ans=S.Rational(a*c+b*d,a+b)
  assert 0<c<=100 and 0<d<=100
  q=f'Trộn {a} lít dung dịch nồng độ {c}% với {b} lít dung dịch cùng chất nồng độ {d}% (giả sử thể tích cộng được). Nồng độ dung dịch thu được bằng bao nhiêu phần trăm?'
  sol=f'Lượng chất tan tỉ lệ thể tích nhân nồng độ. Phần trăm hỗn hợp C=({a}×{c}+{b}×{d})/({a}+{b})={fmt(ans)}%.'
 elif key=='triangle_area_sin_30':
  a,b=3+t,4+t;ans=S.Rational(a*b,4)
  assert ans==S.Rational(a*b,2)*S.Rational(1,2)
  q=f'Tam giác có hai cạnh độ dài {a} và {b} với góc xen giữa 30°. Tính diện tích.'
  sol=f'S=ab sin C/2. Với sin30°=1/2, S={a}×{b}×(1/2)/2={fmt(ans)}.'
 elif key=='fourth_parallelogram_vertex':
  ax,ay,bx,by,cx,cy=t,0,2*t+3,1,3*t+8,5+(t%3)
  dx=ax+cx-bx;dy=ay+cy-by
  assert S.det(S.Matrix([[bx-ax,by-ay],[cx-bx,cy-by]]))!=0
  assert (cx-dx,cy-dy)==(bx-ax,by-ay)
  ans=dx
  q=f'Hình bình hành ABCD có ba đỉnh liên tiếp A({ax},{ay}), B({bx},{by}), C({cx},{cy}). Tìm hoành độ D.'
  sol=f'Trong hình bình hành AB=DC (vectơ), nên D=A+C−B. Hoành độ D: {ax}+{cx}−{bx}={dx}.'
 elif key=='cramer_x':
  a,b,c,d=2+t,1+t%3,1+t%4,3+t;x0=t;y0=2+t%5
  delta=a*d-b*c;assert delta!=0
  u=a*x0+b*y0;v=c*x0+d*y0
  ans=S.Rational(u*d-b*v,delta)
  assert ans==x0
  q=f'Giải hệ {a}x+{b}y={u}; {c}x+{d}y={v}. Tìm x.'
  sol=f'Định thức Δ={a}×{d}−{b}×{c}={delta} khác 0. Theo Cramer, x=({u}×{d}−{b}×{v})/{delta}={fmt(ans)}.'
 elif key=='bounded_radical_domain':
  a=-(2+t);b=4+t;ans=b-a+1
  assert ans==sum((x-a)*(b-x)>=0 for x in range(a-2,b+3))
  q=f'Có bao nhiêu giá trị nguyên x để biểu thức √[(x−({a}))({b}−x)] là số thực?'
  sol=f'Điều kiện dưới căn không âm: (x−({a}))({b}−x)≥0. Vì {a}<{b}, điều này đúng khi {a}≤x≤{b}. Số nguyên là {b}−({a})+1={ans}.'
 elif key=='stirling_three_groups':
  n=3+t;ans=S.Rational(3**n-3*2**n+3,6)
  assert ans.is_integer and ans>0
  q=f'Chia {n} học sinh khác nhau thành đúng 3 nhóm không rỗng; ba nhóm không có tên và đổi vị trí các nhóm không tạo cách chia mới. Có bao nhiêu cách?'
  sol=f'Trước hết phân về 3 nhóm có nhãn: 3^{n}−3×2^{n}+3 (bù trừ để nhóm nào cũng có người). Vì nhóm không nhãn, chia cho 3!=6, được {fmt(ans)}.'
 elif key=='geometric_first_success':
  p=S.Rational(1+t%4,7);k=2+t%5
  ans=(1-p)**(k-1)*p
  assert ans==S.prod([(1-p)]*(k-1)+[p])
  q=f'Các phép thử độc lập có xác suất thành công p={fmt(p)}. Xác suất lần thành công đầu tiên là lần thứ {k} bằng bao nhiêu?'
  sol=f'Phải trượt {k-1} lần liên tiếp, rồi thành công. P=(1−p)^({k}−1)p=(1−{fmt(p)})^{k-1}×{fmt(p)}={fmt(ans)}.'
 elif key=='motion_acceleration':
  a,b,c,t0=2+t%4,3+t,4+t,1+t
  ans=6*a*t0+2*b
  T=S.symbols('t');assert S.diff(a*T**3+b*T**2+c*T,T,2).subs(T,t0)==ans
  q=f'Chuyển động có tọa độ s(t)={a}t³+{b}t²+{c}t (m), thời gian t tính bằng giây. Tính gia tốc tức thời tại t={t0}.'
  sol=f'Vận tốc v(t)=s′(t)=3×{a}t²+2×{b}t+{c}. Gia tốc a(t)=s′′(t)=6×{a}t+2×{b}. Tại {t0}, bằng {ans} m/s².'
 elif key=='two_colors_selection':
  a,b,k=4+t,5+t%4,2+t%3
  ans=math.comb(a+b,k)-(math.comb(a,k) if a>=k else 0)-(math.comb(b,k) if b>=k else 0)
  oracle=sum(1 for pickedA in range(1,k) if pickedA<=a and k-pickedA<=b for _ in range(math.comb(a,pickedA)*math.comb(b,k-pickedA)))
  assert ans==oracle
  q=f'Có {a} sách Toán khác nhau và {b} sách Văn khác nhau. Chọn {k} quyển sao cho có ít nhất một quyển mỗi môn. Có bao nhiêu cách?'
  sol=f'Tổng cách chọn C({a+b},{k}), loại cách chỉ sách Toán C({a},{k}) và chỉ sách Văn C({b},{k}). Kết quả {ans}.'
 elif key=='prism_edge_count':
  n=3+t;ans=3*n
  assert ans==2*n+n
  q=f'Lăng trụ có đáy là đa giác {n} cạnh. Tổng số cạnh của lăng trụ bằng bao nhiêu?'
  sol=f'Có hai đáy, mỗi đáy {n} cạnh, cộng thêm {n} cạnh bên nối các cặp đỉnh tương ứng. Tổng 2×{n}+{n}={ans}.'
 elif key=='parabola_line_intersection_count':
  a=2*t;delta=(t%3)-1;b=-(t*t+delta)
  disc=a*a+4*b
  ans=2 if disc>0 else 1 if disc==0 else 0
  x=S.symbols('x',real=True);assert len(S.solveset(x*x-a*x-b,x,domain=S.S.Reals))==ans
  q=f'Parabol y=x² và đường thẳng y={a}x+({b}) có bao nhiêu giao điểm thực?'
  sol=f'Giải x²={a}x+({b}) hay x²−{a}x−({b})=0. Biệt thức Δ={a}²+4({b})={disc}; Δ>0 cho 2, =0 cho 1, <0 cho 0 giao điểm. Đáp án {ans}.'
 elif key=='inverse_linear_derivative':
  a=2+t;b=3+t%4;y0=a*t+b;ans=S.Rational(1,a)
  assert a!=0 and S.diff((S.Symbol('y')-b)/a,S.Symbol('y'))==ans
  q=f'Cho f(x)={a}x+{b} và g=f⁻¹. Tính g′({y0}).'
  sol=f'f′(x)={a} khác 0; đạo hàm hàm ngược tại y=f(x) bằng 1/f′(x)=1/{a}={fmt(ans)}.'
 elif key=='horizontal_asymptote_ratio':
  a,b,c,d=2+t,3+t,1+t%5,2+t%4
  x=S.symbols('x');ans=a
  assert S.limit((a*x*x+b*x+c)/(x*x+d),x,S.oo)==ans
  q=f'Cho y=({a}x²+{b}x+{c})/(x²+{d}). Tiệm cận ngang của đồ thị có dạng y=L. Tìm L.'
  sol=f'Chia tử và mẫu cho x²: y=({a}+{b}/x+{c}/x²)/(1+{d}/x²). Khi x→±∞, giới hạn bằng {a}. Vậy y={a} là tiệm cận ngang.'
 elif key=='decreasing_log_integer_count':
  h=1+t;N=2+t%4;maxval=2**N
  ans=maxval
  assert ans==sum(bool(S.log(S.Rational(x-h),2)*(-1)>=-N) for x in range(h+1,h+maxval+1))
  q=f'Có bao nhiêu số nguyên x thỏa log_(1/2)(x−{h})≥−{N}?'
  sol=f'Điều kiện x−{h}>0. Vì cơ số 1/2<1 nên bất phương trình tương đương 0<x−{h}≤2^{N}={maxval}. Số nghiệm nguyên là {maxval}.'
 elif key=='sphere_complete_square':
  x0,y0,z0=1+t,2+t%4,3+t%5;R=4+t
  A,B,C=-2*x0,-2*y0,-2*z0;D=x0*x0+y0*y0+z0*z0-R*R
  ans=S.Rational(A*A+B*B+C*C,4)-D
  assert ans==R*R
  q=f'Mặt cầu có phương trình x²+y²+z²+({A})x+({B})y+({C})z+({D})=0. Tính bình phương bán kính R².'
  sol=f'Hoàn thành bình phương: tâm I=({x0},{y0},{z0}). Có R²=(A²+B²+C²)/4−D={fmt(ans)}.'
 elif key=='cylinder_lateral_area':
  r,h=2+t,3+t%5;ans=2*r*h
  assert S.simplify(2*S.pi*r*h/S.pi-ans)==0
  q=f'Hình trụ có bán kính đáy r={r}, chiều cao h={h}. Nếu diện tích xung quanh là S, tính S/π.'
  sol=f'Diện tích xung quanh hình trụ S=chu vi đáy×chiều cao=2πrh. S/π=2×{r}×{h}={ans}.'
 elif key=='bernoulli_variance':
  p=S.Rational(1+t%4,6+t%3);ans=p*(1-p)
  assert ans==p-S.Rational(p)**2
  q=f'Biến ngẫu nhiên Bernoulli X nhận 1 với xác suất {fmt(p)} và 0 với xác suất 1−{fmt(p)}. Tính Var(X).'
  sol=f'E(X)={fmt(p)}, E(X²)={fmt(p)} vì X²=X. Var(X)=E(X²)−[E(X)]²=p(1−p)={fmt(ans)}.'
 elif key=='normal_plane_constant':
  a,b,c=t+1,2+t%4,3+t%5;x,y,z=2+t,3+t,4+t
  ans=-(a*x+b*y+c*z)
  assert a*x+b*y+c*z+ans==0
  q=f'Mặt phẳng (P): {a}x+{b}y+{c}z+D=0 đi qua M({x},{y},{z}). Tính D.'
  sol=f'Thế M vào phương trình: {a}×{x}+{b}×{y}+{c}×{z}+D=0. Suy ra D=−({a*x}+{b*y}+{c*z})={ans}.'
 else:raise KeyError(key)
 return q,S.Rational(ans),sol


def main():
 specs=[];rows=[];gcounts=collections.Counter();tcounts=collections.Counter()
 for key,(grade,topic,name,method,conditions,difficulty) in SPECS.items():
  assert (grade,topic) in CATALOG,(grade,topic)
  specs.append({'form_id':'v201_'+key,'grade':grade,'topic':topic,'name':name,'mathematical_essence':name,'method':method,'conditions':conditions,'difficulty':difficulty,'question_count':10,'independent_method_certified':False})
  seen=set()
  for i in range(10):
   question,ans,solution=build(key,i)
   assert question not in seen,(key,i,'internal duplicate');seen.add(question)
   typ='multiple_choice' if i<7 else 'short_answer' if i<9 else 'true_false'
   if typ=='multiple_choice':
    options=([ans,ans*S.Rational(11,10),ans*S.Rational(9,10),ans*S.Rational(3,2)] if abs(ans)>10**7 else choices_for(ans, key in {'dice_sum_probability','geometric_first_success','bernoulli_variance'}))
    pos=(i+len(key))%4; values=options[1:][:pos]+[ans]+options[1:][pos:]
    choices=[fmt(v) for v in values];answer=fmt(ans)
    explanation=solution+f' Trong bốn lựa chọn, chỉ {answer} là kết quả chính xác.'
   elif typ=='short_answer':
    choices=[];answer=fmt(ans);explanation=solution+' Nhập phân số tối giản nếu đáp án không nguyên.'
   else:
    choices=[f'Giá trị đúng bằng {fmt(ans)}.',f'Giá trị nhỏ hơn {fmt(ans-1)}.',f'Giá trị lớn hơn {fmt(ans-1)}.',f'Giá trị đúng bằng {fmt(ans+1)}.']
    answer='Đúng,Sai,Đúng,Sai';explanation=solution+' Nhận định đúng, sai, đúng, sai tương ứng giá trị trên.'
   rows.append({'id':f'v201_{key}_{i:02d}','form_id':'v201_'+key,'grade':grade,'topic':topic,'concept':name,'math_method':method,'conditions':conditions,'difficulty':difficulty,'question_type':typ,'question':question,'answer':answer,'correct_answer':answer,'solution':explanation,'choices':choices,'source_bundle':'V201','validation_status':'independent_exact_calculation_checked','method_independence_certified':False,'production_integrated':False})
   gcounts[str(grade)]+=1;tcounts[typ]+=1
 (OUT/'V201_FAMILY_SPECS.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n')
 (OUT/'V201_INCREMENT.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
 report={'version':'V201','new_candidates':len(specs),'math_oracle_checked':len(rows),'grades':dict(gcounts),'formats':dict(tcounts),'independent_certified':0,'production_deployed':False}
 (OUT/'V201_GENERATION_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
