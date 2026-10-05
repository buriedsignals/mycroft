#!/usr/bin/env python3
"""Regression checks for Mycroft grounding/provenance tooling."""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd or ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_ok(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        raise AssertionError(f"command failed: {result.args}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_fake_firecrawl(tmp: Path) -> Path:
    bin_dir = tmp / "bin"
    bin_dir.mkdir()
    firecrawl = bin_dir / "firecrawl"
    firecrawl.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                'if [ "$1" = "--version" ]; then echo "fake-firecrawl 1.0"; exit 0; fi',
                'if [ "$1" = "scrape" ]; then printf "# Source\\nEvidence for %s\\n" "$2"; exit 0; fi',
                'if [ "$1" = "search" ]; then printf "[{\\"url\\":\\"https://example.org/source\\"}]\\n"; exit 0; fi',
                'echo "unexpected args: $*" >&2',
                "exit 2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    firecrawl.chmod(0o755)
    return bin_dir


def main() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        fake_bin = make_fake_firecrawl(tmp)
        prov_dir = tmp / "provenance"
        config = tmp / "mycroft-config.json"
        config.write_text(json.dumps({"acquisition": {
            "search": "firecrawl", "scrape": "firecrawl", "firecrawl": "fallback",
        }}), encoding="utf-8")
        env = {
            **os.environ,
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "MYCROFT_PROV_DIR": str(prov_dir),
            "MYCROFT_CONFIG": str(config),
        }

        fetch = run([str(ROOT / "scripts/mycroft-fetch"), "scrape", "https://example.org/source"], env=env)
        assert_ok(fetch)
        payload = json.loads(fetch.stdout)
        evidence = payload["evidence"]
        assert evidence["id"].startswith("E-")
        raw_path = Path(evidence["raw_path"])
        assert raw_path.exists()
        assert evidence["sha256"] == sha256_text(raw_path.read_text(encoding="utf-8"))

        package = tmp / "package"
        data_dir = package / "data"
        source_dir = package / "sources/raw"
        data_dir.mkdir(parents=True)
        source_dir.mkdir(parents=True)
        source_text = raw_path.read_text(encoding="utf-8")
        package_source = source_dir / "source.md"
        package_source.write_text(source_text, encoding="utf-8")
        source_hash = sha256_text(source_text)

        evidence_bundle = {
            "schema_version": "1.0",
            "project": "sample",
            "created_at": "2026-05-18T12:00:00Z",
            "items": [
                {
                    "id": "E-source",
                    "source_url": "https://example.org/source",
                    "acquisition_method": "firecrawl",
                    "accessed_at": "2026-05-18T12:00:00Z",
                    "raw_path": "sources/raw/source.md",
                    "sha256": source_hash,
                    "content_type": "text/markdown",
                    "access_method": "full_text",
                    "human_verification_required": False,
                    "claim_links": [{"claim_id": "claim-001", "claim_text": "Example source exists.", "support_type": "direct"}],
                    "missing_source_gate": {
                        "requested_source": "Example source",
                        "returned_artifact": "sources/raw/source.md",
                        "missing": "",
                        "fallback_required": False,
                        "confidence_effect": "none",
                    },
                }
            ],
        }
        sift_manifest = {
            "schema": "sift-manifest-v1",
            "timestamp": "2026-05-18T12:01:00Z",
            "draft": {"content_hash": f"sha256:{'a' * 64}", "title": "Sample"},
            "claims": [
                {
                    "id": "claim-001",
                    "text": "Example source exists.",
                    "verdict": "verified",
                    "confidence": "high",
                    "evidence_refs": ["E-source"],
                    "sources": ["E-source"],
                    "grounding": {
                        "support_type": "direct",
                        "grounding_strength": "full",
                        "source_role": "primary",
                        "quote_match": "exact",
                        "claim_elements_checked": ["source"],
                        "missing_assumptions": [],
                        "contradiction_search": "No contradiction found in fixture.",
                        "confidence_cap": "high",
                        "misgrounding_risk": "low",
                        "assessment": "Fixture source directly supports fixture claim.",
                    },
                }
            ],
            "sources": [
                {
                    "id": "E-source",
                    "evidence_id": "E-source",
                    "url": "https://example.org/source",
                    "content_hash": f"sha256:{source_hash}",
                    "access_timestamp": "2026-05-18T12:00:00Z",
                    "access_type": "full",
                    "sift_step": "trace_to_original",
                    "is_primary": True,
                }
            ],
            "summary": {
                "verified": 1,
                "partially_verified": 0,
                "unverified": 0,
                "contradicted": 0,
                "mischaracterized": 0,
                "total_claims": 1,
                "total_sources": 1,
            },
        }
        (data_dir / "evidence-bundle.json").write_text(json.dumps(evidence_bundle, indent=2) + "\n", encoding="utf-8")
        (data_dir / "sift-manifest.json").write_text(json.dumps(sift_manifest, indent=2) + "\n", encoding="utf-8")

        assert_ok(run([sys.executable, str(ROOT / "tools/validate-grounding.py"), str(package), "--strict-files"]))
        assert_ok(run([sys.executable, str(ROOT / "tools/build-provenance-manifest.py"), str(package)]))

        manifest = json.loads((data_dir / "provenance-manifest.json").read_text(encoding="utf-8"))
        assert manifest["status"] == "unsigned"
        assert manifest["evidence"][0]["sha256"] == source_hash
        assert any(item["kind"] == "source" and item["sha256"] == source_hash for item in manifest["artifacts"])
        expected_input_set_hash = hashlib.sha256(
            json.dumps(manifest["artifacts"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        assert manifest["input_set_hash"] == expected_input_set_hash

        sift_manifest["claims"][0]["confidence"] = "high"
        sift_manifest["claims"][0]["grounding"]["confidence_cap"] = "medium"
        (data_dir / "sift-manifest.json").write_text(json.dumps(sift_manifest, indent=2) + "\n", encoding="utf-8")
        failed = run([sys.executable, str(ROOT / "tools/validate-grounding.py"), str(package), "--strict-files"])
        if failed.returncode == 0 or "exceeds grounding cap" not in failed.stderr:
            raise AssertionError("validator did not reject confidence above cap")
        sift_manifest["claims"][0]["confidence"] = "medium"
        (data_dir / "sift-manifest.json").write_text(json.dumps(sift_manifest, indent=2) + "\n", encoding="utf-8")

        check_signer_responses(package, tmp)

    check_managed_key_origin()
    check_noosphere_fixture()
    print("grounding/provenance checks: OK")
    return 0


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_provenance_manifest", ROOT / "tools/build-provenance-manifest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signer_record(request_body: dict) -> dict:
    """The record Noosphere signs: Mycroft's manifest projected onto the
    provider vocabulary (HASHING.md section 5), as in the vendor fixture."""
    manifest = request_body["provenance_manifest"]
    return {
        "profile": request_body["profile"],
        "input_set_hash": manifest["input_set_hash"],
        "inventory": [{k: a[k] for k in ("kind", "path", "sha256", "bytes")} for a in manifest["artifacts"]],
        "claims": [{"id": c["claim_id"], "text": c["claim_text"], "verdict": c["verdict"]} for c in manifest["claims"]],
        "sources": [{"id": e["evidence_id"], "url": e["source_url"], "hash": e["sha256"]} for e in manifest["evidence"]],
    }


def signer_response(request_body: dict, record: dict | None = None, **overrides: object) -> dict:
    """A response shaped like Noosphere's 1.3.0 contract for the request it answers."""
    record = record if record is not None else signer_record(request_body)
    record_bytes = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    response = {
        "status": "signed",
        "contract_version": "1.3.0",
        "profile": request_body["profile"],
        "manifest_id": "provenance_test.json",
        "input_set_hash": request_body["provenance_manifest"]["input_set_hash"],
        "content_hash": "sha256:" + hashlib.sha256(record_bytes).hexdigest(),
        "record": record,
        "record_b64": base64.b64encode(record_bytes).decode("ascii"),
        "c2pa_manifest_b64": base64.b64encode(b"synthetic c2pa sidecar").decode("ascii"),
        "signer": {"org_id": "org_test", "signing_source": "gcp-cloud-hsm"},
        "certificate_chain": {"grade": "production"},
        "signed_at": "2026-10-01T00:00:00Z",
    }
    response.update(overrides)
    return response


def drop_evidence(body: dict) -> dict:
    record = signer_record(body)
    record["sources"] = []
    return signer_response(body, record=record)


HTTP_STATUS_CASES = {
    "/http-401": (401, {}, "rejected the API key (401)"),
    "/http-429": (429, {"Retry-After": "30"}, "rate limiting (429); retry after 30 s"),
    "/http-503": (503, {}, "no production certificate chain (503)"),
}

SIGNER_CASES = {
    # path: (response builder, expected error fragment or None for an accepted receipt)
    "/ok": (lambda body: signer_response(body), None),
    "/bare-success": (lambda body: {"status": "signed"}, "record_b64 is missing"),
    "/development-chain": (
        lambda body: signer_response(body, certificate_chain={"grade": "development"}),
        "certificate chain grade is 'development'",
    ),
    "/tampered-hash": (
        lambda body: signer_response(body, content_hash="sha256:" + "0" * 64),
        "content_hash does not match",
    ),
    "/other-input-set": (
        lambda body: signer_response(body, input_set_hash="1" * 64),
        "input_set_hash does not match",
    ),
    "/generic-profile": (lambda body: signer_response(body, profile="provenance"), "profile is 'provenance'"),
    "/dropped-evidence": (drop_evidence, "1 evidence item(s) missing or changed"),
    "/redirect": (None, "redirects are refused"),
    **{path: (None, message) for path, (_, _, message) in HTTP_STATUS_CASES.items()},
}

# Stands in for c2patool so the builder's signed/unsigned decision can be
# exercised without a real production-signed sidecar.
TRUSTED_VERIFIER = """#!/bin/sh
if [ "$1" = "--version" ]; then echo "c2patool 0.27.22"; exit 0; fi
echo '{"validation_state": "Trusted", "validation_results": {"activeManifest": {"failure": []}}}'
"""


def check_signer_responses(package: Path, tmp: Path) -> None:
    """The builder names the mycroft profile, keeps a structurally sound
    response as an unverified receipt, marks it signed only when the verifier
    reports it Trusted, and refuses false success, mismatched hashes, dropped
    evidence, a development chain, redirects and HTTP errors. Until this check,
    any JSON response marked the package signed. A custom endpoint never
    receives the managed key."""
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    seen: list[tuple[str, dict, dict]] = []

    class Signer(BaseHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            pass

        def send_json(self, value: object, status: int = 200, headers: dict | None = None) -> None:
            data = json.dumps(value).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            for name, header in (headers or {}).items():
                self.send_header(name, header)
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:
            seen.append((self.path, {}, {}))
            self.send_json({"status": "signed"})

        def do_POST(self) -> None:
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            seen.append((self.path, {k.lower(): v for k, v in self.headers.items()}, body))
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header("Location", f"http://127.0.0.1:{self.server.server_port}/stolen")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if self.path in HTTP_STATUS_CASES:
                status, headers, _ = HTTP_STATUS_CASES[self.path]
                self.send_json({"error": "refused"}, status=status, headers=headers)
                return
            self.send_json(SIGNER_CASES[self.path.split("?")[0]][0](body))

    server = ThreadingHTTPServer(("127.0.0.1", 0), Signer)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    endpoint = f"http://127.0.0.1:{server.server_port}"
    base_env = {**os.environ, "NOOSPHERE_PROVENANCE_API_KEY": "", "C2PATOOL": "/nonexistent/c2patool"}
    manifest_path = package / "data" / "provenance-manifest.json"

    def build(path: str, *extra: str, **env: str) -> dict:
        result = run([sys.executable, str(ROOT / "tools/build-provenance-manifest.py"), str(package),
                      "--sign-endpoint", endpoint + path, *extra], env={**base_env, **env})
        assert_ok(result)
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    try:
        for path, (_, expected_error) in SIGNER_CASES.items():
            manifest = build(path)
            assert manifest["status"] != "signed", path
            if expected_error is None:
                assert manifest["status"] == "unsigned", path
                assert manifest["signing"]["receipt_status"] == "received_unverified", path
                assert manifest["signing"]["verification"]["verified"] is False, path
            else:
                assert manifest["status"] == "signing_failed", path
                assert expected_error in manifest["signing"]["error"], (path, manifest["signing"]["error"])

        verifier = tmp / "c2patool"
        verifier.write_text(TRUSTED_VERIFIER, encoding="utf-8")
        verifier.chmod(0o755)
        manifest = build("/ok?trusted", C2PATOOL=str(verifier))
        assert manifest["status"] == "signed", manifest["signing"]
        assert manifest["signing"]["verification"]["validation_state"] == "Trusted"

        manifest = build("/ok?keyed", NOOSPHERE_PROVENANCE_API_KEY="test-key")
        assert manifest["status"] == "signing_failed"
        assert "only sent to https://platform.noosphere.tech" in manifest["signing"]["error"]
        assert "test-key" not in json.dumps(manifest)

        flagged = run([sys.executable, str(ROOT / "tools/build-provenance-manifest.py"), str(package),
                       "--api-key", "test-key"], env=base_env)
        assert flagged.returncode == 2 and "unrecognized arguments: --api-key" in flagged.stderr
    finally:
        server.shutdown()
        server.server_close()

    _, headers, body = next(entry for entry in seen if entry[0] == "/ok")
    assert body["profile"] == "mycroft"
    assert body["provenance_manifest"]["input_set_hash"]
    assert "x-api-key" not in headers
    assert not any(entry[0] in ("/stolen", "/ok?keyed") for entry in seen)


def check_managed_key_origin() -> None:
    """The managed key goes to platform.noosphere.tech as X-API-Key."""
    builder = load_builder()
    sent: list = []

    class Opener:
        def open(self, request, timeout):  # noqa: ARG002
            sent.append(request)
            raise builder.urllib.error.HTTPError(request.full_url, 401, "Unauthorized", {}, None)

    original = builder.urllib.request.build_opener
    builder.urllib.request.build_opener = lambda *handlers: Opener()
    os.environ["NOOSPHERE_PROVENANCE_API_KEY"] = "managed-key"
    try:
        builder.post_for_signing(
            "https://platform.noosphere.tech/api/provenance/sign", {"input_set_hash": "x"}, None, None)
    except builder.SigningHTTPError as exc:
        assert "rejected the API key (401)" in str(exc) and "managed-key" not in str(exc)
    else:
        raise AssertionError("a 401 must raise SigningHTTPError")
    finally:
        builder.urllib.request.build_opener = original
        del os.environ["NOOSPHERE_PROVENANCE_API_KEY"]
    assert sent and sent[0].get_header("X-api-key") == "managed-key"


def check_noosphere_fixture() -> None:
    """Noosphere's signed Mycroft fixture (contract 1.3.0, development CA)
    keeps every artifact, claim and evidence item, and c2patool verifies its
    sidecar: Trusted with the development CA pinned, untrusted against the
    C2PA trust list, invalid after one record byte changes."""
    if not shutil.which("c2patool") and not os.environ.get("C2PATOOL"):
        if os.environ.get("CI"):
            raise AssertionError("c2patool is required in CI")
        print("SKIP check_noosphere_fixture: c2patool not installed")
        return
    builder = load_builder()
    verify = builder.noosphere_verify
    bundle = ROOT / "tests" / "fixtures" / "noosphere" / "dev-v1" / "mycroft"
    request = json.loads((bundle / "request.json").read_text(encoding="utf-8"))
    response = json.loads((bundle / "response.json").read_text(encoding="utf-8"))
    assert builder.signing_response_problems(response, request["provenance_manifest"]) == [
        "certificate chain grade is 'development', not 'production'"
    ]
    with tempfile.TemporaryDirectory() as raw_tmp:
        dev_ca = Path(raw_tmp) / "dev-ca.pem"
        chain = (bundle / "certificate-chain.pem").read_text(encoding="utf-8")
        dev_ca.write_text("-----BEGIN CERTIFICATE-----" + chain.split("-----BEGIN CERTIFICATE-----")[2])
        os.environ["NOOSPHERE_C2PA_TRUST_ANCHORS"] = str(dev_ca)
        try:
            trusted = verify.verify_sidecar(response)
            record = bytearray(base64.b64decode(response["record_b64"]))
            record[10] ^= 1
            tampered = verify.verify_sidecar({**response, "record_b64": base64.b64encode(bytes(record)).decode()})
        finally:
            del os.environ["NOOSPHERE_C2PA_TRUST_ANCHORS"]
        public = verify.verify_sidecar(response)
    assert trusted["verified"] and trusted["validation_state"] == "Trusted", trusted
    assert not public["verified"] and "signingCredential.untrusted" in public["failures"], public
    assert not tampered["verified"] and "assertion.dataHash.mismatch" in tampered["failures"], tampered


if __name__ == "__main__":
    raise SystemExit(main())
