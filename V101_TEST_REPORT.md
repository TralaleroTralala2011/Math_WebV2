# V101 regression verification

- Browser: Chromium blocked local HTTP navigation with `ERR_BLOCKED_BY_ADMINISTRATOR` for index, login, admin, battle, practice and geometry-studio. This is an environment restriction, not evidence of a website defect.
- V100 targeted regression: 49/49 passed, plus Node syntax and SSS tests passed.
- Full suite (fail-fast): after fixing stale fixture in `backend/tests/test_2000_types_gate.py`, 80 tests passed, then `tests/test_problem_generator.py::ProblemGeneratorTests::test_mixed_question_set_contains_multiple_answer_modes` failed: `true_false` missing from a mixed 9-question set.
- A further unrestricted full suite run did not finish within the available 90-second window; do not interpret it as a pass.
- No production bug fix for mixed mode has been validated. No end-to-end browser certification, no 100% geometry coverage certification.
- No new problem types or questions were added.

## Reproduce

```bash
cd backend
PYTHONPATH=. python -m pytest -q tests/test_problem_generator.py::ProblemGeneratorTests::test_mixed_question_set_contains_multiple_answer_modes
PYTHONPATH=. python -m pytest -q --disable-warnings --maxfail=1
```
