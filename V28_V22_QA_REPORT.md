# MATH_WEB V28 Classic V22 – Function QA and assessment review
Date: 2026-11-12.

## Changes
- Updated `learning-path.js`: assessment report now presents a per-topic breakdown (correct/total and sample-size caveat). Existing V28 Classic styling left untouched.
- Added `backend/tests/test_v22_two_account_flow.py`: two registered account flow including invitation, acceptance, match start, complete 10-question skip-and-finish, two simultaneous authenticated battle WebSocket connections, friendship, messaging and notification endpoint.
- Added executable offline structural audits in `scripts/audit_v22_assessment_quality.py` and `scripts/audit_v22_html_static.py`.

## Verified technical test results
- 36/36 selected backend pytest tests passed; this includes 4 new two-account integration tests with a temporary database.
- 20 HTML pages parsed with viewport and local asset references checked: 0 missing in static audit.
- 900 assessment entries, 150 topic mappings, 0 matrix/answer-index/duplicate-ID/exact-question structural errors.
- 4,000 V254 B25 imported question-bank records retained.
- `node --check learning-path.js`: PASS.
- ZIP CRC check required before distributing package.

## Important limitations
- The 900 questions have NOT been independently certified for mathematical correctness, pedagogy or calibrated difficulty. All 900 remain pending independent review according to source `review_status` fields.
- True/false key distribution is 198 true / 102 false, a bias worth revising during item validation. Do not flip keys without rewriting propositions and checking answers.
- Browser visual testing could NOT run here. Chromium/Playwright blocked both localhost and file navigation with ERR_BLOCKED_BY_ADMINISTRATOR. All 20 pages were tested statically instead, not visually or interactively at desktop/mobile sizes.
- Two-user Battle tests run in FastAPI TestClient and exercise backend WebSocket events, not two separate real browser windows. Disconnect recovery, client-side timer rendering and actual multi-browser UI still need end-to-end validation.
- Chat/friend/notification flow was exercised by two independent auth tokens and a temporary SQLite DB; UI realtime rendering remains unverified.
- These results do not establish 100% end-to-end website completion. No independent human pedagogical evaluation has occurred.
