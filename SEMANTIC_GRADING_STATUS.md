# MATH_WEB semantic grading incremental update

- Improves the existing backend answer comparison used by AI practice: scalar `x=2` versus `2`, coordinate `(x,y)=(7;5)` versus `(7;5)`; rejects wrong variable or reversed coordinates.
- Regression tests added; full backend suite: 106 passed, 4 FastAPI deprecation warnings.
- Preserves all other files in the prior Study Center ZIP unchanged.
- This is NOT a complete AI essay grader. Does not complete 2,000+ unique types per topic, verified lessons for every topic, production performance, or all end-to-end workflows.
