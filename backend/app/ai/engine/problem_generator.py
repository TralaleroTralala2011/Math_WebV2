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

    @staticmethod
    def validate_problem(problem):
        """Validate the complete problem before any part is sent to the client."""
        errors = []
        if not isinstance(problem, dict) or not problem.get("title") or not problem.get("context"):
            errors.append("missing title/context")
        parts = problem.get("parts", []) if isinstance(problem, dict) else []
        if not isinstance(parts, list) or not 2 <= len(parts) <= 6:
            errors.append("part count must be between 2 and 6")
            parts = []
        labels = [str(p.get("part", "")) for p in parts]
        if len(set(labels)) != len(labels):
            errors.append("duplicate part labels")
        for i, part in enumerate(parts):
            if not part.get("question") or part.get("answer") is None or not part.get("solution"):
                errors.append(f"part {i+1} is missing question/answer/solution")
            qtype = part.get("question_type")
            if qtype not in {"multiple_choice", "short_answer", "true_false"}:
                errors.append(f"part {i+1} has unsupported question type")
            if qtype == "multiple_choice":
                opts = part.get("options", [])
                values = [str(o.get("value")) for o in opts if isinstance(o, dict)]
                if len(opts) != 4 or len(values) != 4 or len(set(values)) != 4:
                    errors.append(f"part {i+1} must have four unique choices")
                if str(part.get("answer")) not in values:
                    errors.append(f"part {i+1} answer key is not one of the choices")
        return errors

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
        wanted = max(2, min(6, int(requested_parts or 4)))
        parts = list(problem.get("parts", []))[:wanted]
        while len(parts) < wanted:
            parts.append(self._make_extension_part(problem, parts, len(parts)))
        problem["parts"] = parts
        problem["part_count"] = len(parts)
        problem["question"] = problem.get("title", "Bài toán thực tế")
        errors = self.validate_problem(problem)
        if errors:
            raise ValueError("Invalid generated problem: " + "; ".join(errors))
        return problem

    def _choose_archetype(self, topic_id, difficulty):
        """Choose a coherent problem family that matches the selected curriculum topic.

        Avoid the old generic fallback that stitched unrelated standalone questions
        under one story. Every returned family has a shared data model.
        """
        t = str(topic_id).lower()
        if "bien_co_doc_lap" in t:
            return "probability_selection"
        if any(k in t for k in ("xac_suat", "probability", "xac-suat", "to_hop_xac_suat")):
            return random.choice(["probability_selection", "probability_experiment"])
        if any(k in t for k in ("thong_ke", "statistics", "du_lieu")):
            return random.choice(["statistics_survey", "data_table_analysis"])
        # Counting terms must be checked before geometry: e.g. "chinh_hop"
        # contains the character sequence "hinh" but is not a geometry topic.
        if any(k in t for k in ("to_hop", "hoan_vi", "chinh_hop", "quy_tac_dem", "dem")):
            return "counting_design"
        if any(k in t for k in ("hinh", "he_thuc_luong", "duong_tron", "toa_do", "mat_phang", "the_tich", "goc_khoang", "vector", "khong_gian")):
            return random.choice(["geometry_measurement", "coordinate_map"])
        if any(k in t for k in ("day_so", "cap_so", "sequence")):
            return "sequence_growth"
        if any(k in t for k in ("ham_so", "dao_ham", "tich_phan", "parabol", "function")):
            return random.choice(["function_model", "optimization"])
        if any(k in t for k in ("phuong_trinh", "he_", "bat_phuong_trinh", "equation", "inequality")):
            return random.choice(["production", "missing_data", "schedule"])
        if difficulty in {"hard", "expert"}:
            return random.choice(["compare_plans", "optimization", "missing_data", "function_model"])
        return random.choice(["compare_plans", "missing_data", "schedule", "production"])

    def _make_extension_part(self, problem, parts, index):
        """Add a genuinely useful extension when the requested part count exceeds a builder's base count."""
        label = chr(97 + index)
        archetype = problem.get("archetype", "")
        last = parts[-1] if parts else {}
        if archetype in {"probability_experiment", "probability_selection"}:
            if index >= 5:
                text = "Dựa vào hai biến cố đối vừa xét, tổng xác suất của chúng bằng bao nhiêu?"
                return self._part(label, text, "1", "Hai biến cố đối có tổng xác suất bằng 1.", "short_answer")
            text = (
                "Trong cùng điều kiện ở phần d, tính xác suất để biến cố đối của biến cố vừa xét xảy ra."
                if archetype == "probability_selection"
                else "Dựa trên kết quả vừa tìm, xác suất biến cố đối của biến cố vừa xét là bao nhiêu?"
            )
            try:
                v = Fraction(str(last.get("answer", "0")))
                answer = _fmt(1 - v)
            except Exception:
                answer = "1 - P"
            solution = f"Dùng công thức biến cố đối: P(Ā)=1-P(A), nên kết quả là {answer}."
            return self._part(label, text, answer, solution, "short_answer")
        if archetype in {"geometry_measurement", "coordinate_map"}:
            text = "Nêu một phép kiểm tra nhanh để xác nhận kết quả hình học vừa tính phù hợp với các dữ kiện của hình."
            answer = "Thay các độ dài hoặc tọa độ đã tính vào quan hệ hình học ban đầu và kiểm tra hai vế bằng nhau."
            solution = "Kiểm tra lại bằng định lý hoặc công thức đã dùng, rồi đối chiếu với toàn bộ dữ kiện của hình."
            return self._part(label, text, answer, solution, "short_answer", diagram=problem.get("diagram"))
        if archetype in {"production", "missing_data", "schedule"}:
            text = "Nếu một đại lượng trong dữ kiện thay đổi nhưng các điều kiện còn lại giữ nguyên, cần làm gì trước khi tính lại?"
            answer = "Lập lại mô hình hoặc phương trình theo dữ kiện mới rồi kiểm tra điều kiện."
            solution = "Không thay số máy móc vào kết quả cũ; trước hết cập nhật mô hình, sau đó giải và kiểm tra điều kiện."
            return self._part(label, text, answer, solution, "short_answer")
        if archetype in {"function_model", "optimization", "sequence_growth", "counting_design"}:
            text = "Nếu thay đổi một tham số của mô hình, kết quả có cần được tính lại không? Hãy nêu cách làm."
            answer = "Có; xác định lại mô hình với tham số mới rồi tính và kiểm tra điều kiện."
            solution = "Tham số mới có thể làm thay đổi kết quả, vì vậy cần cập nhật biểu thức hoặc quy tắc rồi tính lại."
            return self._part(label, text, answer, solution, "short_answer")
        text = "Hãy kiểm tra kết quả của phần trước bằng cách đối chiếu với ít nhất một dữ kiện ban đầu."
        answer = "Thay kết quả vào dữ kiện liên quan và kiểm tra điều kiện ban đầu được thỏa mãn."
        solution = "Một kết quả hợp lệ phải thỏa mãn dữ kiện hoặc quan hệ đã nêu trong đề; thay ngược để kiểm tra."
        return self._part(label, text, answer, solution, "short_answer", diagram=problem.get("diagram"))

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
            correct = _fmt(answer)
            raw = [correct] + [_fmt(x) for x in (distractors or [])]
            labels = []
            for candidate in raw:
                if candidate not in labels:
                    labels.append(candidate)
            # Keep the correct value exactly once and use the same value sent by
            # the frontend as the server-side answer key.
            labels = [correct] + [x for x in labels if x != correct]
            # Fill missing distractors with meaningful numeric near-misses rather
            # than UI-looking placeholders such as "Phương án 4".
            if len(labels) < 4:
                try:
                    from fractions import Fraction
                    base = Fraction(str(correct))
                    candidates = [_fmt(base + 1), _fmt(base - 1), _fmt(base * 2), _fmt(base / 2), _fmt(base + Fraction(1, 2))]
                except Exception:
                    candidates = []
                if not candidates:
                    candidates = ["Không đủ dữ kiện", "Không thỏa điều kiện", "Không xác định"]
                for candidate in candidates:
                    if candidate not in labels:
                        labels.append(candidate)
                    if len(labels) == 4:
                        break
            labels = labels[:4]
            random.shuffle(labels)
            item["options"] = [{"value": x, "label": x} for x in labels]
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

    def _build_probability_selection(self, grade, topic, difficulty):
        """One textbook-style real-life scenario with dependent subquestions."""
        from math import comb
        a_count = random.randint(6, 9)
        b_count = random.randint(4, 7)
        chosen = random.choice([3, 4])
        total_students = a_count + b_count
        total_groups = comb(total_students, chosen)
        all_a = comb(a_count, chosen) if a_count >= chosen else 0
        both_classes = total_groups - comb(a_count, chosen) - comb(b_count, chosen)
        # Conditional probability: given at least one B student, exactly chosen-1 are A.
        condition_total = total_groups - all_a
        exact_a = comb(a_count, chosen - 1) * comb(b_count, 1)
        conditional = Fraction(exact_a, condition_total) if condition_total else Fraction(0, 1)
        context = (
            f"Một trường THPT tổ chức hội thao với {total_students} học sinh, gồm "
            f"{a_count} học sinh lớp 11A và {b_count} học sinh lớp 11B. "
            f"Ban tổ chức chọn ngẫu nhiên {chosen} học sinh để tham gia một hoạt động. "
            "Giả sử mọi nhóm học sinh có cùng khả năng được chọn."
        )
        parts = [
            self._part("a", f"Có bao nhiêu cách chọn {chosen} học sinh từ toàn bộ nhóm?", total_groups,
                       f"Có {total_students} học sinh và không xét thứ tự, nên số cách là C({total_students},{chosen})={total_groups}.",
                       "short_answer"),
            self._part("b", f"Tính xác suất để cả {chosen} học sinh đều thuộc lớp 11A.",
                       _fmt(Fraction(all_a, total_groups)),
                       f"Số nhóm toàn lớp 11A là C({a_count},{chosen})={all_a}; do đó P={all_a}/{total_groups}={_fmt(Fraction(all_a,total_groups))}.",
                       "multiple_choice", [_fmt(Fraction(comb(a_count, chosen-1), total_groups)), _fmt(Fraction(comb(b_count, chosen), total_groups)), _fmt(Fraction(a_count, total_students))]),
            self._part("c", "Tính xác suất để nhóm được chọn có học sinh của cả hai lớp.",
                       _fmt(Fraction(both_classes, total_groups)),
                       f"Loại nhóm chỉ thuộc 11A và chỉ thuộc 11B: {total_groups}-C({a_count},{chosen})-C({b_count},{chosen})={both_classes}; xác suất là {both_classes}/{total_groups}={_fmt(Fraction(both_classes,total_groups))}.",
                       "short_answer"),
            self._part("d", f"Biết nhóm được chọn có ít nhất một học sinh lớp 11B. Tính xác suất để nhóm có đúng {chosen-1} học sinh lớp 11A.",
                       _fmt(conditional),
                       f"Không gian điều kiện có {total_groups}-{all_a}={condition_total} nhóm. Số nhóm có đúng {chosen-1} học sinh 11A và 1 học sinh 11B là C({a_count},{chosen-1})·C({b_count},1)={exact_a}; xác suất có điều kiện là {exact_a}/{condition_total}={_fmt(conditional)}.",
                       "short_answer"),
        ]
        return self._wrap("Bài toán thực tế: chọn học sinh và xác suất", context, parts,
                          {"class_11a": a_count, "class_11b": b_count, "group_size": chosen,
                           "total_groups": total_groups, "all_a_groups": all_a,
                           "both_classes_groups": both_classes, "conditional_favorable": exact_a,
                           "conditional_total": condition_total})

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
        # Safe coherent fallback: select one complete model, never concatenate
        # unrelated legacy questions under a made-up common context.
        t = str(topic).lower()
        if any(k in t for k in ("xac_suat", "prob")):
            return self._build_probability_selection(grade, topic, difficulty)
        if any(k in t for k in ("thong_ke", "statistics", "du_lieu")):
            return self._build_statistics_survey(grade, topic, difficulty)
        if any(k in t for k in ("hinh", "toa_do", "vector", "duong_tron")):
            return self._build_coordinate_map(grade, topic, difficulty)
        if any(k in t for k in ("ham_so", "parabol", "dao_ham", "tich_phan")):
            return self._build_function_model(grade, topic, difficulty)
        return self._build_missing_data(grade, topic, difficulty)

    _build_experiment_to_model = _build_probability_experiment
    _build_data_table_analysis = _build_statistics_survey
    _build_reverse_result = _build_missing_data
    _build_hidden_condition = _build_multi_stage_real_life
    _build_error_hunt = _build_multi_stage_real_life
    _build_parameter_change = _build_function_model
