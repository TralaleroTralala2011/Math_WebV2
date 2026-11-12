# MATH_WEB V149 - Candidate identity audit

Base: V148_REVIEW_RISK_AUDIT.zip. This release changes only `scripts/audit_research_method_collisions.py`, adds one unit test and a release checkpoint; no SQLite, application backend or frontend files modified.

## Measured
- Candidate records scanned: 1609 across 10 JSONL files.
- Exact normalized topic+method collision groups: 0.
- Duplicate nonblank candidate ID groups: 0.
- Candidate records without an ID in recognized fields: 1530 (metadata warning, **not** a mathematical duplicate finding).
- Invalid candidate records: 0.
- New certified independent methods: 0. New published questions: 0.

## Test evidence
`python -m unittest discover -s scripts -p test_v149_candidate_identity.py -v`: 3/3 passed. Full backend regression and browser E2E: not run.

## Scope and limitations
Candidate ID audit catches exact ID reuse, not mathematical method equivalence. Some historical candidate schemas may use different ID keys; missing ID count should be inspected before enforcing ID requirements. All existing database files preserved. This release does not meet the target of 1,000 independent types per batch.

## Next
Inspect historical candidate schema for the 1,530 missing IDs; reconcile candidate-to-question references, manually review solving-method independence, then test backend and Battle/Admin E2E. Keep research candidates unpublished until verified.
