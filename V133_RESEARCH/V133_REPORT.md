# MATH_WEB V133: Unpublished Mathematics Research Batch

Base: `MATH_WEB_GITHUB_READY_V132_RESEARCH_ENGINE_FIX.zip`, preserving existing frontend/backend/runtime files.

## Produced and verified in this batch

- **12 candidate method descriptions**, spanning grades 10, 11, 12.
- **120 new short-answer items**, exactly **10 for each candidate**; each contains an answer and worked solution.
- Two independent calculations agree on **120/120** numerical/symbolic answers in this reproducible set. This does not guarantee the pedagogical quality of each word problem or prove new methods.
- **0** normalized exact stem collisions in indexed **10,750 older distinct question texts** from V123, V131, and V132. No comprehensive semantic or all-version deduplication has been performed.
- **0 newly certified independent methods**, **0 published questions**. Every new record has `published=false`, `independence_certified=false`, `review_status=pending-expert-review`.
- V133 unit checks: **10 passed** (including altered-answer detection).
- Selected existing backend regression checks: **12 passed** (`test_v123_research.py`, `test_question_factory_v121.py`, `test_answer_equivalence_extension.py`).

## Outstanding work

- Request for >=1,000 *genuinely new methods* with ten exercises each is not met. There are 12 candidate methods, none with completed independent novelty review. Numeric variants of one method are not new methods.
- Final target is 150 x 2,000 = 300,000 independently distinct methods, 3,000,000 worked exercises. This release cannot certify that target.
- Answers are mechanically checked, while clarity, curriculum-topic mapping, misconception-based multiple choice distractors and meaningful exercise diversity require manual/independent expert evaluation.
- The bank remains **research only**, not integrated into the live question-serving routes.
- **Full end-to-end website regression, Battle, account flows, frontend UI and production DB were not executed**. No assertion that the website is bug-free.

## Reproduction

```
python V133_RESEARCH_generate.py
python -m unittest V133_RESEARCH.audit -v
cd backend && PYTHONPATH=. python -m pytest -q tests/test_v123_research.py tests/test_question_factory_v121.py tests/test_answer_equivalence_extension.py
```

Detailed machine-readable output: `V133_RESEARCH/V133_RESULTS.json`; logs in V133_RESEARCH.
