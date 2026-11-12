# Geometry AI upgrade

This additive update introduces `backend/app/ai/engine/geometry_curriculum.py` and routes supported geometry topics through it before the existing Super Bank / Extended Bank fallback. It does not change HTML, CSS, page layout, or game UI.

## Design
- Three levels map to the existing API difficulty values: `easy` = Cơ bản, `medium` = Trung cấp, `hard` = Nâng cao.
- Grade 10 focuses on triangle metrics, vectors, coordinate geometry, lines, circles and introductory conics.
- Grade 11 focuses on plane transformations, parallel/perpendicular relations, spatial reasoning and sections.
- Grade 12 focuses on Oxyz vectors, lines and planes, spheres, distances and volumes.
- Generated questions are original curriculum-aligned variants, not verbatim copies of SGK/SBT pages. The JSON catalog lists skill coverage and quality rules.

## Files changed
- `backend/app/ai/engine/geometry_curriculum.py` (new)
- `backend/app/ai/engine/generator.py` (additive import and fallback hook)
- `backend/app/ai/knowledge/geometry_curriculum_catalog.json` (new)

Existing legacy question/game banks remain in place.
