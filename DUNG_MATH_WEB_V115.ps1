$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
docker compose -f docker-compose.mathweb.yml stop
Write-Host 'Da dung services. Docker volume chua bi xoa; du lieu van duoc luu.'
