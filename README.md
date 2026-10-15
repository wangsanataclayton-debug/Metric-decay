# Metric Decay of Financial Manifolds — Empirical Pipeline

Research data foundation for testing topological/geometric market hypotheses on **real** data (no fabricated observations).

## Quick start
```bash
pip install -r requirements.txt
set PYTHONPATH=.
python src/data/download_all.py
python -c "import yfinance"  # Yahoo already under data/raw/yahoo/
python src/data/build_processed.py
python src/data/download_sec_13f.py
python src/data/make_notebooks.py
```

## Status
See **`docs/DATA_ACQUISITION_SUMMARY.md`** and **`docs/RESEARCH_GAP_REPORT.md`**.

## Layout
`data/raw|interim|processed|metadata` · `src/{data,features,topology,curvature,statistics}` · `notebooks/` · `results/statistics/` · `docs/`

## Scientific guardrails
- Discrete **Ollivier–Ricci** ≠ Ricci flow
- Null results are valuable
- `Sent_AI` omitted until an observable series is validated
