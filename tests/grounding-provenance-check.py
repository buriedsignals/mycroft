#!/usr/bin/env python3
"""Regression checks for Mycroft grounding/provenance tooling."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
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
        env = {
            **os.environ,
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "MYCROFT_PROV_DIR": str(prov_dir),
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

        sift_manifest["claims"][0]["confidence"] = "high"
        sift_manifest["claims"][0]["grounding"]["confidence_cap"] = "medium"
        (data_dir / "sift-manifest.json").write_text(json.dumps(sift_manifest, indent=2) + "\n", encoding="utf-8")
        failed = run([sys.executable, str(ROOT / "tools/validate-grounding.py"), str(package), "--strict-files"])
        if failed.returncode == 0 or "exceeds grounding cap" not in failed.stderr:
            raise AssertionError("validator did not reject confidence above cap")

    print("grounding/provenance checks: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
