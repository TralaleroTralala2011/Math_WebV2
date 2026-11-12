/* MATH WEB API configuration */
(function () {
    const params = new URLSearchParams(window.location.search);
    const host = window.location.hostname;
    const isLocalHost = ["localhost", "127.0.0.1"].includes(host);
    // When a phone opens the frontend over home/school Wi-Fi, the backend is
    // on that same computer at port 8000, NOT on the public Render deployment.
    const isLanHost = /^(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.(?:\d{1,3}\.)\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3})$/.test(host);
    const isLocalNetwork = isLocalHost || isLanHost;
    // Ignore URL-controlled backend redirects on public deployments: a crafted
    // ?api= address must never receive a signed account bearer token.
    const queryApi = isLocalNetwork ? params.get("api") : null;
    let storedApi = null;
    try { storedApi = window.localStorage.getItem("mathweb_api_url"); } catch (_) {}


    const productionApi = "https://math-webv2.onrender.com";
    const localApi = `http://${isLocalHost ? "127.0.0.1" : host}:8000`;
    // A saved production API must not override the LAN backend when the user
    // opens the website from a phone on the same Wi-Fi. Explicit ?api= remains
    // available on local installs for advanced configuration.
    let applicableSavedApi = storedApi;
    if (isLocalNetwork && storedApi) {
        try {
            const savedHost = new URL(storedApi).hostname;
            const isSavedLan = ["localhost", "127.0.0.1"].includes(savedHost) ||
                /^(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.(?:\d{1,3}\.)\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3})$/.test(savedHost);
            if (!isSavedLan) applicableSavedApi = null;
        } catch (_) { applicableSavedApi = null; }
    }
    const configuredApi =
        queryApi ||
        applicableSavedApi ||
        window.MATHWEB_API_URL ||
        (isLocalNetwork ? localApi : productionApi);

    let validApi = isLocalNetwork ? localApi : productionApi;
    try {
        const parsed = new URL(configuredApi);
        if (["http:", "https:"].includes(parsed.protocol) && !parsed.username && !parsed.password &&
            (isLocalNetwork || parsed.protocol === "https:") && !parsed.search && !parsed.hash) {
            validApi = parsed.origin + parsed.pathname.replace(/\/+$/, "");
        }
    } catch (_) {}
    window.MATHWEB_API_URL = validApi;
})();
