"""Download Kenneth French Data Library factor files (public, no auth)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.download_utils import RAW, download_url, update_manifest, utc_now_iso  # noqa: E402

BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"

FILES = {
    "ff3_daily": "F-F_Research_Data_Factors_daily_CSV.zip",
    "ff5_daily": "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip",
    "mom_daily": "F-F_Momentum_Factor_daily_CSV.zip",
    "ff3_monthly": "F-F_Research_Data_Factors_CSV.zip",
    "ff5_monthly": "F-F_Research_Data_5_Factors_2x3_CSV.zip",
    "industry_49_daily": "49_Industry_Portfolios_Daily_CSV.zip",
}


def main() -> None:
    out_dir = RAW / "fama_french"
    files_meta = []
    for key, fname in FILES.items():
        url = BASE + fname
        dest = out_dir / fname
        m = download_url(url, dest)
        m["key"] = key
        files_meta.append(m)

    update_manifest(
        "ken_french_factors",
        {
            "dataset_name": "Kenneth French Data Library — factors & industry portfolios",
            "provider": "Kenneth R. French / Tuck School of Business, Dartmouth",
            "official_url": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html",
            "download_base": BASE,
            "access_date_utc": utc_now_iso(),
            "timezone": "calendar dates (US market convention; no intraday)",
            "frequency": "daily and monthly",
            "asset_universe": "US factor portfolios / 49 industries",
            "fields": ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF", "Mom", "industry returns"],
            "licensing": "Free for academic research; cite French Data Library",
            "methodology_url": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html",
            "identifier_system": "portfolio names (not CUSIP)",
            "corporate_action_treatment": "returns constructed from CRSP; see French documentation",
            "missing_data_treatment": "blank / -99.99 sentinels in raw files — cleaner must handle",
            "survivorship_bias_implications": "Factor construction uses CRSP delisting with standard FF rules; still not full CRSP security panel",
            "look_ahead_bias_implications": "Use formation rules as documented; do not peek at future portfolio assignments",
            "suitability": "DIRECTLY_USABLE",
            "files": files_meta,
        },
    )


if __name__ == "__main__":
    main()
