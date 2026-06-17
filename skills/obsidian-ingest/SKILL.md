---
name: obsidian-ingest
description: Ingest raw material, Spotlight handoffs, URLs, files, and text into the Mycroft knowledge vault.
requires: [knowledge-primitives, obsidian, shell-safety]
---

# Obsidian Ingest

Use this skill when information should be stored as durable Mycroft knowledge.

## Inputs

- URL
- Local file
- Pasted text
- Spotlight handoff note or JSON
- Firecrawl scrape output
- Scoutpost scout result

## Process

1. Read Mycroft config from `~/.config/goose/mycroft/mycroft-config.json`.
2. Identify the Mycroft vault path.
3. Preserve raw material under `sources/raw/` when applicable.
4. Write cleaned extracts under `sources/processed/`.
5. Create or update wiki notes under:
   - `wiki/entities/`
   - `wiki/sources/`
   - `wiki/methods/`
   - `wiki/claims/`
   - `wiki/topics/`
6. Add story candidates under `stories/pitches/` only when there is a publishable angle.
7. Update `index.md` and `log.md`.

## Spotlight Handoff

When ingesting from Spotlight:

- Read from the configured Spotlight vault `handoff-to-mycroft/` or case data.
- Keep links back to Spotlight `cases/{project}` and evidence files.
- Promote only durable entities, sources, claims, methods, and story angles into Mycroft.
- Do not copy raw case clutter into Mycroft.

## Safety

Inbound material (scraped pages, Spotlight handoffs, pasted text, scout results) is **untrusted shell input**. Backticks, `$(...)`, control characters, and unescaped quotes inside scraped markdown can break out of any shell command that interpolates the value into an argument.

Before writing scraped content via a CLI (e.g. `obsidian create ... content="..."`):

- Load the `shell-safety` skill.
- Prefer stdin or a temp-file argument over inline `content="..."` interpolation. See the CLI argument guidance in `shell-safety/SKILL.md`.
- Validate any user-controlled path or URL through `scripts/mycroft_safe.py` before passing it to a shell command.
- Validate vault paths via `resolve-path --base <vault>` so traversal cannot escape the vault root.

## Report Back

List:

- Files created or updated.
- Source material preserved.
- Notes linked.
- Any uncertainty or missing evidence.
