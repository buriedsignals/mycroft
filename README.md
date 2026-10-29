# Mycroft

**The on-device investigator harness.**

Mycroft runs in [Osaurus](https://osaurus.ai/) on your Mac. Plan research with
Navigator, investigate with Spotlight, keep watch with Scoutpost, and connect
what you find in your [OpenKnowledge](https://openknowledge.ai/) wiki.

[Website](https://mycroft.buriedsignals.com/) ·
[Install with Indicator Lab](https://indicator.media/indicator-lab) ·
[Manual setup](docs/install.md) · [Contributing](CONTRIBUTING.md)

## Install

[Indicator Lab](https://indicator.media/indicator-lab) provides guided setup,
connections to the tools, repair and updates. Mycroft's Osaurus setup is for
Mac; the installer checks compatibility before installation. Managed installation
is included for members of Indicator’s Lab tier.

Buried Signals Engine (`bsig`) handles installation for both Indicator Lab
and manual users. It installs the versions pinned in its signed catalogue.
Cloning this repository previews the website and gives you the source; it
does not configure the agents or install their models.

For manual or agent-led installation, follow [signed Engine setup](docs/install.md).
The old [`install.sh`](install.sh) deliberately exits without installing anything.

For an existing Engine installation, `bsig configure plan mycroft` prepares
an install plan and `bsig keys list` identifies optional credentials. See the
manual guide for configuration input and private key entry.

## Agents

| Agent | Role | Where it runs |
|---|---|---|
| Mycroft | Searches your wiki, finds OSINT tools with Navigator, works with Scoutpost monitors and extracts fields from documents. | On-device in Osaurus |
| Spotlight | Runs an investigation, with your review of the method and findings. | On-device in Osaurus |
| Analyst | Connects findings and proposes sourced additions to your wiki. You confirm writes before they land. | On-device; available through Osaurus and OpenKnowledge's Agents panel |
| Watson | Does web research when you select the cloud option. It has no wiki access. | Cloud, through OpenRouter using Mistral EU endpoints with zero data retention |

On-device inference does not make every connected service local. Navigator
and Scoutpost are hosted services. Osaurus asks before calls that create
something or send text to them. Keep confidential source identities out of
external requests.

The system instructions are in [`instructions/`](instructions/). The Analyst's
Pi and ACP dependencies are pinned in [`analyst/`](analyst/); Engine installs
them beside the managed checkout. Model choices come from Engine's signed
catalogue rather than this README.

## Skills

The installation and the website catalogue serve different purposes.

[`skills.manifest`](skills.manifest) lists **six installed skills**, each exposed
as a slash command on Mycroft:

| Skill | Purpose |
|---|---|
| [`navigator`](skills/osaurus/navigator/SKILL.md) | Find OSINT tools and methods |
| [`scoutpost`](skills/osaurus/scoutpost/SKILL.md) | Set up monitors and read their findings |
| [`foia-requests`](skills/foia-requests/SKILL.md) | Draft and track public-records requests |
| [`interview-prep`](skills/interview-prep/SKILL.md) | Prepare questions, background and attribution rules |
| [`story-pitch`](skills/story-pitch/SKILL.md) | Frame a story pitch |
| [`ai-writing-detox`](skills/ai-writing-detox/SKILL.md) | Remove formulaic AI writing patterns |

The **website features four skills and methods**: fact-checking, public-records
requests, interview preparation and story pitches. It omits the tool-connection
skills and AI-writing cleanup. Fact-checking is an archived method reference,
credited to Verso and Buried Signals; it is **not included in the current
Osaurus installation**. Its source and status are recorded in
[`catalog/featured-skills.json`](catalog/featured-skills.json).

The four installed journalism skills are adapted from Joe Amditis's
MIT-licensed work. Each retains its credit; see [third-party notices](NOTICE.md)
and the [provenance record](docs/amditis-catalogue.md).

## Repository guide

| Path | Contents |
|---|---|
| [`index.html`](index.html), [`DESIGN.md`](DESIGN.md) | Static landing page and its visual rules |
| [`assets/`](assets/), [`fonts/`](fonts/) | Product media, partner marks and typefaces |
| [`instructions/`](instructions/), [`skills/`](skills/) | Agent instructions and installed skills |
| [`analyst/`](analyst/) | Pinned Analyst runtime dependencies |
| [`install/contracts/`](install/contracts/) | Install schemas, templates and fixtures imported by Engine |
| [`catalog/`](catalog/) | Signed Engine catalogue mirror and website-only featured methods |
| [`runtimes/`](runtimes/) | Runtime-pack release record and licence notices |
| [`tests/`](tests/) | Website, catalogue and installer-pointer checks |

Preview the site with `python3 -m http.server 8765`, then open
`http://127.0.0.1:8765/`. There is no site build step. See
[Contributing](CONTRIBUTING.md) for checks and deployment.

## Credits and licence

Built by [Buried Signals](https://buriedsignals.com/), with
[Osaurus](https://osaurus.ai/) and [OpenKnowledge](https://openknowledge.ai/).
The Analyst uses [Pi](https://github.com/earendil-works/pi); the website uses
[Three.js](https://threejs.org/). Model versions and availability are controlled
by Engine. Media provenance is recorded beside the
[preview clips](assets/previews/README.md) and [screenshots](assets/screenshots/README.md).

[MIT](LICENSE) · [Third-party notices](NOTICE.md) · [Security](SECURITY.md)
