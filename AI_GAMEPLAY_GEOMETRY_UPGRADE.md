# MATH WEB AI + GAMEPLAY + CIRCLE GEOMETRY UPGRADE

## Base preservation
- Based on the uploaded `MATH_WEB_FINAL_GEOMETRY_TOPICS_VISIBLE.zip` project.
- Kept the existing practice page structure, account/auth pages, battle page, and game page layout.
- Did not replace the project with a new UI.

## Three distinct game interactions per current knowledge topic
The archive currently contains **92 knowledge topics and 276 individual HTML game pages**. Each topic's numbered game pages now select a different interaction pattern:
1. `1-*`: easy, multiple-choice discovery.
2. `2-*`: medium, typed-answer mission.
3. `3-*`: hard, linked multi-part boss challenge.

This changes gameplay/input mechanics while retaining the existing page structure and score/feedback/completion components. It does not yet expand the current 92-topic catalog to 135 topics; that larger catalog requires a separate curriculum and AI-topic mapping pass rather than creating topics that silently map to unrelated generators.

## AI question engine improvements
- Expanded the Grade 10 `duong_tron` question bank to cover circle equations/center/radius, central and inscribed angles, a triangle inscribed in a circle, Thales' theorem when a triangle side is a diameter, a rectangle inscribed in a circle, diagonal/side calculations, area, and maximum-area proof.
- Added level-aware families and game-aware routing so the circle games can receive questions about the intended circle subtopic.
- Added a dedicated multi-part `circle_geometry_challenge` problem archetype for the third game, alternating between an inscribed rectangle and an inscribed triangle. Each problem links four parts to one coherent set of data.
- Added structured diagram types for an inscribed rectangle and an inscribed triangle in the practice renderer and the individual game renderers.
- Expanded the geometry curriculum catalog and quality rules to require mathematical consistency and proof of the maximum-area condition.
- Kept the server-side answer checking, anti-repeat history, and existing AI question banks.

## Verification
- `python -m pytest -q`: **34 passed**.
- `node --check js/practise.js`: passed.
- Parsed **552 inline scripts** across the 276 individual game pages with `node --check`: **0 syntax errors**.
- Verified all **92 knowledge folders** have exactly **3 HTML game pages** (276 total).
- Generated test sets for circle easy/medium/hard and verified the multi-part circle boss problem returns four linked parts with answers and solutions.

## Scope notes
- These checks are local source-code checks, not a guarantee that an external deployment or every browser/device works identically.
- The existing topic catalog remains at 92 topics in this build. The previously discussed 135-topic/405-game target is not claimed as completed in this archive.
- The AI is a deterministic generator with verified templates and banks, not a live external LLM connection. This design prioritizes answer correctness and repeat resistance; future bank expansion should add more validated archetypes instead of merely randomizing numbers.
