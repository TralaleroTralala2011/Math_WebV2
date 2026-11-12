# MATH_WEB V158: Question Bank Research Checkpoint

**Scope:** Research question bank only; no application/runtime code or database modified. 
**Input:** MATH_WEB_GITHUB_READY_V157_PRIVATE_CHECKPOINT.zip (archive verified: 2306 entries; `ZipFile.testzip()` passed). No Git commit verified.
**Archive source SHA256:** 670fc22ae66e67ba1c2b63f346262d45abba2757fdcc5e80a14e82448bc1fce2
**Recorded UTC:** 2026-11-09T06:33:15.984210+00:00. Start/end elapsed time not independently recorded; no 50–60 minute runtime claim.

## New material
- New candidate methods: **6**, including CRT, binomial coefficients, 3D line-plane intersection, orthogonal vectors, finite geometric series and frequency-weighted variance.
- New questions with step-by-step worked solutions and cross-check oracles: **60**, exactly **10 per candidate**.
- MCQ **42** (four distinct options, exactly one matching canonical solution); free-response **12**; true/false **6**.
- New certified independent methods: **0**. New published question bank questions: **0**. Candidate methods remain pending external method-level review.
- Previous candidates and questions retained, but total unique certified corpus **not independently determined**.

## Duplication and tests
- Normalized exact-text scan of **649,653** historical question records and **1,740** title records across **56** JSONL files.
- Exact question collisions: **0**; exact method-title collisions: **0**. This does **not** establish semantic distinctness or method independence.
- **6/6** V158 research unit tests passed (`V158_RESEARCH/TEST_RESULTS.log`); **60/60** numerical/symbolic reference answers checked by a separate computational route in each method.
- Previous V157 claim: 281 tests passed; NOT rerun in V158. Battle/Admin browser tests, stress tests and responsive checks not run.
- All **6** packaged historical SQLite files byte-for-byte unchanged relative to V157. **No DB migration** or credential handling in V158.

## Pending and limitations
- Compare these six methods manually against historical method families, not just titles, to decide novelty. Do not auto-certify.
- Review mathematical phrasing, distractor plausibility and curriculum-topic mapping before publication.
- Full-app regressions, staging verification and million-question benchmark not run.
- Target 300,000 independent forms / 3,000,000 published verified questions remains **unmet**; do not infer cumulative certified totals.
- Keep source code package separate from private checkpoint; never upload private historical SQLite to GitHub.

## Reproduce
`python V158_RESEARCH/build.py`
`python -m unittest discover -s V158_RESEARCH -p 'test_v158.py' -v`
`python V158_RESEARCH/audit.py`

## Deliverables
`MATH_WEB_GITHUB_READY_V158_PRIVATE_CHECKPOINT.zip` has historical DB and is private; `MATH_WEB_GITHUB_READY_V158_GITHUB_SOURCE_ONLY.zip` excludes SQLite. V158 source files are in `V158_RESEARCH` and this report in `V158_RELEASE`.
