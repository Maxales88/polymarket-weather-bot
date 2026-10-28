"""Per-city / per-model bias correction."""

from __future__ import annotations


class BiasCorrector:
    def __init__(self):
        self._bias: dict[str, float] = {}

    def fit(self, records: list[dict]) -> None:
        """records: list of {city, model, predicted, actual}."""
        from collections import defaultdict
        sums = defaultdict(float)
        counts = defaultdict(int)
        for r in records:
            key = f"{r['city']}::{r['model']}"
            sums[key] += r["predicted"] - r["actual"]
            counts[key] += 1
        for key in sums:
            self._bias[key] = sums[key] / counts[key]

    def correct(self, city: str, model: str, value: float) -> float:
        key = f"{city}::{model}"
        return value - self._bias.get(key, 0.0)
