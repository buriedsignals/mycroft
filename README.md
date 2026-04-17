# Mycroft

A Goose Extension Pack for investigative journalists. Privacy-preserving, ZDR-first, sovereign-capable.

**Status:** Phase 1 — killer demos + provider configs. See the plan: `~/.claude/plans/if-goose-can-we-modular-feather.md`.

## What it is

- Curated Goose Recipes for journalism workflows (vault Q&A, SIFT fact-check, beat monitoring, interview prep, inbox sweep, story pitch)
- Opinionated provider configs: **Zero Data Retention** providers only by default (Fireworks, Together, OpenRouter; local MLX or llama-server for sovereign mode). No Claude / OpenAI / Gemini defaults — their retention policies aren't suitable for journalism.
- Journalism system prompt with SIFT methodology, strict attribution rules, no-fabrication guardrails
- Vault template (coming Phase 2) and memory scaffolding

## Install

### Guided install (hosted setup page)

Visit the setup page (deployed from `index.html` in this repo — URL TBD, e.g. `mycroft.buriedsignals.com`):

1. Fill the form: sovereignty preference, API keys, cloud providers, vault path
2. Click **Download mycroft-setup.command** — your browser saves a bash script with your selections baked in
3. Run it:
   ```sh
   chmod +x ~/Downloads/mycroft-setup.command
   ~/Downloads/mycroft-setup.command
   ```
4. Open a new terminal — shell rc updates take effect

The setup page runs **entirely in your browser** — no form submissions, no server round-trips, no API keys crossing the network. The downloaded `.command` script clones this repo to `~/.mycroft/`, copies provider configs to `~/.config/goose/custom_providers/`, copies the journalism Instructions to `~/.config/goose/.goosehints`, and appends a `# === mycroft ===` block to your shell rc.

### Local install (no hosted page)

Clone the repo and open `index.html` directly:

```sh
git clone https://github.com/buriedsignals/mycroft.git ~/.mycroft
open ~/.mycroft/index.html
```

Same setup form, just loaded from `file://`. Follow steps 1-4 above.

### Manual install (advanced)

If you'd rather not run the guided installer:

```sh
# 1. Clone
git clone https://github.com/buriedsignals/mycroft.git ~/.mycroft

# 2. Point Goose at the recipes
export GOOSE_RECIPE_PATH=~/.mycroft/recipes  # add to ~/.zshrc or ~/.bashrc

# 3. Copy whichever provider configs you want to use (all ZDR, US-hosted unless noted)
mkdir -p ~/.config/goose/custom_providers
cp ~/.mycroft/providers/fireworks-qwen36plus.json   ~/.config/goose/custom_providers/  # primary — Qwen 3.6 Plus (US, ZDR)
cp ~/.mycroft/providers/together-qwen.json          ~/.config/goose/custom_providers/  # alternative — Qwen 2.5-72B Turbo (US, ZDR opt-in)
cp ~/.mycroft/providers/local-mlx.json              ~/.config/goose/custom_providers/  # sovereign — Apple Silicon
cp ~/.mycroft/providers/local-llama-server.json     ~/.config/goose/custom_providers/  # sovereign — cross-platform
# NOTE: providers/openrouter-fallback.json is in the repo but not a shipped default —
# OpenRouter's GLM-5.1 routing can hit Z.AI-direct (China-hosted). If you want it,
# copy it manually and configure provider preferences to exclude Z.AI-direct.

# 4. Set env vars
export FIREWORKS_API_KEY=...
export TOGETHER_API_KEY=...
export OPENROUTER_API_KEY=...

# 5. Install journalism Instructions
cp ~/.mycroft/instructions/journalism.md ~/.config/goose/.goosehints
```

## Run the Phase 1 demos

### Vault Q&A (killer demo 1)

```sh
goose run --recipe ~/.mycroft/recipes/vault-qa.yaml \
  --params question="What do I already have on the Acme Corp investigation?" \
  --params vault_path=~/Documents/my-vault
```

Answers from your vault + live web (via `firecrawl` CLI). Every claim cited.

### SIFT fact-check (killer demo 2)

```sh
goose run --recipe ~/.mycroft/recipes/fact-check.yaml \
  --params draft_path=./article.md
```

Per-claim verdicts: verified / unverified / contradicted / mischaracterized.

## Sovereign mode

All shipped providers are ZDR. For full local (zero network egress), start `mlx_lm.server` or `llama-server` with a Mycroft Qwen fine-tune (release TBD — fine-tune in training as of 2026-04-17) and use the `local-mlx` or `local-llama-server` provider.

## Shipping recipes

**Core journalism:**
- `vault-qa` — vault + web Q&A with citations
- `fact-check` — SIFT, per-claim verdicts
- `source-verify` — SIFT against a single source's credibility
- `morning-brief` — daily digest from ft (X bookmarks) + AgentMail + vault recent changes
- `newsletter-summarize` — extract signal from a newsletter (URL, AgentMail message, pasted)
- `vault-sync` — write findings into Obsidian vault with proper frontmatter + wiki-links

**Firecrawl wrappers:**
- `firecrawl-scrape` / `firecrawl-change-track` / `firecrawl-pdf` / `firecrawl-batch` / `firecrawl-map`

**Apify social scrapers** (need `APIFY_API_TOKEN`):
- `apify-social/select-actor` — natural-language router
- `apify-social/{instagram, x, facebook, tiktok, instagram-comments, linkedin}`

**Document + interactive:**
- `dev-browser` — interactive source acquisition with chain-of-custody
- `liteparse` — fast structured extraction from PDF/HTML/docx

**Optional config:**
- `voice-setup` — TTS/STT (edge + local whisper defaults)

## What's not in Mycroft (by design)

- **Beat monitoring** — belongs in coJournalist (async scout pipeline; a laptop that closes at night can't monitor a beat). Separate product. Integration later when its MCP ships.
- **Interview prep / story pitch** — out of scope. Not in this pack.
- **AgentMail MCP** — current morning-brief uses the AgentMail REST API via curl. A proper MCP extension is on the later roadmap.

## Roadmap

- Spotlight + coJournalist MCP integrations (when their harness-agnostic versions ship, separate tracks)
- MCP Apps for investigation dashboard + fact-check scorecard (visual UI in Goose Desktop)
- Pilot with 3-5 grant-target journalists

## Documentation

- [Architecture](docs/architecture.md) — how Mycroft plugs into Goose
- [Plugin authoring](docs/plugin-authoring.md) — how to add a new plugin
- [Troubleshooting](docs/troubleshooting.md) — common failures + fixes
- [Security policy](SECURITY.md) — disclosure process
- [Contributing](CONTRIBUTING.md) — how to submit changes
- [Changelog](CHANGELOG.md) — version history

## License

[MIT](LICENSE) — © 2026 Buried Signals.
