"""Basic cleaning utilities for OHLCV / LOB frames."""
from __future__ import annotations

import pandas as pd


def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out[~out.index.duplicated(keep="first")].sort_index()
    for c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    if "Close" in out.columns:
        out = out[out["Close"] > 0]
    if "Volume" in out.columns:
        out.loc[out["Volume"] < 0, "Volume"] = pd.NA
    return out


def lob_sanity(df: pd.DataFrame) -> dict:
    """FACT checks on LOB columns if present."""
    report = {}
    if {"ask_p_1", "bid_p_1"}.issubset(df.columns):
        crossed = (df["ask_p_1"] < df["bid_p_1"]).sum()
        locked = (df["ask_p_1"] == df["bid_p_1"]).sum()
        report["crossed_markets"] = int(crossed)
        report["locked_markets"] = int(locked)
    if "spread" in df.columns:
        report["negative_spreads"] = int((df["spread"] < 0).sum())
    return report
