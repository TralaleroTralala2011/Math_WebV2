const API_URL = window.MATHWEB_API_URL || window.MATH_WEB_API_URL || window.MATH_WEB_API_BASE || "https://math-webv2.onrender.com";


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
            "Dá»¯ liá»‡u Ä‘Äƒng nháº­p khÃ´ng há»£p lá»‡."
        );
    }


    const token =
        typeof data.token === "string"
            ? data.token.trim()
            : "";


    if (!token) {

        throw new Error(
            "MÃ¡y chá»§ khÃ´ng tráº£ vá» token Ä‘Äƒng nháº­p."
        );
    }


    if (
        token.length >
        4096
    ) {

        throw new Error(
            "Token Ä‘Äƒng nháº­p khÃ´ng há»£p lá»‡."
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
            "Dá»¯ liá»‡u user trong localStorage khÃ´ng há»£p lá»‡."
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

        return "Vui lÃ²ng nháº­p tÃªn tÃ i khoáº£n.";
    }


    if (
        value.length <
        MIN_USERNAME_LENGTH
    ) {

        return `TÃªn tÃ i khoáº£n pháº£i cÃ³ Ã­t nháº¥t ${MIN_USERNAME_LENGTH} kÃ½ tá»±.`;
    }


    if (
        value.length >
        MAX_USERNAME_LENGTH
    ) {

        return `TÃªn tÃ i khoáº£n khÃ´ng Ä‘Æ°á»£c vÆ°á»£t quÃ¡ ${MAX_USERNAME_LENGTH} kÃ½ tá»±.`;
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

        return "Vui lÃ²ng nháº­p máº­t kháº©u.";
    }


    if (!password) {

        return "Vui lÃ²ng nháº­p máº­t kháº©u.";
    }


    if (
        password.length <
        MIN_PASSWORD_LENGTH
    ) {

        return `Máº­t kháº©u pháº£i cÃ³ Ã­t nháº¥t ${MIN_PASSWORD_LENGTH} kÃ½ tá»±.`;
    }


    if (
        password.length >
        MAX_PASSWORD_LENGTH
    ) {

        return `Máº­t kháº©u khÃ´ng Ä‘Æ°á»£c vÆ°á»£t quÃ¡ ${MAX_PASSWORD_LENGTH} kÃ½ tá»±.`;
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
        "ÄÃ£ xáº£y ra lá»—i."
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
                "Káº¿t ná»‘i mÃ¡y chá»§ quÃ¡ lÃ¢u. Vui lÃ²ng thá»­ láº¡i."
            );
        }


        if (
            error instanceof
            TypeError
        ) {

            throw new Error(
                "KhÃ´ng thá»ƒ káº¿t ná»‘i Ä‘áº¿n MATH WEB API. HÃ£y kiá»ƒm tra server."
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
                "ÄÄƒng kÃ½ tháº¥t báº¡i."
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
                "ÄÄƒng nháº­p tháº¥t báº¡i."
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
            "Kiá»ƒm tra session:",
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
            "API /api/auth/me khÃ´ng tráº£ vá» user há»£p lá»‡."
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
         * ChÆ°a tá»«ng Ä‘Äƒng nháº­p.
         */

        if (!token) {

            return;
        }


        /*
         * Kiá»ƒm tra token vá»›i server.
         */

        const user =
            await getCurrentUser();


        /*
         * Token há»£p lá»‡.
         */

        if (user) {

            /*
             * Chá»‰ chuyá»ƒn hÆ°á»›ng náº¿u
             * ngÆ°á»i dÃ¹ng Ä‘ang á»Ÿ login/register.
             */

            if (
                isAuthPage()
            ) {

                redirectToAccount();
            }


            return;
        }


        /*
         * Náº¿u server xÃ¡c nháº­n token
         * khÃ´ng há»£p lá»‡ thÃ¬ getCurrentUser()
         * Ä‘Ã£ xÃ³a auth data.
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
                    "ÄANG ÄÄ‚NG NHáº¬P...",
                    "ÄÄ‚NG NHáº¬P"
                );


                showMessage(
                    message,
                    "Äang kiá»ƒm tra tÃ i khoáº£n...",
                    "loading"
                );


                await loginUser(
                    username,
                    password
                );


                showMessage(
                    message,
                    "ÄÄƒng nháº­p thÃ nh cÃ´ng!",
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
                    "ÄÄƒng nháº­p:",
                    error
                );


                showMessage(
                    message,
                    error.message ||
                    "ÄÄƒng nháº­p tháº¥t báº¡i.",
                    "error"
                );


                setButtonLoading(
                    button,
                    false,
                    "",
                    "ÄÄ‚NG NHáº¬P"
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
                    "Máº­t kháº©u nháº­p láº¡i khÃ´ng khá»›p.",
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
                    "ÄANG Táº O TÃ€I KHOáº¢N...",
                    "Táº O TÃ€I KHOáº¢N"
                );


                showMessage(
                    message,
                    "Äang táº¡o tÃ i khoáº£n...",
                    "loading"
                );


                await registerUser(
                    username,
                    password
                );


                showMessage(
                    message,
                    "Táº¡o tÃ i khoáº£n thÃ nh cÃ´ng!",
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
                    "ÄÄƒng kÃ½:",
                    error
                );


                showMessage(
                    message,
                    error.message ||
                    "ÄÄƒng kÃ½ tháº¥t báº¡i.",
                    "error"
                );


                setButtonLoading(
                    button,
                    false,
                    "",
                    "Táº O TÃ€I KHOáº¢N"
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
