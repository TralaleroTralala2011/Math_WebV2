# V183 question-bank-only checkpoint

Continues V182. Adds 755 unique (against V182 exact normalized prompts) arithmetic-oracle and app-validated questions to 83 existing candidate families. **No new independent forms certified**; these are numeric variants within existing candidate families, not 755 new forms. V181+V182+V183 combined import-ready count: 6110; not production-integrated. The source ZIP does not contain a verified live production SQLite database. Never treat these staging rows as production integration.

To import into an existing compatible, backed-up, authorized actual MATH_WEB SQLite DB, use:

`python backend/scripts/import_bank_updates.py --db PATH_TO_EXISTING_DB --input bank_updates/V183_IMPORT_READY.jsonl`

Then, only after reviewing preview and backup location:

`python backend/scripts/import_bank_updates.py --db PATH_TO_EXISTING_DB --input bank_updates/V183_IMPORT_READY.jsonl --write --backup NEW_UNUSED_BACKUP_PATH`

Use `python backend/scripts/bank_coverage_v182.py --db PATH_TO_EXISTING_DB --output bank_updates/V183_ACTUAL_DB_COVERAGE.json` for read-only stored-row audit. This script does not certify mathematical form independence. V183 has no changes to Battle, UI, accounts, or Admin.
