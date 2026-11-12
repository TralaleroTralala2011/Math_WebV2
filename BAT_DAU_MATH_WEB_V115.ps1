# MATH_WEB V115: local-only Windows Docker launcher; GitHub authentication not required.
# Run in PowerShell: powershell -ExecutionPolicy Bypass -File .\BAT_DAU_MATH_WEB_V115.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host 'Chua co Docker Desktop: cai dat Docker Desktop va khoi dong no truoc.' -ForegroundColor Red
    exit 1
}
try { docker info --format '{{.ServerVersion}}' | Out-Null } catch {
    Write-Host 'Docker Desktop chua chay. Hay bat Docker Desktop.' -ForegroundColor Red
    exit 1
}
if ($LASTEXITCODE -ne 0) { throw 'Khong the ket noi Docker daemon.' }
if (-not (Test-Path .env)) {
    # Secure random secrets, not fixed demo passwords. Never print them in terminal logs.
    $bytes = New-Object byte[] 48
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $token = [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+','-').Replace('/','_')
    $bytes2 = New-Object byte[] 48
    $rng2 = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng2.GetBytes($bytes2) } finally { $rng2.Dispose() }
    $pass = [Convert]::ToBase64String($bytes2).TrimEnd('=').Replace('+','-').Replace('/','_')
    @("QF_ADMIN_TOKEN=$token", "MATHWEB_BOOTSTRAP_ADMIN_PASSWORD=$pass", 'MATHWEB_WEB_PORT=8080') |
        Set-Content -Encoding ASCII .env
    Write-Host 'Da tao .env bang secret ngau nhien. Luu tru an toan, khong chia se.'
}
Write-Host 'Kiem tra docker compose...'
docker compose -f docker-compose.mathweb.yml config --quiet
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose config invalid' }
Write-Host 'Build va khoi dong 4 dich vu...'
docker compose -f docker-compose.mathweb.yml up -d --build
if ($LASTEXITCODE -ne 0) { throw 'Khong the khoi dong compose' }
Write-Host 'MATH_WEB dang duoc cau hinh tren may nay:'
Write-Host 'Frontend: http://127.0.0.1:8080/index.html'
Write-Host 'Backend:  http://127.0.0.1:8000/health'
Write-Host 'Progress: docker compose -f docker-compose.mathweb.yml exec factory-operator cat /data/operations/progress-latest.json'
Write-Host 'Theo doi:  docker compose -f docker-compose.mathweb.yml logs -f factory-operator factory-worker'
Write-Host 'Chua trien khai Internet/VPS. Dang ung vien khong duoc tu dong phe duyet.'
