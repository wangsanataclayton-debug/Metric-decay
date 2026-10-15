"""Shared download utilities: provenance, no silent overwrite of raw files."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"
MANIFEST = ROOT / "data_manifest.json"
LOGS = ROOT / "logs"

LOGS.mkdir(parents=True, exist_ok=True)
META.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS / "downloads.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("download")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def safe_target(path: Path, overwrite: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        stem, suf = path.stem, path.suffix
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        alt = path.with_name(f"{stem}__kept_existing__{ts}{suf}")
        log.warning("Refusing silent overwrite of %s; writing sidecars only", path)
        return path  # keep existing; caller should skip byte write
    return path


def download_url(
    url: str,
    dest: Path,
    *,
    overwrite: bool = False,
    headers: Optional[dict] = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """Download bytes to dest without silently overwriting existing raw files."""
    meta: dict[str, Any] = {
        "url": url,
        "dest": str(dest.relative_to(ROOT)).replace("\\", "/"),
        "access_date_utc": utc_now_iso(),
        "status": "pending",
    }
    if dest.exists() and not overwrite:
        meta["status"] = "skipped_exists"
        meta["sha256"] = sha256_file(dest)
        meta["bytes"] = dest.stat().st_size
        log.info("SKIP (exists): %s", dest)
        return meta

    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers=headers or {"User-Agent": "metric-decay-research/0.1 (academic; reproducible)"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            meta["http_status"] = getattr(resp, "status", None)
            meta["content_type"] = resp.headers.get("Content-Type")
        dest.write_bytes(data)
        meta["status"] = "downloaded"
        meta["bytes"] = len(data)
        meta["sha256"] = sha256_file(dest)
        log.info("OK %s (%s bytes)", dest.name, meta["bytes"])
    except Exception as e:  # noqa: BLE001 — record and continue pipeline
        meta["status"] = "error"
        meta["error"] = repr(e)
        log.error("FAIL %s: %s", url, e)
    return meta


def update_manifest(dataset_id: str, record: dict[str, Any]) -> None:
    if MANIFEST.exists():
        man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        man = {"schema_version": "1.0", "datasets": {}}
    man["access_date_utc"] = utc_now_iso()
    man.setdefault("datasets", {})[dataset_id] = record
    MANIFEST.write_text(json.dumps(man, indent=2), encoding="utf-8")
    side = META / f"{dataset_id}_download.json"
    side.write_text(json.dumps(record, indent=2), encoding="utf-8")
