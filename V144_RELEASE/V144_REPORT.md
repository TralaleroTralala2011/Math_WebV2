# V144: certificate evidence integrity and legacy test alignment

Base: MATH_WEB_GITHUB_READY_V143_CERTIFICATE_ELIGIBILITY.zip.

Changes: normalize valid JSON evidence before checking for empty objects, so whitespace-only `{ }` cannot be accepted as a nonempty certification record. Correct three obsolete V141 tests to reflect V143 eligibility rules. Add seven parameterized evidence tests.

Tests: 15/15 focused V141-V144 tests passed. Broader backend regression was attempted but did not finish within execution budget; its partial log contains six setup errors and cannot be marked passing. No full browser E2E. No independent mathematical forms certified; no new questions published. Retain 11 research candidates and 110 research questions as unapproved.

Important: nonempty JSON evidence alone does NOT prove method independence. A trusted reviewer and actual mathematical comparison remain required.

Next: investigate six regression setup errors; run full suite with explicit environment; audit Battle/Admin; independently review V141 research candidates; preserve existing SQLite files.
