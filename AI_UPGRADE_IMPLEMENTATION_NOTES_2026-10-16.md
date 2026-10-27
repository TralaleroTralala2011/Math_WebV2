# MATH_WEB AI and Geometry Implementation Notes

Date: 2026-10-16

## Changes in this build

1. Preserved the existing Practice/Game/Battle/Friends/Chat page structure and added functionality in the AI geometry layer rather than replacing the site's UI.
2. Added a normalizer that converts supported legacy question diagram payloads (`right_triangle`, `triangle_area`, coordinate `points`, dimensioned circles, tangents, and schematic pyramids) into the shared geometry representation. This prevents the renderer from silently using its old fixed-size triangle/circle art when numeric data is available.
3. Added stricter validation for empty, malformed, non-numeric, and inconsistent geometry payloads. Invalid diagrams are suppressed by the existing generation safety gate instead of being shown as valid geometry.
4. Rectangular-prism diagrams now retain exact 3D coordinates for all eight vertices in addition to their display projection. Dimension metadata remains separate from projected screen distances.
5. The existing geometry SVG renderer now uses retained 3D coordinates to render a rotatable wireframe for diagrams with 3D source coordinates. Rotation controls change yaw/pitch and offer reset. Rotating switches to a wireframe view so stale front/back edge styling is not falsely retained.
6. Added responsive, keyboard-focusable styles for the 3D controls without redesigning the existing practice interface.
7. Added regression tests for legacy diagram normalization, numeric validation, and exact rectangular-prism vertices.

## Verification performed

- `python -m pytest -q`: 70 passed.
- `python -m compileall -q backend`: passed.
- `node --check js/practise.js`: passed.
- `node --check js/api-config.js`: passed.
- JSON parsing for template-bank, topic index, problem-bank catalog, super-bank catalog, and game manifests: passed.
- Generator sweep across 94 curriculum topics × 3 difficulty levels × 3 answer types: 846 questions generated and validated; 270 carried diagrams; zero generation or diagram-validation failures in this sweep.

## Important scope notes

- The question engine is an internal rule/template/composer-based mathematical generator, not a connected general-purpose LLM. It can generate many varied questions within its implemented banks and rules, but it cannot guarantee arbitrary open-ended reasoning like ChatGPT for every possible prompt.
- 3D rotation is an interactive projected wireframe, not a full CAD/GeoGebra-style constraint editor. It does not automatically solve every possible solid-geometry configuration or calculate a mathematically unique 3D construction from arbitrary prose.
- When a problem does not uniquely determine a shape, the diagram remains schematic and must not be used as proof of unstated lengths, angles, or parallel/perpendicular relations.
- The automated tests are not a substitute for a final manual browser pass on the user's target Windows/browser setup and hosted backend configuration.
