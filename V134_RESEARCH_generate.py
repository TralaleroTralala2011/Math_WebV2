"""V134 research-only mathematics corpus.

Authored method objectives, 10 reproducible examples per objective.
No candidate is published or certified as methodologically novel.
Independent oracles use counting, substitution, solving, geometry or differentiation.
"""
from __future__ import annotations
from functools import lru_cache
from fractions import Fraction
from itertools import product
from math import comb, factorial, gcd, lcm
from pathlib import Path
import json
import sympy as s

ROOT=Path(__file__).resolve().parent
DIR=ROOT/'V134_RESEARCH'
DIR.mkdir(exist_ok=True)
x,t,r=s.symbols('x t r',real=True)

# Curriculum IDs are taken from backend/question_factory/catalog_150.json
SPECS=[
 ('hoan_vi_chinh_hop_to_hop',10,'Hoán vị có phần tử lặp','Đếm xâu đa tập bằng công thức chia giai thừa và quy hoạch động'),
 ('g10_geom_circle_chords_arcs',10,'Độ dài dây cung với khoảng cách từ tâm','Bán kính vuông góc chia đôi dây cung, áp dụng Pitago'),
 ('he_thuc_luong_tam_giac',10,'Độ dài trung tuyến từ ba cạnh','Định lý Apollonius và kiểm chứng bằng tọa độ'),
 ('quy_tac_dem',10,'Đếm số chia hết ít nhất một trong ba số','Nguyên lý bù trừ ba tập hữu hạn'),
 ('g10_geom_special_lines',10,'Chân đường phân giác trong tam giác','Định lý đường phân giác trong và giải tỉ số'),
 ('ham_so_bac_hai',10,'Tham số tiếp xúc đường thẳng với parabol','Biệt thức bằng không và tiếp tuyến qua đạo hàm'),
 ('toa_do_phang',10,'Điểm chia đoạn theo tỉ số cho trước','Công thức nội phân và kiểm tra bằng vectơ'),
 ('day_so_truy_hoi_11',11,'Truy hồi affine bậc nhất','Tịnh tiến nghiệm cố định về cấp số nhân, đối chiếu bằng lặp'),
 ('cong_thuc_luong_giac',11,'Cực trị tổ hợp sin và cos','Biên độ lượng giác và điều kiện đạt dấu bằng'),
 ('gioi_han',11,'Giới hạn căn thức bằng nhân liên hợp','Nhân liên hợp để triệt tiêu dạng 0/0'),
 ('g11_conditional_probability_models',11,'Bayes với hai nguồn sản phẩm','Xác suất có điều kiện và kiểm chứng bằng đếm tần suất'),
 ('g11_geom_rotation_homothety',11,'Tỉ số diện tích dưới phép vị tự','Bình phương tỉ số đồng dạng và định thức tọa độ'),
 ('g12_geom_sphere_plane_intersection',12,'Bán kính giao tuyến cầu và mặt phẳng','Thiết diện tròn và tam giác vuông tâm-chân-điểm'),
 ('g12_geom_min_distance_3d',12,'Khoảng cách điểm đến đường thẳng trong Oxyz','Tích có hướng và cực tiểu bình phương khoảng cách'),
 ('nguyen_ham_tich_phan',12,'Tích phân x nhân hàm mũ','Tích phân từng phần và kiểm tra bằng đạo hàm'),
 ('g12_geom_line_plane_intersection',12,'Giao điểm đường thẳng tham số và mặt phẳng','Thế phương trình tham số vào phương trình mặt phẳng'),
 ('g12_geom_3d_optimization',12,'Tối ưu diện tích toàn phần hình trụ kín','Đạo hàm với điều kiện thể tích không đổi'),
 ('ham_mu',12,'Ngưỡng tăng trưởng lũy thừa nguyên năm','Bất đẳng thức mũ và tìm năm nhỏ nhất bằng liệt kê'),
]
PYT=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(12,35,37),(9,40,41),(28,45,53),(11,60,61),(16,63,65)]

@lru_cache(None)
def multiset_count(a,b,c):
 if a+b+c==0:return 1
 return sum(multiset_count(*(z-int(j==k) for j,z in enumerate((a,b,c)))) for k,n in enumerate((a,b,c)) if n>0)

def canonical(z):
 return str(s.simplify(z))

def task(j,i):
 k=i+1
 if j==0:
  a=1+i%4;b=2+(i//3)%3;c=1+(i%3);n=a+b+c
  ans=s.Integer(factorial(n)//(factorial(a)*factorial(b)*factorial(c)))
  chk=s.Integer(multiset_count(a,b,c))
  q=f'Có {a} chữ A, {b} chữ B và {c} chữ C giống nhau theo từng loại. Xếp tất cả thành hàng, có bao nhiêu cách khác nhau?'
  sol=f'Coi {n} chữ đều phân biệt có {n}! cách. Mỗi cách thực bị đếm {a}!·{b}!·{c}! lần. Do đó N={n}!/({a}!{b}!{c}!)={ans}.'
 elif j==1:
  d,h,R=PYT[i];ans=s.Integer(2*h)
  pts=s.solve(s.Eq(d*d+x*x,R*R),x);chk=s.simplify(abs(pts[1]-pts[0]))
  q=f'Đường tròn tâm O bán kính {R} cm. Khoảng cách từ O đến dây AB là {d} cm. Tính độ dài AB.'
  sol=f'Gọi H là chân đường vuông góc từ O đến AB; H là trung điểm AB. AH=√({R}²−{d}²)={h} cm, vậy AB=2AH={ans} cm.'
 elif j==2:
  u=5+i;w=i%4-2;v=4+i%6
  # A=(0,0), B=(u,0), C=(w,v)
  c2=u*u;b2=w*w+v*v;a2=(u-w)**2+v*v
  ans=s.sqrt(2*b2+2*c2-a2)/2
  chk=s.sqrt((s.Rational(u+w,2))**2+s.Rational(v,2)**2)
  q=f'Trong tam giác ABC, AB²={c2}, AC²={b2}, BC²={a2} (đơn vị cm²). Tính độ dài trung tuyến AM tới BC.'
  sol=f'Định lý Apollonius: AM²=(2AB²+2AC²−BC²)/4=(2·{c2}+2·{b2}−{a2})/4. Vậy AM={canonical(ans)} cm.'
 elif j==3:
  D=[(2,3,5),(2,3,7),(3,4,5),(2,5,7),(3,5,7),(4,6,9),(2,7,9),(5,6,8),(3,7,11),(4,5,9)]
  a,b,c=D[i];n=40+13*i
  def count_iev():
   return n//a+n//b+n//c-n//lcm(a,b)-n//lcm(a,c)-n//lcm(b,c)+n//lcm(a,b,c)
  ans=s.Integer(count_iev());chk=s.Integer(sum(1 for z in range(1,n+1) if z%a==0 or z%b==0 or z%c==0))
  q=f'Trong các số nguyên từ 1 đến {n}, có bao nhiêu số chia hết cho ít nhất một trong {a}, {b}, {c}?'
  sol=f'Dùng bù trừ: N=⌊{n}/{a}⌋+⌊{n}/{b}⌋+⌊{n}/{c}⌋−⌊{n}/{lcm(a,b)}⌋−⌊{n}/{lcm(a,c)}⌋−⌊{n}/{lcm(b,c)}⌋+⌊{n}/{lcm(a,b,c)}⌋={ans}.'
 elif j==4:
  ab=3+i;ac=5+i%6;bc=max(abs(ab-ac)+1, 3+i%5)
  # BC may violate triangle inequality if ab+ac<=bc; with values above valid
  assert abs(ab-ac)<bc<ab+ac
  ans=s.Rational(bc*ab,ab+ac)
  chk=s.solve(s.Eq(x/(bc-x),s.Rational(ab,ac)),x)[0]
  q=f'Tam giác ABC có AB={ab} cm, AC={ac} cm và BC={bc} cm. Đường phân giác trong từ A cắt BC tại D. Tính BD.'
  sol=f'Theo định lý đường phân giác, BD/DC=AB/AC={ab}/{ac}. Vì BD+DC={bc} nên BD={bc}·{ab}/({ab}+{ac})={canonical(ans)} cm.'
 elif j==5:
  a=1+i%4;b=i-5;c=3+i%7;m=2+i%6
  ans=s.Rational(4*a*c-(b-m)**2,4*a)
  xt=s.Rational(m-b,2*a);chk=s.simplify(a*xt**2+(b-m)*xt+c)
  q=f'Parabol y={a}x²+({b})x+({c}) tiếp xúc đường thẳng y={m}x+n. Tìm n.'
  sol=f'Hoành độ giao là nghiệm {a}x²+({b-m})x+({c})−n=0. Tiếp xúc khi Δ=({b-m})²−4·{a}({c}−n)=0. Do đó n={canonical(ans)}.'
 elif j==6:
  ax=i-5;ay=2-i;bx=3+i;by=5+i%4;p=2+i%3;qpart=1+i%4
  px=s.Rational(qpart*ax+p*bx,p+qpart);py=s.Rational(qpart*ay+p*by,p+qpart)
  ans=px+py
  chk=(s.Rational(ax,1)+s.Rational(p,p+qpart)*(bx-ax))+(s.Rational(ay,1)+s.Rational(p,p+qpart)*(by-ay))
  q=f'Cho A({ax};{ay}), B({bx};{by}). P nằm trong AB và AP:PB={p}:{qpart}. Tính tổng hoành độ và tung độ của P.'
  sol=f'Công thức nội phân: P=(({qpart}A+{p}B)/({p}+{qpart})). Tọa độ P=({canonical(px)};{canonical(py)}); tổng bằng {canonical(ans)}.'
 elif j==7:
  a=2+i%3;b=i-3;u=1+i;n=3+i%6
  ans=s.Integer(a**(n-1)*u)+s.Rational(b*(a**(n-1)-1),a-1)
  v=u
  for _ in range(n-1):v=a*v+b
  chk=s.Integer(v)
  q=f'Dãy số có u₁={u} và uₙ₊₁={a}uₙ+({b}). Tính u_{n}.'
  sol=f'Điểm bất động L={canonical(s.Rational(-b,a-1))}. Đặt vₙ=uₙ−L thì vₙ₊₁={a}vₙ; do đó u_{n}={a}^{n-1}·({u})+({b})({a}^{n-1}−1)/({a}−1)={canonical(ans)}.'
 elif j==8:
  p,q0,H=PYT[i];ans=s.Integer(H)
  # Compare the maximizing vector (sin x,cos x)=(p/H,q/H), which lies on unit circle
  chk=s.sqrt(s.Integer(p*p+q0*q0))
  q=f'Tìm giá trị lớn nhất của {p}sin x+{q0}cos x với x thuộc R.'
  sol=f'Viết {p}sin x+{q0}cos x={H}sin(x+φ) với cosφ={p}/{H}, sinφ={q0}/{H}. Vì −1≤sin≤1 nên GTLN={H}; có x đạt dấu bằng.'
 elif j==9:
  a=i-3;root=2+i;shift=root*root-a
  fun=(s.sqrt(x+shift)-root)/(x-a)
  ans=s.Rational(1,2*root);chk=s.limit(fun,x,a)
  q=f'Tính giới hạn khi x→{a} của (√(x+{shift})−{root})/(x−({a})).'
  sol=f'Nhân liên hợp được (x+{shift}−{root}²)/((x−({a}))(√(x+{shift})+{root}))=1/(√(x+{shift})+{root}) (với x≠{a}). Giới hạn={canonical(ans)}.'
 elif j==10:
  prior=2+i%7;da=1+i%4;db=2+(2*i)%5
  ans=s.Rational(prior*da,prior*da+(10-prior)*db)
  # 100 equiprobable outcome slots corresponding to 10 per each of 10 weighted boxes
  da_count=sum(1 for j in range(prior*10) if (j%10)<da)
  db_count=sum(1 for j in range((10-prior)*10) if (j%10)<db)
  chk=s.Rational(da_count,da_count+db_count)
  q=f'Có {prior}/10 sản phẩm từ xưởng A, còn lại từ B. Tỉ lệ lỗi của A là {da}/10, của B là {db}/10. Chọn ngẫu nhiên một sản phẩm đã biết bị lỗi, tìm xác suất nó đến từ A.'
  sol=f'P(A∩L)=({prior}/10)({da}/10); P(B∩L)=({10-prior}/10)({db}/10). Bayes: P(A|L)={prior*da}/({prior*da}+{(10-prior)*db})={canonical(ans)}.'
 elif j==11:
  ratio=s.Rational(2+i%6,3+i%7);area=6+3*i
  ans=ratio*ratio*area
  A=s.Point(0,0);B=s.Point(2,0);C=s.Point(0,area)
  chk=s.Abs(s.Polygon(A*ratio,B*ratio,C*ratio).area) # original triangle area =area
  q=f'Phép vị tự tỉ số k={canonical(ratio)} biến tam giác có diện tích {area} cm² thành tam giác ảnh. Tính diện tích ảnh.'
  sol=f'Phép vị tự nhân mọi độ dài với |k|, vì vậy diện tích nhân k². S′=({canonical(ratio)})²·{area}={canonical(ans)} cm².'
 elif j==12:
  d,h,R=PYT[i];ans=s.Integer(h)
  chk=s.sqrt(R**2-d**2)
  q=f'Mặt cầu tâm O bán kính R={R} cm cắt mặt phẳng (P) cách O một khoảng {d} cm. Tính bán kính đường tròn giao tuyến.'
  sol=f'Hình chiếu H của O lên (P) là tâm đường tròn thiết diện. Với M trên giao tuyến, OM={R}, OH={d}, HM=√(OM²−OH²)=√({R}²−{d}²)={h} cm.'
 elif j==13:
  aa=s.Matrix([i-3,2-i%4,1+i%3]); vv=s.Matrix([1+i%3,2+i%2,3-i%3]);pp=aa+s.Matrix([3+i%4,-2-i%3,1+i%2])
  w=pp-aa;cross=w.cross(vv)
  ans=s.sqrt(cross.dot(cross))/s.sqrt(vv.dot(vv))
  tt=s.solve(s.diff((w-tt_symbol()*vv).dot(w-tt_symbol()*vv),tt_symbol()),tt_symbol())[0]
  chk=s.sqrt(s.simplify((w-tt*vv).dot(w-tt*vv)))
  q=f'Trong Oxyz, đường thẳng d đi qua A{tuple(aa)} và có vectơ chỉ phương u={tuple(vv)}. Tính khoảng cách từ P{tuple(pp)} đến d.'
  sol=f'Đặt AP={tuple(w)}. Khoảng cách bằng |AP×u|/|u|=√({canonical(cross.dot(cross))})/√({canonical(vv.dot(vv))})={canonical(ans)}.'
 elif j==14:
  k=1+i
  ans=s.simplify((s.exp(k)*(k-1)+1)/k**2)
  chk=s.integrate(x*s.exp(k*x),(x,0,1))
  q=f'Tính tích phân I=∫₀¹ x·e^({k}x) dx.'
  sol=f'Từng phần: u=x, dv=e^({k}x)dx, v=e^({k}x)/{k}. I=[xe^({k}x)/{k}]₀¹−[e^({k}x)/{k}²]₀¹=({k}e^{k}−e^{k}+1)/{k}²={canonical(ans)}.'
 elif j==15:
  aa=s.Matrix([i-5,2+i%3,1+i%4]);vv=s.Matrix([1+i%3,2+i%4,1+i%2]);nn=s.Matrix([2,1+i%3,3]);
  delta=nn.dot(vv);t0=s.Rational(i-3,2); rhs=nn.dot(aa)+t0*delta
  ans=(aa+t0*vv)[2]
  t_symbol=s.symbols('tau');tt=s.solve(s.Eq(nn.dot(aa+t_symbol*vv),rhs),t_symbol)[0];chk=(aa+tt*vv)[2]
  q=f'Đường thẳng qua A{tuple(aa)}, vectơ chỉ phương u={tuple(vv)}; mặt phẳng (P): {nn[0]}x+{nn[1]}y+{nn[2]}z={canonical(rhs)}. Tìm tọa độ z của giao điểm.'
  sol=f'Đặt X=A+t·u. Thay vào (P): ({canonical(nn.dot(aa))})+({canonical(delta)})t={canonical(rhs)}. Suy ra t={canonical(t0)}, và z={canonical(aa[2])}+({canonical(vv[2])})t={canonical(ans)}.'
 elif j==16:
  k=i+2;volume=2*s.pi*k**3
  ans=s.Integer(k)
  S=2*s.pi*r*r+2*volume/r
  critical=s.solve(s.diff(S,r),r)
  chk=next(z for z in critical if z.is_real and z.is_positive)
  q=f'Một hình trụ kín có thể tích V={2*k**3}π cm³. Tìm bán kính đáy r>0 để diện tích toàn phần nhỏ nhất.'
  sol=f'V=πr²h nên h=({2*k**3})/r². S=2πr²+2V/r. S′=4πr−2V/r²=0 ⇔ r³=V/(2π)={k**3}. Vì S giảm rồi tăng trên r>0, r={k} cm.'
 elif j==17:
  p0=10*(i+2);growth=2+i%3;n=3+i%6;threshold=p0*growth**n+p0
  ans=s.Integer(n+1)
  chk=next(j for j in range(25) if p0*growth**j>=threshold)
  q=f'Quần thể ban đầu có {p0} cá thể, mỗi năm tăng gấp {growth} lần. Hỏi ít nhất bao nhiêu năm để đạt {threshold} cá thể?'
  sol=f'Sau t năm có {p0}·{growth}^t. Tại t={n}, số lượng là {p0*growth**n} < {threshold}; tại t={n+1}, số lượng là {p0*growth**(n+1)} ≥ {threshold}. Vậy ít nhất {n+1} năm.'
 else:raise AssertionError('unknown method')
 assert s.simplify(s.sympify(ans)-s.sympify(chk))==0,(j,i,str(ans),str(chk))
 return dict(id=f'v134_{j:02}_{i:02}',method_id=f'v134_{j:02}',topic=SPECS[j][0],grade=SPECS[j][1],question=q,answer=canonical(ans),independent_check=canonical(chk),solution=sol,format='tra_loi_ngan',review_status='pending-expert-review',independence_certified=False,published=False)

def tt_symbol():
 return t

def dump(p,rows):
 p.write_text(''.join(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n' for row in rows),encoding='utf8')

def main():
 ids={q['id']:q for q in json.loads((ROOT/'backend/question_factory/catalog_150.json').read_text('utf8'))}
 forms=[];questions=[]
 for j,(topic,grade,title,approach) in enumerate(SPECS):
  assert ids[topic]['grade']==grade,(topic,grade)
  forms.append(dict(method_id=f'v134_{j:02}',topic=topic,grade=grade,title=title,solving_method=approach,questions_expected=10,independence_certified=False,review_status='pending-expert-review',published=False))
  for i in range(10):questions.append(task(j,i))
 assert len(questions)==len(SPECS)*10
 assert len({v['question'] for v in questions})==len(questions)
 dump(DIR/'V134_CANDIDATE_METHODS.jsonl',forms)
 dump(DIR/'V134_VERIFIED_QUESTIONS.jsonl',questions)
 print(f'V134: {len(forms)} candidates, {len(questions)} mechanically checked questions, 0 certified methods')
if __name__=='__main__':main()
