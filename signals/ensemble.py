"""Ensemble statistics over multi-model forecasts."""

from __future__ import annotations

import math
from typing import Iterable


def mean(values: Iterable[float]) -> float:
    vals = [float(v) for v in values]
    if not vals:
        return 0.0
    return sum(vals) / len(vals)


def std(values: Iterable[float]) -> float:
    vals = [float(v) for v in values]
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    var = sum((v - m) ** 2 for v in vals) / len(vals)
    return math.sqrt(var)


def spread_score(values: Iterable[float]) -> float:
    """Normalized spread: std / max(|mean|, 1)."""
    vals = [float(v) for v in values]
    if not vals:
        return 0.0
    m = mean(vals)
    return std(vals) / max(abs(m), 1.0)


def combine(models: dict[str, float]) -> tuple[float, float, float]:
    """Return (mean, std, spread_score) from {model: temp}."""
    vals = list(models.values())
    return mean(vals), std(vals), spread_score(vals)
