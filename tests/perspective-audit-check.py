#!/usr/bin/env python3
"""Contract checks for the Mycroft perspective-audit skill and validator."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills/perspective-audit/scripts/validate_perspective_audit.py"
SCHEMA = ROOT / "schemas/perspective-audit.schema.json"


def run_validator(path: Path, bundle: Path | None = None) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(VALIDATOR), str(path)]
    if bundle:
        args.extend(["--evidence-bundle", str(bundle)])
    return subprocess.run(args, text=True, capture_output=True, check=False)


def fixture() -> dict:
    review = {"state": "unreviewed"}
    return {
        "schema": "perspective-audit-v1",
        "audit_id": "PA-sample",
        "created_at": "2026-08-11T12:00:00Z",
        "topic": "Proposed night-bus route",
        "question": "Which concerns and benefits appear in the supplied comments?",
        "corpus": {
            "description": "Two captured comments from one council thread.",
            "evidence_ids": ["E-thread"],
            "included_source_count": 2,
            "included_passage_count": 2,
            "excluded": [],
            "sampling_notes": "Complete supplied fixture.",
            "deduplication_notes": "No duplicates found.",
            "representativeness_statement": "Describes only the supplied thread.",
        },
        "perspectives": [
            {
                "id": "P-001",
                "label": "Improved access for shift workers",
                "description": "The route would help people traveling outside daytime service hours.",
                "stance_axes": ["access versus operating cost"],
                "evidence_refs": ["E-thread#comment-1"],
                "observed_source_count": 1,
                "extraction_confidence": "high",
                "representativeness": "corpus_only",
                "counterevidence_refs": [],
                "human_review": review,
            }
        ],
        "summaries": [
            {
                "id": "S-001",
                "text": "One commenter said night service would improve transport access for shift workers.",
                "perspective_refs": ["P-001"],
                "evidence_refs": ["E-thread#comment-1"],
                "support_type": "direct",
                "omitted_evidence_refs": [],
                "human_review": review,
            }
        ],
        "draft_sentences": [
            {
                "id": "D-001",
                "text": "A commenter said the proposal could improve access for shift workers.",
                "summary_refs": ["S-001"],
                "perspective_refs": ["P-001"],
                "evidence_refs": ["E-thread#comment-1"],
                "flags": [],
                "model_signals": [],
                "suggested_rewrites": [],
                "human_review": review,
            }
        ],
        "lineage": [
            {
                "from_ref": "E-thread#comment-1",
                "to_ref": "P-001",
                "relation": "supports",
                "note": "The comment directly states the access concern.",
            },
            {
                "from_ref": "P-001",
                "to_ref": "S-001",
                "relation": "summarized_as",
                "note": "The perspective is compressed without changing attribution.",
            },
            {
                "from_ref": "E-thread#comment-1",
                "to_ref": "S-001",
                "relation": "supports",
                "note": "The source passage supports the summary sentence.",
            },
            {
                "from_ref": "S-001",
                "to_ref": "D-001",
                "relation": "propagates_to",
                "note": "The draft retains the summary's qualification.",
            },
            {
                "from_ref": "P-001",
                "to_ref": "D-001",
                "relation": "propagates_to",
                "note": "The draft represents this perspective.",
            },
            {
                "from_ref": "E-thread#comment-1",
                "to_ref": "D-001",
                "relation": "supports",
                "note": "The sentence remains linked to the source passage.",
            },
        ],
        "audit_findings": [],
        "reporting_gaps": [
            {
                "id": "G-001",
                "type": "missing_source_type",
                "description": "No transit operator appears in the supplied corpus.",
                "basis": "Only public comments were supplied.",
                "observed_in_corpus": False,
            }
        ],
        "limitations": ["The fixture is not representative of residents."],
        "human_review": review,
    }


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    json.loads(SCHEMA.read_text(encoding="utf-8"))
    skill = (ROOT / "skills/perspective-audit/SKILL.md").read_text(encoding="utf-8")
    assert "Do not create an opposing view solely to make a story appear balanced" in skill
    assert "representativeness" in skill
    assert "suggested_rewrites" in skill
    recipe = (ROOT / "recipes/perspective-audit.yaml").read_text(encoding="utf-8")
    assert "shell-safety skill" in recipe
    assert '"{{ output_dir }}/perspective-audit.json"' not in recipe
    assert "pass them as argv" in recipe

    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        audit_path = tmp / "perspective-audit.json"
        bundle_path = tmp / "evidence-bundle.json"
        valid = fixture()
        write_json(audit_path, valid)
        write_json(bundle_path, {"items": [{"id": "E-thread"}]})

        result = run_validator(audit_path, bundle_path)
        if result.returncode != 0:
            raise AssertionError(f"valid fixture rejected\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

        missing_lineage = copy.deepcopy(valid)
        missing_lineage["lineage"] = missing_lineage["lineage"][1:]
        write_json(audit_path, missing_lineage)
        result = run_validator(audit_path)
        assert result.returncode != 0
        assert "missing supports edge E-thread#comment-1 -> P-001" in result.stderr

        invented_gap = copy.deepcopy(valid)
        invented_gap["reporting_gaps"][0]["observed_in_corpus"] = True
        write_json(audit_path, invented_gap)
        result = run_validator(audit_path)
        assert result.returncode != 0
        assert "observed_in_corpus: must be false" in result.stderr

        write_json(audit_path, valid)
        write_json(bundle_path, {"items": [{"id": "E-other"}]})
        result = run_validator(audit_path, bundle_path)
        assert result.returncode != 0
        assert "not found in evidence bundle: E-thread" in result.stderr

    print("perspective-audit checks: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
