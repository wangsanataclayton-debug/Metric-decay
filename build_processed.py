"""Build cleaned panels, dependence series, quality report, availability matrix."""
from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim"
RESULTS = ROOT / "results" / "statistics"
DOCS = ROOT / "docs"

for p in (PROC, INTERIM, RESULTS, DOCS):
    p.mkdir(parents=True, exist_ok=True)


def load_ind49() -> pd.DataFrame:
    zpath = RAW / "fama_french" / "ind49_daily.zip"
    with zipfile.ZipFile(zpath) as z:
        name = z.namelist()[0]
        text = z.read(name).decode("latin-1")
    # First table: Average Value Weighted Returns — ends before Equal Weighted or blank section title
    lines = text.splitlines()
    # find first YYYYMMDD line
    i0 = next(i for i, L in enumerate(lines) if L[:8].isdigit() and "," in L)
    header = [h.strip() for h in lines[i0 - 1].split(",")]
    rows = []
    for L in lines[i0:]:
        if not L.strip() or not L[:1].isdigit():
            break
        if "Average Equal" in L or "Number of Firms" in L:
            break
        rows.append(L)
    df = pd.read_csv(StringIO(",".join(header) + "\n" + "\n".join(rows)))
    dc = df.columns[0]
    df[dc] = pd.to_datetime(df[dc].astype(str), format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=[dc]).set_index(dc)
    df = df.apply(pd.to_numeric, errors="coerce").replace([-99.99, -999], np.nan)
    return df


def load_ff5_daily() -> pd.DataFrame:
    zpath = RAW / "fama_french" / "ff5_daily.zip"
    with zipfile.ZipFile(zpath) as z:
        name = z.namelist()[0]
        text = z.read(name).decode("latin-1")
    lines = text.splitlines()
    i0 = next(i for i, L in enumerate(lines) if L[:8].isdigit() and "," in L)
    header = [h.strip() for h in lines[i0 - 1].split(",")]
    rows = []
    for L in lines[i0:]:
        if not L.strip() or not L[:1].isdigit() or len(L.split(",")[0].strip()) != 8:
            break
        rows.append(L)
    df = pd.read_csv(StringIO(",".join(header) + "\n" + "\n".join(rows)))
    dc = df.columns[0]
    df[dc] = pd.to_datetime(df[dc].astype(str), format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=[dc]).set_index(dc)
    return df.apply(pd.to_numeric, errors="coerce") / 100.0  # percent -> decimal


def load_yahoo_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    prices = {}
    for f in sorted((RAW / "yahoo").glob("*_daily.csv")):
        t = f.name.replace("_daily.csv", "")
        d = pd.read_csv(f, parse_dates=[0], index_col=0)
        col = "Close" if "Close" in d.columns else d.columns[0]
        prices[t] = d[col]
    px = pd.DataFrame(prices).sort_index()
    rets = px.pct_change()
    return px, rets


def load_fred() -> dict[str, pd.DataFrame]:
    out = {}
    for f in (RAW / "fred").glob("*.csv"):
        d = pd.read_csv(f)
        d.columns = ["date", f.stem]
        d["date"] = pd.to_datetime(d["date"], errors="coerce")
        d = d.dropna(subset=["date"]).set_index("date")
        d[f.stem] = pd.to_numeric(d[f.stem], errors="coerce")
        out[f.stem] = d
    return out


def rolling_dep(returns: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    import sys

    sys.path.insert(0, str(ROOT))
    from src.features.dependence import rolling_corr_stats

    return rolling_corr_stats(returns, window)


def quality_checks() -> dict:
    report: dict = {"generated_utc": datetime.now(timezone.utc).isoformat(), "datasets": {}}

    ind = load_ind49()
    ind.to_csv(PROC / "ind49_daily_vw_returns_pct.csv")
    report["datasets"]["ind49"] = {
        "rows": int(len(ind)),
        "cols": int(ind.shape[1]),
        "start": str(ind.index.min().date()),
        "end": str(ind.index.max().date()),
        "missing_frac": float(ind.isna().mean().mean()),
        "duplicate_index": int(ind.index.duplicated().sum()),
        "neg99_style_missing_replaced": True,
    }

    ff5 = load_ff5_daily()
    ff5.to_csv(PROC / "ff5_daily.csv")
    report["datasets"]["ff5_daily"] = {
        "rows": int(len(ff5)),
        "cols": int(ff5.shape[1]),
        "start": str(ff5.index.min().date()),
        "end": str(ff5.index.max().date()),
        "missing_frac": float(ff5.isna().mean().mean()),
        "duplicate_index": int(ff5.index.duplicated().sum()),
    }

    px, rets = load_yahoo_panel()
    px.to_csv(PROC / "yahoo_etf_prices.csv")
    rets.to_csv(PROC / "yahoo_etf_returns.csv")
    report["datasets"]["yahoo_etf"] = {
        "rows": int(len(px)),
        "tickers": list(px.columns),
        "start": str(px.index.min().date()),
        "end": str(px.index.max().date()),
        "missing_frac_prices": float(px.isna().mean().mean()),
        "impossible_nonpositive_prices": int((px <= 0).sum().sum()),
        "duplicate_index": int(px.index.duplicated().sum()),
    }

    fred = load_fred()
    for k, d in fred.items():
        d.to_csv(PROC / f"fred_{k}.csv")
        report["datasets"][f"fred_{k}"] = {
            "rows": int(len(d)),
            "start": str(d.index.min().date()),
            "end": str(d.index.max().date()),
            "missing_frac": float(d.isna().mean().mean()),
        }

    # dependence on industries 2007-2024
    ind_use = ind.loc["2007":"2024"].dropna(axis=1, how="all")
    # convert pct to decimal-like for corr (scale invariant for corr)
    dep = rolling_dep(ind_use, 60)
    dep.to_csv(PROC / "ind49_rolling_dependence_w60.csv")
    report["datasets"]["ind49_dependence_w60"] = {
        "rows": int(len(dep)),
        "start": str(dep.index.min().date()) if len(dep) else None,
        "end": str(dep.index.max().date()) if len(dep) else None,
    }

    # ETF dependence
    etf_cols = [c for c in rets.columns if c not in ("GME", "AMC", "XLRE")]
    dep_e = rolling_dep(rets[etf_cols].loc["2007":"2024"], 60)
    dep_e.to_csv(PROC / "yahoo_etf_rolling_dependence_w60.csv")

    # LOBSTER/Stooq status
    lob = list((RAW / "lobster").glob("*.zip"))
    report["datasets"]["lobster_attempt"] = {
        "files": len(lob),
        "status": "INSUFFICIENT — HTML stubs not LOB data",
        "bytes": [p.stat().st_size for p in lob],
    }
    stooq = list((RAW / "stooq").glob("*.csv"))
    report["datasets"]["stooq_attempt"] = {
        "files": len(stooq),
        "status": "INSUFFICIENT — JS challenge HTML",
    }

    (RESULTS / "data_quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    # simple HTML
    rows_html = []
    for name, meta in report["datasets"].items():
        rows_html.append(f"<tr><td>{name}</td><td><pre>{json.dumps(meta, indent=2)}</pre></td></tr>")
    html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>Data Quality Report</title>
    <style>body{{font-family:system-ui;margin:2rem}} table{{border-collapse:collapse}} td,th{{border:1px solid #ccc;padding:.5rem;vertical-align:top}}</style>
    </head><body>
    <h1>Data Quality Report</h1>
    <p>Generated {report['generated_utc']} — FACT checks only; no fabricated observations.</p>
    <table><tr><th>Dataset</th><th>Checks</th></tr>
    {''.join(rows_html)}
    </table></body></html>"""
    (RESULTS / "data_quality_report.html").write_text(html, encoding="utf-8")
    return report


def write_availability_matrix() -> None:
    rows = [
        # variable, dataset, direct/proxy, frequency, coverage, quality, missingness
        ["bid/ask/sizes (LOB)", "LOBSTER samples", "DATA NOT AVAILABLE (auto)", "event", "n/a", "INSUFFICIENT", "n/a"],
        ["spread/OBI/depth", "LOBSTER", "derived if LOB acquired", "event", "blocked", "INACCESSIBLE publicly for stress days", "n/a"],
        ["ETF OHLCV", "Yahoo Finance", "Direct", "daily", "2007-2024", "usable", "XLRE starts 2015"],
        ["ETF returns", "derived Yahoo", "Derived", "daily", "2007-2024", "usable", "first row NA"],
        ["industry returns", "French 49 Ind", "Direct", "daily", "long history→2024+", "usable", "-99.99→NA"],
        ["FF5/MOM factors", "French library", "Direct", "daily", "long history", "usable", "low"],
        ["VIX", "FRED VIXCLS", "Direct", "daily", "1990+", "usable", "weekends/holidays absent"],
        ["financial stress", "FRED NFCI/STLFSI4", "Direct/proxy", "weekly/daily", "series-dependent", "usable", "varies"],
        ["repo rates", "FRED SOFR/EFFR", "Direct", "daily", "SOFR from 2018", "usable", "pre-2018 SOFR NA"],
        ["avg corr / eff rank", "derived ind49/ETF", "Derived", "rolling daily", "2007-2024", "usable", "window warmup"],
        ["persistence/W1/ORC", "computed objects", "Derived", "windowed", "needs point clouds", "code ready; empirics pending LOB/panels", "n/a"],
        ["holdings similarity", "SEC 13F", "PROXY (low-freq)", "quarterly", "EDGAR public", "ingestion stub only", "not downloaded"],
        ["Sent_AI", "—", "DATA NOT AVAILABLE", "—", "—", "omit or GDELT PROXY later", "n/a"],
        ["hist. S&P membership", "CRSP/WRDS", "DATA NOT AVAILABLE here", "daily", "—", "INACCESSIBLE without WRDS", "survivorship risk if ignored"],
    ]
    df = pd.DataFrame(
        rows,
        columns=["research_variable", "dataset", "direct_or_proxy", "frequency", "historical_coverage", "quality", "missingness"],
    )
    df.to_csv(DOCS / "DATA_AVAILABILITY_MATRIX.csv", index=False)
    df.to_markdown(DOCS / "DATA_AVAILABILITY_MATRIX.md", index=False)


def main() -> None:
    report = quality_checks()
    write_availability_matrix()
    print(json.dumps({k: {a: b for a, b in v.items() if a != "tickers"} for k, v in report["datasets"].items()}, indent=2))


if __name__ == "__main__":
    main()
