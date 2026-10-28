"""Open-Meteo multi-model forecast fetcher (GFS, ECMWF, ICON, GEM, Météo-France)."""

from __future__ import annotations

from typing import Any

import requests

OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"
OPENMETEO_ENSEMBLE_URL = "https://ensemble-api.open-meteo.com/v1/ensemble"

MODELS = ["gfs", "ecmwf_ifs", "icon", "gem", "meteofrance"]


def fetch_forecast(lat: float, lon: float, model: str = "gfs") -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "models": model,
    }
    r = requests.get(OPENMETEO_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def fetch_ensemble(lat: float, lon: float) -> dict[str, list[float]]:
    """Return per-model daily max temperature arrays (skeleton)."""
    out: dict[str, list[float]] = {}
    for m in MODELS:
        try:
            data = fetch_forecast(lat, lon, m)
            daily = data.get("daily", {})
            vals = daily.get("temperature_2m_max", [])
            out[m] = [float(v) for v in vals if v is not None]
        except Exception:
            out[m] = []
    return out


def ensemble_stats(values_by_model: dict[str, list[float]], day_index: int = 0) -> tuple[float, float]:
    """Mean and std of daily max across models for a given day index."""
    vals = []
    for m, arr in values_by_model.items():
        if len(arr) > day_index:
            vals.append(arr[day_index])
    if not vals:
        return 0.0, 0.0
    import statistics
    mean = statistics.fmean(vals)
    std = statistics.pstdev(vals) if len(vals) > 1 else 0.0
    return mean, std
