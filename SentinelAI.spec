# MODULE: OPS-002
# FILE: OPS-002-001
# Module Name: PyInstaller Specification
# Version: 0.3.0
# Purpose: Builds Sentinel AI as a Windows standalone application with packaged resources.
# Dependencies: PyInstaller, pathlib
# Change History:
# - 0.1.0: Added PyInstaller collection build for Sprint 1 foundation.
# - 0.3.0: Added explicit MetaTrader5 hidden import for lazy MT5 gateway loading.

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path.cwd()
resource_root = project_root / "src" / "sentinel_ai" / "resources"

a = Analysis(
    [str(project_root / "src" / "sentinel_ai" / "main.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[(str(resource_root), "sentinel_ai/resources")],
    hiddenimports=["MetaTrader5"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SentinelAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SentinelAI",
)
