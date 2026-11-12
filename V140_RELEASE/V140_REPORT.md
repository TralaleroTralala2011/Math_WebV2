# MATH_WEB V140 | Grading and optional candidate source safety

**Source:** locally verified `MATH_WEB_GITHUB_READY_V139_ANTI_REPEAT_RETRY_FIX.zip`.
**Date:** 2026-11-08. **Release class:** incremental, NOT project completion.

## Verified changes

1. Improved `backend/question_factory/grading.py` to accept mathematically equivalent numeric single-variable assignments (`x=2` and `2`, `x=1/2` and `x=0.5`) and unambiguous two-coordinate answers (`(x,y)=(7;5)` vs `(7;5)` or `x=7;y=5`). The parser uses bounded Python AST inspection and SymPy arithmetic; user input is **never** passed to eval, sympify, parse_expr, or any execution primitive. The comma form `(7,5)` is NOT treated as an ordered pair because Vietnamese notation uses decimal commas. Distinct variable names and swapped coordinates are not equated. Arbitrary symbolic equations and proofs remain unsupported; they must not be auto-certified by string equality.
2. `backend/question_factory/storage.py` skips opt-in V122 method registration cleanly when the V122 Python module is missing, returning **zero** candidates and retaining no false certification.
3. `backend/question_factory/operations.py` records `v122_requested`, `v122_source_available` and `v122_skipped_missing_source` in its progress snapshot, with a warning if opt-in requested but unavailable. Missing optional V122 can no longer crash the whole operator cycle.
4. Added `backend/tests/test_v140_factory_grading_and_optional_v122.py` with 6 regression tests including expression injection rejection, replay protection and V122 source reporting.

## Test evidence

- Targeted backend, session/worker, operations, grading and API tests: **44 passed**, 6 FastAPI deprecation warnings (`on_event`).
- Complete backend suite: **NOT certified in this run**. It progressed through 69% before timeout in an expensive V120 test that generates 1,500 stems, without a final overall result. No claim of full backend/website regression.
- New tests alone: 6 passed in 0.80s.

## Provenance and integrity

Constructed by streaming the original V139 ZIP, replacing only the three patched Python modules and adding this release report/checkpoint and the test file. Source SQLite, previously working UI, Battle, accounts and all unrelated files are **byte-identical to V139**. ZIP integrity and unchanged entries are separately checked in `V140_PACKAGE_AUDIT.json` outside ZIP. No active deployment or live browser E2E test.

## Target progress, accurately stated

- Requested per iteration: **100,000 truly independent new mathematical methods** with **1,000,000 verified worked examples**.
- Original final target: **150 topics × 2,000 genuinely distinct types/topic × 10 questions = 300,000 methods / 3,000,000 questions**.
- V140 new independent methods certified: **0**. New authored questions: **0**. V140 is a runtime correctness fix, not a numerical expansion.
- Existing V131–V135 research candidates remain unapproved pending real mathematical novelty and subject review; changing numeric inputs, IDs, story text, or formats does not count as a new method. No claim of zero defects.

## Next checkpoint

1. Integrate stable sequence keys into actual practice/Battle UI after testing two-user Battle flows.
2. Build independent mathematical method ontology per topic, deduplicate by **solution strategy**, then review and certify. Only then generate ten verified distinct questions per accepted method.
3. Address expensive V120 full test and add split/parallel pipeline; re-run full backend and browser E2E regressions.
4. Keep official DB clean; never auto-publish unreviewed candidate forms. Resume from this V140 ZIP if available.

Automation `Tiếp tục MATH_WEB` confirmed enabled and configured hourly; separate scheduled runs, not one continuous 60-minute process.
