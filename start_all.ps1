# 5G PCAN-5G Research Platform Startup Script (PowerShell)
# This script starts both backend and frontend simultaneously

Write-Host ""
Write-Host "================================================================================"
Write-Host "  5G CROSS-LAYER DQN PCAN-5G RESEARCH PLATFORM v2.0"
Write-Host "  Startup Script"
Write-Host "================================================================================"
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion"
} catch {
    Write-Host "✗ Python is not installed or not in PATH"
    Write-Host "Please install Python or add it to your PATH environment variable"
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version 2>&1
    Write-Host "✓ npm found: version $npmVersion"
} catch {
    Write-Host "✗ npm is not installed or not in PATH"
    Write-Host "Please install Node.js which includes npm"
    exit 1
}

Write-Host ""
Write-Host "[1/4] Installing Python dependencies..."
Push-Location "backend"
python -m pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Warning: Some Python dependencies could not be installed"
}
Pop-Location
Write-Host "       Complete!"
Write-Host ""

Write-Host "[2/4] Installing Node.js dependencies..."
Push-Location "frontend"
npm install --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Warning: Some Node.js dependencies could not be installed"
}
Pop-Location
Write-Host "       Complete!"
Write-Host ""

Write-Host "[3/4] Starting FastAPI Backend on port 8000..."
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py" -PassThru
Start-Sleep -Seconds 4
Write-Host "       ✓ Backend started (PID: $($backendProcess.Id))"
Write-Host ""

Write-Host "[4/4] Starting Vite Frontend on port 5173..."
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru
Start-Sleep -Seconds 4
Write-Host "       ✓ Frontend started (PID: $($frontendProcess.Id))"
Write-Host ""

Write-Host "================================================================================"
Write-Host "  All services started successfully!"
Write-Host "================================================================================"
Write-Host ""
Write-Host "  Backend API:             http://localhost:8000"
Write-Host "  API Documentation:       http://localhost:8000/docs"
Write-Host "  Interactive API Tester:  http://localhost:8000/redoc"
Write-Host "  Frontend Dashboard:      http://localhost:5173"
Write-Host ""
Write-Host "================================================================================"
Write-Host ""
Write-Host "  Note: Two new PowerShell windows will open for Backend and Frontend"
Write-Host "  Close those windows or press Ctrl+C to stop the services"
Write-Host ""

Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"

# Keep this window open
Read-Host "Press Enter to exit (services will keep running in their windows)"
