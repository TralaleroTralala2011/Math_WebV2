"""V117 research-grade *candidate* problem archetypes, NOT certified global independence.

Each entry has a learning target and a distinct primary procedure within this batch.
Both cross-corpus semantic uniqueness and teacher review are required before promotion.
Examples are deterministic, generated as 10 genuinely different input instances per
candidate and rechecked using exact SymPy arithmetic and independent invariants.
Source alignment is indicative, not a claim of permission to copy textbook exercises.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
from hashlib import sha256
from math import comb, factorial
import json, re
from sympy import Integer as I, Rational as Q, sqrt, pi, sin, cos, log, simplify, binomial, diff, integrate, Symbol, solve, expand, factor

x = Symbol('x', real=True)

@dataclass(frozen=True)
class Method:
    family: str
    topic: str
    title: str
    signature: str
    skill: str
    grade: int
    difficulty: str
    real_world: bool = False

METHODS=[]
HANDLERS={}

def method(family, topic, title, signature, skill, grade, difficulty='trung cấp', real_world=False):
    def deco(fn):
        if family in HANDLERS: raise RuntimeError(f'family repeated: {family}')
        METHODS.append(Method(family,topic,title,signature,skill,grade,difficulty,real_world))
        HANDLERS[family]=fn
        return fn
    return deco

# --- Grade 10: different structures of reasoning (not merely rewording) ---
@method('v117_de_morgan_3','tap_hop','Đếm phần bù của hợp hai tập','complement-cardinality-of-union','Nguyên lý cộng trừ rồi lấy phần bù',10)
def de_morgan(t):
    total=50+3*t; a=15+t; b=18+t; common=3+t%4
    val=total-a-b+common
    return dict(N=total,A=a,B=b,C=common), f'Lớp có {total} học sinh, {a} bạn học tiếng Anh, {b} bạn học tiếng Pháp, {common} bạn học cả hai. Hỏi bao nhiêu bạn không học môn nào trong hai môn?', I(val), f'Có {a}+{b}−{common} bạn học ít nhất một môn; phần còn lại bằng {total}−({a}+{b}−{common})={val}.'

@method('v117_exactly_two','menh_de_tap_hop','Số phần tử thuộc chính xác hai trong ba tập','three-set-exactly-two-inc-exc','Bóc phần giao ba lần khỏi ba giao đôi',10)
def exactly_two(t):
    ab=8+t; ac=9+t; bc=10+t; abc=2+t%4
    val=ab+ac+bc-3*abc
    return dict(ab=ab,ac=ac,bc=bc,abc=abc), f'Ba nhóm A,B,C có |A∩B|={ab}, |A∩C|={ac}, |B∩C|={bc}, |A∩B∩C|={abc}. Có bao nhiêu người thuộc đúng hai nhóm?',I(val),f'Mỗi người ở cả ba bị đếm ba lần, phải loại 3·{abc}. Đúng hai nhóm = {ab}+{ac}+{bc}−3·{abc}={val}.'

@method('v117_abs_inequality_length','bat_phuong_trinh','Đếm nghiệm nguyên bất phương trình giá trị tuyệt đối','absolute-value-bound-integer-lattice','Đổi |x−c|≤r thành đoạn rồi đếm',10)
def abs_interval(t):
    c=t-6;r=3+t%4;val=2*r+1
    return dict(c=c,r=r),f'Có bao nhiêu số nguyên x thỏa |x−({c})|≤{r}?',I(val),f'Điều kiện tương đương {c-r}≤x≤{c+r}. Có {c+r}−({c-r})+1={val} nghiệm nguyên.'

@method('v117_quadratic_root_count','phuong_trinh','Phân loại số nghiệm thực của phương trình bậc hai','quadratic-discriminant-root-multiplicity','Xét dấu biệt thức và nghiệm kép',10)
def quad_count(t):
    a=t+1;b=2*(t-2);c=[(t-2)**2-a, (t-2)**2, (t-2)**2+a][t%3]  # discriminant variant
    # want D 4*((t-2)^2-a*c) actual computed for all variants
    D=b*b-4*a*c; val=2 if D>0 else (1 if D==0 else 0)
    return dict(a=a,b=b,c=c),f'Phương trình {a}x²+({b})x+({c})=0 có bao nhiêu nghiệm thực phân biệt?',I(val),f'Tính Δ=b²−4ac={b}²−4·{a}·({c})={D}. Do đó số nghiệm thực phân biệt là {val}.'

@method('v117_parabola_line_tangency','ham_so_bac_hai','Xác định tham số để đường thẳng tiếp xúc parabol','discriminant-zero-line-parabola-tangency','Biệt thức của phương trình hoành độ giao điểm bằng 0',10)
def parabola_tan(t):
    a=1+t%4; b=2+t; c=3+t; m=b+2*a*(t-5); k=c-a*(t-5)**2
    # y=ax^2+bx+c, line y=mx+k -> discriminant-zero if k=c-(b-m)^2/(4a)
    return dict(a=a,b=b,c=c,m=m), f'Cho y={a}x²+{b}x+{c} và đường thẳng y={m}x+k. Tìm k để đường thẳng tiếp xúc parabol.', Q(k),f'Phương trình giao điểm {a}x²+({b}-{m})x+({c}-k)=0 tiếp xúc khi Δ=0. Vậy k={c}−({b}−{m})²/(4·{a})={k}.'

@method('v117_linear_optimal_corner','he_bat_phuong_trinh','Tối ưu tuyến tính trên hình chữ nhật','linear-programming-vertex-sign-selection','Xét dấu hệ số trên miền đa giác',10,real_world=True)
def lp_corner(t):
    W=4+t;H=3+t%4;p=(t%5)-2;q=3+t%3
    val=(p*W if p>0 else 0)+q*H
    return dict(W=W,H=H,p=p,q=q),f'Với 0≤x≤{W}, 0≤y≤{H}, giá trị lớn nhất của F={p}x+{q}y là bao nhiêu?',I(val),f'Hàm tuyến tính đạt cực trị tại đỉnh; hệ số của y dương nên chọn y={H}. Với x chọn {W if p>0 else 0 if p<0 else "bất kỳ"}. Fmax={val}.'

@method('v117_triangle_inradius','he_thuc_luong','Bán kính đường tròn nội tiếp từ diện tích','incircle-radius-area-semiperimeter','S=r·p với p là nửa chu vi',10)
def inradius(t):
    scale=t; a=3*scale;b=4*scale;c=5*scale;S=6*scale*scale;semi=6*scale
    return dict(a=a,b=b,c=c),f'Tam giác vuông có ba cạnh {a}, {b}, {c} cm. Tính bán kính đường tròn nội tiếp (cm).',I(scale),f'Diện tích S=({a}·{b})/2={S}, nửa chu vi p=({a}+{b}+{c})/2={semi}. Vì S=pr nên r={S}/{semi}={scale}.'

@method('v117_triangle_circumradius','he_thuc_luong_van_dung_10','Bán kính ngoại tiếp từ diện tích và cạnh','circumradius-abc-over-four-area','Áp dụng R=abc/(4S)',10)
def circumradius(t):
    sc=t;a=3*sc;b=4*sc;c=5*sc;S=6*sc*sc;val=Q(a*b*c,4*S)
    return dict(a=a,b=b,c=c),f'Tam giác có ba cạnh {a}, {b}, {c} cm và diện tích {S} cm². Tìm bán kính ngoại tiếp (cm).',val,f'Bán kính đường tròn ngoại tiếp R=abc/(4S)={a}·{b}·{c}/(4·{S})={val} cm.'

@method('v117_centroid_coordinates','toa_do_phang','Tọa độ trọng tâm tam giác','centroid-average-of-three-vertices','Lấy trung bình cộng tọa độ của ba đỉnh',10)
def centroid(t):
    A=(t,-t);B=(2*t+1,t+3);C=(-t+2,2*t-3)
    val=Q(A[0]+B[0]+C[0],3)
    return dict(A=A,B=B,C=C),f'Tam giác A{A}, B{B}, C{C} có trọng tâm G. Tính hoành độ G.',val,f'Trọng tâm có tọa độ bằng trung bình ba đỉnh: xG=({A[0]}+{B[0]}+{C[0]})/3={val}.'

@method('v117_triangle_area_sine','he_thuc_luong_tam_giac','Diện tích tam giác theo hai cạnh và góc xen giữa','triangle-area-two-sides-sine-angle','S=ab sin(C)/2',10)
def area_sine(t):
    a=2*t;b=t+3;ang=[30,60,90][t%3];v=simplify(Q(a*b,2)*sin(pi*ang/180))
    return dict(a=a,b=b,ang=ang),f'Hai cạnh của một tam giác dài {a} cm, {b} cm, góc xen giữa {ang}°. Tính diện tích chính xác.',v,f'Dùng S=(ab sin C)/2=({a}·{b}·sin{ang}°)/2={v} cm².'

@method('v117_hypergeometric_selection','xac_suat','Xác suất rút đúng k vật cùng loại không hoàn lại','hypergeometric-exact-count','Tổ hợp thuận lợi chia tổng tổ hợp',10,real_world=True)
def hypgeom(t):
    red=5+t; blue=7+t;draw=3;want=2
    val=Q(comb(red,want)*comb(blue,draw-want),comb(red+blue,draw))
    return dict(red=red,blue=blue,draw=draw,want=want),f'Hộp có {red} bi đỏ, {blue} bi xanh. Lấy ngẫu nhiên đồng thời {draw} viên. Xác suất đúng {want} đỏ bằng bao nhiêu?',val,f'Có C({red},2)·C({blue},1) trường hợp thuận lợi trong C({red+blue},3) cách lấy. Xác suất={val}.'

@method('v117_bayes_inverse','bai_toan_thuc_te_10','Tìm xác suất nguồn gốc khi đã quan sát kết quả','bayes-inversion-two-populations','Định lý Bayes sau xác suất toàn phần',10,real_world=True)
def bayes(t):
    pa=Q(1,t+2);a=Q(3,4);b=Q(1,5)
    val=simplify(pa*a/(pa*a+(1-pa)*b))
    return dict(pA=str(pa),p1=str(a),p0=str(b)),f'Loại A chiếm {pa} số sản phẩm. Tỉ lệ đạt chuẩn của A là {a}, của loại khác là {b}. Biết sản phẩm lấy được đạt chuẩn, xác suất nó thuộc A bằng bao nhiêu?',val,f'Bayes: P(A|đạt)=P(A)P(đạt|A)/[P(A)P(đạt|A)+P(khác)P(đạt|khác)]={val}.'

@method('v117_nonadjacent_selection','g10_combinatorics_olympiad','Chọn vị trí không kề nhau trong một hàng','nonadjacent-subset-gap-bijection','Dồn khe, C(n−k+1,k)',10)
def no_adj(t):
    n=12+t;k=2+(t%3);val=binomial(n-k+1,k)
    return dict(n=n,k=k),f'Từ {n} ghế thành hàng có bao nhiêu cách chọn {k} ghế sao cho không có hai ghế được chọn kề nhau?',val,f'Gọi i1<...<ik là vị trí chọn, đặt j_r=i_r−(r−1). Khi đó chọn k vị trí trong 1..{n-k+1}, được C({n-k+1},{k})={val}.'

@method('v117_stars_bars_positive','quy_tac_dem','Số nghiệm nguyên dương của tổng cố định','stars-and-bars-positive-integers','Phân tích N thành k phần dương C(N−1,k−1)',10)
def stars(t):
    n=15+t;k=3+t%3;v=binomial(n-1,k-1)
    return dict(n=n,k=k),f'Có bao nhiêu bộ (x₁,...,x{k}) nguyên dương thỏa x₁+...+x{k}={n}?',v,f'Đặt y_i=x_i−1≥0, tổng y_i={n-k}; theo chia k−1 vạch ngăn, số cách C({n-1},{k-1})={v}.'

@method('v117_weighted_mean','thong_ke','Trung bình cộng có trọng số','weighted-mean-frequency-table','Tổng tích giá trị-tần số chia tổng tần số',10,real_world=True)
def weighted_mean(t):
    a=t+3;b=t+7;na=t+2;nb=3+t%4
    v=Q(a*na+b*nb,na+nb)
    return dict(a=a,b=b,na=na,nb=nb),f'Một lớp có {na} bài kiểm tra được {a} điểm, {nb} bài được {b} điểm. Tính điểm trung bình của toàn bộ bài.',v,f'Điểm trung bình =({na}·{a}+{nb}·{b})/({na}+{nb})={v}.'

@method('v117_variance_affine','thong_ke_11','Phương sai sau phép đổi đơn vị tuyến tính','variance-affine-transformation-square-scale','Var(aX+b)=a² Var(X)',11,real_world=True)
def affine_variance(t):
    a=t%5+2;b=t+1;v=3+t
    return dict(a=a,b=b,variance=v),f'Một mẫu dữ liệu X có phương sai {v}. Đổi số đo thành Y={a}X+{b}. Tính phương sai của Y.',I(a*a*v),f'Phép cộng {b} không đổi phương sai, nhân {a} làm phương sai nhân với {a}². Do đó Var(Y)={a}²·{v}={a*a*v}.'

# --- Grade 11: sequences, trigonometry, calculus and transformations ---
@method('v117_trig_double_sin','cong_thuc_luong_giac','Tính sin(2x) từ sin và cos','trig-double-angle-product','sin(2x)=2sin(x)cos(x)',11)
def sin2(t):
    a=t+1;b=t+2;h=sqrt(a*a+b*b);v=simplify(Q(2*a*b,1)/(a*a+b*b))
    return dict(a=a,b=b),f'Góc nhọn α có sin α={a}/{h}, cos α={b}/{h}. Tính sin(2α).',v,f'Công thức góc đôi sin(2α)=2sinαcosα=2·{a}/{h}·{b}/{h}={v}.'

@method('v117_trig_cos_sum','gia_tri_luong_giac','Tính cos tổng hai góc đặc biệt','cos-sum-trig-identity','cos(a+b)=cos a cos b−sin a sin b',11)
def cos_sum(t):
    pairs=[(0,30),(0,45),(30,45),(30,60),(45,60),(60,60),(90,30),(30,90),(45,90),(60,90)]
    a,b=pairs[t-2];v=simplify(cos(pi*(a+b)/180))
    return dict(a=a,b=b),f'Tính chính xác cos({a}°+{b}°).',v,f'Áp dụng cos(a+b)=cos a cos b−sin a sin b; thay {a}° và {b}° được {v}.'

@method('v117_trig_equation_count','phuong_trinh_luong_giac','Đếm nghiệm sin(x)=0 trên một đoạn đóng','count-trigonometric-zeroes-on-interval','x=kπ và đếm k nguyên',11)
def trig_count(t):
    a=2+t%4;b=a+t+3;v=b-a+1
    return dict(a=a,b=b),f'Có bao nhiêu nghiệm thực x∈[{a}π;{b}π] thỏa sin x=0?',I(v),f'Vì sin x=0 ⇔ x=kπ, k nguyên; các k={a},...,{b} có {v} giá trị.'

@method('v117_recursion_fixed_point','day_so_truy_hoi_11','Điểm bất động của truy hồi affine','affine-recurrence-fixed-point','Giải u=au+b',11)
def recur_fixed(t):
    a=Q(1,2+t%4);b=t+1;v=simplify(Q(b)/(1-a))
    return dict(a=str(a),b=b),f'Dãy xác định uₙ₊₁={a}uₙ+{b}. Nếu dãy hội tụ đến L, hãy tính L.',v,f'Giả sử hội tụ và |{a}|<1, chuyển giới hạn cho L={a}L+{b}, nên L={b}/(1−{a})={v}.'

@method('v117_telescoping_sum','day_so','Tổng rút gọn 1/[k(k+1)]','telescoping-partial-fractions','1/[k(k+1)]=1/k−1/(k+1)',11)
def telescoping(t):
    n=3+t;v=Q(n,n+1)
    return dict(n=n),f'Tính chính xác S=∑(k=1..{n}) 1/[k(k+1)].',v,f'1/[k(k+1)]=1/k−1/(k+1), các số hạng triệt tiêu liên tiếp: S=1−1/({n}+1)={v}.'

@method('v117_geometric_infinite_sum','cap_so_nhan','Tổng cấp số nhân vô hạn hội tụ','infinite-geometric-series-convergence','S=a/(1−q) với |q|<1',11)
def geom_inf(t):
    first=t+1;q=Q(1,2+t%3);v=simplify(Q(first)/(1-q))
    return dict(a=first,q=str(q)),f'Tổng vô hạn S={first}+{first}·({q})+{first}·({q})²+... bằng bao nhiêu?',v,f'Vì |q|={q}<1, công thức S=a/(1−q)={first}/(1−{q})={v}.'

@method('v117_removable_limit','gioi_han_ham_so','Giới hạn tại điểm khuyết sau khi phân tích nhân tử','removable-limit-factor-cancel','Phân tích hiệu hai bình phương rồi khử nhân tử',11)
def removable(t):
    a=t+2;b=t+4;v=a+b
    return dict(a=a,b=b),f'Tính lim(x→{a}) (x²−{a*a})/(x−{a}).',I(2*a),f'Với x≠{a}, (x²−{a*a})/(x−{a})=x+{a}. Lấy x→{a} được {2*a}.'

@method('v117_piecewise_continuity','ham_so_lien_tuc','Chọn tham số để hàm từng phần liên tục','piecewise-continuity-matching-limits','So khớp giới hạn tại điểm ghép',11)
def piecewise(t):
    a=t+1;b=t+2;c=t-3;v=a*c+b
    return dict(a=a,b=b,c=c),f'Cho f(x)={a}x+{b} khi x<{c}, và f(x)=k khi x≥{c}. Tìm k để f liên tục tại x={c}.',I(v),f'Liên tục yêu cầu k=lim(x→{c}−)f(x)={a}·({c})+{b}={v}.'

@method('v117_product_derivative','dao_ham_quy_tac','Đạo hàm tích đa thức với hàm số mũ','product-rule-polynomial-exp','(uv)′=u′v+uv′',11)
def product_der(t):
    a=t+1;b=t-2;n=2+t%3
    v=simplify(diff((a*x+b)*x**n,x).subs(x,1))
    return dict(a=a,b=b,n=n),f'Cho f(x)=({a}x+({b}))x^{n}. Tính f′(1).',v,f'Đặt u={a}x+({b}), v=x^{n}. Đạo hàm f′={a}x^{n}+({a}x+{b})·{n}x^{n-1}. Thay x=1 được {v}.'

@method('v117_trig_derivative','dao_ham','Đạo hàm sin của hàm tuyến tính','chain-rule-sine-linear','Đạo hàm sin(u) bằng cos(u)u′',11)
def deriv_sin(t):
    a=t+1;v=I(a)
    return dict(a=a),f'Cho f(x)=sin({a}x). Tính f′(0).',v,f'Quy tắc hàm hợp: f′(x)={a}cos({a}x); tại x=0 thì cos0=1 nên f′(0)={v}.'

@method('v117_tangent_slope_normal','ung_dung_dao_ham_11','Hệ số góc pháp tuyến của đồ thị','normal-line-negative-reciprocal','Pháp tuyến có hệ số góc −1/f′(x₀)',11)
def normal_slope(t):
    a=t+1;b=t+2;x0=1;m=2*a*x0+b;v=Q(-1,m)
    return dict(a=a,b=b,x0=x0),f'Cho y={a}x²+{b}x. Tìm hệ số góc pháp tuyến tại điểm có x={x0}.',v,f'Tiếp tuyến có hệ số góc y′={2*a}x+{b}, tại x={x0} bằng {m}≠0. Pháp tuyến có hệ số góc −1/{m}={v}.'

@method('v117_translation_image','g11_geom_transform_translation','Ảnh của điểm qua phép tịnh tiến','translation-point-add-vector','Cộng tọa độ điểm và vectơ tịnh tiến',11)
def trans(t):
    a=t;b=-t+2;u=t+3;v=2-t
    return dict(A=[a,b],v=[u,v]),f'Tịnh tiến điểm A({a};{b}) theo vectơ ({u};{v}). Tìm hoành độ ảnh A′.',I(a+u),f'Ảnh A′=(a+u;b+v); x′={a}+{u}={a+u}.'

@method('v117_rotation_90','g11_geom_rotation_homothety','Ảnh qua phép quay 90° quanh gốc','rotation-quarter-turn-coordinate-map','(x,y)↦(−y,x)',11)
def rot90(t):
    a=t+2;b=t-4
    return dict(a=a,b=b),f'Phép quay tâm O(0;0), góc +90° biến P({a};{b}) thành P′. Hoành độ P′ bằng bao nhiêu?',I(-b),f'Quay ngược chiều kim đồng hồ +90°: (x;y)→(−y;x). Do đó x′=−({b})={-b}.'

@method('v117_reflect_diag','g11_geom_transform_reflection','Đối xứng qua đường y=x','reflection-in-diagonal-coordinate-exchange','(x,y)↦(y,x)',11)
def refl_diag(t):
    a=t+2;b=2*t-3
    return dict(a=a,b=b),f'Đối xứng điểm M({a};{b}) qua đường thẳng y=x được M′. Tìm hoành độ M′.',I(b),f'Đường y=x hoán đổi hai tọa độ: M′({b};{a}), nên hoành độ là {b}.'

@method('v117_homothety_nonorigin','g11_geom_transform_composition','Phép vị tự tâm khác gốc','homothety-center-affine-map','P′=C+k(P−C)',11)
def homot(t):
    cx=t;cy=-t;px=t+3;py=2*t;k=t%4+2
    return dict(C=[cx,cy],P=[px,py],k=k),f'Phép vị tự tâm C({cx};{cy}), tỉ số k={k} biến P({px};{py}) thành P′. Tìm hoành độ P′.',I(cx+k*(px-cx)),f'Theo P′=C+k(P−C), hoành độ x′={cx}+{k}·({px}−{cx})={cx+k*(px-cx)}.'

@method('v117_3d_prism_diagonal','nhan_biet_hinh_khong_gian_11','Đường chéo không gian của hộp chữ nhật','space-box-pythagoras-three-axes','Dùng định lý Pythagoras trong ba chiều',11)
def prism_diag(t):
    a=3*t;b=4*t;c=12*t;v=I(13*t)
    return dict(a=a,b=b,c=c),f'Khối hộp chữ nhật có ba cạnh kề {a}, {b}, {c}. Tính đường chéo khối hộp.',v,f'D²=a²+b²+c²={a*a}+{b*b}+{c*c}={v*v}, nên D=√({v*v})={v}.'

@method('v117_line_plane_angle','g11_geom_dihedral_angles','Góc đường thẳng với mặt phẳng từ độ cao','line-plane-angle-sine-projection','sin góc = khoảng cách độ cao / độ dài đoạn',11)
def angle_lp(t):
    h=3*t;l=6*t;v=I(30)
    return dict(h=h,l=l),f'Đoạn AB dài {l} cm có hình chiếu vuông góc lên mặt phẳng (P); A thuộc (P), độ cao của B là {h} cm. Góc giữa AB và (P) bằng bao nhiêu độ?',v,f'Gọi H là hình chiếu B lên (P). sin góc(AB,(P))=BH/AB={h}/{l}=1/2. Góc nhọn bằng 30°.'

# --- Grade 12: analysis, complex numbers and 3D analytic geometry ---
@method('v117_cubic_critical_point','cuc_tri','Hoành độ hai điểm tới hạn của hàm bậc ba','cubic-derivative-factorized-critical-points','Giải f′(x)=0 từ phân tích nhân tử',12)
def cubic_critical(t):
    a=t-4;b=t+2+t%4;v=I(b-a)
    return dict(a=a,b=b),f'Cho f′(x)=3(x−({a}))(x−({b})). Khoảng cách giữa hai điểm dừng trên trục hoành là bao nhiêu?',v,f'Giải f′(x)=0 được x={a} hoặc x={b}. Khoảng cách |{b}−({a})|={v}.'

@method('v117_quadratic_interval_min','gtln_gtnn','GTNN bậc hai trên đoạn khi đỉnh ở trong','quadratic-convex-vertex-interval-minimum','Hoàn thành bình phương và kiểm vị trí đỉnh',12)
def q_interval(t):
    a=1+t%4;c=t-5;d=t+3
    return dict(a=a,c=c,d=d),f'Tìm GTNN của f(x)={a}(x−({c}))²+({d}) trên đoạn [{c-2};{c+2}].',I(d),f'Vì {a}>0 và x={c} thuộc đoạn, (x−{c})²≥0; giá trị nhỏ nhất tại x={c}, bằng {d}.'

@method('v117_rational_oblique_asymptote','tien_can','Hệ số tự do tiệm cận xiên qua chia đa thức','oblique-asymptote-polynomial-division','Chia đa thức phân thức bậc 2/1',12)
def oblique(t):
    a=t+1;b=t-3;c=t+2;r=t+3
    # (ax+b)(x-c)+r numerator; asymptote y=ax+b
    A=a;B=b-a*c;C=r-b*c
    return dict(a=a,b=b,c=c,r=r),f'Cho f(x)=({A}x²+({B})x+({C}))/(x−({c})). Tìm hệ số tự do của tiệm cận xiên.',I(b),f'Tử bằng ({a}x+({b}))(x−{c})+{r}, nên f={a}x+({b})+{r}/(x−{c}). Tiệm cận xiên y={a}x+({b}); hệ số tự do là {b}.'

@method('v117_exponential_quadratic_substitution','pt_mu','Phương trình bậc hai theo 2^x','exponential-equation-exponential-substitution','Đặt t=2^x>0 rồi giải phương trình bậc hai',12)
def exp_quad(t):
    a=t+1;b=a+2+t%3;v=I(a)  # positive distinct roots
    return dict(a=a,b=b),f'Đặt u=2^x>0. Phương trình 4^x−({a+b})2^x+{a*b}=0 có hai nghiệm u>0. Nghiệm u nhỏ hơn bằng bao nhiêu?',v,f'Do 4^x=(2^x)², ta có u²−({a+b})u+{a*b}=(u−{a})(u−{b})=0. Hai nghiệm dương {a} và {b}, nhỏ hơn là {a}.'

@method('v117_log_change_base','ham_logarit','Đổi cơ số logarit và thu gọn','log-change-base-quotient','log_a(b)=ln b/ln a',12)
def log_change(t):
    a=2+t%4;n=2+t%3;b=a**n
    return dict(a=a,b=b),f'Tính log_{a}({b}) bằng công thức đổi cơ số.',I(n),f'Vì {b}={a}^{n}, theo định nghĩa hay đổi cơ số log_{a}({b})=ln({b})/ln({a})={n}.'

@method('v117_log_inequality_direction','bpt_logarit','Đổi chiều bất phương trình logarit khi cơ số nhỏ hơn 1','decreasing-log-monotonic-reversal','Log cơ số (0,1) là hàm nghịch biến',12)
def log_bpt(t):
    a=Q(1,2+t%4);c=t+1;v=I(c)
    return dict(a=str(a),c=c),f'Giải bất phương trình log_{a}(x)≥log_{a}({c}), với x>0. Giá trị nguyên lớn nhất của x là bao nhiêu?',v,f'Cơ số {a} thuộc (0,1), log nghịch biến, nên x≤{c}. Kèm x>0, giá trị nguyên lớn nhất là {c}.'

@method('v117_integral_substitute_affine','nguyen_ham_tich_phan','Tích phân đổi biến một đa thức theo ax+b','substitution-linear-inner-power','u=ax+b và đổi hai cận',12)
def int_sub(t):
    a=t+1;n=2+t%3;end=t+2
    v=simplify(integrate(a*(a*x+1)**n,(x,0,end)))
    return dict(a=a,n=n,end=end),f'Tính I=∫₀^{end} {a}({a}x+1)^{n} dx.',v,f'Đặt u={a}x+1 thì du={a}dx. Cận 0→1, {end}→{a*end+1}. I=[u^{n+1}/({n+1})]₁^{a*end+1}={v}.'

@method('v117_integral_cos','nguyen_ham_tich_phan','Tích phân cos trên đoạn đặc biệt','integral-cos-chain-rule','Nguyên hàm cos(ax)=sin(ax)/a',12)
def int_cos(t):
    a=t+1;upper=pi/(2*a);v=Q(1,a)
    return dict(a=a),f'Tính I=∫₀^(π/{2*a}) cos({a}x) dx.',v,f'Nguyên hàm là sin({a}x)/{a}. Khi x=π/{2*a}, sin(π/2)=1; tại 0 bằng 0, nên I={v}.'

@method('v117_integral_abs_area','ung_dung_tich_phan','Diện tích khi hàm đổi dấu trên đoạn','absolute-integral-split-at-zero','Chia tích phân |f| tại nghiệm của f',12)
def int_abs(t):
    a=t+1;v=I(a*a)
    return dict(a=a),f'Tính diện tích phần giữa y=x và trục Ox trên đoạn [−{a};{a}].',v,f'Vì x đổi dấu tại 0, diện tích ∫_−{a}^0 (−x)dx+∫₀^{a} x dx={a*a}/2+{a*a}/2={v}.'

@method('v117_complex_modulus','bieu_dien_so_phuc','Môđun số phức','complex-modulus-pythagorean','|a+bi|=√(a²+b²)',12)
def complex_norm(t):
    a=3*t;b=4*t;v=I(5*t)
    return dict(a=a,b=b),f'Cho z={a}+{b}i. Tính |z|.',v,f'Theo môđun, |z|=√({a}²+{b}²)=√({25*t*t})={v}.'

@method('v117_complex_quadratic_real_part','pt_so_phuc','Giải phương trình bậc hai có nghiệm thuần ảo','complex-square-negative-root','i²=−1, nghiệm ±bi',12)
def complex_roots(t):
    a=t+2;v=I(a)
    return dict(a=a),f'Phương trình z²+{a*a}=0 có hai nghiệm phức. Môđun của mỗi nghiệm bằng bao nhiêu?',v,f'z²=−{a*a} ⇒ z=±{a}i. Cả hai có môđun |z|={a}.'

@method('v117_complex_conjugate_norm_sq','so_phuc','Tích số phức với liên hợp','complex-conjugate-product-modulus-square','z·conj(z)=a²+b²',12)
def conj_prod(t):
    a=t+1;b=t-2;v=I(a*a+b*b)
    return dict(a=a,b=b),f'Với z={a}+({b})i, tính z·z̄.',v,f'Vì (a+bi)(a−bi)=a²+b², giá trị là {a}²+({b})²={v}.'

@method('v117_point_plane_foot','g12_geom_point_plane_distance','Hình chiếu vuông góc của điểm lên mặt phẳng trục','orthogonal-projection-coordinate-plane','Hình chiếu trên z=c giữ nguyên x,y',12)
def foot_plane(t):
    a=t+2;b=t+1;c=-t;h=3+t
    return dict(a=a,b=b,c=c,h=h),f'Trong Oxyz, hình chiếu H của A({a};{b};{h}) lên mặt phẳng z={c} có tọa độ z_H bằng bao nhiêu?',I(c),f'Mặt phẳng z={c} song song Oxy, đường vuông góc song song Oz, nên H({a};{b};{c}), suy ra z_H={c}.'

@method('v117_plane_line_intersection','g12_geom_line_plane_intersection','Tìm tham số giao điểm đường thẳng và mặt phẳng','line-plane-parameter-substitution','Thế tọa độ tham số vào ax+by+cz=d',12)
def intersect_lp(t):
    x0=t;y0=2*t;z0=-t;vx=1;vy=2;vz=-1;T=t+1;d=(x0+vx*T)+2*(y0+vy*T)+3*(z0+vz*T)
    den=vx+2*vy+3*vz
    return dict(P=[x0,y0,z0],v=[vx,vy,vz],d=d),f'Đường thẳng (x;y;z)=({x0};{y0};{z0})+s(1;2;−1) cắt mặt phẳng x+2y+3z={d}. Tìm tham số s.',I(T),f'Thế đường thẳng vào mặt phẳng: ({x0}+s)+2({y0}+2s)+3({z0}−s)={d}, hệ số s={den}≠0; s={T}.'

@method('v117_plane_parallel_parameter','g12_geom_plane_equation','Điều kiện hai mặt phẳng song song từ vectơ pháp tuyến','plane-parallel-normal-proportionality','Hai vectơ pháp tuyến cùng phương',12)
def planes_parallel(t):
    a=t+1;b=2*a;c=3*a
    return dict(a=a,b=b,c=c),f'Mặt phẳng P: {a}x+{b}y+{c}z=1 và Q: kx+4y+6z=8. Tìm k để P và Q song song.',I(2),f'Pháp tuyến P={a}(1;2;3), pháp tuyến Q=(k;4;6). Để cùng phương, tỉ số từ thành phần y và z bằng 2, nên k=2. Hai mặt phẳng không trùng vì hệ số tự do không tỉ lệ tương ứng.'

@method('v117_3d_cross_product_norm','g12_geom_vectors_3d','Diện tích hình bình hành qua tích có hướng','cross-product-magnitude-three-dimensional','|u×v| qua định thức 3D',12)
def cross_norm(t):
    a=t+2;b=t+3
    return dict(a=a,b=b),f'Trong Oxyz, hai cạnh hình bình hành có vectơ u=({a};0;0), v=(0;{b};0). Tính diện tích hình bình hành.',I(a*b),f'u×v=(0;0;{a*b}), nên diện tích bằng |u×v|={a*b}.'

@method('v117_volume_revolution','g12_solid_of_revolution','Thể tích vật thể tròn xoay bằng phương pháp đĩa','disk-method-solid-of-revolution','V=π∫y(x)² dx',12,real_world=True)
def rev_vol(t):
    a=t+1;b=t+2;v=simplify(pi*a*a*b**3/3)
    return dict(a=a,b=b),f'Quay miền dưới y={a}x, 0≤x≤{b}, quanh Ox. Tính thể tích khối tròn xoay.',v,f'Phương pháp đĩa: V=π∫₀^{b}({a}x)² dx=π·{a*a}·{b}³/3={v}.'

@method('v117_binomial_variance','xac_suat_12','Phương sai số lần thành công nhị thức','binomial-count-variance-npq','Var(X)=np(1−p)',12,real_world=True)
def bin_var(t):
    n=t+5;p=Q(1,2+t%3);v=simplify(n*p*(1-p))
    return dict(n=n,p=str(p)),f'Một phép thử Bernoulli có P(thành công)={p}, thực hiện {n} lần độc lập. Phương sai của số lần thành công bằng bao nhiêu?',v,f'X∼Bin({n},{p}), Var(X)=np(1−p)={n}·{p}·(1−{p})={v}.'

@method('v117_uniform_integer_expectation','xac_suat_12','Kỳ vọng của biến đều rời rạc liên tiếp','discrete-uniform-arithmetic-mean','E[X]=(a+b)/2',12)
def uniform_exp(t):
    a=t;b=3*t+2;v=Q(a+b,2)
    return dict(a=a,b=b),f'Biến ngẫu nhiên X nhận đều các giá trị nguyên từ {a} tới {b} (kể cả hai đầu). Tính E[X].',v,f'Giá trị trung bình của dãy số nguyên liên tiếp bằng trung bình đầu cuối: E[X]=({a}+{b})/2={v}.'

@method('v117_truncated_cone_volume','g12_geom_solid_surface_area','Thể tích hình nón cụt','frustum-volume-radii-heights','V=πh(R²+Rr+r²)/3',12,real_world=True)
def frustum(t):
    R=t+4;r=t+1;h=3*t;v=simplify(pi*h*(R*R+R*r+r*r)/3)
    return dict(R=R,r=r,h=h),f'Một hình nón cụt có bán kính đáy lớn R={R}, bán kính đáy nhỏ r={r}, chiều cao h={h}. Tính thể tích.',v,f'V=πh(R²+Rr+r²)/3=π·{h}·({R}²+{R}·{r}+{r}²)/3={v}.'

@method('v117_sphere_plane_circle_radius','g12_geom_sphere_plane_intersection','Bán kính đường tròn giao giữa mặt cầu và mặt phẳng','sphere-plane-section-radius-pythagorean','ρ=√(R²−d²) với d<R',12)
def sphere_slice(t):
    R=5*t;d=3*t;v=I(4*t)
    return dict(R=R,d=d),f'Mặt phẳng cách tâm mặt cầu bán kính {R} cm một khoảng {d} cm. Tính bán kính giao tuyến tròn.',v,f'Gọi ρ là bán kính giao tuyến. Tam giác vuông cho ρ²=R²−d²={R*R}−{d*d}={v*v}, nên ρ={v} cm.'

@method('v117_point_line_min_distance','g12_geom_min_distance_3d','Khoảng cách ngắn nhất từ điểm đến trục Oz','distance-to-axis-in-3d','Khoảng cách điểm tới trục Oz bằng √(x²+y²)',12)
def point_axis_dist(t):
    px=3*t;py=4*t;pz=t+7;v=I(5*t)
    return dict(P=[px,py,pz]),f'Trong Oxyz, khoảng cách ngắn nhất từ P({px};{py};{pz}) tới trục Oz bằng bao nhiêu?',v,f'Hình chiếu P lên Oz là (0;0;{pz}); khoảng cách bằng √({px}²+{py}²)={v}.'

@method('v117_rect_optimal_area','gtln_gtnn','Tối ưu diện tích chữ nhật khi cố định chu vi','amgm-rectangle-fixed-perimeter','AM-GM cho hai cạnh cùng tổng',12,real_world=True)
def rectangle_opt(t):
    p=8*t;v=I(t*t*4)
    return dict(P=p),f'Một hình chữ nhật có chu vi {p} m. Diện tích lớn nhất có thể là bao nhiêu m²?',v,f'Gọi hai cạnh a,b, a+b={p}/2={p//2}. Theo AM-GM ab≤[(a+b)/2]²={p//4}²={v}, đạt khi a=b={p//4}.'

FAMILIES=frozenset(HANDLERS)
BY_ID={m.family:m for m in METHODS}
FORMATS=('tra_loi_ngan','trac_nghiem','dung_sai','tu_luan_ngan','van_dung')

def _normalize(value):return str(simplify(value))
def _hash(text):return sha256(re.sub(r'\s+',' ',text.casefold().strip()).encode('utf-8')).hexdigest()

def generate(family, ordinal, difficulty=None, seed_key=None):
    if family not in FAMILIES or type(ordinal)!=int or not 0<=ordinal<10:
        raise ValueError('unknown family / ordinal out of range')
    m=BY_ID[family]; p,base,value,reason=HANDLERS[family](ordinal+2)
    value=simplify(value);actual=_normalize(value);fmt=FORMATS[ordinal%5];extra={}
    if fmt=='trac_nghiem':
        # Keep distractors in the answer's mathematical domain; avoid
        # negative counts or impossible probabilities.
        pool=[]
        if family in {'v117_hypergeometric_selection','v117_bayes_inverse'}:
            pool=[1-value, value/2, (value+1)/2, Q(1,10),Q(1,4),Q(1,3),Q(2,3),Q(3,4),Q(9,10)]
        elif family in {'v117_trig_cos_sum','v117_trig_double_sin'}:
            pool=[I(-1),-sqrt(3)/2,-sqrt(2)/2,Q(-1,2),I(0),Q(1,2),sqrt(2)/2,sqrt(3)/2,I(1)]
        elif family in {'v117_quadratic_root_count','v117_trig_equation_count',
                        'v117_stars_bars_positive','v117_nonadjacent_selection'}:
            pool=[value+1, value+2, value+3,abs(value-1),2*value]
        else:
            pool=[value+1,value-1,2*value,value/2,value+2,value-2,value+3]
        distractors=[]
        for trial in pool:
            trial=simplify(trial)
            if simplify(trial-value)==0: continue
            if family in {'v117_hypergeometric_selection','v117_bayes_inverse'} and not 0<=trial<=1: continue
            if family in {'v117_trig_cos_sum','v117_trig_double_sin'} and not -1<=float(trial)<=1: continue
            if family in {'v117_quadratic_root_count','v117_trig_equation_count',
                          'v117_stars_bars_positive','v117_nonadjacent_selection'} and trial<0: continue
            if any(simplify(trial-z)==0 for z in distractors):continue
            distractors.append(trial)
            if len(distractors)==3:break
        if len(distractors)!=3:raise RuntimeError('cannot build 3 valid distractors')
        index=(ordinal//5+1)%4
        options=list(map(_normalize,distractors));options.insert(index,actual)
        text=base+' Chọn một trong bốn kết quả chính xác.'
        ans=actual;extra={'options':options,'correct_index':index}
        solution=reason+f' Đáp án đúng: {"ABCD"[index]}.'
    elif fmt=='dung_sai':
        guess=value if ordinal<5 else value+1
        truth=bool(simplify(guess-value)==0)
        text=base+f' Nhận định: “Kết quả bằng {_normalize(guess)}”. Đúng hay sai?'
        ans='Đúng' if truth else 'Sai';extra={'assertion_value':_normalize(guess),'truth':truth}
        solution=reason+f' Nhận định {ans.lower()}.'
    elif fmt=='tu_luan_ngan':
        text=base+' Trình bày các bước giải ngắn gọn và ghi kết quả.';ans=actual;solution=reason
    elif fmt=='van_dung':
        fmt='toan_thuc_te' if m.real_world else 'van_dung'
        text=base+' Giải thích điều kiện áp dụng công thức trước khi kết luận.';ans=actual;solution=reason
    else:
        text=base+' Điền đáp số chính xác, không làm tròn.';ans=actual;solution=reason
    return dict(family=family,ordinal=ordinal,params=p,stem=text,answer=ans,solution=solution,
                difficulty=difficulty or m.difficulty,question_type=fmt,numeric_result=actual,
                topic_id=m.topic,method_signature=m.signature,skill=m.skill,
                method_review_status='pending-expert-review',independence_certified=False,
                seed_key=seed_key or '', fingerprint=_hash(text),**extra)

def verify(data):
    try:
        if data.get('family') not in FAMILIES:return False,{'error':'unknown family'}
        if data != generate(data['family'],data['ordinal'],data['difficulty'],data.get('seed_key')):
            return False,{'error':'tampering / generator mismatch'}
        m=BY_ID[data['family']]
        from .v117_oracle import expected as independent_expected
        p,base,actual,worked=HANDLERS[m.family](data['ordinal']+2)
        oracle=independent_expected(m.family,data['params'])
        if simplify(oracle-actual)!=0 or simplify(oracle-__import__('sympy').sympify(data['numeric_result']))!=0:
            return False,{'error':'arithmetic mismatch'}
        if data['question_type']=='trac_nghiem':
            opts=data['options'];k=data['correct_index']
            if len(opts)!=4 or len(set(opts))!=4 or not 0<=k<4 or opts[k]!=data['numeric_result']:
                return False,{'error':'MCQ invariant failed'}
        if data['question_type']=='dung_sai':
            truth=bool(simplify(__import__('sympy').sympify(data['assertion_value'])-actual)==0)
            if truth!=data['truth'] or data['answer']!=('Đúng' if truth else 'Sai'):
                return False,{'error':'true-false invariant failed'}
        if len(data['stem'])<25 or len(data['solution'])<25:return False,{'error':'insufficient explanation'}
        return True,dict(math='separately-implemented-symbolic-oracle',record='deterministic-integrity-check',
                         independence_certified=False,review_required=True)
    except Exception as exc:
        return False,{'error':f'{type(exc).__name__}: {exc}'}


def export(destination):
    from pathlib import Path
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    out_forms=destination/'V117_NEW_CANDIDATE_FORMS.jsonl'
    out_questions=destination/'V117_NEW_QUESTIONS.jsonl'
    seen=set();total=0;format_counts=Counter()
    with out_forms.open('w',encoding='utf8') as fo, out_questions.open('w',encoding='utf8') as qo:
        for m in METHODS:
            fo.write(json.dumps({**m.__dict__,'status':'pending-expert-review','certified_independent':False},ensure_ascii=False)+'\n')
            for i in range(10):
                item=generate(m.family,i)
                ok,evidence=verify(item)
                if not ok:raise RuntimeError(f'{m.family}/{i} verification failed: {evidence}')
                if item['fingerprint'] in seen:raise RuntimeError('duplicate stem')
                seen.add(item['fingerprint'])
                format_counts[item['question_type']]+=1
                qo.write(json.dumps({**item,'verification':evidence},ensure_ascii=False,default=str)+'\n')
                total+=1
    return dict(candidate_methods=len(METHODS),questions=total,distinct_texts=len(seen),
                formats=dict(format_counts),independent_certified=0,publication='blocked')
