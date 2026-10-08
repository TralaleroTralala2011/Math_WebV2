"use strict";

/*
 * =========================================================
 * MATH WEB
 * XÁC SUẤT | BỐC BI
 *
 * File này chỉ chứa dữ liệu câu hỏi.
 * Game logic nằm ở:
 * - game-engine.js
 * - marble.html
 *
 * Tổng:
 * - 15 câu
 * - 5 DỄ
 * - 5 VỪA
 * - 5 KHÓ
 * =========================================================
 */

const MARBLE_QUESTIONS = [

    /* =====================================================
       DỄ
    ====================================================== */

    {
        id: 1,

        code: "marble-easy-001",

        type: "choice",

        difficulty: "easy",

        question:
            "Một hộp có 3 viên bi đỏ và 2 viên bi xanh. Lấy ngẫu nhiên 1 viên. Xác suất lấy được bi đỏ là?",

        options: [
            "2/5",
            "3/5",
            "1/2",
            "3/2"
        ],

        answer: 1,

        explanation:
            "Có 3 viên đỏ trên tổng 5 viên. Vì vậy xác suất lấy được bi đỏ là 3/5."
    },


    {
        id: 2,

        code: "marble-easy-002",

        type: "input",

        difficulty: "easy",

        question:
            "Một hộp có 8 viên bi, trong đó có 2 viên bi đỏ. Xác suất lấy được bi đỏ là bao nhiêu? Nhập phân số tối giản.",

        answer: "1/4",

        explanation:
            "Có 2 viên đỏ trên tổng 8 viên. Ta có 2/8 = 1/4."
    },


    {
        id: 3,

        code: "marble-easy-003",

        type: "choice",

        difficulty: "easy",

        question:
            "Một túi có 1 bi đỏ và 4 bi xanh. Xác suất lấy được bi xanh là?",

        options: [
            "1/5",
            "4/5",
            "1/4",
            "1/2"
        ],

        answer: 1,

        explanation:
            "Có 4 viên xanh trên tổng 5 viên. Xác suất là 4/5."
    },


    {
        id: 4,

        code: "marble-easy-004",

        type: "choice",

        difficulty: "easy",

        question:
            "Một hộp có 6 viên bi gồm 2 đỏ, 1 xanh và 3 vàng. Lấy ngẫu nhiên 1 viên. Xác suất lấy được bi vàng là?",

        options: [
            "1/6",
            "1/3",
            "1/2",
            "2/3"
        ],

        answer: 2,

        explanation:
            "Có 3 viên vàng trên tổng 6 viên. Xác suất là 3/6 = 1/2."
    },


    {
        id: 5,

        code: "marble-easy-005",

        type: "choice",

        difficulty: "easy",

        question:
            "Một túi có 5 bi đỏ và 5 bi xanh. Lấy ngẫu nhiên 1 viên. Xác suất lấy được bi đỏ là?",

        options: [
            "1/5",
            "1/4",
            "1/2",
            "2/3"
        ],

        answer: 2,

        explanation:
            "Có 5 viên đỏ trên tổng 10 viên. Xác suất là 5/10 = 1/2."
    },


    /* =====================================================
       VỪA
    ====================================================== */

    {
        id: 6,

        code: "marble-medium-001",

        type: "choice",

        difficulty: "medium",

        question:
            "Một túi có 4 viên bi đỏ, 3 viên bi xanh và 3 viên bi vàng. Lấy ngẫu nhiên 1 viên. Xác suất lấy được bi không phải màu vàng là?",

        options: [
            "3/10",
            "7/10",
            "4/10",
            "1/2"
        ],

        answer: 1,

        explanation:
            "Có 4 + 3 = 7 viên không phải màu vàng trên tổng 10 viên. Xác suất là 7/10."
    },


    {
        id: 7,

        code: "marble-medium-002",

        type: "choice",

        difficulty: "medium",

        question:
            "Một hộp có 5 bi đỏ và 5 bi xanh. Lấy 2 viên liên tiếp không hoàn lại. Xác suất cả hai đều là bi đỏ là?",

        options: [
            "1/4",
            "2/5",
            "2/9",
            "1/2"
        ],

        answer: 2,

        explanation:
            "Lần đầu lấy đỏ có xác suất 5/10. Sau đó còn 4 bi đỏ trên 9 viên nên xác suất là 4/9. Do đó P = 5/10 × 4/9 = 2/9."
    },


    {
        id: 8,

        code: "marble-medium-003",

        type: "choice",

        difficulty: "medium",

        question:
            "Một túi có 2 bi đỏ, 3 bi xanh và 5 bi vàng. Xác suất lấy được bi đỏ hoặc xanh là?",

        options: [
            "1/5",
            "1/2",
            "3/5",
            "2/3"
        ],

        answer: 1,

        explanation:
            "Có 2 + 3 = 5 viên đỏ hoặc xanh trên tổng 10 viên. Xác suất là 5/10 = 1/2."
    },


    {
        id: 9,

        code: "marble-medium-004",

        type: "choice",

        difficulty: "medium",

        question:
            "Một hộp có 8 viên bi gồm 3 đỏ và 5 xanh. Lấy 2 viên không hoàn lại. Xác suất lấy được hai viên khác màu là?",

        options: [
            "15/28",
            "3/8",
            "5/14",
            "1/2"
        ],

        answer: 0,

        explanation:
            "Có hai trường hợp: đỏ rồi xanh hoặc xanh rồi đỏ. P = 3/8 × 5/7 + 5/8 × 3/7 = 30/56 = 15/28."
    },


    {
        id: 10,

        code: "marble-medium-005",

        type: "input",

        difficulty: "medium",

        question:
            "Một túi có 12 viên bi, trong đó có 9 viên không phải màu đỏ. Xác suất lấy được bi đỏ là bao nhiêu? Nhập phân số tối giản.",

        answer: "1/4",

        explanation:
            "Có 12 - 9 = 3 viên đỏ. Xác suất là 3/12 = 1/4."
    },


    /* =====================================================
       KHÓ
    ====================================================== */

    {
        id: 11,

        code: "marble-hard-001",

        type: "choice",

        difficulty: "hard",

        question:
            "Một hộp có 6 bi đỏ và 4 bi xanh. Lấy 2 viên không hoàn lại. Xác suất lấy được đúng 1 viên đỏ là?",

        options: [
            "4/15",
            "8/15",
            "1/2",
            "2/5"
        ],

        answer: 1,

        explanation:
            "Có hai trường hợp: đỏ-xanh hoặc xanh-đỏ. P = 6/10 × 4/9 + 4/10 × 6/9 = 48/90 = 8/15."
    },


    {
        id: 12,

        code: "marble-hard-002",

        type: "input",

        difficulty: "hard",

        question:
            "Một hộp có 5 bi đỏ và 7 bi xanh. Lấy đồng thời 2 viên. Xác suất cả hai đều xanh là bao nhiêu? Nhập phân số tối giản.",

        answer: "7/22",

        explanation:
            "Có C(7,2) cách chọn 2 bi xanh và C(12,2) cách chọn 2 viên bất kỳ. P = C(7,2)/C(12,2) = 21/66 = 7/22."
    },


    {
        id: 13,

        code: "marble-hard-003",

        type: "choice",

        difficulty: "hard",

        question:
            "Một hộp có 4 bi đỏ và 6 bi xanh. Lấy 3 viên không hoàn lại. Xác suất cả 3 viên đều đỏ là?",

        options: [
            "1/30",
            "2/15",
            "1/10",
            "1/20"
        ],

        answer: 0,

        explanation:
            "P = 4/10 × 3/9 × 2/8 = 24/720 = 1/30."
    },


    {
        id: 14,

        code: "marble-hard-004",

        type: "choice",

        difficulty: "hard",

        question:
            "Một hộp có 5 bi đỏ và 5 bi xanh. Lấy 3 viên không hoàn lại. Xác suất có ít nhất 1 viên đỏ là?",

        options: [
            "1/2",
            "11/12",
            "5/6",
            "3/4"
        ],

        answer: 1,

        explanation:
            "Dùng biến cố đối. Xác suất cả 3 viên đều xanh là 5/10 × 4/9 × 3/8 = 1/12. Vì vậy xác suất có ít nhất 1 viên đỏ là 1 - 1/12 = 11/12."
    },


    {
        id: 15,

        code: "marble-hard-005",

        type: "input",

        difficulty: "hard",

        question:
            "Một hộp có 4 bi đỏ, 3 bi xanh và 3 bi vàng. Lấy đồng thời 2 viên. Xác suất hai viên cùng màu là bao nhiêu? Nhập phân số tối giản.",

        answer: "4/15",

        explanation:
            "Số cách chọn hai viên cùng màu là C(4,2) + C(3,2) + C(3,2) = 6 + 3 + 3 = 12. Tổng số cách chọn 2 viên là C(10,2) = 45. Xác suất là 12/45 = 4/15."
    }

];


/* =========================================================
   VALIDATION
========================================================= */

function validateMarbleQuestions() {

    if (
        !Array.isArray(
            MARBLE_QUESTIONS
        )
    ) {
        return false;
    }


    if (
        MARBLE_QUESTIONS.length !== 15
    ) {
        return false;
    }


    const ids =
        new Set();


    const codes =
        new Set();


    for (
        const question
        of MARBLE_QUESTIONS
    ) {

        if (
            !question ||
            typeof question !== "object"
        ) {
            return false;
        }


        if (
            !Number.isInteger(
                question.id
            )
        ) {
            return false;
        }


        if (
            ids.has(
                question.id
            )
        ) {
            return false;
        }


        ids.add(
            question.id
        );


        if (
            typeof question.code !==
            "string" ||
            !question.code.trim()
        ) {
            return false;
        }


        if (
            codes.has(
                question.code
            )
        ) {
            return false;
        }


        codes.add(
            question.code
        );


        if (
            ![
                "easy",
                "medium",
                "hard"
            ].includes(
                question.difficulty
            )
        ) {
            return false;
        }


        if (
            ![
                "choice",
                "input"
            ].includes(
                question.type
            )
        ) {
            return false;
        }


        if (
            typeof question.question !==
            "string" ||
            !question.question.trim()
        ) {
            return false;
        }


        if (
            typeof question.explanation !==
            "string" ||
            !question.explanation.trim()
        ) {
            return false;
        }


        if (
            question.type ===
            "choice"
        ) {

            if (
                !Array.isArray(
                    question.options
                ) ||
                question.options.length <
                    2
            ) {
                return false;
            }


            if (
                !Number.isInteger(
                    question.answer
                )
            ) {
                return false;
            }


            if (
                question.answer < 0 ||
                question.answer >=
                    question.options.length
            ) {
                return false;
            }

        }


        if (
            question.type ===
            "input"
        ) {

            if (
                typeof question.answer !==
                    "string" &&
                typeof question.answer !==
                    "number"
            ) {
                return false;
            }

        }

    }


    return true;
}


/* =========================================================
   STATISTICS
========================================================= */

function getMarbleQuestionStatistics() {

    const statistics = {

        total: MARBLE_QUESTIONS.length,

        easy: 0,

        medium: 0,

        hard: 0,

        choice: 0,

        input: 0

    };


    MARBLE_QUESTIONS.forEach(
        function(question) {

            if (
                question.difficulty ===
                "easy"
            ) {
                statistics.easy++;
            }


            if (
                question.difficulty ===
                "medium"
            ) {
                statistics.medium++;
            }


            if (
                question.difficulty ===
                "hard"
            ) {
                statistics.hard++;
            }


            if (
                question.type ===
                "choice"
            ) {
                statistics.choice++;
            }


            if (
                question.type ===
                "input"
            ) {
                statistics.input++;
            }

        }
    );


    return statistics;
}


/* =========================================================
   PUBLIC DATA
========================================================= */

if (
    typeof window !==
    "undefined"
) {

    window.MARBLE_QUESTIONS =
        MARBLE_QUESTIONS;


    window.MATHWEB_MARBLE_QUESTIONS =
        MARBLE_QUESTIONS;


    window.validateMarbleQuestions =
        validateMarbleQuestions;


    window.getMarbleQuestionStatistics =
        getMarbleQuestionStatistics;

}