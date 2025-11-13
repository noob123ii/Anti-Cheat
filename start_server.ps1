# AntiCheat Server Startup Script
Write-Host "Starting AntiCheat API Server..." -ForegroundColor Green

# Try to find Python
$pythonCmd = $null

# Try different Python commands
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    try {
        $result = Get-Command $cmd -ErrorAction Stop
        $pythonCmd = $cmd
        Write-Host "Found Python: $($result.Source)" -ForegroundColor Yellow
        break
    } catch {
        continue
    }
}

if ($null -eq $pythonCmd) {
    Write-Host "Python not found. Trying to use python.exe directly..." -ForegroundColor Yellow
    # Try to use python.exe from WindowsApps
    $pythonExe = "C:\Users\cpatt\AppData\Local\Microsoft\WindowsApps\python.exe"
    if (Test-Path $pythonExe) {
        # Check if it's the actual Python or just a stub
        $fileInfo = Get-Item $pythonExe
        if ($fileInfo.Length -gt 1000) {
            $pythonCmd = $pythonExe
            Write-Host "Using Python from: $pythonExe" -ForegroundColor Yellow
        }
    }
}

if ($null -eq $pythonCmd) {
    Write-Host "ERROR: Could not find Python installation!" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and in your PATH." -ForegroundColor Red
    exit 1
}

# Change to script directory
Set-Location $PSScriptRoot

# Start the server
Write-Host "`nStarting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

try {
    if ($pythonCmd -like "*.exe") {
        & $pythonCmd -m uvicorn main:app --host 0.0.0.0 --port 8000
    } else {
        & $pythonCmd -m uvicorn main:app --host 0.0.0.0 --port 8000
    }
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
    Write-Host "Trying alternative method..." -ForegroundColor Yellow
    & $pythonCmd main.py
}

