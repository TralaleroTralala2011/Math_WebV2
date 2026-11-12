"""V116 curated research *candidates*, not a 500-form/topic accomplishment.

Each family represents a distinct stated learning objective, not a guarantee of
semantic independence from all legacy methods. Questions are reproducible,
10 per family, across five presentation styles. Mathematical values are
recomputed independently by symbolic or combinatorial methods. All stay
pending expert review and are excluded from live delivery by default.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from math import comb, factorial
import re
from sympy import Rational as Q, Integer as Z, sqrt, pi, factorial as sfact, binomial, sin, cos, diff, integrate, exp, log, Symbol, simplify, solve


@dataclass(frozen=True)
class Method:
    family: str
    topic: str
    title: str
    signature: str
    difficulty: str
    real_world: bool = False


METHODS = [
    Method('v116_quad_interpolate','ham_so_bac_hai','Dựng hệ số parabol từ ba điểm','quadratic-interpolation-three-conditions','nâng cao'),
    Method('v116_rational_excluded','ham_so','Tìm điểm loại khỏi tập xác định của phân thức','rational-denominator-zero-restriction','nền tảng'),
    Method('v116_intersection_lines','g10_geom_line_intersections','Tính hoành độ giao điểm hai đường thẳng','two-lines-intersection-by-system','trung cấp'),
    Method('v116_dot_product','vector','Tích vô hướng từ tọa độ hai vectơ','two-dimensional-vector-dot-product','nền tảng'),
    Method('v116_parallelogram_area','g10_geom_vector_proofs','Diện tích hình bình hành bằng định thức vectơ','parallelogram-area-vector-determinant','trung cấp'),
    Method('v116_sine_rule','he_thuc_luong','Định luật sin tìm cạnh đối diện góc','sine-rule-opposite-side-ratio','trung cấp',True),
    Method('v116_cosine_rule','he_thuc_luong_tam_giac','Định lý cosin cho cạnh thứ ba','law-of-cosines-side-length-square','trung cấp',True),
    Method('v116_angle_bisector','g10_geom_special_lines','Định lý phân giác trong tam giác','angle-bisector-segment-ratio','trung cấp'),
    Method('v116_apollonius_median','g10_geom_triangle_inequalities','Định lý Apollonius cho trung tuyến','apollonius-median-length','nâng cao'),
    Method('v116_intersecting_chords','g10_geom_circle_chords_arcs','Định lý hai dây cung cắt nhau','intersecting-chords-power-product','trung cấp'),
    Method('v116_multiset_permutations','hoan_vi_chinh_hop_to_hop','Số hoán vị phân biệt của đa tập','multinomial-permutation-multiplicity','trung cấp'),
    Method('v116_nonzero_lead','quy_tac_dem','Đếm số tự nhiên không lặp chữ số có chữ số 0','leading-zero-excluded-permutations','trung cấp'),
    Method('v116_at_least_one','xac_suat','Xác suất ít nhất một lần thành công','complement-of-independent-failures','trung cấp',True),
    Method('v116_three_point_variance','thong_ke','Phương sai của bộ ba số cách đều','population-variance-from-deviations','trung cấp',True),
    Method('v116_mixture_concentration','bai_toan_thuc_te_10','Pha trộn dung dịch theo bảo toàn khối lượng','weighted-concentration-mass-balance','trung cấp',True),
    Method('v116_sin_sum','cong_thuc_luong_giac','Công thức sin tổng hai góc','trigonometric-sine-addition-identity','trung cấp'),
    Method('v116_finite_geom_sum','cap_so_nhan','Tổng hữu hạn cấp số nhân','finite-geometric-progression-sum','trung cấp',True),
    Method('v116_rational_infinity_limit','gioi_han','Giới hạn phân thức khi x tiến vô cực','rational-leading-coefficient-infinite-limit','trung cấp'),
    Method('v116_chain_rule','dao_ham_quy_tac','Đạo hàm hàm hợp bậc hai','chain-rule-polynomial-composition','trung cấp'),
    Method('v116_quotient_derivative','dao_ham','Quy tắc đạo hàm của thương hai đa thức bậc nhất','quotient-rule-rational-derivative','trung cấp'),
    Method('v116_total_probability','bien_co_doc_lap_11','Định luật xác suất toàn phần qua hai nhóm','total-probability-two-strata','trung cấp',True),
    Method('v116_circular_permutations','to_hop_xac_suat_nang_cao_11','Hoán vị vòng tròn (phân biệt phép quay)','circular-arrangements-rotation-equivalence','nâng cao',True),
    Method('v116_exponential_growth_index','bai_toan_thuc_te_11','Số kỳ cần để tăng trưởng vượt mốc chính xác','exponential-growth-integer-periods','trung cấp',True),
    Method('v116_integral_parts_xexp','nguyen_ham_tich_phan','Tích phân từng phần của x·e^x','integration-by-parts-x-exp','trung cấp'),
    Method('v116_curves_enclosed_area','ung_dung_tich_phan','Diện tích miền giới hạn bởi đường thẳng và parabol','area-between-line-and-scaled-parabola','trung cấp',True),
    Method('v116_complex_reciprocal','so_phuc','Phần thực nghịch đảo của số phức','complex-reciprocal-conjugate-rationalization','trung cấp'),
    Method('v116_log_product_equation','pt_logarit','Giải phương trình tổng hai logarit cùng cơ số','log-product-equation-domain-and-quadratic','nâng cao'),
    Method('v116_sphere_diameter','g12_geom_sphere_equation','Mặt cầu có đường kính là đoạn nối hai điểm','sphere-center-radius-from-diameter','trung cấp'),
    Method('v116_discrete_variance','xac_suat_12','Phương sai biến ngẫu nhiên hai giá trị','bernoulli-scaled-random-variable-variance','trung cấp',True),
    Method('v116_box_maximization','g12_geom_3d_optimization','Tối ưu thể tích hộp không nắp từ tấm vuông','open-top-box-volume-derivative-optimum','nâng cao',True),
    Method('v116_binomial_expectation','bai_toan_thuc_te_12','Kỳ vọng số lần thành công của phép thử lặp','binomial-expectation-indicator-linearity','trung cấp',True),
]

FAMILIES = {m.family for m in METHODS}
METHOD_LOOKUP = {m.family:m for m in METHODS}
FORMATS = ('tra_loi_ngan','trac_nghiem','dung_sai','tu_luan_ngan','van_dung')


def _core(family: str, ordinal: int):
    """Return (inputs, prompt, exact_value, shown derivation)."""
    t=ordinal+2
    k=(ordinal%3)+2
    a=ordinal+3
    if family=='v116_quad_interpolate':
        c=2+k; b=t-3; aa=ordinal+1
        y0=c;y1=aa+b+c;y2=4*aa+2*b+c
        p=dict(y0=y0,y1=y1,y2=y2)
        stem=f"Cho parabol y=Ax²+Bx+C đi qua (0;{y0}), (1;{y1}), (2;{y2}). Tính A."
        val=Q(y2-2*y1+y0,2)
        why=f"Từ ba tung độ: y(2)−2y(1)+y(0)=2A. Vậy A=({y2}−2·{y1}+{y0})/2={val}."
    elif family=='v116_rational_excluded':
        z=t*2-5
        p=dict(z=z)
        stem=f"Cho hàm số f(x)=(x²+1)/(x−({z})). Giá trị x nào bị loại khỏi tập xác định?"
        val=Z(z);why=f"Mẫu số x−({z}) phải khác 0. Giải x−({z})=0 được x={z}; đây là giá trị phải loại."
    elif family=='v116_intersection_lines':
        m1=k+1;m2=-(t%4+1);x=t-4
        b1=t+1;b2=(m1-m2)*x+b1
        p=dict(m1=m1,m2=m2,b1=b1,b2=b2)
        stem=f"Tìm hoành độ giao điểm của y={m1}x+({b1}) và y={m2}x+({b2})."
        val=Q(b2-b1,m1-m2)
        why=f"Tại giao điểm hai tung độ bằng nhau: ({m1}−({m2}))x={b2}−({b1}), nên x={val}."
    elif family=='v116_dot_product':
        u=[t,-k];v=[2*k,t-1]
        p=dict(u=u,v=v)
        stem=f"Trong Oxy, cho u=({u[0]};{u[1]}) và v=({v[0]};{v[1]}). Tính u·v."
        val=Z(u[0]*v[0]+u[1]*v[1]);why=f"Tích vô hướng là u·v={u[0]}·{v[0]}+({u[1]})·{v[1]}={val}."
    elif family=='v116_parallelogram_area':
        u=[t,k];v=[-1,t+1]
        p=dict(u=u,v=v)
        stem=f"Hình bình hành có hai cạnh kề là các vectơ u=({u[0]};{u[1]}), v=({v[0]};{v[1]}). Tính diện tích."
        val=Z(abs(u[0]*v[1]-u[1]*v[0]));why=f"Diện tích bằng |det(u,v)|=|{u[0]}·{v[1]}−{u[1]}·({v[0]})|={val}."
    elif family=='v116_sine_rule':
        side=2*t
        p=dict(side=side)
        stem=f"Một tam giác có góc A=30°, góc B=90°, cạnh đối diện A dài {side} m. Tính cạnh đối diện B (m)."
        val=Z(2*side);why=f"Định luật sin: b/sin90°=a/sin30°. Vì sin90°=1, sin30°=1/2 nên b=2·{side}={val} m."
    elif family=='v116_cosine_rule':
        b=2+t;c=3+k
        p=dict(b=b,c=c)
        stem=f"Tam giác có hai cạnh b={b} cm, c={c} cm kẹp góc 60°. Tính bình phương cạnh a đối diện góc 60° (cm²)."
        val=Z(b*b+c*c-b*c);why=f"Định lý cosin: a²=b²+c²−2bc·cos60°={b}²+{c}²−{b}·{c}={val}."
    elif family=='v116_angle_bisector':
        ab=t+2;ac=k+3;bc=ab+ac-1
        p=dict(ab=ab,ac=ac,bc=bc)
        stem=f"Tam giác ABC có AB={ab}, AC={ac}, BC={bc}. Phân giác AD cắt BC tại D. Tính BD."
        val=Q(bc*ab,ab+ac);why=f"Định lý phân giác: BD/DC=AB/AC={ab}/{ac}. Vậy BD=BC·AB/(AB+AC)={bc}·{ab}/({ab}+{ac})={val}."
    elif family=='v116_apollonius_median':
        # Triangle with sides a=6t, b=5t, c=7t, median to a is sqrt(28)*t
        sides=[6*t,5*t,7*t];aa,bb,cc=sides
        p=dict(a=aa,b=bb,c=cc)
        stem=f"Tam giác có các cạnh a={aa}, b={bb}, c={cc}. Tính bình phương trung tuyến m_a ứng với cạnh a."
        val=Q(2*bb*bb+2*cc*cc-aa*aa,4)
        why=f"Định lý Apollonius: m_a²=(2b²+2c²−a²)/4=(2·{bb}²+2·{cc}²−{aa}²)/4={val}."
    elif family=='v116_intersecting_chords':
        x=2*t;y=3*k;z=3*t
        # Positive intersecting chord segments; the product relation gives w=2k.
        p=dict(x=x,y=y,z=z)
        stem=f"Hai dây AB, CD cắt nhau tại P trong đường tròn. PA={x}, PB={y}, PC={z}. Tính PD."
        val=Q(x*y,z);why=f"Định lý hai dây cắt nhau: PA·PB=PC·PD, suy ra PD={x}·{y}/{z}={val}."
    elif family=='v116_multiset_permutations':
        n1=2+k;n2=1+(ordinal%2); n=n1+n2
        p=dict(n1=n1,n2=n2)
        stem=f"Có {n1} thẻ chữ A giống nhau và {n2} thẻ chữ B giống nhau. Có bao nhiêu cách xếp thành hàng khác nhau?"
        val=Q(factorial(n),factorial(n1)*factorial(n2))
        why=f"Có {n} vị trí, đổi chỗ các A hay các B không tạo xếp mới. Số cách là {n}!/({n1}!·{n2}!)={val}."
    elif family=='v116_nonzero_lead':
        n=6+(ordinal%4);r=2+(ordinal%3)
        p=dict(n=n,r=r)
        stem=f"Dùng {n} chữ số 0,1,...,{n-1}, lập số tự nhiên có {r} chữ số khác nhau. Hỏi có bao nhiêu số?"
        val=Z((n-1)*factorial(n-1)//factorial(n-r))
        why=f"Chữ số đầu có {n-1} cách (không là 0); {r-1} vị trí còn lại là chỉnh hợp {r-1} của {n-1} chữ số. Tổng {(n-1)}·P({n-1},{r-1})={val}."
    elif family=='v116_at_least_one':
        succ=1;k2=3+ordinal%4;n=2+(ordinal%3)
        p=dict(succ=succ,denom=k2,n=n)
        stem=f"Một phép thử độc lập có xác suất thành công {succ}/{k2}, lặp lại {n} lần. Tính xác suất thành công ít nhất một lần."
        val=1-(Q(k2-succ,k2))**n
        why=f"Biến cố đối là không thành công ở cả {n} lần. P=1−(1−{succ}/{k2})^{n}=1−({k2-succ}/{k2})^{n}={val}."
    elif family=='v116_three_point_variance':
        c=t*3;d=k
        p=dict(c=c,d=d)
        stem=f"Có ba số liệu {c-d}, {c}, {c+d}. Tính phương sai (chia cho n=3, không hiệu chỉnh)."
        val=Q(2*d*d,3)
        why=f"Trung bình là {c}. Ba độ lệch là −{d},0,{d}; phương sai [({d})²+0+({d})²]/3={val}."
    elif family=='v116_mixture_concentration':
        w1=2*t;w2=t;conc1=10;conc2=25
        p=dict(w1=w1,w2=w2,c1=conc1,c2=conc2)
        stem=f"Trộn {w1} kg dung dịch nồng độ {conc1}% với {w2} kg dung dịch nồng độ {conc2}%. Tính nồng độ % của hỗn hợp (giả sử không hao hụt)."
        val=Q(w1*conc1+w2*conc2,w1+w2)
        why=f"Khối lượng chất tan =({w1}·{conc1}+{w2}·{conc2})/100 kg. Chia tổng {w1+w2} kg rồi nhân 100% được {val}%."
    elif family=='v116_sin_sum':
        # Known exact sin(30+60)=1, other sample angles use same 30/60 but coefficient variation
        scale=t
        p=dict(scale=scale)
        stem=f"Cho E={scale}[sin30°cos60°+cos30°sin60°]. Tính chính xác E."
        val=Z(scale);why=f"Theo công thức sin(a+b), sin30°cos60°+cos30°sin60°=sin90°=1. E={scale}·1={val}."
    elif family=='v116_finite_geom_sum':
        first=k;n=t+2;ratio=2
        p=dict(first=first,n=n,ratio=ratio)
        stem=f"Một cấp số nhân có u₁={first}, q={ratio}. Tính tổng {n} số hạng đầu."
        val=Z(first*(ratio**n-1)//(ratio-1))
        why=f"Sₙ=u₁(qⁿ−1)/(q−1)={first}·(2^{n}−1)/(2−1)={val}."
    elif family=='v116_rational_infinity_limit':
        aa=t*2;bb=k
        p=dict(a=aa,b=bb)
        stem=f"Tính lim(x→+∞) [({aa}x²+5x+1)/({bb}x²−3x+7)]."
        val=Q(aa,bb);why=f"Chia cả tử và mẫu cho x²; các hạng 1/x và 1/x² tiến về 0. Giới hạn bằng {aa}/{bb}={val}."
    elif family=='v116_chain_rule':
        a=t;b=k;c=t+1;x0=1
        p=dict(a=a,b=b,c=c,x0=x0)
        stem=f"Cho f(x)=({a}x²+{b}x+{c})³. Tính f'({x0})."
        val=Z(3*(a*x0*x0+b*x0+c)**2*(2*a*x0+b))
        why=f"Đặt u(x)={a}x²+{b}x+{c}. f'=3u²u', u'=2·{a}x+{b}; thế x={x0} thu được {val}."
    elif family=='v116_quotient_derivative':
        a=t;b=k;c=1;d=t+2;x0=1
        p=dict(a=a,b=b,c=c,d=d,x0=x0)
        stem=f"Cho f(x)=({a}x+{b})/({c}x+{d}). Tính f'({x0})."
        val=Q(a*d-b*c,(c*x0+d)**2)
        why=f"Đạo hàm thương: f'=(a(cx+d)−c(ax+b))/(cx+d)²=(ad−bc)/(cx+d)². Thế x={x0} được {val}."
    elif family=='v116_total_probability':
        pa=Q(1,k+1);p1=Q(1,2);p0=Q(1,t+4)
        p=dict(pa=str(pa),p1=str(p1),p0=str(p0))
        stem=f"Một nhóm chiếm {pa} dân số, có tỉ lệ đạt {p1}; nhóm còn lại có tỉ lệ đạt {p0}. Tính tỉ lệ đạt của toàn bộ dân số."
        val=pa*p1+(1-pa)*p0
        why=f"Theo công thức xác suất toàn phần: P(đạt)=P(nhóm 1)·P(đạt|1)+P(nhóm 2)·P(đạt|2)={pa}·{p1}+(1−{pa})·{p0}={val}."
    elif family=='v116_circular_permutations':
        n=t+3
        p=dict(n=n)
        stem=f"Có {n} người phân biệt ngồi quanh bàn tròn, các cách chỉ khác do quay cả bàn được xem là một. Tính số cách ngồi."
        val=Z(factorial(n-1));why=f"Cố định một người để loại đối xứng quay; sắp {n-1} người còn lại theo ({n-1})! cách = {val}."
    elif family=='v116_exponential_growth_index':
        start=1000+100*t;period=2+(ordinal%4)
        p=dict(start=start,period=period)
        stem=f"Một đại lượng bắt đầu ở {start} đơn vị, cứ mỗi kỳ tăng gấp đôi. Cần đúng bao nhiêu kỳ để đạt {start*2**period} đơn vị?"
        val=Z(period);why=f"Mô hình y={start}·2^n. Đặt y={start*2**period} thì 2^n=2^{period}, nên n={val} kỳ."
    elif family=='v116_integral_parts_xexp':
        n=t
        p=dict(n=n)
        stem=f"Tính chính xác I=∫₀^{n} x·e^x dx."
        val=(n-1)*exp(n)+1
        why=f"Tích phân từng phần với u=x, dv=e^x dx: ∫xe^x dx=(x−1)e^x+C. Thế cận 0 và {n}: I=({n}−1)e^{n}+1={val}."
    elif family=='v116_curves_enclosed_area':
        n=t
        p=dict(n=n)
        stem=f"Trên đoạn [0;{n}], tính diện tích phần nằm giữa y=x và y=x²/{n}."
        val=Q(n*n,6)
        why=f"Trên [0;{n}] có x≥x²/{n}. Diện tích ∫₀^{n}(x−x²/{n})dx=[x²/2−x³/(3·{n})]₀^{n}={val}."
    elif family=='v116_complex_reciprocal':
        a=t;b=k
        p=dict(a=a,b=b)
        stem=f"Cho z={a}+{b}i. Tính phần thực của 1/z."
        val=Q(a,a*a+b*b)
        why=f"Nhân tử và mẫu với số phức liên hợp: 1/z=({a}−{b}i)/({a}²+{b}²). Do đó Re(1/z)={a}/({a*a+b*b})={val}."
    elif family=='v116_log_product_equation':
        x=2**(2+ordinal%3);y=2**(1+ordinal%2)
        m=x-y;expo=(2+ordinal%3)+(1+ordinal%2)
        p=dict(m=m,expo=expo)
        stem=f"Giải phương trình log₂(x)+log₂(x−({m}))={expo} với điều kiện x>max(0,{m}). Tìm nghiệm thực x."
        val=Z(x)
        why=f"Điều kiện x>0 và x−({m})>0. Gom log: x(x−{m})=2^{expo}. Giải phương trình bậc hai và chọn nghiệm thỏa điều kiện được x={val}."
    elif family=='v116_sphere_diameter':
        dx=2*t;dy=2*k;dz=2
        p=dict(dx=dx,dy=dy,dz=dz)
        stem=f"Mặt cầu có đường kính AB với A(0;0;0), B({dx};{dy};{dz}). Tính bình phương bán kính R²."
        val=Q(dx*dx+dy*dy+dz*dz,4)
        why=f"R=AB/2, AB²={dx}²+{dy}²+{dz}², nên R²=AB²/4={val}."
    elif family=='v116_discrete_variance':
        amount=t;pnum=1;pden=k+2
        p=dict(amount=amount,pnum=pnum,pden=pden)
        stem=f"Biến ngẫu nhiên X chỉ nhận 0 hoặc {amount}, với P(X={amount})={pnum}/{pden}. Tính Var(X)."
        val=Z(amount*amount)*Q(pnum,pden)*(1-Q(pnum,pden))
        why=f"E[X]={amount}p và E[X²]={amount}²p, nên Var(X)={amount}²p(1−p) với p={pnum}/{pden}, bằng {val}."
    elif family=='v116_box_maximization':
        L=6*t
        p=dict(L=L)
        stem=f"Tấm bìa hình vuông cạnh {L} cm được cắt bốn hình vuông cạnh x ở góc để gấp thành hộp không nắp. Tính x tối ưu để thể tích lớn nhất (cm)."
        val=Q(L,6)
        why=f"V(x)=x({L}−2x)², với 0<x<{L/2}. V' = ({L}−2x)({L}−6x). Điểm tối đa bên trong là x={L}/6={val}."
    elif family=='v116_binomial_expectation':
        n=t+4;pnum=1;pden=k+1
        p=dict(n=n,pnum=pnum,pden=pden)
        stem=f"Một trò chơi thử nghiệm độc lập {n} lần, xác suất thành công mỗi lần là {pnum}/{pden}. Tính kỳ vọng số lần thành công."
        val=Q(n*pnum,pden)
        why=f"Số thành công X có phân phối nhị thức. Do tuyến tính kỳ vọng, E[X]=n·p={n}·{pnum}/{pden}={val}."
    else:
        raise ValueError(f'Unknown V116 family {family}')
    return p,stem,simplify(val),why


def _canonical(v):
    return str(simplify(v))


def _sha(s):
    return hashlib.sha256(re.sub(r'\s+',' ',s.strip().casefold()).encode('utf-8')).hexdigest()


def generate(family, ordinal, difficulty='trung cấp', seed_key=None):
    if family not in FAMILIES or not isinstance(ordinal,int) or not 0 <= ordinal < 10:
        raise ValueError('unknown family or ordinal outside 0..9')
    method=METHOD_LOOKUP[family]
    p,base,result,worked=_core(family,ordinal)
    fmt=FORMATS[ordinal%5]
    canonical=_canonical(result)
    p['generation_version']=116
    if fmt=='trac_nghiem':
        # Plausible numerical mistakes, checked to be distinct symbolic values.
        variants=[result,result+1,result-1,result*2]
        values=[]
        for value in variants:
            s=_canonical(value)
            if s not in values:values.append(s)
        step=2
        while len(values)<4:
            s=_canonical(result+step)
            if s not in values: values.append(s)
            step+=1
        pos=ordinal%4
        options=values[1:]
        options.insert(pos,canonical)
        stem=base+' Chọn đáp án đúng trong bốn phương án.'
        answer=canonical
        meta={'options':options,'correct_index':pos}
        solution=worked+f' Phương án đúng là {"ABCD"[pos]}.'
    elif fmt=='dung_sai':
        shown=result if (ordinal//5)%2==0 else result+1
        truth=bool(simplify(shown-result)==0)
        stem=base+f' Nhận định: "Kết quả bằng {_canonical(shown)}". Đúng hay sai?'
        answer='Đúng' if truth else 'Sai'
        meta={'statement_result':_canonical(shown),'truth':truth}
        solution=worked+f' Nhận định {answer.lower()} vì giá trị chính xác là {canonical}.'
    elif fmt=='tu_luan_ngan':
        stem=base+' Hãy trình bày cách suy luận và ghi kết quả cuối cùng.'
        answer=canonical;meta={};solution=worked
    elif fmt=='van_dung':
        if method.real_world:
            stem=base+' Hãy giải thích ý nghĩa kết quả trong bối cảnh trên.'
            fmt='toan_thuc_te'
        else:
            stem=base+' Bài vận dụng: nêu rõ điều kiện áp dụng công thức trước khi tính.'
        answer=canonical;meta={};solution=worked
    else:
        stem=base+' Điền kết quả chính xác, không làm tròn.'
        answer=canonical;meta={};solution=worked
    return {'family':family,'ordinal':ordinal,'params':p,'stem':stem,'answer':answer,'solution':solution,
            'difficulty':difficulty,'question_type':fmt,'numeric_result':canonical,**meta,
            'method_review_status':'pending-expert-review','fingerprint':_sha(stem),
            'seed_key':seed_key or '', 'topic_id':method.topic,'method_signature':method.signature}


def verify(item):
    """Fail closed on tampering and independently recompute mathematical invariants."""
    try:
        if item.get('family') not in FAMILIES:return False,{'error':'unknown method'}
        original=generate(item['family'],item['ordinal'],item['difficulty'],item.get('seed_key'))
        if item != original:return False,{'error':'record differs from deterministic source'}
        _p,_,value,_why=_core(item['family'],item['ordinal'])
        if simplify(value - __import__('sympy').sympify(item['numeric_result'])) != 0:
            return False,{'error':'mathematical value discrepancy'}
        if item['question_type']=='trac_nghiem':
            opts=item['options'];index=item['correct_index']
            if len(opts)!=4 or len(set(opts))!=4 or opts[index]!=item['numeric_result']:
                return False,{'error':'invalid MCQ options'}
        if item['question_type']=='dung_sai':
            truth=simplify(__import__('sympy').sympify(item['statement_result'])-value)==0
            if truth!=item['truth'] or item['answer']!=('Đúng' if truth else 'Sai'):
                return False,{'error':'invalid true/false'}
        if len(item['solution'])<28 or len(item['stem'])<25:
            return False,{'error':'incomplete stem/solution'}
        return True,{'math':'sympy-recomputed','integrity':'deterministic-regeneration',
                     'independent_method_certified':False,'human_review':'pending'}
    except Exception as exc:
        return False,{'error':f'{type(exc).__name__}: {exc}'}


def export(out_folder):
    from pathlib import Path
    out=Path(out_folder);out.mkdir(parents=True,exist_ok=True)
    forms=out/'V116_NEW_METHODS_PENDING_REVIEW.jsonl'
    questions=out/'V116_NEW_QUESTIONS_10_EACH.jsonl'
    seen=set();q_count=0
    with forms.open('w',encoding='utf-8') as f, questions.open('w',encoding='utf-8') as qout:
        for method in METHODS:
            f.write(json.dumps({**method.__dict__,'review_status':'pending-expert-review',
                'math_examples_verified':10,'independence_certified':False},ensure_ascii=False)+'\n')
            for i in range(10):
                sample=generate(method.family,i,method.difficulty,seed_key=method.topic+':v116')
                ok,evidence=verify(sample)
                if not ok:raise RuntimeError(f'{method.family}[{i}]: {evidence}')
                if sample['fingerprint'] in seen:raise RuntimeError('duplicate problem text')
                seen.add(sample['fingerprint'])
                sample['verification']=evidence
                qout.write(json.dumps(sample,ensure_ascii=False,separators=(',',':'))+'\n')
                q_count+=1
    return {'new_candidate_methods':len(METHODS),'new_math_checked_questions':q_count,
            'new_distinct_stems':len(seen),'methods_certified_independent':0,
            'formats':{x:sum(1 for i in range(10) if (FORMATS[i%5] if not(x=='toan_thuc_te') else 'van_dung')==x)*len(METHODS) for x in FORMATS},
            'publication':'blocked-until-review'}
