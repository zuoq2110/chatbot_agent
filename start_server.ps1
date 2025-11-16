# Startup script for KMA ChatBot Agent with OpenMP fix

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "KMA ChatBot Agent - Starting Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variable to fix OpenMP library conflict
$env:KMP_DUPLICATE_LIB_OK = "TRUE"
Write-Host "[OK] OpenMP conflict fix enabled" -ForegroundColor Green

# Navigate to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
Write-Host "[OK] Changed to project directory: $scriptPath" -ForegroundColor Green

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "[WARNING] No virtual environment found, using system Python" -ForegroundColor Yellow
}

# Start the server
Write-Host ""
Write-Host "[INFO] Starting Uvicorn server..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    uvicorn src.backend.main:app --reload --host 127.0.0.1 --port 8000
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error starting server: $_" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Server stopped" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
