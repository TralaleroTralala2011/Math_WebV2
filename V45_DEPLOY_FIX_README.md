# V45 Render/GitHub deployment dependency patch

- Added sympy to all bundled Python requirements variants.
- Render blueprint now verifies installed dependencies before startup.
- GitHub workflows now verify sympy imports before testing.

IMPORTANT: Render dashboard settings can override render.yaml. Verify Root Directory, Build Command, and Start Command in Render Settings. For root repository deployment, use `python -m pip install -r backend/requirements.txt && python -m pip check && python scripts/restore_v254_bank.py` as build command and `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT` as start command. For nested root MATH_WEB_GITHUB_READY, ensure correct path.

GitHub Action failures need exact job logs to diagnose; this patch does not certify their resolution. Preserve persistent data disk. Do not commit passwords.
