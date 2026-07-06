# Amditis skill catalogue — curation record (T5)

**Upstream:** `jamditis/claude-skills-journalism` (MIT, Joe Amditis, Center for Cooperative Media)
**Pinned SHA:** `2097d218c6f38a8e7be77ce5f0ff6c2e39671f13` (master, fetched 2026-07-06)
**Skill source paths:** `journalism-core/skills/<id>/` at that SHA
**Deciding PRD:** engine `docs/plans/2026-07-06-amditis-skills-and-skill-architecture-prd.md`
**List finalized by Tom 2026-07-06 (rev 2, post-Gate A):** 5 skills, no opt-in tier —
data-journalism EXCLUDED (Buried Signals is building a better in-house option). This doc records
the deep-read verdicts and the edits required on vendor (T7).

## Verdicts (cleanest → riskiest)

| Skill | Lines | Verdict | Goose-compat | US-centric |
|---|---|---|---|---|
| story-pitch | 393 | SHIP | clean | examples only — fine |
| photo-metadata | 106 | SHIP-WITH-EDITS | needs `exiftool` + python3 | cosmetic |
| interview-prep | 331 | SHIP-WITH-EDITS | clean | recording-consent law is US |
| ai-writing-detox | 265 | SHIP-WITH-EDITS | 1 Claude-Code hooks ref | AP style = US house style |
| foia-requests | 631 | SHIP-WITH-EDITS | clean | **blocking — US-law-only** |
| ~~data-journalism~~ | 1086 | **EXCLUDED at Gate A** — in-house replacement planned | — | — |

## Required edits on vendor (T7 checklist)

**Cross-cutting**
- Dangling skill refs → remap or delete: `web-archiving` (interview-prep L46, photo-metadata L24),
  `interview-transcription` (interview-prep L294/298), `accessibility-compliance`
  (photo-metadata L23). Delete or inline.
- **Hook references policy (Tom, Gate A):** do NOT strip mentions of upstream hook companions —
  rewrite them as OPTIONAL, harness-dependent pointers: "Optional (Claude Code only): the upstream
  repo ships an automated companion hook — see jamditis/claude-skills-journalism `hooks/`."
  Goose has no hook support; the pointer must say so.
- Attribution frontmatter block + footer on every file (sync script injects; SHA above).
- US-scope banners where flagged below.

**foia-requests**
- **Bug:** tracker computes `date_submitted + 28 days` (L347) while docstring says "20 business
  days" (L345). Fix submitted upstream: jamditis/claude-skills-journalism#180 (business-day count,
  holiday caveat). Vendor applies the same patch locally regardless of merge timing.
- Add "US-only; EU Reg. 1049/2001 / UK FOIA 2000 users see national equivalents" banner.
- Move 50-state statute table (L74-129) + Python tracker (L295-373) to `reference.md` (~-130 lines).

**interview-prep**
- GDPR note on the US recording-consent section (L138-156).

**photo-metadata**
- MUST vendor companions `reference.md` + `embed.py` (+ skip `test_embed.py`).
- State the `exiftool` + `python3` install prerequisite in the skill header.

**ai-writing-detox**
- Rewrite L265 (`hooks/ai-slop-detector.md`) as an optional Claude-Code-only pointer per the hook
  policy above (do not delete).
- One-line scope boundary vs Mycroft `copywriting`: "copywriting owns outlet voice; this owns
  AI-tell removal." Mark AP "over"-rule + sentence-case headings as US house style.

**data-journalism** — EXCLUDED. Not vendored in any form; Buried Signals is building a better
in-house data-journalism option. The deep-read findings (hallucinated Datawrapper API, plaintext
key pattern, US-only sources) are preserved in git history if ever needed.

## Gate A — RESOLVED (Tom, 2026-07-06)

1. **data-journalism: EXCLUDED** — final set is 5 skills (foia-requests, interview-prep,
   story-pitch, photo-metadata, ai-writing-detox).
2. **foia deadline bug: fix submitted upstream** — jamditis/claude-skills-journalism#180.
3. **Hooks: optional pointers**, not deletions (policy above).
4. **Credit text approved** (five skills; text below updated):
   > Five journalism skills adapted from [claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism)
   > by Joe Amditis (Center for Cooperative Media, Montclair State University), MIT License —
   > vendored at `2097d218` with localization and integration edits for Mycroft.
