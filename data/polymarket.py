"""Polymarket API clients: Gamma (discovery), CLOB (orderbook/orders), Data, geoblock."""

from __future__ import annotations

import os
import time
from typing import Any

import requests

from config import CFG


def _get(url: str, params: dict | None = None, timeout: int = 15) -> Any:
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def geoblock_check() -> dict:
    return _get(CFG.GEOBLOCK_URL)


def get_weather_markets(limit: int = 50, tag: str = "weather") -> list[dict]:
    params = {"tag": tag, "active": "true", "closed": "false", "limit": limit}
    try:
        data = _get(f"{CFG.GAMMA_URL}/markets", params=params)
    except Exception:
        data = _get(f"{CFG.GAMMA_URL}/markets", params={"active": "true", "closed": "false", "limit": limit})
    if isinstance(data, dict):
        data = data.get("data") or data.get("markets") or []
    out = []
    for m in data or []:
        q = (m.get("question") or "").lower()
        keywords = ("snow", "rain", "temperature", "weather", "°f", "°c", "inch", "precip")
        if not any(k in q for k in keywords):
            continue
        tokens = m.get("tokens") or []
        yes_tok = tokens[0] if len(tokens) > 0 else {}
        no_tok = tokens[1] if len(tokens) > 1 else {}
        out.append({
            "market_id": m.get("conditionId") or m.get("id"),
            "question": m.get("question"),
            "condition_id": m.get("conditionId"),
            "token_yes": yes_tok.get("token_id") or m.get("clobTokenIds", [None])[0] if m.get("clobTokenIds") else None,
            "token_no": no_tok.get("token_id") or (m.get("clobTokenIds", [None, None])[1] if m.get("clobTokenIds") else None),
            "yes_price": float(yes_tok.get("price", m.get("outcomePrices", ["0.5"])[0] if m.get("outcomePrices") else 0.5)),
            "no_price": float(no_tok.get("price", m.get("outcomePrices", ["0.5", "0.5"])[1] if m.get("outcomePrices") else 0.5)),
            "volume": float(m.get("volume", 0) or 0),
            "neg_risk": bool(m.get("negRisk", False)),
            "resolution_source": m.get("resolutionSource"),
            "end_date": m.get("endDate"),
        })
    return out


def get_orderbook(token_id: str) -> dict:
    return _get(f"{CFG.CLOB_URL}/book", params={"token_id": token_id})


def top5_depth_usdc(book: dict) -> float:
    asks = book.get("asks", [])[:5]
    return sum(float(a.get("price", 0)) * float(a.get("size", 0)) for a in asks)


def mid_price(book: dict) -> float:
    bids = book.get("bids", [])
    asks = book.get("asks", [])
    if not bids or not asks:
        return float(book.get("last_trade_price", 0.5))
    return (float(bids[0]["price"]) + float(asks[0]["price"])) / 2.0


def best_ask(book: dict) -> float | None:
    asks = book.get("asks", [])
    return float(asks[0]["price"]) if asks else None


def best_bid(book: dict) -> float | None:
    bids = book.get("bids", [])
    return float(bids[0]["price"]) if bids else None


class ClobClientWrapper:
    """Thin wrapper around py-clob-client. Lazy import to keep skeleton importable."""

    def __init__(self):
        self._client = None

    def _init(self):
        if self._client is not None:
            return self._client
        try:
            from py_clob_client.client import ClobClient
        except ImportError as e:
            raise RuntimeError("py-clob-client not installed") from e
        pk = os.getenv("POLYMARKET_PRIVATE_KEY")
        if not pk:
            raise RuntimeError("POLYMARKET_PRIVATE_KEY not set")
        proxy = os.getenv("POLYMARKET_PROXY_ADDRESS")
        chain = 137
        self._client = ClobClient(
            host=CFG.CLOB_URL, key=pk, chain_id=chain, signature_type=1 if proxy else 0,
            funder=proxy,
        )
        # derive api creds
        try:
            creds = self._client.create_or_derive_api_creds()
            self._client.set_api_creds(creds)
        except Exception:
            pass
        return self._client

    def create_order(self, token_id: str, price: float, size_usdc: float, side: str = "BUY") -> dict:
        client = self._init()
        from py_clob_client.clob_types import OrderArgs
        from py_clob_client.order_builder.constants import BUY, SELL
        s = BUY if side.upper() == "BUY" else SELL
        # size in shares: size_usdc / price
        shares = size_usdc / price if price > 0 else 0
        args = OrderArgs(token_id=token_id, price=price, size=shares, side=s)
        signed = client.create_order(args)
        return client.post_order(signed)

    def cancel_all(self) -> None:
        client = self._init()
        try:
            client.cancel_all()
        except Exception:
            pass

    def get_positions(self) -> list[dict]:
        try:
            import requests
            # Data API
            r = requests.get(f"{CFG.DATA_URL}/positions", timeout=15)
            r.raise_for_status()
            return r.json() if isinstance(r.json(), list) else r.json().get("data", [])
        except Exception:
            return []
