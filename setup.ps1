# Setup script for Windows (PowerShell)

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  Equity Research Generator Setup  " -ForegroundColor Cyan
Write-Host "  Platform: Windows (PowerShell)   " -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
    
    # Check if Python 3.10+
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
    $versionNum = [double]$version
    
    if ($versionNum -lt 3.10) {
        Write-Host "Error: Python 3.10+ required" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Python version OK" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.10+ from:"
    Write-Host "  https://www.python.org/downloads/"
    Write-Host ""
    exit 1
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
try {
    python -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} catch {
    Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not activate virtual environment automatically" -ForegroundColor Yellow
    Write-Host "You may need to enable script execution:" -ForegroundColor Yellow
    Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
}
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "[OK] pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies (placeholder - will be created during Phase 1)
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[!] requirements.txt not found - will be created during Phase 1" -ForegroundColor Yellow
}
Write-Host ""

# Check Ollama installation
Write-Host "Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "[OK] Ollama is installed" -ForegroundColor Green
    Write-Host "   Version: $ollamaVersion" -ForegroundColor Gray
    
    # Check if llama3 is available
    $models = ollama list 2>&1
    if ($models -match "llama3") {
        Write-Host "[OK] llama3 model is already pulled" -ForegroundColor Green
    } else {
        Write-Host "Pulling llama3 model (this may take a few minutes)..." -ForegroundColor Yellow
        ollama pull llama3
        Write-Host "[OK] llama3 model pulled" -ForegroundColor Green
    }
} catch {
    Write-Host "[!] Ollama is not installed" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To install Ollama:" -ForegroundColor Cyan
    Write-Host "  1. Go to: https://ollama.com/download/windows"
    Write-Host "  2. Download and run the installer"
    Write-Host "  3. Run: ollama pull llama3"
    Write-Host ""
}
Write-Host ""

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "[OK] Setup Complete!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the virtual environment:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "To run the application (after Phase 1):" -ForegroundColor Cyan
Write-Host "  streamlit run ui\app.py"
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

