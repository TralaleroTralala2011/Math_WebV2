# MATH_WEB V152 - Safe SQLite restore

Base: V151_PERSISTENT_DATA_BACKUP.zip (actual local ZIP). No application DB modified.

## Changes
- Added backend/scripts/restore_sqlite.py: validates manifest, SHA-256, file size and SQLite integrity before restoring; refuses nonempty destinations and traversal/duplicate names.
- Added backend/tests/test_v152_restore_sqlite.py: round-trip XP preservation, overwrite refusal, tamper rejection.
- Existing V151 backup script unchanged.

## Verified
- `python -m pytest -q tests/test_v152_restore_sqlite.py tests/test_v151_persistent_data.py`: 8 passed.
- No full backend, frontend, Battle or Admin E2E executed. No load benchmarks.
- Restore must run with backend stopped and an empty target directory; no migration of production data performed.

## Question bank
New candidates: 0; newly certified independent types: 0; newly verified/published questions: 0. Prior reported 1,609 candidate records and 1,050 shared-core-method flags are not certified independent types. No new mathematical or semantic deduplication audit this run.

## Remaining work
- Validate restore on a representative copy of all production DBs, including WAL concurrency and rollback behavior.
- Ensure all DB consumers use persistent data paths; add safe first-deployment migration with user confirmation and backups.
- Run full regression, E2E, accessibility/mobile and benchmark tests.
- Audit candidate mathematical methods and author genuinely independent types with verified exercises.
