"""Create minimal analysis notebook stubs (01–11)."""
from pathlib import Path
import json

NB = Path(__file__).resolve().parents[2] / "notebooks"
NB.mkdir(exist_ok=True)

TITLES = [
    (1, "01_data_inventory", "Inventory acquired datasets and suitability codes"),
    (2, "02_cleaning", "Cleaning checks — see results/statistics/data_quality_report.html"),
    (3, "03_market_states", "Build point clouds from industry/ETF features"),
    (4, "04_persistence", "Persistent homology via src.topology.persistence"),
    (5, "05_wasserstein", "Wasserstein distances between regime diagrams"),
    (6, "06_curvature", "Discrete Ollivier–Ricci (not Ricci flow)"),
    (7, "07_effective_dimension", "Eff rank / participation ratio time series"),
    (8, "08_event_studies", "Event windows from stress_events.json"),
    (9, "09_null_models", "Nulls 1–6 — SYNTHETIC / METHOD VALIDATION ONLY where generated"),
    (10, "10_predictive_models", "Expanding-window OLS/logit incremental tests"),
    (11, "11_robustness", "Frequency, window, kNN, scaling sweeps"),
]


def nb(title: str, body: str) -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": [f"# {title}\n", "\n", f"{body}\n"]},
            {
                "cell_type": "code",
                "metadata": {},
                "outputs": [],
                "execution_count": None,
                "source": [
                    "from pathlib import Path\n",
                    "ROOT = Path('..').resolve()\n",
                    "print('Root:', ROOT)\n",
                    "print('Processed:', list((ROOT / 'data' / 'processed').glob('*.csv'))[:10])\n",
                ],
            },
        ],
    }


for _, fname, desc in TITLES:
    path = NB / f"{fname}.ipynb"
    path.write_text(json.dumps(nb(fname, desc), indent=1), encoding="utf-8")
print("wrote", len(TITLES), "notebooks")
