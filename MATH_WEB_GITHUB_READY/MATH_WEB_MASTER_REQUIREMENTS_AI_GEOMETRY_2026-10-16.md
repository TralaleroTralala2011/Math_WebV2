# MATH_WEB - Master requirements: 45 geometry topics, diverse AI questions, and verified geometry diagrams

Date: 2026-10-16  
Base archive: `MATH_WEB_FRIENDS_CHAT_BATTLE_AI_GENERATION_3D_GEOMETRY_COMPLETE.zip`  
Scope: additive upgrade to the existing project. This is not a replacement project.

## 1. Non-negotiable compatibility requirements

- Preserve the existing Practice/Practise, Game, Battle, friend, and chat experiences and their existing page structure and behavior.
- Do not redesign or remove existing UI as a side effect of the AI upgrade.
- Integrate AI question generation and diagrams into the existing backend/API and the existing practice/game/battle flows.
- Keep current routes, authentication, social features, and existing games working.
- A topic is not complete merely because its name appears in a catalogue: it must map to content generation and relevant game/practice integration.

## 2. Geometry topic target and honest counting

The requested target is 147 topics in total: 102 existing topics plus 45 new geometry topics before duplicate removal. The 45 additions must be distributed exactly as follows:

| Grade | Foundation (Nền tảng) | Intermediate (Trung cấp) | Advanced (Nâng cao) | New geometry topics |
|---|---:|---:|---:|---:|
| 10 | 5 | 5 | 5 | 15 |
| 11 | 5 | 5 | 5 | 15 |
| 12 | 5 | 5 | 5 | 15 |
| **Total** | **15** | **15** | **15** | **45** |

Audit the new topics against all existing catalogues by normalized name, aliases, skills/subtopics, and mathematical meaning. Do not delete a topic solely because its name is similar; record decisions about overlaps. Do not claim 147 unless the audited, deduplicated, canonical topic catalogue actually contains 147 valid topics.

### Count found in this source archive

The current `backend/app/ai/knowledge/index.json` contains 139 records: Grade 10 = 45, Grade 11 = 47, Grade 12 = 47. It includes 45 records marked by the ID prefixes `g10_geom_`, `g11_geom_`, and `g12_geom_`. Thus this archive's current index does **not** prove the claimed baseline of 102 existing topics: 94 non-expansion records + 45 additions = 139 records. Eight baseline topics are not accounted for by this index compared with the requested 102. Keep this discrepancy open until the other historical/current catalogue sources are reconciled. Do not invent eight placeholder topics to inflate the count.

## 3. AI question generation requirements (B1)

### Diversity

- Generate materially different problem archetypes within a topic, varying the task, given data, requested result, context, reasoning method, and representation, not just changing numbers in a fixed sentence.
- Support calculations, interpretation, proof, reasoning, conditions, function/graph analysis, parameters, optimization, and multi-concept synthesis when appropriate to the grade and topic.
- Include realistic applied problems only when the context naturally matches the mathematics and the data are coherent.
- Allow generation by grade, topic, difficulty, question type, requested step depth, and supported game context.
- Support multiple-choice, short-answer/written response, and true/false question types.

### Solutions

- Provide a clear sequence of steps and explain the formula, theorem, or method used.
- Check domains, assumptions, admissible roots, special cases, units, and the interpretation of real-world results where applicable.
- Proof questions require a logically sufficient argument; do not skip a decisive inference.
- Offer alternate methods only when they are mathematically valid and useful.

### Validation gate

- Reject incomplete or contradictory prompts, missing answers/solutions, invalid MCQ options, mismatched answers, and malformed true/false payloads.
- MCQ must have four distinct options and the keyed answer must be one of them.
- Written response must have a checkable answer or explicit grading/verification criteria.
- Where feasible, verify arithmetic/algebra independently with deterministic code or a symbolic/numeric method.
- If verification is inconclusive, label the item as unverified or withhold it from automatic competitive play; never silently claim it is verified.
- Track exact fingerprints and structural/archetype history to reduce repeats across sets and sessions.

### Difficulty semantics

- **Nền tảng:** concepts, core formulas, direct calculations, and simple applications.
- **Trung cấp:** multi-step application and interpretation of data.
- **Nâng cao:** synthesis, deeper reasoning, parameters, extrema, and nontrivial proof.
- **Địa ngục/Olympic:** a separate optional challenge tier requiring an original insight and rigorous reasoning. It must not merely use larger numbers or longer arithmetic.

Difficulty must be based on reasoning demand, not cosmetic wording or number size. Adaptive difficulty is optional and must not override a learner's explicit level selection without clear product behavior.

## 4. Intelligent mathematical diagram requirements (C1)

### Coverage

- 2D: triangles and notable lines, quadrilaterals/polygons, circles/chords/tangents/secants/angles, parallel/perpendicular/intersecting/concurrent lines, transformations, vectors, loci, conics, and coordinate geometry.
- 3D: pyramids, prisms, cuboids/cubes, polyhedra, sections, line-plane relationships, angles/distances/projections, spheres, and Oxyz where relevant.
- Graphs/coordinates: Oxy/Oxyz points, lines, circles, functions/conics, intersections, vectors, projections, and surfaces when supported.

### Structured interpretation and geometry truth

- Parse named points/objects, coordinates, lengths, angles, incidence, parallelism, perpendicularity, tangency, intersections, target objects, and constraints before drawing.
- Build the figure from structured coordinates/constraints using deterministic geometry functions where possible, not from an unvalidated AI-generated picture.
- Respect explicit coordinates, lengths, angles, right-angle vertices, tangency, and incidence. Labels and measurements must match the prompt.
- For 3D, preserve the underlying vertices/relationships separately from their 2D projection; distinguish visible/hidden edges where supported.
- If the data underdetermine a unique figure, render only a configuration consistent with the stated constraints and label it as schematic. Never infer an unstated theorem from appearance.
- If constraints are inconsistent or parsing is uncertain, suppress the misleading diagram or show a clear unavailable/ambiguous state.
- Label layout may change for readability, but geometry coordinates/constraints must not be distorted for aesthetics.

### Interactive support

Where supported and without changing the locked UI, allow zoom/pan, 3D rotation, toggling labels/auxiliary objects, highlighting referenced objects, construction steps, and parameter-driven updates. Unsupported interaction should not be represented as complete.

## 5. Required integration and acceptance tests (C2)

- All 45 added topics appear under the correct grade and level and are addressable by the existing API.
- Every new topic maps to relevant question generation; geometry-specific prompts use a diagram builder compatible with the actual prompt data.
- Practice, games, and Battle receive topic-correct questions and matching diagrams; no stale diagram from a previous question.
- Validate answer/solution consistency and each question-type schema.
- Test 2D metric geometry, right triangles, circles/tangents, coordinate data, 3D solids/sections, parameter changes, close labels, underdetermined cases, and contradictory cases.
- Regression-test existing authentication, Practice, Battle, friends, chat, and games. Keep a record of any browser/manual checks not yet completed.

## 6. Current implementation status and limitations

Present in this source archive: a 139-record topic index with 45 prefixed geometry additions; question generation service; multiple-choice/short-answer/true-false schemas; persistent duplicate history; geometry-diagram builders and renderer support; regression tests.

Verified in this packaging pass: backend test suite run from `backend/` (72 tests passed). The suite includes topic distribution, generator, diagram and API integration tests.

Not claimed complete: an unrestricted general-purpose LLM equivalent to ChatGPT is not connected by this rule/template/composer generator; universal arbitrary-prose-to-geometry constraint solving is not implemented; the interactive 3D view is a projected wireframe rather than a full GeoGebra/CAD constraint editor; 45 independent custom game engines have not been demonstrated; full manual browser regression of all social/game flows remains required. These are explicit remaining work items, not hidden assumptions.

## 7. Release gate

Release only with: canonical topic audit; no unexplained count inflation; passing backend/JS/manifest checks; topic-correct question/diagram tests; and a manual smoke test of the preserved pages. Any failed or unverified condition must be listed in the release notes.


## Addendum 2026-10-16: Game catalog integration

The current UI catalog originally exposed 102 game topics (306 individual pages). The 45 new geometry topics must be integrated into Practice as well as AI. The latest integration adds 45 Practice knowledge cards and 135 individual game pages, giving a target/current manifest of 147 topics and 441 pages. See `MATH_WEB_45_GEOMETRY_GAME_INTEGRATION_REPORT_2026-10-16.md` and `MATH_WEB_10_GEOMETRY_END_TO_END_TEST_CASES.md`. Passing catalog and unit tests is not evidence of full manual browser verification or perfect topic-specific question/diagram correctness.
