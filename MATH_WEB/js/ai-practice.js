/* =========================================================
   MATH WEB - AI PRACTICE
   File: frontend/js/ai-practice.js

   AI chạy trực tiếp bên trong:
   #knowledgePopup .popup-container

   KHÔNG tạo popup thứ hai.
   KHÔNG tạo overlay.
   KHÔNG tạo nút X thứ hai.

   AI sẽ thay thế nội dung bên trong popup hiện tại.
   ========================================================= */

(() => {
    "use strict";

    /* =====================================================
       CONFIG
       ===================================================== */

    const CONFIG = {
        API_BASE:
            window.MATHWEB_API_BASE ||
            "http://127.0.0.1:8000",

        REQUEST_TIMEOUT: 30000,

        DEFAULT_GRADE: 10,
        DEFAULT_COUNT: 10,

        MIN_COUNT: 1,
        MAX_COUNT: 30,

        LEVELS: {
            easy: "Dễ",
            medium: "Vừa",
            hard: "Khó",
            expert: "Chuyên"
        },

        QUESTION_TYPES: {
            multiple_choice: "Trắc nghiệm",
            true_false: "Đúng / Sai",
            short_answer: "Tự luận ngắn"
        }
    };


    /* =====================================================
       STATE
       ===================================================== */

    const state = {
        active: false,
        mode: "form",

        grade: CONFIG.DEFAULT_GRADE,

        topics: [],
        selectedTopics: [],

        count: CONFIG.DEFAULT_COUNT,
        difficulty: "medium",
        questionType: "multiple_choice",

        questions: [],
        currentIndex: 0,

        answers: {},
        results: {},

        score: 0,
        correct: 0,
        wrong: 0,
        skipped: 0,

        startedAt: 0,
        finishedAt: 0,

        generating: false,
        submitting: false,

        knowledgeLoaded: false,

        lastSetId: null,

        answerRevealed: false,

        popup: null,
        popupContainer: null,
        aiView: null,

        originalChildren: [],
        originalDisplay: new Map(),

        currentTopicName: "",
        currentTopicId: ""
    };


    /* =====================================================
       INIT
       ===================================================== */

    function init() {
        injectStyles();
        bindGlobalEvents();

        window.MATHWEB_AI_PRACTICE = {
            open: openForm,
            close,
            reset: resetState
        };
    }


    /* =====================================================
       GLOBAL EVENTS
       ===================================================== */

    function bindGlobalEvents() {

        /*
         * QUAN TRỌNG:
         *
         * AI button nằm trong .game-button.
         * practise.js có thể cũng đang bắt click của
         * .game-button.
         *
         * Vì vậy phải bắt ở CAPTURE PHASE trước khi
         * event tới practise.js.
         */
        document.addEventListener(
            "click",
            event => {
                const button =
                    event.target.closest(
                        ".mathweb-ai-practice-button"
                    );

                if (!button) {
                    return;
                }

                /*
                 * Chặn toàn bộ handler khác xử lý nút này.
                 */
                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();

                openForm();
            },
            true
        );


        /*
         * Xử lý nút X gốc.
         *
         * Không tạo X mới.
         */
        document.addEventListener(
            "click",
            event => {
                if (!state.active) {
                    return;
                }

                const closeButton =
                    event.target.closest(
                        "#popupClose"
                    );

                if (!closeButton) {
                    return;
                }

                /*
                 * Chỉ khôi phục popup.
                 * Không ngăn handler gốc của practise.js.
                 */
                exitAI();

            },
            true
        );


        /*
         * Escape:
         *
         * Đang ở AI -> quay về popup gốc.
         */
        document.addEventListener(
            "keydown",
            event => {
                if (!state.active) {
                    return;
                }

                if (event.key !== "Escape") {
                    return;
                }

                event.preventDefault();
                event.stopPropagation();

                exitAI();
            },
            true
        );
    }


    /* =====================================================
       FIND POPUP
       ===================================================== */

    function getKnowledgePopup() {
        return (
            document.getElementById(
                "knowledgePopup"
            ) ||
            document.querySelector(
                ".knowledge-popup"
            )
        );
    }


    function getPopupContainer() {
        const popup =
            getKnowledgePopup();

        if (!popup) {
            return null;
        }

        return (
            popup.querySelector(
                ".popup-container"
            ) ||
            null
        );
    }


    /* =====================================================
       OPEN
       ===================================================== */

    async function openForm() {

        const popup =
            getKnowledgePopup();

        const container =
            getPopupContainer();

        if (!popup || !container) {
            console.error(
                "MATH WEB AI: Không tìm thấy #knowledgePopup .popup-container"
            );

            return;
        }


        state.popup = popup;
        state.popupContainer = container;

        /*
         * Đảm bảo popup vẫn đang mở.
         */
        popup.classList.add("active");
        popup.setAttribute(
            "aria-hidden",
            "false"
        );


        state.active = true;
        state.mode = "form";

        resetQuestionState();

        /*
         * Đọc topic trước khi thay nội dung.
         */
        readCurrentTopic();

        /*
         * Tạo / lấy AI view.
         */
        prepareAIView();

        /*
         * Ẩn nội dung cũ.
         */
        showAIView();

        /*
         * Hiện form.
         */
        renderForm();


        /*
         * Tải kiến thức nếu chưa có.
         */
        if (!state.knowledgeLoaded) {
            await loadKnowledge();
        }


        if (!state.active) {
            return;
        }

        selectCurrentTopicIfPossible();
    }


    /* =====================================================
       PREPARE AI VIEW
       ===================================================== */

    function prepareAIView() {

        const container =
            state.popupContainer;

        if (!container) {
            return;
        }


        /*
         * Lấy AI view cũ nếu đã tồn tại.
         */
        let aiView =
            container.querySelector(
                ":scope > .mw-ai-view"
            );


        /*
         * Nếu chưa có thì tạo đúng MỘT div.
         *
         * Đây KHÔNG phải popup.
         * Nó chỉ là phần nội dung AI bên trong
         * popup hiện tại.
         */
        if (!aiView) {
            aiView =
                document.createElement(
                    "div"
                );

            aiView.id =
                "mwAiView";

            aiView.className =
                "mw-ai-view";

            container.appendChild(
                aiView
            );
        }


        state.aiView = aiView;


        /*
         * Chỉ chụp các phần tử gốc.
         *
         * Không bao gồm AI view.
         */
        state.originalChildren =
            Array.from(
                container.children
            ).filter(
                element =>
                    element !== aiView
            );


        state.originalDisplay =
            new Map();


        state.originalChildren.forEach(
            element => {
                state.originalDisplay.set(
                    element,
                    {
                        display:
                            element.style.display,
                        visibility:
                            element.style.visibility,
                        hidden:
                            element.hidden
                    }
                );
            }
        );
    }


    /* =====================================================
       SHOW AI VIEW
       ===================================================== */

    function showAIView() {

        const container =
            state.popupContainer;

        const aiView =
            state.aiView;

        if (!container || !aiView) {
            return;
        }


        /*
         * Ẩn toàn bộ nội dung gốc.
         *
         * GIỮ nguyên popupClose.
         */
        state.originalChildren.forEach(
            element => {

                if (!element) {
                    return;
                }

                if (
                    element.id ===
                    "popupClose"
                ) {
                    return;
                }

                if (
                    element.classList.contains(
                        "popup-close"
                    )
                ) {
                    return;
                }

                element.style.display =
                    "none";
            }
        );


        /*
         * AI chỉ là content trong popup.
         */
        aiView.style.display =
            "block";
    }


    /* =====================================================
       EXIT AI
       ===================================================== */

    function exitAI() {

        const container =
            state.popupContainer;

        const aiView =
            state.aiView;


        /*
         * Không có popup thì chỉ reset state.
         */
        if (!container) {
            state.active = false;
            return;
        }


        /*
         * Ẩn AI.
         */
        if (aiView) {
            aiView.innerHTML = "";
            aiView.style.display =
                "none";
        }


        /*
         * Khôi phục toàn bộ nội dung cũ.
         */
        state.originalChildren.forEach(
            element => {

                if (!element) {
                    return;
                }

                const original =
                    state.originalDisplay.get(
                        element
                    );

                if (!original) {
                    element.style.display =
                        "";
                    element.style.visibility =
                        "";
                    element.hidden = false;
                    return;
                }

                element.style.display =
                    original.display;

                element.style.visibility =
                    original.visibility;

                element.hidden =
                    original.hidden;
            }
        );


        state.active = false;
        state.mode = "form";

        resetQuestionState();
    }


    /* =====================================================
       CLOSE
       ===================================================== */

    function close() {
        exitAI();
    }


    /* =====================================================
       RESET
       ===================================================== */

    function resetState() {

        resetQuestionState();

        state.topics = [];
        state.selectedTopics = [];

        state.knowledgeLoaded = false;

        state.currentTopicName = "";
        state.currentTopicId = "";
    }


    function resetQuestionState() {

        state.questions = [];
        state.currentIndex = 0;

        state.answers = {};
        state.results = {};

        state.score = 0;
        state.correct = 0;
        state.wrong = 0;
        state.skipped = 0;

        state.startedAt = 0;
        state.finishedAt = 0;

        state.generating = false;
        state.submitting = false;

        state.lastSetId = null;

        state.answerRevealed = false;
    }


    /* =====================================================
       CURRENT TOPIC
       ===================================================== */

    function readCurrentTopic() {

        const topicElement =
            document.getElementById(
                "popupTopic"
            );

        const titleElement =
            document.getElementById(
                "popupTitle"
            );


        const topic =
            topicElement?.textContent?.trim() ||
            titleElement?.textContent?.trim() ||
            "";


        state.currentTopicName =
            topic;

        state.currentTopicId =
            "";
    }


    /* =====================================================
       LOAD KNOWLEDGE
       ===================================================== */

    async function loadKnowledge() {

        try {

            const data =
                await apiRequest(
                    "/api/ai/knowledge"
                );


            state.topics =
                normalizeKnowledge(
                    data
                );

            state.knowledgeLoaded =
                true;


            selectCurrentTopicIfPossible();


            if (state.active) {
                renderForm();
            }

        } catch (error) {

            console.error(
                "AI knowledge error:",
                error
            );

            state.topics = [];


            if (state.active) {

                renderForm();

                showInlineError(
                    "Không tải được danh sách kiến thức. " +
                    "Hãy kiểm tra backend MATH-WEB đang chạy."
                );
            }
        }
    }


    /* =====================================================
       NORMALIZE KNOWLEDGE
       ===================================================== */

    function normalizeKnowledge(data) {

        let source = data;


        if (
            data &&
            Array.isArray(
                data.topics
            )
        ) {
            source =
                data.topics;
        }


        if (
            data &&
            Array.isArray(
                data.knowledge
            )
        ) {
            source =
                data.knowledge;
        }


        if (!Array.isArray(source)) {
            return [];
        }


        return source
            .map(item => {

                if (
                    typeof item ===
                    "string"
                ) {
                    return {
                        id: item,
                        name: item,
                        grade: null
                    };
                }


                return {

                    id:
                        item.id ||
                        item.topic_id ||
                        item.slug ||
                        item.code ||
                        "",

                    name:
                        item.name ||
                        item.title ||
                        item.label ||
                        item.id ||
                        item.topic_id ||
                        "Kiến thức",

                    grade:
                        Number.isInteger(
                            item.grade
                        )
                            ? item.grade
                            : null
                };
            })
            .filter(
                item =>
                    item.id
            );
    }


    /* =====================================================
       SELECT CURRENT TOPIC
       ===================================================== */

    function selectCurrentTopicIfPossible() {

        if (
            !state.currentTopicName ||
            !state.topics.length
        ) {
            return;
        }


        const topics =
            getTopicsForGrade(
                state.grade
            );


        const current =
            normalizeTopicText(
                state.currentTopicName
            );


        if (!current) {
            return;
        }


        /*
         * 1. Match chính xác.
         */
        let match =
            topics.find(
                topic => {

                    const name =
                        normalizeTopicText(
                            topic.name
                        );

                    const id =
                        normalizeTopicText(
                            topic.id
                        );

                    return (
                        name === current ||
                        id === current
                    );
                }
            );


        /*
         * 2. Match contains.
         */
        if (!match) {

            match =
                topics.find(
                    topic => {

                        const name =
                            normalizeTopicText(
                                topic.name
                            );

                        const id =
                            normalizeTopicText(
                                topic.id
                            );

                        return (
                            (
                                name &&
                                current.includes(
                                    name
                                )
                            ) ||
                            (
                                name &&
                                name.includes(
                                    current
                                )
                            ) ||
                            (
                                id &&
                                current.includes(
                                    id
                                )
                            ) ||
                            (
                                id &&
                                id.includes(
                                    current
                                )
                            )
                        );
                    }
                );
        }


        /*
         * 3. Alias cho các topic thường dùng.
         */
        if (!match) {

            const alias =
                getTopicAlias(
                    current
                );

            if (alias) {

                match =
                    topics.find(
                        topic => {

                            const id =
                                normalizeTopicText(
                                    topic.id
                                );

                            const name =
                                normalizeTopicText(
                                    topic.name
                                );

                            return (
                                id === alias ||
                                name === alias ||
                                id.includes(alias) ||
                                alias.includes(id)
                            );
                        }
                    );
            }
        }


        if (match) {

            state.currentTopicId =
                match.id;


            /*
             * Chỉ tự chọn topic hiện tại
             * nếu người dùng chưa chọn gì.
             */
            if (
                !state.selectedTopics.length
            ) {
                state.selectedTopics = [
                    match.id
                ];
            }
        }
    }


    /* =====================================================
       TOPIC ALIAS
       ===================================================== */

    function getTopicAlias(value) {

        const aliases = {
            "xac suat": "probability",
            "to hop": "combination",
            "chinh hop": "permutation",
            "ham so": "function",
            "he phuong trinh":
                "system-equation",
            "phuong trinh bac nhat":
                "linear-equation",
            "bat phuong trinh bac nhat":
                "inequality",
            "day so": "sequence",
            "chia het": "divisibility",
            "chia du": "remainder",
            "can thuc": "radical",
            "hang dang thuc":
                "identities",
            "phan thuc dai so":
                "algebraic-fraction",
            "hinh hoc": "geometry",
            "thong ke": "statistics"
        };


        return aliases[value] || "";
    }


    /* =====================================================
       RENDER FORM
       ===================================================== */

    function renderForm() {

        const content =
            getContent();

        if (!content) {
            return;
        }


        const topics =
            getTopicsForGrade(
                state.grade
            );


        content.innerHTML = `

            <div class="mw-ai-header">

                <div>
                    <div class="mw-ai-title">
                        🤖 AI Luyện tập
                    </div>

                    <div class="mw-ai-subtitle">
                        ${
                            state.currentTopicName
                                ? `Chủ đề hiện tại: <b>${escapeHTML(
                                      state.currentTopicName
                                  )}</b>`
                                : "Tạo một bộ câu hỏi riêng theo lựa chọn của bạn"
                        }
                    </div>
                </div>

            </div>


            <div class="mw-ai-body">

                <div class="mw-ai-field">

                    <label>
                        📚 Lớp
                    </label>

                    <select
                        id="mw-ai-grade"
                        class="mw-ai-select"
                    >

                        <option
                            value="10"
                            ${
                                state.grade === 10
                                    ? "selected"
                                    : ""
                            }
                        >
                            Lớp 10
                        </option>

                        <option
                            value="11"
                            ${
                                state.grade === 11
                                    ? "selected"
                                    : ""
                            }
                        >
                            Lớp 11
                        </option>

                        <option
                            value="12"
                            ${
                                state.grade === 12
                                    ? "selected"
                                    : ""
                            }
                        >
                            Lớp 12
                        </option>

                    </select>

                </div>


                <div class="mw-ai-field">

                    <div class="mw-ai-label-row">

                        <label>
                            📖 Kiến thức
                        </label>

                        <button
                            type="button"
                            class="mw-ai-small-button"
                            data-ai-action="toggle-topics"
                        >
                            Chọn tất cả
                        </button>

                    </div>


                    <div class="mw-ai-topic-list">

                        ${
                            topics.length
                                ? topics
                                      .map(
                                          topic => `
                                            <label
                                                class="mw-ai-topic"
                                            >

                                                <input
                                                    type="checkbox"
                                                    value="${escapeAttr(
                                                        topic.id
                                                    )}"
                                                    data-ai-topic
                                                    ${
                                                        state.selectedTopics.includes(
                                                            topic.id
                                                        )
                                                            ? "checked"
                                                            : ""
                                                    }
                                                >

                                                <span>
                                                    ${escapeHTML(
                                                        topic.name
                                                    )}
                                                </span>

                                            </label>
                                        `
                                      )
                                      .join("")
                                : `
                                    <div class="mw-ai-empty">
                                        Chưa tải được danh sách kiến thức.
                                    </div>
                                `
                        }

                    </div>


                    <div class="mw-ai-selected-count">
                        Đã chọn:
                        <b>
                            ${state.selectedTopics.length}
                        </b>
                    </div>

                </div>


                <div class="mw-ai-field">

                    <label>
                        🎯 Độ khó
                    </label>

                    <div class="mw-ai-levels">

                        ${renderLevel(
                            "easy",
                            "🟢",
                            "Dễ"
                        )}

                        ${renderLevel(
                            "medium",
                            "🔵",
                            "Vừa"
                        )}

                        ${renderLevel(
                            "hard",
                            "🟠",
                            "Khó"
                        )}

                        ${renderLevel(
                            "expert",
                            "🔴",
                            "Chuyên"
                        )}

                    </div>

                </div>


                <div class="mw-ai-field">

                    <label>
                        📝 Dạng câu hỏi
                    </label>

                    <select
                        id="mw-ai-question-type"
                        class="mw-ai-select"
                    >

                        <option
                            value="multiple_choice"
                            ${
                                state.questionType ===
                                "multiple_choice"
                                    ? "selected"
                                    : ""
                            }
                        >
                            Trắc nghiệm
                        </option>

                        <option
                            value="true_false"
                            ${
                                state.questionType ===
                                "true_false"
                                    ? "selected"
                                    : ""
                            }
                        >
                            Đúng / Sai
                        </option>

                        <option
                            value="short_answer"
                            ${
                                state.questionType ===
                                "short_answer"
                                    ? "selected"
                                    : ""
                            }
                        >
                            Tự luận ngắn
                        </option>

                    </select>

                </div>


                <div class="mw-ai-field">

                    <div class="mw-ai-label-row">

                        <label>
                            🔢 Số câu
                        </label>

                        <span
                            id="mw-ai-count-value"
                            class="mw-ai-count-value"
                        >
                            ${state.count}
                        </span>

                    </div>


                    <input
                        id="mw-ai-count"
                        class="mw-ai-range"
                        type="range"
                        min="${CONFIG.MIN_COUNT}"
                        max="${CONFIG.MAX_COUNT}"
                        value="${state.count}"
                    >


                    <div class="mw-ai-range-labels">

                        <span>
                            ${CONFIG.MIN_COUNT} câu
                        </span>

                        <span>
                            ${CONFIG.MAX_COUNT} câu
                        </span>

                    </div>

                </div>


                <div
                    id="mw-ai-form-error"
                    class="mw-ai-error"
                    hidden
                ></div>


                <div class="mw-ai-form-actions">

                    <button
                        type="button"
                        class="mw-ai-back"
                        data-ai-action="back"
                    >
                        ← Quay lại
                    </button>

                    <button
                        type="button"
                        class="mw-ai-generate"
                        data-ai-action="generate"
                    >
                        <span>🚀</span>
                        <span>TẠO BỘ CÂU HỎI</span>
                    </button>

                </div>

            </div>
        `;


        bindFormEvents();
    }


    /* =====================================================
       LEVEL
       ===================================================== */

    function renderLevel(
        value,
        icon,
        label
    ) {

        return `
            <button
                type="button"
                class="mw-ai-level ${
                    state.difficulty === value
                        ? "selected"
                        : ""
                }"
                data-ai-level="${value}"
            >
                <span>${icon}</span>
                <span>${label}</span>
            </button>
        `;
    }


    /* =====================================================
       FORM EVENTS
       ===================================================== */

    function bindFormEvents() {

        const root =
            getContent();

        if (!root) {
            return;
        }


        const grade =
            root.querySelector(
                "#mw-ai-grade"
            );

        const type =
            root.querySelector(
                "#mw-ai-question-type"
            );

        const count =
            root.querySelector(
                "#mw-ai-count"
            );


        grade?.addEventListener(
            "change",
            () => {

                state.grade =
                    Number(
                        grade.value
                    );

                state.selectedTopics =
                    [];

                selectCurrentTopicIfPossible();

                renderForm();
            }
        );


        type?.addEventListener(
            "change",
            () => {

                state.questionType =
                    type.value;
            }
        );


        count?.addEventListener(
            "input",
            () => {

                state.count =
                    clamp(
                        Number(
                            count.value
                        ),
                        CONFIG.MIN_COUNT,
                        CONFIG.MAX_COUNT
                    );


                const display =
                    root.querySelector(
                        "#mw-ai-count-value"
                    );

                if (display) {
                    display.textContent =
                        state.count;
                }
            }
        );


        root
            .querySelectorAll(
                "[data-ai-topic]"
            )
            .forEach(input => {

                input.addEventListener(
                    "change",
                    updateSelectedTopics
                );
            });


        root
            .querySelectorAll(
                "[data-ai-level]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        state.difficulty =
                            button.dataset.aiLevel;

                        renderForm();
                    }
                );
            });


        root
            .querySelectorAll(
                "[data-ai-action]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    handleAction
                );
            });
    }


    /* =====================================================
       ACTIONS
       ===================================================== */

    function handleAction(event) {

        event.preventDefault();

        const action =
            event.currentTarget
                .dataset.aiAction;


        if (action === "back") {
            exitAI();
            return;
        }


        if (action === "close") {
            exitAI();
            return;
        }


        if (action === "generate") {
            generateQuestions();
            return;
        }


        if (
            action ===
            "toggle-topics"
        ) {
            toggleAllTopics();
            return;
        }


        if (action === "submit") {

            if (
                state.answerRevealed
            ) {
                nextQuestion();
            } else {
                submitCurrentAnswer();
            }

            return;
        }


        if (action === "skip") {
            skipCurrentQuestion();
            return;
        }


        if (action === "next") {
            nextQuestion();
            return;
        }


        if (action === "retry") {
            retry();
        }
    }


    /* =====================================================
       TOPICS
       ===================================================== */

    function updateSelectedTopics() {

        const root =
            getContent();

        if (!root) {
            return;
        }


        state.selectedTopics =
            Array.from(
                root.querySelectorAll(
                    "[data-ai-topic]:checked"
                )
            ).map(
                input =>
                    input.value
            );


        const count =
            root.querySelector(
                ".mw-ai-selected-count b"
            );


        if (count) {
            count.textContent =
                state.selectedTopics.length;
        }
    }


    function toggleAllTopics() {

        const topics =
            getTopicsForGrade(
                state.grade
            );


        const allSelected =
            topics.length > 0 &&
            topics.every(
                topic =>
                    state.selectedTopics.includes(
                        topic.id
                    )
            );


        state.selectedTopics =
            allSelected
                ? []
                : topics.map(
                      topic =>
                          topic.id
                  );


        renderForm();
    }


    function getTopicsForGrade(
        grade
    ) {

        const filtered =
            state.topics.filter(
                topic =>
                    topic.grade === null ||
                    topic.grade === undefined ||
                    topic.grade === grade
            );


        return filtered.length
            ? filtered
            : state.topics;
    }


    /* =====================================================
       GENERATE
       ===================================================== */

    async function generateQuestions() {

        updateSelectedTopics();


        const error =
            validateForm();


        if (error) {

            showInlineError(
                error
            );

            return;
        }


        if (state.generating) {
            return;
        }


        state.generating = true;

        renderGenerating();


        try {

            const result =
                await apiRequest(
                    "/api/ai/questions",
                    {
                        method: "POST",

                        body: {

                            grade:
                                state.grade,

                            topics:
                                state.selectedTopics,

                            count:
                                state.count,

                            difficulty:
                                state.difficulty,

                            question_type:
                                state.questionType,

                            history: []
                        }
                    }
                );


            const questions =
                normalizeQuestions(
                    result
                );


            if (!questions.length) {
                throw new Error(
                    "AI không trả về câu hỏi hợp lệ."
                );
            }


            state.questions =
                questions;

            state.lastSetId =
                result?.set_id ||
                result?.id ||
                null;


            state.currentIndex = 0;

            state.answers = {};
            state.results = {};

            state.correct = 0;
            state.wrong = 0;
            state.skipped = 0;
            state.score = 0;

            state.startedAt =
                Date.now();

            state.answerRevealed =
                false;

            state.mode =
                "quiz";


            renderQuestion();

        } catch (error) {

            console.error(
                "AI generation error:",
                error
            );

            state.mode =
                "form";

            renderForm();

            showInlineError(
                getErrorMessage(
                    error
                )
            );

        } finally {

            state.generating =
                false;
        }
    }


    /* =====================================================
       VALIDATE FORM
       ===================================================== */

    function validateForm() {

        if (
            !Number.isInteger(
                state.grade
            ) ||
            state.grade < 10 ||
            state.grade > 12
        ) {
            return "Vui lòng chọn lớp hợp lệ.";
        }


        if (
            !state.selectedTopics.length
        ) {
            return "Hãy chọn ít nhất một kiến thức.";
        }


        if (
            state.count <
                CONFIG.MIN_COUNT ||
            state.count >
                CONFIG.MAX_COUNT
        ) {
            return `Số câu phải từ ${CONFIG.MIN_COUNT} đến ${CONFIG.MAX_COUNT}.`;
        }


        if (
            !CONFIG.LEVELS[
                state.difficulty
            ]
        ) {
            return "Độ khó không hợp lệ.";
        }


        if (
            !CONFIG.QUESTION_TYPES[
                state.questionType
            ]
        ) {
            return "Dạng câu hỏi không hợp lệ.";
        }


        return "";
    }


    /* =====================================================
       GENERATING
       ===================================================== */

    function renderGenerating() {

        const content =
            getContent();

        if (!content) {
            return;
        }


        content.innerHTML = `

            <div class="mw-ai-loading">

                <div class="mw-ai-spinner"></div>

                <div class="mw-ai-loading-title">
                    🤖 AI đang tạo bộ câu hỏi...
                </div>

                <div class="mw-ai-loading-text">
                    Đang tạo câu hỏi đa dạng và phù hợp
                    với lựa chọn của bạn.
                </div>

                <div class="mw-ai-loading-info">
                    ${state.count} câu
                    ·
                    ${escapeHTML(
                        CONFIG.LEVELS[
                            state.difficulty
                        ]
                    )}
                    ·
                    ${escapeHTML(
                        CONFIG.QUESTION_TYPES[
                            state.questionType
                        ]
                    )}
                </div>

            </div>
        `;
    }


    /* =====================================================
       NORMALIZE QUESTIONS
       ===================================================== */

    function normalizeQuestions(
        result
    ) {

        let source =
            result;


        if (
            result &&
            Array.isArray(
                result.questions
            )
        ) {
            source =
                result.questions;
        }


        if (!Array.isArray(source)) {
            return [];
        }


        return source
            .map(
                (
                    question,
                    index
                ) => ({

                    id:
                        question.id ||
                        question.question_id ||
                        `ai-q-${index + 1}`,

                    question:
                        question.question ||
                        question.text ||
                        question.prompt ||
                        "",

                    question_type:
                        question.question_type ||
                        question.type ||
                        state.questionType,

                    options:
                        Array.isArray(
                            question.options
                        )
                            ? question.options
                            : [],

                    statements:
                        Array.isArray(
                            question.statements
                        )
                            ? question.statements
                            : [],

                    topic:
                        question.topic ||
                        question.topic_id ||
                        "",

                    difficulty:
                        question.difficulty ||
                        state.difficulty,

                    answer:
                        question.answer,

                    statement_answers:
                        question.statement_answers,

                    solution:
                        question.solution ||
                        "",

                    explanation:
                        question.explanation ||
                        ""
                })
            )
            .filter(
                question =>
                    question.question
            );
    }


    /* =====================================================
       QUESTION
       ===================================================== */

    function renderQuestion() {

        if (
            state.currentIndex >=
            state.questions.length
        ) {
            finishQuiz();
            return;
        }


        const question =
            state.questions[
                state.currentIndex
            ];


        const total =
            state.questions.length;

        const number =
            state.currentIndex + 1;


        const percent =
            Math.round(
                (number / total) *
                    100
            );


        const content =
            getContent();

        if (!content) {
            return;
        }


        state.answerRevealed =
            false;


        content.innerHTML = `

            <div class="mw-ai-header">

                <div>

                    <div class="mw-ai-title">
                        🤖 AI Luyện tập
                    </div>

                    <div class="mw-ai-progress-text">
                        Câu ${number}/${total}
                    </div>

                </div>

            </div>


            <div class="mw-ai-progress">
                <div
                    class="mw-ai-progress-bar"
                    style="width:${percent}%"
                ></div>
            </div>


            <div class="mw-ai-quiz">

                <div class="mw-ai-question-meta">

                    <span class="mw-ai-badge">
                        ${
                            CONFIG.LEVELS[
                                question.difficulty
                            ] ||
                            CONFIG.LEVELS[
                                state.difficulty
                            ]
                        }
                    </span>

                    <span class="mw-ai-badge">
                        ${
                            CONFIG.QUESTION_TYPES[
                                question.question_type
                            ] ||
                            CONFIG.QUESTION_TYPES[
                                state.questionType
                            ]
                        }
                    </span>

                </div>


                <div class="mw-ai-question">
                    ${formatQuestionText(
                        question.question
                    )}
                </div>


                <div
                    id="mw-ai-answer-area"
                    class="mw-ai-answer-area"
                >
                    ${renderAnswerArea(
                        question
                    )}
                </div>


                <div
                    id="mw-ai-feedback"
                    class="mw-ai-feedback"
                    hidden
                ></div>


                <div class="mw-ai-actions">

                    <button
                        type="button"
                        class="mw-ai-secondary"
                        data-ai-action="skip"
                    >
                        Bỏ qua
                    </button>

                    <button
                        type="button"
                        class="mw-ai-submit"
                        data-ai-action="submit"
                    >
                        Kiểm tra ✓
                    </button>

                </div>

            </div>
        `;


        bindQuestionEvents();
    }


    /* =====================================================
       ANSWER AREA
       ===================================================== */

    function renderAnswerArea(
        question
    ) {

        switch (
            question.question_type
        ) {

            case "multiple_choice":

                return renderMultipleChoice(
                    question
                );

            case "true_false":

                return renderTrueFalse(
                    question
                );

            default:

                return renderShortAnswer();
        }
    }


    /* =====================================================
       MULTIPLE CHOICE
       ===================================================== */

    function renderMultipleChoice(
        question
    ) {

        if (
            !question.options.length
        ) {
            return renderShortAnswer();
        }


        return `

            <div class="mw-ai-options">

                ${question.options
                    .map(
                        (
                            option,
                            index
                        ) => `

                            <button
                                type="button"
                                class="mw-ai-option"
                                data-answer-index="${index}"
                            >

                                <span
                                    class="mw-ai-option-letter"
                                >
                                    ${getOptionLetter(
                                        index
                                    )}
                                </span>

                                <span>
                                    ${formatOption(
                                        option
                                    )}
                                </span>

                            </button>
                        `
                    )
                    .join("")}

            </div>
        `;
    }


    /* =====================================================
       TRUE / FALSE
       ===================================================== */

    function renderTrueFalse(
        question
    ) {

        if (
            question.statements?.length
        ) {

            return `

                <div class="mw-ai-statements">

                    ${question.statements
                        .map(
                            (
                                statement,
                                index
                            ) => `

                                <div
                                    class="mw-ai-statement"
                                >

                                    <div
                                        class="mw-ai-statement-text"
                                    >
                                        ${index + 1}.
                                        ${escapeHTML(
                                            statement
                                        )}
                                    </div>

                                    <div
                                        class="mw-ai-tf-buttons"
                                    >

                                        <button
                                            type="button"
                                            class="mw-ai-tf"
                                            data-statement="${index}"
                                            data-value="true"
                                        >
                                            Đúng
                                        </button>

                                        <button
                                            type="button"
                                            class="mw-ai-tf"
                                            data-statement="${index}"
                                            data-value="false"
                                        >
                                            Sai
                                        </button>

                                    </div>

                                </div>
                            `
                        )
                        .join("")}

                </div>
            `;
        }


        return `

            <div class="mw-ai-options">

                <button
                    type="button"
                    class="mw-ai-option"
                    data-tf-value="true"
                >
                    <span
                        class="mw-ai-option-letter"
                    >
                        ✓
                    </span>

                    <span>
                        Đúng
                    </span>
                </button>


                <button
                    type="button"
                    class="mw-ai-option"
                    data-tf-value="false"
                >
                    <span
                        class="mw-ai-option-letter"
                    >
                        ✕
                    </span>

                    <span>
                        Sai
                    </span>
                </button>

            </div>
        `;
    }


    /* =====================================================
       SHORT ANSWER
       ===================================================== */

    function renderShortAnswer() {

        return `

            <input
                id="mw-ai-short-answer"
                class="mw-ai-input"
                type="text"
                autocomplete="off"
                placeholder="Nhập đáp án của bạn..."
            >
        `;
    }


    /* =====================================================
       QUESTION EVENTS
       ===================================================== */

    function bindQuestionEvents() {

        const root =
            getContent();

        if (!root) {
            return;
        }


        root
            .querySelectorAll(
                "[data-answer-index]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        root
                            .querySelectorAll(
                                "[data-answer-index]"
                            )
                            .forEach(
                                item =>
                                    item.classList.remove(
                                        "selected"
                                    )
                            );


                        button.classList.add(
                            "selected"
                        );
                    }
                );
            });


        root
            .querySelectorAll(
                "[data-tf-value]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        root
                            .querySelectorAll(
                                "[data-tf-value]"
                            )
                            .forEach(
                                item =>
                                    item.classList.remove(
                                        "selected"
                                    )
                            );


                        button.classList.add(
                            "selected"
                        );
                    }
                );
            });


        root
            .querySelectorAll(
                ".mw-ai-tf"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        const index =
                            button.dataset
                                .statement;


                        root
                            .querySelectorAll(
                                `.mw-ai-tf[data-statement="${index}"]`
                            )
                            .forEach(
                                item =>
                                    item.classList.remove(
                                        "selected"
                                    )
                            );


                        button.classList.add(
                            "selected"
                        );
                    }
                );
            });


        const input =
            root.querySelector(
                "#mw-ai-short-answer"
            );


        input?.addEventListener(
            "keydown",
            event => {

                if (
                    event.key ===
                    "Enter"
                ) {

                    event.preventDefault();

                    if (
                        !state.answerRevealed
                    ) {
                        submitCurrentAnswer();
                    }
                }
            }
        );
    }


    /* =====================================================
       CURRENT ANSWER
       ===================================================== */

    function getCurrentAnswer() {

        const question =
            state.questions[
                state.currentIndex
            ];


        if (!question) {
            return null;
        }


        const root =
            getContent();

        if (!root) {
            return null;
        }


        if (
            question.question_type ===
            "multiple_choice"
        ) {

            const selected =
                root.querySelector(
                    ".mw-ai-option.selected[data-answer-index]"
                );


            if (!selected) {
                return null;
            }


            const index =
                Number(
                    selected.dataset
                        .answerIndex
                );


            return question.options[
                index
            ];
        }


        if (
            question.question_type ===
            "true_false"
        ) {

            if (
                question.statements?.length
            ) {

                const values =
                    question.statements.map(
                        (
                            _,
                            index
                        ) => {

                            const selected =
                                root.querySelector(
                                    `.mw-ai-tf[data-statement="${index}"].selected`
                                );


                            if (!selected) {
                                return null;
                            }


                            return (
                                selected.dataset
                                    .value ===
                                "true"
                            );
                        }
                    );


                if (
                    values.some(
                        value =>
                            value ===
                            null
                    )
                ) {
                    return null;
                }


                return values;
            }


            const selected =
                root.querySelector(
                    "[data-tf-value].selected"
                );


            if (!selected) {
                return null;
            }


            return (
                selected.dataset
                    .tfValue ===
                "true"
            );
        }


        const input =
            root.querySelector(
                "#mw-ai-short-answer"
            );


        if (!input) {
            return null;
        }


        const value =
            input.value.trim();


        return value || null;
    }


    /* =====================================================
       SUBMIT ANSWER
       ===================================================== */

    async function submitCurrentAnswer() {

        if (
            state.submitting ||
            state.answerRevealed
        ) {
            return;
        }


        const question =
            state.questions[
                state.currentIndex
            ];


        if (!question) {
            return;
        }


        const answer =
            getCurrentAnswer();


        if (answer === null) {

            showFeedback(
                "warning",
                "📝 Hãy chọn hoặc nhập đáp án trước nhé!"
            );

            return;
        }


        state.submitting = true;


        const root =
            getContent();


        const submit =
            root?.querySelector(
                "[data-ai-action='submit']"
            );


        if (submit) {

            submit.disabled =
                true;

            submit.textContent =
                "Đang kiểm tra...";
        }


        try {

            let result;


            if (
                question.id &&
                !question.id.startsWith(
                    "ai-q-"
                )
            ) {

                result =
                    await apiRequest(
                        `/api/ai/questions/${encodeURIComponent(
                            question.id
                        )}/answer`,
                        {
                            method: "POST",

                            body: {
                                answer
                            }
                        }
                    );

            } else {

                result =
                    checkLocalAnswer(
                        question,
                        answer
                    );
            }


            const correct =
                Boolean(
                    result?.correct
                );


            state.answers[
                question.id
            ] = answer;


            state.results[
                question.id
            ] = {
                correct,
                result
            };


            if (correct) {

                state.correct += 1;

                state.score +=
                    getQuestionPoints(
                        question
                    );

            } else {

                state.wrong += 1;
            }


            showAnswerResult(
                question,
                result,
                correct
            );


        } catch (error) {

            console.error(
                "AI answer error:",
                error
            );


            showFeedback(
                "error",
                getErrorMessage(
                    error
                )
            );


            if (submit) {

                submit.disabled =
                    false;

                submit.textContent =
                    "Kiểm tra ✓";
            }


        } finally {

            state.submitting =
                false;
        }
    }


    /* =====================================================
       LOCAL ANSWER
       ===================================================== */

    function checkLocalAnswer(
        question,
        userAnswer
    ) {

        const type =
            question.question_type;


        if (
            type ===
            "multiple_choice"
        ) {

            return {
                correct:
                    normalizeText(
                        userAnswer
                    ) ===
                    normalizeText(
                        question.answer
                    ),

                correct_answer:
                    question.answer,

                solution:
                    question.solution
            };
        }


        if (
            type ===
            "true_false"
        ) {

            if (
                Array.isArray(
                    userAnswer
                ) &&
                Array.isArray(
                    question.statement_answers
                )
            ) {

                return {
                    correct:
                        JSON.stringify(
                            userAnswer
                        ) ===
                        JSON.stringify(
                            question.statement_answers
                        ),

                    correct_answer:
                        question.statement_answers,

                    solution:
                        question.solution
                };
            }


            return {
                correct:
                    Boolean(
                        userAnswer
                    ) ===
                    Boolean(
                        question.answer
                    ),

                correct_answer:
                    question.answer,

                solution:
                    question.solution
            };
        }


        return {
            correct:
                normalizeText(
                    userAnswer
                ) ===
                normalizeText(
                    question.answer
                ),

            correct_answer:
                question.answer,

            solution:
                question.solution
        };
    }


    /* =====================================================
       ANSWER RESULT
       ===================================================== */

    function showAnswerResult(
        question,
        result,
        correct
    ) {

        const root =
            getContent();

        if (!root) {
            return;
        }


        const feedback =
            root.querySelector(
                "#mw-ai-feedback"
            );


        const area =
            root.querySelector(
                "#mw-ai-answer-area"
            );


        if (!feedback) {
            return;
        }


        if (correct) {

            feedback.className =
                "mw-ai-feedback correct";


            feedback.innerHTML = `

                <div class="mw-ai-feedback-title">
                    ${randomCorrectFeedback()}
                </div>

                <div class="mw-ai-feedback-text">
                    Chính xác! Bạn làm rất tốt.
                </div>
            `;

        } else {

            feedback.className =
                "mw-ai-feedback wrong";


            const correctAnswer =
                result &&
                result.correct_answer !==
                    undefined
                    ? result.correct_answer
                    : null;


            const solution =
                result?.solution ||
                question.solution ||
                question.explanation ||
                "";


            feedback.innerHTML = `

                <div class="mw-ai-feedback-title">
                    ${randomWrongFeedback()}
                </div>

                ${
                    correctAnswer !== null
                        ? `
                            <div class="mw-ai-correct-answer">
                                <b>Đáp án:</b>
                                ${formatAnswer(
                                    correctAnswer
                                )}
                            </div>
                        `
                        : ""
                }

                ${
                    solution
                        ? `
                            <div class="mw-ai-solution">

                                <b>💡 Lời giải:</b>

                                <div>
                                    ${formatSolution(
                                        solution
                                    )}
                                </div>

                            </div>
                        `
                        : ""
                }
            `;
        }


        feedback.hidden =
            false;


        if (area) {

            area
                .querySelectorAll(
                    "button,input"
                )
                .forEach(
                    element => {
                        element.disabled =
                            true;
                    }
                );
        }


        const submit =
            root.querySelector(
                "[data-ai-action='submit']"
            );


        const skip =
            root.querySelector(
                "[data-ai-action='skip']"
            );


        state.answerRevealed =
            true;


        if (submit) {

            submit.textContent =
                state.currentIndex >=
                state.questions.length - 1
                    ? "Xem kết quả 🏆"
                    : "Câu tiếp theo →";

            submit.disabled =
                false;
        }


        if (skip) {
            skip.disabled =
                true;
        }
    }


    /* =====================================================
       NEXT
       ===================================================== */

    function nextQuestion() {

        if (!state.answerRevealed) {
            return;
        }


        state.currentIndex += 1;


        if (
            state.currentIndex >=
            state.questions.length
        ) {

            finishQuiz();

            return;
        }


        renderQuestion();
    }


    /* =====================================================
       SKIP
       ===================================================== */

    function skipCurrentQuestion() {

        if (
            state.submitting ||
            state.answerRevealed
        ) {
            return;
        }


        const question =
            state.questions[
                state.currentIndex
            ];


        if (!question) {
            return;
        }


        state.answers[
            question.id
        ] = null;


        state.results[
            question.id
        ] = {
            correct: false,
            skipped: true
        };


        state.skipped += 1;


        showSkipFeedback();
    }


    /* =====================================================
       SKIP FEEDBACK
       ===================================================== */

    function showSkipFeedback() {

        const root =
            getContent();


        const feedback =
            root?.querySelector(
                "#mw-ai-feedback"
            );


        if (!feedback) {

            nextQuestion();

            return;
        }


        feedback.className =
            "mw-ai-feedback warning";


        feedback.innerHTML = `

            <div class="mw-ai-feedback-title">
                ⏭️ Bạn đã bỏ qua câu này.
            </div>

            <div class="mw-ai-feedback-text">
                Không sao, tiếp tục chiến đấu nhé!
            </div>
        `;


        feedback.hidden =
            false;


        const area =
            root.querySelector(
                "#mw-ai-answer-area"
            );


        if (area) {

            area
                .querySelectorAll(
                    "button,input"
                )
                .forEach(
                    element => {
                        element.disabled =
                            true;
                    }
                );
        }


        const submit =
            root.querySelector(
                "[data-ai-action='submit']"
            );


        const skip =
            root.querySelector(
                "[data-ai-action='skip']"
            );


        state.answerRevealed =
            true;


        if (submit) {

            submit.textContent =
                state.currentIndex >=
                state.questions.length - 1
                    ? "Xem kết quả 🏆"
                    : "Câu tiếp theo →";

            submit.disabled =
                false;
        }


        if (skip) {
            skip.disabled =
                true;
        }
    }


    /* =====================================================
       FINISH
       ===================================================== */

    function finishQuiz() {

        state.finishedAt =
            Date.now();

        state.mode =
            "result";

        state.answerRevealed =
            false;

        renderResult();
    }


    /* =====================================================
       RESULT
       ===================================================== */

    function renderResult() {

        const total =
            state.questions.length;


        const elapsed =
            Math.max(
                0,
                state.finishedAt -
                    state.startedAt
            );


        const seconds =
            Math.round(
                elapsed / 1000
            );


        const percent =
            total
                ? Math.round(
                      (state.correct /
                          total) *
                          100
                  )
                : 0;


        const content =
            getContent();


        if (!content) {
            return;
        }


        content.innerHTML = `

            <div class="mw-ai-result">

                <div class="mw-ai-result-icon">
                    ${getResultEmoji(
                        percent
                    )}
                </div>

                <div class="mw-ai-result-title">
                    ${getResultTitle(
                        percent
                    )}
                </div>

                <div class="mw-ai-result-subtitle">
                    Bạn đã hoàn thành bộ câu hỏi AI!
                </div>


                <div class="mw-ai-result-score">
                    ${state.score}
                    <span>XP</span>
                </div>


                <div class="mw-ai-result-grid">

                    <div class="mw-ai-stat">
                        <span>Đúng</span>
                        <b class="correct">
                            ${state.correct}
                        </b>
                    </div>

                    <div class="mw-ai-stat">
                        <span>Sai</span>
                        <b class="wrong">
                            ${state.wrong}
                        </b>
                    </div>

                    <div class="mw-ai-stat">
                        <span>Bỏ qua</span>
                        <b>
                            ${state.skipped}
                        </b>
                    </div>

                    <div class="mw-ai-stat">
                        <span>Thời gian</span>
                        <b>
                            ${formatTime(
                                seconds
                            )}
                        </b>
                    </div>

                </div>


                <div class="mw-ai-result-percent">
                    ${percent}% chính xác
                </div>


                <div class="mw-ai-result-actions">

                    <button
                        type="button"
                        class="mw-ai-secondary"
                        data-ai-action="retry"
                    >
                        🔄 Làm lại
                    </button>

                    <button
                        type="button"
                        class="mw-ai-submit"
                        data-ai-action="back"
                    >
                        ← Về luyện tập
                    </button>

                </div>

            </div>
        `;


        bindResultEvents();
    }


    /* =====================================================
       RESULT EVENTS
       ===================================================== */

    function bindResultEvents() {

        const root =
            getContent();

        if (!root) {
            return;
        }


        root
            .querySelector(
                "[data-ai-action='retry']"
            )
            ?.addEventListener(
                "click",
                retry
            );


        root
            .querySelector(
                "[data-ai-action='back']"
            )
            ?.addEventListener(
                "click",
                exitAI
            );
    }


    /* =====================================================
       RETRY
       ===================================================== */

    function retry() {

        resetQuestionState();

        state.mode =
            "form";

        renderForm();
    }


    /* =====================================================
       POINTS
       ===================================================== */

    function getQuestionPoints(
        question
    ) {

        switch (
            question.difficulty ||
            state.difficulty
        ) {

            case "easy":
                return 10;

            case "medium":
                return 15;

            case "hard":
                return 20;

            case "expert":
                return 30;

            default:
                return 15;
        }
    }


    /* =====================================================
       API
       ===================================================== */

    async function apiRequest(
        path,
        options = {}
    ) {

        const controller =
            new AbortController();


        const timeout =
            setTimeout(
                () =>
                    controller.abort(),
                CONFIG.REQUEST_TIMEOUT
            );


        try {

            const headers = {
                Accept:
                    "application/json"
            };


            const fetchOptions = {

                method:
                    options.method ||
                    "GET",

                headers,

                signal:
                    controller.signal
            };


            if (
                options.body !==
                    undefined &&
                options.body !== null
            ) {

                headers[
                    "Content-Type"
                ] =
                    "application/json";


                fetchOptions.body =
                    JSON.stringify(
                        options.body
                    );
            }


            const response =
                await fetch(
                    CONFIG.API_BASE +
                        path,
                    fetchOptions
                );


            const text =
                await response.text();


            let data = null;


            if (text) {

                try {

                    data =
                        JSON.parse(
                            text
                        );

                } catch {

                    data = {
                        message: text
                    };
                }
            }


            if (!response.ok) {

                const message =
                    data?.detail ||
                    data?.message ||
                    data?.error;


                throw new Error(
                    message ||
                        `API lỗi ${response.status}`
                );
            }


            return data;

        } catch (error) {

            if (
                error.name ===
                "AbortError"
            ) {

                throw new Error(
                    "Máy chủ phản hồi quá lâu. Hãy thử lại."
                );
            }


            if (
                error instanceof
                TypeError
            ) {

                throw new Error(
                    "Không kết nối được tới MATH WEB API."
                );
            }


            throw error;

        } finally {

            clearTimeout(
                timeout
            );
        }
    }


    /* =====================================================
       FEEDBACK
       ===================================================== */

    function randomCorrectFeedback() {

        const messages = [

            "🎉 Wow, bạn giỏi quá!",

            "✨ Chính xác! Quá tuyệt!",

            "🔥 Làm tốt lắm!",

            "🚀 Chuẩn luôn!",

            "🧠 Bộ não toán học đang hoạt động hết công suất!",

            "💙 Chính xác rồi! Tiếp tục nhé!",

            "🏆 Tuyệt vời!"
        ];


        return messages[
            Math.floor(
                Math.random() *
                    messages.length
            )
        ];
    }


    function randomWrongFeedback() {

        const messages = [

            "😅 Oh oh, bạn sai mất tiu rồi!",

            "💪 Chưa đúng lần này, cố lên nhé!",

            "🧩 Gần rồi! Xem lại cách làm nha!",

            "🌱 Sai một câu không sao, mình học tiếp!",

            "🔎 Cùng xem lại câu này nhé!",

            "⚡ Không sao! Câu tiếp theo chiến tiếp!"
        ];


        return messages[
            Math.floor(
                Math.random() *
                    messages.length
            )
        ];
    }


    /* =====================================================
       FEEDBACK UI
       ===================================================== */

    function showInlineError(
        message
    ) {

        const root =
            getContent();

        const element =
            root?.querySelector(
                "#mw-ai-form-error"
            );


        if (!element) {
            return;
        }


        element.textContent =
            message;

        element.hidden =
            false;
    }


    function showFeedback(
        type,
        message
    ) {

        const root =
            getContent();

        const feedback =
            root?.querySelector(
                "#mw-ai-feedback"
            );


        if (!feedback) {
            return;
        }


        feedback.className =
            `mw-ai-feedback ${type}`;


        feedback.innerHTML =
            `<div>${escapeHTML(
                message
            )}</div>`;


        feedback.hidden =
            false;
    }


    /* =====================================================
       FORMAT
       ===================================================== */

    function formatQuestionText(
        text
    ) {

        return escapeHTML(
            String(text)
        ).replace(
            /\n/g,
            "<br>"
        );
    }


    function formatOption(
        option
    ) {

        if (
            option &&
            typeof option ===
                "object"
        ) {

            if (
                option.text !==
                undefined
            ) {

                return escapeHTML(
                    String(
                        option.text
                    )
                );
            }


            return escapeHTML(
                JSON.stringify(
                    option
                )
            );
        }


        return escapeHTML(
            String(option)
        );
    }


    function formatAnswer(
        answer
    ) {

        if (
            Array.isArray(answer)
        ) {

            return escapeHTML(
                answer
                    .map(
                        value =>
                            value ===
                            true
                                ? "Đúng"
                                : value ===
                                  false
                                ? "Sai"
                                : String(
                                      value
                                  )
                    )
                    .join(", ")
            );
        }


        if (
            answer &&
            typeof answer ===
                "object"
        ) {

            return escapeHTML(
                JSON.stringify(
                    answer
                )
            );
        }


        return escapeHTML(
            String(answer)
        );
    }


    function formatSolution(
        solution
    ) {

        return escapeHTML(
            String(solution)
        ).replace(
            /\n/g,
            "<br>"
        );
    }


    function getOptionLetter(
        index
    ) {

        return String.fromCharCode(
            65 + index
        );
    }


    function normalizeText(
        value
    ) {

        return String(
            value ?? ""
        )
            .trim()
            .toLowerCase()
            .replace(
                /\s+/g,
                " "
            );
    }


    function normalizeTopicText(
        value
    ) {

        return normalizeText(
            value
        )
            .normalize("NFD")
            .replace(
                /[\u0300-\u036f]/g,
                ""
            )
            .replace(
                /đ/g,
                "d"
            );
    }


    /* =====================================================
       RESULT HELPERS
       ===================================================== */

    function getResultEmoji(
        percent
    ) {

        if (percent >= 90) {
            return "🏆";
        }


        if (percent >= 70) {
            return "🔥";
        }


        if (percent >= 50) {
            return "💪";
        }


        return "🌱";
    }


    function getResultTitle(
        percent
    ) {

        if (percent >= 90) {
            return "Xuất sắc!";
        }


        if (percent >= 70) {
            return "Rất tốt!";
        }


        if (percent >= 50) {
            return "Làm tốt lắm!";
        }


        return "Cố gắng thêm nhé!";
    }


    function formatTime(
        seconds
    ) {

        const min =
            Math.floor(
                seconds / 60
            );


        const sec =
            seconds % 60;


        return `${String(
            min
        ).padStart(
            2,
            "0"
        )}:${String(
            sec
        ).padStart(
            2,
            "0"
        )}`;
    }


    /* =====================================================
       ERROR
       ===================================================== */

    function getErrorMessage(
        error
    ) {

        return (
            error?.message ||
            "Đã xảy ra lỗi. Hãy thử lại."
        );
    }


    /* =====================================================
       ESCAPE
       ===================================================== */

    function escapeHTML(
        value
    ) {

        return String(
            value ?? ""
        )
            .replace(
                /&/g,
                "&amp;"
            )
            .replace(
                /</g,
                "&lt;"
            )
            .replace(
                />/g,
                "&gt;"
            )
            .replace(
                /"/g,
                "&quot;"
            )
            .replace(
                /'/g,
                "&#039;"
            );
    }


    function escapeAttr(
        value
    ) {

        return escapeHTML(
            value
        );
    }


    /* =====================================================
       CLAMP
       ===================================================== */

    function clamp(
        value,
        min,
        max
    ) {

        return Math.min(
            max,
            Math.max(
                min,
                value
            )
        );
    }


    /* =====================================================
       CONTENT
       ===================================================== */

    function getContent() {

        if (!state.aiView) {
            return null;
        }


        return state.aiView;
    }


    /* =====================================================
       STYLES
       ===================================================== */

    function injectStyles() {

        if (
            document.getElementById(
                "mw-ai-practice-styles"
            )
        ) {
            return;
        }


        const style =
            document.createElement(
                "style"
            );


        style.id =
            "mw-ai-practice-styles";


        style.textContent = `

            /* =================================================
               AI VIEW
               Đây chỉ là nội dung bên trong popup.
               Không fixed.
               Không absolute toàn màn hình.
               Không overlay.
               ================================================= */

            #knowledgePopup .popup-container > .mw-ai-view {

                position: relative;

                width: 100%;

                max-width: 100%;

                min-width: 0;

                margin: 0;

                padding: 0;

                box-sizing: border-box;

                color: #fff;

                overflow: visible;

            }


            #knowledgePopup .popup-container > .mw-ai-view *,
            #knowledgePopup .popup-container > .mw-ai-view *::before,
            #knowledgePopup .popup-container > .mw-ai-view *::after {

                box-sizing: border-box;

            }


            /* =================================================
               HEADER
               ================================================= */

            .mw-ai-header {

                display: flex;

                align-items: center;

                width: 100%;

                padding: 22px 26px 17px;

                border-bottom: 1px solid rgba(
                    255,
                    255,
                    255,
                    .08
                );

            }


            .mw-ai-title {

                font-size: 23px;

                font-weight: 800;

                line-height: 1.3;

            }


            .mw-ai-subtitle,
            .mw-ai-progress-text {

                margin-top: 6px;

                color: #94a3b8;

                font-size: 13px;

                line-height: 1.5;

            }


            .mw-ai-subtitle b {

                color: #70b7ff;

            }


            /* =================================================
               FORM
               ================================================= */

            .mw-ai-body {

                width: 100%;

                padding: 22px 26px 25px;

            }


            .mw-ai-field {

                margin-bottom: 20px;

            }


            .mw-ai-field > label,
            .mw-ai-label-row > label {

                display: block;

                margin-bottom: 9px;

                font-size: 14px;

                font-weight: 700;

            }


            .mw-ai-label-row {

                display: flex;

                justify-content: space-between;

                align-items: center;

                gap: 12px;

            }


            /* =================================================
               SELECT / INPUT
               ================================================= */

            .mw-ai-select,
            .mw-ai-input {

                width: 100%;

                min-height: 46px;

                padding: 11px 14px;

                border: 1px solid rgba(
                    148,
                    163,
                    184,
                    .2
                );

                border-radius: 12px;

                outline: none;

                background: rgba(
                    15,
                    23,
                    42,
                    .9
                );

                color: #fff;

                font-size: 14px;

            }


            .mw-ai-select:focus,
            .mw-ai-input:focus {

                border-color: #55aaff;

                box-shadow:
                    0 0 0 3px rgba(
                        85,
                        170,
                        255,
                        .1
                    );

            }


            /* =================================================
               TOPICS
               ================================================= */

            .mw-ai-topic-list {

                display: grid;

                grid-template-columns:
                    repeat(2, minmax(0, 1fr));

                gap: 8px;

                max-height: 190px;

                overflow-y: auto;

                padding: 2px;

            }


            .mw-ai-topic {

                display: flex;

                align-items: center;

                gap: 9px;

                min-height: 42px;

                padding: 8px 10px;

                border: 1px solid rgba(
                    255,
                    255,
                    255,
                    .06
                );

                border-radius: 10px;

                background: rgba(
                    255,
                    255,
                    255,
                    .04
                );

                color: #e2e8f0;

                cursor: pointer;

                font-size: 13px;

                transition:
                    border-color .16s ease,
                    background .16s ease;

            }


            .mw-ai-topic:hover {

                border-color: rgba(
                    70,
                    150,
                    255,
                    .25
                );

                background: rgba(
                    70,
                    150,
                    255,
                    .1
                );

            }


            .mw-ai-topic input {

                margin: 0;

                accent-color: #4ea1ff;

            }


            .mw-ai-selected-count {

                margin-top: 8px;

                color: #94a3b8;

                font-size: 12px;

            }


            .mw-ai-selected-count b {

                color: #70b7ff;

            }


            .mw-ai-small-button {

                border: 0;

                border-radius: 9px;

                padding: 7px 10px;

                background: rgba(
                    70,
                    150,
                    255,
                    .1
                );

                color: #70b7ff;

                cursor: pointer;

                font-size: 12px;

            }


            /* =================================================
               LEVELS
               ================================================= */

            .mw-ai-levels {

                display: grid;

                grid-template-columns:
                    repeat(4, minmax(0, 1fr));

                gap: 8px;

            }


            .mw-ai-level {

                min-width: 0;

                border: 1px solid rgba(
                    255,
                    255,
                    255,
                    .08
                );

                border-radius: 11px;

                padding: 10px 7px;

                background: rgba(
                    255,
                    255,
                    255,
                    .035
                );

                color: #dbeafe;

                cursor: pointer;

                display: flex;

                flex-direction: column;

                align-items: center;

                gap: 5px;

                font-size: 12px;

                transition: .16s ease;

            }


            .mw-ai-level:hover {

                background: rgba(
                    78,
                    161,
                    255,
                    .08
                );

            }


            .mw-ai-level.selected {

                border-color: #4ea1ff;

                background: rgba(
                    78,
                    161,
                    255,
                    .14
                );

                box-shadow:
                    0 0 18px rgba(
                        78,
                        161,
                        255,
                        .08
                    );

            }


            /* =================================================
               RANGE
               ================================================= */

            .mw-ai-range {

                width: 100%;

                accent-color: #4ea1ff;

                cursor: pointer;

            }


            .mw-ai-range-labels {

                display: flex;

                justify-content: space-between;

                color: #64748b;

                font-size: 11px;

            }


            .mw-ai-count-value {

                min-width: 38px;

                padding: 5px 8px;

                border-radius: 8px;

                background: rgba(
                    78,
                    161,
                    255,
                    .12
                );

                color: #70b7ff;

                font-weight: 800;

                text-align: center;

            }


            /* =================================================
               BUTTONS
               ================================================= */

            .mw-ai-form-actions,
            .mw-ai-actions,
            .mw-ai-result-actions {

                display: flex;

                gap: 10px;

            }


            .mw-ai-form-actions {

                margin-top: 5px;

            }


            .mw-ai-generate,
            .mw-ai-submit,
            .mw-ai-secondary,
            .mw-ai-back {

                min-height: 45px;

                padding: 10px 16px;

                border: 0;

                border-radius: 12px;

                font-weight: 800;

                cursor: pointer;

                transition:
                    filter .18s ease,
                    transform .18s ease,
                    background .18s ease;

            }


            .mw-ai-generate,
            .mw-ai-submit {

                background:
                    linear-gradient(
                        135deg,
                        #267cff,
                        #6d5cff
                    );

                color: #fff;

                box-shadow:
                    0 8px 24px rgba(
                        45,
                        110,
                        255,
                        .18
                    );

            }


            .mw-ai-generate {

                flex: 1;

                display: flex;

                align-items: center;

                justify-content: center;

                gap: 9px;

            }


            .mw-ai-generate:hover,
            .mw-ai-submit:hover {

                filter: brightness(1.08);

                transform: translateY(-1px);

            }


            .mw-ai-secondary,
            .mw-ai-back {

                background: rgba(
                    255,
                    255,
                    255,
                    .07
                );

                color: #e2e8f0;

            }


            .mw-ai-secondary:hover,
            .mw-ai-back:hover {

                background: rgba(
                    255,
                    255,
                    255,
                    .11
                );

            }


            .mw-ai-back {

                min-width: 125px;

            }


            .mw-ai-submit {

                flex: 1;

            }


            .mw-ai-submit:disabled,
            .mw-ai-secondary:disabled,
            .mw-ai-back:disabled {

                opacity: .55;

                cursor: not-allowed;

                transform: none;

            }


            /* =================================================
               ERROR
               ================================================= */

            .mw-ai-error {

                margin-bottom: 15px;

                padding: 11px 13px;

                border: 1px solid rgba(
                    248,
                    113,
                    113,
                    .22
                );

                border-radius: 11px;

                background: rgba(
                    248,
                    113,
                    113,
                    .1
                );

                color: #fca5a5;

                font-size: 13px;

                line-height: 1.5;

            }


            /* =================================================
               LOADING
               ================================================= */

            .mw-ai-loading {

                min-height: 380px;

                padding: 45px 25px;

                display: flex;

                flex-direction: column;

                align-items: center;

                justify-content: center;

                text-align: center;

            }


            .mw-ai-spinner {

                width: 50px;

                height: 50px;

                margin-bottom: 20px;

                border: 4px solid rgba(
                    255,
                    255,
                    255,
                    .1
                );

                border-top-color: #55aaff;

                border-right-color: #7c5cff;

                border-radius: 50%;

                animation:
                    mwAiSpin .8s linear infinite;

            }


            @keyframes mwAiSpin {

                to {
                    transform: rotate(360deg);
                }

            }


            .mw-ai-loading-title {

                font-size: 20px;

                font-weight: 800;

            }


            .mw-ai-loading-text {

                max-width: 470px;

                margin-top: 10px;

                color: #94a3b8;

                font-size: 14px;

                line-height: 1.6;

            }


            .mw-ai-loading-info {

                margin-top: 18px;

                color: #70b7ff;

                font-size: 13px;

            }


            /* =================================================
               PROGRESS
               ================================================= */

            .mw-ai-progress {

                height: 5px;

                background: rgba(
                    255,
                    255,
                    255,
                    .07
                );

            }


            .mw-ai-progress-bar {

                height: 100%;

                background:
                    linear-gradient(
                        90deg,
                        #32a4ff,
                        #8a5cff
                    );

                transition: width .2s ease;

            }


            /* =================================================
               QUIZ
               ================================================= */

            .mw-ai-quiz {

                padding: 23px 26px 27px;

            }


            .mw-ai-question-meta {

                display: flex;

                gap: 7px;

                flex-wrap: wrap;

                margin-bottom: 15px;

            }


            .mw-ai-badge {

                display: inline-flex;

                align-items: center;

                min-height: 27px;

                padding: 4px 9px;

                border-radius: 999px;

                background: rgba(
                    78,
                    161,
                    255,
                    .1
                );

                color: #7cc0ff;

                font-size: 11px;

                font-weight: 700;

            }


            .mw-ai-question {

                margin-bottom: 22px;

                font-size: 19px;

                font-weight: 750;

                line-height: 1.6;

            }


            /* =================================================
               OPTIONS
               ================================================= */

            .mw-ai-options {

                display: grid;

                gap: 9px;

            }


            .mw-ai-option {

                width: 100%;

                min-height: 51px;

                display: flex;

                align-items: center;

                gap: 12px;

                padding: 12px;

                border: 1px solid rgba(
                    255,
                    255,
                    255,
                    .08
                );

                border-radius: 12px;

                background: rgba(
                    255,
                    255,
                    255,
                    .035
                );

                color: #e2e8f0;

                cursor: pointer;

                text-align: left;

                transition: .16s ease;

            }


            .mw-ai-option:hover {

                border-color: rgba(
                    78,
                    161,
                    255,
                    .3
                );

                background: rgba(
                    78,
                    161,
                    255,
                    .09
                );

            }


            .mw-ai-option.selected {

                border-color: #55aaff;

                background: rgba(
                    78,
                    161,
                    255,
                    .14
                );

            }


            .mw-ai-option-letter {

                width: 30px;

                height: 30px;

                flex: 0 0 auto;

                display: inline-flex;

                align-items: center;

                justify-content: center;

                border-radius: 9px;

                background: rgba(
                    255,
                    255,
                    255,
                    .07
                );

                color: #9dccff;

                font-weight: 800;

            }


            /* =================================================
               TRUE / FALSE
               ================================================= */

            .mw-ai-statements {

                display: grid;

                gap: 11px;

            }


            .mw-ai-statement {

                padding: 12px;

                border: 1px solid rgba(
                    255,
                    255,
                    255,
                    .07
                );

                border-radius: 12px;

                background: rgba(
                    255,
                    255,
                    255,
                    .035
                );

            }


            .mw-ai-statement-text {

                margin-bottom: 10px;

                font-size: 14px;

                line-height: 1.55;

            }


            .mw-ai-tf-buttons {

                display: flex;

                gap: 8px;

            }


            .mw-ai-tf {

                flex: 1;

                padding: 9px;

                border: 1px solid rgba(
                    255,
                    255,
                    255,
                    .09
                );

                border-radius: 9px;

                background: rgba(
                    255,
                    255,
                    255,
                    .04
                );

                color: #fff;

                cursor: pointer;

            }


            .mw-ai-tf.selected {

                border-color: #55aaff;

                background: rgba(
                    78,
                    161,
                    255,
                    .14
                );

            }


            /* =================================================
               ANSWER / FEEDBACK
               ================================================= */

            .mw-ai-answer-area {

                margin-bottom: 16px;

            }


            .mw-ai-feedback {

                margin: 14px 0;

                padding: 13px;

                border-radius: 12px;

                line-height: 1.55;

            }


            .mw-ai-feedback.correct {

                border: 1px solid rgba(
                    34,
                    197,
                    94,
                    .2
                );

                background: rgba(
                    34,
                    197,
                    94,
                    .1
                );

                color: #bbf7d0;

            }


            .mw-ai-feedback.wrong,
            .mw-ai-feedback.error {

                border: 1px solid rgba(
                    248,
                    113,
                    113,
                    .2
                );

                background: rgba(
                    248,
                    113,
                    113,
                    .09
                );

                color: #fecaca;

            }


            .mw-ai-feedback.warning {

                border: 1px solid rgba(
                    251,
                    191,
                    36,
                    .18
                );

                background: rgba(
                    251,
                    191,
                    36,
                    .08
                );

                color: #fde68a;

            }


            .mw-ai-feedback-title {

                margin-bottom: 5px;

                font-weight: 800;

            }


            .mw-ai-correct-answer {

                margin-top: 9px;

            }


            .mw-ai-solution {

                margin-top: 10px;

                padding-top: 10px;

                border-top: 1px solid rgba(
                    255,
                    255,
                    255,
                    .08
                );

            }


            .mw-ai-actions {

                justify-content: space-between;

                margin-top: 17px;

            }


            /* =================================================
               RESULT
               ================================================= */

            .mw-ai-result {

                padding: 38px 26px 32px;

                text-align: center;

            }


            .mw-ai-result-icon {

                margin-bottom: 8px;

                font-size: 55px;

            }


            .mw-ai-result-title {

                font-size: 27px;

                font-weight: 900;

            }


            .mw-ai-result-subtitle {

                margin-top: 6px;

                color: #94a3b8;

            }


            .mw-ai-result-score {

                margin: 23px auto;

                color: #70b7ff;

                font-size: 40px;

                font-weight: 900;

            }


            .mw-ai-result-score span {

                color: #94a3b8;

                font-size: 15px;

            }


            .mw-ai-result-grid {

                display: grid;

                grid-template-columns:
                    repeat(4, minmax(0, 1fr));

                gap: 9px;

                margin-bottom: 18px;

            }


            .mw-ai-stat {

                padding: 12px 7px;

                border-radius: 11px;

                background: rgba(
                    255,
                    255,
                    255,
                    .04
                );

                display: flex;

                flex-direction: column;

                gap: 5px;

            }


            .mw-ai-stat span {

                color: #94a3b8;

                font-size: 11px;

            }


            .mw-ai-stat b {

                font-size: 19px;

            }


            .mw-ai-stat b.correct {

                color: #4ade80;

            }


            .mw-ai-stat b.wrong {

                color: #fb7185;

            }


            .mw-ai-result-percent {

                color: #cbd5e1;

                font-size: 14px;

            }


            .mw-ai-result-actions {

                margin-top: 24px;

            }


            .mw-ai-result-actions > * {

                flex: 1;

            }


            /* =================================================
               EMPTY
               ================================================= */

            .mw-ai-empty {

                grid-column: 1 / -1;

                padding: 20px;

                border-radius: 11px;

                background: rgba(
                    255,
                    255,
                    255,
                    .035
                );

                color: #94a3b8;

                font-size: 13px;

                text-align: center;

            }


            /* =================================================
               MOBILE
               ================================================= */

            @media (max-width: 650px) {

                .mw-ai-header,
                .mw-ai-body,
                .mw-ai-quiz {

                    padding-left: 15px;

                    padding-right: 15px;

                }


                .mw-ai-topic-list {

                    grid-template-columns: 1fr;

                }


                .mw-ai-levels {

                    grid-template-columns:
                        repeat(2, 1fr);

                }


                .mw-ai-result-grid {

                    grid-template-columns:
                        repeat(2, 1fr);

                }


                .mw-ai-question {

                    font-size: 17px;

                }


                .mw-ai-form-actions,
                .mw-ai-result-actions {

                    flex-direction: column;

                }


                .mw-ai-back {

                    width: 100%;

                }


                .mw-ai-generate {

                    width: 100%;

                }

            }
        `;


        document.head.appendChild(
            style
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
            init,
            {
                once: true
            }
        );

    } else {

        init();
    }

})();