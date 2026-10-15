"""Download FI-2010 LOB benchmark (DeepLOB mirror of Ntakaris et al.)."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.data.download_utils import RAW, download_url, update_manifest, utc_now_iso

URL = (
    "https://raw.githubusercontent.com/zcakhaa/"
    "DeepLOB-Deep-Convolutional-Neural-Networks-for-Limit-Order-Books/"
    "master/data/data.zip"
)


def main() -> None:
    dest = RAW / "fi2010" / "deeplob_fi2010_data.zip"
    meta = download_url(URL, dest, timeout=300)
    extract_dir = RAW / "fi2010" / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    files = []
    if dest.exists() and dest.stat().st_size > 1000:
        try:
            with zipfile.ZipFile(dest) as z:
                z.extractall(extract_dir)
                files = z.namelist()
            meta["extract_ok"] = True
            meta["extracted_files"] = files
        except zipfile.BadZipFile as e:
            meta["extract_ok"] = False
            meta["error"] = repr(e)
    rec = {
        "dataset_name": "FI-2010 Limit Order Book benchmark (via DeepLOB redistribution)",
        "provider": "Ntakaris et al. (2018); mirrored in DeepLOB repo",
        "official_url": "https://etsin.fairdata.fi/dataset/73eb48d7-4dbc-4a10-a52a-da745b47a649",
        "download_url": URL,
        "original_source": "NASDAQ Nordic / Helsinki equities LOB reconstruction",
        "access_date_utc": utc_now_iso(),
        "frequency": "event-based LOB snapshots (10 levels)",
        "period": "1–14 June 2010 (10 business days), 5 Finnish stocks",
        "licensing": "Academic benchmark; cite Ntakaris et al. J Forecasting 2018",
        "suitability": "DIRECTLY_USABLE for LOB topology method tests; NOT US stress-event days",
        "limitation": "Nordic market June 2010 — proxy for LOB geometry, not US Flash Crash",
        "download": meta,
        "extracted_files": files,
    }
    update_manifest("fi2010", rec)
    print(rec["suitability"], dest, dest.stat().st_size if dest.exists() else None, len(files))


if __name__ == "__main__":
    main()
