/* =========================================================
   MATH WEB
   BATTLE / PVP
   AI 2.0 + SERVER AUTHORITATIVE
   ========================================================= */

(function () {

    "use strict";


    /* =====================================================
       CONFIG
    ===================================================== */

    const BATTLE_API_URL =
        window.MATHWEB_API_BASE ||
        "http://127.0.0.1:8000";

    const BATTLE_CONFIG = {

        REQUEST_TIMEOUT: 15000,

        POLL_INTERVAL: 2500,

        RESULT_POLL_INTERVAL: 1800,

        ONLINE_TIMEOUT: 30000,

        MAX_MATCH_WAIT_SECONDS: 3600,

        MAX_GAME_TIME_SECONDS: 3600,

        MAX_QUESTIONS: 100,

        ANSWER_FEEDBACK_DELAY: 650,

        SKIP_FEEDBACK_DELAY: 450,

        WS_RECONNECT_DELAY: 1500,

        WS_MAX_RECONNECT_DELAY: 10000,

        WS_MAX_RECONNECT_ATTEMPTS: 20
    };


    /* =====================================================
       STATE
    ===================================================== */

    let currentMatchId = null;

    let currentMatch = null;

    let questions = [];

    let currentQuestionIndex = 0;

    let correct = 0;

    let wrong = 0;

    let blank = 0;

    let gameStartedAt = null;

    let currentQuestionStartedAt = null;

    let gameTimer = null;

    let matchmakingTimer = null;

    let randomPollTimer = null;

    let matchPollTimer = null;

    let invitePollTimer = null;

    let selectedAnswer = false;

    let startingInProgress = false;

    let gameFinished = false;

    let finishingGame = false;

    let resultShown = false;

    let openingMatch = false;

    let incomingInviteVisible = false;

    let answerSubmitting = false;

    let currentRequestController = null;

    let currentSearchController = null;

    let battleSocket = null;

    let socketReconnectTimer = null;

    let socketReconnectAttempts = 0;

    let socketManualClose = false;

    let opponentState = null;

    let finalResultData = null;


    /* =====================================================
       DOM HELPERS
    ===================================================== */

    function getElement(id) {
        return document.getElementById(id);
    }


    const battleMenu =
        getElement("battleMenu");

    const randomScreen =
        getElement("randomScreen");

    const friendsScreen =
        getElement("friendsScreen");

    const playerIdScreen =
        getElement("playerIdScreen");

    const inviteScreen =
        getElement("inviteScreen");

    const startingScreen =
        getElement("startingScreen");

    const gameScreen =
        getElement("gameScreen");

    const resultScreen =
        getElement("resultScreen");


    /* =====================================================
       AUTH
    ===================================================== */

    function getToken() {

        return localStorage.getItem(
            "mathweb_token"
        );
    }


    function authHeaders(includeJSON = false) {

        const token =
            getToken();

        const headers = {
            "Accept": "application/json"
        };

        if (token) {

            headers.Authorization =
                `Bearer ${token}`;
        }

        if (includeJSON) {

            headers["Content-Type"] =
                "application/json";
        }

        return headers;
    }


    function clearBattleAuthData() {

        localStorage.removeItem(
            "mathweb_token"
        );

        localStorage.removeItem(
            "mathweb_user"
        );

        localStorage.removeItem(
            "mathweb_profile"
        );
    }


    function checkLogin() {

        const token =
            getToken();

        if (!token) {

            window.location.replace(
                "login.html"
            );

            return false;
        }

        return true;
    }


    function handleUnauthorized() {

        clearBattleAuthData();

        clearAllTimers();

        closeBattleSocket(true);

        currentMatchId = null;

        currentMatch = null;

        window.location.replace(
            "login.html"
        );
    }


    /* =====================================================
       SCREEN
    ===================================================== */

    function showScreen(screen) {

        [
            battleMenu,
            randomScreen,
            friendsScreen,
            playerIdScreen,
            inviteScreen,
            startingScreen,
            gameScreen,
            resultScreen
        ].forEach(function (item) {

            if (item) {

                item.classList.add(
                    "hidden"
                );
            }
        });

        if (screen) {

            screen.classList.remove(
                "hidden"
            );
        }
    }


    /* =====================================================
       UTILS
    ===================================================== */

    function formatTime(seconds) {

        let safeSeconds =
            Number(seconds);

        if (
            !Number.isFinite(
                safeSeconds
            ) ||
            safeSeconds < 0
        ) {

            safeSeconds = 0;
        }

        safeSeconds =
            Math.floor(
                safeSeconds
            );

        const minutes =
            Math.floor(
                safeSeconds / 60
            );

        const remaining =
            safeSeconds % 60;

        return (
            String(minutes)
                .padStart(2, "0") +
            ":" +
            String(remaining)
                .padStart(2, "0")
        );
    }


    function escapeHTML(text) {

        const div =
            document.createElement(
                "div"
            );

        div.textContent =
            String(text ?? "");

        return div.innerHTML;
    }


    function isOnline(lastSeen) {

        if (!lastSeen) {
            return false;
        }

        const time =
            new Date(
                lastSeen
            ).getTime();

        if (
            Number.isNaN(time)
        ) {

            return false;
        }

        const difference =
            Date.now() - time;

        return (
            difference >= -5000 &&
            difference <=
                BATTLE_CONFIG.ONLINE_TIMEOUT
        );
    }


    function getProfile() {

        try {

            return JSON.parse(
                localStorage.getItem(
                    "mathweb_profile"
                ) || "{}"
            );

        } catch {

            return {};
        }
    }


    function getCurrentUserId() {

        const profile =
            getProfile();

        const id =
            Number(
                profile.id || 0
            );

        return (
            Number.isFinite(id) &&
            id > 0
        )
            ? id
            : 0;
    }


    function safeNumber(
        value,
        fallback = 0
    ) {

        const number =
            Number(value);

        return Number.isFinite(
            number
        )
            ? number
            : fallback;
    }


    function safeInteger(
        value,
        fallback = 0
    ) {

        const number =
            Number(value);

        if (
            !Number.isFinite(
                number
            )
        ) {

            return fallback;
        }

        return Math.trunc(
            number
        );
    }


    function showToast(
        message,
        type = "normal"
    ) {

        let toast =
            getElement(
                "battleToast"
            );

        if (!toast) {

            toast =
                document.createElement(
                    "div"
                );

            toast.id =
                "battleToast";

            toast.className =
                "battle-toast";

            document.body.appendChild(
                toast
            );
        }

        toast.className =
            `battle-toast ${type}`;

        toast.textContent =
            String(
                message || ""
            );

        if (
            showToast.timer
        ) {

            clearTimeout(
                showToast.timer
            );
        }

        requestAnimationFrame(
            function () {

                toast.classList.add(
                    "show"
                );
            }
        );

        showToast.timer =
            setTimeout(
                function () {

                    toast.classList.remove(
                        "show"
                    );

                },
                2800
            );
    }


    async function readJSON(
        response
    ) {

        try {

            return await response.json();

        } catch {

            return {};
        }
    }


    function getAPIErrorMessage(
        data,
        fallback
    ) {

        if (!data) {
            return fallback;
        }

        if (
            typeof data.detail ===
                "string" &&
            data.detail.trim()
        ) {

            return data.detail.trim();
        }

        if (
            typeof data.message ===
                "string" &&
            data.message.trim()
        ) {

            return data.message.trim();
        }

        if (
            typeof data.error ===
                "string" &&
            data.error.trim()
        ) {

            return data.error.trim();
        }

        if (
            Array.isArray(
                data.detail
            )
        ) {

            const messages =
                data.detail
                    .map(
                        function (item) {

                            if (
                                typeof item ===
                                "string"
                            ) {

                                return item;
                            }

                            if (
                                item &&
                                typeof item.msg ===
                                "string"
                            ) {

                                return item.msg;
                            }

                            return "";
                        }
                    )
                    .filter(Boolean);

            if (
                messages.length
            ) {

                return messages.join(
                    ", "
                );
            }
        }

        return fallback;
    }


    /* =====================================================
       API REQUEST
    ===================================================== */

    async function apiFetch(
        url,
        options = {},
        timeout =
            BATTLE_CONFIG.REQUEST_TIMEOUT
    ) {

        if (!getToken()) {

            handleUnauthorized();

            throw new Error(
                "Phiên đăng nhập đã hết."
            );
        }

        if (
            currentRequestController
        ) {

            try {

                currentRequestController.abort();

            } catch {
                // Không làm gián đoạn request mới.
            }
        }

        const controller =
            new AbortController();

        currentRequestController =
            controller;

        const timer =
            setTimeout(
                function () {

                    controller.abort();

                },
                timeout
            );

        try {

            const response =
                await fetch(
                    url,
                    {
                        ...options,
                        signal:
                            controller.signal
                    }
                );

            if (
                response.status ===
                401
            ) {

                handleUnauthorized();

                throw new Error(
                    "Phiên đăng nhập đã hết. Vui lòng đăng nhập lại."
                );
            }

            return response;

        } catch (error) {

            if (
                error.name ===
                "AbortError"
            ) {

                throw new Error(
                    "Kết nối máy chủ quá thời gian."
                );
            }

            if (
                error instanceof
                TypeError
            ) {

                throw new Error(
                    "Không thể kết nối đến máy chủ."
                );
            }

            throw error;

        } finally {

            clearTimeout(
                timer
            );

            if (
                currentRequestController ===
                controller
            ) {

                currentRequestController =
                    null;
            }
        }
    }


    /* =====================================================
       SEARCH REQUEST
    ===================================================== */

    function cancelSearchRequest() {

        if (
            currentSearchController
        ) {

            try {

                currentSearchController.abort();

            } catch {
                // Không làm gián đoạn UI.
            }

            currentSearchController =
                null;
        }
    }


    async function searchFetch(
        url,
        options = {}
    ) {

        cancelSearchRequest();

        const controller =
            new AbortController();

        currentSearchController =
            controller;

        const timer =
            setTimeout(
                function () {

                    controller.abort();

                },
                BATTLE_CONFIG.REQUEST_TIMEOUT
            );

        try {

            const response =
                await fetch(
                    url,
                    {
                        ...options,
                        signal:
                            controller.signal
                    }
                );

            if (
                response.status ===
                401
            ) {

                handleUnauthorized();

                throw new Error(
                    "Phiên đăng nhập đã hết."
                );
            }

            return response;

        } catch (error) {

            if (
                error.name ===
                "AbortError"
            ) {

                throw new Error(
                    "Yêu cầu tìm kiếm đã hết thời gian."
                );
            }

            if (
                error instanceof
                TypeError
            ) {

                throw new Error(
                    "Không thể kết nối đến máy chủ."
                );
            }

            throw error;

        } finally {

            clearTimeout(
                timer
            );

            if (
                currentSearchController ===
                controller
            ) {

                currentSearchController =
                    null;
            }
        }
    }


    /* =====================================================
       TIMER CLEANUP
    ===================================================== */

    function clearMatchmakingTimers() {

        if (
            matchmakingTimer
        ) {

            clearInterval(
                matchmakingTimer
            );

            matchmakingTimer =
                null;
        }

        if (
            randomPollTimer
        ) {

            clearInterval(
                randomPollTimer
            );

            randomPollTimer =
                null;
        }

        if (
            matchPollTimer
        ) {

            clearInterval(
                matchPollTimer
            );

            matchPollTimer =
                null;
        }

        if (
            invitePollTimer
        ) {

            clearInterval(
                invitePollTimer
            );

            invitePollTimer =
                null;
        }
    }


    function clearGameTimer() {

        if (gameTimer) {

            clearInterval(
                gameTimer
            );

            gameTimer =
                null;
        }
    }


    function clearAllTimers() {

        clearMatchmakingTimers();

        clearGameTimer();
    }


    /* =====================================================
       MATCH VALIDATION
    ===================================================== */

    function isValidMatchId(
        matchId
    ) {

        return (
            typeof matchId ===
                "string" &&
            matchId.trim().length > 0 &&
            matchId.length <= 200
        );
    }


    function normalizeMatchStatus(
        status
    ) {

        return String(
            status || ""
        )
            .trim()
            .toUpperCase();
    }


    function isActiveMatchStatus(
        status
    ) {

        const normalized =
            normalizeMatchStatus(
                status
            );

        return (
            normalized ===
                "INVITED" ||
            normalized ===
                "STARTING" ||
            normalized ===
                "PLAYING"
        );
    }


    function validateMatchData(
        match
    ) {

        if (
            !match ||
            typeof match !==
                "object"
        ) {

            return false;
        }

        if (
            !Array.isArray(
                match.players
            ) ||
            match.players.length <
                2
        ) {

            return false;
        }

        return true;
    }


    /* =====================================================
       QUESTION NORMALIZATION
       
       IMPORTANT:
       SERVER MUST NOT SEND `answer`.
       ===================================================== */

    function normalizeQuestions(
        rawQuestions
    ) {

        if (
            !Array.isArray(
                rawQuestions
            )
        ) {

            return [];
        }

        return rawQuestions
            .slice(
                0,
                BATTLE_CONFIG.MAX_QUESTIONS
            )
            .filter(
                function (question) {

                    return (
                        question &&
                        typeof question ===
                            "object" &&
                        typeof question.question ===
                            "string"
                    );
                }
            )
            .map(
                function (question) {

                    const normalized = {

                        id:
                            question.id ??
                            null,

                        type:
                            normalizeQuestionType(
                                question.type
                            ),

                        topic:
                            String(
                                question.topic ||
                                "Toán học"
                            ),

                        difficulty:
                            String(
                                question.difficulty ||
                                "easy"
                            ),

                        question:
                            String(
                                question.question ||
                                ""
                            ),

                        options:
                            Array.isArray(
                                question.options
                            )
                                ? question.options.map(
                                    function (
                                        option
                                    ) {

                                        return String(
                                            option
                                        );
                                    }
                                )
                                : []
                    };

                    return normalized;
                }
            );
    }


    function normalizeQuestionType(
        type
    ) {

        const normalized =
            String(
                type || ""
            )
                .trim()
                .toLowerCase();

        if (
            normalized ===
                "choice" ||
            normalized ===
                "mcq" ||
            normalized ===
                "multiple_choice" ||
            normalized ===
                "multiple-choice"
        ) {

            return "choice";
        }

        if (
            normalized ===
                "true_false" ||
            normalized ===
                "true-false" ||
            normalized ===
                "tf"
        ) {

            return "true_false";
        }

        if (
            normalized ===
                "short_answer" ||
            normalized ===
                "short-answer" ||
            normalized ===
                "short"
        ) {

            return "input";
        }

        return "input";
    }


    /* =====================================================
       RANDOM MATCH
    ===================================================== */

    async function joinRandom() {

        if (
            !checkLogin()
        ) {

            return;
        }

        if (
            openingMatch ||
            startingInProgress
        ) {

            return;
        }

        clearAllTimers();

        closeBattleSocket(
            true
        );

        currentMatchId =
            null;

        currentMatch =
            null;

        showScreen(
            randomScreen
        );

        const timerElement =
            getElement(
                "randomTimer"
            );

        const statusElement =
            getElement(
                "randomStatus"
            );

        let elapsed = 0;

        if (timerElement) {

            timerElement.textContent =
                "00:00";
        }

        if (statusElement) {

            statusElement.textContent =
                "Đang tìm một người chơi phù hợp...";
        }

        matchmakingTimer =
            setInterval(
                function () {

                    elapsed++;

                    if (timerElement) {

                        timerElement.textContent =
                            formatTime(
                                elapsed
                            );
                    }

                    if (
                        elapsed >=
                        BATTLE_CONFIG
                            .MAX_MATCH_WAIT_SECONDS
                    ) {

                        cancelRandom();

                        showToast(
                            "Đã hết thời gian tìm đối thủ.",
                            "normal"
                        );
                    }

                },
                1000
            );

        try {

            const response =
                await apiFetch(
                    `${BATTLE_API_URL}/api/matchmaking/random/join`,
                    {
                        method:
                            "POST",
                        headers:
                            authHeaders()
                    }
                );

            const data =
                await readJSON(
                    response
                );

            if (
                !response.ok
            ) {

                throw new Error(
                    getAPIErrorMessage(
                        data,
                        "Không thể tìm đối thủ."
                    )
                );
            }

            const status =
                normalizeMatchStatus(
                    data.status
                );

            if (
                (
                    status ===
                        "MATCHED" ||
                    status ===
                        "STARTING" ||
                    status ===
                        "PLAYING"
                ) &&
                data.match_id
            ) {

                clearMatchmakingTimers();

                if (
                    statusElement
                ) {

                    statusElement.textContent =
                        "⚔️ Đã tìm thấy đối thủ!";
                }

                await openMatch(
                    data.match_id
                );

                return;
            }

            if (
                statusElement
            ) {

                statusElement.textContent =
                    "🔎 Đang chờ người chơi khác...";
            }

            startRandomPolling();

        } catch (error) {

            clearMatchmakingTimers();

            if (
                statusElement
            ) {

                statusElement.textContent =
                    error.message;
            }

            showToast(
                "❌ " +
                error.message,
                "error"
            );
        }
    }


    function startRandomPolling() {

        if (
            randomPollTimer
        ) {

            return;
        }

        randomPollTimer =
            setInterval(
                async function () {

                    if (
                        currentMatchId ||
                        gameFinished
                    ) {

                        return;
                    }

                    try {

                        const response =
                            await fetch(
                                `${BATTLE_API_URL}/api/matchmaking/current`,
                                {
                                    headers:
                                        authHeaders()
                                }
                            );

                        if (
                            response.status ===
                            401
                        ) {

                            handleUnauthorized();

                            return;
                        }

                        const data =
                            await readJSON(
                                response
                            );

                        if (
                            data.match_id &&
                            data.status &&
                            normalizeMatchStatus(
                                data.status
                            ) !== "QUEUED"
                        ) {

                            clearMatchmakingTimers();

                            await openMatch(
                                data.match_id
                            );
                        }

                    } catch {
                        // Tiếp tục tìm trận.
                    }

                },
                BATTLE_CONFIG.POLL_INTERVAL
            );
    }


    async function cancelRandom() {

        clearMatchmakingTimers();

        try {

            const response =
                await fetch(
                    `${BATTLE_API_URL}/api/matchmaking/random/cancel`,
                    {
                        method:
                            "POST",
                        headers:
                            authHeaders()
                    }
                );

            if (
                response.status ===
                401
            ) {

                handleUnauthorized();

                return;
            }

        } catch {
            // Không làm gián đoạn UI.
        }

        currentMatchId =
            null;

        currentMatch =
            null;

        showToast(
            "Đã hủy tìm đối thủ.",
            "normal"
        );

        showScreen(
            battleMenu
        );
    }


    /* =====================================================
       FRIENDS
    ===================================================== */

    async function loadBattleFriends() {

        if (
            !checkLogin()
        ) {

            return;
        }

        clearAllTimers();

        showScreen(
            friendsScreen
        );

        const container =
            getElement(
                "battleFriendList"
            );

        if (!container) {
            return;
        }

        container.innerHTML =
            `
            <div class="battle-loading">
                <div class="small-loader"></div>
                Đang tải danh sách bạn bè...
            </div>
            `;

        try {

            const response =
                await apiFetch(
                    `${BATTLE_API_URL}/api/friends`,
                    {
                        headers:
                            authHeaders()
                    }
                );

            const friends =
                await readJSON(
                    response
                );

            if (
                !response.ok
            ) {

                throw new Error(
                    getAPIErrorMessage(
                        friends,
                        "Không thể tải bạn bè."
                    )
                );
            }

            if (
                !Array.isArray(
                    friends
                ) ||
                !friends.length
            ) {

                container.innerHTML =
                    `
                    <div class="empty-state">
                        <div class="empty-icon">
                            👥
                        </div>

                        <strong>
                            Chưa có bạn bè
                        </strong>

                        <p>
                            Hãy thêm bạn bè trước khi đấu PvP.
                        </p>
                    </div>
                    `;

                return;
            }

            container.innerHTML =
                "";

            friends.forEach(
                function (friend) {

                    if (!friend) {
                        return;
                    }

                    const item =
                        document.createElement(
                            "div"
                        );

                    item.className =
                        "battle-friend";

                    const online =
                        Boolean(
                            friend.online
                        );

                    item.innerHTML =
                        `
                        <div class="friend-main">

                            <div class="friend-avatar">
                                ${online
                                    ? "🟢"
                                    : "⚫"}
                            </div>

                            <div class="friend-info">

                                <strong>
                                    ${escapeHTML(
                                        friend.username
                                    )}
                                </strong>

                                <span>
                                    ${escapeHTML(
                                        friend.player_id
                                    )}
                                </span>

                                <small
                                    class="${
                                        online
                                            ? "online"
                                            : ""
                                    }"
                                >
                                    ${
                                        online
                                            ? "Đang online"
                                            : "Đang offline"
                                    }
                                </small>

                            </div>

                        </div>

                        <button
                            class="battle-main-button battle-invite-button"
                            ${
                                online
                                    ? ""
                                    : "disabled"
                            }
                            type="button"
                        >
                            ⚔️ Mời đấu
                        </button>
                        `;

                    const button =
                        item.querySelector(
                            ".battle-invite-button"
                        );

                    if (button) {

                        button.addEventListener(
                            "click",
                            function () {

                                invitePlayer(
                                    friend.player_id
                                );
                            }
                        );
                    }

                    container.appendChild(
                        item
                    );
                }
            );

        } catch (error) {

            container.innerHTML =
                `
                <div class="error-state">
                    ❌ ${
                        escapeHTML(
                            error.message
                        )
                    }
                </div>
                `;
        }
    }


    /* =====================================================
       PLAYER ID
    ===================================================== */

    async function searchPlayer() {

        if (
            !checkLogin()
        ) {

            return;
        }

        const input =
            getElement(
                "battlePlayerIdInput"
            );

        const result =
            getElement(
                "battlePlayerResult"
            );

        if (
            !input ||
            !result
        ) {

            return;
        }

        const playerId =
            input.value
                .trim()
                .toUpperCase();

        if (!playerId) {

            result.innerHTML =
                `
                <div class="error-state">
                    Vui lòng nhập Player ID.
                </div>
                `;

            return;
        }

        if (
            playerId.length >
            100
        ) {

            result.innerHTML =
                `
                <div class="error-state">
                    Player ID không hợp lệ.
                </div>
                `;

            return;
        }

        result.innerHTML =
            `
            <div class="battle-loading">
                🔎 Đang tìm người chơi...
            </div>
            `;

        try {

            const response =
                await searchFetch(
                    `${BATTLE_API_URL}/api/matchmaking/player?player_id=${encodeURIComponent(playerId)}`,
                    {
                        headers:
                            authHeaders()
                    }
                );

            const data =
                await readJSON(
                    response
                );

            if (
                !response.ok
            ) {

                throw new Error(
                    getAPIErrorMessage(
                        data,
                        "Không tìm thấy người chơi."
                    )
                );
            }

            const online =
                Boolean(
                    data.online
                ) ||
                isOnline(
                    data.last_seen
                );

            result.innerHTML =
                `
                <div class="player-result-card">

                    <div class="search-player-avatar">
                        👤
                    </div>

                    <div class="search-player-info">

                        <strong>
                            ${escapeHTML(
                                data.username
                            )}
                        </strong>

                        <span>
                            ${escapeHTML(
                                data.player_id
                            )}
                        </span>

                        <span>
                            Level ${
                                safeInteger(
                                    data.level,
                                    0
                                )
                            }
                        </span>

                        <span
                            class="${
                                online
                                    ? "online"
                                    : ""
                            }"
                        >
                            ${
                                online
                                    ? "🟢 Online"
                                    : "⚫ Offline"
                            }
                        </span>

                    </div>

                    <button
                        id="inviteSearchPlayer"
                        class="battle-main-button"
                        ${
                            online
                                ? ""
                                : "disabled"
                        }
                        type="button"
                    >
                        ⚔️ Mời đấu
                    </button>

                </div>
                `;

            const button =
                getElement(
                    "inviteSearchPlayer"
                );

            if (button) {

                button.addEventListener(
                    "click",
                    function () {

                        invitePlayer(
                            data.player_id
                        );
                    }
                );
            }

        } catch (error) {

            result.innerHTML =
                `
                <div class="error-state">
                    ❌ ${
                        escapeHTML(
                            error.message
                        )
                    }
                </div>
                `;
        }
    }


    /* =====================================================
       INVITE
    ===================================================== */

    async function invitePlayer(
        playerId
    ) {

        if (
            !checkLogin()
        ) {

            return;
        }

        if (!playerId) {
            return;
        }

        clearMatchmakingTimers();

        try {

            const response =
                await apiFetch(
                    `${BATTLE_API_URL}/api/matchmaking/invite`,
                    {
                        method:
                            "POST",
                        headers:
                            authHeaders(
                                true
                            ),
                        body:
                            JSON.stringify(
                                {
                                    player_id:
                                        String(
                                            playerId
                                        )
                                            .trim()
                                            .toUpperCase()
                                }
                            )
                    }
                );

            const data =
                await readJSON(
                    response
                );

            if (
                !response.ok
            ) {

                throw new Error(
                    getAPIErrorMessage(
                        data,
                        "Không thể gửi lời mời."
                    )
                );
            }

            if (
                !data.match_id
            ) {

                throw new Error(
                    "Máy chủ chưa trả về mã trận."
                );
            }

            currentMatchId =
                String(
                    data.match_id
                );

            showToast(
                "⚔️ Đã gửi lời mời đấu!",
                "success"
            );

            showOutgoingInviteWaiting(
                currentMatchId
            );

        } catch (error) {

            showToast(
                "❌ " +
                error.message,
                "error"
            );
        }
    }


    function showOutgoingInviteWaiting(
        matchId
    ) {

        clearMatchmakingTimers();

        showScreen(
            startingScreen
        );

        const text =
            getElement(
                "startingText"
            );

        const subtext =
            getElement(
                "startingSubtext"
            );

        const loader =
            document.querySelector(
                ".starting-loader"
            );

        if (text) {

            text.textContent =
                "⏳ Đang chờ đối phương chấp nhận...";
        }

        if (subtext) {

            subtext.textContent =
                "Bạn có thể chờ đối phương xác nhận lời mời.";
        }

        if (loader) {

            loader.classList.add(
                "active"
            );
        }

        matchPollTimer =
            setInterval(
                async function () {

                    try {

                        const response =
                            await fetch(
                                `${BATTLE_API_URL}/api/matchmaking/match/${encodeURIComponent(matchId)}`,
                                {
                                    headers:
                                        authHeaders()
                                }
                            );

                        if (
                            response.status ===
                            401
                        ) {

                            handleUnauthorized();

                            return;
                        }

                        const match =
                            await readJSON(
                                response
                            );

                        if (
                            !response.ok
                        ) {

                            return;
                        }

                        const status =
                            normalizeMatchStatus(
                                match.status
                            );

                        if (
                            status ===
                                "STARTING" ||
                            status ===
                                "PLAYING"
                        ) {

                            clearMatchmakingTimers();

                            await openMatch(
                                matchId
                            );

                            return;
                        }

                        if (
                            status ===
                                "CANCELLED" ||
                            status ===
                                "REJECTED" ||
                            status ===
                                "EXPIRED" ||
                            status ===
                                "FINISHED"
                        ) {

                            clearMatchmakingTimers();

                            showToast(
                                "Đối phương đã từ chối hoặc trận đã hủy.",
                                "error"
                            );

                            currentMatchId =
                                null;

                            currentMatch =
                                null;

                            showScreen(
                                battleMenu
                            );
                        }

                    } catch {
                        // Tiếp tục chờ.
                    }

                },
                BATTLE_CONFIG.POLL_INTERVAL
            );
    }


    /* =====================================================
       INCOMING INVITE
    ===================================================== */

    async function checkIncomingMatch() {

        if (
            !checkLogin()
        ) {

            return;
        }

        if (
            currentMatchId ||
            gameFinished ||
            openingMatch
        ) {

            return;
        }

        try {

            const response =
                await fetch(
                    `${BATTLE_API_URL}/api/matchmaking/current`,
                    {
                        headers:
                            authHeaders()
                    }
                );

            if (
                response.status ===
                401
            ) {

                handleUnauthorized();

                return;
            }

            const data =
                await readJSON(
                    response
                );

            if (
                !response.ok ||
                !data.match_id
            ) {

                return;
            }

            const status =
                normalizeMatchStatus(
                    data.status
                );

            if (
                status ===
                "INVITED"
            ) {

                showIncomingInvite(
                    data
                );

                return;
            }

            if (
                status ===
                    "STARTING" ||
                status ===
                    "PLAYING"
            ) {

                await openMatch(
                    data.match_id
                );
            }

        } catch {
            // Không làm gián đoạn trang.
        }
    }


    function showIncomingInvite(
        data
    ) {

        clearMatchmakingTimers();

        currentMatchId =
            String(
                data.match_id
            );

        const players =
            Array.isArray(
                data.players
            )
                ? data.players
                : [];

        const currentUserId =
            getCurrentUserId();

        let opponent =
            null;

        players.some(
            function (player) {

                if (
                    Number(
                        player?.id || 0
                    ) !==
                    currentUserId
                ) {

                    opponent =
                        player;

                    return true;
                }

                return false;
            }
        );

        if (!opponent) {

            opponent =
                players.length
                    ? players[0]
                    : null;
        }

        const nameElement =
            getElement(
                "inviteOpponentName"
            );

        const idElement =
            getElement(
                "inviteOpponentId"
            );

        if (nameElement) {

            nameElement.textContent =
                opponent
                    ? String(
                        opponent.username ||
                        "Một người chơi"
                    )
                    : "Một người chơi";
        }

        if (idElement) {

            idElement.textContent =
                opponent
                    ? String(
                        opponent.player_id ||
                        ""
                    )
                    : "";
        }

        incomingInviteVisible =
            true;

        showScreen(
            inviteScreen
        );

        startInvitePolling();
    }


    function startInvitePolling() {

        if (
            invitePollTimer
        ) {

            return;
        }

        invitePollTimer =
            setInterval(
                async function () {

                    try {

                        const response =
                            await fetch(
                                `${BATTLE_API_URL}/api/matchmaking/current`,
                                {
                                    headers:
                                        authHeaders()
                                }
                            );

                        if (
                            response.status ===
                            401
                        ) {

                            handleUnauthorized();

                            return;
                        }

                        const data =
                            await readJSON(
                                response
                            );

                        if (
                            !response.ok
                        ) {

                            return;
                        }

                        if (
                            data.match_id &&
                            normalizeMatchStatus(
                                data.status
                            ) ===
                                "INVITED"
                        ) {

                            return;
                        }

                        if (
                            data.match_id &&
                            (
                                normalizeMatchStatus(
                                    data.status
                                ) ===
                                    "STARTING" ||
                                normalizeMatchStatus(
                                    data.status
                                ) ===
                                    "PLAYING"
                            )
                        ) {

                            clearMatchmakingTimers();

                            incomingInviteVisible =
                                false;

                            await openMatch(
                                data.match_id
                            );
                        }

                        if (
                            !data.match_id ||
                            normalizeMatchStatus(
                                data.status
                            ) ===
                                "CANCELLED" ||
                            normalizeMatchStatus(
                                data.status
                            ) ===
                                "REJECTED" ||
                            normalizeMatchStatus(
                                data.status
                            ) ===
                                "EXPIRED"
                        ) {

                            clearMatchmakingTimers();

                            incomingInviteVisible =
                                false;

                            currentMatchId =
                                null;

                            showScreen(
                                battleMenu
                            );
                        }

                    } catch {
                        // Tiếp tục kiểm tra.
                    }

                },
                BATTLE_CONFIG.POLL_INTERVAL
            );
    }


    /* =====================================================
       ACCEPT / REJECT INVITE
    ===================================================== */

    async function acceptInvite() {

        if (
            !currentMatchId
        ) {

            return;
        }

        try {

            const response =
                await apiFetch(
                    `${BATTLE_API_URL}/api/matchmaking/match/${encodeURIComponent(currentMatchId)}/accept`,
                    {
                        method:
                            "POST",
                        headers:
                            authHeaders(
                                true
                            ),
                        body:
                            JSON.stringify(
                                {}
                            )
                    }
                );

            const data =
                await readJSON(
                    response
                );

            if (
                !response.ok
            ) {

                throw new Error(
                    getAPIErrorMessage(
                        data,
                        "Không thể chấp nhận lời mời."
                    )
                );
            }

            clearMatchmakingTimers();

            incomingInviteVisible =
                false;

            showToast(
                "⚔️ Đã chấp nhận! Chuẩn bị trận đấu...",
                "success"
            );

            await openMatch(
                currentMatchId
            );

        } catch (error) {

            showToast(
                "❌ " +
                error.message,
                "error"
            );
        }
    }


    async function rejectInvite() {

        if (
            !currentMatchId
        ) {

            return;
        }

        try {

            const response =
                await apiFetch(
                    `${BATTLE_API_URL}/api/matchmaking/match/${encodeURIComponent(currentMatchId)}/reject`,
                    {
                        method:
                            "POST",
                        headers:
                            authHeaders(
                                true
                            ),
                        body:
                            JSON.stringify(
                                {}
                            )
                    }
                );

            const data =
                await readJSON(
                    response
                );

            if (
                !response.ok
            ) {

                throw new Error(
                    getAPIErrorMessage(
                        data,
                        "Không thể từ chối lời mời."
                    )
                );
            }

            clearMatchmakingTimers();

            incomingInviteVisible =
                false;

            showToast(
                "Đã từ chối lời mời.",
                "normal"
            );

            currentMatchId =
                null;

            currentMatch =
                null;

            showScreen(
                battleMenu
            );

        } catch (error) {

            showToast(
                "❌ " +
                error.message,
                "error"
            );
        }
    }


    /* =====================================================
       OPEN MATCH
    ===================================================== */

    async function openMatch(
        matchId
    ) {

        if (
            !isValidMatchId(
                String(
                    matchId || ""
                )
            )
        ) {

            showToast(
                "❌ Mã trận không hợp lệ.",
                "error"
            );

            return;
        }

        if (
            openingMatch
        ) {

            return;
        }

        openingMatch =
            true;

        currentMatchId =
            String(
                matchId
            );

        try {

            const response =
                await apiFetch(
                    `${BATTLE_API_URL}/api/matchmaking/match/${encodeURIComponent(currentMatchId)}`,
                    {
                        headers:
                            authHeaders()
                    }
                );

            const match =
                await readJSON(
                    response
                );

            if (
                !response.ok
            ) {

                throw new Error(
                    getAPIErrorMessage(
                        match,
                        "Không thể mở trận."
                    )
                );
            }

            if (
                !validateMatchData(
                    match
                )
            ) {

                throw new Error(
                    "Dữ liệu trận đấu không hợp lệ."
                );
            }

            currentMatch =
                match;

            renderPlayers(
                match.players
            );

            const status =
                normalizeMatchStatus(
                    match.status
                );

            if (
                status ===
                "PLAYING"
            ) {

                startGame();

                return;
            }

            if (
                status ===
                "FINISHED"
            ) {

                showToast(
                    "Trận đấu đã kết thúc.",
                    "normal"
                );

                await loadFinishedMatchResult();

                return;
            }

            if (
                status ===
                    "CANCELLED" ||
                status ===
                    "REJECTED" ||
                status ===
                    "EXPIRED"
            ) {

                showToast(
                    "Trận đấu đã bị hủy.",
                    "error"
                );

                showScreen(
                    battleMenu
                );

                return;
            }

            showStartingScreen(
                match
            );

        } catch (error) {

            showToast(
                "❌ " +
                error.message,
                "error"
            );

            showScreen(
                battleMenu
            );

        } finally {

            openingMatch =
                false;
        }
    }


    /* =====================================================
       STARTING
    ===================================================== */

    function showStartingScreen(
        match
    ) {

        clearMatchmakingTimers();

        showScreen(
            startingScreen
        );

        const text =
            getElement(
                "startingText"
            );

        const subtext =
            getElement(
                "startingSubtext"
            );

        const loader =
            document.querySelector(
                ".starting-loader"
            );

        if (loader) {

            loader.classList.add(
                "active"
            );
        }

        if (text) {

            text.textContent =
                "⚔️ Tìm thấy đối thủ!";
        }

        if (subtext) {

            subtext.textContent =
                "Hai người chơi đã sẵn sàng.";
        }

        if (
            startingInProgress
        ) {

            return;
        }

        startingInProgress =
            true;

        setTimeout(
            async function () {

                if (
                    !currentMatchId
                ) {

                    startingInProgress =
                        false;

                    return;
                }

                if (text) {

                    text.textContent =
                        "🔥 Chuẩn bị trận đấu...";
                }

                if (subtext) {

                    subtext.textContent =
                        "AI đang chuẩn bị bộ câu hỏi giống nhau cho cả hai người.";
                }

                try {

                    const response =
                        await fetch(
                            `${BATTLE_API_URL}/api/matchmaking/match/${encodeURIComponent(currentMatchId)}/start`,
                            {
                                method:
                                    "POST",
                                headers:
                                    authHeaders(
                                        true
                                    ),
                                body:
                                    JSON.stringify(
                                        {}
                                    )
                            }
                        );

                    if (
                        response.status ===
                        401
                    ) {

                        handleUnauthorized();

                        return;
                    }

                } catch {
                    // Refresh trạng thái trận ở bước tiếp theo.
                }

                setTimeout(
                    async function () {

                        startingInProgress =
                            false;

                        await refreshMatchAndStart();

                    },
                    800
                );

            },
            700
        );
    }


    async function refreshMatchAndStart() {

        if (
            !currentMatchId
        ) {

            return;
        }

        try {

            const response =
                await apiFetch(
                    `${BATTLE_API_URL}/api/matchmaking/match/${encodeURIComponent(currentMatchId)}`,
                    {
                        headers:
                            authHeaders()
                    }
                );

            const match =
                await readJSON(
                    response
                );

            if (
                !response.ok
            ) {

                throw new Error(
                    getAPIErrorMessage(
                        match,
                        "Không thể bắt đầu trận."
                    )
                );
            }

            currentMatch =
                match;

            const status =
                normalizeMatchStatus(
                    match.status
                );

            if (
                status ===
                "STARTING"
            ) {

                await waitForMatchToStart();

                return;
            }

            if (
                status ===
                "PLAYING"
            ) {

                startGame();

                return;
            }

            if (
                status ===
                    "CANCELLED" ||
                status ===
                    "REJECTED" ||
                status ===
                    "EXPIRED"
            ) {

                showToast(
                    "Trận đấu đã bị hủy.",
                    "error"
                );

                showScreen(
                    battleMenu
                );

                return;
            }

            showToast(
                "Trận đấu chưa sẵn sàng.",
                "error"
            );

            showScreen(
                battleMenu
            );

        } catch (error) {

            showToast(
                "❌ " +
                error.message,
                "error"
            );

            showScreen(
                battleMenu
            );
        }
    }


    function waitForMatchToStart() {

        return new Promise(
            function (resolve) {

                let attempts =
                    0;

                const maxAttempts =
                    40;

                const timer =
                    setInterval(
                        async function () {

                            attempts++;

                            if (
                                !currentMatchId
                            ) {

                                clearInterval(
                                    timer
                                );

                                resolve();

                                return;
                            }

                            try {

                                const response =
                                    await fetch(
                                        `${BATTLE_API_URL}/api/matchmaking/match/${encodeURIComponent(currentMatchId)}`,
                                        {
                                            headers:
                                                authHeaders()
                                        }
                                    );

                                if (
                                    response.status ===
                                    401
                                ) {

                                    clearInterval(
                                        timer
                                    );

                                    handleUnauthorized();

                                    resolve();

                                    return;
                                }

                                const match =
                                    await readJSON(
                                        response
                                    );

                                if (
                                    !response.ok
                                ) {

                                    return;
                                }

                                currentMatch =
                                    match;

                                const status =
                                    normalizeMatchStatus(
                                        match.status
                                    );

                                if (
                                    status ===
                                    "PLAYING"
                                ) {

                                    clearInterval(
                                        timer
                                    );

                                    startGame();

                                    resolve();

                                    return;
                                }

                                if (
                                    status ===
                                        "CANCELLED" ||
                                    status ===
                                        "REJECTED" ||
                                    status ===
                                        "EXPIRED"
                                ) {

                                    clearInterval(
                                        timer
                                    );

                                    showToast(
                                        "Trận đấu đã bị hủy.",
                                        "error"
                                    );

                                    showScreen(
                                        battleMenu
                                    );

                                    resolve();

                                    return;
                                }

                                if (
                                    attempts >=
                                    maxAttempts
                                ) {

                                    clearInterval(
                                        timer
                                    );

                                    showToast(
                                        "Không thể bắt đầu trận đấu.",
                                        "error"
                                    );

                                    showScreen(
                                        battleMenu
                                    );

                                    resolve();
                                }

                            } catch {

                                if (
                                    attempts >=
                                    maxAttempts
                                ) {

                                    clearInterval(
                                        timer
                                    );

                                    showToast(
                                        "Không thể xác nhận trạng thái trận.",
                                        "error"
                                    );

                                    showScreen(
                                        battleMenu
                                    );

                                    resolve();
                                }
                            }

                        },
                        1000
                    );
            }
        );
    }


    /* =====================================================
       PLAYERS
    ===================================================== */

    function renderPlayers(
        players
    ) {

        if (
            !Array.isArray(
                players
            ) ||
            players.length < 2
        ) {

            return;
        }

        const first =
            players[0] || {};

        const second =
            players[1] || {};

        const playerOneName =
            getElement(
                "playerOneName"
            );

        const playerOneLevel =
            getElement(
                "playerOneLevel"
            );

        const playerTwoName =
            getElement(
                "playerTwoName"
            );

        const playerTwoLevel =
            getElement(
                "playerTwoLevel"
            );

        if (
            playerOneName
        ) {

            playerOneName.textContent =
                String(
                    first.username ||
                    "Người chơi"
                );
        }

        if (
            playerOneLevel
        ) {

            playerOneLevel.textContent =
                `Level ${
                    safeInteger(
                        first.level,
                        0
                    )
                }`;
        }

        if (
            playerTwoName
        ) {

            playerTwoName.textContent =
                String(
                    second.username ||
                    "Người chơi"
                );
        }

        if (
            playerTwoLevel
        ) {

            playerTwoLevel.textContent =
                `Level ${
                    safeInteger(
                        second.level,
                        0
                    )
                }`;
        }
    }


    /* =====================================================
       GAME START
    ===================================================== */

    function startGame() {

        if (
            !currentMatch
        ) {

            return;
        }

        questions =
            normalizeQuestions(
                currentMatch.questions
            );

        if (
            !questions.length
        ) {

            showToast(
                "❌ Trận đấu chưa có bộ câu hỏi AI.",
                "error"
            );

            showScreen(
                battleMenu
            );

            return;
        }

        clearMatchmakingTimers();

        clearGameTimer();

        currentQuestionIndex =
            0;

        correct =
            0;

        wrong =
            0;

        blank =
            0;

        selectedAnswer =
            false;

        answerSubmitting =
            false;

        gameFinished =
            false;

        finishingGame =
            false;

        resultShown =
            false;

        finalResultData =
            null;

        opponentState =
            null;

        gameStartedAt =
            currentMatch.started_at
                ? new Date(
                    currentMatch.started_at
                ).getTime()
                : Date.now();

        if (
            !Number.isFinite(
                gameStartedAt
            )
        ) {

            gameStartedAt =
                Date.now();
        }

        currentQuestionStartedAt =
            Date.now();

        const timerElement =
            getElement(
                "battleGameTimer"
            );

        if (timerElement) {

            timerElement.textContent =
                "00:00";
        }

        showScreen(
            gameScreen
        );

        connectBattleSocket();

        startGameTimer();

        renderQuestion();
    }


    /* =====================================================
       GAME TIMER
    ===================================================== */

    function startGameTimer() {

        clearGameTimer();

        gameTimer =
            setInterval(
                function () {

                    if (
                        !gameStartedAt
                    ) {

                        return;
                    }

                    const seconds =
                        Math.floor(
                            (
                                Date.now() -
                                gameStartedAt
                            ) / 1000
                        );

                    const safeSeconds =
                        Math.min(
                            Math.max(
                                seconds,
                                0
                            ),
                            BATTLE_CONFIG
                                .MAX_GAME_TIME_SECONDS
                        );

                    const timerElement =
                        getElement(
                            "battleGameTimer"
                        );

                    if (
                        timerElement
                    ) {

                        timerElement.textContent =
                            formatTime(
                                safeSeconds
                            );
                    }

                    if (
                        seconds >=
                        BATTLE_CONFIG
                            .MAX_GAME_TIME_SECONDS
                    ) {

                        handleGameTimeout();
                    }

                },
                500
            );
    }


    function handleGameTimeout() {

        if (
            gameFinished ||
            finishingGame
        ) {

            return;
        }

        if (
            !selectedAnswer
        ) {

            submitAnswerToServer(
                null,
                true
            );
        }
    }


    /* =====================================================
       QUESTION
    ===================================================== */

    function renderQuestion() {

        if (
            gameFinished
        ) {

            return;
        }

        if (
            currentQuestionIndex >=
            questions.length
        ) {

            finishGame();

            return;
        }

        selectedAnswer =
            false;

        answerSubmitting =
            false;

        currentQuestionStartedAt =
            Date.now();

        const question =
            questions[
                currentQuestionIndex
            ];

        const numberElement =
            getElement(
                "battleQuestionNumber"
            );

        const totalElement =
            getElement(
                "battleTotalQuestions"
            );

        const topicElement =
            getElement(
                "questionTopic"
            );

        const difficultyElement =
            getElement(
                "questionDifficulty"
            );

        const textElement =
            getElement(
                "questionText"
            );

        const options =
            getElement(
                "questionOptions"
            );

        const input =
            getElement(
                "inputAnswer"
            );

        const submit =
            getElement(
                "submitInputAnswer"
            );

        const skip =
            getElement(
                "skipQuestionButton"
            );

        const feedback =
            getElement(
                "battleFeedback"
            );

        if (
            numberElement
        ) {

            numberElement.textContent =
                `Câu ${
                    currentQuestionIndex + 1
                }`;
        }

        if (
            totalElement
        ) {

            totalElement.textContent =
                questions.length;
        }

        if (
            topicElement
        ) {

            topicElement.textContent =
                question.topic ||
                "Toán học";
        }

        if (
            difficultyElement
        ) {

            difficultyElement.textContent =
                getDifficultyName(
                    question.difficulty
                );
        }

        if (
            textElement
        ) {

            textElement.textContent =
                question.question ||
                "";
        }

        if (options) {

            options.innerHTML =
                "";
        }

        if (feedback) {

            feedback.textContent =
                "";

            feedback.className =
                "battle-feedback";
        }

        if (input) {

            input.classList.add(
                "hidden"
            );

            input.value =
                "";

            input.disabled =
                false;
        }

        if (submit) {

            submit.classList.add(
                "hidden"
            );

            submit.disabled =
                false;
        }

        if (skip) {

            skip.disabled =
                false;
        }

        if (
            question.type ===
                "choice" &&
            Array.isArray(
                question.options
            ) &&
            question.options.length
        ) {

            if (!options) {
                return;
            }

            options.classList.remove(
                "hidden"
            );

            question.options.forEach(
                function (
                    option,
                    index
                ) {

                    const button =
                        document.createElement(
                            "button"
                        );

                    button.type =
                        "button";

                    button.className =
                        "question-option";

                    button.textContent =
                        option;

                    button.addEventListener(
                        "click",
                        function () {

                            answerQuestion(
                                index
                            );
                        }
                    );

                    options.appendChild(
                        button
                    );
                }
            );

        } else {

            if (options) {

                options.classList.add(
                    "hidden"
                );
            }

            if (input) {

                input.classList.remove(
                    "hidden"
                );

                setTimeout(
                    function () {

                        if (
                            !gameFinished &&
                            !selectedAnswer
                        ) {

                            input.focus();
                        }

                    },
                    50
                );
            }

            if (submit) {

                submit.classList.remove(
                    "hidden"
                );
            }
        }
    }


    function getDifficultyName(
        difficulty
    ) {

        const normalized =
            String(
                difficulty || ""
            )
                .toLowerCase();

        if (
            normalized ===
            "easy"
        ) {

            return "DỄ";
        }

        if (
            normalized ===
            "medium"
        ) {

            return "VỪA";
        }

        if (
            normalized ===
            "hard"
        ) {

            return "KHÓ";
        }

        if (
            normalized ===
            "expert"
        ) {

            return "CHUYÊN";
        }

        return "TOÁN";
    }


    /* =====================================================
       ANSWER
       
       Client DOES NOT know correct answer.
       ===================================================== */

    async function answerQuestion(
        answer
    ) {

        if (
            selectedAnswer ||
            gameFinished ||
            finishingGame ||
            answerSubmitting
        ) {

            return;
        }

        const question =
            questions[
                currentQuestionIndex
            ];

        if (
            !question ||
            !question.id
        ) {

            showToast(
                "❌ Câu hỏi không hợp lệ.",
                "error"
            );

            return;
        }

        await submitAnswerToServer(
            answer,
            false
        );
    }


    async function skipQuestion() {

        if (
            selectedAnswer ||
            gameFinished ||
            finishingGame ||
            answerSubmitting
        ) {

            return;
        }

        const question =
            questions[
                currentQuestionIndex
            ];

        if (
            !question ||
            !question.id
        ) {

            return;
        }

        await submitAnswerToServer(
            null,
            true
        );
    }


    async function submitAnswerToServer(
        answer,
        skipped = false
    ) {

        if (
            answerSubmitting ||
            selectedAnswer ||
            gameFinished
        ) {

            return;
        }

        const question =
            questions[
                currentQuestionIndex
            ];

        if (
            !question ||
            !question.id
        ) {

            return;
        }

        answerSubmitting =
            true;

        selectedAnswer =
            true;

        disableQuestionControls();

        const responseTime =
            currentQuestionStartedAt
                ? Math.max(
                    0,
                    Math.floor(
                        (
                            Date.now() -
                            currentQuestionStartedAt
                        ) / 1000
                    )
                )
                : 0;

        const feedback =
            getElement(
                "battleFeedback"
            );

        if (feedback) {

            feedback.textContent =
                skipped
                    ? "⏭️ Đang bỏ qua..."
                    : "⏳ Đang kiểm tra...";

            feedback.className =
                "battle-feedback";
        }

        try {

            const response =
                await apiFetch(
                    `${BATTLE_API_URL}/api/matchmaking/match/${encodeURIComponent(currentMatchId)}/answer`,
                    {
                        method:
                            "POST",

                        headers:
                            authHeaders(
                                true
                            ),

                        body:
                            JSON.stringify(
                                {
                                    question_id:
                                        String(
                                            question.id
                                        ),

                                    answer:
                                        skipped
                                            ? null
                                            : normalizeSubmittedAnswer(
                                                answer
                                            ),

                                    skipped:
                                        Boolean(
                                            skipped
                                        ),

                                    client_response_time:
                                        responseTime
                                }
                            )
                    }
                );

            const data =
                await readJSON(
                    response
                );

            if (
                !response.ok
            ) {

                throw new Error(
                    getAPIErrorMessage(
                        data,
                        "Không thể gửi câu trả lời."
                    )
                );
            }

            processServerAnswer(
                data,
                skipped
            );

        } catch (error) {

            selectedAnswer =
                false;

            answerSubmitting =
                false;

            enableAIAnswerControls();

            if (feedback) {

                feedback.textContent =
                    "❌ " +
                    error.message;

                feedback.className =
                    "battle-feedback wrong";
            }

            showToast(
                "❌ " +
                error.message,
                "error"
            );
        }
    }


    function normalizeSubmittedAnswer(
        answer
    ) {

        if (
            answer === null ||
            answer === undefined
        ) {

            return null;
        }

        if (
            typeof answer ===
            "boolean"
        ) {

            return answer;
        }

        if (
            typeof answer ===
            "number"
        ) {

            return answer;
        }

        return String(
            answer
        ).trim();
    }


    function processServerAnswer(
        data,
        skipped
    ) {

        const isCorrect =
            Boolean(
                data.correct
            );

        const isSkipped =
            Boolean(
                skipped ||
                data.skipped
            );

        if (isSkipped) {

            blank++;

            renderBattleFeedback(
                "⏭️ Bạn đã bỏ qua câu này.",
                "blank"
            );

        } else if (isCorrect) {

            correct++;

            renderBattleFeedback(
                "🌟 Chính xác!",
                "correct"
            );

        } else {

            wrong++;

            renderBattleFeedback(
                "😯 Chưa đúng rồi!",
                "wrong"
            );
        }

        updateOpponentState(
            data.opponent_progress
        );

        if (
            data.finished
        ) {

            setTimeout(
                function () {

                    finishGame();

                },
                BATTLE_CONFIG
                    .ANSWER_FEEDBACK_DELAY
            );

            return;
        }

        setTimeout(
            function () {

                nextQuestion();

            },
            isSkipped
                ? BATTLE_CONFIG
                    .SKIP_FEEDBACK_DELAY
                : BATTLE_CONFIG
                    .ANSWER_FEEDBACK_DELAY
        );
    }


    function renderBattleFeedback(
        message,
        type
    ) {

        const feedback =
            getElement(
                "battleFeedback"
            );

        if (!feedback) {
            return;
        }

        feedback.textContent =
            message;

        feedback.className =
            `battle-feedback ${type}`;
    }


    function disableQuestionControls() {

        document
            .querySelectorAll(
                ".question-option"
            )
            .forEach(
                function (button) {

                    button.disabled =
                        true;
                }
            );

        const submit =
            getElement(
                "submitInputAnswer"
            );

        const skip =
            getElement(
                "skipQuestionButton"
            );

        const input =
            getElement(
                "inputAnswer"
            );

        if (submit) {

            submit.disabled =
                true;
        }

        if (skip) {

            skip.disabled =
                true;
        }

        if (input) {

            input.disabled =
                true;
        }
    }


    function enableAIAnswerControls() {

        document
            .querySelectorAll(
                ".question-option"
            )
            .forEach(
                function (button) {

                    button.disabled =
                        false;
                }
            );

        const submit =
            getElement(
                "submitInputAnswer"
            );

        const skip =
            getElement(
                "skipQuestionButton"
            );

        const input =
            getElement(
                "inputAnswer"
            );

        if (submit) {

            submit.disabled =
                false;
        }

        if (skip) {

            skip.disabled =
                false;
        }

        if (input) {

            input.disabled =
                false;
        }
    }


    function nextQuestion() {

        if (
            gameFinished
        ) {

            return;
        }

        currentQuestionIndex++;

        if (
            currentQuestionIndex >=
            questions.length
        ) {

            finishGame();

            return;
        }

        renderQuestion();
    }


    /* =====================================================
       WEBSOCKET
    ===================================================== */

    function getWebSocketURL() {

        if (
            !currentMatchId
        ) {

            return null;
        }

        const userId =
            getCurrentUserId();

        if (
            !userId
        ) {

            return null;
        }

        let base =
            String(
                BATTLE_API_URL
            );

        base =
            base.replace(
                /^http:/i,
                "ws:"
            );

        base =
            base.replace(
                /^https:/i,
                "wss:"
            );

        return (
            `${base}/api/ai/battle/ws/` +
            `${encodeURIComponent(
                currentMatchId
            )}/` +
            `${encodeURIComponent(
                userId
            )}`
        );
    }


    function connectBattleSocket() {

        if (
            !currentMatchId ||
            gameFinished
        ) {

            return;
        }

        if (
            battleSocket &&
            (
                battleSocket.readyState ===
                    WebSocket.OPEN ||
                battleSocket.readyState ===
                    WebSocket.CONNECTING
            )
        ) {

            return;
        }

        const url =
            getWebSocketURL();

        if (!url) {
            return;
        }

        socketManualClose =
            false;

        try {

            battleSocket =
                new WebSocket(
                    url
                );

        } catch {

            scheduleSocketReconnect();

            return;
        }

        battleSocket.onopen =
            function () {

                socketReconnectAttempts =
                    0;

                clearSocketReconnectTimer();

                sendSocketEvent(
                    {
                        type:
                            "sync"
                    }
                );
            };


        battleSocket.onmessage =
            function (event) {

                handleSocketMessage(
                    event
                );
            };


        battleSocket.onerror =
            function () {
                // onclose xử lý reconnect.
            };


        battleSocket.onclose =
            function () {

                battleSocket =
                    null;

                if (
                    !socketManualClose &&
                    !gameFinished &&
                    currentMatchId
                ) {

                    scheduleSocketReconnect();
                }
            };
    }


    function handleSocketMessage(
        event
    ) {

        let data;

        try {

            data =
                JSON.parse(
                    event.data
                );

        } catch {

            return;
        }

        if (
            !data ||
            typeof data !==
                "object"
        ) {

            return;
        }

        const type =
            String(
                data.type || ""
            )
                .trim()
                .toLowerCase();

        if (
            type ===
                "player_progress" ||
            type ===
                "progress" ||
            type ===
                "battle_progress"
        ) {

            updateOpponentState(
                data.progress ||
                data
            );

            return;
        }

        if (
            type ===
                "state" ||
            type ===
                "battle_state" ||
            type ===
                "sync"
        ) {

            if (
                data.progress
            ) {

                updateOpponentState(
                    data.progress
                );
            }

            if (
                data.status
            ) {

                handleRealtimeStatus(
                    data.status,
                    data
                );
            }

            return;
        }

        if (
            type ===
                "player_joined"
        ) {

            return;
        }

        if (
            type ===
                "player_left"
        ) {

            showToast(
                "⚠️ Đối thủ vừa mất kết nối. Trận đấu vẫn được máy chủ giữ lại.",
                "normal"
            );

            return;
        }

        if (
            type ===
                "battle_finished" ||
            type ===
                "finished"
        ) {

            if (
                data.result
            ) {

                finalResultData =
                    data.result;
            }

            if (
                !gameFinished
            ) {

                gameFinished =
                    true;

                clearGameTimer();

                loadFinishedMatchResult();
            }

            return;
        }
    }


    function handleRealtimeStatus(
        status,
        data
    ) {

        const normalized =
            normalizeMatchStatus(
                status
            );

        if (
            normalized ===
            "FINISHED"
        ) {

            if (
                data.result
            ) {

                finalResultData =
                    data.result;
            }

            if (
                !resultShown
            ) {

                loadFinishedMatchResult();
            }

            return;
        }

        if (
            normalized ===
                "CANCELLED" ||
            normalized ===
                "REJECTED" ||
            normalized ===
                "EXPIRED"
        ) {

            if (
                !gameFinished
            ) {

                gameFinished =
                    true;

                clearGameTimer();

                showToast(
                    "Trận đấu đã kết thúc.",
                    "normal"
                );

                showScreen(
                    battleMenu
                );
            }
        }
    }


    function sendSocketEvent(
        payload
    ) {

        if (
            !battleSocket ||
            battleSocket.readyState !==
                WebSocket.OPEN
        ) {

            return false;
        }

        try {

            battleSocket.send(
                JSON.stringify(
                    payload
                )
            );

            return true;

        } catch {

            return false;
        }
    }


    function scheduleSocketReconnect() {

        if (
            socketManualClose ||
            gameFinished ||
            !currentMatchId
        ) {

            return;
        }

        if (
            socketReconnectTimer
        ) {

            return;
        }

        if (
            socketReconnectAttempts >=
            BATTLE_CONFIG
                .WS_MAX_RECONNECT_ATTEMPTS
        ) {

            return;
        }

        socketReconnectAttempts++;

        const attempt =
            socketReconnectAttempts;

        const delay =
            Math.min(
                BATTLE_CONFIG
                    .WS_RECONNECT_DELAY *
                    attempt,
                BATTLE_CONFIG
                    .WS_MAX_RECONNECT_DELAY
            );

        socketReconnectTimer =
            setTimeout(
                function () {

                    socketReconnectTimer =
                        null;

                    if (
                        !gameFinished &&
                        currentMatchId
                    ) {

                        connectBattleSocket();
                    }

                },
                delay
            );
    }


    function clearSocketReconnectTimer() {

        if (
            socketReconnectTimer
        ) {

            clearTimeout(
                socketReconnectTimer
            );

            socketReconnectTimer =
                null;
        }
    }


    function closeBattleSocket(
        manual = false
    ) {

        socketManualClose =
            Boolean(
                manual
            );

        clearSocketReconnectTimer();

        socketReconnectAttempts =
            0;

        if (
            battleSocket
        ) {

            try {

                battleSocket.close();

            } catch {
                // Socket đã đóng.
            }

            battleSocket =
                null;
        }
    }


    /* =====================================================
       OPPONENT PROGRESS
    ===================================================== */

    function updateOpponentState(
        progress
    ) {

        if (
            !progress ||
            typeof progress !==
                "object"
        ) {

            return;
        }

        opponentState =
            {
                correct:
                    safeInteger(
                        progress.correct,
                        0
                    ),

                wrong:
                    safeInteger(
                        progress.wrong,
                        0
                    ),

                blank:
                    safeInteger(
                        progress.blank,
                        0
                    ),

                answered:
                    safeInteger(
                        progress.answered,
                        0
                    ),

                total:
                    safeInteger(
                        progress.total,
                        questions.length
                    ),

                finished:
                    Boolean(
                        progress.finished
                    ),

                time:
                    safeInteger(
                        progress.time,
                        0
                    )
            };

        renderOpponentProgress();
    }


    function renderOpponentProgress() {

        if (
            !opponentState
        ) {

            return;
        }

        const selectors = [
            "opponentProgress",
            "battleOpponentProgress"
        ];

        let element =
            null;

        for (
            let i = 0;
            i < selectors.length;
            i++
        ) {

            element =
                getElement(
                    selectors[i]
                );

            if (element) {
                break;
            }
        }

        if (!element) {
            return;
        }

        const total =
            Math.max(
                1,
                safeInteger(
                    opponentState.total,
                    questions.length
                )
            );

        const answered =
            Math.min(
                total,
                Math.max(
                    0,
                    safeInteger(
                        opponentState.answered,
                        0
                    )
                )
            );

        const percent =
            Math.round(
                (
                    answered /
                    total
                ) * 100
            );

        element.textContent =
            `${answered}/${total} câu • ${percent}%`;
    }


    /* =====================================================
       FINISH GAME
    ===================================================== */

    async function finishGame() {

        if (
            finishingGame ||
            resultShown
        ) {

            return;
        }

        finishingGame =
            true;

        gameFinished =
            true;

        clearGameTimer();

        clearMatchmakingTimers();

        const resultIcon =
            getElement(
                "resultIcon"
            );

        const resultTitle =
            getElement(
                "resultTitle"
            );

        const resultText =
            getElement(
                "resultText"
            );

        if (resultIcon) {

            resultIcon.textContent =
                "⏳";
        }

        if (resultTitle) {

            resultTitle.textContent =
                "Đang xác nhận kết quả...";

            resultTitle.className =
                "result-title";
        }

        if (resultText) {

            resultText.textContent =
                "Máy chủ đang hoàn tất trận đấu.";
        }

        showScreen(
            resultScreen
        );

        sendSocketEvent(
            {
                type:
                    "finished"
            }
        );

        await loadFinishedMatchResult();

        finishingGame =
            false;
    }


    async function loadFinishedMatchResult() {

        if (
            resultShown
        ) {

            return;
        }

        if (
            !currentMatchId
        ) {

            showToast(
                "❌ Không tìm thấy mã trận.",
                "error"
            );

            return;
        }

        if (
            finalResultData
        ) {

            showResult(
                finalResultData
            );

            return;
        }

        showScreen(
            resultScreen
        );

        const resultIcon =
            getElement(
                "resultIcon"
            );

        const resultTitle =
            getElement(
                "resultTitle"
            );

        const resultText =
            getElement(
                "resultText"
            );

        if (resultIcon) {

            resultIcon.textContent =
                "⏳";
        }

        if (resultTitle) {

            resultTitle.textContent =
                "Đang chờ kết quả";

            resultTitle.className =
                "result-title";
        }

        if (resultText) {

            resultText.textContent =
                "Máy chủ đang chờ cả hai người chơi hoàn thành.";
        }

        if (
            matchPollTimer
        ) {

            clearInterval(
                matchPollTimer
            );

            matchPollTimer =
                null;
        }

        let resultElapsed =
            0;

        matchPollTimer =
            setInterval(
                async function () {

                    resultElapsed++;

                    if (
                        resultElapsed >
                        BATTLE_CONFIG
                            .MAX_MATCH_WAIT_SECONDS
                    ) {

                        clearInterval(
                            matchPollTimer
                        );

                        matchPollTimer =
                            null;

                        showToast(
                            "⚠️ Không thể nhận kết quả cuối cùng.",
                            "error"
                        );

                        return;
                    }

                    try {

                        const response =
                            await fetch(
                                `${BATTLE_API_URL}/api/matchmaking/match/${encodeURIComponent(currentMatchId)}`,
                                {
                                    headers:
                                        authHeaders()
                                }
                            );

                        if (
                            response.status ===
                            401
                        ) {

                            clearInterval(
                                matchPollTimer
                            );

                            matchPollTimer =
                                null;

                            handleUnauthorized();

                            return;
                        }

                        const match =
                            await readJSON(
                                response
                            );

                        if (
                            !response.ok
                        ) {

                            return;
                        }

                        currentMatch =
                            match;

                        const status =
                            normalizeMatchStatus(
                                match.status
                            );

                        if (
                            status ===
                            "FINISHED"
                        ) {

                            clearInterval(
                                matchPollTimer
                            );

                            matchPollTimer =
                                null;

                            showResult(
                                match
                            );

                            return;
                        }

                        if (
                            status ===
                                "CANCELLED" ||
                            status ===
                                "REJECTED" ||
                            status ===
                                "EXPIRED"
                        ) {

                            clearInterval(
                                matchPollTimer
                            );

                            matchPollTimer =
                                null;

                            showToast(
                                "Trận đấu đã bị hủy.",
                                "error"
                            );

                            showScreen(
                                battleMenu
                            );
                        }

                    } catch {
                        // Tiếp tục chờ.
                    }

                },
                BATTLE_CONFIG
                    .RESULT_POLL_INTERVAL
            );
    }


    /* =====================================================
       RESULT
    ===================================================== */

    function showResult(
        match
    ) {

        if (
            resultShown
        ) {

            return;
        }

        resultShown =
            true;

        clearGameTimer();

        clearMatchmakingTimers();

        closeBattleSocket(
            true
        );

        const profile =
            getProfile();

        const myId =
            safeInteger(
                profile.id,
                0
            );

        const winner =
            safeInteger(
                match?.winner_id,
                0
            );

        const isDraw =
            winner === 0;

        let title =
            "🤝 HÒA!";

        let icon =
            "🤝";

        let type =
            "draw";

        if (!isDraw) {

            if (
                winner === myId
            ) {

                title =
                    "🏆 BẠN CHIẾN THẮNG!";

                icon =
                    "🏆";

                type =
                    "win";

            } else {

                title =
                    "⚔️ BẠN ĐÃ THUA";

                icon =
                    "💙";

                type =
                    "lose";
            }
        }

        const resultIcon =
            getElement(
                "resultIcon"
            );

        const resultTitle =
            getElement(
                "resultTitle"
            );

        const resultText =
            getElement(
                "resultText"
            );

        if (resultIcon) {

            resultIcon.textContent =
                icon;
        }

        if (resultTitle) {

            resultTitle.textContent =
                title;

            resultTitle.className =
                `result-title ${type}`;
        }

        if (resultText) {

            resultText.textContent =
                "Kết quả đã được máy chủ xác nhận.";
        }

        renderResultStats(
            match,
            myId
        );
    }


    function renderResultStats(
        match,
        myId
    ) {

        const players =
            Array.isArray(
                match?.players
            )
                ? match.players
                : [];

        const playerOne =
            players[0] ||
            null;

        const playerTwo =
            players[1] ||
            null;

        const playerOneId =
            safeInteger(
                playerOne?.id,
                0
            );

        const myIsPlayerOne =
            playerOneId ===
            myId;

        let myCorrect =
            0;

        let myWrong =
            0;

        let myBlank =
            0;

        let opponentCorrect =
            0;

        let opponentWrong =
            0;

        let opponentBlank =
            0;

        let opponentTime =
            0;

        let myTime =
            0;

        if (
            myIsPlayerOne
        ) {

            myCorrect =
                safeInteger(
                    match.player1_correct,
                    correct
                );

            myWrong =
                safeInteger(
                    match.player1_wrong,
                    wrong
                );

            myBlank =
                safeInteger(
                    match.player1_blank,
                    blank
                );

            myTime =
                safeInteger(
                    match.player1_time,
                    0
                );

            opponentCorrect =
                safeInteger(
                    match.player2_correct,
                    0
                );

            opponentWrong =
                safeInteger(
                    match.player2_wrong,
                    0
                );

            opponentBlank =
                safeInteger(
                    match.player2_blank,
                    0
                );

            opponentTime =
                safeInteger(
                    match.player2_time,
                    0
                );

        } else {

            myCorrect =
                safeInteger(
                    match.player2_correct,
                    correct
                );

            myWrong =
                safeInteger(
                    match.player2_wrong,
                    wrong
                );

            myBlank =
                safeInteger(
                    match.player2_blank,
                    blank
                );

            myTime =
                safeInteger(
                    match.player2_time,
                    0
                );

            opponentCorrect =
                safeInteger(
                    match.player1_correct,
                    0
                );

            opponentWrong =
                safeInteger(
                    match.player1_wrong,
                    0
                );

            opponentBlank =
                safeInteger(
                    match.player1_blank,
                    0
                );

            opponentTime =
                safeInteger(
                    match.player1_time,
                    0
                );
        }

        const opponent =
            myIsPlayerOne
                ? playerTwo
                : playerOne;

        const resultStats =
            getElement(
                "resultStats"
            );

        if (!resultStats) {
            return;
        }

        resultStats.innerHTML =
            `
            <div class="result-player-header">

                <span class="result-you">
                    BẠN
                </span>

                <span>
                    ĐỐI THỦ
                </span>

            </div>

            <div class="result-row">

                <span>
                    👤 Câu đúng
                </span>

                <strong>
                    ${myCorrect}
                </strong>

                <strong>
                    ${opponentCorrect}
                </strong>

            </div>

            <div class="result-row">

                <span>
                    ❌ Câu sai
                </span>

                <strong>
                    ${myWrong}
                </strong>

                <strong>
                    ${opponentWrong}
                </strong>

            </div>

            <div class="result-row">

                <span>
                    ⏭️ Câu bỏ
                </span>

                <strong>
                    ${myBlank}
                </strong>

                <strong>
                    ${opponentBlank}
                </strong>

            </div>

            <div class="result-row">

                <span>
                    ⏱️ Thời gian
                </span>

                <strong>
                    ${formatTime(
                        myTime
                    )}
                </strong>

                <strong>
                    ${formatTime(
                        opponentTime
                    )}
                </strong>

            </div>

            <div class="result-opponent">

                Đối thủ:

                <strong>
                    ${escapeHTML(
                        opponent?.username ||
                        "Người chơi"
                    )}
                </strong>

            </div>
            `;
    }


    /* =====================================================
       RETURN / RESET
    ===================================================== */

    function resetBattle() {

        clearAllTimers();

        cancelSearchRequest();

        closeBattleSocket(
            true
        );

        currentMatchId =
            null;

        currentMatch =
            null;

        questions =
            [];

        currentQuestionIndex =
            0;

        correct =
            0;

        wrong =
            0;

        blank =
            0;

        gameStartedAt =
            null;

        currentQuestionStartedAt =
            null;

        selectedAnswer =
            false;

        answerSubmitting =
            false;

        startingInProgress =
            false;

        gameFinished =
            false;

        finishingGame =
            false;

        resultShown =
            false;

        openingMatch =
            false;

        incomingInviteVisible =
            false;

        opponentState =
            null;

        finalResultData =
            null;
    }


    function backToMenu() {

        resetBattle();

        showScreen(
            battleMenu
        );

        setTimeout(
            checkIncomingMatch,
            100
        );
    }


    /* =====================================================
       SAFE EVENT BINDING
    ===================================================== */

    function onClick(
        id,
        handler
    ) {

        const element =
            getElement(id);

        if (!element) {
            return;
        }

        element.addEventListener(
            "click",
            handler
        );
    }


    /* =====================================================
       EVENTS
    ===================================================== */

    onClick(
        "randomButton",
        joinRandom
    );


    onClick(
        "cancelRandomButton",
        cancelRandom
    );


    onClick(
        "friendsButton",
        loadBattleFriends
    );


    onClick(
        "playerIdButton",
        function () {

            clearMatchmakingTimers();

            showScreen(
                playerIdScreen
            );
        }
    );


    onClick(
        "searchBattlePlayer",
        searchPlayer
    );


    onClick(
        "acceptInviteButton",
        acceptInvite
    );


    onClick(
        "rejectInviteButton",
        rejectInvite
    );


    onClick(
        "submitInputAnswer",
        function () {

            const input =
                getElement(
                    "inputAnswer"
                );

            if (!input) {
                return;
            }

            answerQuestion(
                input.value
            );
        }
    );


    const inputAnswer =
        getElement(
            "inputAnswer"
        );

    if (inputAnswer) {

        inputAnswer.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key ===
                        "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    answerQuestion(
                        event.target.value
                    );
                }
            }
        );
    }


    onClick(
        "skipQuestionButton",
        skipQuestion
    );


    document
        .querySelectorAll(
            "[data-back-menu]"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    backToMenu
                );
            }
        );


    onClick(
        "playAgainButton",
        function () {

            resetBattle();

            showScreen(
                battleMenu
            );

            setTimeout(
                checkIncomingMatch,
                100
            );
        }
    );


    onClick(
        "backAccountButton",
        function () {

            resetBattle();

            window.location.href =
                "account.html";
        }
    );


    /* =====================================================
       PAGE LIFECYCLE
    ===================================================== */

    window.addEventListener(
        "beforeunload",
        function () {

            clearAllTimers();

            cancelSearchRequest();

            closeBattleSocket(
                true
            );
        }
    );


    document.addEventListener(
        "visibilitychange",
        function () {

            if (
                document.visibilityState ===
                "visible"
            ) {

                if (
                    getToken() &&
                    currentMatchId &&
                    !gameFinished
                ) {

                    if (
                        !battleSocket ||
                        battleSocket.readyState !==
                            WebSocket.OPEN
                    ) {

                        connectBattleSocket();
                    }

                } else if (
                    getToken() &&
                    !currentMatchId &&
                    !gameFinished
                ) {

                    checkIncomingMatch();
                }
            }
        }
    );


    /* =====================================================
       START
    ===================================================== */

    function initializeBattle() {

        if (
            !checkLogin()
        ) {

            return;
        }

        showScreen(
            battleMenu
        );

        checkIncomingMatch();
    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initializeBattle,
            {
                once: true
            }
        );

    } else {

        initializeBattle();
    }


    /* =====================================================
       PUBLIC API
    ===================================================== */

    window.MATHWEB_BATTLE = {

        resetBattle,

        backToMenu,

        checkIncomingMatch,

        joinRandom,

        cancelRandom,

        loadBattleFriends,

        searchPlayer,

        invitePlayer,

        acceptInvite,

        rejectInvite,

        connectBattleSocket,

        closeBattleSocket
    };


})();