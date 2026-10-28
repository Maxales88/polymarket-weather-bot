"""Central configuration for the Polymarket weather bot.

All tunable parameters live here. Override via environment variables where noted.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # --- Strategy thresholds ---
    MIN_EDGE: float = float(os.getenv("MIN_EDGE", "0.08"))
    KELLY_FRACTION: float = float(os.getenv("KELLY_FRACTION", "0.25"))
    MAX_TRADE_USDC: float = float(os.getenv("MAX_TRADE_USDC", "15.0"))
    MAX_DEPLOYED_FRACTION: float = float(os.getenv("MAX_DEPLOYED_FRACTION", "0.40"))
    NO_ENTRY_MIN_PRICE: float = float(os.getenv("NO_ENTRY_MIN_PRICE", "0.20"))
    NO_ENTRY_MAX_PRICE: float = float(os.getenv("NO_ENTRY_MAX_PRICE", "0.75"))
    NO_MIN_ENSEMBLE_STD: float = float(os.getenv("NO_MIN_ENSEMBLE_STD", "0.8"))
    FORECAST_T_DF: int = int(os.getenv("FORECAST_T_DF", "4"))

    # --- Filters ---
    MIN_MARKET_VOLUME_USDC: float = float(os.getenv("MIN_MARKET_VOLUME_USDC", "5000"))
    MIN_TOP5_DEPTH_USDC: float = float(os.getenv("MIN_TOP5_DEPTH_USDC", "150"))
    PER_MARKET_CAP_USDC: float = float(os.getenv("PER_MARKET_CAP_USDC", "50"))
    DAILY_LOSS_LIMIT_FRACTION: float = float(os.getenv("DAILY_LOSS_LIMIT_FRACTION", "0.10"))

    # --- Weather model ---
    NWP_MODELS: list[str] = field(default_factory=lambda: [
        "gfs", "ecmwf", "icon", "gem", "meteofrance",
    ])
    NOWCAST_WEIGHT_MAX: float = 0.8  # observation weight by market close

    # --- Calibration ---
    PLATT_ALPHA_DEFAULT: float = 1.3
    PLATT_ALPHA_GRID: tuple[float, ...] = tuple(
        round(0.8 + 0.05 * i, 2) for i in range(35)
    )  # 0.8 .. 2.5
    MIN_RESOLVED_FOR_PLATT: int = 30
    MIN_RESOLVED_FOR_ISOTONIC: int = 1000

    # --- Polymarket fees (weather) ---
    WEATHER_TAKER_FEE_RATE: float = 0.05
    WEATHER_MAKER_REBATE: float = 0.25

    # --- API ---
    GAMMA_URL: str = "https://gamma-api.polymarket.com"
    CLOB_URL: str = "https://clob.polymarket.com"
    DATA_URL: str = "https://data-api.polymarket.com"
    GEOBLOCK_URL: str = "https://polymarket.com/api/geoblock"
    WS_MARKET_URL: str = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    REST_RATE_LIMIT_PER_MIN: int = 60

    # --- Runtime ---
    DB_PATH: str = os.getenv("DB_PATH", "paper_trades.db")
    DASHBOARD_PORT: int = int(os.getenv("DASHBOARD_PORT", "5001"))
    SCAN_INTERVAL_MIN: int = int(os.getenv("SCAN_INTERVAL_MIN", "360"))


CFG = Config()


def is_paper_mode() -> bool:
    return os.getenv("PAPER_TRADING", "1") == "1"
