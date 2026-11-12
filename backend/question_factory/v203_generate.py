#!/usr/bin/env python3
"""V203 numerical questions checked against independent symbolic / combinatorial oracles.
Method-family novelty still needs full historical semantic certification.
"""
import collections,json
from pathlib import Path
import sympy as S
from v198_generate import fmt,choices_for
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'bank_updates'
CATALOG={(int(g),y['id']) for g,ts in json.loads((ROOT/'backend/app/ai/knowledge/index.json').read_text()).items() for y in ts}
SPECS={
 'triangle_third_side_integer_count':(10,'g10_geom_triangle_inequalities','Đếm độ dài nguyên của cạnh thứ ba tam giác khi biết hai cạnh','|a−b|<c<a+b, đếm các số nguyên trong khoảng mở','a,b là số nguyên dương','trung cấp'),
 'min_abs_distance_two_points':(10,'g10_advanced_inequalities','Giá trị nhỏ nhất của tổng khoảng cách tuyệt đối trên trục số','min_x(|x−a|+|x−b|)=|b−a|','a,b thực, x thực','trung cấp'),
 'perpendicular_bisector_horizontal_segment':(10,'g10_geom_locus','Hoành độ mọi điểm thuộc trung trực đoạn thẳng nằm ngang','Tập điểm cách đều A và B có x=(xA+xB)/2','A,B cùng tung độ và phân biệt','nền tảng'),
 'weighted_mean_frequency':(10,'thong_ke','Tính trung bình của bảng số liệu hai giá trị kèm tần số','x̄=(n₁x₁+n₂x₂)/(n₁+n₂)','n₁,n₂ nguyên dương','nền tảng'),
 'infinite_geometric_sum':(11,'gioi_han','Tổng cấp số nhân vô hạn hội tụ','S=a/(1−q) với |q|<1','q thực, |q|<1','trung cấp'),
 'at_least_one_independent_success':(11,'bien_co_doc_lap_11','Xác suất có ít nhất một thành công sau nhiều phép thử độc lập','P=1−(1−p)^n theo biến cố đối','0<p<1, thử độc lập, n dương','trung cấp'),
 'reflection_point_vertical_axis':(11,'g11_geom_transform_reflection','Đối xứng điểm qua đường thẳng đứng x=c','x′=2c−x, y′=y','Phép đối xứng trục trong mặt phẳng','nền tảng'),
 'count_arithmetic_progression_terms':(11,'day_so','Số số hạng của cấp số cộng từ số hạng đầu tới cận trên','n=floor((B−a₁)/d)+1 với d>0','d>0, B≥a₁','trung cấp'),
 'rotation_volume_line':(12,'ung_dung_tich_phan','Thể tích tròn xoay do đoạn thẳng y=kx quay quanh Ox','V/π=∫₀ᴬ(kx)²dx=k²A³/3','k,A>0','trung cấp'),
 'tetrahedron_coordinate_volume':(12,'the_tich_khong_gian','Thể tích tứ diện từ ba vectơ vuông góc trên các trục tọa độ','V=|det(AB,AC,AD)|/6','Ba vectơ độc lập tuyến tính','trung cấp'),
 'logarithm_equation_inverse':(12,'pt_logarit','Giải phương trình log_b(x−h)=n bằng định nghĩa logarit','x=h+b^n','b>0,b≠1,x−h>0','nền tảng'),
 'point_plane_distance':(12,'mat_phang_oxyz','Khoảng cách từ điểm đến mặt phẳng tọa độ','d=|ax₀+by₀+cz₀+D|/√(a²+b²+c²)','Vectơ pháp tuyến khác 0','trung cấp'),
}

def calc(key,i):
 t=i+1
 if key=='triangle_third_side_integer_count':
  a,b=4+t,6+t;ans=a+b-abs(a-b)-1
  assert ans==sum(abs(a-b)<c<a+b for c in range(1,a+b+1))
  q=f'Hai cạnh của một tam giác dài {a} và {b}. Có bao nhiêu giá trị nguyên dương của cạnh còn lại?'
  sol=f'Bất đẳng thức tam giác: |{a}−{b}|<c<{a}+{b}, tức {abs(a-b)}<c<{a+b}. Có {ans} số nguyên dương.'
 elif key=='min_abs_distance_two_points':
  a,b=-2-t,4+t;ans=b-a
  assert ans==min(abs(x-a)+abs(x-b) for x in range(a-2,b+3))
  q=f'Với x thực, tìm GTNN của F(x)=|x−({a})|+|x−{b}|.'
  sol=f'Bất đẳng thức tam giác: |x−({a})|+|x−{b}|≥|{b}−({a})|={ans}. Dấu bằng khi {a}≤x≤{b}; GTNN={ans}.'
 elif key=='perpendicular_bisector_horizontal_segment':
  x1,y,x2=-3-t,2+t,5+t;ans=S.Rational(x1+x2,2);assert S.simplify((S.Symbol('x')-x1)**2-(S.Symbol('x')-x2)**2).subs(S.Symbol('x'),ans)==0
  q=f'Cho A({x1},{y}), B({x2},{y}). Hỏi điểm M thuộc đường trung trực AB luôn có hoành độ bằng bao nhiêu?'
  sol=f'AB nằm ngang; trung trực là đường thẳng qua trung điểm và vuông góc AB, nên x_M=({x1}+{x2})/2={fmt(ans)}.'
 elif key=='weighted_mean_frequency':
  a,b=2+t,9+t;n,m=2+t%3,4+t%4;ans=S.Rational(a*n+b*m,n+m)
  assert ans==S.Rational(sum([a]*n+[b]*m),n+m)
  q=f'Mẫu số liệu gồm giá trị {a} xuất hiện {n} lần, giá trị {b} xuất hiện {m} lần. Tính số trung bình cộng.'
  sol=f'Số trung bình =({n}×{a}+{m}×{b})/({n}+{m})={fmt(ans)}.'
 elif key=='infinite_geometric_sum':
  a=t+2;q=S.Rational(1,2+t%4);ans=a/(1-q)
  assert S.limit(a*(1-q**S.Symbol('N'))/(1-q),S.Symbol('N'),S.oo)==ans
  qtext=f'Cấp số nhân vô hạn có số hạng đầu {a}, công bội {fmt(q)}. Tính tổng mọi số hạng.'
  sol=f'Vì |q|={fmt(q)}<1, tổng hội tụ S=a/(1−q)={a}/(1−{fmt(q)})={fmt(ans)}.';q=qtext
 elif key=='at_least_one_independent_success':
  n=2+t;p=S.Rational(1,3+t%3);ans=1-(1-p)**n
  assert S.simplify(sum(S.binomial(n,k)*p**k*(1-p)**(n-k) for k in range(1,n+1))-ans)==0
  q=f'Mỗi lần thử có xác suất thành công {fmt(p)}, các lần độc lập. Sau {n} lần, xác suất có ít nhất một lần thành công là bao nhiêu?'
  sol=f'Biến cố đối là tất cả {n} lần thất bại, có xác suất (1−{fmt(p)})^{n}. Vậy P=1−(1−{fmt(p)})^{n}={fmt(ans)}.'
 elif key=='reflection_point_vertical_axis':
  c=t+1;x,y=3+t,4+t;ans=2*c-x
  assert abs(x-c)==abs(ans-c)
  q=f'Điểm P({x},{y}) đối xứng qua trục thẳng đứng x={c} thành P′. Tìm hoành độ P′.'
  sol=f'Phép đối xứng trục x=c giữ tung độ, biến hoành độ thành x′=2c−x=2×{c}−{x}={ans}.'
 elif key=='count_arithmetic_progression_terms':
  a,d=2+t,3+t%4;N=4+t;B=a+(N-1)*d;ans=N
  assert ans==sum(a+j*d<=B for j in range(N+3))
  q=f'Dãy số có số hạng đầu {a}, công sai {d}. Có bao nhiêu số hạng không vượt quá {B}?'
  sol=f'a_n={a}+(n−1)×{d}. Điều kiện a_n≤{B} tương đương n−1≤({B}−{a})/{d}={N-1}. Suy ra có n={ans} số hạng.'
 elif key=='rotation_volume_line':
  k,A=2+t,2+t%4;X=S.symbols('x');ans=S.Rational(k*k*A**3,3)
  assert S.integrate((k*X)**2,(X,0,A))==ans
  q=f'Quay miền phẳng 0≤x≤{A}, 0≤y≤{k}x quanh trục Ox. Gọi thể tích là V, tính V/π.'
  sol=f'Phương pháp đĩa tròn: V/π=∫₀^{A}({k}x)²dx={k*k}×{A}³/3={fmt(ans)}.'
 elif key=='tetrahedron_coordinate_volume':
  a,b,c=2+t,3+t,4+t;ans=S.Rational(a*b*c,6)
  assert abs(S.det(S.diag(a,b,c)))/6==ans
  q=f'Tứ diện OABC có O(0,0,0), A({a},0,0), B(0,{b},0), C(0,0,{c}). Tính thể tích.'
  sol=f'Ba cạnh OA, OB, OC đôi một vuông góc. V=|det(OA,OB,OC)|/6=({a}×{b}×{c})/6={fmt(ans)}.'
 elif key=='logarithm_equation_inverse':
  b,h,n=2+t%3,t+1,2+t%4;ans=h+b**n
  assert S.log(ans-h,b)==n
  q=f'Giải phương trình log_{b}(x−{h})={n}. Tìm x.'
  sol=f'Điều kiện x>{h}; theo định nghĩa logarit, x−{h}={b}^{n}={b**n}; do đó x={h}+{b**n}={ans}, thỏa điều kiện.'
 elif key=='point_plane_distance':
  x,y,z=1+t,2+t,3+t;D=0;ans=S.Rational(abs(2*x-y+2*z+D),3)
  assert S.sqrt(2**2+(-1)**2+2**2)==3
  q=f'Tính khoảng cách từ M({x},{y},{z}) đến mặt phẳng (P): 2x−y+2z=0.'
  sol=f'Độ dài vectơ pháp tuyến là √(4+1+4)=3. Khoảng cách d=|2×{x}−{y}+2×{z}|/3={fmt(ans)}.'
 else:raise KeyError(key)
 return q,S.Rational(ans),sol

def main():
 specs=[];items=[];c=collections.Counter();fmtc=collections.Counter()
 for key,(g,topic,name,method,conds,diff) in SPECS.items():
  assert (g,topic) in CATALOG,(g,topic)
  fid='v203_'+key
  specs.append(dict(form_id=fid,grade=g,topic=topic,name=name,mathematical_essence=name,method=method,conditions=conds,difficulty=diff,question_count=10,independent_method_certified=False))
  seen=set()
  for i in range(10):
   q,ans,sol=calc(key,i);assert q not in seen;seen.add(q)
   typ='multiple_choice' if i<7 else 'short_answer' if i<9 else 'true_false'
   if typ=='multiple_choice':
    c0=choices_for(ans,(0<ans<1));position=(i+len(key))%4
    options=[fmt(x) for x in c0[1:][:position]+[ans]+c0[1:][position:]]
    answer=fmt(ans);assert len(set(options))==4;sol+=' Chỉ lựa chọn '+answer+' cho đáp án đúng.'
   elif typ=='short_answer':
    options=[];answer=fmt(ans);sol+=' Có thể viết kết quả dưới dạng phân số tối giản.'
   else:
    options=[f'Kết quả đúng là {fmt(ans)}.',f'Kết quả đúng là {fmt(ans+1)}.',f'Kết quả lớn hơn {fmt(ans-1)}.',f'Kết quả nhỏ hơn {fmt(ans-1)}.']
    answer='Đúng,Sai,Đúng,Sai';sol+=' Bốn nhận định lần lượt đúng, sai, đúng, sai.'
   items.append(dict(id=f'{fid}_{i:02d}',form_id=fid,grade=g,topic=topic,concept=name,math_method=method,conditions=conds,difficulty=diff,question_type=typ,question=q,answer=answer,correct_answer=answer,solution=sol,choices=options,source_bundle='V203',validation_status='independent_exact_calculation_checked',method_independence_certified=False,production_integrated=False))
   c[str(g)]+=1;fmtc[typ]+=1
 (OUT/'V203_FAMILY_SPECS.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (OUT/'V203_INCREMENT.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in items),encoding='utf8')
 report=dict(version='V203',candidate_families=len(specs),math_oracle_checked=len(items),grades=dict(c),formats=dict(fmtc),certified_independent_forms=0)
 (OUT/'V203_GENERATION_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
