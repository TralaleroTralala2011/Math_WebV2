# MATH_WEB V46 - Safe base preservation and admin reset integration

BASE: Math_WebV2-main (1).zip supplied by user. All original files are retained unchanged, except two added files.

Added: backend/scripts/reset_admin_password.py from V45, verified compatible with the identical backend/app/admin_routes.py, backend/app/auth/routes.py and backend/database/database.py.

IMPORTANT: This is a targeted compatibility integration, NOT a claim that all bank content and every feature has been merged or 100% tested. Do not overwrite production databases or replace the user's stable UI.

For Render admin password reset, configure MATHWEB_ADMIN_RESET_PASSWORD (12-128 characters) privately on the actual Render service. Run the script in an authorized Render shell with access to its persistent database, not on local Windows. Then remove the environment variable. Never commit passwords to GitHub.

GitHub upload: unzip and copy the contents of Math_WebV2-main/ to repository root, preserving .git, then commit/push. Render must separately deploy the backend commit.

Before production: test user and admin login, persistence after restart, Battle two-client realtime, bank deduplication, learning routes, and mobile navigation.
