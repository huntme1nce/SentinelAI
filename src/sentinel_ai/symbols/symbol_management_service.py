"""
MODULE: SYM-001
FILE: SYM-001-001
Module Name: Symbol Management Service
Version: 0.6.0
Purpose: Resolves broker/account-specific MT5 symbols without coupling GUI to MT5 symbol-search logic.
Dependencies: logging, re, sentinel_ai.config, sentinel_ai.models, sentinel_ai.services
Change History:
- 0.6.0: Added catalog loading, alias matching, exact activation, fallback resolution, and selected-symbol persistence.
"""

from __future__ import annotations

import logging
import re

from sentinel_ai.config.config_service import ConfigService
from sentinel_ai.models.market import SymbolValidationResult
from sentinel_ai.models.symbol import SymbolCatalogItem, SymbolResolutionResult
from sentinel_ai.services.contracts import MarketDataServiceContract


class SymbolManagementService:
    """Manage active MT5 symbol selection using broker-provided symbol metadata."""

    def __init__(
        self,
        market_data_gateway: MarketDataServiceContract,
        config_service: ConfigService,
        logger: logging.Logger,
    ) -> None:
        """Initialize the symbol service with explicit replaceable dependencies."""
        self._market_data_gateway = market_data_gateway
        self._config_service = config_service
        self._logger = logger
        self._catalog: tuple[SymbolCatalogItem, ...] = ()

    @property
    def available_symbol_count(self) -> int:
        """Return the number of symbols loaded from the current MT5 account."""
        return len(self._catalog)

    def load_available_symbols(self) -> tuple[SymbolCatalogItem, ...]:
        """Load and cache all symbols available from the active MT5 account."""
        catalog = self._market_data_gateway.list_symbols()
        self._catalog = tuple(sorted(catalog, key=lambda item: item.symbol.upper()))
        self._logger.info("Loaded %s available MT5 symbols from active account.", len(self._catalog))
        return self._catalog

    def resolve_startup_symbol(
        self,
        configured_symbol: str,
        preferred_aliases: tuple[str, ...],
        auto_resolve_enabled: bool,
    ) -> SymbolResolutionResult:
        """Resolve the configured startup symbol against the active account symbol catalog."""
        requested_symbol = str(configured_symbol).strip()
        if requested_symbol:
            exact_result = self._validate_exact_symbol(requested_symbol)
            if self._is_usable_validation(exact_result):
                self._persist_active_symbol(exact_result.symbol)
                return SymbolResolutionResult(
                    requested_symbol=requested_symbol,
                    active_symbol=exact_result.symbol,
                    resolved=True,
                    message=f"Symbol {exact_result.symbol}: {exact_result.message}",
                    validation=exact_result,
                    candidates=(),
                )
            if not auto_resolve_enabled:
                candidates = self.suggest_symbols(requested_symbol, preferred_aliases, 8)
                return self._unresolved_result(requested_symbol, exact_result.message, candidates)

        if not auto_resolve_enabled:
            return self._unresolved_result(
                requested_symbol,
                "Symbol auto-resolution is disabled.",
                self.suggest_symbols(requested_symbol, preferred_aliases, 8),
            )

        candidates = self.suggest_symbols(requested_symbol, preferred_aliases, 12)
        for candidate in candidates:
            validation = self._validate_exact_symbol(candidate.symbol)
            if self._is_usable_validation(validation):
                self._persist_active_symbol(validation.symbol)
                message = self._resolved_fallback_message(requested_symbol, validation.symbol)
                return SymbolResolutionResult(
                    requested_symbol=requested_symbol,
                    active_symbol=validation.symbol,
                    resolved=True,
                    message=message,
                    validation=validation,
                    candidates=candidates,
                )

        return self._unresolved_result(
            requested_symbol,
            "No usable broker symbol could be resolved for the active MT5 account.",
            candidates,
        )

    def activate_symbol(self, requested_symbol: str) -> SymbolResolutionResult:
        """Activate a user-requested symbol and persist it when it is usable."""
        clean_symbol = str(requested_symbol).strip()
        if not clean_symbol:
            return self._unresolved_result("", "Symbol is empty.", ())

        exact_result = self._validate_exact_symbol(clean_symbol)
        if self._is_usable_validation(exact_result):
            self._persist_active_symbol(exact_result.symbol)
            return SymbolResolutionResult(
                requested_symbol=clean_symbol,
                active_symbol=exact_result.symbol,
                resolved=True,
                message=f"Symbol {exact_result.symbol}: {exact_result.message}",
                validation=exact_result,
                candidates=(),
            )

        candidates = self.suggest_symbols(clean_symbol, (), 8)
        for candidate in candidates:
            validation = self._validate_exact_symbol(candidate.symbol)
            if self._is_usable_validation(validation):
                self._persist_active_symbol(validation.symbol)
                return SymbolResolutionResult(
                    requested_symbol=clean_symbol,
                    active_symbol=validation.symbol,
                    resolved=True,
                    message=self._resolved_fallback_message(clean_symbol, validation.symbol),
                    validation=validation,
                    candidates=candidates,
                )

        return self._unresolved_result(clean_symbol, exact_result.message, candidates)

    def suggest_symbols(
        self,
        query: str,
        preferred_aliases: tuple[str, ...],
        limit: int,
    ) -> tuple[SymbolCatalogItem, ...]:
        """Return ranked symbol suggestions from cached MT5 symbols."""
        if not self._catalog:
            self.load_available_symbols()

        normalized_terms = self._normalized_terms((query, *preferred_aliases))
        if not normalized_terms:
            return self._catalog[: max(0, int(limit))]

        ranked: list[tuple[int, int, str, SymbolCatalogItem]] = []
        for item in self._catalog:
            score = self._score_symbol(item, normalized_terms)
            if score <= 0:
                continue
            ranked.append((score, -len(item.symbol), item.symbol.upper(), item))
        ranked.sort(reverse=True)
        return tuple(entry[3] for entry in ranked[: max(0, int(limit))])

    def _validate_exact_symbol(self, symbol: str) -> SymbolValidationResult:
        """Validate one exact symbol through the market-data gateway."""
        return self._market_data_gateway.validate_symbol(symbol)

    def _persist_active_symbol(self, symbol: str) -> None:
        """Persist the active symbol through the configuration service."""
        self._config_service.update_trading_symbol(symbol)
        self._logger.info("Active symbol persisted: %s", symbol)

    @staticmethod
    def _is_usable_validation(validation: SymbolValidationResult) -> bool:
        """Return True when a validation result is usable for market-data requests."""
        return bool(validation.valid and validation.visible)

    @staticmethod
    def _normalized_terms(values: tuple[str, ...]) -> tuple[str, ...]:
        """Normalize requested and alias terms for broker-symbol matching."""
        terms: list[str] = []
        for value in values:
            normalized = SymbolManagementService._normalize_match_text(value)
            if normalized and normalized not in terms:
                terms.append(normalized)
        return tuple(terms)

    @staticmethod
    def _normalize_match_text(value: str) -> str:
        """Return an uppercase alphanumeric-only symbol comparison string."""
        return re.sub(r"[^A-Z0-9]", "", str(value).upper())

    @classmethod
    def _score_symbol(cls, item: SymbolCatalogItem, normalized_terms: tuple[str, ...]) -> int:
        """Score one symbol against normalized requested terms."""
        symbol_text = cls._normalize_match_text(item.symbol)
        description_text = cls._normalize_match_text(item.description)
        path_text = cls._normalize_match_text(item.path)
        searchable_text = f"{symbol_text} {description_text} {path_text}"
        best_score = 0
        for term in normalized_terms:
            if not term:
                continue
            if symbol_text == term:
                best_score = max(best_score, 1000)
            elif symbol_text.startswith(term):
                best_score = max(best_score, 850)
            elif term in symbol_text:
                best_score = max(best_score, 760)
            elif symbol_text and term.startswith(symbol_text):
                best_score = max(best_score, 620)
            elif term in searchable_text:
                best_score = max(best_score, 520)
        if item.visible and best_score > 0:
            best_score += 20
        return best_score

    @staticmethod
    def _resolved_fallback_message(requested_symbol: str, active_symbol: str) -> str:
        """Build a deterministic fallback resolution status message."""
        if requested_symbol:
            return f"Configured/requested symbol {requested_symbol} is unavailable. Auto-resolved to {active_symbol}."
        return f"No configured symbol was provided. Auto-resolved to {active_symbol}."

    @staticmethod
    def _unresolved_result(
        requested_symbol: str,
        message: str,
        candidates: tuple[SymbolCatalogItem, ...],
    ) -> SymbolResolutionResult:
        """Build a deterministic unresolved symbol result."""
        return SymbolResolutionResult(
            requested_symbol=requested_symbol,
            active_symbol=None,
            resolved=False,
            message=message,
            validation=None,
            candidates=candidates,
        )
