# MATH_WEB geometry drawing patch report (2026-10-14)

## Scope
Additive correction to geometry diagram construction and AI diagram rendering. Existing practice, game, battle, authentication, and account UI has not been redesigned.

## Fixes
1. Triangle altitude AH is explicitly drawn as a dashed auxiliary segment, with H on BC and a valid right-angle marker.
2. Triangle median AM terminates at the actual midpoint M of BC.
3. Triangle angle bisector AD places D using the angle-bisector theorem ratio BD/DC = AB/AC.
4. Circle problems that state diameter AB now carry a radius of half the diameter and explicit A, O, B geometry metadata.
5. `js/practise.js` renders dashed segments and chooses an actually perpendicular pair for right-angle markers.

## Validation
- `python -m pytest -q`: 43 passed.
- `node --check js/practise.js`: passed.
- Visual browser QA remains necessary before deployment.
