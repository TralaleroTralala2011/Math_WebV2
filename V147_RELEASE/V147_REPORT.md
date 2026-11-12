# MATH_WEB V147: Research batch integrity

Base: V146 ZIP, extracted without altering original SQLite data. Added a reusable V141 research batch audit to detect duplicate question IDs, duplicate method IDs, duplicate question stems across different methods, orphan questions, empty stems, and wrong question counts. Added numeric-template diagnostic. Numeric reparameterizations are NEVER counted as new independent methods. This audit is structural and cannot prove mathematical independence.

Actual V141 candidate batch: 11 method candidates, 110 questions; structural issues: 0. Certified independent methods added: 0; published qualified questions added: 0. Existing pending candidates remain pending. No changes to production bank or SQLite.

Tests: 4/4 new V147 integrity tests passed; 15/15 selected backend certification tests passed. Full backend and Battle/Admin browser E2E not run. Existing math-oracle claims are inherited from V141, not revalidated in this run.

Next: Expert semantic-method comparison across all catalogs, independent math verification, production integration only after certification; broad backend and browser E2E tests. Target 300,000 independent types and 3,000,000 verified questions not met.
