# MATH_WEB V121 | 2 candidate problem objectives per official topic

## Task and actual output

- Base: `MATH_WEB_GITHUB_READY_V120_150_TOPICS_1500_QUESTIONS.zip`.
- Official catalog: **150 topic IDs**, grades 10, 11 and 12.
- New authored **candidate** problem objectives: **300**, exactly two per topic.
- New example questions: **3,000**, exactly ten per candidate and twenty per topic.
- Cumulative Question Factory candidate forms V113–V121: **770** (470 prior + 300 new); no claim that these are globally independent.
- Every new question has a stem, an exact response, a four-step method/substitution/exact-answer explanation, a category, a topic ID and a blocked-publication quality status.
- Distribution: 600 short answers, 600 multiple choice, 600 true/false, 600 short essay, 548 applied exercises, 52 problems marked as real-world context.
- All newly authored content is **pending expert review**: 0 mathematically independent methods certified; 0 pedagogy-reviewed questions certified.

## Verification scope

- 3,000/3,000 records regenerated successfully, expressions computed with SymPy, MCQ answers uniquely matched one choice and true/false assertions compared with the computed answer.
- 3,000 new stems are not exactly duplicated within this batch.
- Compared against 348,956 normalized unique stem hashes from 348,980 readable legacy candidate/core rows: **0 exact stem collisions**. Text matching is not a semantic plagiarism or method-equivalence proof.
- Method-similarity triage produced **235 warnings comparing newly authored candidates against 470 existing candidate types in the same topic**. These may contain false positives.
- There are **49 shared expression groups** across different topics, which need pedagogical consideration. A shared numerical formula does not alone prove the same conceptual objective, but cannot certify novelty either.
- Some questions are closely related to other objectives or are narrow subskills. They remain quarantined; do not claim 300 genuinely independent methods without expert adjudication.

## Integration

- `question_factory/v121_research.py`: topic-aligned candidate generator + arithmetic/veracity checks.
- `question_factory/v121_specs.txt`: 150 authored rows, each with two objectives, stems, formulas and explanatory principles.
- `question_factory/v121_audit.py`: reproducible topical coverage, exact-text and similarity triage.
- `question_factory/engine.py`: V121 dispatch for generation and verification.
- `question_factory/storage.py`: `seed_v121` idempotently imports 300 pending-review entries.
- `question_factory/operations.py`: registers V121 entries during ordinary scheduler cycles; only approved types can enter worker jobs.
- `tests/test_question_factory_v121.py`: 6 new tests covering coverage, 3,000 symbolic substitutions, tampering, worker review gate and idempotent orchestrator. Historical operational test expected totals are updated from 470 to 770 to match intentional additional registrations.
- Existing learning, Battle, accounts, friends, chat and UI source files were not edited.

## Tests completed in this work session

| Executed group | Passed | Failing |
|---|---:|---:|
| Question Factory V121 | 6 | 0 |
| V115 operations | 6 | 0 |
| V119 + V120 regression | 10 | 0 |
| Backend API integration | 9 | 0 |
| Learning assignments + geometry curriculum | 7 | 0 |
| Geometry diagrams + equivalence + semantic grading | 23 | 0 |
| **Total of disjoint completed groups** | **61** | **0** |

The entire backend test suite was **not** completed in a single full run; some larger grouped attempts timed out. The 61 completed tests are not a production certification. Docker and real devices were not tested here.

## Remaining limitations

1. **Independence of candidate forms**: unsolved; human mathematics review of near-duplicates and topic fit is required.
2. **Pedagogical quality**: numeric verification and template integrity do not validate all prose assumptions, proof steps and plausible distractors.
3. **Existing historical question bank**: not overwritten or reclassified by this release.
4. **Public publication**: blocked by review status; no automatic rollout to games, learning path or Battle.
5. **Long-running deployment**: no VPS was connected or modified.
6. **75,000-form/750,000-question intermediate goal**: still not achieved or certified.

Use V121 as a review-pending extension, not as an independently verified 300-method publication.
