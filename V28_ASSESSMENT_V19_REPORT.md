# MATH_WEB V28 Classic - V19 audit and scoring patch

- Source: `MATH_WEB_V28_CLASSIC_ASSESSMENT_V18.zip`
- Authored questions: **900/900**; complete and mapped topics: **150/150**.
- Structural validation: **PASS** (each topic has slots 1..6 with expected difficulty, context and format; answer/solution present).
- V254 B25 records: **4000**, SHA-256: `6f356f9bede0d79b75bd75a314050dc8bf202a3ccf53297c87dc377cfc26a6a4` (unchanged).
- Original MCQ correct positions: A=182, B=138, C=112, D=18; options now shuffled when displayed, while grading preserves original indices.
- Short answers accept equivalent fractions/decimals and arithmetic expressions, e.g. `2/5` and `0.4`, `2√13` and `sqrt(52)`.
- Numeric parser doesn't execute arbitrary JavaScript, and text answers are compared after normalization.
- **Independent mathematics review:** NOT DONE.
- **Independent pedagogy review and assessment calibration:** NOT DONE.
- **Two-account Battle / real-browser / 20-page E2E:** NOT RUN.
- Static and runtime scoring tests are included in `V28_ASSESSMENT_V19_TESTS.json`.

This patch retains V28 Classic HTML/CSS and does not alter existing V254 bank records. Structural integrity cannot certify content correctness.
