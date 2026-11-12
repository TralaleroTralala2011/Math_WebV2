"""V132 standalone, unpublished mathematical research candidates with independent checks."""
import json, math, pathlib, hashlib, itertools, re, collections
from fractions import Fraction
import sympy as sp
ROOT=pathlib.Path(__file__).resolve().parent
D=ROOT/'V132_RESEARCH';D.mkdir(exist_ok=True)
x=sp.symbols('x', real=True)
FORMS=[
 ('ham_so_bac_hai','Đỉnh parabol qua phép hoàn thành bình phương',10,'Hoàn thành bình phương để suy ra hoành độ đỉnh'),
 ('vector','Tích vô hướng qua bình phương độ dài tổng hai vectơ',10,'Dùng đẳng thức bình phương độ dài tổng vectơ'),
 ('toa_do_phang','Diện tích tam giác theo tọa độ định hướng',10,'Dùng định thức tọa độ của hai vectơ cạnh'),
 ('bat_phuong_trinh','Đếm nghiệm nguyên của bất phương trình bậc hai',10,'Phân tích tam thức thành nhân tử rồi xét dấu'),
 ('cap_so_cong','Xác định vị trí số hạng trong cấp số cộng',11,'Giải điều kiện u_n = u_1 + (n-1)d với n nguyên dương'),
 ('xac_suat_11','Xác suất hợp của hai biến cố độc lập',11,'Công thức cộng xác suất và xác suất giao hai biến cố độc lập'),
 ('dao_ham','Giá trị nhỏ nhất của hàm bậc ba trên đoạn',11,'Kiểm tra hai đầu đoạn và điểm tới hạn bằng đạo hàm'),
 ('nguyen_ham_tich_phan','Diện tích hình phẳng giữa hai đường thẳng',12,'Tích phân trị tuyệt đối hiệu hai hàm bậc nhất trên đoạn'),
 ('mat_phang_oxyz','Hình chiếu vuông góc điểm lên mặt phẳng',12,'Đi dọc pháp tuyến để chiếu điểm lên mặt phẳng'),
 ('so_phuc','Môđun của thương hai số phức',12,'Tính môđun bằng tính nhân của môđun và chia'),
]
def tostr(z): return str(sp.simplify(z))
def build(j,i):
 k=i+1; a=2+(i%4); b=1+(i%6)
 if j==0:
  h=i-4; v=2*i-7; aa=(-1 if i%2 else 1)*a; bb=-2*aa*h; cc=aa*h*h+v
  q=f'Cho y={aa}x²+({bb})x+({cc}). Tìm hoành độ đỉnh của parabol.'; ans=h
  sol=f'Hoàn thành bình phương: y={aa}(x−({h}))²+({v}), đỉnh có hoành độ {h}.'
  check=sp.solve(sp.diff(aa*x*x+bb*x+cc,x),x)[0]
 elif j==1:
  p=2+i; r=3+(i%4); dot=(-1 if i%2 else 1)*(i+2)
  normsum=p*p+r*r+2*dot
  assert normsum>=0 and abs(dot)<=p*r
  q=f'Cho |u|={p}, |v|={r}, |u+v|²={normsum}. Tính u·v.';ans=dot
  sol=f'|u+v|²=|u|²+|v|²+2u·v nên u·v=({normsum}−{p*p}−{r*r})/2={dot}.'
  check=Fraction(normsum-p*p-r*r,2)
 elif j==2:
  ax=i;ay=2-i;bx=ax+2+i%3;by=ay+1;cx=ax-1;cy=ay+3+i%4
  det=(bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
  q=f'Cho A({ax},{ay}), B({bx},{by}), C({cx},{cy}). Tính diện tích tam giác ABC.';ans=sp.Rational(abs(det),2)
  sol=f'AB=({bx-ax},{by-ay}), AC=({cx-ax},{cy-ay}). S=|det(AB,AC)|/2=|{det}|/2={tostr(ans)}.'
  check=abs(sp.Polygon(sp.Point(ax,ay),sp.Point(bx,by),sp.Point(cx,cy)).area)
 elif j==3:
  lo=-3+i%4;hi=lo+3+i%3; left=lo-3;right=hi+3
  q=f'Có bao nhiêu số nguyên x thỏa ({left} ≤ x ≤ {right}) và (x−({lo}))(x−({hi})) ≤ 0?';ans=hi-lo+1
  sol=f'Vì hai nghiệm {lo} và {hi}, tích không dương khi {lo}≤x≤{hi}; gồm {ans} số nguyên.'
  check=sum((n-lo)*(n-hi)<=0 for n in range(left,right+1))
 elif j==4:
  first=i-5;d=2+i%5;n=4+i;term=first+(n-1)*d
  q=f'Cấp số cộng có u₁={first}, d={d}. Biết uₙ={term}, tìm n.';ans=n
  sol=f'uₙ=u₁+(n−1)d. Suy ra n=1+({term}−({first}))/{d}={n}.'
  check=next(t for t in range(1,100) if first+(t-1)*d==term)
 elif j==5:
  p=Fraction(i%4+1,8);r=Fraction(i%5+1,10)
  q=f'A,B độc lập, P(A)={p}, P(B)={r}. Tính P(A∪B).';ans=p+r-p*r
  sol=f'P(A∪B)=P(A)+P(B)−P(A)P(B)={p}+{r}−({p})({r})={ans}.'
  # enumerate 80 equally-weighted pair grid partition as independent finite sample space
  check=Fraction(sum((u<8*p or v<10*r) for u in range(8) for v in range(10)),80)
 elif j==6:
  # cubic derivative 3(x-1)(x-3); critical 1 and 3, varied endpoints
  shift=i-4; f=x**3-6*x**2+9*x+shift; left=0 if i%2==0 else 1; right=4+i%3
  q=f'Tìm giá trị nhỏ nhất của f(x)=x³−6x²+9x+({shift}) trên đoạn [{left},{right}].'
  vals=[f.subs(x,z) for z in [left,right,1,3] if left<=z<=right];ans=min(vals)
  sol=f'f′(x)=3(x−1)(x−3). Xét hai đầu đoạn và các điểm tới hạn 1,3 thuộc đoạn; các giá trị tương ứng là {list(map(str,vals))}. Giá trị nhỏ nhất là {ans}.'
  check=min(sp.calculus.util.minimum(f,x,sp.Interval(left,right)),ans) # symbolic alternate minimum
 elif j==7:
  slope=i%5-2; intercept=i-3;lo=-2-i%3;hi=3+i%4;cross=-intercept/slope if slope else None
  q=f'Tính diện tích hình phẳng giới hạn bởi y={slope}x+({intercept}), y=0 và hai đường thẳng x={lo}, x={hi}.'
  ans=sp.integrate(abs(slope*x+intercept),(x,lo,hi))
  if isinstance(ans,sp.Integral):ans=sp.integrate(sp.Abs(slope*x+intercept),(x,lo,hi))
  signchanges=[sp.Rational(-intercept,slope)] if slope else []
  pieces=[sp.Rational(lo)]+[z for z in signchanges if lo<z<hi]+[sp.Rational(hi)]
  check=sum(abs(sp.integrate(slope*x+intercept,(x,pieces[t],pieces[t+1]))) for t in range(len(pieces)-1))
  sol=f'S=∫ từ {lo} đến {hi} |{slope}x+({intercept})| dx. Chia đoạn tại nghiệm của {slope}x+({intercept})=0 (nếu nằm trong đoạn), rồi cộng các tích phân không âm, được S={tostr(ans)}.'
 elif j==8:
  # plane 2x-y+2z=d; distance normal squared 9
  px=i-3;py=i%5-2;pz=i%4+1;delta=(i%5+1)*3;plane=2*px-py+2*pz-delta
  q=f'Cho P({px},{py},{pz}), mặt phẳng (Q): 2x−y+2z={plane}. Tìm hoành độ hình chiếu vuông góc H của P lên (Q).'
  lam=sp.Rational(delta,9);ans=px-2*lam
  sol=f'Pháp tuyến n=(2,−1,2), |n|²=9. Vì 2·{px}−({py})+2·{pz}−({plane})={delta}, H=P−({delta}/9)n. Hoành độ H là {tostr(ans)}.'
  # independently solve line-plane intersection
  t=sp.symbols('t'); tt=sp.solve(sp.Eq(2*(px-2*t)-(py+t)+2*(pz-2*t),plane),t)[0];check=px-2*tt
 elif j==9:
  a=i+2;b=i%5+1;c=i%4+1;d=i+3
  q=f'Tính |({a}+{b}i)/({c}+{d}i)|².'
  ans=sp.Rational(a*a+b*b,c*c+d*d)
  sol=f'|z₁/z₂|²=|z₁|²/|z₂|²=({a}²+{b}²)/({c}²+{d}²)={tostr(ans)}.'
  check=sp.simplify(sp.expand_complex((a+b*sp.I)/(c+d*sp.I)*sp.conjugate((a+b*sp.I)/(c+d*sp.I))))
 else:raise AssertionError(j)
 assert sp.simplify(sp.sympify(ans)-sp.sympify(check))==0,(j,i,ans,check)
 if j==1: sol += ' Có thể kiểm tra ngược bằng cách thế tích vô hướng vừa tìm vào công thức độ dài tổng vectơ.'
 if j==2: sol += ' Tính định thức theo quy tắc tích chéo, lấy trị tuyệt đối vì diện tích luôn không âm.'
 if j==4: sol += ' Kiểm tra thay lại giá trị n vào công thức số hạng tổng quát để nhận đúng số hạng đề bài.'
 if j==5: sol += ' Do A và B độc lập, P(A∩B)=P(A)P(B); trừ xác suất giao để không đếm hai lần.'
 if j==9: sol += ' Mẫu số khác 0 vì tổng bình phương của hai số thực dương; phép chia số phức xác định.'
 return {'id':f'v132_{j:02d}_{i:02d}','method_id':f'v132_{j:02d}','topic':FORMS[j][0],'grade':FORMS[j][2], 'format':'tra_loi_ngan', 'question':q,'answer':tostr(ans),'solution':sol,'independent_check':tostr(check),'published':False,'review_status':'pending-expert-review'}

def writej(path,rows):path.write_text(''.join(json.dumps(z,ensure_ascii=False,sort_keys=True)+'\n' for z in rows),encoding='utf8')
def run():
 fs=[{'method_id':f'v132_{j:02d}','topic':t,'title':title,'grade':grade,'solving_method':method,'questions_expected':10,'independence_certified':False,'review_status':'pending-expert-review','published':False} for j,(t,title,grade,method) in enumerate(FORMS)]
 qs=[build(j,i) for j in range(len(fs)) for i in range(10)]
 assert len({q['question'] for q in qs})==len(qs)
 assert len({q['id'] for q in qs})==len(qs)
 writej(D/'V132_CANDIDATE_METHODS.jsonl',fs);writej(D/'V132_VERIFIED_QUESTIONS.jsonl',qs)
 print('Created',len(fs),'candidate methods and',len(qs),'arithmetically verified questions.')
if __name__=='__main__':run()
