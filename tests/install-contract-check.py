#!/usr/bin/env python3
"""Dependency-free checks for the authored Mycroft install contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "install" / "contracts"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def lookup(inputs: dict[str, Any], dotted: str) -> Any:
    value: Any = inputs
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise AssertionError(f"missing template input: {dotted}")
        value = value[part]
    return value


def render(node: Any, inputs: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        if set(node) == {"$input"}:
            assert isinstance(node["$input"], str)
            return lookup(inputs, node["$input"])
        assert "$input" not in node, "$input must be the only key in an operation object"
        return {key: render(value, inputs) for key, value in node.items()}
    if isinstance(node, list):
        return [render(value, inputs) for value in node]
    return node


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def validate_manifest() -> None:
    manifest = load(CONTRACTS / "contract-manifest.json")
    assert manifest["schema_version"] == "mycroft-install-contract/v1"
    seen: set[str] = set()
    total = 0
    for entry in manifest["files"]:
        relative = Path(entry["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        assert entry["path"] not in seen
        seen.add(entry["path"])
        path = CONTRACTS / relative
        assert path.is_file() and not path.is_symlink()
        body = path.read_bytes()
        assert len(body) <= 256 * 1024
        total += len(body)
        assert hashlib.sha256(body).hexdigest() == entry["sha256"]
    assert total <= 1024 * 1024


def validate_schema_surface() -> None:
    for name in ("install-choices.schema.json", "mycroft-config.schema.json"):
        schema = load(CONTRACTS / name)
        encoded = json.dumps(schema)
        assert "http://" not in encoded
        assert '"pattern"' not in encoded
        assert '"$ref"' not in encoded


def validate_fixtures() -> None:
    template = load(CONTRACTS / "mycroft-config.template.json")
    assert template["schema_version"] == "mycroft-template/v1"
    assert template["output_schema"] == "mycroft-config/v2"
    for input_path in sorted((CONTRACTS / "testdata").glob("*.inputs.json")):
        stem = input_path.name.removesuffix(".inputs.json")
        expected_path = input_path.with_name(stem + ".expected.json")
        rendered = render(template["document"], load(input_path))
        assert canonical(rendered) == canonical(load(expected_path)), stem
        assert rendered["schema_version"] == "mycroft-config/v2"
        assert rendered["product"] == "mycroft"
        assert rendered["acquisition"]["search"] == "searxng"
        assert rendered["acquisition"]["scrape"] == "crawl4ai"
        assert rendered["acquisition"]["firecrawl"] in {"disabled", "fallback"}
        assert "installed_by" not in rendered
        assert "env" not in rendered["paths"]


def main() -> None:
    validate_manifest()
    validate_schema_surface()
    validate_fixtures()
    print("install contract ok")


if __name__ == "__main__":
    main()
