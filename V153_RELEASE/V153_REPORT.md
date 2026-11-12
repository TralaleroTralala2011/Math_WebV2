# MATH_WEB V153 checkpoint

Source: V152. This release adds external storage routing for Question Factory and AI history, and a dry-run-first legacy database migration.

Selected regression: 81 passed, 6 warnings. Source database SHA-256 unchanged: True.

New independent certified forms: 0. New verified questions: 0. Full backend, browser E2E and load tests not run. No production migration performed.

Migration: stop backend; inspect `python backend/scripts/migrate_persistent_data.py --help` from project root and run from backend directory; dry run first, then --apply only with separate empty destination and backup directories. Set MATHWEB_DATA_DIR only after successful restore and verification. Do not commit private databases.
