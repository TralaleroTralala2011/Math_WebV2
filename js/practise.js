/* =========================================================
   MATH WEB
   PRACTICE SYSTEM + AI QUESTION ENGINE
   ========================================================= */

(function () {

    "use strict";


    /* =====================================================
       CONFIG
       ===================================================== */

    const API_BASE =
        window.MATHWEB_API_BASE ||
        window.MATHWEB_API_URL || "http://127.0.0.1:8000";

    const AI_API =
        API_BASE + "/api/ai";


    const MAX_PRACTICE_COUNT = 30;

    const DEFAULT_GRADE = 12;

    const DEFAULT_DIFFICULTY = "medium";

    const DEFAULT_QUESTION_TYPE = "mixed";

    const DEFAULT_COUNT = 10;


    /* =====================================================
       KNOWLEDGE DATA
    ===================================================== */

    const knowledgeData = [
    {
        "id": "REMAINDER",
        "name": "Chia dư",
        "grade": 10,
        "games": [
            {
                "name": "Bốc số",
                "icon": "🎱",
                "path": "games/remainder/draw.html"
            },
            {
                "name": "Săn số dư",
                "icon": "🔎",
                "path": "games/remainder/hunt.html"
            },
            {
                "name": "Thử thách modulo",
                "icon": "%",
                "path": "games/remainder/modulo.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 1
    },
    {
        "id": "DIVISIBILITY",
        "name": "Chia hết",
        "grade": 10,
        "games": [
            {
                "name": "Truy tìm số",
                "icon": "🔎",
                "path": "games/divisibility/find.html"
            },
            {
                "name": "Chọn số",
                "icon": "🎯",
                "path": "games/divisibility/select.html"
            },
            {
                "name": "Phá khóa",
                "icon": "🔐",
                "path": "games/divisibility/unlock.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 2
    },
    {
        "id": "FUNCTION",
        "name": "Hàm số",
        "grade": 10,
        "games": [
            {
                "name": "Bắt điểm",
                "icon": "🎯",
                "path": "games/function/point.html"
            },
            {
                "name": "Tìm giao điểm",
                "icon": "✖️",
                "path": "games/function/intersection.html"
            },
            {
                "name": "Đồ thị bí ẩn",
                "icon": "📈",
                "path": "games/function/graph.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 3
    },
    {
        "id": "ham_so_bac_nhat",
        "name": "Hàm số bậc nhất",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 4
    },
    {
        "id": "he_phuong_trinh",
        "name": "Hệ phương trình",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 5
    },
    {
        "id": "SYSTEM_EQUATION",
        "name": "Hệ phương trình",
        "grade": 10,
        "games": [
            {
                "name": "Điều tra",
                "icon": "🕵️",
                "path": "games/system-equation/investigation.html"
            },
            {
                "name": "Tìm giá trị",
                "icon": "🔢",
                "path": "games/system-equation/value.html"
            },
            {
                "name": "Ghép đáp án",
                "icon": "🧩",
                "path": "games/system-equation/match.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 6
    },
    {
        "id": "menh_de",
        "name": "Mệnh đề",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 7
    },
    {
        "id": "STATISTICS",
        "name": "Thống kê",
        "grade": 10,
        "games": [
            {
                "name": "Đọc biểu đồ",
                "icon": "📊",
                "path": "games/statistics/chart.html"
            },
            {
                "name": "Săn số liệu",
                "icon": "🔎",
                "path": "games/statistics/data.html"
            },
            {
                "name": "Thử thách thống kê",
                "icon": "🏆",
                "path": "games/statistics/challenge.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 8
    },
    {
        "id": "tap_hop",
        "name": "Tập hợp và các phép toán",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 9
    },
    {
        "id": "vector",
        "name": "Vectơ",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 10
    },
    {
        "id": "PROBABILITY",
        "name": "Xác suất",
        "grade": 10,
        "games": [
            {
                "name": "Bốc bi",
                "icon": "🔮",
                "path": "games/probability/marble.html"
            },
            {
                "name": "Xúc xắc",
                "icon": "🎲",
                "path": "games/probability/dice.html"
            },
            {
                "name": "Chọn tình huống",
                "icon": "🎯",
                "path": "games/probability/situation.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 11
    },
    {
        "id": "RADICAL",
        "name": "Căn thức",
        "grade": 10,
        "games": [
            {
                "name": "Săn căn",
                "icon": "√",
                "path": "games/radical/hunt.html"
            },
            {
                "name": "Rút gọn nhanh",
                "icon": "⚡",
                "path": "games/radical/simplify.html"
            },
            {
                "name": "Mở khóa căn thức",
                "icon": "🔓",
                "path": "games/radical/unlock.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 12
    },
    {
        "id": "SEQUENCE",
        "name": "Dãy số",
        "grade": 10,
        "games": [
            {
                "name": "Tìm quy luật",
                "icon": "🔍",
                "path": "games/sequence/rule.html"
            },
            {
                "name": "Điền số",
                "icon": "🔢",
                "path": "games/sequence/fill.html"
            },
            {
                "name": "Đường đua dãy số",
                "icon": "🏁",
                "path": "games/sequence/race.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 13
    },
    {
        "id": "GEOMETRY",
        "name": "Hình học",
        "grade": 10,
        "games": [
            {
                "name": "Tìm góc",
                "icon": "📐",
                "path": "games/geometry/angle.html"
            },
            {
                "name": "Săn độ dài",
                "icon": "📏",
                "path": "games/geometry/length.html"
            },
            {
                "name": "Bản đồ hình học",
                "icon": "🗺️",
                "path": "games/geometry/map.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 14
    },
    {
        "id": "menh_de_tap_hop",
        "name": "Mệnh đề và tập hợp",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 15
    },
    {
        "id": "phuong_trinh",
        "name": "Phương trình",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 16
    },
    {
        "id": "QUADRATIC_EQUATION",
        "name": "Phương trình bậc hai",
        "grade": 10,
        "games": [
            {
                "name": "Săn nghiệm",
                "icon": "🎯",
                "path": "games/quadratic-equation/root.html"
            },
            {
                "name": "Ghép nghiệm",
                "icon": "🧩",
                "path": "games/quadratic-equation/match.html"
            },
            {
                "name": "Mở khóa",
                "icon": "🔓",
                "path": "games/quadratic-equation/unlock.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 17
    },
    {
        "id": "toa_do_phang",
        "name": "Tọa độ trong mặt phẳng",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 18
    },
    {
        "id": "COMBINATION",
        "name": "Tổ hợp",
        "grade": 10,
        "games": [
            {
                "name": "Chọn đội",
                "icon": "👥",
                "path": "games/combination/team.html"
            },
            {
                "name": "Ghép lựa chọn",
                "icon": "🧩",
                "path": "games/combination/choice.html"
            },
            {
                "name": "Săn tổ hợp",
                "icon": "🔎",
                "path": "games/combination/hunt.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 19
    },
    {
        "id": "duong_thang",
        "name": "Đường thẳng",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 20
    },
    {
        "id": "duong_tron",
        "name": "Đường tròn",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 21
    },
    {
        "id": "bai_toan_thuc_te_10",
        "name": "Bài toán thực tế Toán 10",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 22
    },
    {
        "id": "INEQUALITY",
        "name": "Bất phương trình",
        "grade": 10,
        "games": [
            {
                "name": "Vùng an toàn",
                "icon": "🛡️",
                "path": "games/inequality/safe-zone.html"
            },
            {
                "name": "Chọn khoảng",
                "icon": "📏",
                "path": "games/inequality/interval.html"
            },
            {
                "name": "Vượt rào",
                "icon": "🚧",
                "path": "games/inequality/barrier.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 23
    },
    {
        "id": "PERMUTATION",
        "name": "Chỉnh hợp",
        "grade": 10,
        "games": [
            {
                "name": "Xếp vị trí",
                "icon": "📍",
                "path": "games/permutation/position.html"
            },
            {
                "name": "Mật mã",
                "icon": "🔐",
                "path": "games/permutation/code.html"
            },
            {
                "name": "Sắp thứ tự",
                "icon": "📋",
                "path": "games/permutation/order.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 24
    },
    {
        "id": "ham_so_bac_hai",
        "name": "Hàm số bậc hai và parabol",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 25
    },
    {
        "id": "IDENTITIES",
        "name": "Hằng đẳng thức",
        "grade": 10,
        "games": [
            {
                "name": "Ghép công thức",
                "icon": "🧩",
                "path": "games/identities/match.html"
            },
            {
                "name": "Phá biểu thức",
                "icon": "💥",
                "path": "games/identities/break.html"
            },
            {
                "name": "Công thức bí ẩn",
                "icon": "❓",
                "path": "games/identities/mystery.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 26
    },
    {
        "id": "he_bat_phuong_trinh",
        "name": "Hệ bất phương trình",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 27
    },
    {
        "id": "he_thuc_luong",
        "name": "Hệ thức lượng trong tam giác",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 28
    },
    {
        "id": "he_thuc_luong_tam_giac",
        "name": "Hệ thức lượng trong tam giác",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 29
    },
    {
        "id": "nhi_thuc_newton",
        "name": "Nhị thức Newton",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 30
    },
    {
        "id": "ALGEBRAIC_FRACTION",
        "name": "Phân thức đại số",
        "grade": 10,
        "games": [
            {
                "name": "Rút gọn",
                "icon": "➗",
                "path": "games/algebraic-fraction/simplify.html"
            },
            {
                "name": "Tìm điều kiện",
                "icon": "🔎",
                "path": "games/algebraic-fraction/condition.html"
            },
            {
                "name": "Phân thức tốc độ",
                "icon": "⚡",
                "path": "games/algebraic-fraction/speed.html"
            }
        ],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 31
    },
    {
        "id": "quy_tac_dem",
        "name": "Quy tắc đếm",
        "grade": 10,
        "games": [],
        "category": "TOÁN 10",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 32
    },
    {
        "id": "cong_thuc_luong_giac",
        "name": "Công thức lượng giác",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 33
    },
    {
        "id": "cap_so_cong",
        "name": "Cấp số cộng",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 34
    },
    {
        "id": "cap_so_nhan",
        "name": "Cấp số nhân",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 35
    },
    {
        "id": "day_so",
        "name": "Dãy số",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 36
    },
    {
        "id": "gia_tri_luong_giac",
        "name": "Giá trị lượng giác",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 37
    },
    {
        "id": "gioi_han",
        "name": "Giới hạn",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 38
    },
    {
        "id": "ham_so_luong_giac",
        "name": "Hàm số lượng giác",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 39
    },
    {
        "id": "thong_ke_11",
        "name": "Thống kê Toán 11",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 40
    },
    {
        "id": "xac_suat_11",
        "name": "Xác suất",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 41
    },
    {
        "id": "dao_ham",
        "name": "Đạo hàm",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 42
    },
    {
        "id": "bai_toan_thuc_te_11",
        "name": "Bài toán thực tế Toán 11",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 43
    },
    {
        "id": "day_so_tong_quat",
        "name": "Dãy số",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 44
    },
    {
        "id": "gioi_han_ham_so",
        "name": "Giới hạn hàm số",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 45
    },
    {
        "id": "goc_khoang_cach_11",
        "name": "Góc và khoảng cách trong không gian",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 46
    },
    {
        "id": "ham_so_lien_tuc",
        "name": "Hàm số liên tục",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 47
    },
    {
        "id": "phuong_trinh_luong_giac",
        "name": "Phương trình lượng giác",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 48
    },
    {
        "id": "song_song_khong_gian",
        "name": "Quan hệ song song trong không gian",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 49
    },
    {
        "id": "vuong_goc_khong_gian",
        "name": "Quan hệ vuông góc trong không gian",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 50
    },
    {
        "id": "dao_ham_quy_tac",
        "name": "Quy tắc đạo hàm",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 51
    },
    {
        "id": "ung_dung_dao_ham_11",
        "name": "Ứng dụng đạo hàm",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 52
    },
    {
        "id": "bien_co_doc_lap_11",
        "name": "Biến cố độc lập và xác suất có điều kiện",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 53
    },
    {
        "id": "bai_toan_thuc_te_tong_hop_11",
        "name": "Bài toán thực tế tổng hợp Toán 11",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 54
    },
    {
        "id": "day_so_truy_hoi_11",
        "name": "Dãy số truy hồi",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 55
    },
    {
        "id": "ham_so_luong_giac_day_du",
        "name": "Hàm số lượng giác",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 56
    },
    {
        "id": "phep_bien_hinh_11",
        "name": "Phép biến hình trong mặt phẳng",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 57
    },
    {
        "id": "phuong_trinh_luong_giac_day_du",
        "name": "Phương trình lượng giác",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 58
    },
    {
        "id": "hinh_khong_gian",
        "name": "Quan hệ song song và vuông góc trong không gian",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 59
    },
    {
        "id": "quy_nap_toan_hoc_11",
        "name": "Quy nạp toán học",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 60
    },
    {
        "id": "thiet_dien_hinh_khong_gian_11",
        "name": "Thiết diện hình không gian",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 61
    },
    {
        "id": "to_hop_xac_suat_nang_cao_11",
        "name": "Tổ hợp và xác suất nâng cao",
        "grade": 11,
        "games": [],
        "category": "TOÁN 11",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 62
    },
    {
        "id": "thong_ke_12",
        "name": "Các số đặc trưng đo xu thế và độ phân tán",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 63
    },
    {
        "id": "cuc_tri",
        "name": "Cực trị",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 64
    },
    {
        "id": "gtln_gtnn",
        "name": "Giá trị lớn nhất và nhỏ nhất",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 65
    },
    {
        "id": "ham_logarit",
        "name": "Hàm số logarit",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 66
    },
    {
        "id": "ham_mu",
        "name": "Hàm số mũ",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 67
    },
    {
        "id": "hinh_hoc_khong_gian",
        "name": "Hình học không gian",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 68
    },
    {
        "id": "so_phuc",
        "name": "Số phức",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 69
    },
    {
        "id": "tinh_don_dieu",
        "name": "Tính đơn điệu",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 70
    },
    {
        "id": "toa_do_khong_gian",
        "name": "Tọa độ trong không gian",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 71
    },
    {
        "id": "xac_suat_12",
        "name": "Xác suất và biến ngẫu nhiên",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "foundation",
        "id_num": 72
    },
    {
        "id": "bieu_dien_so_phuc",
        "name": "Biểu diễn số phức",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 73
    },
    {
        "id": "khao_sat_ham_so",
        "name": "Khảo sát và vẽ đồ thị hàm số",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 74
    },
    {
        "id": "mat_phang_oxyz",
        "name": "Mặt phẳng trong Oxyz",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 75
    },
    {
        "id": "nguyen_ham_tich_phan",
        "name": "Nguyên hàm và tích phân",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 76
    },
    {
        "id": "pt_logarit",
        "name": "Phương trình logarit",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 77
    },
    {
        "id": "pt_mu",
        "name": "Phương trình mũ",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 78
    },
    {
        "id": "tiep_tuyen",
        "name": "Tiếp tuyến",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 79
    },
    {
        "id": "tien_can",
        "name": "Tiệm cận",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 80
    },
    {
        "id": "duong_thang_oxyz",
        "name": "Đường thẳng trong Oxyz",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 81
    },
    {
        "id": "ung_dung_dao_ham",
        "name": "Ứng dụng đạo hàm",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "medium",
        "id_num": 82
    },
    {
        "id": "bai_toan_thuc_te_12",
        "name": "Bài toán thực tế Toán 12",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 83
    },
    {
        "id": "tong_hop_thpt",
        "name": "Bài toán tổng hợp THPT",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 84
    },
    {
        "id": "bpt_logarit",
        "name": "Bất phương trình logarit",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 85
    },
    {
        "id": "bpt_mu",
        "name": "Bất phương trình mũ",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 86
    },
    {
        "id": "goc_khoang_cach_oxyz",
        "name": "Góc và khoảng cách Oxyz",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 87
    },
    {
        "id": "mat_cau",
        "name": "Mặt cầu",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 88
    },
    {
        "id": "pt_so_phuc",
        "name": "Phương trình số phức",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 89
    },
    {
        "id": "the_tich_khong_gian",
        "name": "Thể tích hình học không gian",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 90
    },
    {
        "id": "tuong_giao",
        "name": "Tương giao đồ thị",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 91
    },
    {
        "id": "ung_dung_tich_phan",
        "name": "Ứng dụng tích phân",
        "grade": 12,
        "games": [],
        "category": "TOÁN 12",
        "description": "Luyện tập kiến thức theo chương trình THPT, từ nền tảng đến vận dụng nâng cao.",
        "level_key": "advanced",
        "id_num": 92
    },
    {
        "id": "hinh_hoc_co_ban_10",
        "name": "Hình học cơ bản: góc, cạnh và diện tích",
        "grade": 10,
        "games": [
            {
                "name": "Hình học cơ bản: góc, cạnh và diện tích [hinh_hoc_co_ban_10] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/hinh-hoc-co-ban-10/1-kham-pha.html"
            },
            {
                "name": "Hình học cơ bản: góc, cạnh và diện tích [hinh_hoc_co_ban_10] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/hinh-hoc-co-ban-10/2-nhiem-vu.html"
            },
            {
                "name": "Hình học cơ bản: góc, cạnh và diện tích [hinh_hoc_co_ban_10] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/hinh-hoc-co-ban-10/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 10 · HÌNH HỌC",
        "description": "Luyện tập hình học cơ bản: góc, cạnh và diện tích với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "foundation",
        "id_num": 93
    },
    {
        "id": "tam_giac_tu_giac_10",
        "name": "Tam giác và tứ giác cơ bản",
        "grade": 10,
        "games": [
            {
                "name": "Tam giác và tứ giác cơ bản [tam_giac_tu_giac_10] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/tam-giac-tu-giac-10/1-kham-pha.html"
            },
            {
                "name": "Tam giác và tứ giác cơ bản [tam_giac_tu_giac_10] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/tam-giac-tu-giac-10/2-nhiem-vu.html"
            },
            {
                "name": "Tam giác và tứ giác cơ bản [tam_giac_tu_giac_10] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/tam-giac-tu-giac-10/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 10 · HÌNH HỌC",
        "description": "Luyện tập tam giác và tứ giác cơ bản với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "foundation",
        "id_num": 94
    },
    {
        "id": "duong_tron_co_ban_10",
        "name": "Đường tròn và các góc cơ bản",
        "grade": 10,
        "games": [
            {
                "name": "Đường tròn và các góc cơ bản [duong_tron_co_ban_10] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/duong-tron-co-ban-10/1-kham-pha.html"
            },
            {
                "name": "Đường tròn và các góc cơ bản [duong_tron_co_ban_10] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/duong-tron-co-ban-10/2-nhiem-vu.html"
            },
            {
                "name": "Đường tròn và các góc cơ bản [duong_tron_co_ban_10] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/duong-tron-co-ban-10/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 10 · HÌNH HỌC",
        "description": "Luyện tập đường tròn và các góc cơ bản với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "foundation",
        "id_num": 95
    },
    {
        "id": "he_thuc_luong_van_dung_10",
        "name": "Hệ thức lượng trong tam giác",
        "grade": 10,
        "games": [
            {
                "name": "Hệ thức lượng trong tam giác [he_thuc_luong_van_dung_10] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/he-thuc-luong-van-dung-10/1-kham-pha.html"
            },
            {
                "name": "Hệ thức lượng trong tam giác [he_thuc_luong_van_dung_10] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/he-thuc-luong-van-dung-10/2-nhiem-vu.html"
            },
            {
                "name": "Hệ thức lượng trong tam giác [he_thuc_luong_van_dung_10] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/he-thuc-luong-van-dung-10/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 10 · HÌNH HỌC",
        "description": "Luyện tập hệ thức lượng trong tam giác với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "medium",
        "id_num": 96
    },
    {
        "id": "toa_do_hinh_hoc_10",
        "name": "Tọa độ và đường thẳng trong mặt phẳng",
        "grade": 10,
        "games": [
            {
                "name": "Tọa độ và đường thẳng trong mặt phẳng [toa_do_hinh_hoc_10] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/toa-do-hinh-hoc-10/1-kham-pha.html"
            },
            {
                "name": "Tọa độ và đường thẳng trong mặt phẳng [toa_do_hinh_hoc_10] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/toa-do-hinh-hoc-10/2-nhiem-vu.html"
            },
            {
                "name": "Tọa độ và đường thẳng trong mặt phẳng [toa_do_hinh_hoc_10] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/toa-do-hinh-hoc-10/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 10 · HÌNH HỌC",
        "description": "Luyện tập tọa độ và đường thẳng trong mặt phẳng với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "medium",
        "id_num": 97
    },
    {
        "id": "chung_minh_hinh_hoc_10",
        "name": "Chứng minh hình học và bài toán tổng hợp",
        "grade": 10,
        "games": [
            {
                "name": "Chứng minh hình học và bài toán tổng hợp [chung_minh_hinh_hoc_10] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/chung-minh-hinh-hoc-10/1-kham-pha.html"
            },
            {
                "name": "Chứng minh hình học và bài toán tổng hợp [chung_minh_hinh_hoc_10] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/chung-minh-hinh-hoc-10/2-nhiem-vu.html"
            },
            {
                "name": "Chứng minh hình học và bài toán tổng hợp [chung_minh_hinh_hoc_10] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/chung-minh-hinh-hoc-10/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 10 · HÌNH HỌC",
        "description": "Luyện tập chứng minh hình học và bài toán tổng hợp với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "advanced",
        "id_num": 98
    },
    {
        "id": "phep_bien_hinh_co_ban_11",
        "name": "Phép biến hình cơ bản",
        "grade": 11,
        "games": [
            {
                "name": "Phép biến hình cơ bản [phep_bien_hinh_co_ban_11] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/phep-bien-hinh-co-ban-11/1-kham-pha.html"
            },
            {
                "name": "Phép biến hình cơ bản [phep_bien_hinh_co_ban_11] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/phep-bien-hinh-co-ban-11/2-nhiem-vu.html"
            },
            {
                "name": "Phép biến hình cơ bản [phep_bien_hinh_co_ban_11] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/phep-bien-hinh-co-ban-11/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 11 · HÌNH HỌC",
        "description": "Luyện tập phép biến hình cơ bản với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "foundation",
        "id_num": 99
    },
    {
        "id": "nhan_biet_hinh_khong_gian_11",
        "name": "Nhận biết hình học không gian",
        "grade": 11,
        "games": [
            {
                "name": "Nhận biết hình học không gian [nhan_biet_hinh_khong_gian_11] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/nhan-biet-hinh-khong-gian-11/1-kham-pha.html"
            },
            {
                "name": "Nhận biết hình học không gian [nhan_biet_hinh_khong_gian_11] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/nhan-biet-hinh-khong-gian-11/2-nhiem-vu.html"
            },
            {
                "name": "Nhận biết hình học không gian [nhan_biet_hinh_khong_gian_11] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/nhan-biet-hinh-khong-gian-11/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 11 · HÌNH HỌC",
        "description": "Luyện tập nhận biết hình học không gian với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "foundation",
        "id_num": 100
    },
    {
        "id": "hinh_khoi_va_the_tich_co_ban_12",
        "name": "Hình khối và thể tích cơ bản",
        "grade": 12,
        "games": [
            {
                "name": "Hình khối và thể tích cơ bản [hinh_khoi_va_the_tich_co_ban_12] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/hinh-khoi-va-the-tich-co-ban-12/1-kham-pha.html"
            },
            {
                "name": "Hình khối và thể tích cơ bản [hinh_khoi_va_the_tich_co_ban_12] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/hinh-khoi-va-the-tich-co-ban-12/2-nhiem-vu.html"
            },
            {
                "name": "Hình khối và thể tích cơ bản [hinh_khoi_va_the_tich_co_ban_12] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/hinh-khoi-va-the-tich-co-ban-12/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 12 · HÌNH HỌC",
        "description": "Luyện tập hình khối và thể tích cơ bản với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "foundation",
        "id_num": 101
    },
    {
        "id": "hinh_hoc_oxyz_van_dung_12",
        "name": "Vận dụng tọa độ Oxyz",
        "grade": 12,
        "games": [
            {
                "name": "Vận dụng tọa độ Oxyz [hinh_hoc_oxyz_van_dung_12] • Khám phá",
                "icon": "🔎",
                "path": "games/knowledge/hinh-hoc-oxyz-van-dung-12/1-kham-pha.html"
            },
            {
                "name": "Vận dụng tọa độ Oxyz [hinh_hoc_oxyz_van_dung_12] • Nhiệm vụ",
                "icon": "🧩",
                "path": "games/knowledge/hinh-hoc-oxyz-van-dung-12/2-nhiem-vu.html"
            },
            {
                "name": "Vận dụng tọa độ Oxyz [hinh_hoc_oxyz_van_dung_12] • Trùm cuối",
                "icon": "🏆",
                "path": "games/knowledge/hinh-hoc-oxyz-van-dung-12/3-trum-cuoi.html"
            }
        ],
        "category": "TOÁN 12 · HÌNH HỌC",
        "description": "Luyện tập vận dụng tọa độ oxyz với dữ kiện rõ ràng, hình minh họa đúng quan hệ và thử thách nhiều bước.",
        "level_key": "medium",
        "id_num": 102
    },
{
            "id": "g10_geom_angles_parallel",
            "name": "Góc tạo bởi hai đường thẳng và đường cắt",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_angles_parallel/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_angles_parallel/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_angles_parallel/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Góc tạo bởi hai đường thẳng và đường cắt. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1001,
            "geometry": true
        },
        {
            "id": "g10_geom_triangle_congruence",
            "name": "Các trường hợp bằng nhau của tam giác",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_triangle_congruence/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_triangle_congruence/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_triangle_congruence/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Các trường hợp bằng nhau của tam giác. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1002,
            "geometry": true
        },
        {
            "id": "g10_geom_special_lines",
            "name": "Đường trung tuyến, phân giác và đường cao",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_special_lines/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_special_lines/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_special_lines/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Đường trung tuyến, phân giác và đường cao. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1003,
            "geometry": true
        },
        {
            "id": "g10_geom_quadrilaterals_properties",
            "name": "Tính chất hình bình hành và hình thoi",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_quadrilaterals_properties/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_quadrilaterals_properties/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_quadrilaterals_properties/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Tính chất hình bình hành và hình thoi. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1004,
            "geometry": true
        },
        {
            "id": "g10_geom_circle_chords_arcs",
            "name": "Dây cung, cung và khoảng cách đến tâm",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_circle_chords_arcs/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_circle_chords_arcs/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_circle_chords_arcs/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Dây cung, cung và khoảng cách đến tâm. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1005,
            "geometry": true
        },
        {
            "id": "g10_geom_thales_similarity",
            "name": "Định lý Thales và tam giác đồng dạng",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_thales_similarity/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_thales_similarity/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_thales_similarity/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Định lý Thales và tam giác đồng dạng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1006,
            "geometry": true
        },
        {
            "id": "g10_geom_triangle_area_ratio",
            "name": "Tỉ số diện tích tam giác",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_triangle_area_ratio/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_triangle_area_ratio/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_triangle_area_ratio/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Tỉ số diện tích tam giác. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1007,
            "geometry": true
        },
        {
            "id": "g10_geom_circle_angles",
            "name": "Góc nội tiếp và góc ở tâm nâng cao",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_circle_angles/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_circle_angles/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_circle_angles/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Góc nội tiếp và góc ở tâm nâng cao. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1008,
            "geometry": true
        },
        {
            "id": "g10_geom_coordinate_distance_midpoint",
            "name": "Trung điểm và khoảng cách trong tọa độ phẳng",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_coordinate_distance_midpoint/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_coordinate_distance_midpoint/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_coordinate_distance_midpoint/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Trung điểm và khoảng cách trong tọa độ phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1009,
            "geometry": true
        },
        {
            "id": "g10_geom_line_intersections",
            "name": "Giao điểm và vị trí tương đối của hai đường thẳng",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_line_intersections/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_line_intersections/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_line_intersections/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Giao điểm và vị trí tương đối của hai đường thẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1010,
            "geometry": true
        },
        {
            "id": "g10_geom_locus",
            "name": "Quỹ tích điểm trong mặt phẳng",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_locus/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_locus/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_locus/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Quỹ tích điểm trong mặt phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1011,
            "geometry": true
        },
        {
            "id": "g10_geom_circle_tangent_chord",
            "name": "Tiếp tuyến và dây cung của đường tròn",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_circle_tangent_chord/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_circle_tangent_chord/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_circle_tangent_chord/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Tiếp tuyến và dây cung của đường tròn. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1012,
            "geometry": true
        },
        {
            "id": "g10_geom_triangle_inequalities",
            "name": "Bất đẳng thức và cực trị trong tam giác",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_triangle_inequalities/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_triangle_inequalities/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_triangle_inequalities/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Bất đẳng thức và cực trị trong tam giác. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1013,
            "geometry": true
        },
        {
            "id": "g10_geom_vector_proofs",
            "name": "Chứng minh hình học bằng vectơ",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_vector_proofs/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_vector_proofs/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_vector_proofs/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Chứng minh hình học bằng vectơ. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1014,
            "geometry": true
        },
        {
            "id": "g10_geom_coordinate_circle_line",
            "name": "Bài toán tổng hợp đường thẳng và đường tròn tọa độ",
            "grade": 10,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g10_geom_coordinate_circle_line/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g10_geom_coordinate_circle_line/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g10_geom_coordinate_circle_line/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 10 • HÌNH HỌC",
            "description": "Bài toán tổng hợp đường thẳng và đường tròn tọa độ. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1015,
            "geometry": true
        },
        {
            "id": "g11_geom_transform_translation",
            "name": "Phép tịnh tiến và ảnh của hình",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_transform_translation/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_transform_translation/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_transform_translation/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Phép tịnh tiến và ảnh của hình. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1016,
            "geometry": true
        },
        {
            "id": "g11_geom_transform_reflection",
            "name": "Phép đối xứng trục",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_transform_reflection/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_transform_reflection/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_transform_reflection/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Phép đối xứng trục. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1017,
            "geometry": true
        },
        {
            "id": "g11_geom_space_lines_planes",
            "name": "Nhận biết đường thẳng và mặt phẳng trong không gian",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_space_lines_planes/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_space_lines_planes/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_space_lines_planes/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Nhận biết đường thẳng và mặt phẳng trong không gian. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1018,
            "geometry": true
        },
        {
            "id": "g11_geom_parallel_line_plane",
            "name": "Đường thẳng song song với mặt phẳng",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_parallel_line_plane/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_parallel_line_plane/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_parallel_line_plane/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Đường thẳng song song với mặt phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1019,
            "geometry": true
        },
        {
            "id": "g11_geom_prism_pyramid_sections",
            "name": "Mặt bên, cạnh bên và đáy của lăng trụ, hình chóp",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_prism_pyramid_sections/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_prism_pyramid_sections/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_prism_pyramid_sections/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Mặt bên, cạnh bên và đáy của lăng trụ, hình chóp. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1020,
            "geometry": true
        },
        {
            "id": "g11_geom_rotation_homothety",
            "name": "Phép quay và phép vị tự",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_rotation_homothety/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_rotation_homothety/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_rotation_homothety/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Phép quay và phép vị tự. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1021,
            "geometry": true
        },
        {
            "id": "g11_geom_parallel_planes",
            "name": "Hai mặt phẳng song song",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_parallel_planes/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_parallel_planes/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_parallel_planes/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Hai mặt phẳng song song. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1022,
            "geometry": true
        },
        {
            "id": "g11_geom_perpendicular_line_plane",
            "name": "Đường thẳng vuông góc với mặt phẳng",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_perpendicular_line_plane/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_perpendicular_line_plane/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_perpendicular_line_plane/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Đường thẳng vuông góc với mặt phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1023,
            "geometry": true
        },
        {
            "id": "g11_geom_dihedral_angles",
            "name": "Góc giữa đường thẳng và mặt phẳng",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_dihedral_angles/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_dihedral_angles/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_dihedral_angles/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Góc giữa đường thẳng và mặt phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1024,
            "geometry": true
        },
        {
            "id": "g11_geom_section_construction",
            "name": "Dựng thiết diện của hình chóp và lăng trụ",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_section_construction/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_section_construction/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_section_construction/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Dựng thiết diện của hình chóp và lăng trụ. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1025,
            "geometry": true
        },
        {
            "id": "g11_geom_skew_lines_distance",
            "name": "Khoảng cách giữa hai đường thẳng chéo nhau",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_skew_lines_distance/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_skew_lines_distance/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_skew_lines_distance/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Khoảng cách giữa hai đường thẳng chéo nhau. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1026,
            "geometry": true
        },
        {
            "id": "g11_geom_three_perpendiculars",
            "name": "Định lý ba đường vuông góc",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_three_perpendiculars/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_three_perpendiculars/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_three_perpendiculars/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Định lý ba đường vuông góc. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1027,
            "geometry": true
        },
        {
            "id": "g11_geom_transform_composition",
            "name": "Hợp thành các phép biến hình",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_transform_composition/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_transform_composition/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_transform_composition/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Hợp thành các phép biến hình. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1028,
            "geometry": true
        },
        {
            "id": "g11_geom_section_ratio",
            "name": "Thiết diện và tỉ số đoạn trong hình không gian",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_section_ratio/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_section_ratio/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_section_ratio/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Thiết diện và tỉ số đoạn trong hình không gian. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1029,
            "geometry": true
        },
        {
            "id": "g11_geom_space_proof",
            "name": "Chứng minh tổng hợp song song và vuông góc",
            "grade": 11,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g11_geom_space_proof/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g11_geom_space_proof/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g11_geom_space_proof/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 11 • HÌNH HỌC",
            "description": "Chứng minh tổng hợp song song và vuông góc. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1030,
            "geometry": true
        },
        {
            "id": "g12_geom_vectors_3d",
            "name": "Vectơ và độ dài trong không gian Oxyz",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_vectors_3d/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_vectors_3d/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_vectors_3d/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Vectơ và độ dài trong không gian Oxyz. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1031,
            "geometry": true
        },
        {
            "id": "g12_geom_plane_equation",
            "name": "Phương trình mặt phẳng",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_plane_equation/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_plane_equation/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_plane_equation/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Phương trình mặt phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1032,
            "geometry": true
        },
        {
            "id": "g12_geom_line_equation_3d",
            "name": "Phương trình đường thẳng trong Oxyz",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_line_equation_3d/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_line_equation_3d/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_line_equation_3d/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Phương trình đường thẳng trong Oxyz. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1033,
            "geometry": true
        },
        {
            "id": "g12_geom_sphere_equation",
            "name": "Phương trình mặt cầu và tâm bán kính",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_sphere_equation/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_sphere_equation/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_sphere_equation/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Phương trình mặt cầu và tâm bán kính. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1034,
            "geometry": true
        },
        {
            "id": "g12_geom_solid_surface_area",
            "name": "Diện tích xung quanh và toàn phần hình khối",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_solid_surface_area/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_solid_surface_area/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_solid_surface_area/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Diện tích xung quanh và toàn phần hình khối. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "foundation",
            "id_num": 1035,
            "geometry": true
        },
        {
            "id": "g12_geom_point_plane_distance",
            "name": "Khoảng cách từ điểm đến mặt phẳng",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_point_plane_distance/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_point_plane_distance/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_point_plane_distance/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Khoảng cách từ điểm đến mặt phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1036,
            "geometry": true
        },
        {
            "id": "g12_geom_line_plane_angle",
            "name": "Góc giữa đường thẳng và mặt phẳng Oxyz",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_line_plane_angle/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_line_plane_angle/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_line_plane_angle/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Góc giữa đường thẳng và mặt phẳng Oxyz. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1037,
            "geometry": true
        },
        {
            "id": "g12_geom_two_planes_angle",
            "name": "Góc giữa hai mặt phẳng",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_two_planes_angle/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_two_planes_angle/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_two_planes_angle/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Góc giữa hai mặt phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1038,
            "geometry": true
        },
        {
            "id": "g12_geom_line_plane_intersection",
            "name": "Giao điểm đường thẳng và mặt phẳng",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_line_plane_intersection/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_line_plane_intersection/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_line_plane_intersection/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Giao điểm đường thẳng và mặt phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1039,
            "geometry": true
        },
        {
            "id": "g12_geom_sphere_tangent_plane",
            "name": "Mặt phẳng tiếp xúc với mặt cầu",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_sphere_tangent_plane/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_sphere_tangent_plane/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_sphere_tangent_plane/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Mặt phẳng tiếp xúc với mặt cầu. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "medium",
            "id_num": 1040,
            "geometry": true
        },
        {
            "id": "g12_geom_skew_line_relation",
            "name": "Vị trí tương đối của hai đường thẳng trong Oxyz",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_skew_line_relation/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_skew_line_relation/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_skew_line_relation/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Vị trí tương đối của hai đường thẳng trong Oxyz. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1041,
            "geometry": true
        },
        {
            "id": "g12_geom_min_distance_3d",
            "name": "Cực trị khoảng cách trong không gian tọa độ",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_min_distance_3d/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_min_distance_3d/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_min_distance_3d/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Cực trị khoảng cách trong không gian tọa độ. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1042,
            "geometry": true
        },
        {
            "id": "g12_geom_sphere_plane_intersection",
            "name": "Giao tuyến mặt cầu và mặt phẳng",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_sphere_plane_intersection/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_sphere_plane_intersection/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_sphere_plane_intersection/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Giao tuyến mặt cầu và mặt phẳng. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1043,
            "geometry": true
        },
        {
            "id": "g12_geom_parameter_geometry",
            "name": "Bài toán tham số hình học Oxyz",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_parameter_geometry/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_parameter_geometry/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_parameter_geometry/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Bài toán tham số hình học Oxyz. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1044,
            "geometry": true
        },
        {
            "id": "g12_geom_3d_optimization",
            "name": "Bài toán tối ưu hình học không gian",
            "grade": 12,
            "games": [
                {
                    "name": "Khám phá hình",
                    "icon": "🧭",
                    "path": "games/knowledge/g12_geom_3d_optimization/1-kham-pha.html"
                },
                {
                    "name": "Nhiệm vụ hình học",
                    "icon": "📐",
                    "path": "games/knowledge/g12_geom_3d_optimization/2-nhiem-vu.html"
                },
                {
                    "name": "Trùm cuối hình học",
                    "icon": "🏆",
                    "path": "games/knowledge/g12_geom_3d_optimization/3-trum-cuoi.html"
                }
            ],
            "category": "TOÁN 12 • HÌNH HỌC",
            "description": "Bài toán tối ưu hình học không gian. Có câu hỏi AI theo chủ đề, lời giải và hình minh họa khi dữ kiện cho phép.",
            "level_key": "advanced",
            "id_num": 1045,
            "geometry": true
        }
];

    /* =====================================================
       DOM
       ===================================================== */

    const knowledgeGrid =
        document.getElementById("knowledgeGrid");

    const knowledgeCount =
        document.getElementById("knowledgeCount");

    const practiceOverlay =
        document.getElementById("practiceOverlay");

    const knowledgePopup =
        document.getElementById("knowledgePopup");

    const popupClose =
        document.getElementById("popupClose");

    const popupNumber =
        document.getElementById("popupNumber");

    const popupCategory =
        document.getElementById("popupCategory");

    const popupTitle =
        document.getElementById("popupTitle");

    const popupTopic =
        document.getElementById("popupTopic");

    const popupLevel =
        document.getElementById("popupLevel");

    const popupDescription =
        document.getElementById("popupDescription");

    const gameList =
        document.getElementById("gameList");


    /* =====================================================
       CARD COLORS
       ===================================================== */

    const cardColors = [
        "color-cyan",
        "color-blue",
        "color-purple",
        "color-pink",
        "color-green"
    ];


    /* =====================================================
       STATE
       ===================================================== */

    let currentKnowledge = null;

    let lastFocusedElement = null;

    let isPopupOpen = false;

    let aiPracticeOpen = false;

    let aiQuestions = [];

    let aiCurrentIndex = 0;

    let aiHistory = [];

    let aiScore = 0;

    let aiCorrect = 0;

    let aiWrong = 0;

    let aiSkipped = 0;

    let aiAnswered = false;

    let aiSessionStartedAt = 0;

    let aiQuestionStartedAt = 0;

    let aiTimer = null;

    let aiCurrentSettings = {
        grade: DEFAULT_GRADE,
        difficulty: DEFAULT_DIFFICULTY,
        question_type: DEFAULT_QUESTION_TYPE,
        count: DEFAULT_COUNT,
        problem_mode: false,
        problem_parts: 4
    };


    /* =====================================================
       FORMAT NUMBER
       ===================================================== */

    function formatNumber(number) {

        const value = Number(number);

        if (!Number.isFinite(value)) {
            return "00";
        }

        return String(
            Math.max(
                0,
                Math.trunc(value)
            )
        ).padStart(2, "0");

    }


    /* =====================================================
       HTML ESCAPE
       ===================================================== */

    function escapeHTML(value) {

        const text =
            String(
                value === null ||
                value === undefined
                    ? ""
                    : value
            );

        return text
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");

    }


    /* =====================================================
       API REQUEST
       ===================================================== */

    async function apiRequest(
        url,
        options = {}
    ) {

        const config = {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        };

        const response =
            await fetch(
                url,
                config
            );

        let data = null;

        try {
            data = await response.json();
        } catch {
            data = null;
        }

        if (!response.ok) {

            let message =
                "Không thể kết nối máy chủ AI.";

            if (
                data &&
                typeof data.detail === "string"
            ) {
                message = data.detail;
            }

            throw new Error(message);

        }

        return data;

    }


    /* =====================================================
       VALIDATE DOM
       ===================================================== */

    function hasRequiredDOM() {

        const requiredElements = [

            knowledgeGrid,
            knowledgeCount,
            practiceOverlay,
            knowledgePopup,
            popupClose,
            popupNumber,
            popupCategory,
            popupTitle,
            popupTopic,
            popupLevel,
            popupDescription,
            gameList

        ];

        return requiredElements.every(
            function (element) {
                return element instanceof HTMLElement;
            }
        );

    }


    /* =====================================================
       VALIDATE KNOWLEDGE
       ===================================================== */

    function isValidKnowledge(knowledge) {

        if (
            !knowledge ||
            typeof knowledge !== "object"
        ) {
            return false;
        }

        const knowledgeId = knowledge.id;
        const hasValidId =
            (typeof knowledgeId === "number" && Number.isFinite(knowledgeId)) ||
            (typeof knowledgeId === "string" && knowledgeId.trim().length > 0);

        if (!hasValidId) {
            return false;
        }

        if (
            typeof knowledge.name !== "string" ||
            !knowledge.name.trim()
        ) {
            return false;
        }

        if (
            !Array.isArray(knowledge.games)
        ) {
            return false;
        }

        return true;

    }


    /* =====================================================
       VALIDATE GAME
       ===================================================== */

    function isValidGame(game) {

        if (
            !game ||
            typeof game !== "object"
        ) {
            return false;
        }

        if (
            typeof game.name !== "string" ||
            !game.name.trim()
        ) {
            return false;
        }

        if (
            typeof game.path !== "string" ||
            !game.path.trim()
        ) {
            return false;
        }

        return true;

    }


    /* =====================================================
       SAFE GAME PATH
       ===================================================== */

    function getSafeGamePath(path) {

        if (
            typeof path !== "string"
        ) {
            return null;
        }

        const cleanPath =
            path.trim();

        if (!cleanPath) {
            return null;
        }

        const lowerPath =
            cleanPath.toLowerCase();

        if (
            lowerPath.startsWith(
                "javascript:"
            ) ||
            lowerPath.startsWith(
                "data:"
            ) ||
            lowerPath.startsWith(
                "vbscript:"
            )
        ) {
            return null;
        }

        return cleanPath;

    }


    /* =====================================================
       RENDER KNOWLEDGE
       ===================================================== */

    function getKnowledgeLevel(knowledge) {
        const level = String(knowledge?.level_key || "").toLowerCase();
        if (level === "foundation" || level === "medium" || level === "advanced") {
            return level;
        }
        return "medium";
    }

    function renderKnowledgeCard(knowledge, index) {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "knowledge-card " + cardColors[index % cardColors.length];
        card.setAttribute("aria-label", "Kiến thức " + knowledge.name);
        card.setAttribute("aria-haspopup", "dialog");
        card.setAttribute("aria-expanded", "false");

        const number = document.createElement("span");
        number.className = "knowledge-number";
        number.textContent = formatNumber(index + 1);

        const top = document.createElement("div");
        top.className = "knowledge-card-top";
        top.appendChild(number);

        const gradeBadge = document.createElement("span");
        gradeBadge.className = "knowledge-grade-badge";
        gradeBadge.textContent = `Toán ${knowledge.grade}`;
        top.appendChild(gradeBadge);
        card.appendChild(top);

        const icon = document.createElement("span");
        icon.className = "knowledge-icon";
        icon.textContent = knowledge.level_key === "foundation" ? "🔰" : knowledge.level_key === "medium" ? "🔵" : "🟣";
        card.appendChild(icon);

        const title = document.createElement("h3");
        title.textContent = knowledge.name;
        card.appendChild(title);

        const description = document.createElement("p");
        description.textContent = knowledge.description || "Luyện tập kiến thức toán THPT.";
        card.appendChild(description);

        const bottom = document.createElement("div");
        bottom.className = "knowledge-card-bottom";
        const levels = document.createElement("span");
        levels.className = "knowledge-games";
        levels.textContent = "AI + Game";
        bottom.appendChild(levels);
        const enter = document.createElement("span");
        enter.className = "knowledge-enter";
        enter.textContent = "MỞ →";
        bottom.appendChild(enter);
        card.appendChild(bottom);

        card.addEventListener("click", function () {
            openKnowledge(knowledge, card);
        });

        return card;
    }

    function renderKnowledge() {
        if (!hasRequiredDOM()) {
            console.error("MATH WEB: Không tìm thấy đầy đủ DOM của practise.html.");
            return false;
        }

        knowledgeGrid.replaceChildren();
        const visibleKnowledge = knowledgeData.filter(k => Number(k.grade) >= 10 && Number(k.grade) <= 12 && isValidKnowledge(k));
        knowledgeCount.textContent = String(visibleKnowledge.length);

        const gradeNames = { 10: "📘 TOÁN 10", 11: "📗 TOÁN 11", 12: "📕 TOÁN 12" };
        const levelInfo = {
            foundation: { title: "🔰 NỀN TẢNG", subtitle: "Kiến thức cốt lõi, làm chắc từng bước.", className: "level-foundation" },
            medium: { title: "🔵 TRUNG CẤP", subtitle: "Vận dụng, kết hợp dữ kiện và bài toán thực tế.", className: "level-medium" },
            advanced: { title: "🟣 NÂNG CAO", subtitle: "Vận dụng cao, biến đổi nhiều bước và thử thách tổng hợp.", className: "level-advanced" }
        };

        [10, 11, 12].forEach(function (grade) {
            const gradeSection = document.createElement("section");
            gradeSection.className = "knowledge-grade-section";
            gradeSection.dataset.grade = String(grade);

            const gradeHeader = document.createElement("div");
            gradeHeader.className = "knowledge-grade-header";
            const gradeTitle = document.createElement("h2");
            gradeTitle.textContent = gradeNames[grade];
            const gradeCount = document.createElement("span");
            const gradeItems = knowledgeData.filter(k => Number(k.grade) === grade && isValidKnowledge(k));
            gradeCount.textContent = `${gradeItems.length} chuyên đề`;
            gradeHeader.appendChild(gradeTitle);
            gradeHeader.appendChild(gradeCount);
            gradeSection.appendChild(gradeHeader);

            ["foundation", "medium", "advanced"].forEach(function (levelKey) {
                const info = levelInfo[levelKey];
                const items = gradeItems.filter(k => getKnowledgeLevel(k) === levelKey);
                if (!items.length) return;

                const levelSection = document.createElement("div");
                levelSection.className = `knowledge-level-section ${info.className}`;

                const levelHeader = document.createElement("div");
                levelHeader.className = "knowledge-level-header";
                const levelTitleWrap = document.createElement("div");
                const levelTitle = document.createElement("h3");
                levelTitle.textContent = info.title;
                const levelSubtitle = document.createElement("p");
                levelSubtitle.textContent = info.subtitle;
                levelTitleWrap.appendChild(levelTitle);
                levelTitleWrap.appendChild(levelSubtitle);
                const levelCount = document.createElement("span");
                levelCount.className = "knowledge-level-count";
                levelCount.textContent = `${items.length} bài học`;
                levelHeader.appendChild(levelTitleWrap);
                levelHeader.appendChild(levelCount);
                levelSection.appendChild(levelHeader);

                const grid = document.createElement("div");
                grid.className = "knowledge-grid knowledge-level-grid";
                items.forEach(function (knowledge, localIndex) {
                    grid.appendChild(renderKnowledgeCard(knowledge, localIndex));
                });
                levelSection.appendChild(grid);
                gradeSection.appendChild(levelSection);
            });

            knowledgeGrid.appendChild(gradeSection);
        });

        return true;
    }


    /* =====================================================
       OPEN KNOWLEDGE
       ===================================================== */

    function openKnowledge(
        knowledge,
        triggerElement
    ) {

        if (
            !isValidKnowledge(
                knowledge
            )
        ) {
            return false;
        }

        if (
            !hasRequiredDOM()
        ) {
            return false;
        }


        currentKnowledge =
            knowledge;

        lastFocusedElement =
            triggerElement instanceof HTMLElement
                ? triggerElement
                : document.activeElement;


        popupNumber.textContent =
            formatNumber(
                knowledge.id
            );

        popupCategory.textContent =
            String(
                knowledge.category ||
                ""
            );

        popupTitle.textContent =
            knowledge.name;

        popupTopic.textContent =
            knowledge.name;

        popupLevel.textContent =
            String(
                knowledge.level ||
                ""
            );

        popupDescription.textContent =
            String(
                knowledge.description ||
                ""
            );


        renderGames(
            ensureKnowledgeGames(knowledge)
        );

        addAIPracticeButton();


        practiceOverlay.classList.add(
            "active"
        );

        knowledgePopup.classList.add(
            "active"
        );


        knowledgePopup.setAttribute(
            "aria-hidden",
            "false"
        );

        practiceOverlay.setAttribute(
            "aria-hidden",
            "false"
        );


        if (
            lastFocusedElement instanceof HTMLElement
        ) {

            lastFocusedElement.setAttribute(
                "aria-expanded",
                "true"
            );

        }


        document.body.classList.add(
            "popup-open"
        );


        isPopupOpen =
            true;


        knowledgePopup.scrollTop =
            0;


        requestAnimationFrame(
            function () {

                if (
                    popupClose instanceof HTMLElement
                ) {
                    popupClose.focus();
                }

            }
        );


        return true;

    }


    /* =====================================================
       BUILD GAMES FOR EVERY KNOWLEDGE TOPIC
       ===================================================== */

    function ensureKnowledgeGames(knowledge) {
        // Each knowledge topic owns three separate HTML game pages.
        // The pages are cloned from the existing legacy game templates so their
        // original visual/gameplay interfaces remain the baseline.
        const gameMap = {
            "REMAINDER": [{"name":"Chia dư • Bốc số","icon":"🎱","path":"games/knowledge/remainder/1-boc-so.html"},{"name":"Chia dư • Săn số dư","icon":"🔎","path":"games/knowledge/remainder/2-san-so-du.html"},{"name":"Chia dư • Thử thách modulo","icon":"%","path":"games/knowledge/remainder/3-thu-thach-modulo.html"}],
            "DIVISIBILITY": [{"name":"Chia hết • Truy tìm số","icon":"🔎","path":"games/knowledge/divisibility/1-truy-tim-so.html"},{"name":"Chia hết • Chọn số","icon":"🎯","path":"games/knowledge/divisibility/2-chon-so.html"},{"name":"Chia hết • Phá khóa","icon":"🔐","path":"games/knowledge/divisibility/3-pha-khoa.html"}],
            "FUNCTION": [{"name":"Hàm số • Bắt điểm","icon":"🎯","path":"games/knowledge/function/1-bat-iem.html"},{"name":"Hàm số • Tìm giao điểm","icon":"✖️","path":"games/knowledge/function/2-tim-giao-iem.html"},{"name":"Hàm số • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/function/3-o-thi-bi-an.html"}],
            "ham_so_bac_nhat": [{"name":"Hàm số bậc nhất • Bắt điểm","icon":"🎯","path":"games/knowledge/ham-so-bac-nhat/1-bat-iem.html"},{"name":"Hàm số bậc nhất • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ham-so-bac-nhat/2-tim-giao-iem.html"},{"name":"Hàm số bậc nhất • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ham-so-bac-nhat/3-o-thi-bi-an.html"}],
            "he_phuong_trinh": [{"name":"Hệ phương trình [he_phuong_trinh] • Điều tra","icon":"🕵️","path":"games/knowledge/he-phuong-trinh/1-ieu-tra.html"},{"name":"Hệ phương trình [he_phuong_trinh] • Tìm giá trị","icon":"🔢","path":"games/knowledge/he-phuong-trinh/2-tim-gia-tri.html"},{"name":"Hệ phương trình [he_phuong_trinh] • Ghép đáp án","icon":"🧩","path":"games/knowledge/he-phuong-trinh/3-ghep-ap-an.html"}],
            "SYSTEM_EQUATION": [{"name":"Hệ phương trình [SYSTEM_EQUATION] • Điều tra","icon":"🕵️","path":"games/knowledge/system-equation/1-ieu-tra.html"},{"name":"Hệ phương trình [SYSTEM_EQUATION] • Tìm giá trị","icon":"🔢","path":"games/knowledge/system-equation/2-tim-gia-tri.html"},{"name":"Hệ phương trình [SYSTEM_EQUATION] • Ghép đáp án","icon":"🧩","path":"games/knowledge/system-equation/3-ghep-ap-an.html"}],
            "menh_de": [{"name":"Mệnh đề • Bắt điểm","icon":"🎯","path":"games/knowledge/menh-de/1-bat-iem.html"},{"name":"Mệnh đề • Tìm giao điểm","icon":"✖️","path":"games/knowledge/menh-de/2-tim-giao-iem.html"},{"name":"Mệnh đề • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/menh-de/3-o-thi-bi-an.html"}],
            "STATISTICS": [{"name":"Thống kê • Đọc biểu đồ","icon":"📊","path":"games/knowledge/statistics/1-oc-bieu-o.html"},{"name":"Thống kê • Săn số liệu","icon":"🔎","path":"games/knowledge/statistics/2-san-so-lieu.html"},{"name":"Thống kê • Thử thách thống kê","icon":"🏆","path":"games/knowledge/statistics/3-thu-thach-thong-ke.html"}],
            "tap_hop": [{"name":"Tập hợp và các phép toán • Bắt điểm","icon":"🎯","path":"games/knowledge/tap-hop/1-bat-iem.html"},{"name":"Tập hợp và các phép toán • Tìm giao điểm","icon":"✖️","path":"games/knowledge/tap-hop/2-tim-giao-iem.html"},{"name":"Tập hợp và các phép toán • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/tap-hop/3-o-thi-bi-an.html"}],
            "vector": [{"name":"Vectơ • Bắt điểm","icon":"🎯","path":"games/knowledge/vector/1-bat-iem.html"},{"name":"Vectơ • Tìm giao điểm","icon":"✖️","path":"games/knowledge/vector/2-tim-giao-iem.html"},{"name":"Vectơ • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/vector/3-o-thi-bi-an.html"}],
            "PROBABILITY": [{"name":"Xác suất [PROBABILITY] • Bốc bi","icon":"🔮","path":"games/knowledge/probability/1-boc-bi.html"},{"name":"Xác suất [PROBABILITY] • Xúc xắc","icon":"🎲","path":"games/knowledge/probability/2-xuc-xac.html"},{"name":"Xác suất [PROBABILITY] • Chọn tình huống","icon":"🎯","path":"games/knowledge/probability/3-chon-tinh-huong.html"}],
            "RADICAL": [{"name":"Căn thức • Săn căn","icon":"√","path":"games/knowledge/radical/1-san-can.html"},{"name":"Căn thức • Rút gọn nhanh","icon":"⚡","path":"games/knowledge/radical/2-rut-gon-nhanh.html"},{"name":"Căn thức • Mở khóa căn thức","icon":"🔓","path":"games/knowledge/radical/3-mo-khoa-can-thuc.html"}],
            "SEQUENCE": [{"name":"Dãy số [SEQUENCE] • Tìm quy luật","icon":"🔍","path":"games/knowledge/sequence/1-tim-quy-luat.html"},{"name":"Dãy số [SEQUENCE] • Điền số","icon":"🔢","path":"games/knowledge/sequence/2-ien-so.html"},{"name":"Dãy số [SEQUENCE] • Đường đua dãy số","icon":"🏁","path":"games/knowledge/sequence/3-uong-ua-day-so.html"}],
            "GEOMETRY": [{"name":"Hình học • Tìm góc","icon":"📐","path":"games/knowledge/geometry/1-tim-goc.html"},{"name":"Hình học • Săn độ dài","icon":"📏","path":"games/knowledge/geometry/2-san-o-dai.html"},{"name":"Hình học • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/geometry/3-ban-o-hinh-hoc.html"}],
            "menh_de_tap_hop": [{"name":"Mệnh đề và tập hợp • Bắt điểm","icon":"🎯","path":"games/knowledge/menh-de-tap-hop/1-bat-iem.html"},{"name":"Mệnh đề và tập hợp • Tìm giao điểm","icon":"✖️","path":"games/knowledge/menh-de-tap-hop/2-tim-giao-iem.html"},{"name":"Mệnh đề và tập hợp • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/menh-de-tap-hop/3-o-thi-bi-an.html"}],
            "phuong_trinh": [{"name":"Phương trình • Bắt điểm","icon":"🎯","path":"games/knowledge/phuong-trinh/1-bat-iem.html"},{"name":"Phương trình • Tìm giao điểm","icon":"✖️","path":"games/knowledge/phuong-trinh/2-tim-giao-iem.html"},{"name":"Phương trình • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/phuong-trinh/3-o-thi-bi-an.html"}],
            "QUADRATIC_EQUATION": [{"name":"Phương trình bậc hai • Săn nghiệm","icon":"🎯","path":"games/knowledge/quadratic-equation/1-san-nghiem.html"},{"name":"Phương trình bậc hai • Ghép nghiệm","icon":"🧩","path":"games/knowledge/quadratic-equation/2-ghep-nghiem.html"},{"name":"Phương trình bậc hai • Mở khóa","icon":"🔓","path":"games/knowledge/quadratic-equation/3-mo-khoa.html"}],
            "toa_do_phang": [{"name":"Tọa độ trong mặt phẳng • Tìm góc","icon":"📐","path":"games/knowledge/toa-do-phang/1-tim-goc.html"},{"name":"Tọa độ trong mặt phẳng • Săn độ dài","icon":"📏","path":"games/knowledge/toa-do-phang/2-san-o-dai.html"},{"name":"Tọa độ trong mặt phẳng • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/toa-do-phang/3-ban-o-hinh-hoc.html"}],
            "COMBINATION": [{"name":"Tổ hợp • Chọn đội","icon":"👥","path":"games/knowledge/combination/1-chon-oi.html"},{"name":"Tổ hợp • Ghép lựa chọn","icon":"🧩","path":"games/knowledge/combination/2-ghep-lua-chon.html"},{"name":"Tổ hợp • Săn tổ hợp","icon":"🔎","path":"games/knowledge/combination/3-san-to-hop.html"}],
            "duong_thang": [{"name":"Đường thẳng • Bắt điểm","icon":"🎯","path":"games/knowledge/duong-thang/1-bat-iem.html"},{"name":"Đường thẳng • Tìm giao điểm","icon":"✖️","path":"games/knowledge/duong-thang/2-tim-giao-iem.html"},{"name":"Đường thẳng • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/duong-thang/3-o-thi-bi-an.html"}],
            "duong_tron": [{"name":"Đường tròn • Góc nội tiếp bí ẩn","icon":"📐","path":"games/knowledge/duong-tron/1-goc-noi-tiep-bi-an.html"},{"name":"Đường tròn • Truy tìm bán kính","icon":"📏","path":"games/knowledge/duong-tron/2-truy-tim-ban-kinh.html"},{"name":"Đường tròn • Tiếp tuyến thử thách","icon":"🗺️","path":"games/knowledge/duong-tron/3-tiep-tuyen-thu-thach.html"}],
            "bai_toan_thuc_te_10": [{"name":"Bài toán thực tế Toán 10 • Bắt điểm","icon":"🎯","path":"games/knowledge/bai-toan-thuc-te-10/1-bat-iem.html"},{"name":"Bài toán thực tế Toán 10 • Tìm giao điểm","icon":"✖️","path":"games/knowledge/bai-toan-thuc-te-10/2-tim-giao-iem.html"},{"name":"Bài toán thực tế Toán 10 • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/bai-toan-thuc-te-10/3-o-thi-bi-an.html"}],
            "INEQUALITY": [{"name":"Bất phương trình • Vùng an toàn","icon":"🛡️","path":"games/knowledge/inequality/1-vung-an-toan.html"},{"name":"Bất phương trình • Chọn khoảng","icon":"📏","path":"games/knowledge/inequality/2-chon-khoang.html"},{"name":"Bất phương trình • Vượt rào","icon":"🚧","path":"games/knowledge/inequality/3-vuot-rao.html"}],
            "PERMUTATION": [{"name":"Chỉnh hợp • Xếp vị trí","icon":"📍","path":"games/knowledge/permutation/1-xep-vi-tri.html"},{"name":"Chỉnh hợp • Mật mã","icon":"🔐","path":"games/knowledge/permutation/2-mat-ma.html"},{"name":"Chỉnh hợp • Sắp thứ tự","icon":"📋","path":"games/knowledge/permutation/3-sap-thu-tu.html"}],
            "ham_so_bac_hai": [{"name":"Hàm số bậc hai và parabol • Bắt điểm","icon":"🎯","path":"games/knowledge/ham-so-bac-hai/1-bat-iem.html"},{"name":"Hàm số bậc hai và parabol • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ham-so-bac-hai/2-tim-giao-iem.html"},{"name":"Hàm số bậc hai và parabol • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ham-so-bac-hai/3-o-thi-bi-an.html"}],
            "IDENTITIES": [{"name":"Hằng đẳng thức • Ghép công thức","icon":"🧩","path":"games/knowledge/identities/1-ghep-cong-thuc.html"},{"name":"Hằng đẳng thức • Phá biểu thức","icon":"💥","path":"games/knowledge/identities/2-pha-bieu-thuc.html"},{"name":"Hằng đẳng thức • Công thức bí ẩn","icon":"❓","path":"games/knowledge/identities/3-cong-thuc-bi-an.html"}],
            "he_bat_phuong_trinh": [{"name":"Hệ bất phương trình • Vùng an toàn","icon":"🛡️","path":"games/knowledge/he-bat-phuong-trinh/1-vung-an-toan.html"},{"name":"Hệ bất phương trình • Chọn khoảng","icon":"📏","path":"games/knowledge/he-bat-phuong-trinh/2-chon-khoang.html"},{"name":"Hệ bất phương trình • Vượt rào","icon":"🚧","path":"games/knowledge/he-bat-phuong-trinh/3-vuot-rao.html"}],
            "he_thuc_luong": [{"name":"Hệ thức lượng trong tam giác [he_thuc_luong] • Giải mã góc","icon":"📐","path":"games/knowledge/he-thuc-luong/1-giai-ma-goc.html"},{"name":"Hệ thức lượng trong tam giác [he_thuc_luong] • Săn cạnh tam giác","icon":"📏","path":"games/knowledge/he-thuc-luong/2-san-canh-tam-giac.html"},{"name":"Hệ thức lượng trong tam giác [he_thuc_luong] • Ứng dụng tam giác","icon":"🗺️","path":"games/knowledge/he-thuc-luong/3-ung-dung-tam-giac.html"}],
            "he_thuc_luong_tam_giac": [{"name":"Hệ thức lượng trong tam giác [he_thuc_luong_tam_giac] • Giải mã góc","icon":"📐","path":"games/knowledge/he-thuc-luong-tam-giac/1-giai-ma-goc.html"},{"name":"Hệ thức lượng trong tam giác [he_thuc_luong_tam_giac] • Săn cạnh tam giác","icon":"📏","path":"games/knowledge/he-thuc-luong-tam-giac/2-san-canh-tam-giac.html"},{"name":"Hệ thức lượng trong tam giác [he_thuc_luong_tam_giac] • Ứng dụng tam giác","icon":"🗺️","path":"games/knowledge/he-thuc-luong-tam-giac/3-ung-dung-tam-giac.html"}],
            "nhi_thuc_newton": [{"name":"Nhị thức Newton • Chọn đội","icon":"👥","path":"games/knowledge/nhi-thuc-newton/1-chon-oi.html"},{"name":"Nhị thức Newton • Ghép lựa chọn","icon":"🧩","path":"games/knowledge/nhi-thuc-newton/2-ghep-lua-chon.html"},{"name":"Nhị thức Newton • Săn tổ hợp","icon":"🔎","path":"games/knowledge/nhi-thuc-newton/3-san-to-hop.html"}],
            "ALGEBRAIC_FRACTION": [{"name":"Phân thức đại số • Rút gọn","icon":"➗","path":"games/knowledge/algebraic-fraction/1-rut-gon.html"},{"name":"Phân thức đại số • Tìm điều kiện","icon":"🔎","path":"games/knowledge/algebraic-fraction/2-tim-ieu-kien.html"},{"name":"Phân thức đại số • Phân thức tốc độ","icon":"⚡","path":"games/knowledge/algebraic-fraction/3-phan-thuc-toc-o.html"}],
            "quy_tac_dem": [{"name":"Quy tắc đếm • Chọn đội","icon":"👥","path":"games/knowledge/quy-tac-dem/1-chon-oi.html"},{"name":"Quy tắc đếm • Ghép lựa chọn","icon":"🧩","path":"games/knowledge/quy-tac-dem/2-ghep-lua-chon.html"},{"name":"Quy tắc đếm • Săn tổ hợp","icon":"🔎","path":"games/knowledge/quy-tac-dem/3-san-to-hop.html"}],
            "cong_thuc_luong_giac": [{"name":"Công thức lượng giác • Bắt điểm","icon":"🎯","path":"games/knowledge/cong-thuc-luong-giac/1-bat-iem.html"},{"name":"Công thức lượng giác • Tìm giao điểm","icon":"✖️","path":"games/knowledge/cong-thuc-luong-giac/2-tim-giao-iem.html"},{"name":"Công thức lượng giác • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/cong-thuc-luong-giac/3-o-thi-bi-an.html"}],
            "cap_so_cong": [{"name":"Cấp số cộng • Tìm quy luật","icon":"🔍","path":"games/knowledge/cap-so-cong/1-tim-quy-luat.html"},{"name":"Cấp số cộng • Điền số","icon":"🔢","path":"games/knowledge/cap-so-cong/2-ien-so.html"},{"name":"Cấp số cộng • Đường đua dãy số","icon":"🏁","path":"games/knowledge/cap-so-cong/3-uong-ua-day-so.html"}],
            "cap_so_nhan": [{"name":"Cấp số nhân • Tìm quy luật","icon":"🔍","path":"games/knowledge/cap-so-nhan/1-tim-quy-luat.html"},{"name":"Cấp số nhân • Điền số","icon":"🔢","path":"games/knowledge/cap-so-nhan/2-ien-so.html"},{"name":"Cấp số nhân • Đường đua dãy số","icon":"🏁","path":"games/knowledge/cap-so-nhan/3-uong-ua-day-so.html"}],
            "day_so": [{"name":"Dãy số [day_so] • Tìm quy luật","icon":"🔍","path":"games/knowledge/day-so/1-tim-quy-luat.html"},{"name":"Dãy số [day_so] • Điền số","icon":"🔢","path":"games/knowledge/day-so/2-ien-so.html"},{"name":"Dãy số [day_so] • Đường đua dãy số","icon":"🏁","path":"games/knowledge/day-so/3-uong-ua-day-so.html"}],
            "gia_tri_luong_giac": [{"name":"Giá trị lượng giác • Bắt điểm","icon":"🎯","path":"games/knowledge/gia-tri-luong-giac/1-bat-iem.html"},{"name":"Giá trị lượng giác • Tìm giao điểm","icon":"✖️","path":"games/knowledge/gia-tri-luong-giac/2-tim-giao-iem.html"},{"name":"Giá trị lượng giác • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/gia-tri-luong-giac/3-o-thi-bi-an.html"}],
            "gioi_han": [{"name":"Giới hạn • Bắt điểm","icon":"🎯","path":"games/knowledge/gioi-han/1-bat-iem.html"},{"name":"Giới hạn • Tìm giao điểm","icon":"✖️","path":"games/knowledge/gioi-han/2-tim-giao-iem.html"},{"name":"Giới hạn • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/gioi-han/3-o-thi-bi-an.html"}],
            "ham_so_luong_giac": [{"name":"Hàm số lượng giác [ham_so_luong_giac] • Bắt điểm","icon":"🎯","path":"games/knowledge/ham-so-luong-giac/1-bat-iem.html"},{"name":"Hàm số lượng giác [ham_so_luong_giac] • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ham-so-luong-giac/2-tim-giao-iem.html"},{"name":"Hàm số lượng giác [ham_so_luong_giac] • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ham-so-luong-giac/3-o-thi-bi-an.html"}],
            "thong_ke_11": [{"name":"Thống kê Toán 11 • Đọc biểu đồ","icon":"📊","path":"games/knowledge/thong-ke-11/1-oc-bieu-o.html"},{"name":"Thống kê Toán 11 • Săn số liệu","icon":"🔎","path":"games/knowledge/thong-ke-11/2-san-so-lieu.html"},{"name":"Thống kê Toán 11 • Thử thách thống kê","icon":"🏆","path":"games/knowledge/thong-ke-11/3-thu-thach-thong-ke.html"}],
            "xac_suat_11": [{"name":"Xác suất [xac_suat_11] • Bốc bi","icon":"🔮","path":"games/knowledge/xac-suat-11/1-boc-bi.html"},{"name":"Xác suất [xac_suat_11] • Xúc xắc","icon":"🎲","path":"games/knowledge/xac-suat-11/2-xuc-xac.html"},{"name":"Xác suất [xac_suat_11] • Chọn tình huống","icon":"🎯","path":"games/knowledge/xac-suat-11/3-chon-tinh-huong.html"}],
            "dao_ham": [{"name":"Đạo hàm • Bắt điểm","icon":"🎯","path":"games/knowledge/dao-ham/1-bat-iem.html"},{"name":"Đạo hàm • Tìm giao điểm","icon":"✖️","path":"games/knowledge/dao-ham/2-tim-giao-iem.html"},{"name":"Đạo hàm • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/dao-ham/3-o-thi-bi-an.html"}],
            "bai_toan_thuc_te_11": [{"name":"Bài toán thực tế Toán 11 • Bắt điểm","icon":"🎯","path":"games/knowledge/bai-toan-thuc-te-11/1-bat-iem.html"},{"name":"Bài toán thực tế Toán 11 • Tìm giao điểm","icon":"✖️","path":"games/knowledge/bai-toan-thuc-te-11/2-tim-giao-iem.html"},{"name":"Bài toán thực tế Toán 11 • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/bai-toan-thuc-te-11/3-o-thi-bi-an.html"}],
            "day_so_tong_quat": [{"name":"Dãy số [day_so_tong_quat] • Tìm quy luật","icon":"🔍","path":"games/knowledge/day-so-tong-quat/1-tim-quy-luat.html"},{"name":"Dãy số [day_so_tong_quat] • Điền số","icon":"🔢","path":"games/knowledge/day-so-tong-quat/2-ien-so.html"},{"name":"Dãy số [day_so_tong_quat] • Đường đua dãy số","icon":"🏁","path":"games/knowledge/day-so-tong-quat/3-uong-ua-day-so.html"}],
            "gioi_han_ham_so": [{"name":"Giới hạn hàm số • Bắt điểm","icon":"🎯","path":"games/knowledge/gioi-han-ham-so/1-bat-iem.html"},{"name":"Giới hạn hàm số • Tìm giao điểm","icon":"✖️","path":"games/knowledge/gioi-han-ham-so/2-tim-giao-iem.html"},{"name":"Giới hạn hàm số • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/gioi-han-ham-so/3-o-thi-bi-an.html"}],
            "goc_khoang_cach_11": [{"name":"Góc và khoảng cách trong không gian • Tìm góc","icon":"📐","path":"games/knowledge/goc-khoang-cach-11/1-tim-goc.html"},{"name":"Góc và khoảng cách trong không gian • Săn độ dài","icon":"📏","path":"games/knowledge/goc-khoang-cach-11/2-san-o-dai.html"},{"name":"Góc và khoảng cách trong không gian • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/goc-khoang-cach-11/3-ban-o-hinh-hoc.html"}],
            "ham_so_lien_tuc": [{"name":"Hàm số liên tục • Bắt điểm","icon":"🎯","path":"games/knowledge/ham-so-lien-tuc/1-bat-iem.html"},{"name":"Hàm số liên tục • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ham-so-lien-tuc/2-tim-giao-iem.html"},{"name":"Hàm số liên tục • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ham-so-lien-tuc/3-o-thi-bi-an.html"}],
            "phuong_trinh_luong_giac": [{"name":"Phương trình lượng giác [phuong_trinh_luong_giac] • Bắt điểm","icon":"🎯","path":"games/knowledge/phuong-trinh-luong-giac/1-bat-iem.html"},{"name":"Phương trình lượng giác [phuong_trinh_luong_giac] • Tìm giao điểm","icon":"✖️","path":"games/knowledge/phuong-trinh-luong-giac/2-tim-giao-iem.html"},{"name":"Phương trình lượng giác [phuong_trinh_luong_giac] • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/phuong-trinh-luong-giac/3-o-thi-bi-an.html"}],
            "song_song_khong_gian": [{"name":"Quan hệ song song trong không gian • Tìm góc","icon":"📐","path":"games/knowledge/song-song-khong-gian/1-tim-goc.html"},{"name":"Quan hệ song song trong không gian • Săn độ dài","icon":"📏","path":"games/knowledge/song-song-khong-gian/2-san-o-dai.html"},{"name":"Quan hệ song song trong không gian • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/song-song-khong-gian/3-ban-o-hinh-hoc.html"}],
            "vuong_goc_khong_gian": [{"name":"Quan hệ vuông góc trong không gian • Tìm góc","icon":"📐","path":"games/knowledge/vuong-goc-khong-gian/1-tim-goc.html"},{"name":"Quan hệ vuông góc trong không gian • Săn độ dài","icon":"📏","path":"games/knowledge/vuong-goc-khong-gian/2-san-o-dai.html"},{"name":"Quan hệ vuông góc trong không gian • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/vuong-goc-khong-gian/3-ban-o-hinh-hoc.html"}],
            "dao_ham_quy_tac": [{"name":"Quy tắc đạo hàm • Bắt điểm","icon":"🎯","path":"games/knowledge/dao-ham-quy-tac/1-bat-iem.html"},{"name":"Quy tắc đạo hàm • Tìm giao điểm","icon":"✖️","path":"games/knowledge/dao-ham-quy-tac/2-tim-giao-iem.html"},{"name":"Quy tắc đạo hàm • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/dao-ham-quy-tac/3-o-thi-bi-an.html"}],
            "ung_dung_dao_ham_11": [{"name":"Ứng dụng đạo hàm [ung_dung_dao_ham_11] • Bắt điểm","icon":"🎯","path":"games/knowledge/ung-dung-dao-ham-11/1-bat-iem.html"},{"name":"Ứng dụng đạo hàm [ung_dung_dao_ham_11] • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ung-dung-dao-ham-11/2-tim-giao-iem.html"},{"name":"Ứng dụng đạo hàm [ung_dung_dao_ham_11] • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ung-dung-dao-ham-11/3-o-thi-bi-an.html"}],
            "bien_co_doc_lap_11": [{"name":"Biến cố độc lập và xác suất có điều kiện • Bốc bi","icon":"🔮","path":"games/knowledge/bien-co-doc-lap-11/1-boc-bi.html"},{"name":"Biến cố độc lập và xác suất có điều kiện • Xúc xắc","icon":"🎲","path":"games/knowledge/bien-co-doc-lap-11/2-xuc-xac.html"},{"name":"Biến cố độc lập và xác suất có điều kiện • Chọn tình huống","icon":"🎯","path":"games/knowledge/bien-co-doc-lap-11/3-chon-tinh-huong.html"}],
            "bai_toan_thuc_te_tong_hop_11": [{"name":"Bài toán thực tế tổng hợp Toán 11 • Bắt điểm","icon":"🎯","path":"games/knowledge/bai-toan-thuc-te-tong-hop-11/1-bat-iem.html"},{"name":"Bài toán thực tế tổng hợp Toán 11 • Tìm giao điểm","icon":"✖️","path":"games/knowledge/bai-toan-thuc-te-tong-hop-11/2-tim-giao-iem.html"},{"name":"Bài toán thực tế tổng hợp Toán 11 • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/bai-toan-thuc-te-tong-hop-11/3-o-thi-bi-an.html"}],
            "day_so_truy_hoi_11": [{"name":"Dãy số truy hồi • Tìm quy luật","icon":"🔍","path":"games/knowledge/day-so-truy-hoi-11/1-tim-quy-luat.html"},{"name":"Dãy số truy hồi • Điền số","icon":"🔢","path":"games/knowledge/day-so-truy-hoi-11/2-ien-so.html"},{"name":"Dãy số truy hồi • Đường đua dãy số","icon":"🏁","path":"games/knowledge/day-so-truy-hoi-11/3-uong-ua-day-so.html"}],
            "ham_so_luong_giac_day_du": [{"name":"Hàm số lượng giác [ham_so_luong_giac_day_du] • Bắt điểm","icon":"🎯","path":"games/knowledge/ham-so-luong-giac-day-du/1-bat-iem.html"},{"name":"Hàm số lượng giác [ham_so_luong_giac_day_du] • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ham-so-luong-giac-day-du/2-tim-giao-iem.html"},{"name":"Hàm số lượng giác [ham_so_luong_giac_day_du] • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ham-so-luong-giac-day-du/3-o-thi-bi-an.html"}],
            "phep_bien_hinh_11": [{"name":"Phép biến hình trong mặt phẳng • Tìm góc","icon":"📐","path":"games/knowledge/phep-bien-hinh-11/1-tim-goc.html"},{"name":"Phép biến hình trong mặt phẳng • Săn độ dài","icon":"📏","path":"games/knowledge/phep-bien-hinh-11/2-san-o-dai.html"},{"name":"Phép biến hình trong mặt phẳng • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/phep-bien-hinh-11/3-ban-o-hinh-hoc.html"}],
            "phuong_trinh_luong_giac_day_du": [{"name":"Phương trình lượng giác [phuong_trinh_luong_giac_day_du] • Bắt điểm","icon":"🎯","path":"games/knowledge/phuong-trinh-luong-giac-day-du/1-bat-iem.html"},{"name":"Phương trình lượng giác [phuong_trinh_luong_giac_day_du] • Tìm giao điểm","icon":"✖️","path":"games/knowledge/phuong-trinh-luong-giac-day-du/2-tim-giao-iem.html"},{"name":"Phương trình lượng giác [phuong_trinh_luong_giac_day_du] • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/phuong-trinh-luong-giac-day-du/3-o-thi-bi-an.html"}],
            "hinh_khong_gian": [{"name":"Quan hệ song song và vuông góc trong không gian • Tìm góc","icon":"📐","path":"games/knowledge/hinh-khong-gian/1-tim-goc.html"},{"name":"Quan hệ song song và vuông góc trong không gian • Săn độ dài","icon":"📏","path":"games/knowledge/hinh-khong-gian/2-san-o-dai.html"},{"name":"Quan hệ song song và vuông góc trong không gian • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/hinh-khong-gian/3-ban-o-hinh-hoc.html"}],
            "quy_nap_toan_hoc_11": [{"name":"Quy nạp toán học • Tìm quy luật","icon":"🔍","path":"games/knowledge/quy-nap-toan-hoc-11/1-tim-quy-luat.html"},{"name":"Quy nạp toán học • Điền số","icon":"🔢","path":"games/knowledge/quy-nap-toan-hoc-11/2-ien-so.html"},{"name":"Quy nạp toán học • Đường đua dãy số","icon":"🏁","path":"games/knowledge/quy-nap-toan-hoc-11/3-uong-ua-day-so.html"}],
            "thiet_dien_hinh_khong_gian_11": [{"name":"Thiết diện hình không gian • Tìm góc","icon":"📐","path":"games/knowledge/thiet-dien-hinh-khong-gian-11/1-tim-goc.html"},{"name":"Thiết diện hình không gian • Săn độ dài","icon":"📏","path":"games/knowledge/thiet-dien-hinh-khong-gian-11/2-san-o-dai.html"},{"name":"Thiết diện hình không gian • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/thiet-dien-hinh-khong-gian-11/3-ban-o-hinh-hoc.html"}],
            "to_hop_xac_suat_nang_cao_11": [{"name":"Tổ hợp và xác suất nâng cao • Bốc bi","icon":"🔮","path":"games/knowledge/to-hop-xac-suat-nang-cao-11/1-boc-bi.html"},{"name":"Tổ hợp và xác suất nâng cao • Xúc xắc","icon":"🎲","path":"games/knowledge/to-hop-xac-suat-nang-cao-11/2-xuc-xac.html"},{"name":"Tổ hợp và xác suất nâng cao • Chọn tình huống","icon":"🎯","path":"games/knowledge/to-hop-xac-suat-nang-cao-11/3-chon-tinh-huong.html"}],
            "thong_ke_12": [{"name":"Các số đặc trưng đo xu thế và độ phân tán • Đọc biểu đồ","icon":"📊","path":"games/knowledge/thong-ke-12/1-oc-bieu-o.html"},{"name":"Các số đặc trưng đo xu thế và độ phân tán • Săn số liệu","icon":"🔎","path":"games/knowledge/thong-ke-12/2-san-so-lieu.html"},{"name":"Các số đặc trưng đo xu thế và độ phân tán • Thử thách thống kê","icon":"🏆","path":"games/knowledge/thong-ke-12/3-thu-thach-thong-ke.html"}],
            "cuc_tri": [{"name":"Cực trị • Bắt điểm","icon":"🎯","path":"games/knowledge/cuc-tri/1-bat-iem.html"},{"name":"Cực trị • Tìm giao điểm","icon":"✖️","path":"games/knowledge/cuc-tri/2-tim-giao-iem.html"},{"name":"Cực trị • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/cuc-tri/3-o-thi-bi-an.html"}],
            "gtln_gtnn": [{"name":"Giá trị lớn nhất và nhỏ nhất • Bắt điểm","icon":"🎯","path":"games/knowledge/gtln-gtnn/1-bat-iem.html"},{"name":"Giá trị lớn nhất và nhỏ nhất • Tìm giao điểm","icon":"✖️","path":"games/knowledge/gtln-gtnn/2-tim-giao-iem.html"},{"name":"Giá trị lớn nhất và nhỏ nhất • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/gtln-gtnn/3-o-thi-bi-an.html"}],
            "ham_logarit": [{"name":"Hàm số logarit • Bắt điểm","icon":"🎯","path":"games/knowledge/ham-logarit/1-bat-iem.html"},{"name":"Hàm số logarit • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ham-logarit/2-tim-giao-iem.html"},{"name":"Hàm số logarit • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ham-logarit/3-o-thi-bi-an.html"}],
            "ham_mu": [{"name":"Hàm số mũ • Bắt điểm","icon":"🎯","path":"games/knowledge/ham-mu/1-bat-iem.html"},{"name":"Hàm số mũ • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ham-mu/2-tim-giao-iem.html"},{"name":"Hàm số mũ • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ham-mu/3-o-thi-bi-an.html"}],
            "hinh_hoc_khong_gian": [{"name":"Hình học không gian • Tìm góc","icon":"📐","path":"games/knowledge/hinh-hoc-khong-gian/1-tim-goc.html"},{"name":"Hình học không gian • Săn độ dài","icon":"📏","path":"games/knowledge/hinh-hoc-khong-gian/2-san-o-dai.html"},{"name":"Hình học không gian • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/hinh-hoc-khong-gian/3-ban-o-hinh-hoc.html"}],
            "so_phuc": [{"name":"Số phức • Bắt điểm","icon":"🎯","path":"games/knowledge/so-phuc/1-bat-iem.html"},{"name":"Số phức • Tìm giao điểm","icon":"✖️","path":"games/knowledge/so-phuc/2-tim-giao-iem.html"},{"name":"Số phức • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/so-phuc/3-o-thi-bi-an.html"}],
            "tinh_don_dieu": [{"name":"Tính đơn điệu • Bắt điểm","icon":"🎯","path":"games/knowledge/tinh-don-dieu/1-bat-iem.html"},{"name":"Tính đơn điệu • Tìm giao điểm","icon":"✖️","path":"games/knowledge/tinh-don-dieu/2-tim-giao-iem.html"},{"name":"Tính đơn điệu • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/tinh-don-dieu/3-o-thi-bi-an.html"}],
            "toa_do_khong_gian": [{"name":"Tọa độ trong không gian • Tìm góc","icon":"📐","path":"games/knowledge/toa-do-khong-gian/1-tim-goc.html"},{"name":"Tọa độ trong không gian • Săn độ dài","icon":"📏","path":"games/knowledge/toa-do-khong-gian/2-san-o-dai.html"},{"name":"Tọa độ trong không gian • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/toa-do-khong-gian/3-ban-o-hinh-hoc.html"}],
            "xac_suat_12": [{"name":"Xác suất và biến ngẫu nhiên • Bốc bi","icon":"🔮","path":"games/knowledge/xac-suat-12/1-boc-bi.html"},{"name":"Xác suất và biến ngẫu nhiên • Xúc xắc","icon":"🎲","path":"games/knowledge/xac-suat-12/2-xuc-xac.html"},{"name":"Xác suất và biến ngẫu nhiên • Chọn tình huống","icon":"🎯","path":"games/knowledge/xac-suat-12/3-chon-tinh-huong.html"}],
            "bieu_dien_so_phuc": [{"name":"Biểu diễn số phức • Bắt điểm","icon":"🎯","path":"games/knowledge/bieu-dien-so-phuc/1-bat-iem.html"},{"name":"Biểu diễn số phức • Tìm giao điểm","icon":"✖️","path":"games/knowledge/bieu-dien-so-phuc/2-tim-giao-iem.html"},{"name":"Biểu diễn số phức • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/bieu-dien-so-phuc/3-o-thi-bi-an.html"}],
            "khao_sat_ham_so": [{"name":"Khảo sát và vẽ đồ thị hàm số • Bắt điểm","icon":"🎯","path":"games/knowledge/khao-sat-ham-so/1-bat-iem.html"},{"name":"Khảo sát và vẽ đồ thị hàm số • Tìm giao điểm","icon":"✖️","path":"games/knowledge/khao-sat-ham-so/2-tim-giao-iem.html"},{"name":"Khảo sát và vẽ đồ thị hàm số • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/khao-sat-ham-so/3-o-thi-bi-an.html"}],
            "mat_phang_oxyz": [{"name":"Mặt phẳng trong Oxyz • Tìm góc","icon":"📐","path":"games/knowledge/mat-phang-oxyz/1-tim-goc.html"},{"name":"Mặt phẳng trong Oxyz • Săn độ dài","icon":"📏","path":"games/knowledge/mat-phang-oxyz/2-san-o-dai.html"},{"name":"Mặt phẳng trong Oxyz • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/mat-phang-oxyz/3-ban-o-hinh-hoc.html"}],
            "nguyen_ham_tich_phan": [{"name":"Nguyên hàm và tích phân • Bắt điểm","icon":"🎯","path":"games/knowledge/nguyen-ham-tich-phan/1-bat-iem.html"},{"name":"Nguyên hàm và tích phân • Tìm giao điểm","icon":"✖️","path":"games/knowledge/nguyen-ham-tich-phan/2-tim-giao-iem.html"},{"name":"Nguyên hàm và tích phân • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/nguyen-ham-tich-phan/3-o-thi-bi-an.html"}],
            "pt_logarit": [{"name":"Phương trình logarit • Bắt điểm","icon":"🎯","path":"games/knowledge/pt-logarit/1-bat-iem.html"},{"name":"Phương trình logarit • Tìm giao điểm","icon":"✖️","path":"games/knowledge/pt-logarit/2-tim-giao-iem.html"},{"name":"Phương trình logarit • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/pt-logarit/3-o-thi-bi-an.html"}],
            "pt_mu": [{"name":"Phương trình mũ • Bắt điểm","icon":"🎯","path":"games/knowledge/pt-mu/1-bat-iem.html"},{"name":"Phương trình mũ • Tìm giao điểm","icon":"✖️","path":"games/knowledge/pt-mu/2-tim-giao-iem.html"},{"name":"Phương trình mũ • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/pt-mu/3-o-thi-bi-an.html"}],
            "tiep_tuyen": [{"name":"Tiếp tuyến • Bắt điểm","icon":"🎯","path":"games/knowledge/tiep-tuyen/1-bat-iem.html"},{"name":"Tiếp tuyến • Tìm giao điểm","icon":"✖️","path":"games/knowledge/tiep-tuyen/2-tim-giao-iem.html"},{"name":"Tiếp tuyến • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/tiep-tuyen/3-o-thi-bi-an.html"}],
            "tien_can": [{"name":"Tiệm cận • Bắt điểm","icon":"🎯","path":"games/knowledge/tien-can/1-bat-iem.html"},{"name":"Tiệm cận • Tìm giao điểm","icon":"✖️","path":"games/knowledge/tien-can/2-tim-giao-iem.html"},{"name":"Tiệm cận • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/tien-can/3-o-thi-bi-an.html"}],
            "duong_thang_oxyz": [{"name":"Đường thẳng trong Oxyz • Bắt điểm","icon":"🎯","path":"games/knowledge/duong-thang-oxyz/1-bat-iem.html"},{"name":"Đường thẳng trong Oxyz • Tìm giao điểm","icon":"✖️","path":"games/knowledge/duong-thang-oxyz/2-tim-giao-iem.html"},{"name":"Đường thẳng trong Oxyz • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/duong-thang-oxyz/3-o-thi-bi-an.html"}],
            "ung_dung_dao_ham": [{"name":"Ứng dụng đạo hàm [ung_dung_dao_ham] • Bắt điểm","icon":"🎯","path":"games/knowledge/ung-dung-dao-ham/1-bat-iem.html"},{"name":"Ứng dụng đạo hàm [ung_dung_dao_ham] • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ung-dung-dao-ham/2-tim-giao-iem.html"},{"name":"Ứng dụng đạo hàm [ung_dung_dao_ham] • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ung-dung-dao-ham/3-o-thi-bi-an.html"}],
            "bai_toan_thuc_te_12": [{"name":"Bài toán thực tế Toán 12 • Bắt điểm","icon":"🎯","path":"games/knowledge/bai-toan-thuc-te-12/1-bat-iem.html"},{"name":"Bài toán thực tế Toán 12 • Tìm giao điểm","icon":"✖️","path":"games/knowledge/bai-toan-thuc-te-12/2-tim-giao-iem.html"},{"name":"Bài toán thực tế Toán 12 • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/bai-toan-thuc-te-12/3-o-thi-bi-an.html"}],
            "tong_hop_thpt": [{"name":"Bài toán tổng hợp THPT • Bắt điểm","icon":"🎯","path":"games/knowledge/tong-hop-thpt/1-bat-iem.html"},{"name":"Bài toán tổng hợp THPT • Tìm giao điểm","icon":"✖️","path":"games/knowledge/tong-hop-thpt/2-tim-giao-iem.html"},{"name":"Bài toán tổng hợp THPT • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/tong-hop-thpt/3-o-thi-bi-an.html"}],
            "bpt_logarit": [{"name":"Bất phương trình logarit • Bắt điểm","icon":"🎯","path":"games/knowledge/bpt-logarit/1-bat-iem.html"},{"name":"Bất phương trình logarit • Tìm giao điểm","icon":"✖️","path":"games/knowledge/bpt-logarit/2-tim-giao-iem.html"},{"name":"Bất phương trình logarit • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/bpt-logarit/3-o-thi-bi-an.html"}],
            "bpt_mu": [{"name":"Bất phương trình mũ • Bắt điểm","icon":"🎯","path":"games/knowledge/bpt-mu/1-bat-iem.html"},{"name":"Bất phương trình mũ • Tìm giao điểm","icon":"✖️","path":"games/knowledge/bpt-mu/2-tim-giao-iem.html"},{"name":"Bất phương trình mũ • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/bpt-mu/3-o-thi-bi-an.html"}],
            "goc_khoang_cach_oxyz": [{"name":"Góc và khoảng cách Oxyz • Tìm góc","icon":"📐","path":"games/knowledge/goc-khoang-cach-oxyz/1-tim-goc.html"},{"name":"Góc và khoảng cách Oxyz • Săn độ dài","icon":"📏","path":"games/knowledge/goc-khoang-cach-oxyz/2-san-o-dai.html"},{"name":"Góc và khoảng cách Oxyz • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/goc-khoang-cach-oxyz/3-ban-o-hinh-hoc.html"}],
            "mat_cau": [{"name":"Mặt cầu • Tìm góc","icon":"📐","path":"games/knowledge/mat-cau/1-tim-goc.html"},{"name":"Mặt cầu • Săn độ dài","icon":"📏","path":"games/knowledge/mat-cau/2-san-o-dai.html"},{"name":"Mặt cầu • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/mat-cau/3-ban-o-hinh-hoc.html"}],
            "pt_so_phuc": [{"name":"Phương trình số phức • Bắt điểm","icon":"🎯","path":"games/knowledge/pt-so-phuc/1-bat-iem.html"},{"name":"Phương trình số phức • Tìm giao điểm","icon":"✖️","path":"games/knowledge/pt-so-phuc/2-tim-giao-iem.html"},{"name":"Phương trình số phức • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/pt-so-phuc/3-o-thi-bi-an.html"}],
            "the_tich_khong_gian": [{"name":"Thể tích hình học không gian • Tìm góc","icon":"📐","path":"games/knowledge/the-tich-khong-gian/1-tim-goc.html"},{"name":"Thể tích hình học không gian • Săn độ dài","icon":"📏","path":"games/knowledge/the-tich-khong-gian/2-san-o-dai.html"},{"name":"Thể tích hình học không gian • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/the-tich-khong-gian/3-ban-o-hinh-hoc.html"}],
            "tuong_giao": [{"name":"Tương giao đồ thị • Tìm góc","icon":"📐","path":"games/knowledge/tuong-giao/1-tim-goc.html"},{"name":"Tương giao đồ thị • Săn độ dài","icon":"📏","path":"games/knowledge/tuong-giao/2-san-o-dai.html"},{"name":"Tương giao đồ thị • Bản đồ hình học","icon":"🗺️","path":"games/knowledge/tuong-giao/3-ban-o-hinh-hoc.html"}],
            "ung_dung_tich_phan": [{"name":"Ứng dụng tích phân • Bắt điểm","icon":"🎯","path":"games/knowledge/ung-dung-tich-phan/1-bat-iem.html"},{"name":"Ứng dụng tích phân • Tìm giao điểm","icon":"✖️","path":"games/knowledge/ung-dung-tich-phan/2-tim-giao-iem.html"},{"name":"Ứng dụng tích phân • Đồ thị bí ẩn","icon":"📈","path":"games/knowledge/ung-dung-tich-phan/3-o-thi-bi-an.html"}],
            "hinh_hoc_co_ban_10": [{"name":"Hình học cơ bản: góc, cạnh và diện tích • Khám phá","icon":"🔎","path":"games/knowledge/hinh-hoc-co-ban-10/1-kham-pha.html"},{"name":"Hình học cơ bản: góc, cạnh và diện tích • Nhiệm vụ","icon":"🧩","path":"games/knowledge/hinh-hoc-co-ban-10/2-nhiem-vu.html"},{"name":"Hình học cơ bản: góc, cạnh và diện tích • Trùm cuối","icon":"🏆","path":"games/knowledge/hinh-hoc-co-ban-10/3-trum-cuoi.html"}],
            "tam_giac_tu_giac_10": [{"name":"Tam giác và tứ giác cơ bản • Khám phá","icon":"🔎","path":"games/knowledge/tam-giac-tu-giac-10/1-kham-pha.html"},{"name":"Tam giác và tứ giác cơ bản • Nhiệm vụ","icon":"🧩","path":"games/knowledge/tam-giac-tu-giac-10/2-nhiem-vu.html"},{"name":"Tam giác và tứ giác cơ bản • Trùm cuối","icon":"🏆","path":"games/knowledge/tam-giac-tu-giac-10/3-trum-cuoi.html"}],
            "duong_tron_co_ban_10": [{"name":"Đường tròn và các góc cơ bản • Khám phá","icon":"🔎","path":"games/knowledge/duong-tron-co-ban-10/1-kham-pha.html"},{"name":"Đường tròn và các góc cơ bản • Nhiệm vụ","icon":"🧩","path":"games/knowledge/duong-tron-co-ban-10/2-nhiem-vu.html"},{"name":"Đường tròn và các góc cơ bản • Trùm cuối","icon":"🏆","path":"games/knowledge/duong-tron-co-ban-10/3-trum-cuoi.html"}],
            "he_thuc_luong_van_dung_10": [{"name":"Hệ thức lượng trong tam giác [he_thuc_luong_van_dung_10] • Khám phá","icon":"🔎","path":"games/knowledge/he-thuc-luong-van-dung-10/1-kham-pha.html"},{"name":"Hệ thức lượng trong tam giác [he_thuc_luong_van_dung_10] • Nhiệm vụ","icon":"🧩","path":"games/knowledge/he-thuc-luong-van-dung-10/2-nhiem-vu.html"},{"name":"Hệ thức lượng trong tam giác [he_thuc_luong_van_dung_10] • Trùm cuối","icon":"🏆","path":"games/knowledge/he-thuc-luong-van-dung-10/3-trum-cuoi.html"}],
            "toa_do_hinh_hoc_10": [{"name":"Tọa độ và đường thẳng trong mặt phẳng • Khám phá","icon":"🔎","path":"games/knowledge/toa-do-hinh-hoc-10/1-kham-pha.html"},{"name":"Tọa độ và đường thẳng trong mặt phẳng • Nhiệm vụ","icon":"🧩","path":"games/knowledge/toa-do-hinh-hoc-10/2-nhiem-vu.html"},{"name":"Tọa độ và đường thẳng trong mặt phẳng • Trùm cuối","icon":"🏆","path":"games/knowledge/toa-do-hinh-hoc-10/3-trum-cuoi.html"}],
            "chung_minh_hinh_hoc_10": [{"name":"Chứng minh hình học và bài toán tổng hợp • Khám phá","icon":"🔎","path":"games/knowledge/chung-minh-hinh-hoc-10/1-kham-pha.html"},{"name":"Chứng minh hình học và bài toán tổng hợp • Nhiệm vụ","icon":"🧩","path":"games/knowledge/chung-minh-hinh-hoc-10/2-nhiem-vu.html"},{"name":"Chứng minh hình học và bài toán tổng hợp • Trùm cuối","icon":"🏆","path":"games/knowledge/chung-minh-hinh-hoc-10/3-trum-cuoi.html"}],
            "phep_bien_hinh_co_ban_11": [{"name":"Phép biến hình cơ bản • Khám phá","icon":"🔎","path":"games/knowledge/phep-bien-hinh-co-ban-11/1-kham-pha.html"},{"name":"Phép biến hình cơ bản • Nhiệm vụ","icon":"🧩","path":"games/knowledge/phep-bien-hinh-co-ban-11/2-nhiem-vu.html"},{"name":"Phép biến hình cơ bản • Trùm cuối","icon":"🏆","path":"games/knowledge/phep-bien-hinh-co-ban-11/3-trum-cuoi.html"}],
            "nhan_biet_hinh_khong_gian_11": [{"name":"Nhận biết hình học không gian • Khám phá","icon":"🔎","path":"games/knowledge/nhan-biet-hinh-khong-gian-11/1-kham-pha.html"},{"name":"Nhận biết hình học không gian • Nhiệm vụ","icon":"🧩","path":"games/knowledge/nhan-biet-hinh-khong-gian-11/2-nhiem-vu.html"},{"name":"Nhận biết hình học không gian • Trùm cuối","icon":"🏆","path":"games/knowledge/nhan-biet-hinh-khong-gian-11/3-trum-cuoi.html"}],
            "hinh_khoi_va_the_tich_co_ban_12": [{"name":"Hình khối và thể tích cơ bản • Khám phá","icon":"🔎","path":"games/knowledge/hinh-khoi-va-the-tich-co-ban-12/1-kham-pha.html"},{"name":"Hình khối và thể tích cơ bản • Nhiệm vụ","icon":"🧩","path":"games/knowledge/hinh-khoi-va-the-tich-co-ban-12/2-nhiem-vu.html"},{"name":"Hình khối và thể tích cơ bản • Trùm cuối","icon":"🏆","path":"games/knowledge/hinh-khoi-va-the-tich-co-ban-12/3-trum-cuoi.html"}],
            "hinh_hoc_oxyz_van_dung_12": [{"name":"Vận dụng tọa độ Oxyz • Khám phá","icon":"🔎","path":"games/knowledge/hinh-hoc-oxyz-van-dung-12/1-kham-pha.html"},{"name":"Vận dụng tọa độ Oxyz • Nhiệm vụ","icon":"🧩","path":"games/knowledge/hinh-hoc-oxyz-van-dung-12/2-nhiem-vu.html"},{"name":"Vận dụng tọa độ Oxyz • Trùm cuối","icon":"🏆","path":"games/knowledge/hinh-hoc-oxyz-van-dung-12/3-trum-cuoi.html"}]
        };
        const key = String(knowledge?.id || knowledge?.code || '').trim();
        const games = gameMap[key] || knowledge?.games || [];
        return games.map(function (game) {
            return { name: game.name, icon: game.icon, path: game.path };
        });
    }

    /* =====================================================
       RENDER GAMES
       ===================================================== */

    function renderGames(games) {

        if (
            !gameList
        ) {
            return false;
        }


        gameList.replaceChildren();


        if (
            !Array.isArray(games) ||
            games.length === 0
        ) {

            const empty =
                document.createElement(
                    "div"
                );

            empty.className =
                "game-empty";

            empty.textContent =
                "Hiện chưa có trò chơi cho chủ đề này.";

            gameList.appendChild(
                empty
            );

            return false;

        }


        games.forEach(
            function (game, gameIndex) {

                if (
                    !isValidGame(
                        game
                    )
                ) {
                    return;
                }


                const safePath =
                    getSafeGamePath(
                        game.path
                    );


                if (!safePath) {
                    return;
                }


                const button =
                    document.createElement(
                        "button"
                    );

                button.type =
                    "button";

                button.className =
                    "game-button";


                const number = document.createElement("span");
                number.className = "game-number";
                number.textContent = String(gameIndex + 1);

                const icon =
                    document.createElement(
                        "span"
                    );

                icon.className =
                    "game-icon";

                icon.textContent =
                    String(
                        game.icon ||
                        "🎮"
                    );


                const name =
                    document.createElement(
                        "span"
                    );

                name.className =
                    "game-name";

                name.textContent =
                    game.name;


                const start =
                    document.createElement(
                        "span"
                    );

                start.className =
                    "game-start";

                start.textContent =
                    "CHƠI NGAY →";


                button.appendChild(number);

                button.appendChild(
                    icon
                );

                button.appendChild(
                    name
                );

                button.appendChild(
                    start
                );


                button.setAttribute(
                    "aria-label",
                    "Chơi " +
                    game.name
                );


                button.addEventListener(
                    "click",
                    function () {

                        launchGame(
                            safePath
                        );

                    }
                );


                gameList.appendChild(
                    button
                );

            }
        );


        return true;

    }


    /* =====================================================
       ADD AI BUTTON
       ===================================================== */

    function addAIPracticeButton() {

        if (
            !gameList
        ) {
            return;
        }


        const aiButton =
            document.createElement(
                "button"
            );

        aiButton.type =
            "button";

        aiButton.className =
            "game-button mathweb-ai-practice-button";


        const icon =
            document.createElement(
                "span"
            );

        icon.className =
            "game-icon";

        icon.textContent =
            "🤖";


        const name =
            document.createElement(
                "span"
            );

        name.className =
            "game-name";

        name.textContent =
            "AI Luyện tập";


        const start =
            document.createElement(
                "span"
            );

        start.className =
            "game-start";

        start.textContent =
            "BẮT ĐẦU →";


        aiButton.appendChild(
            icon
        );

        aiButton.appendChild(
            name
        );

        aiButton.appendChild(
            start
        );


        aiButton.setAttribute(
            "aria-label",
            "Luyện tập với AI"
        );


        aiButton.addEventListener(
            "click",
            function () {

                openAISetup();

            }
        );


        gameList.prepend(
            aiButton
        );

    }


    /* =====================================================
       LAUNCH GAME
       ===================================================== */

    function launchGame(path) {

        const safePath =
            getSafeGamePath(
                path
            );

        if (!safePath) {

            console.error(
                "MATH WEB: Đường dẫn game không hợp lệ."
            );

            return false;

        }


        window.location.href =
            safePath;

        return true;

    }


    /* =====================================================
       CLOSE POPUP
       ===================================================== */

    function closeKnowledge(
        restoreFocus = true
    ) {

        if (
            !hasRequiredDOM()
        ) {
            return;
        }


        stopAITimer();


        knowledgePopup.classList.remove(
            "active"
        );

        practiceOverlay.classList.remove(
            "active"
        );


        knowledgePopup.setAttribute(
            "aria-hidden",
            "true"
        );

        practiceOverlay.setAttribute(
            "aria-hidden",
            "true"
        );


        document.body.classList.remove(
            "popup-open"
        );


        if (
            lastFocusedElement instanceof HTMLElement
        ) {

            lastFocusedElement.setAttribute(
                "aria-expanded",
                "false"
            );

        }


        const focusTarget =
            lastFocusedElement;


        resetAIState();


        currentKnowledge =
            null;

        lastFocusedElement =
            null;

        isPopupOpen =
            false;


        if (
            restoreFocus &&
            focusTarget instanceof HTMLElement &&
            document.contains(
                focusTarget
            )
        ) {

            requestAnimationFrame(
                function () {

                    try {
                        focusTarget.focus();
                    } catch {
                        /* Không làm gì */
                    }

                }
            );

        }

    }


    /* =====================================================
       AI STYLE
       ===================================================== */

    function injectAIStyle() {

        if (
            document.getElementById(
                "mathweb-ai-practice-style"
            )
        ) {
            return;
        }


        const style =
            document.createElement(
                "style"
            );

        style.id =
            "mathweb-ai-practice-style";


        style.textContent = `

            .mathweb-ai-panel {
                width: min(900px, 94vw);
                max-height: 88vh;
                overflow-y: auto;
                margin: auto;
                padding: 24px;
                border-radius: 22px;
                background:
                    linear-gradient(
                        145deg,
                        rgba(15, 20, 40, .98),
                        rgba(20, 28, 58, .98)
                    );
                color: #fff;
                box-shadow:
                    0 25px 80px rgba(0,0,0,.45);
                border: 1px solid rgba(255,255,255,.12);
                position: relative;
                z-index: 1002;
            }

            .mathweb-ai-title {
                font-size: 26px;
                font-weight: 800;
                margin-bottom: 6px;
            }

            .mathweb-ai-subtitle {
                opacity: .72;
                margin-bottom: 22px;
                line-height: 1.5;
            }

            .mathweb-ai-settings {
                display: grid;
                grid-template-columns:
                    repeat(
                        2,
                        minmax(0, 1fr)
                    );
                gap: 14px;
            }

            .mathweb-ai-field {
                display: flex;
                flex-direction: column;
                gap: 7px;
            }

            .mathweb-ai-field label {
                font-size: 13px;
                opacity: .72;
            }

            .mathweb-ai-field select,
            .mathweb-ai-field input {
                width: 100%;
                box-sizing: border-box;
                padding: 12px 13px;
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,.12);
                background: rgba(255,255,255,.07);
                color: #fff;
                outline: none;
            }

            .mathweb-ai-field select option {
                color: #111;
                background: #fff;
            }

            .mathweb-ai-actions {
                display: flex;
                gap: 10px;
                margin-top: 20px;
                flex-wrap: wrap;
            }

            .mathweb-ai-btn {
                border: 0;
                border-radius: 12px;
                padding: 12px 18px;
                cursor: pointer;
                font-weight: 700;
                color: #fff;
                background: rgba(255,255,255,.10);
                transition: .2s;
            }

            .mathweb-ai-btn:hover {
                transform: translateY(-1px);
                background: rgba(255,255,255,.16);
            }

            .mathweb-ai-btn-primary {
                background:
                    linear-gradient(
                        135deg,
                        #286cff,
                        #7a42ff
                    );
            }

            .mathweb-ai-error {
                margin-top: 15px;
                padding: 12px 14px;
                border-radius: 12px;
                background: rgba(255,70,90,.12);
                border: 1px solid rgba(255,70,90,.25);
                color: #ffb8c0;
                line-height: 1.45;
            }

            .mathweb-ai-loading {
                padding: 35px 10px;
                text-align: center;
            }

            .mathweb-ai-loader {
                width: 42px;
                height: 42px;
                border-radius: 50%;
                border: 4px solid rgba(255,255,255,.15);
                border-top-color: #6b8cff;
                animation: mathwebAiSpin .8s linear infinite;
                margin: 0 auto 14px;
            }

            @keyframes mathwebAiSpin {
                to {
                    transform: rotate(360deg);
                }
            }

            .mathweb-ai-progress {
                display: flex;
                justify-content: space-between;
                gap: 10px;
                font-size: 13px;
                opacity: .8;
                margin-bottom: 8px;
            }

            .mathweb-ai-progress-bar {
                height: 8px;
                border-radius: 99px;
                background: rgba(255,255,255,.10);
                overflow: hidden;
                margin-bottom: 22px;
            }

            .mathweb-ai-progress-fill {
                height: 100%;
                width: 0;
                background:
                    linear-gradient(
                        90deg,
                        #36d1dc,
                        #5b7cff,
                        #a45cff
                    );
                transition: width .25s ease;
            }

            .mathweb-ai-question {
                font-size: 20px;
                line-height: 1.6;
                font-weight: 700;
                margin-bottom: 18px;
                white-space: pre-wrap;
            }

            .mathweb-ai-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 16px;
            }

            .mathweb-ai-chip {
                padding: 5px 10px;
                border-radius: 99px;
                background: rgba(255,255,255,.08);
                font-size: 12px;
                opacity: .85;
            }

            .mathweb-ai-options {
                display: grid;
                gap: 10px;
            }

            .mathweb-ai-option {
                width: 100%;
                text-align: left;
                border: 1px solid rgba(255,255,255,.12);
                border-radius: 13px;
                padding: 13px 15px;
                background: rgba(255,255,255,.05);
                color: #fff;
                cursor: pointer;
                font-size: 15px;
                line-height: 1.45;
                transition: .18s;
            }

            .mathweb-ai-option:hover {
                background: rgba(255,255,255,.10);
                transform: translateX(2px);
            }

            .mathweb-ai-option:disabled {
                cursor: default;
            }

            .mathweb-ai-input {
                width: 100%;
                box-sizing: border-box;
                min-height: 48px;
                border-radius: 13px;
                border: 1px solid rgba(255,255,255,.13);
                background: rgba(255,255,255,.06);
                color: #fff;
                padding: 13px;
                outline: none;
                resize: vertical;
            }

            .mathweb-ai-feedback {
                margin-top: 18px;
                padding: 15px;
                border-radius: 14px;
                line-height: 1.55;
            }

            .mathweb-ai-correct {
                background: rgba(45,205,125,.12);
                border: 1px solid rgba(45,205,125,.25);
            }

            .mathweb-ai-wrong {
                background: rgba(255,90,100,.12);
                border: 1px solid rgba(255,90,100,.25);
            }

            .mathweb-ai-solution {
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid rgba(255,255,255,.10);
                font-size: 14px;
                opacity: .9;
                white-space: pre-wrap;
            }

            .mathweb-ai-diagram-wrap {
                margin: 14px auto 4px;
                width: min(100%, 360px);
                text-align: center;
                opacity: .95;
            }

            .mathweb-ai-diagram {
                width: 100%;
                max-height: 190px;
                color: currentColor;
            }

            .mathweb-ai-result {
                text-align: center;
                padding: 18px 5px;
            }

            .mathweb-ai-result-score {
                font-size: 46px;
                font-weight: 900;
                margin: 12px 0;
            }

            .mathweb-ai-result-grid {
                display: grid;
                grid-template-columns:
                    repeat(
                        4,
                        minmax(0, 1fr)
                    );
                gap: 10px;
                margin: 20px 0;
            }

            .mathweb-ai-stat {
                padding: 12px 8px;
                border-radius: 13px;
                background: rgba(255,255,255,.06);
            }

            .mathweb-ai-stat strong {
                display: block;
                font-size: 20px;
                margin-bottom: 4px;
            }

            .mathweb-ai-stat span {
                font-size: 12px;
                opacity: .65;
            }

            .mathweb-ai-practice-button {
                border: 1px solid rgba(90,130,255,.35);
            }

            @media (max-width: 650px) {

                .mathweb-ai-settings {
                    grid-template-columns: 1fr;
                }

                .mathweb-ai-result-grid {
                    grid-template-columns:
                        repeat(
                            2,
                            minmax(0, 1fr)
                        );
                }

                .mathweb-ai-panel {
                    padding: 17px;
                }

                .mathweb-ai-question {
                    font-size: 18px;
                }

            }

        `;


        document.head.appendChild(
            style
        );

    }


    /* =====================================================
       AI OVERLAY
       ===================================================== */

    let aiOverlay = null;


    function createAIOverlay() {

        injectAIStyle();


        if (
            aiOverlay &&
            document.contains(aiOverlay)
        ) {
            return aiOverlay;
        }


        aiOverlay =
            document.createElement(
                "div"
            );

        aiOverlay.id =
            "mathwebAIOverlay";

        aiOverlay.style.position =
            "fixed";

        aiOverlay.style.inset =
            "0";

        aiOverlay.style.zIndex =
            "2000";

        aiOverlay.style.display =
            "none";

        aiOverlay.style.alignItems =
            "center";

        aiOverlay.style.justifyContent =
            "center";

        aiOverlay.style.padding =
            "15px";

        aiOverlay.style.boxSizing =
            "border-box";

        aiOverlay.style.background =
            "rgba(0,0,0,.72)";


        aiOverlay.addEventListener(
            "click",
            function (event) {

                if (
                    event.target ===
                    aiOverlay
                ) {

                    closeAIPractice();

                }

            }
        );


        document.body.appendChild(
            aiOverlay
        );


        return aiOverlay;

    }


    /* =====================================================
       OPEN AI SETUP
       ===================================================== */

    function openAISetup() {

        // Close the topic/game information popup first; keep currentKnowledge so
        // the selected topic is still sent to the AI question engine.
        if (knowledgePopup) knowledgePopup.classList.remove("active");
        if (practiceOverlay) practiceOverlay.classList.remove("active");
        if (knowledgePopup) knowledgePopup.setAttribute("aria-hidden", "true");
        if (practiceOverlay) practiceOverlay.setAttribute("aria-hidden", "true");
        document.body.classList.remove("popup-open");
        isPopupOpen = false;

        const overlay =
            createAIOverlay();


        overlay.style.display =
            "flex";


        aiPracticeOpen =
            true;


        renderAISetup();

    }


    /* =====================================================
       RENDER AI SETUP
       ===================================================== */

    function renderAISetup() {

        const overlay =
            createAIOverlay();


        const topicName =
            currentKnowledge
                ? currentKnowledge.name
                : "Toán học";


        overlay.innerHTML = `

            <section
                class="mathweb-ai-panel"
                role="dialog"
                aria-modal="true"
                aria-label="AI Luyện tập"
            >

                <div class="mathweb-ai-title">
                    🤖 AI Luyện tập
                </div>

                <div class="mathweb-ai-subtitle">
                    Chủ đề:
                    <strong>
                        ${escapeHTML(topicName)}
                    </strong>
                    <br>
                    Chọn hình thức câu hỏi và độ khó trước khi tạo đề.
                    Nền tảng tập trung kiến thức cơ bản; Trung cấp tăng vận dụng;
                    Nâng cao ưu tiên suy luận nhiều bước; Địa ngục hướng tới bài toán
                    thử thách cực khó. Mỗi câu được kiểm tra trùng lặp trong bộ đề.
                </div>


                <div class="mathweb-ai-settings">

                    <div class="mathweb-ai-field">

                        <label for="mathwebAiGrade">
                            Lớp
                        </label>

                        <select id="mathwebAiGrade">

                            <option value="10">
                                Lớp 10
                            </option>

                            <option value="11">
                                Lớp 11
                            </option>

                            <option value="12">
                                Lớp 12
                            </option>

                        </select>

                    </div>


                    <div class="mathweb-ai-field">

                        <label for="mathwebAiDifficulty">
                            Cấp kiến thức
                        </label>

                        <select id="mathwebAiDifficulty">

                            <option value="easy">
                                🔰 Nền tảng · Dễ, nắm chắc kiến thức
                            </option>

                            <option value="medium" selected>
                                🔵 Trung cấp · Vận dụng nhiều bước
                            </option>

                            <option value="hard">
                                🟣 Nâng cao · HSG quốc gia/quốc tế
                            </option>

                            <option value="hell">
                                🔥 Địa ngục · Thử thách cực hạn
                            </option>

                        </select></div>


                    <div class="mathweb-ai-field">

                        <label for="mathwebAiType">
                            Dạng câu hỏi
                        </label>

                        <select id="mathwebAiType">

                            <option value="multiple_choice">
                                Trắc nghiệm
                            </option>

                            <option value="true_false">
                                Đúng / Sai
                            </option>

                            <option value="short_answer">
                                Điền đáp án
                            </option>

                            <option value="mixed" selected>
                                ✨ Tất cả hình thức (mặc định)
                            </option>

                        </select>

                    </div>


                    <div class="mathweb-ai-field">

                        <label for="mathwebAiProblemMode">
                            Kiểu luyện tập
                        </label>

                        <select id="mathwebAiProblemMode">

                            <option value="false" selected>
                                Câu hỏi riêng lẻ
                            </option>

                            <option value="true">
                                🧩 Bài toán thực tế nhiều phần
                            </option>

                        </select>

                    </div>


                    <div class="mathweb-ai-field" id="mathwebAiProblemPartsField" style="display:none;">

                        <label for="mathwebAiProblemParts">
                            Số phần / bài
                        </label>

                        <select id="mathwebAiProblemParts">
                            <option value="3">3 phần</option>
                            <option value="4" selected>4 phần</option>
                            <option value="5">5 phần</option>
                            <option value="6">6 phần</option>
                        </select>

                    </div>


                    <div class="mathweb-ai-field">

                        <label for="mathwebAiCount">
                            Số câu
                        </label>

                        <select id="mathwebAiCount">

                            <option value="5">
                                5 câu
                            </option>

                            <option value="10" selected>
                                10 câu
                            </option>

                            <option value="15">
                                15 câu
                            </option>

                            <option value="20">
                                20 câu
                            </option>

                            <option value="30">
                                30 câu
                            </option>

                        </select>

                    </div>

                </div>


                <div
                    id="mathwebAiSetupError"
                    style="display:none"
                ></div>


                <div class="mathweb-ai-actions">

                    <button
                        type="button"
                        class="mathweb-ai-btn mathweb-ai-btn-primary"
                        id="mathwebAiStart"
                    >
                        🚀 Bắt đầu luyện tập
                    </button>

                    <button
                        type="button"
                        class="mathweb-ai-btn"
                        id="mathwebAiBack"
                    >
                        ← Quay lại
                    </button>

                </div>

            </section>

        `;


        const grade =
            document.getElementById(
                "mathwebAiGrade"
            );

        const difficulty =
            document.getElementById(
                "mathwebAiDifficulty"
            );

        const type =
            document.getElementById(
                "mathwebAiType"
            );

        const count =
            document.getElementById(
                "mathwebAiCount"
            );


        if (grade) {
            const preferredGrade = Number(currentKnowledge?.grade);
            grade.value = String(
                Number.isInteger(preferredGrade) && preferredGrade >= 10 && preferredGrade <= 12
                    ? preferredGrade
                    : aiCurrentSettings.grade
            );
        }

        if (difficulty) {
            difficulty.value =
                aiCurrentSettings.difficulty;
        }

        if (type) {
            type.value =
                aiCurrentSettings.question_type;
        }

        if (count) {
            count.value =
                String(
                    aiCurrentSettings.count
                );
        }


        const problemMode =
            document.getElementById("mathwebAiProblemMode");
        const problemPartsField =
            document.getElementById("mathwebAiProblemPartsField");
        const problemParts =
            document.getElementById("mathwebAiProblemParts");

        if (problemMode) {
            problemMode.value = aiCurrentSettings.problem_mode ? "true" : "false";
            const syncProblemMode = function () {
                const enabled = problemMode.value === "true";
                if (problemPartsField) problemPartsField.style.display = enabled ? "" : "none";
                const countLabel = document.querySelector('label[for="mathwebAiCount"]');
                if (countLabel) countLabel.textContent = enabled ? "Số bài toán" : "Số câu";
                aiCurrentSettings.problem_mode = enabled;
            };
            problemMode.addEventListener("change", syncProblemMode);
            syncProblemMode();
        }
        if (problemParts) {
            problemParts.value = String(aiCurrentSettings.problem_parts || 4);
        }


        document
            .getElementById(
                "mathwebAiStart"
            )
            ?.addEventListener(
                "click",
                startAIPractice
            );


        document
            .getElementById(
                "mathwebAiBack"
            )
            ?.addEventListener(
                "click",
                closeAIPractice
            );

    }


    /* =====================================================
       CANONICAL AI TOPIC
       ===================================================== */

    function getCanonicalAITopic(knowledge) {
        if (!knowledge) return "";
        const aliases = {
            PROBABILITY: "xac_suat",
            COMBINATION: "hoan_vi_chinh_hop_to_hop",
            PERMUTATION: "hoan_vi_chinh_hop_to_hop",
            FUNCTION: "ham_so_bac_hai",
            SYSTEM_EQUATION: "phuong_trinh_he",
            QUADRATIC_EQUATION: "phuong_trinh_he",
            INEQUALITY: "bat_phuong_trinh",
            SEQUENCE: "day_so",
            DIVISIBILITY: "menh_de_tap_hop",
            REMAINDER: "menh_de_tap_hop",
            RADICAL: "menh_de_tap_hop",
            IDENTITIES: "menh_de_tap_hop",
            ALGEBRAIC_FRACTION: "menh_de_tap_hop",
            GEOMETRY: "hinh_hoc_10",
            hinh_hoc_co_ban_10: "hinh_hoc_10",
            tam_giac_tu_giac_10: "hinh_hoc_10",
            duong_tron_co_ban_10: "duong_tron",
            he_thuc_luong_van_dung_10: "he_thuc_luong_tam_giac",
            toa_do_hinh_hoc_10: "duong_thang",
            chung_minh_hinh_hoc_10: "hinh_hoc_10",
            phep_bien_hinh_co_ban_11: "phep_bien_hinh_11",
            nhan_biet_hinh_khong_gian_11: "hinh_khong_gian",
            hinh_khoi_va_the_tich_co_ban_12: "the_tich_khong_gian",
            hinh_hoc_oxyz_van_dung_12: "goc_khoang_cach_oxyz",
            STATISTICS: "thong_ke"
        };
        const raw=String(knowledge.code || knowledge.id || "").trim();
        return aliases[raw] || raw;
    }


    /* =====================================================
       START AI PRACTICE
       ===================================================== */

    async function startAIPractice() {

        const grade =
            Number(
                document.getElementById(
                    "mathwebAiGrade"
                )?.value ||
                DEFAULT_GRADE
            );

        const difficulty =
            String(
                document.getElementById(
                    "mathwebAiDifficulty"
                )?.value ||
                DEFAULT_DIFFICULTY
            );

        const questionType =
            String(
                document.getElementById(
                    "mathwebAiType"
                )?.value ||
                DEFAULT_QUESTION_TYPE
            );

        const count =
            Number(
                document.getElementById(
                    "mathwebAiCount"
                )?.value ||
                DEFAULT_COUNT
            );

        const problemMode =
            document.getElementById("mathwebAiProblemMode")?.value === "true";

        const problemParts =
            Number(
                document.getElementById("mathwebAiProblemParts")?.value || 4
            );


        if (!currentKnowledge) {
            showAIError("Chưa xác định được chủ đề luyện tập.");
            return;
        }

        const canonicalTopic = getCanonicalAITopic(currentKnowledge);
        if (!canonicalTopic) {
            showAIError("Không xác định được mã kiến thức để tạo đề AI.");
            return;
        }


        if (
            !Number.isInteger(grade) ||
            grade < 10 ||
            grade > 12
        ) {

            showAIError(
                "Lớp không hợp lệ."
            );

            return;

        }


        if (
            !Number.isInteger(count) ||
            count < 1 ||
            count > MAX_PRACTICE_COUNT
        ) {

            showAIError(
                "Số câu luyện tập không hợp lệ."
            );

            return;

        }


        aiCurrentSettings = {
            grade: grade,
            difficulty: difficulty,
            question_type: questionType,
            count: count,
            problem_mode: problemMode,
            problem_parts: problemParts
        };


        renderAILoading(
            problemMode
                ? "AI đang xây dựng các bài toán nhiều phần..."
                : "AI đang tạo bộ câu hỏi..."
        );


        try {

            const history =
                aiHistory.map(
                    function (item) {

                        return {
                            difficulty:
                                item.difficulty,
                            correct:
                                item.correct,
                            response_time:
                                item.response_time
                        };

                    }
                );


            const result =
                await apiRequest(
                    AI_API +
                    "/practice/session",
                    {
                        method: "POST",
                        body: JSON.stringify({
                            grade: grade,
                            topics: [
                                canonicalTopic
                            ],
                            count: count,
                            difficulty: difficulty,
                            question_type: questionType,
                            history: history,
                            problem_mode: problemMode,
                            problem_parts: problemParts
                        })
                    }
                );


            const questions =
                extractQuestions(
                    result
                );


            if (
                !questions.length
            ) {

                throw new Error(
                    "AI không trả về câu hỏi hợp lệ."
                );

            }


            aiQuestions =
                questions;

            aiCurrentIndex =
                0;

            aiHistory =
                [];

            aiScore =
                0;

            aiCorrect =
                0;

            aiWrong =
                0;

            aiSkipped =
                0;

            aiAnswered =
                false;

            aiSessionStartedAt =
                Date.now();

            aiQuestionStartedAt =
                Date.now();


            renderAIQuestion();

        } catch (error) {

            console.error(
                "MATH WEB AI:",
                error
            );

            showAIError(
                error?.message ||
                "Không thể tạo bộ câu hỏi AI."
            );

        }

    }


    /* =====================================================
       EXTRACT QUESTIONS
       ===================================================== */

    function extractQuestions(data) {

        if (
            !data ||
            typeof data !== "object"
        ) {
            return [];
        }


        if (
            Array.isArray(
                data.questions
            )
        ) {
            return data.questions;
        }


        if (
            Array.isArray(
                data.items
            )
        ) {
            return data.items;
        }


        if (
            data.data &&
            Array.isArray(
                data.data.questions
            )
        ) {
            return data.data.questions;
        }


        if (
            Array.isArray(data)
        ) {
            return data;
        }


        return [];

    }


    /* =====================================================
       QUESTION HELPERS
       ===================================================== */

    function getQuestionText(question) {

        if (!question) {
            return "";
        }


        const candidates = [

            question.question,

            question.text,

            question.content,

            question.prompt,

            question.question_text,

            question.title

        ];


        for (
            const candidate of candidates
        ) {

            if (
                typeof candidate === "string" &&
                candidate.trim()
            ) {

                return candidate;

            }

        }


        return "Không đọc được nội dung câu hỏi.";

    }


    function getQuestionType(question) {

        if (!question) {
            return DEFAULT_QUESTION_TYPE;
        }


        const type =
            String(
                question.question_type ||
                question.type ||
                DEFAULT_QUESTION_TYPE
            ).toLowerCase();


        if (
            type === "mcq" ||
            type === "multiple-choice"
        ) {
            return "multiple_choice";
        }


        if (
            type === "tf" ||
            type === "true-false"
        ) {
            return "true_false";
        }


        if (
            type === "short" ||
            type === "short-answer"
        ) {
            return "short_answer";
        }


        return type;

    }


    function getQuestionOptions(question) {

        if (!question) {
            return [];
        }


        const options =
            question.options ||
            question.choices ||
            question.answers;


        if (
            !Array.isArray(options)
        ) {
            return [];
        }


        return options.map(
            function (option, index) {

                if (
                    option &&
                    typeof option === "object"
                ) {

                    return {
                        value:
                            option.value ??
                            option.id ??
                            option.key ??
                            String(index),
                        label:
                            option.label ??
                            option.text ??
                            option.content ??
                            String(option)
                    };

                }


                return {
                    value:
                        String(index),
                    label:
                        String(option)
                };

            }
        );

    }


    function getQuestionDifficulty(question) {

        if (!question) {
            return aiCurrentSettings.difficulty;
        }


        return String(
            question.difficulty ||
            aiCurrentSettings.difficulty ||
            "medium"
        );

    }


    function getDifficultyLabel(level) {

        const labels = {
            easy: "Dễ",
            medium: "Vừa",
            hard: "Khó",
            expert: "Chuyên"
        };


        return (
            labels[
                String(level).toLowerCase()
            ] ||
            String(level || "Vừa")
        );

    }


    /* =====================================================
       RENDER AI LOADING
       ===================================================== */

    function renderAILoading(message) {

        const overlay =
            createAIOverlay();


        overlay.style.display =
            "flex";


        overlay.innerHTML = `

            <section
                class="mathweb-ai-panel"
                role="dialog"
                aria-modal="true"
            >

                <div class="mathweb-ai-loading">

                    <div class="mathweb-ai-loader"></div>

                    <div style="font-size:18px;font-weight:700;">
                        ${escapeHTML(message)}
                    </div>

                    <div style="margin-top:8px;opacity:.65;">
                        Đang kiểm tra và chuẩn bị câu hỏi...
                    </div>

                </div>

            </section>

        `;

    }


    /* =====================================================
       RENDER AI QUESTION
       ===================================================== */

    function renderAIQuestion() {

        stopAITimer();


        const question =
            aiQuestions[
                aiCurrentIndex
            ];


        if (!question) {

            finishAIPractice();

            return;

        }


        aiAnswered =
            false;

        aiQuestionStartedAt =
            Date.now();


        const overlay =
            createAIOverlay();


        overlay.style.display =
            "flex";


        const questionText =
            getQuestionText(
                question
            );

        const problemTitle =
            question?.problem_title || "";
        const problemContext =
            question?.problem_context || "";
        const problemPart =
            question?.part || "";

        const type =
            getQuestionType(
                question
            );

        const difficulty =
            getQuestionDifficulty(
                question
            );

        const options =
            getQuestionOptions(
                question
            );


        const progress =
            aiQuestions.length
                ? (
                    (
                        aiCurrentIndex /
                        aiQuestions.length
                    ) *
                    100
                )
                : 0;


        overlay.innerHTML = `

            <section
                class="mathweb-ai-panel"
                role="dialog"
                aria-modal="true"
                aria-label="Câu hỏi AI"
            >

                <div class="mathweb-ai-progress">

                    <span>
                        Câu
                        ${aiCurrentIndex + 1}
                        /
                        ${aiQuestions.length}
                    </span>

                    <span>
                        ${escapeHTML(
                            currentKnowledge?.name ||
                            "Toán học"
                        )}
                    </span>

                </div>


                <div class="mathweb-ai-progress-bar">

                    <div
                        class="mathweb-ai-progress-fill"
                        style="width:${progress}%"
                    ></div>

                </div>


                <div class="mathweb-ai-meta">

                    <span class="mathweb-ai-chip">
                        Lớp ${aiCurrentSettings.grade}
                    </span>

                    <span class="mathweb-ai-chip">
                        ${escapeHTML(
                            getDifficultyLabel(
                                difficulty
                            )
                        )}
                    </span>

                    <span class="mathweb-ai-chip">
                        ${getTypeLabel(type)}
                    </span>

                    <span
                        class="mathweb-ai-chip"
                        id="mathwebAiTime"
                    >
                        ⏱ 0s
                    </span>

                </div>


                ${problemTitle ? `
                    <div style="margin-bottom:12px;padding:12px 14px;border-radius:14px;background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.16);">
                        <div style="font-weight:800;margin-bottom:5px;">🧩 ${escapeHTML(problemTitle)}${problemPart ? ` · Phần ${escapeHTML(problemPart)}` : ""}</div>
                        <div style="font-size:13px;line-height:1.65;opacity:.84;">${escapeHTML(problemContext)}</div>
                    </div>
                ` : ""}

                <div class="mathweb-ai-question">
                    ${escapeHTML(
                        questionText
                    )}
                </div>

                ${renderAIDiagram(question?.diagram)}

                <div
                    id="mathwebAiAnswerArea"
                >
                    ${renderAnswerArea(
                        question,
                        type,
                        options
                    )}
                </div>


                <div
                    id="mathwebAiFeedback"
                ></div>


                <div class="mathweb-ai-actions">

                    <button
                        type="button"
                        class="mathweb-ai-btn"
                        id="mathwebAiSkip"
                    >
                        Bỏ qua
                    </button>

                </div>

            </section>

        `;


        const skip =
            document.getElementById(
                "mathwebAiSkip"
            );


        if (skip) {

            skip.addEventListener(
                "click",
                function () {

                    skipAIQuestion();

                }
            );

        }


        startAITimer();

    }


    /* =====================================================
       TYPE LABEL
       ===================================================== */

    function getTypeLabel(type) {

        const labels = {

            multiple_choice:
                "Trắc nghiệm",

            true_false:
                "Đúng / Sai",

            short_answer:
                "Trả lời ngắn"

        };


        return (
            labels[type] ||
            "Câu hỏi"
        );

    }


    /* =====================================================
       RENDER OPTIONAL GEOMETRY DIAGRAM
       ===================================================== */

    function renderAIDiagram(diagram) {
        if (!diagram || !diagram.type) return "";

        const label = function (value) {
            return escapeHTML(String(value ?? ""));
        };

        if (diagram.type === "graph" && Array.isArray(diagram.x_range) && Array.isArray(diagram.y_range)) {
            const xmin = Number(diagram.x_range[0]), xmax = Number(diagram.x_range[1]);
            const ymin = Number(diagram.y_range[0]), ymax = Number(diagram.y_range[1]);
            if (![xmin, xmax, ymin, ymax].every(Number.isFinite) || xmin >= xmax || ymin >= ymax) return "";
            const W = 360, H = 220, left = 38, right = 14, top = 14, bottom = 30;
            const plotW = W-left-right, plotH = H-top-bottom;
            const px = x => left + (Number(x)-xmin)/(xmax-xmin)*plotW;
            const py = y => top + (ymax-Number(y))/(ymax-ymin)*plotH;
            const niceStep = span => {
                const rough = span / 6, power = Math.pow(10, Math.floor(Math.log10(Math.max(rough, 1e-9))));
                const unit = rough / power;
                return (unit <= 1 ? 1 : unit <= 2 ? 2 : unit <= 5 ? 5 : 10) * power;
            };
            const fmtTick = v => Number(v.toPrecision(4)).toString();
            const sx = niceStep(xmax-xmin), sy = niceStep(ymax-ymin);
            const bits = [];
            if (diagram.grid !== false) {
                for (let x = Math.ceil(xmin/sx)*sx; x <= xmax+sx*1e-7; x += sx) {
                    bits.push(`<line x1="${px(x)}" y1="${top}" x2="${px(x)}" y2="${top+plotH}" stroke="currentColor" opacity=".12" stroke-width="1"/>`);
                }
                for (let y = Math.ceil(ymin/sy)*sy; y <= ymax+sy*1e-7; y += sy) {
                    bits.push(`<line x1="${left}" y1="${py(y)}" x2="${left+plotW}" y2="${py(y)}" stroke="currentColor" opacity=".12" stroke-width="1"/>`);
                }
            }
            if (xmin <= 0 && xmax >= 0) bits.push(`<line x1="${px(0)}" y1="${top}" x2="${px(0)}" y2="${top+plotH}" stroke="currentColor" stroke-width="1.5" opacity=".75"/>`);
            if (ymin <= 0 && ymax >= 0) bits.push(`<line x1="${left}" y1="${py(0)}" x2="${left+plotW}" y2="${py(0)}" stroke="currentColor" stroke-width="1.5" opacity=".75"/>`);
            for (let x = Math.ceil(xmin/sx)*sx; x <= xmax+sx*1e-7; x += sx) {
                if (Math.abs(x) < sx*1e-7) continue;
                bits.push(`<text x="${px(x)}" y="${Math.min(H-5, Math.max(top+11, (ymin<=0&&ymax>=0?py(0):top+plotH)+14))}" font-size="9" text-anchor="middle" fill="currentColor" opacity=".75">${label(fmtTick(x))}</text>`);
            }
            for (let y = Math.ceil(ymin/sy)*sy; y <= ymax+sy*1e-7; y += sy) {
                if (Math.abs(y) < sy*1e-7) continue;
                bits.push(`<text x="${Math.max(7, (xmin<=0&&xmax>=0?px(0):left)+ (xmin<=0&&xmax>=0?-5: -6))}" y="${py(y)+3}" font-size="9" text-anchor="end" fill="currentColor" opacity=".75">${label(fmtTick(y))}</text>`);
            }
            if (xmin <= 0 && xmax >= 0 && ymin <= 0 && ymax >= 0) bits.push(`<text x="${px(0)-7}" y="${py(0)+12}" font-size="10" fill="currentColor">O</text>`);
            bits.push(`<text x="${W-right-2}" y="${Math.min(H-3, Math.max(11, (ymin<=0&&ymax>=0?py(0):H-bottom)+12))}" font-size="11" fill="currentColor">${label(diagram.x_label || "x")}</text>`);
            bits.push(`<text x="${Math.min(W-10, Math.max(10, (xmin<=0&&xmax>=0?px(0):left)+8))}" y="${top+7}" font-size="11" fill="currentColor">${label(diagram.y_label || "y")}</text>`);
            (diagram.asymptotes || []).forEach(a => {
                if (a.axis === "x" && Number.isFinite(Number(a.value)) && a.value >= xmin && a.value <= xmax) {
                    bits.push(`<line x1="${px(a.value)}" y1="${top}" x2="${px(a.value)}" y2="${top+plotH}" stroke="#e6a23c" stroke-width="1.5" stroke-dasharray="5 4"/>`);
                    if (a.label) bits.push(`<text x="${px(a.value)+3}" y="${top+12}" font-size="10" fill="#e6a23c">${label(a.label)}</text>`);
                } else if (a.axis === "y" && Number.isFinite(Number(a.value)) && a.value >= ymin && a.value <= ymax) {
                    bits.push(`<line x1="${left}" y1="${py(a.value)}" x2="${left+plotW}" y2="${py(a.value)}" stroke="#e6a23c" stroke-width="1.5" stroke-dasharray="5 4"/>`);
                    if (a.label) bits.push(`<text x="${left+4}" y="${py(a.value)-4}" font-size="10" fill="#e6a23c">${label(a.label)}</text>`);
                }
            });
            const palette = ["#22a06b", "#378add", "#e06c9f", "#e6a23c"];
            (diagram.curves || []).forEach((curve, index) => {
                const runs = []; let run = [];
                (curve.points || []).forEach(p => {
                    if (!Array.isArray(p) || p.length < 2 || !Number.isFinite(Number(p[0])) || !Number.isFinite(Number(p[1])) || Number(p[0]) < xmin || Number(p[0]) > xmax || Number(p[1]) < ymin || Number(p[1]) > ymax) {
                        if (run.length >= 2) runs.push(run);
                        run = [];
                        return;
                    }
                    run.push(p);
                });
                if (run.length >= 2) runs.push(run);
                const dash = curve.style === "dashed" ? 'stroke-dasharray="5 4"' : "";
                runs.forEach(pts => {
                    const coords = pts.map(p => `${px(p[0])},${py(p[1])}`).join(" ");
                    bits.push(`<polyline points="${coords}" fill="none" stroke="${palette[index % palette.length]}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round" ${dash}/>`);
                });
            });
            (diagram.marked_points || []).forEach(p => {
                const x = Number(p.x), y = Number(p.y);
                if (!Number.isFinite(x) || !Number.isFinite(y) || x < xmin || x > xmax || y < ymin || y > ymax) return;
                bits.push(`<circle cx="${px(x)}" cy="${py(y)}" r="3.6" fill="#e06c9f" stroke="white" stroke-width="1"/>`);
                if (p.label) bits.push(`<text x="${px(x)+5}" y="${py(y)-6}" font-size="10" fill="currentColor">${label(p.label)}</text>`);
            });
            return `<div class="mathweb-ai-diagram-wrap"><svg class="mathweb-ai-diagram" viewBox="0 0 ${W} ${H}" role="img" aria-label="Đồ thị tọa độ được dựng từ dữ kiện đề bài">${bits.join("")}</svg><div style="font-size:11px;opacity:.7;margin-top:4px;">${label(diagram.caption || "Đồ thị theo dữ kiện đề bài")}</div></div>`;
        }

        if (diagram.type === "geometry" && diagram.points) {
            const points = diagram.points || {};
            const drawPoints = { ...points };
            const rotation = diagram._rotation || { yaw: -28, pitch: 18 };
            if (diagram.coordinates_3d && typeof diagram.coordinates_3d === "object") {
                const yaw = Number(rotation.yaw || 0) * Math.PI / 180;
                const pitch = Number(rotation.pitch || 0) * Math.PI / 180;
                Object.entries(diagram.coordinates_3d).forEach(([name, xyz]) => {
                    if (!Array.isArray(xyz) || xyz.length < 3 || !xyz.slice(0, 3).every(v => Number.isFinite(Number(v)))) return;
                    const [x, y, z] = xyz.map(Number);
                    const xr = x * Math.cos(yaw) - z * Math.sin(yaw);
                    const zr = x * Math.sin(yaw) + z * Math.cos(yaw);
                    const yr = y * Math.cos(pitch) - zr * Math.sin(pitch);
                    drawPoints[name] = [xr, yr];
                });
            }
            const entries = Object.entries(drawPoints);
            if (!entries.length) return "";
            const xs = entries.map(e => Number(e[1]?.[0] || 0));
            const ys = entries.map(e => Number(e[1]?.[1] || 0));
            (diagram.circles || []).forEach(c => {
                const center = c.center || [0, 0], r = Number(c.radius || 0);
                xs.push(Number(center[0])-r, Number(center[0])+r);
                ys.push(Number(center[1])-r, Number(center[1])+r);
            });
            (diagram.polylines || []).forEach(linePoints => (linePoints || []).forEach(xy => {
                xs.push(Number(xy[0]) || 0); ys.push(Number(xy[1]) || 0);
            }));
            const minX = Math.min(...xs), maxX = Math.max(...xs);
            const minY = Math.min(...ys), maxY = Math.max(...ys);
            const spanX = Math.max(1, maxX - minX);
            const spanY = Math.max(1, maxY - minY);
            const pad = 38;
            const sx = (360 - pad * 2) / spanX;
            const sy = (190 - pad * 2) / spanY;
            const scale = Math.min(sx, sy);
            const ox = (360 - spanX * scale) / 2;
            const oy = (190 - spanY * scale) / 2;
            const project = function (xy) {
                return [ox + (Number(xy[0]) - minX) * scale, 190 - oy - (Number(xy[1]) - minY) * scale];
            };
            const svgLines = [];
            if (diagram.axes) {
                svgLines.push(`<line x1="20" y1="${190/2}" x2="340" y2="${190/2}" stroke="currentColor" stroke-width="1.5" opacity=".45"/>`);
                svgLines.push(`<line x1="180" y1="15" x2="180" y2="175" stroke="currentColor" stroke-width="1.5" opacity=".45"/>`);
            }
            (diagram.circles || []).forEach(c => {
                const center = project(c.center || [0, 0]);
                const edge = project([(c.center || [0,0])[0] + Number(c.radius || 1), (c.center || [0,0])[1]]);
                const radiusPx = Math.hypot(edge[0]-center[0], edge[1]-center[1]);
                svgLines.push(`<circle cx="${center[0]}" cy="${center[1]}" r="${radiusPx}" fill="none" stroke="currentColor" stroke-width="2.2" opacity=".8"/>`);
            });
            (diagram.segments || []).forEach(seg => {
                const a = project(drawPoints[seg[0]]), b = project(drawPoints[seg[1]]);
                svgLines.push(`<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="currentColor" stroke-width="3"/>`);
            });
            (diagram.hidden_segments || []).forEach(seg => {
                if (!drawPoints[seg[0]] || !drawPoints[seg[1]]) return;
                const a = project(drawPoints[seg[0]]), b = project(drawPoints[seg[1]]);
                svgLines.push(`<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4" opacity=".7"/>`);
            });
            (diagram.dashed_segments || []).forEach(seg => {
                if (!drawPoints[seg[0]] || !drawPoints[seg[1]]) return;
                const a = project(drawPoints[seg[0]]), b = project(drawPoints[seg[1]]);
                svgLines.push(`<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#ffd166" stroke-width="2.4" stroke-dasharray="6 4"/>`);
            });
            (diagram.polylines || []).forEach(linePoints => {
                const coords = (linePoints || []).map(xy => project(xy)).map(p => p.join(",")).join(" ");
                if (coords) svgLines.push(`<polyline points="${coords}" fill="none" stroke="#58d9f7" stroke-width="2.5" stroke-linejoin="round"/>`);
            });
            entries.forEach(([name, xy]) => {
                const p = project(xy);
                if (!(diagram.hide_labels || []).includes(name)) {
                    svgLines.push(`<circle cx="${p[0]}" cy="${p[1]}" r="4" fill="currentColor"/>`);
                    svgLines.push(`<text x="${p[0] + 7}" y="${p[1] - 7}" font-size="15" font-weight="700">${label(name)}</text>`);
                }
            });
            if (diagram.measurements) {
                diagram.measurements.forEach(m => {
                    if (!drawPoints[m.from] || !drawPoints[m.to]) return;
                    const a = project(drawPoints[m.from]), b = project(drawPoints[m.to]);
                    const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
                    svgLines.push(`<text x="${mx + 5}" y="${my - 5}" font-size="13">${label(m.text)}</text>`);
                });
            }
            if (diagram.angle_labels) {
                Object.entries(diagram.angle_labels).forEach(([key, value]) => {
                    const names = key.split("").filter(ch => drawPoints[ch]);
                    if (!names.length) return;
                    const ps = names.map(n => project(drawPoints[n]));
                    const x = ps.reduce((sum,p)=>sum+p[0],0)/ps.length;
                    const y = ps.reduce((sum,p)=>sum+p[1],0)/ps.length;
                    svgLines.push(`<text x="${x+5}" y="${y-5}" font-size="12" fill="#e7c66b">${label(value + "°")}</text>`);
                });
            }
            const rightAngles = Array.isArray(diagram.right_angles) ? diagram.right_angles : (diagram.right_angle ? [diagram.right_angle] : []);
            rightAngles.forEach(vertex => {
                const adjacent = (diagram.segments || []).filter(seg => seg.includes(vertex)).map(seg => seg.find(n => n !== vertex)).filter(n => drawPoints[n]);
                if (adjacent.length < 2) return;
                const raw = drawPoints[vertex];
                let pair = null, best = Infinity;
                for (let i = 0; i < adjacent.length; i++) for (let j = i + 1; j < adjacent.length; j++) {
                    const a = drawPoints[adjacent[i]], b = drawPoints[adjacent[j]];
                    const u = [Number(a[0])-Number(raw[0]), Number(a[1])-Number(raw[1])];
                    const v = [Number(b[0])-Number(raw[0]), Number(b[1])-Number(raw[1])];
                    const nu = Math.hypot(...u), nv = Math.hypot(...v);
                    if (!nu || !nv) continue;
                    const score = Math.abs((u[0]*v[0]+u[1]*v[1])/(nu*nv));
                    if (score < best) { best = score; pair = [adjacent[i], adjacent[j]]; }
                }
                if (!pair || best > 1e-4) return;
                const p = project(drawPoints[vertex]), p1 = project(drawPoints[pair[0]]), p2 = project(drawPoints[pair[1]]);
                const v1 = [p1[0]-p[0], p1[1]-p[1]], v2 = [p2[0]-p[0], p2[1]-p[1]];
                const n1 = Math.hypot(...v1) || 1, n2 = Math.hypot(...v2) || 1, size = 9;
                const q1 = [p[0]+v1[0]/n1*size,p[1]+v1[1]/n1*size], q2 = [p[0]+v2[0]/n2*size,p[1]+v2[1]/n2*size], q3=[q1[0]+q2[0]-p[0],q1[1]+q2[1]-p[1]];
                svgLines.push(`<path d="M ${q1[0]} ${q1[1]} L ${q3[0]} ${q3[1]} L ${q2[0]} ${q2[1]}" fill="none" stroke="currentColor" stroke-width="1.8"/>`);
            });
            const is3D = Boolean(diagram.coordinates_3d && Object.keys(diagram.coordinates_3d).length);
            const controls = is3D ? `<div class="mathweb-3d-controls" aria-label="Điều khiển góc nhìn 3D"><button type="button" onclick="window.mathwebRotateAIDiagram(this,'yaw',-15)" aria-label="Xoay trái">↶ Xoay trái</button><button type="button" onclick="window.mathwebRotateAIDiagram(this,'yaw',15)" aria-label="Xoay phải">Xoay phải ↷</button><button type="button" onclick="window.mathwebRotateAIDiagram(this,'pitch',-10)" aria-label="Nghiêng lên">Nghiêng lên</button><button type="button" onclick="window.mathwebRotateAIDiagram(this,'pitch',10)" aria-label="Nghiêng xuống">Nghiêng xuống</button><button type="button" onclick="window.mathwebRotateAIDiagram(this,'reset',0)">Đặt lại</button></div>` : "";
            const payload = is3D ? ` data-mathweb-geometry="${label(JSON.stringify({ ...diagram, _rotation: rotation }))}"` : "";
            const warning = diagram.diagram_mode === "schematic_projection" ? `<div class="mathweb-3d-note">Hình chiếu minh họa; dùng tọa độ và số liệu đề bài để tính toán.</div>` : "";
            return `<div class="mathweb-ai-diagram-wrap"${payload}><svg class="mathweb-ai-diagram" viewBox="0 0 360 190" role="img" aria-label="${is3D ? "Mô hình không gian 3D có thể xoay" : "Hình minh họa chính xác theo dữ kiện"}">${svgLines.join("")}</svg>${controls}<div style="font-size:11px;opacity:.7;margin-top:4px;">${label(diagram.caption || "Hình minh họa theo dữ kiện")}</div>${warning}</div>`;
        }

        const common = 'class="mathweb-ai-diagram" viewBox="0 0 360 190" role="img" aria-label="Hình minh họa"';

        if (diagram.type === "circle_inscribed_triangle") {
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <circle cx="180" cy="95" r="70" fill="none" stroke="currentColor" stroke-width="2.5"/>
                        <polygon points="180,25 112,132 248,132" fill="none" stroke="currentColor" stroke-width="3"/>
                        <line x1="180" y1="95" x2="180" y2="25" stroke="currentColor" stroke-width="1.8" stroke-dasharray="4 4"/>
                        <circle cx="180" cy="95" r="3.5" fill="currentColor"/>
                        <text x="174" y="18" font-size="15">A</text><text x="95" y="145" font-size="15">B</text><text x="251" y="145" font-size="15">C</text><text x="187" y="91" font-size="14">O</text>
                    </svg><div style="font-size:11px;opacity:.6;margin-top:4px;">${label(diagram.caption || "Tam giác nội tiếp đường tròn")}</div>
                </div>`;
        }

        if (diagram.type === "circle_inscribed" && diagram.shape === "rectangle") {
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <circle cx="180" cy="95" r="70" fill="none" stroke="currentColor" stroke-width="2.5"/>
                        <polygon points="125,35 235,35 235,155 125,155" fill="none" stroke="currentColor" stroke-width="3"/>
                        <line x1="125" y1="35" x2="235" y2="155" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/>
                        <line x1="235" y1="35" x2="125" y2="155" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/>
                        <text x="113" y="32" font-size="15">A</text><text x="239" y="32" font-size="15">B</text><text x="239" y="170" font-size="15">C</text><text x="112" y="170" font-size="15">D</text>
                    </svg><div style="font-size:11px;opacity:.6;margin-top:4px;">${label(diagram.caption || "Hình chữ nhật nội tiếp đường tròn")}</div>
                </div>`;
        }

        if (diagram.type === "triangle") {
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <polygon points="70,150 290,150 190,35" fill="none" stroke="currentColor" stroke-width="3"/>
                        <text x="58" y="168" font-size="16">${label(diagram.labels?.[0] || "A")}</text>
                        <text x="292" y="168" font-size="16">${label(diagram.labels?.[1] || "B")}</text>
                        <text x="194" y="27" font-size="16">${label(diagram.labels?.[2] || "C")}</text>
                    </svg>
                </div>`;
        }

        if (diagram.type === "circle_chord") {
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <circle cx="180" cy="95" r="65" fill="none" stroke="currentColor" stroke-width="3"/>
                        <line x1="115" y1="95" x2="245" y2="95" stroke="currentColor" stroke-width="3"/>
                        <line x1="180" y1="95" x2="180" y2="30" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/>
                        <line x1="180" y1="30" x2="180" y2="95" stroke="currentColor" stroke-width="2"/>
                        <circle cx="180" cy="95" r="4" fill="currentColor"/>
                        <text x="166" y="113" font-size="15">O</text><text x="105" y="91" font-size="15">A</text><text x="248" y="91" font-size="15">B</text><text x="185" y="31" font-size="15">H</text>
                    </svg><div style="font-size:11px;opacity:.6;margin-top:4px;">${label(diagram.caption || "Dây cung minh họa")}</div>
                </div>`;
        }

        if (diagram.type === "circle_tangent") {
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <circle cx="145" cy="105" r="58" fill="none" stroke="currentColor" stroke-width="3"/>
                        <line x1="145" y1="105" x2="203" y2="105" stroke="currentColor" stroke-width="2.5"/>
                        <line x1="203" y1="28" x2="203" y2="165" stroke="currentColor" stroke-width="3"/>
                        <circle cx="145" cy="105" r="4" fill="currentColor"/><circle cx="203" cy="105" r="4" fill="currentColor"/>
                        <path d="M 193 105 L 193 95 L 203 95" fill="none" stroke="currentColor" stroke-width="2"/>
                        <text x="132" y="98" font-size="15">O</text><text x="207" y="100" font-size="15">T</text><text x="169" y="96" font-size="13">R</text>
                    </svg><div style="font-size:11px;opacity:.6;margin-top:4px;">${label(diagram.caption || "Tiếp tuyến và bán kính")}</div>
                </div>`;
        }

        if (diagram.type === "circle_inscribed") {
            const polygon = diagram.shape === "rectangle" ? "125,35 235,35 235,155 125,155" : "132,43 239,76 214,151 104,126";
            const labels = diagram.shape === "rectangle"
                ? '<text x="113" y="32" font-size="15">A</text><text x="239" y="32" font-size="15">B</text><text x="239" y="170" font-size="15">C</text><text x="112" y="170" font-size="15">D</text>'
                : '<text x="119" y="40" font-size="15">A</text><text x="243" y="75" font-size="15">B</text><text x="218" y="165" font-size="15">C</text><text x="86" y="133" font-size="15">D</text>';
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <circle cx="180" cy="95" r="70" fill="none" stroke="currentColor" stroke-width="2.5"/>
                        <polygon points="${polygon}" fill="none" stroke="currentColor" stroke-width="3"/>
                        ${diagram.shape === "rectangle" ? '<line x1="125" y1="35" x2="235" y2="155" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/><line x1="235" y1="35" x2="125" y2="155" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/>' : ''}
                        ${labels}
                    </svg><div style="font-size:11px;opacity:.6;margin-top:4px;">${label(diagram.caption || "Tứ giác nội tiếp")}</div>
                </div>`;
        }

        if (diagram.type === "pyramid") {
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <polygon points="105,115 210,145 285,105 177,76" fill="none" stroke="currentColor" stroke-width="2.5"/>
                        <line x1="192" y1="25" x2="105" y2="115" stroke="currentColor" stroke-width="3"/><line x1="192" y1="25" x2="210" y2="145" stroke="currentColor" stroke-width="3"/><line x1="192" y1="25" x2="285" y2="105" stroke="currentColor" stroke-width="3"/><line x1="192" y1="25" x2="177" y2="76" stroke="currentColor" stroke-width="2.5" stroke-dasharray="5 4"/>
                        <text x="188" y="19" font-size="15">S</text><text x="88" y="118" font-size="15">A</text><text x="212" y="161" font-size="15">B</text><text x="289" y="105" font-size="15">C</text><text x="163" y="71" font-size="15">D</text>
                    </svg><div style="font-size:11px;opacity:.6;margin-top:4px;">${label(diagram.caption || "Hình chóp minh họa")}</div>
                </div>`;
        }

        if (diagram.type === "circle") {
            if (diagram.shape === "diameter" && diagram.points?.A && diagram.points?.B) {
                const diameterText = Number.isFinite(Number(diagram.diameter)) ? `AB=${label(diagram.diameter)}` : "AB";
                const radiusText = Number.isFinite(Number(diagram.radius)) ? `R=${label(diagram.radius)}` : "R";
                return `
                    <div class="mathweb-ai-diagram-wrap">
                        <svg ${common}>
                            <circle cx="180" cy="95" r="62" fill="none" stroke="currentColor" stroke-width="3"/>
                            <line x1="118" y1="95" x2="242" y2="95" stroke="currentColor" stroke-width="2.8"/>
                            <circle cx="180" cy="95" r="4" fill="currentColor"/>
                            <circle cx="118" cy="95" r="3.5" fill="currentColor"/><circle cx="242" cy="95" r="3.5" fill="currentColor"/>
                            <text x="106" y="84" font-size="15">A</text><text x="246" y="84" font-size="15">B</text><text x="185" y="88" font-size="15">O</text>
                            <text x="150" y="117" font-size="13">${diameterText}</text><text x="187" y="132" font-size="13">${radiusText}</text>
                        </svg><div style="font-size:11px;opacity:.6;margin-top:4px;">${label(diagram.caption || "Đường kính đi qua tâm, bằng hai lần bán kính")}</div>
                    </div>`;
            }
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <circle cx="180" cy="95" r="62" fill="none" stroke="currentColor" stroke-width="3"/>
                        <line x1="180" y1="95" x2="242" y2="95" stroke="currentColor" stroke-width="2"/>
                        <circle cx="180" cy="95" r="4" fill="currentColor"/>
                        <text x="168" y="88" font-size="16">${label(diagram.labels?.[0] || "O")}</text>
                        <text x="208" y="87" font-size="14">${label(diagram.radius ? `R=${diagram.radius}` : "R")}</text>
                    </svg><div style="font-size:11px;opacity:.6;margin-top:4px;">${label(diagram.caption || "Đường tròn và bán kính")}</div>
                </div>`;
        }

        if (diagram.type === "coordinate") {
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <line x1="35" y1="150" x2="325" y2="150" stroke="currentColor" stroke-width="2"/>
                        <line x1="65" y1="175" x2="65" y2="20" stroke="currentColor" stroke-width="2"/>
                        <line x1="110" y1="125" x2="250" y2="55" stroke="currentColor" stroke-width="3"/>
                        <circle cx="110" cy="125" r="5" fill="currentColor"/>
                        <circle cx="250" cy="55" r="5" fill="currentColor"/>
                        <text x="98" y="145" font-size="16">${label(diagram.labels?.[0] || "A")}</text>
                        <text x="258" y="50" font-size="16">${label(diagram.labels?.[1] || "B")}</text>
                        <text x="316" y="143" font-size="14">x</text>
                        <text x="72" y="28" font-size="14">y</text>
                    </svg>
                </div>`;
        }

        if (diagram.type === "box") {
            return `
                <div class="mathweb-ai-diagram-wrap">
                    <svg ${common}>
                        <polygon points="95,70 220,70 270,100 145,100" fill="none" stroke="currentColor" stroke-width="3"/>
                        <polygon points="95,70 145,100 145,160 95,130" fill="none" stroke="currentColor" stroke-width="3"/>
                        <polygon points="145,100 270,100 270,160 145,160" fill="none" stroke="currentColor" stroke-width="3"/>
                        <text x="82" y="65" font-size="14">${label(diagram.labels?.[0] || "A")}</text>
                        <text x="224" y="65" font-size="14">${label(diagram.labels?.[1] || "B")}</text>
                        <text x="275" y="98" font-size="14">${label(diagram.labels?.[2] || "C")}</text>
                        <text x="137" y="177" font-size="14">${label(diagram.labels?.[3] || "D")}</text>
                    </svg>
                </div>`;
        }

        return "";
    }

    // Interactive 3D rotation uses the exact coordinates stored with each diagram.
    // It re-renders only the current diagram and never changes question data or answers.
    window.mathwebRotateAIDiagram = function (button, axis, delta) {
        try {
            const wrapper = button && button.closest("[data-mathweb-geometry]");
            if (!wrapper) return;
            const diagram = JSON.parse(wrapper.getAttribute("data-mathweb-geometry"));
            const rotation = { ...(diagram._rotation || { yaw: -28, pitch: 18 }) };
            if (axis === "reset") { rotation.yaw = -28; rotation.pitch = 18; }
            else if (axis === "yaw" || axis === "pitch") rotation[axis] = Math.max(-85, Math.min(85, Number(rotation[axis] || 0) + Number(delta || 0)));
            diagram._rotation = rotation;
            // A rotated wireframe no longer assumes the original front/back view.
            // Keep all edges visible rather than leaving stale hidden-edge markings.
            if (axis !== "reset") diagram.hidden_segments = [];
            const holder = document.createElement("div");
            holder.innerHTML = renderAIDiagram(diagram);
            const next = holder.firstElementChild;
            if (next) wrapper.replaceWith(next);
        } catch (error) {
            console.warn("Không thể xoay hình 3D:", error);
        }
    };


    /* =====================================================
       RENDER ANSWER AREA
       ===================================================== */

    function renderAnswerArea(
        question,
        type,
        options
    ) {

        if (
            type ===
            "multiple_choice"
        ) {

            if (
                !options.length
            ) {

                return `

                    <input
                        id="mathwebAiShortAnswer"
                        class="mathweb-ai-input"
                        type="text"
                        autocomplete="off"
                        placeholder="Nhập đáp án..."
                    >

                    <div class="mathweb-ai-actions">

                        <button
                            type="button"
                            class="mathweb-ai-btn mathweb-ai-btn-primary"
                            id="mathwebAiSubmit"
                        >
                            Trả lời
                        </button>

                    </div>

                `;

            }


            return `

                <div class="mathweb-ai-options">

                    ${options
                        .map(
                            function (option, index) {

                                return `

                                    <button
                                        type="button"
                                        class="mathweb-ai-option"
                                        data-ai-answer="${escapeHTML(
                                            option.value
                                        )}"
                                    >
                                        <strong>
                                            ${String.fromCharCode(
                                                65 + index
                                            )}.
                                        </strong>
                                        ${escapeHTML(
                                            option.label
                                        )}
                                    </button>

                                `;

                            }
                        )
                        .join("")}

                </div>

            `;

        }


        if (
            type ===
            "true_false"
        ) {

            return `

                <div class="mathweb-ai-options">

                    <button
                        type="button"
                        class="mathweb-ai-option"
                        data-ai-answer="true"
                    >
                        ✅ Đúng
                    </button>

                    <button
                        type="button"
                        class="mathweb-ai-option"
                        data-ai-answer="false"
                    >
                        ❌ Sai
                    </button>

                </div>

            `;

        }


        return `

            <textarea
                id="mathwebAiShortAnswer"
                class="mathweb-ai-input"
                rows="2"
                autocomplete="off"
                placeholder="Nhập đáp án của bạn..."
            ></textarea>

            <div class="mathweb-ai-actions">

                <button
                    type="button"
                    class="mathweb-ai-btn mathweb-ai-btn-primary"
                    id="mathwebAiSubmit"
                >
                    ✓ Kiểm tra đáp án
                </button>

            </div>

        `;

    }


    /* =====================================================
       BIND ANSWER EVENTS
       ===================================================== */

    document.addEventListener(
        "click",
        function (event) {

            const target =
                event.target;


            if (
                !(target instanceof HTMLElement)
            ) {
                return;
            }


            const option =
                target.closest(
                    "[data-ai-answer]"
                );


            if (
                option &&
                document.getElementById(
                    "mathwebAiAnswerArea"
                )
            ) {

                const answer =
                    option.getAttribute(
                        "data-ai-answer"
                    );

                submitAIAnswer(
                    answer
                );

            }

        }
    );


    document.addEventListener(
        "click",
        function (event) {

            const target =
                event.target;


            if (
                !(target instanceof HTMLElement)
            ) {
                return;
            }


            if (
                target.id ===
                "mathwebAiSubmit"
            ) {

                const input =
                    document.getElementById(
                        "mathwebAiShortAnswer"
                    );


                submitAIAnswer(
                    input
                        ? input.value
                        : ""
                );

            }

        }
    );


    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key !== "Enter"
            ) {
                return;
            }


            if (
                !aiPracticeOpen ||
                aiAnswered
            ) {
                return;
            }


            const input =
                document.getElementById(
                    "mathwebAiShortAnswer"
                );


            if (
                input &&
                document.activeElement === input
            ) {

                event.preventDefault();

                submitAIAnswer(
                    input.value
                );

            }

        }
    );


    /* =====================================================
       SUBMIT ANSWER
       ===================================================== */

    async function submitAIAnswer(
        answer
    ) {

        if (
            aiAnswered
        ) {
            return;
        }


        const question =
            aiQuestions[
                aiCurrentIndex
            ];


        if (
            !question
        ) {
            return;
        }


        aiAnswered =
            true;


        stopAITimer();


        disableAIAnswerControls();


        const responseTime =
            Math.max(
                0,
                (
                    Date.now() -
                    aiQuestionStartedAt
                ) /
                1000
            );


        const questionId =
            question.id ||
            question.question_id;


        if (
            !questionId
        ) {

            handleLocalAnswerFallback(
                question,
                answer,
                responseTime
            );

            return;

        }


        try {

            const result =
                await apiRequest(
                    AI_API +
                    "/questions/" +
                    encodeURIComponent(
                        String(
                            questionId
                        )
                    ) +
                    "/answer",
                    {
                        method: "POST",
                        body: JSON.stringify({
                            answer:
                                normalizeAnswerForAPI(
                                    answer,
                                    question
                                )
                        })
                    }
                );


            const correct =
                Boolean(
                    result?.correct
                );


            registerAIAnswer(
                correct,
                responseTime
            );


            renderAIFeedback(
                correct,
                result,
                responseTime
            );


        } catch (error) {

            console.error(
                "MATH WEB AI answer:",
                error
            );


            aiAnswered =
                false;


            enableAIAnswerControls();


            renderAIErrorInsideQuestion(
                error?.message ||
                "Không thể chấm đáp án."
            );

        }

    }


    /* =====================================================
       NORMALIZE ANSWER
       ===================================================== */

    function normalizeAnswerForAPI(
        answer,
        question
    ) {

        const type =
            getQuestionType(
                question
            );


        if (
            type ===
            "true_false"
        ) {

            if (
                String(answer).toLowerCase()
                === "true"
            ) {
                return true;
            }

            if (
                String(answer).toLowerCase()
                === "false"
            ) {
                return false;
            }

        }


        return answer;

    }


    /* =====================================================
       LOCAL FALLBACK
       ===================================================== */

    function handleLocalAnswerFallback(
        question,
        answer,
        responseTime
    ) {

        const expected =
            question.answer;


        const correct =
            normalizeCompare(
                answer,
                expected
            );


        registerAIAnswer(
            correct,
            responseTime
        );


        renderAIFeedback(
            correct,
            {
                correct_answer:
                    correct
                        ? null
                        : expected,
                solution:
                    question.solution ||
                    ""
            },
            responseTime
        );

    }


    /* =====================================================
       NORMALIZE COMPARE
       ===================================================== */

    function normalizeCompare(
        a,
        b
    ) {

        const left =
            String(
                a === null ||
                a === undefined
                    ? ""
                    : a
            )
                .trim()
                .toLowerCase()
                .replaceAll(
                    ",",
                    "."
                );

        const right =
            String(
                b === null ||
                b === undefined
                    ? ""
                    : b
            )
                .trim()
                .toLowerCase()
                .replaceAll(
                    ",",
                    "."
                );


        if (
            left === right
        ) {
            return true;
        }


        const leftNumber =
            Number(left);

        const rightNumber =
            Number(right);


        if (
            Number.isFinite(leftNumber) &&
            Number.isFinite(rightNumber)
        ) {

            return Math.abs(
                leftNumber -
                rightNumber
            ) < 0.000001;

        }


        return false;

    }


    /* =====================================================
       REGISTER ANSWER
       ===================================================== */

    function registerAIAnswer(
        correct,
        responseTime
    ) {

        const question =
            aiQuestions[
                aiCurrentIndex
            ];


        const difficulty =
            getQuestionDifficulty(
                question
            );


        if (
            correct
        ) {

            aiCorrect++;

            aiScore +=
                getDifficultyScore(
                    difficulty
                );

        } else {

            aiWrong++;

        }


        aiHistory.push({

            question_id:
                question?.id ||
                null,

            difficulty:
                difficulty,

            correct:
                correct,

            response_time:
                responseTime

        });

    }


    /* =====================================================
       DIFFICULTY SCORE
       ===================================================== */

    function getDifficultyScore(
        difficulty
    ) {

        const scores = {

            easy: 10,

            medium: 15,

            hard: 25,

            expert: 40

        };


        return (
            scores[
                String(
                    difficulty
                ).toLowerCase()
            ] ||
            15
        );

    }


    /* =====================================================
       FEEDBACK
       ===================================================== */

    function renderAIFeedback(
        correct,
        result,
        responseTime
    ) {

        const container =
            document.getElementById(
                "mathwebAiFeedback"
            );


        if (
            !container
        ) {
            return;
        }


        const feedback =
            getFeedback(
                correct,
                result?.feedback
            );


        const solution =
            result?.solution ||
            result?.explanation ||
            "";


        const correctAnswer =
            result?.correct_answer;


        container.innerHTML = `

            <div class="
                mathweb-ai-feedback
                ${
                    correct
                        ? "mathweb-ai-correct"
                        : "mathweb-ai-wrong"
                }
            ">

                <strong>
                    ${escapeHTML(
                        feedback
                    )}
                </strong>

                ${
                    !correct &&
                    correctAnswer !== undefined &&
                    correctAnswer !== null
                        ? `
                            <div style="margin-top:8px;">
                                <strong>
                                    Đáp án:
                                </strong>
                                ${escapeHTML(
                                    formatAnswer(
                                        correctAnswer
                                    )
                                )}
                            </div>
                        `
                        : ""
                }

                ${
                    solution
                        ? `
                            <div class="mathweb-ai-solution">
                                <strong>
                                    💡 Lời giải
                                </strong>
                                <br>
                                ${escapeHTML(
                                    String(
                                        solution
                                    )
                                )}
                            </div>
                        `
                        : ""
                }

                <div
                    style="
                        margin-top:8px;
                        font-size:12px;
                        opacity:.65;
                    "
                >
                    Thời gian:
                    ${responseTime.toFixed(1)}s
                </div>

            </div>


            <div class="mathweb-ai-actions">
                ${correct
                    ? `<div style="font-size:12px;opacity:.7;">✓ Đáp án đúng, đang chuyển câu...</div>`
                    : `<button type="button" class="mathweb-ai-btn mathweb-ai-btn-primary" id="mathwebAiNextAfterWrong">➡️ CÂU TIẾP THEO</button>`}
            </div>

        `;


        const nextAfterWrong = document.getElementById("mathwebAiNextAfterWrong");
        if (nextAfterWrong) {
            nextAfterWrong.addEventListener("click", function () {
                nextAIQuestion();
            });
        }
        if (correct) {
            window.setTimeout(function () {
                if (aiAnswered) nextAIQuestion();
            }, 1200);
        }

    }


    /* =====================================================
       FEEDBACK TEXT
       ===================================================== */

    function getFeedback(
        correct,
        serverFeedback
    ) {

        if (
            typeof serverFeedback ===
                "string" &&
            serverFeedback.trim()
        ) {

            return serverFeedback;

        }


        const correctMessages = [

            "Wow, bạn làm đúng rồi! 🔥",

            "Chuẩn bài! 🎯",

            "Quá tốt! Tiếp tục nào! 🚀",

            "Chính xác! Bạn đang vào guồng rồi! ⚡",

            "Đỉnh! Câu này không làm khó được bạn! 🧠"

        ];


        const wrongMessages = [

            "Oh oh, câu này chưa đúng. Cố lên nhé! 💪",

            "Chưa chính xác rồi, thử lại ở câu tiếp theo nhé! 🌟",

            "Tiếc một chút thôi! Đừng để câu này làm mất phong độ! 🔥",

            "Sai một câu không sao cả. Tiếp tục chiến! 🚀",

            "Chưa đúng, nhưng mình còn rất nhiều cơ hội phía trước! 💙"

        ];


        const messages =
            correct
                ? correctMessages
                : wrongMessages;


        return messages[
            Math.floor(
                Math.random() *
                messages.length
            )
        ];

    }


    /* =====================================================
       FORMAT ANSWER
       ===================================================== */

    function formatAnswer(
        answer
    ) {

        if (
            Array.isArray(answer)
        ) {
            return answer
                .map(
                    function (item) {
                        return String(item);
                    }
                )
                .join(", ");
        }


        if (
            typeof answer === "boolean"
        ) {
            return answer
                ? "Đúng"
                : "Sai";
        }


        if (
            answer &&
            typeof answer === "object"
        ) {
            try {
                return JSON.stringify(
                    answer
                );
            } catch {
                return String(answer);
            }
        }


        return String(
            answer ?? ""
        );

    }


    /* =====================================================
       DISABLE CONTROLS
       ===================================================== */

    function disableAIAnswerControls() {

        const controls =
            document.querySelectorAll(
                "#mathwebAiAnswerArea button, #mathwebAiAnswerArea input, #mathwebAiAnswerArea textarea"
            );


        controls.forEach(
            function (element) {

                if (
                    element instanceof
                    HTMLButtonElement ||
                    element instanceof
                    HTMLInputElement ||
                    element instanceof
                    HTMLTextAreaElement
                ) {

                    element.disabled =
                        true;

                }

            }
        );


        const skip =
            document.getElementById(
                "mathwebAiSkip"
            );


        if (
            skip
        ) {
            skip.disabled =
                true;
        }

    }


    /* =====================================================
       ENABLE CONTROLS
       ===================================================== */

    function enableAIAnswerControls() {

        const controls =
            document.querySelectorAll(
                "#mathwebAiAnswerArea button, #mathwebAiAnswerArea input, #mathwebAiAnswerArea textarea"
            );


        controls.forEach(
            function (element) {

                if (
                    element instanceof
                    HTMLButtonElement ||
                    element instanceof
                    HTMLInputElement ||
                    element instanceof
                    HTMLTextAreaElement
                ) {

                    element.disabled =
                        false;

                }

            }
        );


        const skip =
            document.getElementById(
                "mathwebAiSkip"
            );


        if (
            skip
        ) {
            skip.disabled =
                false;
        }

    }


    /* =====================================================
       NEXT QUESTION
       ===================================================== */

    function nextAIQuestion() {

        aiCurrentIndex++;

        if (
            aiCurrentIndex >=
            aiQuestions.length
        ) {

            finishAIPractice();

            return;

        }


        renderAIQuestion();

    }


    /* =====================================================
       SKIP QUESTION
       ===================================================== */

    function skipAIQuestion() {

        if (
            aiAnswered
        ) {
            return;
        }


        const responseTime =
            Math.max(
                0,
                (
                    Date.now() -
                    aiQuestionStartedAt
                ) /
                1000
            );


        aiSkipped++;

        aiAnswered =
            true;


        stopAITimer();


        const question =
            aiQuestions[
                aiCurrentIndex
            ];


        aiHistory.push({

            question_id:
                question?.id ||
                null,

            difficulty:
                getQuestionDifficulty(
                    question
                ),

            correct:
                false,

            skipped:
                true,

            response_time:
                responseTime

        });


        disableAIAnswerControls();


        const container =
            document.getElementById(
                "mathwebAiFeedback"
            );


        if (
            container
        ) {

            container.innerHTML = `

                <div class="
                    mathweb-ai-feedback
                    mathweb-ai-wrong
                ">

                    <strong>
                        Bỏ qua câu này rồi nhé! 📝
                    </strong>

                    <div
                        style="
                            margin-top:7px;
                            opacity:.8;
                        "
                    >
                        Không sao, hãy tiếp tục câu tiếp theo.
                    </div>

                </div>


                <div class="mathweb-ai-actions">

                    <button
                        type="button"
                        class="mathweb-ai-btn mathweb-ai-btn-primary"
                        id="mathwebAiNext"
                    >
                        Câu tiếp theo →
                    </button>

                </div>

            `;


            document
                .getElementById(
                    "mathwebAiNext"
                )
                ?.addEventListener(
                    "click",
                    nextAIQuestion
                );

        }

    }


    /* =====================================================
       AI TIMER
       ===================================================== */

    function startAITimer() {

        stopAITimer();


        aiQuestionStartedAt =
            Date.now();


        const update =
            function () {

                const element =
                    document.getElementById(
                        "mathwebAiTime"
                    );


                if (
                    !element
                ) {
                    return;
                }


                const seconds =
                    Math.floor(
                        (
                            Date.now() -
                            aiQuestionStartedAt
                        ) /
                        1000
                    );


                element.textContent =
                    "⏱ " +
                    seconds +
                    "s";

            };


        update();


        aiTimer =
            window.setInterval(
                update,
                1000
            );

    }


    function stopAITimer() {

        if (
            aiTimer !== null
        ) {

            clearInterval(
                aiTimer
            );

            aiTimer =
                null;

        }

    }


    /* =====================================================
       FINISH PRACTICE
       ===================================================== */

    function finishAIPractice() {

        stopAITimer();


        const total =
            aiQuestions.length;


        const accuracy =
            total > 0
                ? (
                    aiCorrect /
                    total
                ) *
                100
                : 0;


        const elapsed =
            aiSessionStartedAt
                ? Math.max(
                    0,
                    (
                        Date.now() -
                        aiSessionStartedAt
                    ) /
                    1000
                )
                : 0;


        const overlay =
            createAIOverlay();


        overlay.style.display =
            "flex";


        overlay.innerHTML = `

            <section
                class="mathweb-ai-panel"
                role="dialog"
                aria-modal="true"
            >

                <div class="mathweb-ai-result">

                    <div
                        style="
                            font-size:48px;
                        "
                    >
                        🏆
                    </div>

                    <div class="mathweb-ai-title">
                        Hoàn thành luyện tập!
                    </div>

                    <div class="mathweb-ai-subtitle">
                        Bạn vừa hoàn thành
                        ${total} câu
                        về
                        ${escapeHTML(
                            currentKnowledge?.name ||
                            "Toán học"
                        )}.
                    </div>


                    <div class="mathweb-ai-result-grid">

                        <div class="mathweb-ai-stat">

                            <strong>
                                ${aiCorrect}
                            </strong>

                            <span>
                                Đúng
                            </span>

                        </div>


                        <div class="mathweb-ai-stat">

                            <strong>
                                ${aiWrong}
                            </strong>

                            <span>
                                Sai
                            </span>

                        </div>


                        <div class="mathweb-ai-stat">

                            <strong>
                                ${aiSkipped}
                            </strong>

                            <span>
                                Bỏ qua
                            </span>

                        </div>


                        <div class="mathweb-ai-stat">

                            <strong>
                                ${accuracy.toFixed(0)}%
                            </strong>

                            <span>
                                Chính xác
                            </span>

                        </div>

                    </div>


                    <div
                        style="
                            opacity:.65;
                            font-size:13px;
                        "
                    >
                        Thời gian:
                        ${formatDuration(
                            elapsed
                        )}
                    </div>


                    <div class="mathweb-ai-actions">

                        <button
                            type="button"
                            class="mathweb-ai-btn mathweb-ai-btn-primary"
                            id="mathwebAiAgain"
                        >
                            🔄 Luyện lại
                        </button>

                        <button
                            type="button"
                            class="mathweb-ai-btn"
                            id="mathwebAiFinish"
                        >
                            ✓ Đóng
                        </button>

                    </div>

                </div>

            </section>

        `;


        document
            .getElementById(
                "mathwebAiAgain"
            )
            ?.addEventListener(
                "click",
                function () {

                    aiHistory = [];

                    startAIPractice();

                }
            );


        document
            .getElementById(
                "mathwebAiFinish"
            )
            ?.addEventListener(
                "click",
                function () {

                    closeAIPractice();

                }
            );

    }


    /* =====================================================
       FORMAT DURATION
       ===================================================== */

    function formatDuration(
        seconds
    ) {

        const value =
            Math.max(
                0,
                Math.floor(
                    Number(seconds) || 0
                )
            );


        const minutes =
            Math.floor(
                value / 60
            );


        const remaining =
            value % 60;


        return (
            String(minutes)
                .padStart(2, "0") +
            ":" +
            String(remaining)
                .padStart(2, "0")
        );

    }


    /* =====================================================
       AI ERROR
       ===================================================== */

    function showAIError(
        message
    ) {

        const overlay =
            createAIOverlay();


        overlay.style.display =
            "flex";


        overlay.innerHTML = `

            <section
                class="mathweb-ai-panel"
                role="dialog"
                aria-modal="true"
            >

                <div class="mathweb-ai-title">
                    ⚠️ Không thể bắt đầu
                </div>

                <div class="mathweb-ai-error">
                    ${escapeHTML(
                        message
                    )}
                </div>

                <div class="mathweb-ai-actions">

                    <button
                        type="button"
                        class="mathweb-ai-btn mathweb-ai-btn-primary"
                        id="mathwebAiErrorBack"
                    >
                        ← Quay lại
                    </button>

                </div>

            </section>

        `;


        document
            .getElementById(
                "mathwebAiErrorBack"
            )
            ?.addEventListener(
                "click",
                function () {

                    renderAISetup();

                }
            );

    }


    function renderAIErrorInsideQuestion(
        message
    ) {

        const container =
            document.getElementById(
                "mathwebAiFeedback"
            );


        if (
            !container
        ) {
            return;
        }


        container.innerHTML = `

            <div class="mathweb-ai-error">
                ${escapeHTML(
                    message
                )}
            </div>

        `;

    }


    /* =====================================================
       CLOSE AI PRACTICE
       ===================================================== */

    function closeAIPractice() {

        stopAITimer();


        if (
            aiOverlay
        ) {

            aiOverlay.style.display =
                "none";

            aiOverlay.replaceChildren();

        }


        aiPracticeOpen =
            false;


        resetAIState();

    }


    /* =====================================================
       RESET AI STATE
       ===================================================== */

    function resetAIState() {

        stopAITimer();

        aiQuestions = [];

        aiCurrentIndex = 0;

        aiHistory = [];

        aiScore = 0;

        aiCorrect = 0;

        aiWrong = 0;

        aiSkipped = 0;

        aiAnswered = false;

        aiSessionStartedAt = 0;

        aiQuestionStartedAt = 0;

    }


    /* =====================================================
       AI ESC KEY
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key !==
                "Escape"
            ) {
                return;
            }


            if (
                aiPracticeOpen
            ) {

                event.preventDefault();

                closeAIPractice();

            }

        }
    );


    /* =====================================================
       POPUP CLOSE BUTTON
       ===================================================== */

    if (
        popupClose
    ) {

        popupClose.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();

                closeKnowledge();

            }
        );

    }


    /* =====================================================
       OVERLAY CLICK
       ===================================================== */

    if (
        practiceOverlay
    ) {

        practiceOverlay.addEventListener(
            "click",
            function (event) {

                if (
                    event.target ===
                    practiceOverlay
                ) {

                    closeKnowledge();

                }

            }
        );

    }


    /* =====================================================
       POPUP CLICK PROTECTION
       ===================================================== */

    if (
        knowledgePopup
    ) {

        knowledgePopup.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

            }
        );

    }


    /* =====================================================
       ESC KEY
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key !==
                "Escape"
            ) {
                return;
            }


            if (
                !isPopupOpen ||
                aiPracticeOpen
            ) {
                return;
            }


            event.preventDefault();

            closeKnowledge();

        }
    );


    /* =====================================================
       TAB FOCUS CONTROL
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key !==
                "Tab"
            ) {
                return;
            }


            if (
                !isPopupOpen ||
                aiPracticeOpen ||
                !knowledgePopup
            ) {
                return;
            }


            const focusable =
                knowledgePopup.querySelectorAll(
                    [
                        "button",
                        "[href]",
                        "input",
                        "select",
                        "textarea",
                        "[tabindex]:not([tabindex='-1'])"
                    ].join(",")
                );


            const elements =
                Array.from(
                    focusable
                ).filter(
                    function (element) {

                        return (
                            element instanceof HTMLElement &&
                            !element.hasAttribute(
                                "disabled"
                            ) &&
                            element.offsetParent !== null
                        );

                    }
                );


            if (
                elements.length === 0
            ) {
                return;
            }


            const first =
                elements[0];

            const last =
                elements[
                    elements.length - 1
                ];


            if (
                event.shiftKey &&
                document.activeElement === first
            ) {

                event.preventDefault();

                last.focus();

                return;

            }


            if (
                !event.shiftKey &&
                document.activeElement === last
            ) {

                event.preventDefault();

                first.focus();

            }

        }
    );


    /* =====================================================
       PREVENT BODY SCROLL
       ===================================================== */

    const style =
        document.createElement(
            "style"
        );

    style.setAttribute(
        "data-mathweb-practice-style",
        "true"
    );

    style.textContent = `
        body.popup-open {
            overflow: hidden;
        }
    `;

    document.head.appendChild(
        style
    );


    /* =====================================================
       PUBLIC API
       ===================================================== */

    window.MATHWEB_PRACTICE = {

        data:
            knowledgeData,

        render:
            renderKnowledge,

        open:
            openKnowledge,

        close:
            closeKnowledge,

        launchGame:
            launchGame,

        getCurrentKnowledge:
            function () {
                return currentKnowledge;
            },

        isPopupOpen:
            function () {
                return isPopupOpen;
            },

        openAI:
            openAISetup,

        closeAI:
            closeAIPractice,

        getAIState:
            function () {

                return {

                    open:
                        aiPracticeOpen,

                    current:
                        aiCurrentIndex,

                    total:
                        aiQuestions.length,

                    score:
                        aiScore,

                    correct:
                        aiCorrect,

                    wrong:
                        aiWrong,

                    skipped:
                        aiSkipped

                };

            }

    };


    /* =====================================================
       INITIALIZE
       ===================================================== */

    function initializePractice() {

        if (
            !hasRequiredDOM()
        ) {

            console.error(
                "MATH WEB: practise.js không thể khởi tạo vì DOM chưa đầy đủ."
            );

            return;

        }


        injectAIStyle();


        createAIOverlay();


        renderKnowledge();


        knowledgePopup.classList.remove(
            "active"
        );

        practiceOverlay.classList.remove(
            "active"
        );


        knowledgePopup.setAttribute(
            "aria-hidden",
            "true"
        );

        practiceOverlay.setAttribute(
            "aria-hidden",
            "true"
        );


        document.body.classList.remove(
            "popup-open"
        );

    }


    /* =====================================================
       START
       ===================================================== */

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initializePractice,
            {
                once: true
            }
        );

    } else {

        initializePractice();

    }

})();