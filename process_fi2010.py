"""Parse FI-2010 LOB features into processed parquet/csv samples + liquidity metrics."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "fi2010" / "extracted"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

# Ntakaris / FI-2010 feature layout (first 40): 10 levels ask/bid price & volume
# a1,v_a1,b1,v_b1,...,a10,v_a10,b10,v_b10  (confirm in paper; DeepLOB uses this convention)


def lob_columns(k: int = 10) -> list[str]:
    cols = []
    for i in range(1, k + 1):
        cols += [f"ask_p_{i}", f"ask_v_{i}", f"bid_p_{i}", f"bid_v_{i}"]
    return cols


def load_train(max_cols: int = 5000) -> pd.DataFrame:
    path = RAW / "Train_Dst_NoAuction_DecPre_CF_7.txt"
    data = np.loadtxt(path)  # typically (features, time)
    if data.shape[0] < data.shape[1]:
        X = data[:, :max_cols].T
    else:
        X = data[:max_cols, :]
    cols = lob_columns(10)
    # keep first 40 LOB + extras as feat_*
    n = X.shape[1]
    names = cols + [f"feat_{i}" for i in range(40, n)]
    df = pd.DataFrame(X, columns=names[:n])
    return df


def add_liquidity(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["spread"] = out["ask_p_1"] - out["bid_p_1"]
    mid = (out["ask_p_1"] + out["bid_p_1"]) / 2.0
    out["rel_spread"] = out["spread"] / mid.replace(0, np.nan)
    out["obi"] = (out["bid_v_1"] - out["ask_v_1"]) / (out["bid_v_1"] + out["ask_v_1"]).replace(0, np.nan)
    out["depth_5"] = out[[f"bid_v_{i}" for i in range(1, 6)]].sum(axis=1) + out[
        [f"ask_v_{i}" for i in range(1, 6)]
    ].sum(axis=1)
    out["mid"] = mid
    out["dmid"] = mid.diff()
    return out


def main() -> None:
    df = load_train(8000)
    df = add_liquidity(df)
    # sample for topology (full train is huge)
    sample = df.iloc[::5].reset_index(drop=True)
    out = PROC / "fi2010_lob_sample.csv"
    sample.to_csv(out, index=False)
    meta = {
        "rows_sample": int(len(sample)),
        "cols": list(sample.columns[:45]),
        "source_file": "Train_Dst_NoAuction_DecPre_CF_7.txt",
        "access_date_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Nordic FI-2010; liquidity fields derived; not US stress events",
    }
    (PROC / "fi2010_lob_sample_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(out, sample.shape, sample[["spread", "obi", "depth_5"]].describe().to_string())


if __name__ == "__main__":
    main()
