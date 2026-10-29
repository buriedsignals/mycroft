<div align="center">

# Mycroft

### Local agents for investigative journalists and investigators, built on Osaurus

**Mycroft runs on your Mac inside [Osaurus](https://osaurus.ai/) and keeps what you know in an [OpenKnowledge](https://openknowledge.ai/) wiki. It plans with Navigator, investigates with Spotlight and monitors with Scoutpost.**

[Website](https://mycroft.buriedsignals.com/) | [Install](#install) | [Agents](#agents) | [Skills](#skills)

[![License: MIT](https://img.shields.io/badge/license-MIT-00c853?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)

Built by [**Buried Signals**](https://buriedsignals.com/) • [tom@buriedsignals.com](mailto:tom@buriedsignals.com)

</div>

---

Mycroft is a set of agents, skills and models that Indicator Lab installs into
[Osaurus](https://osaurus.ai/), the local AI app for Mac. Our partners are
Osaurus, which runs the agents and the on-device models, and
[OpenKnowledge](https://openknowledge.ai/), which holds the wiki.

## Agents

| Agent | Where it runs | What it does |
|---|---|---|
| Mycroft | Osaurus, on-device (Gemma 4 12B) | Searches your wiki, finds OSINT methods with Navigator, sets up and reads Scoutpost monitors, and pulls fields from documents with an on-device extraction model (NuExtract3). |
| Spotlight | Osaurus, on-device | Runs a full investigation locally, with your approval on the method and the report. |
| Analyst (pilot) | OpenKnowledge's Agents panel, on-device | Files what Spotlight and Scoutpost find into your wiki. Every write is a proposal you confirm. |
| Watson | Cloud, only when you choose it | Web research through OpenRouter, routed only to Mistral's EU endpoints with zero data retention. It never sees your wiki. |

Navigator and Scoutpost are hosted services. Osaurus asks before any call that
sends your text to them.

The agents' instructions live in [`instructions/`](instructions/):
[`osaurus-system.md`](instructions/osaurus-system.md) for Mycroft and
[`analyst-system.md`](instructions/analyst-system.md) for the Analyst.
[`analyst/`](analyst/) pins the Pi runtime the Analyst runs on.

## Skills

[`skills.manifest`](skills.manifest) lists the skills the Osaurus install ships.
Each becomes a slash command on Mycroft.

| Skill | Role |
|---|---|
| `navigator` | Find OSINT tools and methods with Navigator ([`skills/osaurus/navigator`](skills/osaurus/navigator)) |
| `scoutpost` | Turn research into page and social monitors and read what they find ([`skills/osaurus/scoutpost`](skills/osaurus/scoutpost)) |
| `foia-requests` | Public-records request drafting and tracking |
| `interview-prep` | Dossiers, question frames and attribution rules |
| `story-pitch` | Pitch framing |
| `ai-writing-detox` | Strip AI-sounding patterns from drafts |

## Install

**Buried Signals Engine (`bsig`) is Mycroft's only installation authority.**
Indicator Labs submits the same Engine plans while adding guided setup,
credential prompts, repair, and automatic updates for
[members](https://indicator.media/indicator-lab).

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
`plan.json`. Preflight and `bsig keys list` name optional provider credential
IDs. A trusted local agent may prepare Engine's protected stdin/keychain flow,
but the user enters each value only through a private operating-system or
terminal prompt—never argv, chat, shell history, or a repository file. Manual
updates use `bsig plan update mycroft`; Indicator Labs automates the same
lifecycle.

[`install.sh`](install.sh) remains a fail-closed pointer for old `curl | bash`
commands; it is not another installer. Contributors may clone
[`buriedsignals/mycroft`](https://github.com/buriedsignals/mycroft), but Engine
installs the catalog-pinned public commit for journalists.

## Acknowledgements

Mycroft stands on open work. *(Listing does not imply affiliation or endorsement.)*

| Category | Projects we're grateful to |
|----------|----------------------------|
| **Partners** | [Osaurus](https://osaurus.ai/) (the local AI app Mycroft runs in) · [OpenKnowledge](https://github.com/inkeep/open-knowledge) (the local wiki and agent workspace) |
| **On-device models** | [Gemma 4](https://huggingface.co/OsaurusAI/gemma-4-12B-it-qat-MXFP4) (Google) · [LFM3](https://huggingface.co/LiquidAI/LFM3-1.7B) (Liquid AI) · [NuExtract3](https://huggingface.co/OsaurusAI/NuExtract3-JANG_6M) (NuMind) |
| **Agent runtime** | [Pi](https://github.com/badlogic/pi-mono) (the agent loop under the Analyst) |
| **Journalism skills** | [claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism) (Joe Amditis, MIT) |

### Vendored skills

Four of Mycroft's journalism skills — `foia-requests`, `interview-prep`,
`story-pitch` and `ai-writing-detox` — are adapted from
[claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism)
by [Joe Amditis](https://skills.amditis.tech/) (Center for Cooperative Media,
Montclair State University), MIT licensed. Each skill carries its attribution
and our localization edits; the full record lives in [NOTICE.md](NOTICE.md)
and [docs/amditis-catalogue.md](docs/amditis-catalogue.md).

## License

[MIT](LICENSE) - © 2026 Buried Signals.
