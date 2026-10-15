# MATH_WEB upgrade notes: exact diagrams, difficulty modes, notifications

## Changes in this revision
- Coordinate graph builder now parses a line defined by slope and a named point, for example `m=-1` through `P(0;4)`, and plots the actual line on Cartesian axes with the exact labeled point.
- Standard-form lines `ax+by+c=0` are plotted, including point-to-line distance questions. Named coordinate points are marked at their supplied coordinates; point-only coordinate questions no longer get a fake horizontal segment.
- Question-specific diagram data takes precedence over stale generic template drawings for explicit geometry/coordinate prompts. Existing plane and spatial diagram renderers remain available.
- Added the `Địa ngục` difficulty alias (`hell`) as a fifth tier. Difficulty selected in the setup remains fixed for the set instead of silently being changed by learner history. The generation banks route this tier through the highest available reasoning builders and wider parameter ranges.
- The AI question setup offers all four requested formats: multiple choice, true/false, short answer, and mixed/all (default). Mixed mode rotates among the three supported answer formats.
- Opening AI setup closes the underlying topic/game-information popup first while retaining the selected topic for generation.
- Notifications use a narrow, full-height panel on desktop and a separate full-screen-ish sheet on mobile.
- Added regression tests for slope-and-point graph data, implicit line equations, and the `hell` difficulty alias.

## Automated validation
Run from `backend/`:
- `python -m pytest -q`
- `python -m compileall -q app ai`
- `node --check ../js/practise.js`
- `node --check ../js/notification.js`
- `node --check ../js/battle.js`
- `node --check ../js/chat.js`

Latest validation during packaging: **55 tests passed**, Python compilation passed, and the four JavaScript syntax checks passed.

## Important accuracy note
The diagrams use exact coordinates when they can be parsed from the question or structured generator data. The question engine does not yet mathematically parse every possible free-form Vietnamese geometry prompt, and the `Địa ngục` label does not certify that every generated item meets national or international olympiad standards. Browser-based visual QA and further topic-by-topic mathematical verification remain necessary before claiming every possible case is complete.

## Compatibility
The locked practice/game/battle layouts were not redesigned. Changes are limited to AI setup behavior, graph/diagram selection and rendering data, difficulty mapping, and the requested notification-panel layout.
