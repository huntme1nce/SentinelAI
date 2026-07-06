"""
MODULE: OPS-001
FILE: OPS-001-001
Module Name: Sprint Validator
Version: 0.2.0
Purpose: Validates Sprint source syntax, required resources, configuration loading, and MT5 timeframe mapping.
Dependencies: compileall, pathlib, sys
Change History:
- 0.1.0: Added compile and resource validation for stable milestone handoff.
- 0.2.0: Added Sprint 2 configuration and MT5 timeframe mapper validation.
"""

from __future__ import annotations

import compileall
import sys
from pathlib import Path


def main() -> int:
    """Compile project source and verify required resource files exist."""
    project_root = Path(__file__).resolve().parents[1]
    source_root = project_root / "src"
    required_files = [
        source_root / "sentinel_ai" / "resources" / "config" / "default_config.json",
        source_root / "sentinel_ai" / "resources" / "theme" / "dark_neon.json",
        source_root / "sentinel_ai" / "mt5" / "mt5_service.py",
        source_root / "sentinel_ai" / "mt5" / "timeframe_mapper.py",
        project_root / "SentinelAI.spec",
        project_root / "requirements.txt",
    ]

    missing_files = [path for path in required_files if not path.exists()]
    if missing_files:
        for path in missing_files:
            print(f"Missing required file: {path}", file=sys.stderr)
        return 1

    compiled = compileall.compile_dir(str(source_root), quiet=1)
    if not compiled:
        print("Python source compilation failed.", file=sys.stderr)
        return 1

    sys.path.insert(0, str(source_root))
    from sentinel_ai.config.config_service import ConfigService
    from sentinel_ai.mt5.timeframe_mapper import Mt5TimeframeMapper

    ConfigService(config_path=project_root / ".validation_config.json").load()
    if "M5" not in Mt5TimeframeMapper.SUPPORTED_TIMEFRAMES:
        print("MT5 timeframe mapper validation failed.", file=sys.stderr)
        return 1

    validation_config = project_root / ".validation_config.json"
    if validation_config.exists():
        validation_config.unlink()

    print("Sprint validation passed: source compiled, resources verified, config loaded, MT5 mapping available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
