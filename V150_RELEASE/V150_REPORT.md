# MATH_WEB V150 | Candidate schema reconciliation

Base: V149_CANDIDATE_IDENTITY_AUDIT.zip (verified readable, ZIP integrity OK).

## Actual work
- Fixed candidate identity extraction: legacy `signature` is recognized as a candidate identity after `method_id`, `form_id`, `id`.
- 1,530 historical records previously reported as missing IDs now resolve to `signature`; 79 records use `method_id`. Missing identities: 0.
- Detected 1,050 candidates explicitly flagged `shared_core_method=true`, which is a serious warning against treating these as independent mathematical forms.
- Candidate records: 1,609 in 10 JSONL files. Exact normalized topic/method collisions: 0. Duplicate candidate identities: 0. Invalid/unsafe candidate records: 0.
- Tests: 7/7 candidate identity/schema tests; 17/17 scripts unit tests passed.

## Boundaries
- 0 new independent methods certified, 0 new questions published; all 1,609 records remain candidates.
- `signature` is a historical candidate key, not proof of a genuinely independent mathematical type.
- 1,050 `shared_core_method` records should be reviewed first for underlying method equivalence; cannot be counted as 1,050 novel types.
- No SQLite, application backend or frontend files intentionally changed. Browser Battle/Admin E2E and complete backend regression not run.
- No claim of reaching 300,000 independent types / 3,000,000 verified questions.

## Next
Review `shared_core_method` group, link candidates to actual questions, compare solving-method graphs against prior certified methods, then test application E2E. Never certify by signature alone.
