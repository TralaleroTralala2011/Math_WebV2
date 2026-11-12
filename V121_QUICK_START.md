# MATH_WEB V121: quick start (without GitHub)

The project root remains `MATH_WEB_GITHUB_READY`.

The new data is located under `V121_RESEARCH/`:

- `V121_300_CANDIDATE_FORMS.jsonl` contains 300 candidate objectives.
- `V121_3000_NEW_QUESTIONS.jsonl` contains 3,000 checked sample records.
- `V121_TOPIC_PROGRESS_150.csv` covers all 150 official topics.
- `V121_AUDIT_REPORT.json` and `V121_POTENTIAL_METHOD_OVERLAPS.json` include similarity warnings.

To run the V121 checks after installing the existing project's dependencies:

```powershell
cd MATH_WEB_GITHUB_READY\backend
python -m pytest -q tests/test_question_factory_v121.py
```

The Question Factory operations already register V121 on the next regular cycle. Registration does NOT make 300 candidates playable. Expert review and explicit approval are required.

Do not change the existing game/UI or public database before regression tests, database backup and mathematical review.
