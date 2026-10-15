"""SEC 13F ingestion interface — LOW-FREQUENCY PROXY FOR PORTFOLIO CONVERGENCE.

Does NOT claim to observe algorithmic trading. Bulk download requires EDGAR
full-index + parsing; this module documents endpoints and provides a stub loader.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "raw" / "sec_13f"
OUT.mkdir(parents=True, exist_ok=True)

EDGAR_FULL_INDEX = "https://www.sec.gov/Archives/edgar/full-index/"
EDGAR_13F_SEARCH = "https://efts.sec.gov/LATEST/search-index?q=%22formType%22%3A%2213F-HR%22"
# Atom/company filings via data.sec.gov
DATA_SEC = "https://data.sec.gov/submissions/"

README = """# SEC 13F access notes

- Provider: U.S. SEC EDGAR
- Form: 13F-HR (institutional holdings, quarterly)
- Official: https://www.sec.gov/edgar
- Bulk: EDGAR full-index by quarter; information tables in XML (older: tab-delimited)
- Identifiers: CUSIP + shares + market value; map to tickers via CRSP/OpenFIGI
- Licensing: public U.S. government data; respect SEC fair-access User-Agent rules
- Suitability: PROXY — institutional portfolio cosine similarity, not HFT/ACH directly
- Status: DATA NOT DOWNLOADED in bulk in this pass (rate limits + large parse job)

Required User-Agent example:
  Sample Research academic@example.edu metric-decay-pipeline
"""


def write_stub() -> None:
    (OUT / "README_ACCESS.md").write_text(README, encoding="utf-8")
    meta = {
        "dataset_name": "SEC 13F institutional holdings",
        "provider": "U.S. Securities and Exchange Commission (EDGAR)",
        "official_url": "https://www.sec.gov/edgar",
        "api_endpoints": {"full_index": EDGAR_FULL_INDEX, "data_sec": DATA_SEC},
        "suitability": "PROXY",
        "status": "INGESTION_STUB_ONLY",
        "note": "LOW-FREQUENCY PROXY FOR PORTFOLIO CONVERGENCE",
    }
    (OUT / "access_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    man_path = ROOT / "data_manifest.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    man.setdefault("datasets", {})["sec_13f"] = meta
    man_path.write_text(json.dumps(man, indent=2), encoding="utf-8")


def cosine_similarity_matrix(W):
    """W: institutions x assets weight matrix (rows sum ~1)."""
    import numpy as np

    X = np.asarray(W, dtype=float)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    Xn = X / norms
    return Xn @ Xn.T


if __name__ == "__main__":
    write_stub()
    print("13F stub written to", OUT)
