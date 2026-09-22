#!/usr/bin/env python3
"""Offline checks for the fact-check lookup tools and the density gate.

Network lookups are exercised by hand; this test covers the parts that must
hold without a network: the density gate's exit codes, and the evidence
record writer's shape, hash and artifact placement.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


def check_density(tmp: Path) -> None:
    src = tmp / "source.txt"
    src.write_text("The plant opened in 1998 and employs 1,200 people. " * 4, encoding="utf-8")  # 36 words
    ok = run(str(TOOLS / "claim-density.py"), str(src), "3")
    assert ok.returncode == 0 and "OK" in ok.stdout, ok
    thin = run(str(TOOLS / "claim-density.py"), str(src), "1")
    assert thin.returncode == 1 and "THIN" in thin.stdout, thin
    zero = run(str(TOOLS / "claim-density.py"), str(src), "0")
    assert zero.returncode == 1, zero
    bad = run(str(TOOLS / "claim-density.py"), str(src))
    assert bad.returncode == 2, bad
    cjk = tmp / "cjk.txt"
    cjk.write_text("東京都の人口は約千四百万人である。" * 5, encoding="utf-8")
    assert run(str(TOOLS / "claim-density.py"), str(cjk), "3").returncode == 0


def check_evidence_record(tmp: Path) -> None:
    sys.path.insert(0, str(TOOLS))
    os.environ["MYCROFT_PROV_DIR"] = str(tmp / "prov")
    import evidence_record  # noqa: E402

    body = b'{"observations": [{"date": "2026-09-18", "value": "5.01"}]}'
    rec = evidence_record.write_api_evidence(
        source_url="https://example.org/api?key=<key>", body=body,
        query_or_task="claim-001", command="marketdata.py fred DGS10",
    )
    for field in ("id", "source_url", "acquisition_method", "accessed_at", "raw_path", "sha256",
                  "access_method", "human_verification_required", "missing_source_gate"):
        assert field in rec, field
    assert rec["acquisition_method"] == "api"
    assert rec["content_type"] == "application/json"
    raw = Path(rec["raw_path"])
    assert raw.parent == tmp / "prov" / "raw", "artifacts must sit under raw/ so records and JSON bodies never collide"
    assert raw.read_bytes() == body
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == rec["sha256"]
    meta = tmp / "prov" / f"{rec['id']}.json"
    assert json.loads(meta.read_text(encoding="utf-8"))["sha256"] == rec["sha256"]
    # A flat E-*.json glob (what mycroft-fetch's provenance list uses) must see one record only.
    assert [p.name for p in (tmp / "prov").glob("E-*.json")] == [meta.name]

    csv_rec = evidence_record.write_api_evidence(
        source_url="https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10", body=b"DATE,DGS10\n2026-09-18,5.01\n",
        query_or_task="claim-002", command="marketdata.py fred DGS10",
    )
    assert csv_rec["content_type"] == "text/csv" and csv_rec["raw_path"].endswith(".csv")


def check_help() -> None:
    for tool in ("evidence-lookup.py", "marketdata.py"):
        proc = run(str(TOOLS / tool), "--help")
        assert proc.returncode == 0 and "--evidence" in proc.stdout, tool
        assert "verso.ink" in (TOOLS / tool).read_text(encoding="utf-8"), f"{tool}: Verso credit missing"
    assert "verso.ink" in (TOOLS / "claim-density.py").read_text(encoding="utf-8")
    assert "mailto=team@verso.ink" not in (TOOLS / "evidence-lookup.py").read_text(encoding="utf-8"), (
        "upstream contact address must not be hard-coded"
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        check_density(tmp)
        check_evidence_record(tmp)
    check_help()
    print("fact-check tools: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
