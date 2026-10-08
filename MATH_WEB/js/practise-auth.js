(function () {

    const token =
        localStorage.getItem("mathweb_token");

    if (!token || token.trim() === "") {

        window.location.replace("login.html");

        return;
    }

})();/* =========================================================
   MATH WEB - PRACTICE AUTH
   Protect practice.html with backend authentication
========================================================= */

(function () {

    "use strict";


    /* =====================================================
       CONFIG
    ===================================================== */

    const API_URL =
        window.MATHWEB_API_URL ||
        "http://127.0.0.1:8000";


    const TOKEN_KEY =
        "mathweb_token";


    const USER_KEY =
        "mathweb_user";


    const PROFILE_KEY =
        "mathweb_profile";


    const LOGIN_PAGE =
        "login.html";


    const PRACTICE_PAGE =
        "practice.html";


    const REQUEST_TIMEOUT =
        10000;


    let redirecting =
        false;


    let checkingAuth =
        false;


    /* =====================================================
       CURRENT PAGE
    ===================================================== */

    function getCurrentPage() {

        const path =
            window.location.pathname
                .split("/")
                .pop()
                .toLowerCase();


        return path || "index.html";

    }


    /* =====================================================
       TOKEN
    ===================================================== */

    function getToken() {

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


        if (
            !trimmed
        ) {

            return null;

        }


        /*
           Backend hiện tại tạo token dạng:
           payload.signature
        */

        const parts =
            trimmed.split(".");


        if (
            parts.length !== 2
        ) {

            return null;

        }


        if (
            parts[0].length === 0 ||
            parts[1].length === 0
        ) {

            return null;

        }


        /*
           Giới hạn tương ứng với backend.
        */

        if (
            trimmed.length > 4096
        ) {

            return null;

        }


        return trimmed;

    }


    /* =====================================================
       CLEAR AUTH
    ===================================================== */

    function clearAuthData() {

        localStorage.removeItem(
            TOKEN_KEY
        );

        localStorage.removeItem(
            USER_KEY
        );

        localStorage.removeItem(
            PROFILE_KEY
        );

    }


    /* =====================================================
       REDIRECT LOGIN
    ===================================================== */

    function redirectToLogin() {

        if (
            redirecting
        ) {

            return;

        }


        redirecting =
            true;


        /*
           Dừng các thao tác tiếp theo
           trước khi chuyển trang.
        */

        window.location.replace(
            LOGIN_PAGE
        );

    }


    /* =====================================================
       BASIC TOKEN CHECK
    ===================================================== */

    function hasUsableToken() {

        const token =
            getToken();


        if (
            !token
        ) {

            return false;

        }


        return true;

    }


    /* =====================================================
       FETCH WITH TIMEOUT
    ===================================================== */

    async function verifyTokenWithServer(
        token
    ) {

        if (
            checkingAuth
        ) {

            return false;

        }


        checkingAuth =
            true;


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
                            controller.signal
                    }
                );


            /*
               Token hết hạn / không hợp lệ.
            */

            if (
                response.status === 401
            ) {

                clearAuthData();

                return false;

            }


            /*
               Các lỗi server khác không đồng nghĩa
               token sai.
            */

            if (
                !response.ok
            ) {

                console.warn(
                    "Không thể xác thực tài khoản với máy chủ:",
                    response.status
                );


                /*
                   Giữ token lại khi backend tạm thời
                   lỗi 5xx hoặc không phản hồi đúng.
                   Không bắt người dùng đăng nhập lại
                   chỉ vì server đang gặp sự cố.
                */

                return true;

            }


            let data = null;


            try {

                data =
                    await response.json();

            } catch {

                data = null;

            }


            /*
               Backend /api/auth/me hiện trả:
               {
                   user: {...}
               }

               Nhưng vẫn hỗ trợ trường hợp backend
               trả trực tiếp object user.
            */

            const user =
                data?.user ||
                data;


            if (
                !user ||
                typeof user !== "object"
            ) {

                console.warn(
                    "Phản hồi xác thực không hợp lệ."
                );

                return true;

            }


            /*
               Đồng bộ user mới nhất.
            */

            try {

                if (
                    user.id !== undefined &&
                    user.id !== null
                ) {

                    localStorage.setItem(
                        USER_KEY,
                        JSON.stringify(user)
                    );

                }


                /*
                   Profile có thể được dùng bởi
                   account.js / các file frontend khác.
                */

                localStorage.setItem(
                    PROFILE_KEY,
                    JSON.stringify(user)
                );

            } catch (storageError) {

                console.warn(
                    "Không thể lưu thông tin tài khoản:",
                    storageError
                );

            }


            return true;

        } catch (error) {

            /*
               Timeout hoặc mất kết nối:
               không xóa token.
            */

            if (
                error &&
                error.name === "AbortError"
            ) {

                console.warn(
                    "Xác thực tài khoản quá thời gian."
                );

                return true;

            }


            console.warn(
                "Không thể kết nối API xác thực:",
                error
            );


            /*
               Server không truy cập được không có nghĩa
               token chắc chắn hết hạn.
            */

            return true;

        } finally {

            clearTimeout(
                timeout
            );

            checkingAuth =
                false;

        }

    }


    /* =====================================================
       AUTHENTICATE PRACTICE PAGE
    ===================================================== */

    async function authenticatePracticePage() {

        /*
           Chỉ bảo vệ practice.html.
        */

        const currentPage =
            getCurrentPage();


        if (
            currentPage !==
            PRACTICE_PAGE
        ) {

            return;

        }


        /*
           Kiểm tra token cục bộ trước.
        */

        if (
            !hasUsableToken()
        ) {

            clearAuthData();

            redirectToLogin();

            return;

        }


        const token =
            getToken();


        /*
           Kiểm tra token thật với backend.
        */

        const valid =
            await verifyTokenWithServer(
                token
            );


        if (
            !valid
        ) {

            redirectToLogin();

            return;

        }


        /*
           Token hợp lệ.
           Cho phép trang Practice tiếp tục tải.
        */

        document.documentElement
            .setAttribute(
                "data-practice-auth",
                "authenticated"
            );

    }


    /* =====================================================
       PUBLIC API
    ===================================================== */

    window.MATHWEB_PRACTICE_AUTH = {
        getToken,
        hasUsableToken,
        authenticate:
            authenticatePracticePage
    };


    /* =====================================================
       START
    ===================================================== */

    authenticatePracticePage();

})();