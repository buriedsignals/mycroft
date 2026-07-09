<div align="center">

# Mycroft

### Goose extension pack for investigative journalists

**Newsroom memory, recurring editorial workflows, and source-grounded fact-checking — 16 skills, 27 recipes, open-weight and local-capable, ZDR cloud optional.**

[Install](#install) | [First Run](#first-run) | [Core Workflows](#core-workflows) | [Recipes](#shipping-recipes) | [Website](https://mycroft.buriedsignals.com/)

[![License: MIT](https://img.shields.io/badge/license-MIT-00c853?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)[![16 Skills](https://img.shields.io/badge/skills-16-0080ff?style=for-the-badge&logo=bookstack&logoColor=white)](https://github.com/buriedsignals/mycroft/tree/main/skills)[![27 Recipes](https://img.shields.io/badge/recipes-27-ff6d00?style=for-the-badge&logo=windowsterminal&logoColor=white)](https://github.com/buriedsignals/mycroft/tree/main/recipes)[![Privacy](https://img.shields.io/badge/privacy-local_or_ZDR_cloud-00bfa5?style=for-the-badge&logo=shield&logoColor=white)](#privacy-and-providers)

[![Stars](https://img.shields.io/github/stars/buriedsignals/mycroft?style=flat-square&logo=github&label=Stars)](https://github.com/buriedsignals/mycroft/stargazers)[![Issues](https://img.shields.io/github/issues/buriedsignals/mycroft?style=flat-square&logo=github&label=Issues)](https://github.com/buriedsignals/mycroft/issues)[![Last Commit](https://img.shields.io/github/last-commit/buriedsignals/mycroft?style=flat-square&logo=github&label=Last%20Commit)](https://github.com/buriedsignals/mycroft/commits)[![Contributors](https://img.shields.io/github/contributors/buriedsignals/mycroft?style=flat-square&logo=github&label=Contributors)](https://github.com/buriedsignals/mycroft/graphs/contributors)

Built by [**Buried Signals**](https://buriedsignals.com/) • [tom@buriedsignals.com](mailto:tom@buriedsignals.com)

</div>

---

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
cp ~/.local/share/goose/mycroft/source/providers/fireworks-glm52.json ~/.config/goose/custom_providers/

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
- **Web search and scrape are sovereign by default** — a local SearXNG (search)
  and Crawl4AI (scrape) run with no API key or vendor account; Firecrawl is only an
  optional fallback when `FIRECRAWL_API_KEY` is set. An opt-in `--tor` fetch can
  route scraping through Tor so a target of investigation never sees the operator's
  IP. The installer provisions this stack, and `mycroft update` keeps it current.
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

**Source acquisition and parsing** — sovereign by default (Crawl4AI scrape, SearXNG search, `pdftotext`, `sitemap.py`); Firecrawl is only an optional fallback when `FIRECRAWL_API_KEY` is set. The recipe filenames keep the `firecrawl-` prefix for now.

- `firecrawl-scrape` — scrape a URL to markdown (Crawl4AI)
- `firecrawl-change-track` — snapshot + diff a page across runs
- `firecrawl-pdf` — extract a civic PDF (pdftotext)
- `firecrawl-batch` — scrape many URLs
- `firecrawl-map` — enumerate a domain's URL space (sitemap.py)
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

Mycroft stands on open work — community-maintained open-source projects and
open methods. A sincere thank-you to every project below — the pack would not
exist without them. *(Listing does not imply affiliation or endorsement.)*

| Category | Projects we're grateful to |
|----------|----------------------------|
| **Agent runtime** | [Goose](https://github.com/block/goose) (Block, Apache-2.0 — the open-source runtime Mycroft is built on) |
| **Journalism skills & methods** | [claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism) (Joe Amditis, MIT) · [SIFT](https://hapgood.us/2019/06/19/sift-the-four-moves/) (Mike Caulfield) |
| **Sovereign search & scraping** | [SearXNG](https://github.com/searxng/searxng) (AGPL-3.0) · [Crawl4AI](https://github.com/unclecode/crawl4ai) (unclecode, Apache-2.0) · [Playwright](https://playwright.dev/) (browser automation) · [Poppler](https://poppler.freedesktop.org/) (`pdftotext` — PDF extraction) · [Tor](https://www.torproject.org/) (opt-in anonymous scraping) |
| **Local inference** | [llama.cpp](https://github.com/ggml-org/llama.cpp) (ggml, MIT) |
| **Media & metadata** | [ExifTool](https://exiftool.org/) (Phil Harvey — powers photo-metadata) |
| **Knowledge vault** | [Obsidian](https://obsidian.md/) (the vault app) · [QMD](https://www.npmjs.com/package/@tobilu/qmd) (tobilu — local vault search) |
| **Provenance** | [C2PA](https://c2pa.org/) (content-provenance standard behind SIFT manifests) |

> Built something here we should credit, or want a listing changed or removed?
> Open an issue or PR — we'll fix it fast.

### Vendored skills

Five of Mycroft's journalism skills — `foia-requests`, `interview-prep`,
`story-pitch`, `photo-metadata`, and `ai-writing-detox` — are adapted from
[claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism)
by [Joe Amditis](https://skills.amditis.tech/) (Center for Cooperative Media,
Montclair State University), MIT licensed. Each skill carries its attribution
and our localization edits; the full record lives in [NOTICE.md](NOTICE.md)
and [docs/amditis-catalogue.md](docs/amditis-catalogue.md).

## License

[MIT](LICENSE) - © 2026 Buried Signals.
