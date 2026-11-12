# MATH_WEB V137 checkpoint

Source: V136 ZIP. No changes to runtime UI, Battle, auth or API source.

## Work done
- Added `scripts/audit_research_linkage_v137.py` to cross-check research method IDs, question IDs, topic/grade linkage, 10-question coverage, literal question duplicates, mandatory fields and publication status.
- Corrected a false-positive pattern in duplicate checking: stripping math signs had treated `x+(-3)` and `x+(3)` as identical. New comparison retains mathematical symbols and ignores whitespace.
- Audited five candidate files and five research question files: **68 candidate methods, 680 questions, 68 linked methods**. No duplicate question text under sign-preserving normalization, no orphan IDs or topic/grade mismatches.
- **1 stored answer/independent_check mismatch** and **1 method with all ten answers equal** flagged for review. These are diagnostics, not proof of mathematical error.
- Six regression tests for the new gate passed.
- Backend full-suite attempt with `pytest` failed collection (Python import path); rerun using `python -m pytest` was interrupted before completion. No claim of backend pass. Original SQLite database files were restored from the V136 ZIP after testing.

## Quantities
- New candidate methods: 0; new questions: 0; independently certified methods: 0.
- Target: 150 topics x 2,000 independent methods x 10 questions = 300,000 methods and 3,000,000 questions. NOT COMPLETE.

## Scope limitations
- This audit does not verify mathematical correctness independently, nor semantic uniqueness of methods. Other historical banks are outside this specific linkage check. All research candidates remain pending review and unpublished.
- No claim of complete Battle/frontend/backend regression.
