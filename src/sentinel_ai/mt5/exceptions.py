"""
MODULE: MT5-001
FILE: MT5-001-001
Module Name: MT5 Exceptions
Version: 0.2.0
Purpose: Defines MT5 integration exceptions without coupling callers to external package errors.
Dependencies: None
Change History:
- 0.2.0: Added MT5 foundation exception types.
"""

from __future__ import annotations


class Mt5ServiceError(RuntimeError):
    """Base exception for recoverable MT5 service failures."""


class Mt5NotConnectedError(Mt5ServiceError):
    """Raised when market data is requested before a valid MT5 connection exists."""


class Mt5TimeframeError(Mt5ServiceError):
    """Raised when an unsupported timeframe is requested."""
