# V136 research candidate audit checkpoint

Source: `MATH_WEB_GITHUB_READY_V135_RESEARCH_DUPLICATES_SAFE_QA.zip`.

Added `scripts/audit_research_method_collisions.py`, a reusable fail-closed check that identifies duplicate *exact normalized topic + method-label* pairs across candidate research banks and flags any candidate marked certified/published. Its output is `V136_AUDIT/method_collisions.json`. Added three unit tests.

**Measured:** 9 candidate JSONL files, 1,598 candidate records, 1,598 records with a topic and a method/skill signature. Zero exact normalized topic+method collisions in this narrow check; zero prematurely published/certified candidates flagged. This does **not** prove that any methods are mathematically distinct: labels can differ while strategies are equivalent, and some older records use generic skill text. No new questions, no certified independent types and no runtime application changes were made in this checkpoint.

**Known limitations:** This check covers the nine research candidate files matching `V*_RESEARCH/*CANDIDATE*jsonl`, not every historical source or the SQLite bank. No browser E2E or complete production audit. Target 300,000 certified independent methods and 3,000,000 verified questions remains unmet. Continue from this archive, expand semantic review and inspect candidate families with expert supervision before publication.

Reproduce: `python scripts/audit_research_method_collisions.py --output V136_AUDIT/method_collisions.json` and `python -m unittest discover -s V136_AUDIT -p 'test_*.py' -v`.
