"""NOAA ASOS station observations (historical + realtime)."""

from __future__ import annotations

import requests

IEM_ASOS_URL = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"


def fetch_asos(station: str, start: str, end: str) -> list[dict]:
    """Fetch ASOS observations for an ICAO station. Returns list of records (skeleton)."""
    params = {
        "station": station,
        "data": "tmpf",
        "year1": start[:4], "month1": start[5:7], "day1": start[8:10],
        "year2": end[:4], "month2": end[5:7], "day2": end[8:10],
        "tz": "UTC", "format": "json",
    }
    try:
        r = requests.get(IEM_ASOS_URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("data", []) if isinstance(data, dict) else []
    except Exception:
        return []


def latest_observation(station: str) -> float | None:
    """Return latest temperature (°C) for station, or None."""
    try:
        r = requests.get(
            f"https://api.weather.gov/stations/{station}/observations/latest",
            timeout=15,
            headers={"User-Agent": "polymarket-weather-bot"},
        )
        r.raise_for_status()
        data = r.json()
        temp_c = data.get("properties", {}).get("temperature", {}).get("value")
        return float(temp_c) if temp_c is not None else None
    except Exception:
        return None
