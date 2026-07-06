"""
MODULE: MODEL-003
FILE: MODEL-003-001
Module Name: Symbol Management Models
Version: 0.6.0
Purpose: Defines immutable symbol catalog and symbol resolution models for broker/account-specific MT5 symbols.
Dependencies: dataclasses, sentinel_ai.models.market
Change History:
- 0.6.0: Added symbol catalog item and resolution result models for Sprint 6 symbol management foundation.
"""

from __future__ import annotations

from dataclasses import dataclass

from sentinel_ai.models.market import SymbolValidationResult


@dataclass(frozen=True)
class SymbolCatalogItem:
    """Represent one broker symbol exposed by the active MT5 account."""

    symbol: str
    description: str
    path: str
    visible: bool
    digits: int | None
    point: float | None
    currency_base: str | None
    currency_profit: str | None
    trade_mode: int | None


@dataclass(frozen=True)
class SymbolResolutionResult:
    """Represent the result of resolving a requested symbol against the active MT5 account."""

    requested_symbol: str
    active_symbol: str | None
    resolved: bool
    message: str
    validation: SymbolValidationResult | None
    candidates: tuple[SymbolCatalogItem, ...]

    @property
    def candidate_symbols(self) -> tuple[str, ...]:
        """Return candidate symbol names only for compact status display."""
        return tuple(candidate.symbol for candidate in self.candidates)
