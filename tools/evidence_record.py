#!/usr/bin/env python3
"""Store a raw API response as a Mycroft evidence item (same shape as mycroft-fetch).

Used by evidence-lookup.py and marketdata.py under --evidence. Artifact under
MYCROFT_PROV_DIR/raw/, record as E-*.json, sha256 from the written bytes.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def provenance_dir() -> Path:
    return Path(os.environ.get("MYCROFT_PROV_DIR", Path.home() / ".mycroft" / "provenance"))


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


_EXT = {
    "application/json": "json",
    "text/csv": "csv",
    "application/xml": "xml",
    "text/xml": "xml",
    "text/html": "html",
    "text/plain": "txt",
}


def content_type_for(url: str, body: bytes) -> str:
    """Best-effort media type for a raw API response, from the body first."""
    head = body.lstrip()[:1]
    if head in (b"{", b"["):
        return "application/json"
    if head == b"<":
        return "application/xml"
    path = url.split("?", 1)[0].lower()
    if path.endswith(".csv") or "csv" in url.lower():
        return "text/csv"
    return "text/plain"


def write_api_evidence(
    *,
    source_url: str,
    body: bytes,
    query_or_task: str,
    command: str,
    content_type: str | None = None,
) -> dict[str, Any]:
    """Store one API response as a Mycroft evidence item and return the record.

    `source_url` must already have any API key masked (`<key>`); it is stored
    verbatim in the record.
    """
    ctype = content_type or content_type_for(source_url, body)
    evidence_id = f"E-{uuid.uuid4().hex[:12]}"
    prov_id = f"prov-{uuid.uuid4().hex[:12]}"
    out_dir = provenance_dir()
    # Artifacts live under raw/ so a JSON response never shares a name with
    # its own E-*.json record (mycroft-fetch lists records with a flat glob).
    artifact_path = out_dir / "raw" / f"{evidence_id}.{_EXT.get(ctype, 'txt')}"
    atomic_write(artifact_path, body)
    accessed_at = now_iso()
    sha = hashlib.sha256(body).hexdigest()

    record: dict[str, Any] = {
        "id": evidence_id,
        "legacy_provenance_id": prov_id,
        "query_or_task": query_or_task,
        "source_url": source_url,
        "url": source_url,
        "acquisition_method": "api",
        "accessed_at": accessed_at,
        "access_timestamp": accessed_at,
        "raw_path": str(artifact_path),
        "sha256": sha,
        "content_hash": f"sha256:{sha}",
        "content_length": len(body),
        "content_type": ctype,
        "format": _EXT.get(ctype, "txt"),
        "access_method": "full_text",
        "human_verification_required": False,
        "missing_source_gate": {
            "requested_source": source_url,
            "returned_artifact": str(artifact_path),
            "missing": "",
            "fallback_required": False,
            "confidence_effect": "none",
        },
        "scraper_version": "mycroft-lookup-tools/1.0",
        "command": command,
    }
    atomic_write(out_dir / f"{evidence_id}.json", (json.dumps(record, indent=2) + "\n").encode("utf-8"))
    legacy = {
        "id": prov_id,
        "evidence_id": evidence_id,
        "url": source_url,
        "access_timestamp": accessed_at,
        "content_hash": record["content_hash"],
        "content_length": len(body),
        "format": record["format"],
        "command": command,
        "scraper_version": record["scraper_version"],
    }
    atomic_write(out_dir / f"{prov_id}.json", (json.dumps(legacy, indent=2) + "\n").encode("utf-8"))
    return record


def print_records(records: list[dict[str, Any]]) -> None:
    """One line per stored response, for the recipe to copy into the bundle."""
    for r in records:
        print(f"evidence: {r['id']}  sha256: {r['sha256']}  raw: {r['raw_path']}")
