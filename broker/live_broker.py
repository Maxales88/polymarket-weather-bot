"""Live broker: real orders via py-clob-client. Thin wrapper; all risk checks in caller."""

from __future__ import annotations

from data.polymarket import ClobClientWrapper, best_ask, best_bid, mid_price


class LiveBroker:
    def __init__(self):
        self.client = ClobClientWrapper()

    def place_limit(self, token_id: str, price: float, size_usdc: float, side: str = "BUY") -> dict:
        return self.client.create_order(token_id=token_id, price=price, size_usdc=size_usdc, side=side)

    def cancel_all(self) -> None:
        self.client.cancel_all()

    def positions(self) -> list[dict]:
        return self.client.get_positions()
