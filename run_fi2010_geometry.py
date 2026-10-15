"""FI-2010 LOB geometry probe — EMPIRICAL on Nordic June 2010 data (not US stress days)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.curvature.ollivier_ricci import ollivier_ricci_knn
from src.topology.persistence import compute_persistence

PROC = ROOT / "data" / "processed"
FIG = ROOT / "results" / "figures"
TAB = ROOT / "results" / "tables"
STAT = ROOT / "results" / "statistics"


def main() -> None:
    path = PROC / "fi2010_lob_sample.csv"
    df = pd.read_csv(path)
    feat = ["spread", "rel_spread", "obi", "depth_5", "dmid"]
    feat += [c for c in df.columns if c.startswith(("ask_p_", "bid_p_", "ask_v_", "bid_v_"))][:20]
    Xall = StandardScaler().fit_transform(df[feat].fillna(0).to_numpy())

    rows = []
    step, win = 50, 80
    for i in range(win, len(Xall), step):
        X = Xall[i - win : i]
        # landmark subsample
        if len(X) > 60:
            X = X[::2][:60]
        rec = {"t": i, "approx": "LOB_state_windows_subsample"}
        try:
            p = compute_persistence(X, maxdim=1)
            rec.update({"tp_h0": p.total_persistence[0], "tp_h1": p.total_persistence.get(1, np.nan)})
        except Exception as e:
            rec["tda_error"] = repr(e)
        try:
            o = ollivier_ricci_knn(X[:40], k=5)
            rec.update({"orc_mean": o.get("mean"), "orc_frac_neg": o.get("frac_negative")})
        except Exception as e:
            rec["orc_error"] = repr(e)
        rows.append(rec)
    out = pd.DataFrame(rows)
    out.to_csv(TAB / "table_fi2010_lob_topology.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 4))
    if "orc_mean" in out:
        ax.plot(out["t"], out["orc_mean"], label="ORC mean")
    if "tp_h1" in out:
        ax.plot(out["t"], out["tp_h1"], label="TP H1")
    ax.set_title("FI-2010 LOB topology/curvature (Nordic; method validation on real LOB)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "fig_fi2010_lob_geometry.png", dpi=120)
    plt.close()

    summary = {
        "claim": "EMPIRICAL RESULT",
        "market": "NASDAQ Nordic FI-2010",
        "limitation": "Not US stress-event days; LOB geometry method test only",
        "n_windows": int(len(out)),
        "orc_mean_avg": float(out["orc_mean"].mean()) if "orc_mean" in out else None,
        "tp_h1_avg": float(out["tp_h1"].mean()) if "tp_h1" in out else None,
    }
    (STAT / "fi2010_lob_topology_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
