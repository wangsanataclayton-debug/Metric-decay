"""Download FRED public CSV series (no API key required via fredgraph.csv)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.download_utils import RAW, download_url, update_manifest, utc_now_iso  # noqa: E402

# Graph CSV endpoint — citation required per FRED/Cboe terms for VIX.
SERIES = {
    "VIXCLS": "CBOE Volatility Index: VIX (daily close)",
    "VIX3M": "CBOE 3-Month Volatility Index",
    "OVXCLS": "CBOE Crude Oil ETF Volatility Index",
    "STLFSI4": "St. Louis Fed Financial Stress Index",
    "NFCI": "Chicago Fed National Financial Conditions Index",
    "TEDRATE": "TED Spread (discontinued series may truncate)",
    "DGS10": "10-Year Treasury Constant Maturity Rate",
    "DGS2": "2-Year Treasury Constant Maturity Rate",
    "SOFR": "Secured Overnight Financing Rate",
    "EFFR": "Effective Federal Funds Rate",
    "DTWEXBGS": "Trade Weighted U.S. Dollar Index: Broad, Goods",
    "BACTOTNSA": "Board of Governors: Bank Credit (if available)",
}


def main() -> None:
    out_dir = RAW / "fred"
    files_meta = []
    for sid, desc in SERIES.items():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        dest = out_dir / f"{sid}.csv"
        m = download_url(url, dest)
        m["series_id"] = sid
        m["description"] = desc
        files_meta.append(m)

    update_manifest(
        "fred_macro_vol",
        {
            "dataset_name": "FRED volatility & financial conditions series",
            "provider": "Federal Reserve Bank of St. Louis (FRED); underlying VIX from Cboe",
            "official_url": "https://fred.stlouisfed.org/",
            "api_endpoint": "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
            "access_date_utc": utc_now_iso(),
            "timezone": "observation_date calendar (US)",
            "frequency": "daily (or index-native)",
            "asset_universe": "indices / rates (not security panel)",
            "fields": list(SERIES.keys()),
            "licensing": "FRED terms; VIXCLS Copyrighted: Citation Required (Cboe)",
            "methodology_documentation": "https://fred.stlouisfed.org/series/VIXCLS",
            "identifier_system": "FRED series IDs",
            "corporate_action_treatment": "N/A",
            "missing_data_treatment": "FRED uses '.' for missing — parser must coerce",
            "survivorship_bias_implications": "N/A for indices",
            "look_ahead_bias_implications": "Use vintage/ALFRED if real-time information set required",
            "suitability": "DIRECTLY_USABLE",
            "files": files_meta,
        },
    )


if __name__ == "__main__":
    main()
