import random
import uuid
from fractions import Fraction


# =========================================================
# CẤU HÌNH ĐỘ KHÓ
# =========================================================

DIFFICULTIES = {
    "easy": "Dễ",
    "medium": "Vừa",
    "hard": "Khó"
}


# =========================================================
# HỆ THỐNG KIẾN THỨC
# =========================================================

TOPICS = {
    "probability": "Xác suất",
    "permutation_combination": "Hoán vị - Chỉnh hợp - Tổ hợp",
    "linear_equation": "Phương trình bậc nhất hai ẩn",
    "system_equation": "Hệ phương trình",
    "linear_inequality": "Bất phương trình bậc nhất một ẩn",
    "divisibility": "Chia hết",
    "remainder": "Chia dư",
    "function": "Hàm số",
    "mixed": "Tổng hợp"
}


KNOWLEDGE_MAP = {

    "probability": {
        "core": [
            "Không gian mẫu",
            "Biến cố",
            "Xác suất của biến cố",
            "Số trường hợp thuận lợi"
        ],
        "related": [
            "Xác suất thực nghiệm",
            "Biến cố đối",
            "Xác suất có điều kiện đơn giản",
            "Phép đếm"
        ],
        "advanced": [
            "Xác suất nhiều bước",
            "Lấy mẫu không hoàn lại",
            "Kết hợp xác suất và tổ hợp"
        ]
    },

    "permutation_combination": {
        "core": [
            "Giai thừa",
            "Hoán vị",
            "Chỉnh hợp",
            "Tổ hợp"
        ],
        "related": [
            "Phân biệt có thứ tự",
            "Phân biệt không có thứ tự",
            "Quy tắc cộng",
            "Quy tắc nhân"
        ],
        "advanced": [
            "Bài toán điều kiện",
            "Xếp chỗ",
            "Lập mật mã",
            "Chọn đội có ràng buộc"
        ]
    },

    "linear_equation": {
        "core": [
            "Phương trình bậc nhất",
            "Chuyển vế",
            "Thu gọn",
            "Tìm nghiệm"
        ],
        "related": [
            "Phương trình có ngoặc",
            "Phương trình có phân số",
            "Phương trình chứa tham số đơn giản"
        ],
        "advanced": [
            "Bài toán thực tế",
            "Lập phương trình từ dữ kiện",
            "Phối hợp nhiều đại lượng"
        ]
    },

    "system_equation": {
        "core": [
            "Hệ hai phương trình",
            "Phương pháp thế",
            "Phương pháp cộng đại số"
        ],
        "related": [
            "Nghiệm của hệ",
            "Điều kiện nghiệm",
            "Bài toán hai đại lượng"
        ],
        "advanced": [
            "Bài toán thực tế",
            "Tuổi",
            "Chuyển động",
            "Số lượng và giá tiền"
        ]
    },

    "linear_inequality": {
        "core": [
            "Bất phương trình bậc nhất",
            "Chuyển vế",
            "Chia cho số dương",
            "Chia cho số âm"
        ],
        "related": [
            "Biểu diễn tập nghiệm",
            "Khoảng nghiệm",
            "Bất phương trình trong bài toán thực tế"
        ],
        "advanced": [
            "Bài toán giới hạn",
            "Điều kiện để biểu thức thỏa mãn",
            "Tối ưu đơn giản"
        ]
    },

    "divisibility": {
        "core": [
            "Ước",
            "Bội",
            "Chia hết",
            "Dấu hiệu chia hết"
        ],
        "related": [
            "Chia hết cho 2",
            "Chia hết cho 3",
            "Chia hết cho 5",
            "Chia hết cho 9",
            "Phân tích thừa số"
        ],
        "advanced": [
            "Tìm số chưa biết",
            "Điều kiện chia hết",
            "Chứng minh chia hết"
        ]
    },

    "remainder": {
        "core": [
            "Số dư",
            "Phép chia có dư",
            "Công thức số bị chia"
        ],
        "related": [
            "Đồng dư đơn giản",
            "Chu kỳ số dư",
            "Chia số lớn"
        ],
        "advanced": [
            "Tìm số dư của biểu thức",
            "Lũy thừa và số dư",
            "Bài toán modulo"
        ]
    },

    "function": {
        "core": [
            "Giá trị hàm số",
            "Biến số",
            "Hệ số",
            "Hàm số bậc nhất"
        ],
        "related": [
            "Đồ thị",
            "Hệ số góc",
            "Giao điểm",
            "Nghiệm của hàm số"
        ],
        "advanced": [
            "Giao điểm hai đồ thị",
            "Bài toán thực tế",
            "Tìm tham số"
        ]
    }
}


# =========================================================
# DANH SÁCH TOPIC CHO MIXED
# =========================================================

QUESTION_TOPICS = [
    "probability",
    "permutation_combination",
    "linear_equation",
    "system_equation",
    "linear_inequality",
    "divisibility",
    "remainder",
    "function"
]


# =========================================================
# ID CÂU HỎI
# =========================================================

def create_question_id():
    return str(
        uuid.uuid4()
    )


# =========================================================
# HÀM CHÍNH
# =========================================================

def create_question(
    topic,
    difficulty,
    preferred_concept=None
):

    if topic not in TOPICS:
        raise ValueError(
            "Chủ đề không hợp lệ."
        )

    if difficulty not in DIFFICULTIES:
        raise ValueError(
            "Độ khó không hợp lệ."
        )

    actual_topic = topic

    if topic == "mixed":
        actual_topic = choose_related_topic()

    if actual_topic == "probability":

        question = create_probability_question(
            difficulty,
            preferred_concept
        )

    elif actual_topic == "permutation_combination":

        question = create_permutation_question(
            difficulty,
            preferred_concept
        )

    elif actual_topic == "linear_equation":

        question = create_linear_equation_question(
            difficulty,
            preferred_concept
        )

    elif actual_topic == "system_equation":

        question = create_system_equation_question(
            difficulty,
            preferred_concept
        )

    elif actual_topic == "linear_inequality":

        question = create_linear_inequality_question(
            difficulty,
            preferred_concept
        )

    elif actual_topic == "divisibility":

        question = create_divisibility_question(
            difficulty,
            preferred_concept
        )

    elif actual_topic == "remainder":

        question = create_remainder_question(
            difficulty,
            preferred_concept
        )

    elif actual_topic == "function":

        question = create_function_question(
            difficulty,
            preferred_concept
        )

    else:
        raise ValueError(
            "Không thể tạo câu hỏi."
        )

    return question


# =========================================================
# CHỌN CHỦ ĐỀ LIÊN QUAN
# =========================================================

def choose_related_topic():

    return random.choice(
        QUESTION_TOPICS
    )


# =========================================================
# CHỌN KIẾN THỨC
# =========================================================

def choose_knowledge(
    topic,
    difficulty
):

    if topic not in KNOWLEDGE_MAP:
        raise ValueError(
            "Topic không có dữ liệu kiến thức."
        )

    data = KNOWLEDGE_MAP[
        topic
    ]

    if difficulty == "easy":

        pool = data["core"]

    elif difficulty == "medium":

        pool = (
            data["core"]
            + data["related"]
        )

    else:

        pool = (
            data["core"]
            + data["related"]
            + data["advanced"]
        )

    return random.choice(
        pool
    )


# =========================================================
# XÁC SUẤT
# =========================================================

def create_probability_question(
    difficulty,
    preferred_concept=None
):

    concept = (
        preferred_concept
        or choose_knowledge(
            "probability",
            difficulty
        )
    )

    if difficulty == "easy":

        total = random.randint(
            6,
            15
        )

        favorable = random.randint(
            1,
            total - 1
        )

        answer = Fraction(
            favorable,
            total
        )

        return build_question(
            topic="probability",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Một hộp có {total} viên bi, "
                f"trong đó có {favorable} viên bi đỏ. "
                "Lấy ngẫu nhiên một viên. "
                "Xác suất lấy được bi đỏ là bao nhiêu?"
            ),
            answer=answer,
            answer_text=format_fraction(answer),
            choices=create_fraction_choices(answer),
            explanation=(
                f"Xác suất = {favorable}/{total} "
                f"= {format_fraction(answer)}."
            ),
            related_knowledge=[
                "Không gian mẫu",
                "Biến cố",
                "Số trường hợp thuận lợi"
            ]
        )

    if difficulty == "medium":

        red = random.randint(
            4,
            12
        )

        blue = random.randint(
            4,
            12
        )

        total = red + blue

        answer = Fraction(
            red,
            total
        )

        return build_question(
            topic="probability",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Một hộp có {red} viên bi đỏ "
                f"và {blue} viên bi xanh. "
                "Lấy ngẫu nhiên một viên. "
                "Xác suất lấy được bi đỏ là bao nhiêu?"
            ),
            answer=answer,
            answer_text=format_fraction(answer),
            choices=create_fraction_choices(answer),
            explanation=(
                f"Có {red} trường hợp thuận lợi "
                f"trên tổng {total} trường hợp. "
                f"Vì vậy P = {red}/{total} "
                f"= {format_fraction(answer)}."
            ),
            related_knowledge=[
                "Không gian mẫu",
                "Biến cố",
                "Phân số"
            ]
        )

    red = random.randint(
        5,
        12
    )

    blue = random.randint(
        4,
        10
    )

    yellow = random.randint(
        3,
        8
    )

    total = (
        red
        + blue
        + yellow
    )

    answer = (
        Fraction(
            red,
            total
        )
        * Fraction(
            red - 1,
            total - 1
        )
    )

    return build_question(
        topic="probability",
        difficulty=difficulty,
        concept=concept,
        question=(
            f"Một hộp có {red} viên bi đỏ, "
            f"{blue} viên bi xanh và "
            f"{yellow} viên bi vàng. "
            "Lấy ngẫu nhiên hai viên liên tiếp "
            "không hoàn lại. "
            "Xác suất cả hai viên đều màu đỏ là bao nhiêu?"
        ),
        answer=answer,
        answer_text=format_fraction(answer),
        choices=create_fraction_choices(answer),
        explanation=(
            f"Lần đầu: {red}/{total}. "
            f"Sau khi lấy một viên đỏ, lần hai: "
            f"{red - 1}/{total - 1}. "
            f"Do đó P = {red}/{total} × "
            f"{red - 1}/{total - 1} "
            f"= {format_fraction(answer)}."
        ),
        related_knowledge=[
            "Xác suất nhiều bước",
            "Lấy mẫu không hoàn lại",
            "Phép nhân xác suất"
        ]
    )


# =========================================================
# HOÁN VỊ - CHỈNH HỢP - TỔ HỢP
# =========================================================

def create_permutation_question(
    difficulty,
    preferred_concept=None
):

    concept = (
        preferred_concept
        or choose_knowledge(
            "permutation_combination",
            difficulty
        )
    )

    if difficulty == "easy":

        n = random.randint(
            4,
            7
        )

        answer = factorial(
            n
        )

        return build_question(
            topic="permutation_combination",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Có {n} học sinh xếp thành "
                "một hàng. Có bao nhiêu cách xếp?"
            ),
            answer=answer,
            answer_text=str(answer),
            choices=create_integer_choices(answer),
            explanation=(
                f"Số cách xếp là {n}! = {answer}."
            ),
            related_knowledge=[
                "Giai thừa",
                "Hoán vị"
            ]
        )

    if difficulty == "medium":

        n = random.randint(
            6,
            10
        )

        k = random.randint(
            2,
            n - 2
        )

        answer = permutation(
            n,
            k
        )

        return build_question(
            topic="permutation_combination",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Có {n} học sinh. "
                f"Chọn và xếp {k} học sinh "
                f"vào {k} vị trí khác nhau. "
                "Có bao nhiêu cách?"
            ),
            answer=answer,
            answer_text=str(answer),
            choices=create_integer_choices(answer),
            explanation=(
                f"Có xét thứ tự nên dùng chỉnh hợp: "
                f"A({n},{k}) = {answer}."
            ),
            related_knowledge=[
                "Chỉnh hợp",
                "Phân biệt thứ tự"
            ]
        )

    n = random.randint(
        8,
        13
    )

    k = random.randint(
        3,
        n - 2
    )

    answer = combination(
        n,
        k
    )

    return build_question(
        topic="permutation_combination",
        difficulty=difficulty,
        concept=concept,
        question=(
            f"Một nhóm có {n} học sinh. "
            f"Cần chọn {k} học sinh để lập một đội. "
            "Không xét thứ tự. Có bao nhiêu cách chọn?"
        ),
        answer=answer,
        answer_text=str(answer),
        choices=create_integer_choices(answer),
        explanation=(
            f"Không xét thứ tự nên dùng tổ hợp: "
            f"C({n},{k}) = {answer}."
        ),
        related_knowledge=[
            "Tổ hợp",
            "Không xét thứ tự"
        ]
    )


# =========================================================
# PHƯƠNG TRÌNH BẬC NHẤT
# =========================================================

def create_linear_equation_question(
    difficulty,
    preferred_concept=None
):

    concept = (
        preferred_concept
        or choose_knowledge(
            "linear_equation",
            difficulty
        )
    )

    # =====================================================
    # EASY
    # =====================================================

    if difficulty == "easy":

        a = random.randint(
            2,
            9
        )

        x = random.randint(
            -15,
            15
        )

        b = random.randint(
            -20,
            20
        )

        c = (
            a * x
            + b
        )

        question = (
            f"Giải phương trình: "
            f"{format_linear_expression(a, 'x', b)} = {c}."
        )

        explanation = (
            f"Chuyển {format_constant(b)} sang vế phải, "
            f"ta có {a}x = {c - b}. "
            f"Do đó x = {x}."
        )

        return build_question(
            topic="linear_equation",
            difficulty=difficulty,
            concept=concept,
            question=question,
            answer=x,
            answer_text=str(x),
            choices=create_integer_choices(x),
            explanation=explanation,
            related_knowledge=[
                "Chuyển vế",
                "Thu gọn",
                "Tìm nghiệm"
            ]
        )

    # =====================================================
    # MEDIUM
    # =====================================================

    if difficulty == "medium":

        a = random.randint(
            2,
            8
        )

        c = random.randint(
            2,
            8
        )

        while c == a:
            c = random.randint(
                2,
                8
            )

        x = random.randint(
            -12,
            12
        )

        b = random.randint(
            -15,
            15
        )

        d = random.randint(
            -15,
            15
        )

        left = (
            a * x
            + b
        )

        right = (
            c * x
            + d
        )

        # Điều chỉnh để phương trình có đúng nghiệm x
        d = (
            left
            - c * x
        )

        right = (
            c * x
            + d
        )

        question = (
            f"Giải phương trình:\n"
            f"{format_linear_expression(a, 'x', b)} "
            f"= {format_linear_expression(c, 'x', d)}."
        )

        explanation = (
            f"Chuyển các hạng tử chứa x về một vế "
            f"và hằng số về vế còn lại. "
            f"Ta được {a - c}x = {d - b}, "
            f"suy ra x = {x}."
        )

        return build_question(
            topic="linear_equation",
            difficulty=difficulty,
            concept=concept,
            question=question,
            answer=x,
            answer_text=str(x),
            choices=create_integer_choices(x),
            explanation=explanation,
            related_knowledge=[
                "Chuyển vế",
                "Thu gọn",
                "Phương trình hai vế"
            ]
        )

    # =====================================================
    # HARD
    # =====================================================

    denominator = random.randint(
        2,
        7
    )

    x = random.randint(
        -12,
        12
    )

    left_constant = random.randint(
        -15,
        15
    )

    right_constant = random.randint(
        -15,
        15
    )

    # a(x + m)/d = x + n
    a = random.randint(
        2,
        6
    )

    m = random.randint(
        -8,
        8
    )

    n = (
        Fraction(
            a * (x + m),
            denominator
        )
        - x
    )

    if n.denominator != 1:
        # Tạo lại với dữ liệu đơn giản hơn nếu n không nguyên
        denominator = 2
        a = 2
        m = random.randint(
            -6,
            6
        )
        n = (
            Fraction(
                a * (x + m),
                denominator
            )
            - x
        )

    n_value = Fraction(n)

    question = (
        f"Giải phương trình:\n"
        f"{a}(x "
        f"{format_signed_number(m)})/{denominator} "
        f"= x "
        f"{format_signed_number(n_value)}."
    )

    explanation = (
        f"Nhân hai vế với {denominator}, "
        "sau đó thu gọn và chuyển vế. "
        f"Kết quả là x = {x}."
    )

    return build_question(
        topic="linear_equation",
        difficulty=difficulty,
        concept=concept,
        question=question,
        answer=x,
        answer_text=str(x),
        choices=create_integer_choices(x),
        explanation=explanation,
        related_knowledge=[
            "Phương trình có phân số",
            "Khử mẫu",
            "Chuyển vế"
        ]
    )


# =========================================================
# HỆ PHƯƠNG TRÌNH
# =========================================================

def create_system_equation_question(
    difficulty,
    preferred_concept=None
):

    concept = (
        preferred_concept
        or choose_knowledge(
            "system_equation",
            difficulty
        )
    )

    # =====================================================
    # EASY
    # =====================================================

    if difficulty == "easy":

        x = random.randint(
            -8,
            8
        )

        y = random.randint(
            -8,
            8
        )

        a = random.randint(
            1,
            5
        )

        b = random.randint(
            1,
            5
        )

        c = random.randint(
            1,
            5
        )

        d = random.randint(
            1,
            5
        )

        while a * d == b * c:
            d = random.randint(
                1,
                5
            )

        e = (
            a * x
            + b * y
        )

        f = (
            c * x
            + d * y
        )

        return build_question(
            topic="system_equation",
            difficulty=difficulty,
            concept=concept,
            question=(
                "Giải hệ phương trình:\n"
                f"{a}x + {b}y = {e}\n"
                f"{c}x + {d}y = {f}"
            ),
            answer=(x, y),
            answer_text=f"x = {x}, y = {y}",
            choices=create_pair_choices(
                x,
                y
            ),
            explanation=(
                "Dùng phương pháp thế hoặc cộng đại số, "
                f"ta thu được x = {x}, y = {y}."
            ),
            related_knowledge=[
                "Phương pháp thế",
                "Phương pháp cộng đại số",
                "Nghiệm của hệ"
            ]
        )

    # =====================================================
    # MEDIUM
    # =====================================================

    if difficulty == "medium":

        x = random.randint(
            -10,
            10
        )

        y = random.randint(
            -10,
            10
        )

        a = random.randint(
            1,
            7
        )

        b = random.randint(
            1,
            7
        )

        c = random.randint(
            1,
            7
        )

        d = random.randint(
            1,
            7
        )

        while a * d == b * c:
            d = random.randint(
                1,
                7
            )

        e = (
            a * x
            + b * y
        )

        f = (
            c * x
            + d * y
        )

        return build_question(
            topic="system_equation",
            difficulty=difficulty,
            concept=concept,
            question=(
                "Giải hệ phương trình:\n"
                f"{a}x + {b}y = {e}\n"
                f"{c}x + {d}y = {f}"
            ),
            answer=(x, y),
            answer_text=f"x = {x}, y = {y}",
            choices=create_pair_choices(
                x,
                y
            ),
            explanation=(
                "Khử một ẩn bằng phương pháp cộng đại số "
                "hoặc thế, sau đó tìm ẩn còn lại. "
                f"Nghiệm là x = {x}, y = {y}."
            ),
            related_knowledge=[
                "Nghiệm của hệ",
                "Phương pháp thế",
                "Phương pháp cộng đại số"
            ]
        )

    # =====================================================
    # HARD
    # =====================================================

    total_price = random.randint(
        120,
        500
    )

    quantity_difference = random.randint(
        1,
        6
    )

    unit_a = random.randint(
        10,
        35
    )

    unit_b = unit_a + random.randint(
        5,
        20
    )

    # Số lượng sao cho có nghiệm nguyên
    while True:

        x = random.randint(
            3,
            15
        )

        y = x + quantity_difference

        total = (
            unit_a * x
            + unit_b * y
        )

        if total <= 1000:
            break

    question = (
        f"Một cửa hàng bán hai loại sản phẩm. "
        f"Sản phẩm A giá {unit_a} nghìn đồng, "
        f"sản phẩm B giá {unit_b} nghìn đồng. "
        f"Một khách mua tổng cộng {x + y} sản phẩm "
        f"và trả {total} nghìn đồng. "
        "Hỏi khách đã mua bao nhiêu sản phẩm mỗi loại?"
    )

    answer = (
        x,
        y
    )

    explanation = (
        f"Gọi số sản phẩm A là x và B là y.\n"
        f"Ta có x + y = {x + y}.\n"
        f"Và {unit_a}x + {unit_b}y = {total}.\n"
        f"Giải hệ, được x = {x}, y = {y}."
    )

    return build_question(
        topic="system_equation",
        difficulty=difficulty,
        concept=concept,
        question=question,
        answer=answer,
        answer_text=f"x = {x}, y = {y}",
        choices=create_pair_choices(
            x,
            y
        ),
        explanation=explanation,
        related_knowledge=[
            "Bài toán thực tế",
            "Số lượng và giá tiền",
            "Hệ phương trình"
        ]
    )


# =========================================================
# BẤT PHƯƠNG TRÌNH
# =========================================================

def create_linear_inequality_question(
    difficulty,
    preferred_concept=None
):

    concept = (
        preferred_concept
        or choose_knowledge(
            "linear_inequality",
            difficulty
        )
    )

    # =====================================================
    # EASY
    # =====================================================

    if difficulty == "easy":

        a = random.randint(
            2,
            9
        )

        threshold = random.randint(
            -10,
            10
        )

        b = random.randint(
            -15,
            15
        )

        operator = random.choice(
            [
                ">",
                "<",
                "≥",
                "≤"
            ]
        )

        c = (
            a * threshold
            + b
        )

        correct_text = (
            f"x {operator} {threshold}"
        )

        return build_question(
            topic="linear_inequality",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Giải bất phương trình: "
                f"{format_linear_expression(a, 'x', b)} "
                f"{operator} {c}."
            ),
            answer=threshold,
            answer_text=correct_text,
            choices=create_inequality_choices(
                threshold,
                operator
            ),
            explanation=(
                f"Vì {a} > 0 nên khi chia hai vế "
                "cho hệ số dương, dấu bất phương trình "
                f"không đổi. Kết quả: {correct_text}."
            ),
            related_knowledge=[
                "Chuyển vế",
                "Chia cho số dương",
                "Tập nghiệm"
            ]
        )

    # =====================================================
    # MEDIUM
    # =====================================================

    if difficulty == "medium":

        a = random.randint(
            2,
            9
        )

        threshold = random.randint(
            -12,
            12
        )

        b = random.randint(
            -15,
            15
        )

        operator = random.choice(
            [
                ">",
                "<",
                "≥",
                "≤"
            ]
        )

        c = (
            a * threshold
            + b
        )

        left = format_linear_expression(
            a,
            "x",
            b
        )

        correct_text = (
            f"x {operator} {threshold}"
        )

        return build_question(
            topic="linear_inequality",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Giải bất phương trình:\n"
                f"{left} {operator} {c}"
            ),
            answer=threshold,
            answer_text=correct_text,
            choices=create_inequality_choices(
                threshold,
                operator
            ),
            explanation=(
                f"Chuyển {b} sang vế phải rồi chia "
                f"cho {a}. Vì {a} > 0 nên dấu không đổi. "
                f"Kết quả: {correct_text}."
            ),
            related_knowledge=[
                "Chuyển vế",
                "Khoảng nghiệm",
                "Biểu diễn tập nghiệm"
            ]
        )

    # =====================================================
    # HARD
    # =====================================================

    a = random.randint(
        -9,
        -2
    )

    threshold = random.randint(
        -10,
        10
    )

    b = random.randint(
        -15,
        15
    )

    operator = random.choice(
        [
            ">",
            "<",
            "≥",
            "≤"
        ]
    )

    c = (
        a * threshold
        + b
    )

    correct_operator = reverse_inequality(
        operator
    )

    correct_text = (
        f"x {correct_operator} {threshold}"
    )

    return build_question(
        topic="linear_inequality",
        difficulty=difficulty,
        concept=concept,
        question=(
            f"Giải bất phương trình:\n"
            f"{format_linear_expression(a, 'x', b)} "
            f"{operator} {c}"
        ),
        answer=threshold,
        answer_text=correct_text,
        choices=create_inequality_choices(
            threshold,
            correct_operator
        ),
        explanation=(
            f"Vì hệ số của x là {a} < 0 nên "
            "khi chia hai vế cho số âm, "
            "dấu bất phương trình phải đổi chiều. "
            f"Kết quả: {correct_text}."
        ),
        related_knowledge=[
            "Chia cho số âm",
            "Đổi chiều bất phương trình",
            "Tập nghiệm"
        ]
    )


# =========================================================
# CHIA HẾT
# =========================================================

def create_divisibility_question(
    difficulty,
    preferred_concept=None
):

    concept = (
        preferred_concept
        or choose_knowledge(
            "divisibility",
            difficulty
        )
    )

    if difficulty == "easy":

        divisor = random.choice(
            [
                2,
                3,
                5,
                9
            ]
        )

        multiplier = random.randint(
            10,
            50
        )

        number = (
            divisor
            * multiplier
        )

        return build_question(
            topic="divisibility",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Số {number} có chia hết "
                f"cho {divisor} không?"
            ),
            answer=True,
            answer_text="Có",
            choices=[
                "A. Có",
                "B. Không",
                "C. Không xác định",
                "D. Không đủ dữ kiện"
            ],
            explanation=(
                f"{number} = {divisor} × {multiplier}, "
                f"nên {number} chia hết cho {divisor}."
            ),
            related_knowledge=[
                "Ước",
                "Bội",
                "Chia hết"
            ]
        )

    if difficulty == "medium":

        divisor = random.choice(
            [
                3,
                5,
                7,
                9,
                11
            ]
        )

        multiplier = random.randint(
            10,
            100
        )

        number = (
            divisor
            * multiplier
            + random.randint(
                1,
                divisor - 1
            )
        )

        return build_question(
            topic="divisibility",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Số {number} có chia hết "
                f"cho {divisor} không?"
            ),
            answer=False,
            answer_text="Không",
            choices=[
                "A. Có",
                "B. Không",
                "C. Không xác định",
                "D. Chỉ khi số đó chẵn"
            ],
            explanation=(
                f"{number} = {divisor} × "
                f"{number // divisor} + "
                f"{number % divisor}. "
                f"Vì số dư là {number % divisor} "
                "nên không chia hết."
            ),
            related_knowledge=[
                "Ước",
                "Bội",
                "Dấu hiệu chia hết"
            ]
        )

    # HARD
    # Tìm chữ số để số chia hết cho một số

    divisor = random.choice(
        [
            3,
            9,
            11
        ]
    )

    prefix = random.randint(
        10,
        99
    )

    missing_digit = random.randint(
        0,
        9
    )

    number = (
        prefix * 10
        + missing_digit
    )

    # Điều chỉnh để có đáp án chữ số
    valid_digits = [
        digit
        for digit in range(10)
        if (
            (prefix * 10 + digit)
            % divisor
            == 0
        )
    ]

    if not valid_digits:
        divisor = 3

        valid_digits = [
            digit
            for digit in range(10)
            if (
                (prefix * 10 + digit)
                % divisor
                == 0
            )
        ]

    missing_digit = random.choice(
        valid_digits
    )

    number = (
        prefix * 10
        + missing_digit
    )

    return build_question(
        topic="divisibility",
        difficulty=difficulty,
        concept=concept,
        question=(
            f"Tìm chữ số x để số "
            f"{prefix}x chia hết cho {divisor}."
        ),
        answer=missing_digit,
        answer_text=str(missing_digit),
        choices=create_digit_choices(
            missing_digit
        ),
        explanation=(
            f"Ta xét điều kiện chia hết cho {divisor}. "
            f"Chọn x = {missing_digit} thì "
            f"{number} chia hết cho {divisor}."
        ),
        related_knowledge=[
            "Điều kiện chia hết",
            "Tìm chữ số chưa biết",
            "Dấu hiệu chia hết"
        ]
    )


# =========================================================
# CHIA DƯ
# =========================================================

def create_remainder_question(
    difficulty,
    preferred_concept=None
):

    concept = (
        preferred_concept
        or choose_knowledge(
            "remainder",
            difficulty
        )
    )

    # =====================================================
    # EASY
    # =====================================================

    if difficulty == "easy":

        divisor = random.randint(
            3,
            12
        )

        quotient = random.randint(
            10,
            60
        )

        remainder = random.randint(
            0,
            divisor - 1
        )

        number = (
            divisor * quotient
            + remainder
        )

        return build_question(
            topic="remainder",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Khi chia {number} cho {divisor}, "
                "số dư là bao nhiêu?"
            ),
            answer=remainder,
            answer_text=str(remainder),
            choices=create_integer_choices(
                remainder
            ),
            explanation=(
                f"{number} = {divisor} × "
                f"{quotient} + {remainder}. "
                f"Vậy số dư là {remainder}."
            ),
            related_knowledge=[
                "Phép chia có dư",
                "Số dư",
                "Công thức số bị chia"
            ]
        )

    # =====================================================
    # MEDIUM
    # =====================================================

    if difficulty == "medium":

        divisor = random.randint(
            4,
            15
        )

        quotient = random.randint(
            10,
            80
        )

        remainder = random.randint(
            0,
            divisor - 1
        )

        number = (
            divisor * quotient
            + remainder
        )

        return build_question(
            topic="remainder",
            difficulty=difficulty,
            concept=concept,
            question=(
                f"Một số n khi chia cho {divisor} "
                f"được thương {quotient} và số dư "
                f"{remainder}. Giá trị của n là bao nhiêu?"
            ),
            answer=number,
            answer_text=str(number),
            choices=create_integer_choices(
                number
            ),
            explanation=(
                f"Áp dụng công thức "
                f"n = {divisor} × {quotient} "
                f"+ {remainder} = {number}."
            ),
            related_knowledge=[
                "Phép chia có dư",
                "Công thức số bị chia",
                "Số dư"
            ]
        )

    # =====================================================
    # HARD
    # =====================================================

    base = random.randint(
        2,
        9
    )

    exponent = random.randint(
        8,
        20
    )

    divisor = random.choice(
        [
            3,
            4,
            5,
            7,
            9,
            11
        ]
    )

    answer = (
        pow(
            base,
            exponent,
            divisor
        )
    )

    question = (
        f"Tìm số dư khi "
        f"{base}^{exponent} "
        f"được chia cho {divisor}."
    )

    explanation = (
        f"Ta xét chu kỳ số dư của "
        f"{base}^n khi chia cho {divisor}. "
        f"Thực hiện phép tính theo modulo, "
        f"ta được số dư {answer}."
    )

    return build_question(
        topic="remainder",
        difficulty=difficulty,
        concept=concept,
        question=question,
        answer=answer,
        answer_text=str(answer),
        choices=create_integer_choices(
            answer
        ),
        explanation=explanation,
        related_knowledge=[
            "Đồng dư",
            "Chu kỳ số dư",
            "Lũy thừa và số dư"
        ]
    )


# =========================================================
# HÀM SỐ
# =========================================================

def create_function_question(
    difficulty,
    preferred_concept=None
):

    concept = (
        preferred_concept
        or choose_knowledge(
            "function",
            difficulty
        )
    )

    a = random.randint(
        -8,
        8
    )

    if a == 0:
        a = 3

    b = random.randint(
        -15,
        15
    )

    x = random.randint(
        -8,
        8
    )

    y = (
        a * x
        + b
    )

    # =====================================================
    # EASY
    # =====================================================

    if difficulty == "easy":

        question = (
            f"Cho hàm số "
            f"f(x) = {format_linear_expression(a, 'x', b)}. "
            f"Tính f({x})."
        )

        answer = y

        explanation = (
            f"Thay x = {x} vào hàm số, "
            f"ta được f({x}) = {y}."
        )

        return build_question(
            topic="function",
            difficulty=difficulty,
            concept=concept,
            question=question,
            answer=answer,
            answer_text=str(answer),
            choices=create_integer_choices(
                answer
            ),
            explanation=explanation,
            related_knowledge=[
                "Giá trị hàm số",
                "Biến số",
                "Hàm số bậc nhất"
            ]
        )

    # =====================================================
    # MEDIUM
    # =====================================================

    if difficulty == "medium":

        question = (
            f"Cho hàm số "
            f"f(x) = {format_linear_expression(a, 'x', b)}. "
            f"Biết f(x) = {y}. Tìm x."
        )

        answer = x

        explanation = (
            f"Giải phương trình "
            f"{format_linear_expression(a, 'x', b)} = {y}, "
            f"ta được x = {x}."
        )

        return build_question(
            topic="function",
            difficulty=difficulty,
            concept=concept,
            question=question,
            answer=answer,
            answer_text=str(answer),
            choices=create_integer_choices(
                answer
            ),
            explanation=explanation,
            related_knowledge=[
                "Hàm số bậc nhất",
                "Nghiệm của hàm số",
                "Phương trình"
            ]
        )

    # =====================================================
    # HARD
    # =====================================================

    c = random.randint(
        -15,
        15
    )

    second_a = -a

    answer = Fraction(
        c - b,
        a - second_a
    )

    question = (
        f"Cho hai hàm số:\n"
        f"f(x) = {format_linear_expression(a, 'x', b)}\n"
        f"g(x) = {format_linear_expression(second_a, 'x', c)}\n"
        "Hoành độ giao điểm của hai đồ thị là bao nhiêu?"
    )

    explanation = (
        "Tại giao điểm, ta có f(x) = g(x). "
        f"Suy ra {format_linear_expression(a, 'x', b)} "
        f"= {format_linear_expression(second_a, 'x', c)}. "
        f"Giải ra x = {format_fraction(answer)}."
    )

    return build_question(
        topic="function",
        difficulty=difficulty,
        concept=concept,
        question=question,
        answer=answer,
        answer_text=format_fraction(answer),
        choices=create_fraction_choices(
            answer
        ),
        explanation=explanation,
        related_knowledge=[
            "Giao điểm hai đồ thị",
            "Hàm số bậc nhất",
            "Phương trình"
        ]
    )


# =========================================================
# BUILD QUESTION
# =========================================================

def build_question(
    topic,
    difficulty,
    concept,
    question,
    answer,
    answer_text,
    choices,
    explanation,
    related_knowledge=None
):

    if topic not in TOPICS:
        raise ValueError(
            "Topic không hợp lệ."
        )

    if difficulty not in DIFFICULTIES:
        raise ValueError(
            "Difficulty không hợp lệ."
        )

    answer_text = str(
        answer_text
    ).strip()

    if not answer_text:
        raise ValueError(
            "answer_text không được rỗng."
        )

    choices = normalize_choices(
        choices,
        answer_text
    )

    random.shuffle(
        choices
    )

    return {
        "question_id": create_question_id(),

        "topic": topic,

        "topic_name": TOPICS[topic],

        "difficulty": difficulty,

        "difficulty_name": DIFFICULTIES[difficulty],

        "concept": concept,

        "related_knowledge": (
            related_knowledge
            or []
        ),

        "question": str(
            question
        ),

        "choices": choices,

        "answer": serialize_answer(
            answer
        ),

        "answer_text": answer_text,

        "explanation": str(
            explanation
        )
    }


# =========================================================
# CHUẨN HÓA ĐÁP ÁN
# =========================================================

def serialize_answer(
    answer
):

    if isinstance(
        answer,
        Fraction
    ):

        return {
            "type": "fraction",
            "numerator": answer.numerator,
            "denominator": answer.denominator
        }

    if isinstance(
        answer,
        tuple
    ):

        if len(answer) != 2:
            raise ValueError(
                "Pair answer phải có đúng 2 phần tử."
            )

        return {
            "type": "pair",
            "x": answer[0],
            "y": answer[1]
        }

    if isinstance(
        answer,
        bool
    ):

        return {
            "type": "boolean",
            "value": answer
        }

    if isinstance(
        answer,
        int
    ):

        return {
            "type": "number",
            "value": answer
        }

    if isinstance(
        answer,
        float
    ):

        return {
            "type": "number",
            "value": answer
        }

    return {
        "type": "text",
        "value": str(
            answer
        )
    }


# =========================================================
# ĐÁP ÁN SỐ NGUYÊN
# =========================================================

def create_integer_choices(
    answer
):

    answer = int(
        answer
    )

    values = set()

    values.add(
        answer
    )

    offsets = [
        -1,
        1,
        -2,
        2,
        -3,
        3,
        -5,
        5,
        -7,
        7,
        -10,
        10,
        -12,
        12,
        -15,
        15
    ]

    for offset in offsets:

        if len(values) >= 4:
            break

        values.add(
            answer + offset
        )

    candidate = answer + 20

    while len(values) < 4:

        values.add(
            candidate
        )

        candidate += 1

    values = list(
        values
    )

    random.shuffle(
        values
    )

    labels = [
        "A",
        "B",
        "C",
        "D"
    ]

    return [
        f"{labels[i]}. {values[i]}"
        for i in range(4)
    ]


# =========================================================
# ĐÁP ÁN CHỮ SỐ 0 -> 9
# =========================================================

def create_digit_choices(
    answer
):

    answer = int(
        answer
    )

    values = {
        answer
    }

    candidates = list(
        range(10)
    )

    random.shuffle(
        candidates
    )

    for value in candidates:

        if len(values) >= 4:
            break

        values.add(
            value
        )

    values = list(
        values
    )

    random.shuffle(
        values
    )

    labels = [
        "A",
        "B",
        "C",
        "D"
    ]

    return [
        f"{labels[i]}. {values[i]}"
        for i in range(4)
    ]


# =========================================================
# ĐÁP ÁN PHÂN SỐ
# =========================================================

def create_fraction_choices(
    answer
):

    answer = Fraction(
        answer
    )

    values = {
        answer
    }

    candidates = [
        answer + Fraction(1, 2),
        answer - Fraction(1, 2),
        answer + Fraction(1, 3),
        answer - Fraction(1, 3),
        answer + Fraction(1, 4),
        answer - Fraction(1, 4),
        answer + Fraction(2, 3),
        answer - Fraction(2, 3),
        answer + 1,
        answer - 1,
        answer + Fraction(2, 5),
        answer - Fraction(2, 5),
        answer + Fraction(3, 5),
        answer - Fraction(3, 5)
    ]

    for value in candidates:

        if len(values) >= 4:
            break

        values.add(
            value
        )

    offset = 1

    while len(values) < 4:

        values.add(
            answer + offset
        )

        offset += 1

    values = list(
        values
    )

    random.shuffle(
        values
    )

    labels = [
        "A",
        "B",
        "C",
        "D"
    ]

    return [
        f"{labels[i]}. {format_fraction(values[i])}"
        for i in range(4)
    ]


# =========================================================
# ĐÁP ÁN HỆ PHƯƠNG TRÌNH
# =========================================================

def create_pair_choices(
    x,
    y
):

    correct_pair = (
        x,
        y
    )

    candidates = [
        correct_pair,

        (
            y,
            x
        ),

        (
            x + 1,
            y
        ),

        (
            x - 1,
            y
        ),

        (
            x,
            y + 1
        ),

        (
            x,
            y - 1
        ),

        (
            y + 1,
            x
        ),

        (
            y - 1,
            x
        ),

        (
            x + 2,
            y - 2
        ),

        (
            x - 2,
            y + 2
        )
    ]

    unique_pairs = []

    for pair in candidates:

        if pair not in unique_pairs:

            unique_pairs.append(
                pair
            )

    random.shuffle(
        unique_pairs
    )

    if correct_pair in unique_pairs:

        unique_pairs.remove(
            correct_pair
        )

    selected = [
        correct_pair
    ]

    for pair in unique_pairs:

        if len(selected) >= 4:
            break

        selected.append(
            pair
        )

    while len(selected) < 4:

        delta = len(selected)

        fallback = (
            x + delta,
            y - delta
        )

        if fallback not in selected:

            selected.append(
                fallback
            )

    random.shuffle(
        selected
    )

    labels = [
        "A",
        "B",
        "C",
        "D"
    ]

    return [
        f"{labels[i]}. "
        f"x = {pair[0]}, "
        f"y = {pair[1]}"
        for i, pair in enumerate(
            selected
        )
    ]


# =========================================================
# ĐÁP ÁN BẤT PHƯƠNG TRÌNH
# =========================================================

def create_inequality_choices(
    threshold,
    correct_operator
):

    operators = [
        ">",
        "<",
        "≥",
        "≤"
    ]

    values = [
        threshold
    ]

    other_values = [
        threshold - 1,
        threshold + 1,
        threshold - 2,
        threshold + 2
    ]

    choices = [
        f"x {correct_operator} {threshold}"
    ]

    wrong_operators = [
        operator
        for operator in operators
        if operator != correct_operator
    ]

    for operator in wrong_operators:

        if len(choices) >= 4:
            break

        choices.append(
            f"x {operator} {threshold}"
        )

    random.shuffle(
        choices
    )

    return choices


# =========================================================
# ĐỊNH DẠNG PHÂN SỐ
# =========================================================

def format_fraction(
    value
):

    value = Fraction(
        value
    )

    if value.denominator == 1:

        return str(
            value.numerator
        )

    return (
        f"{value.numerator}/"
        f"{value.denominator}"
    )


# =========================================================
# ĐỊNH DẠNG SỐ CÓ DẤU
# =========================================================

def format_signed_number(
    value
):

    value = Fraction(
        value
    )

    if value > 0:
        return (
            f"+ {format_fraction(value)}"
        )

    if value < 0:
        return (
            f"- {format_fraction(abs(value))}"
        )

    return ""


# =========================================================
# ĐỊNH DẠNG HẰNG SỐ
# =========================================================

def format_constant(
    value
):

    if value > 0:
        return str(
            value
        )

    if value < 0:
        return (
            f"({value})"
        )

    return "0"


# =========================================================
# ĐỊNH DẠNG BIỂU THỨC
# =========================================================

def format_linear_expression(
    coefficient,
    variable,
    constant
):

    coefficient = Fraction(
        coefficient
    )

    constant = Fraction(
        constant
    )

    if coefficient == 0:

        return format_fraction(
            constant
        )

    if coefficient == 1:

        result = variable

    elif coefficient == -1:

        result = (
            "-"
            + variable
        )

    else:

        result = (
            f"{format_fraction(coefficient)}"
            f"{variable}"
        )

    if constant > 0:

        result += (
            f" + "
            f"{format_fraction(constant)}"
        )

    elif constant < 0:

        result += (
            f" - "
            f"{format_fraction(abs(constant))}"
        )

    return result


# =========================================================
# ĐỔI CHIỀU BẤT PHƯƠNG TRÌNH
# =========================================================

def reverse_inequality(
    operator
):

    mapping = {
        ">": "<",
        "<": ">",
        "≥": "≤",
        "≤": "≥"
    }

    return mapping.get(
        operator,
        operator
    )


# =========================================================
# CHUẨN HÓA 4 ĐÁP ÁN
# =========================================================

def normalize_choices(
    choices,
    answer_text
):

    if not isinstance(
        choices,
        list
    ):
        choices = []

    result = []

    seen = set()

    for choice in choices:

        choice = str(
            choice
        ).strip()

        if not choice:
            continue

        normalized = normalize_choice_text(
            choice
        )

        key = normalized.casefold()

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            normalized
        )

    normalized_answer = normalize_choice_text(
        answer_text
    )

    answer_key = normalized_answer.casefold()

    if answer_key not in seen:

        result.append(
            normalized_answer
        )

        seen.add(
            answer_key
        )

    fallback = [
        "-1",
        "1",
        "-2",
        "2",
        "-3",
        "3",
        "-5",
        "5",
        "-7",
        "7",
        "0",
        "10",
        "11",
        "12"
    ]

    for candidate in fallback:

        if len(result) >= 4:
            break

        key = candidate.casefold()

        if key not in seen:

            result.append(
                candidate
            )

            seen.add(
                key
            )

    # Trường hợp đặc biệt:
    # nếu somehow vẫn chưa đủ 4 đáp án
    candidate_number = 20

    while len(result) < 4:

        candidate = str(
            candidate_number
        )

        if candidate.casefold() not in seen:

            result.append(
                candidate
            )

            seen.add(
                candidate.casefold()
            )

        candidate_number += 1

    result = result[:4]

    # Đảm bảo đáp án đúng không bị cắt mất
    if answer_key not in [
        item.casefold()
        for item in result
    ]:

        result[-1] = normalized_answer

    labels = [
        "A",
        "B",
        "C",
        "D"
    ]

    final_result = []

    for index, choice in enumerate(
        result
    ):

        final_result.append(
            f"{labels[index]}. {choice}"
        )

    return final_result


# =========================================================
# CHUẨN HÓA NỘI DUNG LỰA CHỌN
# =========================================================

def normalize_choice_text(
    text
):

    if not text:
        return ""

    text = str(
        text
    ).strip()

    if len(text) >= 2:

        if (
            text[0].upper()
            in "ABCD"
            and text[1] == "."
        ):

            return text[2:].strip()

    return text


# =========================================================
# TOÁN CƠ BẢN
# =========================================================

def factorial(
    n
):

    if not isinstance(
        n,
        int
    ):
        raise ValueError(
            "n phải là số nguyên."
        )

    if n < 0:
        raise ValueError(
            "Không thể tính giai thừa của số âm."
        )

    result = 1

    for i in range(
        2,
        n + 1
    ):

        result *= i

    return result


def permutation(
    n,
    k
):

    validate_n_k(
        n,
        k
    )

    return (
        factorial(n)
        // factorial(n - k)
    )


def combination(
    n,
    k
):

    validate_n_k(
        n,
        k
    )

    return (
        factorial(n)
        // (
            factorial(k)
            * factorial(n - k)
        )
    )


# =========================================================
# KIỂM TRA N, K
# =========================================================

def validate_n_k(
    n,
    k
):

    if not isinstance(
        n,
        int
    ) or not isinstance(
        k,
        int
    ):

        raise ValueError(
            "n và k phải là số nguyên."
        )

    if n < 0:

        raise ValueError(
            "n không được âm."
        )

    if k < 0 or k > n:

        raise ValueError(
            "k phải thỏa mãn 0 <= k <= n."
        )