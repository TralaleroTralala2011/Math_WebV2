# MATH_WEB V48 · Battle, Learning & Question Bank Integration

Release date: 2026-11-14. Baseline: `MATH_WEB_V47_PRACTICE_FRIENDS_BATTLE_FIX_20261113.zip` (2,916 original ZIP entries).

## Code changes and data preservation

Only six original files were modified: `battle.html`, `learn.html`, `learning-path.html`, `js/battle.js`, `backend/app/matchmaking/routes.py`, and `backend/app/ai/engine/service.py`.

Six files were added: `css/mw-battle-bank-v48.css`, `css/mw-learning-bank-v48.css`, `js/mw-learning-bank-v48.js`, `backend/app/ai/engine/v254_bank.py`, `backend/tests/test_v48_matchmaking_bank_contract.py`, and this report. All other original ZIP member data is byte-for-byte unchanged, including the original account, friends, chat, Admin, and user database code. No hardcoded admin password or elevated bypass was introduced.

## Completed integration

1. **Random Battle** now sends the selected grade (10/11/12) instead of omitting the request JSON and silently defaulting to grade 12. Grade 10 is shown initially; previous choice is kept in localStorage. The server continues to require a compatible grade and common topics.
2. **Player ID** and **friend invitations** use that same Battle grade setting; the established server-side invite, approval, and friend-checking logic is unchanged. The UI clarifies that an Online indicator may update slowly, and does not block invites based on stale presence.
3. **Battle questions** come from the existing reviewed admin bank plus packaged V254 candidates. A single deck is stored in the match and shared with both players. Answers and solutions are excluded from match question responses. No new problems are generated during a match. Requested difficulty is tried first; where unavailable, a medium fallback is visibly identified per question.
4. **Practice** continues using `AIQuestionService.generate_set` with its previously integrated V254 and admin-curated sources. A lightweight database filter now rejects grossly malformed question text, answer, or solution lengths before further structural checks.
5. **Study (`learn.html`)** and **Personal Learning Path (`learning-path.html`)** now offer an optional, isolated “Luyện tập bổ trợ theo chủ đề” panel using the **same** `/api/ai/practice/session` and `/api/ai/questions/{id}/answer` engine. Users choose grade/topic and get five questions plus server-graded answers and solutions. This feature does **not** replace verified lessons or official Roadmap assessments. It clearly labels V254 questions as unverified candidates.
6. **V254 seed restore**: if the read-only V254 SQLite is absent after a local start/deploy, a helper restores it from the existing packaged archive with byte count and SHA-256 verification, using an atomic file replacement. This does not touch accounts or production user data.

## Bank evidence (not quality certification)

The existing V254/B54 packaged seed contains **83,298 candidate questions** across **147 of the 150** `(grade, topic)` pairs used by the AI knowledge list: Grade 10 has 24,557; Grade 11 has 29,474; Grade 12 has 29,267. Of these, 41,128 are multiple-choice and 42,170 are short-answer. No V254 true/false rows exist; mixed-mode generation can draw this type from other validated sources.

Topics absent from this V254 seed are Grade 10 `he_thuc_luong`, `he_thuc_luong_van_dung_10` and Grade 11 `ham_so_luong_giac_day_du`. Candidate status is **not mathematical certification**. The Roadmap assessment retains its own independently reviewed question gate, while the new optional panel is unscored practice.

The unrelated optional `verified_seed_bank.jsonl` is only a **134-byte Git LFS pointer** in the original ZIP, not the full verified-seed data. Tests of that optional dataset fail until the actual LFS object is provided; do not claim that bank is integrated or verified.

## Tests and limits

- `PYTHONPATH=backend pytest -q backend/tests/test_v48_matchmaking_bank_contract.py backend/tests/test_v37_battle_bank.py backend/tests/test_api_integration.py backend/tests/test_security_battle_logout.py backend/tests/test_question_diversity.py backend/tests/test_v36_api_config_order.py backend/tests/test_mixed_mode_distribution_v102.py backend/tests/test_semantic_grading_regression.py`: **33 passed**.
- `node --check js/battle.js` and `node --check js/mw-learning-bank-v48.js`: passed.
- `python -m compileall` on modified backend modules: passed.
- ZIP integrity and byte-level comparison against V47: passed (see release output).
- A Chromium-based browser test was attempted, but this environment blocked loopback navigation with `ERR_BLOCKED_BY_ADMINISTRATOR`. **Real browser UI and the deployed Render/GitHub services were not validated.**
- The existing `backend/tests/test_verified_bank_quality.py` fails because the Git LFS pointer is not the JSONL data. This is an identified unresolved external-asset issue, separate from the packaged V254 seed.

## Deployment

Deploy this ZIP's `MATH_WEB_GITHUB_READY` contents as the matching GitHub Pages frontend and Render backend. The packaged `render.yaml` retains the V254 restore build step. Make sure both devices use the same working backend and persistent user database. Do not delete the existing user database to restore a question bank. A green ZIP integrity check is not a guarantee of zero production bugs.
