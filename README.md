# Polymarket Weather Trading Bot (skeleton)

Autonomous weather prediction-market bot skeleton: Gamma/CLOB/Data clients,
multi-model ensemble, Student-t bucket probability, EV scoring, Kelly sizing,
paper broker, calibration metrics, dashboard.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# fill .env
python main.py scan --limit 20
pytest -q
```

## Paper trading (default)
`PAPER_TRADING=1` (default). Live broker requires `PAPER_TRADING=0` and funded wallet.

## Geo restriction
Russia is in Polymarket's close-only list (new positions forbidden on frontend & API).
Run live only from a permitted jurisdiction. Check: `GET https://polymarket.com/api/geoblock`.
This skeleton is for research/paper trading from any location.

## Layout
See instruction document. Modules under `data/`, `signals/`, `broker/`, `metrics/`.

## Tests
`pytest -q`
