# MATH_WEB V134 | Research corpus and topic-catalog repair

**Base:** `MATH_WEB_GITHUB_READY_V133_RESEARCH_AUDITED.zip` (a complete accessible ZIP, not a guessed earlier artifact).

## What changed

1. Created 18 **authored research candidate objectives** spanning grade 10, grade 11, and grade 12, with **10 worked questions each (180 total)**. Mathematical generation asserts independent answer calculations (enumeration, exact geometry, solving, direct substitution, calculus, or optimization).
2. Fixed four mismatches against the official 150-topic curriculum catalog. In V132, corrected `vectơ → vector`, `toa_do_trong_mat_phang → toa_do_phang`, and `to_hop_xac_suat → xac_suat_11`. In V133, corrected `logarit → pt_logarit`. This repairs **four candidate method records and 40 question records**. Both generator source definitions and their corresponding checked JSONL outputs were changed; regeneration matched the amended files byte for byte.
3. Introduced a reusable audit (`V134_RESEARCH/audit.py`) to block unknown topic IDs, wrong grade mappings, repeated question IDs/stems, incomplete groups, unreviewed publication, corrupted answer fields, and collision with the older indexed banks. Its regression tests include deliberately mutated records.
4. Did **not** edit the application runtime files under `backend/`, the frontend, Battle, authentication, or account handling. Research content is quarantined and is **not** served to learners.

## Results: measured, not extrapolated

| Check | Measured result |
|---|---:|
| Official curriculum topics in catalog | 150 |
| New authored candidate objectives | 18 |
| New worked questions | 180 |
| Mathematically cross-checked generated answers | 180/180 |
| Indexed previous question records | 13,870 |
| Normalized literal duplicate stems | 0 |
| V134 quality-gate unit tests | 11/11 pass |
| Selected question-factory and equivalence backend tests | 12/12 pass |
| Selected real FastAPI integration tests: accounts, matchmaking, friends/chat, assignments | 10/10 pass, 6 warnings |
| New independent methods **certified** | **0** |
| Newly published questions | **0** |
| Complete frontend/backend UI and production deployment end-to-end regression | **not run** |

The previous 13,870 indexed question records are the datasets from V121 (3,000), V123 (10,500), V131 (150), V132 (100), and V133 (120). The audit checks normalized exact question stems only, not full semantic identity, topic quality, or 100% of all historical datasets. A successful arithmetic oracle does not establish that a method is genuinely new, every solution is pedagogically optimal, or the complete website has no bugs.

## Reproduce in the project root

```sh
python V132_RESEARCH_generate.py
python V133_RESEARCH_generate.py
python V134_RESEARCH_generate.py
python V134_RESEARCH/audit.py
python -m unittest discover -s V134_RESEARCH -p 'test_v134.py' -v
cd backend
PYTHONPATH=. python -m pytest -q tests/test_v123_research.py tests/test_question_factory_v121.py tests/test_answer_equivalence_extension.py
PYTHONPATH=. python -m pytest -q tests/test_api_integration.py tests/test_learning_assignments.py
```

## Goal progress and limits

Requested end state: **150 topics × 2,000 independent mathematical methods × 10 exercises = 300,000 independently validated methods and 3 million fully solved questions.** A batch of 1,000 genuine new methods would also require 10,000 independently validated exercises. This batch contains 18 candidates and 180 mathematically cross-checked exercises, but **0 methods newly certified independent**. Differing numerical values, IDs, order or question wording do not count as distinct methods. The goals are **not reached**.

Nothing here guarantees continuous cloud execution. The installed recurring ChatGPT task is a scheduled invocation, not an always-running process. Full-stack testing, expert novelty assessment, semantic deduplication, and a production deployment review are still needed.
