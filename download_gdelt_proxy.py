"""GDELT DOC 2.1 tone proxy — optional sentiment replacement for Sent_AI.

Downloads a small recent/historical export if reachable; otherwise records DATA NOT AVAILABLE.
Does NOT fabricate Sent_AI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.data.download_utils import RAW, download_url, update_manifest, utc_now_iso

# GDELT 2.0 DOC API example — may rate-limit; treat failures honestly
# Master file list:
LAST_UPDATE = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"


def main() -> None:
    dest_dir = RAW / "gdelt"
    dest_dir.mkdir(parents=True, exist_ok=True)
    meta = download_url(LAST_UPDATE, dest_dir / "lastupdate.txt", timeout=60)
    files = []
    if meta.get("status") == "downloaded":
        text = (dest_dir / "lastupdate.txt").read_text(encoding="utf-8", errors="ignore")
        # pick first gkg csv zip if present
        for line in text.splitlines():
            parts = line.split()
            if len(parts) >= 3 and "gkg.csv.zip" in parts[2]:
                url = parts[2]
                name = url.split("/")[-1]
                files.append(download_url(url, dest_dir / name, timeout=180))
                break
    rec = {
        "dataset_name": "GDELT GKG tone (proxy for manuscript Sent_AI)",
        "provider": "GDELT Project",
        "official_url": "https://www.gdeltproject.org/",
        "access_date_utc": utc_now_iso(),
        "suitability": "PROXY" if files and files[0].get("status") == "downloaded" else "INSUFFICIENT",
        "conceptual_change": "Replace Sent_AI with GDELT average tone if coverage validated; else OMIT sentiment dimension",
        "download_lastupdate": meta,
        "downloads": files,
        "note": "Not an AI-generated trading signal; media tone proxy only",
    }
    update_manifest("gdelt_gkg_proxy", rec)
    (dest_dir / "README.md").write_text(
        "# GDELT sentiment proxy\n\n"
        "Manuscript `Sent_AI` is **DATA NOT AVAILABLE** as a historical AI signal.\n"
        "If GKG files download, use `tone` fields as a **PROXY** and document the conceptual change.\n",
        encoding="utf-8",
    )
    print(json.dumps({k: rec[k] for k in ("suitability", "conceptual_change")}, indent=2))


if __name__ == "__main__":
    main()
