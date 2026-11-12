# MATH_WEB V182 bank expansion

The new 1,660 question records are in `V182_IMPORT_READY.jsonl`. They belong to 83 candidate mathematical families, 20 questions per family, 83 formerly uncovered topics. The V181 import file remains unchanged (3,695 records). Together they cover the 150-topic catalog with 5,355 import-ready records.

**Do not count these 83 families as independently certified forms.** They are candidate families only, pending full semantic and mathematical proof auditing. A new family name, ID, or numeric variant does not establish independence.

Use the existing `backend/scripts/import_bank_updates.py` with `--input bank_updates/V182_IMPORT_READY.jsonl`. `IMPORT_BANK_V182.bat` previews, backs up, imports V181 first, then V182, and audits the 150-topic count. Do not run while the backend is writing to SQLite.

The generator source is `backend/question_factory/v182_generate.py`; it reproduces the JSONL and audit into a separate output folder and does not write to production.
