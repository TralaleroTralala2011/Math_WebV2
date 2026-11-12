# V167 Question Factory import patch

Source: V158_GITHUB_SOURCE_ONLY.zip (latest full source accessible in this execution). Research source: V166_REVIEW_ONLY.zip. The V166 archive is NOT full website source.

- 530 pending research questions were inventoried. 20 numerical questions from two method groups were independently checked by direct summation and safely imported into an isolated 150-topic Question Factory SQLite test database.
- 20 imported; 0 rejected in selected scope; 510 remain pending review. 0 independent mathematical methods certified.
- Two topics with imported questions: `day_so` and `cap_so_cong` (grade 11).
- Importer is idempotent: rerun imported 0 and reused 20.
- Factory API `/api/factory/next` and `/api/factory/answer` returned HTTP 200 and correct grading for both topics; replay was rejected with HTTP 404.
- Existing `backend/app/main.py` mounts Question Factory router. This test does NOT demonstrate that existing Practice or Battle gameplay has been rewired to call this API, nor that any remote deployed website has been updated.
- No user account DB was accessed or modified; sandbox SQLite is not bundled in public ZIP. No GitHub push was made.
- `review_status='approved'` means approved for *numerical question serving in the sandbox*, not certified mathematical independence. Independence certification remains 0.

## Import into a controlled staging deployment

1. Back up your separate Question Factory SQLite database and deploy the patched source into a staging copy of the actual website. Do not overwrite a newer source version with this older V158 baseline.
2. Run from `backend` with `PYTHONPATH=.`:
   `python -m question_factory.import_reviewed_v167 --db /path/to/staging/question_factory.sqlite3 --source-zip /path/to/MATH_WEB_GITHUB_READY_V166_REVIEW_ONLY.zip`
3. Ensure the 150-topic catalog is installed first (`question_factory.bootstrap.initialize_factory` or normal app startup).
4. Test `/api/factory/next?topic_id=day_so&surface=practice` and `/api/factory/answer`; then test real Practice and Battle clients separately.
5. Do not deploy on live user DB without backups, migration review, and complete regression testing.

## Next

Review the remaining 510 candidates, especially multiple-choice and symbolic-expression grading; compare method signatures with the existing historical corpus, and integrate into actual Practice/Battle request paths with end-to-end tests.
