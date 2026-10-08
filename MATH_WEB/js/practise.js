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
        "http://127.0.0.1:8000";

    const AI_API =
        API_BASE + "/api/ai";


    const MAX_PRACTICE_COUNT = 30;

    const DEFAULT_GRADE = 12;

    const DEFAULT_DIFFICULTY = "medium";

    const DEFAULT_QUESTION_TYPE = "multiple_choice";

    const DEFAULT_COUNT = 10;


    /* =====================================================
       KNOWLEDGE DATA
    ===================================================== */

    const knowledgeData = [

        {
            id: 1,
            code: "PROBABILITY",
            name: "Xác suất",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Ôn tập cách xác định không gian mẫu, biến cố và tính xác suất trong các tình huống thực tế.",
            games: [
                {
                    name: "Bốc bi",
                    icon: "🔮",
                    path: "../games/probability/marble.html"
                },
                {
                    name: "Xúc xắc",
                    icon: "🎲",
                    path: "../games/probability/dice.html"
                },
                {
                    name: "Chọn tình huống",
                    icon: "🎯",
                    path: "../games/probability/situation.html"
                }
            ]
        },

        {
            id: 2,
            code: "COMBINATION",
            name: "Tổ hợp",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện tập cách lựa chọn đối tượng mà không quan tâm đến thứ tự và áp dụng công thức tổ hợp.",
            games: [
                {
                    name: "Chọn đội",
                    icon: "👥",
                    path: "../games/combination/team.html"
                },
                {
                    name: "Ghép lựa chọn",
                    icon: "🧩",
                    path: "../games/combination/choice.html"
                },
                {
                    name: "Săn tổ hợp",
                    icon: "🔎",
                    path: "../games/combination/hunt.html"
                }
            ]
        },

        {
            id: 3,
            code: "PERMUTATION",
            name: "Chỉnh hợp",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện cách chọn và sắp xếp các phần tử khi thứ tự của chúng có ý nghĩa.",
            games: [
                {
                    name: "Xếp vị trí",
                    icon: "📍",
                    path: "../games/permutation/position.html"
                },
                {
                    name: "Mật mã",
                    icon: "🔐",
                    path: "../games/permutation/code.html"
                },
                {
                    name: "Sắp thứ tự",
                    icon: "📋",
                    path: "../games/permutation/order.html"
                }
            ]
        },

        {
            id: 4,
            code: "FUNCTION",
            name: "Hàm số",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện đọc, tính toán và phân tích hàm số thông qua bảng giá trị, biểu thức và đồ thị.",
            games: [
                {
                    name: "Bắt điểm",
                    icon: "🎯",
                    path: "../games/function/point.html"
                },
                {
                    name: "Tìm giao điểm",
                    icon: "✖️",
                    path: "../games/function/intersection.html"
                },
                {
                    name: "Đồ thị bí ẩn",
                    icon: "📈",
                    path: "../games/function/graph.html"
                }
            ]
        },

        {
            id: 5,
            code: "SYSTEM_EQUATION",
            name: "Hệ phương trình",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Giải và kiểm tra nghiệm của hệ phương trình bằng các phương pháp phù hợp.",
            games: [
                {
                    name: "Điều tra",
                    icon: "🕵️",
                    path: "../games/system-equation/investigation.html"
                },
                {
                    name: "Tìm giá trị",
                    icon: "🔢",
                    path: "../games/system-equation/value.html"
                },
                {
                    name: "Ghép đáp án",
                    icon: "🧩",
                    path: "../games/system-equation/match.html"
                }
            ]
        },

        {
            id: 6,
            code: "QUADRATIC_EQUATION",
            name: "Phương trình bậc hai",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện giải phương trình bậc hai, tính biệt thức và xác định nghiệm.",
            games: [
                {
                    name: "Săn nghiệm",
                    icon: "🎯",
                    path: "../games/quadratic-equation/root.html"
                },
                {
                    name: "Ghép nghiệm",
                    icon: "🧩",
                    path: "../games/quadratic-equation/match.html"
                },
                {
                    name: "Mở khóa",
                    icon: "🔓",
                    path: "../games/quadratic-equation/unlock.html"
                }
            ]
        },

        {
            id: 7,
            code: "INEQUALITY",
            name: "Bất phương trình",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện giải bất phương trình và biểu diễn tập nghiệm trên trục số.",
            games: [
                {
                    name: "Vùng an toàn",
                    icon: "🛡️",
                    path: "../games/inequality/safe-zone.html"
                },
                {
                    name: "Chọn khoảng",
                    icon: "📏",
                    path: "../games/inequality/interval.html"
                },
                {
                    name: "Vượt rào",
                    icon: "🚧",
                    path: "../games/inequality/barrier.html"
                }
            ]
        },

        {
            id: 8,
            code: "SEQUENCE",
            name: "Dãy số",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Tìm quy luật, số hạng và mối quan hệ giữa các phần tử trong dãy số.",
            games: [
                {
                    name: "Tìm quy luật",
                    icon: "🔍",
                    path: "../games/sequence/rule.html"
                },
                {
                    name: "Điền số",
                    icon: "🔢",
                    path: "../games/sequence/fill.html"
                },
                {
                    name: "Đường đua dãy số",
                    icon: "🏁",
                    path: "../games/sequence/race.html"
                }
            ]
        },

        {
            id: 9,
            code: "DIVISIBILITY",
            name: "Chia hết",
            category: "SỐ HỌC",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện nhận biết và vận dụng các dấu hiệu chia hết để xử lý nhanh các bài toán số học.",
            games: [
                {
                    name: "Truy tìm số",
                    icon: "🔎",
                    path: "../games/divisibility/find.html"
                },
                {
                    name: "Chọn số",
                    icon: "🎯",
                    path: "../games/divisibility/select.html"
                },
                {
                    name: "Phá khóa",
                    icon: "🔐",
                    path: "../games/divisibility/unlock.html"
                }
            ]
        },

        {
            id: 10,
            code: "REMAINDER",
            name: "Chia dư",
            category: "SỐ HỌC",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện xác định số dư và vận dụng quy tắc chia dư trong các bài toán số học.",
            games: [
                {
                    name: "Bốc số",
                    icon: "🎱",
                    path: "../games/remainder/draw.html"
                },
                {
                    name: "Săn số dư",
                    icon: "🔎",
                    path: "../games/remainder/hunt.html"
                },
                {
                    name: "Thử thách modulo",
                    icon: "%",
                    path: "../games/remainder/modulo.html"
                }
            ]
        },

        {
            id: 11,
            code: "RADICAL",
            name: "Căn thức",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện tính toán, rút gọn và biến đổi các biểu thức chứa căn thức.",
            games: [
                {
                    name: "Săn căn",
                    icon: "√",
                    path: "../games/radical/hunt.html"
                },
                {
                    name: "Rút gọn nhanh",
                    icon: "⚡",
                    path: "../games/radical/simplify.html"
                },
                {
                    name: "Mở khóa căn thức",
                    icon: "🔓",
                    path: "../games/radical/unlock.html"
                }
            ]
        },

        {
            id: 12,
            code: "IDENTITIES",
            name: "Hằng đẳng thức",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Nhận biết và vận dụng các hằng đẳng thức đáng nhớ để biến đổi biểu thức.",
            games: [
                {
                    name: "Ghép công thức",
                    icon: "🧩",
                    path: "../games/identities/match.html"
                },
                {
                    name: "Phá biểu thức",
                    icon: "💥",
                    path: "../games/identities/break.html"
                },
                {
                    name: "Công thức bí ẩn",
                    icon: "❓",
                    path: "../games/identities/mystery.html"
                }
            ]
        },

        {
            id: 13,
            code: "ALGEBRAIC_FRACTION",
            name: "Phân thức đại số",
            category: "ĐẠI SỐ",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện tìm điều kiện xác định, rút gọn và thực hiện phép toán với phân thức đại số.",
            games: [
                {
                    name: "Rút gọn",
                    icon: "➗",
                    path: "../games/algebraic-fraction/simplify.html"
                },
                {
                    name: "Tìm điều kiện",
                    icon: "🔎",
                    path: "../games/algebraic-fraction/condition.html"
                },
                {
                    name: "Phân thức tốc độ",
                    icon: "⚡",
                    path: "../games/algebraic-fraction/speed.html"
                }
            ]
        },

        {
            id: 14,
            code: "GEOMETRY",
            name: "Hình học",
            category: "HÌNH HỌC",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện nhận biết hình, tính góc, độ dài và giải quyết các tình huống hình học.",
            games: [
                {
                    name: "Tìm góc",
                    icon: "📐",
                    path: "../games/geometry/angle.html"
                },
                {
                    name: "Săn độ dài",
                    icon: "📏",
                    path: "../games/geometry/length.html"
                },
                {
                    name: "Bản đồ hình học",
                    icon: "🗺️",
                    path: "../games/geometry/map.html"
                }
            ]
        },

        {
            id: 15,
            code: "STATISTICS",
            name: "Thống kê",
            category: "THỐNG KÊ",
            level: "Cơ bản → Nâng cao",
            description:
                "Luyện đọc bảng số liệu, biểu đồ và phân tích các thông tin thống kê.",
            games: [
                {
                    name: "Đọc biểu đồ",
                    icon: "📊",
                    path: "../games/statistics/chart.html"
                },
                {
                    name: "Săn số liệu",
                    icon: "🔎",
                    path: "../games/statistics/data.html"
                },
                {
                    name: "Thử thách thống kê",
                    icon: "🏆",
                    path: "../games/statistics/challenge.html"
                }
            ]
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
        count: DEFAULT_COUNT
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

        if (
            !Number.isFinite(
                Number(knowledge.id)
            )
        ) {
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

    function renderKnowledge() {

        if (!hasRequiredDOM()) {

            console.error(
                "MATH WEB: Không tìm thấy đầy đủ DOM của practise.html."
            );

            return false;

        }

        knowledgeGrid.replaceChildren();

        knowledgeCount.textContent =
            String(
                knowledgeData.length
            );


        knowledgeData.forEach(
            function (knowledge, index) {

                if (
                    !isValidKnowledge(
                        knowledge
                    )
                ) {
                    return;
                }


                const card =
                    document.createElement(
                        "button"
                    );

                card.type =
                    "button";

                card.className =
                    "knowledge-card " +
                    cardColors[
                        index %
                        cardColors.length
                    ];


                card.setAttribute(
                    "aria-label",
                    "Kiến thức " +
                    knowledge.name
                );

                card.setAttribute(
                    "aria-haspopup",
                    "dialog"
                );

                card.setAttribute(
                    "aria-expanded",
                    "false"
                );


                const number =
                    document.createElement(
                        "span"
                    );

                number.className =
                    "knowledge-number";

                number.textContent =
                    formatNumber(
                        knowledge.id
                    );


                card.appendChild(
                    number
                );


                card.addEventListener(
                    "click",
                    function () {

                        openKnowledge(
                            knowledge,
                            card
                        );

                    }
                );


                knowledgeGrid.appendChild(
                    card
                );

            }
        );

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
            knowledge.games
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
            function (game) {

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
                    AI sẽ tạo bộ câu hỏi riêng cho bạn,
                    kiểm tra đáp án ở máy chủ và điều chỉnh
                    độ khó dựa trên kết quả làm bài.
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
                            Độ khó
                        </label>

                        <select id="mathwebAiDifficulty">

                            <option value="easy">
                                Dễ
                            </option>

                            <option value="medium" selected>
                                Vừa
                            </option>

                            <option value="hard">
                                Khó
                            </option>

                            <option value="expert">
                                Chuyên
                            </option>

                        </select>

                    </div>


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
                                Trả lời ngắn
                            </option>

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
            grade.value =
                String(
                    aiCurrentSettings.grade
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


        if (
            !currentKnowledge
        ) {

            showAIError(
                "Chưa xác định được chủ đề luyện tập."
            );

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
            count: count
        };


        renderAILoading(
            "AI đang tạo bộ câu hỏi..."
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
                                currentKnowledge.code
                            ],
                            count: count,
                            difficulty: difficulty,
                            question_type: questionType,
                            history: history
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


                <div class="mathweb-ai-question">
                    ${escapeHTML(
                        questionText
                    )}
                </div>


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

                <button
                    type="button"
                    class="mathweb-ai-btn mathweb-ai-btn-primary"
                    id="mathwebAiNext"
                >
                    ${
                        aiCurrentIndex + 1 >=
                        aiQuestions.length
                            ? "🏁 Xem kết quả"
                            : "Câu tiếp theo →"
                    }
                </button>

            </div>

        `;


        const next =
            document.getElementById(
                "mathwebAiNext"
            );


        if (next) {

            next.addEventListener(
                "click",
                function () {

                    nextAIQuestion();

                }
            );

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


                    <div class="mathweb-ai-result-score">
                        ${aiScore} XP
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