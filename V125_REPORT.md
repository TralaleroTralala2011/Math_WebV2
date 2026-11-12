# MATH_WEB V125 - conservative quality gate

Source: V124 ZIP. This release adds a separate audit tool and seven unit tests; no production question bank or user-facing code was changed.

## Real V123 dataset audit
- 1,050 candidate structures, 10,500 question records, 150 topics.
- 150 shared source-method clusters, all with more than one candidate; no new independent mathematical type certified.
- Structural checks: PASS. No duplicate normalized stems or fingerprints within this V123 dataset; no candidate ID collisions; all candidate families have 10 questions.
- 2,100 answer/numeric_result differences flagged for review. These may be MCQ answer labels rather than mathematical errors. The gate does not reject them automatically.
- Mathematical correctness of the 10,500 questions and semantic novelty are NOT certified by this check.
- New candidates: 0; new questions: 0; new certified independent types: 0.

## Regression
- `PYTHONPATH=. python -m unittest question_factory.test_v124_quality_gate question_factory.test_v125_quality_gate -v` from backend: 11/11 passed (4 inherited + 7 new).
- Full backend, UI, Battle, and integration regression were NOT run. Unmodified original project files retained.

## Usage
`cd backend && PYTHONPATH=. python -m question_factory.v125_quality_gate /path/to/candidates.jsonl /path/to/questions.jsonl`

## Next priorities
Inspect the 2,100 answer/numeric-result differences by question type, implement type-specific mathematical oracles, and require human method-level review before any candidate is certified or published.
