/* MATH WEB API configuration */
(function () {
    const params = new URLSearchParams(window.location.search);
    const queryApi = params.get("api");
    const storedApi = window.localStorage.getItem("mathweb_api_url");
    const productionApi = "https://math-webv2.onrender.com";
    const localApi = "http://127.0.0.1:8000";
    const isLocalHost = ["localhost", "127.0.0.1"].includes(window.location.hostname);
    const configuredApi = queryApi || storedApi || window.MATHWEB_API_URL || (isLocalHost ? localApi : productionApi);
    window.MATHWEB_API_URL = String(configuredApi).replace(/\/+$/, "");
})();
