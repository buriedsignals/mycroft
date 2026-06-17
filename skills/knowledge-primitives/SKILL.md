---
name: knowledge-primitives
description: Knowledge-base structure for journalist vaults. Load before creating or updating durable Mycroft wiki notes.
---

# Knowledge Primitives

Use this skill whenever information should become durable knowledge in the Mycroft vault.

## Core Model

Mycroft uses a journalist knowledge base with three layers:

1. Raw sources: immutable source material in `sources/raw/`.
2. Processed sources: cleaned extracts and summaries in `sources/processed/`.
3. Wiki knowledge: atomic, linked notes in `wiki/`.

The vault also keeps:

- `_schema/` for rules, frontmatter, and ingestion policy.
- `index.md` for navigation.
- `log.md` for ingestion history.
- `stories/` for publishable story work derived from investigations and knowledge.
- `handoff/from-spotlight/` for findings promoted from Spotlight.

## Note Rules

- One durable idea, entity, source, method, claim, or story object per note.
- Use frontmatter on every note.
- Link aggressively with `[[wikilinks]]`.
- Prefer precise filenames: lowercase, hyphen-separated, no spaces.
- Preserve raw sources. Do not overwrite source material.
- Keep uncertain material marked as `confidence: low` or `confidence: partial`.

## Minimum Frontmatter

```yaml
---
title: ""
description: ""
type: entity|source|method|claim|topic|story|context
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high|medium|low|partial|verified|unverified
tags: []
---
```

## Post-Write Checks

After writing a durable note:

1. Add links to related notes when obvious.
2. Update `index.md` if the note is important.
3. Append a short entry to `log.md` with date, path, and source.
4. If the note came from Spotlight, preserve the case reference and evidence path.
