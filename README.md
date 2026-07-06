# Mycroft

Mycroft is a Goose extension pack for newsroom memory, recurring editorial
workflows, source-grounded fact-checking, and handoffs between monitoring,
investigation, and publishing.

It gives an investigative journalist a durable local knowledge base, a set of
Goose recipes for common reporting work, and a privacy-conscious provider setup
that can run with ZDR cloud models or local inference.

## What Mycroft Does

- Maintains an Obsidian-compatible journalism vault for sources, notes, methods,
  story material, and handoffs.
- Ingests links, PDFs, newsletters, pasted notes, documents, and folders into
  structured local knowledge.
- Answers questions over the vault with citations.
- Runs SIFT-style source checks and draft fact-checks.
- Produces morning briefs and recurring vault audits.
- Helps set up beats, watchlists, source-monitoring profiles, and story
  triggers.
- Connects Scoutpost monitoring to Spotlight investigations and durable vault
  memory.
- Keeps provider and vault configuration local to the user's machine.

## Core Workflows

| Workflow | What it does | Main recipe |
|---|---|---|
| Start | First-run menu for beats, knowledge ingest, morning brief, scouts, lead investigation, or demo flow. | `start` |
| Vault Q&A | Answers questions over local newsroom memory and live sources with citations. | `vault-qa` |
| Knowledge ingest | Turns links, notes, files, PDFs, folders, and newsletters into structured vault material. | `vault-sync`, `obsidian-ingest`, `newsletter-summarize` |
| Fact-check | Checks article drafts or claims with SIFT-style verdicts and optional provenance packaging. | `fact-check` |
| Source verification | Evaluates a single source's credibility and evidence value. | `source-verify` |
| Morning brief | Builds a recurring digest from configured beats, watchlists, AgentMail, bookmarks, and recent vault changes. | `morning-brief` |
| Vault audit | Finds weak claims, missing frontmatter, orphaned sources, and stale handoffs. | `vault-audit` |
| Browser acquisition | Opens a journalist-controlled browser session for portals, forms, downloads, and authenticated source capture. | `dev-browser` |
| Scoutpost | Sets up or queries hosted monitoring scouts and information units. | `scoutpost` skill |
| Spotlight handoff | Moves active case findings into durable newsroom memory. | Spotlight plugin + ingest |

## Mycroft, Spotlight, Scoutpost

- **Mycroft** is durable knowledge and publishing support: source records, wiki
  notes, claim checks, methods, story pitches, drafts, briefings, and published
  packages.
- **Spotlight** is active OSINT casework: briefs, methodology, research cycles,
  evidence, fact-checking, review, exports, and handoffs.
- **Scoutpost** is hosted monitoring: page scouts, beat scouts, social/civic
  scouts, information units, and follow-up alerts.

The normal loop is: Scoutpost surfaces leads, Spotlight investigates them,
Mycroft preserves the durable knowledge and supports publication.

## First Run

When the installer finishes it opens a personalized getting-started guide in
the browser — example prompts and first workflows, written to
`~/.config/goose/mycroft/getting-started.html`. Mycroft also
opens Goose and writes `START_HERE.md` into the vault. The first-run menu
offers:

- Set up my beat.
- Add material to my knowledge base.
- Create my morning brief.
- Investigate a lead.
- Set up scouts.
- Show me a demo workflow.

If the vault is empty and the journalist already has material, start with
knowledge ingest. If the journalist already knows the beat, start with the
morning brief preflight. If the lead needs active OSINT work, hand it to
Spotlight.

See [docs/first-run.md](docs/first-run.md).

## Vaults

Mycroft and Spotlight use separate vaults because they serve different editorial
states.

The Mycroft vault is durable newsroom memory:

```text
_schema/
sources/raw/
sources/processed/
wiki/
stories/
context/
handoff/from-spotlight/
```

The Spotlight vault is active casework:

```text
cases/
evidence/
captures/
briefs/
exports/
_schema/
```

QMD indexes both vaults when Spotlight is enabled, so agents can search prior
work without flattening casework into published knowledge.

## Install

### Guided Install

```bash
curl -fsSL https://mycroft.buriedsignals.com/install.sh | bash
```

One static, reviewable script ([`install.sh`](install.sh)) for every install.
It surfaces exactly the skills listed in [`skills.manifest`](skills.manifest) — the
engine-resolved set for the Goose runtime (`bsig skills resolve`; the engine catalog is the
source of truth) — into `~/.agents/skills/mycroft/`. Regenerate the manifest when the catalog
changes. The script also fetches this repo, then opens a local configurator page in the browser —
served from `127.0.0.1` by `install/setup_server.py`. Sovereignty preference,
provider keys, plugins, and vault paths (with a native folder picker) are all
collected there; keys are verified live with each provider and written straight
to `~/.config/goose/mycroft/.env` with owner-only permissions. **No API key
ever appears on a website or inside a downloadable artifact.**

Prefer a file? The hosted setup page offers a ZIP whose `install.command`
fetches and runs the same canonical script. When the install finishes, open a
new terminal so shell configuration changes take effect.

The installer configures Goose, provider files, recipe discovery, vault paths,
QMD indexing, Mycroft instructions, updater recipes, scheduled workflows, and
the first-run menu. Architecture details live in
[docs/architecture.md](docs/architecture.md).

### Local Install

Clone the repo and run the same installer from the working tree:

```sh
mkdir -p ~/.local/share/goose/mycroft
git clone https://github.com/buriedsignals/mycroft.git ~/.local/share/goose/mycroft/source
bash ~/.local/share/goose/mycroft/source/install.sh
```

### Manual Install

Manual setup is for development and debugging. At minimum:

```sh
mkdir -p ~/.local/share/goose/mycroft
git clone https://github.com/buriedsignals/mycroft.git ~/.local/share/goose/mycroft/source

export GOOSE_RECIPE_PATH=~/.local/share/goose/mycroft/source/recipes:~/.config/goose/mycroft/generated-recipes

mkdir -p ~/.config/goose/custom_providers
cp ~/.local/share/goose/mycroft/source/providers/fireworks-qwen36plus.json ~/.config/goose/custom_providers/
cp ~/.local/share/goose/mycroft/source/providers/together-qwen.json ~/.config/goose/custom_providers/

mkdir -p ~/.config/goose/mycroft
cp ~/.local/share/goose/mycroft/source/instructions/mycroft-soul.md ~/.config/goose/mycroft/SOUL.md
cp ~/.local/share/goose/mycroft/source/instructions/journalism.md ~/.config/goose/.goosehints
```

Use the guided installer for normal use; it also handles QMD, schedules, updater
state, generated instructions, and first-run files.

## Privacy And Providers

Mycroft is designed for privacy-sensitive reporting:

- ZDR providers are the default cloud posture.
- Local inference is available for sovereign workflows.
- Vaults, schedules, generated instructions, and fallback script secrets live on
  the user's machine.
- API keys are stored locally through Goose or Mycroft config files, not in the
  vault.
- Source acquisition and fact-check recipes preserve local evidence trails where
  tooling is available.

Model choice belongs in provider/runtime docs, not the product overview. The
important contract is that Mycroft can operate with the newsroom's chosen
provider posture.

## Shipping Recipes

**Core journalism**

- `start`
- `vault-qa`
- `fact-check`
- `source-verify`
- `morning-brief`
- `morning-brief-preflight`
- `vault-audit`
- `newsletter-summarize`
- `vault-sync`
- `qmd`

**Source acquisition and parsing**

- `firecrawl-scrape`
- `firecrawl-change-track`
- `firecrawl-pdf`
- `firecrawl-batch`
- `firecrawl-map`
- `dev-browser`
- `liteparse`

**Social and optional workflows**

- `apify-social/select-actor`
- `apify-social/instagram`
- `apify-social/x`
- `apify-social/facebook`
- `apify-social/tiktok`
- `apify-social/instagram-comments`
- `apify-social/linkedin`
- `voice-setup`
- `update-mycroft`

## Documentation

- [Architecture](docs/architecture.md) — how Mycroft layers onto Goose.
- [First run](docs/first-run.md) — what happens after setup.
- [Grounding and provenance](docs/grounding-provenance-spec.md) — evidence
  bundles, claim grounding, and optional C2PA signing.
- [Schedules](docs/schedules.md) — morning brief, vault audit, and updater
  schedules.
- [Plugin authoring](docs/plugin-authoring.md) — adding workflows and plugins.
- [Troubleshooting](docs/troubleshooting.md) — common install and runtime
  failures.
- [Security policy](SECURITY.md) — disclosure process.
- [Contributing](CONTRIBUTING.md) — contribution guidance.
- [Changelog](CHANGELOG.md) — release history.

## What To Do Next

Start Goose with the Mycroft profile and choose one action from the first-run
menu. Use Mycroft for durable knowledge and publishing support. Use Spotlight
when a lead needs active investigation. Use Scoutpost when something should be
monitored over time.

## Acknowledgements

Five of Mycroft's journalism skills — `foia-requests`, `interview-prep`,
`story-pitch`, `photo-metadata`, and `ai-writing-detox` — are adapted from
[claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism)
by [Joe Amditis](https://skills.amditis.tech/) (Center for Cooperative Media,
Montclair State University), MIT licensed. Each skill carries its attribution
and our localization edits; the full record lives in [NOTICE.md](NOTICE.md)
and [docs/amditis-catalogue.md](docs/amditis-catalogue.md).

## License

[MIT](LICENSE) - © 2026 Buried Signals.
