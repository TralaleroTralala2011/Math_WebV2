# MATH WEB Question Engine: three learning tiers

- **Sơ cấp** (`learning_tier=foundation`): grade-specific school curriculum and textbook-aligned original exercises.
- **Mở rộng** (`learning_tier=provincial`): multi-step reasoning, non-routine applications and provincial gifted-student preparation.
- **Chuyên sâu** (`learning_tier=national`): proof, parameters, synthesis and olympiad-style extensions.

The API translates these tiers to controlled generator levels (`easy`, `expert`, `hell`) and returns the tier label. The generator remains deterministic for answer correctness; open-response grading normalizes equivalent forms rather than relying on an unconfigured external LLM. The question generator must be configured with a real model provider before claiming external-LLM grading.

## Quality gates
- Topic ID and grade are preserved from the selected game.
- The coordinate-midpoint topic has a dedicated generator with midpoint, point distance, missing endpoint, section ratio, parameter and olympiad archetypes.
- Individual game pages load `js/api-config.js` correctly; the malformed nested `<script>` injection was repaired where found.
- When the backend is unavailable, the coordinate-midpoint game now has a topic-specific local fallback instead of generic arithmetic.
