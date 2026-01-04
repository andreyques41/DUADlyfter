# Start LyfterCook backend with LOCAL environment configuration
param(
	[switch]$ResetDb
)

# Ensure we run relative to backend/
$BackendRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $BackendRoot

# Activate virtual environment
& (Join-Path $BackendRoot "venv\Scripts\Activate.ps1")

$env:APP_ENV = "local"
$env:FLASK_ENV = "development"

Write-Host "Starting LyfterCook Backend (LOCAL environment)" -ForegroundColor Green
Write-Host "   PostgreSQL: localhost:5432/lyftercook" -ForegroundColor Cyan
Write-Host "   Redis: Cloud instance" -ForegroundColor Cyan
Write-Host ""

if ($ResetDb) {
	Write-Host "Resetting LOCAL database (destructive)" -ForegroundColor Yellow
	& (Join-Path $BackendRoot "venv\Scripts\python.exe") (Join-Path $BackendRoot "scripts\init_db.py") --drop
	if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
	Write-Host "" 
}

python run.py
