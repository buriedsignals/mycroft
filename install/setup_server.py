#!/usr/bin/env python3
"""Mycroft local configurator server.

Launched by install.sh. Serves install/configure.html on 127.0.0.1, receives
the journalist's choices and API keys via POST (nothing ever leaves the
machine), live-validates the keys against their providers, then writes:

  <profile>/.env                  — full Mycroft environment incl. secrets (0600)
  <profile>/setup-config.env      — non-secret choice flags for install.sh (0600)
  <profile>/skill-registry.json   — enabled-skill registry
  <profile>/getting-started.html  — personalized post-install guide

Exits 0 once configuration is written, 1 on timeout/abort. Stdlib only.
"""

import argparse
import json
import os
import platform
import secrets
import shlex
import string
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from engine_bridge import EngineBridge, EngineUnavailable
from navigator_bridge import NavigatorBridgeError, NavigatorInstallerBridge

SUBMIT_TIMEOUT_SECONDS = 30 * 60

PICKER_PROMPTS = {"vault_path": "Choose your Mycroft vault folder", "spotlight_vault_path": "Choose your Spotlight vault folder"}

# Public Supabase anon key for hosted Scoutpost (functions/v1). Not a secret — it is
# baked into the engine binary and the SPA; sent as the `apikey:` header alongside the
# cj_ bearer token, which the Edge Functions front door requires.
SCOUTPOST_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdmbWR6aXBsdGljZm9ha2hyZnB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc2MDYzMjIsImV4cCI6MjA4MzE4MjMyMn0.Liz22BqK2qfHBcIsIJxGTT4VvMzfBE_yRFraVrUPKq4"


def detect_platform():
    """mac | linux | windows-wsl — the page preselects matching path defaults."""
    sysname = platform.system()
    if sysname == "Darwin":
        return "mac"
    if sysname == "Linux":
        try:
            with open("/proc/version", encoding="utf-8") as f:
                if "microsoft" in f.read().lower():
                    return "windows-wsl"
        except OSError:
            pass
        return "linux"
    return "linux"


def pick_folder_natively(prompt):
    """Open a native OS folder dialog; returns (path|None, error|None).

    Runs on the install machine, so this works where a hosted page never
    could. Cancel returns (None, None).
    """
    sysname = platform.system()
    try:
        if sysname == "Darwin":
            r = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to activate',
                 "-e", f'POSIX path of (choose folder with prompt "{prompt}")'],
                capture_output=True, text=True, timeout=300)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip().rstrip("/"), None
            return None, None  # cancelled
        for cmd in (["zenity", "--file-selection", "--directory", "--title", prompt],
                    ["kdialog", "--getexistingdirectory", os.path.expanduser("~"), "--title", prompt]):
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            except FileNotFoundError:
                continue
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip(), None
            return None, None  # cancelled
        return None, "No folder picker available — type the path instead."
    except subprocess.TimeoutExpired:
        return None, None
    except Exception as e:
        return None, f"Folder picker failed: {e}"

LOCAL_MODELS = {
    "gemma31b": {
        # Served via the official Ollama Gemma-4 31B QAT tag → GOOSE_MODEL
        # "gemma4:31b-it-qat" (repo:quantization). No HF GGUF download / no
        # thinking mode / no stop-token workaround.
        "name": "gemma4-31b",
        "repo": "gemma4",
        "filename": "",
        "quantization": "31b-it-qat",
        "vision": False,
        "enable_thinking": False,
        "label": "Gemma 4 31B · recommended · runs on your machine, $0/mo",
    },
    "qwen27b": {
        "name": "qwen3.6-27b-abliterated-journalist",
        "repo": "tomvaillant/qwen3.6-27b-abliterated-journalist-GGUF",
        "filename": "qwen3.6-27b-abliterated-journalist-Q4_K_M.gguf",
        "quantization": "Q4_K_M",
        "vision": False,
        "enable_thinking": True,
        "label": "Qwen 3.6 27B Journalist · runs on your machine, $0/mo",
    },
}


def expand_home_for_shell(path):
    """Mirror the old setup page: ~/x -> $HOME/x so sourcing expands it."""
    p = str(path or "").strip()
    if p == "~":
        return "$HOME"
    if p.startswith("~/"):
        return "$HOME/" + p[2:]
    return p


def b01(value):
    return "1" if value else "0"


# ── Structural validation (mirror of the old client-side validateForm) ──

def validate_choices(d):
    errors = []
    if not str(d.get("vault") or "").strip():
        errors.append({"field": "vault_path", "message": "Vault path is required — Mycroft has nowhere to keep your knowledge without it."})
    if d.get("installFirecrawl") and not d.get("firecrawlKey"):
        errors.append({"field": "firecrawl_key", "message": "A FIRECRAWL_API_KEY is required only when the optional Firecrawl fallback is selected."})
    if not d.get("localOnly"):
        if not d.get("fireworksKey"):
            errors.append({"field": "fireworks_key", "message": "Cloud-first runs on Fireworks (GLM-5.2, ZDR) — FIREWORKS_API_KEY is required, or switch to Local-first."})
    if d.get("scoutpost") and not d.get("scoutpostKey"):
        errors.append({"field": "scoutpost_api_key", "message": "SCOUTPOST_API_KEY is required while Scoutpost is enabled — add a key or untick the plugin."})
    if d.get("spotlight") and not str(d.get("spotlightVaultPath") or "").strip():
        errors.append({"field": "spotlight_vault_path", "message": "Spotlight needs its own vault path while it is enabled."})
    return errors


# ── Live key validation ──
# Strict checks reject only on 401/403 — an unreachable or moved endpoint
# must never block an install. Lenient checks warn but never reject.

def probe(url, headers):
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=8):
            return "ok"
    except urllib.error.HTTPError as e:
        return "rejected" if e.code in (401, 403) else "ok"
    except Exception:
        return "unreachable"


def validate_keys(d, skip=False):
    errors, warnings = [], []
    if skip:
        return errors, warnings
    checks = []
    if d.get("firecrawlKey"):
        checks.append(("firecrawl_key", "FIRECRAWL_API_KEY", True,
                       "https://api.firecrawl.dev/v1/team/credit-usage",
                       {"Authorization": "Bearer " + d["firecrawlKey"]}))
    if not d.get("localOnly") and d.get("fireworksKey"):
        checks.append(("fireworks_key", "FIREWORKS_API_KEY", True,
                       "https://api.fireworks.ai/inference/v1/models",
                       {"Authorization": "Bearer " + d["fireworksKey"]}))
    if d.get("scoutpost") and d.get("scoutpostKey"):
        checks.append(("scoutpost_api_key", "SCOUTPOST_API_KEY", False,
                       "https://scoutpost.ai/functions/v1/scouts",
                       {"Authorization": "Bearer " + d["scoutpostKey"],
                        "apikey": SCOUTPOST_ANON_KEY}))
    for field, name, strict, url, headers in checks:
        result = probe(url, headers)
        if result == "rejected" and strict:
            errors.append({"field": field, "message": f"{name} was rejected by the provider (401/403) — check the key and try again."})
        elif result == "rejected":
            warnings.append(f"{name} could not be verified (provider returned 401/403); continuing anyway.")
        elif result == "unreachable":
            warnings.append(f"{name} could not be verified (provider unreachable); continuing anyway.")
    return errors, warnings


# ── Generated artifacts ──

def build_env_lines(d):
    vault = expand_home_for_shell(d["vault"])
    spotlight_vault = expand_home_for_shell(d.get("spotlightVaultPath") or "~/Documents/Spotlight")
    lines = [
        "# Mycroft environment — generated by the local configurator",
        f"MYCROFT_DEFAULT_SOVEREIGNTY={shlex.quote(d['sovereignty'])}",
        f'MYCROFT_VAULT_PATH="{vault}"',
        'MYCROFT_PROFILE_DIR="$HOME/.config/goose/mycroft"',
        'MYCROFT_DATA_DIR="$HOME/.local/share/goose/mycroft"',
        'MYCROFT_SOURCE_DIR="$MYCROFT_DATA_DIR/source"',
        'MYCROFT_DIR="$MYCROFT_SOURCE_DIR"',
        'MYCROFT_PLUGINS_DIR="$MYCROFT_DATA_DIR/plugins"',
        'MYCROFT_PROFILE_SKILLS_DIR="$MYCROFT_PROFILE_DIR/skills"',
        'MYCROFT_SKILLS_DIR="$MYCROFT_DIR/skills"',
        'MYCROFT_SKILL_REGISTRY="$MYCROFT_PROFILE_DIR/skill-registry.json"',
        'MYCROFT_GENERATED_RECIPES="$MYCROFT_PROFILE_DIR/generated-recipes"',
        'MYCROFT_MORNING_BRIEF_CONFIG="$MYCROFT_PROFILE_DIR/morning-brief-config.md"',
        'GOOSE_MOIM_MESSAGE_FILE="$MYCROFT_PROFILE_DIR/SOUL.md"',
        'GOOSE_RECIPE_PATH="$MYCROFT_DIR/recipes:$MYCROFT_GENERATED_RECIPES"',
        f"MYCROFT_LOCAL_ONLY={b01(d['localOnly'])}",
    ]
    if d["localOnly"]:
        model = LOCAL_MODELS.get(d.get("localModel") or "gemma31b", LOCAL_MODELS["gemma31b"])
        lines += [
            "GOOSE_PROVIDER=local",
            "GOOSE_MODEL=" + model["repo"] + ":" + model["quantization"],
            "MYCROFT_LOCAL_MODEL=" + model["name"],
            "MYCROFT_LOCAL_MODEL_REPO=" + model["repo"],
            "MYCROFT_LOCAL_MODEL_FILE=" + model["filename"],
            "MYCROFT_LOCAL_MODEL_QUANT=" + model["quantization"],
            "MYCROFT_LOCAL_MODEL_VISION=" + b01(model["vision"]),
            "MYCROFT_LOCAL_MODEL_THINKING=" + b01(model["enable_thinking"]),
        ]
    else:
        lines += ["GOOSE_PROVIDER=fireworks-glm52",
                  "GOOSE_MODEL=accounts/fireworks/models/glm-5p2"]
    for key, name in [("fireworksKey", "FIREWORKS_API_KEY"),
                      ("firecrawlKey", "FIRECRAWL_API_KEY"), ("apifyToken", "APIFY_API_TOKEN"),
                      ("agentmailKey", "AGENTMAIL_API_KEY")]:
        if d.get(key):
            lines.append(f"{name}={shlex.quote(d[key])}")
    if d.get("scoutpost") and d.get("scoutpostKey"):
        lines.append("SCOUTPOST_API_KEY=" + shlex.quote(d["scoutpostKey"]))
        lines.append("SCOUTPOST_API_BASE=https://scoutpost.ai/functions/v1")
        lines.append("SCOUTPOST_SUPABASE_ANON_KEY=" + shlex.quote(SCOUTPOST_ANON_KEY))
    if d.get("spotlight"):
        lines.append('SPOTLIGHT_DIR="$MYCROFT_PLUGINS_DIR/spotlight"')
        lines.append(f'SPOTLIGHT_VAULT_PATH="{spotlight_vault}"')
        lines.append(f'SPOTLIGHT_INGEST_TARGET="{vault}"')
        lines.append("SPOTLIGHT_SOVEREIGNTY_INHERITS_MYCROFT=1")
        if d.get("scoutpost"):
            lines.append("SPOTLIGHT_MONITORING_BACKEND=scoutpost")
            lines.append("SPOTLIGHT_SCOUT_REQUESTS=scoutpost")
        if d.get("junkipediaKey"):
            lines.append("JUNKIPEDIA_API_KEY=" + shlex.quote(d["junkipediaKey"]))
    return "\n".join(lines) + "\n"


def build_setup_config(d):
    required = []
    if d.get("firecrawlKey"):
        required.append("FIRECRAWL_API_KEY")
    if not d["localOnly"]:
        required.append("FIREWORKS_API_KEY")
    if d.get("scoutpost"):
        required.append("SCOUTPOST_API_KEY")
    lines = [
        "# Mycroft setup choices — generated by the local configurator (no secrets)",
        f"SOVEREIGNTY={shlex.quote(d['sovereignty'])}",
        f"LOCAL_ONLY={b01(d['localOnly'])}",
        f"LOCAL_MODEL={shlex.quote(d.get('localModel') or 'gemma31b')}",
        f'VAULT_PATH="{expand_home_for_shell(d["vault"])}"',
        f'SPOTLIGHT_VAULT_INPUT="{expand_home_for_shell(d.get("spotlightVaultPath") or "~/Documents/Spotlight")}"',
        f"INSTALL_GOOSE={b01(d.get('installGoose'))}",
        f"INSTALL_OBSIDIAN={b01(d.get('installObsidian'))}",
        f"INSTALL_FIRECRAWL={b01(d.get('installFirecrawl'))}",
        f"ENABLE_SPOTLIGHT={b01(d.get('spotlight'))}",
        f"ENABLE_SCOUTPOST={b01(d.get('scoutpost'))}",
        f"ENABLE_FIREWORKS={b01(not d['localOnly'])}",
        f"ENABLE_FT={b01(d.get('ftEnabled'))}",
        f"ENABLE_AGENTMAIL={b01(d.get('agentmailEnabled') or d.get('agentmailKey'))}",
        f"ENABLE_APIFY={b01(d.get('apifyEnabled') or d.get('apifyToken'))}",
        f"SPOT_DEVBROWSER={b01(d.get('spotDevBrowser'))}",
        f"HAS_OSINT_NAVIGATOR={b01(d.get('navigatorConnected'))}",
        f"NAVIGATOR_CONNECTION={'connected' if d.get('navigatorConnected') else 'locked'}",
        f"HAS_JUNKIPEDIA={b01(d.get('junkipediaKey'))}",
        f'REQUIRED_DOCTOR_ENV="{" ".join(required)}"',
    ]
    return "\n".join(lines) + "\n"


# Skill ids come from the vendored skills.manifest (generated by the engine's
# `bsig skills vendor`; the signed catalog is the source of truth). T12 removed
# the hardcoded list — only install-flow nuances the flat manifest cannot
# express live in the tables below.
SKILL_SOURCE_ROOT = "~/.local/share/goose/mycroft/source"
SKILL_ENABLE_GATES = {
    "obsidian": lambda d: bool(d.get("installObsidian")),
    "obsidian-ingest": lambda d: bool(d.get("installObsidian")),
    "firecrawl": lambda d: bool(d.get("installFirecrawl") or d.get("firecrawlKey")),
}
SKILL_STATUS = {"copywriting": "placeholder"}


def build_skill_registry(d):
    manifest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills.manifest")
    try:
        with open(manifest) as f:
            ids = [line.strip() for line in f if line.strip()]
    except OSError:
        ids = []
    skills = []
    for sid in ids:
        if sid == "scoutpost":
            continue  # hosted skill; the conditional block below owns it
        gate = SKILL_ENABLE_GATES.get(sid)
        entry = {
            "id": sid,
            "path": "%s/skills/%s/SKILL.md" % (SKILL_SOURCE_ROOT, sid),
            "source": "mycroft",
            "enabled": gate(d) if gate else True,
        }
        if sid in SKILL_STATUS:
            entry["status"] = SKILL_STATUS[sid]
        skills.append(entry)
    if d.get("scoutpost"):
        skills.append({"id": "scoutpost", "path": "~/.agents/skills/mycroft/scoutpost/SKILL.md", "source": "mycroft-repo", "enabled": True, "product_skill_url": "https://scoutpost.ai/skills/scoutpost.md"})
    if d.get("spotlight"):
        skills += [
            {"id": "spotlight", "path": "~/.local/share/goose/mycroft/plugins/spotlight/skills/spotlight/SKILL.md", "source": "spotlight", "enabled": True},
            {"id": "spotlight-ingest", "path": "~/.local/share/goose/mycroft/plugins/spotlight/skills/ingest/SKILL.md", "source": "spotlight", "enabled": True},
            {"id": "spotlight-monitoring", "path": "~/.local/share/goose/mycroft/plugins/spotlight/skills/monitoring/SKILL.md", "source": "spotlight", "enabled": True},
            {"id": "spotlight-integrations", "path": "~/.local/share/goose/mycroft/plugins/spotlight/skills/integrations/SKILL.md", "source": "spotlight", "enabled": True},
        ]
    return {"schema_version": "mycroft-skill-registry/v1", "skills": skills}


GETTING_STARTED_TEMPLATE = string.Template("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mycroft — Getting started</title>
<style>
  :root {
    --vellum: #e8e0cf; --vellum-bright: #faf5e8; --vellum-2: #dfd5be;
    --ink: #1a1a1f; --ink-soft: #4a4439; --ink-dim: #8e8676;
    --oxide: #4a7363; --hairline: 1px solid rgba(26,26,31,0.22);
    --serif: Georgia, 'Times New Roman', serif;
    --mono: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
    --sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--vellum); color: var(--ink); font: 15px/1.65 var(--sans); }
  .shell { max-width: 860px; margin: 0 auto; padding: clamp(32px, 6vw, 80px) clamp(20px, 4vw, 48px) 96px; }
  .brand { font-family: var(--serif); font-weight: 800; font-size: 20px; letter-spacing: -0.01em; }
  .brand em { color: var(--oxide); font-style: normal; }
  h1 { font-family: var(--serif); font-weight: 800; font-size: clamp(40px, 7vw, 64px); line-height: 1.02; letter-spacing: -0.02em; margin: 24px 0 12px; }
  h1 em { font-style: italic; color: var(--oxide); }
  .lede { font-size: 17px; color: var(--ink-soft); max-width: 56ch; }
  .num { font-family: var(--mono); font-size: 11px; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink-dim); margin: 64px 0 8px; }
  h2 { font-family: var(--serif); font-weight: 800; font-size: clamp(26px, 4vw, 34px); letter-spacing: -0.015em; margin: 0 0 16px; }
  h2 em { font-style: italic; color: var(--oxide); }
  .card { background: var(--vellum-bright); border: var(--hairline); padding: 20px 22px; margin: 0 0 12px; }
  .card .k { font-family: var(--mono); font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--ink-dim); margin: 0 0 8px; }
  .card code, .card pre { font-family: var(--mono); font-size: 13px; color: var(--ink); background: none; white-space: pre-wrap; word-break: break-word; }
  table { width: 100%; border-collapse: collapse; background: var(--vellum-bright); border: var(--hairline); }
  th, td { text-align: left; padding: 10px 16px; border-bottom: 1px solid rgba(26,26,31,0.12); font-size: 14px; vertical-align: top; }
  th { font-family: var(--mono); font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--ink-dim); font-weight: 500; }
  td code { font-family: var(--mono); font-size: 12.5px; word-break: break-all; }
  .callout { background: var(--vellum-2); border: var(--hairline); border-left: 3px solid var(--oxide); padding: 18px 22px; margin: 16px 0; }
  .callout.urgent { border-left-color: #a83a26; }
  ol, ul { padding-left: 1.3em; } li { margin: 6px 0; }
  a { color: var(--oxide); }
  .foot { margin-top: 80px; padding-top: 24px; border-top: var(--hairline); font-size: 13px; color: var(--ink-dim); }
</style>
</head>
<body>
<div class="shell">
  <p class="brand">Mycroft<em>.</em></p>
  <h1>You're <em>in.</em></h1>
  <p class="lede">Mycroft is installed and wired into Goose. This page is your map for the first hour — what landed on your machine, the two switches that matter, and what to say to Mycroft first.</p>

  <p class="num">01 — Your install</p>
  <h2>What landed <em>where.</em></h2>
  <table>
    <tr><th>Mode</th><td>$mode_label · $provider_label</td></tr>
    <tr><th>Knowledge vault</th><td><code>$vault</code> — your durable newsroom memory (Obsidian-compatible)</td></tr>
$spotlight_vault_row    <tr><th>Profile</th><td><code>~/.config/goose/mycroft</code> — config, env, skill registry</td></tr>
    <tr><th>Source</th><td><code>~/.local/share/goose/mycroft/source</code> — recipes + skills, auto-updated weekly</td></tr>
$plugins_row$optional_row  </table>

$obsidian_section  <p class="num">$n_first — First run</p>
  <h2>Open Goose, meet <em>Mycroft.</em></h2>
  <p>Goose opened at the end of setup with the <strong>Start Mycroft</strong> recipe (if not, open Goose and pick it from the recipe list). Your vault also has a <code>START_HERE.md</code> note. The first-run menu offers: set up your beat, add material to your knowledge base, create your morning brief, investigate a lead, set up scouts, or a demo workflow.</p>

  <p class="num">$n_prompts — Things to say</p>
  <h2>Copy, paste, <em>adapt.</em></h2>
$prompt_cards
  <p class="num">$n_schedule — On schedule</p>
  <h2>While you <em>sleep.</em></h2>
  <table>
    <tr><th>Morning brief</th><td>Daily 07:00 — digest from your beats, watchlists$brief_sources, and recent vault changes. Run "Create my morning brief" once to configure it.</td></tr>
    <tr><th>Vault audit</th><td>Daily 18:15 — flags weak claims, missing frontmatter, orphaned sources, stale handoffs.</td></tr>
    <tr><th>Updates</th><td>Weekly Monday 10:15 — pulls the latest recipes and skills, verifies with <code>mycroft doctor</code>, rolls back on failure.</td></tr>
  </table>

  <p class="num">$n_doctor — When something breaks</p>
  <h2>Doctor first, <em>then docs.</em></h2>
  <div class="card"><p class="k">In a new terminal</p><pre>mycroft doctor    # checks every install path and key
mycroft update    # manual update anytime</pre></div>
  <p>Still stuck? <a href="https://github.com/buriedsignals/mycroft/blob/main/docs/troubleshooting.md">Troubleshooting guide</a> · <a href="https://github.com/buriedsignals/mycroft/issues">Open an issue</a></p>

  <p class="foot">Mycroft · Every journalist, a newsroom. Built by <a href="https://buriedsignals.com/">Buried Signals</a>. This guide lives at <code>~/.config/goose/mycroft/getting-started.html</code>.</p>
</div>
</body>
</html>
""")

OBSIDIAN_SECTION = """  <p class="num">02 — Before anything else</p>
  <h2>Two switches in <em>Obsidian.</em></h2>
  <div class="callout urgent">
    <strong>Vault recipes fail silently without these.</strong>
    <ol>
      <li>Open Obsidian → Settings → General → Advanced → <strong>CLI: ON</strong></li>
      <li>Keep Obsidian <strong>running</strong> whenever you work with Mycroft</li>
    </ol>
  </div>

"""


def esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_getting_started(d):
    if d["localOnly"]:
        model = LOCAL_MODELS.get(d.get("localModel") or "gemma31b", LOCAL_MODELS["gemma31b"])
        provider_label = model["label"]
    else:
        provider_label = "Fireworks AI · GLM-5.2 (ZDR cloud)"

    optional = []
    if d.get("ftEnabled"):
        optional.append("ft CLI (X bookmarks)")
    if d.get("agentmailEnabled") or d.get("agentmailKey"):
        optional.append("AgentMail (newsletters + tips inbox)")
    if d.get("apifyEnabled") or d.get("apifyToken"):
        optional.append("Apify (social scraping)")
    if d.get("navigatorConnected"):
        optional.append("Navigator (Pro: OSINT; Lab: OSINT + Data Navigator)")
    else:
        optional.append("Navigator skill (locked; no credential or CLI)")

    plugins = []
    if d.get("spotlight"):
        plugins.append("Spotlight (OSINT investigations)")
    if d.get("scoutpost"):
        plugins.append("Scoutpost (free monitoring tier, including MuckRock)")

    prompts = [
        ("Set up your beat", "Set up my beat. I cover [your beat] in [your region]."),
        ("Feed the vault", "Add this to my knowledge base: [paste a link, or drop a PDF / folder path]"),
        ("Ask your vault", "What do we know about [person, company, or topic]?"),
        ("Morning brief", "Create my morning brief."),
        ("Fact-check", "Fact-check this draft: [paste your draft]"),
    ]
    if d.get("spotlight"):
        prompts.append(("Investigate", "Investigate [your lead] — open a Spotlight case."))
    if d.get("scoutpost"):
        prompts.append(("Watch a source", "Set up a scout to watch [page, account, or council agenda]."))
    prompts.append(("See it work", "Show me a demo workflow."))
    prompt_cards = "".join(
        f'      <div class="card">\n        <p class="k">{i + 1:02d} — {esc(label)}</p>\n        <code>{esc(text)}</code>\n      </div>\n'
        for i, (label, text) in enumerate(prompts)
    )

    brief_sources = ""
    if d.get("agentmailEnabled") or d.get("agentmailKey"):
        brief_sources += ", AgentMail inbox"
    if d.get("ftEnabled"):
        brief_sources += ", X bookmarks"

    has_obsidian = bool(d.get("installObsidian"))
    base = 3 if has_obsidian else 2
    return GETTING_STARTED_TEMPLATE.substitute(
        mode_label="Local-first" if d["localOnly"] else "Cloud-first",
        provider_label=esc(provider_label),
        vault=esc(d["vault"]),
        spotlight_vault_row=(
            f'    <tr><th>Spotlight vault</th><td><code>{esc(d.get("spotlightVaultPath"))}</code> — active investigation casework, kept separate</td></tr>\n'
            if d.get("spotlight") else ""
        ),
        plugins_row=(f'    <tr><th>Plugins</th><td>{esc(" · ".join(plugins))}</td></tr>\n' if plugins else ""),
        optional_row=(f'    <tr><th>Optional tools</th><td>{esc(" · ".join(optional))}</td></tr>\n' if optional else ""),
        obsidian_section=OBSIDIAN_SECTION if has_obsidian else "",
        n_first=f"0{base}",
        n_prompts=f"0{base + 1}",
        prompt_cards=prompt_cards,
        n_schedule=f"0{base + 2}",
        brief_sources=brief_sources,
        n_doctor=f"0{base + 3}",
    )


def write_artifacts(d, profile_dir):
    os.makedirs(profile_dir, mode=0o700, exist_ok=True)

    def write(name, content, mode=0o600):
        path = os.path.join(profile_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(path, mode)
        return path

    write(".env", build_env_lines(d))
    write("setup-config.env", build_setup_config(d))
    write("skill-registry.json", json.dumps(build_skill_registry(d), indent=2) + "\n", 0o644)
    write("getting-started.html", build_getting_started(d), 0o644)


def normalize(payload):
    """Coerce the POSTed form payload into the canonical choice dict."""
    def s(k):
        return str(payload.get(k) or "").strip()

    def b(k):
        return bool(payload.get(k))

    sovereignty = s("sovereignty") or "cloud"
    return {
        "sovereignty": sovereignty,
        "localOnly": sovereignty == "local",
        "localModel": s("localModel") or "gemma31b",
        # No silent defaults here: an emptied path must fail validation,
        # not quietly install somewhere the user didn't choose.
        "vault": s("vault"),
        "spotlightVaultPath": s("spotlightVaultPath"),
        "installGoose": b("installGoose"),
        "installObsidian": b("installObsidian"),
        "installFirecrawl": b("installFirecrawl"),
        "ftEnabled": b("ftEnabled"),
        "agentmailEnabled": b("agentmailEnabled"),
        "apifyEnabled": b("apifyEnabled"),
        "fireworks": b("fireworks"),
        "spotlight": b("spotlight"),
        "scoutpost": b("scoutpost"),
        "spotDevBrowser": b("spotDevBrowser"),
        "fireworksKey": s("fireworksKey"),
        "firecrawlKey": s("firecrawlKey"),
        "apifyToken": s("apifyToken"),
        "agentmailKey": s("agentmailKey"),
        "scoutpostKey": s("scoutpostKey"),
        "navigatorConnected": b("navigatorConnected"),
        "junkipediaKey": s("junkipediaKey"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-dir", required=True)
    parser.add_argument("--repo-dir", required=True)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--skip-key-validation", action="store_true",
                        help="Skip live provider key checks (tests, offline installs)")
    parser.add_argument("--engine-required", action="store_true",
                        help="Refuse instead of falling back to the retired legacy writer")
    parser.add_argument("--legacy-only", action="store_true",
                        help="Use the compatibility writer for an identified legacy install")
    args = parser.parse_args()

    page_path = os.path.join(args.repo_dir, "install", "configure.html")
    try:
        page = open(page_path, encoding="utf-8").read()
    except OSError:
        print(f"configure.html not found at {page_path}", file=sys.stderr)
        return 1

    token = secrets.token_urlsafe(16)
    page = page.replace("__SETUP_TOKEN__", token)
    page = page.replace("__PLATFORM__", detect_platform())
    done = threading.Event()
    result = {"written": False}
    engine_bridge = None
    engine_descriptor = None
    navigator_bridge = NavigatorInstallerBridge(
        os.path.join(args.repo_dir, "install", "navigator-transport-matrix.json"),
        "goose",
    )
    if not args.legacy_only:
        try:
            engine_bridge = EngineBridge("mycroft")
            engine_descriptor = engine_bridge.descriptor()
        except (EngineUnavailable, RuntimeError, KeyError) as error:
            if args.engine_required:
                print(f"  A compatible, activated Buried Signals Engine is required for a new Mycroft install: {error}. Install Indicator Labs or the signed bsig release, then re-run this installer.", file=sys.stderr)
                return 2

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def _send(self, code, body, ctype="application/json"):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _same_origin(self):
            origin = self.headers.get("Origin")
            if not origin:
                return True
            return origin == "http://" + self.headers.get("Host", "")

        def do_GET(self):
            parsed = urllib.parse.urlsplit(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            if query.get("t", [""])[0] != token:
                self._send(403, "forbidden — open the exact URL printed in the terminal", "text/plain")
                return
            if parsed.path == "/":
                self._send(200, page, "text/html")
            elif parsed.path == "/engine-descriptor" and engine_descriptor is not None:
                self._send(200, json.dumps(engine_descriptor))
            else:
                self._send(404, "not found", "text/plain")

        def do_POST(self):
            parsed_path = urllib.parse.urlsplit(self.path).path
            if parsed_path not in (
                "/submit",
                "/pick-folder",
                "/engine-submit",
                "/navigator/start",
                "/navigator/poll",
                "/navigator/cancel",
                "/navigator/status",
            ):
                self._send(404, "not found", "text/plain")
                return
            try:
                length = int(self.headers.get("Content-Length") or 0)
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except Exception:
                self._send(400, json.dumps({"errors": [{"field": "", "message": "Malformed request."}]}))
                return
            if payload.get("token") != token:
                self._send(403, json.dumps({"errors": [{"field": "", "message": "Bad token — reload the page from the terminal URL."}]}))
                return
            if not self._same_origin():
                self._send(403, json.dumps({"errors": [{"field": "", "message": "Cross-origin setup request rejected."}]}))
                return
            if parsed_path == "/navigator/status":
                self._send(200, json.dumps(navigator_bridge.existing_status()))
                return
            if parsed_path == "/navigator/start":
                try:
                    self._send(200, json.dumps(navigator_bridge.start(str(payload.get("email") or "").strip())))
                except NavigatorBridgeError as error:
                    self._send(503, json.dumps({"status": "offline", "detail": str(error)}))
                return
            if parsed_path == "/navigator/poll":
                try:
                    self._send(200, json.dumps(navigator_bridge.poll(str(payload.get("flow_id") or ""))))
                except NavigatorBridgeError as error:
                    self._send(503, json.dumps({"status": "failed", "detail": str(error)}))
                return
            if parsed_path == "/navigator/cancel":
                try:
                    self._send(200, json.dumps(navigator_bridge.cancel(str(payload.get("flow_id") or ""))))
                except NavigatorBridgeError as error:
                    self._send(503, json.dumps({"status": "failed", "detail": str(error)}))
                return
            if parsed_path == "/pick-folder":
                path, error = pick_folder_natively(PICKER_PROMPTS.get(str(payload.get("field") or ""), "Choose a folder"))
                self._send(200, json.dumps({"path": path, "error": error}))
                return
            if parsed_path == "/engine-submit":
                if engine_bridge is None:
                    self._send(404, json.dumps({"errors": [{"field": "", "message": "Engine configuration is unavailable."}]}))
                    return
                try:
                    response = engine_bridge.submit(payload.get("request") or {}, payload.get("secrets") or {})
                    marker = os.path.join(args.profile_dir, "engine-plan.ready")
                    os.makedirs(args.profile_dir, mode=0o700, exist_ok=True)
                    fd, tmp = tempfile.mkstemp(prefix=".engine-plan.", dir=args.profile_dir)
                    try:
                        with os.fdopen(fd, "w", encoding="utf-8") as handle:
                            json.dump(response["plan"], handle)
                            handle.flush()
                            os.fsync(handle.fileno())
                        os.chmod(tmp, 0o600)
                        os.replace(tmp, marker)
                    except Exception:
                        try: os.unlink(tmp)
                        except FileNotFoundError: pass
                        raise
                except Exception as e:
                    self._send(400, json.dumps({"errors":[{"field":"","message":str(e)}]})); return
                result["written"] = True
                self._send(200, json.dumps(response))
                threading.Timer(0.5, done.set).start(); return
            if engine_bridge is not None and not args.legacy_only:
                self._send(410, json.dumps({"errors": [{"field": "", "message": "Use the Engine-managed form shown in this session."}]}))
                return
            d = normalize(payload)
            navigator_choice = str(payload.get("navigatorChoice") or "")
            if navigator_choice not in {"connect", "skip"}:
                self._send(400, json.dumps({"errors": [{"field": "navigator", "message": "Choose Connect Navigator or Continue without Navigator."}]}))
                return
            if navigator_choice == "connect" and navigator_bridge.existing_status().get("status") != "connected":
                self._send(400, json.dumps({"errors": [{"field": "navigator", "message": "Navigator is not connected. Finish sign-in or choose Continue without Navigator."}]}))
                return
            d["navigatorConnected"] = navigator_choice == "connect"
            errors = validate_choices(d)
            warnings = []
            if not errors:
                key_errors, warnings = validate_keys(d, skip=args.skip_key_validation)
                errors += key_errors
            if errors:
                self._send(400, json.dumps({"errors": errors, "warnings": warnings}))
                return
            try:
                write_artifacts(d, args.profile_dir)
            except Exception as e:
                self._send(500, json.dumps({"errors": [{"field": "", "message": f"Could not write configuration: {e}"}]}))
                return
            result["written"] = True
            self._send(200, json.dumps({"ok": True, "warnings": warnings}))
            threading.Timer(0.5, done.set).start()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/?t={token}"
    print(f"  Configurator: {url}", flush=True)
    print("  Waiting for you to finish in the browser (Ctrl-C to abort)...", flush=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        finished = done.wait(SUBMIT_TIMEOUT_SECONDS)
    except KeyboardInterrupt:
        finished = False
        print("\n  Aborted.")
    server.shutdown()
    if not finished or not result["written"]:
        if not result["written"]:
            print("  No configuration received; nothing was written.", file=sys.stderr)
        return 1
    print("  Configuration saved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
