# MATH_WEB V34 · Pilot Deployment QA (13/11/2026)

## Files
- Input: `MATH_WEB_V28_CLASSIC_V33_GITHUB_RENDER_MOBILE_FIX.zip`
- Release: `MATH_WEB_V28_CLASSIC_V34_GITHUB_PILOT_QA.zip`
- ZIP size: 64.00 MiB
- ZIP integrity: PASS
- Original source files unchanged: 1971
- Original source files intentionally modified: 16
- New files (including bank compression, QA tests and deployment docs): 7

## What was fixed
1. `study-suite.html`, `curriculum-studio.html`, `final-features.html` and other feature pages now load the canonical API configuration.
2. `js/study-suite.js`, `js/learning-progress.js`, `js/curriculum-studio.js` and inline final features script use `MATHWEB_API_URL`, not GitHub Pages as an API origin.
3. Public deployment ignores untrusted API URLs saved in localStorage (protects bearer tokens).
4. Database can be recreated from a Git-committable 12 MiB seed zip during Render build, exact checksum and record counts tested, keeping generated SQLite ignored by Git.
5. Render pilot blueprint includes persistent disk variables for user data; secondary learning/exam/progress databases respect `MATHWEB_DATA_DIR`.
6. GitHub Pages build now runs full backend regression and preflight and excludes backend/SQLite/private files from public artifact.
7. Production bootstrap admin password is never printed; initial secret is supplied via `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` in Render Environment.

## Tests actually run
| Check | Result | Scope |
|---|---|---|
| Complete pytest backend suite | **240/240 PASS** | Source/backend regression, tests run in isolated SQLite |
| Focused deploy/account/two-user regression | **10/10 PASS** | Overlaps the full 240; not additional unique tests |
| SQLite restore from seed, sha comparison | **PASS** | Raw DB replaced from source compressed ZIP; exact SHA match |
| V254/B54 SQLite PRAGMA quick_check | **PASS** | 83,298 candidate records; 95,514 labels |
| Preflight assets and routes | **PASS** | 20 HTML pages; 536 local references; 157 API registered routes |
| Node JS syntax | **40/40 PASS** | Root `js/` files |
| Static Chromium CSS rendering | **40/40 no overflow/errors** | 20 pages at mobile 390x844 and desktop 1440x900, static DOM without application JS or actual API |
| ZIP integrity / critical JS hash | **PASS** | Battle/Chat/Practice/AI service behavior sources unchanged |
| Real GitHub Pages and Render live deployment | **NOT VERIFIED** | This environment could not access user deployments; not pushed by assistant |
| Real 2-device E2E Battle/Chat/login | **NOT VERIFIED** | Backend integration tests not a substitute for real browsers |
| Independent mathematical/school review of B54 | **NOT DONE** | 95,514 labels ≠ independently certified exercises |

## Release readiness and risk

**Source smoke/regression tests pass. This is NOT a guarantee of zero errors after deployment.** 

- **Frontend/backend deploy synchronization**: update BOTH from the same commit. The Render service URL in `js/api-config.js` must be the service that actually runs this backend.
- **Pilot data persistence**: existing default Render filesystem is ephemeral. Attach a paid persistent disk at `/var/data` or use a supported managed persistent database BEFORE collecting student records. The V34 `render.yaml` specifies `plan: starter` and a disk, which can incur charges; do not create/upgrade a paid service without reviewing cost.
- **Data migration**: copying source files does not migrate the old Render user database. Backup and restore any existing accounts/results from the previous backend before activating new `MATHWEB_DB_PATH`; the pipeline does not migrate old data automatically.
- **Confidentiality**: avoid adding real students' names, scores, phone numbers or account secrets to the GitHub repository or to this ZIP. Collect only consented data needed for the pilot.
- **Real deployment**: `python scripts/check_live_deploy.py` runs non-destructive smoke tests after deployment. Then test with two dummy accounts and a backend restart before any research data collection.

Details: `MATH_WEB_GITHUB_READY/DEPLOY_GITHUB_RENDER_V34.md` inside the ZIP.

## Changed original files
- `.github/workflows/pages.yml`
- `.gitignore`
- `backend/app/admin_routes.py`
- `backend/app/final_features_routes.py`
- `backend/app/learning_progress_routes.py`
- `backend/app/study_suite_routes.py`
- `curriculum-studio.html`
- `final-features.html`
- `geometry-lab.html`
- `geometry-learning.html`
- `js/api-config.js`
- `js/curriculum-studio.js`
- `js/learning-progress.js`
- `js/study-suite.js`
- `render.yaml`
- `study-suite.html`
