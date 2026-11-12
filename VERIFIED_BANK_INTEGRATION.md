# Verified bank API (opt-in)

The 100-question seed bank is now accessible without changing existing practice or Battle flows.

- `GET /api/verified-bank/catalog` lists actual coverage.
- `GET /api/verified-bank/next?grade=10&topic=Phương%20trình` returns a question and one-time session ID, without revealing its answer.
- `POST /api/verified-bank/answer` accepts `{"session_id":"...","answer":"..."}` and returns a correctness check, feedback and solution.

Only numeric equivalence and exact-text fallback are supported. This is NOT reasoning-aware grading. Sessions are stored in memory and reset on restart. This endpoint is an opt-in pilot, not yet wired into the existing practice UI. The seed contains 10 forms / 100 questions, not 300,000 / 3,000,000.
