"""Resolve the installed acquisition policy without silently changing providers."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


class AcquisitionConfigError(ValueError):
    """The selected configuration cannot safely select an acquisition backend."""


def load_acquisition() -> dict[str, str]:
    if os.name == "nt":
        appdata = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        goose_config = appdata / "Block" / "goose" / "config"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME", "")
        config_home = Path(xdg) if Path(xdg).is_absolute() else Path.home() / ".config"
        goose_config = config_home / "goose"
    profile = Path(os.environ.get("MYCROFT_PROFILE_DIR") or goose_config / "mycroft")
    selected = os.environ.get("MYCROFT_CONFIG")
    if selected == "":
        raise AcquisitionConfigError("MYCROFT_CONFIG is empty")
    path = Path(selected).expanduser() if selected is not None else profile.expanduser() / "mycroft-config.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        if (selected is None and "MYCROFT_PROFILE_DIR" not in os.environ
                and not profile.expanduser().exists() and not path.is_symlink()):
            # Standalone, unmanaged tools retain the local-only default.
            return {"search": "searxng", "scrape": "crawl4ai", "firecrawl": "disabled"}
        raise AcquisitionConfigError(f"Selected Mycroft config is missing: {path}") from exc
    except (OSError, ValueError) as exc:
        raise AcquisitionConfigError(f"Cannot read Mycroft config {path}: {exc}") from exc
    policy = config.get("acquisition") if isinstance(config, dict) else None
    if not isinstance(policy, dict):
        raise AcquisitionConfigError(f"Missing acquisition policy in {path}")
    search, scrape, cloud = (policy.get(key) for key in ("search", "scrape", "firecrawl"))
    if (search not in ("searxng", "firecrawl") or scrape not in ("crawl4ai", "firecrawl")
            or cloud not in ("disabled", "fallback")
            or ("firecrawl" in (search, scrape) and cloud != "fallback")):
        raise AcquisitionConfigError(f"Invalid acquisition policy in {path}: select known search/scrape providers and enable Firecrawl when selected")
    return {"search": search, "scrape": scrape, "firecrawl": cloud}


if __name__ == "__main__":
    try:
        policy = load_acquisition()
    except AcquisitionConfigError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(3)
    # Fixed enum values, for shell callers; never evaluate configuration as code.
    print(policy["search"], policy["scrape"], policy["firecrawl"])
