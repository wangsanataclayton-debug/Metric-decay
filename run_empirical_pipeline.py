"""
End-to-end daily empirical pass on acquired data.
Produces tables/figures for dependence, topology, curvature, events, nulls, prediction.
Never fabricates market observations; null-model draws are labeled SYNTHETIC.
"""
from __future__ import annotations

import json
import sys
import warnings
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
from src.features.dependence import ach_mean_abs_corr, rolling_corr_stats
from src.statistics.event_study import load_events, panel_event_study
from src.statistics.lead_lag import lead_lag_corr
from src.statistics.null_models import (
    null_correlation_only,
    null_permutation,
    null_time_shift,
    null_volatility_only,
)
from src.statistics.predictive import ols_predict
from src.topology.persistence import compute_persistence, wasserstein_diagrams

PROC = ROOT / "data" / "processed"
FIG = ROOT / "results" / "figures"
TAB = ROOT / "results" / "tables"
STAT = ROOT / "results" / "statistics"
for p in (FIG, TAB, STAT):
    p.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(42)


def load_panels():
    ind = pd.read_csv(PROC / "ind49_daily_vw_returns_pct.csv", index_col=0, parse_dates=True)
    ind = ind.replace([-99.99, -999], np.nan).loc["2007":"2024"]
    dep = pd.read_csv(PROC / "ind49_rolling_dependence_w60.csv", index_col=0, parse_dates=True)
    vix = pd.read_csv(PROC / "fred_VIXCLS.csv", index_col=0, parse_dates=True)
    etf = pd.read_csv(PROC / "yahoo_etf_returns.csv", index_col=0, parse_dates=True)
    return ind, dep, vix, etf


def point_cloud_from_window(R: pd.DataFrame) -> np.ndarray:
    """Each asset = point; features = [mean, std, skew-ish, last] over window. z-scored."""
    X = np.column_stack(
        [
            R.mean(axis=0).to_numpy(),
            R.std(axis=0).to_numpy(),
            R.iloc[-1].to_numpy(),
            R.mean(axis=0).abs().to_numpy(),
        ]
    )
    X = np.nan_to_num(X, nan=0.0)
    return StandardScaler().fit_transform(X)


def topology_curvature_series(ind: pd.DataFrame, step: int = 63, window: int = 60, k: int = 5) -> pd.DataFrame:
    """COST CONTROL (documented): month-ish steps, <=25 landmarks, H1 only, k=5 ORC."""
    rows = []
    cols = [c for c in ind.columns if ind[c].notna().mean() > 0.9]
    R = ind[cols]
    dates = R.index
    # prefer month-ends
    month_ends = R.groupby([R.index.year, R.index.month]).tail(1).index
    targets = [d for d in month_ends if d >= dates[window - 1]]
    if len(targets) < 10:
        targets = list(dates[window - 1 :: step])
    for d in targets:
        i = dates.get_loc(d)
        if isinstance(i, slice):
            continue
        block = R.iloc[i - window + 1 : i + 1].dropna(axis=1)
        if block.shape[1] < 15:
            continue
        X = point_cloud_from_window(block)
        if X.shape[0] > 25:
            idx = RNG.choice(X.shape[0], size=25, replace=False)
            X = X[idx]
            approx = "subsample_25_assets_monthly"
        else:
            approx = "monthly"
        rec = {
            "date": dates[i],
            "n_assets": int(block.shape[1]),
            "approximation": approx,
            "ach": ach_mean_abs_corr(block.to_numpy()),
        }
        try:
            pers = compute_persistence(X, maxdim=1)
            rec["tp_h0"] = pers.total_persistence.get(0, np.nan)
            rec["tp_h1"] = pers.total_persistence.get(1, np.nan)
            rec["max_h1"] = pers.max_persistence.get(1, np.nan)
            rec["ent_h1"] = pers.entropy.get(1, np.nan)
            rec["tda_backend"] = pers.backend
            rec["_dgm1"] = pers.diagrams[1] if len(pers.diagrams) > 1 else np.zeros((0, 2))
        except Exception as e:
            rec["tda_error"] = repr(e)
        try:
            orc = ollivier_ricci_knn(X, k=min(k, max(X.shape[0] - 1, 1)), alpha=0.5)
            for key in ("mean", "median", "q10", "frac_negative", "min", "variance"):
                rec[f"orc_{key}"] = orc.get(key, np.nan)
        except Exception as e:
            rec["orc_error"] = repr(e)
        rows.append(rec)
    df = pd.DataFrame(rows).set_index("date")
    # Wasserstein to first calm baseline diagram
    baseline = None
    w1s = []
    for _, row in df.iterrows():
        dgm = row.get("_dgm1")
        if not isinstance(dgm, np.ndarray):
            w1s.append(np.nan)
            continue
        if baseline is None and isinstance(dgm, np.ndarray) and dgm.size > 0:
            baseline = dgm
        if baseline is None or dgm.size == 0:
            w1s.append(np.nan)
            continue
        try:
            w1s.append(wasserstein_diagrams(baseline, dgm, order=1.0))
        except Exception:
            w1s.append(np.nan)
    df["w1_h1_vs_baseline"] = w1s
    return df.drop(columns=[c for c in df.columns if c.startswith("_")], errors="ignore")


def run_null_comparison(ind: pd.DataFrame, n_draw: int = 20) -> pd.DataFrame:
    """Compare mean |corr| under nulls vs empirical on a fixed window. SYNTHETIC draws labeled."""
    block = ind.loc["2019-01-02":"2019-03-29"].dropna(axis=1)
    X = block.to_numpy(dtype=float)
    emp = ach_mean_abs_corr(X)
    rows = [{"model": "empirical", "mean_abs_corr": emp, "claim": "EMPIRICAL RESULT"}]
    for name, fn in [
        ("null_volatility_only", null_volatility_only),
        ("null_correlation_only", null_correlation_only),
        ("null_permutation", null_permutation),
        ("null_time_shift", null_time_shift),
    ]:
        vals = []
        for _ in range(n_draw):
            Y = fn(X, RNG)
            vals.append(ach_mean_abs_corr(Y))
        rows.append(
            {
                "model": name,
                "mean_abs_corr": float(np.mean(vals)),
                "std": float(np.std(vals)),
                "claim": "SYNTHETIC / METHOD VALIDATION ONLY",
            }
        )
    return pd.DataFrame(rows)


def run_predictive(dep: pd.DataFrame, vix: pd.DataFrame) -> dict:
    d = dep.join(vix, how="inner").dropna()
    d["stress"] = (d["VIXCLS"] > d["VIXCLS"].rolling(252, min_periods=50).quantile(0.9)).astype(float)
    d["y_vix"] = d["VIXCLS"]
    out = {}
    out["A_vol_proxy"] = ols_predict(d, "y_vix", ["pc1_share"], h=5)
    out["B_vol_corr"] = ols_predict(d, "y_vix", ["pc1_share", "avg_abs_corr"], h=5)
    out["C_dim"] = ols_predict(d, "y_vix", ["pc1_share", "avg_abs_corr", "eff_rank"], h=5)
    # next-day VIX change
    d["dvix"] = d["VIXCLS"].diff()
    out["dvix_from_effrank"] = ols_predict(d.dropna(), "dvix", ["eff_rank", "avg_abs_corr"], h=1)
    return out


def make_figures(dep, topo, vix):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dep.index, dep["eff_rank"], label="eff_rank", lw=0.8)
    ax.plot(dep.index, dep["avg_abs_corr"] * 10, label="avg_abs_corr×10", lw=0.8)
    ax.set_title("Figure 2/3 — Effective rank & correlation (industries)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "fig02_03_effrank_corr.png", dpi=120)
    plt.close()

    if len(topo):
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(topo.index, topo.get("orc_mean"), label="ORC mean", lw=0.8)
        ax.plot(topo.index, topo.get("orc_frac_negative"), label="ORC frac neg", lw=0.8)
        ax.set_title("Figure 7/8 — Discrete Ollivier–Ricci (daily industry clouds)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG / "fig07_08_orc.png", dpi=120)
        plt.close()

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(topo.index, topo.get("w1_h1_vs_baseline"), label="W1 H1 vs baseline", lw=0.8)
        ax.plot(topo.index, topo.get("tp_h1"), label="total pers H1", lw=0.8)
        ax.set_title("Figure 5/6 — Persistence / Wasserstein")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG / "fig05_06_persistence_w1.png", dpi=120)
        plt.close()

    # event study plot
    es = panel_event_study(dep, "eff_rank")
    fig, ax = plt.subplots(figsize=(8, 4))
    for idx, row in es.iterrows():
        ax.plot(row.index.astype(int), row.values, marker="o", label=idx, lw=1)
    ax.axvline(0, color="k", ls="--", lw=0.8)
    ax.set_title("Figure 10 — Eff rank around stress events")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / "fig10_event_effrank.png", dpi=120)
    plt.close()

    # vs VIX
    j = dep.join(vix, how="inner").dropna()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(j["VIXCLS"], j["eff_rank"], s=3, alpha=0.3)
    ax.set_xlabel("VIX")
    ax.set_ylabel("eff_rank")
    ax.set_title("Figure 12 — Topology proxy vs VIX")
    fig.tight_layout()
    fig.savefig(FIG / "fig12_effrank_vs_vix.png", dpi=120)
    plt.close()


def fi2010_lob_probe():
    """If FI-2010 extracted, compute ORC/persistence on LOB state vectors (method validation)."""
    path = ROOT / "data" / "raw" / "fi2010" / "extracted" / "Train_Dst_NoAuction_DecPre_CF_7.txt"
    if not path.exists():
        return {"status": "DATA NOT AVAILABLE yet"}
    # File is features x time in DeepLOB convention
    data = np.loadtxt(path)
    if data.shape[0] < data.shape[1]:
        # features x T
        lob = data[:40, :2000].T  # first 40 = 10-level ask/bid price/vol typically
    else:
        lob = data[:2000, :40]
    # rolling clouds of 50 consecutive LOB states as points? Better: each row is a state point
    X = StandardScaler().fit_transform(lob[::10][:200])  # subsample states
    out = {"n_points": int(X.shape[0]), "dim": int(X.shape[1]), "claim": "EMPIRICAL RESULT on FI-2010 Nordic LOB"}
    try:
        pers = compute_persistence(X[:100], maxdim=1)
        out["tp_h0"] = pers.total_persistence[0]
        out["tp_h1"] = pers.total_persistence.get(1, np.nan)
        out["backend"] = pers.backend
    except Exception as e:
        out["tda_error"] = repr(e)
    try:
        orc = ollivier_ricci_knn(X[:80], k=10)
        out["orc_mean"] = orc.get("mean")
        out["orc_frac_negative"] = orc.get("frac_negative")
    except Exception as e:
        out["orc_error"] = repr(e)
    return out


def main():
    warnings.filterwarnings("ignore")
    ind, dep, vix, etf = load_panels()

    # summary stats table
    summary = dep.describe().T
    summary.to_csv(TAB / "table02_dependence_summary.csv")

    events = pd.DataFrame(load_events())
    events.to_csv(TAB / "table03_events.csv", index=False)

    es_eff = panel_event_study(dep, "eff_rank")
    es_corr = panel_event_study(dep, "avg_abs_corr")
    es_eff.to_csv(TAB / "table04_event_eff_rank.csv")
    es_corr.to_csv(TAB / "table_event_avg_abs_corr.csv")

    print("Computing topology/curvature series (monthly, 25 landmarks)...")
    topo = topology_curvature_series(ind, step=63, window=60, k=5)
    topo.to_csv(PROC / "ind49_topology_curvature_series.csv")
    topo.drop(columns=[c for c in topo.columns if "error" in c], errors="ignore").describe().T.to_csv(
        TAB / "table05_06_persistence_curvature_summary.csv"
    )

    nulls = run_null_comparison(ind)
    nulls.to_csv(TAB / "table09_null_models.csv", index=False)

    pred = run_predictive(dep, vix)
    (TAB / "table08_predictive.json").write_text(json.dumps(pred, indent=2), encoding="utf-8")

    # lead-lag eff_rank vs future VIX
    j = dep.join(vix, how="inner").dropna()
    ll = lead_lag_corr(j["eff_rank"], j["VIXCLS"], tau_min=-60, tau_max=60)
    ll.to_csv(TAB / "table07_leadlag_effrank_vix.csv", index=False)
    best = ll.dropna().sort_values("corr", key=lambda s: s.abs(), ascending=False).head(1)
    (STAT / "leadlag_best.json").write_text(best.to_json(orient="records"), encoding="utf-8")

    make_figures(dep, topo, vix)

    fi = fi2010_lob_probe()
    (STAT / "fi2010_lob_probe.json").write_text(json.dumps(fi, indent=2, default=str), encoding="utf-8")

    # robustness small grid
    rob = []
    for w in (30, 60, 120):
        d = rolling_corr_stats(ind.dropna(axis=1), w)
        rob.append({"window": w, "mean_eff_rank": float(d["eff_rank"].mean()), "mean_abs_corr": float(d["avg_abs_corr"].mean())})
    pd.DataFrame(rob).to_csv(TAB / "table10_robustness_windows.csv", index=False)

    report = {
        "claim_note": "Results are EMPIRICAL RESULT / ESTIMATE on daily public data unless marked SYNTHETIC",
        "topo_rows": int(len(topo)),
        "predictive": pred,
        "nulls": nulls.to_dict(orient="records"),
        "fi2010_probe": fi,
        "best_leadlag": json.loads(best.to_json(orient="records")),
    }
    (STAT / "empirical_run_summary.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("topo_rows", "fi2010_probe")}, indent=2, default=str))
    print("predictive", pred)
    print("Wrote figures to", FIG)


if __name__ == "__main__":
    main()
