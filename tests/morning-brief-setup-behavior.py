#!/usr/bin/env python3
"""Exercise the setup recipes' typed actions against an isolated Engine binary.

Usage: python3 tests/morning-brief-setup-behavior.py /absolute/path/to/bsig
No network, keys, mail, subscriptions, OS jobs or real user state are used.
This tests command/state contracts; it is not a model conversation evaluation.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import yaml

engine = Path(sys.argv[1]).resolve(strict=True)
root = Path(__file__).resolve().parents[1]
setup = yaml.safe_load((root / "recipes/morning-brief-preflight.yaml").read_text())
news = yaml.safe_load((root / "recipes/newsletter-setup.yaml").read_text())
recipe_text = setup["prompt"] + news["prompt"]

with tempfile.TemporaryDirectory(prefix="mycroft-setup-behavior-") as temporary:
    home = Path(temporary)
    env = {"PATH": os.defpath, "HOME": str(home), "USERPROFILE": str(home),
           "XDG_CONFIG_HOME": str(home / "config"), "APPDATA": str(home / "appdata"),
           "LOCALAPPDATA": str(home / "local"), "TMPDIR": str(home)}

    def command(action, *args, data=None, ok=True):
        assert f"bsig brief {action}" in recipe_text, f"uncovered recipe action {action}"
        result = subprocess.run([str(engine), "brief", action, *args, "--json"],
                                input=json.dumps(data) if data is not None else "",
                                text=True, capture_output=True, env=env, timeout=20)
        assert (result.returncode == 0) == ok, (action, result.returncode, result.stdout, result.stderr)
        events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        for event in events:
            # Editorial choices belong in private files, not the NDJSON/audit channel.
            assert "fixture confidential beat" not in json.dumps(event)
        if not ok:
            return None
        results = [event["data"] for event in events if event.get("event") == "result"]
        assert results, (action, events)
        return results[-1]

    draft = {"beat": "newsletter-only draft", "source_notes": ["Selected publication; inbox not connected"], "channel": "email"}
    command("setup-draft", data=draft)
    assert json.loads(Path(command("setup-draft-show")["draft_file"]).read_text()) == draft
    assert command("status")["setup_draft_available"] is True
    config = {"version": 1, "profile": "morning", "beat": "fixture confidential beat",
              "watchlist": ["selected institution"], "exclusions": ["sports"],
              "sources": [{"id": "chosen", "kind": "rss", "location": "https://example.com/feed",
                           "collect": True, "disclose": True, "visibility": "public"}],
              "window_hours": 24, "days": [1, 2, 3, 4, 5], "local_time": "07:30",
              "timezone": "Europe/Zurich", "channel": "goose"}
    assert command("status")["schedule"] == "unconfigured"
    plan = command("plan", data=config)
    assert plan["next_run"] and plan["timezone"] == config["timezone"]
    assert command("status")["schedule"] == "unconfigured", "planning activated recurrence"
    command("apply", plan["plan_id"])
    state = command("status")
    assert state["schedule"] == "paused" and state["verification"]["status"] == "not_started"
    assert state["setup_draft_available"] is False
    command("verify", ok=False)  # No Enable: no background job may be installed.
    restored = json.loads(Path(command("config")["config_file"]).read_text())
    assert restored == config, "credential handoff/new chat lost the saved draft"

    # Choosing email and then Goose-only preserves editorial choices and a mail source.
    newsletter = {"id": "newsletter", "kind": "newsletter", "location": "https://example.com/news",
                  "inbox_id": "inbox_fixture", "sender": "news@example.com", "collect": True,
                  "disclose": False, "visibility": "private"}
    email = {**config, "sources": config["sources"] + [newsletter], "channel": "email",
             "recipient": "reader@example.com", "inbox": "inbox_fixture", "inbox_address": "brief@agentmail.to"}
    command("apply", command("plan", data=email)["plan_id"])
    goose = {**email, "channel": "goose"}
    for key in ("recipient", "inbox", "inbox_address"):
        goose.pop(key)
    command("apply", command("plan", data=goose)["plan_id"])
    resumed = json.loads(Path(command("config")["config_file"]).read_text())
    assert resumed == goose
    generation = command("status")["generation"]

    publication = {"id": "chosen-news", "name": "Selected publication", "url": "https://example.com/news",
                   "inbox_id": "inbox_fixture", "inbox_address": "brief@agentmail.to", "sender": "",
                   "selected": True, "status": "human_action_required", "evidence_kind": "manual_handoff",
                   "evidence_ref": "https://example.com/news"}
    for status, kind in [("human_action_required", "captcha"), ("submitted", "user_reported_submission"),
                         ("confirmation_pending", "confirmation_requested"), ("active", "user_confirmed_receipt")]:
        publication.update(status=status, evidence_kind=kind)
        if status == "active":
            publication.update(sender="news@example.com", evidence_ref="Journalist reports the welcome issue arrived")
        command("newsletter-record", data=publication)
        records = json.loads(Path(command("newsletter-list")["newsletters_file"]).read_text())
        assert records[0]["publication"]["status"] == status
    # Retry/restart preserves one evidence event; source permissions are separate.
    command("newsletter-record", data=publication)
    records = json.loads(Path(command("newsletter-list")["newsletters_file"]).read_text())
    assert len(records[0]["events"]) == 4
    command("newsletter-record", data={**publication, "evidence_kind": "form_submitted"}, ok=False)
    command("newsletter-record", data={**publication, "selected": False}, ok=False)
    command("newsletter-record", data={**publication, "url": "https://example.com/confirm?token=secret"}, ok=False)
    assert command("status")["generation"] == generation
    assert json.loads(Path(command("config")["config_file"]).read_text()) == goose
print("morning brief setup action/state scenarios passed (isolated Engine; no live model or services)")
