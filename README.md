# Mycroft

A Goose Extension Pack for investigative journalists. Privacy-preserving, ZDR-first, sovereign-capable.

**Status:** Phase 1 — killer demos + provider configs. See the plan: `~/.claude/plans/if-goose-can-we-modular-feather.md`.

## What it is

- Curated Goose Recipes for journalism workflows (vault Q&A, SIFT fact-check, beat monitoring, interview prep, inbox sweep, story pitch)
- Opinionated provider configs: **Zero Data Retention** providers only by default (Fireworks, Together, OpenRouter; local MLX or llama-server for sovereign mode). No Claude / OpenAI / Gemini defaults — their retention policies aren't suitable for journalism.
- Journalism system prompt with SIFT methodology, strict attribution rules, no-fabrication guardrails
- Obsidian vault scaffolding for durable journalist knowledge, story work, and Spotlight handoffs
- Selected skill registry for Goose-aware workflows: knowledge primitives, Obsidian ingest, Firecrawl, Scoutpost, Spotlight ingest, maintenance, and copywriting placeholder

## Install

### Guided install (hosted setup page)

Visit the setup page (deployed from `index.html` in this repo — URL TBD, e.g. `mycroft.buriedsignals.com`):

1. Fill the form: sovereignty preference, API keys, cloud providers, vault path
2. Click **Download installer ZIP** — your browser saves `mycroft-setup.zip` with a double-clickable `mycroft-setup.command` and `README-FIRST.txt`
3. Extract the ZIP anywhere, then double-click `mycroft-setup.command`. The script configures Goose with the Mycroft profile at `~/.config/goose/mycroft`, keeps updateable source at `~/.local/share/goose/mycroft/source`, and uses the vault paths you selected.
   If macOS says Apple could not verify it, choose **Done**, then use **System Settings → Privacy & Security → Open Anyway**; later runs can be double-clicked.
4. Optional: click **Download agent setup ZIP** to export a local JSON manifest plus a prompt another agent can use to perform and verify the install without asking you to paste secrets into chat.
5. Open a new terminal — shell rc updates take effect

The setup page runs **entirely in your browser** — no form submissions, no server round-trips, no API keys crossing the network. The downloaded `.command` script clones this repo to `~/.local/share/goose/mycroft/source/`, copies provider configs to `~/.config/goose/custom_providers/`, writes fallback script secrets to `~/.config/goose/mycroft/.env`, stores selected provider keys in Goose's secret store when possible, persists `GOOSE_PROVIDER`, `GOOSE_MODEL`, `GOOSE_RECIPE_PATH`, and `GOOSE_MOIM_MESSAGE_FILE` in `~/.config/goose/config.yaml`, installs QMD for local vault search, references skills from the source checkout, generates Goose instructions at `~/.config/goose/mycroft/goose-mycroft.md`, copies them to `~/.config/goose/.goosehints`, and installs a replaceable `# === mycroft ===` block in your shell rc. The agent setup ZIP also contains the API keys in its local manifest so an agent can write `.env`; keep it private like the command installer.

The Mycroft Obsidian vault is a durable journalist knowledge base: `_schema/`, `_index.md`, `_log.md`, `sources/`, `wiki/`, `stories/`, `context/`, and `handoff/from-spotlight/`. If Spotlight is enabled, its separate vault stays casework-oriented: `cases/`, `evidence/`, `captures/`, `briefs/`, `exports/`, and `handoff-to-mycroft/`. Goose is told both paths and the Spotlight ingest target through generated instructions.

QMD is installed as a required local search dependency. Setup registers the Mycroft vault as the `mycroft` QMD collection and, when Spotlight is enabled, registers the Spotlight vault as `spotlight`. Spotlight's `query-vault` path depends on QMD.

The guided installer also installs a weekly updater for the Mycroft repo and bundled plugin repos:

- macOS: user crontab entry, not a Login Item
- Linux with systemd: `~/.config/systemd/user/mycroft-update.timer`
- Other Linux shells: a crontab entry

The updater fetches `origin main` for the Mycroft source checkout and bundled plugin repos, then fast-forwards only. It skips dirty or divergent checkouts rather than stashing or merging local work. Source recipes and skills are loaded directly from the checkout, so updates apply without copying. After each update, the updater refreshes `~/.config/goose/mycroft/SOUL.md`, regenerates `~/.config/goose/.goosehints`, refreshes provider JSON files that are already installed under Goose, and runs `mycroft doctor`. If doctor fails, it rolls app checkouts back to the pre-update commits and leaves the log at `~/.local/share/goose/mycroft/logs/update.log`.

Desktop users can also trigger the same safe updater by asking Goose to run the `update-mycroft` recipe.

Goose itself stays current through Goose/Homebrew, not through the Mycroft repo updater. Mycroft only layers local recipes, provider configs, instructions, skills, and vault scaffolding on top of Goose.

The installer also registers Goose-native schedules for the morning brief and vault audit. On first launch it opens the `start` recipe and writes `START_HERE.md` into the vault. The first-run flow offers concrete actions: set up a beat, add material to the knowledge base, create a morning brief, investigate a lead, set up scouts, or generate a demo workflow.

### Local install (no hosted page)

Clone the repo and open `index.html` directly:

```sh
mkdir -p ~/.local/share/goose/mycroft
git clone https://github.com/buriedsignals/mycroft.git ~/.local/share/goose/mycroft/source
open ~/.local/share/goose/mycroft/source/index.html
```

Same setup form, just loaded from `file://`. Follow steps 1-4 above. The installer still puts the durable install under Goose's config/data paths.

### Manual install (advanced)

If you'd rather not run the guided installer:

```sh
# 1. Clone
mkdir -p ~/.local/share/goose/mycroft
git clone https://github.com/buriedsignals/mycroft.git ~/.local/share/goose/mycroft/source

# 2. Point Goose at the recipes
export GOOSE_RECIPE_PATH=~/.local/share/goose/mycroft/source/recipes:~/.config/goose/mycroft/generated-recipes

# 3. Copy whichever cloud provider configs you want to use (macOS/Linux Goose config path)
mkdir -p ~/.config/goose/custom_providers
cp ~/.local/share/goose/mycroft/source/providers/fireworks-qwen36plus.json   ~/.config/goose/custom_providers/
cp ~/.local/share/goose/mycroft/source/providers/together-qwen.json          ~/.config/goose/custom_providers/
# For local-only, use Goose Desktop's built-in Local Inference (llama.cpp embedded).
# Settings -> Local Inference -> pick a Mycroft journalist GGUF from HuggingFace.
# NOTE: providers/openrouter-fallback.json is in the repo but not a shipped default —
# OpenRouter's GLM-5.1 routing can hit Z.AI-direct (China-hosted). If you want it,
# copy it manually and configure provider preferences to exclude Z.AI-direct.

# 4. Set env vars
export FIREWORKS_API_KEY=...
export TOGETHER_API_KEY=...
export OPENROUTER_API_KEY=...

# 5. Install global journalism instructions and persistent identity
mkdir -p ~/.config/goose/mycroft
cp ~/.local/share/goose/mycroft/source/instructions/mycroft-soul.md ~/.config/goose/mycroft/SOUL.md
cp ~/.local/share/goose/mycroft/source/instructions/journalism.md ~/.config/goose/.goosehints
```

Goose path notes checked against the Goose docs: macOS/Linux use `~/.config/goose/config.yaml`, `~/.config/goose/custom_providers/`, and global `~/.config/goose/.goosehints`. Provider/model defaults belong in `config.yaml`; provider secrets belong in the Goose keychain or file-backed secret store; recipe discovery uses `GOOSE_RECIPE_PATH`.

## Run the Phase 1 demos

### Vault Q&A (killer demo 1)

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/vault-qa.yaml \
  --params question="What do I already have on the Acme Corp investigation?" \
  --params vault_path=~/Documents/my-vault
```

Answers from your vault + live web (via `firecrawl` CLI). Every claim cited.

### SIFT fact-check (killer demo 2)

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/fact-check.yaml \
  --params draft_path=./article.md
```

Per-claim verdicts: verified / unverified / contradicted / mischaracterized.

## Sovereign mode

All shipped cloud providers are ZDR. For full local (zero network egress), use Goose Desktop's built-in **Local Inference** (`GOOSE_PROVIDER=local`, llama.cpp embedded — no separate server). The guided installer downloads the Mycroft journalist GGUF you picked into `~/models/` and registers it with Goose. Manual route: Goose Desktop -> Settings -> Local Inference -> add a model by HuggingFace repo id (e.g. `tomvaillant/qwen3.5-9b-abliterated-journalist-GGUF:Q4_K_M`).

## Shipping recipes

**Core journalism:**
- `vault-qa` — vault + web Q&A with citations
- `fact-check` — SIFT, per-claim verdicts
- `qmd` — local markdown search over Mycroft and Spotlight vaults
- `source-verify` — SIFT against a single source's credibility
- `start` — first-run menu for setting up a beat, adding material, creating a morning brief, investigating a lead, setting up scouts, or generating a demo
- `morning-brief` — daily digest from ft (X bookmarks) + AgentMail + vault recent changes
- `morning-brief-preflight` — first-run monitoring profile setup for the morning brief
- `update-mycroft` — desktop-triggered safe update using the installed Mycroft updater
- `vault-audit` — scheduled audit for weak claims, missing frontmatter, orphaned sources, and Spotlight handoffs
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

## What belongs where

- **Mycroft** is durable knowledge and publishing support: source records, wiki notes, claims, methods, story pitches, drafts, published packages, and copywriting guidance.
- **Spotlight** is active OSINT casework: cases, evidence, captures, briefs, exports, and handoffs into Mycroft.
- **Scoutpost** is hosted beat monitoring and scout requests. When enabled, Mycroft stores the API configuration locally and Goose instructions prefer MCP if available, then the `scout` CLI, then the hosted API.
- **AgentMail MCP** is not bundled yet. Current recipes use the AgentMail REST API via curl where needed.

## Plugins

- **Spotlight** installs under `~/.local/share/goose/mycroft/plugins/spotlight`, inherits Mycroft's cloud/local provider preference, and keeps its investigation vault separate from the Mycroft vault by default.
- **Scoutpost** is hosted API only in the Mycroft setup flow. Mycroft stores `SCOUTPOST_API_KEY` and exposes it to Spotlight so investigations can request durable scouts and later read information units.
- MCP Apps for investigation dashboard + fact-check scorecard (visual UI in Goose Desktop)
- Pilot with 3-5 grant-target journalists

## Documentation

- [Architecture](docs/architecture.md) — how Mycroft plugs into Goose
- [Grounding and provenance](docs/grounding-provenance-spec.md) — evidence bundles, claim grounding, and C2PA package signing
- [Schedules](docs/schedules.md) — Goose schedules, morning brief, vault audit, and repo updater
- [First run](docs/first-run.md) — getting started in Goose and adding first material
- [Plugin authoring](docs/plugin-authoring.md) — how to add a new plugin
- [Troubleshooting](docs/troubleshooting.md) — common failures + fixes
- [Security policy](SECURITY.md) — disclosure process
- [Contributing](CONTRIBUTING.md) — how to submit changes
- [Changelog](CHANGELOG.md) — version history

## What To Do Next

Start chatting with Mycroft in Goose or open `START_HERE.md` in the Mycroft vault. Pick one first action: set up your beat, add links/files/notes to the knowledge base, create a morning brief, investigate a lead, set up scouts, or ask for a demo workflow.

Then create a folder for your investigations in the Spotlight vault and ask Mycroft to Spotlight it. Use Spotlight for active OSINT casework and evidence; promote durable findings back into Mycroft when they become useful story or knowledge material.

## License

[MIT](LICENSE) — © 2026 Buried Signals.
