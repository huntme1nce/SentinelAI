"""
============================================================
MODULE ID   : CORE-006
MODULE NAME : Version Manager
VERSION     : 1.0.0
AUTHOR      : Sentinel AI Project
============================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    major: int = 1
    minor: int = 0
    patch: int = 0
    stage: str = "alpha"
    build: str = "001"

    @property
    def full(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}-{self.stage}.{self.build}"


APP_VERSION = Version()