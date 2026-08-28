<div align="center">

# Mycroft

### Goose extension pack for investigative journalists

**Newsroom memory, recurring editorial workflows, and source-grounded fact-checking — 18 skills, open-weight and local-capable, ZDR cloud optional.**

[Install](#install) | [First Run](#first-run) | [Core Workflows](#core-workflows) | [Skills](#skills) | [Recipes](#shipping-recipes) | [Website](https://mycroft.buriedsignals.com/)

[![License: MIT](https://img.shields.io/badge/license-MIT-00c853?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)[![18 Skills](https://img.shields.io/badge/skills-18-0080ff?style=for-the-badge&logo=bookstack&logoColor=white)](https://github.com/buriedsignals/mycroft/tree/main/skills)[![Privacy](https://img.shields.io/badge/privacy-local_or_ZDR_cloud-00bfa5?style=for-the-badge&logo=shield&logoColor=white)](#privacy-and-providers)

[![Stars](https://img.shields.io/github/stars/buriedsignals/mycroft?style=flat-square&logo=github&label=Stars)](https://github.com/buriedsignals/mycroft/stargazers)[![Issues](https://img.shields.io/github/issues/buriedsignals/mycroft?style=flat-square&logo=github&label=Issues)](https://github.com/buriedsignals/mycroft/issues)[![Last Commit](https://img.shields.io/github/last-commit/buriedsignals/mycroft?style=flat-square&logo=github&label=Last%20Commit)](https://github.com/buriedsignals/mycroft/commits)[![Contributors](https://img.shields.io/github/contributors/buriedsignals/mycroft?style=flat-square&logo=github&label=Contributors)](https://github.com/buriedsignals/mycroft/graphs/contributors)

Built by [**Buried Signals**](https://buriedsignals.com/) • [tom@buriedsignals.com](mailto:tom@buriedsignals.com)

</div>

---

Mycroft is a Goose extension pack for newsroom memory, recurring editorial
workflows, source-grounded fact-checking, and connections to the rest of the
Buried Signals suite.

It gives an investigative journalist a durable local OpenKnowledge wiki, a set
of Goose recipes for common reporting work, and a privacy-conscious provider
setup that can run with ZDR cloud models or local inference.

## What Mycroft Does

- Maintains an OpenKnowledge journalism wiki for sources, notes, methods,
  story material, and promoted Spotlight findings.
- Ingests links, PDFs, newsletters, pasted notes, documents, and folders into
  structured local knowledge.
- Answers questions over that wiki with citations.
- Runs SIFT-style source checks and draft fact-checks.
- Produces morning briefs and recurring wiki audits.
- Helps set up beats, watchlists, source-monitoring profiles, and story
  triggers.
- Connects to Scoutpost monitoring and Spotlight investigations when those
  sibling products are installed.
- Keeps provider and workspace configuration local to the user's machine.

## Core Workflows

| Workflow | What it does | Main recipe |
|---|---|---|
| Start | First-run menu for beats, knowledge ingest, morning brief, scouts, lead investigation, or demo flow. | `start` |
| Wiki Q&A | Answers questions over local newsroom memory and live sources with citations. | `wiki-qa` |
| Knowledge ingest | Turns links, notes, files, PDFs, folders, and newsletters into structured knowledge. | `wiki-sync`, `newsletter-summarize` |
| Fact-check | Checks article drafts or claims with SIFT-style verdicts and optional provenance packaging. | `fact-check` |
| Perspective audit | Traces observed viewpoints from source passages through summaries and an optional draft. | `perspective-audit` |
| Source verification | Evaluates a single source's credibility and evidence value. | `source-verify` |
| Morning brief | Builds a recurring digest from configured beats, watchlists, bookmarks, and recent wiki changes. | `morning-brief` |
| Wiki audit | Finds weak claims, missing frontmatter, orphaned sources, and stale promoted Spotlight findings. | `wiki-audit` |
| Browser acquisition | Opens a journalist-controlled browser session for portals, forms, downloads, and authenticated source capture. | `dev-browser` |
| Scoutpost | Sets up or queries hosted monitoring scouts and information units. | `scoutpost` skill |
| Spotlight case | Reads an existing Spotlight case read-only, or launches Spotlight for a new lead (Spotlight owns the brief gate). | `spotlight-case` |

## Mycroft, Spotlight, Scoutpost

These are **sibling products**. Indicator Lab can install several of them on one
machine; Mycroft does **not** install Spotlight (or Scoutpost) for you.

- **Mycroft** — durable knowledge and publishing support: source records, wiki
  notes, claim checks, methods, story pitches, drafts, briefings.
- **Spotlight** — active OSINT casework: briefs, methodology, research cycles,
  evidence, review, exports. Own installer, own workspace, own update path —
  including its own brief approval gate.
- **Scoutpost** — hosted monitoring: page/beat/social scouts and alerts.

When both Mycroft and Spotlight are present, Mycroft records Spotlight’s paths
so it can (1) launch Spotlight with a lead and let Spotlight brief the case, or
(2) read an existing case read-only without copying live files into the wiki
(`spotlight-case`). Material you choose to keep long-term can be promoted into
Mycroft under `handoff/from-spotlight/`.

Typical loop: Scoutpost surfaces leads → Spotlight investigates → Mycroft keeps
the durable notes and supports publication.

## First Run

When the installer finishes it opens a personalized getting-started guide in
the browser — example prompts and first workflows, written to
`~/.config/goose/mycroft/getting-started.html`. Mycroft also
opens Goose and writes `START_HERE.md` into the wiki. The first-run menu
offers:

- Set up my beat.
- Add material to my knowledge base.
- Create my morning brief.
- Investigate a lead.
- Set up scouts.
- Show me a demo workflow.

If the wiki is empty and the journalist already has material, start with
knowledge ingest. If the journalist already knows the beat, start with the
morning brief preflight. If the lead needs active OSINT work and Spotlight is
installed, launch Spotlight (`spotlight-case` with action `launch`) and let it
run its brief gate.

See [docs/first-run.md](docs/first-run.md).

## OpenKnowledge wiki

Mycroft’s durable memory is an OpenKnowledge workspace. Default location:
`~/Documents/OpenKnowledge/Mycroft`.

```text
_schema/
sources/raw/
sources/processed/
wiki/
stories/
context/
handoff/from-spotlight/
_audits/
```

Spotlight uses a **separate** workspace / case root for active investigations.
Mycroft never mixes live case state into its wiki; it only reads cases
read-only (`spotlight-case`), and only keeps what you promote under
`handoff/from-spotlight/`.

## Skills

Shipped skill set is the engine-resolved list in
[`skills.manifest`](skills.manifest) (18 skills):

| Skill | Role |
|---|---|
| `ai-writing-detox` | Strip AI-sounding patterns from drafts |
| `bsig-engine` | Talk to the Buried Signals Engine / Indicator Labs stack |
| `copywriting` | Editorial copy help |
| `epistemic-grounding` | Confidence, sourcing, and claim discipline |
| `fact-check` | SIFT-style claim checking |
| `foia-requests` | Public-records request drafting and tracking |
| `interview-prep` | Dossiers, question frames, attribution rules |
| `knowledge-ingest` | Bring material into the wiki |
| `knowledge-primitives` | Note types, frontmatter, link structure |
| `knowledge-workspace` | OpenKnowledge as the primary wiki interface |
| `mycroft-maintenance` | Doctor, update, and repair helpers |
| `navigator` | OSINT Navigator connection (membership unlocks) |
| `perspective-audit` | Trace viewpoints through sources and drafts |
| `photo-metadata` | Caption / IPTC / EXIF workflows |
| `scoutpost` | Hosted monitoring scouts |
| `shell-safety` | Safe shell use with untrusted inbound text |
| `story-pitch` | Pitch framing |
| `web-acquisition` | Local search/scrape (SearXNG + Crawl4AI) |

## Install

**Buried Signals Engine (`bsig`) is Mycroft's only installation authority.**
Indicator Labs submits the same Engine plans while adding guided setup,
credential prompts, repair, and automatic updates for
[members](https://buriedsignals.com/join).

For agent-led manual setup, fetch the signed Engine descriptor at:

```text
https://navigator.indicator.media/api/artifacts/bootstrap/bsig/<platform>
```

Use `darwin-arm64`, `darwin-amd64`, `linux-arm64`, `linux-amd64`, or
`windows-amd64`. Download the archive, checksum, signature, and public key
before the 60-second grants expire; verify SHA-256 and Minisign before running
`bsig`. Then:

```text
bsig catalog sync
bsig --json configure describe mycroft
```

The agent selects values from that signed descriptor and submits the JSON
request on stdin to `bsig configure plan mycroft`. Review and apply the emitted
`plan.json`. Secrets use Engine's stdin/keychain path, never argv or chat.
Manual updates use `bsig plan update mycroft`; Indicator Labs automates the
same lifecycle.

[`install.sh`](install.sh) remains a fail-closed pointer for old `curl | bash`
commands; it is not another installer. Contributors may clone
[`buriedsignals/mycroft`](https://github.com/buriedsignals/mycroft), but Engine
installs the catalog-pinned public commit for journalists.

## Privacy And Providers

Mycroft is designed for privacy-sensitive reporting:

- ZDR providers are the default cloud posture.
- The guided install defaults to OpenRouter with GLM-5.2. It configures Goose's
  `OPENROUTER_PARAMETERS` so every request includes `provider.zdr=true`, and
  checks OpenRouter's live endpoint list for a healthy GLM-5.2 ZDR route during
  setup. It also requires confirmation that account-level ZDR is enabled for
  OpenRouter's Non-frontier model group, protecting other Goose clients as
  defense in depth. This route requires Goose 1.41 or newer; the installer
  checks it. Fireworks remains the direct-host cloud alternative.
- Local inference is available when you want on-device models.
- **Web search and scrape are local by default** — SearXNG (search) and
  Crawl4AI (scrape) run with no API key or vendor account; Firecrawl is only an
  optional fallback when `FIRECRAWL_API_KEY` is set. An opt-in `--tor` fetch can
  route scraping through Tor so a target of investigation never sees the operator's
  IP. The installer provisions this stack, and `mycroft update` keeps it current.
- Wiki, schedules, generated instructions, and fallback script secrets live on
  the user's machine.
- API keys are stored locally through Goose or Mycroft config files, not in the
  wiki.
- Source acquisition and fact-check recipes preserve local evidence trails where
  tooling is available.

Model choice belongs in provider/runtime docs, not the product overview. The
important contract is that Mycroft can operate with the newsroom's chosen
provider posture.

## Shipping Recipes

**Core journalism**

- `start`
- `wiki-qa`
- `fact-check`
- `fact-check-c2pa`
- `perspective-audit`
- `source-verify`
- `morning-brief`
- `morning-brief-preflight`
- `wiki-audit`
- `newsletter-summarize`
- `wiki-sync`
- `spotlight-case`

**Source acquisition and parsing** — local by default (Crawl4AI scrape, SearXNG search, `pdftotext`, `sitemap.py`); Firecrawl is only an optional fallback when `FIRECRAWL_API_KEY` is set. The recipe filenames keep the `firecrawl-` prefix for now.

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
- `ft-preflight`

## Documentation

- [Architecture](docs/architecture.md) — how Mycroft layers onto Goose.
- [First run](docs/first-run.md) — what happens after setup.
- [Grounding and provenance](docs/grounding-provenance-spec.md) — evidence
  bundles, claim grounding, and optional C2PA signing.
- [Schedules](docs/schedules.md) — morning brief, wiki audit, and updater
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
| **Local search & scraping** | [SearXNG](https://github.com/searxng/searxng) (AGPL-3.0) · [Crawl4AI](https://github.com/unclecode/crawl4ai) (unclecode, Apache-2.0) · [Playwright](https://playwright.dev/) (browser automation) · [Poppler](https://poppler.freedesktop.org/) (`pdftotext` — PDF extraction) · [Tor](https://www.torproject.org/) (opt-in anonymous scraping) |
| **Local inference** | [llama.cpp](https://github.com/ggml-org/llama.cpp) (ggml, MIT) |
| **Media & metadata** | [ExifTool](https://exiftool.org/) (Phil Harvey — powers photo-metadata) |
| **Voice** | [Whisper](https://github.com/openai/whisper) (MIT — open-weight local dictation) · [Edge TTS](https://github.com/rany2/edge-tts) (rany2, LGPL-3.0 — spoken briefings) |
| **Knowledge workspace** | [OpenKnowledge](https://github.com/inkeep/open-knowledge) (local knowledge app, CLI, search, and agent workspace) |
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
