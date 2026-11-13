# MATH_WEB V35 – Optional API loading hotfix

## Confirmed V34 defect
17 HTML pages loaded `neon-v6-experience.js` / `neon-v7-experience.js` without first loading `js/optional-api-v33.js`. When logged-in scripts invoked `window.MATHWEB_OPTIONAL_API.get(...)`, this could throw `TypeError` and interrupt dashboard/progress updates. Only `index.html` and `learn.html` loaded the required helper in V34.

## Fix
Added the shared optional API helper before the dependent scripts on all 17 affected pages. No Battle, Chat, question-bank, drawing, or UI feature implementation was removed. Added `backend/tests/test_v35_optional_api_pages.py` to enforce script ordering on every page.

## Verification
- 19/19 dependent HTML pages now load the helper before dependent scripts.
- `node qa/v33_optional_api_test.cjs`: PASS (old backend skips unsupported APIs, updated backend calls supported features).
- Focused pytest (`test_v33_deploy_contract.py`, `test_v34_pilot_deploy.py`, `test_v35_optional_api_pages.py`): 6 PASS.
- Full backend suite was attempted but exceeded the available execution timeout; **do not claim full suite passed for V35**. V34 previously reported 240/240 pass.

## Important remaining risks
- This is a source-level fix, **not a live GitHub Pages/Render deployment**.
- Backend must be redeployed from the same commit; CORS, actual Render health, real-device Battle/Chat, database persistence, and two-account pilot tests still require live verification.
- No guarantee of zero bugs. Do not collect real student data until persistent storage and backup are confirmed.
