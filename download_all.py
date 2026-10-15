"""Download publicly available empirical datasets (no fabrication)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.data.download_utils import RAW, download_url, update_manifest, utc_now_iso

FF = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv"
LOBSTER = "https://lobsterdata.com/info/Data"


def download_fama_french() -> dict:
    files = {
        "ff5_daily": f"{FF}/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip",
        "ff3_daily": f"{FF}/F-F_Research_Data_Factors_daily_CSV.zip",
        "mom_daily": f"{FF}/F-F_Momentum_Factor_daily_CSV.zip",
        "ff5_monthly": f"{FF}/F-F_Research_Data_5_Factors_2x3_CSV.zip",
        "ind49_daily": f"{FF}/49_Industry_Portfolios_Daily_CSV.zip",
    }
    outs = []
    for k, url in files.items():
        dest = RAW / "fama_french" / f"{k}.zip"
        outs.append(download_url(url, dest))
    rec = {
        "dataset_name": "Kenneth French Data Library factors & industry portfolios",
        "provider": "Kenneth R. French / Tuck Dartmouth",
        "official_url": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html",
        "access_date_utc": utc_now_iso(),
        "frequency": "daily/monthly",
        "licensing": "Free for research; cite French Data Library",
        "suitability": "DIRECTLY_USABLE",
        "downloads": outs,
    }
    update_manifest("fama_french", rec)
    return rec


def download_fred() -> dict:
    series = {
        "VIXCLS": "CBOE VIX",
        "SP500": "S&P 500",
        "DTWEXBGS": "Trade-weighted USD",
        "SOFR": "SOFR",
        "EFFR": "Effective Fed Funds",
        "TEDRATE": "TED spread (discontinued segments possible)",
        "NFCI": "Chicago Fed NFCI",
        "STLFSI4": "St Louis Financial Stress Index",
    }
    outs = []
    for sid, label in series.items():
        dest = RAW / "fred" / f"{sid}.csv"
        outs.append({**download_url(f"{FRED}?id={sid}", dest), "label": label})
    rec = {
        "dataset_name": "FRED market/stress/volatility series",
        "provider": "Federal Reserve Bank of St. Louis (FRED); VIX via Cboe",
        "official_url": "https://fred.stlouisfed.org/",
        "access_date_utc": utc_now_iso(),
        "frequency": "daily (series-dependent)",
        "licensing": "Cite FRED/Cboe; redistribution restrictions may apply to copyrighted series",
        "suitability": "DIRECTLY_USABLE",
        "downloads": outs,
    }
    update_manifest("fred", rec)
    return rec


def download_lobster_samples() -> dict:
    # Public LOBSTER samples (single day). Full history requires paid academic access.
    tickers_levels = [("AAPL", 10), ("MSFT", 10), ("INTC", 5), ("AMZN", 5), ("GOOG", 5)]
    outs = []
    for t, lvl in tickers_levels:
        url = f"{LOBSTER}/{t}_{lvl}_levels.zip"
        dest = RAW / "lobster" / f"{t}_L{lvl}.zip"
        outs.append(download_url(url, dest))
    rec = {
        "dataset_name": "LOBSTER free sample files",
        "provider": "LOBSTER (NASDAQ TotalView-ITCH reconstruction)",
        "official_url": "https://lobsterdata.com/info/DataSamples.php",
        "access_date_utc": utc_now_iso(),
        "frequency": "event-time / nanosecond message + LOB snapshots",
        "asset_universe": [t for t, _ in tickers_levels],
        "period": "single sample day (verify in zip readme; NOT stress-event days)",
        "licensing": "Sample free; full data academic subscription + NASDAQ agreements",
        "suitability": "DIRECTLY_USABLE for method validation on LOB geometry; INSUFFICIENT for event studies on stress dates",
        "downloads": outs,
        "limitation": "DATA NOT AVAILABLE freely for 2010-05-06 / 2020-03 / etc.",
    }
    update_manifest("lobster_samples", rec)
    return rec


def download_stooq_etfs() -> dict:
    tickers = [
        "spy", "qqq", "iwm", "dia", "xlf", "xlk", "xle", "xlv", "xli",
        "xlp", "xly", "xlu", "xlb", "xlre",
    ]
    outs = []
    for t in tickers:
        url = f"https://stooq.com/q/d/l/?s={t}.us&i=d"
        dest = RAW / "stooq" / f"{t}_us_d.csv"
        outs.append(download_url(url, dest, headers={"User-Agent": "Mozilla/5.0 research-bot"}))
    rec = {
        "dataset_name": "Stooq daily ETF OHLCV",
        "provider": "Stooq",
        "official_url": "https://stooq.com/",
        "access_date_utc": utc_now_iso(),
        "frequency": "daily",
        "asset_universe": [f"{t}.us" for t in tickers],
        "licensing": "Check Stooq terms; for research use",
        "suitability": "USABLE_WITH_TRANSFORM",
        "survivorship_bias": "ETF panel ≠ historical S&P 500 membership — LIMITATION",
        "downloads": outs,
    }
    update_manifest("stooq_etf", rec)
    return rec


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--only", choices=["all", "ff", "fred", "lobster", "stooq"], default="all")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if args.dry_run:
        print(json.dumps({"would_run": args.only}, indent=2))
        return
    runners = {
        "ff": download_fama_french,
        "fred": download_fred,
        "lobster": download_lobster_samples,
        "stooq": download_stooq_etfs,
    }
    if args.only == "all":
        for fn in runners.values():
            fn()
    else:
        runners[args.only]()


if __name__ == "__main__":
    main()
