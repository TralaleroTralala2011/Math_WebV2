/* MATH WEB API configuration */

(function () {
    "use strict";

    const params = new URLSearchParams(window.location.search);
    const queryApi = params.get("api");

    const productionApi =
        "https://math-web-api-tralalerotralala2011.onrender.com";

    const localApi =
        "http://127.0.0.1:8000";

    const isLocalHost =
        ["localhost", "127.0.0.1", "[::1]"]
            .includes(window.location.hostname);

    const storedApi =
        window.localStorage.getItem("mathweb_api_url");

    let configuredApi;

    /*
     * GitHub Pages:
     * luôn dùng Render, không dùng API localhost
     * đã lưu từ những lần chạy local trước.
     */
    if (!isLocalHost) {
        configuredApi =
            queryApi ||
            productionApi;
    } else {
        /*
         * Chạy local:
         * cho phép dùng API đã lưu hoặc localhost.
         */
        configuredApi =
            queryApi ||
            storedApi ||
            window.MATHWEB_API_URL ||
            localApi;
    }

    window.MATHWEB_API_URL =
        String(configuredApi).replace(/\/+$/, "");

    window.MATHWEB_API_READY = true;

    console.log(
        "[MATH WEB API]",
        window.location.hostname,
        "→",
        window.MATHWEB_API_URL
    );
})();