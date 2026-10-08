"""Additive diversity engine for MATH WEB.

This module deliberately sits beside the original game/template generators.
It does not remove or replace the old bank.  It supplies many independently
structured question families so a practice set is not just the same template
with different numbers.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction


def _fmt(v):
    if isinstance(v, Fraction):
        return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def _sign(v):
    return f"+ {v}" if v >= 0 else f"- {abs(v)}"


class DiversityQuestionEngine:
    """Generate genuinely different mathematical tasks from the same topic.

    The engine is deterministic only with respect to the random source passed
    by Python.  Each result exposes a family, style, context and diversity key
    so the service can reject repeats even when the wording is different.
    """

    STYLES = (
        "calculation", "reasoning", "reverse", "application", "scenario",
        "multi_step", "real_life", "theory_check", "mistake_check",
        "comparison", "construction", "data_interpretation",
    )

    CONTEXTS = (
        "một tình huống trong học tập",
        "một bài toán đo đạc thực tế",
        "một tình huống mua bán",
        "một mô hình sản xuất",
        "một trò chơi tính điểm",
        "một bảng dữ liệu khảo sát",
        "một bài toán chuyển động",
        "một tình huống thiết kế",
        "một mô hình khoa học đơn giản",
        "một tình huống công nghệ",
        "một bài toán tối ưu trong đời sống",
        "một tình huống thể thao",
    )

    def generate(self, topic, difficulty="medium", question_type="multiple_choice", game_id=None):
        name = str(topic.get("name", ""))
        topic_id = str(topic.get("id", ""))
        sub = " ".join(str(x) for x in topic.get("subtopics", []))
        key = (name + " " + topic_id + " " + sub).lower()
        game = str(game_id or "").lower()

        # A selected game remains a hard mathematical boundary.
        if game:
            q = self._game(game, difficulty)
            if q:
                return self._finish(q, topic, question_type)

        q = None
        if any(x in key for x in ("bai_toan_thuc_te", "bài toán thực tế")):
            q = self._real_world(key, difficulty)
        elif any(x in key for x in ("xác suất", "xac_suat", "biến cố")):
            q = self._probability(difficulty)
        elif any(x in key for x in ("tổ hợp", "chỉnh hợp", "hoán vị", "quy tắc đếm", "nhị thức newton")):
            q = self._counting(difficulty)
        elif any(x in key for x in ("số phức", "so_phuc")):
            q = self._complex(difficulty)
        elif any(x in key for x in ("tích phân", "nguyên hàm", "tich_phan")):
            q = self._integral(difficulty)
        elif any(x in key for x in ("logarit", "log", "mũ", "mu", "pt_log", "pt_mu", "bpt_log", "bpt_mu")):
            q = self._exponential_log(key, difficulty)
        elif any(x in key for x in ("lượng giác", "luong_giac", "sin", "cos", "tan")):
            q = self._trig(key, difficulty)
        elif any(x in key for x in ("dãy số", "day_so", "cấp số", "cap_so")):
            q = self._sequences(key, difficulty)
        elif any(x in key for x in ("đạo hàm", "đơn điệu", "cực trị", "gtln", "gtnn", "tiếp tuyến", "tiệm cận", "tương giao", "khảo sát")):
            q = self._calculus(key, difficulty)
        elif any(x in key for x in ("hình", "tam giác", "đường tròn", "mặt phẳng", "đường thẳng", "vectơ", "vector", "góc", "khoảng cách", "thể tích", "mặt cầu", "tọa độ")):
            q = self._geometry(key, difficulty)
        elif any(x in key for x in ("thống kê", "thong_ke", "tứ phân vị", "phương sai")):
            q = self._statistics(difficulty)
        elif any(x in key for x in ("bất phương trình", "bpt", "bat_phuong_trinh")):
            q = self._inequality(difficulty)
        elif any(x in key for x in ("phương trình", "pt_", "hệ phương trình", "he_phuong_trinh")):
            q = self._equations(difficulty)
        elif any(x in key for x in ("căn thức", "radical")):
            q = self._radical(difficulty)
        elif any(x in key for x in ("hằng đẳng thức", "identities")):
            q = self._identity(difficulty)
        elif any(x in key for x in ("phân thức", "algebraic_fraction")):
            q = self._rational(difficulty)
        elif any(x in key for x in ("chia hết", "chia dư", "divisibility", "remainder", "modulo")):
            q = self._number_theory(key, difficulty)
        elif any(x in key for x in ("tập hợp", "mệnh đề", "menh_de", "tap_hop")):
            q = self._sets_logic(difficulty)

        if q is None:
            q = self._mixed_foundation(name, difficulty)
        return self._finish(q, topic, question_type)

    def _finish(self, q, topic, question_type):
        q.setdefault("template_family", q.get("problem_family", "diverse"))
        q.setdefault("generation_style", random.choice(self.STYLES))
        q.setdefault("context", random.choice(self.CONTEXTS))
        q.setdefault("template_source", "diversity_engine")
        q["diversity_key"] = "|".join(str(q.get(x, "")) for x in (
            "problem_family", "generation_style", "reasoning_mode", "context"
        ))
        if str(q.get("hint", "")).startswith("Tự vẽ:"):
            q["drawing_prompt"] = q["hint"]
            q["question"] = q["question"].rstrip() + "\n\n✏️ " + q["drawing_prompt"]
        q["question_type"] = question_type
        return q

    def _base(self, question, answer, solution, distractors, family, style, mode, hint=""):
        return {
            "question": question,
            "answer": answer,
            "solution": solution,
            "distractors": list(distractors),
            "template_family": family,
            "generation_style": style,
            "reasoning_mode": mode,
            "context": random.choice(self.CONTEXTS),
            "variant": random.randint(1, 10_000_000),
            "hint": hint,
        }

    def _game(self, game, d):
        if "xúc xắc" in game:
            variant = random.randrange(6)
            if variant == 0:
                face = random.randint(1, 6)
                return self._base(f"Một con xúc xắc cân đối được gieo một lần. Xác suất xuất hiện mặt {face} là bao nhiêu?", "1/6", "Có 6 kết quả đồng khả năng và chỉ 1 kết quả thuận lợi.", ["1/3", "1/2", "1/4"], "dice_single", "calculation", "classical_probability")
            if variant == 1:
                s = random.randint(5, 9)
                pairs = [(a, b) for a in range(1, 7) for b in range(1, 7) if a + b == s]
                p = Fraction(len(pairs), 36)
                return self._base(f"Gieo đồng thời hai xúc xắc. Xác suất tổng số chấm bằng {s} là bao nhiêu?", _fmt(p), f"Có {len(pairs)} cặp thuận lợi trên 36 cặp đồng khả năng, nên P={_fmt(p)}.", ["1/6", "1/9", "1/3"], "dice_sum", "reasoning", "count_outcomes")
            if variant == 2:
                k = random.randint(2, 4)
                p = Fraction(6-k, 6)
                return self._base(f"Gieo một xúc xắc. Xác suất số chấm lớn hơn {k} là bao nhiêu?", _fmt(p), f"Các mặt lớn hơn {k} có {6-k} kết quả nên P={6-k}/6={_fmt(p)}.", ["1/6", "1/2", "2/3"], "dice_inequality", "comparison", "favorable_count")
            if variant == 3:
                p = Fraction(11, 36)
                return self._base("Gieo một xúc xắc hai lần. Xác suất xuất hiện ít nhất một lần mặt 6 là bao nhiêu?", _fmt(p), "Dùng biến cố đối: 1-(5/6)²=11/36.", ["1/6", "1/3", "25/36"], "dice_complement", "reasoning", "complement")
            if variant == 4:
                p = Fraction(1, 6)
                return self._base("Gieo hai xúc xắc. Xác suất để hai mặt xuất hiện giống nhau là bao nhiêu?", _fmt(p), "Có 6 cặp giống nhau trong 36 cặp, nên P=6/36=1/6.", ["1/12", "1/3", "1/2"], "dice_equal", "calculation", "ordered_pairs")
            s = random.randint(7, 9)
            pairs = [(a, b) for a in range(1, 7) for b in range(1, 7) if a + b >= s]
            p = Fraction(len(pairs), 36)
            return self._base(f"Gieo hai xúc xắc. Xác suất tổng số chấm không nhỏ hơn {s} là bao nhiêu?", _fmt(p), f"Có {len(pairs)} cặp thỏa điều kiện trên 36 cặp.", ["1/4", "5/18", "1/3"], "dice_threshold", "reasoning", "count_outcomes")
        if "bốc bi" in game:
            r, b = random.randint(3, 9), random.randint(3, 9)
            variant = random.randrange(5)
            if variant == 0:
                p = Fraction(r, r+b)
                return self._base(f"Một túi có {r} bi đỏ và {b} bi xanh. Lấy 1 viên ngẫu nhiên. Xác suất lấy bi đỏ là?", _fmt(p), f"Có {r+b} viên, {r} viên đỏ: P={r}/{r+b}={_fmt(p)}.", [_fmt(Fraction(b,r+b)), "1/2", "1/3"], "marble_single", "calculation", "favorable_total")
            if variant == 1:
                p = Fraction(r*(r-1), (r+b)*(r+b-1))
                return self._base(f"Có {r} bi đỏ và {b} bi xanh. Lấy 2 viên không hoàn lại. Xác suất cả hai đều đỏ là?", _fmt(p), f"P={r}/{r+b} × {r-1}/{r+b-1}={_fmt(p)}.", [_fmt(Fraction(r,r+b)), _fmt(Fraction(r*(r-1),(r+b)**2)), "1/2"], "marble_two_same", "multi_step", "conditional_product")
            if variant == 2:
                p = Fraction(2*r*b, (r+b)*(r+b-1))
                return self._base(f"Túi có {r} bi đỏ và {b} bi xanh. Lấy 2 viên không hoàn lại. Xác suất hai viên khác màu là?", _fmt(p), f"Hai thứ tự đỏ-xanh và xanh-đỏ đều thuận lợi, nên P=2rb/[(r+b)(r+b-1)]={_fmt(p)}.", [_fmt(Fraction(r*b,(r+b)**2)), _fmt(Fraction(r,r+b)), "1/2"], "marble_different", "reasoning", "two_orders")
            if variant == 3:
                k = random.randint(2, 4)
                p = Fraction(math.comb(r, k), math.comb(r+b, k)) if k <= r else Fraction(0)
                return self._base(f"Túi có {r} bi đỏ và {b} bi xanh. Chọn {k} viên cùng lúc. Xác suất tất cả đều đỏ là?", _fmt(p), f"Có C({r},{k}) cách thuận lợi trên C({r+b},{k}) cách, nên P={_fmt(p)}.", ["1/2", _fmt(Fraction(r,r+b)), "1/3"], "marble_combination", "multi_step", "combination_probability")
            p = Fraction(r-1, r+b-1)
            return self._base(f"Sau khi đã lấy một viên đỏ và không hoàn lại, túi còn {r-1} đỏ và {b} xanh. Xác suất lần sau lấy đỏ là?", _fmt(p), f"Tổng còn {r+b-1} viên, trong đó {r-1} đỏ.", [_fmt(Fraction(r,r+b)), _fmt(Fraction(b,r+b)), "1/2"], "marble_conditional", "reverse", "conditional_probability")
        if any(x in game for x in ("chọn đội", "ghép lựa chọn", "săn tổ hợp", "xếp vị trí", "mật mã", "sắp thứ tự")):
            return self._counting(d)
        if any(x in game for x in ("bắt điểm", "tìm giao điểm", "đồ thị bí ẩn")):
            return self._functions(d, game)
        if any(x in game for x in ("điều tra", "tìm giá trị", "ghép đáp án")):
            return self._equations(d)
        if any(x in game for x in ("săn nghiệm", "ghép nghiệm", "mở khóa")):
            return self._equations(d)
        if any(x in game for x in ("vùng an toàn", "chọn khoảng", "vượt rào")):
            return self._inequality(d)
        if any(x in game for x in ("tìm quy luật", "điền số", "đường đua dãy số")):
            return self._sequences("dãy số", d)
        if any(x in game for x in ("truy tìm số", "chọn số", "phá khóa", "bốc số", "săn số dư", "modulo")):
            return self._number_theory(game, d)
        if any(x in game for x in ("săn căn", "rút gọn nhanh", "mở khóa căn thức")):
            return self._radical(d)
        if any(x in game for x in ("phá biểu thức", "ghép công thức", "công thức bí ẩn")):
            return self._identity(d)
        if any(x in game for x in ("rút gọn", "tìm điều kiện", "phân thức tốc độ")):
            return self._rational(d)
        if any(x in game for x in ("tìm góc", "săn độ dài", "bản đồ hình học")):
            return self._geometry("hinh_hoc_10", d)
        if any(x in game for x in ("đọc biểu đồ", "săn số liệu", "thống kê")):
            return self._statistics(d)
        return None

    def _probability(self, d):
        variant = random.randrange(8)
        if variant == 0:
            n, good = random.randint(20, 60), random.randint(5, 18)
            p = Fraction(good, n)
            return self._base(f"Một khảo sát có {n} người, trong đó {good} người chọn phương án A. Chọn ngẫu nhiên một người. Xác suất người đó chọn A là?", _fmt(p), f"P={good}/{n}={_fmt(p)}.", [_fmt(Fraction(n-good,n)), "1/2", "1/3"], "survey_probability", "real_life", "ratio")
        if variant == 1:
            p = Fraction(random.randint(2, 5), 10)
            return self._base(f"Một biến cố có xác suất {p}. Xác suất biến cố đối là bao nhiêu?", _fmt(1-p), f"P(Ā)=1-P(A)=1-{p}={_fmt(1-p)}.", [_fmt(p), _fmt(1+p), "0"], "complement_probability", "reasoning", "complement")
        if variant == 2:
            a, b = random.randint(2, 6), random.randint(2, 6)
            p = Fraction(a, a+b)
            return self._base(f"Một hộp có {a} sản phẩm đạt chuẩn và {b} sản phẩm chưa đạt. Chọn một sản phẩm. Xác suất chọn được sản phẩm đạt chuẩn là?", _fmt(p), f"P={a}/{a+b}={_fmt(p)}.", [_fmt(Fraction(b,a+b)), "1/2", "2/3"], "quality_probability", "application", "ratio")
        if variant == 3:
            n = random.randint(8, 15); k = random.randint(2, n-2)
            p = Fraction(math.comb(k, 2), math.comb(n, 2))
            return self._base(f"Trong {n} học sinh có {k} bạn thuộc câu lạc bộ. Chọn ngẫu nhiên 2 bạn. Xác suất cả hai đều thuộc câu lạc bộ là?", _fmt(p), f"P=C({k},2)/C({n},2)={_fmt(p)}.", [_fmt(Fraction(k,n)), "1/2", _fmt(Fraction(k*(k-1),n*n))], "club_two_draws", "multi_step", "combination_ratio")
        if variant == 4:
            return self._base("Một biến cố A có P(A)=0,7 và B có P(B)=0,5. Nếu A và B độc lập, P(A∩B) bằng bao nhiêu?", "0,35", "Với hai biến cố độc lập: P(A∩B)=P(A)P(B)=0,7×0,5=0,35.", ["0,2", "0,6", "1,2"], "independence", "reasoning", "independent_product")
        if variant == 5:
            return self._base("Một biến cố có xác suất 0,2. Sau 3 lần thử độc lập, xác suất không xảy ra biến cố trong cả 3 lần là bao nhiêu?", "0,512", "Mỗi lần không xảy ra có xác suất 0,8, nên 0,8³=0,512.", ["0,216", "0,6", "0,488"], "repeated_trials", "multi_step", "complement_power")
        if variant == 6:
            return self._base("Một hộp có 4 bi đỏ và 6 bi xanh. Biết viên đầu tiên lấy ra là đỏ và không hoàn lại. Xác suất viên thứ hai là đỏ là?", "1/3", "Sau khi lấy một bi đỏ, còn 3 đỏ trên tổng 9 viên nên xác suất là 3/9=1/3.", ["2/5", "4/10", "1/2"], "conditional_draw", "reverse", "conditional")
        return self._base("Nếu P(A)=0,4 thì mệnh đề nào đúng?", "0 ≤ P(A) ≤ 1", "Mọi xác suất đều nằm trong đoạn từ 0 đến 1.", ["P(A)>1", "P(A)<0", "P(A)=1,4"], "probability_theory", "theory_check", "axiom")

    def _counting(self, d):
        variant = random.randrange(8)
        if variant == 0:
            n,k=random.randint(6,10),random.randint(2,4); ans=math.comb(n,k)
            return self._base(f"Một lớp có {n} học sinh. Chọn {k} bạn vào đội, không xét thứ tự. Có bao nhiêu cách?", ans, f"Vì không xét thứ tự, số cách là C({n},{k})={ans}.", [ans+1, max(1,ans-k), ans+n], "combination", "calculation", "choose_without_order")
        if variant == 1:
            n,k=random.randint(6,9),random.randint(2,4); ans=math.perm(n,k)
            return self._base(f"Có {n} học sinh. Chọn và xếp {k} bạn vào {k} vị trí. Có bao nhiêu cách?", ans, f"Thứ tự quan trọng nên dùng A({n},{k})={ans}.", [math.comb(n,k), ans+1, ans-k], "arrangement", "calculation", "order_matters")
        if variant == 2:
            n=random.randint(5,8); ans=math.factorial(n)
            return self._base(f"Có {n} cuốn sách khác nhau xếp thành một hàng. Có bao nhiêu thứ tự?", ans, f"Số hoán vị là {n}!={ans}.", [math.perm(n,2), ans//n, ans+n], "permutation", "calculation", "all_order")
        if variant == 3:
            a,b,c=random.randint(2,5),random.randint(2,5),random.randint(2,4); ans=a*b*c
            return self._base(f"Có {a} áo, {b} quần và {c} đôi giày. Mỗi bộ gồm một món mỗi loại. Có bao nhiêu bộ?", ans, f"Quy tắc nhân: {a}×{b}×{c}={ans}.", [ans+a, ans-b, ans+c], "product_rule", "application", "multiplication_rule")
        if variant == 4:
            n=random.randint(5,9); k=random.randint(2,n-1); ans=math.comb(n-1,k-1)
            return self._base(f"Có {n} người, trong đó An bắt buộc có mặt. Chọn {k} người. Có bao nhiêu nhóm?", ans, f"Cố định An, chọn thêm {k-1} người từ {n-1}: C({n-1},{k-1})={ans}.", [math.comb(n,k), ans+1, max(1,ans-k)], "forced_member", "reasoning", "fixed_element")
        if variant == 5:
            n=random.randint(4,7); ans=n**3
            return self._base(f"Một mã gồm 3 chữ số, mỗi vị trí có {n} lựa chọn và được phép lặp. Có bao nhiêu mã?", ans, f"Có {n} lựa chọn cho mỗi vị trí: {n}³={ans}.", [math.perm(n,3), 3*n, ans-n], "code_with_repetition", "scenario", "multiplication_rule")
        if variant == 6:
            n=random.randint(5,9); k=random.randint(2,4); ans=math.comb(n,k)
            return self._base(f"Chọn {k} thành viên từ {n} người. Nếu đổi thứ tự các thành viên đã chọn thì có tạo nhóm mới không?", "Không", "Một nhóm chỉ phụ thuộc vào tập thành viên, không phụ thuộc thứ tự.", ["Có", "Chỉ khi k=2", "Chỉ khi n là số chẵn"], "order_check", "theory_check", "order_irrelevant")
        return self._base("Trong khai triển (a+b)^5, hệ số của a³b² là bao nhiêu?", "10", "Hệ số là C(5,2)=10.", ["5", "20", "15"], "newton_coefficient", "reasoning", "binomial")

    def _functions(self, d, game=""):
        variant=random.randrange(8)
        if "bắt điểm" in game:
            a=random.randint(-6,6) or 2; b=random.randint(-9,9); x=random.randint(-6,6); y=a*x+b
            return self._base(f"Điểm M({x};y) thuộc đồ thị y={a}x{_sign(b)}. Tìm y.", y, f"Thay x={x}: y={a}×{x}{_sign(b)}={y}.", [y+1,y-1,a+b], "function_point", "calculation", "substitution")
        if "tìm giao điểm" in game:
            x=random.randint(-5,6); m1=random.randint(1,5); m2=random.choice([-4,-3,-2,-1,2,3,4]); b1=random.randint(-6,6); b2=(m1-m2)*x+b1
            return self._base(f"Hai đường thẳng y={m1}x{_sign(b1)} và y={m2}x{_sign(b2)} cắt nhau. Hoành độ giao điểm là?", x, f"Cho hai biểu thức bằng nhau: ({m1}−{m2})x={b2-b1}, suy ra x={x}.", [x+1,x-1,0], "function_intersection", "reasoning", "equate_functions")
        a=random.choice([1,2,-1,-2]); h=random.randint(-5,5); k=random.randint(-8,8);
        if variant%2==0:
            return self._base(f"Đồ thị y={a}(x−{h})²{_sign(k)} có đỉnh tại điểm nào?", f"({h};{k})", f"Dạng y=a(x−h)²+k có đỉnh I({h};{k}).", [f"({-h};{k})",f"({h};{-k})",f"(0;{k})"], "function_vertex", "construction", "vertex", f"Tự vẽ: đặt đỉnh I({h};{k}) và trục đối xứng x={h}.")
        x=random.randint(-4,4); y=a*(x-h)**2+k
        return self._base(f"Cho y={a}(x−{h})²{_sign(k)}. Tính y khi x={x}.", y, f"Thay x={x} vào hàm được y={y}.", [y+1,y-1,k], "function_value", "calculation", "substitution")

    def _equations(self, d):
        variant=random.randrange(8)
        if variant==0:
            x=random.randint(-8,8); a=random.choice([2,3,4,5]); b=random.randint(-12,12); c=a*x+b
            return self._base(f"Giải phương trình {a}x {_sign(b)} = {c}.", x, f"{a}x={c-b}={a}×{x}, nên x={x}.", [x+1,x-1,-x], "linear_equation", "calculation", "inverse_operation")
        if variant==1:
            r1=random.randint(-6,6); r2=random.randint(-6,6); B=-(r1+r2); C=r1*r2
            ans=f"{r1}; {r2}"
            return self._base(f"Phương trình x² {_sign(B)}x {_sign(C)}=0 có hai nghiệm nào?", ans, f"Phân tích thành (x-{r1})(x-{r2})=0 nên nghiệm là {r1} và {r2}.", [f"{r1+1}; {r2}", f"{r1}; {r2+1}", f"{-r1}; {-r2}"], "quadratic_roots", "reasoning", "factorization")
        if variant==2:
            a=random.randint(2,6); x=random.randint(-5,5); y=random.randint(-5,5); b=random.randint(1,5); c=a*x+b*y; p=random.randint(1,5); q=random.randint(1,5)
            if a*q==b*p: p+=1
            r=p*x+q*y
            ans=f"({x}; {y})"
            return self._base(f"Giải hệ {a}x+{b}y={c}; {p}x+{q}y={r}.", ans, f"Thay ({x};{y}) vào hai phương trình đều đúng, và hai đường thẳng không song song nên nghiệm duy nhất là cặp đó.", [f"({x+1}; {y})", f"({x}; {y+1})", f"({-x}; {-y})"], "system", "multi_step", "linear_system")
        if variant==3:
            a=random.choice([1,2,3]); h=random.randint(-4,4); k=random.randint(-6,6); x=random.randint(-3,5); y=a*(x-h)**2+k
            return self._base(f"Cho y={a}(x-{h})²{_sign(k)}. Tính giá trị y khi x={x}.", y, f"Thay x={x}: y={a}({x}-{h})²{_sign(k)}={y}.", [y+1,y-1,y+2], "function_value", "calculation", "substitution")
        if variant==4:
            a=random.randint(2,8); b=random.randint(-10,10); c=random.randint(-10,10); D=b*b-4*a*c
            truth="hai nghiệm phân biệt" if D>0 else ("nghiệm kép" if D==0 else "vô nghiệm thực")
            return self._base(f"Với {a}x²{_sign(b)}x{_sign(c)}=0, biệt thức Δ={D}. Phương trình có trạng thái nào?", truth, f"Vì Δ={D}, nên phương trình có {truth}.", ["hai nghiệm phân biệt","nghiệm kép","vô nghiệm thực"], "quadratic_discriminant", "theory_check", "discriminant")
        if variant==5:
            m=random.randint(-5,5); x=m+2; return self._base(f"Tìm m để x={x} là nghiệm của phương trình x+m={x+m}.", m, f"Thế x={x}: {x}+m={x+m}, suy ra m={m}.", [m+1,m-1,-m], "parameter_reverse", "reverse", "parameter_from_root")
        if variant==6:
            return self._base("Một bạn giải 2x−6=0 và kết luận x=6. Lỗi nằm ở bước nào?", "Chia hai vế cho 2 nhưng phải được x=3", "Từ 2x=6 suy ra x=3, không phải x=6.", ["Chuyển 6 sang trái", "Đổi dấu 2", "Không có lỗi"], "mistake_linear", "mistake_check", "operation_error")
        return self._base("Nếu một phương trình có đúng một nghiệm kép thì biệt thức của phương trình bậc hai bằng bao nhiêu?", "0", "Phương trình bậc hai có nghiệm kép khi và chỉ khi Δ=0.", ["1", "−1", "4"], "quadratic_theory", "theory_check", "discriminant")

    def _inequality(self, d):
        variant=random.randrange(6); a=random.randint(2,7); b=random.randint(-10,10); c=random.randint(-8,8); r=Fraction(c-b,a)
        if variant==0:
            ans=f"x > {_fmt(r)}"; return self._base(f"Giải {a}x{_sign(b)}>{c}.", ans, f"{a}x>{c-b}, chia cho a>0 được x>{_fmt(r)}.", [f"x < {_fmt(r)}",f"x ≥ {_fmt(r)}",f"x ≤ {_fmt(r)}"], "linear_inequality", "calculation", "sign_preservation")
        if variant==1:
            ans=f"x < {_fmt(r)}"; return self._base(f"Giải {-a}x{_sign(b)}>{c}.", ans, f"Chia cho số âm {-a} phải đổi chiều: x<{_fmt(r)}.", [f"x > {_fmt(r)}",f"x ≥ {_fmt(r)}",f"x ≤ {_fmt(r)}"], "negative_inequality", "mistake_check", "sign_flip")
        p,q=random.randint(-5,5),random.randint(-5,5); return self._base(f"Giải hệ x>{p} và x≤{q}. Hệ có nghiệm khi nào?", f"{p} < x ≤ {q}" if p<q else "Không có nghiệm", "Giao hai miền nghiệm là khoảng nằm đồng thời bên phải p và không vượt quá q.", [f"x>{q}",f"x≤{p}",f"{q}<x≤{p}"], "inequality_system", "reasoning", "intersection")
        return self._base("Khi nhân cả hai vế của bất phương trình với một số âm, dấu bất phương trình phải làm gì?", "Đổi chiều", "Nhân hoặc chia với số âm làm đổi chiều bất phương trình.", ["Giữ nguyên","Đổi thành dấu bằng","Bỏ dấu"], "inequality_rule", "theory_check", "sign_flip")

    def _sequences(self, key, d):
        variant=random.randrange(7)
        if "cấp số cộng" in key or "cap_so_cong" in key:
            a1=random.randint(-5,8); r=random.choice([-4,-2,-1,2,3,5]); n=random.randint(5,12); an=a1+(n-1)*r
            if variant%2: return self._base(f"Một CSC có a₁={a1}, công sai {r}. Tính a₍{n}₎.", an, f"aₙ=a₁+(n−1)d={a1}+({n}−1)×{r}={an}.", [an+1,an-1,an+r], "arithmetic_term", "calculation", "nth_term")
            s=n*(a1+an)//2
            return self._base(f"CSC có a₁={a1}, d={r}. Tính tổng {n} số hạng đầu.", s, f"Sₙ=n(a₁+aₙ)/2={s}.", [s+n,s-n,an], "arithmetic_sum", "multi_step", "sum")
        if "cấp số nhân" in key or "cap_so_nhan" in key:
            a1=random.choice([1,2,3,-1,-2]); q=random.choice([2,3,-2]); n=random.randint(4,7); an=a1*q**(n-1)
            return self._base(f"CSN có a₁={a1}, công bội q={q}. Tính a₍{n}₎.", an, f"aₙ=a₁qⁿ⁻¹={an}.", [an+q,an-q,a1*q], "geometric_term", "calculation", "nth_term")
        a=random.randint(1,8); d0=random.randint(1,5); n=random.randint(4,10); ans=a+(n-1)*d0
        return self._base(f"Dãy có dạng aₙ={a}+({d0})(n−1). Số hạng thứ {n} bằng bao nhiêu?", ans, f"Thay n={n}: aₙ={ans}.", [ans-1,ans+1,a+d0*n], "sequence_formula", "calculation", "substitution")

    def _trig(self, key, d):
        variant=random.randrange(12)
        values=[("0", "0"), ("π/6", "1/2"), ("π/4", "√2/2"), ("π/3", "√3/2"), ("π/2", "1"), ("2π/3", "√3/2"), ("3π/4", "√2/2"), ("5π/6", "1/2")]
        if variant < len(values):
            x,ans=values[variant]
            fn=random.choice(["sin","cos"]);
            if fn == "cos":
                cmap={"0":"1","π/6":"√3/2","π/4":"√2/2","π/3":"1/2","π/2":"0","2π/3":"−1/2","3π/4":"−√2/2","5π/6":"−√3/2"}; ans=cmap[x]
            return self._base(f"Tính {fn}({x}).", ans, f"Dùng giá trị lượng giác của góc đặc biệt: {fn}({x})={ans}.", ["0","1/2","√2/2","√3/2"], "trig_value", "calculation", "special_angle")
        if variant == 8:
            return self._base("Hàm số y=sin x có chu kỳ bằng bao nhiêu?", "2π", "Sin lặp lại sau mỗi 2π.", ["π","π/2","4π"], "trig_period", "theory_check", "periodicity")
        if variant == 9:
            return self._base("Hàm số y=cos x có chu kỳ bằng bao nhiêu?", "2π", "Cos cũng lặp lại sau mỗi 2π.", ["π","π/2","4π"], "trig_cos_period", "theory_check", "periodicity")
        if variant == 10:
            return self._base("Giá trị lớn nhất của sin x là bao nhiêu?", "1", "Với mọi x, −1≤sin x≤1 nên GTLN là 1.", ["0","−1","2"], "trig_sine_range", "reasoning", "range")
        return self._base("Giá trị nhỏ nhất của cos x là bao nhiêu?", "−1", "Với mọi x, −1≤cos x≤1 nên GTNN là −1.", ["0","1","−2"], "trig_cos_range", "reasoning", "range")

    def _calculus(self, key, d):
        variant=random.randrange(8)
        broad = "ung_dung_dao_ham" in key or "khao_sat_ham_so" in key
        if ("tiếp tuyến" in key or "tiep_tuyen" in key) and not broad:
            a=random.randint(1,4); x0=random.randint(-3,3); y0=a*x0*x0; slope=2*a*x0
            return self._base(f"Cho f(x)={a}x². Hệ số góc tiếp tuyến tại x={x0} là bao nhiêu?", slope, f"f'(x)=2·{a}x, nên f'({x0})={slope}.", [slope+1,slope-1,a], "tangent_slope", "calculation", "derivative")
        if ("tiệm cận" in key or "tien_can" in key) and not broad:
            variant=random.randrange(5)
            if variant==0:
                return self._base("Đồ thị y=1/x có tiệm cận đứng nào?", "x=0", "Hàm không xác định tại x=0.", ["y=0","x=1","y=1"], "vertical_asymptote", "theory_check", "domain_behavior")
            if variant==1:
                return self._base("Đồ thị y=1/x có tiệm cận ngang nào?", "y=0", "Khi x tiến tới vô cực, 1/x tiến tới 0.", ["x=0","y=1","x=1"], "horizontal_asymptote", "reasoning", "limit")
            a=random.randint(2,9)
            if variant==2:
                return self._base(f"Hàm y={a}/x có tiệm cận đứng nào?", "x=0", "Mẫu số bằng 0 tại x=0.", ["y=0","x=1","y="+str(a)], "vertical_asymptote_scaled", "calculation", "domain_behavior")
            b=random.randint(-5,5); c=random.choice([1,2,3])
            return self._base(f"Hàm y=({a}x+{b})/({c}x+1) có tiệm cận ngang nào?", f"y={a/c:g}", "Tỉ số hệ số của các hạng bậc cao nhất cho tiệm cận ngang.", [f"y={b}",f"x={-1/c:g}","y=0"], "rational_horizontal_asymptote", "reasoning", "leading_coefficients")
        if ("đơn điệu" in key or "tinh_don_dieu" in key) and not broad:
            variant=random.randrange(6)
            if variant<3:
                a=random.choice([-7,-4,-2,1,2,5,8]); b=random.randint(-9,9); direction="Đồng biến" if a>0 else "Nghịch biến"
                return self._base(f"Trên R, hàm f(x)={a}x{_sign(b)} là hàm gì?", direction, f"Hệ số góc {a} {'dương' if a>0 else 'âm'} nên hàm {direction.lower()}.", ["Đồng biến" if direction=="Nghịch biến" else "Nghịch biến","Không đổi","Không xác định"], "monotonic_linear", "reasoning", "slope_sign")
            if variant==3:
                a=random.choice([1,2,3]); h=random.randint(-5,5); return self._base(f"Hàm f(x)={a}(x−{h})² đồng biến trên khoảng nào?", f"({h};+∞)", f"f'(x)=2{a}(x−{h}), dương khi x>{h}.", [f"(−∞;{h})",f"R",f"({h-1};+∞)"], "monotonic_parabola", "reasoning", "derivative_sign")
            if variant==4:
                return self._base("Nếu f'(x)<0 trên một khoảng thì hàm số có tính chất gì trên khoảng đó?", "Nghịch biến", "Đạo hàm âm trên khoảng suy ra hàm nghịch biến trên khoảng đó.", ["Đồng biến","Không đổi","Luôn bằng 0"], "monotonic_derivative", "theory_check", "derivative_sign")
            return self._base("Nếu f'(x)>0 trên một khoảng thì hàm số có tính chất gì trên khoảng đó?", "Đồng biến", "Đạo hàm dương trên khoảng suy ra hàm đồng biến trên khoảng đó.", ["Nghịch biến","Không đổi","Luôn bằng 0"], "monotonic_derivative_positive", "theory_check", "derivative_sign")
        if ("cực trị" in key or "cuc_tri" in key) and not broad:
            h=random.randint(-4,4); k=random.randint(-6,6); return self._base(f"Hàm y=(x−{h})²+{k} có GTNN bằng bao nhiêu?", k, f"Parabol mở lên và đạt đỉnh tại ({h},{k}), nên GTNN={k}.", [k+1,k-1,0], "extremum_parabola", "reasoning", "vertex")
        if ("gtln" in key or "gtnn" in key) and not broad:
            a=random.randint(1,5); lo=random.randint(-3,0); hi=random.randint(1,5); vals=[a*lo*lo,a*hi*hi]; mx=max(vals); mn=0
            return self._base(f"Trên đoạn [{lo};{hi}], hàm f(x)=x² đạt GTNN bằng bao nhiêu?", mn, "Đoạn chứa x=0 nên x² nhỏ nhất bằng 0 tại x=0.", [1,mx,lo*hi], "absolute_extremum", "application", "closed_interval")
        if ("tương giao" in key or "tuong_giao" in key) and not broad:
            a=random.randint(1,4); b=random.randint(-5,5); x=random.randint(-3,3); y=a*x+b
            return self._base(f"Đường thẳng y={a}x{_sign(b)} cắt trục Oy tại điểm có tung độ bằng bao nhiêu?", b, f"Cho x=0 thì y={b}.", [a,x,y], "graph_intersection", "data_interpretation", "axis_intersection")
        if broad and variant == 0:
            a=random.randint(1,4); x=random.randint(-4,4); ans=2*a*x
            return self._base(f"Cho f(x)={a}x²+1. Tính f'({x}).", ans, f"f'(x)=2·{a}x, nên f'({x})={ans}.", [ans+1,ans-1,a*x], "broad_derivative", "calculation", "power_rule")
        if broad and variant == 1:
            h=random.randint(-4,4); k=random.randint(-6,6)
            return self._base(f"Hàm y=(x−{h})²+{k} có GTNN bằng bao nhiêu?", k, f"Parabol mở lên nên GTNN là {k} tại x={h}.", [k+1,k-1,0], "broad_extremum", "reasoning", "vertex")
        if broad and variant == 2:
            return self._base("Hàm y=1/x có bao nhiêu tiệm cận?", "2", "Đồ thị có tiệm cận đứng x=0 và tiệm cận ngang y=0.", ["0","1","3"], "broad_asymptote", "theory_check", "asymptote_count")
        if broad and variant == 3:
            return self._base("Hàm f(x)=x³ có đồng biến trên R không?", "Có", "f'(x)=3x²≥0 trên R và hàm x³ tăng trên R.", ["Không","Chỉ trên (0;+∞)","Chỉ trên (−∞;0)"], "broad_monotonic", "reasoning", "derivative_sign")
        if broad and variant == 4:
            a=random.randint(1,5); b=random.randint(-4,4); x=random.randint(-3,3); y=a*x+b
            return self._base(f"Đường thẳng y={a}x{_sign(b)} cắt trục Oy tại tung độ nào?", b, f"Đặt x=0 thì y={b}.", [a,x,y+1], "broad_intersection", "data_interpretation", "axis_intersection")
        if broad and variant == 5:
            return self._base("Nếu f'(x)>0 trên một khoảng thì f trên khoảng đó có tính chất gì?", "Đồng biến", "Đạo hàm dương trên khoảng suy ra hàm số đồng biến trên khoảng đó.", ["Nghịch biến","Không đổi","Luôn bằng 0"], "broad_derivative_sign", "theory_check", "sign_rule")
        if broad and variant == 6:
            return self._base("Tại điểm cực trị của hàm khả vi, đạo hàm bằng bao nhiêu?", "0", "Nếu hàm khả vi tại điểm cực trị thì đạo hàm tại đó bằng 0.", ["1","−1","Không xác định"], "broad_extremum_condition", "theory_check", "necessary_condition")
        a=random.randint(1,5); b=random.randint(-6,6); x=random.randint(-4,4); ans=2*a*x+b
        return self._base(f"Cho f(x)={a}x²{_sign(b)}x+3. Tính f'({x}).", ans, f"f'(x)=2·{a}x{_sign(b)}, nên f'({x})={ans}.", [ans+2,ans-2,a*x+b], "derivative_calculation", "calculation", "power_rule")

    def _integral(self, d):
        variant=random.randrange(5); a=random.randint(1,6); b=random.randint(-4,5); lo=random.randint(0,2); hi=lo+random.randint(2,5)
        if variant==0:
            ans=Fraction(a,2)*(hi*hi-lo*lo)+b*(hi-lo)
            return self._base(f"Tính ∫[{lo},{hi}]({a}x{_sign(b)})dx.", _fmt(ans), f"Nguyên hàm là {a}/2·x²{_sign(b)}x. Thay cận được {_fmt(ans)}.", [_fmt(ans+1),_fmt(ans-1),_fmt(ans+2)], "definite_integral", "calculation", "antiderivative")
        if variant==1:
            return self._base(f"Một vật có vận tốc v(t)={a}t. Quãng đường đi từ t=0 đến t={hi} là bao nhiêu?", _fmt(Fraction(a*hi*hi,2)), f"Quãng đường là ∫₀^{hi}{a}t dt={_fmt(Fraction(a*hi*hi,2))}.", [_fmt(a*hi),_fmt(a*hi*hi),_fmt(Fraction(a*hi*hi,4))], "motion_integral", "real_life", "accumulation")
        return self._base("Một nguyên hàm của 2x là biểu thức nào?", "x²+C", "Vì (x²)'=2x nên nguyên hàm là x²+C.", ["2x²+C","x+C","2+C"], "basic_antiderivative", "theory_check", "reverse_derivative")

    def _complex(self, d):
        variant=random.randrange(5); a=random.randint(-5,5); b=random.randint(-5,5)
        if variant==0:
            ans=a*a+b*b; return self._base(f"Cho z={a}{'+' if b>=0 else ''}{b}i. Tính |z|².", ans, f"|z|²={a}²+{b}²={ans}.", [ans+1,max(0,ans-1),ans+2], "complex_modulus", "calculation", "modulus")
        if variant==1:
            return self._base(f"Số phức z={a}{'+' if b>=0 else ''}{b}i có phần thực bằng bao nhiêu?", a, "Phần thực là hệ số của 1, tức là a.", [b,-a,-b], "complex_real", "calculation", "component")
        if variant==2:
            return self._base(f"Liên hợp của z={a}{'+' if b>=0 else ''}{b}i là gì?", f"{a}{'-' if b>=0 else '+'}{abs(b)}i", "Giữ phần thực và đổi dấu phần ảo.", [f"{-a}{'+' if b>=0 else '-'}{abs(b)}i", f"{a}{'+' if b>=0 else '-'}{abs(b)}i", f"{b}+{a}i"], "complex_conjugate", "reasoning", "conjugation")
        return self._base("Nếu z=a+bi thì |z|² bằng biểu thức nào?", "a²+b²", "Theo định nghĩa môđun: |z|=√(a²+b²), nên bình phương là a²+b².", ["a²−b²","a+b","ab"], "complex_definition", "theory_check", "definition")

    def _geometry(self, key, d):
        variant=random.randrange(10)
        broad2d = "hinh_hoc_10" in key or "geometry" in key
        broad3d = any(x in key for x in ("hinh_khong_gian", "hinh_hoc_khong_gian", "thiet_dien_hinh_khong_gian_11", "goc_khoang_cach_11", "goc_khoang_cach_oxyz", "hình học không gian"))
        broad_line = "duong_thang" in key or "đường thẳng" in key
        if ("vectơ" in key or "vector" in key) and not (broad2d or broad3d or broad_line):
            ax,ay,bx,by=[random.randint(-5,5) for _ in range(4)]
            if variant%2:
                ans=ax*bx+ay*by
                return self._base(f"Cho u=({ax};{ay}), v=({bx};{by}). Tính u·v.", ans, f"u·v={ax}×{bx}+{ay}×{by}={ans}.", [ans+1,ans-1,ax+ay+bx+by], "vector_dot", "calculation", "coordinate_product")
            return self._base(f"Cho A({ax};{ay}), B({bx};{by}). Tọa độ vectơ AB là?", f"({bx-ax}; {by-ay})", f"AB=(x_B-x_A;y_B-y_A)=({bx-ax};{by-ay}).", [f"({bx+ax};{by+ay})",f"({ax-bx};{ay-by})",f"({ax};{ay})"], "vector_coordinates", "calculation", "difference_coordinates")
        if ("đường tròn" in key or "duong_tron" in key or "mat_cau" in key) and not (broad2d or broad3d or broad_line):
            h,kc=random.randint(-5,5),random.randint(-5,5); r=random.randint(2,12)
            ans=f"(x{_sign(-h)})²+(y{_sign(-kc)})²={r*r}"
            return self._base(f"Đường tròn tâm I({h};{kc}) bán kính {r} có phương trình nào?", ans, f"Dùng (x−h)²+(y−k)²=r², nên phương trình là {ans}.", [f"(x{_sign(-h)})²+(y{_sign(-kc)})²={r}",f"x²+y²={r*r}",f"(x{_sign(h)})²+(y{_sign(kc)})²={r*r}"], "circle_equation", "construction", "circle_model", f"Tự vẽ: đặt tâm I({h};{kc}), rồi lấy bán kính {r} đơn vị và vẽ đường tròn.")
        if ("mặt phẳng" in key or "mat_phang" in key) and not (broad2d or broad3d or broad_line):
            a,b,c,d0=[random.randint(-4,4) or 1 for _ in range(4)]
            return self._base(f"Trong Oxyz, mặt phẳng có dạng {a}x+{b}y+{c}z+{d0}=0. Một vectơ pháp tuyến có thể chọn là?", f"({a};{b};{c})", "Các hệ số của x,y,z tạo thành một vectơ pháp tuyến của mặt phẳng.", [f"({b};{c};{d0})",f"({a};{d0};{c})",f"(1;1;1)"], "plane_normal", "theory_check", "normal_vector")
        if ("tọa độ" in key or "toa_do" in key) and not (broad2d or broad3d or broad_line):
            x1,y1=random.randint(-5,5),random.randint(-5,5); x2,y2=random.randint(-5,5),random.randint(-5,5); ans=Fraction(x1+x2,2),Fraction(y1+y2,2)
            return self._base(f"Trung điểm M của A({x1};{y1}) và B({x2};{y2}) là?", f"({_fmt(ans[0])}; {_fmt(ans[1])})", f"M=((x₁+x₂)/2;(y₁+y₂)/2)=({_fmt(ans[0])};{_fmt(ans[1])}).", [f"({x1+x2};{y1+y2})",f"({x2-x1};{y2-y1})",f"({x1};{y1})"], "midpoint", "calculation", "midpoint_formula", "Tự vẽ: chấm A và B trên mặt phẳng tọa độ rồi đánh dấu điểm nằm chính giữa.")
        if ("thể tích" in key or "the_tich" in key or "hình chóp" in key) and not (broad2d or broad3d or broad_line):
            s=random.randint(6,20); h=random.randint(3,10); ans=Fraction(s*h,3)
            return self._base(f"Một hình chóp có diện tích đáy {s} cm² và chiều cao {h} cm. Thể tích là?", f"{_fmt(ans)} cm³", f"V=1/3·S_đáy·h={s}·{h}/3={_fmt(ans)} cm³.", [f"{s*h} cm³",f"{_fmt(Fraction(s*h,2))} cm³",f"{s+h} cm³"], "pyramid_volume", "real_life", "volume_formula", "Tự vẽ: vẽ đa giác đáy, chọn một đỉnh ngoài mặt đáy và nối đỉnh đó với các đỉnh của đáy.")
        if ("góc" in key or "khoảng cách" in key) and not (broad2d or broad3d or broad_line):
            return self._base("Trong hình học không gian, khoảng cách từ một điểm đến một mặt phẳng được đo theo đoạn nào?", "Đoạn vuông góc từ điểm đến mặt phẳng", "Khoảng cách từ điểm đến mặt phẳng là độ dài đoạn vuông góc kẻ từ điểm đó đến mặt phẳng.", ["Đoạn bất kỳ nối điểm với mặt phẳng","Đoạn song song với mặt phẳng","Đường trung tuyến"], "space_distance", "theory_check", "perpendicular_distance", "Tự vẽ: vẽ mặt phẳng (P), điểm A ngoài (P), rồi dựng AH vuông góc (P).")
        if broad_line:
            mode=random.randrange(6)
            if "oxyz" in key:
                a,b,c=random.randint(-5,5) or 1, random.randint(-5,5) or 1, random.randint(-5,5) or 1
                return self._base(f"Một đường thẳng trong Oxyz có vectơ chỉ phương u=({a};{b};{c}). Vectơ nào cùng phương với u?", f"({2*a};{2*b};{2*c})", "Hai vectơ cùng phương khi một vectơ là bội khác 0 của vectơ kia.", [f"({a};{b};{c+1})",f"({a+1};{b};{c})",f"({-a};{b};{c})"], "line_direction_3d", "reasoning", "parallel_vectors")
            if mode==0:
                m=random.randint(-5,5); b=random.randint(-6,6); return self._base(f"Đường thẳng y={m}x{_sign(b)} có hệ số góc bằng bao nhiêu?", m, f"Trong y=mx+b, hệ số góc là m={m}.", [b,m+1,m-1], "line_slope", "calculation", "coefficient")
            if mode==1:
                m=random.choice([-4,-2,1,3]); return self._base(f"Một đường thẳng có hệ số góc {m}. Đường thẳng nào song song với nó?", f"Hệ số góc {m}", "Hai đường thẳng song song có cùng hệ số góc.", [f"Hệ số góc {-m}",f"Hệ số góc {m+1}","Hệ số góc 0"], "parallel_lines", "theory_check", "slope_equality")
            if mode==2:
                return self._base("Hai đường thẳng có hệ số góc khác nhau thì quan hệ thế nào trong mặt phẳng?", "Cắt nhau", "Hai đường thẳng không song song có hệ số góc khác nhau nên cắt nhau tại một điểm.", ["Song song","Trùng nhau","Luôn vuông góc"], "line_intersection", "reasoning", "slope_comparison")
            if mode==3:
                a,b=random.randint(2,8),random.randint(-5,5); x=random.randint(-4,4); y=a*x+b
                return self._base(f"Cho đường thẳng y={a}x{_sign(b)}. Tìm tung độ điểm có hoành độ x={x}.", y, f"Thay x={x}: y={a}×{x}{_sign(b)}={y}.", [y+1,y-1,a+b], "line_point", "calculation", "substitution")
            if mode==4:
                return self._base("Khoảng cách từ điểm đến đường thẳng được đo theo đoạn nào?", "Đoạn vuông góc", "Khoảng cách ngắn nhất là độ dài đoạn vuông góc.", ["Đoạn song song","Đoạn bất kỳ","Đoạn trung tuyến"], "line_distance", "theory_check", "perpendicular")
            return self._base("Hai đường thẳng vuông góc có tích hai hệ số góc bằng bao nhiêu?", "−1", "Với hai đường thẳng không đứng, vuông góc khi m₁m₂=−1.", ["0","1","2"], "perpendicular_slopes", "theory_check", "slope_product")

        if broad2d or broad3d:
            mode = random.randrange(8)
            if mode == 0:
                a,b=random.randint(3,9),random.randint(4,12)
                c=math.sqrt(a*a+b*b)
                if abs(c-round(c)) < 1e-9:
                    c=int(round(c))
                return self._base(f"Một tam giác vuông có hai cạnh góc vuông {a} cm và {b} cm. Cạnh huyền bằng bao nhiêu?", _fmt(c), f"Theo Pythagore, c=√({a}²+{b}²)=√{a*a+b*b}.", [str(a+b),str(abs(b-a)),str(round(float(c)+1,2))], "geometry_pythagorean", "application", "pythagorean", f"Tự vẽ: dựng tam giác vuông và ghi hai cạnh góc vuông {a} cm, {b} cm.")
            if mode == 1:
                A=random.randint(35,75); B=random.randint(25,80-A+35); C=180-A-B
                return self._base(f"Một tam giác có hai góc A={A}° và B={B}°. Góc C bằng bao nhiêu?", C, f"A+B+C=180° nên C=180−{A}−{B}={C}°.", [A+B,180-A,180-B], "triangle_angle", "calculation", "angle_sum", "Tự vẽ: vẽ tam giác ABC và ghi A={A}°, B={B}°.")
            if mode == 2:
                h,kc=random.randint(-4,4),random.randint(-4,4); r=random.randint(2,10); ans=f"(x{_sign(-h)})²+(y{_sign(-kc)})²={r*r}"
                return self._base(f"Đường tròn tâm I({h};{kc}) bán kính {r} có phương trình nào?", ans, f"Dùng (x−h)²+(y−k)²=r².", [f"x²+y²={r*r}",f"(x{_sign(h)})²+(y{_sign(kc)})²={r*r}",f"(x{_sign(-h)})²+(y{_sign(-kc)})²={r}"], "geometry_circle", "construction", "circle_model", f"Tự vẽ: đặt tâm I({h};{kc}) và bán kính {r}.")
            if mode == 3:
                x1,y1=random.randint(-5,5),random.randint(-5,5); x2,y2=random.randint(-5,5),random.randint(-5,5); ans=f"({x2-x1}; {y2-y1})"
                return self._base(f"Cho A({x1};{y1}), B({x2};{y2}). Tọa độ vectơ AB là?", ans, "Lấy tọa độ điểm cuối trừ tọa độ điểm đầu.", [f"({x1+x2};{y1+y2})",f"({x1-x2};{y1-y2})",f"({x1};{y1})"], "geometry_vector", "calculation", "coordinate_difference")
            if mode == 4:
                S=random.randint(6,24); h=random.randint(3,12); ans=Fraction(S*h,3)
                return self._base(f"Hình chóp có diện tích đáy {S} cm² và chiều cao {h} cm. Thể tích bằng?", f"{_fmt(ans)} cm³", f"V=S·h/3={S}·{h}/3={_fmt(ans)} cm³.", [f"{S*h} cm³",f"{_fmt(Fraction(S*h,2))} cm³",f"{S+h} cm³"], "geometry_volume", "real_life", "pyramid_volume", f"Tự vẽ: vẽ hình chóp, mặt đáy và đường cao {h} cm.")
            if mode == 5:
                return self._base("Trong không gian, nếu một đường thẳng vuông góc với hai đường thẳng cắt nhau nằm trong một mặt phẳng thì đường thẳng đó quan hệ thế nào với mặt phẳng?", "Vuông góc với mặt phẳng", "Đây là định lý đường thẳng vuông góc với mặt phẳng.", ["Song song với mặt phẳng","Nằm trong mặt phẳng","Không xác định"], "space_perpendicular_theorem", "theory_check", "perpendicularity", "Tự vẽ: vẽ mặt phẳng (P), hai đường thẳng cắt nhau trong (P) và đường thẳng d vuông góc cả hai.")
            if mode == 6:
                r=random.randint(2,8); ans=f"{r}√2"
                return self._base(f"Hình vuông cạnh {r} cm có đường chéo bằng bao nhiêu?", ans, f"Đường chéo d=r√2={r}√2 cm.", [f"{2*r} cm",f"{r} cm",f"{r*r} cm"], "square_diagonal", "application", "pythagorean")
            return self._base("Khoảng cách từ một điểm đến một đường thẳng được đo bằng đoạn nào?", "Đoạn vuông góc", "Khoảng cách ngắn nhất từ điểm đến đường thẳng là độ dài đoạn vuông góc.", ["Đoạn song song","Đoạn bất kỳ","Đoạn trung tuyến"], "point_line_distance", "theory_check", "perpendicular_distance", "Tự vẽ: từ điểm A ngoài đường thẳng d, dựng AH vuông góc d.")

        a,b=random.randint(3,9),random.randint(4,10); c=math.isqrt(a*a+b*b)
        if c*c==a*a+b*b:
            return self._base(f"Một tam giác vuông có hai cạnh góc vuông dài {a} cm và {b} cm. Cạnh huyền dài bao nhiêu?", c, f"Theo Pythagore: c²={a}²+{b}²={c*c}, nên c={c} cm.", [a+b,abs(b-a),c+1], "right_triangle_length", "application", "pythagorean", "Tự vẽ: dựng tam giác ABC vuông tại A, đặt hai cạnh góc vuông lần lượt là a và b.")
        return self._base("Tổng ba góc trong một tam giác bằng bao nhiêu?", "180°", "Tổng ba góc trong mọi tam giác bằng 180°.", ["90°","270°","360°"], "triangle_angle_sum", "theory_check", "angle_sum", "Tự vẽ: vẽ một tam giác bất kỳ và ghi ba góc A, B, C.")

    def _statistics(self, d):
        variant=random.randrange(6); data=[random.randint(2,20) for _ in range(random.randint(5,8))]
        if variant==0:
            ans=Fraction(sum(data),len(data)); return self._base(f"Cho mẫu số liệu {data}. Tính số trung bình cộng.", _fmt(ans), f"x̄={sum(data)}/{len(data)}={_fmt(ans)}.", [_fmt(ans+1),_fmt(ans-1),_fmt(ans+2)], "mean", "data_interpretation", "average")
        data=sorted(data); mid=data[len(data)//2] if len(data)%2 else Fraction(data[len(data)//2-1]+data[len(data)//2],2)
        return self._base(f"Mẫu số liệu đã sắp xếp là {data}. Trung vị bằng bao nhiêu?", _fmt(mid), "Lấy giá trị giữa; nếu có hai giá trị giữa thì lấy trung bình của chúng.", [_fmt(data[0]),_fmt(data[-1]),_fmt(Fraction(sum(data),len(data)))], "median", "data_interpretation", "central_value")

    def _sets_logic(self, d):
        variant=random.randrange(5)
        if variant==0:
            a=set(random.sample(range(1,13),random.randint(3,6))); b=set(random.sample(range(1,13),random.randint(3,6))); ans=len(a&b)
            return self._base(f"Cho A={sorted(a)}, B={sorted(b)}. Số phần tử của A∩B là?", ans, f"Phần giao là {sorted(a&b)}, có {ans} phần tử.", [len(a|b),len(a),len(b)], "set_intersection", "calculation", "intersection")
        if variant==1:
            return self._base("Mệnh đề 'x>2' phủ định thành mệnh đề nào?", "x≤2", "Phủ định của x>2 là x≤2.", ["x<2","x≥2","x=2"], "statement_negation", "reasoning", "negation")
        return self._base("Nếu A⊂B thì mệnh đề nào chắc chắn đúng?", "Mọi phần tử của A đều thuộc B", "Đó là định nghĩa của quan hệ tập con.", ["A và B có cùng số phần tử","Mọi phần tử B thuộc A","A không có phần tử"], "subset_definition", "theory_check", "definition")

    def _radical(self, d):
        a=random.randint(2,12); k=random.randint(2,6); n=a*a*k
        return self._base(f"Rút gọn √{n}.", f"{a}√{k}", f"√{n}=√({a*a}·{k})={a}√{k}.", [f"{a*k}",f"{k}√{a}",f"{a}+√{k}"], "radical_simplify", "calculation", "perfect_square_factor")

    def _identity(self, d):
        a=random.randint(2,8); b=random.randint(1,7); x=a+b
        return self._base(f"Khai triển ({a}+{b})² được kết quả nào?", x*x, f"({a}+{b})²={a*a}+2·{a}·{b}+{b*b}={x*x}.", [a*a+b*b,(a-b)**2,x*x+1], "identity_expand", "calculation", "perfect_square")

    def _rational(self, d):
        a=random.randint(2,8); b=random.randint(1,6); x=random.randint(1,5); den=x+b; num=a*x+a*b; ans=a
        return self._base(f"Với x≠{-b}, rút gọn ( {a}x + {a*b} )/(x+{b}).", ans, f"Tử số={a}(x+{b}), nên phân thức bằng {a} khi x≠{-b}.", [a+1,a-1,b], "rational_simplify", "reasoning", "factor_cancel")

    def _number_theory(self, key, d):
        if "chia dư" in key or "remainder" in key:
            m=random.randint(4,11); a=random.randint(20,100); r=a%m
            return self._base(f"Tính số dư khi {a} chia cho {m}.", r, f"{a}={a//m}·{m}+{r}, nên số dư là {r}.", [r+1,(r-1)%m,(r+2)%m], "remainder_direct", "calculation", "division_algorithm")
        n=random.randint(100,999); s=sum(map(int,str(n))); return self._base(f"Số {n} có chia hết cho 3 không?", "Có" if s%3==0 else "Không", f"Tổng chữ số là {s}; số chia hết cho 3 khi tổng chữ số chia hết cho 3.", ["Không" if s%3==0 else "Có","Chỉ khi số chẵn","Không thể biết"], "divisibility_rule", "reasoning", "digit_sum")

    def _exponential_log(self, key, d):
        a=random.randint(2,7); p=random.randint(1,5); n=a**p
        if "bpt_log" in key:
            base=random.choice([2,3,5]); p=random.randint(1,4); n=base**p
            return self._base(f"Giải bất phương trình log cơ số {base} của x > {p}.", f"x>{n}", f"Vì cơ số {base}>1, log_{base}(x)>{p} tương đương x>{base}^{p}={n}, đồng thời x>0 đã được thỏa.", [f"x<{n}",f"x≥{n}",f"0<x<{n}"], "log_inequality", "reasoning", "monotonic_log")
        if "bpt_mu" in key:
            base=random.choice([2,3,5]); p=random.randint(1,4); n=base**p
            return self._base(f"Giải {base}^x>{n}.", f"x>{p}", f"Hàm mũ cơ số {base}>1 tăng, nên x>{p}.", [f"x<{p}",f"x≥{p}",f"x≤{p}"], "exp_inequality", "reasoning", "monotonic_exp")
        if "pt_log" in key:
            base=random.choice([2,3,5,10]); p=random.randint(1,5); n=base**p
            return self._base(f"Giải log cơ số {base} của x = {p}.", n, f"Theo định nghĩa logarit, x={base}^{p}={n}.", [p,base+p,base*p], "log_equation", "reverse", "inverse_log")
        if "pt_mu" in key:
            return self._base(f"Giải {a}^x={n}.", p, f"{n}={a}^{p} nên x={p}.", [p+1,p-1,a*p], "exponential_equation", "reverse", "inverse_exponent")
        if "ham_logarit" in key or "hàm số logarit" in key:
            base=random.choice([2,3,4,5,7,10]); variant=random.randrange(4); x=random.randint(1,8)
            if variant==0:
                return self._base(f"Tập xác định của y=log_{base}(x) là gì?", "x>0", "Đối số của logarit phải dương.", ["x≥0","x<0","mọi x"], "log_domain", "theory_check", "domain")
            if variant==1:
                return self._base(f"Hàm y=log_{base}(x) đồng biến hay nghịch biến trên (0;+∞)?", "Đồng biến", f"Vì cơ số {base}>1 nên hàm logarit đồng biến.", ["Nghịch biến","Không đổi","Không xác định"], "log_monotonic", "reasoning", "base_rule")
            n=base**x
            return self._base(f"Tính log cơ số {base} của {n}.", x, f"Vì {base}^{x}={n}, log_{base}({n})={x}.", [x+1,x-1,base*x], "log_value", "calculation", "inverse_exponent")
        if "ham_mu" in key or "hàm số mũ" in key:
            base=random.choice([2,3,4,5,7]); variant=random.randrange(4); x=random.randint(1,6); n=base**x
            if variant==0:
                return self._base(f"Tập xác định của y={base}^x là gì?", "R", "Hàm số mũ xác định với mọi số thực x.", ["x>0","x≥0","x<0"], "exp_domain", "theory_check", "domain")
            if variant==1:
                return self._base(f"Hàm y={base}^x đồng biến hay nghịch biến trên R?", "Đồng biến", f"Vì cơ số {base}>1 nên hàm mũ đồng biến.", ["Nghịch biến","Không đổi","Không xác định"], "exp_monotonic", "reasoning", "base_rule")
            return self._base(f"Tính {base}^{x}.", n, f"{base}^{x}={n}.", [n+base,n-base,max(1,n//base)], "exp_value", "calculation", "power")
        return self._base(f"Tính log cơ số {a} của {n}.", p, f"Vì {a}^{p}={n}, nên log_{a}({n})={p}.", [p+1,p-1,n], "log_value", "calculation", "inverse_exponent")

    def _real_world(self, key, d):
        variant=random.randrange(5)
        if variant==0:
            price=random.randint(50,300)*1000; pct=random.choice([10,15,20,25]); ans=price*(100-pct)//100
            return self._base(f"Một món hàng giá {price:,} đồng được giảm {pct}%. Giá sau giảm là bao nhiêu?".replace(",","."), ans, f"Giá mới={price}×(1−{pct}/100)={ans} đồng.", [price-pct,price*(100+pct)//100,price//100], "discount", "real_life", "percentage")
        if variant==1:
            v=random.randint(40,90); t=random.randint(2,5); ans=v*t
            return self._base(f"Một xe đi đều với vận tốc {v} km/h trong {t} giờ. Quãng đường đi được là?", ans, f"s=v·t={v}×{t}={ans} km.", [v+t,v*(t-1),ans+v], "motion_distance", "real_life", "rate_time")
        if variant==2:
            return self._base("Một khu vườn hình chữ nhật có chu vi 40 m. Nếu chiều dài hơn chiều rộng 6 m, chiều rộng là bao nhiêu?", "7 m", "Gọi rộng x, dài x+6. 2(x+x+6)=40 nên x=7.", ["6 m","8 m","10 m"], "rectangle_model", "multi_step", "system_model")
        if variant==3:
            a=random.randint(4,10); b=random.randint(2,8); c=random.randint(1,6); ans=a*b*c
            return self._base(f"Một hộp chữ nhật có kích thước {a} cm, {b} cm, {c} cm. Thể tích là?", ans, f"V={a}×{b}×{c}={ans} cm³.", [a*b+b*c+c*a,ans+a,ans-c], "box_volume", "application", "volume")
        return self._base("Một cửa hàng bán 120 sản phẩm, mỗi sản phẩm lãi 15 nghìn đồng. Tổng tiền lãi là bao nhiêu?", "1.800.000 đồng", "120×15.000=1.800.000 đồng.", ["180.000 đồng","1.200.000 đồng","2.000.000 đồng"], "profit", "real_life", "unit_conversion")

    def _mixed_foundation(self, name, d):
        n=random.randint(4,12); k=random.randint(2,8); ans=n*k
        return self._base(f"Trong chuyên đề {name}, một tình huống có {n} lựa chọn loại A và {k} lựa chọn loại B độc lập. Có bao nhiêu phương án kết hợp?", ans, f"Quy tắc nhân cho {n}×{k}={ans} phương án.", [ans+1,ans-k,ans+n], "mixed_model", "application", "multiplication_rule")
