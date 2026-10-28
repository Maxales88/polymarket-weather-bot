"""SQLite persistence layer for trades, predictions, and calibration state."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    city TEXT,
    bucket_lo REAL,
    bucket_hi REAL,
    raw_prob REAL NOT NULL,
    calibrated_prob REAL NOT NULL,
    blended_prob REAL NOT NULL,
    market_mid REAL NOT NULL,
    edge REAL NOT NULL,
    side TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    resolved INTEGER NOT NULL DEFAULT 0,
    outcome REAL
);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    token_id TEXT NOT NULL,
    side TEXT NOT NULL,
    price REAL NOT NULL,
    size_usdc REAL NOT NULL,
    shares REAL NOT NULL,
    fee_usdc REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'open',
    mode TEXT NOT NULL DEFAULT 'paper',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at TEXT,
    pnl_usdc REAL
);

CREATE TABLE IF NOT EXISTS calibration_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def init_db(path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


@contextmanager
def connect(path: str):
    conn = sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def log_prediction(path: str, **kwargs) -> int:
    with connect(path) as conn:
        cur = conn.execute(
            """INSERT INTO predictions
            (market_id, city, bucket_lo, bucket_hi, raw_prob, calibrated_prob,
             blended_prob, market_mid, edge, side)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                kwargs["market_id"], kwargs.get("city"), kwargs.get("bucket_lo"),
                kwargs.get("bucket_hi"), kwargs["raw_prob"], kwargs["calibrated_prob"],
                kwargs["blended_prob"], kwargs["market_mid"], kwargs["edge"],
                kwargs["side"],
            ),
        )
        return cur.lastrowid


def log_trade(path: str, **kwargs) -> int:
    with connect(path) as conn:
        cur = conn.execute(
            """INSERT INTO trades
            (market_id, token_id, side, price, size_usdc, shares, fee_usdc, mode)
            VALUES (?,?,?,?,?,?,?,?)""",
            (
                kwargs["market_id"], kwargs["token_id"], kwargs["side"],
                kwargs["price"], kwargs["size_usdc"], kwargs["shares"],
                kwargs.get("fee_usdc", 0.0), kwargs.get("mode", "paper"),
            ),
        )
        return cur.lastrowid


def fetch_unresolved_predictions(path: str) -> list[dict]:
    with connect(path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM predictions WHERE resolved = 0"
        ).fetchall()
        return [dict(r) for r in rows]


def set_prediction_outcome(path: str, pred_id: int, outcome: float) -> None:
    with connect(path) as conn:
        conn.execute(
            "UPDATE predictions SET resolved = 1, outcome = ? WHERE id = ?",
            (outcome, pred_id),
        )


def count_resolved(path: str, strategy: str | None = None) -> int:
    with connect(path) as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM predictions WHERE resolved = 1"
        ).fetchone()[0]


def get_calibration_state(path: str, key: str) -> str | None:
    with connect(path) as conn:
        row = conn.execute(
            "SELECT value FROM calibration_state WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None


def set_calibration_state(path: str, key: str, value: str) -> None:
    with connect(path) as conn:
        conn.execute(
            """INSERT INTO calibration_state (key, value) VALUES (?,?)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value,
               updated_at = datetime('now')""",
            (key, value),
        )
