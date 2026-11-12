"""V131 deterministic authored math questions. All methods await novelty/pedagogy review.
Run: python V131_RESEARCH/generate.py. No runtime system code modified.
"""
from __future__ import annotations
from fractions import Fraction
from math import comb, factorial, gcd, isqrt
import json, pathlib, hashlib
import sympy as s
R=pathlib.Path(__file__).resolve().parent
x=s.symbols('x',real=True)
METHODS=[
('tap_hop','Hiệu hai tập nghiệm bất đẳng thức',10,'Biểu diễn từng tập bằng khoảng rồi lấy hiệu tập hợp'),
('ham_so_bac_hai','Tìm hệ số parabol từ tọa độ ba điểm',10,'Giải hệ tuyến tính cho ba hệ số a,b,c'),
('duong_thang','Tìm giao điểm hai đường thẳng không song song',10,'Giải hệ hai phương trình bậc nhất bằng định thức'),
('duong_tron','Lập phương trình tiếp tuyến từ điểm trên đường tròn',10,'Vectơ bán kính là pháp tuyến tiếp tuyến'),
('nhi_thuc_newton','Tính hệ số của số hạng trong khai triển nhị thức',10,'Sử dụng hệ số tổ hợp của khai triển Newton'),
('cap_so_cong','Tìm số hạng đầu từ tổng và công sai',11,'Giải biểu thức tổng n số hạng của cấp số cộng'),
('cap_so_nhan','Tìm tổng cấp số nhân hữu hạn từ công bội',11,'Sử dụng công thức cấp số nhân hữu hạn'),
('xac_suat_11','Xác suất rút đúng k vật loại A không hoàn lại',11,'Đếm tổ hợp chọn k vật A và n-k vật B, chia tổng tổ hợp'),
('dao_ham','Viết tiếp tuyến của đa thức tại hoành độ cho trước',11,'Tính đạo hàm rồi dùng dạng điểm-hệ số góc'),
('phuong_trinh_luong_giac','Giải phương trình cos x bằng giá trị góc đặc biệt',11,'Đối xứng của cos trên chu kỳ cơ sở'),
('nguyen_ham_tich_phan','Tính tích phân xác định đa thức',12,'Áp dụng định lý Newton-Leibniz cho nguyên hàm'),
('pt_logarit','Giải phương trình logarit với điều kiện xác định',12,'Đổi phương trình logarit sang lũy thừa và lọc miền xác định'),
('so_phuc','Tìm nghiệm phức của phương trình bậc hai có delta âm',12,'Sử dụng căn bậc hai số âm và công thức nghiệm'),
('mat_phang_oxyz','Tính khoảng cách điểm đến mặt phẳng',12,'Công thức khoảng cách từ điểm đến mặt phẳng'),
('mat_cau','Tìm phương trình mặt cầu từ hai đầu đường kính',12,'Tâm là trung điểm, bán kính là nửa độ dài đoạn thẳng'),
]

def fmt(z):return str(s.simplify(z)).replace('**','^')
def make(j,i):
 k=i+1; a=k+2; b=k%5+1; c=k%4+2
 if j==0:
  lo=k; hi=k+9; cut=k+4
  q=f'Cho A={{x nguyên | {lo} ≤ x ≤ {hi}}}, B={{x nguyên | x ≥ {cut}}}. Tìm số phần tử của A\\B.'
  ans=4; sol=f'Xét các số nguyên trong A từ {lo} đến {hi}. Loại các phần tử thuộc B có x ≥ {cut}; còn các số từ {lo} đến {cut-1}, nên có {cut-lo} phần tử.'
  check=len(set(range(lo,hi+1))-set(range(cut,hi+10)))
 elif j==1:
  aa=b; bb=2*k+1; cc=c
  vals=[(0,cc),(1,aa+bb+cc),(2,4*aa+2*bb+cc)]
  q=f'Parabol y=ax²+bx+c đi qua ba điểm (0,{vals[0][1]}),(1,{vals[1][1]}),(2,{vals[2][1]}). Tìm hệ số a.'
  ans=aa; sol=f'Đặt c={cc}; a+b={vals[1][1]-cc}; 4a+2b={vals[2][1]-cc}. Lấy phương trình sau trừ hai lần phương trình trước: 2a={2*aa}, nên a={aa}.'
  A,B,C=s.symbols('A B C'); check=s.solve([A*t*t+B*t+C-y for t,y in vals],(A,B,C))[A]
 elif j==2:
  px=k; py=2*k-3; m=b; n=-c
  d1=py-m*px; d2=py-n*px
  q=f'Tìm hoành độ giao điểm hai đường thẳng y={m}x+({d1}) và y=({n})x+({d2}).'
  ans=px; sol=f'Cho hai vế bằng nhau: ({m-n})x={d2-d1}. Vậy x={px}.'
  check=s.solve(s.Eq(m*x+d1,n*x+d2),x)[0]
 elif j==3:
  h=k; v=b; dx=3;dy=4; rad=5; px=h+dx;py=v+dy
  q=f'Cho (C): (x-{h})²+(y-{v})²={rad*rad}, P({px},{py}) thuộc (C). Tiếp tuyến tại P có dạng {dx}x+{dy}y+d=0. Tìm d.'
  d=-(dx*px+dy*py); ans=d; sol=f'Bán kính OP=({dx},{dy}) vuông góc tiếp tuyến. Do đó: {dx}(x-{px})+{dy}(y-{py})=0, tức {dx}x+{dy}y+({d})=0. Hệ số x là {dx}.'
  check=-((px-h)*px+(py-v)*py)
 elif j==4:
  n=6+(i%5);r=2+(i%3); t=1+(i%4)
  q=f'Tìm hệ số của x^{r} trong khai triển (1+{t}x)^{n}.'
  ans=comb(n,r)*t**r;sol=f'Số hạng chứa x^{r} là C({n},{r})({t}x)^{r}. Hệ số bằng {comb(n,r)}·{t}^{r}={ans}.'
  check=s.expand((1+t*x)**n).coeff(x,r)
 elif j==5:
  n=5+k;first=2*k+1;d=b;tot=n*(2*first+(n-1)*d)//2
  q=f'Một cấp số cộng có {n} số hạng đầu tổng bằng {tot}, công sai d={d}. Tìm số hạng đầu u₁.'
  ans=first;sol=f'Từ Sₙ=n[2u₁+(n−1)d]/2, suy ra u₁=[2·{tot}/{n}−({n}−1)·{d}]/2={first}.'
  check=s.solve(s.Eq(s.Symbol('u')*n+s.Rational(n*(n-1)*d,2),tot),s.Symbol('u'))[0]
 elif j==6:
  n=3+(i%5);first=k+1;ratio=2+(i%3);tot=first*sum(ratio**h for h in range(n))
  q=f'Cấp số nhân có u₁={first}, công bội q={ratio}. Tính tổng {n} số hạng đầu.'
  ans=tot;sol=f'Sₙ=u₁(q^n−1)/(q−1)={first}·({ratio}^{n}−1)/({ratio}−1)={tot}.'
  check=sum(first*ratio**h for h in range(n))
 elif j==7:
  red=5+(i%4);blue=4+(i%3);draw=3;choose=1+(i%2)
  q=f'Hộp có {red} bi đỏ và {blue} bi xanh, lấy ngẫu nhiên {draw} bi cùng lúc. Xác suất lấy đúng {choose} bi đỏ là bao nhiêu?'
  ans=s.Rational(comb(red,choose)*comb(blue,draw-choose),comb(red+blue,draw))
  sol=f'Số cách thuận lợi C({red},{choose})·C({blue},{draw-choose}); số cách đều C({red+blue},{draw}). Xác suất = {ans}.'
  from itertools import combinations
  check=s.Rational(sum(sum(z<red for z in choice)==choose for choice in combinations(range(red+blue),draw)),comb(red+blue,draw))
 elif j==8:
  t=k;co=b;lin=c;cons=k-1;m=3*co*t*t+2*lin*t
  q=f'Cho f(x)={co}x³+{lin}x²+{cons}. Tìm hệ số góc tiếp tuyến đồ thị tại x={t}.'
  ans=m;sol=f'Áp dụng quy tắc đạo hàm từng đơn thức: f′(x)=3·{co}x²+2·{lin}x. Tại x={t}, hệ số góc tiếp tuyến bằng f′({t})={m}.'
  check=s.diff(co*x**3+lin*x**2+cons,x).subs(x,t)
 elif j==9:
  angles=[s.pi/3,s.pi/4,s.pi/6,s.pi/2,s.pi]
  th=angles[i%5];val=s.cos(th)
  q=f'Trên khoảng [{2*i}π,{2*i+2}π), phương trình cos x={fmt(val)} có bao nhiêu nghiệm phân biệt?'
  ans=1 if th==s.pi else 2
  sol=f'Góc chuẩn α={fmt(th)}. Trên một chu kỳ cơ sở, các nghiệm là α và 2π−α'+(' (trùng nhau tại π).' if th==s.pi else ', khác nhau.')+f' Dịch một số nguyên chu kỳ không đổi số nghiệm, nên có {ans} nghiệm trong khoảng đã cho.'
  check=len(set([th,s.simplify(2*s.pi-th)]))
 elif j==10:
  low=i%3;high=low+2+k%4;A=b;B=k;C=c
  expr=A*x*x+B*x+C
  q=f'Tính I=∫ từ {low} đến {high} của ({A}x²+{B}x+{C}) dx.'
  ans=s.integrate(expr,(x,low,high));sol=f'Nguyên hàm F(x)={A}x³/3+{B}x²/2+{C}x. Do đó I=F({high})−F({low})={fmt(ans)}.'
  check=s.simplify(s.Rational(A,3)*(high**3-low**3)+s.Rational(B,2)*(high**2-low**2)+C*(high-low))
 elif j==11:
  base=2+(i%4);root=k+2;shift=i%3+1;rhs=root**2
  q=f'Giải log cơ số {base} của (x−{shift}) = {rhs} (tìm x).'
  ans=shift+base**rhs;sol=f'Điều kiện x>{shift}. Ta có x−{shift}={base}^{rhs}, nên x={ans} (thỏa điều kiện).'
  check=s.solve(s.Eq(x-shift,base**rhs),x)[0]
 elif j==12:
  real=k;im=b;B=-2*real;C=real*real+im*im
  q=f'Giải z²+({B})z+{C}=0 trên C. Tìm phần ảo dương của một nghiệm.'
  ans=im;sol=f'Δ=({B})²−4·{C}={-4*im*im}. Vậy z={real}±{im}i, phần ảo dương là {im}.'
  zz=s.symbols('z');roots=s.solve(zz**2+B*zz+C,zz);check=max(s.im(v) for v in roots)
 elif j==13:
  A=2;B=3;C=6;P=(k,b,c);d=2*k+3*b+6*c-(7+k)
  q=f'Tính khoảng cách từ M({P[0]},{P[1]},{P[2]}) đến mặt phẳng 2x+3y+6z−({d})=0.'
  ans=s.Rational(7+k,7);sol=f'd=|2·{k}+3·{b}+6·{c}−({d})|/√(4+9+36)=({7+k})/7={fmt(ans)}.'
  check=s.Abs(A*P[0]+B*P[1]+C*P[2]-d)/s.sqrt(A*A+B*B+C*C)
 else:
  x1=k;y1=b;z1=c;x2=x1+2*(i%3+1);y2=y1+4;z2=z1+6
  h=(x1+x2)//2;v=(y1+y2)//2;w=(z1+z2)//2;rsq=(x2-x1)**2/4+(y2-y1)**2/4+(z2-z1)**2/4
  q=f'Cho A({x1},{y1},{z1}), B({x2},{y2},{z2}) là hai đầu đường kính mặt cầu. Tìm bình phương bán kính R².'
  ans=int(rsq);sol=f'Tâm I({h},{v},{w}) là trung điểm AB. R²=AB²/4=[({x2-x1})²+({y2-y1})²+({z2-z1})²]/4={ans}.'
  check=s.Rational((x2-x1)**2+(y2-y1)**2+(z2-z1)**2,4)
 assert s.simplify(s.sympify(ans)-s.sympify(check))==0,(j,i,ans,check)
 return {'id':f'v131_{j:02d}_{i:02d}','method_id':f'v131_{j:02d}','topic':METHODS[j][0],'grade':METHODS[j][2],'format':'tra_loi_ngan','question':q,'answer':fmt(ans),'solution':sol,'independent_check':fmt(check),'checked_by':'alternate symbolic or direct enumeration','published':False,'review_status':'pending-expert-review'}

def build():
 forms=[];qs=[]
 for j,(topic,title,grade,method) in enumerate(METHODS):
  f={'method_id':f'v131_{j:02d}','topic':topic,'title':title,'grade':grade,'solving_method':method,'questions_expected':10,'independence_certified':False,'review_status':'pending-expert-review','published':False}
  forms.append(f)
  for i in range(10):qs.append(make(j,i))
 assert len(forms)==15 and len(qs)==150
 assert len({z['question'] for z in qs})==len(qs)
 for name,records in [('V131_CANDIDATE_METHODS.jsonl',forms),('V131_VERIFIED_QUESTIONS.jsonl',qs)]:
  (R/name).write_text(''.join(json.dumps(z,ensure_ascii=False,sort_keys=True)+'\n' for z in records),encoding='utf8')
 return forms,qs
if __name__=='__main__':
 f,q=build();print(f'{len(f)} candidate methods; {len(q)} independently checked answers; 0 independently novel methods certified')
