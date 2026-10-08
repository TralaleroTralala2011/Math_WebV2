/* =========================================================
   MATH WEB - MAIN
   Frontend global controller
========================================================= */

const MAIN_API_URL = "http://127.0.0.1:8000";

const AUTH_TOKEN_KEY = "mathweb_token";
const AUTH_USER_KEY = "mathweb_user";
const AUTH_PROFILE_KEY = "mathweb_profile";

const CHAT_FRIEND_STORAGE_KEY = "mathweb_open_chat_friend";

const CHAT_UNREAD_REFRESH_INTERVAL = 10000;
const CHAT_FRIEND_REFRESH_INTERVAL = 15000;

let chatTaskbarPanel = null;
let chatTaskbarList = null;
let chatTaskbarBadge = null;

let chatUnreadRefreshTimer = null;
let chatFriendRefreshTimer = null;

let chatTaskbarLoading = false;
let chatUnreadLoading = false;


/* =========================================================
   CHAT FULLSCREEN / MESSENGER STYLE
========================================================= */

function installChatFullscreenStyle() {

    if (
        document.getElementById(
            "mathweb-chat-fullscreen-style"
        )
    ) {
        return;
    }

    const style =
        document.createElement("style");

    style.id =
        "mathweb-chat-fullscreen-style";

    style.textContent = `

        /* =====================================================
           CHAT OVERLAY
        ===================================================== */

        #chatTaskbarPanel.mathweb-chat-fullscreen {

            position: fixed !important;

            top: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            left: 0 !important;

            width: 100vw !important;
            min-width: 100vw !important;

            height: 100vh !important;
            height: 100dvh !important;

            min-height: 100vh !important;
            min-height: 100dvh !important;

            max-width: none !important;
            max-height: none !important;

            margin: 0 !important;
            padding: 0 !important;

            box-sizing: border-box !important;

            border: 0 !important;
            border-radius: 0 !important;

            overflow: hidden !important;

            transform: none !important;

            opacity: 1 !important;
            visibility: visible !important;

            pointer-events: auto !important;

            display: flex !important;
            flex-direction: column !important;

            z-index: 2147483647 !important;

            background:
                linear-gradient(
                    145deg,
                    rgba(10, 15, 29, 0.99),
                    rgba(6, 10, 20, 0.99)
                ) !important;

            box-shadow: none !important;

        }


        /* =====================================================
           CHAT HEADER
        ===================================================== */

        #chatTaskbarPanel.mathweb-chat-fullscreen
        .chat-taskbar-header {

            flex: 0 0 auto !important;

            width: 100% !important;

            min-height: 72px !important;

            box-sizing: border-box !important;

            display: flex !important;

            align-items: center !important;

            justify-content: space-between !important;

            gap: 15px !important;

            padding:
                14px
                max(18px, 4vw) !important;

            border-bottom:
                1px solid
                rgba(255, 255, 255, 0.08) !important;

            background:
                rgba(7, 10, 19, 0.97) !important;

            position: relative !important;

            z-index: 2 !important;

        }


        /* =====================================================
           CHAT LIST
        ===================================================== */

        #chatTaskbarPanel.mathweb-chat-fullscreen
        .chat-taskbar-list {

            flex: 1 1 auto !important;

            width: 100% !important;

            min-width: 0 !important;
            min-height: 0 !important;

            box-sizing: border-box !important;

            overflow-y: auto !important;
            overflow-x: hidden !important;

            -webkit-overflow-scrolling: touch !important;

            overscroll-behavior: contain !important;

            padding:
                18px
                max(18px, 4vw)
                30px !important;

            touch-action: pan-y !important;

        }


        /* =====================================================
           CLOSE BUTTON
        ===================================================== */

        #chatTaskbarPanel.mathweb-chat-fullscreen
        .chat-panel-close {

            flex: 0 0 auto !important;

            width: 42px !important;
            height: 42px !important;

            display: flex !important;

            align-items: center !important;
            justify-content: center !important;

            box-sizing: border-box !important;

            border:
                1px solid
                rgba(255, 255, 255, 0.10) !important;

            border-radius: 12px !important;

            background:
                rgba(255, 255, 255, 0.045) !important;

            color: #c9d4e5 !important;

            font-size: 25px !important;

            line-height: 1 !important;

            cursor: pointer !important;

            transition:
                background 0.2s ease,
                color 0.2s ease,
                border-color 0.2s ease,
                transform 0.2s ease !important;

        }


        #chatTaskbarPanel.mathweb-chat-fullscreen
        .chat-panel-close:hover {

            color: white !important;

            border-color:
                rgba(255, 80, 110, 0.45) !important;

            background:
                rgba(255, 80, 110, 0.10) !important;

            transform: rotate(90deg) !important;

        }


        /* =====================================================
           FRIEND ITEM
        ===================================================== */

        #chatTaskbarPanel.mathweb-chat-fullscreen
        .chat-friend-item {

            width: 100% !important;

            min-width: 0 !important;

            box-sizing: border-box !important;

        }


        /* =====================================================
           BODY SCROLL LOCK
        ===================================================== */

        html.mathweb-chat-lock,
        body.mathweb-chat-lock {

            overflow: hidden !important;

            overscroll-behavior: none !important;

        }


        body.mathweb-chat-lock {

            touch-action: none !important;

        }


        /* =====================================================
           MOBILE
        ===================================================== */

        @media (max-width: 700px) {

            #chatTaskbarPanel.mathweb-chat-fullscreen {

                width: 100vw !important;
                min-width: 100vw !important;

                height: 100vh !important;
                height: 100dvh !important;

                min-height: 100vh !important;
                min-height: 100dvh !important;

            }


            #chatTaskbarPanel.mathweb-chat-fullscreen
            .chat-taskbar-header {

                min-height: 64px !important;

                padding:
                    max(
                        10px,
                        env(safe-area-inset-top)
                    )
                    14px
                    10px
                    14px !important;

            }


            #chatTaskbarPanel.mathweb-chat-fullscreen
            .chat-taskbar-list {

                padding:
                    12px
                    12px
                    max(
                        20px,
                        env(safe-area-inset-bottom)
                    ) !important;

            }


            #chatTaskbarPanel.mathweb-chat-fullscreen
            .chat-panel-close {

                width: 40px !important;
                height: 40px !important;

                border-radius: 10px !important;

                font-size: 24px !important;

            }


            #chatTaskbarPanel.mathweb-chat-fullscreen
            .chat-friend-item {

                min-height: 68px !important;

            }

        }


        /* =====================================================
           VERY SMALL PHONES
        ===================================================== */

        @media (max-width: 420px) {

            #chatTaskbarPanel.mathweb-chat-fullscreen
            .chat-taskbar-header {

                padding-left: 10px !important;
                padding-right: 10px !important;

            }


            #chatTaskbarPanel.mathweb-chat-fullscreen
            .chat-taskbar-list {

                padding-left: 8px !important;
                padding-right: 8px !important;

            }

        }

    `;

    document.head.appendChild(style);
}


/* =========================================================
   CHAT BODY SCROLL LOCK
========================================================= */

function setChatFullscreenState(
    isOpen
) {

    const html =
        document.documentElement;

    const body =
        document.body;

    if (!html || !body) {
        return;
    }

    if (isOpen) {

        html.classList.add(
            "mathweb-chat-lock"
        );

        body.classList.add(
            "mathweb-chat-lock"
        );

    } else {

        html.classList.remove(
            "mathweb-chat-lock"
        );

        body.classList.remove(
            "mathweb-chat-lock"
        );

    }
}


/* =========================================================
   MOBILE MENU
========================================================= */

const mobileMenuButton =
    document.getElementById(
        "mobileMenuButton"
    );

const navMenu =
    document.querySelector(
        ".nav-menu"
    );


function closeMobileMenu() {

    if (!navMenu) {
        return;
    }

    navMenu.classList.remove(
        "show"
    );

    if (mobileMenuButton) {

        mobileMenuButton.textContent =
            "☰";

        mobileMenuButton.setAttribute(
            "aria-expanded",
            "false"
        );

    }

}


function toggleMobileMenu() {

    if (!navMenu || !mobileMenuButton) {
        return;
    }

    const isOpen =
        navMenu.classList.toggle(
            "show"
        );

    mobileMenuButton.textContent =
        isOpen
            ? "✕"
            : "☰";

    mobileMenuButton.setAttribute(
        "aria-expanded",
        isOpen
            ? "true"
            : "false"
    );

}


if (
    mobileMenuButton &&
    navMenu
) {

    mobileMenuButton.setAttribute(
        "aria-expanded",
        "false"
    );


    mobileMenuButton.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

            toggleMobileMenu();

        }
    );


    const navLinks =
        document.querySelectorAll(
            ".nav-link, .nav-button, .nav-chat-button"
        );


    navLinks.forEach(
        function (link) {

            link.addEventListener(
                "click",
                function () {

                    closeMobileMenu();

                }
            );

        }
    );


    document.addEventListener(
        "click",
        function (event) {

            if (
                !navMenu.classList.contains(
                    "show"
                )
            ) {

                return;

            }


            if (
                event.target.closest(
                    ".nav-menu"
                ) ||
                event.target.closest(
                    "#mobileMenuButton"
                )
            ) {

                return;

            }


            closeMobileMenu();

        }
    );

}


/* =========================================================
   SCROLL EFFECT
========================================================= */

const navbar =
    document.querySelector(
        ".navbar"
    );


function updateNavbarScrollState() {

    if (!navbar) {
        return;
    }


    if (
        window.scrollY > 30
    ) {

        navbar.style.background =
            "rgba(7, 10, 19, 0.92)";

        navbar.style.boxShadow =
            "0 10px 35px rgba(0, 0, 0, 0.18)";

    } else {

        navbar.style.background =
            "rgba(7, 10, 19, 0.78)";

        navbar.style.boxShadow =
            "none";

    }

}


window.addEventListener(
    "scroll",
    updateNavbarScrollState,
    {
        passive: true
    }
);


updateNavbarScrollState();


/* =========================================================
   SMOOTH ANCHOR
========================================================= */

const anchorLinks =
    document.querySelectorAll(
        'a[href^="#"]'
    );


anchorLinks.forEach(
    function (link) {

        link.addEventListener(
            "click",
            function (event) {

                const targetId =
                    link.getAttribute(
                        "href"
                    );


                if (
                    !targetId ||
                    targetId === "#"
                ) {

                    return;

                }


                let target = null;


                try {

                    target =
                        document.querySelector(
                            targetId
                        );

                } catch {

                    return;

                }


                if (!target) {
                    return;
                }


                event.preventDefault();


                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });


                if (history.pushState) {

                    try {

                        history.pushState(
                            null,
                            "",
                            targetId
                        );

                    } catch {
                        // Không làm gián đoạn cuộn.
                    }

                }

            }
        );

    }
);


/* =========================================================
   REVEAL ANIMATION
========================================================= */

const revealElements =
    document.querySelectorAll(
        ".feature-card, .section-heading, .start-box"
    );


if (
    "IntersectionObserver" in window
) {

    const observer =
        new IntersectionObserver(
            function (entries) {

                entries.forEach(
                    function (entry) {

                        if (
                            entry.isIntersecting
                        ) {

                            entry.target.classList.add(
                                "reveal-visible"
                            );

                            observer.unobserve(
                                entry.target
                            );

                        }

                    }
                );

            },
            {
                threshold: 0.15
            }
        );


    revealElements.forEach(
        function (element) {

            element.classList.add(
                "reveal-hidden"
            );

            observer.observe(
                element
            );

        }
    );

} else {

    revealElements.forEach(
        function (element) {

            element.classList.add(
                "reveal-visible"
            );

        }
    );

}


/* =========================================================
   AUTH
========================================================= */

function getLoginToken() {

    const token =
        localStorage.getItem(
            AUTH_TOKEN_KEY
        );


    if (
        typeof token !== "string" ||
        !token.trim()
    ) {

        return null;

    }


    return token.trim();

}


function getSavedAuthUser() {

    try {

        const raw =
            localStorage.getItem(
                AUTH_USER_KEY
            );


        if (!raw) {
            return null;
        }


        const user =
            JSON.parse(
                raw
            );


        if (
            !user ||
            typeof user !== "object"
        ) {

            return null;

        }


        return user;

    } catch {

        return null;

    }

}


function getSavedProfile() {

    try {

        const raw =
            localStorage.getItem(
                AUTH_PROFILE_KEY
            );


        if (!raw) {
            return null;
        }


        const profile =
            JSON.parse(
                raw
            );


        if (
            !profile ||
            typeof profile !== "object"
        ) {

            return null;

        }


        return profile;

    } catch {

        return null;

    }

}


function clearLoginData() {

    localStorage.removeItem(
        AUTH_TOKEN_KEY
    );

    localStorage.removeItem(
        AUTH_USER_KEY
    );

    localStorage.removeItem(
        AUTH_PROFILE_KEY
    );

}


function isAuthenticated() {

    return Boolean(
        getLoginToken()
    );

}


/* =========================================================
   NAVIGATION HELPERS
========================================================= */

function goToAccount() {

    if (
        isAuthenticated()
    ) {

        window.location.href =
            "account.html";

    } else {

        window.location.href =
            "login.html";

    }

}


function goToPractice() {

    if (
        isAuthenticated()
    ) {

        window.location.href =
            "practice.html";

    } else {

        window.location.href =
            "login.html";

    }

}


function goToBattle() {

    if (
        isAuthenticated()
    ) {

        window.location.href =
            "battle.html";

    } else {

        window.location.href =
            "login.html";

    }

}


/* =========================================================
   PRACTICE PROTECTION
========================================================= */

const practiceLinks =
    document.querySelectorAll(
        ".protected-practice-link"
    );


practiceLinks.forEach(
    function (link) {

        link.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                goToPractice();

            }
        );

    }
);


/* =========================================================
   ACCOUNT PROTECTION
========================================================= */

const accountLinks =
    document.querySelectorAll(
        ".protected-account-link"
    );


accountLinks.forEach(
    function (link) {

        link.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                goToAccount();

            }
        );

    }
);


/* =========================================================
   BATTLE PROTECTION
========================================================= */

const battleLinks =
    document.querySelectorAll(
        ".protected-battle-link"
    );


battleLinks.forEach(
    function (link) {

        link.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                goToBattle();

            }
        );

    }
);


/* =========================================================
   CURRENT PAGE
========================================================= */

const currentPage =
    window.location.pathname
        .split("/")
        .pop()
        .toLowerCase();


/* =========================================================
   DIRECT PRACTICE PROTECTION
========================================================= */

if (
    currentPage === "practice.html"
) {

    if (
        !isAuthenticated()
    ) {

        window.location.replace(
            "login.html"
        );

    }

}


/* =========================================================
   DIRECT ACCOUNT PROTECTION
========================================================= */

if (
    currentPage === "account.html"
) {

    if (
        !isAuthenticated()
    ) {

        window.location.replace(
            "login.html"
        );

    }

}


/* =========================================================
   DIRECT BATTLE PROTECTION
========================================================= */

if (
    currentPage === "battle.html"
) {

    if (
        !isAuthenticated()
    ) {

        window.location.replace(
            "login.html"
        );

    }

}


/* =========================================================
   CHAT TASKBAR
========================================================= */

function createChatTaskbar() {

    const nav =
        document.querySelector(
            ".nav-menu"
        );


    if (!nav) {
        return;
    }


    const existingWrapper =
        document.getElementById(
            "chatNavWrapper"
        );


    if (existingWrapper) {

        chatTaskbarPanel =
            document.getElementById(
                "chatTaskbarPanel"
            );

        chatTaskbarList =
            document.getElementById(
                "chatTaskbarList"
            );

        chatTaskbarBadge =
            document.getElementById(
                "chatNavBadge"
            );

        return;

    }


    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.id =
        "chatNavWrapper";


    wrapper.className =
        "chat-nav-wrapper";


    const button =
        document.createElement(
            "button"
        );


    button.type =
        "button";


    button.id =
        "chatNavButton";


    button.className =
        "nav-chat-button";


    button.setAttribute(
        "aria-label",
        "Mở Chat"
    );


    button.setAttribute(
        "aria-expanded",
        "false"
    );


    button.innerHTML = `
        <span class="chat-nav-icon">💬</span>
        <span>Chat</span>
        <span
            id="chatNavBadge"
            class="chat-nav-badge"
            style="display:none"
        ></span>
    `;


    const panel =
        document.createElement(
            "div"
        );


    panel.id =
        "chatTaskbarPanel";


    panel.className =
        "chat-taskbar-panel";


    panel.innerHTML = `
        <div class="chat-taskbar-header">

            <div>
                <strong>Đoạn chat</strong>

                <small>
                    Bạn bè của bạn
                </small>
            </div>

            <button
                type="button"
                id="chatPanelClose"
                class="chat-panel-close"
                aria-label="Đóng Chat"
            >
                ×
            </button>

        </div>

        <div
            id="chatTaskbarList"
            class="chat-taskbar-list"
        ></div>
    `;


    /* =====================================================
       BUTTON NẰM TRONG NAVBAR
    ===================================================== */

    wrapper.appendChild(
        button
    );


    const notificationWrapper =
        nav.querySelector(
            ".notification-wrapper"
        );


    if (notificationWrapper) {

        nav.insertBefore(
            wrapper,
            notificationWrapper
        );

    } else {

        nav.appendChild(
            wrapper
        );

    }


    /* =====================================================
       PANEL ĐƯA THẲNG RA BODY
       ĐỂ FIXED THỰC SỰ BÁM VIEWPORT
    ===================================================== */

    document.body.appendChild(
        panel
    );


    chatTaskbarPanel =
        panel;


    chatTaskbarList =
        document.getElementById(
            "chatTaskbarList"
        );


    chatTaskbarBadge =
        document.getElementById(
            "chatNavBadge"
        );


    /* =====================================================
       OPEN CHAT
    ===================================================== */

    button.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

            toggleChatTaskbar();

        }
    );


    /* =====================================================
       CLOSE CHAT
    ===================================================== */

    const closeButton =
        document.getElementById(
            "chatPanelClose"
        );


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                closeChatTaskbar();

            }
        );

    }


    /* =====================================================
       KHÔNG CHO CLICK TRONG PANEL
       BỊ COI LÀ CLICK OUTSIDE
    ===================================================== */

    panel.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

        }
    );


    loadChatFriends();

}


/* =========================================================
   OPEN / CLOSE CHAT PANEL
========================================================= */

function toggleChatTaskbar() {

    if (!chatTaskbarPanel) {
        return;
    }


    const isOpen =
        chatTaskbarPanel.classList.toggle(
            "show"
        );


    const button =
        document.getElementById(
            "chatNavButton"
        );


    if (button) {

        button.setAttribute(
            "aria-expanded",
            isOpen
                ? "true"
                : "false"
        );

    }


    if (isOpen) {

        /* =================================================
           MESSENGER FULLSCREEN
        ================================================= */

        chatTaskbarPanel.classList.add(
            "mathweb-chat-fullscreen"
        );


        setChatFullscreenState(
            true
        );


        loadChatFriends();

    } else {

        chatTaskbarPanel.classList.remove(
            "mathweb-chat-fullscreen"
        );


        setChatFullscreenState(
            false
        );

    }

}


/* =========================================================
   CLOSE CHAT PANEL
========================================================= */

function closeChatTaskbar() {

    if (!chatTaskbarPanel) {
        return;
    }


    chatTaskbarPanel.classList.remove(
        "show"
    );


    chatTaskbarPanel.classList.remove(
        "mathweb-chat-fullscreen"
    );


    setChatFullscreenState(
        false
    );


    const button =
        document.getElementById(
            "chatNavButton"
        );


    if (button) {

        button.setAttribute(
            "aria-expanded",
            "false"
        );

    }

}


/* =========================================================
   CLOSE CHAT WHEN CLICK OUTSIDE
========================================================= */

document.addEventListener(
    "click",
    function (event) {

        const insideChatWrapper =
            event.target.closest(
                "#chatNavWrapper"
            );


        const insideChatPanel =
            event.target.closest(
                "#chatTaskbarPanel"
            );


        if (
            !insideChatWrapper &&
            !insideChatPanel
        ) {

            closeChatTaskbar();

        }

    }
);


/* =========================================================
   CHAT API ERROR
========================================================= */

async function readMainAPIResponse(
    response
) {

    let data = null;


    try {

        data =
            await response.json();

    } catch {

        data = null;

    }


    if (
        response.status === 401
    ) {

        clearLoginData();


        return {
            ok: false,
            unauthorized: true,
            data: data
        };

    }


    if (!response.ok) {

        const detail =
            data?.detail ||
            data?.message ||
            data?.error ||
            "Không thể kết nối máy chủ.";


        return {
            ok: false,
            unauthorized: false,
            message: String(detail),
            data: data
        };

    }


    return {
        ok: true,
        unauthorized: false,
        data: data
    };

}


/* =========================================================
   LOAD FRIENDS FOR CHAT
========================================================= */

async function loadChatFriends(
    options = {}
) {

    if (!chatTaskbarList) {
        return;
    }


    if (
        chatTaskbarLoading
    ) {

        return;

    }


    const token =
        getLoginToken();


    if (!token) {

        updateChatBadge(0);

        return;

    }


    chatTaskbarLoading = true;


    if (
        options.showLoading !== false
    ) {

        chatTaskbarList.innerHTML = `
            <div class="chat-taskbar-loading">
                Đang tải danh sách bạn bè...
            </div>
        `;

    }


    try {

        const response =
            await fetch(
                `${MAIN_API_URL}/api/friends`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            "Bearer " + token,
                        "Accept":
                            "application/json"
                    }
                }
            );


        const result =
            await readMainAPIResponse(
                response
            );


        if (
            result.unauthorized
        ) {

            renderChatLoginRequired();

            updateNavbarAuth();

            return;

        }


        if (
            !result.ok
        ) {

            throw new Error(
                result.message
            );

        }


        let friends =
            result.data;


        if (
            !Array.isArray(
                friends
            )
        ) {

            if (
                Array.isArray(
                    result.data?.friends
                )
            ) {

                friends =
                    result.data.friends;

            } else {

                friends = [];

            }

        }


        renderChatFriends(
            friends
        );


    } catch (error) {

        console.error(
            "Không thể tải bạn bè:",
            error
        );


        chatTaskbarList.innerHTML = `
            <div class="chat-taskbar-empty">

                <strong>
                    Không thể tải danh sách bạn bè.
                </strong>

                <p>
                    ${escapeMainHTML(
                        error.message ||
                        "Đã xảy ra lỗi."
                    )}
                </p>

                <button
                    type="button"
                    class="chat-empty-button"
                    id="retryChatFriendsButton"
                >
                    🔄 Thử lại
                </button>

            </div>
        `;


        const retryButton =
            document.getElementById(
                "retryChatFriendsButton"
            );


        if (retryButton) {

            retryButton.addEventListener(
                "click",
                function () {

                    loadChatFriends();

                }
            );

        }


    } finally {

        chatTaskbarLoading = false;

    }

}


/* =========================================================
   LOGIN REQUIRED CHAT
========================================================= */

function renderChatLoginRequired() {

    if (!chatTaskbarList) {
        return;
    }


    chatTaskbarList.innerHTML = `
        <div class="chat-taskbar-empty">

            <div class="chat-empty-icon">
                🔐
            </div>

            <strong>
                Vui lòng đăng nhập
            </strong>

            <p>
                Đăng nhập để sử dụng Chat.
            </p>

            <a
                href="login.html"
                class="chat-empty-button"
            >
                🔑 Đăng nhập
            </a>

        </div>
    `;

}


/* =========================================================
   RENDER FRIEND LIST
========================================================= */

function renderChatFriends(
    friends
) {

    if (!chatTaskbarList) {
        return;
    }


    if (
        !Array.isArray(friends) ||
        friends.length === 0
    ) {

        chatTaskbarList.innerHTML = `
            <div class="chat-taskbar-empty">

                <div class="chat-empty-icon">
                    💬
                </div>

                <strong>
                    Không có bạn bè nào
                </strong>

                <p>
                    Hãy kết bạn để trò chuyện.
                </p>

                <a
                    href="account.html"
                    class="chat-empty-button"
                >
                    👥 Kết bạn
                </a>

            </div>
        `;


        updateChatBadge(0);

        return;

    }


    chatTaskbarList.innerHTML = "";


    friends.forEach(
        function (friend) {

            if (
                !friend ||
                !friend.id
            ) {

                return;

            }


            const item =
                document.createElement(
                    "button"
                );


            item.type =
                "button";


            item.className =
                "chat-friend-item";


            item.dataset.friendId =
                String(
                    friend.id
                );


            const avatar =
                document.createElement(
                    "div"
                );


            avatar.className =
                "chat-friend-avatar";


            avatar.textContent =
                friend.avatar ||
                "👤";


            const info =
                document.createElement(
                    "div"
                );


            info.className =
                "chat-friend-info";


            const name =
                document.createElement(
                    "strong"
                );


            name.textContent =
                friend.username ||
                friend.name ||
                friend.player_id ||
                "Người dùng";


            const playerId =
                document.createElement(
                    "small"
                );


            playerId.textContent =
                friend.player_id ||
                "";


            const status =
                document.createElement(
                    "div"
                );


            status.className =
                "chat-friend-status";


            const online =
                Boolean(
                    friend.online === true ||
                    friend.is_online === true
                );


            const dot =
                document.createElement(
                    "span"
                );


            dot.className =
                online
                    ? "online-dot"
                    : "offline-dot";


            const statusText =
                document.createElement(
                    "span"
                );


            statusText.textContent =
                online
                    ? "Đang hoạt động"
                    : "Ngoại tuyến";


            status.appendChild(
                dot
            );


            status.appendChild(
                statusText
            );


            info.appendChild(
                name
            );


            if (
                playerId.textContent
            ) {

                info.appendChild(
                    playerId
                );

            }


            info.appendChild(
                status
            );


            const arrow =
                document.createElement(
                    "span"
                );


            arrow.className =
                "chat-friend-arrow";


            arrow.textContent =
                "›";


            item.appendChild(
                avatar
            );


            item.appendChild(
                info
            );


            item.appendChild(
                arrow
            );


            item.addEventListener(
                "click",
                function () {

                    openFriendChat(
                        friend
                    );

                }
            );


            chatTaskbarList.appendChild(
                item
            );

        }
    );


    loadTotalChatUnread(
        friends
    );

}


/* =========================================================
   OPEN INDIVIDUAL CHAT
========================================================= */

function openFriendChat(
    friend
) {

    if (
        !friend ||
        !friend.id
    ) {

        return;

    }


    closeChatTaskbar();


    if (
        typeof window.openChat ===
        "function"
    ) {

        window.openChat(
            friend
        );

        return;

    }


    try {

        localStorage.setItem(
            CHAT_FRIEND_STORAGE_KEY,
            JSON.stringify(
                friend
            )
        );

    } catch {

        // Không làm gián đoạn chuyển trang.

    }


    window.location.href =
        "chat.html";

}


/* =========================================================
   UNREAD TOTAL
========================================================= */

async function loadTotalChatUnread(
    friends
) {

    if (
        chatUnreadLoading
    ) {

        return;

    }


    const token =
        getLoginToken();


    if (
        !token ||
        !Array.isArray(friends) ||
        friends.length === 0
    ) {

        updateChatBadge(0);

        return;

    }


    chatUnreadLoading = true;


    let total = 0;


    try {

        const requests =
            friends.map(
                async function (friend) {

                    if (
                        !friend ||
                        !friend.id
                    ) {

                        return 0;

                    }


                    try {

                        const response =
                            await fetch(
                                `${MAIN_API_URL}/api/chat/${encodeURIComponent(friend.id)}/unread-count`,
                                {
                                    method: "GET",
                                    headers: {
                                        "Authorization":
                                            "Bearer " + token,
                                        "Accept":
                                            "application/json"
                                    }
                                }
                            );


                        if (
                            response.status === 401
                        ) {

                            clearLoginData();

                            return 0;

                        }


                        if (
                            !response.ok
                        ) {

                            return 0;

                        }


                        const data =
                            await response.json();


                        return Math.max(
                            0,
                            Number(
                                data?.count || 0
                            )
                        );

                    } catch {

                        return 0;

                    }

                }
            );


        const counts =
            await Promise.all(
                requests
            );


        counts.forEach(
            function (count) {

                if (
                    Number.isFinite(
                        count
                    )
                ) {

                    total += count;

                }

            }
        );


        updateChatBadge(
            total
        );


    } finally {

        chatUnreadLoading = false;

    }

}


/* =========================================================
   CHAT BADGE
========================================================= */

function updateChatBadge(
    count
) {

    if (!chatTaskbarBadge) {
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

        chatTaskbarBadge.textContent =
            "";

        chatTaskbarBadge.style.display =
            "none";

        return;

    }


    chatTaskbarBadge.textContent =
        safeCount > 99
            ? "99+"
            : String(
                safeCount
            );


    chatTaskbarBadge.style.display =
        "inline-flex";

}


/* =========================================================
   CHAT BACKGROUND REFRESH
========================================================= */

function startChatRefreshTimers() {

    stopChatRefreshTimers();


    if (
        !isAuthenticated()
    ) {

        return;

    }


    chatUnreadRefreshTimer =
        setInterval(
            async function () {

                if (
                    document.hidden ||
                    !isAuthenticated()
                ) {

                    return;

                }


                await refreshChatTaskbar();

            },
            CHAT_UNREAD_REFRESH_INTERVAL
        );


    chatFriendRefreshTimer =
        setInterval(
            async function () {

                if (
                    document.hidden ||
                    !isAuthenticated()
                ) {

                    return;

                }


                await loadChatFriends({
                    showLoading: false
                });

            },
            CHAT_FRIEND_REFRESH_INTERVAL
        );

}


function stopChatRefreshTimers() {

    if (
        chatUnreadRefreshTimer
    ) {

        clearInterval(
            chatUnreadRefreshTimer
        );

        chatUnreadRefreshTimer = null;

    }


    if (
        chatFriendRefreshTimer
    ) {

        clearInterval(
            chatFriendRefreshTimer
        );

        chatFriendRefreshTimer = null;

    }

}


async function refreshChatTaskbar() {

    if (
        !chatTaskbarList ||
        !isAuthenticated()
    ) {

        return;

    }


    try {

        const response =
            await fetch(
                `${MAIN_API_URL}/api/friends`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            "Bearer " +
                            getLoginToken(),
                        "Accept":
                            "application/json"
                    }
                }
            );


        if (
            response.status === 401
        ) {

            clearLoginData();

            updateNavbarAuth();

            return;

        }


        if (
            !response.ok
        ) {

            return;

        }


        const data =
            await response.json();


        const friends =
            Array.isArray(data)
                ? data
                : Array.isArray(
                    data?.friends
                )
                    ? data.friends
                    : [];


        await loadTotalChatUnread(
            friends
        );


    } catch {

        // Không làm gián đoạn trang.

    }

}


/* =========================================================
   NAVBAR AUTH STATE
========================================================= */

function updateNavbarAuth() {

    const token =
        getLoginToken();


    const loginNavLink =
        document.getElementById(
            "loginNavLink"
        );


    const registerNavLink =
        document.getElementById(
            "registerNavLink"
        );


    const accountNavLink =
        document.getElementById(
            "accountNavLink"
        );


    const battleNavLink =
        document.getElementById(
            "battleNavLink"
        );


    const chatNavWrapper =
        document.getElementById(
            "chatNavWrapper"
        );


    if (!token) {

        closeChatTaskbar();


        if (loginNavLink) {

            loginNavLink.style.display =
                "";

        }


        if (registerNavLink) {

            registerNavLink.style.display =
                "";

        }


        if (accountNavLink) {

            accountNavLink.style.display =
                "none";

        }


        if (battleNavLink) {

            battleNavLink.style.display =
                "none";

        }


        /* =================================================
           PANEL CHAT NẰM NGOÀI WRAPPER
           NÊN PHẢI XÓA RIÊNG
        ================================================= */

        const existingChatPanel =
            document.getElementById(
                "chatTaskbarPanel"
            );


        if (existingChatPanel) {

            existingChatPanel.remove();

        }


        if (chatNavWrapper) {

            chatNavWrapper.remove();

        }


        chatTaskbarPanel = null;
        chatTaskbarList = null;
        chatTaskbarBadge = null;


        stopChatRefreshTimers();

        return;

    }


    if (loginNavLink) {

        loginNavLink.style.display =
            "none";

    }


    if (registerNavLink) {

        registerNavLink.style.display =
            "none";

    }


    if (accountNavLink) {

        accountNavLink.style.display =
            "";

    }


    if (battleNavLink) {

        battleNavLink.style.display =
            "";

    }


    createChatTaskbar();

    startChatRefreshTimers();

}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeMainHTML(
    value
) {

    const element =
        document.createElement(
            "div"
        );


    element.textContent =
        String(
            value ?? ""
        );


    return element.innerHTML;

}


/* =========================================================
   STORAGE CHANGE
========================================================= */

window.addEventListener(
    "storage",
    function (event) {

        if (
            event.key === AUTH_TOKEN_KEY ||
            event.key === AUTH_USER_KEY ||
            event.key === AUTH_PROFILE_KEY
        ) {

            updateNavbarAuth();

        }

    }
);


/* =========================================================
   PAGE VISIBILITY
========================================================= */

document.addEventListener(
    "visibilitychange",
    function () {

        if (
            !document.hidden &&
            isAuthenticated()
        ) {

            updateNavbarAuth();


            if (
                chatTaskbarPanel
            ) {

                refreshChatTaskbar();

            }

        }

    }
);


/* =========================================================
   BEFORE UNLOAD
========================================================= */

window.addEventListener(
    "beforeunload",
    function () {

        stopChatRefreshTimers();

        setChatFullscreenState(
            false
        );

    }
);


/* =========================================================
   INITIALIZE
========================================================= */

function initializeMain() {

    installChatFullscreenStyle();

    updateNavbarAuth();

}


/* =========================================================
   START
========================================================= */

if (
    document.readyState === "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeMain,
        {
            once: true
        }
    );

} else {

    initializeMain();

}