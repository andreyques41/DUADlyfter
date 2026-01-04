# Run unit tests with LOCAL database
# Ensure we run relative to backend/
$BackendRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $BackendRoot

# Activate virtual environment
& (Join-Path $BackendRoot "venv\Scripts\Activate.ps1")

$env:APP_ENV = "local"
$env:FLASK_ENV = "testing"

Write-Host "Running Unit Tests (LOCAL database)" -ForegroundColor Magenta
Write-Host "   Database: localhost:5432/lyftercook_test" -ForegroundColor Cyan
Write-Host ""

python -m pytest tests/unit -v
