# Architecture

Mycroft is an **extension pack for [Goose](https://goose-docs.ai/)** — the open-source AI agent runtime. Not a fork. Not a replacement. A curated overlay.

## Layers

```
┌───────────────────────────────────────────────────────────────┐
│  User's laptop                                                │
│                                                               │
│   Goose (brew-installed, stock upstream)                      │
│   ├─ ~/.config/goose/custom_providers/                        │
│   │   ← mycroft copies provider JSONs here                    │
│   ├─ ~/.config/goose/.goosehints                              │
│   │   ← mycroft copies instructions/journalism.md here        │
│   └─ recipes loaded via GOOSE_RECIPE_PATH                     │
│       ← points to ~/.mycroft/recipes/                         │
│                                                               │
│   ~/.mycroft/ (this repo, git-cloned by the setup script)     │
│   ├─ recipes/               Goose Recipe YAML files           │
│   ├─ providers/             Goose custom provider JSONs       │
│   ├─ instructions/          Journalism system prompt          │
│   ├─ extensions/manifest.json  Declared MCP deps              │
│   ├─ memory/                Memory templates                  │
│   └─ plugins/               Sub-packs (cloned as needed)      │
│       ├─ spotlight/         buriedsignals/spotlight           │
│       ├─ cojournalist/      buriedsignals/cojournalist        │
│       └─ ...                                                  │
└───────────────────────────────────────────────────────────────┘
```

## Component responsibilities

### Goose (upstream — not us)

- Agent runtime (Rust)
- Provider abstraction — `custom_providers/*.json` describes OpenAI-compatible endpoints
- Recipe loading from `GOOSE_RECIPE_PATH`
- Extension (MCP) discovery
- Session management, tool calling, prompt flow

### Mycroft pack

- **Recipes** (`recipes/`) — opinionated workflows for investigative journalism
- **Providers** (`providers/`) — curated set (ZDR-first: Fireworks, Together, local MLX, local llama-server, optional OpenRouter)
- **Instructions** (`instructions/journalism.md`) — SIFT, attribution, source-protection posture injected on every session
- **Extensions manifest** (`extensions/manifest.json`) — declares which MCP servers recipes expect
- **Memory templates** (`memory/`) — USER.md + MEMORY.md scaffolds
- **Setup UI** (`index.html`, `setup.html`) — hosted static page; generates a bash install script client-side

### Plugins (sub-packs)

Each plugin is a separate GitHub repo that follows the Mycroft plugin contract (see `docs/plugin-authoring.md`). The installer clones them into `~/.mycroft/plugins/{name}/` and wires their recipes + skills into Goose via the same mechanisms Mycroft uses.

Current plugins:
- **Spotlight** — OSINT investigations
- **coJournalist** — beat monitoring (web or self-host)
- **DataHound** — open-data APIs (May 2026)
- **Atelier** — visual production (May 2026)

## Data flow

### Cloud mode (default)

1. User invokes a recipe (`goose run --recipe morning-brief.yaml ...`).
2. Goose loads the recipe + `.goosehints` + provider config.
3. LLM calls route to the selected cloud provider (Fireworks / Together). ZDR is enforced by the provider; we can verify their claims, we can't technically enforce from our side.
4. Tool calls (Firecrawl, Apify, AgentMail) hit those services directly — no Mycroft middleman.
5. Results write to the user's Obsidian vault via the `obsidian` CLI (requires app to be running).

### Local-first (sovereign) mode

1. `MYCROFT_LOCAL_ONLY=1` is set in shell rc (by the setup script, when user picks Local-first).
2. User starts `mlx_lm.server` or `llama-server` locally.
3. Recipes' `instructions:` honour the flag — LLM inference routes to `local-mlx` or `local-llama-server`.
4. Tool calls (Firecrawl, Apify) still hit cloud APIs; sovereignty is about LLM inference, not data ingestion. This distinction is documented in the setup flow.

## Setup script architecture

`setup.html` contains a client-side JavaScript `buildScript()` function that generates a bash `.command` file with the user's selections baked in. The user's API keys are embedded in the downloaded script, never sent to a server. The setup page has no backend.

The generated script:

1. Platform guard (macOS-first, warns on Linux)
2. Brew-installs Goose + Obsidian if requested (auto-opens them after)
3. npm-installs Firecrawl CLI if requested
4. Clones Mycroft to `~/.mycroft/` (or `git pull` if exists)
5. Copies provider JSONs to `~/.config/goose/custom_providers/`
6. Copies `instructions/journalism.md` to `~/.config/goose/.goosehints`
7. Clones selected plugins into `~/.mycroft/plugins/`
8. Appends a `# === mycroft ===` block to the user's shell rc — idempotent (replaces prior block if found)
9. Prints next steps

## Why this shape

- **Standards-based, no fork** — upgrading Goose doesn't break Mycroft; uninstalling Mycroft doesn't break Goose.
- **Sub-packs, not monolith** — plugins ship independent release cadences (Spotlight iterates faster than Mycroft; DataHound ships in May).
- **Client-side setup** — journalism audience can't trust a backend that receives API keys.
- **Opinionated defaults** — the curation (ZDR-first, Qwen-first, firecrawl-only for web) is the product. Extracted to `instructions/journalism.md`, `providers/`, and `extensions/manifest.json` so each opinion is single-sourced.
