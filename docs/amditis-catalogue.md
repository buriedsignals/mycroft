# Amditis skill catalogue — curation record (T5)

**Upstream:** `jamditis/claude-skills-journalism` (MIT, Joe Amditis, Center for Cooperative Media)
**Pinned SHA:** `2097d218c6f38a8e7be77ce5f0ff6c2e39671f13` (master, fetched 2026-07-06)
**Skill source paths:** `journalism-core/skills/<id>/` at that SHA
**Deciding PRD:** engine `docs/plans/2026-07-06-amditis-skills-and-skill-architecture-prd.md`
**List finalized by Tom 2026-07-06:** 6 skills, no opt-in tier. This doc records the deep-read
verdicts and the edits required on vendor (T7).

## Verdicts (cleanest → riskiest)

| Skill | Lines | Verdict | Goose-compat | US-centric |
|---|---|---|---|---|
| story-pitch | 393 | SHIP | clean | examples only — fine |
| photo-metadata | 106 | SHIP-WITH-EDITS | needs `exiftool` + python3 | cosmetic |
| interview-prep | 331 | SHIP-WITH-EDITS | clean | recording-consent law is US |
| ai-writing-detox | 265 | SHIP-WITH-EDITS | 1 Claude-Code hooks ref | AP style = US house style |
| foia-requests | 631 | SHIP-WITH-EDITS | clean | **blocking — US-law-only** |
| data-journalism | 1086 | SHIP-TRIMMED (Gate A decision) | assumes full Python data stack | sources section near-blocking |

## Required edits on vendor (T7 checklist)

**Cross-cutting**
- Dangling skill refs → remap or delete: `web-archiving` (interview-prep L46, photo-metadata L24),
  `interview-transcription` (interview-prep L294/298), `accessibility-compliance`
  (photo-metadata L23), `fact-check-workflow`/`source-verification`/`social-media-intelligence`
  (data-journalism L1073). Remap fact-check-workflow→`fact-check`; delete the rest or inline.
- Attribution frontmatter block + footer on every file (sync script injects; SHA above).
- US-scope banners where flagged below.

**foia-requests**
- **Bug:** tracker computes `date_submitted + 28 days` (L347) while docstring says "20 business
  days" (L345) — a journalist trusting it gets the wrong statutory deadline. Fix or drop tracker.
- Add "US-only; EU Reg. 1049/2001 / UK FOIA 2000 users see national equivalents" banner.
- Move 50-state statute table (L74-129) + Python tracker (L295-373) to `reference.md` (~-130 lines).

**interview-prep**
- GDPR note on the US recording-consent section (L138-156).

**photo-metadata**
- MUST vendor companions `reference.md` + `embed.py` (+ skip `test_embed.py`).
- State the `exiftool` + `python3` install prerequisite in the skill header.

**ai-writing-detox**
- Delete L265 (`hooks/ai-slop-detector.md` — Claude-Code-only, dead in Goose).
- One-line scope boundary vs Mycroft `copywriting`: "copywriting owns outlet voice; this owns
  AI-tell removal." Mark AP "over"-rule + sentence-case headings as US house style.

**data-journalism** (heaviest; see Gate A decision)
- **Likely-hallucinated code:** the Datawrapper OOP API (`dw.BarChart(...)` etc., L630-668,
  L1024-1057) does not match the real `datawrapper` PyPI client interface. Verify or cut.
- Teaches plaintext API-key file (`datawrapper_api_key.txt`, L623/L1012) — env-var only.
- Scraping bullet (L155) → defer to the `firecrawl` skill.
- AI-cautions section (L357-378) → cross-link `fact-check`/`epistemic-grounding`, don't restate.
- Forward-dated US-politics claims stated as fact (L103/L109) — add verify-before-relying caveat.
- Sources section (L96-139) is ~all US federal; add EU/Eurostat/national-statistics block.
- Split ~600 lines of Python into `reference.md`; SKILL.md keeps methodology + sources.

## Gate A decisions for Tom

1. **data-journalism shape.** Mycroft users are non-developers with no shipped Python data stack;
   the code half is unrunnable for them and contains the likely-fake Datawrapper API. RECOMMENDED:
   vendor the trimmed methodology+sources variant (~450 lines) with code moved to `reference.md`
   marked "requires a Python environment; untested." Alternative: ship full with the same split
   but keep code in the body (rejected: 1086 lines of always-loaded context, embarrassment risk).
2. **Credit text** (NOTICE.md + getting-started), proposed:
   > Six journalism skills adapted from [claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism)
   > by Joe Amditis (Center for Cooperative Media, Montclair State University), MIT License —
   > vendored at `2097d218` with localization and integration edits for Mycroft.
3. **Nothing demotes outright.** All six survive the deep-read given the edits above.
