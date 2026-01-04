# Run integration tests with DOCKER environment
# Ensure we run relative to backend/
$BackendRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $BackendRoot

# Activate virtual environment
& (Join-Path $BackendRoot "venv\Scripts\Activate.ps1")

$env:APP_ENV = "docker"
$env:FLASK_ENV = "testing"

Write-Host "Running Integration Tests (DOCKER environment)" -ForegroundColor Magenta
Write-Host "   Database: localhost:5433/lyftercook_docker" -ForegroundColor Cyan
Write-Host "   Redis: localhost:6380" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Make sure:" -ForegroundColor Yellow
Write-Host "   1. Docker containers are running: docker compose up -d" -ForegroundColor Gray
Write-Host "   2. Backend server is running in another terminal" -ForegroundColor Gray
Write-Host ""

python -m pytest tests/integration -v
