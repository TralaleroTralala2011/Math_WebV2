"""MATH WEB Super Bank: additive, structure-first question generation.

This module intentionally sits beside the legacy generator.  It does not
remove or rewrite the old game/template bank.  Instead it adds a large set of
safe problem archetypes and combines them with topic metadata, contexts and
parameter pools.  The result is a much larger question space without storing
millions of near-duplicate questions.
"""
from __future__ import annotations

import math
import random
import re
from fractions import Fraction


def _base(question, answer, solution, distractors=None, hint="", **meta):
    return {
        "question": question,
        "answer": answer,
        "solution": solution,
        "distractors": list(distractors or []),
        "hint": hint,
        "template_source": "super_bank",
        **meta,
    }


def _frac(v):
    f = v if isinstance(v, Fraction) else Fraction(v)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def _pick(seq):
    return random.choice(seq)


def _signed_nonzero(low=-9, high=9):
    return _pick([x for x in range(low, high + 1) if x])


def _linear_equation(d):
    a = _signed_nonzero(-7, 7)
    x = random.randint(-8, 8)
    b = random.randint(-12, 12)
    c = a * x + b
    return _base(
        f"Tìm x: {a}x {b:+d} = {c}.", x,
        f"{a}x={c-b} nên x=({c-b})/{a}={x}.",
        [x + 1, x - 1, -x], "Cô lập hạng chứa x rồi chia cho hệ số của x.",
        archetype="linear_solve", generation_style="calculation", template_family="giải phương trình tuyến tính"
    )


def _linear_reverse(d):
    a = _pick([2, 3, 4, 5, 6])
    x = random.randint(2, 12)
    b = random.randint(-8, 12)
    y = a * x + b
    return _base(
        f"Một đại lượng được mô hình hóa bởi y={a}x{b:+d}. Khi y={y}, giá trị của x là bao nhiêu?",
        x,
        f"{a}x{b:+d}={y} nên {a}x={y-b} và x={x}.",
        [x + 2, x - 2, y], "Đảo ngược mô hình bằng cách đưa phương trình về dạng x=...",
        archetype="reverse_model", generation_style="reverse", template_family="tìm ngược từ mô hình"
    )


def _quadratic_factor(d):
    r1, r2 = random.randint(-7, 7), random.randint(-7, 7)
    b = -(r1 + r2)
    c = r1 * r2
    q = f"x² {b:+d}x {c:+d}=0"
    roots = f"x={r1} hoặc x={r2}" if r1 != r2 else f"x={r1} (nghiệm kép)"
    wrong = [f"x={-r1} hoặc x={-r2}", f"x={r1+r2}", f"x={c}"]
    return _base(
        f"Giải phương trình {q}.", roots,
        f"Ta có {q}=(x−({r1}))(x−({r2})), nên các nghiệm là {roots}.",
        wrong, "Tìm hai số có tổng bằng hệ số đối của x và tích bằng hệ số tự do.",
        archetype="quadratic_factor", generation_style="calculation", template_family="phân tích nhân tử"
    )


def _quadratic_parameter(d):
    r = random.randint(-5, 5)
    s = random.choice([x for x in range(-7, 8) if x != r])
    return _base(
        f"Phương trình (x−{r})({s:+d}−x)=0 có bao nhiêu nghiệm thực phân biệt?",
        2,
        f"Mỗi thừa số bằng 0 cho x={r} hoặc x={s}; vì {r}≠{s}, có 2 nghiệm thực phân biệt.",
        [0, 1, 3], "Đếm các giá trị x khác nhau làm ít nhất một thừa số bằng 0.",
        archetype="root_count", generation_style="reasoning", template_family="đếm nghiệm"
    )


def _system_construct(d):
    x, y = random.randint(-6, 6), random.randint(-6, 6)
    a, b = _pick([1, 2, 3]), _pick([1, 2, 3])
    p, q = _pick([1, 2, 3]), _pick([1, 2, 3])
    if a * q == b * p:
        q += 1
    c, r = a * x + b * y, p * x + q * y
    ans = f"({x}; {y})"
    return _base(
        f"Giải hệ: {a}x+{b}y={c}; {p}x+{q}y={r}.", ans,
        f"Thay x={x}, y={y}: {a}·{x}+{b}·{y}={c} và {p}·{x}+{q}·{y}={r}. Do hệ có định thức {a*q-b*p} khác 0, nghiệm duy nhất là ({x};{y}).",
        [f"({x+1}; {y})", f"({x}; {y+1})", f"({-x}; {y})"],
        "Có thể dùng thế hoặc cộng đại số; sau cùng kiểm tra cả hai phương trình.",
        archetype="system_solve", generation_style="multi_step", template_family="hệ hai ẩn"
    )


def _inequality(d):
    a = _pick([2, 3, 4, 5])
    b = random.randint(-12, 12)
    x0 = random.randint(-5, 5)
    c = a * x0 + b
    sign = _pick(["≥", "≤"])
    ans = f"x {'≥' if sign == '≥' else '≤'} {x0}"
    return _base(
        f"Giải bất phương trình {a}x {b:+d} {sign} {c}.",
        ans,
        f"Chuyển {b:+d} sang vế phải rồi chia cho {a}>0, nên giữ nguyên chiều: x {sign} {x0}.",
        [f"x {'≤' if sign == '≥' else '≥'} {x0}", f"x>{x0}", f"x<{x0}"], "Chú ý dấu khi chia cho hệ số của x.",
        archetype="linear_inequality", generation_style="calculation", template_family="bất phương trình tuyến tính"
    )


def _exponential_inequality(d):
    base = _pick([2,3,5])
    k = random.randint(-3,3)
    target = base ** k
    if _pick([True,False]):
        sign = ">"; ans = f"x>{k}"
    else:
        sign = "≤"; ans = f"x≤{k}"
    return _base(
        f"Giải bất phương trình {base}^x {sign} {target}.", ans,
        f"Vì {base}>1 nên hàm {base}^x đồng biến. So sánh với {base}^{k} suy ra x {sign} {k}.",
        [f"x<{k}", f"x≥{k}", f"x={k}"],
        "Với cơ số lớn hơn 1, hàm mũ giữ nguyên chiều khi so sánh số mũ.",
        archetype="exponential_inequality", generation_style="reasoning", template_family="bất phương trình mũ"
    )

def _logarithmic_inequality(d):
    base = _pick([2,3,5]); k = random.randint(-2,3); target = base ** k
    exact_target = _frac(Fraction(1, base**(-k))) if k < 0 else str(target)
    if _pick([True,False]):
        sign = ">"; ans = f"x>{exact_target}"
    else:
        sign = "≤"; ans = f"x≤{exact_target}"
    return _base(
        f"Giải bất phương trình log_{base}(x) {sign} {k}.", ans,
        f"Vì {base}>1, log_{base}(x) đồng biến và log_{base}(x) {sign} {k} tương đương x {sign} {base}^{k}={target}, đồng thời x>0.",
        [f"x<{target}", f"x≥{target}", f"x={k}"],
        "Đưa bất phương trình logarit về so sánh số mũ và nhớ điều kiện x>0.",
        archetype="logarithmic_inequality", generation_style="reasoning", template_family="bất phương trình logarit"
    )


def _set_operation(d):
    universe = set(range(1, 10))
    a = set(random.sample(sorted(universe), random.randint(3, 5)))
    b = set(random.sample(sorted(universe), random.randint(3, 5)))
    op = _pick(["A∩B", "A∪B", "A\\B"])
    if op == "A∩B": r = sorted(a & b)
    elif op == "A∪B": r = sorted(a | b)
    else: r = sorted(a - b)
    ans = "{" + ", ".join(map(str, r)) + "}" if r else "∅"
    return _base(
        f"Cho A={{{', '.join(map(str, sorted(a)))}}}, B={{{', '.join(map(str, sorted(b)))}}}. Tính {op}.",
        ans,
        f"Theo phép toán tập hợp {op}, ta lấy đúng các phần tử thỏa điều kiện tương ứng, được {ans}.",
        ["∅", "{" + ", ".join(map(str, sorted(a))) + "}", "{" + ", ".join(map(str, sorted(b))) + "}"],
        "Viết từng tập hợp theo thứ tự tăng dần rồi xét điều kiện của phép toán.",
        archetype="set_operation", generation_style="reasoning", template_family="phép toán tập hợp"
    )


def _count_choice(d):
    n = random.randint(6, 12)
    k = random.randint(2, min(5, n-1))
    ans = math.comb(n, k)
    return _base(
        f"Một nhóm có {n} học sinh. Chọn {k} bạn để lập một đội, không xét thứ tự. Có bao nhiêu cách chọn?",
        ans,
        f"Không xét thứ tự nên dùng tổ hợp: C({n},{k})={ans}.",
        [math.perm(n,k), math.comb(n,k-1), n*k],
        "Khi chỉ quan tâm ai được chọn mà không quan tâm vị trí, dùng tổ hợp.",
        archetype="combination", generation_style="calculation", template_family="chọn nhóm"
    )


def _arrange(d):
    n = random.randint(4, 8)
    ans = math.factorial(n)
    return _base(
        f"Có {n} quyển sách khác nhau. Xếp tất cả lên một giá sách. Có bao nhiêu cách xếp?",
        ans,
        f"Có n! cách hoán vị {n} phần tử, nên số cách là {n}!={ans}.",
        [n * (n-1), math.comb(n, 2), n*n],
        "Tất cả phần tử đều được dùng và thứ tự có ý nghĩa.",
        archetype="permutation", generation_style="calculation", template_family="sắp xếp toàn bộ"
    )


def _dice_event(d):
    threshold = random.randint(5, 10)
    good = sum(1 for a in range(1,7) for b in range(1,7) if a+b >= threshold)
    p = Fraction(good,36)
    return _base(
        f"Gieo một con xúc xắc công bằng liên tiếp hai lần. Xác suất để tổng số chấm lớn hơn hoặc bằng {threshold} là bao nhiêu?",
        _frac(p),
        f"Có 36 kết quả đồng khả năng. Số cặp (a,b) với a+b≥{threshold} là {good}, nên P={good}/36={_frac(p)}.",
        [_frac(Fraction(good+1,36)), _frac(Fraction(max(0,good-2),36)), _frac(Fraction(1,2))],
        "Mô tả mỗi kết quả bằng một cặp có thứ tự rồi đếm các cặp thỏa điều kiện.",
        archetype="dice_two_rolls", generation_style="scenario", template_family="xúc xắc hai lần"
    )


def _dice_reverse(d):
    total = random.randint(7, 11)
    good = [(a,b) for a in range(1,7) for b in range(1,7) if a+b == total]
    return _base(
        f"Gieo một con xúc xắc hai lần. Có bao nhiêu kết quả có thứ tự có tổng đúng bằng {total}?",
        len(good),
        f"Các cặp thỏa a+b={total} là: {', '.join(map(str, good))}. Có {len(good)} kết quả.",
        [len(good)+1, max(1,len(good)-1), total],
        "Liệt kê các cặp (a,b) với 1≤a,b≤6 và tổng bằng giá trị đã cho.",
        archetype="dice_count", generation_style="reverse", template_family="đếm kết quả"
    )


def _coin_experiment(d):
    n = random.randint(3, 6)
    ans = 2 ** n
    return _base(
        f"Gieo một đồng xu {n} lần. Nếu mỗi kết quả được phân biệt theo chuỗi mặt, không gian mẫu có bao nhiêu phần tử?",
        ans,
        f"Mỗi lần có 2 khả năng và có {n} lần gieo, nên |Ω|=2^{n}={ans}.",
        [2*n, n*n, math.factorial(n)],
        "Mỗi lần gieo độc lập có hai khả năng; dùng quy tắc nhân.",
        archetype="coin_sample_space", generation_style="theory_check", template_family="thí nghiệm đồng xu"
    )


def _mean_median(d):
    data = sorted(random.sample(range(4, 30), 5))
    mean = Fraction(sum(data), 5)
    median = data[2]
    if _pick([True, False]):
        q = f"Mẫu số liệu {data}. Trung bình cộng là bao nhiêu?"
        ans = _frac(mean); sol = f"Tổng là {sum(data)}, chia cho 5 được {_frac(mean)}."
    else:
        q = f"Mẫu số liệu đã sắp xếp {data}. Trung vị là bao nhiêu?"
        ans = median; sol = f"Có 5 giá trị nên trung vị là giá trị đứng thứ 3, bằng {median}."
    return _base(q, ans, sol, [median, _frac(mean+1), max(data)], "Xác định trước xem đề đang hỏi trung bình cộng hay trung vị.",
                 archetype="statistics_center", generation_style="data_analysis", template_family="phân tích mẫu số liệu")


def _sequence_arithmetic(d):
    a1 = random.randint(-8, 10); step = _signed_nonzero(-6, 6); n = random.randint(5, 15)
    ans = a1 + (n-1)*step
    return _base(
        f"Một dãy số có số hạng đầu {a1} và mỗi bước tăng {step}. Số hạng thứ {n} bằng bao nhiêu?",
        ans,
        f"Đây là cấp số cộng: aₙ=a₁+(n−1)d={a1}+({n}−1)·({step})={ans}.",
        [ans+step, ans-step, a1+n*step], "Kiểm tra xem hiệu giữa hai số liên tiếp có không đổi không.",
        archetype="arithmetic_sequence", generation_style="application", template_family="cấp số cộng"
    )


def _sequence_sum(d):
    a1 = random.randint(1, 8); step = random.randint(1, 6); n = random.randint(5, 12)
    an = a1 + (n-1)*step
    s = n*(a1+an)//2
    return _base(
        f"Cho cấp số cộng có a₁={a1}, công sai {step}. Tính tổng {n} số hạng đầu.",
        s,
        f"aₙ={a1}+({n}−1)·{step}={an}; Sₙ={n}({a1}+{an})/2={s}.",
        [n*an, n*(a1+step), s+step], "Tìm số hạng cuối trước rồi áp dụng công thức tổng cấp số cộng.",
        archetype="sequence_sum", generation_style="multi_step", template_family="tổng cấp số cộng"
    )


def _function_point(d):
    a = random.randint(2, 6); b = random.randint(-8, 8); x = random.randint(-5, 6); y = a*x+b
    return _base(
        f"Cho f(x)={a}x{b:+d}. Điểm có hoành độ x={x} thuộc đồ thị có tung độ bằng bao nhiêu?",
        y,
        f"y=f({x})={a}·{x}{b:+d}={y}.",
        [y+1, y-1, a*x], "Điểm trên đồ thị y=f(x) có tung độ bằng giá trị hàm tại hoành độ đó.",
        archetype="function_value", generation_style="calculation", template_family="điểm trên đồ thị"
    )


def _quadratic_vertex(d):
    h = random.randint(-5,5); k = random.randint(-8,8); a = _pick([1,2,-1,-2])
    return _base(
        f"Hàm số y={a}(x−{h})²{ k:+d} có đỉnh là điểm nào?",
        f"({h}; {k})",
        f"Dạng y=a(x−h)²+k có đỉnh I(h;k), nên đỉnh là ({h};{k}).",
        [f"({-h}; {k})", f"({h}; {-k})", f"({k}; {h})"], "Nhận dạng dạng chuẩn của parabol.",
        archetype="quadratic_vertex", generation_style="theory_check", template_family="đỉnh parabol"
    )


def _coordinate_distance(d):
    x1,y1=random.randint(-5,4),random.randint(-5,4)
    dx,dy=random.randint(1,6),random.randint(1,6)
    x2,y2=x1+dx,y1+dy
    ans=dx*dx+dy*dy
    return _base(
        f"Trong mặt phẳng tọa độ, A({x1};{y1}), B({x2};{y2}). Tính AB².", ans,
        f"AB²=({x2}−{x1})²+({y2}−{y1})²={dx}²+{dy}²={ans}.",
        [dx+dy, dx*dy, ans+1], "Với AB² không cần khai căn; chỉ dùng tổng hai bình phương độ chênh tọa độ.",
        archetype="coordinate_distance", generation_style="calculation", template_family="khoảng cách tọa độ"
    )


def _vector_dot(d):
    ax,ay=random.randint(-5,5),random.randint(-5,5)
    bx,by=random.randint(-5,5),random.randint(-5,5)
    ans=ax*bx+ay*by
    return _base(
        f"Cho u=({ax};{ay}) và v=({bx};{by}). Tính tích vô hướng u·v.", ans,
        f"u·v={ax}·{bx}+{ay}·{by}={ans}.", [ax*by+ay*bx, ax+bx+ay+by, ax*bx-ay*by],
        "Nhân từng hoành độ với nhau, từng tung độ với nhau rồi cộng.",
        archetype="vector_dot", generation_style="calculation", template_family="tích vô hướng"
    )


def _trig_value(d):
    table=[("0", "0", "1"), ("π/6", "1/2", "√3/2"), ("π/4", "√2/2", "√2/2"), ("π/3", "√3/2", "1/2"), ("π/2", "1", "0")]
    angle,s,c=_pick(table)
    if _pick([True,False]):
        return _base(f"Tính sin({angle}).", s, f"Theo bảng giá trị lượng giác cơ bản, sin({angle})={s}.", [c,"0","1"], "Nhớ các giá trị lượng giác góc đặc biệt.", archetype="trig_table", generation_style="theory_check", template_family="giá trị lượng giác")
    return _base(f"Tính cos({angle}).", c, f"Theo bảng giá trị lượng giác cơ bản, cos({angle})={c}.", [s,"0","1"], "Nhớ các giá trị lượng giác góc đặc biệt.", archetype="trig_table", generation_style="theory_check", template_family="giá trị lượng giác")


def _trig_identity(d):
    return _base(
        "Với mọi x mà biểu thức xác định, giá trị của sin²x + cos²x bằng bao nhiêu?",
        1,
        "Đây là hệ thức lượng giác cơ bản sin²x+cos²x=1.", [0,2,"sin x+cos x"],
        "Đây là hệ thức cơ bản liên hệ sin và cos của cùng một góc.",
        archetype="trig_identity", generation_style="knowledge", template_family="hệ thức lượng giác"
    )


def _limit_simple(d):
    a=random.randint(-5,5); h=random.randint(1,6)
    return _base(
        f"Tính lim(x→{h}) ({a}x+{2*a}).",
        3*a*h,
        f"Hàm bậc nhất liên tục nên thay trực tiếp x={h}: {a}·{h}+{2*a}={3*a*h}.",
        [a*h, 2*a*h, 3*a+h], "Với đa thức, có thể thay trực tiếp giá trị tiến tới.",
        archetype="limit_substitution", generation_style="calculation", template_family="giới hạn đa thức"
    )


def _derivative_basic(d):
    a=random.randint(1,7); n=random.choice([2,3,4]); x=random.randint(1,5)
    ans=a*n*(x**(n-1))
    return _base(
        f"Cho f(x)={a}x^{n}. Tính f'({x}).", ans,
        f"f'(x)={a*n}x^{n-1}, nên f'({x})={a*n}·{x}^{n-1}={ans}.",
        [a*x**n, a*n*x**n, a*(n-1)*x**n], "Dùng quy tắc đạo hàm của lũy thừa rồi thay x.",
        archetype="derivative_power", generation_style="calculation", template_family="đạo hàm lũy thừa"
    )


def _tangent_line(d):
    a=random.randint(1,4); x0=random.randint(-3,3); b=random.randint(-4,4)
    y0=a*x0*x0+b; m=2*a*x0
    # y = m(x-x0)+y0 = mx + intercept
    intercept=y0-m*x0
    ans=f"y={m}x{intercept:+d}"
    return _base(
        f"Cho f(x)={a}x²{b:+d}. Phương trình tiếp tuyến tại x={x0} là gì?",
        ans,
        f"f'({x0})={m}, f({x0})={y0}. Tiếp tuyến: y={m}(x−({x0}))+{y0}={ans}.",
        [f"y={m}x{(intercept+1):+d}", f"y={-m}x{intercept:+d}", f"y={a}x²{b:+d}"],
        "Tính hệ số góc bằng f'(x₀), rồi dùng điểm (x₀,f(x₀)).",
        archetype="tangent", generation_style="multi_step", template_family="tiếp tuyến"
    )


def _integral_power(d):
    a=random.randint(1,5); n=random.choice([1,2,3]); hi=random.randint(2,5)
    ans=Fraction(a*hi**(n+1),n+1)
    return _base(
        f"Tính ∫₀^{hi} {a}x^{n} dx.", _frac(ans),
        f"Nguyên hàm là {a}/({n+1})·x^{n+1}. Thay cận 0 và {hi} được {_frac(ans)}.",
        [_frac(ans*2), str(a*hi**n), _frac(Fraction(a*hi**n,n+1))],
        "Tăng số mũ lên 1 rồi chia cho số mũ mới trước khi thế cận.",
        archetype="definite_integral", generation_style="calculation", template_family="tích phân lũy thừa"
    )


def _complex_modulus(d):
    a,b=random.randint(-6,6),random.randint(-6,6)
    m2=a*a+b*b
    return _base(
        f"Cho z={a}{b:+d}i. Tính |z|².", m2,
        f"|z|²=a²+b²={a}²+{b}²={m2}.", [a*a+b, abs(a)+abs(b), m2+1],
        "Bình phương môđun bằng tổng bình phương phần thực và phần ảo.",
        archetype="complex_modulus", generation_style="calculation", template_family="môđun số phức"
    )


def _complex_operation(d):
    a,b,c,e=[random.randint(-5,5) for _ in range(4)]
    real=a+c; imag=b+e
    ans=f"{real}{imag:+d}i"
    return _base(
        f"Tính ({a}{b:+d}i)+({c}{e:+d}i).", ans,
        f"Cộng phần thực với phần thực và phần ảo với phần ảo: {a}+({c})={real}, {b}+({e})={imag}.",
        [f"{real}{(b-e):+d}i", f"{(a-c)}{imag:+d}i", f"{a+c+b+e}"],
        "Gom riêng phần thực và phần ảo.", archetype="complex_add", generation_style="calculation", template_family="phép toán số phức"
    )


def _real_life_linear(d):
    fixed=random.randint(10,50); unit=random.randint(3,12); qty=random.randint(2,15)
    total=fixed+unit*qty
    return _base(
        f"Một dịch vụ có phí cố định {fixed} nghìn đồng và thêm {unit} nghìn đồng cho mỗi đơn vị. Với {qty} đơn vị, tổng phí là bao nhiêu nghìn đồng?",
        total,
        f"Tổng phí={fixed}+{unit}·{qty}={total} nghìn đồng.",
        [unit*qty, total+unit, fixed+qty], "Tách chi phí cố định và chi phí phụ thuộc số lượng.",
        archetype="real_life_linear", generation_style="real_life", template_family="mô hình chi phí"
    )


def _real_life_growth(d):
    start=random.choice([200,500,800,1000]); rate=random.choice([5,10,20]);
    after=Fraction(start*(100+rate),100)
    return _base(
        f"Một lượng hàng ban đầu là {start} đơn vị và tăng {rate}% trong một giai đoạn. Sau giai đoạn đó có bao nhiêu đơn vị?",
        _frac(after),
        f"Lượng mới={start}·(1+{rate}/100)={_frac(after)} đơn vị.",
        [_frac(after+start*Fraction(rate,100)), str(start+rate), str(start*(100-rate)//100)],
        "Tăng r% nghĩa là giữ 100% ban đầu và cộng thêm r%.",
        archetype="percent_growth", generation_style="real_life", template_family="tăng trưởng thực tế"
    )


def _error_check(d):
    a=random.randint(2,9); x=random.randint(2,9); b=random.randint(1,8)
    correct=a*(x+b); wrong=a*x+b
    return _base(
        f"Một bạn biến đổi a({x}+{b}) thành {wrong}. Bước biến đổi đó đúng hay sai? Nếu sai, kết quả đúng là bao nhiêu với a={a}?",
        f"Sai; {a}({x}+{b})={correct}",
        f"Phải phân phối a cho cả hai số: {a}({x}+{b})={a}·{x}+{a}·{b}={correct}.",
        [f"Đúng; {wrong}", f"Sai; {wrong+a}", f"Đúng; {correct}"],
        "Kiểm tra xem hệ số ngoài ngoặc đã được nhân với mọi hạng tử chưa.",
        archetype="error_diagnosis", generation_style="mistake_check", template_family="phát hiện sai lầm"
    )


def _experiment_probability(d):
    red=random.randint(2,6); blue=random.randint(2,6); total=red+blue
    # Without replacement: probability of two red draws.
    p=Fraction(red,total)*Fraction(red-1,total-1)
    return _base(
        f"Một hộp có {red} thẻ đỏ và {blue} thẻ xanh. Rút ngẫu nhiên liên tiếp 2 thẻ không hoàn lại. Xác suất cả hai thẻ đều đỏ là bao nhiêu?",
        _frac(p),
        f"Lần 1: {red}/{total}. Sau khi lấy một thẻ đỏ còn {red-1} thẻ đỏ trên {total-1} thẻ. Do đó P={red}/{total}·{red-1}/{total-1}={_frac(p)}.",
        [_frac(Fraction(red,total)), _frac(Fraction(red-1,total-1)), _frac(Fraction(red*2,total))],
        "Vì không hoàn lại, mẫu số và số thẻ đỏ thay đổi ở lần rút thứ hai.",
        archetype="urn_without_replacement", generation_style="experiment", template_family="thí nghiệm rút thẻ"
    )


def _sample_space_dice(d):
    rolls = random.choice([2, 3])
    ans = 6 ** rolls
    return _base(
        f"Gieo một con xúc xắc {rolls} lần liên tiếp. Nếu phân biệt thứ tự các lần gieo, không gian mẫu có bao nhiêu kết quả?",
        ans,
        f"Mỗi lần gieo có 6 khả năng. Theo quy tắc nhân, |Ω|=6^{rolls}={ans}.",
        [6*rolls, 6**(rolls-1), math.factorial(rolls)],
        "Mỗi lần gieo có cùng số khả năng và thứ tự được phân biệt.",
        archetype="dice_sample_space", generation_style="knowledge", template_family="không gian mẫu xúc xắc"
    )


def _dice_exact_event(d):
    total = random.randint(4, 10)
    good = sum(1 for a in range(1,7) for b in range(1,7) if a+b == total)
    p = Fraction(good,36)
    return _base(
        f"Gieo xúc xắc hai lần. Xác suất để tổng số chấm đúng bằng {total} là bao nhiêu?",
        _frac(p),
        f"Có 36 cặp đồng khả năng và {good} cặp có tổng {total}, nên P={good}/36={_frac(p)}.",
        [_frac(Fraction(good+1,36)), _frac(Fraction(max(0,good-1),36)), _frac(Fraction(total,36))],
        "Đếm các cặp có thứ tự thỏa đúng tổng đã cho.",
        archetype="dice_exact_sum", generation_style="calculation", template_family="xúc xắc tổng đúng"
    )


def _probability_complement(d):
    n = random.randint(3, 10)
    favorable = random.randint(1, n-1)
    p = Fraction(favorable, n)
    comp = 1-p
    return _base(
        f"Một biến cố A có xác suất { _frac(p) }. Xác suất của biến cố đối của A bằng bao nhiêu?",
        _frac(comp),
        f"P(Ā)=1−P(A)=1−{_frac(p)}={_frac(comp)}.",
        [_frac(p), _frac(1+p), _frac(Fraction(favorable+1,n))],
        "Xác suất của một biến cố và biến cố đối cộng lại bằng 1.",
        archetype="complement_probability", generation_style="reasoning", template_family="biến cố đối"
    )


def _card_event(d):
    n = random.randint(8, 15)
    even = n // 2
    p = Fraction(even, n)
    return _base(
        f"Một hộp có các thẻ được đánh số từ 1 đến {n}. Rút ngẫu nhiên một thẻ. Xác suất rút được số chẵn là bao nhiêu?",
        _frac(p),
        f"Có {even} số chẵn trong {n} thẻ, nên P={even}/{n}={_frac(p)}.",
        [_frac(Fraction(even+1,n)), _frac(Fraction(1,n)), _frac(Fraction(n-even,n))],
        "Đếm số thẻ mang số chẵn rồi chia cho tổng số thẻ.",
        archetype="card_even", generation_style="scenario", template_family="rút thẻ số"
    )


def _empirical_probability(d):
    trials = random.choice([50, 100, 200, 500])
    success = random.randint(trials//5, trials*4//5)
    p = Fraction(success,trials)
    return _base(
        f"Trong {trials} lần thử một thí nghiệm, biến cố A xảy ra {success} lần. Tần suất của A là bao nhiêu?",
        _frac(p),
        f"Tần suất={success}/{trials}={_frac(p)}.",
        [_frac(Fraction(success+1,trials)), _frac(Fraction(success,trials+1)), _frac(Fraction(trials,success))],
        "Tần suất thực nghiệm bằng số lần biến cố xảy ra chia cho tổng số lần thử.",
        archetype="empirical_frequency", generation_style="experiment", template_family="tần suất thực nghiệm"
    )


def _probability_union_simple(d):
    n = random.randint(8, 16)
    a = random.randint(2, n//2)
    b = random.randint(2, n//2)
    inter = random.randint(0, min(a,b)-1)
    union = a+b-inter
    p = Fraction(union,n)
    return _base(
        f"Một không gian mẫu có {n} kết quả đồng khả năng. Hai biến cố A, B có lần lượt {a}, {b} kết quả và giao của chúng có {inter} kết quả. Tính P(A∪B).",
        _frac(p),
        f"|A∪B|=|A|+|B|−|A∩B|={a}+{b}−{inter}={union}; do đó P={union}/{n}={_frac(p)}.",
        [_frac(Fraction(a+b,n)), _frac(Fraction(inter,n)), _frac(Fraction(a*b,n))],
        "Dùng công thức cộng có trừ phần giao để tránh đếm hai lần.",
        archetype="probability_union", generation_style="multi_step", template_family="hợp hai biến cố"
    )


def _conditional_probability(d):
    # Simple two-stage population, exact Bayes-like result without requiring a named theorem.
    a,b=random.randint(2,7),random.randint(2,7)
    good_a=random.randint(1,a); good_b=random.randint(1,b)
    total=a+b; good=good_a+good_b
    return _base(
        f"Có hai nhóm I và II lần lượt gồm {a} và {b} sản phẩm. Nhóm I có {good_a} sản phẩm đạt chuẩn, nhóm II có {good_b} sản phẩm đạt chuẩn. Chọn ngẫu nhiên một sản phẩm từ toàn bộ hai nhóm. Xác suất chọn được sản phẩm đạt chuẩn là bao nhiêu?",
        _frac(Fraction(good,total)),
        f"Tổng có {total} sản phẩm, trong đó {good} đạt chuẩn. Xác suất={good}/{total}={_frac(Fraction(good,total))}.",
        [_frac(Fraction(good_a,a)), _frac(Fraction(good_b,b)), _frac(Fraction(good,total+1))],
        "Gộp số sản phẩm của hai nhóm trước khi tính xác suất chọn một sản phẩm bất kỳ.",
        archetype="population_probability", generation_style="scenario", template_family="xác suất theo nhóm"
    )


def _geometry_right_triangle(d):
    triples=[(3,4,5),(5,12,13),(6,8,10),(8,15,17)]
    a,b,c=_pick(triples); scale=random.randint(1,3); a*=scale;b*=scale;c*=scale
    return _base(
        f"Một tam giác vuông có hai cạnh góc vuông dài {a} cm và {b} cm. Cạnh huyền dài bao nhiêu cm?",
        c,
        f"Theo Pythagore: c=√({a}²+{b}²)=√({c}²)={c} cm.",
        [a+b, c+1, abs(b-a)], "Trong tam giác vuông, cạnh huyền liên hệ với hai cạnh góc vuông bằng định lý Pythagore.",
        archetype="right_triangle", generation_style="application", template_family="tam giác vuông",
        diagram={"type":"right_triangle","a":a,"b":b,"c":c}
    )


def _geometry_circle(d):
    r=random.randint(2,12)
    return _base(
        f"Một hình tròn có bán kính {r} cm. Diện tích theo π là bao nhiêu cm²?",
        f"{r*r}π",
        f"S=πr²=π·{r}²={r*r}π cm².",
        [f"{2*r}π",f"{r}π",f"{r*r*r}π"], "Diện tích hình tròn dùng bình phương bán kính.",
        archetype="circle_area", generation_style="calculation", template_family="diện tích hình tròn",
        diagram={"type":"circle","r":r}
    )


def _triangle_area(d):
    base=random.randint(4,15); height=random.randint(3,12)
    area=Fraction(base*height,2)
    return _base(
        f"Một tam giác có đáy {base} cm và chiều cao tương ứng {height} cm. Diện tích bằng bao nhiêu cm²?",
        _frac(area), f"S=1/2·{base}·{height}={_frac(area)} cm².",
        [_frac(area*2), str(base+height), _frac(Fraction(base,height))],
        "Diện tích tam giác bằng một nửa tích đáy và chiều cao tương ứng.",
        archetype="triangle_area", generation_style="calculation", template_family="diện tích tam giác"
    )


def _circle_circumference(d):
    r=random.randint(2,10)
    return _base(
        f"Một đường tròn có bán kính {r} cm. Chu vi theo π là bao nhiêu cm?",
        f"{2*r}π", f"C=2πr=2π·{r}={2*r}π cm.",
        [f"{r}π",f"{r*r}π",f"{4*r}π"],
        "Chu vi đường tròn dùng 2πr, không phải πr².",
        archetype="circle_circumference", generation_style="calculation", template_family="chu vi đường tròn"
    )


def _box_surface(d):
    a,b,c=[random.randint(2,8) for _ in range(3)]
    s=2*(a*b+b*c+c*a)
    return _base(
        f"Một hình hộp chữ nhật có kích thước {a} cm, {b} cm, {c} cm. Diện tích toàn phần là bao nhiêu cm²?",
        s, f"S_tp=2({a}·{b}+{b}·{c}+{c}·{a})={s} cm².",
        [a*b+b*c+c*a, a+b+c, a*b*c],
        "Cộng diện tích ba cặp mặt đối diện rồi nhân 2.",
        archetype="box_surface", generation_style="multi_step", template_family="diện tích toàn phần"
    )


def _angle_triangle(d):
    a=random.randint(30,80); b=random.randint(20,90); c=180-a-b
    if c<=10: return _angle_triangle(d)
    missing=_pick([a,b,c]); total=a+b+c; ans=180-(total-missing)
    return _base(
        f"Một tam giác có hai góc lần lượt là {a}° và {b}°. Góc còn lại bằng bao nhiêu độ?",
        c, f"Tổng ba góc tam giác bằng 180°, nên góc còn lại=180−{a}−{b}={c}°.",
        [180-a,180-b, a+b], "Tổng ba góc trong một tam giác bằng 180°.",
        archetype="triangle_angle", generation_style="reasoning", template_family="góc trong tam giác"
    )


def _derivative_quadratic(d):
    a=random.randint(1,6); b=random.randint(-8,8); x=random.randint(-4,5)
    ans=2*a*x+b
    return _base(
        f"Cho f(x)={a}x²{b:+d}x. Tính f'({x}).", ans,
        f"f'(x)={2*a}x{b:+d}; thay x={x} được {ans}.",
        [a*x*x+b, 2*a*x, 2*a*x-b], "Đạo hàm của ax²+bx là 2ax+b.",
        archetype="derivative_quadratic", generation_style="calculation", template_family="đạo hàm hàm bậc hai"
    )


def _integral_constant(d):
    a=random.randint(2,9); lo=random.randint(0,3); hi=random.randint(lo+1,7)
    ans=a*(hi-lo)
    return _base(
        f"Tính ∫_{lo}^{hi} {a} dx.", ans,
        f"∫_{lo}^{hi}{a}dx={a}({hi}−{lo})={ans}.",
        [a*hi, a*(hi+lo), hi-lo], "Tích phân của hằng số trên đoạn bằng hằng số nhân độ dài đoạn.",
        archetype="integral_constant", generation_style="calculation", template_family="tích phân hằng số"
    )

def _geometry_space(d):
    # Rectangular box volume is a safe spatial-geometry base.
    a,b,c=[random.randint(2,9) for _ in range(3)]; v=a*b*c
    return _base(
        f"Một hình hộp chữ nhật có ba kích thước {a} cm, {b} cm và {c} cm. Thể tích bằng bao nhiêu cm³?",
        v,
        f"V={a}·{b}·{c}={v} cm³.", [a*b, a+b+c, v+c],
        "Thể tích hình hộp chữ nhật bằng tích ba kích thước.",
        archetype="box_volume", generation_style="application", template_family="thể tích không gian"
    )


def _graph_reasoning(d):
    a=random.randint(2,6); b=random.randint(-8,8)
    if a>0:
        ans="đồng biến"
    else:
        ans="nghịch biến"
    return _base(
        f"Xét hàm số f(x)={a}x{b:+d} trên ℝ. Hàm số đồng biến hay nghịch biến?",
        ans,
        f"Hàm bậc nhất có hệ số góc {a}>0 nên đồng biến trên ℝ.", ["nghịch biến","không đổi","không xác định"],
        "Đối với hàm bậc nhất, dấu của hệ số x quyết định chiều biến thiên.",
        archetype="linear_monotonicity", generation_style="reasoning", template_family="tính đơn điệu hàm bậc nhất"
    )


def _newton_binomial(d):
    n=random.randint(4,8); k=random.randint(0,n)
    coeff=math.comb(n,k)
    return _base(
        f"Trong khai triển (a+b)^{n}, hệ số của a^{n-k}b^{k} là bao nhiêu?",
        coeff,
        f"Theo nhị thức Newton, hệ số là C({n},{k})={coeff}.",
        [math.comb(n,k-1) if k>0 else 1, math.comb(n,k+1) if k<n else 1, n*k],
        "Hệ số của hạng tổng quát liên quan đến một hệ số tổ hợp.",
        archetype="newton_coefficient", generation_style="calculation", template_family="hệ số nhị thức Newton"
    )


def _induction_structure(d):
    n=random.randint(2,6)
    return _base(
        f"Trong một chứng minh quy nạp cho mệnh đề P(n), sau khi đã chứng minh P({n}) đúng, bước tiếp theo cần chứng minh điều gì?",
        f"P({n+1}) đúng",
        f"Bước quy nạp phải chỉ ra từ giả thiết P({n}) đúng suy ra P({n+1}) đúng.",
        [f"P({n-1}) đúng", "P(0) sai", f"P({n}) sai"],
        "Quy nạp chuyển từ một chỉ số bất kỳ sang chỉ số kế tiếp.",
        archetype="induction_step", generation_style="knowledge", template_family="cấu trúc quy nạp"
    )


def _transformation_point(d):
    x,y=random.randint(-5,5),random.randint(-5,5); a,b=random.randint(-4,4),random.randint(-4,4)
    ans=f"({x+a}; {y+b})"
    return _base(
        f"Phép tịnh tiến theo vectơ ({a};{b}) biến điểm A({x};{y}) thành điểm nào?",
        ans,
        f"Cộng từng tọa độ với vectơ tịnh tiến: A'=({x}+{a};{y}+{b})={ans}.",
        [f"({x-a}; {y-b})", f"({x+a}; {y-b})", f"({x-a}; {y+b})"],
        "Phép tịnh tiến cộng cùng một vectơ vào tọa độ điểm.",
        archetype="translation_point", generation_style="calculation", template_family="phép tịnh tiến"
    )


def _survey_parabola(d):
    h=random.randint(-5,5); k=random.randint(-7,7); a=random.choice([1,2,-1,-2])
    direction="hướng lên" if a>0 else "hướng xuống"
    return _base(
        f"Cho y={a}(x−{h})²{ k:+d}. Parabol có đỉnh tại đâu và mở theo hướng nào?",
        f"I({h}; {k}), {direction}",
        f"Dạng y=a(x−h)²+k cho đỉnh I(h;k)=({h};{k}). Vì a {'>' if a>0 else '<'} 0 nên parabol {direction}.",
        [f"I({-h}; {k}), {direction}", f"I({h}; {-k}), {direction}", f"I({h}; {k}), {'hướng xuống' if a>0 else 'hướng lên'}"],
        "Đọc trực tiếp h, k và dấu của hệ số a trong dạng chuẩn.",
        archetype="parabola_survey", generation_style="reasoning", template_family="khảo sát parabol"
    )


def _space_distance(d):
    x1,y1,z1=[random.randint(-4,4) for _ in range(3)]
    dx,dy,dz=[random.randint(1,5) for _ in range(3)]
    x2,y2,z2=x1+dx,y1+dy,z1+dz
    ans2=dx*dx+dy*dy+dz*dz
    return _base(
        f"Trong Oxyz, A({x1};{y1};{z1}), B({x2};{y2};{z2}). Tính AB².", ans2,
        f"AB²=({x2}−{x1})²+({y2}−{y1})²+({z2}−{z1})²={ans2}.",
        [dx*dx+dy*dy, dx+dy+dz, ans2+1],
        "Trong không gian, bình phương khoảng cách là tổng ba bình phương độ chênh tọa độ.",
        archetype="space_distance", generation_style="calculation", template_family="khoảng cách trong Oxyz"
    )


def _asymptote(d):
    a=random.randint(-5,5); b=random.randint(-4,4)
    return _base(
        f"Hàm số f(x)=1/(x−({a})){b:+d} có tiệm cận đứng là đường thẳng nào?",
        f"x={a}",
        f"Mẫu số bằng 0 tại x={a}, trong khi tử số khác 0, nên tiệm cận đứng là x={a}.",
        [f"y={b}", f"x={-a}", f"y={a}"],
        "Tìm giá trị làm mẫu số bằng 0.",
        archetype="vertical_asymptote", generation_style="theory_check", template_family="tiệm cận đứng"
    )


def _line_intersection(d):
    x=random.randint(-4,5); y=random.randint(-5,5)
    m1=random.randint(1,4); m2=random.choice([z for z in range(-4,5) if z!=m1])
    b1=y-m1*x; b2=y-m2*x
    ans=f"({x}; {y})"
    return _base(
        f"Hai đường thẳng y={m1}x{b1:+d} và y={m2}x{b2:+d} cắt nhau tại điểm nào?",
        ans,
        f"Tại giao điểm hai giá trị y bằng nhau. Thay x={x} cho cả hai đường đều cho y={y}, nên giao điểm là {ans}.",
        [f"({x+1}; {y})", f"({x}; {y+1})", f"({-x}; {y})"],
        "Giao điểm phải thỏa mãn đồng thời cả hai phương trình đường thẳng.",
        archetype="line_intersection", generation_style="reasoning", template_family="giao điểm hai đường thẳng"
    )


def _exponential_function(d):
    base=random.choice([2,3,5]); k=random.randint(-2,4); ans=base**k
    return _base(
        f"Tính {base}^{k}.", ans,
        f"Lũy thừa với số mũ {k} cho giá trị {ans}.",
        [base*k, base+k, base**(k+1)],
        "Đọc đúng cơ số và số mũ; với số mũ âm, dùng nghịch đảo.",
        archetype="exponential_value", generation_style="calculation", template_family="giá trị hàm mũ"
    )


def _log_function(d):
    base=random.choice([2,3,5]); k=random.randint(0,4); value=base**k
    return _base(
        f"Tính log_{base}({value}).", k,
        f"Vì {base}^{k}={value} nên log_{base}({value})={k}.",
        [value, base, k+1],
        "Đưa về câu hỏi: cơ số phải lũy thừa mấy để được số trong ngoặc?",
        archetype="log_value", generation_style="calculation", template_family="giá trị logarit"
    )


def _exponential_equation(d):
    base=random.choice([2,3,5]); k=random.randint(-2,4); target=Fraction(1,base**(-k)) if k<0 else base**k
    return _base(
        f"Giải phương trình {base}^x={_frac(target)}.", k,
        f"Vì {base}^x={base}^{k} và hàm mũ cơ số {base}>1 đơn ánh, suy ra x={k}.",
        [k+1,k-1,-k], "Đưa vế phải về cùng cơ số rồi so sánh số mũ.",
        archetype="exponential_equation", generation_style="reasoning", template_family="phương trình mũ"
    )


def _log_equation(d):
    base=random.choice([2,3,5]); k=random.randint(-1,4); target=Fraction(1,base**(-k)) if k<0 else base**k
    return _base(
        f"Giải phương trình log_{base}(x)={k}.", _frac(target),
        f"Theo định nghĩa logarit, x={base}^{k}={_frac(target)} và x>0.",
        [str(k), str(base), _frac(target+1)],
        "Đổi phương trình logarit sang dạng lũy thừa.",
        archetype="log_equation", generation_style="reasoning", template_family="phương trình logarit"
    )


def _generic_theory(topic_name, subtopics, d):
    sub = _pick(subtopics or [topic_name])
    return _base(
        f"Trong chủ đề “{topic_name}”, nội dung nào dưới đây là một hướng kiến thức được học?",
        sub,
        f"Chủ đề {topic_name} bao gồm nội dung “{sub}” theo cấu trúc kiến thức của MATH WEB.",
        [x for x in [topic_name, "một nội dung không thuộc chủ đề", "một phép tính ngẫu nhiên"] if x != sub][:3],
        "Đọc tên chủ đề và đối chiếu với các mảng kiến thức con.",
        archetype="curriculum_theory", generation_style="knowledge", template_family="kiến thức chương"
    )


def _remainder(d):
    m = random.choice([3, 4, 5, 6, 7, 8, 9])
    r = random.randint(0, m - 1)
    k = random.randint(3, 8)
    n = k * m + r
    return _base(
        f"Chia {n} cho {m}, số dư là bao nhiêu?", r,
        f"{n}={k}·{m}+{r}, với 0≤{r}<{m}, nên số dư là {r}.",
        [(r + 1) % m, (r - 1) % m, m - r if r else 1],
        "Viết số bị chia dưới dạng thương nhân số chia cộng số dư.",
        archetype="remainder", generation_style="calculation", template_family="phép chia có dư"
    )


def _divisibility(d):
    divisor = random.choice([3, 4, 5, 6, 8, 9, 10])
    base = random.randint(10, 99)
    number = base * divisor
    return _base(
        f"Trong các số sau, số nào chắc chắn chia hết cho {divisor}? Xét số {number}.", number,
        f"{number}={number//divisor}·{divisor}, nên {number} chia hết cho {divisor}.",
        [number + 1, number + 2, number - 1],
        "Kiểm tra xem số đã cho có thể viết thành tích của số chia và một số nguyên hay không.",
        archetype="divisibility", generation_style="calculation", template_family="dấu hiệu chia hết"
    )


def _radical(d):
    a = random.randint(2, 9)
    k = random.choice([2, 3, 4, 5])
    value = a * a * k
    ans = f"{a}√{k}"
    return _base(
        f"Rút gọn √{value}.", ans,
        f"{value}={a}²·{k}, nên √{value}={a}√{k}.",
        [f"{k}√{a}", f"{a}√{value}", str(a * k)],
        "Tách dưới dấu căn thành một bình phương hoàn chỉnh nhân với phần còn lại.",
        archetype="radical_simplify", generation_style="calculation", template_family="rút gọn căn thức"
    )


def _identity(d):
    a = random.randint(2, 9)
    b = random.randint(1, 7)
    ans = a*a + 2*a*b + b*b
    return _base(
        f"Tính nhanh {a}²+2·{a}·{b}+{b}².", ans,
        f"Nhận ra (a+b)²: ({a}+{b})²={ans}.",
        [a*a + b*b, (a+b)*2, a*a + 2*b],
        "Nhận dạng dạng bình phương của một tổng.",
        archetype="identity", generation_style="calculation", template_family="hằng đẳng thức"
    )


def _algebraic_fraction(d):
    a = random.randint(2, 8)
    b = random.randint(1, 5)
    x = random.randint(2, 9)
    ans = f"{a}/{b}"
    return _base(
        f"Với x={x}, tính phân thức {a}x/{b}x.", ans,
        f"Vì x={x}≠0 nên {a}x/({b}x)={a}/{b}.",
        [f"{a*x}/{b}", f"{a}/{b*x}", f"{a+b}/{x}"],
        "Kiểm tra điều kiện mẫu khác 0 rồi rút gọn nhân tử chung x.",
        archetype="algebraic_fraction", generation_style="calculation", template_family="rút gọn phân thức"
    )


# Topic groups.  A topic may have several archetypes, so each generation can
# choose a different structure even when the topic stays fixed.
GROUPS = {
    "algebra": {"builders":[_linear_equation,_linear_reverse,_error_check]},
    "remainder": {"builders":[_remainder]},
    "divisibility": {"builders":[_divisibility]},
    "radical": {"builders":[_radical]},
    "identity": {"builders":[_identity]},
    "algebraic_fraction": {"builders":[_algebraic_fraction]},
    "quadratic": {"builders":[_quadratic_factor,_quadratic_parameter,_quadratic_vertex]},
    "system": {"builders":[_system_construct,_error_check]},
    "inequality": {"builders":[_inequality,_error_check]},
    "exponential_inequality": {"builders":[_exponential_inequality]},
    "logarithmic_inequality": {"builders":[_logarithmic_inequality]},
    "set": {"builders":[_set_operation,_generic_theory]},
    "counting": {"builders":[_count_choice,_arrange]},
    "probability": {"builders":[_dice_event,_dice_reverse,_sample_space_dice,_dice_exact_event,_coin_experiment,_experiment_probability,_empirical_probability,_probability_complement,_card_event,_probability_union_simple,_conditional_probability]},
    "statistics": {"builders":[_mean_median]},
    "sequence": {"builders":[_sequence_arithmetic,_sequence_sum]},
    "function": {"builders":[_function_point,_quadratic_vertex,_graph_reasoning]},
    "coordinate": {"builders":[_coordinate_distance,_vector_dot]},
    "trig": {"builders":[_trig_value,_trig_identity]},
    "limit": {"builders":[_limit_simple]},
    "derivative": {"builders":[_derivative_basic,_derivative_quadratic,_tangent_line,_graph_reasoning]},
    "integral": {"builders":[_integral_power,_integral_constant]},
    "complex": {"builders":[_complex_modulus,_complex_operation]},
    "geometry": {"builders":[_geometry_right_triangle,_triangle_area,_geometry_circle,_circle_circumference,_angle_triangle,_geometry_space,_box_surface]},
    "real_life": {"builders":[_real_life_linear,_real_life_growth]},
    "newton": {"builders":[_newton_binomial]},
    "induction": {"builders":[_induction_structure]},
    "transformation": {"builders":[_transformation_point]},
    "survey": {"builders":[_survey_parabola]},
    "space_coordinate": {"builders":[_space_distance]},
    "asymptote": {"builders":[_asymptote]},
    "intersection": {"builders":[_line_intersection]},
    "exponential": {"builders":[_exponential_function]},
    "logarithmic": {"builders":[_log_function]},
    "exponential_equation": {"builders":[_exponential_equation]},
    "logarithmic_equation": {"builders":[_log_equation]},
}

TOPIC_GROUP = {}

def _register(group, *ids):
    for tid in ids: TOPIC_GROUP[tid]=group

_register("remainder", "chia_du")
_register("divisibility", "chia_het")
_register("radical", "can_thuc")
_register("identity", "hang_dang_thuc")
_register("algebraic_fraction", "phan_thuc_dai_so")
_register("quadratic", "phuong_trinh_bac_hai")
_register("counting", "to_hop", "chinh_hop")
_register("inequality", "bat_phuong_trinh")
_register("set", "menh_de_tap_hop", "menh_de", "tap_hop")
_register("inequality", "bat_phuong_trinh", "he_bat_phuong_trinh")
_register("exponential_inequality", "bpt_mu")
_register("logarithmic_inequality", "bpt_logarit")
_register("system", "phuong_trinh_he", "he_phuong_trinh")
_register("quadratic", "ham_so_bac_hai", "phuong_trinh", "cuc_tri", "gtln_gtnn")
_register("counting", "quy_tac_dem", "hoan_vi_chinh_hop_to_hop", "to_hop_xac_suat_nang_cao_11")
_register("probability", "xac_suat", "xac_suat_11", "xac_suat_12", "bien_co_doc_lap_11")
_register("statistics", "thong_ke", "thong_ke_11", "thong_ke_12")
_register("sequence", "day_so", "day_so_10", "cap_so_cong", "cap_so_nhan", "day_so_tong_quat", "day_so_truy_hoi_11")
_register("function", "ham_so", "ham_so_bac_nhat")
_register("coordinate", "vector", "toa_do_phang", "duong_thang", "mat_phang_oxyz", "duong_thang_oxyz")
_register("trig", "he_thuc_luong", "he_thuc_luong_tam_giac", "gia_tri_luong_giac", "cong_thuc_luong_giac", "phuong_trinh_luong_giac", "phuong_trinh_luong_giac_day_du", "ham_so_luong_giac", "ham_so_luong_giac_day_du")
_register("limit", "gioi_han", "gioi_han_ham_so", "ham_so_lien_tuc")
_register("derivative", "dao_ham", "dao_ham_quy_tac", "ung_dung_dao_ham_11", "ung_dung_dao_ham", "tiep_tuyen", "tinh_don_dieu")
_register("integral", "nguyen_ham_tich_phan", "nguyen_ham", "tich_phan", "ung_dung_tich_phan")
_register("complex", "so_phuc", "bieu_dien_so_phuc", "pt_so_phuc")
_register("geometry", "hinh_hoc_10", "hinh_khong_gian", "hinh_hoc_khong_gian", "song_song_khong_gian", "vuong_goc_khong_gian", "goc_khoang_cach_11", "thiet_dien_hinh_khong_gian_11", "duong_tron", "goc_khoang_cach_oxyz", "the_tich_khong_gian", "mat_cau")
_register("real_life", "bai_toan_thuc_te_10", "bai_toan_thuc_te_11", "bai_toan_thuc_te_tong_hop_11", "bai_toan_thuc_te_12", "tong_hop_thpt")
_register("newton", "nhi_thuc_newton")
_register("induction", "quy_nap_toan_hoc_11")
_register("transformation", "phep_bien_hinh_11")
_register("survey", "khao_sat_ham_so")
_register("space_coordinate", "toa_do_khong_gian")
_register("asymptote", "tien_can")
_register("intersection", "tuong_giao")
_register("exponential", "ham_mu")
_register("logarithmic", "ham_logarit")
_register("exponential_equation", "pt_mu")
_register("logarithmic_equation", "pt_logarit")


def generate(topic_id: str, grade: int, difficulty: str, topic_info=None):
    """Generate one structurally diverse item for a topic.

    Returns None when no safe specialized archetype is registered.  This is
    deliberate: the legacy engine remains the fallback and is never deleted.
    """
    group = TOPIC_GROUP.get(topic_id)
    if not group:
        return None
    builders = GROUPS[group]["builders"]
    # Easy favors direct/calculation; harder levels deliberately increase the
    # chance of reverse, multi-step, error-check and reasoning archetypes.
    if difficulty in {"hard", "expert"}:
        preferred=[b for b in builders if getattr(b, "__name__", "") in {
            "_linear_reverse","_quadratic_parameter","_system_construct","_error_check",
            "_dice_reverse","_conditional_probability","_sequence_sum","_tangent_line",
            "_graph_reasoning","_real_life_growth"
        }]
        if preferred and random.random()<0.78:
            builders=preferred
    builder=random.choice(builders)
    if builder is _generic_theory:
        info=topic_info or {}
        return builder(info.get("name",topic_id), info.get("subtopics",[]), difficulty)
    q=builder(difficulty)
    q["topic_group"]=group
    return q


SUPER_BANK_STATS = {
    "version":"1.0-super-bank",
    "archetypes":len({b.__name__ for g in GROUPS.values() for b in g["builders"]}),
    "topic_mappings":len(TOPIC_GROUP),
    "groups":sorted(GROUPS),
}
