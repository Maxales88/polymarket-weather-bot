"""Historical temperature climatology (prior distribution)."""

from __future__ import annotations

import math
from typing import Iterable


def normal_pdf(x: float, mu: float, sigma: float) -> float:
    if sigma <= 0:
        return 0.0
    return (1.0 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def climatology_prior(mean: float, std: float, bucket_lo: float, bucket_hi: float) -> float:
    """Approximate P(temp in [lo,hi]) via trapezoidal integration of normal prior."""
    if std <= 0:
        return 0.0
    n = 200
    step = (bucket_hi - bucket_lo) / n
    if step <= 0:
        return 0.0
    s = 0.0
    for i in range(n):
        x = bucket_lo + (i + 0.5) * step
        s += normal_pdf(x, mean, std) * step
    return max(0.0, min(1.0, s))
