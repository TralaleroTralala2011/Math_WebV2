# V151 | Persistent data isolation and consistent backup

Base: V150_CANDIDATE_SCHEMA_RECONCILED.zip, verified by ZipFile.testzip() == None.

Changes:
- Optional MATHWEB_DATA_DIR redirects main users database plus study_suite, final_features and learning_progress SQLite files outside deployment tree; default paths remain unchanged for existing installations.
- Added SQLite online backup utility with integrity_check and SHA-256 manifest. No automatic overwrite/restore, no mutation of existing DB.
- Expanded .gitignore to exclude external data/backups and SQLite WAL sidecars.

IMPORTANT: Setting MATHWEB_DATA_DIR does not automatically migrate old DBs. Back up all old DBs, copy the resulting consistent snapshot files into the new directory BEFORE starting the backend. Existing MATHWEB_DB_PATH still overrides the main DB location. Other independent factory/history stores require separate migration/configuration and are NOT covered by this setting. Do not commit backups or user data to GitHub. A backup is not a full restore test.

Tests: 5/5 new unit tests passed; 17/17 selected V141-V145 pytest tests passed with PYTHONPATH=.; compileall passed. Full backend E2E, concurrent workload, mobile frontend and restoration on real user data NOT RUN. No performance improvement claimed without benchmarks.

Bank: 0 new candidates, 0 newly certified independent types, 0 newly verified/published questions. Previous V150 candidate audits remain intact. 300000/3000000 target not met.

Next: cover factory/history DBs with external persistent path, add safe migration dry-run and restore rehearsal, benchmark queries, inspect 1050 shared-core candidates, run full regression and Battle/Admin browser tests.
