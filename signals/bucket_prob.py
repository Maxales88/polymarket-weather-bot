"""Bucket probability via Student-t (fat tails) integration over [lo, hi]."""

from __future__ import annotations

import math


def student_t_pdf(x: float, df: int, loc: float, scale: float) -> float:
    if scale <= 0 or df <= 0:
        return 0.0
    z = (x - loc) / scale
    # Student-t pdf
    from math import gamma, pi
    coef = gamma((df + 1) / 2) / (math.sqrt(df * pi) * gamma(df / 2) * scale)
    return coef * (1 + z * z / df) ** (-(df + 1) / 2)


def bucket_probability(mean: float, std: float, lo: float, hi: float, df: int = 4) -> float:
    """P(actual_high in [lo, hi]) integrating Student-t over the bucket."""
    if std <= 0 or hi <= lo:
        return 0.0
    n = 400
    step = (hi - lo) / n
    s = 0.0
    for i in range(n):
        x = lo + (i + 0.5) * step
        s += student_t_pdf(x, df, mean, std) * step
    return max(0.0, min(1.0, s))
