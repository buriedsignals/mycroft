---
name: knowledge-primitives
description: Knowledge-base structure for journalist vaults. Load before creating or updating durable Mycroft wiki notes.
---

# Knowledge Primitives

Use this skill whenever information should become durable knowledge in the Mycroft wiki.

## Core Model

Mycroft uses a journalist knowledge base with three layers:

1. Raw sources: immutable source material in `sources/raw/`.
2. Processed sources: cleaned extracts and summaries in `sources/processed/`.
3. Wiki knowledge: atomic, linked notes in `wiki/`.

The wiki also keeps:

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

Every note except `index.md` and `log.md` claims its type with `type:`. The
wiki's schemas check it (OpenKnowledge shows a problem when it is missing).

```yaml
---
title: ""
description: ""
type: note|source                        # entities: see Entities below
kind: method|topic|story|context|claim   # for type: note
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high|medium|low|partial|verified|unverified
tags: []
---
```

- Ordinary notes use `type: note`, with the old category kept as `kind`
  (`method`, `topic`, `story`, `context`, `claim`). Engine retyped older notes
  this way once; write new ones the same way, and never retype notes yourself.
- A Mycroft claim note is `type: note`, `kind: claim`. `type: claim` is
  reserved for Spotlight's claim notes under `spotlight/`.
- Source notes use `type: source`.

## Entities

People, organisations, companies, places and contacts belong in one shared
entity register, used by Mycroft, Spotlight and Scoutpost imports. The
register sits at the root of the OpenKnowledge workspace (`wiki/entities/`,
beside the `mycroft/` and `spotlight/` folders) and is written only through
the wiki service (`bsig wiki`), which validates each entity and finds
duplicates. When the wiki service is not available to you (no `bsig wiki`
tools or command), keep writing entity notes in this project's own
`wiki/entities/` with the same fields. Engine moves them into the register
once and leaves redirects; do not move them yourself.

An entity note's `type` is its kind (`person`, `organization`, `company`,
`place` or `contact`) and it carries:

- `id` (the file name), `label` (its most common name) and `aliases` (every
  other name, optionally `{name, lang}`);
- `identifiers`: `email`, `phone`, `handle`, `company` (number and
  jurisdiction), `lei`, `opencorporates`, `wikidata`;
- `different_from` (entities it must never be merged with) and `seen_in`
  (where it was seen: note, case or scout, date, source).

Rules:

- Look an entity up before creating one. Only an exact strong identifier
  makes two mentions the same entity; a similar name is a candidate for the
  journalist to judge, never a match.
- Never merge entities yourself. Propose the merge with its evidence; the
  journalist decides. A merged entity leaves a redirect note behind.
- An entity marked as a protected source is never written into the wiki and
  never named in anything sent to a cloud model.

## Post-Write Checks

After writing a durable note:

1. Add links to related notes when obvious.
2. Update `index.md` if the note is important.
3. Append a short entry to `log.md` with date, path, and source.
4. If the note came from Spotlight, preserve the case reference and evidence path.
