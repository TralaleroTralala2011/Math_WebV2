"""Reproducible V158 mathematical research data. Candidate status only."""
import json, math, hashlib
from pathlib import Path
from fractions import Fraction
from itertools import product
from collections import Counter

ROOT=Path(__file__).parent
METHODS=[
 ('crt','Chia dư','Giải hệ hai đồng dư bằng định lý số dư Trung Hoa','chung_minh_chia_du',10,'Tìm nghiệm không âm nhỏ nhất của hai đồng dư nguyên tố cùng nhau'),
 ('binomial','Nhị thức Newton','Hệ số đơn thức trong khai triển nhị thức','nhi_thuc_newton',10,'Sử dụng công thức hệ số C(n,k)a^(n-k)b^k'),
 ('lineplane','Tọa độ Oxyz','Tìm giao điểm đường thẳng tham số với mặt phẳng','toa_do_oxyz',12,'Thế tọa độ tham số vào phương trình mặt phẳng rồi giải tham số'),
 ('orthogonal','Vectơ','Xác định tham số để hai vectơ vuông góc','vec_to',10,'Giải phương trình tích vô hướng hai vectơ bằng không'),
 ('geomseries','Cấp số nhân','Tổng n số hạng đầu của cấp số nhân','cap_so_nhan',11,'Sử dụng công thức tổng hữu hạn và xét công bội bằng 1'),
 ('variance','Các số đặc trưng','Phương sai của mẫu dữ liệu có tần số','cac_so_dac_trung',12,'Tính trung bình có trọng số và phương sai theo các tần số'),
]

def jwrite(path, rows):
 path.write_text(''.join(json.dumps(o,ensure_ascii=False,sort_keys=True)+'\n' for o in rows),encoding='utf8')

def val(x):
 if isinstance(x,Fraction):return str(x.numerator) if x.denominator==1 else f'{x.numerator}/{x.denominator}'
 return str(x)

def mk(method,i):
 if method=='crt':
  m=[5,7,8,9,11,13,5,7,9,11][i]; n=[7,9,11,13,8,5,13,11,7,9][i]
  assert math.gcd(m,n)==1
  r=(2*i+1)%m;s=(3*i+2)%n
  ans=next(t for t in range(m*n) if t%m==r and t%n==s)
  # independently: CRT inverse construction
  via=((r*n*pow(n,-1,m))+(s*m*pow(m,-1,n)))%(m*n)
  assert ans==via
  q=f'Tìm số nguyên không âm nhỏ nhất x thỏa mãn x ≡ {r} (mod {m}) và x ≡ {s} (mod {n}).'
  sol=f'Vì gcd({m},{n})=1 nên có nghiệm duy nhất theo modulo {m*n}. Đặt x={r}+{m}t, suy ra {m}t ≡ {s-r} (mod {n}). Tìm t theo modulo {n}, nhận nghiệm x={ans} trong [0,{m*n-1}]. Kiểm tra: {ans} mod {m}={r} và {ans} mod {n}={s}.'
  return q,ans,sol,{'m':m,'n':n,'r':r,'s':s},'enumeration vs CRT modular inverse'
 if method=='binomial':
  n=5+i%6;k=1+(i*3)%(n-1);a=1+i%3;b=1+(i+1)%4
  ans=math.comb(n,k)*a**(n-k)*b**k
  # independent Pascal-triangle polynomial convolution
  coeff=[1]
  for _ in range(n):
   nextc=[0]*(len(coeff)+1)
   for j,c in enumerate(coeff):nextc[j]+=a*c;nextc[j+1]+=b*c
   coeff=nextc
  assert ans==coeff[k]
  q=f'Tìm hệ số của x^{k} trong khai triển ({a}+{b}x)^{n}.'
  sol=f'Số hạng tổng quát là C({n},j)·{a}^({n}-j)·({b}x)^j. Để có x^{k}, lấy j={k}. Hệ số = C({n},{k})·{a}^{n-k}·{b}^{k} = {ans}.'
  return q,ans,sol,{'n':n,'k':k,'a':a,'b':b},'binomial formula vs polynomial coefficient convolution'
 if method=='lineplane':
  x0,y0,z0=i-3,2-i%5,i%4-2; u,v,w=1+i%3,(-1)**i*(2+i%2),1+(i+1)%4
  a,b,c=1+i%3,2+(i+1)%3,1+i%4
  target=i%5-2
  d=a*(x0+u*target)+b*(y0+v*target)+c*(z0+w*target)
  denom=a*u+b*v+c*w;assert denom!=0
  recovered=Fraction(d-a*x0-b*y0-c*z0,denom);assert recovered==target
  point=(x0+u*target,y0+v*target,z0+w*target)
  assert a*point[0]+b*point[1]+c*point[2]==d
  q=f'Tìm giao điểm của đường thẳng (x,y,z)=({x0},{y0},{z0})+t({u},{v},{w}) với mặt phẳng {a}x+{b}y+{c}z={d}.'
  sol=f'Thế x={x0}+{u}t, y={y0}+({v})t, z={z0}+{w}t vào mặt phẳng, được {denom}t={d-(a*x0+b*y0+c*z0)} nên t={target}. Thay trở lại: I={point}. Kiểm tra tọa độ I thỏa phương trình mặt phẳng.'
  return q,point,sol,{'p':[x0,y0,z0],'v':[u,v,w],'normal':[a,b,c],'d':d},'parameter substitution vs plane residual'
 if method=='orthogonal':
  a,b=2+i%4,1+i%3; c=3+i%5;d=2+i%3
  # u=(k,a),v=(b,c) would k=-ac/b
  ans=Fraction(-a*c,b)
  assert ans*b+a*c==0
  q=f'Tìm tham số k để hai vectơ u=(k,{a}) và v=({b},{c}) vuông góc.'
  sol=f'Hai vectơ vuông góc khi u·v=0. Suy ra {b}k+{a}·{c}=0, do đó k={val(ans)}. Kiểm tra tích vô hướng bằng 0.'
  return q,ans,sol,{'a':a,'b':b,'c':c},'dot product equation vs direct substitution'
 if method=='geomseries':
  first=i+2;r=[2,3,-2,4,-1,1,2,-3,3,1][i]; n=3+i%5
  ans=sum(first*r**t for t in range(n))
  closed=first*n if r==1 else Fraction(first*(r**n-1),r-1)
  assert ans==closed
  q=f'Cho cấp số nhân có u₁={first}, công bội q={r}. Tính tổng {n} số hạng đầu.'
  sol=f'Công thức tổng Sₙ=u₁(1−qⁿ)/(1−q) nếu q≠1, còn q=1 thì Sₙ=n·u₁. Với u₁={first}, q={r}, n={n}, suy ra Sₙ={ans}. Kiểm tra bằng cộng trực tiếp {n} số hạng.'
  return q,ans,sol,{'first':first,'r':r,'n':n},'closed form vs explicit summation'
 if method=='variance':
  values=[i%4,2+i%4,6+i%4];frequencies=[2+i%3,3+(i+1)%4,1+i%5]
  N=sum(frequencies)
  mean=sum(v*f for v,f in zip(values,frequencies))
  ans=Fraction(sum(f*v*v for v,f in zip(values,frequencies)),N)-Fraction(mean,N)**2
  expanded=sum(([v]*f for v,f in zip(values,frequencies)),[])
  oracle=sum((Fraction(v)-Fraction(sum(expanded),len(expanded)))**2 for v in expanded)/len(expanded)
  assert oracle==ans
  q=f'Mẫu dữ liệu có giá trị {values[0]}, {values[1]}, {values[2]} với tần số lần lượt là {frequencies[0]}, {frequencies[1]}, {frequencies[2]}. Tính phương sai theo công thức chia cho N.'
  sol=f'Tổng số quan sát N={N}. Trung bình x̄={mean}/{N}={val(Fraction(mean,N))}. Dùng s²=[Σ(fᵢxᵢ²)]/N−x̄², suy ra s²={val(ans)}. Đối chiếu trực tiếp bình phương sai lệch của {N} quan sát.'
  return q,ans,sol,{'values':values,'frequencies':frequencies},'second-moment identity vs expanded squared deviations'
 raise AssertionError(method)

def options(answer,i):
 if isinstance(answer,tuple):
  a=answer;opts=[a,(a[0]+1,a[1],a[2]),(a[0],a[1]+2,a[2]),(a[0],a[1],a[2]-1)]
 else:
  ans=Fraction(answer)
  opts=[ans,ans+1,ans-1,ans+2]
  if len(set(opts))<4:raise AssertionError('invalid MCQ')
 order=[0,1,2,3]; order=order[i%4:]+order[:i%4]
 rendered=[val(opts[z]) for z in order]
 assert len(set(rendered))==4
 letters='ABCD'
 return dict(zip(letters,rendered)),letters[order.index(0)]

def main():
 candidates=[];rows=[]
 for method,title,full,topic,grade,solving_method in METHODS:
  mid='v158_'+method
  candidates.append(dict(method_id=mid,topic=topic,grade=grade,title=full,solving_method=solving_method,method_family=method,independence_certified=False,published=False,review_status='pending-expert-review',questions_expected=10,novelty_note='Only question answers verified; mathematical-method independence across historic corpus NOT certified.'))
  for i in range(10):
   question,answer,solution,params,oracle=mk(method,i)
   fmt='trac_nghiem' if i<7 else ('tu_luan' if i<9 else 'dung_sai')
   actual=val(answer)
   row=dict(id=f'{mid}_{i:02}',method_id=mid,topic=topic,grade=grade,question=question,format=fmt,canonical_answer=actual,solution=solution,parameters=params,oracle_method=oracle,answer_oracle_match=True,published=False,independence_certified=False,review_status='pending-expert-review')
   if fmt=='trac_nghiem':row['options'],row['answer']=options(answer,i)
   elif fmt=='tu_luan':row['answer']=actual
   else:
    statement=actual if [m[0] for m in METHODS].index(method)%2==0 else (val(tuple(v+1 for v in answer)) if isinstance(answer,tuple) else val(Fraction(answer)+1))
    row['question']+=f' Nhận định: “Kết quả là {statement}”. Đúng hay sai?'
    row['answer']='Đúng' if statement==actual else 'Sai'
   rows.append(row)
 assert len(rows)==60 and len(candidates)==6
 assert len(set(r['question'] for r in rows))==60
 assert len(set(r['id'] for r in rows))==60
 assert all(len([r for r in rows if r['method_id']==c['method_id']])==10 for c in candidates)
 assert Counter(r['format'] for r in rows)=={'trac_nghiem':42,'tu_luan':12,'dung_sai':6}
 jwrite(ROOT/'V158_CANDIDATE_METHODS.jsonl',candidates)
 jwrite(ROOT/'V158_VERIFIED_ANSWERS_PENDING_REVIEW.jsonl',rows)
 manifest=dict(candidate_methods=len(candidates),questions=len(rows),independence_certified=0,questions_published=0,answer_oracle_checked=60,format_counts=dict(Counter(r['format'] for r in rows)),status='PENDING EXPERT REVIEW',method_ids=[c['method_id'] for c in candidates],methodology='Six independent arithmetic/combinatorial oracles check numeric answers, not independent-method novelty')
 (ROOT/'V158_RESULTS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(manifest,ensure_ascii=False))
if __name__=='__main__':main()
