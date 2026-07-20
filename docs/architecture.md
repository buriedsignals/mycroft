# Mycroft Architecture

## Install contract ownership

Mycroft owns the product content and declarative install contract under
`install/contracts/`: normalized choices, the versioned runtime-config schema,
the lookup-only config template, validation limits, and golden fixtures. The
Engine compiles the website channel's canonical paths, catalog-pinned source,
resolved skills, projections, and ownership operations into a reduced signed
bundle at release time. The public installer applies that bundle without ever
receiving Engine. Mycroft's local configurator retains its established product
configuration writer so provider choices, Goose behavior, and OpenKnowledge
paths remain compatible; Engine owns the generated acquisition and lifecycle
contract, while the product phase fills that declared ownership boundary.

Mycroft is a Goose extension pack, not a fork of Goose.

The installer sets up Goose separately, then layers Mycroft configuration on top:

- provider JSON files in `~/.config/goose/custom_providers/`
- global Goose hints at `~/.config/goose/.goosehints`
- Mycroft Goose profile under `~/.config/goose/mycroft/`
- updateable Mycroft source checkout under `~/.local/share/goose/mycroft/source/`
- plugin checkouts under `~/.local/share/goose/mycroft/plugins/`
- recipe discovery through `GOOSE_RECIPE_PATH=~/.local/share/goose/mycroft/source/recipes:~/.config/goose/mycroft/generated-recipes`
- Mycroft skills under `~/.local/share/goose/mycroft/source/skills`
- generated scheduled recipes under `~/.config/goose/mycroft/generated-recipes`
- local runtime config at `~/.config/goose/mycroft/mycroft-config.json`
- fallback script secrets at `~/.config/goose/mycroft/.env`
- QMD local markdown search collections for the Mycroft and Spotlight vaults

Goose stays current through Goose's own update path, such as Homebrew for the
Desktop cask and the Goose CLI updater. Mycroft's updater applies the latest
signature-verified product release and never advances the source to an unsigned
branch head. A separately installed Spotlight owns its own signed update path.

## Goose Context

Mycroft uses two Goose context mechanisms:

- `~/.config/goose/.goosehints` for install-specific paths, vault locations, skills, schedules, and plugin context loaded at session start.
- `GOOSE_MOIM_MESSAGE_FILE=~/.config/goose/mycroft/SOUL.md` for persistent instructions injected every turn by Goose's Top Of Mind extension.

The soul file gives Goose the Mycroft identity, voice, and core operating principles. It stays concise because persistent instructions are injected every turn.

## Vaults

Mycroft and Spotlight use separate Obsidian vaults.

Mycroft is durable knowledge and publishing support:

- `_schema/`
- `sources/raw/`
- `sources/processed/`
- `wiki/`
- `stories/`
- `context/`
- `handoff/from-spotlight/`

Spotlight is active OSINT casework:

- `cases/`
- `evidence/`
- `captures/`
- `briefs/`
- `exports/`
- `handoff-to-mycroft/`

Goose instructions include both paths when Spotlight is enabled, plus the Spotlight ingest target back into the Mycroft vault.

## QMD

QMD is the local markdown search dependency used by Mycroft and Spotlight.

Setup installs the CLI with `npm install -g @tobilu/qmd`, registers the Mycroft vault as collection `mycroft`, registers the Spotlight vault as collection `spotlight` when enabled, and runs `qmd update`.

QMD also provides an MCP server through `qmd mcp`; agents that support MCP can use that server directly. Spotlight's `query-vault` verb is backed by `BUN_INSTALL="" qmd query`.
