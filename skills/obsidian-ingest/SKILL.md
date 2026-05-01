---
name: obsidian-ingest
description: Ingest raw material, Spotlight handoffs, URLs, files, and text into the Mycroft knowledge vault.
requires: [knowledge-primitives, obsidian]
---

# Obsidian Ingest

Use this skill when information should be stored as durable Mycroft knowledge.

## Inputs

- URL
- Local file
- Pasted text
- Spotlight handoff note or JSON
- Firecrawl scrape output
- coJournalist scout result

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
7. Update `_index.md` and `_log.md`.

## Spotlight Handoff

When ingesting from Spotlight:

- Read from the configured Spotlight vault `handoff-to-mycroft/` or case data.
- Keep links back to Spotlight `cases/{project}` and evidence files.
- Promote only durable entities, sources, claims, methods, and story angles into Mycroft.
- Do not copy raw case clutter into Mycroft.

## Report Back

List:

- Files created or updated.
- Source material preserved.
- Notes linked.
- Any uncertainty or missing evidence.
