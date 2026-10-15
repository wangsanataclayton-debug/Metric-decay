"""Event-study helpers around stress_events.json (no fabricated series)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "data" / "raw" / "events" / "stress_events.json"


def load_events() -> list[dict]:
    return json.loads(EVENTS.read_text(encoding="utf-8"))["events"]


def event_windows(series: pd.Series, event_date: str, offsets: list[int]) -> pd.Series:
    """Return values at event_date + offset (trading calendar = series index)."""
    idx = series.index
    # nearest date on/after event
    ed = pd.Timestamp(event_date)
    if ed not in idx:
        pos = idx.searchsorted(ed)
        if pos >= len(idx):
            return pd.Series(dtype=float)
        center = idx[pos]
    else:
        center = ed
    loc = idx.get_loc(center)
    out = {}
    for o in offsets:
        j = loc + o
        if 0 <= j < len(idx):
            out[o] = float(series.iloc[j])
        else:
            out[o] = np.nan
    return pd.Series(out, name=str(event_date))


def panel_event_study(df: pd.DataFrame, column: str, offsets=None) -> pd.DataFrame:
    offsets = offsets or [-30, -20, -10, -5, 0, 5, 10, 20, 30]
    rows = {}
    for ev in load_events():
        if "primary_date" not in ev:
            continue
        rows[ev["id"]] = event_windows(df[column], ev["primary_date"], offsets)
    return pd.DataFrame(rows).T
