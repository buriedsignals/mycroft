# Plugin authoring

Plugins extend Mycroft with domain-specific recipes, skills, and MCP integrations. Each plugin is a separate repo that Mycroft's setup clones into `~/.mycroft/plugins/{name}/`.

## Contract

A Mycroft plugin is a git repo with this minimum structure:

```
plugin-name/
├── AGENTS.md              (optional — cross-runtime agent instructions)
├── README.md              (required — what it does, how it plugs in)
├── recipes/               (optional — Goose Recipe YAMLs)
├── skills/                (optional — skill markdown files)
├── extensions/
│   └── manifest.json      (optional — MCP servers this plugin needs)
├── providers/             (optional — custom provider JSONs specific to plugin)
├── docs/                  (optional)
└── plugin.json            (required — Mycroft plugin manifest)
```

## `plugin.json` (the contract)

```json
{
  "name": "spotlight",
  "version": "0.1.0",
  "description": "OSINT investigation system for journalists",
  "repo": "https://github.com/buriedsignals/spotlight",
  "mycroft_min_version": "0.1.0",
  "setup_vars": [
    {
      "name": "SPOTLIGHT_VAULT_PATH",
      "default": "~/Documents/intelligence",
      "description": "Dedicated investigations vault (separate from main vault)"
    }
  ],
  "optional_keys": [
    {"env": "OSINT_NAVIGATOR_API_KEY", "provider": "OSINT Navigator"},
    {"env": "ACLED_API_KEY",           "provider": "ACLED"},
    {"env": "JUNKIPEDIA_API_KEY",      "provider": "Junkipedia"}
  ],
  "extensions": ["firecrawl", "apify"],
  "recipes_register": true,
  "skills_register": true
}
```

Mycroft's setup reads this file on install to:
- Collect relevant env vars into the user's shell rc
- Add recipes + skills to Goose's discovery paths
- Verify MCP extensions are present

## Install flow

When the user selects a plugin in `setup.html` (or the setup script detects one from a manifest), the generated bash does:

```bash
if [ ! -d "$MYCROFT_DIR/plugins/{name}/.git" ]; then
  git clone {repo} "$MYCROFT_DIR/plugins/{name}"
fi
```

Plus conditional `mkdir` for any `setup_vars` that specify a path default.

## Recipe discovery

Plugin recipes are picked up via `GOOSE_RECIPE_PATH` — Mycroft's install script appends plugin recipe dirs:

```sh
export GOOSE_RECIPE_PATH="$MYCROFT_DIR/recipes:$MYCROFT_DIR/plugins/spotlight/recipes"
```

## Sovereignty posture

All plugins must honour `MYCROFT_LOCAL_ONLY`:

- **In local-only mode:** the plugin's LLM-invoking recipes MUST route to `local-mlx` or `local-llama-server`.
- **Cloud data APIs** (Firecrawl, Apify, AgentMail, etc.) remain cloud-bound even in local-only mode — sovereign mode is about LLM inference, not data ingestion. Plugins should flag any recipe step where source-sensitive data would transit a third-party service.

## Shipping checklist

- [ ] `plugin.json` at repo root
- [ ] `README.md` with "What it does" / "How it plugs into Mycroft" / "Standalone install (without Mycroft)"
- [ ] Recipes validated via `python3 tools/validate-recipes.py` from the Mycroft checkout
- [ ] At least one recipe that exercises the plugin's core capability
- [ ] Optional: `setup.html` of your own for standalone (non-Mycroft) users — follow the Spotlight repo pattern
- [ ] MIT / Apache-2.0 license compatible with Mycroft's MIT

## Reference

- [Spotlight](https://github.com/buriedsignals/spotlight) — canonical example
- [coJournalist](https://github.com/buriedsignals/cojournalist) — web-hosted backend + local-install pattern
