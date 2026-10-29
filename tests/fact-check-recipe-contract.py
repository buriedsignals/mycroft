#!/usr/bin/env python3
"""Contract checks for the default Mycroft fact-check recipe."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "recipes/fact-check.yaml"
FACT_CHECK_RECIPES = (RECIPE, ROOT / "recipes/fact-check-c2pa.yaml")


def parameter_default(recipe: str, key: str) -> str:
    match = re.search(
        rf"- key: {re.escape(key)}\n(?:(?:    .*\n)*?)    default: ([^\n]+)",
        recipe,
    )
    if not match:
        raise AssertionError(f"missing parameter default for {key}")
    return match.group(1).strip()


def check_parameter_use(path: Path) -> None:
    """Goose rejects declared-but-unused parameters, and renders every
    parameter value as a string, so a bare `{% if flag %}` is true for "false"."""
    recipe = path.read_text(encoding="utf-8")
    expressions = " ".join(re.findall(r"\{\{.*?\}\}|\{%.*?%\}", recipe, re.S))
    for key in re.findall(r"^  - key: (\w+)$", recipe, re.M):
        assert re.search(rf"\b{key}\b", expressions), f"{path.name}: {key} is declared but never used in a template"
    for key in re.findall(r"^  - key: (\w+)\n    input_type: boolean$", recipe, re.M):
        assert not re.search(rf"\{{%\s*if\s+{key}\s*%\}}", recipe), (
            f"{path.name}: bare {{% if {key} %}} is true for the string \"false\""
        )
        assert f'{{% if {key} | string | lower == "true" %}}' in recipe, f"{path.name}: {key} must compare to \"true\""


def main() -> int:
    for path in FACT_CHECK_RECIPES:
        check_parameter_use(path)

    recipe = RECIPE.read_text(encoding="utf-8")

    assert "mycroft-fetch" in recipe, "default fact-checking must capture provenance through mycroft-fetch"
    assert "firecrawl CLI for verification" not in recipe, "default fact-checking must not point agents at raw firecrawl"
    assert parameter_default(recipe, "emit_manifest") == "true"
    assert parameter_default(recipe, "strict_provenance") == "false"
    assert parameter_default(recipe, "c2pa_sign") == "false"
    assert "Provenance is default but not mandatory" in recipe
    assert "If provenance validation or manifest generation fails" in recipe
    assert "Strict provenance is on." in recipe and "continue the fact-check. Preserve the markdown verdict table" in recipe
    assert "C2PA signing is optional and off by default" in recipe
    assert "build-provenance-manifest.py" in recipe
    assert "NOOSPHERE_C2PA_URL" in recipe
    assert "references/extraction.md" in recipe, "extraction must load the Big If True-derived rules"
    assert "claim-density.py" in recipe, "extraction must run the density gate before verification"
    assert "marketdata.py\" --evidence" in recipe and "evidence-lookup.py\" --evidence" in recipe, (
        "primary-record lookups must capture provenance with --evidence"
    )
    skill = (ROOT / "skills/fact-check/SKILL.md").read_text(encoding="utf-8")
    assert "references/extraction.md" in skill and "claim-density.py" in skill
    for route in ("markets-economy", "quotes-attribution", "web-social-archives", "science-studies", "companies-courts", "official-statistics"):
        assert (ROOT / f"skills/fact-check/references/routes/{route}.md").is_file(), f"missing route file {route}"
        assert route in skill, f"SKILL.md must name the {route} route"
    soul = (ROOT / "instructions/mycroft-soul.md").read_text(encoding="utf-8")
    assert "Do not use this skill for software code" in skill and "route those to compound-engineering." in skill, (
        "fact-check must route software code review to compound-engineering"
    )
    assert "Do not route software code" in soul and "Use the host's compound-engineering or code-review workflow." in soul
    for stale in ("escalating to Spotlight for deeper adversarial review", "If Spotlight is installed and the request needs adversarial review"):
        assert stale not in skill, f"SKILL.md must not escalate code review to Spotlight: {stale}"
    assert "Escalate to Spotlight when the work needs adversarial review" not in soul
    assert "verso.ink" in skill and "verso.ink/big-if-true" in (ROOT / "index.html").read_text(encoding="utf-8"), "Verso credit missing"

    print("fact-check recipe contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
