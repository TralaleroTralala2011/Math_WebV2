$ErrorActionPreference = 'Stop'
Write-Host '=== MATH WEB PREFLIGHT ===' -ForegroundColor Cyan
if (-not (Test-Path '.\backend\app\main.py')) { throw 'Missing backend/app/main.py' }
if (-not (Test-Path '.\practise.html')) { throw 'Missing practise.html' }
if (-not (Test-Path '.\js\api-config.js')) { throw 'Missing js/api-config.js' }
if (-not (Test-Path '.\backend\app\ai\engine\problem_generator.py')) { throw 'Missing problem generator' }
if (-not (Test-Path '.\backend\app\ai\engine\geometry_diagrams.py')) { throw 'Missing geometry generator' }
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
  python -m compileall -q .\backend\app
  if ($LASTEXITCODE -ne 0) { throw 'Python compile check failed' }
  python -c "import json, pathlib; [json.loads(p.read_text(encoding='utf-8')) for p in pathlib.Path('backend/app/ai/knowledge').glob('*.json')]; print('JSON OK')"
  if ($LASTEXITCODE -ne 0) { throw 'JSON validation failed' }
} else { Write-Warning 'Python was not found, so Python compile check was skipped.' }
$api = Get-Content '.\js\api-config.js' -Raw
if ($api -notmatch 'https://math-webv2\.onrender\.com') { throw 'Production API configuration is not math-webv2.onrender.com' }
if (Test-Path '.\.gitmodules') { throw '.gitmodules exists. Remove stale submodule metadata before pushing.' }
if (Get-ChildItem -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue) { Write-Warning 'Generated __pycache__ folders exist. They are ignored and will not be committed.' }
Write-Host 'PREFLIGHT PASSED' -ForegroundColor Green
