"""Download LOBSTER free sample order-book files (NASDAQ TotalView-ITCH sample day)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.download_utils import RAW, download_url, update_manifest, utc_now_iso  # noqa: E402

# Public sample table from https://data.lobsterdata.com/info/DataSamples.php
# Exact sample trading date must be read from each archive's readme after download.
SAMPLES = [
    ("AMZN", 1),
    ("AMZN", 5),
    ("AMZN", 10),
    ("AAPL", 1),
    ("AAPL", 5),
    ("AAPL", 10),
    ("GOOG", 1),
    ("GOOG", 5),
    ("GOOG", 10),
    ("INTC", 1),
    ("INTC", 5),
    ("INTC", 10),
    ("MSFT", 1),
    ("MSFT", 5),
    ("MSFT", 10),
]


def sample_url(ticker: str, level: int) -> str:
    # Historical pattern used by LOBSTER sample CDN; verify HTTP status on run.
    return (
        "https://lobsterdata.com/info/Data/"
        f"{ticker}_{level}_2012-06-21.zip"
    )


def main() -> None:
    out_dir = RAW / "lobster"
    files_meta = []
    for ticker, level in SAMPLES:
        # Try documented sample path patterns
        candidates = [
            f"https://lobsterdata.com/info/Data/{ticker}_{level}_2012-06-21.zip",
            f"https://www.lobsterdata.com/info/Data/{ticker}_{level}_2012-06-21.zip",
            f"https://lobsterdata.com/info/DataSamples/{ticker}_{level}.zip",
        ]
        dest = out_dir / f"{ticker}_level{level}_sample.zip"
        got = None
        for url in candidates:
            m = download_url(url, dest)
            m["ticker"] = ticker
            m["level"] = level
            if m.get("status") == "downloaded" or m.get("status") == "skipped_exists":
                got = m
                break
            # remove empty/error file if created with 0 bytes
            if dest.exists() and dest.stat().st_size == 0:
                dest.unlink()
        if got is None:
            got = {
                "ticker": ticker,
                "level": level,
                "status": "error",
                "error": "All candidate URLs failed — see LOBSTER site for manual sample download",
                "manual_url": "https://data.lobsterdata.com/info/DataSamples.php",
                "access_date_utc": utc_now_iso(),
            }
        files_meta.append(got)

    update_manifest(
        "lobster_samples",
        {
            "dataset_name": "LOBSTER free sample LOB files",
            "provider": "LOBSTER (frischedaten UG) / NASDAQ TotalView-ITCH sample",
            "official_url": "https://data.lobsterdata.com/info/DataSamples.php",
            "original_source": "NASDAQ Historical TotalView-ITCH sample",
            "access_date_utc": utc_now_iso(),
            "timezone": "nanosecond timestamps from exchange; US equity session",
            "frequency": "event-time (message) + LOB snapshots",
            "asset_universe": "AMZN, AAPL, GOOG, INTC, MSFT (sample day only)",
            "fields": [
                "time", "event_type", "order_id", "size", "price", "direction",
                "ask_price_i", "ask_size_i", "bid_price_i", "bid_size_i",
            ],
            "licensing": "Sample for familiarization; full historical access requires LOBSTER application + NASDAQ agreement (paid/academic)",
            "methodology_documentation": "https://data.lobsterdata.com/info/Documents.php",
            "identifier_system": "NASDAQ ticker + order ID",
            "corporate_action_treatment": "Single sample day — N/A",
            "missing_data_treatment": "Dummy levels with volume 0 for unoccupied prices",
            "survivorship_bias_implications": "N/A (5 mega-cap sample)",
            "look_ahead_bias_implications": "Event-time reconstruction; do not align future messages",
            "suitability": "DIRECTLY_USABLE for method validation on LOB geometry; INSUFFICIENT for stress-event studies (wrong dates)",
            "limitation": "DATA NOT AVAILABLE for Flash Crash / COVID / etc. without paid LOBSTER access",
            "files": files_meta,
        },
    )


if __name__ == "__main__":
    main()
