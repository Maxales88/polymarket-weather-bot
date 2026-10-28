"""Calibration metrics: Brier, Platt scaling, isotonic."""

from __future__ import annotations

import math
from typing import Iterable


def brier_score(preds: Iterable[float], outcomes: Iterable[float]) -> float:
    pairs = list(zip(preds, outcomes))
    if not pairs:
        return float("nan")
    return sum((p - o) ** 2 for p, o in pairs) / len(pairs)


def logit(p: float) -> float:
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1 - p))


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    z = math.exp(x)
    return z / (1 + z)


def platt_calibrate(p: float, alpha: float = 1.3) -> float:
    return sigmoid(alpha * logit(p))


def find_best_alpha(preds: Iterable[float], outcomes: Iterable[float],
                    grid: Iterable[float] = (i * 0.05 + 0.8 for i in range(35))) -> float:
    best_a, best_b = 1.0, float("inf")
    for a in grid:
        bs = brier_score([platt_calibrate(p, a) for p in preds], outcomes)
        if bs < best_b:
            best_b, best_a = bs, a
    return best_a


def calibration_slope(preds: Iterable[float], outcomes: Iterable[float]) -> float:
    """Mincer-Zarnowitz slope: regress outcome on predicted. Returns slope (ideal ~1)."""
    ps = list(preds)
    os_ = list(outcomes)
    n = len(ps)
    if n < 2:
        return float("nan")
    mean_p = sum(ps) / n
    mean_o = sum(os_) / n
    cov = sum((ps[i] - mean_p) * (os_[i] - mean_o) for i in range(n))
    var_p = sum((p - mean_p) ** 2 for p in ps)
    if var_p == 0:
        return float("nan")
    return cov / var_p


def isotonic_available() -> bool:
    try:
        import sklearn  # noqa
        return True
    except ImportError:
        return False
