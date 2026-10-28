"""Nowcasting: blend live ASOS observations into forecast with time-weighted regime."""

from __future__ import annotations

from datetime import datetime


def observation_weight(now: datetime, market_close: datetime) -> float:
    """Weight rises from 0 at midnight to MAX (0.8) by market close. Linear in hours."""
    if market_close <= now:
        return 0.8
    # hours since midnight
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    total = (market_close - midnight).total_seconds()
    elapsed = (now - midnight).total_seconds()
    if total <= 0:
        return 0.0
    frac = min(1.0, max(0.0, elapsed / total))
    return 0.8 * frac


def blend(forecast_mean: float, obs: float | None, weight: float) -> float:
    if obs is None:
        return forecast_mean
    w = max(0.0, min(0.8, weight))
    return (1 - w) * forecast_mean + w * obs
