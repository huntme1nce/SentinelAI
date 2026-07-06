"""
MODULE: APP-001
FILE: APP-001-002
Module Name: Application Entry Point
Version: 0.1.0
Purpose: Provides the executable entry point for Sentinel AI.
Dependencies: sys, sentinel_ai.app
Change History:
- 0.1.0: Added main entry point for source execution and PyInstaller packaging.
"""

from __future__ import annotations

import sys

from sentinel_ai.app import run_application


def main() -> int:
    """Run Sentinel AI and return the process exit code."""
    return run_application()


if __name__ == "__main__":
    sys.exit(main())
