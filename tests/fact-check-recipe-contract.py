#!/usr/bin/env python3
"""Contract checks for the default Mycroft fact-check recipe."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "recipes/fact-check.yaml"


def parameter_default(recipe: str, key: str) -> str:
    match = re.search(
        rf"- key: {re.escape(key)}\n(?:(?:    .*\n)*?)    default: ([^\n]+)",
        recipe,
    )
    if not match:
        raise AssertionError(f"missing parameter default for {key}")
    return match.group(1).strip()


def main() -> int:
    recipe = RECIPE.read_text(encoding="utf-8")

    assert "mycroft-fetch" in recipe, "default fact-checking must capture provenance through mycroft-fetch"
    assert "firecrawl CLI for verification" not in recipe, "default fact-checking must not point agents at raw firecrawl"
    assert parameter_default(recipe, "emit_manifest") == "true"
    assert parameter_default(recipe, "strict_provenance") == "false"
    assert parameter_default(recipe, "c2pa_sign") == "false"
    assert "Provenance is default but not mandatory" in recipe
    assert "If provenance validation or manifest generation fails" in recipe
    assert "continue the fact-check unless `strict_provenance` is true" in recipe
    assert "C2PA signing is optional and off by default" in recipe
    assert "build-provenance-manifest.py" in recipe
    assert "NOOSPHERE_C2PA_URL" in recipe

    print("fact-check recipe contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
