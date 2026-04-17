#!/usr/bin/env python3
"""Recipe schema validator for the Mycroft pack.

Walks recipes/ and extensions/manifest.json and asserts each file meets the
minimum Goose Recipe schema + our own manifest shape.

Exit 0 on success, 1 on any failure. Use from CI or manually.

Usage: python3 tools/validate-recipes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


REPO = Path(__file__).resolve().parent.parent
RECIPES = REPO / "recipes"
MANIFEST = REPO / "extensions" / "manifest.json"

REQUIRED_RECIPE_FIELDS = ["title", "description"]
REQUIRED_ONE_OF = ["instructions", "prompt"]  # Recipe must have at least one

VALID_EXTENSION_TYPES = {"builtin", "stdio", "platform", "streamable_http", "frontend", "inline_python"}


def validate_recipe(path: Path) -> list[str]:
    errs: list[str] = []
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict):
        return ["Top-level must be a mapping"]

    for field in REQUIRED_RECIPE_FIELDS:
        if field not in data:
            errs.append(f"missing required field: {field}")
        elif not isinstance(data[field], str) or not data[field].strip():
            errs.append(f"field {field} must be a non-empty string")

    if not any(data.get(k) for k in REQUIRED_ONE_OF):
        errs.append(f"must have at least one of: {', '.join(REQUIRED_ONE_OF)}")

    for ext in data.get("extensions", []) or []:
        if not isinstance(ext, dict):
            errs.append(f"extension entry must be a mapping: {ext!r}")
            continue
        t = ext.get("type")
        n = ext.get("name")
        if t not in VALID_EXTENSION_TYPES:
            errs.append(f"extension {n!r}: invalid type {t!r} (expected one of {sorted(VALID_EXTENSION_TYPES)})")
        if not n or not isinstance(n, str):
            errs.append(f"extension missing/invalid name: {ext!r}")

    for param in data.get("parameters", []) or []:
        if not isinstance(param, dict):
            errs.append(f"parameter entry must be a mapping: {param!r}")
            continue
        for k in ("key", "input_type", "requirement", "description"):
            if k not in param:
                errs.append(f"parameter missing required field {k!r}: {param.get('key', param)}")

    return errs


def validate_manifest(path: Path) -> list[str]:
    if not path.exists():
        return ["extensions/manifest.json missing"]
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"JSON parse error: {e}"]
    errs: list[str] = []
    for field in ("name", "version", "mcp_extensions", "plugins"):
        if field not in data:
            errs.append(f"manifest missing field: {field}")
    for ext in data.get("mcp_extensions", []):
        for k in ("name", "required", "used_by"):
            if k not in ext:
                errs.append(f"mcp_extensions entry missing {k!r}: {ext.get('name', ext)}")
    for plugin in data.get("plugins", []):
        for k in ("name", "repo", "status"):
            if k not in plugin:
                errs.append(f"plugins entry missing {k!r}: {plugin.get('name', plugin)}")
    return errs


def main() -> int:
    failed = 0
    checked = 0

    # Recipes
    recipe_files = sorted(RECIPES.rglob("*.yaml"))
    if not recipe_files:
        print(f"WARNING: no recipes found under {RECIPES}", file=sys.stderr)
    for f in recipe_files:
        errs = validate_recipe(f)
        rel = f.relative_to(REPO)
        if errs:
            failed += 1
            print(f"FAIL  {rel}")
            for e in errs:
                print(f"      - {e}")
        else:
            checked += 1
            print(f"OK    {rel}")

    # Manifest
    errs = validate_manifest(MANIFEST)
    rel = MANIFEST.relative_to(REPO)
    if errs:
        failed += 1
        print(f"FAIL  {rel}")
        for e in errs:
            print(f"      - {e}")
    else:
        checked += 1
        print(f"OK    {rel}")

    print()
    print(f"Checked: {checked}  Failed: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
