(function () {
    "use strict";


    /*
     * ============================================================
     * MATH WEB GAME PROGRESS
     * ============================================================
     *
     * Chịu trách nhiệm:
     *
     * - Lưu kết quả game
     * - Đồng bộ kết quả với server
     * - Lưu tiến trình offline
     * - Quản lý XP / Level offline
     * - Đồng bộ profile
     * - Quản lý lịch sử game local
     * - Hiển thị Level Up
     *
     * Khi đăng nhập:
     *     SERVER = nguồn dữ liệu chính
     *
     * Khi chưa đăng nhập:
     *     LOCAL STORAGE = nguồn dữ liệu chính
     * ============================================================
     */


    /*
     * ============================================================
     * CONFIG
     * ============================================================
     */

    const MATHWEB_API_URL =
        window.MATHWEB_API_URL ||
        window.MATHWEB_API_URL || "http://127.0.0.1:8000";


    const TOKEN_KEY =
        "mathweb_token";


    const PROFILE_KEY =
        "mathweb_profile";


    const PROGRESS_KEY =
        "mathweb_progress";


    const MAX_HISTORY =
        50;


    const REQUEST_TIMEOUT =
        10000;


    /*
     * ============================================================
     * DEFAULT LOCAL PROGRESS
     * ============================================================
     */

    const DEFAULT_PROGRESS = {

        level: 0,

        xp: 0,

        totalGames: 0,

        totalCorrect: 0,

        totalWrong: 0,

        totalBlank: 0,

        totalScore: 0,

        history: []

    };


    /*
     * ============================================================
     * TOKEN
     * ============================================================
     */

    function getMathWebToken() {

        try {

            return (
                localStorage.getItem(
                    TOKEN_KEY
                ) || ""
            ).trim();

        } catch {

            return "";
        }
    }


    /*
     * ============================================================
     * KIỂM TRA TOKEN
     * ============================================================
     */

    function isValidToken(token) {

        if (
            typeof token !== "string" ||
            !token.trim()
        ) {

            return false;
        }


        const parts =
            token.split(".");


        return (
            parts.length === 2 &&
            parts[0].length > 0 &&
            parts[1].length > 0 &&
            token.length <= 4096
        );
    }


    /*
     * ============================================================
     * KIỂM TRA ĐĂNG NHẬP
     * ============================================================
     */

    function isLoggedIn() {

        return isValidToken(
            getMathWebToken()
        );
    }


    /*
     * ============================================================
     * XÓA SESSION
     * ============================================================
     */

    function clearAuthData() {

        try {

            localStorage.removeItem(
                TOKEN_KEY
            );

            localStorage.removeItem(
                PROFILE_KEY
            );

        } catch {
            /* Không làm crash game */
        }
    }


    /*
     * ============================================================
     * LOCAL PROGRESS
     * ============================================================
     */

    function createDefaultProgress() {

        return {

            ...DEFAULT_PROGRESS,

            history: []

        };
    }


    function normalizeProgress(data) {

        const progress =
            createDefaultProgress();


        if (
            !data ||
            typeof data !== "object"
        ) {

            return progress;
        }


        progress.level =
            normalizeNonNegativeNumber(
                data.level,
                0
            );


        progress.xp =
            normalizeNonNegativeNumber(
                data.xp,
                0
            );


        progress.totalGames =
            normalizeNonNegativeNumber(
                data.totalGames,
                0
            );


        progress.totalCorrect =
            normalizeNonNegativeNumber(
                data.totalCorrect,
                0
            );


        progress.totalWrong =
            normalizeNonNegativeNumber(
                data.totalWrong,
                0
            );


        progress.totalBlank =
            normalizeNonNegativeNumber(
                data.totalBlank,
                0
            );


        progress.totalScore =
            normalizeNonNegativeNumber(
                data.totalScore,
                0
            );


        progress.history =
            Array.isArray(data.history)
                ? data.history.slice(
                    0,
                    MAX_HISTORY
                )
                : [];


        return progress;
    }


    function getProgress() {

        try {

            const saved =
                localStorage.getItem(
                    PROGRESS_KEY
                );


            if (!saved) {

                return createDefaultProgress();
            }


            const data =
                JSON.parse(saved);


            return normalizeProgress(
                data
            );

        } catch {

            return createDefaultProgress();
        }
    }


    /*
     * ============================================================
     * SAVE LOCAL PROGRESS
     * ============================================================
     */

    function saveProgress(progress) {

        const normalized =
            normalizeProgress(
                progress
            );


        try {

            localStorage.setItem(
                PROGRESS_KEY,
                JSON.stringify(
                    normalized
                )
            );


            return true;

        } catch (error) {

            console.error(
                "Không thể lưu tiến trình local:",
                error
            );


            return false;
        }
    }


    /*
     * ============================================================
     * XP CẦN CHO LEVEL
     * ============================================================
     *
     * Level 0 → 100 XP
     * Level 1 → 150 XP
     * Level 2 → 200 XP
     * ...
     *
     * Giữ đúng công thức backend hiện tại.
     * ============================================================
     */

    function getRequiredXP(level) {

        const safeLevel =
            normalizeNonNegativeNumber(
                level,
                0
            );


        return (
            100 +
            safeLevel * 50
        );
    }


    /*
     * ============================================================
     * CỘNG XP LOCAL
     * ============================================================
     */

    function addLocalXP(amount) {

        const progress =
            getProgress();


        const safeAmount =
            normalizeNonNegativeNumber(
                amount,
                0
            );


        progress.xp +=
            safeAmount;


        let levelUp = false;

        let levelsGained = 0;


        /*
         * Có thể lên nhiều level
         * nếu XP nhận được rất lớn.
         */

        while (
            progress.xp >=
            getRequiredXP(
                progress.level
            )
        ) {

            progress.xp -=
                getRequiredXP(
                    progress.level
                );


            progress.level++;

            levelsGained++;

            levelUp = true;
        }


        saveProgress(
            progress
        );


        return {

            progress,

            levelUp,

            levelsGained

        };
    }


    /*
     * ============================================================
     * FETCH HELPER
     * ============================================================
     */

    async function request(
        url,
        options = {}
    ) {

        const controller =
            new AbortController();


        const timeoutId =
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


            return response;

        } finally {

            clearTimeout(
                timeoutId
            );
        }
    }


    /*
     * ============================================================
     * LẤY PROFILE SERVER
     * ============================================================
     */

    async function getServerProfile() {

        const token =
            getMathWebToken();


        if (
            !isValidToken(token)
        ) {

            return null;
        }


        try {

            const response =
                await request(
                    `${MATHWEB_API_URL}/api/users/me`,
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


            /*
             * TOKEN KHÔNG HỢP LỆ
             */

            if (
                response.status === 401
            ) {

                clearAuthData();

                return null;
            }


            if (!response.ok) {

                return null;
            }


            const data =
                await response.json();


            if (
                !data ||
                typeof data !== "object"
            ) {

                return null;
            }


            try {

                localStorage.setItem(
                    PROFILE_KEY,
                    JSON.stringify(
                        data
                    )
                );

            } catch {
                /* Không làm crash game */
            }


            return data;

        } catch (error) {

            if (
                error &&
                error.name !== "AbortError"
            ) {

                console.error(
                    "Không thể đồng bộ profile:",
                    error
                );
            }


            return null;
        }
    }


    /*
     * ============================================================
     * LƯU GAME RESULT
     * ============================================================
     */

    async function saveGameResult(result) {

        const normalizedResult =
            normalizeGameResult(
                result
            );


        /*
         * ĐÃ ĐĂNG NHẬP
         *
         * Server là nguồn chính.
         */

        if (
            isLoggedIn()
        ) {

            return saveGameResultToServer(
                normalizedResult
            );
        }


        /*
         * CHƯA ĐĂNG NHẬP
         *
         * Lưu local.
         */

        return saveGameResultLocally(
            normalizedResult
        );
    }


    /*
     * ============================================================
     * NORMALIZE GAME RESULT
     * ============================================================
     */

    function normalizeGameResult(
        result
    ) {

        const source =
            result &&
            typeof result === "object"
                ? result
                : {};


        return {

            gameName:
                safeString(
                    source.gameName,
                    "Math Game"
                ),

            topicName:
                safeString(
                    source.topicName,
                    "Toán học"
                ),

            total:
                normalizeNonNegativeNumber(
                    source.total,
                    0
                ),

            correct:
                normalizeNonNegativeNumber(
                    source.correct,
                    0
                ),

            wrong:
                normalizeNonNegativeNumber(
                    source.wrong,
                    0
                ),

            blank:
                normalizeNonNegativeNumber(
                    source.blank,
                    0
                ),

            score:
                normalizeNonNegativeNumber(
                    source.score,
                    0
                ),

            xp:
                normalizeNonNegativeNumber(
                    source.xp,
                    0
                ),

            time:
                normalizeNonNegativeNumber(
                    source.time,
                    0
                )
        };
    }


    /*
     * ============================================================
     * LƯU SERVER
     * ============================================================
     */

    async function saveGameResultToServer(
        result
    ) {

        const token =
            getMathWebToken();


        if (
            !isValidToken(token)
        ) {

            return {

                success: false,

                source: "server",

                error:
                    "Không có token đăng nhập."
            };
        }


        try {

            const response =
                await request(
                    `${MATHWEB_API_URL}/api/games/result`,
                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json",

                            "Authorization":
                                `Bearer ${token}`,

                            "Accept":
                                "application/json"
                        },

                        body:
                            JSON.stringify({

                                game_name:
                                    result.gameName,

                                topic_name:
                                    result.topicName,

                                total:
                                    result.total,

                                correct:
                                    result.correct,

                                wrong:
                                    result.wrong,

                                blank:
                                    result.blank,

                                score:
                                    result.score,

                                xp:
                                    result.xp,

                                time:
                                    result.time

                            })
                    }
                );


            /*
             * TOKEN KHÔNG HỢP LỆ
             */

            if (
                response.status === 401
            ) {

                clearAuthData();


                /*
                 * Không tự chuyển trang ở đây.
                 *
                 * Engine/game có thể đang ở giữa
                 * màn hình kết quả.
                 */

                return {

                    success: false,

                    source: "server",

                    unauthorized: true,

                    error:
                        "Phiên đăng nhập đã hết hạn."
                };
            }


            /*
             * SERVER ERROR
             */

            if (!response.ok) {

                let errorMessage =
                    "Không thể lưu kết quả lên server.";


                try {

                    const errorData =
                        await response.json();


                    if (
                        errorData &&
                        typeof errorData.detail ===
                        "string"
                    ) {

                        errorMessage =
                            errorData.detail;
                    }

                } catch {
                    /* Không có JSON lỗi */
                }


                console.error(
                    "Server không thể lưu kết quả game."
                );


                return {

                    success: false,

                    source: "server",

                    error:
                        errorMessage
                };
            }


            /*
             * Đọc response
             */

            let data =
                null;


            try {

                data =
                    await response.json();

            } catch {

                data = {};
            }


            /*
             * Đồng bộ profile.
             *
             * Không để lỗi profile
             * làm mất kết quả game.
             */

            const profile =
                await getServerProfile();


            /*
             * LEVEL UP
             */

            if (
                data &&
                data.level_up
            ) {

                showLevelUp(
                    data.level
                );
            }


            /*
             * KHÔNG CỘNG XP LOCAL
             *
             * Server đã xử lý XP.
             */

            return {

                success: true,

                source: "server",

                data:

                    data,

                profile:
                    profile
            };

        } catch (error) {

            console.error(
                "Lỗi kết nối server:",
                error
            );


            /*
             * CỐ Ý KHÔNG FALLBACK LOCAL
             *
             * Vì server có thể đã nhận game
             * nhưng response bị mất.
             *
             * Nếu lưu local lần nữa,
             * có nguy cơ cộng kết quả hai lần.
             */

            return {

                success: false,

                source: "server",

                networkError: true,

                error:
                    error &&
                    error.name === "AbortError"
                        ? "Server phản hồi quá lâu."
                        : "Không thể kết nối server."
            };
        }
    }


    /*
     * ============================================================
     * LƯU LOCAL
     * ============================================================
     */

    function saveGameResultLocally(
        result
    ) {

        const xpResult =
            addLocalXP(
                result.xp
            );


        const updated =
            xpResult.progress;


        /*
         * =========================
         * THỐNG KÊ
         * =========================
         */

        updated.totalGames += 1;

        updated.totalCorrect +=
            result.correct;

        updated.totalWrong +=
            result.wrong;

        updated.totalBlank +=
            result.blank;

        updated.totalScore +=
            result.score;


        /*
         * =========================
         * LỊCH SỬ
         * =========================
         */

        updated.history.unshift({

            gameName:
                result.gameName,

            topicName:
                result.topicName,

            total:
                result.total,

            correct:
                result.correct,

            wrong:
                result.wrong,

            blank:
                result.blank,

            score:
                result.score,

            xp:
                result.xp,

            time:
                result.time,

            date:
                new Date().toISOString()

        });


        /*
         * =========================
         * GIỚI HẠN LỊCH SỬ
         * =========================
         */

        if (
            updated.history.length >
            MAX_HISTORY
        ) {

            updated.history =
                updated.history.slice(
                    0,
                    MAX_HISTORY
                );
        }


        saveProgress(
            updated
        );


        /*
         * =========================
         * LEVEL UP
         * =========================
         */

        if (
            xpResult.levelUp
        ) {

            showLevelUp(
                updated.level
            );
        }


        return {

            success: true,

            source: "local",

            progress:
                updated,

            levelUp:
                xpResult.levelUp,

            levelsGained:
                xpResult.levelsGained
        };
    }


    /*
     * ============================================================
     * LEVEL UP
     * ============================================================
     */

    function showLevelUp(level) {

        const safeLevel =
            normalizeNonNegativeNumber(
                level,
                0
            );


        /*
         * Nếu UI có hệ thống riêng,
         * ưu tiên dùng nó.
         */

        if (
            typeof window !== "undefined" &&
            typeof window.onMathWebLevelUp ===
            "function"
        ) {

            try {

                window.onMathWebLevelUp(
                    safeLevel
                );

                return;

            } catch (error) {

                console.error(
                    "Level Up UI error:",
                    error
                );
            }
        }


        /*
         * Fallback đơn giản.
         */

        setTimeout(
            function () {

                alert(
                    "🚀 LEVEL UP! 🎉\n\n" +
                    "Chúc mừng! Bạn đã đạt Level " +
                    safeLevel +
                    "!"
                );

            },
            300
        );
    }


    /*
     * ============================================================
     * XP HIỆN TẠI
     * ============================================================
     */

    function getXPProgress() {

        const progress =
            getProgress();


        const required =
            getRequiredXP(
                progress.level
            );


        const percent =
            required > 0
                ? (
                    progress.xp /
                    required
                ) * 100
                : 0;


        return {

            level:
                progress.level,

            currentXP:
                progress.xp,

            requiredXP:
                required,

            percent:
                Math.min(
                    100,
                    Math.max(
                        0,
                        Number(
                            percent.toFixed(2)
                        )
                    )
                )
        };
    }


    /*
     * ============================================================
     * SERVER XP PROGRESS
     * ============================================================
     *
     * Nếu profile server có:
     *
     * level
     * xp
     *
     * thì dùng trực tiếp.
     *
     * Nếu không có profile,
     * fallback local.
     * ============================================================
     */

    function getServerXPProgress(
        profile
    ) {

        if (
            !profile ||
            typeof profile !== "object"
        ) {

            return null;
        }


        const level =
            normalizeNonNegativeNumber(
                profile.level,
                0
            );


        const xp =
            normalizeNonNegativeNumber(
                profile.xp,
                0
            );


        const required =
            getRequiredXP(
                level
            );


        return {

            level:

                level,

            currentXP:

                xp,

            requiredXP:

                required,

            percent:

                required > 0
                    ? Math.min(
                        100,
                        Math.max(
                            0,
                            Number(
                                (
                                    xp /
                                    required *
                                    100
                                ).toFixed(2)
                            )
                        )
                    )
                    : 0
        };
    }


    /*
     * ============================================================
     * FORMAT THỜI GIAN
     * ============================================================
     */

    function formatHistoryTime(
        seconds
    ) {

        const safeSeconds =
            normalizeNonNegativeNumber(
                seconds,
                0
            );


        const minutes =
            Math.floor(
                safeSeconds / 60
            );


        const remaining =
            safeSeconds % 60;


        return (

            String(minutes)
                .padStart(
                    2,
                    "0"
                )

            +

            ":"

            +

            String(
                remaining
            ).padStart(
                2,
                "0"
            )
        );
    }


    /*
     * ============================================================
     * ĐỒNG BỘ PROFILE
     * ============================================================
     */

    async function syncProfile() {

        if (!isLoggedIn()) {
            return null;
        }


        return getServerProfile();
    }


    /*
     * ============================================================
     * LẤY PROFILE LOCAL
     * ============================================================
     */

    function getLocalProfile() {

        try {

            const saved =
                localStorage.getItem(
                    PROFILE_KEY
                );


            if (!saved) {
                return null;
            }


            const data =
                JSON.parse(
                    saved
                );


            return (
                data &&
                typeof data === "object"
                    ? data
                    : null
            );

        } catch {

            return null;
        }
    }


    /*
     * ============================================================
     * LẤY THỐNG KÊ LOCAL
     * ============================================================
     */

    function getLocalStatistics() {

        const progress =
            getProgress();


        return {

            totalGames:
                progress.totalGames,

            totalCorrect:
                progress.totalCorrect,

            totalWrong:
                progress.totalWrong,

            totalBlank:
                progress.totalBlank,

            totalScore:
                progress.totalScore,

            accuracy:
                progress.totalGames > 0
                    ? Number(
                        (
                            progress.totalCorrect /
                            Math.max(
                                1,
                                progress.totalCorrect +
                                progress.totalWrong +
                                progress.totalBlank
                            ) *
                            100
                        ).toFixed(2)
                    )
                    : 0
        };
    }


    /*
     * ============================================================
     * XÓA LOCAL PROGRESS
     * ============================================================
     */

    function clearLocalProgress() {

        try {

            localStorage.removeItem(
                PROGRESS_KEY
            );

            return true;

        } catch {

            return false;
        }
    }


    /*
     * ============================================================
     * UTILITY
     * ============================================================
     */

    function normalizeNonNegativeNumber(
        value,
        fallback
    ) {

        const number =
            Number(value);


        if (
            !Number.isFinite(number) ||
            number < 0
        ) {

            return fallback;
        }


        return Math.floor(
            number
        );
    }


    function safeString(
        value,
        fallback
    ) {

        if (
            typeof value !== "string"
        ) {

            return fallback;
        }


        const trimmed =
            value.trim();


        return trimmed
            ? trimmed
            : fallback;
    }


    /*
     * ============================================================
     * GLOBAL API
     * ============================================================
     */

    window.MATHWEB_PROGRESS = {

        getMathWebToken,

        isLoggedIn,

        getProgress,

        saveProgress,

        getRequiredXP,

        addLocalXP,

        getServerProfile,

        saveGameResult,

        saveGameResultToServer,

        saveGameResultLocally,

        showLevelUp,

        getXPProgress,

        getServerXPProgress,

        formatHistoryTime,

        syncProfile,

        getLocalProfile,

        getLocalStatistics,

        clearLocalProgress

    };


    /*
     * ============================================================
     * BACKWARD COMPATIBILITY
     * ============================================================
     *
     * Giữ các hàm cũ để game-engine.js và những file cũ
     * vẫn có thể gọi trực tiếp.
     * ============================================================
     */

    window.getMathWebToken =
        getMathWebToken;

    window.isLoggedIn =
        isLoggedIn;

    window.getProgress =
        getProgress;

    window.saveProgress =
        saveProgress;

    window.getRequiredXP =
        getRequiredXP;

    window.addLocalXP =
        addLocalXP;

    window.getServerProfile =
        getServerProfile;

    window.saveGameResult =
        saveGameResult;

    window.saveGameResultToServer =
        saveGameResultToServer;

    window.saveGameResultLocally =
        saveGameResultLocally;

    window.showLevelUp =
        showLevelUp;

    window.getXPProgress =
        getXPProgress;

    window.formatHistoryTime =
        formatHistoryTime;

    window.syncProfile =
        syncProfile;


})();