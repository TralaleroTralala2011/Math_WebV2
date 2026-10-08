"""Additive question bank for newer curriculum and real-world variants.

This module is intentionally separate from the original game bank.  It is a
fallback layer only, so the legacy generators and template bank remain intact.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction


def _fmt(v):
    v = Fraction(v) if not isinstance(v, Fraction) else v
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def _base(question, answer, solution, distractors, hint=""):
    return {
        "question": question,
        "answer": answer,
        "solution": solution,
        "distractors": list(distractors),
        "hint": hint,
    }


def generate(topic_id: str, grade: int, difficulty: str):
    """Return an additive verified question for selected curriculum topics."""
    fn = TOPIC_BUILDERS.get(topic_id)
    return fn(difficulty) if fn else None


def _thuc_te_10(d):
    w = random.randint(3, 8)
    h = random.randint(4, 12)
    area = w * h
    return _base(
        f"Một khu đất hình chữ nhật dài {h} m, rộng {w} m. Cần lát kín khu đất. Diện tích cần lát là bao nhiêu?",
        area,
        f"Diện tích hình chữ nhật = dài × rộng = {h} × {w} = {area} m².",
        [area + w, area - w, h + w],
        "Xác định công thức diện tích hình chữ nhật rồi thay số.",
    )


def _thuc_te_11(d):
    rate = random.choice([2, 3, 4, 5, 8])
    start = random.choice([100, 200, 500, 1000])
    after = start * (1 + rate / 100)
    after = Fraction(after).limit_denominator()
    return _base(
        f"Một khoản tiền {start} nghìn đồng tăng {rate}% sau một năm. Giá trị mới là bao nhiêu nghìn đồng?",
        _fmt(after),
        f"Giá trị mới = {start} × (1 + {rate}/100) = {_fmt(after)} nghìn đồng.",
        [_fmt(after + 10), _fmt(after - 10), str(start + rate)],
        "Tăng r% nghĩa là nhân giá trị ban đầu với 1 + r/100.",
    )


def _thuc_te_12(d):
    a = random.randint(2, 6)
    x = random.randint(3, 9)
    revenue = a * x * x
    return _base(
        f"Doanh thu của một mô hình được xấp xỉ bởi R(x)={a}x² (triệu đồng). Khi x={x}, doanh thu là bao nhiêu triệu đồng?",
        revenue,
        f"Thay x={x}: R({x})={a}·{x}²={revenue} triệu đồng.",
        [a * x, revenue + a, max(0, revenue - x)],
        "Thay giá trị x vào mô hình rồi tính lũy thừa trước khi nhân.",
    )


def _triangle(d):
    a = random.randint(3, 8)
    b = random.randint(4, 9)
    c = math.gcd(a, b)
    # Keep a right triangle by constructing the hypotenuse from Pythagorean triples.
    triples = [(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17)]
    x, y, z = random.choice(triples)
    scale = random.randint(1, 3)
    x, y, z = x * scale, y * scale, z * scale
    return _base(
        f"Một tam giác vuông có hai cạnh góc vuông dài {x} cm và {y} cm. Cạnh huyền dài bao nhiêu cm?",
        z,
        f"Theo Pythagore: c=√({x}²+{y}²)=√({z}²)={z} cm.",
        [x + y, z + 1, abs(y - x)],
        "Trong tam giác vuông, bình phương cạnh huyền bằng tổng bình phương hai cạnh góc vuông.",
    ) | {"diagram": {"type": "right_triangle", "a": x, "b": y, "c": z}}


def _circle(d):
    r = random.randint(2, 9)
    return _base(
        f"Một biển báo hình tròn có bán kính {r} cm. Diện tích biển báo theo π là bao nhiêu cm²?",
        f"{r*r}π",
        f"S=πr²=π·{r}²={r*r}π cm².",
        [f"{2*r}π", f"{r}π", f"{r*r*r}π"],
        "Diện tích hình tròn dùng bình phương bán kính.",
    ) | {"diagram": {"type": "circle", "r": r}}


def _coordinate(d):
    x1, y1 = random.randint(-6, 4), random.randint(-5, 5)
    dx, dy = random.randint(2, 6), random.randint(2, 6)
    x2, y2 = x1 + dx, y1 + dy
    dist2 = dx * dx + dy * dy
    return _base(
        f"Trong mặt phẳng tọa độ, A({x1};{y1}) và B({x2};{y2}). Tính AB².",
        dist2,
        f"AB²=({x2}-{x1})²+({y2}-{y1})²={dx}²+{dy}²={dist2}.",
        [dist2 + 1, dx + dy, abs(dx * dy)],
        "Dùng công thức khoảng cách giữa hai điểm rồi giữ ở dạng bình phương.",
    ) | {"diagram": {"type": "points", "a": [x1, y1], "b": [x2, y2]}}


def _area_triangle(d):
    base = random.randint(4, 12)
    height = random.randint(3, 10)
    area = Fraction(base * height, 2)
    return _base(
        f"Một tam giác có đáy {base} cm và chiều cao {height} cm. Diện tích là bao nhiêu cm²?",
        _fmt(area),
        f"S=1/2·đáy·cao=1/2·{base}·{height}={_fmt(area)} cm².",
        [_fmt(area * 2), str(base + height), _fmt(Fraction(base, height))],
        "Diện tích tam giác bằng một nửa tích của đáy và chiều cao tương ứng.",
    ) | {"diagram": {"type": "triangle_area", "base": base, "height": height}}


def _mean(d):
    data = [random.randint(5, 25) for _ in range(5)]
    total = sum(data)
    ans = Fraction(total, len(data))
    return _base(
        f"Mẫu số liệu ghi nhận: {data}. Số trung bình cộng bằng bao nhiêu?",
        _fmt(ans),
        f"x̄=({'+'.join(map(str, data))})/{len(data)}={total}/{len(data)}={_fmt(ans)}.",
        [_fmt(ans + 1), _fmt(ans - 1), str(max(data))],
        "Cộng tất cả giá trị rồi chia cho số quan sát.",
    )


def _sequence_real(d):
    start = random.randint(2, 8)
    step = random.randint(2, 6)
    n = random.randint(6, 12)
    ans = start + (n - 1) * step
    return _base(
        f"Một hệ thống ghi nhận {start}, {start+step}, {start+2*step}, ... đơn vị mỗi ngày. Ngày thứ {n} ghi nhận bao nhiêu đơn vị?",
        ans,
        f"Đây là cấp số cộng với a₁={start}, d={step}. aₙ=a₁+(n−1)d={start}+({n}−1)·{step}={ans}.",
        [ans + step, ans - step, start + n * step],
        "Nhận ra lượng thay đổi mỗi ngày là không đổi.",
    )


def _linear_model(d):
    a = random.randint(2, 9)
    b = random.randint(5, 20)
    x = random.randint(2, 8)
    y = a * x + b
    return _base(
        f"Chi phí vận chuyển được mô hình hóa bởi C(x)={a}x+{b} (nghìn đồng). Với x={x}, chi phí là bao nhiêu?",
        y,
        f"C({x})={a}·{x}+{b}={y} nghìn đồng.",
        [y + a, y - a, a * (x + 1) + b],
        "Đây là hàm bậc nhất, nên chỉ cần thay x vào biểu thức.",
    )


def _derivative_real(d):
    a = random.randint(1, 6)
    x = random.randint(2, 8)
    ans = 2 * a * x
    return _base(
        f"Quãng đường của một vật được mô hình hóa bởi s(t)={a}t² (m). Tốc độ tức thời s'(t) tại t={x} là bao nhiêu m/s?",
        ans,
        f"s'(t)=2·{a}t. Tại t={x}: s'({x})={ans} m/s.",
        [a * x, ans + a, ans - x],
        "Tốc độ tức thời được mô tả bởi đạo hàm của quãng đường theo thời gian.",
    )


def _integral_area(d):
    a = random.randint(1, 4)
    hi = random.randint(2, 6)
    ans = Fraction(a * hi**2, 2)
    return _base(
        f"Một vận tốc có dạng v(t)={a}t trên khoảng 0≤t≤{hi}. Quãng đường đi được là bao nhiêu?",
        _fmt(ans),
        f"S=∫₀^{hi}{a}t dt={a}/2·{hi}²={_fmt(ans)}.",
        [_fmt(ans * 2), str(a * hi), _fmt(Fraction(a * hi, 2))],
        "Quãng đường được tính bằng tích phân của vận tốc theo thời gian.",
    )


TOPIC_BUILDERS = {
    "bai_toan_thuc_te_10": _thuc_te_10,
    "bai_toan_thuc_te_11": _thuc_te_11,
    "bai_toan_thuc_te_12": _thuc_te_12,
    "bai_toan_thuc_te_tong_hop_11": _thuc_te_11,
    "hinh_hoc_10": _triangle,
    "he_thuc_luong": _triangle,
    "he_thuc_luong_tam_giac": _triangle,
    "duong_tron": _circle,
    "hinh_khong_gian": _circle,
    "toa_do_phang": _coordinate,
    "duong_thang": _coordinate,
    "hinh_hoc": _triangle,
    "thong_ke": _mean,
    "thong_ke_11": _mean,
    "thong_ke_12": _mean,
    "day_so": _sequence_real,
    "day_so_tong_quat": _sequence_real,
    "cap_so_cong": _sequence_real,
    "ham_so": _linear_model,
    "ham_so_bac_nhat": _linear_model,
    "dao_ham": _derivative_real,
    "dao_ham_quy_tac": _derivative_real,
    "ung_dung_dao_ham_11": _derivative_real,
    "nguyen_ham": _integral_area,
    "tich_phan": _integral_area,
    "ung_dung_tich_phan": _integral_area,
}
