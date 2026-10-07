/* MATH WEB API configuration */
(function () {
    const params = new URLSearchParams(window.location.search);
    const queryApi = params.get("api");
    const storedApi = window.localStorage.getItem("mathweb_api_url");
    const configuredApi = queryApi || storedApi || window.MATHWEB_API_URL || "http://127.0.0.1:8000";
    window.MATHWEB_API_URL = String(configuredApi).replace(/\/+$/, "");
})();
