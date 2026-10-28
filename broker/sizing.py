"""Position sizing: Kelly criterion for binary prediction markets."""

from __future__ import annotations

from config import CFG


def kelly_fraction_yes(p: float, market_price: float) -> float:
    """Full Kelly fraction for YES side. Negative => no edge."""
    if market_price <= 0 or market_price >= 1:
        return 0.0
    num = p - market_price
    den = 1 - market_price
    if den <= 0:
        return 0.0
    f = num / den
    return f


def kelly_fraction_no(p_yes: float, market_price_yes: float) -> float:
    """Full Kelly fraction for NO side (flip)."""
    p_no = 1 - p_yes
    price_no = 1 - market_price_yes
    return kelly_fraction_yes(p_no, price_no)


def size_position(
    p_win: float,
    market_price: float,
    bankroll: float,
    method: str = "fractional_kelly",
    kelly_multiplier: float = CFG.KELLY_FRACTION,
    min_ev: float = 0.0,
    max_fraction: float = 0.95,
    max_trade_usdc: float = CFG.MAX_TRADE_USDC,
) -> float:
    """Return dollar amount to trade. 0 if no edge / invalid."""
    if bankroll <= 0 or market_price <= 0 or market_price >= 1:
        return 0.0
    # EV gate
    ev = p_win - market_price
    if ev <= min_ev:
        return 0.0
    if method == "kelly":
        f = kelly_fraction_yes(p_win, market_price)
    elif method == "fractional_kelly":
        f = kelly_fraction_yes(p_win, market_price) * kelly_multiplier
    elif method == "fixed":
        f = kelly_multiplier
    else:
        return 0.0
    if f <= 0:
        return 0.0
    f = min(f, max_fraction)
    amount = bankroll * f
    amount = min(amount, max_trade_usdc)
    # fee buffer: ensure not negative edge after fees
    return round(amount, 2)


def fee_usdc(shares: float, price: float, fee_rate: float = CFG.WEATHER_TAKER_FEE_RATE) -> float:
    c = shares
    return round(c * fee_rate * price * (1 - price), 5)
