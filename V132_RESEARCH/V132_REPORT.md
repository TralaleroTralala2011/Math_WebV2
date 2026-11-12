# MATH_WEB V132: Research Batch and Question Factory Import Fix

## Scope
Based on `MATH_WEB_GITHUB_READY_V131_RESEARCH_VERIFIED_PENDING_REVIEW.zip`.

- **10 new unpublished candidate methods**, **100 worked short-answer questions** (10 per candidate); grades 10–12 across 10 selected topics.
- Independent mathematical cross-checks in `V132_RESEARCH_generate.py`: 100/100 consistent. These check *answer arithmetic*, not deep review of pedagogy or mathematical novelty.
- 100/100 distinct question strings within batch. Exact normalized comparison against **10,650 previous question records**: no overlaps found. **No semantic proof of non-duplication.**
- All candidates and questions remain `pending-expert-review`, `published=false`, and `independence_certified=false`.
- Fixed a reproducible backend crash: `backend/question_factory/engine.py` previously unconditionally imported `v122_research`, absent from the inherited ZIP. Generate/verify now skips that *optional* module when it is missing. It does not mask errors inside installed modules.

## Tests executed

- V132 unit tests: **11/11 passed**, one initial solution-length failure was addressed by expanding explanations, then retested.
- V131 unit tests: **10/10 passed**.
- Targeted backend tests `test_v123_research.py`, `test_question_factory_v121.py`, `test_answer_equivalence_extension.py`: **12/12 passed** after engine fix. Before fix: 3 failed (missing module and related worker failure).
- Full integrated UI, Battle, account, DB and API regression: **NOT RUN**. Thus this release does **not** warrant a whole-website health claim.

## Numbers that must not be conflated

| Metric | This release |
|---|---:|
| New method candidates | 10 |
| New questions | 100 |
| Answer checks matching | 100/100 |
| Exact normalized overlaps found against scanned banks | 0 |
| New methods *independently certified as novel* | **0** |
| New questions published to production bank | **0** |
| User-requested total final target | 300,000 genuinely distinct methods, 3,000,000 questions |

## Limitations

- The 10 candidates have not passed independent expert novelty checks against all prior formulas and techniques; numbering does not prove novelty.
- Only the V131 and V123 research JSONL banks were available at known paths for this specific exact-string scan. Earlier library files exist but were not exhaustively compared semantically.
- Ten questions within each candidate share a method by design. Diverse parameters do not create additional methods. Diversity of problem statement and didactic quality still needs scrutiny.
- This update does **not** fulfill the request for 1,000 new independent problem types nor the final 2,000 types per topic.

## Reproduce

```sh
python V132_RESEARCH_generate.py
python V132_RESEARCH/audit.py
python -m unittest discover -s V132_RESEARCH -p test_v132.py -v
python -m unittest discover -s V131_RESEARCH -p test_v131.py -v
cd backend
PYTHONPATH=. python -m pytest -q tests/test_v123_research.py tests/test_question_factory_v121.py tests/test_answer_equivalence_extension.py
```
