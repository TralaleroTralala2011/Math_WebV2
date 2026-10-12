# MATH WEB unified game build

This build consolidates the AI multipart problem engine with a shared play-loop upgrade across the individual game pages and the universal game.

## Unified play rules

- Difficulty picker controls are removed from individual game pages. The game chooses its question-generation mode internally.
- A correct answer adds 5 progress points. A wrong answer subtracts 1 point, with a floor of 0 and a cap of 100.
- The progress bar is the live score out of 100. Reaching 100 ends the round and opens the congratulations screen.
- Every submitted answer locks the question and shows the answer plus solution before a visible **Câu tiếp theo** button is used. There is no forced five-second advance.
- Question sessions continue in batches until progress reaches 100. Batches alternate standalone questions and multipart problems; question types can include multiple choice and short answer/fill-in.
- Geometry questions render their structured diagram data as SVG when the AI supplies a diagram. Point labels, line segments and measurements are read from the problem data rather than using an unrelated stock image.
- Per-game best progress, best correct count, aggregate answer totals and completed rounds are stored in browser `localStorage` so the achievement survives leaving the page or restarting the browser on that device.
- The completion screen includes animated celebration, congratulations text and a record of the round.
- Individual game pages keep their own existing files, topics, names, and game-specific generation configuration; this upgrade does not collapse them into one page.

## AI generation

The existing AI question service and multipart problem generator remain in place. The game frontend alternates standalone question batches with multipart problem batches and passes recent question metadata back as history to reduce repetitive structures. Multipart context, part labels, solutions, answer types and structured geometry diagrams are retained for display.

## Local validation performed

- Python regression tests in `backend/tests/test_problem_generator.py`: 4 tests passed.
- JavaScript syntax checked with `node --check` for all inline scripts on the 321 standard game HTML pages: no syntax errors.
- `games/universal/game.js` checked with `node --check`: passed.
- The 321 standard game HTML pages no longer contain the old `.levels` selector row. The universal game also hides its old difficulty label and uses the unified progress rules.

## Notes

The achievement is saved per browser/device using `localStorage`; it is not a server-wide profile statistic. The diagram renderer can only draw a geometry diagram when the question response contains structured diagram data. Production API behaviour still depends on the deployed backend being online and serving the updated AI routes.
