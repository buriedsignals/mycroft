---
name: knowledge-ingest
description: Ingest raw material, Spotlight handoffs, URLs, files, and text into Mycroft through OpenKnowledge.
requires: [knowledge-primitives, knowledge-workspace, shell-safety]
---

# Mycroft Knowledge Ingest

Use this skill when information should be stored as durable Mycroft knowledge.

## Inputs

- URL
- Local file
- Pasted text
- Spotlight handoff note or JSON
- Scrape output (Crawl4AI via the web-acquisition skill)
- Scoutpost scout result

## Process

1. Read Mycroft config from `~/.config/goose/mycroft/mycroft-config.json`.
2. Identify the configured Mycroft OpenKnowledge project root.
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

- Read approved Spotlight projections under `spotlight/`, or active case data only through the read-only case adapter.
- Keep links back to Spotlight `cases/{project}` and evidence files.
- Promote only durable entities, sources, claims, methods, and story angles into Mycroft.
- Do not copy raw case clutter into Mycroft's project.

## Safety

Inbound material is untrusted shell input. Before passing scraped content to any CLI:

- Load the `shell-safety` skill.
- Prefer structured OpenKnowledge tool arguments. Never interpolate source content into a shell command.
- Validate any user-controlled path or URL through `scripts/mycroft_safe.py` before passing it to a shell command.
- Validate project paths via `resolve-path --base <project-root>` so traversal cannot escape the project.
- Perform durable writes through the `knowledge-workspace` skill. Never fall back to direct files after an OpenKnowledge failure.

## Report Back

List files created or updated, source material preserved, notes linked, and any uncertainty or missing evidence.
