"""Paper broker: simulated execution with all risk checks."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from broker.sizing import size_position, fee_usdc
from config import CFG
from data.polymarket import top5_depth_usdc, mid_price
from db import log_trade


@dataclass
class RiskState:
    bankroll: float
    deployed: float = 0.0
    daily_pnl: float = 0.0
    halted: bool = False


class PaperBroker:
    def __init__(self, db_path: str | None = None, bankroll: float = 1000.0):
        self.db_path = db_path or CFG.DB_PATH
        self.state = RiskState(bankroll=bankroll)

    def can_trade(self, market: dict, book: dict) -> tuple[bool, str]:
        if self.state.halted:
            return False, "halted"
        if self.state.deployed / max(self.state.bankroll, 1e-9) >= CFG.MAX_DEPLOYED_FRACTION:
            return False, "deployed_cap"
        if float(market.get("volume", 0)) < CFG.MIN_MARKET_VOLUME_USDC:
            return False, "low_volume"
        if top5_depth_usdc(book) < CFG.MIN_TOP5_DEPTH_USDC:
            return False, "low_depth"
        if abs(self.state.daily_pnl) / max(self.state.bankroll, 1e-9) >= CFG.DAILY_LOSS_LIMIT_FRACTION and self.state.daily_pnl < 0:
            self.state.halted = True
            return False, "daily_loss_limit"
        return True, "ok"

    def execute(self, market: dict, book: dict, p_model: float, side: str, bankroll: float) -> dict | None:
        ok, reason = self.can_trade(market, book)
        if not ok:
            return {"skipped": True, "reason": reason}
        mid = mid_price(book)
        if side == "YES":
            price = best_ask_safe(book, mid)
            p_win = p_model
            mprice = mid
        else:
            price = 1 - best_bid_safe(book, mid)  # NO price
            p_win = 1 - p_model
            mprice = 1 - mid
        # NO price gate
        if side == "NO" and not (CFG.NO_ENTRY_MIN_PRICE <= price <= CFG.NO_ENTRY_MAX_PRICE):
            return {"skipped": True, "reason": "no_price_gate"}
        amount = size_position(p_win, mprice, bankroll)
        if amount <= 0:
            return {"skipped": True, "reason": "zero_size"}
        amount = min(amount, CFG.PER_MARKET_CAP_USDC)
        token_id = market["token_yes"] if side == "YES" else market["token_no"]
        shares = amount / price if price > 0 else 0
        fee = fee_usdc(shares, price)
        trade_id = log_trade(
            self.db_path, market_id=market["market_id"], token_id=token_id,
            side=side, price=price, size_usdc=amount, shares=shares,
            fee_usdc=fee, mode="paper",
        )
        self.state.deployed += amount
        return {"trade_id": trade_id, "side": side, "price": price, "size": amount, "shares": shares, "fee": fee}


def best_ask_safe(book: dict, mid: float) -> float:
    from data.polymarket import best_ask
    a = best_ask(book)
    return a if a is not None else mid


def best_bid_safe(book: dict, mid: float) -> float:
    from data.polymarket import best_bid
    b = best_bid(book)
    return b if b is not None else mid
