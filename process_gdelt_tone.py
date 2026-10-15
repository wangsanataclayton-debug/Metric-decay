"""Extract GDELT GKG tone summary as sentiment PROXY (not Sent_AI)."""
from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "gdelt"
PROC = ROOT / "data" / "processed"


def main() -> None:
    zips = list(RAW.glob("*.gkg.csv.zip"))
    if not zips:
        print("DATA NOT AVAILABLE: no GKG zip")
        return
    zpath = zips[0]
    with zipfile.ZipFile(zpath) as z:
        name = z.namelist()[0]
        # GKG is tab-separated; tone often in V2Tone field — columns vary by version
        with z.open(name) as f:
            # read limited rows
            df = pd.read_csv(f, sep="\t", header=None, nrows=5000, dtype=str, low_memory=False)
    # V2 GKG: col 15 often is V2Tone (comma-separated scores) — verify by numeric parse attempt
    tone_vals = []
    for col in df.columns:
        sample = df[col].dropna().astype(str).head(20)
        # look like "1.5,1.2,..." 
        if sample.str.contains(r"^-?\d+\.\d+,").mean() > 0.5:
            for v in df[col].dropna().astype(str):
                try:
                    tone_vals.append(float(v.split(",")[0]))
                except Exception:
                    pass
            break
    out = PROC / "gdelt_tone_proxy_sample.csv"
    if tone_vals:
        s = pd.Series(tone_vals, name="gdelt_tone")
        s.to_csv(out, index=False)
        print(out, len(s), float(s.mean()), float(s.std()))
    else:
        # save raw peek for manual mapping
        peek = RAW / "gkg_peek_head.csv"
        df.head(20).to_csv(peek, index=False)
        print("Could not auto-detect tone column; wrote", peek, "shape", df.shape)


if __name__ == "__main__":
    main()
