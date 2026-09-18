#!/usr/bin/env python3
"""Morning brief delegates privileged work to the typed Engine boundary."""
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
recipe = yaml.safe_load((root / "recipes/morning-brief.yaml").read_text())
text = recipe["prompt"] + recipe["instructions"]
for command in ("bsig brief status --json", "bsig brief run-now --json", "bsig brief open-result --json"):
    assert command in text, command
for unsafe in ("ft sync", "ft list", "curl ", "/v1/inboxes/default", "AGENTMAIL_API_KEY", "find {{", "openknowledge `write`"):
    assert unsafe not in text, unsafe
assert recipe["extensions"] == [{"type": "builtin", "name": "developer"}]
assert "explicit disclosure approval" in text
assert "confirmed inbox delivery" in text
print("morning brief Engine contract passed")
