# MODULE: OPS-003
# FILE: OPS-003-001
# Module Name: Windows Build Script
# Version: 0.8.0
# Purpose: Validates and builds Sentinel AI as a PyInstaller Windows standalone package.
# Dependencies: PowerShell, Python, PyInstaller
# Change History:
# - 0.1.0: Added local virtual environment build flow.
# - 0.3.0: Preserved validation-first build flow for Sprint 3 market data feed foundation.
# - 0.4.0: Preserved validation-first build flow for chart rendering resources.
# - 0.5.0: Preserved validation-first build flow for live market refresh engine.
# - 0.5.1: Preserved validation-first build flow for refresh timing and chart navigation patch.
# - 0.6.0: Preserved validation-first build flow for symbol management foundation.
# - 0.7.0: Preserved validation-first build flow for market structure engine foundation.
# - 0.8.0: Preserved validation-first build flow for support/resistance engine foundation.

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
