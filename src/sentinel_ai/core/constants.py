"""
MODULE: CORE-001
FILE: CORE-001-001
Module Name: Application Constants
Version: 0.9.0
Purpose: Stores immutable application-level constants used across Sentinel AI.
Dependencies: None
Change History:
- 0.1.0: Added core application identity constants.
- 0.2.0: Updated application version for Sprint 2 MT5 connection foundation.
- 0.3.0: Updated application version for Sprint 3 market data feed foundation.
- 0.4.0: Updated application version for Sprint 4 live chart rendering.
- 0.5.0: Updated application version for Sprint 5 live market refresh engine.
- 0.5.1: Updated application version for one-second refresh and chart navigation patch.
- 0.6.0: Updated application version for symbol management foundation.
- 0.7.0: Updated application version for market structure engine foundation.
- 0.8.0: Updated application version for support/resistance engine foundation.
- 0.9.0: Updated application version for BOS visibility and liquidity engine foundation.
"""

APP_NAME = "Sentinel AI"
APP_VERSION = "0.9.0"
ORGANIZATION_NAME = "RR Digital"
APPLICATION_ID = "com.rrdigital.sentinelai"
DATABASE_FILENAME = "sentinel_ai.sqlite3"
LOG_FILENAME = "sentinel_ai.log"
DEFAULT_CONFIG_RESOURCE = "config/default_config.json"
DEFAULT_THEME_RESOURCE = "theme/dark_neon.json"
