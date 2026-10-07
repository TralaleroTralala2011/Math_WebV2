/* =========================================
   MATH_WEB - CHAT
   ========================================= */

const CHAT_API_URL = "http://127.0.0.1:8000";

const CHAT_CONFIG = {
    MESSAGE_LIMIT: 200,
    MAX_MESSAGE_LENGTH: 1000,
    REQUEST_TIMEOUT: 15000,
    MESSAGE_POLL_INTERVAL: 3000,
    PRESENCE_POLL_INTERVAL: 10000,
    HEARTBEAT_INTERVAL: 15000,
    MAX_MESSAGE_ID: 2147483647,
    MAX_USER_ID: 2147483647
};


let currentUser = null;
let friends = [];
let selectedFriend = null;
let currentMessages = [];

let messagePolling = null;
let presencePolling = null;
let heartbeatTimer = null;

let loadingFriends = false;
let loadingMessages = false;
let sendingMessage = false;
let refreshingPresence = false;
let refreshingUnread = false;

let conversationRequestId = 0;


/* =========================================
   DOM
========================================= */

const friendList =
    document.getElementById("friendList");

const friendSearchInput =
    document.getElementById("friendSearchInput");

const friendCountText =
    document.getElementById("friendCountText");

const refreshFriendsButton =
    document.getElementById("refreshFriendsButton");

const emptyConversation =
    document.getElementById("emptyConversation");

const conversationContent =
    document.getElementById("conversationContent");

const conversationAvatar =
    document.getElementById("conversationAvatar");

const conversationName =
    document.getElementById("conversationName");

const conversationStatus =
    document.getElementById("conversationStatus");

const messageList =
    document.getElementById("messageList");

const messageForm =
    document.getElementById("messageForm");

const messageInput =
    document.getElementById("messageInput");

const sendMessageButton =
    document.getElementById("sendMessageButton");

const mobileBackButton =
    document.getElementById("mobileBackButton");


/* =========================================
   AUTH
========================================= */

function getToken() {
    const token =
        localStorage.getItem("mathweb_token");

    if (!token || token.trim() === "") {
        return null;
    }

    return token.trim();
}


function getHeaders(extraHeaders = {}) {
    const token = getToken();

    const headers = {
        "Accept": "application/json",
        ...extraHeaders
    };

    if (token) {
        headers["Authorization"] =
            `Bearer ${token}`;
    }

    return headers;
}


function getJSONHeaders() {
    return getHeaders({
        "Content-Type": "application/json"
    });
}


function getSavedUser() {
    try {
        const savedUser =
            localStorage.getItem("mathweb_user");

        if (!savedUser) {
            return null;
        }

        const parsed =
            JSON.parse(savedUser);

        if (
            !parsed ||
            typeof parsed !== "object" ||
            Array.isArray(parsed)
        ) {
            return null;
        }

        return parsed;

    } catch {
        return null;
    }
}


function clearAuthData() {
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


function handleUnauthorized() {
    clearAuthData();

    stopMessagePolling();
    stopPresencePolling();
    stopHeartbeat();

    if (
        !window.location.pathname.endsWith(
            "/login.html"
        )
    ) {
        window.location.replace(
            "login.html"
        );
    }
}


/* =========================================
   API HELPER
========================================= */

async function apiFetch(
    url,
    options = {},
    timeout = CHAT_CONFIG.REQUEST_TIMEOUT
) {
    const controller =
        new AbortController();

    const timeoutId =
        setTimeout(
            function () {
                controller.abort();
            },
            timeout
        );

    let externalAbortHandler = null;

    try {
        const externalSignal =
            options.signal || null;

        if (externalSignal) {
            if (externalSignal.aborted) {
                controller.abort();
            } else {
                externalAbortHandler =
                    function () {
                        controller.abort();
                    };

                externalSignal.addEventListener(
                    "abort",
                    externalAbortHandler,
                    {
                        once: true
                    }
                );
            }
        }

        const response =
            await fetch(
                url,
                {
                    ...options,
                    headers: {
                        ...getHeaders(),
                        ...(options.headers || {})
                    },
                    signal:
                        controller.signal
                }
            );

        let data = null;

        try {
            data =
                await response.json();
        } catch {
            data = null;
        }

        if (response.status === 401) {
            handleUnauthorized();

            throw new Error(
                "Phiên đăng nhập đã hết hạn."
            );
        }

        if (!response.ok) {
            throw new Error(
                getAPIErrorMessage(
                    data,
                    response.status
                )
            );
        }

        return data;

    } catch (error) {
        if (
            error &&
            error.name === "AbortError"
        ) {
            throw new Error(
                "Yêu cầu mất quá nhiều thời gian."
            );
        }

        if (
            error instanceof TypeError
        ) {
            throw new Error(
                "Không thể kết nối máy chủ."
            );
        }

        throw error;

    } finally {
        clearTimeout(
            timeoutId
        );

        if (
            options.signal &&
            externalAbortHandler
        ) {
            options.signal.removeEventListener(
                "abort",
                externalAbortHandler
            );
        }
    }
}


function getAPIErrorMessage(
    data,
    status = 0
) {
    if (
        typeof data?.detail === "string" &&
        data.detail.trim()
    ) {
        return data.detail.trim();
    }

    if (
        typeof data?.message === "string" &&
        data.message.trim()
    ) {
        return data.message.trim();
    }

    if (Array.isArray(data?.detail)) {
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

        if (messages.length) {
            return messages.join(", ");
        }
    }

    if (status === 404) {
        return "Không tìm thấy dữ liệu.";
    }

    if (status === 403) {
        return "Bạn không có quyền thực hiện thao tác này.";
    }

    if (status >= 500) {
        return "Máy chủ đang gặp sự cố.";
    }

    return "Có lỗi xảy ra.";
}


/* =========================================
   VALIDATION
========================================= */

function isValidUserId(id) {
    const number =
        Number(id);

    return (
        Number.isInteger(number) &&
        number > 0 &&
        number <=
            CHAT_CONFIG.MAX_USER_ID
    );
}


function isValidMessageId(id) {
    const number =
        Number(id);

    return (
        Number.isInteger(number) &&
        number > 0 &&
        number <=
            CHAT_CONFIG.MAX_MESSAGE_ID
    );
}


function normalizeFriendId(friend) {
    if (!friend) {
        return 0;
    }

    const id =
        Number(friend.id);

    return isValidUserId(id)
        ? id
        : 0;
}


/* =========================================
   LOAD CURRENT USER
========================================= */

async function loadCurrentUser() {
    const savedUser =
        getSavedUser();

    if (
        savedUser &&
        isValidUserId(savedUser.id)
    ) {
        currentUser =
            savedUser;

        return currentUser;
    }

    if (!getToken()) {
        return null;
    }

    try {
        const data =
            await apiFetch(
                `${CHAT_API_URL}/api/auth/me`
            );

        currentUser =
            data?.user ||
            data ||
            null;

        if (
            currentUser &&
            isValidUserId(currentUser.id)
        ) {
            localStorage.setItem(
                "mathweb_user",
                JSON.stringify(
                    currentUser
                )
            );

            localStorage.setItem(
                "mathweb_profile",
                JSON.stringify(
                    currentUser
                )
            );
        }

        return currentUser;

    } catch (error) {
        console.error(
            "Không thể tải thông tin tài khoản:",
            error
        );

        return null;
    }
}


/* =========================================
   LOAD FRIENDS
========================================= */

async function loadFriends() {
    if (!getToken()) {
        friends = [];

        updateFriendCount();
        renderFriendList([]);
        showEmptyConversation();

        return;
    }

    if (loadingFriends) {
        return;
    }

    loadingFriends = true;

    try {
        const data =
            await apiFetch(
                `${CHAT_API_URL}/api/friends`
            );

        let loadedFriends = [];

        if (Array.isArray(data)) {
            loadedFriends =
                data;

        } else if (
            Array.isArray(data?.friends)
        ) {
            loadedFriends =
                data.friends;
        }

        friends =
            loadedFriends.filter(
                function (friend) {
                    return (
                        friend &&
                        isValidUserId(
                            friend.id
                        )
                    );
                }
            );

        updateFriendCount();

        renderFriendList(
            getFilteredFriends()
        );

        if (selectedFriend) {
            const stillFriend =
                friends.find(
                    function (friend) {
                        return (
                            Number(friend.id) ===
                            Number(
                                selectedFriend.id
                            )
                        );
                    }
                );

            if (!stillFriend) {
                showEmptyConversation();

            } else {
                selectedFriend =
                    stillFriend;

                showConversation(
                    stillFriend
                );
            }
        }

    } catch (error) {
        console.error(
            "Không thể tải danh sách bạn bè:",
            error
        );

        if (friendList) {
            friendList.innerHTML = `
                <div class="chat-error">
                    ${escapeHTML(
                        error.message ||
                        "Không thể tải danh sách bạn bè."
                    )}

                    <button
                        type="button"
                        id="retryFriendsButton"
                    >
                        Thử lại
                    </button>
                </div>
            `;

            const retryButton =
                document.getElementById(
                    "retryFriendsButton"
                );

            if (retryButton) {
                retryButton.addEventListener(
                    "click",
                    loadFriends
                );
            }
        }

    } finally {
        loadingFriends = false;
    }
}


/* =========================================
   FRIEND COUNT
========================================= */

function updateFriendCount() {
    if (!friendCountText) {
        return;
    }

    const count =
        friends.length;

    friendCountText.textContent =
        count === 0
            ? "Chưa có bạn bè"
            : `${count} người bạn`;
}


/* =========================================
   FRIEND DATA
========================================= */

function getFriendName(friend) {
    return (
        friend?.username ||
        friend?.name ||
        friend?.player_id ||
        `Người dùng #${friend?.id || ""}`
    );
}


function getFriendPlayerId(friend) {
    return (
        friend?.player_id ||
        ""
    );
}


function getFriendAvatar(friend) {
    const avatar =
        friend?.avatar;

    if (
        typeof avatar === "string" &&
        avatar.trim()
    ) {
        return avatar;
    }

    return "👤";
}


/* =========================================
   ONLINE STATUS
========================================= */

function isFriendOnline(friend) {
    return Boolean(
        friend?.online === true ||
        friend?.is_online === true
    );
}


/* =========================================
   RENDER FRIEND LIST
========================================= */

function renderFriendList(list) {
    if (!friendList) {
        return;
    }

    if (
        !Array.isArray(list) ||
        list.length === 0
    ) {
        friendList.innerHTML = `
            <div class="no-friends">
                <div class="no-friends-icon">
                    👥
                </div>

                <div class="no-friends-title">
                    Chưa có bạn bè
                </div>

                <div class="no-friends-text">
                    Hãy kết bạn để bắt đầu trò chuyện.
                </div>
            </div>
        `;

        return;
    }

    const fragment =
        document.createDocumentFragment();

    list.forEach(
        function (friend) {
            const friendItem =
                document.createElement(
                    "button"
                );

            friendItem.type =
                "button";

            friendItem.className =
                "friend-item";

            if (
                selectedFriend &&
                Number(
                    selectedFriend.id
                ) ===
                    Number(friend.id)
            ) {
                friendItem.classList.add(
                    "active"
                );
            }

            const online =
                isFriendOnline(friend);

            const name =
                getFriendName(friend);

            const playerId =
                getFriendPlayerId(friend);

            const unreadCount =
                Number(
                    friend.unread_count ||
                    friend.unread ||
                    friend.message_unread ||
                    0
                );

            const safeUnread =
                Number.isFinite(
                    unreadCount
                )
                    ? Math.max(
                          0,
                          Math.floor(
                              unreadCount
                          )
                      )
                    : 0;

            friendItem.innerHTML = `
                <div class="friend-avatar">
                    ${escapeHTML(
                        getFriendAvatar(
                            friend
                        )
                    )}

                    <span
                        class="friend-online-dot ${
                            online
                                ? "online"
                                : ""
                        }"
                    ></span>
                </div>

                <div class="friend-info">
                    <div class="friend-top">
                        <div class="friend-name">
                            ${escapeHTML(
                                name
                            )}
                        </div>

                        ${
                            safeUnread > 0
                                ? `
                                    <span class="friend-unread">
                                        ${
                                            safeUnread >
                                            99
                                                ? "99+"
                                                : safeUnread
                                        }
                                    </span>
                                  `
                                : ""
                        }
                    </div>

                    ${
                        playerId
                            ? `
                                <div class="friend-player-id">
                                    ID:
                                    ${escapeHTML(
                                        playerId
                                    )}
                                </div>
                              `
                            : ""
                    }

                    <div class="friend-status">
                        <span
                            class="status-dot ${
                                online
                                    ? "online"
                                    : ""
                            }"
                        ></span>

                        ${
                            online
                                ? "Đang online"
                                : "Offline"
                        }
                    </div>
                </div>
            `;

            friendItem.addEventListener(
                "click",
                function () {
                    openConversation(
                        friend
                    );
                }
            );

            fragment.appendChild(
                friendItem
            );
        }
    );

    friendList.innerHTML = "";

    friendList.appendChild(
        fragment
    );
}


/* =========================================
   SEARCH FRIENDS
========================================= */

function getFilteredFriends() {
    const keyword =
        friendSearchInput?.value
            ?.trim()
            .toLowerCase() ||
        "";

    if (!keyword) {
        return friends;
    }

    return friends.filter(
        function (friend) {
            const name =
                getFriendName(
                    friend
                ).toLowerCase();

            const playerId =
                getFriendPlayerId(
                    friend
                ).toLowerCase();

            return (
                name.includes(
                    keyword
                ) ||
                playerId.includes(
                    keyword
                )
            );
        }
    );
}


function filterFriends() {
    renderFriendList(
        getFilteredFriends()
    );
}


/* =========================================
   OPEN CONVERSATION
========================================= */

async function openConversation(
    friend
) {
    const friendId =
        normalizeFriendId(
            friend
        );

    if (!friendId) {
        return;
    }

    conversationRequestId++;

    const requestId =
        conversationRequestId;

    stopMessagePolling();

    selectedFriend =
        friend;

    currentMessages = [];

    renderFriendList(
        getFilteredFriends()
    );

    showConversation(
        friend
    );

    await loadMessages(
        friendId,
        false,
        requestId
    );

    if (
        requestId !==
        conversationRequestId
    ) {
        return;
    }

    await markMessagesRead(
        friendId
    );

    if (
        requestId !==
        conversationRequestId
    ) {
        return;
    }

    startMessagePolling();
    startPresencePolling();
}


/* =========================================
   SHOW CONVERSATION
========================================= */

function showConversation(
    friend
) {
    if (
        !emptyConversation ||
        !conversationContent
    ) {
        return;
    }

    emptyConversation.hidden =
        true;

    conversationContent.hidden =
        false;

    const name =
        getFriendName(
            friend
        );

    const online =
        isFriendOnline(
            friend
        );

    if (conversationAvatar) {
        conversationAvatar.textContent =
            getFriendAvatar(
                friend
            );
    }

    if (conversationName) {
        conversationName.textContent =
            name;
    }

    updateConversationStatus(
        online
    );

    document.body.classList.add(
        "chat-conversation-open"
    );
}


/* =========================================
   EMPTY CONVERSATION
========================================= */

function showEmptyConversation() {
    conversationRequestId++;

    selectedFriend = null;
    currentMessages = [];

    stopMessagePolling();
    stopPresencePolling();

    if (emptyConversation) {
        emptyConversation.hidden =
            false;
    }

    if (conversationContent) {
        conversationContent.hidden =
            true;
    }

    document.body.classList.remove(
        "chat-conversation-open"
    );
}


/* =========================================
   LOAD MESSAGES
========================================= */

async function loadMessages(
    friendId,
    silent = false,
    requestId = conversationRequestId
) {
    if (
        !isValidUserId(
            friendId
        ) ||
        !getToken()
    ) {
        return;
    }

    if (loadingMessages && !silent) {
        return;
    }

    if (!silent) {
        loadingMessages = true;
    }

    try {
        let url =
            `${CHAT_API_URL}/api/chat/${friendId}/messages`;

        const params =
            new URLSearchParams();

        params.set(
            "limit",
            String(
                CHAT_CONFIG.MESSAGE_LIMIT
            )
        );

        const lastMessage =
            currentMessages[
                currentMessages.length - 1
            ];

        if (
            silent &&
            lastMessage &&
            isValidMessageId(
                lastMessage.id
            )
        ) {
            params.set(
                "after_id",
                String(
                    lastMessage.id
                )
            );
        }

        url += `?${params.toString()}`;

        const data =
            await apiFetch(
                url
            );

        if (
            requestId !==
            conversationRequestId
        ) {
            return;
        }

        let messages = [];

        if (Array.isArray(data)) {
            messages = data;

        } else if (
            Array.isArray(
                data?.messages
            )
        ) {
            messages =
                data.messages;
        }

        if (silent) {
            mergeNewMessages(
                messages
            );

        } else {
            currentMessages =
                normalizeMessages(
                    messages
                );

            renderMessages(
                currentMessages,
                true
            );
        }

    } catch (error) {
        console.error(
            "Không thể tải tin nhắn:",
            error
        );

        if (
            !silent &&
            requestId ===
                conversationRequestId
        ) {
            renderMessageError();
        }

    } finally {
        if (!silent) {
            loadingMessages =
                false;
        }
    }
}


/* =========================================
   NORMALIZE MESSAGES
========================================= */

function normalizeMessages(
    messages
) {
    if (!Array.isArray(messages)) {
        return [];
    }

    const unique =
        new Map();

    messages.forEach(
        function (message) {
            if (
                !message ||
                !isValidMessageId(
                    message.id
                )
            ) {
                return;
            }

            unique.set(
                Number(message.id),
                message
            );
        }
    );

    return Array.from(
        unique.values()
    ).sort(
        function (a, b) {
            return (
                Number(a.id) -
                Number(b.id)
            );
        }
    );
}


/* =========================================
   MERGE NEW MESSAGES
========================================= */

function mergeNewMessages(
    messages
) {
    if (
        !Array.isArray(
            messages
        ) ||
        !messages.length
    ) {
        return;
    }

    const existingIds =
        new Set(
            currentMessages.map(
                function (message) {
                    return Number(
                        message.id
                    );
                }
            )
        );

    let changed = false;

    messages.forEach(
        function (message) {
            if (
                !message ||
                !isValidMessageId(
                    message.id
                )
            ) {
                return;
            }

            const id =
                Number(message.id);

            if (
                !existingIds.has(id)
            ) {
                currentMessages.push(
                    message
                );

                existingIds.add(
                    id
                );

                changed = true;
            }
        }
    );

    if (!changed) {
        return;
    }

    currentMessages.sort(
        function (a, b) {
            return (
                Number(a.id) -
                Number(b.id)
            );
        }
    );

    renderMessages(
        currentMessages,
        true
    );
}


/* =========================================
   RENDER MESSAGES
========================================= */

function renderMessages(
    messages,
    scrollToBottom = true
) {
    if (!messageList) {
        return;
    }

    messageList.innerHTML = "";

    if (
        !messages ||
        messages.length === 0
    ) {
        messageList.innerHTML = `
            <div class="empty-message-conversation">
                <div class="empty-message-icon">
                    💬
                </div>

                <div class="empty-message-title">
                    Hãy cùng nhau xây dựng cuộc trò chuyện nào
                </div>

                <div class="empty-message-subtitle">
                    Gửi một tin nhắn để bắt đầu nhé!
                </div>
            </div>
        `;

        return;
    }

    const fragment =
        document.createDocumentFragment();

    messages.forEach(
        function (message) {
            const messageElement =
                document.createElement(
                    "div"
                );

            const isMine =
                currentUser &&
                Number(
                    message.sender_id
                ) ===
                    Number(
                        currentUser.id
                    );

            messageElement.className =
                `message-row ${
                    isMine
                        ? "mine"
                        : "theirs"
                }`;

            const time =
                formatMessageTime(
                    message.created_at
                );

            messageElement.innerHTML = `
                <div class="message-bubble">
                    <div class="message-content">
                        ${formatMessageContent(
                            message.content
                        )}
                    </div>

                    <div class="message-time">
                        ${escapeHTML(
                            time
                        )}
                    </div>
                </div>
            `;

            fragment.appendChild(
                messageElement
            );
        }
    );

    messageList.appendChild(
        fragment
    );

    if (scrollToBottom) {
        scrollMessagesToBottom();
    }
}


/* =========================================
   MESSAGE ERROR
========================================= */

function renderMessageError() {
    if (!messageList) {
        return;
    }

    messageList.innerHTML = `
        <div class="message-error">
            Không thể tải cuộc trò chuyện.

            <button
                type="button"
                id="retryMessagesButton"
            >
                Thử lại
            </button>
        </div>
    `;

    const retryButton =
        document.getElementById(
            "retryMessagesButton"
        );

    if (
        retryButton &&
        selectedFriend
    ) {
        retryButton.addEventListener(
            "click",
            function () {
                loadMessages(
                    selectedFriend.id
                );
            }
        );
    }
}


/* =========================================
   SEND MESSAGE
========================================= */

async function sendMessage(
    event
) {
    event.preventDefault();

    if (
        sendingMessage ||
        !selectedFriend ||
        !messageInput
    ) {
        return;
    }

    const friendId =
        normalizeFriendId(
            selectedFriend
        );

    if (!friendId) {
        return;
    }

    const content =
        messageInput.value.trim();

    if (!content) {
        return;
    }

    if (
        content.length >
        CHAT_CONFIG.MAX_MESSAGE_LENGTH
    ) {
        showTemporaryError(
            `Tin nhắn tối đa ${CHAT_CONFIG.MAX_MESSAGE_LENGTH} ký tự.`
        );

        return;
    }

    if (!getToken()) {
        handleUnauthorized();
        return;
    }

    sendingMessage = true;

    setSendButtonLoading(
        true
    );

    try {
        const data =
            await apiFetch(
                `${CHAT_API_URL}/api/chat/${friendId}/messages`,
                {
                    method: "POST",
                    headers:
                        getJSONHeaders(),
                    body: JSON.stringify({
                        content
                    })
                }
            );

        const newMessage =
            data?.message ||
            data;

        if (
            newMessage &&
            isValidMessageId(
                newMessage.id
            )
        ) {
            mergeNewMessages([
                newMessage
            ]);

        } else {
            await loadMessages(
                friendId
            );
        }

        messageInput.value =
            "";

        autoResizeTextarea();

        messageInput.focus();

    } catch (error) {
        console.error(
            "Không thể gửi tin nhắn:",
            error
        );

        showTemporaryError(
            error.message ||
            "Không thể gửi tin nhắn."
        );

    } finally {
        sendingMessage =
            false;

        setSendButtonLoading(
            false
        );
    }
}


/* =========================================
   SEND BUTTON
========================================= */

function setSendButtonLoading(
    loading
) {
    if (!sendMessageButton) {
        return;
    }

    sendMessageButton.disabled =
        loading;

    if (loading) {
        if (
            !sendMessageButton.dataset
                .oldText
        ) {
            sendMessageButton.dataset
                .oldText =
                sendMessageButton
                    .textContent;
        }

        sendMessageButton.textContent =
            "Đang gửi...";

    } else {
        sendMessageButton.textContent =
            sendMessageButton.dataset
                .oldText ||
            "Gửi";

        delete sendMessageButton
            .dataset.oldText;
    }
}


/* =========================================
   MARK MESSAGES READ
========================================= */

async function markMessagesRead(
    friendId
) {
    if (
        !isValidUserId(
            friendId
        ) ||
        !getToken()
    ) {
        return;
    }

    try {
        await apiFetch(
            `${CHAT_API_URL}/api/chat/${friendId}/read`,
            {
                method: "POST"
            }
        );

        const friend =
            friends.find(
                function (item) {
                    return (
                        Number(
                            item.id
                        ) ===
                        Number(
                            friendId
                        )
                    );
                }
            );

        if (friend) {
            friend.unread_count =
                0;
        }

        renderFriendList(
            getFilteredFriends()
        );

    } catch (error) {
        console.error(
            "Không thể đánh dấu đã đọc:",
            error
        );
    }
}


/* =========================================
   UNREAD COUNT
========================================= */

async function loadUnreadCount(
    friend
) {
    const friendId =
        normalizeFriendId(
            friend
        );

    if (!friendId) {
        return 0;
    }

    try {
        const data =
            await apiFetch(
                `${CHAT_API_URL}/api/chat/${friendId}/unread-count`
            );

        const count =
            Number(
                data?.count || 0
            );

        return Number.isFinite(
            count
        )
            ? Math.max(
                  0,
                  Math.floor(
                      count
                  )
              )
            : 0;

    } catch {
        return 0;
    }
}


/* =========================================
   REFRESH UNREAD COUNTS
========================================= */

async function refreshUnreadCounts() {
    if (
        refreshingUnread ||
        !friends.length ||
        !getToken()
    ) {
        return;
    }

    refreshingUnread = true;

    try {
        const results =
            await Promise.allSettled(
                friends.map(
                    function (friend) {
                        return loadUnreadCount(
                            friend
                        );
                    }
                )
            );

        results.forEach(
            function (
                result,
                index
            ) {
                if (
                    !friends[index]
                ) {
                    return;
                }

                if (
                    result.status ===
                    "fulfilled"
                ) {
                    friends[index]
                        .unread_count =
                        result.value;
                }
            }
        );

        renderFriendList(
            getFilteredFriends()
        );

    } finally {
        refreshingUnread =
            false;
    }
}


/* =========================================
   MESSAGE POLLING
========================================= */

function startMessagePolling() {
    stopMessagePolling();

    if (!selectedFriend) {
        return;
    }

    messagePolling =
        setInterval(
            async function () {
                if (
                    document.hidden ||
                    !selectedFriend ||
                    !getToken()
                ) {
                    return;
                }

                const friendId =
                    normalizeFriendId(
                        selectedFriend
                    );

                if (!friendId) {
                    return;
                }

                await loadMessages(
                    friendId,
                    true
                );

                await markMessagesRead(
                    friendId
                );
            },
            CHAT_CONFIG.MESSAGE_POLL_INTERVAL
        );
}


function stopMessagePolling() {
    if (messagePolling) {
        clearInterval(
            messagePolling
        );

        messagePolling = null;
    }
}


/* =========================================
   PRESENCE
========================================= */

async function updateFriendPresence(
    friend
) {
    const friendId =
        normalizeFriendId(
            friend
        );

    if (
        !friendId ||
        !getToken()
    ) {
        return;
    }

    try {
        const data =
            await apiFetch(
                `${CHAT_API_URL}/api/presence/${friendId}`
            );

        friend.online =
            Boolean(
                data?.online
            );

        if (
            selectedFriend &&
            Number(
                selectedFriend.id
            ) === friendId
        ) {
            selectedFriend =
                friend;

            updateConversationStatus(
                friend.online
            );
        }

    } catch (error) {
        console.debug(
            "Presence không cập nhật được:",
            error.message
        );
    }
}


async function refreshPresence() {
    if (
        refreshingPresence ||
        !friends.length ||
        !getToken()
    ) {
        return;
    }

    refreshingPresence =
        true;

    try {
        await Promise.allSettled(
            friends.map(
                function (friend) {
                    return updateFriendPresence(
                        friend
                    );
                }
            )
        );

        renderFriendList(
            getFilteredFriends()
        );

    } finally {
        refreshingPresence =
            false;
    }
}


/* =========================================
   PRESENCE POLLING
========================================= */

function startPresencePolling() {
    stopPresencePolling();

    presencePolling =
        setInterval(
            function () {
                if (
                    !document.hidden &&
                    getToken()
                ) {
                    refreshPresence();
                }
            },
            CHAT_CONFIG.PRESENCE_POLL_INTERVAL
        );
}


function stopPresencePolling() {
    if (presencePolling) {
        clearInterval(
            presencePolling
        );

        presencePolling = null;
    }
}


/* =========================================
   HEARTBEAT
========================================= */

async function sendHeartbeat() {
    if (!getToken()) {
        return;
    }

    try {
        await apiFetch(
            `${CHAT_API_URL}/api/presence/heartbeat`,
            {
                method: "POST"
            }
        );

    } catch (error) {
        console.debug(
            "Heartbeat không thành công:",
            error.message
        );
    }
}


function startHeartbeat() {
    if (!getToken()) {
        return;
    }

    sendHeartbeat();

    if (heartbeatTimer) {
        clearInterval(
            heartbeatTimer
        );
    }

    heartbeatTimer =
        setInterval(
            sendHeartbeat,
            CHAT_CONFIG.HEARTBEAT_INTERVAL
        );
}


function stopHeartbeat() {
    if (heartbeatTimer) {
        clearInterval(
            heartbeatTimer
        );

        heartbeatTimer = null;
    }
}


/* =========================================
   CONVERSATION STATUS
========================================= */

function updateConversationStatus(
    online
) {
    if (!conversationStatus) {
        return;
    }

    conversationStatus.innerHTML = `
        <span
            class="conversation-status-dot ${
                online
                    ? "online"
                    : ""
            }"
        ></span>

        ${
            online
                ? "Online"
                : "Offline"
        }
    `;

    conversationStatus.classList.toggle(
        "online",
        Boolean(online)
    );
}


/* =========================================
   SCROLL MESSAGE
========================================= */

function scrollMessagesToBottom() {
    if (!messageList) {
        return;
    }

    requestAnimationFrame(
        function () {
            messageList.scrollTop =
                messageList.scrollHeight;
        }
    );
}


/* =========================================
   TEXTAREA
========================================= */

function autoResizeTextarea() {
    if (!messageInput) {
        return;
    }

    messageInput.style.height =
        "auto";

    const maxHeight = 120;

    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            maxHeight
        ) + "px";
}


/* =========================================
   MOBILE BACK
========================================= */

function goBackToFriendList() {
    showEmptyConversation();

    renderFriendList(
        getFilteredFriends()
    );
}


/* =========================================
   TEMPORARY ERROR
========================================= */

function showTemporaryError(
    message
) {
    const oldError =
        document.querySelector(
            ".chat-temporary-error"
        );

    if (oldError) {
        oldError.remove();
    }

    const errorElement =
        document.createElement(
            "div"
        );

    errorElement.className =
        "chat-temporary-error";

    errorElement.textContent =
        String(
            message ||
            "Có lỗi xảy ra."
        );

    document.body.appendChild(
        errorElement
    );

    setTimeout(
        function () {
            errorElement.classList.add(
                "show"
            );
        },
        10
    );

    setTimeout(
        function () {
            errorElement.classList.remove(
                "show"
            );

            setTimeout(
                function () {
                    if (
                        errorElement
                            .parentNode
                    ) {
                        errorElement.remove();
                    }
                },
                300
            );
        },
        2500
    );
}


/* =========================================
   FORMAT MESSAGE
========================================= */

function formatMessageContent(
    content
) {
    if (
        content === null ||
        content === undefined
    ) {
        return "";
    }

    return escapeHTML(
        String(content)
    ).replace(
        /\n/g,
        "<br>"
    );
}


function formatMessageTime(
    dateString
) {
    if (!dateString) {
        return "";
    }

    const date =
        new Date(
            dateString
        );

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "";
    }

    return date.toLocaleTimeString(
        "vi-VN",
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}


/* =========================================
   ESCAPE HTML
========================================= */

function escapeHTML(
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


/* =========================================
   REFRESH BUTTON
========================================= */

async function refreshChatData() {
    if (
        !refreshFriendsButton
    ) {
        return;
    }

    refreshFriendsButton.classList.add(
        "loading"
    );

    refreshFriendsButton.disabled =
        true;

    try {
        await loadFriends();
        await refreshPresence();
        await refreshUnreadCounts();

        if (
            selectedFriend
        ) {
            await loadMessages(
                selectedFriend.id,
                true
            );

            await markMessagesRead(
                selectedFriend.id
            );
        }

        await sendHeartbeat();

    } finally {
        refreshFriendsButton.classList.remove(
            "loading"
        );

        refreshFriendsButton.disabled =
            false;
    }
}


/* =========================================
   EVENT LISTENERS
========================================= */

if (friendSearchInput) {
    friendSearchInput.addEventListener(
        "input",
        filterFriends
    );
}


if (refreshFriendsButton) {
    refreshFriendsButton.addEventListener(
        "click",
        refreshChatData
    );
}


if (messageForm) {
    messageForm.addEventListener(
        "submit",
        sendMessage
    );
}


if (messageInput) {
    messageInput.addEventListener(
        "input",
        autoResizeTextarea
    );

    messageInput.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key ===
                    "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();

                if (
                    !sendMessageButton
                        ?.disabled
                ) {
                    if (
                        messageForm &&
                        typeof messageForm
                            .requestSubmit ===
                            "function"
                    ) {
                        messageForm.requestSubmit();

                    } else {
                        sendMessage(
                            event
                        );
                    }
                }
            }
        }
    );
}


if (mobileBackButton) {
    mobileBackButton.addEventListener(
        "click",
        goBackToFriendList
    );
}


/* =========================================
   VISIBILITY
========================================= */

document.addEventListener(
    "visibilitychange",
    async function () {
        if (
            document.hidden
        ) {
            stopMessagePolling();
            stopPresencePolling();

            return;
        }

        if (!getToken()) {
            return;
        }

        await loadFriends();
        await refreshPresence();
        await refreshUnreadCounts();

        if (
            selectedFriend
        ) {
            await loadMessages(
                selectedFriend.id,
                true
            );

            await markMessagesRead(
                selectedFriend.id
            );

            startMessagePolling();
            startPresencePolling();
        }

        await sendHeartbeat();
    }
);


/* =========================================
   WINDOW FOCUS
========================================= */

window.addEventListener(
    "focus",
    async function () {
        if (
            document.hidden ||
            !getToken()
        ) {
            return;
        }

        await sendHeartbeat();

        if (selectedFriend) {
            await loadMessages(
                selectedFriend.id,
                true
            );

            await markMessagesRead(
                selectedFriend.id
            );
        }
    }
);


/* =========================================
   BEFORE UNLOAD
========================================= */

window.addEventListener(
    "beforeunload",
    function () {
        stopMessagePolling();
        stopPresencePolling();
        stopHeartbeat();
    }
);


/* =========================================
   INITIALIZE CHAT
========================================= */

async function initChat() {
    showEmptyConversation();

    if (!getToken()) {
        friends = [];

        updateFriendCount();
        renderFriendList([]);

        return;
    }

    const user =
        await loadCurrentUser();

    if (
        !user ||
        !isValidUserId(
            user.id
        )
    ) {
        return;
    }

    await loadFriends();

    await refreshPresence();
    await refreshUnreadCounts();

    startHeartbeat();
    startPresencePolling();
}


/* =========================================
   GLOBAL API
========================================= */

window.MATHWEB_CHAT = {
    openConversation,
    loadFriends,
    refreshChatData,
    sendMessage,
    markMessagesRead,
    stopMessagePolling,
    stopPresencePolling
};


/* =========================================
   START
========================================= */

if (
    document.readyState ===
    "loading"
) {
    document.addEventListener(
        "DOMContentLoaded",
        initChat,
        {
            once: true
        }
    );
} else {
    initChat();
}