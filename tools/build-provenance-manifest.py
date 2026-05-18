#!/usr/bin/env python3
"""Build a Mycroft provenance manifest and optionally submit it for C2PA signing."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ARTIFACTS = [
    ("draft", "draft.md"),
    ("evidence_bundle", "data/evidence-bundle.json"),
    ("sift_manifest", "data/sift-manifest.json"),
    ("review", "review.md"),
    ("review", "review.html"),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            total += len(chunk)
    return digest.hexdigest(), total


def rel_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def resolve_artifact(base: Path, raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    for candidate in (base / path, base.parent / path):
        if candidate.exists():
            return candidate
    return base / path


def artifact_entries(base: Path) -> list[dict[str, Any]]:
    entries = []
    seen = set()
    for kind, rel in ARTIFACTS:
        path = base / rel
        if not path.exists():
            continue
        digest, size = sha256_file(path)
        seen.add(path.resolve())
        entries.append({"kind": kind, "path": rel, "sha256": digest, "bytes": size})
    evidence_bundle_path = base / "data/evidence-bundle.json"
    if evidence_bundle_path.exists():
        evidence_bundle = load_json(evidence_bundle_path)
        for item in evidence_bundle.get("items", []):
            raw_path = item.get("raw_path")
            if not raw_path:
                continue
            path = resolve_artifact(base, raw_path)
            if not path.exists() or path.resolve() in seen:
                continue
            digest, size = sha256_file(path)
            seen.add(path.resolve())
            entries.append({"kind": "source", "path": rel_path(path, base), "sha256": digest, "bytes": size})
    return entries


def claim_entries(sift_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    claims = []
    for claim in sift_manifest.get("claims", []):
        grounding = claim.get("grounding", {}) or {}
        claims.append({
            "claim_id": claim.get("id", ""),
            "claim_text": claim.get("text", ""),
            "verdict": claim.get("verdict", "unverified"),
            "confidence": claim.get("confidence", "unknown"),
            "confidence_cap": grounding.get("confidence_cap", "unknown"),
            "grounding_strength": grounding.get("grounding_strength", "unknown"),
            "evidence_refs": claim.get("evidence_refs", claim.get("sources", [])),
        })
    return claims


def evidence_entries(base: Path, evidence_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    entries = []
    for item in evidence_bundle.get("items", []):
        entry = {
            "evidence_id": item.get("id", ""),
            "source_url": item.get("source_url", item.get("url", "")),
            "acquisition_method": item.get("acquisition_method", ""),
            "accessed_at": item.get("accessed_at", item.get("access_timestamp", "")),
            "raw_path": item.get("raw_path", ""),
            "archive_url": item.get("archive_url", ""),
            "human_verification_required": bool(item.get("human_verification_required", False)),
            "claim_links": item.get("claim_links", []),
        }
        raw_path = item.get("raw_path")
        if raw_path:
            path = resolve_artifact(base, raw_path)
            if path.exists():
                entry["sha256"], _ = sha256_file(path)
            else:
                entry["sha256"] = item.get("sha256", "")
        else:
            entry["sha256"] = item.get("sha256", "")
        entries.append(entry)
    return entries


def build_manifest(base: Path, credential_id: str | None, endpoint: str | None) -> dict[str, Any]:
    evidence_bundle = load_json(base / "data/evidence-bundle.json")
    sift_manifest = load_json(base / "data/sift-manifest.json")
    return {
        "schema_version": "1.0",
        "project": evidence_bundle.get("project") or base.name,
        "generated_at": now_iso(),
        "status": "unsigned",
        "signing": {
            "profile": "noosphere-c2pa",
            "requires_api_key": False,
            "requires_signing_credential": True,
            "credential_id": credential_id,
            "endpoint": endpoint,
        },
        "artifacts": artifact_entries(base),
        "claims": claim_entries(sift_manifest),
        "evidence": evidence_entries(base, evidence_bundle),
    }


def post_for_signing(endpoint: str, manifest: dict[str, Any], artifact_path: str | None, credential_id: str | None) -> dict[str, Any]:
    payload = {
        "artifact_path": artifact_path,
        "provenance_manifest": manifest,
        "credential_id": credential_id,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "Mycroft-C2PA/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", help="Directory containing data/evidence-bundle.json and data/sift-manifest.json")
    parser.add_argument("--output", help="Output path; defaults to data/provenance-manifest.json")
    parser.add_argument("--credential-id", default=None)
    parser.add_argument("--sign-endpoint", default=None)
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--receipt-output", default=None)
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()

    base = Path(args.package_dir).expanduser().resolve()
    if not base.is_dir():
        print(f"package directory not found: {base}", file=sys.stderr)
        return 2

    if not args.skip_validation:
        validator = Path(__file__).resolve().parent / "validate-grounding.py"
        result = subprocess.run([sys.executable, str(validator), str(base), "--strict-files"], check=False)
        if result.returncode != 0:
            return result.returncode

    output = Path(args.output).expanduser().resolve() if args.output else base / "data/provenance-manifest.json"
    manifest = build_manifest(base, args.credential_id, args.sign_endpoint)

    if args.sign_endpoint:
        receipt_path = (
            Path(args.receipt_output).expanduser().resolve()
            if args.receipt_output
            else base / "data/provenance-signing-receipt.json"
        )
        try:
            receipt = post_for_signing(args.sign_endpoint, manifest, args.artifact, args.credential_id)
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            manifest["status"] = "signed"
            manifest["signing"]["signed_at"] = now_iso()
            manifest["signing"]["receipt_path"] = rel_path(receipt_path, base)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            manifest["status"] = "signing_failed"
            manifest["signing"]["error"] = f"{type(exc).__name__}: {exc}"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
