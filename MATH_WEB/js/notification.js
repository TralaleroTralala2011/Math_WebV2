/* =========================================================
   MATH WEB - NOTIFICATION
   Global notification controller
========================================================= */

const NOTIFICATION_API_URL =
    window.MATHWEB_API_URL ||
    "http://127.0.0.1:8000";


/* =========================================================
   CONFIG
========================================================= */

const NOTIFICATION_TOKEN_KEY =
    "mathweb_token";

const NOTIFICATION_POLL_INTERVAL =
    10000;

const NOTIFICATION_REQUEST_TIMEOUT =
    15000;

const MAX_NOTIFICATION_DISPLAY =
    50;


/* =========================================================
   STATE
========================================================= */

let notificationBadgeLoading = false;
let notificationListLoading = false;
let notificationReadLoading = false;

let notificationBadgeTimer = null;

let notificationListRequestId = 0;

let notificationInitialized = false;


/* =========================================================
   AUTH
========================================================= */

function getNotificationToken() {

    const token =
        localStorage.getItem(
            NOTIFICATION_TOKEN_KEY
        );


    if (
        typeof token !== "string" ||
        !token.trim()
    ) {

        return null;

    }


    return token.trim();

}


/* =========================================================
   CLEAR AUTH
========================================================= */

function clearNotificationAuth() {

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


/* =========================================================
   API ERROR
========================================================= */

function getNotificationErrorMessage(
    data,
    fallback = "Có lỗi xảy ra."
) {

    if (!data) {
        return fallback;
    }


    if (
        typeof data.detail === "string"
    ) {

        return data.detail;

    }


    if (
        typeof data.message === "string"
    ) {

        return data.message;

    }


    if (
        typeof data.error === "string"
    ) {

        return data.error;

    }


    if (
        Array.isArray(data.detail)
    ) {

        const messages =
            data.detail
                .map(function (item) {

                    if (
                        typeof item === "string"
                    ) {

                        return item;

                    }

                    if (
                        item &&
                        typeof item.msg === "string"
                    ) {

                        return item.msg;

                    }

                    return "";

                })
                .filter(Boolean);


        if (
            messages.length > 0
        ) {

            return messages.join(", ");

        }

    }


    return fallback;

}


/* =========================================================
   FETCH WITH TIMEOUT
========================================================= */

async function notificationFetch(
    url,
    options = {}
) {

    const controller =
        new AbortController();


    const timeout =
        setTimeout(
            function () {

                controller.abort();

            },
            NOTIFICATION_REQUEST_TIMEOUT
        );


    const token =
        getNotificationToken();


    const headers = {
        "Accept":
            "application/json"
    };


    if (
        options.body &&
        !(
            options.body instanceof FormData
        )
    ) {

        headers[
            "Content-Type"
        ] =
            "application/json";

    }


    if (token) {

        headers[
            "Authorization"
        ] =
            `Bearer ${token}`;

    }


    try {

        const response =
            await fetch(
                url,
                {
                    ...options,
                    headers: {
                        ...headers,
                        ...(options.headers || {})
                    },
                    signal:
                        controller.signal
                }
            );


        let data = null;


        try {

            const text =
                await response.text();


            if (text) {

                try {

                    data =
                        JSON.parse(text);

                } catch {

                    data = text;

                }

            }

        } catch {

            data = null;

        }


        if (
            response.status === 401
        ) {

            clearNotificationAuth();


            return {
                ok: false,
                unauthorized: true,
                status: 401,
                data: data,
                message:
                    "Phiên đăng nhập đã hết hạn."
            };

        }


        if (
            !response.ok
        ) {

            return {
                ok: false,
                unauthorized: false,
                status:
                    response.status,
                data: data,
                message:
                    getNotificationErrorMessage(
                        data,
                        "Không thể kết nối máy chủ."
                    )
            };

        }


        return {
            ok: true,
            unauthorized: false,
            status:
                response.status,
            data: data,
            message: ""

        };

    } catch (error) {

        if (
            error &&
            error.name === "AbortError"
        ) {

            return {
                ok: false,
                unauthorized: false,
                timeout: true,
                status: 0,
                data: null,
                message:
                    "Yêu cầu mất quá nhiều thời gian."
            };

        }


        return {
            ok: false,
            unauthorized: false,
            timeout: false,
            status: 0,
            data: null,
            message:
                "Không thể kết nối máy chủ."
        };

    } finally {

        clearTimeout(
            timeout
        );

    }

}


/* =========================================================
   GET NOTIFICATIONS
========================================================= */

async function getNotifications() {

    const token =
        getNotificationToken();


    if (!token) {
        return [];
    }


    const result =
        await notificationFetch(
            `${NOTIFICATION_API_URL}/api/notifications`,
            {
                method: "GET"
            }
        );


    if (
        result.unauthorized
    ) {

        return [];

    }


    if (
        !result.ok
    ) {

        console.error(
            "Không thể tải thông báo:",
            result.message
        );

        return [];

    }


    let notifications =
        result.data;


    if (
        Array.isArray(
            result.data?.notifications
        )
    ) {

        notifications =
            result.data.notifications;

    }


    if (
        !Array.isArray(
            notifications
        )
    ) {

        return [];

    }


    return notifications
        .slice(
            0,
            MAX_NOTIFICATION_DISPLAY
        );

}


/* =========================================================
   GET UNREAD COUNT
========================================================= */

async function getUnreadNotificationCount() {

    const token =
        getNotificationToken();


    if (!token) {
        return 0;
    }


    const result =
        await notificationFetch(
            `${NOTIFICATION_API_URL}/api/notifications/unread-count`,
            {
                method: "GET"
            }
        );


    if (
        result.unauthorized ||
        !result.ok
    ) {

        return 0;

    }


    const count =
        Number(
            result.data?.count
        );


    if (
        !Number.isFinite(count)
    ) {

        return 0;

    }


    return Math.max(
        0,
        Math.floor(count)
    );

}


/* =========================================================
   MARK ONE NOTIFICATION READ
========================================================= */

async function markNotificationRead(
    id
) {

    const token =
        getNotificationToken();


    if (
        !token ||
        !id
    ) {

        return false;

    }


    const numericId =
        Number(id);


    if (
        !Number.isSafeInteger(
            numericId
        ) ||
        numericId <= 0
    ) {

        return false;

    }


    if (
        notificationReadLoading
    ) {

        return false;

    }


    notificationReadLoading = true;


    try {

        const result =
            await notificationFetch(
                `${NOTIFICATION_API_URL}/api/notifications/${encodeURIComponent(numericId)}/read`,
                {
                    method: "POST"
                }
            );


        return Boolean(
            result.ok
        );

    } finally {

        notificationReadLoading = false;

    }

}


/* =========================================================
   MARK ALL NOTIFICATIONS READ
========================================================= */

async function markAllNotificationsRead() {

    const token =
        getNotificationToken();


    if (!token) {
        return false;
    }


    const result =
        await notificationFetch(
            `${NOTIFICATION_API_URL}/api/notifications/read-all`,
            {
                method: "POST"
            }
        );


    return Boolean(
        result.ok
    );

}


/* =========================================================
   NOTIFICATION ICON
========================================================= */

function getNotificationIcon(
    type
) {

    const icons = {
        friend_request: "👤",
        friend_accepted: "🤝",
        chat_message: "💬",
        pvp_invite: "⚔️",
        game_completed: "🎮",
        level_up: "⭐",
        achievement: "🏆"
    };


    return (
        icons[type] ||
        "🔔"
    );

}


/* =========================================================
   NOTIFICATION TITLE
========================================================= */

function getNotificationTitle(
    notification
) {

    if (
        notification &&
        typeof notification.title ===
            "string" &&
        notification.title.trim()
    ) {

        return notification.title.trim();

    }


    const titles = {
        friend_request:
            "Lời mời kết bạn",

        friend_accepted:
            "Đã chấp nhận lời mời",

        chat_message:
            "Tin nhắn mới",

        pvp_invite:
            "Lời mời PvP",

        game_completed:
            "Hoàn thành game",

        level_up:
            "Lên cấp!",

        achievement:
            "Thành tựu mới"
    };


    return (
        titles[
            notification?.type
        ] ||
        "Thông báo"
    );

}


/* =========================================================
   NOTIFICATION MESSAGE
========================================================= */

function getNotificationMessage(
    notification
) {

    if (
        !notification
    ) {

        return "";

    }


    if (
        typeof notification.message ===
            "string"
    ) {

        return notification.message;

    }


    if (
        typeof notification.content ===
            "string"
    ) {

        return notification.content;

    }


    return "";

}


/* =========================================================
   DATE PARSER
========================================================= */

function parseNotificationDate(
    dateString
) {

    if (
        !dateString
    ) {

        return null;

    }


    if (
        dateString instanceof Date
    ) {

        return dateString;

    }


    if (
        typeof dateString !== "string"
    ) {

        return null;

    }


    let normalized =
        dateString.trim();


    if (
        !normalized
    ) {

        return null;

    }


    /*
       Backend lưu UTC dạng:
       YYYY-MM-DD HH:MM:SS

       Nếu không có timezone,
       coi là UTC để hiển thị đúng
       theo múi giờ máy người dùng.
    */

    if (
        /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/
            .test(normalized)
    ) {

        normalized =
            normalized.replace(
                " ",
                "T"
            ) + "Z";

    }


    if (
        /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/
            .test(normalized)
    ) {

        normalized += "Z";

    }


    const date =
        new Date(
            normalized
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return null;

    }


    return date;

}


/* =========================================================
   FORMAT NOTIFICATION DATE
========================================================= */

function formatNotificationDate(
    dateString
) {

    const date =
        parseNotificationDate(
            dateString
        );


    if (
        !date
    ) {

        return "";

    }


    const now =
        new Date();


    const diff =
        Math.max(
            0,
            now.getTime() -
                date.getTime()
        );


    const minute =
        60 * 1000;

    const hour =
        60 * minute;

    const day =
        24 * hour;


    if (
        diff < minute
    ) {

        return "Vừa xong";

    }


    if (
        diff < hour
    ) {

        return (
            Math.floor(
                diff / minute
            ) +
            " phút trước"
        );

    }


    if (
        diff < day &&
        date.toDateString() ===
            now.toDateString()
    ) {

        return (
            Math.floor(
                diff / hour
            ) +
            " giờ trước"
        );

    }


    return date.toLocaleString(
        "vi-VN",
        {
            day: "2-digit",
            month: "2-digit",
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeNotificationHTML(
    text
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        text == null
            ? ""
            : String(text);


    return div.innerHTML;

}


/* =========================================================
   SAFE NOTIFICATION ID
========================================================= */

function getNotificationId(
    notification
) {

    const id =
        Number(
            notification?.id
        );


    if (
        !Number.isSafeInteger(id) ||
        id <= 0
    ) {

        return null;

    }


    return id;

}


/* =========================================================
   UPDATE BADGE
========================================================= */

function renderNotificationBadge(
    count
) {

    const badge =
        document.getElementById(
            "notificationBadge"
        );


    if (!badge) {
        return;
    }


    const safeCount =
        Math.max(
            0,
            Number(count) || 0
        );


    if (
        safeCount <= 0
    ) {

        badge.textContent =
            "";

        badge.style.display =
            "none";

        badge.setAttribute(
            "aria-label",
            "Không có thông báo chưa đọc"
        );

        return;

    }


    badge.textContent =
        safeCount > 99
            ? "99+"
            : String(safeCount);


    badge.style.display =
        "flex";


    badge.setAttribute(
        "aria-label",
        `${safeCount} thông báo chưa đọc`
    );

}


/* =========================================================
   LOAD NOTIFICATION BADGE
========================================================= */

async function loadNotificationBadge() {

    const badge =
        document.getElementById(
            "notificationBadge"
        );


    if (!badge) {
        return;
    }


    if (
        notificationBadgeLoading
    ) {

        return;

    }


    if (
        !getNotificationToken()
    ) {

        renderNotificationBadge(
            0
        );

        return;

    }


    notificationBadgeLoading = true;


    try {

        const count =
            await getUnreadNotificationCount();


        renderNotificationBadge(
            count
        );

    } finally {

        notificationBadgeLoading = false;

    }

}


/* =========================================================
   CREATE NOTIFICATION ITEM
========================================================= */

function createNotificationItem(
    notification
) {

    const item =
        document.createElement(
            "div"
        );


    item.className =
        "notification-item";


    if (
        !notification.is_read
    ) {

        item.classList.add(
            "unread"
        );

    }


    const icon =
        document.createElement(
            "div"
        );


    icon.className =
        "notification-icon";


    icon.textContent =
        getNotificationIcon(
            notification.type
        );


    const content =
        document.createElement(
            "div"
        );


    content.className =
        "notification-content";


    const title =
        document.createElement(
            "div"
        );


    title.className =
        "notification-title";


    title.textContent =
        getNotificationTitle(
            notification
        );


    const message =
        document.createElement(
            "div"
        );


    message.className =
        "notification-text";


    message.textContent =
        getNotificationMessage(
            notification
        );


    const time =
        document.createElement(
            "div"
        );


    time.className =
        "notification-time";


    time.textContent =
        formatNotificationDate(
            notification.created_at
        );


    content.appendChild(
        title
    );

    if (
        message.textContent
    ) {

        content.appendChild(
            message
        );

    }

    if (
        time.textContent
    ) {

        content.appendChild(
            time
        );

    }


    item.appendChild(
        icon
    );

    item.appendChild(
        content
    );


    item.dataset.notificationId =
        String(
            notification.id
        );


    return item;

}


/* =========================================================
   RENDER EMPTY
========================================================= */

function renderNotificationEmpty(
    message
) {

    const list =
        document.getElementById(
            "notificationList"
        );


    if (!list) {
        return;
    }


    list.innerHTML = `
        <div class="notification-empty">
            ${escapeNotificationHTML(
                message
            )}
        </div>
    `;

}


/* =========================================================
   LOAD NOTIFICATION LIST
========================================================= */

async function loadNotificationList() {

    const list =
        document.getElementById(
            "notificationList"
        );


    if (!list) {
        return;
    }


    if (
        notificationListLoading
    ) {

        return;

    }


    const token =
        getNotificationToken();


    if (!token) {

        renderNotificationEmpty(
            "Vui lòng đăng nhập để xem thông báo."
        );

        return;

    }


    notificationListLoading = true;


    const requestId =
        ++notificationListRequestId;


    list.innerHTML = `
        <div class="notification-empty">
            Đang tải thông báo...
        </div>
    `;


    try {

        const notifications =
            await getNotifications();


        if (
            requestId !==
            notificationListRequestId
        ) {

            return;

        }


        list.innerHTML = "";


        if (
            notifications.length === 0
        ) {

            renderNotificationEmpty(
                "Chưa có thông báo"
            );

            return;

        }


        notifications.forEach(
            function (notification) {

                const id =
                    getNotificationId(
                        notification
                    );


                if (!id) {
                    return;
                }


                const item =
                    createNotificationItem(
                        {
                            ...notification,
                            id: id
                        }
                    );


                item.addEventListener(
                    "click",
                    async function () {

                        if (
                            notification.is_read
                        ) {

                            return;

                        }


                        if (
                            item.dataset.reading ===
                            "true"
                        ) {

                            return;

                        }


                        item.dataset.reading =
                            "true";


                        const success =
                            await markNotificationRead(
                                id
                            );


                        item.dataset.reading =
                            "false";


                        if (
                            !success
                        ) {

                            return;

                        }


                        notification.is_read =
                            true;


                        item.classList.remove(
                            "unread"
                        );


                        await loadNotificationBadge();

                    }
                );


                list.appendChild(
                    item
                );

            }
        );


        if (
            list.children.length === 0
        ) {

            renderNotificationEmpty(
                "Chưa có thông báo"
            );

        }

    } catch (error) {

        console.error(
            "Lỗi tải danh sách thông báo:",
            error
        );


        if (
            requestId ===
            notificationListRequestId
        ) {

            renderNotificationEmpty(
                "Không thể tải thông báo. Vui lòng thử lại."
            );

        }

    } finally {

        notificationListLoading = false;

    }

}


/* =========================================================
   OPEN NOTIFICATIONS
========================================================= */

async function openNotifications() {

    const panel =
        document.getElementById(
            "notificationPanel"
        );


    const button =
        document.getElementById(
            "notificationButton"
        );


    if (!panel) {
        return;
    }


    const isOpening =
        !panel.classList.contains(
            "active"
        );


    panel.classList.toggle(
        "active"
    );


    if (button) {

        button.setAttribute(
            "aria-expanded",
            isOpening
                ? "true"
                : "false"
        );

    }


    if (
        !isOpening
    ) {

        return;

    }


    await loadNotificationList();

    await loadNotificationBadge();

}


/* =========================================================
   CLOSE NOTIFICATIONS
========================================================= */

function closeNotifications() {

    const panel =
        document.getElementById(
            "notificationPanel"
        );


    const button =
        document.getElementById(
            "notificationButton"
        );


    if (!panel) {
        return;
    }


    panel.classList.remove(
        "active"
    );


    if (button) {

        button.setAttribute(
            "aria-expanded",
            "false"
        );

    }

}


/* =========================================================
   MARK ALL AS READ UI
========================================================= */

async function handleMarkAllNotificationsRead(
    event
) {

    if (event) {

        event.preventDefault();
        event.stopPropagation();

    }


    if (
        !getNotificationToken()
    ) {

        return;

    }


    const button =
        document.getElementById(
            "readAllNotifications"
        );


    if (
        button &&
        button.dataset.loading ===
            "true"
    ) {

        return;

    }


    if (button) {

        button.dataset.loading =
            "true";

        button.disabled =
            true;

    }


    try {

        const success =
            await markAllNotificationsRead();


        if (
            !success
        ) {

            return;

        }


        const unreadItems =
            document.querySelectorAll(
                "#notificationList .notification-item.unread"
            );


        unreadItems.forEach(
            function (item) {

                item.classList.remove(
                    "unread"
                );

            }
        );


        renderNotificationBadge(
            0
        );


    } finally {

        if (button) {

            button.dataset.loading =
                "false";

            button.disabled =
                false;

        }

    }

}


/* =========================================================
   OUTSIDE CLICK
========================================================= */

function handleNotificationOutsideClick(
    event
) {

    const panel =
        document.getElementById(
            "notificationPanel"
        );


    const button =
        document.getElementById(
            "notificationButton"
        );


    if (
        !panel ||
        !button
    ) {

        return;

    }


    if (
        !panel.classList.contains(
            "active"
        )
    ) {

        return;

    }


    if (
        panel.contains(
            event.target
        ) ||
        button.contains(
            event.target
        )
    ) {

        return;

    }


    closeNotifications();

}


/* =========================================================
   ESCAPE KEY
========================================================= */

function handleNotificationEscape(
    event
) {

    if (
        event.key !== "Escape"
    ) {

        return;

    }


    closeNotifications();

}


/* =========================================================
   POLLING
========================================================= */

function startNotificationPolling() {

    stopNotificationPolling();


    if (
        !getNotificationToken()
    ) {

        return;

    }


    notificationBadgeTimer =
        setInterval(
            async function () {

                if (
                    document.hidden
                ) {

                    return;

                }


                if (
                    !getNotificationToken()
                ) {

                    stopNotificationPolling();

                    renderNotificationBadge(
                        0
                    );

                    return;

                }


                await loadNotificationBadge();

            },
            NOTIFICATION_POLL_INTERVAL
        );

}


function stopNotificationPolling() {

    if (
        notificationBadgeTimer
    ) {

        clearInterval(
            notificationBadgeTimer
        );

        notificationBadgeTimer =
            null;

    }

}


/* =========================================================
   VISIBILITY CHANGE
========================================================= */

function handleNotificationVisibility() {

    if (
        document.hidden
    ) {

        return;

    }


    if (
        !getNotificationToken()
    ) {

        renderNotificationBadge(
            0
        );

        stopNotificationPolling();

        return;

    }


    loadNotificationBadge();


    const panel =
        document.getElementById(
            "notificationPanel"
        );


    if (
        panel &&
        panel.classList.contains(
            "active"
        )
    ) {

        loadNotificationList();

    }

}


/* =========================================================
   STORAGE CHANGE
========================================================= */

function handleNotificationStorage(
    event
) {

    if (
        event.key !==
        NOTIFICATION_TOKEN_KEY
    ) {

        return;

    }


    if (
        getNotificationToken()
    ) {

        loadNotificationBadge();

        startNotificationPolling();

    } else {

        renderNotificationBadge(
            0
        );

        closeNotifications();

        stopNotificationPolling();

    }

}


/* =========================================================
   INITIALIZE
========================================================= */

async function initializeNotifications() {

    if (
        notificationInitialized
    ) {

        return;

    }


    notificationInitialized =
        true;


    const button =
        document.getElementById(
            "notificationButton"
        );


    const readAllButton =
        document.getElementById(
            "readAllNotifications"
        );


    if (button) {

        button.setAttribute(
            "aria-expanded",
            "false"
        );


        if (
            !button.dataset.notificationBound
        ) {

            button.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();
                    event.stopPropagation();

                    openNotifications();

                }
            );


            button.dataset.notificationBound =
                "true";

        }

    }


    if (
        readAllButton &&
        !readAllButton.dataset.notificationBound
    ) {

        readAllButton.addEventListener(
            "click",
            handleMarkAllNotificationsRead
        );


        readAllButton.dataset.notificationBound =
            "true";

    }


    document.addEventListener(
        "click",
        handleNotificationOutsideClick
    );


    document.addEventListener(
        "keydown",
        handleNotificationEscape
    );


    document.addEventListener(
        "visibilitychange",
        handleNotificationVisibility
    );


    window.addEventListener(
        "storage",
        handleNotificationStorage
    );


    if (
        getNotificationToken()
    ) {

        await loadNotificationBadge();

        startNotificationPolling();

    } else {

        renderNotificationBadge(
            0
        );

    }

}


/* =========================================================
   PUBLIC API
========================================================= */

window.MATHWEB_NOTIFICATIONS = {
    getNotifications,
    getUnreadNotificationCount,
    markNotificationRead,
    markAllNotificationsRead,
    loadNotificationBadge,
    loadNotificationList,
    openNotifications,
    closeNotifications,
    startNotificationPolling,
    stopNotificationPolling
};


/* =========================================================
   START
========================================================= */

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeNotifications,
        {
            once: true
        }
    );

} else {

    initializeNotifications();

}