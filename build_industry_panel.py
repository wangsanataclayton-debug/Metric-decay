"""Load French daily industry returns → processed panel (no fabrication)."""
from __future__ import annotations

import zipfile
from io import StringIO
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "fama_french" / "ind49_daily.zip"
OUT = ROOT / "data" / "processed" / "ind49_daily_avg.csv"


def load_ind49_average_value_weighted() -> pd.DataFrame:
    with zipfile.ZipFile(RAW) as z:
        name = [n for n in z.namelist() if n.lower().endswith(".csv") or n.lower().endswith(".txt")][0]
        raw = z.read(name).decode("latin-1")
    # File contains multiple blocks; first block is typically Average Value Weighted Returns
    parts = raw.split("\n\n")
    block = parts[0]
    lines = block.strip().splitlines()
    # skip preamble until header with industry names / Date
    start = 0
    for i, line in enumerate(lines[:50]):
        if line.strip().lower().startswith("date") or (line[:6].isdigit() and "," in line):
            start = i
            break
        if "Average Value Weighted Returns" in line:
            start = i + 1
    # find numeric start
    for i, line in enumerate(lines):
        toks = line.split(",")
        if toks and toks[0].strip().isdigit() and len(toks[0].strip()) == 8:
            start = i - 1 if i > 0 and not lines[i - 1].split(",")[0].strip().isdigit() else i
            # if previous is header
            if i > 0 and not lines[i - 1].split(",")[0].strip().isdigit():
                header = [h.strip() for h in lines[i - 1].split(",")]
                data = "\n".join(lines[i:])
                # stop at blank or non-date
                keep = []
                for L in lines[i:]:
                    if not L.strip():
                        break
                    if not L.split(",")[0].strip()[:1].isdigit():
                        break
                    keep.append(L)
                df = pd.read_csv(StringIO(",".join(header) + "\n" + "\n".join(keep)))
            else:
                df = pd.read_csv(StringIO("\n".join(lines[i:])), header=None)
            break
    else:
        raise RuntimeError("Could not parse French 49 industry daily file")

    date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col].astype(str), format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=[date_col]).set_index(date_col)
    df = df.apply(pd.to_numeric, errors="coerce")
    # French often uses -99.99 for missing
    df = df.replace([-99.99, -999], pd.NA)
    return df


def main() -> None:
    df = load_ind49_average_value_weighted()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT)
    print(OUT, df.shape, df.index.min(), df.index.max())


if __name__ == "__main__":
    main()
