"""
MODULE: MKT-000
FILE: MKT-000-001
Module Name: Market Data Package
Version: 0.5.0
Purpose: Exposes market data feed services without coupling package import to GUI or trading execution.
Dependencies: sentinel_ai.market_data.market_data_feed
Change History:
- 0.3.0: Added market data package for Sprint 3 feed foundation.
- 0.5.0: Kept Qt-dependent refresh service as a direct import to protect lightweight validation imports.
"""

from sentinel_ai.market_data.market_data_feed import MarketDataFeedService

__all__ = ["MarketDataFeedService"]
