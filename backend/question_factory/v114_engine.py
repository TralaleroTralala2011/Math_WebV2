"""Sixty-six manually differentiated mathematical tasks with deterministic examples.

Verifies the numeric/symbolic answer with a separate parameter-based oracle,
then checks that stem/solution match the deterministic specification. This
verification does *not* prove global independence of problem-solving methods.
"""
from __future__ import annotations
from hashlib import sha256
import json
import random
import re
from sympy import Integer, Rational, Symbol, pi, sqrt, simplify, sympify, binomial, ceiling, factorial
from .v114_catalog import BLUEPRINTS

FAMILIES = frozenset(item[0] for item in BLUEPRINTS)


def generate(family: str, ordinal: int, difficulty: str, seed_key=None) -> dict:
    if family not in FAMILIES:
        raise ValueError(f'Unknown V114 family {family}')
    if type(ordinal) is not int or not 0 <= ordinal < 10:
        raise ValueError('ordinal must be an integer 0..9')
    source = str(seed_key or family)
    rng = random.Random(int.from_bytes(sha256(f'v114|{family}|{source}|{ordinal}'.encode()).digest()[:8], 'big'))
    randint = rng.randint
    k = ordinal + 2
    a, b, c = 4*k+randint(1, 2), 4*k+randint(1, 2), 4*k+randint(1, 2)
    p = {}
    stem = explanation = ''
    result = None
    if family == 'truth_implication':
        p=dict(p=ordinal % 2, q=(ordinal // 2 + randint(0, 1))%2, context=k)
        result=int((not p['p']) or bool(p['q']))
        stem=f"Trong mệnh đề giả định {k}, P có giá trị {p['p']} và Q có giá trị {p['q']} (1=đúng, 0=sai). Tính giá trị chân trị của P ⇒ Q (ghi 0 hoặc 1)."
        explanation=f"Phép kéo theo P ⇒ Q chỉ sai khi P đúng và Q sai; trong trường hợp này kết quả là {result}."
    elif family == 'cartesian_product_count':
        p=dict(a=a+k,b=b+k); result=p['a']*p['b']
        stem=f"Tập A có {p['a']} phần tử và tập B có {p['b']} phần tử. Hỏi tích Descartes A×B có bao nhiêu cặp có thứ tự?"
        explanation=f"Mỗi phần tử của A ghép được với mọi phần tử B, nên |A×B|=|A|·|B|={p['a']}·{p['b']}={result}."
    elif family == 'three_set_union':
        p=dict(only_a=k+2,only_b=a,only_c=b,only_ab=c,only_ac=randint(1,5),only_bc=randint(1,5),all_three=randint(1,4))
        p.update(A=p['only_a']+p['only_ab']+p['only_ac']+p['all_three'],B=p['only_b']+p['only_ab']+p['only_bc']+p['all_three'],C=p['only_c']+p['only_ac']+p['only_bc']+p['all_three'])
        p.update(AB=p['only_ab']+p['all_three'],AC=p['only_ac']+p['all_three'],BC=p['only_bc']+p['all_three'],ABC=p['all_three'])
        result=p['A']+p['B']+p['C']-p['AB']-p['AC']-p['BC']+p['ABC']
        stem=f"Ba câu lạc bộ A,B,C có |A|={p['A']}, |B|={p['B']}, |C|={p['C']}, |A∩B|={p['AB']}, |A∩C|={p['AC']}, |B∩C|={p['BC']}, |A∩B∩C|={p['ABC']}. Có bao nhiêu người tham gia ít nhất một câu lạc bộ?"
        explanation=f"Áp dụng nguyên lý cộng trừ ba tập: |A∪B∪C|=|A|+|B|+|C|−|A∩B|−|A∩C|−|B∩C|+|A∩B∩C|={result}."
    elif family == 'integer_interval_count':
        p=dict(low=randint(-12,3),high=20*k+randint(1,5));result=p['high']-p['low']
        stem=f"Hỏi có bao nhiêu nghiệm nguyên x thỏa mãn đồng thời {p['low']} < x và x ≤ {p['high']}?"
        explanation=f"Các số nguyên được phép là {p['low']+1},{p['low']+2},…,{p['high']}. Số lượng bằng {p['high']}−({p['low']})={result}."
    elif family == 'sqrt_domain_lower_bound':
        p=dict(a=a,b=b+k);result=Rational(-p['b'],p['a'])
        stem=f"Với f(x)=√({p['a']}x+{p['b']}), hãy tìm giá trị x nhỏ nhất thuộc miền xác định (viết dưới dạng phân số nếu cần)."
        explanation=f"Điều kiện biểu thức dưới căn không âm: {p['a']}x+{p['b']}≥0, tương đương x≥−{p['b']}/{p['a']}={result}."
    elif family == 'linear_zero':
        p=dict(a=a,b=b+k);result=Rational(-p['b'],p['a'])
        stem=f"Cho hàm số y={p['a']}x+{p['b']}. Hoành độ giao điểm của đồ thị với trục Ox bằng bao nhiêu?"
        explanation=f"Điểm thuộc Ox có tung độ bằng 0: {p['a']}x+{p['b']}=0, nên x=−{p['b']}/{p['a']}={result}."
    elif family == 'vieta_squares':
        p=dict(r=12*k+randint(0,4),s=-randint(1,9));p['sum']=p['r']+p['s'];p['product']=p['r']*p['s'];result=p['r']**2+p['s']**2
        stem=f"Không giải phương trình x²−({p['sum']})x+({p['product']})=0, hãy tính x₁²+x₂² với x₁,x₂ là hai nghiệm."
        explanation=f"Theo Viète x₁+x₂={p['sum']}, x₁x₂={p['product']}. Do đó x₁²+x₂²=(x₁+x₂)²−2x₁x₂={p['sum']}²−2({p['product']})={result}."
    elif family == 'symmetric_system_xy':
        p=dict(x=12*k+randint(0,4),y=randint(1,8));p['S']=p['x']+p['y'];p['Q']=p['x']**2+p['y']**2;result=p['x']*p['y']
        stem=f"Hai số thực x,y thỏa mãn x+y={p['S']} và x²+y²={p['Q']}. Tính tích xy."
        explanation=f"Ta có (x+y)²=x²+y²+2xy, vì thế xy=[{p['S']}²−{p['Q']}]/2={result}."
    elif family == 'radical_equation_isolation':
        p=dict(m=k+randint(1,4),offset=a);result=p['m']**2-p['offset']
        stem=f"Giải phương trình √(x+{p['offset']})={p['m']}. Hỏi nghiệm x bằng bao nhiêu?"
        explanation=f"Vế phải dương nên bình phương hai vế được x+{p['offset']}={p['m']}². Suy ra x={result}; thử lại √({result}+{p['offset']})={p['m']}."
    elif family == 'alternate_interior_angle':
        p=dict(angle=15+12*k+randint(0,4));result=p['angle']
        stem=f"Hai đường thẳng a,b song song, đường c cắt a,b. Một góc so le trong có số đo {p['angle']}°. Góc so le trong còn lại bằng bao nhiêu độ?"
        explanation=f"Khi hai đường thẳng song song bị một đường cắt, hai góc so le trong bằng nhau; do đó góc cần tìm là {result}°."
    elif family == 'congruent_triangle_corresponding':
        p=dict(length=12*k+randint(1,5));result=p['length']
        stem=f"Hai tam giác ABC và DEF bằng nhau với thứ tự tương ứng A↔D, B↔E, C↔F. Nếu AB={p['length']} cm, tính DE (cm)."
        explanation=f"Hai tam giác bằng nhau có các cạnh tương ứng bằng nhau. Cạnh DE tương ứng với AB nên DE={result} cm."
    elif family == 'right_triangle_median':
        p=dict(hyp=10*k);result=Rational(p['hyp'],2)
        stem=f"Tam giác ABC vuông tại A, cạnh huyền BC={p['hyp']} cm. Tính độ dài trung tuyến từ A đến trung điểm M của BC."
        explanation=f"Trung điểm cạnh huyền cách đều ba đỉnh của tam giác vuông, nên AM=BC/2={p['hyp']}/2={result} cm."
    elif family == 'rhombus_diagonal_area':
        p=dict(d1=2*(k+3),d2=2*(a+1));result=Rational(p['d1']*p['d2'],2)
        stem=f"Hình thoi có độ dài hai đường chéo lần lượt là {p['d1']} cm và {p['d2']} cm. Tính diện tích (cm²)."
        explanation=f"Hai đường chéo hình thoi vuông góc và chia hình thành bốn tam giác; S=d₁d₂/2={p['d1']}·{p['d2']}/2={result}."
    elif family == 'circle_chord_length':
        p=dict(radius=5*k,distance=3*k);result=8*k
        stem=f"Đường tròn bán kính {p['radius']} cm có dây AB cách tâm O một khoảng {p['distance']} cm. Tính độ dài dây AB."
        explanation=f"Hạ OH⊥AB thì H là trung điểm AB. AH=√(OA²−OH²)=√({p['radius']}²−{p['distance']}²)={4*k}; vậy AB=2AH={result} cm."
    elif family == 'thales_similarity_length':
        p=dict(small=k+2,large=2*(k+2),known=2*(a+k));result=Rational(p['small']*p['known'],p['large'])
        stem=f"Hai tam giác đồng dạng theo thứ tự ABC∼DEF có AB={p['small']}, DE={p['large']} và DF={p['known']}. Tính AC."
        explanation=f"Đồng dạng cho AB/DE=AC/DF, nên AC=AB·DF/DE={p['small']}·{p['known']}/{p['large']}={result}."
    elif family == 'triangle_area_common_height':
        p=dict(base1=k+3,base2=a+2);result=Rational(p['base1'],p['base2'])
        stem=f"Hai tam giác có cùng chiều cao tương ứng, độ dài hai đáy là {p['base1']} cm và {p['base2']} cm. Tính tỉ số diện tích S₁/S₂."
        explanation=f"Vì S=bh/2 và hai chiều cao bằng nhau, nên S₁/S₂=b₁/b₂={p['base1']}/{p['base2']}={result}."
    elif family == 'inscribed_angle':
        p=dict(central=20+10*k);result=Rational(p['central'],2)
        stem=f"Trên cùng một đường tròn, góc ở tâm AOB chắn cung AB nhỏ bằng {p['central']}°. Góc nội tiếp ACB chắn chính cung nhỏ AB có số đo bao nhiêu?"
        explanation=f"Theo định lý góc nội tiếp, góc ACB bằng một nửa số đo cung AB bị chắn: {p['central']}/2={result}°."
    elif family == 'tangent_segment_length':
        p=dict(OP=5*k,r=3*k);result=4*k
        stem=f"Từ P ngoài đường tròn tâm O kẻ tiếp tuyến PT (T là tiếp điểm), biết OP={p['OP']} cm và OT={p['r']} cm. Tính PT."
        explanation=f"Bán kính OT vuông góc PT. Tam giác OPT vuông ở T nên PT=√(OP²−OT²)=√({p['OP']}²−{p['r']}²)={result} cm."
    elif family == 'triangle_inequality_integer_sides':
        p=dict(a=k+3,b=a+2);result=2*min(p['a'],p['b'])-1
        stem=f"Có bao nhiêu số nguyên dương c để ba độ dài {p['a']}, {p['b']}, c lập thành một tam giác không suy biến?"
        explanation=f"Bất đẳng thức tam giác yêu cầu |{p['a']}−{p['b']}|<c<{p['a']}+{p['b']}. Đếm số nguyên trong khoảng mở được {result}."
    elif family == 'amgm_two_positive_min':
        p=dict(product=k*k);result=2*k
        stem=f"Với hai số thực dương x,y thỏa mãn xy={p['product']}, giá trị nhỏ nhất của x+y bằng bao nhiêu?"
        explanation=f"Bất đẳng thức AM-GM: x+y≥2√(xy)=2√{p['product']}={result}; dấu bằng khi x=y={k}."
    elif family == 'pigeonhole_minimum':
        p=dict(boxes=2+k,objects=(2+k)*(a+1)+1);result=a+2
        stem=f"Có {p['objects']} học sinh chia vào {p['boxes']} nhóm. Chứng minh có nhóm chứa ít nhất bao nhiêu học sinh bằng nguyên lý Dirichlet?"
        explanation=f"Nếu mỗi nhóm có nhiều nhất {result-1} học sinh thì tổng chỉ có {p['boxes']}·{result-1}={p['boxes']*(result-1)}. Mâu thuẫn, nên ít nhất {result}."
    elif family == 'circle_line_secant_count':
        state=ordinal%3;p=dict(r=8+k,y=[8+k,7+k,9+k][state]);result=[1,2,0][state]
        stem=f"Trong mặt phẳng Oxy, đường tròn x²+y²={p['r']**2} và đường thẳng y={p['y']} có bao nhiêu giao điểm thực?"
        explanation=f"Thay y={p['y']} được x²={p['r']**2}−{p['y']**2}; số nghiệm thực x tương ứng là {result}, nên có {result} giao điểm."
    elif family == 'economic_linear_break_even':
        p=dict(sale=a+12,unit=a+3,quantity=k+10);p['fixed']=(p['sale']-p['unit'])*p['quantity'];result=p['quantity']
        stem=f"Một cửa hàng bán sản phẩm giá {p['sale']} nghìn đồng/chiếc, biến phí {p['unit']} nghìn đồng/chiếc và định phí {p['fixed']} nghìn đồng. Cần bán bao nhiêu chiếc để hòa vốn?"
        explanation=f"Doanh thu={p['sale']}n và tổng chi phí={p['unit']}n+{p['fixed']}. Giải ({p['sale']}−{p['unit']})n={p['fixed']} được n={result}."
    elif family == 'vector_component_projection':
        p=dict(x=12*k+randint(1,5),y=b);result=p['x']
        stem=f"Trong Oxy, vectơ u=({p['x']};{p['y']}). Thành phần đại số của hình chiếu vectơ u lên trục Ox là bao nhiêu?"
        explanation=f"Hình chiếu vuông góc lên Ox giữ nguyên hoành độ và cho tung độ bằng 0; hệ số trên trục Ox là {result}."
    elif family == 'trig_cos_double_angle':
        p=dict(num=randint(1,4),den=5+k);result=2*Rational(p['num']**2,p['den']**2)-1
        stem=f"Góc α có cos α={p['num']}/{p['den']}. Tính cos(2α) dưới dạng chính xác."
        explanation=f"Dùng công thức nhân đôi cos(2α)=2cos²α−1=2({p['num']}/{p['den']})²−1={result}."
    elif family == 'trig_equation_zero_solution_count':
        p=dict(n=k+2);result=p['n']+1
        stem=f"Có bao nhiêu nghiệm x của phương trình sin x=0 trên đoạn [0; {p['n']}π]? Tính cả hai đầu mút."
        explanation=f"sin x=0 ⇔ x=jπ với j nguyên. Trong đoạn đã cho j=0,1,…,{p['n']}, nên có {result} nghiệm."
    elif family == 'ap_difference_two_terms':
        p=dict(i=2,j=k+4,d=a+2,first=b);p['ui']=p['first']+(p['i']-1)*p['d'];p['uj']=p['first']+(p['j']-1)*p['d'];result=p['d']
        stem=f"Cấp số cộng có u{p['i']}={p['ui']} và u{p['j']}={p['uj']}. Tìm công sai d."
        explanation=f"Vì uⱼ−uᵢ=(j−i)d nên d=({p['uj']}−{p['ui']})/({p['j']}−{p['i']})={result}."
    elif family == 'ap_missing_index':
        p=dict(first=b,d=a+1,index=k+6);p['value']=p['first']+(p['index']-1)*p['d'];result=p['index']
        stem=f"Cấp số cộng có u₁={p['first']} và công sai d={p['d']}. Số hạng nào bằng {p['value']} (hỏi chỉ số n)?"
        explanation=f"Giải {p['first']}+(n−1)·{p['d']}={p['value']}, suy ra n=1+({p['value']}−{p['first']})/{p['d']}={result}."
    elif family == 'removable_limit_difference_squares':
        p=dict(a=k+3);result=2*p['a']
        stem=f"Tính giới hạn lim(x→{p['a']}) (x²−{p['a']**2})/(x−{p['a']}) với x≠{p['a']}."
        explanation=f"Với x≠{p['a']}, x²−{p['a']**2}=(x−{p['a']})(x+{p['a']}). Khử nhân tử rồi lấy giới hạn x+{p['a']}→{result}."
    elif family == 'piecewise_continuity_parameter':
        p=dict(a=a,b=b,t=k+1);result=p['a']*p['t']+p['b']
        stem=f"Hàm f(x)={p['a']}x+{p['b']} nếu x<{p['t']}, và f(x)=m nếu x≥{p['t']}. Tìm m để f liên tục tại x={p['t']}."
        explanation=f"Liên tục tại điểm ghép đòi hỏi lim x→{p['t']}⁻ f(x)=f({p['t']})=m. Suy ra m={p['a']}·{p['t']}+{p['b']}={result}."
    elif family == 'derivative_product_at':
        p=dict(a=a,b=b,c=c,d=k,t=k-1);result=p['a']*(p['c']*p['t']+p['d'])+p['c']*(p['a']*p['t']+p['b'])
        stem=f"Xét hàm số f(x)=({p['a']}x+{p['b']})({p['c']}x+{p['d']}). Hãy tính giá trị đạo hàm f'({p['t']}) bằng quy tắc đạo hàm của tích."
        explanation=f"Quy tắc tích: f'(x)={p['a']}({p['c']}x+{p['d']})+{p['c']}({p['a']}x+{p['b']}); thế x={p['t']} được {result}."
    elif family == 'tangent_slope_cubic':
        p=dict(a=a+1,t=k);result=3*p['t']**2-p['a']
        stem=f"Cho hàm f(x)=x³−{p['a']}x. Hệ số góc tiếp tuyến của đồ thị tại x={p['t']} là bao nhiêu?"
        explanation=f"Hệ số góc là đạo hàm f'({p['t']}). Do f'(x)=3x²−{p['a']} nên f'({p['t']})={result}."
    elif family == 'recurrence_arithmetic_summation':
        p=dict(u0=a,n=k+3);result=p['u0']+Rational(p['n']*(p['n']+1),2)
        stem=f"Dãy (uₙ) xác định bởi u₀={p['u0']}, uₙ=uₙ₋₁+n với n≥1. Tính u{p['n']}."
        explanation=f"Cộng các đẳng thức truy hồi từ 1 đến {p['n']}: uₙ=u₀+(1+2+…+n)=u₀+n(n+1)/2={result}."
    elif family == 'square_sum_induction':
        p=dict(n=k+2);result=Rational(p['n']*(p['n']+1)*(2*p['n']+1),6)
        stem=f"Sử dụng công thức chứng minh bằng quy nạp 1²+2²+…+n²=n(n+1)(2n+1)/6 để tính 1²+…+{p['n']}²."
        explanation=f"Cơ sở n=1 đúng; từ Sₙ cộng (n+1)² rồi rút gọn được Sₙ₊₁=(n+1)(n+2)(2n+3)/6. Với n={p['n']} kết quả là {result}."
    elif family == 'independent_intersection':
        p=dict(a=a,b=a+k,c=b,d=b+k);result=Rational(p['a'],p['b'])*Rational(p['c'],p['d'])
        stem=f"Hai biến cố A,B độc lập, P(A)={p['a']}/{p['b']}, P(B)={p['c']}/{p['d']}. Tính P(A∩B)."
        explanation=f"Biến cố độc lập thỏa P(A∩B)=P(A)P(B)=({p['a']}/{p['b']})({p['c']}/{p['d']})={result}."
    elif family == 'vandermonde_convolution':
        p=dict(n=k+3,m=a+4,choose=min(k+1,a+2));result=binomial(p['n']+p['m'],p['choose'])
        stem=f"Dùng đẳng thức Vandermonde tính tổng Σ(j=0..{p['choose']}) C({p['n']},j)·C({p['m']},{p['choose']}−j)."
        explanation=f"Mỗi cách chọn {p['choose']} người từ hai nhóm kích thước {p['n']},{p['m']} được đếm một lần theo số lấy từ nhóm đầu. Tổng bằng C({p['n']+p['m']},{p['choose']})={result}."
    elif family == 'translation_point_2d':
        p=dict(x=k+3,y=a,dx=b,dy=c);result=p['x']+p['dx']
        stem=f"Trong Oxy, phép tịnh tiến theo vectơ v=({p['dx']};{p['dy']}) biến M({p['x']};{p['y']}) thành M'. Tính hoành độ M'."
        explanation=f"Phép tịnh tiến cộng từng tọa độ vectơ v: M'=({p['x']}+{p['dx']};{p['y']}+{p['dy']}). Hoành độ M' là {result}."
    elif family == 'reflection_diagonal':
        p=dict(x=k+1,y=-a);result=p['x']
        stem=f"Điểm M({p['x']};{p['y']}) phản xạ qua đường thẳng y=x thành M'. Hãy tìm tung độ của M'."
        explanation=f"Đối xứng qua đường phân giác y=x hoán đổi hai tọa độ (x,y)→(y,x). Tung độ của M' bằng {result}."
    elif family == 'rotation_quarter_turn':
        p=dict(x=k+2,y=a);result=-p['y']
        stem=f"Quay điểm M({p['x']};{p['y']}) 90° ngược chiều kim đồng hồ quanh O được M'. Tính hoành độ của M'."
        explanation=f"Ma trận quay 90° biến (x,y) thành (−y,x), nên hoành độ M' là −{p['y']}={result}."
    elif family == 'composition_transforms':
        p=dict(x=k+2,y=a,dy=b);result=-p['y']+p['dy']
        stem=f"Trong Oxy, phản xạ M({p['x']};{p['y']}) qua trục Ox, rồi tịnh tiến ảnh theo vectơ ({c};{p['dy']}). Tính tung độ cuối."
        explanation=f"Sau đối xứng Ox, tung độ từ {p['y']} thành −{p['y']}; tịnh tiến thêm {p['dy']} nên y'={result}."
    elif family == 'rectangular_prism_diagonal':
        p=dict(a=3*k,b=4*k,c=12*k);result=13*k
        stem=f"Hình hộp chữ nhật có ba kích thước {p['a']}, {p['b']}, {p['c']} cm. Tính độ dài đường chéo không gian."
        explanation=f"Áp dụng định lý Pythagore trong không gian: d=√(a²+b²+c²)=√({p['a']}²+{p['b']}²+{p['c']}²)={result} cm."
    elif family == 'angle_line_plane_right_triangle':
        p=dict(height=3*k,projection=4*k,length=5*k);result=Rational(3,5)
        stem=f"Đường xiên AB dài {p['length']} cm đi tới mặt phẳng (P), độ cao từ B tới (P) là {p['height']} cm. Tính sin góc giữa AB và (P)."
        explanation=f"Góc giữa đường thẳng và mặt phẳng là góc với hình chiếu vuông góc. sinθ=độ cao/độ dài xiên={p['height']}/{p['length']}={result}."
    elif family == 'infinite_geometric_series':
        p=dict(first=k+2,den=a+1);result=Rational(p['first']*p['den'],p['den']-1)
        stem=f"Cho cấp số nhân vô hạn có số hạng đầu u₁={p['first']} và công bội q=1/{p['den']}. Tính tổng hội tụ S."
        explanation=f"Vì |q|=1/{p['den']}<1, tổng vô hạn S=u₁/(1−q)={p['first']}/(1−1/{p['den']})={result}."
    elif family == 'conditional_bayes_table':
        p=dict(ill=randint(1,6),total=20+k,positive_if_ill=randint(7,9),base=10,positive_if_well=1)
        result=Rational(p['ill']*p['positive_if_ill'],p['ill']*p['positive_if_ill']+(p['total']-p['ill'])*p['positive_if_well'])
        stem=f"Trong nhóm có {p['total']} người, {p['ill']} người mắc bệnh. Xét nghiệm dương tính với xác suất {p['positive_if_ill']}/10 nếu mắc bệnh, 1/10 nếu không mắc. Tính P(mắc bệnh | dương tính)."
        explanation=f"Theo Bayes, P(bệnh|+)=[{p['ill']}·{p['positive_if_ill']}]/[{p['ill']}·{p['positive_if_ill']}+({p['total']}−{p['ill']})·1]={result}."
    elif family == 'investment_geometric_growth':
        p=dict(initial=a*100,years=k+1,multiplier=2);result=p['initial']*p['multiplier']**p['years']
        stem=f"Một mô hình tăng trưởng giả định số lượng ban đầu {p['initial']} đơn vị và gấp đôi mỗi năm. Sau {p['years']} năm sẽ có bao nhiêu đơn vị?"
        explanation=f"Sau mỗi năm nhân 2, vì vậy mô hình cấp số nhân cho N={p['initial']}·2^{p['years']}={result}."
    elif family == 'cubic_stationary_positive':
        p=dict(a=k+2);result=p['a']
        stem=f"Cho f(x)=x³−{3*p['a']**2}x. Tìm hoành độ dương của điểm dừng (nghiệm f'(x)=0)."
        explanation=f"Đạo hàm f'(x)=3x²−{3*p['a']**2}=3(x²−{p['a']**2}). Giải f'(x)=0 được x=±{p['a']}; nghiệm dương là {result}."
    elif family == 'increasing_quadratic_threshold':
        p=dict(a=k+2);result=p['a']
        stem=f"Tìm giá trị t nhỏ nhất để hàm f(x)=x²−{2*p['a']}x đồng biến trên mọi khoảng (t;+∞)."
        explanation=f"f'(x)=2x−{2*p['a']}, dương với x>{p['a']}. Khoảng đồng biến phía phải bắt đầu tại t={result}."
    elif family == 'rational_vertical_asymptote':
        p=dict(k=k+2,a=a,b=b);result=p['k']
        stem=f"Hàm y=({p['a']}x+{p['b']})/(x−{p['k']}) có tiệm cận đứng x=c. Tìm c."
        explanation=f"Mẫu số triệt tiêu tại x={p['k']}; tử số tại đây bằng {p['a']*p['k']+p['b']}≠0, nên x={result} là tiệm cận đứng."
    elif family == 'tangent_intercept_quadratic':
        p=dict(a=a,b=b,c=c,t=k+1);result=p['c']-p['a']*p['t']**2
        stem=f"Tiếp tuyến tại x={p['t']} của parabol f(x)={p['a']}x²+{p['b']}x+{p['c']} có dạng y=mx+n. Tìm tung độ gốc n."
        explanation=f"Hệ số góc m=f'({p['t']})=2·{p['a']}·{p['t']}+{p['b']}. Vì tiếp tuyến qua ({p['t']}, f({p['t']})), n=f({p['t']})−m·{p['t']}={result}."
    elif family == 'exponential_inequality_integer':
        p=dict(power=k+2);result=p['power']+1
        stem=f"Tìm nghiệm nguyên không âm nhỏ nhất của bất phương trình 2^x > 2^{p['power']}."
        explanation=f"Vì hàm 2^x đồng biến, 2^x>2^{p['power']} ⇔ x>{p['power']}. Nghiệm nguyên nhỏ nhất là {result}."
    elif family == 'logarithm_inequality_integer':
        p=dict(power=1+k%5,top=2**(1+k%5)+k+5);result=p['top']-2**p['power']+1
        stem=f"Có bao nhiêu số nguyên x thỏa mãn log₂(x)≥{p['power']} và x≤{p['top']}?"
        explanation=f"Vì log₂ tăng và x>0, điều kiện tương đương 2^{p['power']}≤x≤{p['top']}. Số số nguyên là {p['top']}−{2**p['power']}+1={result}."
    elif family == 'log_change_of_base':
        p=dict(base=2**(k%3+2),exponent=k+1);p['arg']=p['base']**p['exponent'];result=p['exponent']
        stem=f"Dùng công thức đổi cơ số để tính log_{p['base']}({p['arg']}) (kết quả chính xác)."
        explanation=f"Theo đổi cơ số log_a b=(ln b)/(ln a). Vì {p['arg']}={p['base']}^{p['exponent']}, ta có ln({p['arg']})/ln({p['base']})={result}."
    elif family == 'plane_constant_from_point':
        p=dict(a=a,b=b,c=c,x=k,y=randint(-5,5),z=randint(-5,5));result=-(p['a']*p['x']+p['b']*p['y']+p['c']*p['z'])
        stem=f"Mặt phẳng (P): {p['a']}x+{p['b']}y+{p['c']}z+d=0 đi qua M({p['x']};{p['y']};{p['z']}). Tìm d."
        explanation=f"Thay tọa độ điểm M vào phương trình: {p['a']}·{p['x']}+{p['b']}·({p['y']})+{p['c']}·({p['z']})+d=0, suy ra d={result}."
    elif family == 'line_parametric_z':
        p=dict(z0=k+1,vz=a,t=randint(-3,5));result=p['z0']+p['vz']*p['t']
        stem=f"Trong Oxyz, đường thẳng d: (x;y;z)=({b};{c};{p['z0']})+t({a};{b};{p['vz']}). Khi t={p['t']}, tọa độ z bằng bao nhiêu?"
        explanation=f"Tọa độ theo tham số của đường thẳng là z={p['z0']}+{p['vz']}t. Thay t={p['t']} được z={result}."
    elif family == 'line_plane_intersection_t':
        p=dict(x0=k,y0=a,z0=b,vx=1,vy=2,vz=3,target=c);p['D']=p['x0']+p['y0']+p['z0']+(p['vx']+p['vy']+p['vz'])*p['target'];result=p['target']
        stem=f"Đường d: (x;y;z)=({p['x0']};{p['y0']};{p['z0']})+t({p['vx']};{p['vy']};{p['vz']}) cắt mặt phẳng x+y+z={p['D']}. Tìm t tại giao điểm."
        explanation=f"Thay tham số vào mặt phẳng: {p['x0']+p['y0']+p['z0']}+({p['vx']+p['vy']+p['vz']})t={p['D']}, suy ra t={result}."
    elif family == 'plane_angle_cos2':
        p=dict(a=3*k+randint(1,3),b=b);result=Rational(p['a']**2*p['b']**2,(1+p['a']**2)*(1+p['b']**2))
        stem=f"Hai mặt phẳng có pháp tuyến n₁=(1;0;{p['a']}) và n₂=(0;1;{p['b']}). Tính cos² của góc nhọn giữa hai mặt phẳng."
        explanation=f"cos²φ=(n₁·n₂)²/(||n₁||²||n₂||²)=({p['a']}·{p['b']})²/[(1+{p['a']}²)(1+{p['b']}²)]={result}."
    elif family == 'line_plane_angle_sin2':
        p=dict(a=a,b=b);result=Rational((1+p['a']*p['b'])**2,(1+p['a']**2)*(1+p['b']**2))
        stem=f"Đường thẳng có vectơ chỉ phương v=(1;{p['a']};0), mặt phẳng có pháp tuyến n=(1;{p['b']};0). Tính sin² góc giữa đường thẳng và mặt phẳng."
        explanation=f"sin²φ=(v·n)²/(||v||²||n||²)=(1+{p['a']}·{p['b']})²/[(1+{p['a']}²)(1+{p['b']}²)]={result}."
    elif family == 'sphere_tangent_plane_d':
        p=dict(cx=k,cy=a,cz=b,r=c);result=-(p['cx']+p['r'])
        stem=f"Mặt cầu tâm I({p['cx']};{p['cy']};{p['cz']}) bán kính {p['r']}. Tiếp xúc tại M({p['cx']+p['r']};{p['cy']};{p['cz']}) với mặt phẳng x+d=0. Tìm d."
        explanation=f"Bán kính IM nằm theo trục Ox nên tiếp diện tại M vuông góc Ox, có phương trình x={p['cx']+p['r']}, tức x+({result})=0."
    elif family == 'sphere_plane_section_area':
        p=dict(R=5*k,d=3*k);result=16*pi*k*k
        stem=f"Mặt cầu bán kính R={p['R']} cm được cắt bởi mặt phẳng cách tâm d={p['d']} cm. Tính diện tích hình tròn thiết diện (cm²)."
        explanation=f"Bán kính giao tuyến r thỏa r²=R²−d²={p['R']}²−{p['d']}²={16*k*k}. Diện tích thiết diện S=πr²={result}."
    elif family == 'projection_3d_coordinate':
        p=dict(x=a,y=3*k,z=4*k);result=5*k
        stem=f"Trong Oxyz, điểm M({p['x']};{p['y']};{p['z']}) có hình chiếu H trên trục Ox. Tính độ dài đoạn MH."
        explanation=f"Hình chiếu H=({p['x']};0;0), do đó MH=√({p['y']}²+{p['z']}²)={result}."
    elif family == 'complex_distance_modulus':
        p=dict(x1=a,y1=b,x2=a+3*k,y2=b+4*k);result=5*k
        stem=f"Hai điểm biểu diễn số phức z₁={p['x1']}+{p['y1']}i và z₂={p['x2']}+{p['y2']}i. Tính khoảng cách giữa hai điểm trong mặt phẳng phức."
        explanation=f"Khoảng cách bằng |z₂−z₁|=√[({p['x2']}−{p['x1']})²+({p['y2']}−{p['y1']})²]={result}."
    elif family == 'volume_revolution_quadratic':
        p=dict(a=a,length=k+2);result=pi*Rational(p['a']**2*p['length']**3,3)
        stem=f"Quay miền nằm dưới đường y={p['a']}x, trên đoạn 0≤x≤{p['length']}, quanh Ox. Tính thể tích vật thể tròn xoay."
        explanation=f"Phương pháp đĩa: V=π∫₀^{p['length']}({p['a']}x)²dx=π·{p['a']}²·{p['length']}³/3={result}."
    elif family == 'integral_area_parabola':
        p=dict(a=k+2);result=Rational(4*p['a']**3,3)
        stem=f"Tính diện tích miền giới hạn bởi parabol y=−x²+{2*p['a']}x và trục Ox."
        explanation=f"Parabol cắt Ox tại 0 và {2*p['a']}, dương ở giữa. Diện tích S=∫₀^{2*p['a']} (−x²+{2*p['a']}x)dx={result}."
    elif family == 'hypergeometric_expected':
        p=dict(N=20+k,K=a+2,n=randint(2,9));result=Rational(p['n']*p['K'],p['N'])
        stem=f"Một lô có {p['N']} sản phẩm, trong đó {p['K']} tốt. Lấy ngẫu nhiên {p['n']} sản phẩm không hoàn lại. Tính kỳ vọng số sản phẩm tốt."
        explanation=f"Đặt X là số sản phẩm tốt được lấy. Tính tuyến tính của kỳ vọng với mỗi lượt lấy có xác suất tốt K/N, E[X]=nK/N={p['n']}·{p['K']}/{p['N']}={result}."
    elif family == 'weighted_mean_frequency':
        p=dict(x1=a,x2=b+k,f1=k+1,f2=c+2);result=Rational(p['x1']*p['f1']+p['x2']*p['f2'],p['f1']+p['f2'])
        stem=f"Trong bảng tần số, giá trị {p['x1']} xuất hiện {p['f1']} lần và giá trị {p['x2']} xuất hiện {p['f2']} lần. Tính số trung bình cộng."
        explanation=f"Số trung bình có tần số bằng tổng giá trị nhân tần số chia tổng tần số: ({p['x1']}·{p['f1']}+{p['x2']}·{p['f2']})/({p['f1']}+{p['f2']})={result}."
    elif family == 'finance_simple_interest':
        p=dict(principal=1000*(a+k),percent=2+k,years=1+ordinal);result=Rational(p['principal']*p['percent']*p['years'],100)
        stem=f"Gửi {p['principal']} nghìn đồng với lãi đơn {p['percent']}% mỗi năm, trong {p['years']} năm. Tính tổng tiền lãi (nghìn đồng), không nhập gốc."
        explanation=f"Theo lãi đơn, lãi I=P·r·t={p['principal']}·({p['percent']}/100)·{p['years']}={result} nghìn đồng."
    elif family == 'coordinate_line_intercept':
        p=dict(x=k+1,y=a+2,slope=b);result=p['y']-p['slope']*p['x']
        stem=f"Trong mặt phẳng Oxy, đường thẳng có hệ số góc m={p['slope']} đi qua điểm M({p['x']};{p['y']}). Viết y=mx+n, tìm n."
        explanation=f"Phương trình điểm-hệ số góc: y−{p['y']}={p['slope']}(x−{p['x']}). Suy ra y={p['slope']}x+({result}); vậy n={result}."
    elif family == 'parallelogram_diagonal_midpoint':
        p=dict(width=2*(k+2),height=2*(a+1));result=Rational(p['width']+p['height'],2)
        stem=f"Tứ giác ABCD là hình bình hành có A(0;0), B({p['width']};0), D(0;{p['height']}). Hai đường chéo cắt nhau tại M. Tính x_M+y_M."
        explanation=f"Trong hình bình hành, hai đường chéo chia đôi nhau. C=({p['width']};{p['height']}) nên M là trung điểm AC, M=({p['width']/2};{p['height']/2}); x_M+y_M={result}."
    elif family == 'perpendicular_bisector_locus':
        p=dict(x1=k+2,x2=k+2+2*a);result=Rational(p['x1']+p['x2'],2)
        stem=f"Cho A({p['x1']};0), B({p['x2']};0) trong Oxy. Tập các điểm M thỏa MA=MB là đường thẳng x=t. Tính t."
        explanation=f"MA²=MB² ⇒ (x−{p['x1']})²+y²=(x−{p['x2']})²+y². Rút gọn được x=({p['x1']}+{p['x2']})/2={result}, trung trực AB."
    elif family == 'prism_edge_count':
        p=dict(n=k+3);result=3*p['n']
        stem=f"Một hình lăng trụ có đáy là đa giác {p['n']} cạnh. Tổng số cạnh của lăng trụ đó là bao nhiêu?"
        explanation=f"Lăng trụ n-giác có n cạnh đáy dưới, n cạnh đáy trên và n cạnh bên. Tổng là 3n=3·{p['n']}={result}."
    elif family == 'trig_fundamental_period':
        p=dict(k=k+1);result=2*pi/p['k']
        stem=f"Xác định chu kỳ dương nhỏ nhất T của hàm số y=sin({p['k']}x). Viết kết quả theo π."
        explanation=f"Hàm sin có chu kỳ 2π theo đối số; cần {p['k']}T=2π. Vậy chu kỳ cơ bản T=2π/{p['k']}={result}."
    elif family == 'trig_cos_one_root_count':
        p=dict(n=k+1);result=p['n']+1
        stem=f"Đếm số nghiệm thực của phương trình cos x=1 trong đoạn 0≤x≤{2*p['n']}π, tính cả hai đầu mút."
        explanation=f"cos x=1 chỉ khi x=2jπ với j nguyên. Điều kiện 0≤j≤{p['n']} cho j=0,…,{p['n']}, nên có {result} nghiệm."
    elif family == 'parallel_3d_direction_ratio':
        p=dict(a=a,b=b);result=3*p['b']
        stem=f"Vectơ u=({p['a']};{2*p['a']};{3*p['a']}) và v=({p['b']};{2*p['b']};m) cùng phương. Tính m."
        explanation=f"Từ hai thành phần đầu, v=({p['b']}/{p['a']})u. Thành phần thứ ba phải bằng 3·{p['b']}={result}."
    elif family == 'perpendicular_3d_dot_parameter':
        p=dict(a=11*k+randint(1,4),b=b);result=-(2*p['a']+3*p['b'])
        stem=f"Hai vectơ không gian u=({p['a']};{p['b']};1), v=(2;3;m) vuông góc. Tìm m."
        explanation=f"Điều kiện vuông góc là tích vô hướng bằng 0: 2·{p['a']}+3·{p['b']}+m=0. Suy ra m={result}."
    elif family == 'vertical_distance_to_floor':
        p=dict(x=a,y=b,z=k+3);result=p['z']
        stem=f"Trong Oxyz, điểm A({p['x']};{p['y']};{p['z']}) cách mặt phẳng (Oxy) một khoảng bao nhiêu đơn vị?"
        explanation=f"Mặt phẳng (Oxy) có phương trình z=0, pháp tuyến Oz. Khoảng cách vuông góc từ A bằng |z_A|=|{p['z']}|={result}."
    elif family == 'median_sorted_odd':
        p=dict(start=a,count=2*k+1,step=b);p['values']=[p['start']+j*p['step'] for j in range(p['count'])];result=p['values'][p['count']//2]
        stem=f"Dãy mẫu đã xếp tăng dần gồm {p['count']} số, bắt đầu từ {p['start']} và mỗi số sau hơn số trước {p['step']}. Tìm trung vị."
        explanation=f"Vì số lượng {p['count']} là lẻ, trung vị là số ở vị trí ({p['count']}+1)/2={k+1}. Giá trị tại đó bằng {result}."
    elif family == 'hypergeometric_exactly_two':
        p=dict(good=11*k+randint(1,4),bad=b+k);p['total']=p['good']+p['bad']
        result=binomial(p['good'],2)*p['bad']/binomial(p['total'],3)
        stem=f"Hộp có {p['good']} bóng đỏ, {p['bad']} bóng xanh. Lấy đồng thời 3 bóng không hoàn lại. Tính xác suất lấy đúng 2 bóng đỏ."
        explanation=f"Chọn đúng 2 đỏ từ {p['good']} bóng và 1 xanh từ {p['bad']} bóng: C({p['good']},2)·C({p['bad']},1). Chia tổng C({p['total']},3) được P={result}."
    elif family == 'homothety_x_coordinate':
        p=dict(x=a+k,y=b,factor=k);result=p['x']*p['factor']
        stem=f"Phép vị tự tâm O(0;0) với tỉ số {p['factor']} biến M({p['x']};{p['y']}) thành M'. Tìm hoành độ của M'."
        explanation=f"Phép vị tự tâm gốc tọa độ nhân mỗi tọa độ với tỉ số {p['factor']}, do đó x_M'={p['x']}·{p['factor']}={result}."
    elif family == 'pyramid_parallel_square_section':
        p=dict(side=4*(k+2));result=Rational(p['side']**2,4)
        stem=f"Hình chóp có đáy hình vuông cạnh {p['side']} cm. Mặt phẳng song song đáy cắt các cạnh bên tại trung điểm. Tính diện tích thiết diện (cm²)."
        explanation=f"Thiết diện đồng dạng đáy với tỉ số cạnh 1/2, nên tỉ số diện tích là (1/2)²=1/4. Diện tích bằng {p['side']}²/4={result}."
    elif family == 'geometric_depreciation_value':
        p=dict(initial=256*(a+k),years=k,remain_num=3,remain_den=4);result=Rational(p['initial']*3**p['years'],4**p['years'])
        stem=f"Một thiết bị có giá {p['initial']} nghìn đồng, mỗi năm còn 75% giá trị năm trước. Sau {p['years']} năm giá trị còn lại là bao nhiêu nghìn đồng?"
        explanation=f"Mỗi kỳ giá trị nhân 3/4, nên mô hình nhân theo cấp số nhân V={p['initial']}·(3/4)^{p['years']}={result}."
    elif family == 'reflection_y_axis_x':
        p=dict(x=a+k,y=b);result=-p['x']
        stem=f"Trong Oxy, lấy ảnh M' của M({p['x']};{p['y']}) qua phép đối xứng trục Oy. Hoành độ của M' là bao nhiêu?"
        explanation=f"Đối xứng qua Oy bảo toàn tung độ và đảo dấu hoành độ: (x,y)→(−x,y). Vậy x_M'={result}."
    elif family == 'euler_polyhedron_edges':
        p=dict(n=k+3);p['V']=2*p['n'];p['F']=p['n']+2;result=p['V']+p['F']-2
        stem=f"Một đa diện lồi có {p['V']} đỉnh và {p['F']} mặt. Theo hệ thức Euler, đa diện đó có bao nhiêu cạnh?"
        explanation=f"Đa diện lồi thỏa V−E+F=2; chuyển vế E=V+F−2={p['V']}+{p['F']}−2={result}."
    elif family == 'coordinate_plane_intersection_line':
        p=dict(x=11*k+randint(1,4),y=b,z=c);result=p['x']+p['y']
        stem=f"Trong không gian, giao tuyến của hai mặt phẳng x={p['x']} và y={p['y']} chứa điểm M({p['x']};{p['y']};{p['z']}). Tính x_M+y_M."
        explanation=f"Hai mặt phẳng giao nhau theo đường thẳng có x={p['x']}, y={p['y']}, còn z tùy ý. Vì vậy tổng hai tọa độ cố định bằng {result}."
    elif family == 'line_plane_parallel_condition':
        p=dict(a=a,b=b,c=c);result=Rational(-(p['a']+2*p['b']),p['c'])
        stem=f"Cho mặt phẳng có pháp tuyến n=({p['a']};{p['b']};{p['c']}). Tìm m để vectơ u=(1;2;m) có phương song song với mặt phẳng."
        explanation=f"Đường song song mặt phẳng khi u·n=0: {p['a']}+2·{p['b']}+{p['c']}m=0. Do {p['c']}≠0, m={result}."
    elif family == 'parallel_plane_normal_parameter':
        p=dict(a=a,b=b,c=c,k=k);result=p['c']*p['k']
        stem=f"Hai mặt phẳng có pháp tuyến n₁=({p['a']};{p['b']};{p['c']}) và n₂=({p['a']*p['k']};{p['b']*p['k']};m). Tìm m để pháp tuyến cùng phương."
        explanation=f"Tỉ số giữa thành phần thứ nhất và thứ hai đều là {p['k']}. Thành phần thứ ba cũng phải nhân {p['k']}, vậy m={result}."
    elif family == 'line_plane_perp_condition':
        p=dict(a=a,b=b,c=c,k=k);result=p['c']*p['k']
        stem=f"Mặt phẳng có pháp tuyến n=({p['a']};{p['b']};{p['c']}). Đường thẳng chỉ phương u=({p['a']*p['k']};{p['b']*p['k']};m). Tìm m để đường thẳng vuông góc mặt phẳng."
        explanation=f"Đường vuông góc mặt phẳng khi u song song pháp tuyến n. Hệ số tỉ lệ là {p['k']}, do đó m={p['k']}·{p['c']}={result}."
    elif family == 'tetrahedron_parallel_section_area':
        p=dict(base_area=9*(k+2));result=Rational(p['base_area'],9)
        stem=f"Tứ diện ABCD có diện tích đáy BCD={p['base_area']} cm². Mặt phẳng song song BCD cắt AB,AC,AD tại các điểm cách A bằng 1/3 cạnh tương ứng. Tính diện tích thiết diện."
        explanation=f"Tam giác thiết diện đồng dạng tam giác đáy theo tỉ số 1/3 (tính từ A), nên diện tích bằng {p['base_area']}·(1/3)²={result} cm²."
    elif family == 'skew_axis_distance':
        p=dict(h=k+2,b=a);result=p['h']
        stem=f"Trong Oxyz, d₁: (x;y;z)=(t;0;0), d₂: (x;y;z)=(0;s;{p['h']}) với t,s∈R. Khoảng cách giữa hai đường thẳng chéo nhau là bao nhiêu?"
        explanation=f"Đoạn vuông góc chung nối (0;0;0)∈d₁ với (0;0;{p['h']})∈d₂, theo trục Oz. Độ dài bằng {result}."
    elif family == 'three_perpendiculars_ramp':
        p=dict(height=3*k,foot_distance=4*k);result=5*k
        stem=f"Điểm P cách mặt phẳng (α) đoạn PH={p['height']} cm; hình chiếu H của P lên (α) cách điểm Q thuộc (α) đoạn HQ={p['foot_distance']} cm. Tính PQ."
        explanation=f"PH vuông góc mọi đoạn qua H nằm trong (α), đặc biệt PH⊥HQ. Áp dụng Pythagore PQ=√(PH²+HQ²)={result} cm."
    elif family == 'tetrahedron_section_volume_ratio':
        p=dict(den=k+1);result=Rational(1,p['den']**3)
        stem=f"Trong tứ diện ABCD, mặt phẳng song song đáy BCD cắt ba cạnh từ A theo tỉ số 1/{p['den']} tính từ A. Tính tỉ số thể tích tứ diện nhỏ so với tứ diện ABCD."
        explanation=f"Hai tứ diện đồng dạng tỉ số chiều dài 1/{p['den']}; tỉ số thể tích là lập phương tỉ số chiều dài: (1/{p['den']})³={result}."
    elif family == 'coplanarity_mixed_product':
        p=dict(a=a,b=b,c=k+2);result=-p['c']
        stem=f"Cho A(0;0;0), B({p['a']};0;0), C(0;{p['b']};0), D(1;2;m+{p['c']}). Tìm m để bốn điểm A,B,C,D đồng phẳng."
        explanation=f"Mặt phẳng ABC là z=0 (AB và AC không cùng phương). D thuộc (ABC) khi m+{p['c']}=0, do đó m={result}."
    elif family == 'factor_trig_equation_root_sine':
        p=dict(cnum=1, cden=k+2);result=Rational(p['cnum'],2*p['cden'])
        stem=f"Giả sử cos x≠0 và sin(2x)=(1/{p['cden']})cos x. Tính sin x theo điều kiện đã cho."
        explanation=f"Thế sin(2x)=2sin x cos x, rồi chia cả hai vế cho cos x≠0: 2sin x=1/{p['cden']}. Vì vậy sin x={result}."
    elif family == 'cubic_local_max_value':
        p=dict(a=k+2);result=2*p['a']**3
        stem=f"Cho f(x)=x³−{3*p['a']**2}x. Giá trị cực đại địa phương của f bằng bao nhiêu?"
        explanation=f"f'(x)=3(x²−{p['a']**2}), đổi dấu + sang − tại x=−{p['a']}. Khi đó f(−{p['a']})=−{p['a']}³+3·{p['a']}³={result}."
    elif family == 'cubic_inflection_x':
        p=dict(a=a,b=b+k,c=c);result=Rational(-p['b'],3*p['a'])
        stem=f"Đồ thị f(x)={p['a']}x³+{p['b']}x²+{p['c']}x+1 có điểm uốn tại x=t. Tìm t."
        explanation=f"Đạo hàm cấp hai f''(x)=6·{p['a']}x+2·{p['b']}. Giải f''(t)=0 được t=−{p['b']}/(3·{p['a']})={result}."
    elif family == 'monotone_cubic_closed_interval_max':
        p=dict(a=a,left=-k,right=k);result=p['right']**3+p['a']*p['right']
        stem=f"Tìm giá trị lớn nhất của f(x)=x³+{p['a']}x trên đoạn [{p['left']};{p['right']}]."
        explanation=f"Đạo hàm f'(x)=3x²+{p['a']}>0 trên R, nên f đồng biến. Giá trị lớn nhất trên đoạn đạt tại x={p['right']}: f={result}."
    elif family == 'parabola_horizontal_intersections':
        p=dict(b=k+2,state=ordinal%3);p['h']=p['b']+[0,1,-1][p['state']];result=[1,2,0][p['state']]
        stem=f"Parabol y=x²+{p['b']} cắt đường thẳng ngang y={p['h']} tại bao nhiêu điểm phân biệt trong mặt phẳng?"
        explanation=f"Phương trình giao điểm x²={p['h']-p['b']}. Vế phải dương có 2 nghiệm, bằng 0 có 1, âm không có nghiệm; ở đây có {result} giao điểm."
    elif family == 'exponential_derivative_origin':
        p=dict(A=a+k,k=b);result=p['A']*p['k']
        stem=f"Cho f(x)={p['A']}e^({p['k']}x). Tính đạo hàm f'(0) với e là cơ số logarit tự nhiên."
        explanation=f"Với e^({p['k']}x), đạo hàm là {p['k']}e^({p['k']}x). Do đó f'(x)={p['A']}·{p['k']}e^({p['k']}x); tại x=0 ta có f'(0)={result}."
    elif family == 'distance_parallel_planes_3d':
        p=dict(a=3,b=4,c=0,d1=k,d2=k+5*a);result=Rational(abs(p['d2']-p['d1']),5)
        stem=f"Hai mặt phẳng song song (P):3x+4y={p['d1']} và (Q):3x+4y={p['d2']}. Tính khoảng cách giữa (P),(Q)."
        explanation=f"Hai mặt phẳng có cùng pháp tuyến (3;4;0), độ dài 5. Khoảng cách d=|{p['d2']}−{p['d1']}|/√(3²+4²)={result}."
    elif family == 'line_projection_parameter':
        p=dict(x0=a,y0=b,z0=c,vx=3,vy=4,vz=2,t=k,offset=randint(1,5));p['X']=p['x0']+p['vx']*p['t']+p['vy']*p['offset'];p['Y']=p['y0']+p['vy']*p['t']-p['vx']*p['offset'];p['Z']=p['z0']+p['vz']*p['t'];result=p['t']
        stem=f"Đường thẳng d: (x,y,z)=({p['x0']},{p['y0']},{p['z0']})+t(3,4,2). Hình chiếu vuông góc của A({p['X']},{p['Y']},{p['Z']}) lên d ứng với tham số t nào?"
        explanation=f"Dùng t=((A−P₀)·v)/(v·v). Vectơ vuông góc cộng thêm ({4*p['offset']};{-3*p['offset']};0) có tích vô hướng với (3;4;2) bằng 0, nên t={result}."
    elif family == 'two_lines_angle_cos2_3d':
        p=dict(a=11*k+randint(1,4),b=b);result=Rational(1,(p['a']**2+1)*(p['b']**2+1))
        stem=f"Hai đường thẳng trong Oxyz có vectơ chỉ phương u=({p['a']};0;1), v=(0;{p['b']};1). Tính cos² góc giữa chúng."
        explanation=f"cos²θ=(u·v)²/(||u||²||v||²). Ở đây u·v=1, ||u||²={p['a']**2+1}, ||v||²={p['b']**2+1}, được {result}."
    elif family == 'shipping_linear_profit_optimal':
        p=dict(k=k,b=b,unit_cost=a,fixed=c);p['A']=p['unit_cost']+2*p['b']*p['k'];result=p['k']
        stem=f"Một doanh nghiệp bán q sản phẩm theo giá P(q)={p['A']}−{p['b']}q (nghìn đồng/chiếc), biến phí {p['unit_cost']} nghìn đồng/chiếc, định phí {p['fixed']} nghìn đồng. Sản lượng q nào tối đa lợi nhuận theo mô hình liên tục?"
        explanation=f"Lợi nhuận L(q)=qP(q)−{p['unit_cost']}q−{p['fixed']}=−{p['b']}q²+{p['A']-p['unit_cost']}q−{p['fixed']}. Đỉnh parabol tại q=({p['A']-p['unit_cost']})/(2·{p['b']})={result}."
    elif family == 'tetrahedron_volume_determinant':
        p=dict(a=3*k,b=2*(k+1),c=6*(a+1));result=Rational(p['a']*p['b']*p['c'],6)
        stem=f"Tứ diện OABC trong Oxyz có O(0;0;0), A({p['a']};0;0), B(0;{p['b']};0), C(0;0;{p['c']}). Tính thể tích."
        explanation=f"Thể tích tứ diện bằng |det(OA,OB,OC)|/6. Ba vectơ nằm trên ba trục nên định thức={p['a']}·{p['b']}·{p['c']}; V={result}."
    elif family == 'skew_lines_scalar_triple':
        p=dict(h=k+2);result=p['h']
        stem=f"Trong Oxyz cho d₁ qua O có chỉ phương u=(1;0;0) và d₂ qua P(0;1;{p['h']}) có chỉ phương v=(0;1;0). Tính giá trị tuyệt đối tích hỗn tạp [OP,u,v] để xét chéo nhau."
        explanation=f"u×v=(0;0;1), OP=(0;1;{p['h']}), nên |OP·(u×v)|=|{p['h']}|={result}≠0, do đó hai đường thẳng chéo nhau."
    elif family == 'parameter_plane_sphere_center':
        p=dict(x=k+1,y=a,z=b,ay=b,az=c,m=k+3);p['D']=p['m']*p['x']+p['ay']*p['y']+p['az']*p['z'];result=p['m']
        stem=f"Mặt cầu có tâm I({p['x']};{p['y']};{p['z']}). Tìm m để mặt phẳng mx+{p['ay']}y+{p['az']}z={p['D']} đi qua tâm I."
        explanation=f"Thế I vào phương trình: m·{p['x']}+{p['ay']}·{p['y']}+{p['az']}·{p['z']}={p['D']}. Suy ra m={result}."
    elif family == 'closest_point_to_plane_squared':
        p=dict(a=3,b=4,c=0,x=k,y=a,z=b,d=randint(0,4));result=Rational((3*p['x']+4*p['y']+p['d'])**2,25)
        stem=f"Xét điểm A({p['x']};{p['y']};{p['z']}) và mặt phẳng (P):3x+4y+{p['d']}=0. Giá trị nhỏ nhất của AM² khi M chạy trên (P) là bao nhiêu?"
        explanation=f"Khoảng cách AM nhỏ nhất khi M là hình chiếu vuông góc của A lên (P). Khi đó AM²=(3·{p['x']}+4·{p['y']}+{p['d']})²/(3²+4²)={result}."
    else:
        raise ValueError(f'Family {family} lacks a validated generator')
    if result is None or not stem or not explanation:
        raise ValueError(f'Incomplete generator {family}')
    answer=str(simplify(result))
    q=dict(family=family,ordinal=ordinal,params=p,stem=stem,answer=answer,
           solution=explanation,difficulty=difficulty,generation_key=source,
           method_review_status='pending-expert-review')
    q['fingerprint']=sha256(re.sub(r'\s+',' ',stem.strip().casefold()).encode('utf-8')).hexdigest()
    return q


def _oracle(f,p):
    """Parameter-based mathematical recomputation distinct from stored answer."""
    x=Symbol('x')
    if f=='truth_implication': return Integer(int(p['p']==0 or p['q']==1))
    if f=='cartesian_product_count': return Integer(p['a']*p['b'])
    if f=='three_set_union':
        return Integer(p['only_a']+p['only_b']+p['only_c']+p['only_ab']+p['only_ac']+p['only_bc']+p['all_three'])
    if f=='integer_interval_count': return Integer(len(range(p['low']+1,p['high']+1)))
    if f=='sqrt_domain_lower_bound': return -Rational(p['b'],p['a'])
    if f=='linear_zero': return -Rational(p['b'],p['a'])
    if f=='vieta_squares': return Integer(p['sum']**2-2*p['product'])
    if f=='symmetric_system_xy': return Rational(p['S']**2-p['Q'],2)
    if f=='radical_equation_isolation': return Integer(p['m']**2-p['offset'])
    if f=='alternate_interior_angle': return Integer(p['angle'])
    if f=='congruent_triangle_corresponding': return Integer(p['length'])
    if f=='right_triangle_median': return Rational(p['hyp'],2)
    if f=='rhombus_diagonal_area': return Rational(p['d1']*p['d2'],2)
    if f=='circle_chord_length': return 2*sqrt(p['radius']**2-p['distance']**2)
    if f=='thales_similarity_length': return Rational(p['small']*p['known'],p['large'])
    if f=='triangle_area_common_height': return Rational(p['base1'],p['base2'])
    if f=='inscribed_angle': return Rational(p['central'],2)
    if f=='tangent_segment_length': return sqrt(p['OP']**2-p['r']**2)
    if f=='triangle_inequality_integer_sides': return Integer(len(range(abs(p['a']-p['b'])+1,p['a']+p['b'])))
    if f=='amgm_two_positive_min': return 2*sqrt(p['product'])
    if f=='pigeonhole_minimum': return ceiling(Rational(p['objects'],p['boxes']))
    if f=='circle_line_secant_count':
        sq=p['r']**2-p['y']**2
        return Integer(2 if sq>0 else (1 if sq==0 else 0))
    if f=='economic_linear_break_even': return Rational(p['fixed'],p['sale']-p['unit'])
    if f=='vector_component_projection': return Integer(p['x'])
    if f=='trig_cos_double_angle': return 2*Rational(p['num'],p['den'])**2-1
    if f=='trig_equation_zero_solution_count': return Integer(p['n']+1)
    if f=='ap_difference_two_terms': return Rational(p['uj']-p['ui'],p['j']-p['i'])
    if f=='ap_missing_index': return 1+Rational(p['value']-p['first'],p['d'])
    if f=='removable_limit_difference_squares': return Integer(2*p['a'])
    if f=='piecewise_continuity_parameter': return Integer(p['a']*p['t']+p['b'])
    if f=='derivative_product_at': return Integer(2*p['a']*p['c']*p['t']+p['a']*p['d']+p['b']*p['c'])
    if f=='tangent_slope_cubic': return Integer(3*p['t']**2-p['a'])
    if f=='recurrence_arithmetic_summation': return Integer(p['u0'])+sum(range(1,p['n']+1))
    if f=='square_sum_induction': return sum(Integer(j)**2 for j in range(1,p['n']+1))
    if f=='independent_intersection': return Rational(p['a']*p['c'],p['b']*p['d'])
    if f=='vandermonde_convolution': return sum(binomial(p['n'],j)*binomial(p['m'],p['choose']-j) for j in range(p['choose']+1))
    if f=='translation_point_2d': return Integer(p['x']+p['dx'])
    if f=='reflection_diagonal': return Integer(p['x'])
    if f=='rotation_quarter_turn': return Integer(-p['y'])
    if f=='composition_transforms': return Integer(-p['y']+p['dy'])
    if f=='rectangular_prism_diagonal': return sqrt(p['a']**2+p['b']**2+p['c']**2)
    if f=='angle_line_plane_right_triangle': return Rational(p['height'],p['length'])
    if f=='infinite_geometric_series': return Rational(p['first']*p['den'],p['den']-1)
    if f=='conditional_bayes_table': return Rational(p['ill']*p['positive_if_ill'],p['ill']*p['positive_if_ill']+(p['total']-p['ill'])*p['positive_if_well'])
    if f=='investment_geometric_growth': return Integer(p['initial']*p['multiplier']**p['years'])
    if f=='cubic_stationary_positive': return sqrt(p['a']**2)
    if f=='increasing_quadratic_threshold': return Integer(p['a'])
    if f=='rational_vertical_asymptote': return Integer(p['k'])
    if f=='tangent_intercept_quadratic': return Integer(p['c']-p['a']*p['t']**2)
    if f=='exponential_inequality_integer': return Integer(p['power']+1)
    if f=='logarithm_inequality_integer': return Integer(len(range(2**p['power'],p['top']+1)))
    if f=='log_change_of_base': return Integer(p['exponent'])
    if f=='plane_constant_from_point': return Integer(-(p['a']*p['x']+p['b']*p['y']+p['c']*p['z']))
    if f=='line_parametric_z': return Integer(p['z0']+p['vz']*p['t'])
    if f=='line_plane_intersection_t': return Rational(p['D']-p['x0']-p['y0']-p['z0'],p['vx']+p['vy']+p['vz'])
    if f=='plane_angle_cos2': return Rational((p['a']*p['b'])**2,(1+p['a']**2)*(1+p['b']**2))
    if f=='line_plane_angle_sin2': return Rational((1+p['a']*p['b'])**2,(1+p['a']**2)*(1+p['b']**2))
    if f=='sphere_tangent_plane_d': return Integer(-p['cx']-p['r'])
    if f=='sphere_plane_section_area': return pi*(p['R']**2-p['d']**2)
    if f=='projection_3d_coordinate': return sqrt(p['y']**2+p['z']**2)
    if f=='complex_distance_modulus': return sqrt((p['x2']-p['x1'])**2+(p['y2']-p['y1'])**2)
    if f=='volume_revolution_quadratic': return Rational(p['a']**2*p['length']**3,3)*pi
    if f=='integral_area_parabola': return Rational(4*p['a']**3,3)
    if f=='hypergeometric_expected': return Rational(p['n']*p['K'],p['N'])
    if f=='weighted_mean_frequency': return Rational(p['x1']*p['f1']+p['x2']*p['f2'],p['f1']+p['f2'])
    if f=='finance_simple_interest': return Rational(p['principal']*p['percent']*p['years'],100)
    if f=='coordinate_line_intercept': return Integer(p['y']-p['slope']*p['x'])
    if f=='parallelogram_diagonal_midpoint': return Rational(p['width']+p['height'],2)
    if f=='perpendicular_bisector_locus': return Rational(p['x1']+p['x2'],2)
    if f=='prism_edge_count': return Integer(3*p['n'])
    if f=='trig_fundamental_period': return 2*pi/Rational(p['k'])
    if f=='trig_cos_one_root_count': return Integer(p['n']+1)
    if f=='parallel_3d_direction_ratio': return Integer(3*p['b'])
    if f=='perpendicular_3d_dot_parameter': return Integer(-2*p['a']-3*p['b'])
    if f=='vertical_distance_to_floor': return Integer(abs(p['z']))
    if f=='median_sorted_odd': return Integer(sorted(p['values'])[len(p['values'])//2])
    if f=='hypergeometric_exactly_two': return binomial(p['good'],2)*binomial(p['bad'],1)/binomial(p['total'],3)
    if f=='homothety_x_coordinate': return Integer(p['x']*p['factor'])
    if f=='pyramid_parallel_square_section': return Rational(p['side']**2,4)
    if f=='geometric_depreciation_value': return Rational(p['initial']*p['remain_num']**p['years'],p['remain_den']**p['years'])
    if f=='reflection_y_axis_x': return Integer(-p['x'])
    if f=='euler_polyhedron_edges': return Integer(p['V']+p['F']-2)
    if f=='coordinate_plane_intersection_line': return Integer(p['x']+p['y'])
    if f=='line_plane_parallel_condition': return Rational(-p['a']-2*p['b'],p['c'])
    if f=='parallel_plane_normal_parameter': return Integer(p['c']*p['k'])
    if f=='line_plane_perp_condition': return Integer(p['c']*p['k'])
    if f=='tetrahedron_parallel_section_area': return Rational(p['base_area'],9)
    if f=='skew_axis_distance': return Integer(abs(p['h']))
    if f=='three_perpendiculars_ramp': return sqrt(p['height']**2+p['foot_distance']**2)
    if f=='tetrahedron_section_volume_ratio': return Rational(1,p['den']**3)
    if f=='coplanarity_mixed_product': return Integer(-p['c'])
    if f=='factor_trig_equation_root_sine': return Rational(p['cnum'],2*p['cden'])
    if f=='cubic_local_max_value': return Integer(2*p['a']**3)
    if f=='cubic_inflection_x': return Rational(-p['b'],3*p['a'])
    if f=='monotone_cubic_closed_interval_max': return Integer(max(p['left']**3+p['a']*p['left'],p['right']**3+p['a']*p['right']))
    if f=='parabola_horizontal_intersections': return Integer(2 if p['h']>p['b'] else (1 if p['h']==p['b'] else 0))
    if f=='exponential_derivative_origin': return Integer(p['A']*p['k'])
    if f=='distance_parallel_planes_3d': return Rational(abs(p['d2']-p['d1']),sqrt(p['a']**2+p['b']**2+p['c']**2))
    if f=='line_projection_parameter':
        delta=(p['X']-p['x0'],p['Y']-p['y0'],p['Z']-p['z0'])
        return Rational(sum(w*v for w,v in zip(delta,(p['vx'],p['vy'],p['vz']))),p['vx']**2+p['vy']**2+p['vz']**2)
    if f=='two_lines_angle_cos2_3d': return Rational(1,(p['a']**2+1)*(p['b']**2+1))
    if f=='shipping_linear_profit_optimal': return Rational(p['A']-p['unit_cost'],2*p['b'])
    if f=='tetrahedron_volume_determinant': return Rational(abs(p['a']*p['b']*p['c']),6)
    if f=='skew_lines_scalar_triple': return Integer(abs(p['h']))
    if f=='parameter_plane_sphere_center': return Rational(p['D']-p['ay']*p['y']-p['az']*p['z'],p['x'])
    if f=='closest_point_to_plane_squared': return Rational((3*p['x']+4*p['y']+p['d'])**2,25)
    raise ValueError(f'No second mathematical oracle for {f}')


def verify(q: dict):
    f=q.get('family')
    if f not in FAMILIES:
        return False,{'error':'unknown family'}
    try:
        # Independently recompute numeric value from the structured parameters.
        expected=_oracle(f,q['params'])
        if simplify(sympify(q['answer'])-expected)!=0:
            return False, {'error':'answer mismatches mathematical oracle','expected':str(expected)}
        catalog=dict((item[0],item) for item in BLUEPRINTS)
        difficulty=catalog[f][4]
        # Check the wording and worked solution were not silently corrupted.
        regenerated=generate(f,q['ordinal'],difficulty,seed_key=q['generation_key'])
        for field in ('params','stem','solution','fingerprint','difficulty'):
            if q[field]!=regenerated[field]:
                return False,{'error':f'noncanonical or tampered {field}'}
        if len(q['stem'])<40 or len(q['solution'])<35:
            return False,{'error':'too brief question or solution'}
        return True,{'engine':'v114-exact-parameter-oracle-and-roundtrip','numeric_math_verified':True,
                     'method_independence':'pending-independent-method-review',
                     'answer':str(expected)}
    except Exception as e:
        return False,{'error':f'{type(e).__name__}: {e}'}
