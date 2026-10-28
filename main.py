"""CLI entry point."""

from __future__ import annotations

import argparse
import json

from config import CFG
from data.polymarket import geoblock_check, get_weather_markets, get_orderbook, mid_price
from db import init_db


def cmd_scan(args):
    init_db(CFG.DB_PATH)
    gb = geoblock_check()
    print("geoblock:", gb)
    markets = get_weather_markets(limit=args.limit)
    print(f"found {len(markets)} weather markets")
    for m in markets[:10]:
        print(m["market_id"], "|", m["question"], "| yes=", m["yes_price"])


def cmd_status(args):
    init_db(CFG.DB_PATH)
    print("db:", CFG.DB_PATH)
    print("paper mode:", __import__("os").getenv("PAPER_TRADING", "1"))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("scan")
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_scan)
    st = sub.add_parser("status")
    st.set_defaults(func=cmd_status)
    args = p.parse_args()
    if not hasattr(args, "func"):
        p.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
