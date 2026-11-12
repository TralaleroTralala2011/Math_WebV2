"""Add independently checked arithmetic question families. Does not certify 2000 forms/topic."""
import json, math
from fractions import Fraction
from pathlib import Path
P=Path(__file__).with_name('verified_seed_bank.jsonl')
rows=[json.loads(s) for s in P.read_text(encoding='utf8').splitlines() if s.strip()]
new=[]
def add(fid,topic,grade,sig,q,ans,steps,proof):
    new.append(dict(form_id=fid,topic=topic,grade=grade,form_signature=sig,question=q,answer=str(ans),solution=steps,proof=proof))
for n in range(1,11):
 a=n+3;b=n+5;c=n+1
 add('gcd_euclid','Chia hết',10,'find gcd of two integers via Euclidean algorithm',f'Tìm ƯCLN của {a*b} và {a*c}.',a*math.gcd(b,c),f'ƯCLN({a*b},{a*c})={a}×ƯCLN({b},{c})={a*math.gcd(b,c)}.',{'x':a*b,'y':a*c})
 x=n+2;y=n+4
 add('lcm_two','Chia hết',10,'find least common multiple using gcd',f'Tìm BCNN của {x} và {y}.',math.lcm(x,y),f'ƯCLN({x},{y})={math.gcd(x,y)}; BCNN={x}×{y}/{math.gcd(x,y)}={math.lcm(x,y)}.',{'x':x,'y':y})
 a=n+2;b=n+4
 add('rectangle_perimeter','Hình học cơ bản: góc/cạnh/diện tích',10,'perimeter of rectangle from two sides',f'Hình chữ nhật dài {a} cm, rộng {b} cm. Tính chu vi (cm).',2*(a+b),f'Chu vi = 2×(dài+rộng)=2×({a}+{b})={2*(a+b)} cm.',{'a':a,'b':b})
 add('triangle_area_base_height','Tam giác và tứ giác cơ bản',10,'triangle area from base and corresponding altitude',f'Tam giác có đáy {2*a} cm và chiều cao tương ứng {b} cm. Tính diện tích (cm²).',a*b,f'Diện tích = đáy×chiều cao/2={2*a}×{b}/2={a*b} cm².',{'base':2*a,'height':b})
 p=n+1;q=n+3
 add('slope_two_points','Tọa độ trong mặt phẳng',10,'slope from two points with distinct x',f'Đường thẳng qua A({n};{p}) và B({n+2};{p+2*q}). Tính hệ số góc.',q,f'Hệ số góc = (yB-yA)/(xB-xA)=({2*q})/2={q}.',{'dx':2,'dy':2*q})
 add('midpoint_x_2d','Tọa độ trong mặt phẳng',10,'x coordinate of midpoint of planar segment',f'A({n};{p}), B({n+2*q};{p+1}). Hoành độ trung điểm AB là bao nhiêu?',n+q,f'Hoành độ trung điểm = ({n}+{n+2*q})/2={n+q}.',{'x1':n,'x2':n+2*q})
 add('quadratic_vertex_x','Hàm số bậc hai và parabol',10,'vertex x coordinate of quadratic ax2+bx+c',f'Parabol y={a}x²-({2*a*q})x+{b}. Tìm hoành độ đỉnh.',q,f'Với a={a}, b={-2*a*q}, hoành độ đỉnh = -b/(2a)={q}.',{'a':a,'b':-2*a*q})
 add('quadratic_discriminant','Phương trình bậc hai',10,'compute discriminant of quadratic',f'Tính biệt thức Δ của {a}x²+{2*b}x+{b*b} = 0.',(2*b)**2-4*a*b*b,f'Δ=b²-4ac=({2*b})²-4×{a}×{b*b}={(2*b)**2-4*a*b*b}.',{'a':a,'b':2*b,'c':b*b})
 add('arithmetic_sum','Cấp số cộng',11,'sum first n terms of arithmetic sequence',f'Cấp số cộng có u1={a}, công sai d=2. Tính tổng {n+3} số hạng đầu.',(n+3)*(2*a+(n+2)*2)//2,f'S={n+3}×[2×{a}+({n+3}-1)×2]/2={(n+3)*(2*a+(n+2)*2)//2}.',{'first':a,'d':2,'count':n+3})
 add('geometric_sum','Cấp số nhân',11,'sum finite geometric sequence ratio two',f'Cấp số nhân có u1={a}, công bội q=2. Tính tổng {n+2} số hạng đầu.',a*(2**(n+2)-1),f'S=u1×(2^m-1)={a}×(2^{n+2}-1)={a*(2**(n+2)-1)}.',{'first':a,'count':n+2})
 add('derivative_power_at_point','Đạo hàm',11,'derivative of monomial degree four at integer',f'Cho f(x)={a}x⁴. Tính f\u2032({n}).',4*a*n**3,f'f\u2032(x)=4×{a}x³; f\u2032({n})={4*a*n**3}.',{'a':a,'x':n})
 add('probability_complement','Xác suất',11,'probability of complement of event',f'Một biến cố A có xác suất {n}/{n+5}. Tính P(không A) dưới dạng phân số tối giản.',Fraction(5,n+5),f'P(không A)=1-P(A)=1-{n}/{n+5}={Fraction(5,n+5)}.',{'num':n,'den':n+5})
 add('sphere_volume_pi_coefficient','Hình khối và thể tích cơ bản',12,'sphere volume coefficient of pi given integer radius multiple three',f'Hình cầu có bán kính {3*n} cm. Thể tích bằng kπ cm³. Tìm k.',36*n**3,f'V=(4/3)πr³=(4/3)π×({3*n})³={36*n**3}π; k={36*n**3}.',{'radius':3*n})
 add('plane_distance_axis','Mặt phẳng Oxyz',12,'distance from point to plane x=c',f'Tính khoảng cách từ M({n+q};{a};{b}) đến mặt phẳng x={n}.',q,f'Mặt phẳng x={n} có pháp tuyến theo trục Ox; khoảng cách = |{n+q}-{n}|={q}.',{'x':n+q,'c':n})
 add('complex_conjugate_imag','Số phức',12,'imaginary part of complex conjugate',f'Cho z={a}+{b}i. Tìm phần ảo của số phức liên hợp z.',-b,f'Số phức liên hợp của z={a}+{b}i là {a}-{b}i, do đó phần ảo bằng {-b}.',{'re':a,'im':b})
 add('integral_constant','Nguyên hàm và tích phân',12,'definite integral of constant function',f'Tính tích phân từ 0 đến {n+2} của hàm số f(x)={a}.',a*(n+2),f'Nguyên hàm của {a} là {a}x; tích phân = {a}×({n+2}-0)={a*(n+2)}.',{'constant':a,'upper':n+2})
 add('log_product_rule','Hàm số logarit',12,'logarithm of product of powers same base',f'Tính log₂(2^{n}×2^{q}).',n+q,f'log₂(2^{n}×2^{q})=log₂(2^{n+q})={n+q}.',{'powers':[n,q]})
 add('binomial_coefficient_choose_two','Tổ hợp',10,'count unordered pairs from n distinct objects',f'Có {n+5} học sinh. Có bao nhiêu cách chọn 2 học sinh?',(n+5)*(n+4)//2,f'Số cách là C({n+5},2)=({n+5})×({n+4})/2={(n+5)*(n+4)//2}.',{'n':n+5})
 add('absolute_value_equation_positive','Phương trình',10,'solve absolute value equation count integer solutions',f'Phương trình |x-{n}|={q} có bao nhiêu nghiệm thực?',2,f'|x-{n}|={q}>0 tương đương x-{n}=±{q}, cho hai nghiệm phân biệt.',{'center':n,'radius':q})
 add('right_triangle_hypotenuse','Hệ thức lượng trong tam giác',10,'Pythagorean hypotenuse from scaled 3-4-5 triangle',f'Tam giác vuông có hai cạnh góc vuông {3*n} và {4*n} cm. Tính cạnh huyền (cm).',5*n,f'Định lý Pythagore: c=√(({3*n})²+({4*n})²)={5*n} cm.',{'legs':[3*n,4*n]})
# verify every new answer independently from proof values
checks={
'gcd_euclid':lambda p:math.gcd(p['x'],p['y']), 'lcm_two':lambda p:math.lcm(p['x'],p['y']),
'rectangle_perimeter':lambda p:2*(p['a']+p['b']), 'triangle_area_base_height':lambda p:Fraction(p['base']*p['height'],2),
'slope_two_points':lambda p:Fraction(p['dy'],p['dx']), 'midpoint_x_2d':lambda p:Fraction(p['x1']+p['x2'],2),
'quadratic_vertex_x':lambda p:Fraction(-p['b'],2*p['a']), 'quadratic_discriminant':lambda p:p['b']**2-4*p['a']*p['c'],
'arithmetic_sum':lambda p:Fraction(p['count']*(2*p['first']+(p['count']-1)*p['d']),2),
'geometric_sum':lambda p:p['first']*(2**p['count']-1), 'derivative_power_at_point':lambda p:4*p['a']*p['x']**3,
'probability_complement':lambda p:Fraction(p['den']-p['num'],p['den']),
'sphere_volume_pi_coefficient':lambda p:Fraction(4*p['radius']**3,3),
'plane_distance_axis':lambda p:abs(p['x']-p['c']), 'complex_conjugate_imag':lambda p:-p['im'],
'integral_constant':lambda p:p['constant']*p['upper'], 'log_product_rule':lambda p:sum(p['powers']),
'binomial_coefficient_choose_two':lambda p:math.comb(p['n'],2),
'absolute_value_equation_positive':lambda p:2 if p['radius']>0 else 1,
'right_triangle_hypotenuse':lambda p:math.isqrt(sum(x*x for x in p['legs']))}
assert len(new)==200
assert len({x['form_id'] for x in new})==20
assert all(str(checks[x['form_id']](x['proof']))==x['answer'] for x in new)
assert len({x['question'] for x in rows+new})==len(rows+new)
assert not ({x['form_id'] for x in rows}&{x['form_id'] for x in new})
with P.open('a',encoding='utf8') as f:
 for r in new:f.write(json.dumps(r,ensure_ascii=False)+'\n')
report={'previous_rows':len(rows),'added_rows':len(new),'total_rows':len(rows+new),'previous_distinct_form_ids':len({x['form_id'] for x in rows}),'added_distinct_form_ids':20,'total_distinct_form_ids':len({x['form_id'] for x in rows+new}),'all_questions_unique_exact':True,'independent_arithmetic_checks_new':200,'warning':'Form IDs are not proof of 2000 independent forms per topic. Existing rows have repeated form IDs; no end-to-end UI test.'}
Path(__file__).with_name('EXPANSION_REPORT_V5.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(report)
