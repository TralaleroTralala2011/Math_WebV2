# V185 consolidated bank import

Source: V182 full website plus V183 and V184 incremental ZIPs.

Use `V185_VALIDATED_IMPORT.jsonl` ONLY. It contains 6,756 records passing the repository's structural and answer-grader checks. 112 repeated prompts and 72 invalid records were excluded. No independent mathematical verification, semantic independence certification, or production integration is claimed.

From the project root, with the actual existing database present:

```bash
python backend/scripts/import_bank_updates.py --db backend/database/mathweb.db --input bank_updates/V185_VALIDATED_IMPORT.jsonl
python backend/scripts/import_bank_updates.py --db backend/database/mathweb.db --input bank_updates/V185_VALIDATED_IMPORT.jsonl --write --backup backups/mathweb-before-v185.sqlite
```

The script refuses to create a missing database, requires an unused backup filename, records import ledger, and checks SQLite integrity. Never run concurrently with another bank writer. Review source provenance and semantic correctness before production import.
