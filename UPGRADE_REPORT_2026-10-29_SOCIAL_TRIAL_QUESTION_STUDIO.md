# MATH_WEB upgrade report · 2026-10-29

## Confirmed fixes

- Battle matchmaking: `/api/matchmaking/current` now returns top-level `match_id` and `status` as expected by the existing polling client, while preserving the nested `match` response for compatibility. This fixes the case where the second player was matched but the first player kept waiting forever.
- Friend and Battle Player ID lookup: SQLite comparisons use `COLLATE NOCASE`, so uppercase/lowercase input does not cause false “not found” results.
- User profile authentication helper: checks SQLite row column names rather than testing whether the string `id` is one of the row's values.

## Topic and game bank

- AI topic index: 150 topics, distributed as Math 10 = 49, Math 11 = 51, Math 12 = 50.
- Added 11 topics and 33 matching game pages. Game catalogue now contains 474 pages; three tiers are registered for each game-topic ID.
- Admin now exposes `/api/admin/library/hierarchy` and a Topic → Game → Question workspace.
- Questions can be added, edited, and deleted in the selected game panel. Question list API supports topic and game filters.
- File importer accepts JSON, CSV, TXT, Markdown, text-based PDF, DOCX, and XLSX, maps known topic/game metadata, routes ambiguous questions to a review list, and supports dry-run preview before committing.
- Admin question bank remains separate from the public source catalogue; saved bank counts are actual rows, not estimated content.

## Learner personalization

- Added `/api/users/me/learning-coach` and `/api/users/me/difficulty`.
- The practice page and dedicated trial-practice page display a study companion based on saved `game_results`, recommend reviewing weaker topics, and suggest a difficulty based on accuracy.
- User-selected difficulty is saved per account. Generated knowledge-game question requests read that account-specific preference. Trial sessions remain disposable `trial_*` accounts and are excluded from real-learner reports.

## Validation

- `python -m pytest -q`: 90 passed.
- `python build_individual_games.py`: passed; 474 game pages, 158 game-topic IDs including legacy aliases, three pages per ID, all paths present.
- JavaScript syntax checked for Admin inline script, learning-coach script, and inline scripts in both practice pages.

## Important limitation

The file-routing assistant is a local metadata/content matcher, not an Internet crawler or an external LLM. It can auto-route explicit or high-confidence topic/game metadata and flags uncertain cases for manual review. Scanned PDFs need OCR and are not parsed as text. Imported content should still be checked for mathematical correctness before being released to learners.
