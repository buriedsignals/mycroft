# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

> **Next tag will be [0.2.0]** (pre-1.0 minor bump): fact-check output contract
> changes shape, which is a breaking change for downstream consumers parsing
> `cases/{project}/data/fact-check.json` or the legacy SIFT manifest.

### Added
- Initial release scaffold.
- Hosted setup page (`index.html`, `setup.html`) — client-side only, generates a `mycroft-setup.command` bash script.
- Goose Extension Pack: 22 recipes across journalism workflows, Firecrawl wrappers, Apify social scrapers, document tools.
- Journalism Instructions (`instructions/journalism.md`) — SIFT, attribution rules, source protection, tone.
- Provider configs: Fireworks (Qwen 3.6 Plus), Together AI, OpenRouter (optional failover), local MLX, local llama-server.
- IM Fell English wordmark + M-alone favicon.
- Plugin scaffolding: Spotlight + Scoutpost (launching with Mycroft), DataHound + Atelier (August-September 2026).
- Memory templates (`memory/USER.md`, `memory/MEMORY.md`).
- `skills/shell-safety/SKILL.md` and `scripts/mycroft_safe.py` — validation
  helper for URLs, DOIs, slugs, timestamps, and paths; rejects shell
  metacharacters, path traversal, leading-dash segments, and non-http schemes.
  Mirrored from the Spotlight bundle's `spotlight_safe.py` so each public
  install is self-contained.
- `tests/shell-safety-check.py` — hostile-input regression suite. Run it after
  any change to `mycroft_safe.py`.
- `skills/epistemic-grounding/SKILL.md` plus `references/failure-router.md`
  and `references/grounding-theory.md` — claim-to-evidence discipline with
  two profiles (newsroom-light for routine work; investigation-grade for
  fact-check). Includes the 5-tier grounding ladder and confidence-cap table.
- Setup installer now symlinks `~/.local/bin/mycroft-safe` →
  `scripts/mycroft_safe.py`, mirroring the existing `mycroft-fetch` pattern.
- `mycroft doctor` checks `mycroft-safe` (presence on PATH, runs a sanity
  `validate-url`) and the new `shell-safety` and `epistemic-grounding` skill
  paths.

### Changed
- `recipes/fact-check.yaml` is now provenance-first by default for
  fact-checking: it instructs agents to use `mycroft-fetch`, emit evidence and
  SIFT manifests, and build an unsigned provenance manifest when available.
  Provenance failures are reported as incomplete but non-blocking unless
  `strict_provenance=true`; live Noosphere/C2PA signing remains opt-in with
  `c2pa_sign=true`.
- **BREAKING — `fact-check/SKILL.md` output contract.** Every claim now
  requires a 7-field `grounding` object (support_type, source_role,
  claim_elements_checked, missing_assumptions, confidence_cap,
  misgrounding_risk, assessment), an `evidence_refs: [...]` array, and a
  `human_review: unreviewed|approved|rejected` field. Downstream consumers of
  `cases/{project}/data/fact-check.json` or the legacy SIFT manifest must
  update their parsers. Earlier drafts of this changelog listed a 10-field
  object; the redundant `grounding_strength` (overlapped support_type),
  `quote_match` (implied by support_type + source_role), and
  `contradiction_search` (free-text duplicate of assessment) were dropped
  before tagging.
- Profile names in `epistemic-grounding/SKILL.md` renamed to be functional
  rather than aspirational: `newsroom-light` → `default`,
  `investigation-grade` → `fact-check`. Names now describe the consumer, not
  the marketing tier.
- `fact-check/SKILL.md` Method section shortened: removed steps that
  duplicated `epistemic-grounding` discipline (claim decomposition, support
  classification, primary-source preference). The skill now lists only the
  three fact-check-specific moves on top of grounding.
- `schemas/sift-manifest.schema.json` and `schemas/provenance-manifest.schema.json`
  updated to match the trimmed grounding shape. provenance-manifest's claim
  block now uses `support_type` instead of `grounding_strength` for
  vocabulary consistency with sift-manifest.
- `recipes/fact-check-c2pa.yaml` JSON template updated to the 7-field shape.
- `fact-check/SKILL.md` now requires `[epistemic-grounding, shell-safety]`.
- `obsidian-ingest/SKILL.md` (public) now requires `shell-safety` and includes
  a Safety section documenting scraped content as untrusted shell input.
- `mycroft-doctor` exports `PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"`
  at the top so the doctor works correctly when run from cron, Goose recipes,
  or other non-interactive shells. (Same fix Spotlight shipped in
  `552637d`.)
- `docs/grounding-provenance-spec.md` status: `draft` → `v1` (2026-05-21).
  Three of four open questions resolved (artifact storage, search evidence
  model, editor verification state); Noosphere endpoint deferred.

### Security
- Hard rule added across Mycroft: any string from a fetched page, email body,
  social post, model output, or external API is untrusted shell input. Validate
  via `mycroft_safe.py` before passing to bash, curl, or any CLI that
  interprets quotes/dollars/backticks. Forbids `eval` and `bash -c "..."` on
  untrusted values.
- `obsidian-ingest` (public skill) now documents that scraped markdown should
  be written via stdin or temp file rather than interpolated into a CLI
  `content="..."` argv element.

## [0.1.0] — TBD

Initial tagged release — pending pilot feedback.
