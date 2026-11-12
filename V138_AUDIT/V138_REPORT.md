# MATH_WEB V138 checkpoint

Source: V137; runtime website code unchanged.

Corrected false alarm for mathematically equivalent complex answers by SymPy symbolic subtraction. The V133 case `10*I*(-1 + I)` equals `-10 - 10*I`. Unsupported expressions are counted separately, not certified.

Audit: {"counts": {"method_files": 5, "candidates": 68, "question_files": 5, "questions": 680, "constant_answer_methods": 1, "linked_methods": 68}, "issue_count": 0}

Tests: ....
----------------------------------------------------------------------
Ran 4 tests in 0.089s

OK

No new candidate methods or questions; no independent mathematical method certification. Full website regression not completed in this run.
