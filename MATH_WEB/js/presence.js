/* =========================================================
   MATH WEB
   PRESENCE SYSTEM
   ========================================================= */

(function () {

    "use strict";


    /* =====================================================
       CONFIG
    ===================================================== */

    const PRESENCE_API_URL =
        window.MATHWEB_API_URL ||
        "http://127.0.0.1:8000";

    const TOKEN_KEY =
        "mathweb_token";

    const HEARTBEAT_INTERVAL =
        10000;

    const REQUEST_TIMEOUT =
        8000;


    /* =====================================================
       STATE
    ===================================================== */

    let heartbeatTimer = null;

    let heartbeatInProgress =
        false;

    let presenceStarted =
        false;

    let pageUnloading =
        false;


    /* =====================================================
       TOKEN
    ===================================================== */

    function getPresenceToken() {

        const token =
            localStorage.getItem(
                TOKEN_KEY
            );

        if (
            typeof token !== "string"
        ) {
            return null;
        }

        const trimmed =
            token.trim();

        if (!trimmed) {
            return null;
        }

        /*
         * Backend hiện tại dùng token
         * dạng:
         *
         * payload.signature
         */

        const parts =
            trimmed.split(".");

        if (
            parts.length !== 2 ||
            !parts[0] ||
            !parts[1]
        ) {
            return null;
        }

        if (
            trimmed.length > 4096
        ) {
            return null;
        }

        return trimmed;

    }


    /* =====================================================
       AUTH CLEAR
    ===================================================== */

    function clearPresenceAuth() {

        localStorage.removeItem(
            TOKEN_KEY
        );

        localStorage.removeItem(
            "mathweb_user"
        );

        localStorage.removeItem(
            "mathweb_profile"
        );

    }


    /* =====================================================
       REQUEST WITH TIMEOUT
    ===================================================== */

    async function presenceRequest(
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
                REQUEST_TIMEOUT
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
                response.status === 401
            ) {

                clearPresenceAuth();

            }


            return response;

        } finally {

            clearTimeout(
                timeout
            );

        }

    }


    /* =====================================================
       SEND HEARTBEAT
    ===================================================== */

    async function sendHeartbeat() {

        if (
            pageUnloading
        ) {
            return false;
        }


        const token =
            getPresenceToken();


        if (!token) {

            stopPresence();

            return false;

        }


        /*
         * Không gửi heartbeat chồng nhau.
         */

        if (
            heartbeatInProgress
        ) {
            return false;
        }


        heartbeatInProgress =
            true;


        try {

            const response =
                await presenceRequest(
                    `${PRESENCE_API_URL}/api/presence/heartbeat`,
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


            if (
                response.status === 401
            ) {

                stopPresence();

                return false;

            }


            if (
                !response.ok
            ) {

                return false;

            }


            return true;

        } catch (error) {

            /*
             * Abort hoặc network error không
             * được phép làm gián đoạn website.
             */

            if (
                error &&
                error.name !== "AbortError"
            ) {

                console.warn(
                    "MATH WEB Presence:",
                    error
                );

            }

            return false;

        } finally {

            heartbeatInProgress =
                false;

        }

    }


    /* =====================================================
       GET USER PRESENCE
    ===================================================== */

    async function getUserPresence(
        userId
    ) {

        const token =
            getPresenceToken();


        if (!token) {

            return {
                online: false
            };

        }


        /*
         * Chỉ chấp nhận ID dạng số nguyên
         * để tránh tạo URL không hợp lệ.
         */

        const numericUserId =
            Number(userId);


        if (
            !Number.isInteger(
                numericUserId
            ) ||
            numericUserId <= 0
        ) {

            return {
                online: false
            };

        }


        try {

            const response =
                await presenceRequest(
                    `${PRESENCE_API_URL}/api/presence/${numericUserId}`,
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


            if (
                response.status === 401
            ) {

                return {
                    online: false
                };

            }


            if (
                !response.ok
            ) {

                return {
                    online: false
                };

            }


            let data = null;


            try {

                data =
                    await response.json();

            } catch {

                return {
                    online: false
                };

            }


            if (
                !data ||
                typeof data !== "object"
            ) {

                return {
                    online: false
                };

            }


            return {
                ...data,

                online:
                    data.online === true
            };

        } catch {

            return {
                online: false
            };

        }

    }


    /* =====================================================
       START HEARTBEAT TIMER
    ===================================================== */

    function startHeartbeatTimer() {

        if (
            heartbeatTimer !== null
        ) {

            return;

        }


        heartbeatTimer =
            window.setInterval(
                function () {

                    sendHeartbeat();

                },
                HEARTBEAT_INTERVAL
            );

    }


    /* =====================================================
       STOP PRESENCE
    ===================================================== */

    function stopPresence() {

        if (
            heartbeatTimer !== null
        ) {

            clearInterval(
                heartbeatTimer
            );

            heartbeatTimer =
                null;

        }


        presenceStarted =
            false;

    }


    /* =====================================================
       START PRESENCE
    ===================================================== */

    function startPresence() {

        if (
            pageUnloading
        ) {
            return false;
        }


        const token =
            getPresenceToken();


        if (!token) {

            stopPresence();

            return false;

        }


        if (
            presenceStarted
        ) {

            return true;

        }


        presenceStarted =
            true;


        /*
         * Gửi ngay khi bắt đầu.
         */

        sendHeartbeat();


        /*
         * Sau đó heartbeat định kỳ.
         */

        startHeartbeatTimer();


        return true;

    }


    /* =====================================================
       VISIBILITY CHANGE
    ===================================================== */

    function handleVisibilityChange() {

        if (
            pageUnloading
        ) {
            return;

        }


        if (
            document.visibilityState ===
            "visible"
        ) {

            const token =
                getPresenceToken();


            if (token) {

                sendHeartbeat();

                startPresence();

            } else {

                stopPresence();

            }

        }

    }


    /* =====================================================
       STORAGE CHANGE
    ===================================================== */

    function handleStorageChange(
        event
    ) {

        if (
            event.key !==
            TOKEN_KEY
        ) {
            return;
        }


        const token =
            getPresenceToken();


        if (!token) {

            stopPresence();

            return;

        }


        startPresence();

    }


    /* =====================================================
       PAGE UNLOAD
    ===================================================== */

    function handlePageUnload() {

        pageUnloading =
            true;

        stopPresence();

    }


    /* =====================================================
       PUBLIC API
    ===================================================== */

    window.MATHWEB_PRESENCE = {

        getToken:
            getPresenceToken,

        sendHeartbeat:
            sendHeartbeat,

        getUserPresence:
            getUserPresence,

        start:
            startPresence,

        stop:
            stopPresence,

        isRunning:
            function () {
                return presenceStarted;
            }

    };


    /*
     * Giữ tương thích với các file cũ
     * đang gọi trực tiếp các hàm này.
     */

    window.getPresenceToken =
        getPresenceToken;

    window.sendHeartbeat =
        sendHeartbeat;

    window.getUserPresence =
        getUserPresence;

    window.startPresence =
        startPresence;


    /* =====================================================
       EVENTS
    ===================================================== */

    document.addEventListener(
        "visibilitychange",
        handleVisibilityChange
    );


    window.addEventListener(
        "storage",
        handleStorageChange
    );


    window.addEventListener(
        "pagehide",
        handlePageUnload,
        {
            once: true
        }
    );


    window.addEventListener(
        "beforeunload",
        handlePageUnload,
        {
            once: true
        }
    );


    /* =====================================================
       INITIALIZE
    ===================================================== */

    function initializePresence() {

        startPresence();

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initializePresence,
            {
                once: true
            }
        );

    } else {

        initializePresence();

    }


})();