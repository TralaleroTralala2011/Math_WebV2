# MATH_WEB V28 Classic V24 · V254 Bank Replacement

- Based on V23, keeps the V28 Classic UI and existing Battle/Chat/assessment components.
- Latest user uploaded V254 ZIP was bundled at `question_bank_v254_source/Question_Bank_V254_latest_uploaded.zip`.
- **83,298 source candidate records** loaded into a read-only SQLite index; old active 4,000-record JSON backed up.
- **147/150** knowledge topics mapped safely; remaining 3 topics fall back to existing generator.
- 3 additional topic names verified explicitly: Quy tắc đếm, Đường thẳng, Định lý ba đường vuông góc.
- Source 150 DOCX counts per grade: 50/50/50, while web taxonomy is 49/51/50; mapping cannot be assumed by list index.
- All imported questions remain **unverified drafts**, mathematical/pedagogical review required.
- Duplicate exact text eliminated at import. Format option checks and engine validation performed at runtime.
- Existing assessment (900), Admin and existing account data remain untouched.
- Test evidence: 5 selected integration tests passing and six sample questions generated from new bank across grades 10–12 and MCQ/free-response.
