"""Original curriculum-aligned geometry question generators for grades 10-12.

Questions are newly authored from curriculum skills and mathematical archetypes;
this module does not reproduce textbook wording or proprietary exercise sets.
"""
from __future__ import annotations
import math, random, re, unicodedata
from fractions import Fraction
from .geometry_diagrams import triangle_3_4_5, triangle_from_sides, triangle_with_base_height, rectangle, square, trapezoid, rhombus, regular_polygon, circle, circle_with_tangent, circle_with_diameter, inscribed_rectangle, inscribed_right_triangle, inscribed_square, validate_geometry_diagram, inscribed_triangle_by_angles, circle_with_central_angle, triangle_from_angles, similar_triangles, circle_with_chord, coordinate_points, parallel_lines_transversal, angle_bisector_triangle, triangle_median_diagram, cyclic_chords_diagram, isosceles_triangle_diagram, parabola_diagram, cube_projection, cylinder_projection, cone_projection, sphere_projection, pyramid_projection, regular_prism_projection, triangular_prism_by_dimensions, pyramid_by_base_height, graph_diagram, line_graph, quadratic_graph, trigonometric_graph, right_triangle_with_altitude, external_tangents_to_circle


def _q(question, answer, solution, distractors, hint, family, style="calculation", diagram=None):
    if diagram:
        errors = validate_geometry_diagram(diagram)
        if errors:
            raise ValueError("Invalid geometry diagram: " + "; ".join(errors))
    return {"question": question, "answer": answer, "solution": solution,
            "distractors": distractors, "hint": hint,
            "template_source": "geometry_curriculum_bank", "archetype": family,
            "template_family": family, "generation_style": style,
            "geometry_curriculum_aligned": True, **({"diagram": diagram} if diagram else {})}


def _fmt_fraction(n, d):
    f = Fraction(n, d)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def _fmt(value):
    """Format integer/rational graph values without leaking floating-point noise."""
    f = Fraction(value).limit_denominator(10000)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def _linear_term(base, coefficient, variable):
    sign = "+" if coefficient >= 0 else "−"
    magnitude = abs(coefficient)
    coef = "" if magnitude == 1 else str(magnitude)
    return f"{base}{sign}{coef}{variable}"


def _shifted(variable, center):
    return f"{variable}{'−' + str(center) if center >= 0 else '+' + str(abs(center))}"


def _game_mode(game_id):
    raw = unicodedata.normalize("NFKD", str(game_id or "")).encode("ascii", "ignore").decode().lower()
    raw = re.sub(r"[^a-z0-9]+", "_", raw)
    if any(k in raw for k in ("giai_ma_goc", "tim_goc", "goc_bi_an", "goc_noi_tiep", "angle")):
        return "angle"
    if any(k in raw for k in ("san_canh", "san_do_dai", "do_dai", "ban_kinh", "length")):
        return "length"
    if any(k in raw for k in ("ung_dung", "ban_do", "thuc_te", "tiep_tuyen", "thu_thach", "application", "challenge")):
        return "application"
    return "mixed"


def _g10_triangle(level, game_id=""):
    mode = _game_mode(game_id)
    if mode == "angle":
        family = random.choice(["cosine_rule", "sine_rule", "cosine_basic"])
    elif mode == "length":
        family = random.choice(["right_triangle", "triangle_area", "triangle_reverse", "altitude_multi_step"] if level != "easy" else ["right_triangle", "triangle_area", "triangle_reverse"])
    elif mode == "application":
        family = random.choice(["bearing", "triangle_reverse", "triangle_area"])
    else:
        family = random.choice(["cosine_rule", "sine_rule", "triangle_area", "bearing", "triangle_reverse"] if level == "hard" else ["cosine_rule", "triangle_area", "right_triangle", "sine_rule", "altitude_multi_step"] if level == "medium" else ["right_triangle", "triangle_area", "cosine_basic"])
    if family == "altitude_multi_step":
        # A 3-4-5 family scaled to keep the altitude exact and the diagram data-consistent.
        k = random.choice([2, 3, 4])
        a, b, c = 3*k, 4*k, 5*k
        altitude = Fraction(a*b, c)
        return _q(
            f"Tam giác ABC vuông tại A có AB={a} cm, AC={b} cm. Kẻ AH vuông góc BC tại H. Tính AH.",
            _fmt_fraction(altitude.numerator, altitude.denominator),
            f"Bước 1: BC=√(AB²+AC²)=√({a}²+{b}²)={c} cm. Bước 2: Diện tích tam giác tính theo hai cách: AB·AC/2=BC·AH/2. Bước 3: AH=AB·AC/BC={a}·{b}/{c}={_fmt_fraction(altitude.numerator, altitude.denominator)} cm.",
            [str(a*b), str(Fraction(a+b,2)), str(c)],
            "Tìm cạnh huyền trước, rồi đồng nhất hai công thức diện tích tam giác.",
            family, "multi_step", diagram=right_triangle_with_altitude(a, b))

    if family == "right_triangle":
        a,b = random.choice([(3,4),(5,12),(8,15),(7,24),(9,12)])
        k = random.randint(1,3 if level != "hard" else 5); a*=k; b*=k; c=math.isqrt(a*a+b*b)
        return _q(f"Một tam giác vuông có hai cạnh góc vuông dài {a} cm và {b} cm. Tính cạnh huyền.", c,
                  f"Theo định lý Pythagore, c²={a}²+{b}²={a*a+b*b}={c}², do đó c={c} cm.", [a+b, c+2, abs(a-b)], "Xác định hai cạnh góc vuông rồi áp dụng định lý Pythagore.", family, diagram=triangle_3_4_5(a,b))
    if family == "triangle_area":
        b=random.randint(5,18); h=random.randint(3,14); area=Fraction(b*h,2)
        return _q(f"Một tam giác có đáy {b} cm và chiều cao tương ứng {h} cm. Tính diện tích.", _fmt_fraction(b*h,2),
                  f"S=1/2·đáy·chiều cao=1/2·{b}·{h}={_fmt_fraction(b*h,2)} cm².", [b*h, b+h, _fmt_fraction(b+h,2)], "Chiều cao phải ứng với cạnh đáy đã chọn.", family, diagram=triangle_with_base_height(b,h))
    if family in ("cosine_rule", "cosine_basic"):
        # Pythagorean triples scaled, angle opposite c
        a,b,c=random.choice([(5,6,7),(7,8,9),(6,7,8),(8,10,12),(5,7,9),(9,10,11)])
        k=random.randint(1,2); a*=k;b*=k;c*=k
        ans=Fraction(a*a+b*b-c*c,2*a*b)
        return _q(f"Trong tam giác ABC, AB={a} cm, AC={b} cm và BC={c} cm. Tính cos A.", _fmt_fraction(ans.numerator,ans.denominator),
                  f"Định lý cos: cos A=(AB²+AC²−BC²)/(2·AB·AC)=({a}²+{b}²−{c}²)/(2·{a}·{b})={_fmt_fraction(ans.numerator,ans.denominator)}.",
                  ["0", "1/2", "-1/2", "1"], "Cạnh đối diện góc A là BC.", family, diagram=triangle_from_sides(c,b,a))
    if family == "sine_rule":
        # construct exact 30-60-90 or 30-30-120 facts
        side=random.choice([6,8,10,12,14]); angle=random.choice([30,45,60])
        other=random.choice([30,45,60,90])
        if angle+other>=170: other=60
        return _q(f"Trong tam giác ABC, góc A={angle}°, góc B={other}° và cạnh a đối diện góc A dài {side} cm. Viết biểu thức tính cạnh b theo định lý sin.",
                  f"{side}·sin({other}°)/sin({angle}°)",
                  f"Định lý sin cho b/sin B=a/sin A, nên b=a·sin B/sin A={side}·sin({other}°)/sin({angle}°).",
                  [f"{side}·sin({angle}°)/sin({other}°)", f"{side}·sin({angle+other}°)", str(side)], "Cạnh nào cũng phải đi cùng sin của góc đối diện.", family, "reasoning", diagram=triangle_from_angles(angle,other))
    if family == "triangle_reverse":
        base=random.choice([6,8,10,12,14,16]); area=random.choice([24,30,36,42,48,60,72]); height=Fraction(2*area,base)
        return _q(f"Một tam giác có diện tích {area} cm² và đáy {base} cm. Tìm chiều cao tương ứng.", _fmt_fraction(height.numerator,height.denominator), f"S=1/2·b·h nên h=2S/b=2·{area}/{base}={_fmt_fraction(height.numerator,height.denominator)} cm.", [str(base/2),str(area/base),str(2*area)], "Đảo công thức diện tích tam giác để tìm chiều cao.", family, "reverse", diagram=triangle_with_base_height(base,height))
    # reverse/real-life bearing, use Pythagorean construction
    x=random.randint(6,18); y=random.randint(6,18); hyp=math.sqrt(x*x+y*y)
    return _q(f"Từ điểm O, một người đi {x} km về phía đông rồi {y} km về phía bắc. Khoảng cách thẳng từ vị trí cuối đến O là bao nhiêu km? (Làm tròn 0,1 km.)",
              f"{hyp:.1f}", f"Hai hướng đông và bắc vuông góc. d=√({x}²+{y}²)=√{x*x+y*y}≈{hyp:.1f} km.", [f"{x+y:.1f}", f"{abs(x-y):.1f}", f"{x*y:.1f}"], "Mô hình đường đi thành hai cạnh góc vuông.", family, "application", diagram=triangle_3_4_5(y,x))



def _g10_plane_geometry(level):
    """Broad plane-geometry bank for foundational, intermediate and olympiad-style practice."""
    if level == "easy":
        family = random.choice(["rectangle_area", "square_perimeter", "triangle_angles", "circle_radius", "parallel_angles", "triangle_area"])
    elif level == "medium":
        family = random.choice(["similar_triangles", "rhombus_area", "cyclic_quadrilateral", "tangent_radius", "trapezoid_area", "circle_chord"])
    else:
        family = random.choice(["angle_bisector", "tangent_secant", "triangle_median", "cyclic_power", "similarity_reverse", "geometry_proof"])

    if family == "rectangle_area":
        a,b=random.randint(3,15),random.randint(2,12)
        return _q(f"Hình chữ nhật ABCD có AB={a} cm, BC={b} cm. Tính diện tích hình chữ nhật.",a*b,
                  f"S=AB·BC={a}·{b}={a*b} cm².",[2*(a+b),a+b,a*b/2],"Diện tích hình chữ nhật bằng chiều dài nhân chiều rộng.",family,diagram=rectangle(a,b))
    if family == "square_perimeter":
        a=random.randint(2,18)
        return _q(f"Hình vuông MNPQ có cạnh dài {a} cm. Tính chu vi và chọn giá trị đúng.",4*a,
                  f"Bốn cạnh bằng nhau nên P=4·{a}={4*a} cm.",[a*a,2*a,4*a+4],"Chu vi là tổng độ dài bốn cạnh.",family,diagram=square(a))
    if family == "triangle_angles":
        a=random.choice([35,42,48,55,63]); b=random.choice([38,46,52,57,64]); c=180-a-b
        return _q(f"Tam giác ABC có ∠A={a}° và ∠B={b}°. Tính ∠C.",c,
                  f"Tổng ba góc trong tam giác bằng 180°, nên ∠C=180°−{a}°−{b}°={c}°.",[a+b,180-a,180-b],"Dùng tổng ba góc trong một tam giác.",family,diagram=triangle_from_angles(a,b))
    if family == "circle_radius":
        r=random.randint(2,12)
        return _q(f"Một đường tròn tâm O có đường kính AB={2*r} cm. Tính bán kính.",r,
                  f"Bán kính bằng một nửa đường kính: R={2*r}/2={r} cm.",[2*r, r+2, r*r],"Đường kính bằng hai lần bán kính.",family,diagram=circle_with_diameter(r))
    if family == "parallel_angles":
        a=random.choice([38,47,59,64,72]); ans=180-a
        return _q(f"Hai đường thẳng song song bị cắt bởi một đường thẳng. Một góc trong cùng phía bằng {a}°. Góc trong cùng phía còn lại bằng bao nhiêu?",ans,
                  f"Hai góc trong cùng phía bù nhau, nên góc cần tìm bằng 180°−{a}°={ans}°.",[a,180-2*a,min(180,a+90)],"Với hai đường thẳng song song, hai góc trong cùng phía có tổng 180°.",family,diagram=parallel_lines_transversal(a))
    if family == "triangle_area":
        b,h=random.randint(4,18),random.randint(3,14); ans=Fraction(b*h,2)
        return _q(f"Tam giác ABC có đáy AB={b} cm và chiều cao ứng với AB là {h} cm. Tính diện tích.",_fmt_fraction(ans.numerator,ans.denominator),
                  f"S=AB·h/2={b}·{h}/2={_fmt_fraction(ans.numerator,ans.denominator)} cm².",[b*h,b+h,_fmt_fraction(b*h,4)],"Chiều cao phải vuông góc với cạnh đáy.",family,diagram=triangle_with_base_height(b,h))
    if family == "similar_triangles":
        small=random.randint(3,9); scale=random.choice([2,3,4]); big=small*scale
        return _q(f"Hai tam giác đồng dạng có tỉ số cạnh tương ứng tam giác nhỏ : tam giác lớn là 1:{scale}. Một cạnh của tam giác nhỏ dài {small} cm. Cạnh tương ứng của tam giác lớn dài bao nhiêu?",big,
                  f"Các cạnh tương ứng tỉ lệ với cùng hệ số {scale}; cạnh cần tìm={small}·{scale}={big} cm.",[small+scale,small*scale*2,big+scale],"Dùng tỉ số đồng dạng cho các cạnh tương ứng.",family,"reasoning",diagram=similar_triangles(small,scale))
    if family == "rhombus_area":
        d1,d2=random.choice([(6,8),(10,12),(12,16),(14,18),(8,15)])
        ans=Fraction(d1*d2,2)
        return _q(f"Hình thoi có hai đường chéo dài {d1} cm và {d2} cm. Tính diện tích.",_fmt_fraction(ans.numerator,ans.denominator),
                  f"S=d₁d₂/2={d1}·{d2}/2={_fmt_fraction(ans.numerator,ans.denominator)} cm².",[d1*d2,d1+d2,_fmt_fraction(d1*d2,4)],"Diện tích hình thoi bằng nửa tích hai đường chéo.",family,diagram=rhombus(d1,d2))
    if family == "cyclic_quadrilateral":
        a=random.choice([72,83,96,105,118]); ans=180-a
        return _q(f"Tứ giác ABCD nội tiếp đường tròn. Nếu ∠A={a}° thì góc đối ∠C bằng bao nhiêu?",ans,
                  f"Hai góc đối của tứ giác nội tiếp bù nhau: ∠C=180°−{a}°={ans}°.",[a,90,180-2*a],"Tổng hai góc đối của tứ giác nội tiếp bằng 180°.",family,"reasoning",diagram=regular_polygon(4,5))
    if family == "tangent_radius":
        ans="90°"
        return _q("Đường thẳng d tiếp xúc đường tròn (O) tại T. Góc giữa bán kính OT và tiếp tuyến d bằng bao nhiêu?",ans,
                  "Bán kính đi qua tiếp điểm vuông góc với tiếp tuyến, nên góc bằng 90°.",["45°","60°","180°"],"Nhớ tính chất bán kính vuông góc với tiếp tuyến tại tiếp điểm.",family,"theory",diagram=circle_with_tangent(4,show_measurement=False))
    if family == "trapezoid_area":
        a,b,h=random.randint(6,18),random.randint(4,14),random.randint(3,10); ans=Fraction((a+b)*h,2)
        return _q(f"Hình thang có hai đáy {a} cm, {b} cm và chiều cao {h} cm. Tính diện tích.",_fmt_fraction(ans.numerator,ans.denominator),
                  f"S=(đáy lớn+đáy nhỏ)·h/2=({a}+{b})·{h}/2={_fmt_fraction(ans.numerator,ans.denominator)} cm².",[ (a+b)*h,(a+b)/2,a*b*h],"Cộng hai đáy song song rồi nhân chiều cao và chia 2.",family,diagram=trapezoid(a,b,h))
    if family == "circle_chord":
        r=random.choice([5,10,13,17]); half=random.randint(1,r-1); chord=2*half
        # Right triangle from centre to midpoint of chord; exact Pythagorean triples only.
        triples=[(5,3,4),(10,6,8),(13,5,12),(17,8,15)]
        r,half,dist=random.choice(triples); chord=2*half
        return _q(f"Trong đường tròn tâm O bán kính {r} cm, khoảng cách từ O đến dây AB là {dist} cm. Biết đường vuông góc từ O đến AB đi qua trung điểm H. Tính AB.",chord,
                  f"OH vuông góc AB nên H là trung điểm dây. AH=√(OA²−OH²)=√({r}²−{dist}²)={half}; AB=2AH={chord} cm.",[half, r+dist,2*dist],"Đường vuông góc từ tâm đến dây cung thì đi qua trung điểm dây.",family,"multi_step",diagram=circle_with_chord(r,half,dist))
    if family == "angle_bisector":
        m,n=random.choice([(4,6),(5,7),(6,9),(8,12)]); a=random.randint(8,20); b=Fraction(a*n,m)
        return _q(f"Trong tam giác ABC, AD là tia phân giác góc A, D thuộc BC. Biết BD:DC={m}:{n} và AB={a} cm. Tính AC.",_fmt_fraction(b.numerator,b.denominator),
                  f"Theo định lý phân giác AB/AC=BD/DC={m}/{n}, nên AC=AB·{n}/{m}={a}·{n}/{m}={_fmt_fraction(b.numerator,b.denominator)} cm.",[str(a*m/n),str(a+n-m),str(a)],"Tỉ số hai cạnh kề góc bằng tỉ số hai đoạn trên cạnh đối diện.",family,"multi_step",diagram=angle_bisector_triangle(a, float(b), m, n))
    if family == "tangent_secant":
        t=random.randint(3,9); ext=random.randint(2,8); total=t*t//ext if t*t%ext==0 else None
        # Choose integer external and whole secant lengths with power theorem.
        ext,whole=random.choice([(3,12),(4,16),(5,20),(6,24),(2,18)])
        ans=ext*whole
        return _q(f"Từ điểm P ngoài đường tròn, kẻ tiếp tuyến PT và cát tuyến PAB. Biết PA={ext} cm, PB={whole} cm. Tính PT.",f"√{ans}",
                  f"Theo định lý tiếp tuyến-cát tuyến, PT²=PA·PB={ext}·{whole}={ans}, do đó PT=√{ans} cm.",[str(ans),str(ext+whole),f"√{ext*ext+whole*whole}"],"Bình phương tiếp tuyến bằng tích đoạn ngoài và toàn bộ cát tuyến.",family,"multi_step",diagram=circle_with_tangent(4,center_label="O",show_measurement=False))
    if family == "triangle_median":
        a,b=random.choice([(6,8),(5,12),(8,15),(7,9)]); c=math.isqrt(a*a+b*b) if math.isqrt(a*a+b*b)**2==a*a+b*b else None
        if c is None: a,b=5,12; c=13
        return _q(f"Tam giác ABC vuông tại A có AB={a} cm, AC={b} cm. M là trung điểm BC. Tính AM.",c/2 if c%2 else c//2,
                  f"BC=√({a}²+{b}²)={c} cm. Trong tam giác vuông, trung điểm cạnh huyền cách đều ba đỉnh nên AM=BC/2={c}/2={_fmt_fraction(c,2)} cm.",[c,c/2+1,a+b],"Tính cạnh huyền trước, sau đó dùng tính chất trung điểm cạnh huyền.",family,"multi_step",diagram=triangle_median_diagram(a,b))
    if family == "cyclic_power":
        a=random.choice([4,5,6,7]); b=random.choice([8,9,10,12]); c=random.choice([2,3,4]); d=Fraction(a*b,c)
        return _q(f"Hai dây AB và CD cắt nhau tại P bên trong đường tròn. Biết PA={a} cm, PB={b} cm, PC={c} cm. Tính PD.",_fmt_fraction(d.numerator,d.denominator),
                  f"Theo định lý hai dây cắt nhau: PA·PB=PC·PD, nên PD={a}·{b}/{c}={_fmt_fraction(d.numerator,d.denominator)} cm.",[str(a+b-c),_fmt_fraction(a*b,2),str(a*b*c)],"Tích hai đoạn của dây thứ nhất bằng tích hai đoạn của dây thứ hai.",family,"multi_step",diagram=cyclic_chords_diagram())
    if family == "similarity_reverse":
        scale=random.choice([2,3,4]); large=random.randint(12,36); small=Fraction(large,scale)
        return _q(f"Hai tam giác đồng dạng. Một cạnh tam giác lớn dài {large} cm, cạnh tương ứng tam giác nhỏ dài {_fmt_fraction(small.numerator,small.denominator)} cm. Tỉ số đồng dạng (nhỏ:lớn) là bao nhiêu?",f"1:{scale}",
                  f"Tỉ số cạnh nhỏ/lớn={_fmt_fraction(small.numerator,small.denominator)}/{large}=1/{scale}, nên tỉ số là 1:{scale}.",[f"{scale}:1",f"1:{scale+1}",f"1:{large}"],"Lấy độ dài cạnh nhỏ chia cho cạnh lớn.",family,"reverse",diagram=similar_triangles(float(small),scale))
    # High-level proof reasoning that asks students to connect the theorem and conclusion.
    return _q("Cho tam giác ABC cân tại A. M là trung điểm BC. Hãy chọn kết luận luôn đúng.",
              "AM vuông góc BC và AM là tia phân giác góc A",
              "Trong tam giác cân tại A, đường trung tuyến kẻ từ đỉnh A đồng thời là đường cao và đường phân giác. Vì M là trung điểm BC, AM có cả hai tính chất.",
              ["AM song song BC", "AB vuông góc AC trong mọi trường hợp", "M là trung điểm AB"],
              "Kết hợp tính chất đường trung tuyến ứng với đáy của tam giác cân.",family,"proof_reasoning",diagram=isosceles_triangle_diagram())

def _g10_vector(level):
    ax,ay=[random.randint(-5,5) for _ in range(2)]; bx,by=[random.randint(-5,5) for _ in range(2)]
    family=random.choice(["vector_components","vector_length","dot_product","midpoint","collinearity"] if level=="hard" else ["vector_components","vector_length","dot_product","midpoint"] if level=="medium" else ["vector_components","midpoint","vector_length"])
    if family=="vector_components":
        ans=(bx-ax,by-ay)
        return _q(f"Cho A({ax}; {ay}), B({bx}; {by}). Tìm tọa độ vectơ AB.", f"({ans[0]}; {ans[1]})", f"AB=(xB−xA; yB−yA)=({bx}−({ax}); {by}−({ay}))=({ans[0]}; {ans[1]}).", [f"({bx+ax}; {by+ay})",f"({ax-bx}; {ay-by})",f"({ans[1]}; {ans[0]})"], "Lấy tọa độ điểm cuối trừ tọa độ điểm đầu.", family, diagram=coordinate_points({"A":[ax,ay],"B":[bx,by]},[["A","B"]],"Hai điểm A, B theo đúng tọa độ trong đề."))
    if family=="midpoint":
        mx,my=Fraction(ax+bx,2),Fraction(ay+by,2)
        return _q(f"Cho A({ax}; {ay}), B({bx}; {by}). Tìm tọa độ trung điểm M của AB.", f"({_fmt_fraction(mx.numerator,mx.denominator)}; {_fmt_fraction(my.numerator,my.denominator)})", f"M=((xA+xB)/2;(yA+yB)/2)=(({ax}+{bx})/2;({ay}+{by})/2).", [f"({ax+bx}; {ay+by})",f"({bx-ax}; {by-ay})",f"({ax}; {by})"], "Tính trung bình cộng riêng cho hoành độ và tung độ.", family, diagram=coordinate_points({"A":[ax,ay],"B":[bx,by],"M":[float(mx),float(my)]},[["A","B"],["A","M"],["M","B"]],"Trung điểm M được dựng từ đúng tọa độ hai đầu mút."))
    if family=="vector_length":
        dx,dy=bx-ax,by-ay; d2=dx*dx+dy*dy
        return _q(f"Với A({ax}; {ay}), B({bx}; {by}), tính bình phương độ dài AB.", d2, f"AB²=(xB−xA)²+(yB−yA)²=({dx})²+({dy})²={d2}.", [d2+1,abs(dx)+abs(dy),dx*dx-dy*dy], "Bình phương khoảng cách là tổng hai bình phương độ lệch tọa độ.", family, diagram=coordinate_points({"A":[ax,ay],"B":[bx,by]},[["A","B"]],"Đoạn AB theo tọa độ đã cho."))
    if family=="dot_product":
        ux,uy=[random.randint(-4,4) for _ in range(2)]; vx,vy=[random.randint(-4,4) for _ in range(2)]; ans=ux*vx+uy*vy
        return _q(f"Cho u=({ux}; {uy}), v=({vx}; {vy}). Tính tích vô hướng u·v.", ans, f"u·v={ux}·{vx}+{uy}·{vy}={ans}.", [ux*vx-uy*vy,ux+vx+uy+vy,ans+2], "Nhân các tọa độ tương ứng rồi cộng lại.", family, diagram=coordinate_points({"O":[0,0],"U":[ux,uy],"V":[vx,vy]},[["O","U"],["O","V"]],"Hai vectơ được biểu diễn bằng các điểm đầu mút theo tọa độ."))
    # collinearity through slope-free determinant
    cx,cy=random.randint(-4,4),random.randint(-4,4); k=random.choice([-3,-2,2,3]); dx,dy=k*(bx-ax),k*(by-ay)
    return _q(f"A({ax};{ay}), B({bx};{by}), C({ax+dx};{ay+dy}). Ba điểm có thẳng hàng không?", "Có", f"AB=({bx-ax};{by-ay}), AC=({dx};{dy})={k}·AB. Hai vectơ cùng phương nên A, B, C thẳng hàng.", ["Không", "Chỉ khi A là gốc tọa độ", "Không đủ dữ kiện"], "Kiểm tra hai vectơ AB và AC có tỉ lệ hay không.", family, "reasoning", diagram=coordinate_points({"A":[ax,ay],"B":[bx,by],"C":[ax+dx,ay+dy]},[["A","B"],["A","C"]],"Ba điểm được dựng theo đúng tọa độ đã cho."))


def _g10_coordinate(level):
    family=random.choice(["distance_line","circle_equation","line_through_point","circle_tangent","parabola_focus"] if level=="hard" else ["distance_line","circle_equation","line_through_point","parabola_basic"] if level=="medium" else ["distance_line","circle_equation","line_slope"])
    if family=="distance_line":
        x,y=random.randint(-5,5),random.randint(-5,5); a,b=random.choice([(1,0),(0,1),(1,1),(1,-1),(2,1)]); c=random.randint(-5,5); num=abs(a*x+b*y+c); den=math.sqrt(a*a+b*b); ans=num/den
        return _q(f"Tính khoảng cách từ P({x};{y}) đến đường thẳng d: {a}x {b:+d}y {c:+d}=0. Làm tròn đến 0,1.", f"{ans:.1f}", f"d(P,d)=|{a}·{x}+({b})·{y}+({c})|/√({a}²+{b}²)={num}/√{a*a+b*b}≈{ans:.1f}.", [f"{num:.1f}",f"{(num/(a*a+b*b)):.1f}",f"{ans+1:.0f}"], "Dùng công thức khoảng cách từ điểm đến đường thẳng.", family, diagram=coordinate_points({"P":[x,y],"L1":[-4,(-a*(-4)-c)/b] if b else [-c/a,-4],"L2":[4,(-a*4-c)/b] if b else [-c/a,4]},[["L1","L2"]],"Điểm P và đường thẳng được đặt theo đúng phương trình."))
    if family=="circle_equation":
        h,k=random.randint(-5,5),random.randint(-5,5); r=random.randint(2,9)
        return _q(f"Viết phương trình đường tròn tâm I({h};{k}), bán kính R={r}.", f"(x−({h}))²+(y−({k}))²={r*r}", f"Dạng chuẩn là (x−a)²+(y−b)²=R². Thay I({h};{k}), R={r} được (x−({h}))²+(y−({k}))²={r*r}.", [f"(x+{h})²+(y+{k})²={r}",f"(x−{h})²+(y−{k})²={2*r}",f"x²+y²={r*r}"], "Tâm là (a,b), nên trong ngoặc phải là x−a và y−b.", family, diagram=circle(r,(h,k),label="I"))
    if family in ("line_through_point","line_slope"):
        m=random.choice([-3,-2,-1,1,2,3]); x0,y0=random.randint(-4,4),random.randint(-4,4); b=y0-m*x0
        return _q(f"Tìm phương trình đường thẳng có hệ số góc {m} và đi qua P({x0};{y0}).", f"y={m}x{b:+d}", f"Dùng y−y₀=m(x−x₀): y−({y0})={m}(x−({x0})), suy ra y={m}x{b:+d}.", [f"y={-m}x{b:+d}",f"y={m}x{-b:+d}",f"y={x0}x{y0:+d}"], "Dùng dạng điểm-hệ số góc y−y₀=m(x−x₀).", family, diagram=coordinate_points({"P":[x0,y0],"Q":[x0+1,y0+m]},[["P","Q"]],"Đường thẳng đi qua điểm P với hệ số góc đã cho."))
    if family=="circle_tangent":
        h,k=random.randint(-3,3),random.randint(-3,3); r=random.randint(2,6); x=h+r
        return _q(f"Đường tròn (x−({h}))²+(y−({k}))²={r*r}. Viết tiếp tuyến tại điểm T({x};{k}) thuộc đường tròn.", f"x={x}", f"T nằm bên phải tâm I({h};{k}); bán kính IT nằm ngang, nên tiếp tuyến vuông góc IT là đường thẳng đứng x={x}.", [f"y={k}",f"x={h}",f"y={x}"], "Tiếp tuyến vuông góc với bán kính tại tiếp điểm.", family, "reasoning", diagram=circle_with_tangent(r,(h,k),center_label="I"))
    p=random.randint(1,5)
    return _q(f"Parabol y²={4*p}x có tiêu điểm nào?", f"F({p};0)", f"Dạng chuẩn y²=4px có tiêu điểm F(p;0). Ở đây p={p}, nên F({p};0).", [f"F(0;{p})",f"F(-{p};0)",f"F(0;{-p})"], "Nhận dạng dạng chuẩn của parabol có trục trùng Ox.", family, diagram=parabola_diagram(p))


def _g11_transform(level):
    family=random.choice(["translation","reflection","rotation"])
    x,y=random.randint(-6,6),random.randint(-6,6)
    if family=="translation":
        a,b=random.randint(-5,5),random.randint(-5,5)
        return _q(f"Phép tịnh tiến theo vectơ v=({a};{b}) biến điểm M({x};{y}) thành M'. Tìm M'.", f"({x+a}; {y+b})", f"Cộng vectơ tịnh tiến vào tọa độ điểm: M'=({x}+{a};{y}+{b})=({x+a};{y+b}).", [f"({x-a};{y-b})",f"({x+b};{y+a})",f"({-x-a};{-y-b})"], "Phép tịnh tiến cộng cùng một vectơ vào mọi điểm.", family, diagram=coordinate_points({"M":[x,y],"M′":[x+a,y+b]},[["M","M′"]],"Điểm gốc và ảnh sau phép tịnh tiến theo đúng vectơ."))
    if family=="reflection":
        axis=random.choice(["Ox","Oy","đường thẳng y=x"])
        ans=(x,-y) if axis=="Ox" else (-x,y) if axis=="Oy" else (y,x)
        return _q(f"Tìm ảnh của M({x};{y}) qua phép đối xứng trục {axis}.", f"({ans[0]}; {ans[1]})", f"Đối xứng qua {axis} biến M({x};{y}) thành M'({ans[0]};{ans[1]}).", [f"({-ans[0]};{-ans[1]})",f"({ans[1]};{ans[0]})",f"({x};{y})"], "Nhớ tọa độ nào đổi dấu hoặc hoán đổi khi đối xứng qua trục đã cho.", family, diagram=coordinate_points({"M":[x,y],"M′":[ans[0],ans[1]]},[["M","M′"]],"Điểm và ảnh qua phép đối xứng đã cho."))
    angle=random.choice([90,180,270]);
    ans=(-y,x) if angle==90 else (-x,-y) if angle==180 else (y,-x)
    return _q(f"Quay điểm M({x};{y}) quanh gốc O góc {angle}° ngược chiều kim đồng hồ. Tìm ảnh M'.", f"({ans[0]}; {ans[1]})", f"Quy tắc quay tâm O: {angle}° biến (x;y) thành ({ans[0]};{ans[1]}).", [f"({-ans[0]};{-ans[1]})",f"({y};{x})",f"({x};{y})"], "Dùng quy tắc tọa độ của phép quay tâm O.", family, diagram=coordinate_points({"O":[0,0],"M":[x,y],"M′":[ans[0],ans[1]]},[["O","M"],["O","M′"]],"Điểm và ảnh sau phép quay quanh gốc O."))


def _g11_space(level):
    family=random.choice(["parallel_planes","line_plane_angle","pyramid_section","perpendicular_distance","space_reasoning"] if level=="hard" else ["parallel_planes","line_plane_angle","pyramid_section","line_plane_position"] if level=="medium" else ["parallel_planes","line_plane_position","cube_diagonal"])
    if family=="parallel_planes":
        return _q("Cho hình lập phương ABCD.A'B'C'D'. Hai mặt phẳng (ABCD) và (A'B'C'D') có quan hệ gì?", "Song song", "Hai mặt phẳng là hai mặt đáy đối diện của hình lập phương; chúng không cắt nhau nên song song.", ["Vuông góc", "Trùng nhau", "Cắt nhau theo đường AC"], "Xét hai mặt đáy đối diện của hình lập phương.", family, "knowledge", diagram=cube_projection())
    if family=="line_plane_position":
        return _q("Trong hình lập phương ABCD.A'B'C'D', đường thẳng AB và mặt phẳng (A'B'C'D') có quan hệ gì?", "Song song", "AB nằm trong mặt đáy dưới, còn (A'B'C'D') là mặt đáy trên song song với đáy dưới; do đó AB song song với mặt phẳng này.", ["Vuông góc", "Nằm trong mặt phẳng", "Cắt mặt phẳng tại A'"], "Một đường thẳng nằm trong mặt phẳng song song với mặt phẳng kia sẽ song song với mặt phẳng đó.", family, "knowledge", diagram=cube_projection())
    if family=="cube_diagonal":
        a=random.randint(2,10); d=a*math.sqrt(3)
        return _q(f"Hình lập phương cạnh {a} cm. Độ dài đường chéo không gian bằng bao nhiêu?", f"{a}√3", f"Đường chéo không gian d=√(a²+a²+a²)=a√3={a}√3 cm.", [f"{a}√2",str(3*a),f"{2*a}√2"], "Đường chéo không gian có bình phương bằng tổng bình phương ba cạnh vuông góc.", family, diagram=cube_projection(a,True,True))
    if family=="line_plane_angle":
        a=random.choice([3,4,5,6,8]); h=random.choice([3,4,5,7]); hyp=math.sqrt(a*a+h*h); sinang=h/hyp
        return _q(f"Một đoạn thẳng nối điểm P ở ngoài mặt phẳng (α) với hình chiếu H của P trên (α), có PH={h} cm. Điểm A nằm trên (α), HA={a} cm và PA là cạnh huyền của tam giác PHA. Viết sin của góc giữa PA và (α).", f"{h}/√({a*a+h*h})", f"Góc giữa PA và mặt phẳng là góc PAH. Trong tam giác vuông PHA, sin∠PAH=PH/PA={h}/√({h}²+{a}²)={h}/√({h*h+a*a}).", [f"{a}/√({a*a+h*h})",f"{h}/{a}","1"], "Góc giữa đường thẳng và mặt phẳng là góc giữa đường thẳng và hình chiếu của nó.", family, "reasoning", diagram=triangle_with_base_height(a,h))
    if family=="pyramid_section":
        return _q("Trong hình chóp S.ABCD có đáy ABCD là hình bình hành. Gọi M, N lần lượt là trung điểm SA, SB. Giao tuyến của mặt phẳng (CMN) với mặt phẳng đáy (ABCD) đi qua điểm nào chắc chắn?", "Điểm C", "Điểm C thuộc cả mặt phẳng (CMN) lẫn mặt phẳng đáy (ABCD), nên C thuộc giao tuyến của hai mặt phẳng.", ["Điểm S", "Trung điểm AB", "Không có điểm chung"], "Giao tuyến chứa mọi điểm chung của hai mặt phẳng.", family, "reasoning", diagram=pyramid_projection())
    # distance / reasoning from cube diagonal
    a=random.randint(2,8)
    return _q(f"Trong hình lập phương cạnh {a} cm, khoảng cách giữa hai mặt phẳng đáy đối diện bằng bao nhiêu?", a, f"Hai đáy đối diện song song; khoảng cách giữa chúng bằng cạnh vuông góc nối hai đáy, tức {a} cm.", [2*a, f"{a}√2", f"{a}√3"], "Khoảng cách giữa hai mặt phẳng song song là độ dài đoạn vuông góc chung.", family, diagram=cube_projection(a,True))


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



def _g10_circle(level, game_id=""):
    """Circle geometry bank, including inscribed rectangles and triangles."""
    mode = _game_mode(game_id)
    if mode == "angle":
        family = random.choice(["circle_angle", "inscribed_triangle_angle", "inscribed_triangle_diameter"])
    elif mode == "length":
        family = random.choice(["circle_center_radius", "circle_intersection", "inscribed_rectangle_diagonal"])
    elif mode == "application":
        family = random.choice(["circle_tangent", "inscribed_rectangle_diagonal", "rectangle_max_area", "inscribed_triangle_diameter", "external_tangents"])
    else:
        pools = {
            "easy": ["circle_equation", "circle_center_radius", "circle_angle", "inscribed_triangle_angle", "inscribed_triangle_diameter", "inscribed_rectangle_diagonal"],
            "medium": ["circle_equation", "circle_center_radius", "circle_tangent", "circle_intersection", "inscribed_triangle_angle", "inscribed_rectangle_diagonal"],
            "hard": ["circle_tangent", "circle_intersection", "inscribed_triangle_angle", "inscribed_triangle_diameter", "inscribed_rectangle_diagonal", "rectangle_max_area", "external_tangents"],
        }
        family = random.choice(pools.get(level, pools["medium"]))

    if family == "external_tangents":
        r = random.choice([1, 2, 3])
        # P=(2r,0); tangent points have x=r/2 and y=±sqrt(3)r/2.
        answer = "3√3/4" if r == 1 else ("3√3" if r == 2 else "27√3/4")
        tangent_length = f"{r}√3"
        return _q(
            f"Đường tròn tâm O bán kính {r} cm có P nằm ngoài đường tròn và OP={2*r} cm. Từ P kẻ hai tiếp tuyến PA, PB tại A, B. Tính diện tích tam giác PAB.",
            answer,
            f"Bước 1: OA vuông góc PA và OB vuông góc PB. Trong tam giác vuông OAP, PA=√(OP²−OA²)=√(({2*r})²−{r}²)={tangent_length} cm. Bước 2: Dây tiếp điểm AB vuông góc OP và có nửa dây bằng r√3/2, nên AB=r√3 cm. Bước 3: Khoảng cách từ P đến AB là OP−r/2=3r/2 cm. Vậy S=AB·(3r/2)/2=3√3·{r*r}/4={answer} cm².",
            [f"{r*r}√3/2", f"{r}√3", f"{3*r*r}√3/2"],
            "Dùng tam giác vuông OAP để tìm tiếp tuyến, rồi khai thác dây tiếp điểm AB.",
            family, "proof", diagram=external_tangents_to_circle(r))

    if family == "circle_angle":
        central = random.choice([40, 60, 80, 90, 100, 120, 140, 160])
        inscribed = central // 2
        return _q(f"Trên đường tròn (O), góc ở tâm AOB chắn cung AB bằng {central}°. Điểm C nằm trên đường tròn ở phía thích hợp. Tính góc nội tiếp ACB cùng chắn cung AB.", inscribed,
                  f"Góc nội tiếp cùng chắn một cung bằng nửa góc ở tâm: ∠ACB = {central}°/2 = {inscribed}°.", [central, max(0, central-30), min(180, central+20)], "Góc nội tiếp cùng chắn cung bằng một nửa góc ở tâm.", family, "reasoning", diagram=circle_with_central_angle(central))

    if family == "inscribed_triangle_angle":
        other = random.choice([30, 35, 40, 45, 50, 55, 60, 65])
        known = random.choice([40, 50, 60, 70, 80])
        missing = 180 - other - known
        return _q(f"Tam giác ABC nội tiếp đường tròn (O). Biết ∠A={known}° và ∠B={other}°. Tính ∠C.", missing,
                  f"Tổng ba góc trong tam giác bằng 180°. Vì vậy ∠C=180°−{known}°−{other}°={missing}°. Ba đỉnh A, B, C cùng nằm trên đường tròn.", [known+other, 180-known, abs(known-other)], "Dùng tổng ba góc tam giác; điều kiện nội tiếp cho biết cả ba đỉnh nằm trên đường tròn.", family, "reasoning", diagram=inscribed_triangle_by_angles(known,other))

    if family == "inscribed_triangle_diameter":
        a, b, c = random.choice([(3,4,5),(5,12,13),(8,15,17),(7,24,25)])
        scale = random.randint(1, 3 if level != "hard" else 5)
        a, b, c = a*scale, b*scale, c*scale
        if random.choice([True, False]): a, b = b, a
        return _q(f"Tam giác ABC nội tiếp đường tròn có AB là đường kính. Biết AC={a} cm và BC={b} cm. Tính đường kính AB.", c,
                  f"Vì AB là đường kính nên ∠ACB=90° (định lý Thales). Theo Pythagore: AB²=AC²+BC²={a}²+{b}²={a*a+b*b}={c}², do đó AB={c} cm.", [a+b, abs(a-b), c*c], "Góc nội tiếp chắn nửa đường tròn là góc vuông, sau đó áp dụng định lý Pythagore.", family, "multi_step", diagram=inscribed_right_triangle(a,b,c))

    if family == "inscribed_rectangle_diagonal":
        a, b, c = random.choice([(3,4,5),(5,12,13),(8,15,17),(7,24,25),(9,12,15)])
        scale = random.randint(1, 3 if level != "hard" else 4)
        width, height, diagonal = a*scale, b*scale, c*scale
        radius = diagonal/2
        if level == "easy":
            ask_area = random.choice([True, False])
            if ask_area:
                answer = width*height
                question = f"Hình chữ nhật ABCD nội tiếp đường tròn (O), có hai cạnh kề dài {width} cm và {height} cm. Tính diện tích hình chữ nhật."
                solution = f"Diện tích hình chữ nhật S=AB·BC={width}·{height}={answer} cm². Vì ABCD nội tiếp đường tròn nên hai đường chéo bằng nhau và cùng là đường kính."
                distractors = [2*(width+height), width+height, width*height+2]
                family = "inscribed_rectangle_area"
            else:
                answer = diagonal
                question = f"Hình chữ nhật ABCD nội tiếp đường tròn bán kính {radius:g} cm. Tính độ dài đường chéo AC."
                solution = f"Đường chéo AC của hình chữ nhật nội tiếp đi qua hai điểm trên đường tròn và là đường kính, nên AC=2R=2·{radius:g}={diagonal} cm."
                distractors = [radius, 2*radius+2, diagonal*2]
                family = "inscribed_rectangle_diagonal"
        else:
            answer = diagonal
            question = f"Hình chữ nhật ABCD nội tiếp đường tròn tâm O bán kính {radius:g} cm. Biết AB={width} cm. Tính cạnh BC, biết các số liệu được chọn sao cho kết quả nguyên dương."
            solution = f"Đường chéo AC là đường kính nên AC=2R={diagonal} cm. Theo Pythagore, BC²=AC²−AB²={diagonal}²−{width}²={diagonal*diagonal-width*width}={height}², suy ra BC={height} cm."
            answer = height
            distractors = [width, diagonal, width+height]
            family = "inscribed_rectangle_diagonal"
        return _q(question, answer, solution, distractors, "Đường chéo hình chữ nhật nội tiếp đường tròn chính là đường kính; kết hợp định lý Pythagore khi cần.", family, "multi_step", diagram=inscribed_rectangle(width/2, height/2, diagonal/2))

    if family == "rectangle_max_area":
        r = random.randint(3, 12)
        area = 2*r*r
        return _q(f"Một hình chữ nhật nội tiếp đường tròn bán kính {r} cm. Diện tích lớn nhất có thể đạt được là bao nhiêu?",
                  area, f"Đường chéo hình chữ nhật bằng đường kính 2{r} cm. Với hai cạnh x,y, ta có x²+y²=(2{r})². Do (x−y)²≥0 nên 2xy≤x²+y²=4·{r}², suy ra S=xy≤2·{r}²={area} cm². Dấu bằng khi x=y, tức hình chữ nhật là hình vuông.",
                  [math.pi*r*r, 4*r*r, r*r], "Dùng đường chéo cố định và bất đẳng thức (x−y)²≥0. Dấu bằng xảy ra khi hình chữ nhật là hình vuông.", family, "proof", diagram=inscribed_square(r))

    h,k=random.randint(-5,5),random.randint(-5,5); r=random.randint(2,9)
    if family=="circle_center_radius":
        return _q(f"Đường tròn có phương trình ({_shifted('x',h)})²+({_shifted('y',k)})²={r*r}. Xác định tâm và bán kính.", f"I({h};{k}), R={r}", f"So sánh với (x−a)²+(y−b)²=R². Suy ra tâm I({h};{k}) và R=√{r*r}={r}.", [f"I({-h};{-k}), R={r*r}",f"I({h};{k}), R={r*r}",f"I({k};{h}), R={r}"], "Đọc tâm từ hai biểu thức bình phương và lấy căn bậc hai vế phải.", family, diagram=circle(r,(h,k),label="I"))
    if family=="circle_tangent":
        x=h+r
        return _q(f"Cho đường tròn tâm I({h};{k}), bán kính {r}. Viết phương trình tiếp tuyến tại điểm T({x};{k}).", f"x={x}", f"IT nằm ngang và T là điểm ngoài cùng bên phải của đường tròn; tiếp tuyến vuông góc IT nên có phương trình x={x}.", [f"y={k}",f"x={h}",f"y={x}"], "Tiếp tuyến vuông góc với bán kính tại tiếp điểm.", family, "reasoning", diagram=circle_with_tangent(r,(h,k),center_label="I"))
    if family=="circle_intersection":
        return _q(f"Đường tròn (C): ({_shifted('x',h)})²+({_shifted('y',k)})²={r*r}. Đường thẳng y={k} cắt (C) tại hai điểm. Khoảng cách giữa hai giao điểm bằng bao nhiêu?", 2*r, f"Đường thẳng y={k} đi qua tâm, nên dây giao tuyến là đường kính. Độ dài bằng 2R=2·{r}={2*r}.", [r, r*r, 4*r], "Đường thẳng đi qua tâm cắt đường tròn theo một đường kính.", family, diagram=circle_with_diameter(r,(h,k),center_label="I"))
    return _q(f"Viết phương trình đường tròn tâm I({h};{k}) bán kính {r}.", f"({_shifted('x',h)})²+({_shifted('y',k)})²={r*r}", f"Dạng chuẩn: (x−a)²+(y−b)²=R². Thay tâm I({h};{k}), R={r} được phương trình yêu cầu.", [f"(x+{h})²+(y+{k})²={r}",f"(x−{h})²+(y−{k})²={2*r}",f"x²+y²={r*r}"], "Tâm I(a;b) cho các hạng x−a, y−b; vế phải là R².", family, diagram=circle(r,(h,k),label="I"))


def _g12_sphere(level):
    family=random.choice(["sphere_equation", "sphere_center_radius", "sphere_point_check"] if level=="hard" else ["sphere_equation", "sphere_center_radius"] if level=="medium" else ["sphere_center_radius", "sphere_equation"])
    a,b,c=[random.randint(-4,4) for _ in range(3)]; r=random.randint(2,8)
    if family=="sphere_center_radius":
        return _q(f"Cho mặt cầu (x−({a}))²+(y−({b}))²+(z−({c}))²={r*r}. Xác định tâm và bán kính.", f"I({a};{b};{c}), R={r}", f"So sánh với dạng (x−a)²+(y−b)²+(z−c)²=R². Tâm là I({a};{b};{c}), bán kính R=√{r*r}={r}.", [f"I({-a};{-b};{-c}), R={r*r}",f"I({a};{b};{c}), R={r*r}",f"I({b};{a};{c}), R={r}"], "Tọa độ tâm xuất hiện trong các bình phương; bán kính là căn bậc hai vế phải.", family, diagram=sphere_projection(r,(a,b,c),center_label="I"))
    if family=="sphere_point_check":
        x,y,z=a+r,b,c
        return _q(f"Mặt cầu tâm I({a};{b};{c}) bán kính {r}. Điểm P({x};{y};{z}) có thuộc mặt cầu không?", "Có", f"IP²=({x}−({a}))²+({y}−({b}))²+({z}−({c}))²={r*r}=R², nên P thuộc mặt cầu.", ["Không", "Chỉ khi I là gốc tọa độ", "Không đủ dữ kiện"], "Điểm thuộc mặt cầu khi khoảng cách đến tâm bằng bán kính.", family, "reasoning", diagram=sphere_projection(r,(a,b,c),center_label="I"))
    return _q(f"Viết phương trình mặt cầu tâm I({a};{b};{c}) bán kính {r}.", f"({_shifted('x',a)})²+({_shifted('y',b)})²+({_shifted('z',c)})²={r*r}", f"Dùng dạng chuẩn (x−a)²+(y−b)²+(z−c)²=R². Thay tâm và bán kính đã cho ta được phương trình yêu cầu.", [f"(x+{a})²+(y+{b})²+(z+{c})²={r}",f"x²+y²+z²={r*r}",f"({_shifted('x',a)})²+({_shifted('y',b)})²+({_shifted('z',c)})²={2*r}"], "Dạng chuẩn của mặt cầu trong Oxyz.", family, diagram=sphere_projection(r,(a,b,c),center_label="I"))

def _g12_volume(level):
    family=random.choice(["pyramid_volume", "cylinder_volume", "sphere_surface", "cone_volume"] if level=="hard" else ["pyramid_volume", "cylinder_volume", "sphere_volume"] if level=="medium" else ["cube_volume", "cylinder_volume", "sphere_volume"])
    if family=="cube_volume":
        a=random.randint(2,12); return _q(f"Một hình lập phương cạnh {a} cm có thể tích bao nhiêu?", a**3, f"V=a³={a}³={a**3} cm³.", [6*a*a, 3*a*a, a*a], "Thể tích hình lập phương bằng lập phương độ dài cạnh.", family, diagram=cube_projection(a,True))
    if family=="cylinder_volume":
        r=random.randint(2,8); h=random.randint(3,12); return _q(f"Một hình trụ có bán kính đáy {r} cm và chiều cao {h} cm. Tính thể tích theo π.", f"{r*r*h}π", f"V=πr²h=π·{r}²·{h}={r*r*h}π cm³.", [f"{2*r*h}π",f"{r*h}π",f"{r*r+h}π"], "Lấy diện tích đáy nhân chiều cao.", family, diagram=cylinder_projection(r,h))
    if family in ("sphere_volume","sphere_surface"):
        r=random.randint(2,8)
        if family=="sphere_surface": return _q(f"Mặt cầu bán kính {r} cm có diện tích mặt cầu bằng bao nhiêu theo π?", f"{4*r*r}π", f"S=4πr²=4π·{r}²={4*r*r}π cm².", [f"{r*r}π",f"{2*r}π",f"{4*r*r*r}π"], "Diện tích mặt cầu là 4πR².", family, diagram=sphere_projection(r))
        return _q(f"Khối cầu bán kính {r} cm có thể tích bằng bao nhiêu theo π?", f"{_fmt_fraction(4*r**3,3)}π", f"V=4/3·πr³=4/3·π·{r}³={_fmt_fraction(4*r**3,3)}π cm³.", [f"{4*r*r}π",f"{r*r*r}π",f"{2*r**3}π"], "Thể tích khối cầu là 4πR³/3.", family, diagram=sphere_projection(r))
    if family=="pyramid_volume":
        area=random.choice([12,18,24,30,36,48]); h=random.choice([3,6,9,12]); ans=Fraction(area*h,3)
        return _q(f"Một hình chóp có diện tích đáy {area} cm² và chiều cao {h} cm. Tính thể tích.", _fmt_fraction(ans.numerator,ans.denominator), f"V=1/3·Sđáy·h=1/3·{area}·{h}={_fmt_fraction(ans.numerator,ans.denominator)} cm³.", [area*h, _fmt_fraction(area*h,2), area+h], "Thể tích hình chóp bằng một phần ba tích diện tích đáy và chiều cao.", family, diagram=pyramid_projection())
    r=random.randint(2,7); h=random.randint(3,12)
    return _q(f"Một hình nón có bán kính đáy {r} cm và chiều cao {h} cm. Viết thể tích theo π.", f"{_fmt_fraction(r*r*h,3)}π", f"V=1/3·πr²h=1/3·π·{r}²·{h}={_fmt_fraction(r*r*h,3)}π cm³.", [f"{r*r*h}π",f"{2*r*h}π",f"{r*h}π"], "Thể tích hình nón bằng một phần ba thể tích hình trụ cùng đáy và chiều cao.", family, diagram=cone_projection(r,h))

def _graph_question(level):
    """Function/coordinate graph questions always include a data-bound plot."""
    if level == "easy":
        m = random.choice([-3, -2, -1, 1, 2, 3]); b = random.randint(-4, 4); x = random.choice([-2, -1, 1, 2])
        y = m*x+b; diagram = line_graph(m, b, (-5, 5), (-10, 10))
        return _q(f"Cho hàm số y={m}x{b:+d}. Dựa vào đồ thị, xác định tung độ điểm thuộc đồ thị có hoành độ x={x}.", y, f"Thay x={x} vào hàm số: y={m}·({x}){b:+d}={y}.", [y+2, y-2, m+b], "Tìm vị trí x trên trục hoành rồi đọc giá trị y trên đường thẳng.", "line_graph_reading", diagram=diagram)
    if level == "medium":
        a = random.choice([-2, -1, 1, 2]); h = random.randint(-2, 2); k = random.randint(-3, 3)
        # y=a(x-h)^2+k, expanded coefficients are used for the prompt.
        b = -2*a*h; c = a*h*h+k; diagram = quadratic_graph(a, b, c, (-5, 5), (-8, 10))
        return _q(f"Đồ thị hàm số y={a}(x{(-h):+d})²{ k:+d} có đỉnh I(h;k). Xác định tọa độ đỉnh I.", f"({h}; {k})", f"Dạng đỉnh y=a(x−h)²+k cho đỉnh I(h;k), do đó I({h}; {k}).", [f"({-h}; {k})", f"({h}; {-k})", f"({k}; {h})"], "Đọc hoành độ và tung độ đỉnh từ dạng y=a(x−h)²+k.", "quadratic_graph_vertex", diagram=diagram)
    a = random.choice([-2, -1, 1, 2]); b = random.randint(-3, 3); c = random.randint(-3, 3)
    diagram = quadratic_graph(a, b, c, (-5, 5), (-10, 10))
    xv = -b/(2*a); yv = a*xv*xv+b*xv+c
    return _q(f"Cho đồ thị parabol y={a}x²{b:+d}x{c:+d}. Tính tung độ đỉnh.", _fmt(yv), f"Hoành độ đỉnh xI=−b/(2a)=−({b})/(2·{a})={_fmt(xv)}. Thay vào hàm số được yI={_fmt(yv)}.", [_fmt(yv+1), _fmt(yv-1), _fmt(c)], "Tìm x đỉnh bằng −b/(2a), sau đó thay vào hàm số.", "quadratic_graph_extremum", diagram=diagram)


def _olympic_extension(kind, grade):
    """Expert-tier tasks require a distinct proof or parameter strategy."""
    if kind == "circle":
        return _q("Hai dây AB và CD của một đường tròn cắt nhau tại P bên trong đường tròn. Biết PA=x, PB=x+5, PC=6 và PD=6. Tìm x>0.", 4,
                  "Theo định lý hai dây cắt nhau: PA·PB=PC·PD, nên x(x+5)=36. Suy ra x²+5x−36=0=(x+9)(x−4). Vì x>0 nên x=4.",
                  [3, 5, 9], "Dùng định lý hai dây cắt nhau, giải phương trình rồi loại nghiệm không dương.", "olympic_circle_power", "proof_reasoning")
    if kind in {"triangle", "plane"}:
        return _q("Một tam giác có ba cạnh 13, 14, 15. Tính diện tích tam giác bằng công thức Heron.", 84,
                  "Nửa chu vi p=(13+14+15)/2=21. Theo Heron, S=√(p(p−13)(p−14)(p−15))=√(21·8·7·6)=√7056=84.",
                  [42, 72, 96], "Tính nửa chu vi trước rồi mới thay vào công thức Heron.", "olympic_triangle_heron", "multi_step", diagram=triangle_from_sides(13, 14, 15))
    if kind in {"coordinate", "line2d"}:
        return _q("Tìm tất cả tung độ gốc b để đường thẳng y=2x+b tiếp xúc với đường tròn x²+y²=1.", "b=±√5",
                  "Viết đường thẳng 2x−y+b=0. Khoảng cách từ tâm O(0,0) đến đường thẳng phải bằng bán kính 1: |b|/√(2²+(-1)²)=1. Do đó |b|=√5, suy ra b=±√5.",
                  ["b=±2", "b=±1", "b=5"], "Điều kiện tiếp xúc là khoảng cách từ tâm đường tròn đến đường thẳng bằng bán kính.", "olympic_circle_tangent_parameter", "proof_reasoning")
    if kind == "graph":
        return _q("Biện luận theo m số nghiệm thực phân biệt của phương trình x²−2mx+m+2=0.", "m<−1 hoặc m>2",
                  "Δ/4=m²−(m+2)=m²−m−2=(m−2)(m+1). Phương trình có hai nghiệm thực phân biệt khi Δ>0, tức (m−2)(m+1)>0. Suy ra m<−1 hoặc m>2.",
                  ["−1<m<2", "m=−1 hoặc m=2", "mọi m thực"], "Tính biệt thức rồi giải bất phương trình tích theo tham số.", "olympic_parameter_quadratic", "proof_reasoning")
    if kind == "space12":
        return _q("Trong Oxyz, cho A(1;−2;3) và mặt phẳng (P): 2x−y+2z−9=0. Tính khoảng cách từ A đến (P).", "1/3",
                  "d=|2·1−(−2)+2·3−9|/√(2²+(−1)²+2²)=|1|/3=1/3.",
                  ["2/3", "1", "2"], "Dùng công thức khoảng cách từ điểm đến mặt phẳng.", "olympic_space_distance", "multi_step")
    return None


def _g10_coordinate_midpoint_topic(level: str):
    """Dedicated topic bank: midpoint, point distance, section ratio and olympiad extensions."""
    level = level if level in {"easy", "medium", "hard", "expert", "hell"} else "easy"
    if level == "easy":
        family = random.choice(["midpoint", "distance_points", "recover_endpoint", "midpoint_axis"])
    elif level in {"medium", "hard"}:
        family = random.choice(["distance_points", "recover_endpoint", "section_ratio", "distance_compare", "midpoint_parameter"])
    else:
        family = random.choice(["distance_locus", "midpoint_parameter", "section_ratio_proof", "parallelogram_midpoint", "distance_sum_parameter"])
    ax, ay = random.randint(-7, 7), random.randint(-7, 7)
    bx, by = random.randint(-7, 7), random.randint(-7, 7)
    while (ax, ay) == (bx, by):
        bx, by = random.randint(-7, 7), random.randint(-7, 7)
    dx, dy = bx-ax, by-ay
    d2 = dx*dx + dy*dy
    dist = math.sqrt(d2)
    if family == "midpoint":
        mx, my = Fraction(ax+bx,2), Fraction(ay+by,2)
        ans = f"({_fmt_fraction(mx.numerator,mx.denominator)}; {_fmt_fraction(my.numerator,my.denominator)})"
        return _q(f"Trong mặt phẳng tọa độ, cho A({ax}; {ay}), B({bx}; {by}). Tìm tọa độ trung điểm M của AB.", ans,
                  f"M=((x_A+x_B)/2;(y_A+y_B)/2)=(({ax}+{bx})/2;({ay}+{by})/2)=({ _fmt_fraction(mx.numerator,mx.denominator)};{_fmt_fraction(my.numerator,my.denominator)}).",
                  [f"({ax+bx}; {ay+by})",f"({ax-bx}; {ay-by})",f"({bx}; {ay})"], "Tính trung bình cộng hai hoành độ và hai tung độ riêng biệt.", family,
                  diagram=coordinate_points({"A":[ax,ay],"B":[bx,by],"M":[float(mx),float(my)]},[["A","B"],["A","M"],["M","B"]],"M là trung điểm của đoạn AB."))
    if family == "distance_points":
        return _q(f"Cho A({ax}; {ay}), B({bx}; {by}). Tính độ dài AB.", f"√{d2}" if int(math.isqrt(d2))**2 != d2 else str(math.isqrt(d2)),
                  f"AB=√[({bx}−({ax}))²+({by}−({ay}))²]=√({dx*dx}+{dy*dy})=√{d2}"+(f"={math.isqrt(d2)}" if int(math.isqrt(d2))**2==d2 else ""),
                  [str(abs(dx)+abs(dy)),str(d2),f"√{abs(dx*dx-dy*dy)}"], "Lấy hiệu hoành độ và tung độ, bình phương rồi cộng lại.", family,
                  diagram=coordinate_points({"A":[ax,ay],"B":[bx,by]},[["A","B"]],"Hai điểm được đặt đúng theo tọa độ đã cho."))
    if family == "recover_endpoint":
        mx,my=Fraction(ax+bx,2),Fraction(ay+by,2)
        cx,cy=2*mx-ax,2*my-ay
        ans=f"({ _fmt_fraction(cx.numerator,cx.denominator)}; {_fmt_fraction(cy.numerator,cy.denominator)})"
        return _q(f"M({ _fmt_fraction(mx.numerator,mx.denominator)}; {_fmt_fraction(my.numerator,my.denominator)}) là trung điểm AB. Biết A({ax}; {ay}), tìm B.",ans,
                  f"x_B=2x_M−x_A=2·{_fmt_fraction(mx.numerator,mx.denominator)}−({ax})={_fmt_fraction(cx.numerator,cx.denominator)}; y_B=2y_M−y_A=2·{_fmt_fraction(my.numerator,my.denominator)}−({ay})={_fmt_fraction(cy.numerator,cy.denominator)}.",
                  [f"({ax+bx}; {ay+by})",f"({ax-bx}; {ay-by})",f"({bx}; {ay})"],"Dùng tính chất trung điểm theo từng tọa độ.",family,
                  diagram=coordinate_points({"A":[ax,ay],"M":[float(mx),float(my)],"B":[float(cx),float(cy)]},[["A","B"],["A","M"],["M","B"]],"M là trung điểm của AB."))
    if family == "midpoint_axis":
        # Choose a point B so midpoint lies on the y-axis, then solve x_A.
        x_b=random.randint(1,8); x_a=-x_b; y_a=random.randint(-5,5); y_b=random.randint(-5,5)
        ans=str(x_a)
        return _q(f"A(m; {y_a}) và B({x_b}; {y_b}) có trung điểm nằm trên trục Oy. Tìm m.",ans,
                  f"Hoành độ trung điểm là (m+{x_b})/2. Vì trung điểm thuộc Oy nên (m+{x_b})/2=0, suy ra m=−{x_b}.",
                  [str(x_b),str(-2*x_b),"0"],"Điểm thuộc trục Oy có hoành độ bằng 0.",family)
    if family == "section_ratio":
        m,n=random.choice([(1,2),(2,1),(2,3),(3,2)])
        # AP:PB = m:n => P=(n*A + m*B)/(m+n)
        px=Fraction(n*ax+m*bx,m+n); py=Fraction(n*ay+m*by,m+n)
        ans=f"({_fmt_fraction(px.numerator,px.denominator)}; {_fmt_fraction(py.numerator,py.denominator)})"
        return _q(f"Cho A({ax}; {ay}), B({bx}; {by}). Điểm P chia đoạn AB trong tỉ số AP:PB={m}:{n}. Tìm P.",ans,
                  f"P=((n·x_A+m·x_B)/(m+n);(n·y_A+m·y_B)/(m+n))=(({n}·{ax}+{m}·{bx})/{m+n};({n}·{ay}+{m}·{by})/{m+n})=({ _fmt_fraction(px.numerator,px.denominator)};{_fmt_fraction(py.numerator,py.denominator)}).",
                  [f"({ax+bx}; {ay+by})",f"({_fmt_fraction(Fraction(ax+bx,2).numerator,Fraction(ax+bx,2).denominator)}; {_fmt_fraction(Fraction(ay+by,2).numerator,Fraction(ay+by,2).denominator)})",f"({bx-ax}; {by-ay})"],"Áp dụng công thức chia đoạn theo tỉ số AP:PB.",family,
                  diagram=coordinate_points({"A":[ax,ay],"B":[bx,by],"P":[float(px),float(py)]},[["A","B"],["A","P"],["P","B"]],"P chia AB theo tỉ số đã cho."))
    if family == "distance_compare":
        cx,cy=random.randint(-5,5),random.randint(-5,5)
        da=(cx-ax)**2+(cy-ay)**2; db=(cx-bx)**2+(cy-by)**2
        ans="CA=CB" if da==db else ("CA<CB" if da<db else "CA>CB")
        return _q(f"Cho A({ax}; {ay}), B({bx}; {by}), C({cx}; {cy}). So sánh CA và CB.",ans,
                  f"CA²=({cx}−{ax})²+({cy}−{ay})²={da}; CB²=({cx}−{bx})²+({cy}−{by})²={db}. So sánh hai bình phương không âm suy ra {ans}.",
                  ["CA=CB" if ans!="CA=CB" else "CA<CB","CA>CB" if ans!="CA>CB" else "CA<CB","Không đủ dữ kiện"],"Tính bình phương hai khoảng cách để tránh căn thức.",family,
                  diagram=coordinate_points({"A":[ax,ay],"B":[bx,by],"C":[cx,cy]},[["C","A"],["C","B"]],"So sánh khoảng cách từ C đến A và B."))
    if family == "midpoint_parameter":
        k=random.randint(-5,5); target=random.randint(-4,4)
        ans=str(2*target-k)
        return _q(f"A(m; {ay}), B({k}; {by}) có trung điểm M thuộc đường thẳng x={target}. Tìm m.",ans,
                  f"Hoành độ trung điểm là (m+{k})/2. Vì M thuộc x={target}, ta có (m+{k})/2={target}, suy ra m={ans}.",
                  [str(k-2*target),str(target-k),str(2*target+k)],"Điều kiện M thuộc đường thẳng x=c quy về hoành độ trung điểm bằng c.",family)
    if family == "distance_locus":
        r=random.randint(2,8); h,k=random.randint(-3,3),random.randint(-3,3)
        ans=f"(x−({h}))²+(y−({k}))²={r*r}"
        return _q(f"Tìm phương trình tập hợp các điểm M(x;y) cách điểm I({h}; {k}) một khoảng {r}.",ans,
                  f"Điều kiện MI={r} tương đương √((x−{h})²+(y−{k})²)={r}. Bình phương hai vế được (x−({h}))²+(y−({k}))²={r*r}.",
                  [f"(x+{h})²+(y+{k})²={r}",f"(x−({h}))²+(y−({k}))²={r}",f"x²+y²={r*r}"],"Tập hợp điểm cách một điểm cố định R là đường tròn tâm I, bán kính R.",family,
                  diagram=circle(r,(h,k),label="I"))
    if family == "section_ratio_proof":
        return _q("Cho A(x₁;y₁), B(x₂;y₂). Chứng minh trung điểm M của AB không phụ thuộc vào cách chọn hệ trục tọa độ?", "Không; tọa độ phụ thuộc hệ trục, còn điểm hình học M thì không đổi",
                  "Khi đổi hệ trục, các tọa độ của A, B và M có thể thay đổi. Tuy nhiên, định nghĩa hình học M là điểm nằm trên AB và MA=MB không phụ thuộc hệ tọa độ.",
                  ["Có; cả điểm M và tọa độ đều luôn giữ nguyên", "M luôn là gốc tọa độ", "Không thể xác định trung điểm"],"Phân biệt điểm hình học với tọa độ của điểm.",family,"proof_reasoning")
    if family == "parallelogram_midpoint":
        ax,ay=0,0; bx,by=random.randint(2,8),random.randint(-4,4); dx,dy=random.randint(-4,4),random.randint(2,8); cx,cy=bx+dx,by+dy
        ans=f"({bx+dx}; {by+dy})"
        return _q(f"Trong hình bình hành ABCD, A({ax};{ay}), B({bx};{by}), D({dx};{dy}). Tìm tọa độ C.",ans,
                  f"Trong hình bình hành, vectơ AC=AB+AD nên C=B+D−A=({bx}+{dx};{by}+{dy})=({bx+dx};{by+dy}).",
                  [f"({bx-dx}; {by-dy})",f"({dx-bx}; {dy-by})",f"({bx}; {dy})"],"Dùng quy tắc hình bình hành theo tọa độ.",family,"multi_step",
                  diagram=coordinate_points({"A":[ax,ay],"B":[bx,by],"D":[dx,dy],"C":[cx,cy]},[["A","B"],["B","C"],["C","D"],["D","A"]],"Hình bình hành được dựng từ ba đỉnh đã cho."))
    # National-level parameterized sum of squared distances; use a correct minimizer.
    x0,y0=random.randint(-4,4),random.randint(-4,4)
    ans=f"({x0}; {y0+1})"
    return _q(f"Với A({x0-2};{y0}), B({x0+2};{y0}), C({x0};{y0+3}), tìm điểm M làm tổng MA²+MB²+MC² nhỏ nhất.",ans,
              f"Tổng bình phương khoảng cách đến các điểm cố định đạt cực tiểu tại trọng tâm G. G=(({x0-2}+{x0+2}+{x0})/3;({y0}+{y0}+{y0+3})/3)=({x0};{y0+1}).",
              [f"({x0}; {y0+1})",f"({x0+1}; {y0})",f"({x0-1}; {y0+1})"],"Dùng đẳng thức tổng bình phương khoảng cách và trọng tâm của ba điểm.",family,"olympiad_reasoning")


def _generate_geometry_question(grade: int, topic_id: str, difficulty: str, game_id: str | None = None):
    """Return an original geometry question, or None for a non-geometry topic."""
    t=(topic_id or "").lower()
    g=int(grade or 10)
    if t == "g10_geom_coordinate_distance_midpoint":
        return _g10_coordinate_midpoint_topic(difficulty)
    aliases={
      "hinh_hoc_co_ban_10":"plane", "tam_giac_tu_giac_10":"plane", "duong_tron_co_ban_10":"circle", "he_thuc_luong_van_dung_10":"triangle", "toa_do_hinh_hoc_10":"coordinate", "chung_minh_hinh_hoc_10":"plane", "phep_bien_hinh_co_ban_11":"transform", "nhan_biet_hinh_khong_gian_11":"space11", "hinh_khoi_va_the_tich_co_ban_12":"volume", "hinh_hoc_oxyz_van_dung_12":"space12",
      "he_thuc_luong":"triangle", "he_thuc_luong_tam_giac":"triangle", "hinh_hoc_10":"plane",
      "vector":"vector", "toa_do_phang":"coordinate", "duong_tron":"circle", "duong_thang":"line2d",
      "phep_bien_hinh_11":"transform", "hinh_khong_gian":"space11", "song_song_khong_gian":"space11",
      "vuong_goc_khong_gian":"space11", "goc_khoang_cach_11":"space11", "thiet_dien_hinh_khong_gian_11":"space11",
      "hinh_hoc_khong_gian":"volume", "toa_do_khong_gian":"space12", "mat_phang_oxyz":"plane", "duong_thang_oxyz":"line3d", "goc_khoang_cach_oxyz":"distance3d", "mat_cau":"sphere", "the_tich_khong_gian":"volume",
      "ham_so_bac_nhat":"graph", "ham_so_bac_hai":"graph", "do_thi_ham_so":"graph", "do_thi":"graph", "ham_so":"graph", "dao_ham":"graph", "cuc_tri":"graph",
      # Added 45 focused geometry topics (2026-10-16), routed to grade-aware validated builders.
      "g10_geom_angles_parallel":"plane",
      "g10_geom_triangle_congruence":"triangle",
      "g10_geom_special_lines":"triangle",
      "g10_geom_quadrilaterals_properties":"plane",
      "g10_geom_circle_chords_arcs":"circle",
      "g10_geom_thales_similarity":"triangle",
      "g10_geom_triangle_area_ratio":"triangle",
      "g10_geom_circle_angles":"circle",
      "g10_geom_coordinate_distance_midpoint":"coordinate",
      "g10_geom_line_intersections":"line2d",
      "g10_geom_locus":"plane",
      "g10_geom_circle_tangent_chord":"circle",
      "g10_geom_triangle_inequalities":"triangle",
      "g10_geom_vector_proofs":"vector",
      "g10_geom_coordinate_circle_line":"coordinate",
      "g11_geom_transform_translation":"transform",
      "g11_geom_transform_reflection":"transform",
      "g11_geom_space_lines_planes":"space11",
      "g11_geom_parallel_line_plane":"space11",
      "g11_geom_prism_pyramid_sections":"space11",
      "g11_geom_rotation_homothety":"transform",
      "g11_geom_parallel_planes":"space11",
      "g11_geom_perpendicular_line_plane":"space11",
      "g11_geom_dihedral_angles":"space11",
      "g11_geom_section_construction":"space11",
      "g11_geom_skew_lines_distance":"space11",
      "g11_geom_three_perpendiculars":"space11",
      "g11_geom_transform_composition":"transform",
      "g11_geom_section_ratio":"space11",
      "g11_geom_space_proof":"space11",
      "g12_geom_vectors_3d":"space12",
      "g12_geom_plane_equation":"plane",
      "g12_geom_line_equation_3d":"line3d",
      "g12_geom_sphere_equation":"sphere",
      "g12_geom_solid_surface_area":"volume",
      "g12_geom_point_plane_distance":"distance3d",
      "g12_geom_line_plane_angle":"distance3d",
      "g12_geom_two_planes_angle":"distance3d",
      "g12_geom_line_plane_intersection":"line3d",
      "g12_geom_sphere_tangent_plane":"sphere",
      "g12_geom_skew_line_relation":"line3d",
      "g12_geom_min_distance_3d":"distance3d",
      "g12_geom_sphere_plane_intersection":"sphere",
      "g12_geom_parameter_geometry":"space12",
      "g12_geom_3d_optimization":"volume",
    }
    kind=aliases.get(t)
    if not kind: return None
    if difficulty in {"expert", "hell"}:
        olympic = _olympic_extension(kind, g)
        if olympic is not None:
            return olympic
    level=difficulty if difficulty in {"easy","medium"} else ("hard" if difficulty in {"hard","expert","hell"} else "medium")
    if kind == "graph": return _graph_question(level)
    if g<=10:
        if kind=="plane": return _g10_plane_geometry(level)
        if kind=="triangle": return _g10_triangle(level, game_id)
        if kind=="vector": return _g10_vector(level)
        if kind=="coordinate": return _g10_coordinate(level)
        if kind=="line2d":
            q = _g10_coordinate(level)
            while q.get("archetype") not in {"distance_line", "line_through_point", "line_slope"}:
                q = _g10_coordinate(level)
            return q
        if kind=="circle": return _g10_circle(level, game_id)
        # If a 10th-grade topic uses a newer spatial alias, retain the topic but
        # use a foundational coordinate-plane archetype rather than unrelated content.
        return _g10_vector(level)
    if g==11:
        if kind=="transform": return _g11_transform(level)
        if kind=="space11": return _g11_space(level)
        if kind=="triangle":
            # Grade 11 uses sine/cosine rules and triangle applications, not vectors.
            family = random.choice(["cosine_rule", "sine_rule", "triangle_area", "bearing"] if level == "hard" else ["cosine_rule", "sine_rule", "triangle_area"])
            return _g10_triangle(level, game_id) if family in {"cosine_rule", "sine_rule", "triangle_area", "bearing"} else _g10_triangle(level, game_id)
        if kind in {"vector","coordinate"}: return _g10_vector(level)
        return _g11_space(level)
    if kind=="volume": return _g12_volume(level)
    if kind=="sphere": return _g12_sphere(level)
    if kind=="plane": return _g12_space_coordinate(level, "plane")
    if kind=="line3d": return _g12_space_coordinate(level, "line3d")
    if kind=="distance3d": return _g12_space_coordinate(level, "distance3d")
    if kind in {"space12","space11"}: return _g12_space_coordinate(level)
    if kind=="coordinate": return _g12_space_coordinate(level)
    if kind=="circle": return _g10_circle(level, game_id)
    return _g12_space_coordinate(level)


def generate(grade: int, topic_id: str, difficulty: str, game_id: str | None = None):
    """Generate a geometry question and ensure new geometry topics have a relevant diagram."""
    q = _generate_geometry_question(grade, topic_id, difficulty, game_id)
    if q is None or not topic_id.startswith(("g10_geom_", "g11_geom_", "g12_geom_")):
        return q
    if not q.get("diagram"):
        tid = topic_id
        # Topic-family fallbacks are intentionally shape-specific; these diagrams
        # are labeled as illustrations and never claim to be numerically to scale.
        if any(k in tid for k in ("circle", "chords", "sphere")) or tid in {"g12_geom_sphere_equation", "g12_geom_sphere_tangent_plane", "g12_geom_sphere_plane_intersection"}:
            diagram = circle(5) if not tid.startswith("g12_geom_sphere") else sphere_projection(5)
        elif any(k in tid for k in ("triangle", "thales", "special_lines", "area_ratio", "inequalities")):
            diagram = triangle_3_4_5()
        elif any(k in tid for k in ("transform", "reflection", "rotation", "homothety")):
            diagram = coordinate_points({"A":[1,1],"B":[4,1],"A′":[1,4],"B′":[4,4]}, [["A","B"],["A′","B′"]], "Minh họa ảnh của đoạn thẳng qua phép biến hình; không theo tỉ lệ dữ kiện.")
        elif grade == 11:
            diagram = pyramid_projection() if any(k in tid for k in ("pyramid", "section", "space_proof", "ratio")) else cube_projection()
        elif grade == 12 and any(k in tid for k in ("volume", "solid", "optimization")):
            diagram = pyramid_projection()
        else:
            diagram = coordinate_points({"A":[0,0],"B":[4,0],"C":[2,3]}, [["A","B"],["B","C"],["C","A"]], "Hình hình học minh họa theo chủ đề; không theo tỉ lệ dữ kiện.")
        errors = validate_geometry_diagram(diagram)
        if errors:
            raise ValueError("Invalid fallback geometry diagram: " + "; ".join(errors))
        q["diagram"] = diagram
        q["diagram_generated_for_topic"] = True
    return q
