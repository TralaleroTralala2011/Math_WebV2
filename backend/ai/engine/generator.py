import math
import random
import uuid
from fractions import Fraction

from .difficulty import normalize
from .math_utils import comb, fmt, perm


class QuestionGenerator:
    """Sinh câu hỏi toán bằng dữ liệu ngẫu nhiên, không cần LLM để chấm đúng/sai."""

    def __init__(self, knowledge):
        self.knowledge = knowledge

    def generate(self, grade, topic_id, difficulty, question_type):
        difficulty = normalize(difficulty)
        topic = self.knowledge.get(topic_id)
        if not topic:
            raise ValueError("Unknown topic")
        fn = getattr(self, f"_g_{topic_id}", self._g_generic)
        q = fn(grade, difficulty)
        q.update({
            "id": uuid.uuid4().hex,
            "grade": grade,
            "topic": topic_id,
            "difficulty": difficulty,
            "question_type": question_type,
            "knowledge_name": topic["name"],
        })
        return self._convert(q, question_type)

    def _base(self, question, answer, solution, distractors=None):
        return {
            "question": question,
            "answer": answer,
            "solution": solution,
            "distractors": distractors or [],
        }

    def _options(self, answer, distractors):
        values = []
        for value in [answer, *distractors]:
            value = fmt(value)
            if value not in values:
                values.append(value)
        while len(values) < 4:
            try:
                base = Fraction(str(answer))
                value = fmt(base + random.choice([-7, -5, -3, 3, 5, 7]))
            except Exception:
                value = f"{answer} + {len(values)}"
            if value not in values:
                values.append(value)
        random.shuffle(values)
        return values[:4]

    def _convert(self, q, question_type):
        if question_type == "multiple_choice":
            answer = fmt(q["answer"])
            q["answer"] = answer
            q["options"] = self._options(answer, q.get("distractors", []))
            q.pop("distractors", None)
            return q

        if question_type == "short_answer":
            q["answer"] = fmt(q["answer"])
            q["options"] = []
            q.pop("distractors", None)
            return q

        answer = q["answer"]
        try:
            n = Fraction(str(answer))
            statements = [
                f"Kết quả cần tìm bằng {fmt(answer)}.",
                f"Nếu tăng đáp án lên 1 thì được {fmt(n + 1)}.",
                f"Đáp án bằng {fmt(n + 2)}.",
                f"Đáp án nhỏ hơn {fmt(n + 3)}.",
            ]
            truth = [True, False, False, True]
        except Exception:
            statements = [
                f"Đáp án của bài là {answer}.",
                "Có thể bỏ qua dữ kiện chính của đề.",
                "Đáp án bằng một giá trị khác.",
                "Lời giải cần dùng dữ kiện của đề.",
            ]
            truth = [True, False, False, True]

        q["answer"] = fmt(answer)
        q["statements"] = statements
        q["statement_answers"] = truth
        q["options"] = []
        q.pop("distractors", None)
        return q

    def _g_ham_so_bac_hai(self, g, d):
        a = random.choice([1, 2, 3, -1, -2])
        h, k = random.randint(-6, 6), random.randint(-8, 8)
        x = random.randint(-8, 8) if d in ("hard", "expert") else random.randint(-4, 4)
        y = a * (x - h) ** 2 + k
        return self._base(
            f"Cho hàm số y={a}(x-{h})²+{k}. Tính f({x}).",
            y, f"f({x})={a}({x}-{h})²+{k}={y}.", [y + 1, y - 1, y + 2]
        )

    def _g_phuong_trinh_he(self, g, d):
        while True:
            x, y = random.randint(-9, 9), random.randint(-9, 9)
            a, b = random.randint(1, 4), random.randint(1, 4)
            p, q = random.randint(1, 4), random.randint(1, 4)
            if a * q != p * b:
                break
        c, r = a * x + b * y, p * x + q * y
        answer = f"({x},{y})"
        return self._base(
            f"Giải hệ: {a}x + {b}y = {c}; {p}x + {q}y = {r}.",
            answer,
            f"Thay x={x}, y={y}: {a}·{x}+{b}·{y}={c} và {p}·{x}+{q}·{y}={r}.",
            [f"({x+1},{y})", f"({x},{y+1})", f"({-x},{y})"]
        )

    def _g_phuong_trinh_luong_giac(self, g, d):
        return self._base(
            "Trên đoạn [0;2π], phương trình sin x = 0 có bao nhiêu nghiệm?",
            3,
            "sin x=0 khi x=kπ. Trên [0;2π] có 0, π, 2π nên có 3 nghiệm.",
            [2, 4, 5]
        )

    def _g_cap_so_cong(self, g, d):
        a1 = random.randint(-8, 8)
        d0 = random.choice([-5, -3, -2, 2, 3, 5])
        n = random.randint(5, 14)
        an = a1 + (n - 1) * d0
        if d == "easy":
            return self._base(
                f"Cho CSC có a₁={a1}, công sai d={d0}. Tính a₍{n}₎.",
                an, f"aₙ=a₁+(n-1)d={an}.", [an + 2, an - 2, an + 5]
            )
        total = n * (a1 + an) // 2
        return self._base(
            f"Cho CSC có a₁={a1}, d={d0}. Tính tổng {n} số hạng đầu.",
            total, f"aₙ={an}; Sₙ=n(a₁+aₙ)/2={total}.", [total + n, total - n, total + 2 * n]
        )

    def _g_cap_so_nhan(self, g, d):
        a1 = random.choice([1, 2, 3, 4, -1, -2])
        ratio = random.choice([2, 3, -2])
        n = random.randint(4, 8)
        an = a1 * ratio ** (n - 1)
        return self._base(
            f"Cho CSN có a₁={a1}, công bội q={ratio}. Tính a₍{n}₎.",
            an, f"aₙ=a₁qⁿ⁻¹={an}.", [an // ratio, an * ratio, an + ratio]
        )

    def _g_hoan_vi_chinh_hop_to_hop(self, g, d):
        n = random.randint(5, 10)
        k = random.randint(2, n - 2)
        if random.choice([True, False]):
            ans = comb(n, k)
            text = f"Có {n} học sinh. Chọn {k} bạn vào một nhóm không xét thứ tự. Có bao nhiêu cách?"
            sol = f"C({n},{k})={ans}."
        else:
            ans = perm(n, k)
            text = f"Có {n} học sinh. Chọn và xếp {k} bạn vào {k} vị trí. Có bao nhiêu cách?"
            sol = f"A({n},{k})={ans}."
        return self._base(text, ans, sol, [ans + 1, max(0, ans - k), ans + n])

    def _g_quy_tac_dem(self, g, d):
        a, b, c = random.randint(3, 8), random.randint(2, 5), random.randint(2, 4)
        ans = a * b * c
        return self._base(
            f"Một bạn có {a} áo, {b} quần và {c} đôi giày. Có bao nhiêu bộ gồm 1 áo, 1 quần và 1 đôi giày?",
            ans, f"Theo quy tắc nhân: {a}·{b}·{c}={ans}.", [ans + a, ans - b, ans + 2]
        )

    def _g_xac_suat(self, g, d):
        red, blue = random.randint(2, 9), random.randint(2, 9)
        total = red + blue
        ans = Fraction(red, total)
        return self._base(
            f"Một hộp có {red} bi đỏ và {blue} bi xanh. Lấy ngẫu nhiên 1 viên. Xác suất lấy bi đỏ?",
            fmt(ans), f"P={red}/{total}={fmt(ans)}.",
            [fmt(Fraction(blue, total)), fmt(Fraction(red + 1, total)), fmt(Fraction(1, total))]
        )

    def _g_vector(self, g, d):
        ax, ay = random.randint(-7, 7), random.randint(-7, 7)
        bx, by = random.randint(-7, 7), random.randint(-7, 7)
        ans = ax * bx + ay * by
        return self._base(
            f"Cho u=({ax};{ay}), v=({bx};{by}). Tính u·v.",
            ans, f"u·v={ax}·{bx}+{ay}·{by}={ans}.", [ans + 1, ans - 1, ans + 2]
        )

    def _g_bat_phuong_trinh(self, g, d):
        a = random.randint(2, 9)
        b, c = random.randint(-15, 15), random.randint(-10, 10)
        r = Fraction(c - b, a)
        ans = f"x > {fmt(r)}"
        return self._base(
            f"Giải bất phương trình {a}x + ({b}) > {c}.",
            ans, f"{a}x>{c-b} nên x>{fmt(r)}.",
            [f"x < {fmt(r)}", f"x ≥ {fmt(r)}", f"x ≤ {fmt(r)}"]
        )

    def _g_menh_de_tap_hop(self, g, d):
        a = set(random.sample(range(1, 14), random.randint(3, 6)))
        b = set(random.sample(range(1, 14), random.randint(3, 6)))
        common = sorted(a & b)
        ans = len(common)
        return self._base(
            f"Cho A={{{','.join(map(str, sorted(a)))}}}, B={{{','.join(map(str, sorted(b)))}}}. Tính số phần tử của A∩B.",
            ans, f"A∩B={{{','.join(map(str, common))}}}, có {ans} phần tử.",
            [ans + 1, max(0, ans - 1), len(a | b)]
        )

    def _g_dao_ham(self, g, d):
        a, b, x = random.randint(2, 8), random.randint(-6, 6), random.randint(-5, 5)
        ans = 2 * a * x + b
        return self._base(
            f"Cho f(x)={a}x²+{b}x+1. Tính f'({x}).",
            ans, f"f'(x)=2·{a}x+{b}, nên f'({x})={ans}.", [ans + 2, ans - 2, ans + 4]
        )

    def _g_ung_dung_dao_ham(self, g, d):
        a, h, k = random.randint(1, 5), random.randint(-4, 4), random.randint(-6, 6)
        return self._base(
            f"Hàm số y={a}(x-{h})²+{k} đạt giá trị nhỏ nhất bằng bao nhiêu?",
            k, f"Vì a>0, parabol mở lên và đạt GTNN={k} tại x={h}.", [k + 1, k - 1, k + 2]
        )

    def _g_so_phuc(self, g, d):
        a, b = random.randint(-8, 8), random.randint(-8, 8)
        ans = a * a + b * b
        return self._base(
            f"Cho z={a}{'+' if b >= 0 else ''}{b}i. Tính |z|².",
            ans, f"|z|²={a}²+{b}²={ans}.", [ans + 1, max(0, ans - 1), ans + 2]
        )

    def _g_nguyen_ham_tich_phan(self, g, d):
        a, b = random.randint(1, 6), random.randint(-5, 5)
        lo, hi = random.randint(0, 2), random.randint(3, 7)
        ans = Fraction(a, 2) * (hi ** 2 - lo ** 2) + b * (hi - lo)
        return self._base(
            f"Tính I=∫[{lo},{hi}] ({a}x+{b})dx.",
            fmt(ans), f"Nguyên hàm là {a}/2·x²+{b}x. Thay cận được I={fmt(ans)}.",
            [fmt(ans + 1), fmt(ans - 1), fmt(ans + 2)]
        )

    def _g_toa_do_khong_gian(self, g, d):
        p = [random.randint(-5, 5) for _ in range(3)]
        q = [random.randint(-5, 5) for _ in range(3)]
        ans = sum((q[i] - p[i]) ** 2 for i in range(3))
        return self._base(
            f"Trong Oxyz, A({p[0]},{p[1]},{p[2]}), B({q[0]},{q[1]},{q[2]}). Tính AB².",
            ans, f"AB²=({q[0]-p[0]})²+({q[1]-p[1]})²+({q[2]-p[2]})²={ans}.",
            [ans + 1, max(0, ans - 1), ans + 3]
        )

    def _g_thong_ke(self, g, d):
        data = [random.randint(2, 20) for _ in range(random.randint(5, 8))]
        ans = Fraction(sum(data), len(data))
        return self._base(
            f"Cho mẫu số liệu {data}. Tính số trung bình cộng.",
            fmt(ans), f"x̄=({'+'.join(map(str, data))})/{len(data)}={fmt(ans)}.",
            [fmt(ans + 1), fmt(ans - 1), fmt(ans + 2)]
        )

    def _g_ham_so_luong_giac(self, g, d):
        return self._base("Giá trị lớn nhất của sin x là bao nhiêu?", 1, "Vì -1≤sin x≤1 nên GTLN là 1.", [0, 2, -1])

    def _g_day_so(self, g, d):
        n, a, d0 = random.randint(3, 10), random.randint(-5, 8), random.randint(1, 5)
        ans = a + d0 * n
        return self._base(
            f"Cho dãy aₙ={a}+({d0})n. Tính a₍{n}₎.",
            ans, f"Thay n={n}: aₙ={a}+{d0}·{n}={ans}.", [ans + 1, ans - 1, ans + 2]
        )

    def _g_gioi_han(self, g, d):
        a = random.randint(2, 8)
        return self._base(f"Tính lim(x→∞) ({a}x²+1)/x².", a, f"Chia tử và mẫu cho x², giới hạn bằng {a}.", [a + 1, a - 1, 0])

    def _g_hinh_khong_gian(self, g, d):
        return self._base(
            "Nếu d vuông góc với hai đường thẳng cắt nhau cùng nằm trong mặt phẳng (P), quan hệ giữa d và (P) là gì?",
            "d ⟂ (P)",
            "Theo định lý, d vuông góc với mặt phẳng (P).",
            ["d ∥ (P)", "d ⊂ (P)", "d cắt (P) nhưng không vuông góc"]
        )

    def _g_hinh_hoc_khong_gian(self, g, d):
        r = random.randint(2, 8)
        value = Fraction(4 * r ** 3, 3)
        return self._base(
            f"Một khối cầu có bán kính {r}. Thể tích theo π là bao nhiêu?",
            f"{fmt(value)}π",
            f"V=4/3·πr³={fmt(value)}π.",
            [f"{fmt(Fraction(4*r*r,3))}π", f"{fmt(Fraction(2*r**3,3))}π", f"{r**3}π"]
        )

    def _g_generic(self, g, d):
        a, b = random.randint(3, 12), random.randint(2, 9)
        ans = a * b
        return self._base(
            f"Có {a} lựa chọn loại A và {b} lựa chọn loại B. Theo quy tắc nhân có bao nhiêu phương án?",
            ans, f"Số phương án={a}·{b}={ans}.", [ans + 1, ans - 1, ans + 2]
        )

    _g_xac_suat_11 = _g_xac_suat
    _g_xac_suat_12 = _g_xac_suat
    _g_thong_ke_12 = _g_thong_ke
    _g_khao_sat_ham_so = _g_ham_so_bac_hai
