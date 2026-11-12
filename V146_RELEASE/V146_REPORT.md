# MATH_WEB V146: stricter certificate eligibility

Base: latest accessible V145 ZIP. Fixed a measurable integrity issue: previously an approved certificate with any nonempty JSON object, including `{"x":1}`, advanced independent-type and qualified-question milestone counters even though V145 already flagged missing method comparison.

Now milestone counters require structured `compared_method_ids` array and an `independence_reason` text of at least 20 characters, in addition to existing reviewer, approval, and JSON checks. The rule applies consistently to global and per-topic progress. This is a structural gate only: it does NOT establish mathematical independence or replace human review.

Regression: 23/23 V14x tests and 33/33 V13x+V14x tests passed. Full backend, browser Battle/Admin E2E not run. Existing SQLite untouched. Newly certified independent types: 0. Newly published questions: 0. Existing 11 research candidates and 110 questions retained as pending.

Next: independently review candidates against mathematical methods, improve semantic deduplication, run full backend suite and Battle/Admin browser tests. No claim of 300,000 independent types or 3,000,000 qualified questions.
