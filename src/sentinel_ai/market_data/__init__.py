"""
MODULE: MKT-000
FILE: MKT-000-001
Module Name: Market Data Package
Version: 0.3.0
Purpose: Exposes market data feed services without coupling them to GUI or trading execution.
Dependencies: sentinel_ai.market_data.market_data_feed
Change History:
- 0.3.0: Added market data package for Sprint 3 feed foundation.
"""

from sentinel_ai.market_data.market_data_feed import MarketDataFeedService

__all__ = ["MarketDataFeedService"]
