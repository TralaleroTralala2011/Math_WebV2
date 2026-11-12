# MATH_WEB V28 Classic V23 – Functional QA

## Implemented
- Fixed client-side Battle WebSocket stale callback race during rapid disconnect/reconnect. Old `onclose`, `onopen`, `onmessage` can no longer overwrite or interfere with a replacement connection.
- Added `backend/tests/test_v23_reconnect.py`: two independent auth identities, two WebSocket connections, disconnect/reconnect and server sync with temporary database.
- Added question-bank secondary audit `V28_V23_QUESTION_REVIEW.json`. All 900 items remain pending independent mathematical and pedagogical validation.

## Honest boundaries
- WebSocket backend integration is **not** a two-browser UI test.
- Chromium in this environment returns `ERR_BLOCKED_BY_ADMINISTRATOR` even for `data:` navigation; visual QA of all 20 pages remains blocked.
- Static checks cannot certify mathematical truth or calibrate difficulty. A qualified independent reviewer and pilot with students are needed for full pedagogical certification.
- Existing V28 Classic visuals, V254 B25 bank data, and diagnostic question dataset have not been modified.
