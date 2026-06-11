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
import threading
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SUBMIT_TIMEOUT_SECONDS = 30 * 60


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
    "qwen9b": {
        "name": "qwen3.5-9b-abliterated-journalist",
        "repo": "tomvaillant/qwen3.5-9b-abliterated-journalist-GGUF",
        "filename": "model-q4_k_m.gguf",
        "quantization": "Q4_K_M",
        "vision": False,
        "enable_thinking": True,
        "label": "Qwen 3.5 9B Journalist · runs on your machine, $0/mo",
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
    if not d.get("firecrawlKey"):
        errors.append({"field": "firecrawl_key", "message": "FIRECRAWL_API_KEY is required — every web-capable recipe depends on it. Get a key at firecrawl.dev."})
    if not d.get("localOnly"):
        if not d.get("fireworks") and not d.get("together"):
            errors.append({"field": "fireworks_key", "message": "Cloud-first needs at least one provider — enable Fireworks or Together, or switch to Local-first."})
        if d.get("fireworks") and not d.get("fireworksKey"):
            errors.append({"field": "fireworks_key", "message": "FIREWORKS_API_KEY is required while Fireworks is your provider."})
        if d.get("together") and not d.get("togetherKey"):
            errors.append({"field": "together_key", "message": "TOGETHER_API_KEY is required while Together is your provider."})
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
    if not d.get("localOnly") and d.get("fireworks") and d.get("fireworksKey"):
        checks.append(("fireworks_key", "FIREWORKS_API_KEY", True,
                       "https://api.fireworks.ai/inference/v1/models",
                       {"Authorization": "Bearer " + d["fireworksKey"]}))
    if not d.get("localOnly") and d.get("together") and d.get("togetherKey"):
        checks.append(("together_key", "TOGETHER_API_KEY", True,
                       "https://api.together.xyz/v1/models",
                       {"Authorization": "Bearer " + d["togetherKey"]}))
    if d.get("scoutpost") and d.get("scoutpostKey"):
        checks.append(("scoutpost_api_key", "SCOUTPOST_API_KEY", False,
                       "https://www.scoutpost.ai/api/v1/scouts",
                       {"Authorization": "Bearer " + d["scoutpostKey"]}))
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
        model = LOCAL_MODELS.get(d.get("localModel") or "qwen9b", LOCAL_MODELS["qwen9b"])
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
    elif d.get("fireworks"):
        lines += ["GOOSE_PROVIDER=fireworks-qwen36plus",
                  "GOOSE_MODEL=accounts/fireworks/models/qwen3p6-plus"]
    elif d.get("together"):
        lines += ["GOOSE_PROVIDER=together-qwen",
                  "GOOSE_MODEL=Qwen/Qwen2.5-72B-Instruct-Turbo"]
    for key, name in [("fireworksKey", "FIREWORKS_API_KEY"), ("togetherKey", "TOGETHER_API_KEY"),
                      ("firecrawlKey", "FIRECRAWL_API_KEY"), ("apifyToken", "APIFY_API_TOKEN"),
                      ("agentmailKey", "AGENTMAIL_API_KEY")]:
        if d.get(key):
            lines.append(f"{name}={shlex.quote(d[key])}")
    if d.get("scoutpost") and d.get("scoutpostKey"):
        lines.append("SCOUTPOST_API_KEY=" + shlex.quote(d["scoutpostKey"]))
        lines.append("SCOUTPOST_API_BASE=https://www.scoutpost.ai/api/v1")
    if d.get("spotlight"):
        lines.append('SPOTLIGHT_DIR="$MYCROFT_PLUGINS_DIR/spotlight"')
        lines.append(f'SPOTLIGHT_VAULT_PATH="{spotlight_vault}"')
        lines.append(f'SPOTLIGHT_INGEST_TARGET="{vault}"')
        lines.append("SPOTLIGHT_SOVEREIGNTY_INHERITS_MYCROFT=1")
        if d.get("scoutpost"):
            lines.append("SPOTLIGHT_MONITORING_BACKEND=scoutpost")
            lines.append("SPOTLIGHT_SCOUT_REQUESTS=scoutpost")
        if d.get("osintNavigatorKey"):
            lines.append("OSINT_NAV_API_KEY=" + shlex.quote(d["osintNavigatorKey"]))
        if d.get("junkipediaKey"):
            lines.append("JUNKIPEDIA_API_KEY=" + shlex.quote(d["junkipediaKey"]))
    return "\n".join(lines) + "\n"


def build_setup_config(d):
    required = []
    if d.get("firecrawlKey"):
        required.append("FIRECRAWL_API_KEY")
    if not d["localOnly"] and d.get("fireworks"):
        required.append("FIREWORKS_API_KEY")
    if not d["localOnly"] and d.get("together"):
        required.append("TOGETHER_API_KEY")
    if d.get("scoutpost"):
        required.append("SCOUTPOST_API_KEY")
    if d.get("spotlight") and d.get("osintNavigatorKey"):
        required.append("OSINT_NAV_API_KEY")
    lines = [
        "# Mycroft setup choices — generated by the local configurator (no secrets)",
        f"SOVEREIGNTY={shlex.quote(d['sovereignty'])}",
        f"LOCAL_ONLY={b01(d['localOnly'])}",
        f"LOCAL_MODEL={shlex.quote(d.get('localModel') or 'qwen9b')}",
        f'VAULT_PATH="{expand_home_for_shell(d["vault"])}"',
        f'SPOTLIGHT_VAULT_INPUT="{expand_home_for_shell(d.get("spotlightVaultPath") or "~/Documents/Spotlight")}"',
        f"INSTALL_GOOSE={b01(d.get('installGoose'))}",
        f"INSTALL_OBSIDIAN={b01(d.get('installObsidian'))}",
        f"INSTALL_FIRECRAWL={b01(d.get('installFirecrawl'))}",
        f"ENABLE_SPOTLIGHT={b01(d.get('spotlight'))}",
        f"ENABLE_SCOUTPOST={b01(d.get('scoutpost'))}",
        f"ENABLE_FIREWORKS={b01(not d['localOnly'] and d.get('fireworks'))}",
        f"ENABLE_TOGETHER={b01(not d['localOnly'] and d.get('together'))}",
        f"ENABLE_FT={b01(d.get('ftEnabled'))}",
        f"ENABLE_AGENTMAIL={b01(d.get('agentmailEnabled') or d.get('agentmailKey'))}",
        f"ENABLE_APIFY={b01(d.get('apifyEnabled') or d.get('apifyToken'))}",
        f"SPOT_DEVBROWSER={b01(d.get('spotDevBrowser'))}",
        f"HAS_OSINT_NAVIGATOR={b01(d.get('osintNavigatorKey'))}",
        f"HAS_JUNKIPEDIA={b01(d.get('junkipediaKey'))}",
        f'REQUIRED_DOCTOR_ENV="{" ".join(required)}"',
    ]
    return "\n".join(lines) + "\n"


def build_skill_registry(d):
    skills = [
        {"id": "knowledge-primitives", "path": "~/.local/share/goose/mycroft/source/skills/knowledge-primitives/SKILL.md", "source": "mycroft", "enabled": True},
        {"id": "qmd", "path": "~/.local/share/goose/mycroft/source/skills/qmd/SKILL.md", "source": "mycroft", "enabled": True},
        {"id": "obsidian", "path": "~/.local/share/goose/mycroft/source/skills/obsidian/SKILL.md", "source": "mycroft", "enabled": bool(d.get("installObsidian"))},
        {"id": "obsidian-ingest", "path": "~/.local/share/goose/mycroft/source/skills/obsidian-ingest/SKILL.md", "source": "mycroft", "enabled": bool(d.get("installObsidian"))},
        {"id": "fact-check", "path": "~/.local/share/goose/mycroft/source/skills/fact-check/SKILL.md", "source": "mycroft", "enabled": True},
        {"id": "copywriting", "path": "~/.local/share/goose/mycroft/source/skills/copywriting/SKILL.md", "source": "mycroft", "enabled": True, "status": "placeholder"},
        {"id": "mycroft-maintenance", "path": "~/.local/share/goose/mycroft/source/skills/mycroft-maintenance/SKILL.md", "source": "mycroft", "enabled": True},
    ]
    if d.get("installFirecrawl") or d.get("firecrawlKey"):
        skills.append({"id": "firecrawl", "path": "~/.local/share/goose/mycroft/source/skills/firecrawl/SKILL.md", "source": "mycroft", "enabled": True})
    if d.get("scoutpost"):
        skills.append({"id": "scoutpost", "path": "~/.config/goose/mycroft/skills/scoutpost/SKILL.md", "source": "mycroft-profile", "enabled": True, "product_skill_url": "https://scoutpost.ai/skills/scoutpost.md"})
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
        model = LOCAL_MODELS.get(d.get("localModel") or "qwen9b", LOCAL_MODELS["qwen9b"])
        provider_label = model["label"]
    elif d.get("fireworks"):
        provider_label = "Fireworks AI · Qwen 3.6 Plus (ZDR cloud)"
    elif d.get("together"):
        provider_label = "Together AI · Qwen 2.5-72B Turbo (ZDR cloud)"
    else:
        provider_label = "No provider configured"

    optional = []
    if d.get("ftEnabled"):
        optional.append("ft CLI (X bookmarks)")
    if d.get("agentmailEnabled") or d.get("agentmailKey"):
        optional.append("AgentMail (newsletters + tips inbox)")
    if d.get("apifyEnabled") or d.get("apifyToken"):
        optional.append("Apify (social scraping)")

    plugins = []
    if d.get("spotlight"):
        plugins.append("Spotlight (OSINT investigations)")
    if d.get("scoutpost"):
        plugins.append("Scoutpost (hosted monitoring)")

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
        "localModel": s("localModel") or "qwen9b",
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
        "together": b("together"),
        "spotlight": b("spotlight"),
        "scoutpost": b("scoutpost"),
        "spotDevBrowser": b("spotDevBrowser"),
        "fireworksKey": s("fireworksKey"),
        "togetherKey": s("togetherKey"),
        "firecrawlKey": s("firecrawlKey"),
        "apifyToken": s("apifyToken"),
        "agentmailKey": s("agentmailKey"),
        "scoutpostKey": s("scoutpostKey"),
        "osintNavigatorKey": s("osintNavigatorKey"),
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

        def do_GET(self):
            if self.path == "/" or self.path.startswith("/?"):
                self._send(200, page, "text/html")
            else:
                self._send(404, "not found", "text/plain")

        def do_POST(self):
            if self.path not in ("/submit", "/pick-folder"):
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
            if self.path == "/pick-folder":
                path, error = pick_folder_natively(str(payload.get("prompt") or "Choose a folder"))
                self._send(200, json.dumps({"path": path, "error": error}))
                return
            d = normalize(payload)
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
    print(f"  Configurator: {url}")
    print("  Waiting for you to finish in the browser (Ctrl-C to abort)...")
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
