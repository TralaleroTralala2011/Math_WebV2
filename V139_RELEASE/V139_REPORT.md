# MATH_WEB V139 | Runtime factory reliability checkpoint

**Based on:** `MATH_WEB_GITHUB_READY_V138_EQUIVALENCE_AUDIT.zip` (verified local archive).
**Date:** 2026-11-08. **Release status:** partial progress, not the 300,000-type / 3,000,000-question final delivery.

## Actual source modifications

1. `backend/question_factory/storage.py`: Added opt-in repeat avoidance when requesting an approved, mathematically verified question. A client passes an opaque `sequence_key` shared across requests. The token is SHA-256 hashed in SQLite. The new flow prioritizes questions not used recently and, when possible, changes the archetype from the previous question. The session history is retained for up to about 24 hours (maximum last 200 records per topic). When the question pool is exhausted, repeats are unavoidable. With no sequence key, the old stateless behavior remains supported. A sequence key is a caller-controlled study-session scope, not a trusted authenticated identity or a privacy identifier.
2. Migrated existing factory SQLite `answer_sessions` tables additively (`sequence_hash`, `created_at`) while retaining previous rows. Set the timestamp **inside `BEGIN IMMEDIATE`** to preserve request ordering under concurrent calls. Exclude expired unused sessions from the active-session cap.
3. `backend/question_factory/api.py`: `/api/factory/next` accepts an optional 12–128 character opaque `sequence_key`, validating it without changing existing callers. No answers are disclosed on retrieval; grading remains one-time-use.
4. `backend/question_factory/storage.py`: If a previously rejected, deterministic question later passes independent verification after a verifier fix, its existing row may transition to `verified` while recording its previous rejected validation. Enforce the existing verified-question hard cap. Old behavior could permanently stall a job despite a fixed verifier.
5. `backend/tests/test_v139_sequence_anti_repeat.py`: 10 regression checks cover alternating methods, unique questions, single-method fallback, uneven pool, API/backward compatibility, concurrent access, migration, key validation, rejected-to-verified retry and the hard cap.

## Measured tests

- **Full Python backend:** 202 / 202 passed in 101.36 seconds (6 `FastAPI on_event` deprecation warnings); test run began before the final fine-tuning of query priority.
- **Latest V139 targeted tests:** 10 / 10 passed after fine-tuning; covers new SQL ordering logic.
- ZIP construction uses unchanged V138 entries and updates only 2 runtime modules, 1 new test file and V139 release metadata/logs. This avoids bundling SQLite changes accidentally introduced in an extracted test workspace.

## Restrictions and qualification

- **0 newly certified independent mathematical types** and **0 newly published/generated questions** in V139. This version fixes serving and retry correctness, not corpus size. In particular it does not satisfy 1,000 independent types/10,000 questions per batch.
- This factory API is an **opt-in pilot**; existing homepage/Practice/Battle web screens are not automatically wired to `/api/factory/next` with `sequence_key`. Passing a new random key on every call would disable history, so an integrating client must retain a stable opaque token per learner session.
- The policy enforces no recent literal repeats within its finite history window, not global semantic novelty across the complete 302k+ corpus. Repeating the mathematical method becomes necessary if the approved pool has too few types with unseen questions. No false 100% anti-repeat or zero-defect claim.
- **No live two-browser Battle E2E**, manual content review, production deployment, front-end visual audit or 150-topic × 2,000-method certification in this run.
- All unreviewed candidate forms remain unapproved and unavailable to student gameplay. Previous website features are not intentionally changed.

## Resume next iteration

1. Wire stable sequence identifiers into each relevant authorized UI/client; validate Battle/practice separately against actual API, not mock-only tests.
2. Maintain separate Battle fallback pools, implement session-aware semantic method exclusion when enough independently certified types exist.
3. Audit question bank per-topic against **independent strategy signatures** with expert review; author genuine novel strategies with 10 independently checked questions each. Do not count numeric substitutions or unreviewed candidate IDs.
4. Confirm persistent production database migrations on a backup and add browser-to-browser E2E tests plus full front-end tests. Address FastAPI lifespan deprecations separately.
5. Preserve this ZIP and checkpoint as input for the next hourly task. No statement that a ChatGPT conversation runs code continuously for an hour is warranted.
