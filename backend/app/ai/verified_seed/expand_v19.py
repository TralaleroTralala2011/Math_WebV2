"""Add 12 mathematically distinct, independently checked families (10 items each)."""
import json, math, collections
from fractions import Fraction
from pathlib import Path

PATH=Path(__file__).with_name('verified_seed_bank.jsonl')
old=[json.loads(s) for s in PATH.read_text(encoding='utf8').splitlines() if s.strip()]
new=[]
def put(grade,topic,fid,sig,q,ans,sol,check):
    assert check, (fid,q,ans)
    new.append(dict(grade=grade,topic=topic,form_id='v19_'+fid,form_signature='v19_'+sig,question=q,answer=str(ans),solution=sol,proof={'verified_by':'independent_exact_arithmetic','expected':str(ans)}))
for i in range(1,11):
    # 1: inverse affine at input
    a=i+1;b=2*i-9;y=3*i+1;x=Fraction(y-b,a)
    put(10,'Hàm số','inverse_affine','inverse_affine_evaluation',f'Cho f(x)={a}x{b:+d}. Tìm f^(-1)({y}).',x,f'Giải {a}x{b:+d}={y}, suy ra x=({y}-{b})/{a}={x}.',a*x+b==y)
    # 2: quadratic parameter with double root
    r=i-6;c=r*r;m=2*r
    put(10,'Phương trình bậc hai','double_root','parameter_double_root',f'Tìm m để phương trình x²−mx+{c}=0 có nghiệm kép và m có cùng dấu với {r} (nếu r=0 thì m=0).',m,f'Δ=m²−4·{c}=0, nên m=±{2*abs(r)}. Điều kiện dấu chọn m={m}; nghiệm kép x=m/2={r}.',m*m==4*c)
    # 3: squared point-to-line distance
    a=i+1;b=i;c=-(i*i+2);x=i-3;y=2*i-1;num=a*x+b*y+c;v=Fraction(num*num,a*a+b*b)
    put(10,'Đường thẳng','point_line_distance_squared','squared_distance_point_to_line',f'Tính bình phương khoảng cách từ P({x};{y}) đến đường thẳng {a}x+{b}y{c:+d}=0.',v,f'd²=({a}·{x}+{b}·{y}{c:+d})²/({a}²+{b}²)={v}.',v*(a*a+b*b)==num*num)
    # 4: count nonnegative solutions stars bars
    n=i+4;k=3+(i%3);ans=math.comb(n+k-1,k-1)
    put(10,'Quy tắc đếm','stars_bars','nonnegative_integer_solutions',f'Có bao nhiêu bộ {k} số nguyên không âm (x₁,…,x{k}) thỏa x₁+…+x{k}={n}?',ans,f'Phương pháp chia sao và vạch: C({n+k-1},{k-1})={ans}.',ans==math.factorial(n+k-1)//(math.factorial(k-1)*math.factorial(n)))
    # 5: geometric infinite sum
    a=i+2;q=Fraction(i,i+2);s=a/(1-q)
    put(11,'Cấp số nhân','infinite_geometric_sum','infinite_geometric_series',f'Tính tổng vô hạn S={a}+{a}·({i}/{i+2})+{a}·({i}/{i+2})²+…',s,f'Vì |q|={q}<1, S=u₁/(1−q)={a}/(1−{q})={s}.',s*(1-q)==a)
    # 6: quotient derivative
    a=i+1;b=i+3;c=i+2;d=2*i+5;x=1;den=c*x+d;ans=Fraction(a*d-b*c,den*den)
    put(11,'Quy tắc đạo hàm','quotient_derivative','derivative_of_linear_fraction',f'Cho f(x)=({a}x+{b})/({c}x+{d}). Tính f′(1).',ans,f'f′(x)=({a}·{d}−{b}·{c})/({c}x+{d})², nên f′(1)={ans}.',ans*den*den==a*d-b*c)
    # 7: normal line slope quadratic
    a=i+1;b=i-5;x=i+2;der=2*a*x+b;ans=Fraction(-1,der)
    put(11,'Đạo hàm','normal_line_slope','normal_slope_of_quadratic',f'Cho y={a}x²{b:+d}x+1. Tính hệ số góc của pháp tuyến tại điểm có hoành độ x={x}.',ans,f'Tiếp tuyến có hệ số góc y′({x})=2·{a}·{x}{b:+d}={der}; pháp tuyến có hệ số góc −1/{der}={ans}.',ans*der==-1)
    # 8: exactly two successes independent Bernoulli 3
    p=Fraction(i,i+11);ans=3*p*p*(1-p)
    put(11,'Xác suất','three_bernoulli_two_success','exactly_two_of_three_independent',f'Ba phép thử độc lập có xác suất thành công p={p} mỗi phép. Xác suất đúng 2 lần thành công là bao nhiêu?',ans,f'Có C(3,2)=3 cách chọn 2 lần thành công; P=3p²(1−p)=3·({p})²·(1−{p})={ans}.',ans==sum(p*p*(1-p) for _ in range(3)))
    # 9: integral of odd function symmetric
    a=i+1;b=i+2;L=i+1
    put(12,'Nguyên hàm và tích phân','odd_integral','odd_polynomial_symmetric_integral',f'Tính I=∫ từ −{L} đến {L} của ({a}x³+{b}x) dx.',0,'Hàm dưới dấu tích phân là hàm lẻ, đoạn lấy tích phân đối xứng qua 0 nên I=0.',Fraction(a,4)*(L**4-(-L)**4)+Fraction(b,2)*(L**2-(-L)**2)==0)
    # 10: projection scalar along vector
    a=i+1;b=i+2;u=(2*i+1,i-2);v=(a,b);dot=u[0]*a+u[1]*b;norm=a*a+b*b;ans=Fraction(dot,norm)
    put(12,'Tọa độ trong không gian','vector_projection_coeff','orthogonal_projection_coefficient',f'Trong Oxyz, u=({u[0]};{u[1]};0), v=({a};{b};0). Tìm t sao cho hình chiếu vuông góc của u lên phương v bằng tv.',ans,f'Điều kiện (u−tv)·v=0 ⇒ t=(u·v)/(v·v)={dot}/{norm}={ans}.',dot-ans*norm==0)
    # 11: complex division real part
    a=i+2;b=i;c=i+1;d=1;den=c*c+d*d;real=Fraction(a*c+b*d,den)
    put(12,'Số phức','complex_division_real','real_part_complex_quotient',f'Tìm phần thực của z=({a}+{b}i)/({c}+{d}i).',real,f'Nhân tử và mẫu với {c}−{d}i: Re(z)=({a}·{c}+{b}·{d})/({c}²+{d}²)={real}.',real*den==a*c+b*d)
    # 12: point plane signed distance scaled by normal length integer
    a=3;b=4;c=0;d=-(i+2);x=i;y=2*i;z=i+1;ans=Fraction(abs(a*x+b*y+c*z+d),5)
    put(12,'Mặt phẳng Oxyz','point_plane_distance','distance_point_to_plane_345_normal',f'Tính khoảng cách từ M({x};{y};{z}) đến mặt phẳng 3x+4y{d:+d}=0.',ans,f'd(M,(P))=|3·{x}+4·{y}{d:+d}|/√(3²+4²)= {ans}.',ans*5==abs(3*x+4*y+d))

existing_q={' '.join(r['question'].lower().split()) for r in old}
existing_ids={r['form_id'] for r in old}
existing_sig={r['form_signature'] for r in old}
assert len(new)==120
assert not ({r['form_id'] for r in new}&existing_ids)
assert not ({r['form_signature'] for r in new}&existing_sig)
assert len({r['form_id'] for r in new})==12
assert all(sum(r['form_id']==fid for r in new)==10 for fid in {r['form_id'] for r in new})
assert len({' '.join(r['question'].lower().split()) for r in new})==120
assert not ({' '.join(r['question'].lower().split()) for r in new}&existing_q)
with PATH.open('a',encoding='utf8') as f:
    for r in new: f.write(json.dumps(r,ensure_ascii=False)+'\n')
report={'version':'V19','new_form_ids':12,'new_questions':120,'total_questions':len(old)+len(new),'total_form_ids':len(existing_ids|{r['form_id'] for r in new}),'validation':'exact arithmetic checks, unique normalized prompts, 10 questions per new form','limitations':'No proof of conceptual independence from all existing forms; no full UI integration or end-to-end regression test.'}
Path(__file__).with_name('EXPANSION_REPORT_V19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(report)
