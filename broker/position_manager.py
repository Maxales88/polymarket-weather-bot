"""Position resolution and P&L tracking."""

from __future__ import annotations

import sqlite3
from datetime import datetime


def resolve_trade(db_path: str, trade_id: int, outcome: float, exit_price: float) -> float:
    """Mark a trade resolved and compute P&L. outcome 1.0 = YES won."""
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT side, price, shares, fee_usdc FROM trades WHERE id = ?", (trade_id,)
        ).fetchone()
        if not row:
            return 0.0
        side, price, shares, fee = row
        if side == "YES":
            pnl = (exit_price - price) * shares - fee
        else:
            pnl = (exit_price - price) * shares - fee
        # simplify: use outcome-based settlement
        if outcome == 1.0 and side == "YES":
            pnl = (1.0 - price) * shares - fee
        elif outcome == 0.0 and side == "YES":
            pnl = -price * shares - fee
        elif outcome == 1.0 and side == "NO":
            pnl = -price * shares - fee  # NO loses if YES won
        elif outcome == 0.0 and side == "NO":
            pnl = (1.0 - price) * shares - fee
        conn.execute(
            "UPDATE trades SET status='resolved', resolved_at=?, pnl_usdc=? WHERE id=?",
            (datetime.utcnow().isoformat(), pnl, trade_id),
        )
        conn.commit()
        return pnl
