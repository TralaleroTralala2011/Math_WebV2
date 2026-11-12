"""V118: authored mathematics archetype candidates, with 10 deterministic items each.

WARNING: mathematical-answer verification != certification of independent pedagogy.
No automatic publication: every archetype remains pending human/topic review.
Each family specifies a distinct objective and an executable rule. Changing data
inside a family is NOT considered another mathematical problem type.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import comb, factorial, gcd, isqrt
from collections import Counter
from pathlib import Path
import json
import re

from sympy import (Integer as Z, Rational as Q, Symbol, pi, sqrt, sin, cos,
                   exp, log, simplify, diff, integrate, limit, oo, Matrix, factor)

x = Symbol('x', real=True)

@dataclass(frozen=True)
class Method:
    family: str
    topic: str
    title: str
    signature: str
    skill: str
    grade: int
    difficulty: str = 'trung cấp'
    real_world: bool = False

METHODS: list[Method] = []
_HANDLERS = {}

def method(family, topic, title, signature, skill, grade, difficulty='trung cấp', real_world=False):
    def deco(fn):
        if family in _HANDLERS:
            raise ValueError('duplicate family '+family)
        METHODS.append(Method(family,topic,title,signature,skill,grade,difficulty,real_world))
        _HANDLERS[family] = fn
        return fn
    return deco

# ----------------- TOÁN 10 -----------------
@method('v118_cartesian_pair_count','tap_hop','Số phần tử tích Descartes','ordered-pair-product-cardinality','Tích Descartes A×B và phép nhân số lượng',10)
def cartesian(t):
    a=t+2;b=2*t+1
    return {'a':a,'b':b}, f'Cho |A|={a}, |B|={b}. Tích Descartes A×B có bao nhiêu cặp có thứ tự?', Z(a*b),f'Mỗi phần tử A ghép được với {b} phần tử B nên số cặp là {a}·{b}={a*b}.'

@method('v118_pigeonhole_ceil','g10_combinatorics_olympiad','Nguyên lý Dirichlet phân vật vào hộp','pigeonhole-ceiling-forced-occupancy','Chứng minh ít nhất một hộp chứa ⌈n/k⌉ vật bằng phản chứng',10)
def pigeonhole(t):
    n=10+3*t;k=3+t%3;v=(n+k-1)//k
    return {'n':n,'k':k},f'Phân {n} viên bi vào {k} hộp (không nhất thiết đều). Số viên nhỏ nhất được đảm bảo có trong ít nhất một hộp là bao nhiêu?',Z(v),f'Giả sử hộp nào cũng có không quá {v-1} bi, tổng tối đa là {k}·{v-1}={k*(v-1)}<{n}, mâu thuẫn. Vậy ít nhất một hộp chứa ⌈{n}/{k}⌉={v} viên.'

@method('v118_two_by_two_cramer_x','he_phuong_trinh','Tính x bằng quy tắc Cramer','linear-two-by-two-cramer-determinants','Định thức hai phương trình và công thức x=Dx/D',10)
def cramer(t):
    a=t+1;b=2;c=1;d=t+2;x0=t-4;y0=2*t-1;e=a*x0+b*y0;f=c*x0+d*y0
    return {'a':a,'b':b,'c':c,'d':d,'e':e,'f':f},f'Hệ {a}x+{b}y={e}; {c}x+{d}y={f}. Tính x (không giải bằng thử nghiệm).',Z(x0),f'Định thức D={a}·{d}−{b}·{c}={a*d-b*c} ≠0. Dx={e}·{d}−{b}·{f}={e*d-b*f}; x=Dx/D={x0}.'

@method('v118_quad_sign_integer_count','bat_phuong_trinh','Đếm nghiệm nguyên của tam thức không dương','quadratic-sign-chart-integer-root-interval','Phân tích nhân tử, lập bảng dấu rồi đếm số nguyên',10)
def quad_sign(t):
    p=t-6;q=t+1+t%4
    return {'p':p,'q':q},f'Có bao nhiêu số nguyên x thỏa (x−({p}))(x−({q}))≤0?',Z(q-p+1),f'Hai nghiệm là {p} và {q}; hệ số x² dương, tích không dương trong đoạn [{p},{q}]. Có {q}−({p})+1={q-p+1} giá trị nguyên.'

@method('v118_similarity_area_scale','g10_geom_thales_similarity','Tỉ số diện tích hai tam giác đồng dạng','similarity-squared-length-factor','Diện tích đồng dạng tỉ lệ với bình phương tỉ số cạnh',10)
def similarity(t):
    A=5+t;k=2+t%4
    return {'area':A,'ratio':k},f'Tam giác B đồng dạng với tam giác A có diện tích {A} cm² và tỉ số cạnh B/A là {k}. Tính diện tích tam giác B.',Z(A*k*k),f'Diện tích tỉ lệ bình phương tỉ số đồng dạng: SB=SA·k²={A}·{k}²={A*k*k} cm².'

@method('v118_external_tangent_length','g10_geom_circle_tangent_chord','Độ dài tiếp tuyến từ điểm ngoài','power-of-point-tangent-pythagoras','Từ bán kính vuông góc tiếp tuyến: PT²=PO²−r²',10)
def tangent_len(t):
    r=3*t;h=4*t;d=5*t
    return {'r':r,'d':d},f'Từ điểm P cách tâm O của đường tròn {d} cm, kẻ tiếp tuyến PT tới đường tròn bán kính {r} cm. Tính PT.',Z(h),f'Vì OT vuông góc PT, PT²=PO²−OT²={d}²−{r}²; do đó PT=√({d*d-r*r})={h} cm.'

@method('v118_cyclic_opposite_angle','duong_tron_co_ban_10','Góc đối trong tứ giác nội tiếp','cyclic-quadrilateral-opposite-supplementary','Hai góc đối của tứ giác nội tiếp có tổng 180°',10)
def cyclic(t):
    a=45+7*t
    return {'angle':a},f'Tứ giác ABCD nội tiếp đường tròn, ∠A={a}°. Tính ∠C (đơn vị độ).',Z(180-a),f'Tứ giác nội tiếp có ∠A+∠C=180°. Vậy ∠C=180−{a}={180-a}°.'

@method('v118_vector_parallel_parameter','vector','Điều kiện hai vectơ phẳng cùng phương','determinant-zero-vector-parallelism','Định thức hai vectơ Oxy bằng 0',10)
def parallel(t):
    a=t+2;b=t+3;c=2*t+1
    return {'a':a,'b':b,'c':c},f'Cho u=({a};{b}), v=({c};m). Tìm m để u và v cùng phương.',Q(b*c,a),f'Hai vectơ khác 0 cùng phương khi định thức của chúng bằng 0. Ta có det(u,v)={a}m−{b}·{c}=0; do đó m={b*c}/{a}={Q(b*c,a)}.'

@method('v118_right_triangle_circumcenter','g10_geom_special_lines','Bán kính ngoại tiếp tam giác vuông','right-triangle-hypotenuse-diameter','Trung điểm cạnh huyền là tâm đường tròn ngoại tiếp',10)
def right_circum(t):
    a=6*t;b=8*t;c=10*t
    return {'a':a,'b':b,'c':c},f'Tam giác vuông có hai cạnh góc vuông {a} cm và {b} cm. Tính bán kính đường tròn ngoại tiếp.',Z(5*t),f'Theo Pythagoras, cạnh huyền c=√({a}²+{b}²)={c}. Trong tam giác vuông, R=c/2={5*t} cm.'

@method('v118_fixed_digit_even_numbers','g10_combinatorics_olympiad','Đếm số chẵn có chữ số khác nhau và chữ số đầu khác 0','even-number-digit-case-split','Chia hai trường hợp chữ số cuối bằng 0 hoặc khác 0',10)
def even_numbers(t):
    n=6+(t-2)%5   # 6..10 digit alphabet, each paired with length 3/4
    k=3+(t-2)//5   # 3 or 4 digits; ten distinct input specifications
    arrangements=factorial(n-2)//factorial(n-k)
    even_nonzero=len([digit for digit in range(2,n,2)])
    end0=(n-1)*arrangements
    endpos=even_nonzero*(n-2)*arrangements
    value=end0+endpos
    return {'n':n,'k':k},f'Dùng các chữ số 0,1,...,{n-1}, lập số tự nhiên chẵn có {k} chữ số phân biệt. Có bao nhiêu số?',Z(value),f'Cuối là 0: {n-1}·P({n-2},{k-2})={end0} cách. Cuối chẵn khác 0: {even_nonzero}·{n-2}·P({n-2},{k-2})={endpos} cách. Tổng {value}.'

@method('v118_binomial_sum_alternating','nhi_thuc_newton','Tổng tổ hợp có dấu xen kẽ','binomial-theorem-at-minus-one','Áp dụng (1−1)^n=Σ(-1)^k C(n,k)',10)
def alternating_binomial(t):
    n=t+3
    return {'n':n},f'Tính S=C({n},0)−C({n},1)+C({n},2)−...+(-1)^{n}C({n},{n}).',Z(0),f'Theo khai triển nhị thức Newton, tổng S chính là giá trị (1−1)^{n}. Vì {n}>0 nên S=0; mọi hạng tử tổ hợp được đếm đầy đủ.'

@method('v118_circle_equation_from_diameter','toa_do_hinh_hoc_10','Tìm bình phương bán kính đường tròn qua đường kính','diameter-endpoints-radius-squared','R²=|AB|²/4 theo hai đầu mút đường kính',10)
def diameter_circle(t):
    a=t-4;b=t+1;c=2*t-1;d=-t
    return {'a':a,'b':b,'c':c,'d':d},f'Trong Oxy, A({a};{b}), B({c};{d}) là hai đầu đường kính. Tính R² của đường tròn.',Q((c-a)**2+(d-b)**2,4),f'Đường kính AB có AB²=({c}−{a})²+({d}−{b})²; R²=AB²/4={Q((c-a)**2+(d-b)**2,4)}.'

# ----------------- TOÁN 11 -----------------
@method('v118_ap_two_terms_reconstruct','cap_so_cong','Tìm số hạng cấp số cộng từ hai số hạng đã biết','arithmetic-sequence-recover-common-difference','d=(u_j−u_i)/(j−i) rồi dùng u_n',11)
def ap_two(t):
    i=2;j=t+5;n=t+9;d=t-3;u1=2*t+1
    ui=u1+(i-1)*d;uj=u1+(j-1)*d
    return {'i':i,'j':j,'n':n,'ui':ui,'uj':uj},f'Cấp số cộng có u{i}={ui}, u{j}={uj}. Tính u{n}.',Z(u1+(n-1)*d),f'Công sai d=({uj}−{ui})/({j}−{i})={d}. u{n}=u{i}+({n}−{i})d={u1+(n-1)*d}.'

@method('v118_affine_recurrence_explicit','day_so_truy_hoi_11','Công thức tường minh truy hồi tuyến tính affine','affine-recurrence-shift-fixed-point-and-geometric','Đặt v_n=u_n−c để quy về cấp số nhân',11)
def recurrence_explicit(t):
    a=2+(t%3);c=t+2;u1=c+2;n=3+t%4;b=(1-a)*c
    val=c+2*a**(n-1)
    return {'a':a,'b':b,'u1':u1,'n':n},f'Dãy có u₁={u1}, u_{{n+1}}={a}u_n+({b}). Tính u{n}.',Z(val),f'Điểm bất động c={c} vì c={a}c+({b}). Đặt v_n=u_n−c, ta có v_{{n+1}}={a}v_n, v₁=2. u{n}={c}+2·{a}^{n-1}={val}.'

@method('v118_square_sum_formula','quy_nap_toan_hoc_11','Tổng bình phương liên tiếp qua quy nạp','sum-first-n-squares-induction','Σk²=n(n+1)(2n+1)/6 chứng minh được quy nạp',11)
def sum_squares(t):
    n=5+t
    return {'n':n},f'Tính tổng S=1²+2²+...+{n}².',Z(n*(n+1)*(2*n+1)//6),f'Công thức chứng minh bằng quy nạp: Σ(k²)=n(n+1)(2n+1)/6. Với n={n}, S={n}·{n+1}·{2*n+1}/6={n*(n+1)*(2*n+1)//6}.'

@method('v118_trig_tan_sum','cong_thuc_luong_giac','Tang tổng hai góc từ hai giá trị tang','tangent-addition-rational-fraction','tan(a+b)=(tan a+tan b)/(1−tan a tan b)',11)
def tan_sum(t):
    a=Q(1,t+2);b=Q(1,t+3);v=(a+b)/(1-a*b)
    return {'a':str(a),'b':str(b)},f'Hai góc α,β có tanα={a}, tanβ={b} và α+β khác π/2 mod π. Tính tan(α+β).',simplify(v),f'Công thức tan tổng: ({a}+{b})/(1−{a}·{b})={simplify(v)}.'

@method('v118_count_trig_cos_period','phuong_trinh_luong_giac','Đếm nghiệm cos x=1 theo chu kỳ','trig-period-two-pi-lattice-count','cos x=1 khi x=2kπ, đếm k nguyên trên đoạn',11)
def cos_period(t):
    a=-t;b=t+3;v=a*(-1)+b+1
    return {'lo':a,'hi':b},f'Có bao nhiêu nghiệm x của cos x=1 trên đoạn [{2*a}π;{2*b}π]?',Z(v),f'cos x=1 ⇔ x=2kπ. Bất đẳng thức {a}≤k≤{b} có {b}−({a})+1={v} giá trị nguyên.'

@method('v118_limit_rational_infinity','gioi_han_ham_so','Giới hạn vô cực của phân thức hai đa thức cùng bậc','rational-infinity-leading-coefficient-ratio','Chia cả tử và mẫu cho lũy thừa cao nhất',11)
def rational_infty(t):
    a=t+3;b=t+4;c=t-2;d=t+6
    return {'a':a,'b':b,'c':c,'d':d},f'Tính lim(x→+∞) ({a}x²+{b}x+1)/({d}x²+{c}x+3).',Q(a,d),f'Chia tử và mẫu cho x², các hạng 1/x và 1/x² tiến về 0. Giới hạn bằng {a}/{d}={Q(a,d)}.'

@method('v118_limit_radical_conjugate','gioi_han','Giới hạn vô cực dạng hiệu căn bằng liên hợp','rationalize-root-difference-at-infinity','Nhân liên hợp √(x²+a x)−x để khử vô định',11)
def radical_infty(t):
    a=t+2
    return {'a':a},f'Tính giới hạn khi x→+∞ của √(x²+{a}x)−x.',Q(a,2),f'Nhân lượng liên hợp, biểu thức thành {a}x/(√(x²+{a}x)+x)={a}/(√(1+{a}/x)+1) → {Q(a,2)}.'

@method('v118_derivative_quotient','dao_ham_quy_tac','Đạo hàm thương hai hàm tuyến tính','quotient-rule-linear-over-linear','(u/v)′=(u′v−uv′)/v²',11)
def derivative_quotient(t):
    a=t+1;b=3+t;c=t+2;d=t+5;x0=t-2;den=c*x0+d
    assert den>0
    v=Q(a*d-b*c,den**2)
    return {'a':a,'b':b,'c':c,'d':d,'x0':x0},f'Cho f(x)=({a}x+{b})/({c}x+{d}). Tính f′({x0}).',v,f'Đạo hàm thương f′(x)=({a}({c}x+{d})−{c}({a}x+{b}))/({c}x+{d})²=({a*d-b*c})/({c}x+{d})². Suy ra f′({x0})={v}.'

@method('v118_inverse_derivative','ung_dung_dao_ham_11','Đạo hàm hàm ngược tại ảnh của một điểm','inverse-function-derivative-reciprocal','(f⁻¹)′(f(a))=1/f′(a)',11)
def inverse_derivative(t):
    a=t+2;v=Q(1,3*a*a+1)
    return {'a':a},f'Cho f(x)=x³+x tăng nghiêm ngặt trên ℝ, g=f⁻¹. Tính g′({a*a*a+a}).',v,f'f({a})={a*a*a+a}; f′({a})=3·{a}²+1={3*a*a+1}. Theo đạo hàm hàm ngược, g′(f({a}))=1/f′({a})={v}.'

@method('v118_pyramid_section_parallel_area','g11_geom_section_ratio','Tỉ số diện tích thiết diện song song đáy hình chóp','pyramid-similar-section-area-square-ratio','Thiết diện song song đáy có tỉ số diện tích bằng bình phương tỉ số khoảng cách từ đỉnh',11)
def pyramid_section(t):
    S=8+t;k=Q(1,t+1)
    return {'S':S,'k':str(k)},f'Một hình chóp có đáy diện tích {S} cm². Thiết diện song song đáy cắt mỗi cạnh bên tại điểm cách đỉnh một đoạn bằng {k} độ dài cạnh bên. Diện tích thiết diện bằng bao nhiêu?',S*k*k,f'Thiết diện đồng dạng với đáy theo tỉ số {k}, nên diện tích bằng {S}·({k})²={S*k*k} cm².'

@method('v118_prism_lateral_area','g11_geom_prism_pyramid_sections','Diện tích xung quanh lăng trụ đứng đáy tam giác vuông','right-triangular-prism-lateral-area-perimeter','Tính chu vi tam giác vuông đáy rồi nhân chiều cao lăng trụ',11)
def prism_lateral_area(t):
    a=3*t;b=4*t;h=t+2;c=5*t
    return {'a':a,'b':b,'h':h},f'Lăng trụ đứng có đáy là tam giác vuông với hai cạnh góc vuông {a} cm, {b} cm và chiều cao {h} cm. Tính diện tích xung quanh.',Z((a+b+c)*h),f'Cạnh huyền đáy =√({a}²+{b}²)={c}. Chu vi đáy = {a}+{b}+{c}={a+b+c}. Diện tích xung quanh = chu vi đáy · chiều cao = {a+b+c}·{h}={(a+b+c)*h} cm².'

@method('v118_3d_skew_lines_distance_axes','g11_geom_skew_lines_distance','Khoảng cách hai đường thẳng chéo nhau theo đoạn vuông góc chung','skew-lines-common-perpendicular-axes','Tìm đoạn nối hai đường vuông góc với cả hai đường trong lăng trụ đứng',11)
def skew_distance(t):
    h=t+2;a=t+1;b=t+3
    return {'h':h,'a':a,'b':b},f'Lăng trụ đứng ABC.A′B′C′ có đáy ABC vuông tại B, AB={a} cm, BC={b} cm, cạnh bên BB′={h} cm. Tính khoảng cách giữa hai đường thẳng AB và B′C′.',Z(h),f'Đoạn BB′ có đầu B thuộc AB, đầu B′ thuộc B′C′. BB′ vuông góc mặt đáy nên vuông góc AB; vì B′C′ song song BC nằm trong mặt phẳng đáy nên BB′ cũng vuông góc B′C′. BB′ là đoạn vuông góc chung, khoảng cách bằng {h} cm.'

# ----------------- TOÁN 12 -----------------
@method('v118_vertical_asymptote_cancel','tien_can','Nhận diện tiệm cận đứng sau khi khử điểm gián đoạn có thể bỏ','vertical-asymptote-versus-removable-hole','Rút gọn nhân tử chung rồi phân biệt điểm khuyết và cực',12)
def vertical(t):
    a=t+1;b=t+3;c=-t-2
    return {'a':a,'b':b,'c':c},f'Cho hàm số y=[(x−({a}))(x−({b}))]/[(x−({a}))(x−({c}))] với x≠{a},{c}. Tìm hoành độ tiệm cận đứng.',Z(c),f'Khử nhân tử x−({a}) khi x≠{a}, ta được (x−({b}))/(x−({c})). Tại x={a} có điểm khuyết, không phải tiệm cận. Mẫu còn lại bằng 0 tại x={c}, tử khác 0, nên x={c} là tiệm cận đứng.'

@method('v118_log_derivative_at','ung_dung_dao_ham','Đạo hàm logarit của biểu thức bậc nhất','logarithmic-chain-derivative-at-point','(ln u)′=u′/u với u>0',12)
def log_derivative(t):
    a=t+1;b=t+2;x0=t+1
    return {'a':a,'b':b,'x0':x0},f'Cho f(x)=ln({a}x+{b}) với {a}x+{b}>0. Tính f′({x0}).',Q(a,a*x0+b),f'Dùng (ln u)′=u′/u: f′(x)={a}/({a}x+{b}); tại x={x0} được {Q(a,a*x0+b)}.'

@method('v118_inflection_cubic','khao_sat_ham_so','Hoành độ điểm uốn của hàm bậc ba','inflection-via-second-derivative-zero','Giải f″(x)=0 rồi kiểm tra dấu',12)
def inflection(t):
    a=t%4+1;b=-(t+2)*3*a;c=t+5
    v=Q(-b,3*a)
    return {'a':a,'b':b,'c':c},f'Cho y={a}x³+({b})x²+{c}x+1. Tính hoành độ điểm uốn.',v,f'f″(x)=6·{a}x+2·({b}). Nghiệm f″(x)=0 là x=−({b})/(3·{a})={v}, tại đó f″ đổi dấu.'

@method('v118_integral_by_parts','nguyen_ham_tich_phan','Tích phân từng phần của x e^(kx)','integration-by-parts-linear-times-exponential','Đặt u=x, dv=e^(kx)dx rồi áp dụng ∫u dv=uv−∫v du',12)
def parts(t):
    k=t+1
    val=Q((k-1),k*k)*exp(k)+Q(1,k*k)
    return {'k':k},f'Tính I=∫ từ 0 đến 1 của x·e^({k}x) dx.',val,f'Đặt u=x, dv=e^({k}x)dx, suy ra v=e^({k}x)/{k}. I=[xe^({k}x)/{k}]₀¹−[e^({k}x)/{k}²]₀¹=(e^{k}·({k}−1)+1)/{k}²={val}.'

@method('v118_area_between_curves','ung_dung_tich_phan','Diện tích giữa parabol và đường thẳng cắt tại hai điểm','area-between-graphs-integral-upper-minus-lower','S=∫(hàm trên−hàm dưới) từ giao điểm trái đến giao điểm phải',12)
def between(t):
    a=t+1;r=t+3
    v=Q(4*a*r**3,3)
    return {'a':a,'r':r},f'Tính diện tích hình phẳng giới hạn bởi y={a}·{r}² và y={a}x² trên đoạn [−{r};{r}].',v,f'Parabol nằm dưới đường thẳng trên đoạn. S=∫_{{−{r}}}^{{{r}}} {a}({r}²−x²)dx=4·{a}·{r}³/3={v}.'

@method('v118_partial_fraction_integral','nguyen_ham_tich_phan','Tích phân phân thức bằng phân tích thành hai phân thức đơn','integral-partial-fractions-distinct-linear-factors','Phân tích 1/[(x+a)(x+b)] thành hiệu 1/(x+a) và 1/(x+b)',12)
def partial_fractions(t):
    a=t+1;b=a+2
    val=Q(1,b-a)*log(Q(b*(a+1),a*(b+1)))
    return {'a':a,'b':b},f'Tính I=∫ từ 0 đến 1 của 1/[(x+{a})(x+{b})] dx.',val,f'1/[(x+{a})(x+{b})]=[1/(x+{a})−1/(x+{b})]/({b}−{a}). Thế cận 0,1: I=ln({b}({a}+1)/[{a}({b}+1)])/({b}−{a})={val}.'

@method('v118_complex_division_real','so_phuc','Phần thực thương hai số phức','complex-division-conjugate-rationalization','Nhân liên hợp mẫu và tách phần thực',12)
def complex_div(t):
    a=t+1;b=t+3;c=t+4;d=2+t
    v=Q(a*c+b*d,c*c+d*d)
    return {'a':a,'b':b,'c':c,'d':d},f'Cho z=({a}+{b}i)/({c}+{d}i). Tính phần thực Re(z).',v,f'Nhân cả tử và mẫu với {c}−{d}i, mẫu bằng {c}²+{d}²; phần thực tử là {a}·{c}+{b}·{d}. Re(z)={v}.'

@method('v118_complex_locus_circle','g12_complex_plane_geometry','Quỹ tích số phức có môđun khoảng cách cố định','complex-modulus-distance-locus-circle','|z−z₀|=r là đường tròn tâm z₀ bán kính r',12)
def locus_circle(t):
    a=t-3;b=t+1;r=t+2
    return {'a':a,'b':b,'r':r},f'Cho số phức z thỏa |z−({a}+{b}i)|={r}. Tính diện tích hình tròn mà đường biên là quỹ tích của z.',pi*r*r,f'Viết z=x+yi, ta được (x−{a})²+(y−{b})²={r}². Quỹ tích là đường tròn bán kính {r}; diện tích hình tròn bằng π{r}²={pi*r*r}.'

@method('v118_sphere_tangent_plane_d','g12_geom_sphere_tangent_plane','Mặt phẳng tiếp xúc mặt cầu tại điểm đã biết','tangent-plane-normal-radius-vector','Vectơ bán kính tại tiếp điểm là pháp tuyến mặt phẳng',12)
def sphere_tangent(t):
    a=t+1;b=t-2;c=t+3;cx=1;cy=-1;cz=2
    d=a*(cx+a)+b*(cy+b)+c*(cz+c)
    return {'a':a,'b':b,'c':c,'cx':cx,'cy':cy,'cz':cz},f'Mặt cầu tâm I({cx};{cy};{cz}), tiếp điểm T({cx+a};{cy+b};{cz+c}). Mặt phẳng tiếp xúc có dạng {a}x+({b})y+{c}z=d. Tính d.',Z(d),f'IT=({a},{b},{c}) là pháp tuyến. Thế T vào phương trình: d={a}·({cx+a})+({b})·({cy+b})+{c}·({cz+c})={d}.'

@method('v118_tetrahedron_volume_det','the_tich_khong_gian','Thể tích tứ diện từ tích hỗn tạp','tetrahedron-scalar-triple-product','V=|det(u,v,w)|/6 của ba cạnh xuất phát từ một đỉnh',12)
def tetra_volume(t):
    a=t+1;b=t+2;c=t+3
    v=Q(a*b*c,6)
    return {'a':a,'b':b,'c':c},f'Tứ diện OABC có O(0,0,0), A({a},0,0), B(0,{b},0), C(0,0,{c}). Tính thể tích.',v,f'V=|det(OA,OB,OC)|/6={a}·{b}·{c}/6={v} đơn vị thể tích.'

@method('v118_binomial_at_least_two','xac_suat_12','Xác suất ít nhất hai thành công trong ba phép thử','binomial-tail-complement-zero-or-one','P(X≥2)=1−P(X=0)−P(X=1)',12,real_world=True)
def binom_tail(t):
    p=Q(1,t+2);v=3*p*p*(1-p)+p**3
    return {'p':str(p),'n':3},f'Một sản phẩm có xác suất đạt chuẩn {p}; kiểm tra độc lập 3 sản phẩm. Xác suất ít nhất 2 sản phẩm đạt chuẩn là bao nhiêu?',v,f'Theo mô hình nhị thức, P(X≥2)=C(3,2)({p})²(1−{p})+({p})³={v}.'

@method('v118_exponential_doubling_time','bai_toan_thuc_te_12','Thời gian tăng gấp đôi trong mô hình lãi liên tục','exponential-growth-logarithm-doubling','Giải e^(rt)=2 bằng logarit',12,real_world=True)
def doubling(t):
    r=Q(t+1,100)
    return {'r':str(r)},f'Một quần thể tăng theo N(t)=N₀e^({r}t) (t tính bằng năm). Sau bao nhiêu năm quần thể tăng gấp đôi?',log(2)/r,f'Đặt N(t)=2N₀ ⇒ e^({r}t)=2; lấy ln hai vế: ({r})t=ln2. Vậy t=ln2/({r})={log(2)/r} năm.'

@method('v118_plane_angle_normal','g12_geom_two_planes_angle','Cosin góc nhọn hai mặt phẳng từ pháp tuyến','angle-two-planes-normal-vector-dot','cosθ=|n₁·n₂|/(|n₁||n₂|)',12)
def plane_angle(t):
    a=t+1;b=t+2;c=t+3
    u=Matrix([a,b,0]);v=Matrix([a,0,c]);z=simplify(abs(u.dot(v))/(sqrt(u.dot(u))*sqrt(v.dot(v))))
    return {'a':a,'b':b,'c':c},f'Cho hai mặt phẳng có pháp tuyến n₁=({a},{b},0), n₂=({a},0,{c}). Tính cosin góc nhọn giữa chúng.',z,f'Tích vô hướng n₁·n₂={a}²; chuẩn hai vectơ lần lượt √({a*a+b*b}) và √({a*a+c*c}); cosθ={z}.'

@method('v118_exponential_inequality_lower','bpt_mu','Giải bất phương trình mũ với cơ số nhỏ hơn 1','exponential-inequality-reverse-for-decay','Hàm a^x giảm khi 0<a<1, đảo chiều khi so sánh số mũ',12)
def exp_inequality(t):
    b=t+2;k=t-5
    return {'b':b,'k':k},f'Cho a=1/{b}. Tập nghiệm của a^x ≤ a^({k}) là x≥m. Tìm m.',Z(k),f'Vì 0<a=1/{b}<1, hàm a^x nghịch biến. Do đó a^x≤a^{k} ⇔ x≥{k}; m={k}.'

BY_ID={m.family:m for m in METHODS}
FAMILIES=frozenset(BY_ID)
FORMATS=('tra_loi_ngan','trac_nghiem','dung_sai','tu_luan_ngan','van_dung')
COUNT_FAMILIES=len(METHODS)

def _normal(value):
    return str(simplify(value))

def _sha(text):
    return sha256(re.sub(r'\s+',' ',text.casefold().strip()).encode('utf-8')).hexdigest()

def generate(family, ordinal, difficulty=None, seed_key=None):
    if family not in FAMILIES or type(ordinal) is not int or not 0 <= ordinal < 10:
        raise ValueError('family unknown or ordinal not 0..9')
    m=BY_ID[family]; params, stem, numeric, explanation = _HANDLERS[family](ordinal+2)
    numeric=simplify(numeric); answer=_normal(numeric);fmt=FORMATS[ordinal%5];extras={}
    if fmt=='trac_nghiem':
        candidates=[numeric+1,numeric-1,numeric+2,numeric/2,2*numeric,numeric+3,numeric-2]
        if family=='v118_binomial_at_least_two':
            candidates=[1-numeric,numeric/2,(numeric+1)/2,Q(1,3),Q(1,5),Q(2,5),Q(3,4)]
        if family=='v118_plane_angle_normal':
            candidates=[0,Q(1,4),Q(1,3),Q(1,2),sqrt(2)/2,sqrt(3)/2,Q(4,5)]
        opts=[]
        for c in candidates:
            c=simplify(c)
            if simplify(c-numeric)==0 or any(simplify(c-b)==0 for b in opts):continue
            if family=='v118_binomial_at_least_two' and not 0<=float(c)<=1:continue
            if family=='v118_plane_angle_normal' and not 0<=float(c)<=1:continue
            if family in {'v118_cartesian_pair_count','v118_euclidean_gcd','v118_quad_sign_integer_count','v118_cyclic_opposite_angle','v118_fixed_digit_even_numbers','v118_square_sum_formula','v118_count_trig_cos_period','v118_prism_lateral_area','v118_tetrahedron_volume_det'} and float(c)<0:continue
            opts.append(c)
            if len(opts)==3:break
        if len(opts)!=3:raise ValueError('distractors impossible: '+family)
        index=ordinal%4
        display=list(map(_normal,opts));display.insert(index,answer)
        extras={'options':display,'correct_index':index}
        stem+=' Chọn đáp án chính xác trong bốn phương án.'
        explanation+=f' Phương án đúng là {"ABCD"[index]}.'
    elif fmt=='dung_sai':
        assertion=numeric if ordinal<5 else numeric+1
        truth=bool(simplify(assertion-numeric)==0)
        stem+=f' Nhận định “Kết quả bằng {_normal(assertion)}” là đúng hay sai?'
        extras={'assertion_value':_normal(assertion),'truth':truth}
        answer='Đúng' if truth else 'Sai'
        explanation+=f' Nhận định trên {"đúng" if truth else "sai"}.'
    elif fmt=='tu_luan_ngan':stem+=' Trình bày cách giải, nêu đáp số chính xác.'
    elif fmt=='van_dung':
        fmt='toan_thuc_te' if m.real_world else 'van_dung'
        stem+=' Giải thích lý do chọn phương pháp và kết luận.'
    else:stem+=' Ghi kết quả chính xác, không làm tròn.'
    return {'family':family,'ordinal':ordinal,'params':params,'stem':stem,
            'answer':answer,'solution':explanation,'difficulty':difficulty or m.difficulty,
            'question_type':fmt,'numeric_result':_normal(numeric),'topic_id':m.topic,
            'method_signature':m.signature,'skill':m.skill,
            'method_review_status':'pending-expert-review','independence_certified':False,
            'seed_key':seed_key or '', 'fingerprint':_sha(stem),**extras}

def verify(data):
    try:
        family=data.get('family');ordinal=data.get('ordinal')
        if family not in FAMILIES or type(ordinal) is not int:return False,{'error':'invalid family / ordinal'}
        if data!=generate(family,ordinal,data.get('difficulty'),data.get('seed_key')):
            return False,{'error':'record differs from deterministic generator'}
        from .v118_oracle import expected
        oracle=simplify(expected(family,data['params']))
        original=simplify(_HANDLERS[family](ordinal+2)[2])
        if simplify(oracle-original)!=0:return False,{'error':'independent oracle mismatch'}
        # SymPy may represent the same logarithmic value with different log sums.
        # Generator reconstruction already verifies the published numeric_result string.
        if data['question_type']=='trac_nghiem':
            opts=data['options'];k=data['correct_index']
            if len(opts)!=4 or len(set(opts))!=4 or opts[k]!=data['numeric_result']:
                return False,{'error':'invalid MCQ options'}
        if data['question_type']=='dung_sai':
            truth=bool(simplify(__import__('sympy').sympify(data['assertion_value'])-oracle)==0)
            if truth!=data['truth'] or data['answer']!=('Đúng' if truth else 'Sai'):
                return False,{'error':'true/false inconsistency'}
        if len(data['solution'])<45:return False,{'error':'solution too short'}
        return True,{'oracle':'independent parameter calculation','integrity':'deterministic record reconstruction',
                     'publication_blocked':True,'independence_certified':False}
    except Exception as e:
        return False,{'error':str(e),'exception':type(e).__name__}

def export(dest):
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    stems=set();question_counts=Counter()
    with (dest/'V118_NEW_CANDIDATE_FORMS.jsonl').open('w',encoding='utf-8') as f, (dest/'V118_NEW_QUESTIONS.jsonl').open('w',encoding='utf-8') as q:
        for m in METHODS:
            f.write(json.dumps({**m.__dict__,'status':'pending-expert-review','certified_independent':False},ensure_ascii=False)+'\n')
            for i in range(10):
                record=generate(m.family,i)
                valid,proof=verify(record)
                if not valid:raise RuntimeError(f'{m.family} #{i}: {proof}')
                if record['fingerprint'] in stems:raise RuntimeError('duplicate stem')
                stems.add(record['fingerprint'])
                question_counts[record['question_type']]+=1
                q.write(json.dumps({**record,'verification':proof},ensure_ascii=False,default=str)+'\n')
    return {'families':len(METHODS),'question_count':len(stems),'question_formats':dict(question_counts),'independence_certified':0}
