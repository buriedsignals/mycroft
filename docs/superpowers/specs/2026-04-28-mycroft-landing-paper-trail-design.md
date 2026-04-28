---
title: Mycroft landing redesign — "The Paper Trail"
date: 2026-04-28
status: design
target: prototypes/proto-13/index.html
---

# Mycroft landing redesign — "The Paper Trail"

## Goal

Redesign the Mycroft landing page (`/index.html`) using the Cellora reference layout (light, editorial, photo-card driven) adapted to Mycroft's product (AI for investigative journalism). Output is a self-contained prototype at `prototypes/proto-13/index.html`. Existing copy is preserved; visuals and structure are remade.

## Core concept

A single Three.js scene of newspaper-paper particles persists across the entire page and **morphs at each section** into a different formation that visually expresses what Mycroft does in that section. The particles are not decoration — they are the product's substrate (information). The hero is `proto-02` intact (sphere dispersing). Subsequent sections re-target the same ~900 particles into new formations.

## Constraints

- Vanilla single-file HTML (matches `index.html` and `proto-02` style). No framework, no bundler.
- Three.js via `esm.sh` import map (same import map as `proto-02`).
- Strict Cellora-light palette (cream, moss, ink). No red stamp accent.
- Existing Mycroft copy is preserved verbatim from `/index.html`. Only structure and visual language change.
- `prefers-reduced-motion`: scene snaps to each section's pose without morph; no continuous animation.
- Falls back gracefully without JS: HTML/CSS layout is readable; canvas is purely visual augmentation.
- Keep `proto-02/index.html` untouched. Don't read or import other prototypes.

## Palette (CSS custom properties)

```css
--bg: #f3eddf;        /* cream — same as proto-02 background */
--bg-2: #ece1ca;      /* warm card */
--paper-top: #ece1ca;
--paper-bot: #ddd0b3;
--ink: #1a1612;       /* near-black, warm */
--ink-muted: #5d5648; /* muted brown-gray for body */
--moss: #2e3d1f;      /* deep moss green — primary CTA, dark section bg */
--moss-2: #5d6b3a;    /* mid moss — accents, active states */
--moss-light: #c4cfa6;/* tint — hover, soft fills */
--border: #d8cdb1;
--radius: 8px;
--radius-lg: 16px;
```

Typography:
- Headings: `IM Fell English` (already loaded), used at large display sizes for the brand name and the "Cellora-style" massive bottom mark. Body headings use a clean sans (system stack) for readability.
- Body: system sans (matches current `index.html`).
- Eyebrows: small caps, letter-spaced, `--ink-muted`.

## Layout (Cellora structure adapted)

In order:

1. **Hero** — full-viewport. Top nav (logo left, primary nav + "Set up" CTA right). Eyebrow "AI for investigative journalism". H1 three-line tagline (existing copy). Small pill button "Set up Mycroft" + ghost "View on GitHub". Floating stat-card overlay near bottom-center with two stats: "~$6/month" and "Zero data retention". Massive "Mycroft" brand name in IM Fell English serif anchored to bottom edge of viewport, formed by particles settling into letterforms (the hero scene's terminal pose).
2. **Logo strip** — horizontal row of small client/partner logos (Le Temps, MAZ Journalistenschule, Republik, 20 Minuten, MediaStorm, The New Humanitarian — sourced from existing copy). Faint, monochrome.
3. **Intro paragraph** (replaces Cellora's moss bioindicator block) — short centered paragraph: *"Most AI tools are generalists. Mycroft is opinionated. It runs on open-weight models, keeps your sources on disk, and is built specifically for investigative methodology."* Two small icon-cards under it: "Open-weight, auditable" and "Zero retention by default".
4. **A day with Mycroft** (dark section, replaces Cellora's "Built for Researchers" dark block) — `--moss` background. Four numbered items (01–04): Morning brief / Fact-check / Investigate / Vault Q&A. Active item highlighted; on the right, a single large paper that "flips" to show content matching the active item (replaces Cellora's photo of a moss-covered rock).
5. **Plugins** (replaces Cellora's "Where Moss Analysis Makes an Impact" 2×2 photo grid) — header "What ships with Mycroft". Four photo-style cards: Spotlight / coJournalist / DataHound / Atelier. Each card has a label "at launch" or "May 2026". Each card hosts a small particle micro-behavior (described below).
6. **Pricing / mode** (replaces Cellora's "Choose the Right Plan") — 3 tabs: *Cloud (~$6/mo)* / *Local ($0)* / *Pro Membership ($25/mo)*. Active tab shows a card with the price big, key bullets, primary CTA. Right side has a paper visual (calmer particles in card form).
7. **Privacy by default** (replaces Cellora's mobile-mockup section) — two-column. Left: section heading + lede. Right: a "vault" visual (particles inside a frosted-glass cube, blurred, anti-interactive). Below: 2×3 grid of privacy bullets (existing copy preserved).
8. **Trusted by** (replaces Cellora's testimonials block) — 3 short testimonial cards. (Placeholder copy if no real testimonials available; flagged in the implementation plan.)
9. **From the team behind Mycroft** (Studio block — preserved from current `index.html`) — two-column: Pro Membership card (with email signup form, existing handler preserved) + Consulting card.
10. **Final CTA** (replaces Cellora's "Start Analyzing Moss the Smart Way") — centered "Built by journalists, for journalists." + 2 CTAs.
11. **Footer** — 4-column links (replicates Cellora's footer structure: Documentation / Resources / Company), with the giant "Mycroft" brand name spanning the bottom edge, half-buried in a pile of accumulated particles.

## Particle scene — state machine

A single `<canvas>` is `position: fixed`, full viewport, `pointer-events: none` except during the hero. ~900 particles persist for the whole page, identical to `proto-02`.

Section ↔ pose mapping. The current pose is determined by which section has the largest visible area (IntersectionObserver with `threshold: [0, 0.25, 0.5, 0.75, 1]`). On change, particles smoothly tween to the new target positions over ~1.2s using `MathUtils.damp` per particle (eased, staggered ±0.3s by `particle.id` for organic feel).

Poses:

- **Hero (proto-02 verbatim)**: receipt-cluster sphere, controls enabled, mouse repulsion enabled. End pose at scroll-out: particles settle into the letterforms of "Mycroft" along the bottom edge (offline-baked target positions sampled from rasterizing the brand SVG into points).
- **Day with Mycroft**: clock arrangement. Particles cluster into 4 zones around a horizontal arc (one per numbered item), tighter cluster on the active item. As the user clicks 01–04, the camera nudges and the active cluster gains density.
- **Plugins**: particles split into 4 orbits, one anchored to each plugin card's center (computed from DOM rect → projected NDC → world coordinates). Each orbit has its own behavior:
  - *Spotlight*: a thin emissive line sweeps left→right across its cluster every 3s
  - *coJournalist*: cluster pulses (radial scale 0.92 ↔ 1.0) every 4s — a "tick"
  - *DataHound*: cluster forms a vertical stack, growing one paper every 200ms up to 30, then resets
  - *Atelier*: cluster cycles through 3 silhouettes (chart-bar / map-pin / card) over 6s, lerping between sampled point sets
- **Pricing**: a single calm cluster on the right of the section, gentle drift, no interaction.
- **Privacy**: cluster contained inside an invisible cube of side 1.6 at the right side. A blurred CSS `backdrop-filter: blur(14px)` rectangle is layered ON TOP of the canvas in this region — the papers stay 3D but look frosted from the user's perspective. Mouse repulsion is disabled here.
- **Trusted by / Studio / Final CTA**: low-density background drift, papers float slowly upward across the viewport at ~0.05 units/s.
- **Footer**: gravity flips. Papers fall and accumulate at the bottom edge, settling into a horizontal pile. The giant "Mycroft" brand name SVG is set behind the pile — papers naturally bury its lower half.

Implementation notes:
- Pose transitions = lerp current particle position toward target position; targets are stored per-particle per-pose in `Float32Array` buffers.
- Targets for letter-form / silhouette poses are precomputed once at load by rasterizing reference SVGs to a temporary 2D canvas and sampling N=900 points by rejection sampling on alpha.
- Pose 1 (hero) keeps the `proto-02` physics; subsequent poses replace physics with target-following (no inter-particle collision after hero).
- `requestAnimationFrame` runs while any pose is animating or the hero is active; otherwise the loop pauses to save CPU/battery.

## Cursor & button micro-interactions

- Within the hero only: cursor casts the mouse-driven repulsion (same as `proto-02`).
- Outside the hero: cursor leaves no trail (kept simple; YAGNI for the "puff" effect).
- Buttons (`btn.primary`, `btn.secondary`): on click, emit 5 small DOM-based `<span>` papers from the click point that translate upward 60–100px and fade out over 700ms (CSS-only, no Three.js, ~30 LOC).

## Accessibility

- All text passes WCAG AA contrast on cream (verify `--ink-muted` ≥ 4.5:1 on `--bg`).
- The canvas is `aria-hidden="true"`. All meaning is in the DOM.
- `prefers-reduced-motion`:
  - No morph between poses; particles snap to each section's target.
  - Button paper bursts disabled.
  - Hero scene: rotation paused, dispersion held; mouse repulsion disabled.
- Keyboard navigation works fully without canvas interaction.
- Focus rings preserved on all interactive elements.

## Performance budget

- ≤900 particles total (matches `proto-02`).
- One canvas, one render loop, paused when off-screen / on settled poses.
- `pixelRatio` capped at 1.5.
- Pose target arrays precomputed; per-frame work is `O(N)` lerp + draw call.
- Mobile / low-core: 600 particles (same heuristic as `proto-02`).
- First paint must not block on scene init. Canvas mounts and runs after `DOMContentLoaded`; HTML is fully readable before then.

## File structure

```
prototypes/proto-13/
  index.html         — single file, all HTML + CSS + JS inline
```

No build step. Open via `python3 -m http.server 5180` (same convention as `proto-02`).

## Out of scope

- Replacing `/index.html` itself — this is a prototype; a separate decision later moves it to root.
- Real testimonial copy — placeholder for now, marked.
- New illustrations / photographs — Cellora uses photo cards heavily; we replace those slots with paper-particle scenes, not stock photography.
- A separate Atelier / DataHound product page.
- Dark mode (Cellora reference is light-only; we follow).
- Mobile micro-interactions for the canvas — on small screens we degrade to the static end-pose of each section (no morph) and keep the hero scene only.

## Open questions for review

1. Logo strip: confirm using the consulting client list (Le Temps, MAZ, Republik, 20 Minuten, MediaStorm, The New Humanitarian) — these are not necessarily Mycroft users; might be misleading. Alternative: drop the logo strip or relabel as "Workshops & collaborations".
2. Pricing tab section: the existing site doesn't have a 3-tier pricing table — it has a single "$6/mo" mention and the studio Pro Membership at $25/mo. Should we (a) build a true 3-tier comparison including Local/$0, Cloud/$6, Pro/$25, or (b) keep it leaner with just two cards and skip the Cellora-style tab pattern?
3. "Trusted by" section: do we have any real journalist testimonials usable now, or is this a placeholder section to fill before publish?

These are tagged for the implementation plan to resolve before scaffolding.
