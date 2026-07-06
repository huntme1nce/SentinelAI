$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe scripts\validate_sprint.py

.\.venv\Scripts\pyinstaller.exe SentinelAI.spec --clean --noconfirm
Write-Host "Build completed: dist\SentinelAI"
