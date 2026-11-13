# MATH_WEB V36 – Geometry API configuration fix

## Confirmed defect
`geometry-studio.html` loaded `js/optional-api-v33.js` and V6/V7 scripts without `js/api-config.js`. On GitHub Pages the helper's fallback base URL is `http://127.0.0.1:8000`, not the production Render backend. This is a configuration defect, even though the affected V6/V7 handlers currently exit early on the geometry page.

## Change
Inserted `js/api-config.js` immediately before the optional API helper in `geometry-studio.html`. Added `backend/tests/test_v36_api_config_order.py` to prevent future regression. No other production file changed from V35.

## Verification
- 19 HTML pages using the optional API helper have API config loaded first.
- 7/7 focused backend contract tests passed.
- Full pytest suite from V35 was attempted; output reached 100%, but the process did not exit before the execution timeout. Do not interpret this as a confirmed full-suite pass.
- This is not a production GitHub Pages/Render end-to-end test. Persisted student data, CORS, Battle/Chat and real device interactions must still be verified on the live deployment.
