---
name: obsidian
description: Obsidian vault operations for Mycroft journalist knowledge bases.
---

# Obsidian Operations

Use this skill for any Mycroft vault read or write.

## Configured Vaults

Read paths from `~/.config/goose/mycroft/mycroft-config.json`:

- Mycroft vault: durable knowledge and story work.
- Spotlight vault: active OSINT casework, if installed.

Do not assume default paths. Use config first, then environment variables:

- `MYCROFT_VAULT_PATH`
- `SPOTLIGHT_VAULT_PATH`

## Write Preference

Use direct filesystem writes for setup scaffolding and generated files. Use Obsidian CLI when available for interactive vault operations.

When using Obsidian CLI:

```sh
obsidian vault=<vault-name> create name="<title>" path="<folder>/" content="<content>" silent
obsidian vault=<vault-name> read path="<path>"
obsidian vault=<vault-name> search query="<terms>"
```

If Obsidian CLI is unavailable, use direct file reads/writes under the configured vault path.

## Mycroft Vault Shape

```text
_schema/
_index.md
_log.md
context/
sources/raw/
sources/processed/
wiki/entities/
wiki/topics/
wiki/sources/
wiki/methods/
wiki/claims/
stories/pitches/
stories/drafts/
stories/published/
handoff/from-spotlight/
```

## Spotlight Vault Shape

```text
cases/
evidence/
captures/
briefs/
exports/
handoff-to-mycroft/
```

Keep Spotlight casework separate from durable Mycroft knowledge.
