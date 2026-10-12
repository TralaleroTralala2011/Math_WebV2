"""Original curriculum-aligned geometry question generators for grades 10-12.

Questions are newly authored from curriculum skills and mathematical archetypes;
this module does not reproduce textbook wording or proprietary exercise sets.
"""
from __future__ import annotations
import math, random
from fractions import Fraction


def _q(question, answer, solution, distractors, hint, family, style="calculation"):
    return {"question": question, "answer": answer, "solution": solution,
            "distractors": distractors, "hint": hint,
            "template_source": "geometry_curriculum_bank", "archetype": family,
            "template_family": family, "generation_style": style,
            "geometry_curriculum_aligned": True}


def _fmt_fraction(n, d):
    f = Fraction(n, d)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def _linear_term(base, coefficient, variable):
    sign = "+" if coefficient >= 0 else "−"
    magnitude = abs(coefficient)
    coef = "" if magnitude == 1 else str(magnitude)
    return f"{base}{sign}{coef}{variable}"


def _shifted(variable, center):
    return f"{variable}{'−' + str(center) if center >= 0 else '+' + str(abs(center))}"


def _g10_triangle(level):
    family = random.choice(["cosine_rule", "sine_rule", "triangle_area", "bearing", "triangle_reverse"] if level == "hard" else ["cosine_rule", "triangle_area", "right_triangle", "sine_rule"] if level == "medium" else ["right_triangle", "triangle_area", "cosine_basic"])
    if family == "right_triangle":
        a,b = random.choice([(3,4),(5,12),(8,15),(7,24),(9,12)])
        k = random.randint(1,3 if level != "hard" else 5); a*=k; b*=k; c=math.isqrt(a*a+b*b)
        return _q(f"Một tam giác vuông có hai cạnh góc vuông dài {a} cm và {b} cm. Tính cạnh huyền.", c,
                  f"Theo định lý Pythagore, c²={a}²+{b}²={a*a+b*b}={c}², do đó c={c} cm.", [a+b, c+2, abs(a-b)], "Xác định hai cạnh góc vuông rồi áp dụng định lý Pythagore.", family)
    if family == "triangle_area":
        b=random.randint(5,18); h=random.randint(3,14); area=Fraction(b*h,2)
        return _q(f"Một tam giác có đáy {b} cm và chiều cao tương ứng {h} cm. Tính diện tích.", _fmt_fraction(b*h,2),
                  f"S=1/2·đáy·chiều cao=1/2·{b}·{h}={_fmt_fraction(b*h,2)} cm².", [b*h, b+h, _fmt_fraction(b+h,2)], "Chiều cao phải ứng với cạnh đáy đã chọn.", family)
    if family in ("cosine_rule", "cosine_basic"):
        # Pythagorean triples scaled, angle opposite c
        a,b,c=random.choice([(5,6,7),(7,8,9),(6,7,8),(8,10,12),(5,7,9),(9,10,11)])
        k=random.randint(1,2); a*=k;b*=k;c*=k
        ans=Fraction(a*a+b*b-c*c,2*a*b)
        return _q(f"Trong tam giác ABC, AB={a} cm, AC={b} cm và BC={c} cm. Tính cos A.", _fmt_fraction(ans.numerator,ans.denominator),
                  f"Định lý cos: cos A=(AB²+AC²−BC²)/(2·AB·AC)=({a}²+{b}²−{c}²)/(2·{a}·{b})={_fmt_fraction(ans.numerator,ans.denominator)}.",
                  ["0", "1/2", "-1/2", "1"], "Cạnh đối diện góc A là BC.", family)
    if family == "sine_rule":
        # construct exact 30-60-90 or 30-30-120 facts
        side=random.choice([6,8,10,12,14]); angle=random.choice([30,45,60])
        other=random.choice([30,45,60,90])
        if angle+other>=170: other=60
        return _q(f"Trong tam giác ABC, góc A={angle}°, góc B={other}° và cạnh a đối diện góc A dài {side} cm. Viết biểu thức tính cạnh b theo định lý sin.",
                  f"{side}·sin({other}°)/sin({angle}°)",
                  f"Định lý sin cho b/sin B=a/sin A, nên b=a·sin B/sin A={side}·sin({other}°)/sin({angle}°).",
                  [f"{side}·sin({angle}°)/sin({other}°)", f"{side}·sin({angle+other}°)", str(side)], "Cạnh nào cũng phải đi cùng sin của góc đối diện.", family, "reasoning")
    if family == "triangle_reverse":
        base=random.choice([6,8,10,12,14,16]); area=random.choice([24,30,36,42,48,60,72]); height=Fraction(2*area,base)
        return _q(f"Một tam giác có diện tích {area} cm² và đáy {base} cm. Tìm chiều cao tương ứng.", _fmt_fraction(height.numerator,height.denominator), f"S=1/2·b·h nên h=2S/b=2·{area}/{base}={_fmt_fraction(height.numerator,height.denominator)} cm.", [str(base/2),str(area/base),str(2*area)], "Đảo công thức diện tích tam giác để tìm chiều cao.", family, "reverse")
    # reverse/real-life bearing, use Pythagorean construction
    x=random.randint(6,18); y=random.randint(6,18); hyp=math.sqrt(x*x+y*y)
    return _q(f"Từ điểm O, một người đi {x} km về phía đông rồi {y} km về phía bắc. Khoảng cách thẳng từ vị trí cuối đến O là bao nhiêu km? (Làm tròn 0,1 km.)",
              f"{hyp:.1f}", f"Hai hướng đông và bắc vuông góc. d=√({x}²+{y}²)=√{x*x+y*y}≈{hyp:.1f} km.", [f"{x+y:.1f}", f"{abs(x-y):.1f}", f"{x*y:.1f}"], "Mô hình đường đi thành hai cạnh góc vuông.", family, "application")


def _g10_vector(level):
    ax,ay=[random.randint(-5,5) for _ in range(2)]; bx,by=[random.randint(-5,5) for _ in range(2)]
    family=random.choice(["vector_components","vector_length","dot_product","midpoint","collinearity"] if level=="hard" else ["vector_components","vector_length","dot_product","midpoint"] if level=="medium" else ["vector_components","midpoint","vector_length"])
    if family=="vector_components":
        ans=(bx-ax,by-ay)
        return _q(f"Cho A({ax}; {ay}), B({bx}; {by}). Tìm tọa độ vectơ AB.", f"({ans[0]}; {ans[1]})", f"AB=(xB−xA; yB−yA)=({bx}−({ax}); {by}−({ay}))=({ans[0]}; {ans[1]}).", [f"({bx+ax}; {by+ay})",f"({ax-bx}; {ay-by})",f"({ans[1]}; {ans[0]})"], "Lấy tọa độ điểm cuối trừ tọa độ điểm đầu.", family)
    if family=="midpoint":
        mx,my=Fraction(ax+bx,2),Fraction(ay+by,2)
        return _q(f"Cho A({ax}; {ay}), B({bx}; {by}). Tìm tọa độ trung điểm M của AB.", f"({_fmt_fraction(mx.numerator,mx.denominator)}; {_fmt_fraction(my.numerator,my.denominator)})", f"M=((xA+xB)/2;(yA+yB)/2)=(({ax}+{bx})/2;({ay}+{by})/2).", [f"({ax+bx}; {ay+by})",f"({bx-ax}; {by-ay})",f"({ax}; {by})"], "Tính trung bình cộng riêng cho hoành độ và tung độ.", family)
    if family=="vector_length":
        dx,dy=bx-ax,by-ay; d2=dx*dx+dy*dy
        return _q(f"Với A({ax}; {ay}), B({bx}; {by}), tính bình phương độ dài AB.", d2, f"AB²=(xB−xA)²+(yB−yA)²=({dx})²+({dy})²={d2}.", [d2+1,abs(dx)+abs(dy),dx*dx-dy*dy], "Bình phương khoảng cách là tổng hai bình phương độ lệch tọa độ.", family)
    if family=="dot_product":
        ux,uy=[random.randint(-4,4) for _ in range(2)]; vx,vy=[random.randint(-4,4) for _ in range(2)]; ans=ux*vx+uy*vy
        return _q(f"Cho u=({ux}; {uy}), v=({vx}; {vy}). Tính tích vô hướng u·v.", ans, f"u·v={ux}·{vx}+{uy}·{vy}={ans}.", [ux*vx-uy*vy,ux+vx+uy+vy,ans+2], "Nhân các tọa độ tương ứng rồi cộng lại.", family)
    # collinearity through slope-free determinant
    cx,cy=random.randint(-4,4),random.randint(-4,4); k=random.choice([-3,-2,2,3]); dx,dy=k*(bx-ax),k*(by-ay)
    return _q(f"A({ax};{ay}), B({bx};{by}), C({ax+dx};{ay+dy}). Ba điểm có thẳng hàng không?", "Có", f"AB=({bx-ax};{by-ay}), AC=({dx};{dy})={k}·AB. Hai vectơ cùng phương nên A, B, C thẳng hàng.", ["Không", "Chỉ khi A là gốc tọa độ", "Không đủ dữ kiện"], "Kiểm tra hai vectơ AB và AC có tỉ lệ hay không.", family, "reasoning")


def _g10_coordinate(level):
    family=random.choice(["distance_line","circle_equation","line_through_point","circle_tangent","parabola_focus"] if level=="hard" else ["distance_line","circle_equation","line_through_point","parabola_basic"] if level=="medium" else ["distance_line","circle_equation","line_slope"])
    if family=="distance_line":
        x,y=random.randint(-5,5),random.randint(-5,5); a,b=random.choice([(1,0),(0,1),(1,1),(1,-1),(2,1)]); c=random.randint(-5,5); num=abs(a*x+b*y+c); den=math.sqrt(a*a+b*b); ans=num/den
        return _q(f"Tính khoảng cách từ P({x};{y}) đến đường thẳng d: {a}x {b:+d}y {c:+d}=0. Làm tròn đến 0,1.", f"{ans:.1f}", f"d(P,d)=|{a}·{x}+({b})·{y}+({c})|/√({a}²+{b}²)={num}/√{a*a+b*b}≈{ans:.1f}.", [f"{num:.1f}",f"{(num/(a*a+b*b)):.1f}",f"{ans+1:.0f}"], "Dùng công thức khoảng cách từ điểm đến đường thẳng.", family)
    if family=="circle_equation":
        h,k=random.randint(-5,5),random.randint(-5,5); r=random.randint(2,9)
        return _q(f"Viết phương trình đường tròn tâm I({h};{k}), bán kính R={r}.", f"(x−({h}))²+(y−({k}))²={r*r}", f"Dạng chuẩn là (x−a)²+(y−b)²=R². Thay I({h};{k}), R={r} được (x−({h}))²+(y−({k}))²={r*r}.", [f"(x+{h})²+(y+{k})²={r}",f"(x−{h})²+(y−{k})²={2*r}",f"x²+y²={r*r}"], "Tâm là (a,b), nên trong ngoặc phải là x−a và y−b.", family)
    if family in ("line_through_point","line_slope"):
        m=random.choice([-3,-2,-1,1,2,3]); x0,y0=random.randint(-4,4),random.randint(-4,4); b=y0-m*x0
        return _q(f"Tìm phương trình đường thẳng có hệ số góc {m} và đi qua P({x0};{y0}).", f"y={m}x{b:+d}", f"Dùng y−y₀=m(x−x₀): y−({y0})={m}(x−({x0})), suy ra y={m}x{b:+d}.", [f"y={-m}x{b:+d}",f"y={m}x{-b:+d}",f"y={x0}x{y0:+d}"], "Dùng dạng điểm-hệ số góc y−y₀=m(x−x₀).", family)
    if family=="circle_tangent":
        h,k=random.randint(-3,3),random.randint(-3,3); r=random.randint(2,6); x=h+r
        return _q(f"Đường tròn (x−({h}))²+(y−({k}))²={r*r}. Viết tiếp tuyến tại điểm T({x};{k}) thuộc đường tròn.", f"x={x}", f"T nằm bên phải tâm I({h};{k}); bán kính IT nằm ngang, nên tiếp tuyến vuông góc IT là đường thẳng đứng x={x}.", [f"y={k}",f"x={h}",f"y={x}"], "Tiếp tuyến vuông góc với bán kính tại tiếp điểm.", family, "reasoning")
    p=random.randint(1,5)
    return _q(f"Parabol y²={4*p}x có tiêu điểm nào?", f"F({p};0)", f"Dạng chuẩn y²=4px có tiêu điểm F(p;0). Ở đây p={p}, nên F({p};0).", [f"F(0;{p})",f"F(-{p};0)",f"F(0;{-p})"], "Nhận dạng dạng chuẩn của parabol có trục trùng Ox.", family)


def _g11_transform(level):
    family=random.choice(["translation","reflection","rotation"])
    x,y=random.randint(-6,6),random.randint(-6,6)
    if family=="translation":
        a,b=random.randint(-5,5),random.randint(-5,5)
        return _q(f"Phép tịnh tiến theo vectơ v=({a};{b}) biến điểm M({x};{y}) thành M'. Tìm M'.", f"({x+a}; {y+b})", f"Cộng vectơ tịnh tiến vào tọa độ điểm: M'=({x}+{a};{y}+{b})=({x+a};{y+b}).", [f"({x-a};{y-b})",f"({x+b};{y+a})",f"({-x-a};{-y-b})"], "Phép tịnh tiến cộng cùng một vectơ vào mọi điểm.", family)
    if family=="reflection":
        axis=random.choice(["Ox","Oy","đường thẳng y=x"])
        ans=(x,-y) if axis=="Ox" else (-x,y) if axis=="Oy" else (y,x)
        return _q(f"Tìm ảnh của M({x};{y}) qua phép đối xứng trục {axis}.", f"({ans[0]}; {ans[1]})", f"Đối xứng qua {axis} biến M({x};{y}) thành M'({ans[0]};{ans[1]}).", [f"({-ans[0]};{-ans[1]})",f"({ans[1]};{ans[0]})",f"({x};{y})"], "Nhớ tọa độ nào đổi dấu hoặc hoán đổi khi đối xứng qua trục đã cho.", family)
    angle=random.choice([90,180,270]);
    ans=(-y,x) if angle==90 else (-x,-y) if angle==180 else (y,-x)
    return _q(f"Quay điểm M({x};{y}) quanh gốc O góc {angle}° ngược chiều kim đồng hồ. Tìm ảnh M'.", f"({ans[0]}; {ans[1]})", f"Quy tắc quay tâm O: {angle}° biến (x;y) thành ({ans[0]};{ans[1]}).", [f"({-ans[0]};{-ans[1]})",f"({y};{x})",f"({x};{y})"], "Dùng quy tắc tọa độ của phép quay tâm O.", family)


def _g11_space(level):
    family=random.choice(["parallel_planes","line_plane_angle","pyramid_section","perpendicular_distance","space_reasoning"] if level=="hard" else ["parallel_planes","line_plane_angle","pyramid_section","line_plane_position"] if level=="medium" else ["parallel_planes","line_plane_position","cube_diagonal"])
    if family=="parallel_planes":
        return _q("Cho hình lập phương ABCD.A'B'C'D'. Hai mặt phẳng (ABCD) và (A'B'C'D') có quan hệ gì?", "Song song", "Hai mặt phẳng là hai mặt đáy đối diện của hình lập phương; chúng không cắt nhau nên song song.", ["Vuông góc", "Trùng nhau", "Cắt nhau theo đường AC"], "Xét hai mặt đáy đối diện của hình lập phương.", family, "knowledge")
    if family=="line_plane_position":
        return _q("Trong hình lập phương ABCD.A'B'C'D', đường thẳng AB và mặt phẳng (A'B'C'D') có quan hệ gì?", "Song song", "AB nằm trong mặt đáy dưới, còn (A'B'C'D') là mặt đáy trên song song với đáy dưới; do đó AB song song với mặt phẳng này.", ["Vuông góc", "Nằm trong mặt phẳng", "Cắt mặt phẳng tại A'"], "Một đường thẳng nằm trong mặt phẳng song song với mặt phẳng kia sẽ song song với mặt phẳng đó.", family, "knowledge")
    if family=="cube_diagonal":
        a=random.randint(2,10); d=a*math.sqrt(3)
        return _q(f"Hình lập phương cạnh {a} cm. Độ dài đường chéo không gian bằng bao nhiêu?", f"{a}√3", f"Đường chéo không gian d=√(a²+a²+a²)=a√3={a}√3 cm.", [f"{a}√2",str(3*a),f"{2*a}√2"], "Đường chéo không gian có bình phương bằng tổng bình phương ba cạnh vuông góc.", family)
    if family=="line_plane_angle":
        a=random.choice([3,4,5,6,8]); h=random.choice([3,4,5,7]); hyp=math.sqrt(a*a+h*h); sinang=h/hyp
        return _q(f"Một đoạn thẳng nối điểm P ở ngoài mặt phẳng (α) với hình chiếu H của P trên (α), có PH={h} cm. Điểm A nằm trên (α), HA={a} cm và PA là cạnh huyền của tam giác PHA. Viết sin của góc giữa PA và (α).", f"{h}/√({a*a+h*h})", f"Góc giữa PA và mặt phẳng là góc PAH. Trong tam giác vuông PHA, sin∠PAH=PH/PA={h}/√({h}²+{a}²)={h}/√({h*h+a*a}).", [f"{a}/√({a*a+h*h})",f"{h}/{a}","1"], "Góc giữa đường thẳng và mặt phẳng là góc giữa đường thẳng và hình chiếu của nó.", family, "reasoning")
    if family=="pyramid_section":
        return _q("Trong hình chóp S.ABCD có đáy ABCD là hình bình hành. Gọi M, N lần lượt là trung điểm SA, SB. Giao tuyến của mặt phẳng (CMN) với mặt phẳng đáy (ABCD) đi qua điểm nào chắc chắn?", "Điểm C", "Điểm C thuộc cả mặt phẳng (CMN) lẫn mặt phẳng đáy (ABCD), nên C thuộc giao tuyến của hai mặt phẳng.", ["Điểm S", "Trung điểm AB", "Không có điểm chung"], "Giao tuyến chứa mọi điểm chung của hai mặt phẳng.", family, "reasoning")
    # distance / reasoning from cube diagonal
    a=random.randint(2,8)
    return _q(f"Trong hình lập phương cạnh {a} cm, khoảng cách giữa hai mặt phẳng đáy đối diện bằng bao nhiêu?", a, f"Hai đáy đối diện song song; khoảng cách giữa chúng bằng cạnh vuông góc nối hai đáy, tức {a} cm.", [2*a, f"{a}√2", f"{a}√3"], "Khoảng cách giữa hai mặt phẳng song song là độ dài đoạn vuông góc chung.", family)


def _g12_space_coordinate(level, requested=None):
    all_families = ["vector_3d", "plane_equation", "sphere_equation", "line_parametric", "point_plane_distance", "angle_vectors"]
    if requested == "plane":
        all_families = ["plane_equation", "point_plane_distance"]
    elif requested == "line3d":
        all_families = ["line_parametric"]
    elif requested == "distance3d":
        all_families = ["point_plane_distance", "angle_vectors"]
    if level == "hard":
        choices = all_families
    elif level == "medium":
        choices = [f for f in all_families if f != "point_plane_distance"] or all_families
    else:
        choices = [f for f in all_families if f in {"vector_3d", "sphere_equation", "line_parametric", "plane_equation"}] or all_families
    family=random.choice(choices)
    if family=="vector_3d":
        a=[random.randint(-4,4) for _ in range(3)]; b=[random.randint(-4,4) for _ in range(3)]; ans=[b[i]-a[i] for i in range(3)]
        return _q(f"Trong không gian Oxyz, A({a[0]};{a[1]};{a[2]}), B({b[0]};{b[1]};{b[2]}). Tìm tọa độ vectơ AB.", f"({ans[0]};{ans[1]};{ans[2]})", f"AB=(xB−xA;yB−yA;zB−zA)=({ans[0]};{ans[1]};{ans[2]}).", [f"({a[0]+b[0]};{a[1]+b[1]};{a[2]+b[2]})",f"({-ans[0]};{-ans[1]};{-ans[2]})",f"({ans[1]};{ans[2]};{ans[0]})"], "Lấy tọa độ điểm B trừ tọa độ điểm A theo từng thành phần.", family)
    if family=="sphere_equation":
        x,y,z=[random.randint(-4,4) for _ in range(3)]; r=random.randint(2,8)
        return _q(f"Viết phương trình mặt cầu tâm I({x};{y};{z}), bán kính {r}.", f"(x−({x}))²+(y−({y}))²+(z−({z}))²={r*r}", f"Mặt cầu tâm I(a;b;c), bán kính R có phương trình (x−a)²+(y−b)²+(z−c)²=R². Thay dữ kiện ta được phương trình đã nêu.", [f"(x+{x})²+(y+{y})²+(z+{z})²={r}",f"x²+y²+z²={r*r}",f"(x−{x})²+(y−{y})²+(z−{z})²={2*r}"], "Dùng dạng chuẩn của mặt cầu trong Oxyz.", family)
    if family=="line_parametric":
        p=[random.randint(-4,4) for _ in range(3)]; v=[random.choice([-3,-2,-1,1,2,3]) for _ in range(3)]
        return _q(f"Đường thẳng đi qua M({p[0]};{p[1]};{p[2]}) và có vectơ chỉ phương u=({v[0]};{v[1]};{v[2]}). Viết phương trình tham số.", f"x={_linear_term(str(p[0]),v[0],'t')}; y={_linear_term(str(p[1]),v[1],'t')}; z={_linear_term(str(p[2]),v[2],'t')}", f"Dạng tham số là (x,y,z)=M+t·u, nên x={_linear_term(str(p[0]),v[0],'t')}, y={_linear_term(str(p[1]),v[1],'t')}, z={_linear_term(str(p[2]),v[2],'t')}.", [f"x={p[0]}t+{v[0]}; y={p[1]}t+{v[1]}; z={p[2]}t+{v[2]}",f"x={p[0]}+t; y={p[1]}+t; z={p[2]}+t", "Không đủ dữ kiện"], "Điểm đi qua là tọa độ tại t=0; vectơ chỉ phương là hệ số của t.", family)
    if family=="plane_equation":
        a,b,c=random.choice([(1,2,2),(2,-1,2),(1,1,1),(3,2,-1)]); x,y,z=[random.randint(-3,3) for _ in range(3)]; d=-(a*x+b*y+c*z)
        return _q(f"Mặt phẳng có vectơ pháp tuyến n=({a};{b};{c}) và đi qua P({x};{y};{z}). Viết phương trình mặt phẳng.", f"{a}x{b:+d}y{c:+d}z{d:+d}=0", f"Phương trình có dạng {a}(x−({x}))+{b}(y−({y}))+{c}(z−({z}))=0. Khai triển được {a}x{b:+d}y{c:+d}z{d:+d}=0.", [f"{a}x{b:+d}y{c:+d}z{(-d):+d}=0",f"x+y+z={x+y+z}","Không đủ dữ kiện"], "Dùng vectơ pháp tuyến làm hệ số của x, y, z rồi thay điểm P.", family)
    if family=="point_plane_distance":
        a,b,c=random.choice([(1,2,2),(2,-1,2),(2,2,1)]); x,y,z=[random.randint(-3,3) for _ in range(3)]; d=random.randint(-4,4); num=abs(a*x+b*y+c*z+d); den=math.sqrt(a*a+b*b+c*c); val=num/den
        return _q(f"Tính khoảng cách từ P({x};{y};{z}) đến mặt phẳng {a}x{b:+d}y{c:+d}z{d:+d}=0. Làm tròn đến 0,01.", f"{val:.2f}", f"d(P,(α))=|{a}·{x}+{b}·{y}+{c}·{z}+{d}|/√({a}²+{b}²+{c}²)={num}/√{a*a+b*b+c*c}≈{val:.2f}.", [f"{num:.2f}",f"{num/(a*a+b*b+c*c):.2f}",f"{val+1:.2f}"], "Lấy trị tuyệt đối biểu thức mặt phẳng tại P rồi chia độ dài vectơ pháp tuyến.", family)
    u=[random.randint(1,5) for _ in range(3)]; v=[random.randint(1,5) for _ in range(3)]; dot=sum(a*b for a,b in zip(u,v)); nu=math.sqrt(sum(a*a for a in u)); nv=math.sqrt(sum(a*a for a in v))
    return _q(f"Cho u=({u[0]};{u[1]};{u[2]}), v=({v[0]};{v[1]};{v[2]}). Viết công thức tính cos góc giữa hai vectơ theo dữ kiện tọa độ.", f"{dot}/(√{sum(a*a for a in u)}·√{sum(a*a for a in v)})", f"cos(u,v)=(u·v)/(|u||v|), với u·v={dot}, |u|=√{sum(a*a for a in u)}, |v|=√{sum(a*a for a in v)}.", [f"{dot}/({sum(a*a for a in u)}+{sum(a*a for a in v)})", f"{dot}/{sum(a*b for a,b in zip(u,v))}", "0"], "Tích vô hướng chia cho tích hai độ dài.", family, "reasoning")



def _g10_circle(level):
    family=random.choice(["circle_equation", "circle_center_radius", "circle_tangent", "circle_intersection"] if level=="hard" else ["circle_equation", "circle_center_radius", "circle_tangent"] if level=="medium" else ["circle_center_radius", "circle_equation"])
    h,k=random.randint(-5,5),random.randint(-5,5); r=random.randint(2,9)
    if family=="circle_center_radius":
        return _q(f"Đường tròn có phương trình ({_shifted('x',h)})²+({_shifted('y',k)})²={r*r}. Xác định tâm và bán kính.", f"I({h};{k}), R={r}", f"So sánh với (x−a)²+(y−b)²=R². Suy ra tâm I({h};{k}) và R=√{r*r}={r}.", [f"I({-h};{-k}), R={r*r}",f"I({h};{k}), R={r*r}",f"I({k};{h}), R={r}"], "Đọc tâm từ hai biểu thức bình phương và lấy căn bậc hai vế phải.", family)
    if family=="circle_tangent":
        x=h+r
        return _q(f"Cho đường tròn tâm I({h};{k}), bán kính {r}. Viết phương trình tiếp tuyến tại điểm T({x};{k}).", f"x={x}", f"IT nằm ngang và T là điểm ngoài cùng bên phải của đường tròn; tiếp tuyến vuông góc IT nên có phương trình x={x}.", [f"y={k}",f"x={h}",f"y={x}"], "Tiếp tuyến vuông góc với bán kính tại tiếp điểm.", family, "reasoning")
    if family=="circle_intersection":
        return _q(f"Đường tròn (C): ({_shifted('x',h)})²+({_shifted('y',k)})²={r*r}. Đường thẳng y={k} cắt (C) tại hai điểm. Khoảng cách giữa hai giao điểm bằng bao nhiêu?", 2*r, f"Đường thẳng y={k} đi qua tâm, nên dây giao tuyến là đường kính. Độ dài bằng 2R=2·{r}={2*r}.", [r, r*r, 4*r], "Đường thẳng đi qua tâm cắt đường tròn theo một đường kính.", family)
    return _q(f"Viết phương trình đường tròn tâm I({h};{k}) bán kính {r}.", f"({_shifted('x',h)})²+({_shifted('y',k)})²={r*r}", f"Dạng chuẩn: (x−a)²+(y−b)²=R². Thay tâm I({h};{k}), R={r} được phương trình yêu cầu.", [f"(x+{h})²+(y+{k})²={r}",f"(x−{h})²+(y−{k})²={2*r}",f"x²+y²={r*r}"], "Tâm I(a;b) cho các hạng x−a, y−b; vế phải là R².", family)



def _g12_sphere(level):
    family=random.choice(["sphere_equation", "sphere_center_radius", "sphere_point_check"] if level=="hard" else ["sphere_equation", "sphere_center_radius"] if level=="medium" else ["sphere_center_radius", "sphere_equation"])
    a,b,c=[random.randint(-4,4) for _ in range(3)]; r=random.randint(2,8)
    if family=="sphere_center_radius":
        return _q(f"Cho mặt cầu (x−({a}))²+(y−({b}))²+(z−({c}))²={r*r}. Xác định tâm và bán kính.", f"I({a};{b};{c}), R={r}", f"So sánh với dạng (x−a)²+(y−b)²+(z−c)²=R². Tâm là I({a};{b};{c}), bán kính R=√{r*r}={r}.", [f"I({-a};{-b};{-c}), R={r*r}",f"I({a};{b};{c}), R={r*r}",f"I({b};{a};{c}), R={r}"], "Tọa độ tâm xuất hiện trong các bình phương; bán kính là căn bậc hai vế phải.", family)
    if family=="sphere_point_check":
        x,y,z=a+r,b,c
        return _q(f"Mặt cầu tâm I({a};{b};{c}) bán kính {r}. Điểm P({x};{y};{z}) có thuộc mặt cầu không?", "Có", f"IP²=({x}−({a}))²+({y}−({b}))²+({z}−({c}))²={r*r}=R², nên P thuộc mặt cầu.", ["Không", "Chỉ khi I là gốc tọa độ", "Không đủ dữ kiện"], "Điểm thuộc mặt cầu khi khoảng cách đến tâm bằng bán kính.", family, "reasoning")
    return _q(f"Viết phương trình mặt cầu tâm I({a};{b};{c}) bán kính {r}.", f"({_shifted('x',a)})²+({_shifted('y',b)})²+({_shifted('z',c)})²={r*r}", f"Dùng dạng chuẩn (x−a)²+(y−b)²+(z−c)²=R². Thay tâm và bán kính đã cho ta được phương trình yêu cầu.", [f"(x+{a})²+(y+{b})²+(z+{c})²={r}",f"x²+y²+z²={r*r}",f"({_shifted('x',a)})²+({_shifted('y',b)})²+({_shifted('z',c)})²={2*r}"], "Dạng chuẩn của mặt cầu trong Oxyz.", family)

def _g12_volume(level):
    family=random.choice(["pyramid_volume", "cylinder_volume", "sphere_surface", "cone_volume"] if level=="hard" else ["pyramid_volume", "cylinder_volume", "sphere_volume"] if level=="medium" else ["cube_volume", "cylinder_volume", "sphere_volume"])
    if family=="cube_volume":
        a=random.randint(2,12); return _q(f"Một hình lập phương cạnh {a} cm có thể tích bao nhiêu?", a**3, f"V=a³={a}³={a**3} cm³.", [6*a*a, 3*a*a, a*a], "Thể tích hình lập phương bằng lập phương độ dài cạnh.", family)
    if family=="cylinder_volume":
        r=random.randint(2,8); h=random.randint(3,12); return _q(f"Một hình trụ có bán kính đáy {r} cm và chiều cao {h} cm. Tính thể tích theo π.", f"{r*r*h}π", f"V=πr²h=π·{r}²·{h}={r*r*h}π cm³.", [f"{2*r*h}π",f"{r*h}π",f"{r*r+h}π"], "Lấy diện tích đáy nhân chiều cao.", family)
    if family in ("sphere_volume","sphere_surface"):
        r=random.randint(2,8)
        if family=="sphere_surface": return _q(f"Mặt cầu bán kính {r} cm có diện tích mặt cầu bằng bao nhiêu theo π?", f"{4*r*r}π", f"S=4πr²=4π·{r}²={4*r*r}π cm².", [f"{r*r}π",f"{2*r}π",f"{4*r*r*r}π"], "Diện tích mặt cầu là 4πR².", family)
        return _q(f"Khối cầu bán kính {r} cm có thể tích bằng bao nhiêu theo π?", f"{_fmt_fraction(4*r**3,3)}π", f"V=4/3·πr³=4/3·π·{r}³={_fmt_fraction(4*r**3,3)}π cm³.", [f"{4*r*r}π",f"{r*r*r}π",f"{2*r**3}π"], "Thể tích khối cầu là 4πR³/3.", family)
    if family=="pyramid_volume":
        area=random.choice([12,18,24,30,36,48]); h=random.choice([3,6,9,12]); ans=Fraction(area*h,3)
        return _q(f"Một hình chóp có diện tích đáy {area} cm² và chiều cao {h} cm. Tính thể tích.", _fmt_fraction(ans.numerator,ans.denominator), f"V=1/3·Sđáy·h=1/3·{area}·{h}={_fmt_fraction(ans.numerator,ans.denominator)} cm³.", [area*h, _fmt_fraction(area*h,2), area+h], "Thể tích hình chóp bằng một phần ba tích diện tích đáy và chiều cao.", family)
    r=random.randint(2,7); h=random.randint(3,12)
    return _q(f"Một hình nón có bán kính đáy {r} cm và chiều cao {h} cm. Viết thể tích theo π.", f"{_fmt_fraction(r*r*h,3)}π", f"V=1/3·πr²h=1/3·π·{r}²·{h}={_fmt_fraction(r*r*h,3)}π cm³.", [f"{r*r*h}π",f"{2*r*h}π",f"{r*h}π"], "Thể tích hình nón bằng một phần ba thể tích hình trụ cùng đáy và chiều cao.", family)

def generate(grade: int, topic_id: str, difficulty: str):
    """Return an original geometry question, or None for a non-geometry topic."""
    t=(topic_id or "").lower()
    g=int(grade or 10)
    aliases={
      "he_thuc_luong":"triangle", "he_thuc_luong_tam_giac":"triangle", "hinh_hoc_10":"triangle",
      "vector":"vector", "toa_do_phang":"coordinate", "duong_tron":"circle", "duong_thang":"line2d",
      "phep_bien_hinh_11":"transform", "hinh_khong_gian":"space11", "song_song_khong_gian":"space11",
      "vuong_goc_khong_gian":"space11", "goc_khoang_cach_11":"space11", "thiet_dien_hinh_khong_gian_11":"space11",
      "hinh_hoc_khong_gian":"volume", "toa_do_khong_gian":"space12", "mat_phang_oxyz":"plane", "duong_thang_oxyz":"line3d", "goc_khoang_cach_oxyz":"distance3d", "mat_cau":"sphere", "the_tich_khong_gian":"volume"
    }
    kind=aliases.get(t)
    if not kind: return None
    level=difficulty if difficulty in {"easy","medium","hard"} else "medium"
    if g<=10:
        if kind=="triangle": return _g10_triangle(level)
        if kind=="vector": return _g10_vector(level)
        if kind=="coordinate": return _g10_coordinate(level)
        if kind=="line2d":
            q = _g10_coordinate(level)
            while q.get("archetype") not in {"distance_line", "line_through_point", "line_slope"}:
                q = _g10_coordinate(level)
            return q
        if kind=="circle": return _g10_circle(level)
        # If a 10th-grade topic uses a newer spatial alias, retain the topic but
        # use a foundational coordinate-plane archetype rather than unrelated content.
        return _g10_vector(level)
    if g==11:
        if kind=="transform": return _g11_transform(level)
        if kind=="space11": return _g11_space(level)
        if kind in {"triangle","vector","coordinate"}: return _g10_vector(level)
        return _g11_space(level)
    if kind=="volume": return _g12_volume(level)
    if kind=="sphere": return _g12_sphere(level)
    if kind=="plane": return _g12_space_coordinate(level, "plane")
    if kind=="line3d": return _g12_space_coordinate(level, "line3d")
    if kind=="distance3d": return _g12_space_coordinate(level, "distance3d")
    if kind in {"space12","space11"}: return _g12_space_coordinate(level)
    if kind=="coordinate": return _g12_space_coordinate(level)
    if kind=="circle": return _g10_circle(level)
    return _g12_space_coordinate(level)
