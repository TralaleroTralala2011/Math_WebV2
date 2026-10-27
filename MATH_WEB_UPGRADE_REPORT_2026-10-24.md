
## 2026-10-24: Question-system audit and tier upgrade

- Repaired 12 malformed individual-game HTML script injections. The affected pages now load `js/api-config.js` and initialize `window.MATH_GAME` as a separate script, so grade/topic IDs reach the question API.
- Added the `learning_tier` API field and mapping for three explicit tracks:
  - `foundation`: Sơ cấp, full THPT curriculum revision.
  - `provincial`: Mở rộng, provincial gifted-student preparation.
  - `national`: Chuyên sâu, national gifted-student preparation.
- Individual knowledge-game stages now request the corresponding tier and generator difficulty.
- Added a dedicated question bank for `g10_geom_coordinate_distance_midpoint`: midpoint, point distance, recover endpoint, point dividing a segment in a ratio, parameter conditions, distance comparisons, locus, parallelogram coordinates and advanced minimization.
- Fixed the browser fallback for this topic so it generates coordinate/midpoint questions instead of falling back to generic arithmetic when the API is unavailable.
- Improved short-answer equivalence checks for coordinate pairs, fractions, decimals and square-root expressions using a restricted arithmetic parser (no `eval`).
- Added regression tests for topic lock, diagrams, solutions and equivalent answers.
- Verification: `PYTHONPATH=. pytest -q` in `backend/` passed **83 tests**; Python AI modules compile; 441 knowledge-game HTML pages audited and 0 malformed nested-script injections remain.

### Important grading note

The current grader uses exact generated answer keys and mathematical equivalence checks. It does not pretend to call a hosted LLM when no model provider/API key is configured. For open-ended proof grading against a rubric, a real model provider still needs to be configured and separately validated before its score is treated as authoritative.
