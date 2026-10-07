const API_URL = "http://127.0.0.1:8000";


/* =========================================================
   CONFIG
========================================================= */

const AUTH_REQUEST_TIMEOUT = 15000;

const MIN_USERNAME_LENGTH = 3;
const MAX_USERNAME_LENGTH = 20;

const MIN_PASSWORD_LENGTH = 6;
const MAX_PASSWORD_LENGTH = 128;


/* =========================================================
   STATE
========================================================= */

let loginSubmitting = false;

let registerSubmitting = false;

let restoreSessionRunning = false;


/* =========================================================
   TOKEN STORAGE KEYS
========================================================= */

const TOKEN_KEY = "mathweb_token";

const USER_KEY = "mathweb_user";

const PROFILE_KEY = "mathweb_profile";


/* =========================================================
   SHOW MESSAGE
========================================================= */

function showMessage(
    element,
    message,
    type
) {

    if (!element) {
        return;
    }


    element.textContent =
        message || "";


    element.className =
        "auth-message " +
        (type || "");
}


/* =========================================================
   CLEAR MESSAGE
========================================================= */

function clearMessage(
    element
) {

    if (!element) {
        return;
    }


    element.textContent =
        "";


    element.className =
        "auth-message";
}


/* =========================================================
   SAVE LOGIN DATA
========================================================= */

function saveLoginData(
    data
) {

    if (
        !data ||
        typeof data !== "object"
    ) {

        throw new Error(
            "Dữ liệu đăng nhập không hợp lệ."
        );
    }


    const token =
        typeof data.token === "string"
            ? data.token.trim()
            : "";


    if (!token) {

        throw new Error(
            "Máy chủ không trả về token đăng nhập."
        );
    }


    if (
        token.length >
        4096
    ) {

        throw new Error(
            "Token đăng nhập không hợp lệ."
        );
    }


    localStorage.setItem(
        TOKEN_KEY,
        token
    );


    if (
        data.user &&
        typeof data.user === "object"
    ) {

        const userJSON =
            JSON.stringify(
                data.user
            );


        localStorage.setItem(
            USER_KEY,
            userJSON
        );


        localStorage.setItem(
            PROFILE_KEY,
            userJSON
        );

    } else {

        localStorage.removeItem(
            USER_KEY
        );

        localStorage.removeItem(
            PROFILE_KEY
        );
    }


    return token;
}


/* =========================================================
   GET TOKEN
========================================================= */

function getToken() {

    const token =
        localStorage.getItem(
            TOKEN_KEY
        );


    if (
        typeof token !==
        "string"
    ) {

        return null;
    }


    const trimmed =
        token.trim();


    if (!trimmed) {

        return null;
    }


    return trimmed;
}


/* =========================================================
   GET SAVED USER
========================================================= */

function getUser() {

    const saved =
        localStorage.getItem(
            USER_KEY
        );


    if (!saved) {

        return null;
    }


    try {

        const user =
            JSON.parse(
                saved
            );


        if (
            !user ||
            typeof user !== "object" ||
            Array.isArray(user)
        ) {

            return null;
        }


        return user;

    } catch (error) {

        console.warn(
            "Dữ liệu user trong localStorage không hợp lệ."
        );


        localStorage.removeItem(
            USER_KEY
        );


        return null;
    }
}


/* =========================================================
   GET SAVED PROFILE
========================================================= */

function getSavedProfile() {

    const saved =
        localStorage.getItem(
            PROFILE_KEY
        );


    if (!saved) {

        return null;
    }


    try {

        const profile =
            JSON.parse(
                saved
            );


        if (
            !profile ||
            typeof profile !== "object" ||
            Array.isArray(profile)
        ) {

            return null;
        }


        return profile;

    } catch (error) {

        localStorage.removeItem(
            PROFILE_KEY
        );


        return null;
    }
}


/* =========================================================
   CLEAR AUTH DATA
========================================================= */

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


/* =========================================================
   LOGOUT
========================================================= */

function logout() {

    clearAuthData();


    window.location.replace(
        "login.html"
    );
}


/* =========================================================
   NORMALIZE USERNAME
========================================================= */

function normalizeUsername(
    username
) {

    if (
        typeof username !==
        "string"
    ) {

        return "";
    }


    return username.trim();
}


/* =========================================================
   VALIDATE USERNAME
========================================================= */

function validateUsername(
    username
) {

    const value =
        normalizeUsername(
            username
        );


    if (!value) {

        return "Vui lòng nhập tên tài khoản.";
    }


    if (
        value.length <
        MIN_USERNAME_LENGTH
    ) {

        return `Tên tài khoản phải có ít nhất ${MIN_USERNAME_LENGTH} ký tự.`;
    }


    if (
        value.length >
        MAX_USERNAME_LENGTH
    ) {

        return `Tên tài khoản không được vượt quá ${MAX_USERNAME_LENGTH} ký tự.`;
    }


    return null;
}


/* =========================================================
   VALIDATE PASSWORD
========================================================= */

function validatePassword(
    password
) {

    if (
        typeof password !==
        "string"
    ) {

        return "Vui lòng nhập mật khẩu.";
    }


    if (!password) {

        return "Vui lòng nhập mật khẩu.";
    }


    if (
        password.length <
        MIN_PASSWORD_LENGTH
    ) {

        return `Mật khẩu phải có ít nhất ${MIN_PASSWORD_LENGTH} ký tự.`;
    }


    if (
        password.length >
        MAX_PASSWORD_LENGTH
    ) {

        return `Mật khẩu không được vượt quá ${MAX_PASSWORD_LENGTH} ký tự.`;
    }


    return null;
}


/* =========================================================
   READ RESPONSE JSON
========================================================= */

async function readResponseJSON(
    response
) {

    const text =
        await response.text();


    if (!text) {

        return {};
    }


    try {

        return JSON.parse(
            text
        );

    } catch (error) {

        return {
            detail:
                text.trim()
        };
    }
}


/* =========================================================
   GET API ERROR MESSAGE
========================================================= */

function getAPIErrorMessage(
    data,
    fallback
) {

    if (
        data &&
        typeof data.detail ===
        "string" &&
        data.detail.trim()
    ) {

        return data.detail.trim();
    }


    if (
        data &&
        typeof data.message ===
        "string" &&
        data.message.trim()
    ) {

        return data.message.trim();
    }


    if (
        data &&
        Array.isArray(
            data.detail
        )
    ) {

        const messages =
            data.detail
                .map(
                    item => {

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
                .filter(
                    message =>
                        message
                );


        if (
            messages.length > 0
        ) {

            return messages.join(
                " "
            );
        }
    }


    if (
        data &&
        typeof data.error ===
        "string" &&
        data.error.trim()
    ) {

        return data.error.trim();
    }


    return (
        fallback ||
        "Đã xảy ra lỗi."
    );
}


/* =========================================================
   REQUEST WITH TIMEOUT
========================================================= */

async function fetchWithTimeout(
    url,
    options = {},
    timeout =
        AUTH_REQUEST_TIMEOUT
) {

    const controller =
        new AbortController();


    const externalSignal =
        options.signal;


    let externalAbortHandler =
        null;


    if (externalSignal) {

        if (
            externalSignal.aborted
        ) {

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
                    once:
                        true
                }
            );
        }
    }


    const timeoutId =
        window.setTimeout(
            function () {

                controller.abort();

            },
            timeout
        );


    try {

        return await fetch(
            url,
            {
                ...options,
                signal:
                    controller.signal
            }
        );

    } catch (error) {

        if (
            error &&
            error.name ===
            "AbortError"
        ) {

            if (
                externalSignal &&
                externalSignal.aborted
            ) {

                throw error;
            }


            throw new Error(
                "Kết nối máy chủ quá lâu. Vui lòng thử lại."
            );
        }


        if (
            error instanceof
            TypeError
        ) {

            throw new Error(
                "Không thể kết nối đến MATH WEB API. Hãy kiểm tra server."
            );
        }


        throw error;

    } finally {

        window.clearTimeout(
            timeoutId
        );


        if (
            externalSignal &&
            externalAbortHandler
        ) {

            externalSignal.removeEventListener(
                "abort",
                externalAbortHandler
            );
        }
    }
}


/* =========================================================
   HANDLE AUTH ERROR
========================================================= */

function handleAuthFailure() {

    clearAuthData();
}


/* =========================================================
   REGISTER USER
========================================================= */

async function registerUser(
    username,
    password
) {

    const normalizedUsername =
        normalizeUsername(
            username
        );


    const usernameError =
        validateUsername(
            normalizedUsername
        );


    if (usernameError) {

        throw new Error(
            usernameError
        );
    }


    const passwordError =
        validatePassword(
            password
        );


    if (passwordError) {

        throw new Error(
            passwordError
        );
    }


    let response;


    try {

        response =
            await fetchWithTimeout(
                API_URL +
                "/api/auth/register",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            username:
                                normalizedUsername,

                            password:
                                password
                        })
                }
            );

    } catch (error) {

        throw error;
    }


    const data =
        await readResponseJSON(
            response
        );


    if (!response.ok) {

        throw new Error(
            getAPIErrorMessage(
                data,
                "Đăng ký thất bại."
            )
        );
    }


    saveLoginData(
        data
    );


    return data;
}


/* =========================================================
   LOGIN USER
========================================================= */

async function loginUser(
    username,
    password
) {

    const normalizedUsername =
        normalizeUsername(
            username
        );


    const usernameError =
        validateUsername(
            normalizedUsername
        );


    if (usernameError) {

        throw new Error(
            usernameError
        );
    }


    const passwordError =
        validatePassword(
            password
        );


    if (passwordError) {

        throw new Error(
            passwordError
        );
    }


    let response;


    try {

        response =
            await fetchWithTimeout(
                API_URL +
                "/api/auth/login",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            username:
                                normalizedUsername,

                            password:
                                password
                        })
                }
            );

    } catch (error) {

        throw error;
    }


    const data =
        await readResponseJSON(
            response
        );


    if (!response.ok) {

        throw new Error(
            getAPIErrorMessage(
                data,
                "Đăng nhập thất bại."
            )
        );
    }


    saveLoginData(
        data
    );


    return data;
}


/* =========================================================
   GET CURRENT USER
========================================================= */

async function getCurrentUser() {

    const token =
        getToken();


    if (!token) {

        return null;
    }


    let response;


    try {

        response =
            await fetchWithTimeout(
                API_URL +
                "/api/auth/me",
                {
                    method:
                        "GET",

                    headers: {
                        "Authorization":
                            "Bearer " +
                            token,

                        "Accept":
                            "application/json"
                    }
                }
            );

    } catch (error) {

        console.error(
            "Kiểm tra session:",
            error
        );


        return null;
    }


    if (
        response.status ===
        401
    ) {

        handleAuthFailure();

        return null;
    }


    const data =
        await readResponseJSON(
            response
        );


    if (!response.ok) {

        console.error(
            "GET /api/auth/me:",
            response.status,
            data
        );


        return null;
    }


    const user =
        data.user ||
        null;


    if (
        !user ||
        typeof user !==
        "object"
    ) {

        console.error(
            "API /api/auth/me không trả về user hợp lệ."
        );


        return null;
    }


    const userJSON =
        JSON.stringify(
            user
        );


    localStorage.setItem(
        USER_KEY,
        userJSON
    );


    localStorage.setItem(
        PROFILE_KEY,
        userJSON
    );


    return user;
}


/* =========================================================
   GET CURRENT PAGE
========================================================= */

function getCurrentPage() {

    const pathname =
        window.location.pathname
            .split("/")
            .pop()
            .toLowerCase();


    return pathname || "index.html";
}


/* =========================================================
   IS AUTH PAGE
========================================================= */

function isAuthPage() {

    const currentPage =
        getCurrentPage();


    return (
        currentPage ===
            "login.html" ||
        currentPage ===
            "register.html"
    );
}


/* =========================================================
   REDIRECT TO ACCOUNT
========================================================= */

function redirectToAccount() {

    window.location.replace(
        "account.html"
    );
}


/* =========================================================
   RESTORE LOGIN SESSION
========================================================= */

async function restoreLoginSession() {

    if (
        restoreSessionRunning
    ) {

        return;
    }


    restoreSessionRunning =
        true;


    try {

        const token =
            getToken();


        /*
         * Chưa từng đăng nhập.
         */

        if (!token) {

            return;
        }


        /*
         * Kiểm tra token với server.
         */

        const user =
            await getCurrentUser();


        /*
         * Token hợp lệ.
         */

        if (user) {

            /*
             * Chỉ chuyển hướng nếu
             * người dùng đang ở login/register.
             */

            if (
                isAuthPage()
            ) {

                redirectToAccount();
            }


            return;
        }


        /*
         * Nếu server xác nhận token
         * không hợp lệ thì getCurrentUser()
         * đã xóa auth data.
         */

    } finally {

        restoreSessionRunning =
            false;
    }
}


/* =========================================================
   SET BUTTON LOADING
========================================================= */

function setButtonLoading(
    button,
    loading,
    loadingText,
    normalText
) {

    if (!button) {

        return;
    }


    if (loading) {

        button.disabled =
            true;


        button.dataset.originalText =
            button.textContent;


        button.textContent =
            loadingText;

    } else {

        button.disabled =
            false;


        button.textContent =
            normalText ||
            button.dataset.originalText ||
            button.textContent;


        delete button.dataset.originalText;
    }
}


/* =========================================================
   LOGIN FORM
========================================================= */

function setupLoginForm() {

    const loginForm =
        document.getElementById(
            "loginForm"
        );


    if (!loginForm) {

        return;
    }


    const usernameInput =
        document.getElementById(
            "loginUsername"
        );


    const passwordInput =
        document.getElementById(
            "loginPassword"
        );


    const message =
        document.getElementById(
            "authMessage"
        );


    const button =
        loginForm.querySelector(
            "button[type='submit']"
        );


    loginForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            if (
                loginSubmitting
            ) {

                return;
            }


            const username =
                usernameInput
                    ? usernameInput.value
                    : "";


            const password =
                passwordInput
                    ? passwordInput.value
                    : "";


            const usernameError =
                validateUsername(
                    username
                );


            if (usernameError) {

                showMessage(
                    message,
                    usernameError,
                    "error"
                );


                if (usernameInput) {

                    usernameInput.focus();
                }


                return;
            }


            const passwordError =
                validatePassword(
                    password
                );


            if (passwordError) {

                showMessage(
                    message,
                    passwordError,
                    "error"
                );


                if (passwordInput) {

                    passwordInput.focus();
                }


                return;
            }


            loginSubmitting =
                true;


            try {

                setButtonLoading(
                    button,
                    true,
                    "ĐANG ĐĂNG NHẬP...",
                    "ĐĂNG NHẬP"
                );


                showMessage(
                    message,
                    "Đang kiểm tra tài khoản...",
                    "loading"
                );


                await loginUser(
                    username,
                    password
                );


                showMessage(
                    message,
                    "Đăng nhập thành công!",
                    "success"
                );


                window.setTimeout(
                    function () {

                        redirectToAccount();

                    },
                    400
                );

            } catch (error) {

                console.error(
                    "Đăng nhập:",
                    error
                );


                showMessage(
                    message,
                    error.message ||
                    "Đăng nhập thất bại.",
                    "error"
                );


                setButtonLoading(
                    button,
                    false,
                    "",
                    "ĐĂNG NHẬP"
                );


                loginSubmitting =
                    false;
            }
        }
    );
}


/* =========================================================
   REGISTER FORM
========================================================= */

function setupRegisterForm() {

    const registerForm =
        document.getElementById(
            "registerForm"
        );


    if (!registerForm) {

        return;
    }


    const usernameInput =
        document.getElementById(
            "registerUsername"
        );


    const passwordInput =
        document.getElementById(
            "registerPassword"
        );


    const confirmPasswordInput =
        document.getElementById(
            "registerConfirmPassword"
        );


    const message =
        document.getElementById(
            "authMessage"
        );


    const button =
        registerForm.querySelector(
            "button[type='submit']"
        );


    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            if (
                registerSubmitting
            ) {

                return;
            }


            const username =
                usernameInput
                    ? usernameInput.value
                    : "";


            const password =
                passwordInput
                    ? passwordInput.value
                    : "";


            const confirmPassword =
                confirmPasswordInput
                    ? confirmPasswordInput.value
                    : "";


            const usernameError =
                validateUsername(
                    username
                );


            if (usernameError) {

                showMessage(
                    message,
                    usernameError,
                    "error"
                );


                if (usernameInput) {

                    usernameInput.focus();
                }


                return;
            }


            const passwordError =
                validatePassword(
                    password
                );


            if (passwordError) {

                showMessage(
                    message,
                    passwordError,
                    "error"
                );


                if (passwordInput) {

                    passwordInput.focus();
                }


                return;
            }


            if (
                password !==
                confirmPassword
            ) {

                showMessage(
                    message,
                    "Mật khẩu nhập lại không khớp.",
                    "error"
                );


                if (
                    confirmPasswordInput
                ) {

                    confirmPasswordInput.focus();
                }


                return;
            }


            registerSubmitting =
                true;


            try {

                setButtonLoading(
                    button,
                    true,
                    "ĐANG TẠO TÀI KHOẢN...",
                    "TẠO TÀI KHOẢN"
                );


                showMessage(
                    message,
                    "Đang tạo tài khoản...",
                    "loading"
                );


                await registerUser(
                    username,
                    password
                );


                showMessage(
                    message,
                    "Tạo tài khoản thành công!",
                    "success"
                );


                window.setTimeout(
                    function () {

                        redirectToAccount();

                    },
                    400
                );

            } catch (error) {

                console.error(
                    "Đăng ký:",
                    error
                );


                showMessage(
                    message,
                    error.message ||
                    "Đăng ký thất bại.",
                    "error"
                );


                setButtonLoading(
                    button,
                    false,
                    "",
                    "TẠO TÀI KHOẢN"
                );


                registerSubmitting =
                    false;
            }
        }
    );
}


/* =========================================================
   AUTH PAGE DOM READY
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        setupLoginForm();

        setupRegisterForm();

        restoreLoginSession();
    }
);


/* =========================================================
   PUBLIC AUTH HELPERS
========================================================= */

window.MATHWEB_AUTH = {

    getToken,

    getUser,

    getSavedProfile,

    saveLoginData,

    clearAuthData,

    logout,

    loginUser,

    registerUser,

    getCurrentUser,

    restoreLoginSession
};