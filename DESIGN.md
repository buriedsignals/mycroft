---
version: alpha
name: Mycroft Vellum
description: Editorial design system for Mycroft — a Goose extension pack for investigative journalists. Parchment canvas, pigment ink, copper-oxide accent.

colors:
  # surface
  vellum: "#e8e0cf"
  vellum-2: "#dfd5be"
  vellum-bright: "#faf5e8"
  vellum-glow: "#fffcf0"
  pigment: "#131013"
  # ink
  primary: "#1a1a1f"
  ink-soft: "#4a4439"
  ink-dim: "#8e8676"
  on-surface: "#1a1a1f"
  # accent
  secondary: "#4a7363"
  secondary-active: "#2b5247"
  # structural
  rule: "#c8bfa8"
  surface: "#e8e0cf"

typography:
  brand:
    fontFamily: Migra
    fontSize: 32px
    fontWeight: 800
    lineHeight: 1
    letterSpacing: -0.02em
  display-xl:
    fontFamily: Migra
    fontSize: 108px
    fontWeight: 200
    lineHeight: 1
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Migra
    fontSize: 88px
    fontWeight: 200
    lineHeight: 1.05
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Migra
    fontSize: 56px
    fontWeight: 200
    lineHeight: 1.1
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Migra
    fontSize: 36px
    fontWeight: 200
    lineHeight: 1.15
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter Tight
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: Inter Tight
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.55
  body-sm:
    fontFamily: Inter Tight
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.55
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.22em
  label-button:
    fontFamily: Inter Tight
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1
  code:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5

rounded:
  none: 0px
  sm: 4px
  md: 4px
  pill: 999px
  full: 9999px

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 28px
  xl: 48px
  2xl: 64px
  3xl: 96px
  gutter: 32px
  shell-max: 1600px
  section-y: 160px
  reading-column: 50ch

components:
  brand:
    typography: "{typography.brand}"
    textColor: "{colors.primary}"
  button-primary:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.vellum}"
    rounded: "{rounded.pill}"
    height: 39px
    padding: 22px
    typography: "{typography.label-button}"
  button-primary-hover:
    backgroundColor: "{colors.secondary-active}"
    textColor: "{colors.vellum}"
  button-default:
    backgroundColor: transparent
    textColor: "{colors.primary}"
    rounded: "{rounded.pill}"
    height: 39px
    padding: 22px
    typography: "{typography.label-button}"
  button-default-hover:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.vellum}"
  button-ghost:
    backgroundColor: transparent
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.pill}"
    height: 39px
    padding: 12px
    typography: "{typography.label-button}"
  button-mono:
    typography: "{typography.label-mono}"
    rounded: "{rounded.pill}"
    height: 39px
    padding: 18px
  card:
    backgroundColor: "{colors.vellum-bright}"
    textColor: "{colors.primary}"
    rounded: "{rounded.sm}"
    padding: 28px
  hairline:
    backgroundColor: "{colors.rule}"
    height: 1px
  input:
    backgroundColor: "{colors.vellum-bright}"
    textColor: "{colors.primary}"
    rounded: "{rounded.sm}"
    padding: 12px
  selection:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.vellum}"
  focus-ring:
    backgroundColor: "{colors.secondary}"
---

# Mycroft Vellum

A design system for Mycroft, a Goose extension pack configured for investigative journalism. It treats the screen like a printed manuscript: warm parchment ground, dense pigment headlines, copper-oxide accents reserved for action. Editorial restraint over decoration. Calm, archival, evidence-first.

## Overview

Mycroft is software for journalists working on long, careful stories. The interface should feel like a well-bound notebook — confident typography, generous breathing room, and only as much chrome as the page actually needs. Information sits on warm vellum; structural lines are hairline-thin; the only saturated color is a dignified copper-green used for live links, focus, and the single most important action on a screen.

The voice is institutional but not corporate. Closer to a serious magazine masthead than a SaaS dashboard. Long-form readability is the default, and every interactive element is sized for deliberate use rather than rapid clicking.

## Colors

The palette is rooted in **parchment** (vellum) and **pigment** (deep ink), with a single accent — **oxide**, a desaturated copper-green that reads like aged metal on paper.

- **Vellum (`#e8e0cf`)** — the canvas. Default page background and the tone of "paper" across the system. Not white. Warm, slightly earthy.
- **Vellum-2 (`#dfd5be`)** — a deeper parchment used for tonal layering when one surface needs to recede behind another.
- **Vellum-bright (`#faf5e8`)** — for cards, modals, and inputs that sit *on top* of the canvas. Reads as "fresh paper" against the aged ground.
- **Vellum-glow (`#fffcf0`)** — the brightest tone, reserved for highlight states and small reveals (focus halos, current-step indicators).
- **Pigment (`#131013`)** — near-black with a faint plum tint. The deepest ink in the system; reserved for inverted dark sections.
- **Ink (`#1a1a1f`)** — primary text on vellum. Not pure black — it sits more comfortably on warm paper.
- **Ink-soft (`#4a4439`)** — long-form body, leads, secondary copy.
- **Ink-dim (`#8e8676`)** — metadata, timestamps, dimmed labels, hairline rules at small scale.
- **Oxide (`#4a7363`)** — the only accent. Used for the single primary action, live indicators, link underlines on dark backgrounds, focus rings, and selection. Treat it as scarce.
- **Oxide-active (`#2b5247`)** — pressed/active state for the primary action. Never used as a static color.
- **Rule (`#c8bfa8`)** — structural hairlines (1px borders, dividers, table rules). Always 1px, never thicker.

Pigment is reserved for whole-section inversions ("dark mode" in a single section) — when used, the canvas becomes pigment, text becomes vellum, and oxide stays oxide.

## Typography

Three families, each doing one job.

- **Migra** — the display serif. Used at extralight (200) for long, airy display headlines and at extrabold (800) italic for the brand mark. The 200 vs. 800 contrast carries the editorial feel; never use Migra at intermediate weights.
- **Inter Tight** — the working sans. Body copy, leads, button labels, navigation. Always 400 for body and 500 for labels.
- **JetBrains Mono** — for "marginalia": eyebrow labels, numerals, code, button-mono variants. Always uppercase with `letter-spacing: 0.22em` when used as a label.

Display headlines lean on Migra Extralight (200) at large sizes — the thinness is the point. Body sets in Inter Tight at 15–18px with line-height 1.55–1.6 for sustained reading. Mono is rare and structural — it labels regions, never paragraphs.

A `<code>` element inherits the size of its surrounding text and switches to JetBrains Mono at `0.92em` so inline code reads tight rather than oversized.

## Layout

A single shell, mobile-first, with three breakpoints: 600 / 980 / 1100px. The shell maxes at 1600px; the reading column stays at 50ch regardless. Sections breathe — vertical padding is `clamp(96px, 18vh, 200px)` at the top, slightly less at the bottom.

- **Spacing scale** (4px base, geometric-ish): 4, 8, 12, 16, 22, 28, 36, 48, 64, 96.
- **Gutter**: `clamp(20px, 4vw, 56px)` — the horizontal page padding.
- **Section padding-y**: `clamp(96px, 18vh, 200px)` top, `clamp(72px, 14vh, 160px)` bottom.
- **Header height**: 72px on mobile, 96px from 980px up.
- **Reading column**: 50ch — the line length the system optimizes around.
- **Headline column**: 16ch — display headlines wrap at this width to feel like a pull quote, not a banner.

Layout is a column-and-margin model, not a heavy grid. Most pages are one or two columns with hairline rules separating concerns. Tables and lists never get filled cells — alignment and whitespace do the structural work.

## Elevation & Depth

Mycroft is a **flat** system. There are no shadows. Depth comes from three sources only:

1. **Tonal layers** — vellum-bright cards on vellum, with no border or shadow.
2. **Hairline rules** — 1px solid `--rule` (or `1px dashed --rule` for "in-progress / coming" states).
3. **Color contrast** — pigment sections against vellum sections create the strongest depth in the system.

Never reach for `box-shadow`. If something needs to feel "above" something else, use a tonal step (vellum → vellum-bright) plus a hairline, or invert the section to pigment.

## Shapes

Two shape languages, paired deliberately.

- **Frames are sharp** — `border-radius: 0` for cards, sections, images, panels. The page reads like a printed layout, not a tile interface.
- **Affordances are pill** — buttons, chips, and pulses use `border-radius: 999px`. The contrast between sharp content frames and pill controls is the visual signature of the system.

Small affordances that aren't pills (form inputs, code blocks) use a 4px radius — present, but barely.

Decorative corner brackets (`.crn`) — 14px L-shapes at 1px and 55% opacity — mark editorial regions in lieu of full borders. They are decorative, not structural.

## Components

### Buttons

One height (39px), one radius (pill), three variants:

- **Solid** — oxide background, vellum text. Reserved for the single primary action on a view. Hover darkens to oxide-active.
- **Default (outline)** — transparent background, ink text, 1px ink border. Hover inverts to ink/vellum. The workhorse.
- **Ghost** — no border, ink-soft text, transparent background. For low-emphasis controls and header navigation.

A `--mono` modifier swaps the label to JetBrains Mono uppercase tracked at 0.22em — used for utility actions like "DOWNLOAD INSTALLER" where the label is the affordance.

Buttons can carry a trailing arrow (`.btn__arr`) that translates 4px right on hover. This is the only animated affordance in the button system.

### Cards

Vellum-bright background on vellum canvas, no border, no shadow, sharp corners (4px max). Internal structure is provided by an eyebrow (mono uppercase label), a serif title, body text, and a hairline-separated footer. Titles can use `<em>` for an italic Migra accent — used sparingly to mark emphasized concepts.

A `card--coming` variant uses `1px dashed --rule` and dims the eyebrow to ink-dim — the agreed visual for "not yet shipped."

### Eyebrow & numeral

Both are mono-uppercase 11px labels at 0.22em tracking, in ink-soft / ink-dim. The **eyebrow** prefixes a section with a 26px hairline. The **numeral** (`01 / 02 / 03`) prefixes a section with a small oxide-tinted index. These are the system's equivalent of a magazine's section dingbats.

### Lead

A sans paragraph at `clamp(15px, 1.15vw, 18px)` in ink-soft, capped at the 50ch reading column. Inline links carry a 1px ink-dim underline that strengthens to ink on hover — never blue, never oxide.

### Meta

Mono-uppercase metadata (timestamps, byline-style attributions) at 11px, 0.18em tracking, ink-dim. `<strong>` inside meta promotes to ink at weight 500, never 700.

### Dot

A 6px oxide circle used as a presence indicator. The `dot--pulse` variant emits a 2.4s `box-shadow` ring and is the only "live" animation in the system.

### Selection & focus

Text selection paints oxide / vellum. Keyboard focus is a 2px solid oxide outline at 2px offset with a 2px corner radius. Both are non-negotiable — they are the accessibility floor.

## Do's and Don'ts

- **Do** keep oxide scarce. One primary action per view. A page with two oxide buttons is a page with no primary action.
- **Don't** introduce a third color. The palette is vellum / ink / oxide, with tonal variants only. New accents go through a system change, not a one-off.
- **Do** trust the hairline. A 1px `--rule` border is enough — resist 2px, dashed-everywhere, or accent-tinted dividers.
- **Don't** add shadows, glows, or blur backdrops. The system is flat. If something needs to feel above, swap to vellum-bright and add a hairline.
- **Do** pair sharp frames with pill controls. The contrast is intentional.
- **Don't** mix radii within the same element family. All buttons are pills; all cards are sharp (or 4px). Never round one card and not its neighbor.
- **Do** use Migra Extralight at 200 for display, Extrabold (800) only for the brand mark. Intermediate weights are off-system.
- **Don't** set body copy in Migra. It is a display face — at 15–18px it loses its character and gets fragile.
- **Do** uppercase mono labels at 0.22em (or 0.18em for meta). Sentence-case mono looks like a code listing, not a label.
- **Don't** put oxide on body text or on hairlines. Oxide is for action and presence, not for decoration.
- **Do** maintain WCAG AA contrast — ink (#1a1a1f) on vellum (#e8e0cf) clears 4.5:1; ink-dim (#8e8676) on vellum is below AA and is reserved for non-essential metadata only.
- **Don't** narrow the reading column below 45ch or widen it past 60ch. 50ch is the target; long-form readability is a primary goal, not a "nice to have."
- **Do** invert whole sections to pigment when the content calls for it (install, footer). Never invert single elements — half-inverted UIs read as broken.
- **Don't** animate beyond the system's vocabulary: 180–900ms with `cubic-bezier(0.16, 1, 0.3, 1)`. No bouncing, no springs, no parallax outside the dedicated 3D hero stack.
