"""Complete multi-part problem generator layered on top of the old question engine.

Nothing in the legacy generator is removed.  This module adds a second mode that
builds a coherent *problem* first, then exposes its parts as normal answerable
items so the existing practice UI can keep working.
"""
from __future__ import annotations

import math
import random
import uuid
from fractions import Fraction

from .problem_bank import BY_ID
from .geometry_diagrams import triangle_3_4_5, rectangle, coordinate_rectangle, circle


def _fmt(v):
    if isinstance(v, Fraction):
        return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


class ProblemGenerator:
    def __init__(self, knowledge, question_generator):
        self.knowledge = knowledge
        self.question_generator = question_generator

    def generate(self, grade, topic_id, difficulty="medium", requested_parts=4, question_type="mixed", game_id=None):
        difficulty = str(difficulty or "medium").lower()
        archetype = self._choose_archetype(topic_id, difficulty)
        builder = getattr(self, f"_build_{archetype}", None)
        if builder is None:
            builder = self._build_multi_stage_real_life
        problem = builder(grade, topic_id, difficulty)
        problem["id"] = uuid.uuid4().hex
        problem["grade"] = grade
        problem["topic"] = topic_id
        problem["difficulty"] = difficulty
        problem["archetype"] = archetype
        problem["archetype_name"] = BY_ID.get(archetype, {}).get("name", archetype)
        problem["problem_mode"] = True
        problem["game_id"] = game_id or ""
        parts = problem.get("parts", [])[: max(2, min(6, int(requested_parts or 4)))]
        problem["parts"] = parts
        problem["part_count"] = len(parts)
        problem["question"] = problem.get("title", "Bài toán thực tế")
        return problem

    def _choose_archetype(self, topic_id, difficulty):
        t = str(topic_id).lower()
        if "xac_suat" in t or "prob" in t:
            return random.choice(["probability_experiment", "experiment_to_model", "missing_data"])
        if "thong_ke" in t or "statistics" in t:
            return random.choice(["statistics_survey", "data_table_analysis", "missing_data"])
        if any(k in t for k in ("hinh", "he_thuc_luong", "duong_tron", "toa_do", "mat_phang", "the_tich", "goc_khoang")):
            return random.choice(["geometry_measurement", "coordinate_map", "optimization"])
        if any(k in t for k in ("to_hop", "hoan_vi", "chinh_hop", "quy_tac_dem")):
            return random.choice(["counting_design", "compare_plans", "probability_experiment"])
        if "day_so" in t or "cap_so" in t:
            return "sequence_growth"
        if "ham_so" in t or "dao_ham" in t or "tich_phan" in t:
            return random.choice(["function_model", "optimization", "parameter_change"])
        if "phuong_trinh" in t or "he_" in t or "bat_phuong_trinh" in t:
            return random.choice(["production", "schedule", "missing_data", "hidden_condition"])
        if difficulty in {"hard", "expert"}:
            return random.choice(["reverse_result", "hidden_condition", "parameter_change", "error_hunt", "mixed_topics"])
        return random.choice(["multi_stage_real_life", "missing_data", "compare_plans", "schedule"])

    def _part(self, label, text, answer, solution, ptype="short_answer", distractors=None, diagram=None):
        item = {
            "id": uuid.uuid4().hex,
            "part": label,
            "question": text,
            "answer": answer,
            "solution": solution,
            "question_type": ptype,
            "options": [],
            "hint": "Tách dữ kiện của phần này khỏi câu chuyện chung rồi kiểm tra điều kiện cần dùng.",
        }
        if diagram:
            item["diagram"] = diagram
        if ptype == "multiple_choice":
            raw = [answer] + list(distractors or [])
            item["options"] = list(dict.fromkeys([_fmt(x) for x in raw]))[:4]
            while len(item["options"]) < 4:
                candidate = _fmt(answer) + f" ({len(item['options'])})"
                if candidate not in item["options"]:
                    item["options"].append(candidate)
        return item

    def _wrap(self, title, context, parts, data=None, diagram=None):
        return {
            "title": title,
            "context": context,
            "data": data or {},
            "diagram": diagram,
            "parts": parts,
        }

    def _build_probability_experiment(self, grade, topic, difficulty):
        faces = random.choice([6, 8, 10, 12])
        target = random.randint(1, faces)
        total = faces * faces
        favorable = faces
        event_sum = random.randint(3, 2 * faces - 1)
        count_sum = event_sum - 1 if event_sum <= faces else 2 * faces - event_sum + 1
        # Better exact count for two dice with equal faces.
        count_sum = sum(1 for a in range(1, faces + 1) for b in range(1, faces + 1) if a + b == event_sum)
        p_target = Fraction(favorable, total)
        p_sum = Fraction(count_sum, total)
        context = f"Một con xúc xắc công bằng có {faces} mặt được gieo hai lần độc lập. Gọi A là biến cố lần gieo thứ nhất xuất hiện mặt {target}, và B là biến cố tổng hai lần gieo bằng {event_sum}."
        parts = [
            self._part("a", "Không gian mẫu của phép thử có bao nhiêu kết quả đồng khả năng?", total, f"Mỗi lần có {faces} khả năng và hai lần độc lập nên có {faces}·{faces}={total} kết quả.", "short_answer"),
            self._part("b", f"Xác suất của biến cố A bằng bao nhiêu?", _fmt(p_target), f"Có {faces} kết quả thuận lợi trên {total} kết quả nên P(A)={faces}/{total}={_fmt(p_target)}.", "multiple_choice", [_fmt(Fraction(1, faces + 1)), _fmt(Fraction(1, faces - 1)), _fmt(Fraction(2, faces))]),
            self._part("c", f"Có bao nhiêu kết quả thuộc biến cố B: tổng hai lần gieo bằng {event_sum}?", count_sum, f"Đếm các cặp (x,y) với 1≤x,y≤{faces} và x+y={event_sum}; có {count_sum} cặp.", "short_answer"),
            self._part("d", f"Tính xác suất của B và viết dưới dạng phân số tối giản.", _fmt(p_sum), f"P(B)={count_sum}/{total}={_fmt(p_sum)}.", "short_answer"),
            self._part("e", "Nếu gọi C là biến cố đối của B, P(C) bằng bao nhiêu?", _fmt(1 - p_sum), f"P(C)=1-P(B)=1-{_fmt(p_sum)}={_fmt(1-p_sum)}.", "short_answer"),
        ]
        return self._wrap("Bài toán xác suất nhiều bước", context, parts)

    def _build_missing_data(self, grade, topic, difficulty):
        x, y = random.randint(2, 9), random.randint(3, 12)
        total = x + y
        weighted = 2 * x + 3 * y
        avg = Fraction(weighted, 5)
        context = "Một bảng thống kê về hai nhóm sản phẩm có một số ô bị che. Nhóm I có x sản phẩm, nhóm II có y sản phẩm. Tổng số sản phẩm là S và tổng trọng số theo hệ số 2 và 3 là T."
        context += f" Ở lần khảo sát này, S={total} và T={weighted}."
        parts = [
            self._part("a", "Gọi x, y lần lượt là số sản phẩm của hai nhóm. Hãy lập hệ phương trình từ dữ kiện tổng và tổng trọng số.", f"x+y={total}; 2x+3y={weighted}", f"Từ tổng số: x+y={total}. Từ tổng trọng số: 2x+3y={weighted}.", "short_answer"),
            self._part("b", "Giải hệ để tìm số sản phẩm của mỗi nhóm.", f"x={x}, y={y}", f"Thế y={total}-x vào 2x+3y={weighted}, suy ra x={x}, y={y}.", "short_answer"),
            self._part("c", "Tính giá trị trung bình của trọng số trên toàn bộ sản phẩm.", _fmt(avg), f"Trung bình={weighted}/({total})={_fmt(avg)}.", "multiple_choice", [_fmt(avg+1), _fmt(avg-1), _fmt(Fraction(weighted+1,total))]),
            self._part("d", "Nếu số sản phẩm nhóm II tăng thêm 2 và nhóm I giữ nguyên, tổng số sản phẩm mới là bao nhiêu?", total + 2, f"Tổng mới={x}+({y}+2)={total+2}.", "short_answer"),
        ]
        return self._wrap("Bài toán dữ liệu bị thiếu và lập hệ", context, parts, {"S": total, "T": weighted})

    def _build_geometry_measurement(self, grade, topic, difficulty):
        a = random.choice([3, 6, 9])
        b = 4 * (a // 3)
        c = 5 * (a // 3)
        area = Fraction(a * b, 2)
        perimeter = a + b + c
        diagram = triangle_3_4_5(a=a, b=b)
        context = f"Một kỹ thuật viên đo một tấm biển hình tam giác vuông ABC. Hai cạnh góc vuông dài {a} cm và {b} cm. Hình minh họa bên dưới bám theo đúng các kích thước đã cho."
        parts = [
            self._part("a", "Xác định cạnh huyền của tam giác.", c, f"Áp dụng định lý Pythagore: BC=√({a}²+{b}²)={c} cm.", "short_answer", diagram=diagram),
            self._part("b", "Tính diện tích tấm biển.", _fmt(area), f"S={a}·{b}/2={_fmt(area)} cm².", "multiple_choice", [_fmt(area*2), _fmt(area/2), _fmt(area+5)], diagram=diagram),
            self._part("c", "Tính chu vi tấm biển.", perimeter, f"P={a}+{b}+{c}={perimeter} cm.", "short_answer", diagram=diagram),
            self._part("d", "Nếu phủ viền quanh toàn bộ tấm biển, chiều dài viền tối thiểu cần chuẩn bị là bao nhiêu?", perimeter, f"Viền bao quanh toàn bộ nên cần đúng chu vi, tức {perimeter} cm.", "short_answer", diagram=diagram),
        ]
        return self._wrap("Bài toán đo đạc hình học", context, parts, diagram=diagram)

    def _build_coordinate_map(self, grade, topic, difficulty):
        x1, y1 = random.randint(-4, 1), random.randint(-3, 1)
        w, h = random.randint(3, 6), random.randint(2, 5)
        x2, y2 = x1 + w, y1 + h
        diagonal2 = w*w + h*h
        area = w*h
        mx, my = Fraction(x1+x2,2), Fraction(y1+y2,2)
        diagram = coordinate_rectangle(x1, y1, x2, y2)
        context = f"Một khu đất hình chữ nhật ABCD được đặt trên bản đồ tọa độ với A({x1};{y1}), B({x2};{y1}), C({x2};{y2}), D({x1};{y2})."
        parts = [
            self._part("a", "Tính độ dài AB.", w, f"AB=|{x2}-{x1}|={w}.", "short_answer", diagram=diagram),
            self._part("b", "Tính bình phương đường chéo AC.", diagonal2, f"AC²={w}²+{h}²={diagonal2}.", "multiple_choice", [diagonal2+1, w+h, w*w-h*h], diagram=diagram),
            self._part("c", "Tìm tọa độ trung điểm AC.", f"({_fmt(mx)}; {_fmt(my)})", f"M=((xA+xC)/2;(yA+yC)/2)=({_fmt(mx)};{_fmt(my)}).", "short_answer", diagram=diagram),
            self._part("d", "Tính diện tích khu đất.", area, f"S=AB·BC={w}·{h}={area} đơn vị diện tích.", "short_answer", diagram=diagram),
        ]
        return self._wrap("Bài toán bản đồ tọa độ", context, parts, diagram=diagram)

    def _build_statistics_survey(self, grade, topic, difficulty):
        data = [random.randint(4, 18) for _ in range(7)]
        total = sum(data)
        mean = Fraction(total, len(data))
        ordered = sorted(data)
        median = ordered[len(data)//2]
        context = f"Một lớp khảo sát số phút mỗi ngày dành cho một hoạt động học tập của 7 học sinh. Số liệu thu được: {', '.join(map(str, data))} phút."
        parts = [
            self._part("a", "Tính tổng số phút của cả 7 học sinh.", total, f"Cộng toàn bộ số liệu: tổng={total} phút.", "short_answer"),
            self._part("b", "Tính số trung bình cộng.", _fmt(mean), f"x̄={total}/7={_fmt(mean)} phút.", "short_answer"),
            self._part("c", "Tìm trung vị của mẫu số liệu.", median, f"Sắp xếp được {ordered}; phần tử đứng giữa là {median}.", "multiple_choice", [ordered[0], ordered[-1], ordered[1]]),
            self._part("d", "Có bao nhiêu học sinh có thời gian không nhỏ hơn trung vị?", sum(v >= median for v in data), f"Đếm các giá trị ≥ {median} trong mẫu số liệu được {sum(v >= median for v in data)} học sinh.", "short_answer"),
        ]
        return self._wrap("Bài toán khảo sát dữ liệu thực tế", context, parts, {"sample": data})

    def _build_counting_design(self, grade, topic, difficulty):
        digits = random.choice([5, 6, 7, 8])
        length = 3
        total = digits * (digits - 1) * (digits - 2)
        context = f"Một hệ thống cần tạo mã gồm {length} chữ số khác nhau từ các chữ số 1 đến {digits}; chữ số đầu tiên không được lặp và mọi mã có thứ tự vị trí khác nhau được xem là khác nhau."
        parts = [
            self._part("a", "Ở vị trí đầu tiên có bao nhiêu lựa chọn?", digits, f"Có {digits} chữ số được phép chọn vì tập chữ số là 1 đến {digits}.", "multiple_choice", [digits, digits-2, digits+1]),
            self._part("b", "Sau khi chọn chữ số đầu, vị trí thứ hai có bao nhiêu lựa chọn?", digits-1, f"Không lặp chữ số nên còn {digits-1} lựa chọn.", "short_answer"),
            self._part("c", "Tổng số mã có thể tạo là bao nhiêu?", total, f"Có {digits}·{digits-1}·{digits-2}={total} mã.", "short_answer"),
            self._part("d", "Nếu yêu cầu chữ số cuối phải là số chẵn, số mã có giảm hay không? Giải thích ngắn gọn.", "Có, vì tập lựa chọn ở vị trí cuối bị thu hẹp.", "Điều kiện chữ số cuối là số chẵn loại bỏ các mã kết thúc bằng chữ số lẻ, nên số mã giảm.", "short_answer"),
        ]
        return self._wrap("Bài toán thiết kế mã và quy tắc đếm", context, parts)

    def _build_sequence_growth(self, grade, topic, difficulty):
        a1 = random.randint(4, 12)
        d = random.randint(2, 6)
        n = random.randint(6, 10)
        an = a1 + (n-1)*d
        s = n*(a1+an)//2
        context = f"Một kế hoạch tiết kiệm bắt đầu với {a1} đơn vị ở kỳ đầu và tăng đều {d} đơn vị sau mỗi kỳ."
        parts = [
            self._part("a", "Đây là cấp số cộng hay cấp số nhân?", "Cấp số cộng", "Mỗi kỳ tăng thêm một lượng không đổi d nên đây là cấp số cộng.", "multiple_choice", ["Cấp số nhân", "Dãy hằng", "Không phải dãy số"]),
            self._part("b", f"Tính số đơn vị ở kỳ thứ {n}.", an, f"aₙ=a₁+(n-1)d={a1}+({n}-1)·{d}={an}.", "short_answer"),
            self._part("c", f"Tính tổng số đơn vị trong {n} kỳ đầu.", s, f"Sₙ=n(a₁+aₙ)/2={n}·({a1}+{an})/2={s}.", "short_answer"),
            self._part("d", "Nếu mức tăng mỗi kỳ tăng thêm 1 đơn vị, quy luật mới còn là cấp số cộng không?", "Có", "Công sai mới vẫn không đổi giữa các kỳ, chỉ chuyển từ d sang d+1.", "short_answer"),
        ]
        return self._wrap("Bài toán tăng trưởng theo dãy số", context, parts)

    def _build_function_model(self, grade, topic, difficulty):
        a = random.choice([-2, -1, 1, 2])
        h = random.randint(2, 6)
        k = random.randint(5, 15)
        x = random.randint(0, 4)
        y = a*(x-h)**2+k
        extreme = k
        context = f"Một mô hình doanh thu đơn giản được xấp xỉ bởi hàm f(x)={a}(x-{h})²+{k}, trong đó x là mức sản lượng chuẩn hóa."
        parts = [
            self._part("a", "Xác định hoành độ đỉnh của parabol.", h, f"Dạng y=a(x-h)²+k có đỉnh tại x={h}.", "short_answer"),
            self._part("b", f"Tính f({x}).", y, f"f({x})={a}({x}-{h})²+{k}={y}.", "multiple_choice", [y+1, y-1, k]),
            self._part("c", "Giá trị lớn nhất hay nhỏ nhất của hàm số là k?", "Giá trị lớn nhất" if a < 0 else "Giá trị nhỏ nhất", f"Vì a={'<0' if a<0 else '>0'}, parabol {'mở xuống' if a<0 else 'mở lên'}, nên giá trị cực trị tại đỉnh là {k}.", "short_answer"),
            self._part("d", "Nếu thay đổi hệ số a nhưng vẫn giữ h và k, vị trí đỉnh có thay đổi không?", "Không", "Trong dạng a(x-h)²+k, h và k quyết định tọa độ đỉnh; thay a chỉ làm thay đổi độ mở và hướng mở.", "short_answer"),
        ]
        return self._wrap("Bài toán mô hình hàm số", context, parts)

    def _build_optimization(self, grade, topic, difficulty):
        perimeter = random.choice([20, 24, 30, 36])
        half = perimeter / 2
        # rectangle x(half-x), max at x=half/2
        x = half / 2
        max_area = x * (half-x)
        context = f"Một khu đất hình chữ nhật có chu vi {perimeter} m. Gọi x là chiều dài và y là chiều rộng. Người thiết kế muốn diện tích lớn nhất."
        parts = [
            self._part("a", "Lập mối liên hệ giữa x và y.", f"x+y={int(half)}", f"2(x+y)={perimeter} nên x+y={int(half)}.", "short_answer"),
            self._part("b", "Biểu diễn diện tích theo x.", f"S=x({int(half)}-x)", f"Từ y={int(half)}-x, S=xy=x({int(half)}-x).", "short_answer"),
            self._part("c", "Khi nào diện tích lớn nhất?", f"x=y={int(x)}", f"Với tổng cố định, tích xy lớn nhất khi x=y={int(x)}.", "multiple_choice", [f"x=1, y={int(half)-1}", f"x={int(x)+1}, y={int(x)-1}", f"x={int(half)-1}, y=1"]),
            self._part("d", "Diện tích lớn nhất là bao nhiêu m²?", int(max_area), f"Smax={int(x)}·{int(x)}={int(max_area)} m².", "short_answer"),
        ]
        return self._wrap("Bài toán tối ưu hóa khu đất", context, parts)

    def _build_production(self, grade, topic, difficulty):
        x, y = random.randint(8, 20), random.randint(6, 16)
        total = x+y
        work = 2*x + 3*y
        context = f"Một xưởng sản xuất hai loại sản phẩm I và II. Trong một ca, tổng số sản phẩm là {total}; mỗi sản phẩm I dùng 2 đơn vị nguyên liệu, mỗi sản phẩm II dùng 3 đơn vị. Tổng lượng nguyên liệu đã dùng là {work} đơn vị."
        parts = [
            self._part("a", "Gọi x, y là số sản phẩm loại I và II. Hệ phương trình là gì?", f"x+y={total}; 2x+3y={work}", f"Từ tổng sản phẩm và nguyên liệu: x+y={total}; 2x+3y={work}.", "short_answer"),
            self._part("b", "Giải hệ để tìm x và y.", f"x={x}, y={y}", f"Giải hệ cho x={x}, y={y}.", "short_answer"),
            self._part("c", "Nếu mỗi sản phẩm I mang lại 4 nghìn đồng và mỗi sản phẩm II mang lại 7 nghìn đồng, doanh thu là bao nhiêu nghìn đồng?", 4*x+7*y, f"Doanh thu=4·{x}+7·{y}={4*x+7*y} nghìn đồng.", "multiple_choice", [4*x+7*y+10, 4*x+7*y-7, total*5]),
            self._part("d", "Nếu ca sau tăng thêm 2 sản phẩm loại II nhưng giữ nguyên số loại I, tổng sản phẩm mới là bao nhiêu?", total+2, f"Tổng mới={x}+({y}+2)={total+2}.", "short_answer"),
        ]
        return self._wrap("Bài toán sản xuất và hệ phương trình", context, parts)

    def _build_schedule(self, grade, topic, difficulty):
        distance = random.choice([120, 150, 180, 210])
        v1 = random.choice([30, 40, 50])
        v2 = v1 + random.choice([10, 20])
        t1 = Fraction(distance//2, v1)
        t2 = Fraction(distance - distance//2, v2)
        total = t1+t2
        context = f"Một tuyến đường dài {distance} km. Một phương tiện đi nửa quãng đường đầu với vận tốc {v1} km/h và nửa còn lại với vận tốc {v2} km/h."
        parts = [
            self._part("a", "Thời gian đi nửa quãng đường đầu là bao nhiêu giờ?", _fmt(t1), f"t₁={distance//2}/{v1}={_fmt(t1)} giờ.", "short_answer"),
            self._part("b", "Thời gian đi nửa quãng đường sau là bao nhiêu giờ?", _fmt(t2), f"t₂={distance-distance//2}/{v2}={_fmt(t2)} giờ.", "short_answer"),
            self._part("c", "Tổng thời gian di chuyển là bao nhiêu giờ?", _fmt(total), f"t=t₁+t₂={_fmt(t1)}+{_fmt(t2)}={_fmt(total)} giờ.", "multiple_choice", [_fmt(total+1), _fmt(total-1), _fmt(total+Fraction(1,2))]),
            self._part("d", "Vì sao không thể lấy trung bình cộng đơn giản của hai vận tốc để suy ra vận tốc trung bình?", "Vì hai vận tốc tác động trên các khoảng thời gian khác nhau; phải dùng tổng quãng đường chia tổng thời gian.", "Vận tốc trung bình được xác định bởi tổng quãng đường chia tổng thời gian, không phải trung bình cộng hai vận tốc.", "short_answer"),
        ]
        return self._wrap("Bài toán lịch trình chuyển động", context, parts)

    def _build_compare_plans(self, grade, topic, difficulty):
        base = random.randint(20, 50) * 1000
        p1 = random.choice([10, 15, 20])
        fee = random.choice([30000, 50000, 70000])
        p2 = random.choice([5, 10, 15])
        qty = random.randint(3, 8)
        cost1 = base * qty * (100-p1) / 100
        cost2 = base * qty + fee - base * qty * p2 / 100
        context = f"Một cửa hàng đưa ra hai phương án mua {qty} sản phẩm giá niêm yết {base:,} đồng mỗi sản phẩm. Phương án A giảm {p1}%; phương án B giảm {p2}% trên toàn đơn rồi trừ thêm {fee:,} đồng.".replace(',', '.')
        c1, c2 = int(cost1), int(cost2)
        better = "A" if c1 < c2 else "B" if c2 < c1 else "Hai phương án bằng nhau"
        parts = [
            self._part("a", "Tính tổng giá niêm yết của đơn hàng.", base*qty, f"Giá niêm yết={base}·{qty}={base*qty} đồng.", "short_answer"),
            self._part("b", "Tính số tiền phải trả theo phương án A.", c1, f"A={base*qty}·(1-{p1}/100)={c1} đồng.", "short_answer"),
            self._part("c", "Tính số tiền phải trả theo phương án B.", c2, f"B={base*qty}·(1-{p2}/100)-{fee}={c2} đồng.", "multiple_choice", [c2+fee, c2-10000, base*qty*(100-p2)//100]),
            self._part("d", "Theo dữ kiện, nên chọn phương án nào để trả ít tiền hơn?", better, f"So sánh {c1} và {c2}, phương án có chi phí nhỏ hơn là {better}.", "short_answer"),
        ]
        return self._wrap("Bài toán so sánh phương án thực tế", context, parts)

    def _build_multi_stage_real_life(self, grade, topic, difficulty):
        # Generic real-world shell.  The mathematical core is delegated to the
        # legacy generator so the old bank remains a source of verified content.
        generated = []
        for idx, ptype in enumerate(["multiple_choice", "short_answer", "short_answer", "multiple_choice"]):
            q = self.question_generator.generate(grade, topic, difficulty, ptype)
            q = dict(q)
            q["part"] = chr(97 + idx)
            generated.append(q)
        name = self.knowledge.get(topic).get("name", topic)
        context = f"Một tình huống thực tế được mô hình hóa bằng kiến thức {name}. Dữ kiện được cho theo từng bước để người học phải kết nối kết quả giữa các phần."
        parts = []
        for q in generated:
            parts.append(self._part(q["part"], q["question"], q["answer"], q.get("solution", ""), q.get("question_type", "short_answer"), q.get("options", []), q.get("diagram")))
        return self._wrap(f"Bài toán vận dụng: {name}", context, parts)

    _build_experiment_to_model = _build_probability_experiment
    _build_data_table_analysis = _build_statistics_survey
    _build_reverse_result = _build_missing_data
    _build_hidden_condition = _build_multi_stage_real_life
    _build_error_hunt = _build_multi_stage_real_life
    _build_parameter_change = _build_function_model
