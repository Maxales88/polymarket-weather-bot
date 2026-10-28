"""Daemon: periodic scan loop."""

from __future__ import annotations

import time
import logging

from config import CFG

logging.basicConfig(level=logging.INFO)


def run_loop():
    while True:
        logging.info("scan tick")
        # TODO: wire scan + signal + broker
        time.sleep(CFG.SCAN_INTERVAL_MIN * 60)


if __name__ == "__main__":
    run_loop()
