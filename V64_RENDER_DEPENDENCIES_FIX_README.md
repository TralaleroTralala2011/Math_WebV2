# MATH_WEB V64 · Render dependency deployment fix (2026-11-15)

## Screenshot diagnosis

Render deployment fails during `backend/app/main.py` import:

```
ModuleNotFoundError: No module named 'cryptography'
```

The Admin encrypted backup module imports `cryptography.hazmat.primitives`.
The backend/requirements.txt already includes `cryptography>=42` and
`python-multipart>=0.0.9`, but the repository-root requirements.txt did not.

## Patch

- Append `cryptography>=42` and `python-multipart>=0.0.9` to root requirements.txt.
- Preserve all original root dependencies, backend dependencies, source files,
  question bank, Word files, user database, and Render configuration.
- No business logic or user-facing UI changes.

## Render (service with Root Directory empty)

Dashboard → math-webv2 → Settings → Build & Deploy:

**Root Directory:** empty (repository root)

**Build Command**:

```sh
python -m pip install -r requirements.txt && python -m pip check && python -c "import cryptography, multipart; print('Admin backup dependencies OK')" && python scripts/restore_v254_bank.py
```

**Start Command** (keep existing working choice, or use):

```sh
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT
```

**Health Check Path**: `/health`

If using the repository `render.yaml` Blueprint instead, its build command
already installs `backend/requirements.txt`, which contains both dependencies.
If your deployed service still fails after V64, review the *build logs* to check
which requirements file Render actually installs. Changing `render.yaml` does
not necessarily override commands set on an existing Dashboard-managed service.

Do not delete/recreate your database, persistent disk, or environment variables
for this fix. Never share backup encryption passphrases or credentials in logs.

## Local checks

- ZIP CRC check and source-entry parity.
- Python import smoke test for `cryptography`, multipart, and FastAPI app.
- No live Render deployment performed by the patch process.
