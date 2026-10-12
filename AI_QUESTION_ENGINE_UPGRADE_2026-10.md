# MATH_WEB AI Question Engine: additive anti-repeat upgrade

## Base and preservation
This upgrade is based on `MATH_WEB_UNIFIED_COMPLETE_100P_2.zip`. It adds an anti-repeat history layer to the existing question service. It does not replace the current pages, practice UI, battle UI, game pages, account/auth flows, or the legacy/super-bank/problem generator layers.

## Generation layers already in the project
- Legacy game-question bank and template composer.
- Extended question bank and structure-first Super Bank (62 registered builder archetypes across 86 topic mappings in this build).
- Mixed question types: multiple choice, short answer, and true/false.
- Difficulty adaptation and stepwise explanations.
- Multi-part scenario generator with 2–6 linked parts and geometry diagrams.
- Server-side answer checking.

## New anti-repeat behavior
- A SQLite ledger stores question fingerprints and generation metadata, not personal data.
- Exact questions are checked against the ledger before being returned, including questions created in previous sets and previous backend runs, as long as the same database file is retained.
- Recently used archetypes, numeric-normalized structures, and generation variations for the same topic are avoided first to reduce number-swapped clones. If the topic has few available archetypes, the engine may eventually reuse a family with new data, but it will not intentionally repeat the exact question text.
- Multi-part scenario signatures are tracked separately. If repeated attempts cannot find a new scenario, the service reports that it could not produce a unique scenario instead of silently returning a known duplicate.
- Requests may ask for `question_type: "mixed"` to rotate multiple-choice, short-answer, and true/false questions within one set.
- Set-level fingerprint, structure, variation, and archetype checks remain active.

## Data location
The ledger is stored in the existing application SQLite database, using `MATHWEB_DB_PATH` when configured; otherwise it uses `backend/database/mathweb.db`. For online deployment, persist the configured database file/disk if anti-repeat history must survive redeploys.

## Important accuracy note
The generator is a local, rule-based mathematical question engine, not an external large language model. It creates parameterized questions from validated mathematical archetypes, so answers can be checked by the backend without requiring an API key. Its coverage and naturalness still depend on the implemented topic builders; every generated item is not equivalent to a teacher-reviewed official textbook question. Keep expanding and testing the bank topic by topic rather than claiming that generated questions are official or infallible.

## Tests
From `backend` run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q app
```
