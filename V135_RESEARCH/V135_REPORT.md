# MATH_WEB V135 | Research candidates, expanded duplicate scan, and safe regression

**Base archive (actually accessible):** `MATH_WEB_GITHUB_READY_V134_TOPIC_REPAIR_RESEARCH_QA.zip`.
**Release naming:** `MATH_WEB_GITHUB_READY_V135_RESEARCH_DUPLICATES_SAFE_QA.zip`.

## What this update really contains

1. **13 authored research method objectives**, each with exactly **10 worked Vietnamese math exercises**: **130 candidate questions**, mapped to official catalog topic IDs in grades 10, 11, and 12.
2. Every question has a solution, mathematical answer and **second computational check** (SymPy solve/integrate/limit, coordinate projection, direct finite enumeration, combination counting, or trigonometric root enumeration). The generator asserts equivalence and the audit separately reproduces all saved records.
3. `V135_RESEARCH/audit.py` scans **30 historical JSONL banks** (147,499,059 source bytes), not just the five selected research files used by V134. It reads **302,513 historical question records** and finds **302,512 distinct normalized stems**. **No normalized literal collisions** were detected for V135's 130 questions. This is **not semantic deduplication** and is not a scan of all possible SQLite/on-demand/web sources.
4. Identified **one existing historical literal duplicate**: V62 line 57 `v62_method_006` and V64 line 57 `v64_geometric_sequence_nth`, both ask for the fifth term of a geometric progression with `u₁=8`, `q=2`. Recorded in `V135_HISTORICAL_DUPLICATES.json`. Neither original record was removed or changed; a future data-import deduplication policy must review it.
5. Added mutation tests for unknown topic, wrong grade, missing exercise, duplicate question, false certification, premature publication, and both answer/check fields tampered together. The latter is caught by *source regeneration*, not a vulnerable answer-vs-check string comparison.
6. Added `scripts/run_backend_tests_isolated.py` to run pytest using temporary copies of SQLite databases via `MATHWEB_DB_PATH` / `MATHWEB_AI_HISTORY_DB_PATH` and verify the shipped originals are unchanged. This reduces risk of a regression run modifying a deliverable database.

**No application-runtime code paths under `backend/app`, `backend/question_factory`, `js`, or `games` were modified**. The new question candidates are **quarantined research content**, not served to students and not certified novel.

## Measured gates

| Check | V135 result |
| --- | ---: |
| Topics in official curriculum catalog | 150 |
| Newly authored research candidate groups | 13 |
| New questions (10 per group) | 130 |
| Mathematically recomputed candidate answers | 130 / 130 |
| Historical JSONL banks scanned | 30 |
| Historical questions scanned | 302,513 |
| New exact normalized question collisions in those banks | 0 |
| Historical normalized duplicates found | 1 |
| V135 mutation/regeneration tests | 13 / 13 passed |
| V131–V134 prior research regression tests | 32 / 32 passed |
| Backend Python suite | 193 / 193 passed, 6 deprecation warnings |
| JavaScript syntax checks (root `js`, `games`, `learn-assets`) | 32 / 32 passed |
| New independent **method types certified** | **0** |
| New published questions | **0** |
| Browser-to-browser Battle, production deployment and frontend visual E2E | **not verified** |

The backend suite contains checks of API and game-related operations, but this does **not** prove the website is universally bug-free. Warnings are FastAPI `on_event` deprecations; no assurance about future library versions.

## Reproduce

```sh
python V135_RESEARCH_generate.py
python V135_RESEARCH/audit.py
python -m unittest discover -s V135_RESEARCH -p 'test_v135.py' -v
python -m unittest discover -s V131_RESEARCH -p 'test_v131.py' -v
python -m unittest discover -s V132_RESEARCH -p 'test_v132.py' -v
python -m unittest discover -s V134_RESEARCH -p 'test_v134.py' -v
python scripts/run_backend_tests_isolated.py -q tests
find js games learn-assets -type f -name '*.js' -print0 | xargs -0 -n1 node --check
```

## Remaining goal and limitations

The target requested by the user is **150 topics × 2,000 genuinely independent types × 10 verified exercises = 300,000 independently distinct method types and 3,000,000 exercises**, plus no known bugs after whole-system regression. The new requirement of at least 1,000 independent types per expansion is **not met** in V135. By design, **13 unreviewed objectives are *candidates*, not independently certified types**. Different coefficients, IDs, wording, or answer formats never raise the certified method count.

The next meaningful work is to develop and expert-review genuinely different strategies, compare method signatures semantically across all historic families, fix historical ingestion collisions, and run browser-to-browser E2E tests against an isolated test database. Periodic ChatGPT scheduled tasks are **not** a continuously running one-hour worker; each run needs current code/file access and must independently report evidence.
