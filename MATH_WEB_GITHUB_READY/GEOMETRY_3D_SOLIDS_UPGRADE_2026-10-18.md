# MATH_WEB: Geometry diagram engine extension (2026-10-18)

## Added diagram builders
- `regular_prism_projection(sides, radius, height)`: computed regular right prism with 3D vertex metadata for triangular, square, pentagonal, hexagonal and other supported regular-prism bases (3–12 sides).
- `triangular_prism_by_dimensions(a, b, c, length)`: triangle base is computed from side lengths using the cosine law; invalid triangle inequalities are rejected.
- `pyramid_by_base_height(sides, radius, height)`: computed regular pyramid for bases with 3–12 sides.
- Existing cylinder, cone, sphere, cube, rectangular prism and generic spatial-point projection functions are retained.

## Accuracy policy
- Keep exact 3D coordinates and solid dimensions in the diagram payload.
- 2D views of 3D solids are explicitly labelled oblique/schematic; projected edge lengths are not treated as true lengths.
- Reject invalid dimensions and impossible triangle side lengths rather than drawing an arbitrary shape.
- Labels and edge topology are computed from vertices, not a decorative generic icon.

## Verification
- Added tests for prism/pyramid vertex counts, dimension metadata, invalid inputs and diagram validation.
- `python -m pytest tests/test_additional_solid_diagrams.py tests/test_geometry_diagrams.py -q`: 28 passed.

## Important scope note
This extension adds and tests geometry primitives in the backend drawing engine. It does not claim that every existing AI question/topic has already been routed to these new primitives, nor that every legacy diagram issue is fixed. Topic-to-diagram routing and exact per-question validation remain necessary integration work.
