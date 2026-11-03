(function () {
    "use strict";


    /*
     * ============================================================
     * MATH GAME ENGINE
     * ============================================================
     *
     * Chịu trách nhiệm:
     *
     * - Quản lý câu hỏi
     * - Quản lý lượt chơi
     * - Kiểm tra đáp án
     * - Tính điểm
     * - Tính XP
     * - Thống kê đúng / sai / bỏ qua
     * - Tính thời gian
     * - Trộn câu hỏi
     * - Lưu kết quả thông qua saveGameResult()
     *
     * Không phụ thuộc trực tiếp vào giao diện.
     * ============================================================
     */


    class MathGameEngine {

        constructor(options = {}) {

            this.questions =
                Array.isArray(options.questions)
                    ? options.questions
                    : [];

            this.gameName =
                typeof options.gameName === "string" &&
                options.gameName.trim()
                    ? options.gameName.trim()
                    : "Math Game";

            this.topicName =
                typeof options.topicName === "string" &&
                options.topicName.trim()
                    ? options.topicName.trim()
                    : "Toán học";


            /*
             * =========================
             * CALLBACKS
             * =========================
             */

            this.onQuestionChange =
                typeof options.onQuestionChange === "function"
                    ? options.onQuestionChange
                    : function () {};

            this.onAnswer =
                typeof options.onAnswer === "function"
                    ? options.onAnswer
                    : function () {};

            this.onFinish =
                typeof options.onFinish === "function"
                    ? options.onFinish
                    : function () {};


            /*
             * =========================
             * CẤU HÌNH
             * =========================
             */

            this.autoFinish =
                options.autoFinish !== false;

            this.shuffle =
                options.shuffle !== false;


            /*
             * =========================
             * TRẠNG THÁI GAME
             * =========================
             */

            this.currentIndex = 0;

            this.score = 0;

            this.xp = 0;

            this.correct = 0;

            this.wrong = 0;

            this.blank = 0;

            this.startTime = null;

            this.endTime = null;

            this.answered = false;

            this.started = false;

            this.finished = false;

            this.isFinishing = false;

            this.lastAnswerResult = null;

            this.lastQuestion = null;

            this._finishPromise = null;
        }


        /*
         * ========================================================
         * START GAME
         * ========================================================
         */

        start() {

            /*
             * Reset toàn bộ trạng thái
             */

            this.currentIndex = 0;

            this.score = 0;

            this.xp = 0;

            this.correct = 0;

            this.wrong = 0;

            this.blank = 0;

            this.startTime = Date.now();

            this.endTime = null;

            this.answered = false;

            this.started = true;

            this.finished = false;

            this.isFinishing = false;

            this.lastAnswerResult = null;

            this.lastQuestion = null;

            this._finishPromise = null;


            /*
             * Không có câu hỏi
             */

            if (this.questions.length === 0) {

                if (this.autoFinish) {
                    return this.finish();
                }

                return null;
            }


            /*
             * Trộn câu hỏi nếu được bật
             */

            if (this.shuffle) {

                this.questions =
                    shuffleQuestions(
                        this.questions
                    );
            }


            this.showQuestion();

            return this.getState();
        }


        /*
         * ========================================================
         * CURRENT QUESTION
         * ========================================================
         */

        getCurrentQuestion() {

            if (
                this.currentIndex < 0 ||
                this.currentIndex >= this.questions.length
            ) {

                return null;
            }

            return this.questions[
                this.currentIndex
            ];
        }


        /*
         * ========================================================
         * SHOW QUESTION
         * ========================================================
         */

        showQuestion() {

            if (this.finished) {
                return null;
            }


            if (
                this.currentIndex >=
                this.questions.length
            ) {

                if (this.autoFinish) {
                    return this.finish();
                }

                return null;
            }


            this.answered = false;

            const question =
                this.getCurrentQuestion();

            this.lastQuestion =
                question;


            this.onQuestionChange(
                question,
                this.currentIndex,
                this.questions.length
            );

            return question;
        }


        /*
         * ========================================================
         * ANSWER
         * ========================================================
         */

        answer(answer) {

            /*
             * Không cho trả lời khi:
             *
             * - Game chưa bắt đầu
             * - Game đã kết thúc
             * - Câu hiện tại đã được trả lời
             */

            if (!this.started) {
                return null;
            }

            if (this.finished) {
                return null;
            }

            if (this.answered) {
                return null;
            }


            const question =
                this.getCurrentQuestion();


            if (!question) {
                return null;
            }


            this.answered = true;


            const result =
                this.checkAnswer(
                    question,
                    answer
                );


            /*
             * =========================
             * ĐÚNG
             * =========================
             */

            if (result.correct) {

                this.correct++;


                const points =
                    this.getPoints(
                        question.difficulty
                    );


                const xp =
                    this.getXP(
                        question.difficulty
                    );


                this.score += points;

                this.xp += xp;

                result.points = points;

                result.xp = xp;
            }


            /*
             * =========================
             * SAI
             * =========================
             */

            else {

                this.wrong++;

                result.points = 0;

                result.xp = 0;
            }


            this.lastAnswerResult =
                result;


            this.onAnswer(
                result,
                question,
                this.currentIndex,
                this.questions.length
            );


            return result;
        }


        /*
         * ========================================================
         * SKIP QUESTION
         * ========================================================
         */

        skip() {

            if (!this.started) {
                return null;
            }

            if (this.finished) {
                return null;
            }

            if (this.answered) {
                return null;
            }


            const question =
                this.getCurrentQuestion();


            if (!question) {
                return null;
            }


            this.answered = true;

            this.blank++;


            const result = {

                correct: false,

                blank: true,

                points: 0,

                xp: 0,

                message:
                    "Bạn đã bỏ qua câu này."
            };


            this.lastAnswerResult =
                result;


            this.onAnswer(
                result,
                question,
                this.currentIndex,
                this.questions.length
            );


            return result;
        }


        /*
         * ========================================================
         * NEXT QUESTION
         * ========================================================
         */

        next() {

            if (!this.started) {
                return null;
            }

            if (this.finished) {
                return null;
            }


            /*
             * Không cho chuyển câu khi
             * câu hiện tại chưa được xử lý.
             */

            if (!this.answered) {
                return null;
            }


            this.currentIndex++;

            return this.showQuestion();
        }


        /*
         * ========================================================
         * CHECK ANSWER
         * ========================================================
         */

        checkAnswer(
            question,
            answer
        ) {

            if (!question) {

                return {

                    correct: false,

                    blank: false,

                    message:
                        "Không tìm thấy câu hỏi."
                };
            }


            /*
             * =========================
             * CÂU TRẮC NGHIỆM
             * =========================
             */

            if (
                question.type ===
                "choice"
            ) {

                const isCorrect =
                    this.compareChoiceAnswer(
                        answer,
                        question.answer
                    );


                return {

                    correct:
                        isCorrect,

                    blank: false,

                    message:
                        isCorrect
                            ? "Chính xác!"
                            : "Chưa đúng rồi!"
                };
            }


            /*
             * =========================
             * CÂU NHẬP ĐÁP ÁN
             * =========================
             */

            if (
                question.type ===
                "input"
            ) {

                const isCorrect =
                    this.compareInputAnswer(
                        answer,
                        question.answer
                    );


                return {

                    correct:
                        isCorrect,

                    blank: false,

                    message:
                        isCorrect
                            ? "Chính xác!"
                            : "Chưa đúng rồi!"
                };
            }


            /*
             * =========================
             * BOOLEAN
             * =========================
             */

            if (
                question.type ===
                "boolean"
            ) {

                const userAnswer =
                    String(answer)
                        .trim()
                        .toLowerCase();


                const correctAnswer =
                    String(question.answer)
                        .trim()
                        .toLowerCase();


                const isCorrect =
                    userAnswer ===
                    correctAnswer;


                return {

                    correct:
                        isCorrect,

                    blank: false,

                    message:
                        isCorrect
                            ? "Chính xác!"
                            : "Chưa đúng rồi!"
                };
            }


            /*
             * =========================
             * LOẠI KHÔNG HỖ TRỢ
             * =========================
             */

            return {

                correct: false,

                blank: false,

                message:
                    "Không xác định được loại câu hỏi."
            };
        }


        /*
         * ========================================================
         * SO SÁNH TRẮC NGHIỆM
         * ========================================================
         */

        compareChoiceAnswer(
            userAnswer,
            correctAnswer
        ) {

            if (
                userAnswer === null ||
                userAnswer === undefined
            ) {

                return false;
            }


            /*
             * Nếu cả hai là số
             */

            const userNumber =
                Number(userAnswer);

            const correctNumber =
                Number(correctAnswer);


            if (
                Number.isFinite(userNumber) &&
                Number.isFinite(correctNumber)
            ) {

                return (
                    userNumber ===
                    correctNumber
                );
            }


            /*
             * Nếu là text
             */

            return (
                String(userAnswer)
                    .trim()
                    .toLowerCase()
                ===
                String(correctAnswer)
                    .trim()
                    .toLowerCase()
            );
        }


        /*
         * ========================================================
         * SO SÁNH INPUT
         * ========================================================
         */

        compareInputAnswer(
            userAnswer,
            correctAnswer
        ) {

            if (
                userAnswer === null ||
                userAnswer === undefined
            ) {

                return false;
            }


            const user =
                normalizeMathAnswer(
                    userAnswer
                );

            const correct =
                normalizeMathAnswer(
                    correctAnswer
                );


            return user === correct;
        }


        /*
         * ========================================================
         * POINTS
         * ========================================================
         */

        getPoints(difficulty) {

            switch (difficulty) {

                case "easy":
                    return 10;

                case "medium":
                    return 20;

                case "hard":
                    return 30;

                default:
                    return 10;
            }
        }


        /*
         * ========================================================
         * XP
         * ========================================================
         */

        getXP(difficulty) {

            switch (difficulty) {

                case "easy":
                    return 5;

                case "medium":
                    return 10;

                case "hard":
                    return 15;

                default:
                    return 5;
            }
        }


        /*
         * ========================================================
         * CURRENT TIME
         * ========================================================
         */

        getElapsedTime() {

            if (!this.startTime) {
                return 0;
            }


            const end =
                this.endTime ||
                Date.now();


            return Math.max(
                0,
                Math.floor(
                    (
                        end -
                        this.startTime
                    ) / 1000
                )
            );
        }


        /*
         * ========================================================
         * FINISH
         * ========================================================
         */

        async finish() {

            /*
             * Nếu đã finish trước đó,
             * trả lại promise cũ để tránh lưu
             * kết quả nhiều lần.
             */

            if (this._finishPromise) {
                return this._finishPromise;
            }


            this._finishPromise =
                this._finishInternal();


            return this._finishPromise;
        }


        /*
         * ========================================================
         * INTERNAL FINISH
         * ========================================================
         */

        async _finishInternal() {

            if (this.finished) {
                return null;
            }


            this.isFinishing = true;


            this.endTime =
                Date.now();


            const totalTime =
                this.getElapsedTime();


            this.finished = true;


            const result = {

                gameName:
                    this.gameName,

                topicName:
                    this.topicName,

                total:
                    this.questions.length,

                correct:
                    this.correct,

                wrong:
                    this.wrong,

                blank:
                    this.blank,

                score:
                    this.score,

                xp:
                    this.xp,

                time:
                    totalTime,

                accuracy:
                    this.getAccuracy(),

                completed:
                    this.questions.length > 0
                        ? (
                            this.correct +
                            this.wrong +
                            this.blank
                        ) >=
                        this.questions.length
                        : true
            };


            let saveResult =
                null;


            /*
             * ====================================================
             * LƯU KẾT QUẢ
             * ====================================================
             *
             * Nếu project có saveGameResult():
             *
             * - Có đăng nhập
             *   → có thể lưu server
             *
             * - Chưa đăng nhập
             *   → saveGameResult có thể xử lý localStorage
             *
             * Engine không tự giả định cách lưu.
             * ====================================================
             */

            try {

                if (
                    typeof window !== "undefined" &&
                    typeof window.saveGameResult ===
                    "function"
                ) {

                    saveResult =
                        await window.saveGameResult(
                            result
                        );
                }

                else if (
                    typeof saveGameResult ===
                    "function"
                ) {

                    saveResult =
                        await saveGameResult(
                            result
                        );
                }

            }

            catch (error) {

                console.error(
                    "Không thể lưu kết quả game:",
                    error
                );


                saveResult = {

                    success: false,

                    error:
                        error instanceof Error
                            ? error.message
                            : "Không thể lưu kết quả."
                };
            }


            this.isFinishing = false;


            /*
             * Callback hoàn thành
             */

            this.onFinish(
                result,
                saveResult
            );


            return {

                result,
                saveResult
            };
        }


        /*
         * ========================================================
         * ACCURACY
         * ========================================================
         */

        getAccuracy() {

            if (
                this.questions.length === 0
            ) {

                return 0;
            }


            return Number(
                (
                    this.correct /
                    this.questions.length *
                    100
                ).toFixed(2)
            );
        }


        /*
         * ========================================================
         * PROGRESS
         * ========================================================
         */

        getProgress() {

            if (
                this.questions.length === 0
            ) {

                return 0;
            }


            return Math.min(
                100,
                Number(
                    (
                        (
                            this.currentIndex
                        ) /
                        this.questions.length *
                        100
                    ).toFixed(2)
                )
            );
        }


        /*
         * ========================================================
         * GAME STATE
         * ========================================================
         */

        getState() {

            return {

                currentIndex:
                    this.currentIndex,

                total:
                    this.questions.length,

                score:
                    this.score,

                xp:
                    this.xp,

                correct:
                    this.correct,

                wrong:
                    this.wrong,

                blank:
                    this.blank,

                answered:
                    this.answered,

                started:
                    this.started,

                finished:
                    this.finished,

                isFinishing:
                    this.isFinishing,

                elapsedTime:
                    this.getElapsedTime(),

                accuracy:
                    this.getAccuracy(),

                progress:
                    this.getProgress(),

                currentQuestion:
                    this.getCurrentQuestion()
            };
        }


        /*
         * ========================================================
         * RESET
         * ========================================================
         */

        reset() {

            this.currentIndex = 0;

            this.score = 0;

            this.xp = 0;

            this.correct = 0;

            this.wrong = 0;

            this.blank = 0;

            this.startTime = null;

            this.endTime = null;

            this.answered = false;

            this.started = false;

            this.finished = false;

            this.isFinishing = false;

            this.lastAnswerResult = null;

            this.lastQuestion = null;

            this._finishPromise = null;

            return this.getState();
        }
    }


    /*
     * ============================================================
     * NORMALIZE MATH ANSWER
     * ============================================================
     *
     * Chuẩn hóa nhẹ:
     *
     *  "  12  " → "12"
     *  "12  3"  → "123"
     *
     * Không tự biến đổi biểu thức toán học phức tạp.
     */

    function normalizeMathAnswer(answer) {

        if (
            answer === null ||
            answer === undefined
        ) {

            return "";
        }


        return String(answer)
            .trim()
            .replace(/\s+/g, "")
            .toLowerCase();
    }


    /*
     * ============================================================
     * SHUFFLE ARRAY
     * ============================================================
     */

    function shuffleArray(array) {

        if (!Array.isArray(array)) {
            return [];
        }


        const result =
            [...array];


        /*
         * Fisher-Yates Shuffle
         */

        for (
            let i =
                result.length - 1;

            i > 0;

            i--
        ) {

            const j =
                Math.floor(
                    Math.random() *
                    (i + 1)
                );


            const temp =
                result[i];

            result[i] =
                result[j];

            result[j] =
                temp;
        }


        return result;
    }


    /*
     * ============================================================
     * SHUFFLE QUESTIONS
     * ============================================================
     */

    function shuffleQuestions(
        questions
    ) {

        if (!Array.isArray(questions)) {
            return [];
        }


        return shuffleArray(
            questions
        );
    }


    /*
     * ============================================================
     * FORMAT TIME
     * ============================================================
     */

    function formatTime(seconds) {

        const safeSeconds =
            Math.max(
                0,
                Number.isFinite(
                    Number(seconds)
                )
                    ? Math.floor(
                        Number(seconds)
                    )
                    : 0
            );


        const minutes =
            Math.floor(
                safeSeconds / 60
            );


        const remainingSeconds =
            safeSeconds % 60;


        return (

            String(minutes)
                .padStart(2, "0")

            +

            ":"

            +

            String(
                remainingSeconds
            ).padStart(2, "0")
        );
    }


    /*
     * ============================================================
     * GLOBAL EXPORT
     * ============================================================
     */

    if (
        typeof window !== "undefined"
    ) {

        window.MathGameEngine =
            MathGameEngine;

        window.shuffleArray =
            shuffleArray;

        window.shuffleQuestions =
            shuffleQuestions;

        window.formatTime =
            formatTime;

        window.normalizeMathAnswer =
            normalizeMathAnswer;
    }


})();