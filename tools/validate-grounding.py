#!/usr/bin/env python3
"""Validate Mycroft evidence, SIFT, and provenance package consistency.

This intentionally avoids third-party JSON Schema dependencies. It performs the
cross-file checks that schema syntax cannot express: evidence ref resolution,
summary counts, confidence caps, and local file hash verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


HASH_RE = re.compile(r"^[a-f0-9]{64}$")
CAP_ORDER = {"low": 0, "medium": 1, "high": 2}
VERDICTS = ["verified", "partially_verified", "unverified", "contradicted", "mischaracterized"]


def load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_artifact(base: Path, raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    candidates = [base / path, base.parent / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def validate_evidence_bundle(base: Path, bundle: dict[str, Any], strict_files: bool) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for index, item in enumerate(bundle.get("items", []), start=1):
        label = f"evidence item {index}"
        evidence_id = item.get("id")
        if not evidence_id:
            errors.append(f"{label}: missing id")
        elif evidence_id in ids:
            errors.append(f"{label}: duplicate id {evidence_id}")
        else:
            ids.add(evidence_id)

        digest = item.get("sha256", "")
        if not HASH_RE.match(digest):
            errors.append(f"{label}: sha256 must be 64 lowercase hex chars")

        raw_path = item.get("raw_path")
        if raw_path:
            artifact = resolve_artifact(base, raw_path)
            if artifact.exists():
                actual = sha256_file(artifact)
                if digest and actual != digest:
                    errors.append(f"{label}: sha256 mismatch for {raw_path}: got {actual}, expected {digest}")
            elif strict_files:
                errors.append(f"{label}: raw_path missing: {raw_path}")
        elif strict_files:
            errors.append(f"{label}: missing raw_path")

        gate = item.get("missing_source_gate", {})
        effect = gate.get("confidence_effect")
        if effect == "human_verification_required" and item.get("human_verification_required") is not True:
            errors.append(f"{label}: missing_source_gate requires human verification but flag is false")
    return errors


def evidence_ids(bundle: dict[str, Any]) -> set[str]:
    return {str(item.get("id")) for item in bundle.get("items", []) if item.get("id")}


def validate_sift_manifest(manifest: dict[str, Any], ids: set[str]) -> list[str]:
    errors: list[str] = []
    claims = manifest.get("claims", [])
    if manifest.get("schema") != "sift-manifest-v1":
        errors.append("sift manifest: schema must be sift-manifest-v1")

    counts = {verdict: 0 for verdict in VERDICTS}
    for claim in claims:
        claim_id = claim.get("id", "<missing>")
        verdict = claim.get("verdict")
        if verdict not in counts:
            errors.append(f"{claim_id}: invalid verdict {verdict!r}")
        else:
            counts[verdict] += 1

        refs = claim.get("evidence_refs", claim.get("sources", []))
        if not refs:
            if verdict not in {"unverified"}:
                errors.append(f"{claim_id}: non-unverified claim has no evidence_refs")
        for ref in refs:
            if ref not in ids:
                errors.append(f"{claim_id}: evidence ref does not resolve: {ref}")

        confidence = claim.get("confidence")
        cap = (claim.get("grounding") or {}).get("confidence_cap")
        if confidence in CAP_ORDER and cap in CAP_ORDER and CAP_ORDER[confidence] > CAP_ORDER[cap]:
            errors.append(f"{claim_id}: confidence {confidence} exceeds grounding cap {cap}")

    summary = manifest.get("summary", {})
    for verdict, count in counts.items():
        if summary.get(verdict) != count:
            errors.append(f"summary.{verdict}={summary.get(verdict)!r}, expected {count}")
    if summary.get("total_claims") != len(claims):
        errors.append(f"summary.total_claims={summary.get('total_claims')!r}, expected {len(claims)}")
    if "total_sources" in summary and summary["total_sources"] < len(ids):
        errors.append("summary.total_sources is lower than evidence bundle item count")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", help="Directory containing data/evidence-bundle.json and data/sift-manifest.json")
    parser.add_argument("--strict-files", action="store_true", help="Require local raw_path files and verify hashes")
    args = parser.parse_args()

    base = Path(args.package_dir).expanduser().resolve()
    evidence_path = base / "data/evidence-bundle.json"
    sift_path = base / "data/sift-manifest.json"

    errors: list[str] = []
    if not evidence_path.exists():
        errors.append(f"missing {evidence_path}")
    if not sift_path.exists():
        errors.append(f"missing {sift_path}")
    if errors:
        for error in errors:
            print(f"FAIL  {error}", file=sys.stderr)
        return 1

    evidence_bundle = load_json(evidence_path)
    sift_manifest = load_json(sift_path)
    errors.extend(validate_evidence_bundle(base, evidence_bundle, args.strict_files))
    errors.extend(validate_sift_manifest(sift_manifest, evidence_ids(evidence_bundle)))

    if errors:
        for error in errors:
            print(f"FAIL  {error}", file=sys.stderr)
        return 1
    print("grounding/provenance package: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
