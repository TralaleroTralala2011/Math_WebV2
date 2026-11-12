# MATH_WEB: verified partial update (04/11/2026)

**Source:** MATH_WEB_ACCOUNT_NOTIFICATION_BATTLE_UPGRADED(2).zip. All existing application files retained.

## Changes in this delivery
- START_MATH_WEB.bat: starts existing backend (including admin routes) and frontend, uses local .venv if present, checks whether ports are already serving, waits for both HTTP endpoints, then opens index.html.
- scripts/wait_and_open.py: startup readiness check.
- scripts/audit_question_bank.py: read-only question import audit for missing fields, exact text duplicates, four-option structure, duplicate options, and mismatched answer values.

## NOT complete or certified
- 149,000 verified, independently sourced and licensed mathematical questions have NOT been collected/imported.
- Semantic mathematical correctness, topic match, multiple mathematically equivalent correct options, and 100% anti-repetition are NOT guaranteed by structural checks.
- The five reported user-facing bugs, Battle two-account flow, and personalization require further implementation and live testing.
- This archive is a partial upgrade, not a 100% completed release.

## Data handling
- Original database files are excluded from this distribution to avoid sharing real user records. Back up the original DB and retain it separately when deploying.
- Existing source tree remains otherwise intact.
