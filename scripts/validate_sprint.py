"""
MODULE: OPS-001
FILE: OPS-001-001
Module Name: Sprint Validator
Version: 0.1.0
Purpose: Validates Sprint 1 source syntax and required packaged resources.
Dependencies: compileall, pathlib, sys
Change History:
- 0.1.0: Added compile and resource validation for stable milestone handoff.
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

    print("Sprint validation passed: source compiled and resources verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
