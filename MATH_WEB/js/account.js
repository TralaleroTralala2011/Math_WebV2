const API_URL =
    window.MATH_WEB_API_URL ||
    "http://127.0.0.1:8000";

const API_TIMEOUT_MS = 10000;
const MAX_PLAYER_ID_LENGTH = 30;
const MAX_REQUEST_ID = 2147483647;

let accountLoading = false;
let accountLoaded = false;

let profileRequestController = null;
let popupProfileRequestController = null;
let historyRequestController = null;
let friendsRequestController = null;
let requestsRequestController = null;

function getToken() {
    const token = localStorage.getItem("mathweb_token");

    if (!token || typeof token !== "string" || !token.trim()) {
        return null;
    }

    return token.trim();
}

function clearAuthData() {
    try {
        localStorage.removeItem("mathweb_token");
        localStorage.removeItem("mathweb_user");
        localStorage.removeItem("mathweb_profile");
    } catch (error) {
        console.error("Không thể xóa dữ liệu đăng nhập:", error);
    }
}

function abortAllRequests() {
    const controllers = [
        profileRequestController,
        popupProfileRequestController,
        historyRequestController,
        friendsRequestController,
        requestsRequestController
    ];

    controllers.forEach(controller => {
        if (controller) {
            try {
                controller.abort();
            } catch (_) {}
        }
    });

    profileRequestController = null;
    popupProfileRequestController = null;
    historyRequestController = null;
    friendsRequestController = null;
    requestsRequestController = null;
}

function logout() {
    clearAuthData();
    accountLoaded = false;
    abortAllRequests();
    window.location.replace("login.html");
}

function handleUnauthorized() {
    clearAuthData();
    accountLoaded = false;
    abortAllRequests();
    window.location.replace("login.html");
}

async function readJSON(response) {
    const text = await response.text();

    if (!text) {
        return {};
    }

    try {
        return JSON.parse(text);
    } catch (error) {
        return {
            detail: text
        };
    }
}

function getAPIErrorMessage(
    data,
    fallback = "Đã xảy ra lỗi."
) {
    if (
        data &&
        typeof data.detail === "string" &&
        data.detail.trim()
    ) {
        return data.detail.trim();
    }

    if (
        data &&
        typeof data.message === "string" &&
        data.message.trim()
    ) {
        return data.message.trim();
    }

    if (data && Array.isArray(data.detail)) {
        const messages = data.detail
            .map(item => {
                if (
                    item &&
                    typeof item.msg === "string"
                ) {
                    return item.msg;
                }

                return "";
            })
            .filter(Boolean);

        if (messages.length > 0) {
            return messages.join(" | ");
        }
    }

    return fallback;
}

function safeString(value, fallback = "") {
    if (value === null || value === undefined) {
        return fallback;
    }

    const result = String(value).trim();

    return result || fallback;
}

function safeNumber(value, fallback = 0) {
    const number = Number(value);

    if (Number.isFinite(number)) {
        return number;
    }

    return fallback;
}

function safeInteger(value, fallback = 0) {
    const number = Number(value);

    if (Number.isFinite(number)) {
        return Math.trunc(number);
    }

    return fallback;
}

function safeNonNegativeInteger(value, fallback = 0) {
    return Math.max(
        0,
        safeInteger(value, fallback)
    );
}

function clamp(value, minimum, maximum) {
    return Math.max(
        minimum,
        Math.min(value, maximum)
    );
}

async function fetchWithTimeout(
    url,
    options = {},
    timeout = API_TIMEOUT_MS
) {
    const externalSignal = options.signal || null;
    const timeoutController = new AbortController();

    let timeoutId = null;

    const abortFromExternal = function () {
        timeoutController.abort();
    };

    if (externalSignal) {
        if (externalSignal.aborted) {
            timeoutController.abort();
        } else {
            externalSignal.addEventListener(
                "abort",
                abortFromExternal,
                {
                    once: true
                }
            );
        }
    }

    timeoutId = window.setTimeout(
        function () {
            timeoutController.abort();
        },
        timeout
    );

    try {
        const requestOptions = {
            ...options,
            signal: timeoutController.signal
        };

        return await fetch(
            url,
            requestOptions
        );
    } finally {
        if (timeoutId !== null) {
            window.clearTimeout(timeoutId);
        }

        if (externalSignal) {
            externalSignal.removeEventListener(
                "abort",
                abortFromExternal
            );
        }
    }
}

function getRequestErrorMessage(
    error,
    fallback
) {
    if (
        error &&
        error.name === "AbortError"
    ) {
        return "Yêu cầu đã bị hủy hoặc quá thời gian chờ.";
    }

    if (
        error &&
        typeof error.message === "string" &&
        error.message.trim()
    ) {
        return error.message.trim();
    }

    return fallback;
}

function normalizePlayerId(playerId) {
    const value = safeString(playerId);

    if (!value) {
        return null;
    }

    if (value.length > MAX_PLAYER_ID_LENGTH) {
        return null;
    }

    return value;
}

function normalizeRequestId(requestId) {
    const id = safeInteger(
        requestId,
        -1
    );

    if (
        id <= 0 ||
        id > MAX_REQUEST_ID
    ) {
        return null;
    }

    return id;
}

async function getProfile() {
    const token = getToken();

    if (!token) {
        handleUnauthorized();
        return null;
    }

    if (profileRequestController) {
        profileRequestController.abort();
    }

    profileRequestController =
        new AbortController();

    try {
        const response =
            await fetchWithTimeout(
                `${API_URL}/api/auth/me`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`,
                        "Accept":
                            "application/json"
                    },
                    signal:
                        profileRequestController.signal
                }
            );

        if (response.status === 401) {
            handleUnauthorized();
            return null;
        }

        const data =
            await readJSON(response);

        if (!response.ok) {
            console.error(
                "GET /api/auth/me:",
                response.status,
                data
            );

            return null;
        }

        const profile =
            data?.user ||
            data?.profile ||
            data;

        if (
            !profile ||
            typeof profile !== "object" ||
            Array.isArray(profile)
        ) {
            console.error(
                "API auth/me không có dữ liệu user hợp lệ."
            );

            return null;
        }

        try {
            localStorage.setItem(
                "mathweb_profile",
                JSON.stringify(profile)
            );

            localStorage.setItem(
                "mathweb_user",
                JSON.stringify(profile)
            );
        } catch (error) {
            console.warn(
                "Không thể lưu cache profile:",
                error
            );
        }

        return profile;
    } catch (error) {
        if (error.name === "AbortError") {
            return null;
        }

        console.error(
            "Không thể kết nối MATH WEB API:",
            error
        );

        return null;
    } finally {
        profileRequestController = null;
    }
}

function getXPPercent(profile) {
    if (!profile) {
        return 0;
    }

    const requiredXP =
        Math.max(
            0,
            safeNumber(
                profile.required_xp,
                0
            )
        );

    let percentage =
        Number(profile.xp_percent);

    if (!Number.isFinite(percentage)) {
        const xp =
            Math.max(
                0,
                safeNumber(
                    profile.xp,
                    0
                )
            );

        percentage =
            requiredXP > 0
                ? (xp / requiredXP) * 100
                : 0;
    }

    return clamp(
        percentage,
        0,
        100
    );
}

function updateXPProgressARIA(
    percentage
) {
    const xpBar =
        document.querySelector(".xp-bar");

    if (!xpBar) {
        return;
    }

    xpBar.setAttribute(
        "aria-valuemin",
        "0"
    );

    xpBar.setAttribute(
        "aria-valuemax",
        "100"
    );

    xpBar.setAttribute(
        "aria-valuenow",
        String(
            Math.round(percentage)
        )
    );
}

function showXP(profile) {
    if (!profile) {
        return;
    }

    const xp =
        safeNonNegativeInteger(
            profile.xp,
            0
        );

    const requiredXP =
        safeNonNegativeInteger(
            profile.required_xp,
            0
        );

    const percentage =
        getXPPercent(profile);

    const xpFill =
        document.getElementById(
            "xpFill"
        );

    const xpText =
        document.getElementById(
            "xpText"
        );

    const xpCurrent =
        document.getElementById(
            "xpCurrent"
        );

    const xpRequired =
        document.getElementById(
            "xpRequired"
        );

    const xpPercent =
        document.getElementById(
            "xpPercent"
        );

    if (xpFill) {
        xpFill.style.width =
            `${percentage}%`;
    }

    if (xpText) {
        xpText.textContent =
            `${xp} / ${requiredXP} XP`;
    }

    if (xpCurrent) {
        xpCurrent.textContent =
            String(xp);
    }

    if (xpRequired) {
        xpRequired.textContent =
            String(requiredXP);
    }

    if (xpPercent) {
        xpPercent.textContent =
            `${Math.round(percentage)}%`;
    }

    updateXPProgressARIA(
        percentage
    );
}

function showProfile(profile) {
    if (!profile) {
        return;
    }

    const username =
        safeString(
            profile.username ||
            profile.name ||
            profile.display_name,
            "Người dùng"
        );

    const playerId =
        safeString(
            profile.player_id ||
            profile.playerId ||
            profile.id,
            ""
        );

    const level =
        safeNonNegativeInteger(
            profile.level ??
            profile.lv ??
            profile.level_number,
            0
        );

    const xp =
        safeNonNegativeInteger(
            profile.xp,
            0
        );

    const requiredXP =
        safeNonNegativeInteger(
            profile.required_xp,
            0
        );

    const avatar =
        safeString(
            profile.avatar ||
            profile.avatar_url ||
            profile.avatarUrl,
            ""
        );

    const usernameElements = [
        "accountUsername",
        "profileUsername",
        "username",
        "userName"
    ];

    usernameElements.forEach(id => {
        const element =
            document.getElementById(id);

        if (element) {
            element.textContent =
                username;
        }
    });

    const playerIdElements = [
        "accountPlayerId",
        "profilePlayerId",
        "playerId"
    ];

    playerIdElements.forEach(id => {
        const element =
            document.getElementById(id);

        if (element) {
            element.textContent =
                playerId || "Chưa có ID";
        }
    });

    const levelElements = [
        "accountLevel",
        "profileLevel",
        "level"
    ];

    levelElements.forEach(id => {
        const element =
            document.getElementById(id);

        if (element) {
            element.textContent =
                `Lv.${level}`;
        }
    });

    const avatarElements = [
        "accountAvatar",
        "profileAvatar",
        "avatar"
    ];

    avatarElements.forEach(id => {
        const element =
            document.getElementById(id);

        if (!element) {
            return;
        }

        if (
            element.tagName ===
            "IMG"
        ) {
            if (avatar) {
                element.src = avatar;
                element.style.display =
                    "";
            }
        } else if (avatar) {
            element.style.backgroundImage =
                `url("${avatar}")`;
        }
    });

    showXP(profile);

    const emailElement =
        document.getElementById(
            "accountEmail"
        );

    if (emailElement) {
        emailElement.textContent =
            safeString(
                profile.email,
                "Chưa cập nhật"
            );
    }

    const createdElement =
        document.getElementById(
            "accountCreatedAt"
        );

    if (createdElement) {
        createdElement.textContent =
            formatDate(
                profile.created_at ||
                profile.createdAt
            );
    }

    return {
        username,
        playerId,
        level,
        xp,
        requiredXP
    };
}

async function getHistory() {
    const token =
        getToken();

    if (!token) {
        return [];
    }

    if (historyRequestController) {
        historyRequestController.abort();
    }

    historyRequestController =
        new AbortController();

    try {
        const response =
            await fetchWithTimeout(
                `${API_URL}/api/games/history`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`,
                        "Accept":
                            "application/json"
                    },
                    signal:
                        historyRequestController.signal
                }
            );

        if (response.status === 401) {
            handleUnauthorized();
            return [];
        }

        const data =
            await readJSON(response);

        if (!response.ok) {
            console.error(
                "GET /api/games/history:",
                response.status,
                data
            );

            return [];
        }

        if (Array.isArray(data)) {
            return data;
        }

        if (
            Array.isArray(data?.history)
        ) {
            return data.history;
        }

        if (
            Array.isArray(data?.games)
        ) {
            return data.games;
        }

        if (
            Array.isArray(data?.items)
        ) {
            return data.items;
        }

        return [];
    } catch (error) {
        if (error.name !== "AbortError") {
            console.error(
                "Không thể tải lịch sử chơi:",
                error
            );
        }

        return [];
    } finally {
        historyRequestController = null;
    }
}

function formatTime(seconds) {
    const value =
        safeNonNegativeInteger(
            seconds,
            0
        );

    const hours =
        Math.floor(
            value / 3600
        );

    const minutes =
        Math.floor(
            (value % 3600) / 60
        );

    const secs =
        value % 60;

    if (hours > 0) {
        return [
            String(hours).padStart(2, "0"),
            String(minutes).padStart(2, "0"),
            String(secs).padStart(2, "0")
        ].join(":");
    }

    return [
        String(minutes).padStart(2, "0"),
        String(secs).padStart(2, "0")
    ].join(":");
}

function formatDate(value) {
    if (!value) {
        return "Chưa cập nhật";
    }

    const date =
        new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return safeString(
            value,
            "Chưa cập nhật"
        );
    }

    return date.toLocaleDateString(
        "vi-VN",
        {
            day: "2-digit",
            month: "2-digit",
            year: "numeric"
        }
    );
}

function showHistory(history) {
    const container =
        document.getElementById(
            "historyList"
        ) ||
        document.querySelector(
            ".history-list"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (
        !Array.isArray(history) ||
        history.length === 0
    ) {
        const empty =
            document.createElement("div");

        empty.className =
            "history-empty";

        empty.textContent =
            "Chưa có lịch sử chơi.";

        container.appendChild(
            empty
        );

        return;
    }

    const fragment =
        document.createDocumentFragment();

    history.forEach(item => {
        if (
            !item ||
            typeof item !== "object"
        ) {
            return;
        }

        const row =
            document.createElement("div");

        row.className =
            "history-item";

        const game =
            safeString(
                item.game_name ||
                item.game ||
                item.title,
                "Trò chơi"
            );

        const score =
            safeNumber(
                item.score,
                0
            );

        const correct =
            safeNonNegativeInteger(
                item.correct,
                0
            );

        const wrong =
            safeNonNegativeInteger(
                item.wrong,
                0
            );

        const time =
            safeNonNegativeInteger(
                item.time_seconds ||
                item.time,
                0
            );

        const date =
            formatDate(
                item.created_at ||
                item.createdAt ||
                item.date
            );

        row.innerHTML = `
            <div class="history-item-main">
                <div class="history-game">
                    ${escapeHTML(game)}
                </div>
                <div class="history-date">
                    ${escapeHTML(date)}
                </div>
            </div>
            <div class="history-item-stats">
                <span>Điểm: ${score}</span>
                <span>Đúng: ${correct}</span>
                <span>Sai: ${wrong}</span>
                <span>Thời gian: ${formatTime(time)}</span>
            </div>
        `;

        fragment.appendChild(
            row
        );
    });

    container.appendChild(
        fragment
    );
}

async function getFriends() {
    const token =
        getToken();

    if (!token) {
        return [];
    }

    if (friendsRequestController) {
        friendsRequestController.abort();
    }

    friendsRequestController =
        new AbortController();

    try {
        const response =
            await fetchWithTimeout(
                `${API_URL}/api/friends`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`,
                        "Accept":
                            "application/json"
                    },
                    signal:
                        friendsRequestController.signal
                }
            );

        if (response.status === 401) {
            handleUnauthorized();
            return [];
        }

        const data =
            await readJSON(response);

        if (!response.ok) {
            console.error(
                "GET /api/friends:",
                response.status,
                data
            );

            return [];
        }

        if (Array.isArray(data)) {
            return data;
        }

        if (Array.isArray(data?.friends)) {
            return data.friends;
        }

        if (Array.isArray(data?.items)) {
            return data.items;
        }

        return [];
    } catch (error) {
        if (error.name !== "AbortError") {
            console.error(
                "Không thể tải danh sách bạn bè:",
                error
            );
        }

        return [];
    } finally {
        friendsRequestController = null;
    }
}

async function getFriendRequests() {
    const token =
        getToken();

    if (!token) {
        return [];
    }

    if (requestsRequestController) {
        requestsRequestController.abort();
    }

    requestsRequestController =
        new AbortController();

    try {
        const response =
            await fetchWithTimeout(
                `${API_URL}/api/friends/requests`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`,
                        "Accept":
                            "application/json"
                    },
                    signal:
                        requestsRequestController.signal
                }
            );

        if (response.status === 401) {
            handleUnauthorized();
            return [];
        }

        const data =
            await readJSON(response);

        if (!response.ok) {
            console.error(
                "GET /api/friends/requests:",
                response.status,
                data
            );

            return [];
        }

        if (Array.isArray(data)) {
            return data;
        }

        if (
            Array.isArray(
                data?.requests
            )
        ) {
            return data.requests;
        }

        if (
            Array.isArray(
                data?.items
            )
        ) {
            return data.items;
        }

        return [];
    } catch (error) {
        if (error.name !== "AbortError") {
            console.error(
                "Không thể tải lời mời kết bạn:",
                error
            );
        }

        return [];
    } finally {
        requestsRequestController = null;
    }
}

function closeProfilePopup() {
    const popup =
        document.getElementById(
            "profilePopup"
        ) ||
        document.querySelector(
            ".profile-popup"
        );

    if (!popup) {
        return;
    }

    popup.classList.remove("show");
    popup.classList.remove("active");

    popup.setAttribute(
        "aria-hidden",
        "true"
    );

    if (
        popupProfileRequestController
    ) {
        try {
            popupProfileRequestController.abort();
        } catch (_) {}
    }

    popupProfileRequestController =
        null;

    document.body.classList.remove(
        "profile-popup-open"
    );

    if (
        typeof window.__mathwebPreviousBodyOverflow ===
        "string"
    ) {
        document.body.style.overflow =
            window.__mathwebPreviousBodyOverflow;

        delete window.__mathwebPreviousBodyOverflow;
    }
}

function showProfilePopupLoading() {
    const container =
        document.getElementById(
            "profilePopupContent"
        ) ||
        document.querySelector(
            ".profile-popup-content"
        );

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="profile-popup-loading">
            <div class="loading-spinner"></div>
            <p>Đang tải thông tin...</p>
        </div>
    `;
}

function showProfilePopupError(
    message
) {
    const container =
        document.getElementById(
            "profilePopupContent"
        ) ||
        document.querySelector(
            ".profile-popup-content"
        );

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="profile-popup-error">
            <p>${escapeHTML(
                safeString(
                    message,
                    "Không thể tải thông tin."
                )
            )}</p>
            <button
                type="button"
                class="profile-popup-close-button"
                onclick="closeProfilePopup()"
            >
                Đóng
            </button>
        </div>
    `;
}

async function openProfilePopup(
    playerId
) {
    const normalized =
        normalizePlayerId(
            playerId
        );

    if (!normalized) {
        showTemporaryMessage(
            "ID người chơi không hợp lệ.",
            "error"
        );

        return null;
    }

    const popup =
        document.getElementById(
            "profilePopup"
        ) ||
        document.querySelector(
            ".profile-popup"
        );

    if (!popup) {
        return null;
    }

    if (
        popupProfileRequestController
    ) {
        popupProfileRequestController.abort();
    }

    popupProfileRequestController =
        new AbortController();

    if (
        typeof window.__mathwebPreviousBodyOverflow !==
        "string"
    ) {
        window.__mathwebPreviousBodyOverflow =
            document.body.style.overflow || "";
    }

    document.body.classList.add(
        "profile-popup-open"
    );

    document.body.style.overflow =
        "hidden";

    popup.classList.add("show");
    popup.classList.add("active");

    popup.setAttribute(
        "aria-hidden",
        "false"
    );

    showProfilePopupLoading();

    const token =
        getToken();

    if (!token) {
        handleUnauthorized();
        return null;
    }

    try {
        const response =
            await fetchWithTimeout(
                `${API_URL}/api/users/profile/${encodeURIComponent(normalized)}`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`,
                        "Accept":
                            "application/json"
                    },
                    signal:
                        popupProfileRequestController.signal
                }
            );

        if (response.status === 401) {
            handleUnauthorized();
            return null;
        }

        const data =
            await readJSON(response);

        if (!response.ok) {
            showProfilePopupError(
                getAPIErrorMessage(
                    data,
                    "Không thể tải hồ sơ người chơi."
                )
            );

            return null;
        }

        const profile =
            data?.user ||
            data?.profile ||
            data;

        renderProfilePopup(
            profile
        );

        return profile;
    } catch (error) {
        if (
            error.name ===
            "AbortError"
        ) {
            return null;
        }

        console.error(
            "Không thể tải profile:",
            error
        );

        showProfilePopupError(
            getRequestErrorMessage(
                error,
                "Không thể kết nối máy chủ."
            )
        );

        return null;
    } finally {
        popupProfileRequestController =
            null;
    }
}

function renderProfilePopup(
    profile
) {
    const container =
        document.getElementById(
            "profilePopupContent"
        ) ||
        document.querySelector(
            ".profile-popup-content"
        );

    if (!container) {
        return;
    }

    if (
        !profile ||
        typeof profile !== "object"
    ) {
        showProfilePopupError(
            "Dữ liệu hồ sơ không hợp lệ."
        );

        return;
    }

    const username =
        safeString(
            profile.username ||
            profile.name ||
            profile.display_name,
            "Người chơi"
        );

    const playerId =
        safeString(
            profile.player_id ||
            profile.playerId ||
            profile.id,
            "Chưa có ID"
        );

    const level =
        safeNonNegativeInteger(
            profile.level ??
            profile.lv ??
            profile.level_number,
            0
        );

    const xp =
        safeNonNegativeInteger(
            profile.xp,
            0
        );

    const requiredXP =
        safeNonNegativeInteger(
            profile.required_xp,
            0
        );

    const percentage =
        getXPPercent(
            profile
        );

    const avatar =
        safeString(
            profile.avatar ||
            profile.avatar_url ||
            profile.avatarUrl,
            ""
        );

    const online =
        Boolean(
            profile.online ??
            profile.is_online ??
            profile.isOnline
        );

    const avatarHTML =
        avatar
            ? `
                <img
                    class="profile-popup-avatar-image"
                    src="${escapeHTML(avatar)}"
                    alt="${escapeHTML(username)}"
                    loading="lazy"
                >
            `
            : `
                <div class="profile-popup-avatar-fallback">
                    ${escapeHTML(
                        username
                            .charAt(0)
                            .toUpperCase()
                    )}
                </div>
            `;

    container.innerHTML = `
        <div class="profile-popup-header">
            <div class="profile-popup-avatar">
                ${avatarHTML}
            </div>

            <div class="profile-popup-main-info">
                <h3>
                    ${escapeHTML(username)}
                </h3>

                <div class="profile-popup-player-id">
                    ID: ${escapeHTML(playerId)}
                </div>

                <div class="profile-popup-online-status">
                    <span
                        class="online-dot ${
                            online
                                ? "online"
                                : "offline"
                        }"
                    ></span>
                    <span>
                        ${
                            online
                                ? "Đang online"
                                : "Offline"
                        }
                    </span>
                </div>
            </div>
        </div>

        <div class="profile-popup-stats">
            <div class="profile-popup-stat">
                <span class="stat-label">
                    Cấp độ
                </span>
                <strong>
                    Lv.${level}
                </strong>
            </div>

            <div class="profile-popup-stat">
                <span class="stat-label">
                    Kinh nghiệm
                </span>
                <strong>
                    ${xp} / ${requiredXP} XP
                </strong>
            </div>
        </div>

        <div class="profile-popup-xp">
            <div class="xp-progress">
                <div
                    class="xp-progress-fill"
                    style="width:${percentage}%"
                ></div>
            </div>

            <span>
                ${Math.round(percentage)}%
            </span>
        </div>
    `;
}

function showFriends(friends) {
    const container =
        document.getElementById(
            "friendsList"
        ) ||
        document.querySelector(
            ".friends-list"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (
        !Array.isArray(friends) ||
        friends.length === 0
    ) {
        container.innerHTML = `
            <div class="friends-empty">
                <p>Chưa có bạn bè.</p>
            </div>
        `;

        updateFriendCount(0);
        return;
    }

    const fragment =
        document.createDocumentFragment();

    friends.forEach(friend => {
        if (
            !friend ||
            typeof friend !== "object"
        ) {
            return;
        }

        const playerId =
            safeString(
                friend.player_id ||
                friend.playerId ||
                friend.id,
                ""
            );

        const username =
            safeString(
                friend.username ||
                friend.name ||
                friend.display_name,
                playerId ||
                "Người chơi"
            );

        const avatar =
            safeString(
                friend.avatar ||
                friend.avatar_url ||
                friend.avatarUrl,
                ""
            );

        const online =
            Boolean(
                friend.online ??
                friend.is_online ??
                friend.isOnline
            );

        const item =
            document.createElement("div");

        item.className =
            "friend-item";

        item.dataset.playerId =
            playerId;

        const avatarHTML =
            avatar
                ? `
                    <img
                        src="${escapeHTML(avatar)}"
                        alt="${escapeHTML(username)}"
                        class="friend-avatar-image"
                        loading="lazy"
                    >
                `
                : `
                    <div class="friend-avatar-fallback">
                        ${escapeHTML(
                            username
                                .charAt(0)
                                .toUpperCase()
                        )}
                    </div>
                `;

        item.innerHTML = `
            <div
                class="friend-main"
                data-player-id="${escapeHTML(playerId)}"
            >
                <div class="friend-avatar">
                    ${avatarHTML}
                    <span
                        class="friend-online-dot ${
                            online
                                ? "online"
                                : "offline"
                        }"
                    ></span>
                </div>

                <div class="friend-info">
                    <div class="friend-name">
                        ${escapeHTML(username)}
                    </div>

                    <div class="friend-id">
                        ID: ${escapeHTML(
                            playerId ||
                            "Không có"
                        )}
                    </div>
                </div>
            </div>

            <div class="friend-actions">
                <button
                    type="button"
                    class="friend-profile-button"
                    data-player-id="${escapeHTML(playerId)}"
                >
                    Hồ sơ
                </button>

                <button
                    type="button"
                    class="friend-chat-button"
                    data-player-id="${escapeHTML(playerId)}"
                >
                    Chat
                </button>

                <button
                    type="button"
                    class="friend-pvp-button"
                    data-player-id="${escapeHTML(playerId)}"
                >
                    PvP
                </button>
            </div>
        `;

        fragment.appendChild(
            item
        );
    });

    container.appendChild(
        fragment
    );

    updateFriendCount(
        friends.length
    );

    bindFriendActionButtons();
}

function showFriendRequests(
    requests
) {
    const container =
        document.getElementById(
            "friendRequestsList"
        ) ||
        document.querySelector(
            ".friend-requests-list"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (
        !Array.isArray(requests) ||
        requests.length === 0
    ) {
        container.innerHTML = `
            <div class="friend-requests-empty">
                <p>Không có lời mời kết bạn.</p>
            </div>
        `;

        updateRequestCount(0);
        return;
    }

    const fragment =
        document.createDocumentFragment();

    requests.forEach(request => {
        if (
            !request ||
            typeof request !== "object"
        ) {
            return;
        }

        const requestId =
            normalizeRequestId(
                request.id ||
                request.request_id ||
                request.requestId
            );

        const playerId =
            safeString(
                request.player_id ||
                request.playerId ||
                request.sender_player_id ||
                request.senderPlayerId,
                ""
            );

        const username =
            safeString(
                request.username ||
                request.name ||
                request.display_name ||
                request.sender_username ||
                request.senderUsername,
                playerId ||
                "Người chơi"
            );

        const avatar =
            safeString(
                request.avatar ||
                request.avatar_url ||
                request.avatarUrl,
                ""
            );

        const item =
            document.createElement("div");

        item.className =
            "friend-request-item";

        item.dataset.requestId =
            requestId || "";

        const avatarHTML =
            avatar
                ? `
                    <img
                        src="${escapeHTML(avatar)}"
                        alt="${escapeHTML(username)}"
                        class="friend-request-avatar-image"
                        loading="lazy"
                    >
                `
                : `
                    <div class="friend-request-avatar-fallback">
                        ${escapeHTML(
                            username
                                .charAt(0)
                                .toUpperCase()
                        )}
                    </div>
                `;

        item.innerHTML = `
            <div class="friend-request-main">
                <div class="friend-request-avatar">
                    ${avatarHTML}
                </div>

                <div class="friend-request-info">
                    <div class="friend-request-name">
                        ${escapeHTML(username)}
                    </div>

                    <div class="friend-request-id">
                        ID: ${escapeHTML(
                            playerId ||
                            "Không có"
                        )}
                    </div>
                </div>
            </div>

            <div class="friend-request-actions">
                <button
                    type="button"
                    class="friend-request-accept"
                    data-request-id="${requestId || ""}"
                >
                    Chấp nhận
                </button>

                <button
                    type="button"
                    class="friend-request-reject"
                    data-request-id="${requestId || ""}"
                >
                    Từ chối
                </button>
            </div>
        `;

        fragment.appendChild(
            item
        );
    });

    container.appendChild(
        fragment
    );

    updateRequestCount(
        requests.length
    );

    bindFriendRequestButtons();
}

async function searchFriend() {
    const input =
        document.getElementById(
            "friendSearchInput"
        ) ||
        document.querySelector(
            ".friend-search-input"
        );

    const resultContainer =
        document.getElementById(
            "friendSearchResult"
        ) ||
        document.querySelector(
            ".friend-search-result"
        );

    if (!input) {
        return null;
    }

    const playerId =
        normalizePlayerId(
            input.value
        );

    if (!playerId) {
        if (resultContainer) {
            resultContainer.innerHTML = `
                <div class="search-result-error">
                    Vui lòng nhập ID người chơi hợp lệ.
                </div>
            `;
        }

        return null;
    }

    if (resultContainer) {
        resultContainer.innerHTML = `
            <div class="search-result-loading">
                Đang tìm...
            </div>
        `;
    }

    const token =
        getToken();

    if (!token) {
        handleUnauthorized();
        return null;
    }

    try {
        const response =
            await fetchWithTimeout(
                `${API_URL}/api/friends/search?player_id=${encodeURIComponent(playerId)}`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`,
                        "Accept":
                            "application/json"
                    }
                }
            );

        if (response.status === 401) {
            handleUnauthorized();
            return null;
        }

        const data =
            await readJSON(response);

        if (!response.ok) {
            const message =
                getAPIErrorMessage(
                    data,
                    "Không tìm thấy người chơi."
                );

            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div class="search-result-error">
                        ${escapeHTML(message)}
                    </div>
                `;
            }

            return null;
        }

        const profile =
            data?.user ||
            data?.profile ||
            data?.friend ||
            data;

        if (
            !profile ||
            typeof profile !== "object"
        ) {
            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div class="search-result-error">
                        Không tìm thấy người chơi.
                    </div>
                `;
            }

            return null;
        }

        renderFriendSearchResult(
            profile
        );

        return profile;
    } catch (error) {
        console.error(
            "Lỗi tìm kiếm bạn:",
            error
        );

        if (resultContainer) {
            resultContainer.innerHTML = `
                <div class="search-result-error">
                    ${escapeHTML(
                        getRequestErrorMessage(
                            error,
                            "Không thể kết nối máy chủ."
                        )
                    )}
                </div>
            `;
        }

        return null;
    }
}

function renderFriendSearchResult(
    profile
) {
    const container =
        document.getElementById(
            "friendSearchResult"
        ) ||
        document.querySelector(
            ".friend-search-result"
        );

    if (!container) {
        return;
    }

    const playerId =
        safeString(
            profile.player_id ||
            profile.playerId ||
            profile.id,
            ""
        );

    const username =
        safeString(
            profile.username ||
            profile.name ||
            profile.display_name,
            playerId ||
            "Người chơi"
        );

    const avatar =
        safeString(
            profile.avatar ||
            profile.avatar_url ||
            profile.avatarUrl,
            ""
        );

    const alreadyFriend =
        Boolean(
            profile.is_friend ??
            profile.isFriend ??
            profile.already_friend
        );

    const requestPending =
        Boolean(
            profile.request_pending ??
            profile.requestPending ??
            profile.pending
        );

    const avatarHTML =
        avatar
            ? `
                <img
                    src="${escapeHTML(avatar)}"
                    alt="${escapeHTML(username)}"
                    class="search-result-avatar-image"
                    loading="lazy"
                >
            `
            : `
                <div class="search-result-avatar-fallback">
                    ${escapeHTML(
                        username
                            .charAt(0)
                            .toUpperCase()
                    )}
                </div>
            `;

    let actionHTML = "";

    if (alreadyFriend) {
        actionHTML = `
            <button
                type="button"
                class="search-result-action"
                disabled
            >
                Đã là bạn
            </button>
        `;
    } else if (requestPending) {
        actionHTML = `
            <button
                type="button"
                class="search-result-action"
                disabled
            >
                Đã gửi lời mời
            </button>
        `;
    } else {
        actionHTML = `
            <button
                type="button"
                class="search-result-add-button"
                data-player-id="${escapeHTML(playerId)}"
            >
                Kết bạn
            </button>
        `;
    }

    container.innerHTML = `
        <div class="search-result-card">
            <div class="search-result-main">
                <div class="search-result-avatar">
                    ${avatarHTML}
                </div>

                <div class="search-result-info">
                    <div class="search-result-name">
                        ${escapeHTML(username)}
                    </div>

                    <div class="search-result-id">
                        ID: ${escapeHTML(
                            playerId ||
                            "Không có"
                        )}
                    </div>
                </div>
            </div>

            <div class="search-result-actions">
                <button
                    type="button"
                    class="search-result-profile-button"
                    data-player-id="${escapeHTML(playerId)}"
                >
                    Xem hồ sơ
                </button>

                ${actionHTML}
            </div>
        </div>
    `;

    const addButton =
        container.querySelector(
            ".search-result-add-button"
        );

    if (addButton) {
        addButton.addEventListener(
            "click",
            () => {
                sendFriendRequest(
                    playerId
                );
            },
            {
                once: true
            }
        );
    }

    const profileButton =
        container.querySelector(
            ".search-result-profile-button"
        );

    if (profileButton) {
        profileButton.addEventListener(
            "click",
            () => {
                openProfilePopup(
                    playerId
                );
            }
        );
    }
}

async function sendFriendRequest(
    playerId
) {
    const normalized =
        normalizePlayerId(
            playerId
        );

    if (!normalized) {
        showTemporaryMessage(
            "ID người chơi không hợp lệ.",
            "error"
        );

        return false;
    }

    const token =
        getToken();

    if (!token) {
        handleUnauthorized();
        return false;
    }

    try {
        const response =
            await fetchWithTimeout(
                `${API_URL}/api/friends/request`,
                {
                    method: "POST",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`,
                        "Accept":
                            "application/json",
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        player_id:
                            normalized
                    })
                }
            );

        if (response.status === 401) {
            handleUnauthorized();
            return false;
        }

        const data =
            await readJSON(response);

        if (!response.ok) {
            showTemporaryMessage(
                getAPIErrorMessage(
                    data,
                    "Không thể gửi lời mời kết bạn."
                ),
                "error"
            );

            return false;
        }

        showTemporaryMessage(
            "Đã gửi lời mời kết bạn!",
            "success"
        );

        const button =
            document.querySelector(
                `.search-result-add-button[data-player-id="${CSS.escape(normalized)}"]`
            );

        if (button) {
            button.disabled = true;
            button.textContent =
                "Đã gửi lời mời";
        }

        return true;
    } catch (error) {
        console.error(
            "Lỗi gửi lời mời kết bạn:",
            error
        );

        showTemporaryMessage(
            getRequestErrorMessage(
                error,
                "Không thể kết nối máy chủ."
            ),
            "error"
        );

        return false;
    }
}

async function acceptFriend(
    requestId
) {
    const id =
        normalizeRequestId(
            requestId
        );

    if (!id) {
        showTemporaryMessage(
            "Lời mời không hợp lệ.",
            "error"
        );

        return false;
    }

    const token =
        getToken();

    if (!token) {
        handleUnauthorized();
        return false;
    }

    try {
        const response =
            await fetchWithTimeout(
                `${API_URL}/api/friends/accept/${id}`,
                {
                    method: "POST",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`,
                        "Accept":
                            "application/json"
                    }
                }
            );

        if (response.status === 401) {
            handleUnauthorized();
            return false;
        }

        const data =
            await readJSON(response);

        if (!response.ok) {
            showTemporaryMessage(
                getAPIErrorMessage(
                    data,
                    "Không thể chấp nhận lời mời."
                ),
                "error"
            );

            return false;
        }

        showTemporaryMessage(
            "Đã kết bạn thành công!",
            "success"
        );

        await loadFriends();

        return true;
    } catch (error) {
        console.error(
            "Lỗi chấp nhận lời mời:",
            error
        );

        showTemporaryMessage(
            getRequestErrorMessage(
                error,
                "Không thể kết nối máy chủ."
            ),
            "error"
        );

        return false;
    }
}

async function rejectFriend(
    requestId
) {
    const id =
        normalizeRequestId(
            requestId
        );

    if (!id) {
        showTemporaryMessage(
            "Lời mời không hợp lệ.",
            "error"
        );

        return false;
    }

    const token =
        getToken();

    if (!token) {
        handleUnauthorized();
        return false;
    }

    try {
        const response =
            await fetchWithTimeout(
                `${API_URL}/api/friends/reject/${id}`,
                {
                    method: "POST",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`,
                        "Accept":
                            "application/json"
                    }
                }
            );

        if (response.status === 401) {
            handleUnauthorized();
            return false;
        }

        const data =
            await readJSON(response);

        if (!response.ok) {
            showTemporaryMessage(
                getAPIErrorMessage(
                    data,
                    "Không thể từ chối lời mời."
                ),
                "error"
            );

            return false;
        }

        showTemporaryMessage(
            "Đã từ chối lời mời.",
            "success"
        );

        await loadFriendRequests();

        return true;
    } catch (error) {
        console.error(
            "Lỗi từ chối lời mời:",
            error
        );

        showTemporaryMessage(
            getRequestErrorMessage(
                error,
                "Không thể kết nối máy chủ."
            ),
            "error"
        );

        return false;
    }
}

async function loadFriends() {
    const [
        friends,
        requests
    ] = await Promise.all([
        getFriends(),
        getFriendRequests()
    ]);

    showFriends(friends);
    showFriendRequests(requests);

    return {
        friends,
        requests
    };
}

function setAccountLoading(
    loading
) {
    accountLoading =
        Boolean(loading);

    const loadingElements =
        document.querySelectorAll(
            ".account-loading"
        );

    loadingElements.forEach(
        element => {
            element.style.display =
                accountLoading
                    ? ""
                    : "none";
        }
    );

    const refreshButtons =
        document.querySelectorAll(
            "#refreshAccount, .refresh-account-button"
        );

    refreshButtons.forEach(
        button => {
            button.disabled =
                accountLoading;
        }
    );
}

function showAccountError(
    message
) {
    const container =
        document.getElementById(
            "accountError"
        ) ||
        document.querySelector(
            ".account-error"
        );

    if (!container) {
        return;
    }

    container.textContent =
        safeString(
            message,
            "Không thể tải dữ liệu tài khoản."
        );

    container.style.display =
        "";
}

function hideAccountError() {
    const container =
        document.getElementById(
            "accountError"
        ) ||
        document.querySelector(
            ".account-error"
        );

    if (!container) {
        return;
    }

    container.textContent = "";
    container.style.display =
        "none";
}

async function loadAccount(
    force = false
) {
    if (
        accountLoading &&
        !force
    ) {
        return;
    }

    if (
        accountLoaded &&
        !force
    ) {
        return;
    }

    const token =
        getToken();

    if (!token) {
        handleUnauthorized();
        return;
    }

    setAccountLoading(true);
    hideAccountError();

    try {
        const [
            profile,
            history,
            friends,
            requests
        ] = await Promise.all([
            getProfile(),
            getHistory(),
            getFriends(),
            getFriendRequests()
        ]);

        if (profile) {
            showProfile(profile);
        }

        showHistory(history);
        showFriends(friends);
        showFriendRequests(requests);

        accountLoaded = true;

        return {
            profile,
            history,
            friends,
            requests
        };
    } catch (error) {
        console.error(
            "Lỗi tải Account:",
            error
        );

        showAccountError(
            getRequestErrorMessage(
                error,
                "Không thể tải dữ liệu tài khoản."
            )
        );

        return null;
    } finally {
        setAccountLoading(false);
    }
}

async function refreshAccount() {
    accountLoaded = false;

    abortAllRequests();

    return await loadAccount(true);
}

function updateFriendCount(
    count
) {
    const value =
        safeNonNegativeInteger(
            count,
            0
        );

    const elements = [
        "friendCount",
        "friendsCount"
    ];

    elements.forEach(id => {
        const element =
            document.getElementById(id);

        if (element) {
            element.textContent =
                String(value);
        }
    });
}

function updateRequestCount(
    count
) {
    const value =
        safeNonNegativeInteger(
            count,
            0
        );

    const elements = [
        "friendRequestCount",
        "requestCount"
    ];

    elements.forEach(id => {
        const element =
            document.getElementById(id);

        if (element) {
            element.textContent =
                String(value);
        }
    });
}

function escapeHTML(value) {
    const string =
        safeString(
            value
        );

    return string.replace(
        /[&<>"']/g,
        character => {
            switch (character) {
                case "&":
                    return "&amp;";
                case "<":
                    return "&lt;";
                case ">":
                    return "&gt;";
                case '"':
                    return "&quot;";
                case "'":
                    return "&#039;";
                default:
                    return character;
            }
        }
    );
}

function showTemporaryMessage(
    message,
    type = "info"
) {
    const old =
        document.querySelector(
            ".account-temporary-message"
        );

    if (old) {
        old.remove();
    }

    const element =
        document.createElement(
            "div"
        );

    element.className =
        `account-temporary-message ${type}`;

    element.textContent =
        safeString(
            message,
            "Đã xảy ra lỗi."
        );

    document.body.appendChild(
        element
    );

    window.setTimeout(
        () => {
            if (
                element &&
                element.parentNode
            ) {
                element.remove();
            }
        },
        3000
    );
}

function openFriendChat(
    playerId
) {
    const normalized =
        normalizePlayerId(
            playerId
        );

    if (!normalized) {
        return;
    }

    const friend = {
        player_id:
            normalized
    };

    try {
        localStorage.setItem(
            "mathweb_open_chat_friend",
            JSON.stringify(friend)
        );
    } catch (_) {}

    if (
        typeof window.openChat ===
        "function"
    ) {
        try {
            window.openChat(friend);
            return;
        } catch (error) {
            console.warn(
                "Không thể mở chat trực tiếp:",
                error
            );
        }
    }

    window.location.href =
        "chat.html";
}

function openFriendPvP(
    playerId
) {
    const normalized =
        normalizePlayerId(
            playerId
        );

    if (!normalized) {
        return;
    }

    try {
        localStorage.setItem(
            "mathweb_pvp_friend",
            normalized
        );
    } catch (_) {}

    window.location.href =
        "battle.html";
}

function bindFriendActionButtons() {
    const profileButtons =
        document.querySelectorAll(
            ".friend-profile-button"
        );

    profileButtons.forEach(
        button => {
            if (
                button.dataset.bound ===
                "true"
            ) {
                return;
            }

            button.dataset.bound =
                "true";

            button.addEventListener(
                "click",
                () => {
                    openProfilePopup(
                        button.dataset.playerId
                    );
                }
            );
        }
    );

    const chatButtons =
        document.querySelectorAll(
            ".friend-chat-button"
        );

    chatButtons.forEach(
        button => {
            if (
                button.dataset.bound ===
                "true"
            ) {
                return;
            }

            button.dataset.bound =
                "true";

            button.addEventListener(
                "click",
                () => {
                    openFriendChat(
                        button.dataset.playerId
                    );
                }
            );
        }
    );

    const pvpButtons =
        document.querySelectorAll(
            ".friend-pvp-button"
        );

    pvpButtons.forEach(
        button => {
            if (
                button.dataset.bound ===
                "true"
            ) {
                return;
            }

            button.dataset.bound =
                "true";

            button.addEventListener(
                "click",
                () => {
                    openFriendPvP(
                        button.dataset.playerId
                    );
                }
            );
        }
    );
}

function bindFriendRequestButtons() {
    const acceptButtons =
        document.querySelectorAll(
            ".friend-request-accept"
        );

    acceptButtons.forEach(
        button => {
            if (
                button.dataset.bound ===
                "true"
            ) {
                return;
            }

            button.dataset.bound =
                "true";

            button.addEventListener(
                "click",
                async () => {
                    const id =
                        button.dataset.requestId;

                    button.disabled =
                        true;

                    const success =
                        await acceptFriend(
                            id
                        );

                    if (!success) {
                        button.disabled =
                            false;
                    }
                }
            );
        }
    );

    const rejectButtons =
        document.querySelectorAll(
            ".friend-request-reject"
        );

    rejectButtons.forEach(
        button => {
            if (
                button.dataset.bound ===
                "true"
            ) {
                return;
            }

            button.dataset.bound =
                "true";

            button.addEventListener(
                "click",
                async () => {
                    const id =
                        button.dataset.requestId;

                    button.disabled =
                        true;

                    const success =
                        await rejectFriend(
                            id
                        );

                    if (!success) {
                        button.disabled =
                            false;
                    }
                }
            );
        }
    );
}

function bindAccountEvents() {
    const logoutButtons =
        document.querySelectorAll(
            "#logoutButton, .logout-button, [data-action='logout']"
        );

    logoutButtons.forEach(
        button => {
            if (
                button.dataset.accountBound ===
                "true"
            ) {
                return;
            }

            button.dataset.accountBound =
                "true";

            button.addEventListener(
                "click",
                event => {
                    event.preventDefault();
                    logout();
                }
            );
        }
    );

    const refreshButtons =
        document.querySelectorAll(
            "#refreshAccount, .refresh-account-button"
        );

    refreshButtons.forEach(
        button => {
            if (
                button.dataset.accountBound ===
                "true"
            ) {
                return;
            }

            button.dataset.accountBound =
                "true";

            button.addEventListener(
                "click",
                event => {
                    event.preventDefault();
                    refreshAccount();
                }
            );
        }
    );

    const searchButton =
        document.getElementById(
            "friendSearchButton"
        ) ||
        document.querySelector(
            ".friend-search-button"
        );

    if (
        searchButton &&
        searchButton.dataset.accountBound !==
        "true"
    ) {
        searchButton.dataset.accountBound =
            "true";

        searchButton.addEventListener(
            "click",
            event => {
                event.preventDefault();
                searchFriend();
            }
        );
    }

    const searchInput =
        document.getElementById(
            "friendSearchInput"
        ) ||
        document.querySelector(
            ".friend-search-input"
        );

    if (
        searchInput &&
        searchInput.dataset.accountBound !==
        "true"
    ) {
        searchInput.dataset.accountBound =
            "true";

        searchInput.addEventListener(
            "keydown",
            event => {
                if (
                    event.key ===
                    "Enter"
                ) {
                    event.preventDefault();
                    searchFriend();
                }
            }
        );
    }

    const popupCloseButtons =
        document.querySelectorAll(
            "#profilePopupClose, .profile-popup-close, [data-action='close-profile-popup']"
        );

    popupCloseButtons.forEach(
        button => {
            if (
                button.dataset.accountBound ===
                "true"
            ) {
                return;
            }

            button.dataset.accountBound =
                "true";

            button.addEventListener(
                "click",
                event => {
                    event.preventDefault();
                    closeProfilePopup();
                }
            );
        }
    );

    const popupOverlay =
        document.querySelector(
            "#profilePopup .profile-popup-overlay"
        ) ||
        document.querySelector(
            ".profile-popup-overlay"
        );

    if (
        popupOverlay &&
        popupOverlay.dataset.accountBound !==
        "true"
    ) {
        popupOverlay.dataset.accountBound =
            "true";

        popupOverlay.addEventListener(
            "click",
            closeProfilePopup
        );
    }

    bindFriendActionButtons();
    bindFriendRequestButtons();
}

function initAccountPage() {
    bindAccountEvents();

    loadAccount();
}

document.addEventListener(
    "DOMContentLoaded",
    initAccountPage,
    {
        once: true
    }
);

document.addEventListener(
    "keydown",
    event => {
        if (
            event.key === "Escape"
        ) {
            const popup =
                document.getElementById(
                    "profilePopup"
                );

            if (
                popup &&
                (
                    popup.classList.contains(
                        "show"
                    ) ||
                    popup.classList.contains(
                        "active"
                    )
                )
            ) {
                closeProfilePopup();
            }
        }
    }
);

window.addEventListener(
    "pagehide",
    () => {
        abortAllRequests();
    },
    {
        once: true
    }
);

window.addEventListener(
    "storage",
    event => {
        if (
            event.key ===
            "mathweb_token"
        ) {
            if (
                !event.newValue
            ) {
                handleUnauthorized();
                return;
            }

            accountLoaded =
                false;

            loadAccount(
                true
            );
        }
    }
);

window.MATHWEB_ACCOUNT = {
    load: loadAccount,
    refresh: refreshAccount,
    logout,
    openProfile:
        openProfilePopup,
    closeProfile:
        closeProfilePopup,
    searchFriend,
    sendFriendRequest,
    acceptFriend,
    rejectFriend,
    openFriendChat,
    openFriendPvP
};