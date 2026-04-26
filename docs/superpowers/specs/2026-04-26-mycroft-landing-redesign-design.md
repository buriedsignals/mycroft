# Mycroft landing redesign — design doc

**Date:** 2026-04-26
**Status:** Draft (awaiting review)
**Author:** Rémy + brainstorming session
**Scope:** Complete redesign of `index.html` (Mycroft landing page) as 3 parallel prototypes to compare, then converge on one.

---

## 1. Brief

The client asked for a creative redesign of the Mycroft landing page. Mycroft is the "big brother" of Sherlock — an AI assistant for investigative journalists. Current page is clean / standard dev-style; the client wants something signature.

Verbatim direction:

> "C'est le grand frère de Sherlock. Je pense pas trop sombre. Peut-être plus journaliste traditionnel mais réinventé ? Ces vieilles typos / papier de New York Times / Washington Post, mais revu avec du PRetext (https://github.com/chenglou/pretext) ça sera fou fou fou. Imagine dans le fond des archives de [NYU Top 100 Works of Journalism], décoratives, mais avec PRetext comme interaction. Pareil le titre 'Mycroft' dans une de ces vieilles typos prestigieuses de journaliste, mais en Three.js avec une interaction. Taking the old into the new. Prendre ces journalistes du passé et les amener vers le futur. Imagine un journal dans le fond, le titre c'est Mycroft, et les articles sont fluides / le layout s'ajuste. Le contenu peut venir des archives ou du texte qu'on doit vraiment mettre dans la page pour la description de l'outil, ou des deux."

Key signals:
- Not dark
- Old prestigious newspaper typography (NYT / WaPo era)
- PRetext as interaction substrate
- NYU Top 100 archives as background atmosphere
- Mycroft title in Three.js
- Old → new bridge as core narrative
- Content can come from archives, product copy, or both

## 2. Goals

- Produce 3 visually-coherent, conceptually-distinct prototypes the client can compare side-by-side.
- Each prototype expresses a different **interaction metaphor** for "old journalism brought into the future".
- Validate technical feasibility of the most ambitious one (PRetext glyph-level animation) early.
- Preserve the existing product copy (the brief said: keep content; structure may evolve).
- After client review, kill 2, refine 1, ship as the new `index.html`.

## 3. Non-goals

- Backend changes. The Goose / vault / agent stack is untouched.
- Setup form rework. `setup.html` stays as-is for this iteration.
- Accessibility regression. The new design must keep at least the current a11y baseline (skip link, focus styles, semantic structure, reduced-motion support).
- SEO / metadata regression. OG tags, structured data, robots.txt unchanged.
- Building all 3 prototypes to production polish. Prototypes are *enough* to make a decision, not deploy-ready.

## 4. Shared visual direction (all 3 prototypes)

Reference: the "Purgatoire" poster shared mid-brainstorm — cool light gray paper, deep textured ink, massive negative space, blackletter typography drama, subtle paper folds, no decorative ornament.

### Palette
- Background: cool off-white paper, ~`#e8e8e6`
- Ink: deep black with grain, `#0e0e0e` rendered with displacement/noise shader
- No accent color. Single signature glyph (TBD — possibly a small mark like the scissor in the Purgatoire ref) acts as rare punctuation.
- No dark mode. Light always.

### Typography
- Headline (Three.js): `UnifrakturMaguntia` (Google Fonts, libre) as base, deformed/grainy via shader. Blackletter, but contemporary — letters can touch, slight irregularity in strokes.
- Body: `Libre Caslon Text` (Google Fonts, libre) — open-source Caslon optimized for screen.
- Section labels / small caps: same Caslon family in italic + small caps.

### Material
- Subtle paper grain overlay (SVG noise or canvas-rendered texture)
- Subtle vertical fold lines (SVG overlay) — like a printed sheet folded
- Composition: centered, symmetric, dramatic via negative space
- No drop shadows, no gradients except the grain itself

## 5. Stack

- **Build:** Bun + Vite, project rooted at `/prototypes/` (separate from `index.html`)
- **Three.js:** ESM via Vite, MSDF text rendering for the headline + custom displacement/noise shader for grain
- **PRetext:** the real TypeScript lib from `chenglou/pretext`, integrated via Vite. (Verify it's published as npm package or vendored; document in setup.)
- **Languages:** TypeScript everywhere
- **Output:** each prototype is a static build. The winner gets extracted: either inlined back into a vanilla `index.html` (preserving current deploy model) or the whole landing migrates under Vite. Decision deferred until after client picks.

### Project layout

```
/prototypes/
  package.json           (Bun + Vite + Three.js + PRetext + TS)
  vite.config.ts
  tsconfig.json
  shared/
    fonts/               (UnifrakturMaguntia, Libre Caslon Text — self-hosted)
    corpus/              (archive texts in plain TXT or markdown)
      bly-mad-house.txt
      wells-southern-horrors.txt
      riis-other-half.txt
      wwi-times.txt
    title/               (Three.js Mycroft headline module — reused by all 3)
      MycroftTitle.ts
      shaders/
        ink-displacement.frag
        ink-displacement.vert
    paper/               (grain + fold overlay module)
      PaperOverlay.ts
    palette.ts           (color tokens)
    content.ts           (Mycroft product copy as structured data — reused by all 3)
  a-newspaper/
    index.html
    main.ts
    layout.ts            (PRetext-driven column layout + reflow on interaction)
  b-archives/
    index.html
    main.ts
    annotations.ts       (PRetext-driven annotation placement around archive text)
  c-transmission/
    index.html
    main.ts
    bridge.ts            (PRetext glyph measurement + scroll-driven morph)
```

## 6. Content corpus

### Archive corpus (background / source material)
Public domain late 19th / early 20th century journalism. Stored as plain text under `/prototypes/shared/corpus/`. Sources to fetch (Project Gutenberg / archive.org):
- Nellie Bly — *Ten Days in a Mad-House* (1887)
- Ida B. Wells — *Southern Horrors: Lynch Law in All Its Phases* (1892)
- Jacob Riis — *How the Other Half Lives* (1890)
- WWI dispatches from The Times of London (collected via archive.org)

Why this corpus: all libre de droits, esthétique journalistique d'époque parfaite, *literally* tells "the journalists of the past whom we bring into the future". Bly and Wells in the background of a Mycroft page is a strong narrative.

### Product copy (preserved verbatim from current `index.html`)
- Hero: "Your morning brief, before coffee / Your fact-check, in minutes / Your sources, kept private" + lede + CTAs + meta line
- Section "A day with Mycroft": 6 day-cards (7am Morning brief, 10am Fact-check, 2pm Investigate, 4pm Vault Q&A, Evening Newsletter, Ongoing Monitored beat)
- Section "A model trained on journalism": 4 cards (What it knows, Where it runs, What it costs, Why it matters)
- Section "Privacy by default": 6 items
- Section "Install in five minutes": 3-step list
- Section "Plugins": 4 cards (Spotlight, coJournalist, DataHound, Atelier)
- Section "From the team behind Mycroft": Pro Membership card + Consulting card
- CTA footer: "Built by journalists, for journalists."
- Site footer: existing copy

Each prototype must surface all of the above content, but the *presentation form* differs (article columns vs annotations vs bridged morph).

## 7. Prototype A — Living newspaper

### Concept
The page **is** a newspaper. Mycroft headline at the top (Three.js, blackletter, grainy ink). Below, a real front-page layout in true columns powered by PRetext. The product content is written *as articles of the front page*, not as cards.

### Sections → newspaper rubrics
- Hero → above-the-fold lead article ("Mycroft" as masthead title; the lede becomes the lead paragraph; "Set up Mycroft" / "View on GitHub" become call-out boxes inside the article)
- "A day with Mycroft" → 6 short articles arranged across columns, each timestamped (7am, 10am...) like a chronicle column
- "A model trained on journalism" → 4-column dossier ("Le modèle, en quatre temps")
- "Privacy by default" → numbered editorial / op-ed
- "Install in five minutes" → mode d'emploi en encart
- "Plugins" → "À paraître" rubric, with badges (at launch / May 2026)
- "From the team behind Mycroft" → tribune / encart abonnement
- CTA footer → bandeau de fin de journal

### Interaction signature: "the front page reorganizes as you read"
- At load, the page is composed and readable.
- Scroll, hover on a rubric, or click on a word triggers PRetext to **recompose** the layout in live: columns redistribute, an inset opens inline within the body text, a paragraph migrates to a different column.
- Always fluid, never frozen. Mycroft = a newspaper that lives with your reading.
- Justifies the cost of PRetext: CSS cannot do this — text reflow with insets and column rebalancing requires DOM-free measurement.

### Risk
Medium. PRetext fluid layout under interaction is its core use case — should be tractable. Main risk: animation between layout states (interpolation between two PRetext-computed layouts).

## 8. Prototype B — Archives that speak

### Concept
Editorial palimpsest. Background = a full archive page (Bly, Wells, Riis...) at low contrast, occupying the screen. Mycroft Three.js headline engraved over it. Product copy appears as **handwritten annotations** in margins, between lines, underlined, with arrows pointing to specific passages of the archive.

### Sections → annotated archive pages
Each section of the site = a different archive page in the background, with its own annotations rewriting:
- Hero → Bly *Mad-House* opening page; product hero copy as marginalia
- "A day with Mycroft" → Wells *Southern Horrors* page; the 6 day-cards as annotations clustered in time-of-day notes
- "A model trained on journalism" → Riis *Other Half* page; the 4 cards as analytical marginalia
- "Privacy by default" → WWI dispatch; the 6 items as cautious editor's notes
- "Install" → simpler archive (page de presse standard); steps as crayon checkmarks
- "Plugins", "Studio", CTA → continuation of the same logic

### Interaction signature: "the journalist who annotates"
- At each section, a new archive page slides into the background (slow cross-fade, no flash).
- Annotations write themselves on top, positioned in the *real* margins / interlines of the underlying archive (PRetext measures the archive layout to find empty spaces for annotations to land, never overlapping the archive text).
- Hover on an annotation: it gets emphasized; the archive passage it points to also subtly highlights, and an arrow appears.
- Scroll: annotations appear progressively, like a reader writing in real time.
- Mycroft = the contemporary journalist who reads the past and extracts method.

### PRetext role here
PRetext is used not for the product copy itself, but to **measure the archive's layout** so annotations land in real empty spaces (margins, interlines, blank ends of paragraphs). Without this, annotations would either overlap the archive (unreadable) or float in approximate positions (gimmick).

### Risk
Low to medium. Annotation placement around measured text is a clear PRetext use case. Risk: visual density — too many annotations on a small archive could be illegible. Mitigation: limit annotations per page, use clear hover affordance to surface details on demand.

## 9. Prototype C — The transmission

### Concept
The literal bridge. At the top of the page, you are in the past: a complete archive article (Bly or Wells), dense columns, blackletter, marked paper grain. At the bottom of the page, you are in the Mycroft product page, clean, contemporary, clear interface. **The same characters** of the archive deconstruct, migrate, and reassemble below as Mycroft interface elements (section titles, lists, buttons, copy). Scroll **is** the transmission. Mycroft = the bridge.

### Page structure
- Top viewport: archive page rendered in full (one of the corpus pieces), occupying the screen — this is the "past"
- Middle: a long scroll where the morphing happens. Characters from the archive lift off the page, drift, regroup, and land as product copy below. The Mycroft Three.js headline lives in this middle zone — it's literally the keystone of the bridge.
- Bottom viewport: Mycroft product page in its full clarity (hero, day-cards, etc.) — this is the "future"
- Sections of the product page (a day with, model, privacy, etc.) are reached by continuing to scroll past the bottom viewport — they exist in the "future" half, organized cleanly.

### Interaction signature: "scroll makes the bridge"
- PRetext measures every glyph of the archive and every glyph of the product copy (off-DOM, no reflow cost).
- At scroll progress 0: archive intact, product invisible.
- At scroll progress 0.3: archive starts losing characters (top characters lift off, drift downward toward the product zone).
- At scroll progress 0.5: peak migration — characters in transit, Mycroft headline in Three.js fully present in the middle.
- At scroll progress 0.7: product copy starts forming from arrived characters.
- At scroll progress 1.0: archive is gone, product copy is fully composed.
- Reverse scroll is symmetric: morph plays backward.

### PRetext role here
PRetext is **mission-critical**. The whole effect requires per-glyph layout knowledge of two distinct text layouts (archive + product) without DOM reflow. This is exactly what PRetext exists for, and exactly what CSS cannot do.

### Risk
High. Glyph-level animation across two different layouts is the most ambitious of the three. Specific concerns:
- Performance: thousands of glyphs animated each frame. Mitigation: WebGL/canvas rendering of the morphing layer (not DOM nodes), Three.js InstancedMesh for glyph instances.
- Mapping: which archive glyph becomes which product glyph? Strategy: by index up to length match; excess archive glyphs fade out; missing product glyphs fade in.
- Mobile: scroll-driven morph at 60fps on phones is tight. Mitigation: at narrow viewport, fall back to a simpler version (cross-fade between archive and product, no glyph morph). Document this fallback explicitly.

### Fallback
If the glyph-level morph proves infeasible after a focused spike (~1 day budget), fall back to: archive in top viewport, palimpseste cleaning during scroll (archive opacity fades while product copy rises through it), with a single residual archive fragment kept visible in the product zone as a signature trace. This is a less-ambitious version of the same metaphor, still distinct from A and B.

## 10. Comparison matrix

| | A — Living newspaper | B — Archives that speak | C — The transmission |
|---|---|---|---|
| Concept | The page IS a newspaper | Editorial palimpsest | Literal past→future bridge |
| Background | Front-page columns (PRetext) | Full archive page (low contrast) | Archive (top) → empty (bottom) |
| Mycroft Three.js | Masthead at top | Engraved over archive | Center, the keystone of the bridge |
| Product copy form | Articles in the front page | Handwritten annotations | Characters reassembled from archive |
| Interaction signature | Layout reorganizes on read | Annotations write themselves | Scroll morphs glyph-by-glyph |
| PRetext role | Fluid column reflow | Measure archive for annotation placement | Per-glyph measurement for morph |
| Technical risk | Medium | Low–medium | High |
| Creative risk | "Just a pretty newspaper" | Visual overload / illegibility | Magic trick that doesn't replay |

## 11. Build order

1. **Shared scaffolding first** — Bun + Vite project, Three.js title module, paper overlay module, fonts self-hosted, palette tokens, content corpus fetched, product copy structured. ~1 day.
2. **Spike on Prototype C** (highest technical risk) — validate that PRetext glyph morph is feasible at acceptable performance. If it fails, fall back to palimpseste-cleaning version of C. ~1 day.
3. **Prototype A** — newspaper layout with PRetext column reflow. ~1 day.
4. **Prototype B** — annotation placement around archive. ~1 day.
5. **Prototype C** finalization (or its fallback). ~0.5–1 day depending on spike result.
6. **Side-by-side review with client.** Kill 2, pick 1.
7. **Ship the winner** as new `index.html` (vanilla extraction or Vite migration — decision then).

Total: ~5–6 days of focused work for the 3 prototypes + comparison.

## 12. Accessibility & performance constraints

- All prototypes must respect `prefers-reduced-motion`. Specifically:
  - A: layout reorganization triggers become instant rather than animated; or disabled entirely with a static layout shown
  - B: annotations appear without sliding/handwriting animation
  - C: scroll morph is replaced by hard cross-fade between two static states
- Skip link, semantic landmarks, focus styles preserved across all prototypes
- Three.js headline must have a fallback `<h1>` with `aria-hidden` Three.js layered on top, so screen readers and noscript users get plain text
- Each prototype must remain readable on a 320px-wide viewport (mobile), with documented fallbacks where a desktop-only effect is degraded
- Total page weight target: <1 MB on first load (fonts subset, archive corpus chunked per section, Three.js title precomputed where possible)

## 13. Open questions (to revisit before build)

- **Signature glyph**: is there a single mark that should recur as Mycroft's punctuation across the page (like the scissor in the Purgatoire ref)? Could be the existing IM Fell M from the favicon, redrawn. To be decided before scaffolding.
- **PRetext packaging**: is `chenglou/pretext` published to npm or do we need to vendor it? To check at start of step 1.
- **Mobile strategy for C**: confirmed fallback is acceptable to client, or do we need a phone-specific reinvention of the transmission idea?

## 14. Out of scope (explicitly)

- Reworking `setup.html`
- Backend, recipes, agent extensions
- Rewriting product copy (only its presentation changes)
- Performance work beyond the targets in §12
- Internationalization beyond the current English-only state
