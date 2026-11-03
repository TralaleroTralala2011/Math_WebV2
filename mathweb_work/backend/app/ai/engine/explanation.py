"""Detailed, student-friendly solution builder for generated math questions."""
from __future__ import annotations

import re
from fractions import Fraction


def _frac_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _signed(n: int) -> str:
    return f"+ {n}" if n >= 0 else f"- {abs(n)}"


def _system_solution(question: str) -> str | None:
    m = re.search(r"x\s*\+\s*y\s*=\s*(-?\d+)\s*;\s*x\s*-\s*y\s*=\s*(-?\d+)", question, re.I)
    if not m:
        m = re.search(r"x\s*\+\s*y\s*=\s*(-?\d+).*?x\s*-\s*y\s*=\s*(-?\d+)", question, re.I | re.S)
    if not m:
        return None
    s, d = int(m.group(1)), int(m.group(2))
    x_num = s + d
    y_num = s - d
    if x_num % 2 or y_num % 2:
        return None
    x, y = x_num // 2, y_num // 2
    base = (
        "Bước 1: Ta có hệ phương trình:\n"
        f"  x + y = {s}\n"
        f"  x - y = {d}\n\n"
        "Bước 2: Cộng từng vế của hai phương trình để khử y:\n"
        f"  (x + y) + (x - y) = {s} + ({d})\n"
        f"  2x = {s + d}\n"
        f"  x = {x}\n\n"
        "Bước 3: Thay x vào phương trình x + y = " + str(s) + ":\n"
        f"  {x} + y = {s}\n"
        f"  y = {y}\n\n"
    )
    lower = question.lower()
    if re.search(r"giá trị cần tìm là\s*x\b", lower):
        return base + f"Bước 4: Vậy giá trị cần tìm là x = {x}."
    if re.search(r"giá trị cần tìm là\s*y\b", lower):
        return base + f"Bước 4: Vậy giá trị cần tìm là y = {y}."
    return base + f"Bước 4: Vậy cặp nghiệm là (x; y) = ({x}; {y})."


def _probability_solution(question: str) -> str | None:
    # One die, one requested face.
    m = re.search(r"mặt\s+(\d+)", question, re.I)
    if m and "một con xúc xắc" in question.lower() and "gieo một lần" in question.lower():
        face = m.group(1)
        return (
            "Bước 1: Một con xúc xắc cân đối có 6 mặt, từ 1 đến 6.\n"
            "Bước 2: Có 6 kết quả đồng khả năng và chỉ có 1 kết quả thuận lợi là mặt " + face + ".\n"
            "Bước 3: Theo công thức xác suất P(A) = số kết quả thuận lợi / số kết quả có thể xảy ra, ta có:\n"
            "  P = 1/6.\n"
            "Kết luận: Xác suất cần tìm là 1/6."
        )

    m = re.search(r"Gieo một con xúc xắc.*?số chấm chẵn", question, re.I | re.S)
    if m:
        return (
            "Bước 1: Các mặt của xúc xắc là 1, 2, 3, 4, 5, 6.\n"
            "Bước 2: Các mặt chẵn là 2, 4, 6, nên có 3 kết quả thuận lợi.\n"
            "Bước 3: Có 6 kết quả đồng khả năng. Vì vậy:\n"
            "  P = 3/6 = 1/2.\n"
            "Kết luận: Xác suất xuất hiện số chấm chẵn là 1/2."
        )

    return None


def _generic_detailed(solution: str, answer=None) -> str:
    """Turn an existing verified compact solution into readable learning steps.

    The original solution remains the mathematical authority. We do not invent
    extra calculations when the generator did not provide enough information.
    """
    raw = str(solution or "").strip()
    if not raw:
        return "Bước 1: Xác định các dữ kiện đã cho trong đề bài.\nBước 2: Áp dụng kiến thức phù hợp để xử lý dữ kiện.\nBước 3: Đối chiếu kết quả với yêu cầu của đề."
    if raw.startswith("Bước 1:"):
        return raw
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", raw) if p.strip()]
    lines = []
    if parts:
        lines.append("Bước 1: Xác định dữ kiện và yêu cầu của bài toán.")
        low = raw.lower()
        if "c(" in low or "comb(" in low:
            lines.append("Bước 2: Vì đây là bài toán chọn nhóm không xét thứ tự, ta áp dụng công thức tổ hợp C(n,k).")
        elif "a(" in low and ("a(" in low or "chỉnh hợp" in low):
            lines.append("Bước 2: Vì thứ tự sắp xếp có ý nghĩa, ta áp dụng công thức chỉnh hợp A(n,k).")
        elif "!=" in low or "n!" in low or "hoán vị" in low:
            lines.append("Bước 2: Vì cần sắp xếp toàn bộ các phần tử theo thứ tự, ta sử dụng công thức hoán vị n!.")
        elif "p=" in low or "xác suất" in low:
            lines.append("Bước 2: Áp dụng công thức xác suất phù hợp với số kết quả thuận lợi và số kết quả có thể xảy ra.")
        elif "δ" in raw or "delta" in low:
            lines.append("Bước 2: Áp dụng biệt thức Δ = b² - 4ac để xét nghiệm của phương trình bậc hai.")
        elif "f'" in raw or "đạo hàm" in low:
            lines.append("Bước 2: Áp dụng quy tắc đạo hàm tương ứng với hàm số đã cho.")
        elif "x̄" in raw or "trung bình" in low:
            lines.append("Bước 2: Tính tổng các giá trị rồi chia cho số lượng giá trị để tìm số trung bình cộng.")
        elif "ab²" in low or "độ dài" in low or "khoảng cách" in low:
            lines.append("Bước 2: Áp dụng công thức hình học phù hợp, sau đó thay các dữ kiện đã cho.")
        else:
            lines.append("Bước 2: Chọn công thức, định lý hoặc quy tắc phù hợp với dạng toán.")
        start = len(lines) + 1
        for i, part in enumerate(parts, start=start):
            lines.append(f"Bước {i}: {part}")
    else:
        lines.append("Bước 1: Áp dụng công thức hoặc định lý phù hợp.")
        lines.append(f"Bước 2: {raw}")
    if answer is not None:
        lines.append(f"Kết luận: Đáp án đúng là {answer}.")
    return "\n".join(lines)


def build_detailed_solution(question: str, solution: str, answer=None, topic: str = "", game_id: str | None = None) -> str:
    """Build a detailed Vietnamese solution while preserving verified math."""
    q = str(question or "")
    special = _system_solution(q)
    if special:
        return special
    special = _probability_solution(q)
    if special:
        return special
    return _generic_detailed(solution, answer)
