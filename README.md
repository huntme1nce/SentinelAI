# Sentinel AI

Sentinel AI is a professional Windows desktop trading workstation foundation built with PySide6, SQLite, JSON configuration, and service-based architecture.

## Sprint 1 Scope

Version: 0.1.0

This sprint establishes the project foundation:

- Application entry point
- Welcome window with Proverbs 13:11
- Main application shell using the approved layout
- JSON configuration service
- Logging service
- SQLite database service
- Permanent prediction repository
- Service contracts
- PyInstaller-compatible path handling
- Windows build command

Live MT5 analysis and trading engines are intentionally outside Sprint 1 scope. The application foundation is structured so those engines can be added without GUI rewrites.

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH="src"
python -m sentinel_ai.main
```

## Validate Sprint

```powershell
$env:PYTHONPATH="src"
python scripts/validate_sprint.py
```

## Build EXE

```powershell
.\build_windows.ps1
```

The build output is created under `dist\SentinelAI`.
