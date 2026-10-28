"""Edge calculation: model prob vs market mid, with fee adjustment."""

from __future__ import annotations

from config import CFG


def expected_value(p_model: float, market_mid: float, fee_rate: float = CFG.WEATHER_TAKER_FEE_RATE) -> float:
    """Edge per share after taker fee: p_model - market_mid - fee.

    Fee is approximated as fee_rate * p * (1-p) per share (worst-ish).
    """
    fee = fee_rate * market_mid * (1 - market_mid)
    return p_model - market_mid - fee


def edge(p_model: float, market_mid: float) -> float:
    return p_model - market_mid


def should_trade_yes(p_model: float, market_mid: float, min_edge: float) -> bool:
    return edge(p_model, market_mid) >= min_edge


def should_trade_no(p_model: float, market_mid: float, min_edge: float) -> bool:
    # NO side: model prob of NO = 1-p_model, market NO price = 1-market_mid
    return (1 - p_model) - (1 - market_mid) >= min_edge


def adaptive_min_edge(base: float, lead_hours: float) -> float:
    """Edge threshold scales down as resolution approaches (more confidence)."""
    if lead_hours <= 6:
        return base * 0.7
    if lead_hours <= 24:
        return base
    return base * 1.2
