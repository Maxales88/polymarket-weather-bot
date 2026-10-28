"""Reporting helpers."""

from __future__ import annotations

from typing import Iterable


def summary(trades: Iterable[dict]) -> dict:
    ts = list(trades)
    n = len(ts)
    wins = [t for t in ts if (t.get("pnl_usdc") or 0) > 0]
    total_pnl = sum(t.get("pnl_usdc", 0) or 0 for t in ts)
    return {
        "n_trades": n,
        "n_wins": len(wins),
        "win_rate": (len(wins) / n) if n else 0.0,
        "total_pnl_usdc": round(total_pnl, 2),
        "avg_pnl": (total_pnl / n) if n else 0.0,
    }
