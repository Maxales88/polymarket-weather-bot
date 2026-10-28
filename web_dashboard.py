"""Minimal Flask dashboard."""

from __future__ import annotations

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/status")
def status():
    return jsonify({"paper_mode": True})


if __name__ == "__main__":
    from config import CFG
    app.run(port=CFG.DASHBOARD_PORT)
