# Start LyfterCook backend with DOCKER environment configuration
param(
	[switch]$ResetDb
)

# Ensure we run relative to backend/
$BackendRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $BackendRoot

# Activate virtual environment
& (Join-Path $BackendRoot "venv\Scripts\Activate.ps1")

$env:APP_ENV = "docker"
$env:FLASK_ENV = "development"

Write-Host "Starting LyfterCook Backend (DOCKER environment)" -ForegroundColor Blue
Write-Host "   PostgreSQL: localhost:5433/lyftercook_docker" -ForegroundColor Cyan
Write-Host "   Redis: localhost:6380" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure Docker containers are running:" -ForegroundColor Yellow
Write-Host "   docker compose up -d" -ForegroundColor Gray
Write-Host ""

if ($ResetDb) {
	Write-Host "Resetting DOCKER database (destructive)" -ForegroundColor Yellow
	& (Join-Path $BackendRoot "venv\Scripts\python.exe") (Join-Path $BackendRoot "scripts\init_db.py") --drop
	if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
	Write-Host "" 
}

python run.py
