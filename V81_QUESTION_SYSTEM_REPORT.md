# MATH_WEB V81: Question system update

Base: V80 complete archive. No runtime account database is included.

## Changes
- Added admin-only `GET /api/admin/learning/assignment-bank/matrix` (depending on router prefix), with `grade` and `topic` query arguments.
- Reports counts of Word-source eligible, shape-deduplicated questions by easy/medium/hard/expert and multiple-choice/short-answer/mixed formats.
- Never treats the reported counts as independently verified mathematical correctness.
- Preserves V80 source-Word exact prompt checks, topic checks, cached-assignment quarantine and no generated filler policy.
- Existing practice and games are retained; this release does NOT certify cross-game global semantic deduplication.

## Tests
7 passed: test_v81_question_matrix.py, test_v78_assignment_word_quality.py, test_learning_assignments.py.

## Deployment caution
Render Free local SQLite is ephemeral; this archive does not migrate accounts to PostgreSQL. Do not use it to replace or overwrite a live account database.
