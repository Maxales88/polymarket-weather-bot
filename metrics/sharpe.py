"""Sharpe ratio and basic performance metrics."""

from __future__ import annotations

import math
from typing import Iterable


def sharpe(returns: Iterable[float], risk_free: float = 0.0) -> float:
    rs = list(returns)
    if len(rs) < 2:
        return 0.0
    mean = sum(rs) / len(rs)
    var = sum((r - mean) ** 2 for r in rs) / (len(rs) - 1)
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (mean - risk_free) / sd


def max_drawdown(equity: Iterable[float]) -> float:
    eq = list(equity)
    if not eq:
        return 0.0
    peak = eq[0]
    mdd = 0.0
    for v in eq:
        peak = max(peak, v)
        mdd = max(mdd, (peak - v) / peak if peak > 0 else 0.0)
    return mdd
