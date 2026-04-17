# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release scaffold.
- Hosted setup page (`index.html`, `setup.html`) — client-side only, generates a `mycroft-setup.command` bash script.
- Goose Extension Pack: 22 recipes across journalism workflows, Firecrawl wrappers, Apify social scrapers, document tools.
- Journalism Instructions (`instructions/journalism.md`) — SIFT, attribution rules, source protection, tone.
- Provider configs: Fireworks (Qwen 3.6 Plus), Together AI, OpenRouter (optional failover), local MLX, local llama-server.
- IM Fell English wordmark + M-alone favicon.
- Plugin scaffolding: Spotlight + coJournalist (launching with Mycroft), DataHound + Atelier (May 2026).
- Memory templates (`memory/USER.md`, `memory/MEMORY.md`).

### Security
- All downloaded artefacts carry user's own API keys embedded client-side; no server ingestion.
- Sovereignty toggle (cloud / local-first) with `MYCROFT_DEFAULT_SOVEREIGNTY` + `MYCROFT_LOCAL_ONLY` env vars.

## [0.1.0] — TBD

Initial tagged release — pending pilot feedback.
