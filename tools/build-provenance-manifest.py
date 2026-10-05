#!/usr/bin/env python3
"""Build a Mycroft provenance manifest and optionally submit it for C2PA signing."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import noosphere_verify  # noqa: E402


ARTIFACTS = [
    ("draft", "draft.md"),
    ("evidence_bundle", "data/evidence-bundle.json"),
    ("sift_manifest", "data/sift-manifest.json"),
    ("review", "review.md"),
    ("review", "review.html"),
]


SIGNING_PROFILE = "mycroft"
# Noosphere caps the signed record at 5 MB and returns it twice (object and
# base64) next to the sidecar; anything far beyond that is not a receipt.
MAX_SIGNING_RESPONSE_BYTES = 32 * 1024 * 1024
# A response that passes every check is still not "signed" until the C2PA
# sidecar verifies locally against the pinned trust anchors (noosphere_verify).
RECEIPT_RECEIVED_UNVERIFIED = "received_unverified"
# The managed signer. NOOSPHERE_PROVENANCE_API_KEY is sent to this origin only.
MANAGED_ORIGIN = ("https", "platform.noosphere.tech")
API_KEY_ENV = "NOOSPHERE_PROVENANCE_API_KEY"
CONTRACT_MAJOR = "1"
HTTP_ERRORS = {
    401: "the signer rejected the API key (401); check NOOSPHERE_PROVENANCE_API_KEY",
    403: "the API key lacks the 'sign' scope (403)",
    413: "the manifest is larger than the signer accepts (413)",
    422: "the signer refused a manifest with no artifacts, claims or evidence (422)",
    429: "the signer is rate limiting (429)",
    503: "the signer has no production certificate chain (503)",
}


class SigningResponseError(ValueError):
    """The signer answered, but the answer is not a usable signature."""


class SigningHTTPError(SigningResponseError):
    """The signer answered with an HTTP error status."""


class _RefuseRedirect(urllib.request.HTTPRedirectHandler):
    # Noosphere never redirects; following one would resend X-API-Key elsewhere.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


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


def canonical_hash(value: Any) -> str:
    """SHA-256 over sorted, compact JSON."""
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


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
    artifacts = artifact_entries(base)
    return {
        "schema_version": "1.0",
        "project": evidence_bundle.get("project") or base.name,
        "generated_at": now_iso(),
        "status": "unsigned",
        # Identifies the exact set of files this manifest describes. The signer
        # carries it through unchanged, so a receipt can be matched to its inputs.
        "input_set_hash": canonical_hash(artifacts),
        "signing": {
            "profile": "noosphere-c2pa",
            "requires_api_key": True,
            "requires_signing_credential": True,
            "credential_id": credential_id,
            "endpoint": endpoint,
        },
        "artifacts": artifacts,
        "claims": claim_entries(sift_manifest),
        "evidence": evidence_entries(base, evidence_bundle),
    }


def is_managed_endpoint(endpoint: str) -> bool:
    parsed = urllib.parse.urlsplit(endpoint)
    return (parsed.scheme, parsed.hostname) == MANAGED_ORIGIN and parsed.port in (None, 443)


def http_error_message(exc: urllib.error.HTTPError) -> str:
    if 300 <= exc.code < 400:
        return f"the signer redirected ({exc.code}); redirects are refused so the API key is never resent"
    message = HTTP_ERRORS.get(exc.code, f"the signer returned HTTP {exc.code}")
    retry_after = exc.headers.get("Retry-After") if exc.code == 429 and exc.headers else None
    if retry_after and retry_after.isdigit():
        message += f"; retry after {retry_after} s"
    return message


def post_for_signing(endpoint: str, manifest: dict[str, Any], artifact_path: str | None, credential_id: str | None) -> dict[str, Any]:
    api_key = os.environ.get(API_KEY_ENV)
    if api_key and not is_managed_endpoint(endpoint):
        # The managed key never reaches a user-supplied origin.
        raise SigningResponseError(
            f"{API_KEY_ENV} is only sent to https://platform.noosphere.tech; "
            "unset it to use a custom signer"
        )
    payload = {
        # The signer records the request under this product profile and echoes it
        # back; without it the record falls back to the generic profile.
        "profile": SIGNING_PROFILE,
        "artifact_path": artifact_path,
        "provenance_manifest": manifest,
        "credential_id": credential_id,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "Mycroft-C2PA/1.0"}
    if api_key:
        headers["X-API-Key"] = api_key
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers=headers,
    )
    opener = urllib.request.build_opener(_RefuseRedirect)
    try:
        with opener.open(request, timeout=30) as response:
            raw = response.read(MAX_SIGNING_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise SigningHTTPError(http_error_message(exc)) from None
    if len(raw) > MAX_SIGNING_RESPONSE_BYTES:
        raise SigningResponseError(f"signing response exceeds {MAX_SIGNING_RESPONSE_BYTES} bytes")
    result = json.loads(raw.decode("utf-8"))
    if not isinstance(result, dict):
        raise SigningResponseError("signing receipt must be a JSON object")
    problems = signing_response_problems(result, manifest)
    if problems:
        raise SigningResponseError("signing response rejected: " + "; ".join(problems))
    return result


def strict_base64(value: Any) -> bytes | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return base64.b64decode(value, validate=True) or None
    except binascii.Error:
        return None


def signing_response_problems(response: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    """Check a signer response against the Noosphere 1.x contract and the
    manifest that was sent. An empty list means structurally sound, not
    cryptographically verified."""
    problems = []
    if str(response.get("contract_version", "")).split(".")[0] != CONTRACT_MAJOR:
        problems.append(f"contract_version is {response.get('contract_version')!r}, not {CONTRACT_MAJOR}.x")
    if response.get("status") != "signed":
        problems.append(f"status is {response.get('status')!r}, not 'signed'")
    if response.get("profile") != SIGNING_PROFILE:
        problems.append(f"profile is {response.get('profile')!r}, not {SIGNING_PROFILE!r}")
    if response.get("input_set_hash") != manifest.get("input_set_hash"):
        problems.append("input_set_hash does not match the manifest that was sent")
    for field, kind in (("manifest_id", str), ("signed_at", str), ("signer", dict), ("record", dict)):
        if not isinstance(response.get(field), kind):
            problems.append(f"{field} is missing or not a {kind.__name__}")

    record_bytes = strict_base64(response.get("record_b64"))
    if record_bytes is None:
        problems.append("record_b64 is missing or not valid base64")
    else:
        content_hash = str(response.get("content_hash", "")).removeprefix("sha256:")
        if content_hash != hashlib.sha256(record_bytes).hexdigest():
            problems.append("content_hash does not match the decoded record_b64 bytes")
        try:
            decoded_record = json.loads(record_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError):
            decoded_record = None
        if decoded_record != response.get("record"):
            problems.append("record_b64 does not decode to the returned record")

    if strict_base64(response.get("c2pa_manifest_b64", response.get("c2pa_manifest"))) is None:
        problems.append("C2PA sidecar is missing or not valid base64")
    chain = response.get("certificate_chain")
    grade = chain.get("grade") if isinstance(chain, dict) else None
    if grade != "production":
        problems.append(f"certificate chain grade is {grade!r}, not 'production'")
    if isinstance(response.get("record"), dict):
        problems.extend(projection_problems(response["record"], manifest))
    return problems


def projection_problems(record: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    """Every artifact, claim and evidence item that was sent must appear in the
    signed record unchanged (Noosphere HASHING.md section 5). The August canary
    lost all three, so this is checked, not assumed."""
    def missing(sent: set, signed: set, label: str) -> list[str]:
        lost = sent - signed
        return [f"{len(lost)} {label} missing or changed in the signed record"] if lost else []

    def rows(value: Any) -> list[dict[str, Any]]:
        return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []

    return (
        missing(
            {(a.get("path"), a.get("sha256"), a.get("bytes")) for a in rows(manifest.get("artifacts"))},
            {(a.get("path"), a.get("sha256"), a.get("bytes")) for a in rows(record.get("inventory"))},
            "artifact(s)",
        )
        + missing(
            {(c.get("claim_id"), c.get("claim_text"), c.get("verdict")) for c in rows(manifest.get("claims"))},
            {(c.get("id"), c.get("text"), c.get("verdict")) for c in rows(record.get("claims"))},
            "claim(s)",
        )
        + missing(
            {(e.get("evidence_id"), e.get("source_url"), e.get("sha256") or None) for e in rows(manifest.get("evidence"))},
            {(s.get("id"), s.get("url"), s.get("hash") or None) for s in rows(record.get("sources"))}
            | {(s.get("id"), s.get("url"), None) for s in rows(record.get("sources"))},
            "evidence item(s)",
        )
    )


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
            verification = noosphere_verify.verify_sidecar(receipt)
            manifest["signing"]["receipt_path"] = rel_path(receipt_path, base)
            manifest["signing"]["verification"] = verification
            if verification["verified"]:
                manifest["status"] = "signed"
                manifest["signing"]["signed_at"] = now_iso()
            else:
                manifest["signing"]["receipt_status"] = RECEIPT_RECEIVED_UNVERIFIED
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError) as exc:
            manifest["status"] = "signing_failed"
            manifest["signing"]["error"] = f"{type(exc).__name__}: {exc}"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
