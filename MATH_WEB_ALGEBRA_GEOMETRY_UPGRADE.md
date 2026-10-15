# MATH_WEB Algebra + Geometry AI Upgrade

## Base and compatibility
- Base project: `MATH_WEB_FRIENDS_CHAT_BATTLE_UPGRADED.zip`.
- Changes are additive and confined to backend AI generation/validation and backend tests/documentation.
- Existing frontend HTML, CSS, and JavaScript files were not redesigned or modified. Practice, game, Friends, Chat, notifications, account, and Battle UI remain as in the base ZIP.

## Algebra improvements
- Added higher-reasoning algebra archetypes to existing game-specific question generation: parameterized line membership, line intersection, quadratic factorization/root reasoning, discriminant-based root classification, compound inequalities, arithmetic-sequence sums, rational-expression simplification with domain restrictions, and radical equations.
- Advanced archetypes are selected more often for internal `hard`, `expert`, and `hell` levels. Existing user-facing three-level labels are not changed.
- Corrected a numeric true/false statement whose truth marker did not match its wording.

## Geometry improvements
- Added a computed right-triangle altitude diagram. The foot of the altitude is calculated by orthogonal projection, then checked against the base and perpendicularity constraints.
- Added a two-tangent circle diagram with exact tangent points, circle membership, and radius/tangent perpendicularity checks.
- Added an intermediate multi-step triangle-altitude question combining Pythagoras and two area formulas.
- Added an advanced external-tangents question combining right triangles, tangent chord geometry, and area.
- Added expert/Olympiad-style geometry tasks for intersecting chords, Heron area, line-circle tangency with a parameter, quadratic parameter analysis, and point-to-plane distance.
- Added a final diagram validation gate in the question generator. If a diagram from any bank fails validation, it is suppressed rather than sent to the UI; diagnostic metadata is retained.
- Added rational formatting for graph vertex values to prevent a latent `NameError` in the advanced parabolic graph generator.

## Verification
- Full backend test suite: **64 passed**.
- Geometry stress run: **2,100 generated questions** across representative grade 10-12 geometry topics and five internal difficulty labels; **420 expert/Olympiad archetype results** were observed and **0 diagram validation issues** were found in this run.
- ZIP integrity and post-extraction tests are checked during packaging.

## Scope note
Automated tests and sampled generation do not prove every possible generated question is mathematically perfect or guarantee that all future questions are unique. The project still contains legacy and fallback generation paths, so ongoing topic-by-topic review remains valuable.

## Run tests
From the `backend` folder:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```
