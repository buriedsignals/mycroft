# Mycroft Landing — "Paper Trail" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `prototypes/proto-13/index.html`: a single-file Cellora-styled landing prototype for Mycroft, with a persistent Three.js paper-particle scene that morphs across sections.

**Architecture:** Vanilla single-file HTML/CSS/JS, no bundler. Three.js loaded via `esm.sh` import map (matches `proto-02`). One fixed full-viewport `<canvas>` runs a state machine driven by an `IntersectionObserver`; ~900 particles persist for the whole page and lerp toward per-section target arrays. HTML/CSS layout is fully readable without JS; canvas is purely visual augmentation.

**Tech Stack:** Three.js 0.162.0 (esm.sh), lil-gui (dev only, removed in final), IM Fell English webfont (Google Fonts), system sans, vanilla CSS custom properties.

**Reference files (read-only context, do not modify):**
- `prototypes/proto-02/index.html` — receipt-cluster scene; we port physics + add poses
- `index.html` — source of truth for copy; preserve verbatim
- `docs/superpowers/specs/2026-04-28-mycroft-landing-paper-trail-design.md` — design

**Do NOT read other prototypes (proto-03..proto-12).** The user explicitly excluded them.

---

## Resolved Decisions

| Question | Decision |
|---|---|
| Logo strip content | Relabel "Workshops & collaborations" — Le Temps · MAZ Journalistenschule · Republik · 20 Minuten · MediaStorm · The New Humanitarian (sourced from current index.html studio block). |
| Pricing section | 2 tabs only: Cloud (~$6/mo) and Local ($0). Pro Membership stays in the Studio block; do not duplicate. |
| Trusted-by testimonials | 3 placeholder cards with `data-placeholder="true"` + HTML comment `<!-- TODO before publish: replace with real testimonials -->`. Visible "[placeholder]" caption in dev mode. |

---

## File Structure

```
prototypes/proto-13/
  index.html             — single file, all HTML + CSS + JS inline
```

Layout map within `index.html` (in order):
1. `<head>` — meta, fonts, CSP, palette CSS vars, full stylesheet
2. `<body>` skip-link
3. `<header class="site">` — sticky nav: brand mark left, links + CTA right
4. `<canvas id="paper-canvas">` — fixed, full-viewport, behind content (`z-index: 0`)
5. `<main>` — sections in order:
   - `#hero` (full-viewport)
   - `#workshops` (logo strip)
   - `#intro` (paragraph + 2 icon cards)
   - `#day` (dark moss section, numbered list 01-04)
   - `#plugins` (4 cards with particle micro-zones)
   - `#pricing` (2 tabs)
   - `#privacy` (frosted vault + bullet grid)
   - `#trusted` (3 testimonial cards)
   - `#studio` (Pro Membership + Consulting — port from current)
   - `#cta` (final CTA)
6. `<footer class="site">` — 4-column links + giant brand mark over particle pile
7. `<script type="importmap">` — Three.js import map
8. `<script type="module">` — scene + state machine + signup form handler

---

## Verification Approach

This is a vanilla HTML prototype — there is no test runner. "Tests" are visual + console verifications run after each task:

- **`bun run`-equivalent**: `cd prototypes/proto-13 && python3 -m http.server 5180`, then `open http://localhost:5180/`.
- **No-JS check**: open with JS disabled in DevTools → all sections must be readable, no broken layout.
- **Reduced-motion check**: macOS System Settings → Accessibility → Display → Reduce motion ON, reload, verify no morph animation.
- **Console**: zero errors, zero warnings (except expected font-loading info).
- **Browser-use validation**: the user's CLAUDE.md mandates browser-use CLI for web tests before reporting completion. Each task that produces visible output ends with a browser-use check capturing a screenshot + console log.

Browser-use invocation pattern (used in verification steps below):
```
bunx browser-use --url http://localhost:5180/ --task "Take a full-page screenshot. Report any console errors. Describe what is visible in section <id>."
```

---

# PHASE A — Static HTML/CSS shell (Tasks 1–10)

## Task 1: Scaffold proto-13 directory and base document

**Files:**
- Create: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Create the directory.

```bash
mkdir -p prototypes/proto-13
```

- [ ] **Step 2:** Write the base document (head + skeleton body, no sections yet, palette CSS vars, IM Fell English font, CSP).

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mycroft — AI for investigative journalism</title>
<meta name="description" content="An opinionated AI assistant for investigative journalists. Open-weight models, zero data retention, local-capable, ~$6/month.">
<meta name="theme-color" content="#f3eddf">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; script-src 'self' 'unsafe-inline' https://esm.sh; connect-src 'self' https://esm.sh; base-uri 'self'; form-action 'self'; frame-ancestors 'none'">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #f3eddf;
  --bg-2: #ece1ca;
  --paper-top: #ece1ca;
  --paper-bot: #ddd0b3;
  --ink: #1a1612;
  --ink-muted: #5d5648;
  --moss: #2e3d1f;
  --moss-2: #5d6b3a;
  --moss-light: #c4cfa6;
  --border: #d8cdb1;
  --radius: 8px;
  --radius-lg: 16px;
  --serif: 'IM Fell English', 'Libre Caslon Text', 'Hoefler Text', Georgia, serif;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
* { box-sizing: border-box; }
html { font-size: 16px; scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } * { transition: none !important; animation: none !important; } }
body { font-family: var(--sans); margin: 0; background: var(--bg); color: var(--ink); line-height: 1.55; -webkit-font-smoothing: antialiased; }
a { color: var(--moss); text-decoration: none; }
a:hover, a:focus-visible { text-decoration: underline; }
:focus-visible { outline: 2px solid var(--moss); outline-offset: 2px; }
.skip { position: absolute; top: -40px; left: 0; background: var(--ink); color: var(--bg); padding: .5rem 1rem; z-index: 100; }
.skip:focus { top: 0; }
canvas#paper-canvas { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
main, header.site, footer.site { position: relative; z-index: 1; }
</style>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<canvas id="paper-canvas" aria-hidden="true"></canvas>
<header class="site"><!-- task 2 --></header>
<main id="main"><!-- tasks 3-12 --></main>
<footer class="site"><!-- task 13 --></footer>
<script type="importmap">
{ "imports": { "three": "https://esm.sh/three@0.162.0", "three/addons/": "https://esm.sh/three@0.162.0/examples/jsm/" } }
</script>
<script type="module">
// scene module — populated in Phase B
</script>
</body>
</html>
```

- [ ] **Step 3:** Start the dev server.

```bash
cd prototypes/proto-13 && python3 -m http.server 5180 &
```

- [ ] **Step 4:** Verify in browser.

Open `http://localhost:5180/`. Expected: blank cream page, no console errors.

- [ ] **Step 5:** Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): scaffold base document with palette and CSP"
```

---

## Task 2: Top navigation header

**Files:**
- Modify: `prototypes/proto-13/index.html` (replace `<header class="site">` placeholder, add styles to `<style>`)

- [ ] **Step 1:** Add header CSS to the stylesheet.

```css
header.site { padding: 1.25rem 0; }
header.site .wrap { max-width: 1240px; margin: 0 auto; padding: 0 2rem; display: flex; align-items: center; justify-content: space-between; }
header.site a.brand { color: var(--ink); display: inline-flex; align-items: center; line-height: 0; }
header.site a.brand svg { height: 1.6rem; width: auto; display: block; }
header.site nav { display: flex; gap: 1.75rem; align-items: center; }
header.site nav a { color: var(--ink-muted); font-size: .9rem; font-weight: 500; }
header.site nav a:hover { color: var(--ink); text-decoration: none; }
header.site nav a.cta { background: var(--ink); color: var(--bg); padding: .5rem 1rem; border-radius: 999px; font-weight: 600; }
header.site nav a.cta:hover { background: var(--moss); }
@media (max-width: 720px) { header.site nav a:not(.cta) { display: none; } }
```

- [ ] **Step 2:** Replace the header placeholder.

```html
<header class="site" role="banner">
  <div class="wrap">
    <a class="brand" href="#" aria-label="Mycroft — home">
      <svg viewBox="0 0 320 60" fill="currentColor" aria-hidden="true">
        <text x="0" y="46" font-family="IM Fell English, serif" font-size="48" letter-spacing="0.005em">Mycroft</text>
      </svg>
    </a>
    <nav aria-label="Primary">
      <a href="#day">A day with Mycroft</a>
      <a href="#plugins">Plugins</a>
      <a href="#privacy">Privacy</a>
      <a href="#pricing">Pricing</a>
      <a href="../../setup.html" class="cta">Set up</a>
    </nav>
  </div>
</header>
```

- [ ] **Step 3:** Reload and verify. Expected: serif brand mark left, 4 nav links + dark pill CTA right; sticky-feel layout.

- [ ] **Step 4:** Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): top navigation header"
```

---

## Task 3: Hero section (HTML + CSS only — particle canvas hooks come in Phase B)

**Files:**
- Modify: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Add hero CSS.

```css
.hero {
  min-height: calc(100vh - 100px);
  padding: 3rem 0 2rem;
  position: relative;
  display: flex; flex-direction: column; justify-content: flex-start;
}
.hero .wrap { max-width: 1240px; margin: 0 auto; padding: 0 2rem; flex: 1; display: flex; flex-direction: column; }
.hero .eyebrow { font-size: .82rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-muted); font-weight: 600; margin: 0 0 1.5rem; }
.hero h1 {
  font-family: var(--sans);
  font-size: clamp(2.4rem, 5vw, 4rem);
  line-height: 1.05;
  letter-spacing: -.02em;
  font-weight: 600;
  margin: 0 0 1.25rem;
  max-width: 22ch;
}
.hero h1 em { font-style: normal; color: var(--moss); }
.hero .lede { font-size: 1.05rem; color: var(--ink-muted); max-width: 36rem; margin: 0 0 2rem; }
.hero .ctas { display: flex; flex-wrap: wrap; gap: .75rem; }
.btn { display: inline-flex; align-items: center; gap: .5rem; padding: .8rem 1.4rem; border-radius: 999px; font-weight: 600; font-size: .95rem; border: 1px solid transparent; cursor: pointer; text-decoration: none; transition: background-color .15s ease, color .15s ease, border-color .15s ease; }
.btn.primary { background: var(--moss); color: var(--bg); }
.btn.primary:hover { background: var(--ink); text-decoration: none; }
.btn.secondary { background: transparent; color: var(--ink); border-color: var(--ink); }
.btn.secondary:hover { background: var(--ink); color: var(--bg); text-decoration: none; }
.hero .stat-card {
  align-self: center;
  margin-top: auto;
  background: rgba(255,255,255,.7);
  backdrop-filter: blur(8px);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 2rem;
  display: flex; gap: 3rem;
  box-shadow: 0 8px 30px rgba(26, 22, 18, 0.08);
}
.hero .stat-card .stat strong { display: block; font-size: 1.6rem; font-weight: 700; color: var(--ink); letter-spacing: -.01em; }
.hero .stat-card .stat span { font-size: .82rem; color: var(--ink-muted); }
.hero .brand-mark {
  font-family: var(--serif);
  font-size: clamp(7rem, 22vw, 18rem);
  line-height: .85;
  color: var(--ink);
  letter-spacing: -.02em;
  margin: 1.5rem 0 0;
  align-self: stretch;
  text-align: center;
  pointer-events: none;
  user-select: none;
  /* will be hidden / revealed by particle scene in Phase C */
}
@media (max-width: 720px) { .hero .stat-card { flex-direction: column; gap: 1rem; padding: 1rem 1.25rem; } }
```

- [ ] **Step 2:** Add hero HTML inside `<main id="main">`.

```html
<section class="hero" aria-labelledby="hero-h" id="hero">
  <div class="wrap">
    <p class="eyebrow">AI for investigative journalism</p>
    <h1 id="hero-h">Your morning brief, before coffee.<br>Your fact-check, in minutes.<br>Your sources, <em>kept private</em>.</h1>
    <p class="lede">Mycroft is an opinionated extension pack for Goose — the open-source agent runtime. Daily digests from your beat, SIFT fact-checking, vault Q&amp;A with citations, investigations via Spotlight.</p>
    <div class="ctas">
      <a class="btn primary" href="../../setup.html">Set up Mycroft</a>
      <a class="btn secondary" href="https://github.com/buriedsignals/mycroft" target="_blank" rel="noreferrer">View on GitHub</a>
    </div>
    <div class="stat-card" role="group" aria-label="Mycroft at a glance">
      <div class="stat"><strong>~$6/mo</strong><span>moderate use · $0 local</span></div>
      <div class="stat"><strong>0 retention</strong><span>by default, all providers</span></div>
    </div>
  </div>
  <div class="brand-mark" aria-hidden="true">Mycroft</div>
</section>
```

- [ ] **Step 3:** Reload. Expected: hero fills viewport, big tagline left, stat card centered low, massive serif "Mycroft" at the bottom edge. No console errors.

- [ ] **Step 4:** Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): hero section static layout"
```

---

## Task 4: Workshops & collaborations strip (logo row)

**Files:**
- Modify: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Add CSS.

```css
.workshops { padding: 2.5rem 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.workshops .wrap { max-width: 1240px; margin: 0 auto; padding: 0 2rem; display: flex; flex-direction: column; align-items: center; gap: 1.25rem; }
.workshops .label { font-size: .76rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-muted); }
.workshops ul { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 2.5rem; justify-content: center; align-items: center; }
.workshops ul li { font-family: var(--serif); font-size: 1.2rem; color: var(--ink-muted); opacity: .7; transition: opacity .15s ease; }
.workshops ul li:hover { opacity: 1; }
@media (max-width: 720px) { .workshops ul { gap: 1.25rem; } .workshops ul li { font-size: 1rem; } }
```

- [ ] **Step 2:** Add HTML inside `<main>`, after the hero.

```html
<section class="workshops" aria-labelledby="workshops-h">
  <div class="wrap">
    <p class="label" id="workshops-h">Workshops &amp; collaborations</p>
    <ul>
      <li>Le Temps</li>
      <li>MAZ Journalistenschule</li>
      <li>Republik</li>
      <li>20 Minuten</li>
      <li>MediaStorm</li>
      <li>The New Humanitarian</li>
    </ul>
  </div>
</section>
```

- [ ] **Step 3:** Reload. Expected: thin horizontal strip with serif client names. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): workshops & collaborations strip"
```

---

## Task 5: Intro paragraph + two icon cards

**Files:**
- Modify: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Add CSS.

```css
.intro { padding: 5rem 0 4rem; }
.intro .wrap { max-width: 760px; margin: 0 auto; padding: 0 2rem; text-align: center; }
.intro .eyebrow { font-size: .76rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-muted); font-weight: 600; margin: 0 0 1.25rem; }
.intro p.body { font-size: 1.1rem; line-height: 1.65; color: var(--ink); margin: 0 0 2.5rem; }
.intro p.body em { font-style: italic; color: var(--moss); }
.intro .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; max-width: 580px; margin: 0 auto; }
.intro .pair .icon-card { background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.25rem; display: flex; flex-direction: column; align-items: center; gap: .5rem; }
.intro .pair .icon-card .glyph { width: 44px; height: 44px; border-radius: 50%; background: var(--moss); color: var(--bg); display: flex; align-items: center; justify-content: center; font-family: var(--serif); font-size: 1.3rem; }
.intro .pair .icon-card strong { font-size: .9rem; font-weight: 700; }
.intro .pair .icon-card span { font-size: .82rem; color: var(--ink-muted); text-align: center; }
@media (max-width: 600px) { .intro .pair { grid-template-columns: 1fr; } }
```

- [ ] **Step 2:** Add HTML.

```html
<section class="intro" aria-labelledby="intro-h">
  <div class="wrap">
    <p class="eyebrow" id="intro-h">About Mycroft</p>
    <p class="body">Most AI tools are generalists — chatbots trained to be agreeable. Mycroft is opinionated. It runs on <em>open-weight models</em>, keeps your sources on disk, and is built specifically for investigative methodology.</p>
    <div class="pair">
      <div class="icon-card"><div class="glyph">⌖</div><strong>Open-weight, auditable</strong><span>Yours to download, audit, run forever</span></div>
      <div class="icon-card"><div class="glyph">⊘</div><strong>Zero retention by default</strong><span>ZDR providers only, local mode optional</span></div>
    </div>
  </div>
</section>
```

- [ ] **Step 3:** Reload, verify centered paragraph + 2 cards below. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): intro paragraph and feature pair"
```

---

## Task 6: "A day with Mycroft" — dark moss section with numbered list

**Files:**
- Modify: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Add CSS.

```css
.day { background: var(--moss); color: var(--bg); padding: 5rem 0; border-radius: var(--radius-lg); margin: 0 1.5rem; }
.day .wrap { max-width: 1180px; margin: 0 auto; padding: 0 2.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
.day h2 { font-family: var(--sans); font-size: clamp(1.8rem, 3vw, 2.4rem); line-height: 1.15; margin: 0 0 2rem; font-weight: 600; letter-spacing: -.01em; }
.day ol { list-style: none; padding: 0; margin: 0; }
.day ol li { display: grid; grid-template-columns: auto 1fr auto; gap: 1.25rem; align-items: center; padding: 1.1rem 1rem; border-bottom: 1px solid rgba(255,255,255,.12); cursor: pointer; transition: background-color .2s ease; }
.day ol li:last-child { border-bottom: none; }
.day ol li[aria-current="true"] { background: rgba(255,255,255,.06); border-radius: var(--radius); }
.day ol li .num { font-family: var(--serif); font-size: 1rem; color: rgba(255,255,255,.55); width: 2ch; }
.day ol li[aria-current="true"] .num { color: var(--moss-light); }
.day ol li .title { font-size: 1.05rem; font-weight: 500; }
.day ol li .arrow { width: 28px; height: 28px; border-radius: 50%; background: var(--moss-light); color: var(--moss); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity .2s ease; }
.day ol li[aria-current="true"] .arrow { opacity: 1; }
.day .paper-zone { aspect-ratio: 1; border-radius: var(--radius-lg); position: relative; min-height: 320px; }
.day .paper-zone .paper-text { position: absolute; inset: 1.5rem; background: var(--bg); color: var(--ink); border-radius: var(--radius); padding: 1.5rem; box-shadow: 0 30px 60px rgba(0,0,0,.3); }
.day .paper-zone .paper-text h3 { margin: 0 0 .5rem; font-size: 1.1rem; font-family: var(--sans); }
.day .paper-zone .paper-text p { margin: 0; font-size: .92rem; color: var(--ink-muted); line-height: 1.55; }
@media (max-width: 900px) { .day { margin: 0; border-radius: 0; } .day .wrap { grid-template-columns: 1fr; gap: 2rem; padding: 0 1.5rem; } .day .paper-zone { min-height: 240px; } }
```

- [ ] **Step 2:** Add HTML.

```html
<section class="day" id="day" aria-labelledby="day-h">
  <div class="wrap">
    <div>
      <p class="eyebrow" style="color: var(--moss-light); margin: 0 0 1rem;">Built for journalists, powered by AI</p>
      <h2 id="day-h">A day with Mycroft</h2>
      <ol id="day-list">
        <li data-day="brief" aria-current="true"><span class="num">01.</span><span class="title">Morning brief — 7am</span><span class="arrow" aria-hidden="true">→</span></li>
        <li data-day="factcheck"><span class="num">02.</span><span class="title">Fact-check a draft — 10am</span><span class="arrow" aria-hidden="true">→</span></li>
        <li data-day="investigate"><span class="num">03.</span><span class="title">Investigate a lead — 2pm</span><span class="arrow" aria-hidden="true">→</span></li>
        <li data-day="vault"><span class="num">04.</span><span class="title">Vault Q&amp;A — 4pm</span><span class="arrow" aria-hidden="true">→</span></li>
      </ol>
    </div>
    <div class="paper-zone" id="day-paper-zone">
      <div class="paper-text" id="day-paper-text">
        <h3>Morning brief</h3>
        <p>Open your laptop. A digest is in your vault: 8 items ranked by editorial value, pulled from your X bookmarks, AgentMail newsletters, and overnight web coverage. Every claim cited.</p>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 3:** Add the click handler in the existing `<script type="module">` block (just append, no scene yet).

```js
const DAY_CONTENT = {
  brief: { title: 'Morning brief', body: 'Open your laptop. A digest is in your vault: 8 items ranked by editorial value, pulled from your X bookmarks, AgentMail newsletters, and overnight web coverage. Every claim cited.' },
  factcheck: { title: 'Fact-check a draft', body: 'Run fact-check on an article draft. Mycroft returns per-claim verdicts — verified, unverified, contradicted — via SIFT methodology. Every quote traced to origin.' },
  investigate: { title: 'Investigate a lead', body: 'Spotlight takes over: multi-phase OSINT research, adversarial SIFT fact-checking, evidence grounding, knowledge-vault ingestion. Full audit trail for editorial defensibility.' },
  vault: { title: 'Vault Q&A', body: '"What do I already have on this topic?" Mycroft answers from your own notes + live web in a single shot, with every claim cited to a vault path or URL.' },
};
const dayList = document.getElementById('day-list');
const dayText = document.getElementById('day-paper-text');
dayList?.addEventListener('click', (e) => {
  const li = e.target.closest('li[data-day]');
  if (!li) return;
  dayList.querySelectorAll('li').forEach(el => el.setAttribute('aria-current', 'false'));
  li.setAttribute('aria-current', 'true');
  const c = DAY_CONTENT[li.dataset.day];
  if (c) dayText.innerHTML = `<h3>${c.title}</h3><p>${c.body}</p>`;
});
```

- [ ] **Step 4:** Reload, click items 01-04, verify the paper text updates and the active-state visual transitions. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): A day with Mycroft section + interaction"
```

---

## Task 7: Plugins grid (4 cards)

**Files:**
- Modify: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Add CSS.

```css
.plugins { padding: 6rem 0 4rem; }
.plugins .wrap { max-width: 1180px; margin: 0 auto; padding: 0 2rem; }
.plugins .head { text-align: center; margin: 0 0 3rem; }
.plugins .head .eyebrow { font-size: .76rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-muted); font-weight: 600; margin: 0 0 .75rem; }
.plugins h2 { font-family: var(--sans); font-size: clamp(1.8rem, 3vw, 2.4rem); margin: 0; font-weight: 600; letter-spacing: -.01em; }
.plugins-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.25rem; }
.plugin-card { background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 0; overflow: hidden; display: flex; flex-direction: column; }
.plugin-card .visual { aspect-ratio: 4 / 3; background: var(--paper-top); position: relative; border-bottom: 1px solid var(--border); }
.plugin-card .body { padding: 1.25rem 1.5rem 1.5rem; display: flex; flex-direction: column; gap: .35rem; }
.plugin-card .badges { display: flex; justify-content: space-between; font-size: .78rem; color: var(--ink-muted); margin-bottom: .25rem; }
.plugin-card .badges .when { color: var(--moss); font-weight: 600; }
.plugin-card h3 { margin: 0; font-size: 1.05rem; font-weight: 600; }
.plugin-card p { margin: .25rem 0 0; font-size: .9rem; color: var(--ink-muted); line-height: 1.55; }
@media (max-width: 720px) { .plugins-grid { grid-template-columns: 1fr; } }
```

- [ ] **Step 2:** Add HTML.

```html
<section class="plugins" id="plugins" aria-labelledby="plugins-h">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">Plugins</p>
      <h2 id="plugins-h">What ships with Mycroft</h2>
    </div>
    <div class="plugins-grid">
      <article class="plugin-card" data-plugin="spotlight">
        <div class="visual" aria-hidden="true"></div>
        <div class="body">
          <div class="badges"><span>2026</span><span class="when">at launch</span></div>
          <h3>Spotlight</h3>
          <p>OSINT investigation system. Multi-phase research, adversarial SIFT fact-checking, evidence grounding, knowledge-vault ingestion.</p>
        </div>
      </article>
      <article class="plugin-card" data-plugin="cojournalist">
        <div class="visual" aria-hidden="true"></div>
        <div class="body">
          <div class="badges"><span>2026</span><span class="when">at launch</span></div>
          <h3>coJournalist</h3>
          <p>Beat-monitoring engine. Scheduled scouts, change detection, relevance scoring. Web-hosted runs 24/7; self-host option available.</p>
        </div>
      </article>
      <article class="plugin-card" data-plugin="datahound">
        <div class="visual" aria-hidden="true"></div>
        <div class="body">
          <div class="badges"><span>2026</span><span class="when">May 2026</span></div>
          <h3>DataHound</h3>
          <p>Government and public-data API discovery with automated monitoring. Turn obscure open-data endpoints into queryable beats.</p>
        </div>
      </article>
      <article class="plugin-card" data-plugin="atelier">
        <div class="visual" aria-hidden="true"></div>
        <div class="body">
          <div class="badges"><span>2026</span><span class="when">May 2026</span></div>
          <h3>Atelier</h3>
          <p>Visual production — charts, maps, video, infographics, social cards. Data and narrative to publication-ready visuals.</p>
        </div>
      </article>
    </div>
  </div>
</section>
```

- [ ] **Step 3:** Reload, verify 2×2 grid, paper-cream visual placeholders. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): plugins grid"
```

---

## Task 8: Pricing section (2 tabs)

**Files:**
- Modify: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Add CSS.

```css
.pricing { padding: 5rem 0; }
.pricing .wrap { max-width: 1180px; margin: 0 auto; padding: 0 2rem; display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
.pricing .head .eyebrow { font-size: .76rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-muted); font-weight: 600; margin: 0 0 .75rem; }
.pricing h2 { font-family: var(--sans); font-size: clamp(1.8rem, 3vw, 2.4rem); margin: 0 0 1rem; font-weight: 600; letter-spacing: -.01em; }
.pricing .lede { color: var(--ink-muted); font-size: 1rem; margin: 0 0 2rem; max-width: 36ch; }
.pricing-card { background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.5rem; }
.pricing-card .tabs { display: flex; gap: .5rem; background: var(--bg); border-radius: 999px; padding: .25rem; margin: 0 0 1.25rem; border: 1px solid var(--border); }
.pricing-card .tabs button { flex: 1; padding: .55rem 1rem; border-radius: 999px; border: none; background: transparent; cursor: pointer; font-family: inherit; font-size: .9rem; color: var(--ink-muted); }
.pricing-card .tabs button[aria-selected="true"] { background: var(--ink); color: var(--bg); }
.pricing-card .tier-name { font-weight: 600; font-size: .9rem; display: flex; gap: .5rem; align-items: center; }
.pricing-card .tier-name .pill { background: var(--moss); color: var(--bg); font-size: .68rem; padding: .15em .5em; border-radius: 999px; font-weight: 700; }
.pricing-card .price { font-family: var(--sans); font-size: 3rem; line-height: 1; font-weight: 700; margin: .75rem 0; letter-spacing: -.02em; }
.pricing-card .price small { font-size: 1rem; font-weight: 400; color: var(--ink-muted); }
.pricing-card ul.bullets { list-style: none; padding: 0; margin: 1rem 0 1.25rem; }
.pricing-card ul.bullets li { padding: .35rem 0 .35rem 1.5rem; font-size: .92rem; color: var(--ink); position: relative; }
.pricing-card ul.bullets li::before { content: "✓"; position: absolute; left: 0; color: var(--moss); font-weight: 700; }
.pricing-card .tier-cta { width: 100%; }
@media (max-width: 900px) { .pricing .wrap { grid-template-columns: 1fr; gap: 2rem; } }
```

- [ ] **Step 2:** Add HTML.

```html
<section class="pricing" id="pricing" aria-labelledby="pricing-h">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">Pricing</p>
      <h2 id="pricing-h">Choose how you run Mycroft</h2>
      <p class="lede">Two modes ship by default. Switch between them with one toggle in your config — your vault and beats stay the same either way.</p>
    </div>
    <div class="pricing-card">
      <div class="tabs" role="tablist">
        <button role="tab" aria-selected="true" data-tier="cloud">Cloud</button>
        <button role="tab" aria-selected="false" data-tier="local">Local</button>
      </div>
      <div class="tier-body" id="tier-body">
        <div class="tier-name">Cloud <span class="pill">Default</span></div>
        <div class="price">~$6<small>/month, moderate use</small></div>
        <ul class="bullets">
          <li>Zero-retention providers only (Fireworks, Together)</li>
          <li>Open-weight models, no GPT/Claude/Gemini</li>
          <li>Hosted in US or Europe</li>
          <li>Pay-per-use, cancel anytime</li>
        </ul>
        <a class="btn primary tier-cta" href="../../setup.html">Set up Cloud mode</a>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 3:** Add tab handler in the script module.

```js
const TIERS = {
  cloud: { name: 'Cloud', pill: 'Default', price: '~$6', unit: '/month, moderate use', bullets: ['Zero-retention providers only (Fireworks, Together)','Open-weight models, no GPT/Claude/Gemini','Hosted in US or Europe','Pay-per-use, cancel anytime'], cta: 'Set up Cloud mode' },
  local: { name: 'Local', pill: 'Private', price: '$0', unit: '/month, your machine', bullets: ['Runs Qwen 3.5 on llama-server / MLX','Zero network egress, ever','5 GB SSD for the 9B (Q4_K_M)','For sensitive sources & confidential docs'], cta: 'Set up Local mode' },
};
const tierBody = document.getElementById('tier-body');
document.querySelectorAll('.pricing-card .tabs button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.pricing-card .tabs button').forEach(b => b.setAttribute('aria-selected', b === btn ? 'true' : 'false'));
    const t = TIERS[btn.dataset.tier];
    tierBody.innerHTML = `
      <div class="tier-name">${t.name} <span class="pill">${t.pill}</span></div>
      <div class="price">${t.price}<small>${t.unit}</small></div>
      <ul class="bullets">${t.bullets.map(b => `<li>${b}</li>`).join('')}</ul>
      <a class="btn primary tier-cta" href="../../setup.html">${t.cta}</a>`;
  });
});
```

- [ ] **Step 4:** Reload, click both tabs, verify content swaps. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): pricing section with cloud/local tabs"
```

---

## Task 9: Privacy section + Trusted-by section + Studio block + Final CTA + Footer

This task batches the remaining static sections (they're structurally simple and share patterns).

**Files:**
- Modify: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Add CSS for all five blocks.

```css
/* Privacy */
.privacy { padding: 5rem 0; background: var(--bg-2); }
.privacy .wrap { max-width: 1180px; margin: 0 auto; padding: 0 2rem; }
.privacy .top { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; margin-bottom: 3rem; }
.privacy .top h2 { font-family: var(--sans); font-size: clamp(1.8rem, 3vw, 2.4rem); margin: .5rem 0 1rem; font-weight: 600; letter-spacing: -.01em; }
.privacy .top p { color: var(--ink-muted); font-size: 1rem; margin: 0; }
.privacy .vault { aspect-ratio: 1; min-height: 280px; border-radius: var(--radius-lg); position: relative; overflow: hidden; background: linear-gradient(135deg, var(--paper-top), var(--paper-bot)); }
.privacy .vault::after { content: ""; position: absolute; inset: 0; backdrop-filter: blur(14px); background: rgba(243, 237, 223, .35); }
.privacy ul { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.privacy ul li { background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.1rem; }
.privacy ul li strong { display: block; font-size: .95rem; margin-bottom: .25rem; }
.privacy ul li span { font-size: .85rem; color: var(--ink-muted); line-height: 1.55; }
@media (max-width: 900px) { .privacy .top { grid-template-columns: 1fr; gap: 2rem; } .privacy ul { grid-template-columns: 1fr; } }

/* Trusted-by */
.trusted { padding: 5rem 0; }
.trusted .wrap { max-width: 1180px; margin: 0 auto; padding: 0 2rem; }
.trusted h2 { font-family: var(--sans); font-size: clamp(1.6rem, 2.8vw, 2.2rem); text-align: center; margin: 0 0 2.5rem; font-weight: 600; letter-spacing: -.01em; }
.trusted-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; }
.testimonial { background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
.testimonial[data-placeholder="true"] { opacity: .85; position: relative; }
.testimonial[data-placeholder="true"]::after { content: "[placeholder]"; position: absolute; top: .5rem; right: .75rem; font-size: .68rem; color: var(--moss-2); letter-spacing: .08em; text-transform: uppercase; }
.testimonial blockquote { margin: 0; font-size: .95rem; line-height: 1.55; color: var(--ink); }
.testimonial cite { display: block; font-style: normal; font-size: .82rem; color: var(--ink-muted); }
.testimonial cite strong { color: var(--ink); font-style: normal; font-weight: 600; display: block; }
@media (max-width: 900px) { .trusted-grid { grid-template-columns: 1fr; } }

/* Studio */
.studio { padding: 5rem 0; background: var(--bg-2); }
.studio .wrap { max-width: 1180px; margin: 0 auto; padding: 0 2rem; }
.studio h2 { font-family: var(--sans); font-size: clamp(1.6rem, 2.8vw, 2.2rem); text-align: center; margin: 0 0 2.5rem; font-weight: 600; }
.studio-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
.studio-card { background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.75rem; display: flex; flex-direction: column; }
.studio-card .eyebrow { color: var(--moss); font-weight: 700; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; margin: 0 0 .5rem; }
.studio-card h3 { margin: 0 0 .35rem; font-size: 1.3rem; font-weight: 700; letter-spacing: -.01em; }
.studio-card .sub { margin: 0 0 1.25rem; color: var(--ink-muted); font-size: .98rem; }
.studio-card ul.features { list-style: none; padding: 0; margin: 0 0 1.25rem; }
.studio-card ul.features li { padding: .65rem 0; border-bottom: 1px solid var(--border); font-size: .92rem; }
.studio-card ul.features li:last-child { border-bottom: none; }
.studio-card .service { padding: .8rem 0; border-bottom: 1px solid var(--border); font-size: .92rem; line-height: 1.55; }
.studio-card .service:last-of-type { border-bottom: none; }
.studio-card .service strong { font-weight: 600; }
.studio-card .service .clients { display: block; color: var(--ink-muted); font-size: .82rem; margin-top: .3rem; }
.studio-card .price { color: var(--ink-muted); font-size: .9rem; margin: 0 0 1rem; }
.studio-card .price strong { color: var(--ink); font-weight: 700; }
.studio-card .spacer { flex: 1; }
.signup-form .row { display: flex; gap: .5rem; flex-wrap: wrap; }
.signup-form input[type="email"] { flex: 1; min-width: 0; padding: .75rem .9rem; background: var(--bg); border: 1px solid var(--border); border-radius: 999px; color: var(--ink); font-family: inherit; font-size: .92rem; }
.signup-form input[type="email"]:focus { outline: 2px solid var(--moss); outline-offset: 1px; border-color: var(--moss); }
.signup-form button { padding: .75rem 1.25rem; background: var(--moss); color: var(--bg); border: none; border-radius: 999px; font-family: inherit; font-size: .92rem; font-weight: 600; cursor: pointer; }
.signup-form button:hover:not(:disabled) { background: var(--ink); }
.signup-form button:disabled { opacity: .6; cursor: default; }
.signup-error { color: #c94444; font-size: .85rem; margin-top: .5rem; }
.signup-success { display: flex; align-items: center; gap: .5rem; color: var(--moss); font-size: .92rem; font-weight: 500; }
.consulting-cta { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; margin-top: auto; }
.consulting-cta .link { color: var(--ink-muted); font-size: .88rem; border-bottom: 1px solid var(--border); }
.consulting-cta .link:hover { color: var(--ink); border-bottom-color: var(--ink); text-decoration: none; }
@media (max-width: 900px) { .studio-grid { grid-template-columns: 1fr; } }

/* Final CTA */
.cta-final { text-align: center; padding: 6rem 0 4rem; }
.cta-final .wrap { max-width: 720px; margin: 0 auto; padding: 0 2rem; }
.cta-final h2 { font-family: var(--sans); font-size: clamp(1.8rem, 3vw, 2.6rem); margin: 0 0 1rem; font-weight: 600; letter-spacing: -.02em; }
.cta-final p { color: var(--ink-muted); font-size: 1.05rem; margin: 0 0 2rem; }
.cta-final .ctas { display: flex; gap: .75rem; justify-content: center; flex-wrap: wrap; }

/* Footer */
footer.site { background: var(--bg-2); padding: 3rem 0 0; margin-top: 4rem; position: relative; overflow: hidden; }
footer.site .wrap { max-width: 1240px; margin: 0 auto; padding: 0 2rem; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 2rem; }
footer.site .brand-block .logo { font-family: var(--serif); font-size: 1.4rem; color: var(--ink); }
footer.site .brand-block p { color: var(--ink-muted); font-size: .88rem; margin: .5rem 0 0; max-width: 28ch; }
footer.site .col h4 { margin: 0 0 .75rem; font-size: .82rem; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-muted); }
footer.site .col ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: .35rem; }
footer.site .col ul li a { color: var(--ink); font-size: .9rem; }
footer.site .col ul li a:hover { color: var(--moss); }
footer.site .giant {
  font-family: var(--serif);
  font-size: clamp(8rem, 26vw, 24rem);
  line-height: .85;
  color: var(--ink);
  text-align: center;
  margin: 3rem 0 0;
  letter-spacing: -.02em;
  user-select: none;
  pointer-events: none;
}
@media (max-width: 900px) { footer.site .wrap { grid-template-columns: 1fr 1fr; } }
@media (max-width: 600px) { footer.site .wrap { grid-template-columns: 1fr; } }
```

- [ ] **Step 2:** Add HTML for all five blocks.

```html
<section class="privacy" id="privacy" aria-labelledby="privacy-h">
  <div class="wrap">
    <div class="top">
      <div>
        <p class="eyebrow" style="color: var(--ink-muted); font-size: .76rem; letter-spacing: .14em; text-transform: uppercase; font-weight: 600; margin: 0 0 .75rem;">Privacy by default</p>
        <h2 id="privacy-h">Investigative journalism has a threat model. Mycroft is built to match it.</h2>
        <p>ZDR providers, local-first mode, no telemetry. Your vault stays on disk. Your keys stay in your browser. The setup form has no backend.</p>
      </div>
      <div class="vault" aria-hidden="true"></div>
    </div>
    <ul>
      <li><strong>Zero Data Retention</strong><span>Only ZDR providers (Fireworks, Together) ship as defaults. No Claude, OpenAI, or Gemini.</span></li>
      <li><strong>Local-first mode</strong><span>One toggle and every inference runs on your machine. Zero egress. $0/month.</span></li>
      <li><strong>Your keys, your machine</strong><span>The setup page runs in your browser. API keys embed in the .command you download.</span></li>
      <li><strong>Firecrawl only for the web</strong><span>Web fetching uses Firecrawl exclusively — no surveillance-adjacent scraping middlemen.</span></li>
      <li><strong>Your vault stays on disk</strong><span>Findings write to your Obsidian vault. Nothing syncs to our infrastructure.</span></li>
      <li><strong>No telemetry</strong><span>No analytics, no crash reporting, no phone home. Open-source; read every line.</span></li>
    </ul>
  </div>
</section>

<section class="trusted" aria-labelledby="trusted-h">
  <div class="wrap">
    <h2 id="trusted-h">Trusted by reporters &amp; investigative teams</h2>
    <!-- TODO before publish: replace with real testimonials -->
    <div class="trusted-grid">
      <article class="testimonial" data-placeholder="true">
        <blockquote>"The morning brief alone replaced two newsletter subs and an hour of scrolling. Cited, deduped, in my vault."</blockquote>
        <cite><strong>Reporter, regional daily</strong>Investigations desk</cite>
      </article>
      <article class="testimonial" data-placeholder="true">
        <blockquote>"SIFT fact-checking with the actual methodology baked in. The verdict tags ship straight into our editor's review."</blockquote>
        <cite><strong>Editor</strong>Independent newsroom</cite>
      </article>
      <article class="testimonial" data-placeholder="true">
        <blockquote>"Local mode for the sensitive interviews, cloud for the rest. The toggle in the config is exactly what we needed."</blockquote>
        <cite><strong>Investigative journalist</strong>Freelance</cite>
      </article>
    </div>
  </div>
</section>

<section class="studio" id="studio" aria-labelledby="studio-h">
  <div class="wrap">
    <h2 id="studio-h">From the team behind Mycroft</h2>
    <div class="studio-grid">
      <article class="studio-card">
        <div class="eyebrow">Launching May 2026</div>
        <h3>Pro Membership</h3>
        <p class="sub">Investigations with AI. The tools to run your own.</p>
        <ul class="features">
          <li>Collaborative investigations — shared leads, data, methodology</li>
          <li>Live bootcamps, workshops, and events</li>
          <li>Hosted Pro tier of agent extensions</li>
          <li>Investigation methodologies and AI techniques, in depth</li>
        </ul>
        <p class="price"><strong>From $25/mo</strong> · 400+ journalists already reading</p>
        <div class="spacer"></div>
        <form class="signup-form" id="signup-form">
          <div class="row">
            <input type="email" id="signup-email" placeholder="you@example.com" required autocomplete="email" aria-label="Email address">
            <button type="submit" id="signup-submit">Subscribe</button>
          </div>
          <div class="signup-error" id="signup-error" hidden role="alert"></div>
        </form>
        <div class="signup-success" id="signup-success" hidden>
          <span>You're in. I'll ping you at launch.</span>
        </div>
      </article>
      <article class="studio-card">
        <h3>Consulting</h3>
        <p class="sub">I train newsrooms to investigate with AI.</p>
        <div class="service"><strong>Workshops &amp; training</strong> — hands-on sessions where journalists investigate live stories with AI.<span class="clients">Le Temps · MAZ · Republik · 20 Minuten</span></div>
        <div class="service"><strong>Custom AI tooling</strong> — AI systems wired into editorial workflow — archive search, source monitoring, research agents.<span class="clients">MediaStorm</span></div>
        <div class="service"><strong>Investigation collaborations</strong> — visual production and AI pipelines paired with field reporting.<span class="clients">The New Humanitarian</span></div>
        <div class="spacer"></div>
        <div class="consulting-cta">
          <a href="mailto:tom@buriedsignals.com?subject=Mycroft%20%E2%80%94%20Consulting" class="btn primary">Get in touch →</a>
          <a href="https://buriedsignals.com/consulting" target="_blank" rel="noreferrer" class="link">See case studies →</a>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="cta-final" aria-labelledby="cta-h">
  <div class="wrap">
    <h2 id="cta-h">Built by journalists, for journalists.</h2>
    <p>Open source. Self-hostable. No lock-in. No surveillance. Just the tool you wish you'd had three investigations ago.</p>
    <div class="ctas">
      <a class="btn primary" href="../../setup.html">Set up Mycroft</a>
      <a class="btn secondary" href="https://github.com/buriedsignals/mycroft" target="_blank" rel="noreferrer">View on GitHub</a>
    </div>
  </div>
</section>
```

- [ ] **Step 3:** Replace the empty `<footer class="site">` with:

```html
<footer class="site" role="contentinfo">
  <div class="wrap">
    <div class="brand-block"><div class="logo">Mycroft</div><p>An opinionated extension pack for Goose. Built by Buried Signals.</p></div>
    <div class="col"><h4>Documentation</h4><ul><li><a href="https://github.com/buriedsignals/mycroft">Source</a></li><li><a href="../../setup.html">Setup</a></li><li><a href="https://goose-docs.ai/">Goose docs</a></li></ul></div>
    <div class="col"><h4>Resources</h4><ul><li><a href="#day">A day with Mycroft</a></li><li><a href="#plugins">Plugins</a></li><li><a href="#privacy">Privacy</a></li></ul></div>
    <div class="col"><h4>Company</h4><ul><li><a href="https://buriedsignals.com">Buried Signals</a></li><li><a href="https://buriedsignals.com/consulting">Consulting</a></li><li><a href="mailto:tom@buriedsignals.com">Contact</a></li></ul></div>
  </div>
  <div class="giant" aria-hidden="true">Mycroft</div>
</footer>
```

- [ ] **Step 4:** Append the signup form handler to the script module (port from current `index.html:490-535`).

```js
const NEWSLETTER_ENDPOINT = '/api/newsletter/subscribe';
const sForm = document.getElementById('signup-form');
const sEmail = document.getElementById('signup-email');
const sBtn = document.getElementById('signup-submit');
const sErr = document.getElementById('signup-error');
const sOk = document.getElementById('signup-success');
sForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = sEmail.value.trim();
  if (!email) return;
  sBtn.disabled = true;
  const orig = sBtn.textContent;
  sBtn.textContent = 'Subscribing…';
  sErr.hidden = true;
  try {
    const r = await fetch(NEWSLETTER_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, newsletters: ['buried_signals'] }) });
    if (r.ok) { sForm.hidden = true; sOk.hidden = false; }
    else { let m = 'Something went wrong. Please try again.'; try { const d = await r.json(); if (d?.detail) m = d.detail; } catch (_) {} sErr.textContent = m; sErr.hidden = false; }
  } catch (_) { sErr.textContent = 'Something went wrong. Please try again.'; sErr.hidden = false; }
  finally { sBtn.disabled = false; sBtn.textContent = orig; }
});
```

- [ ] **Step 5:** Reload, scroll the entire page, verify all sections render, click privacy bullets / studio CTAs / pricing tabs / day items, no console errors. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): privacy, trusted-by, studio, final cta, footer"
```

---

## Task 10: Browser-use full-page visual review (Phase A gate)

**Files:** none

- [ ] **Step 1:** Run a full-page visual review.

```bash
bunx browser-use --url http://localhost:5180/ --task "Capture full-page screenshot. Scroll from top to bottom. Report: any console errors, any layout breakage on standard 1440x900 viewport, whether the following sections exist in order: hero, workshops strip, intro, day, plugins, pricing, privacy, trusted, studio, cta-final, footer with giant Mycroft mark. Confirm Cellora-style cream palette."
```

- [ ] **Step 2:** If browser-use reports any layout breakage or console errors, fix them inline before proceeding.

- [ ] **Step 3:** Commit any fixes.

```bash
git add prototypes/proto-13/index.html
git commit -m "fix(proto-13): phase A visual review fixes"
```

---

# PHASE B — Three.js scene + hero pose (Tasks 11–14)

## Task 11: Scene boilerplate + particles initialised in receipt-cluster sphere

**Files:**
- Modify: `prototypes/proto-13/index.html` (script module)

This task ports the proto-02 receipt-cluster sphere as the initial particle layout. Read `prototypes/proto-02/index.html` for reference patterns (do not modify it).

- [ ] **Step 1:** Replace the empty `<script type="module">` content with the scene module structure (keep the day-list, pricing-tab, signup-form handlers). Append at the END of the same script block:

```js
import * as THREE from 'three';

const COUNT = (navigator.hardwareConcurrency || 4) >= 8 ? 900 : 600;
const SPHERE_RADIUS = 1.25;
const RECEIPT_W = 0.14;
const RECEIPT_H = 0.10;

const canvas = document.getElementById('paper-canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
renderer.setSize(innerWidth, innerHeight);
renderer.setClearColor(0x000000, 0);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xf3eddf, 4.5, 9);

const camera = new THREE.PerspectiveCamera(35, innerWidth / innerHeight, 0.05, 50);
camera.position.set(0, 0, 4.6);

// lighting
const hemi = new THREE.HemisphereLight(0xffffff, 0xc8b89e, 0.9);
scene.add(hemi);
const dir = new THREE.DirectionalLight(0xffffff, 0.6);
dir.position.set(2, 3, 2);
scene.add(dir);

// particle geometry — InstancedMesh of paper sheets
const sheetGeo = new THREE.PlaneGeometry(RECEIPT_W, RECEIPT_H);
const sheetMat = new THREE.MeshStandardMaterial({
  color: 0xece1ca, roughness: 0.95, metalness: 0,
  side: THREE.DoubleSide, flatShading: true,
});
const sheets = new THREE.InstancedMesh(sheetGeo, sheetMat, COUNT);
sheets.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(sheets);

// per-particle state arrays
const positions = new Float32Array(COUNT * 3);
const targets = new Float32Array(COUNT * 3);
const rotations = new Float32Array(COUNT * 3);

// init: random points on sphere surface
function initSphere() {
  for (let i = 0; i < COUNT; i++) {
    const u = Math.random(), v = Math.random();
    const theta = 2 * Math.PI * u;
    const phi = Math.acos(2 * v - 1);
    const r = SPHERE_RADIUS * (0.85 + Math.random() * 0.15);
    positions[i*3+0] = r * Math.sin(phi) * Math.cos(theta);
    positions[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i*3+2] = r * Math.cos(phi);
    rotations[i*3+0] = Math.random() * Math.PI * 2;
    rotations[i*3+1] = Math.random() * Math.PI * 2;
    rotations[i*3+2] = Math.random() * Math.PI * 2;
  }
  targets.set(positions);
}
initSphere();

const dummy = new THREE.Object3D();
function writeMatrices() {
  for (let i = 0; i < COUNT; i++) {
    dummy.position.set(positions[i*3], positions[i*3+1], positions[i*3+2]);
    dummy.rotation.set(rotations[i*3], rotations[i*3+1], rotations[i*3+2]);
    dummy.updateMatrix();
    sheets.setMatrixAt(i, dummy.matrix);
  }
  sheets.instanceMatrix.needsUpdate = true;
}
writeMatrices();

let raf = null;
function tick(t) {
  // slow rotation of the sphere as a whole
  sheets.rotation.y = t * 0.0001;
  renderer.render(scene, camera);
  raf = requestAnimationFrame(tick);
}
raf = requestAnimationFrame(tick);

addEventListener('resize', () => {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
});
```

- [ ] **Step 2:** Reload. Expected: a slowly rotating cluster of cream paper sheets fills the hero. Verify no WebGL errors.

- [ ] **Step 3:** Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): three.js scene with receipt-cluster sphere"
```

---

## Task 12: Hero physics — mouse repulsion + dispersion

**Files:**
- Modify: `prototypes/proto-13/index.html` (script module)

- [ ] **Step 1:** Replace the simple `tick` loop with physics-driven dispersion (port simplified from proto-02). After the initial `tick` declaration, insert:

```js
const velocities = new Float32Array(COUNT * 3);
const PARTICLE_R = RECEIPT_H * 0.5;
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let mouseActive = false;
const mousePoint = new THREE.Vector3();
const mousePlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);

addEventListener('pointermove', (e) => {
  ndc.x = (e.clientX / innerWidth) * 2 - 1;
  ndc.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(ndc, camera);
  if (raycaster.ray.intersectPlane(mousePlane, mousePoint)) mouseActive = true;
});
addEventListener('pointerleave', () => { mouseActive = false; });

let elapsed = 0;
let prev = performance.now();
const DISPERSE_START = 1500; // ms
const DISPERSE_DURATION = 4000;

function tickHero(now) {
  const dt = Math.min(0.05, (now - prev) / 1000);
  prev = now;
  elapsed += dt * 1000;

  const dispersion = Math.max(0, Math.min(1, (elapsed - DISPERSE_START) / DISPERSE_DURATION));

  for (let i = 0; i < COUNT; i++) {
    const ix = i*3, iy = i*3+1, iz = i*3+2;
    // outward drift after dispersion onset
    const px = positions[ix], py = positions[iy], pz = positions[iz];
    const dist = Math.hypot(px, py, pz) || 0.001;
    velocities[ix] += (px / dist) * dispersion * 0.04 * dt;
    velocities[iy] += (py / dist) * dispersion * 0.04 * dt;
    velocities[iz] += (pz / dist) * dispersion * 0.04 * dt;

    // mouse repulsion
    if (mouseActive) {
      const dx = px - mousePoint.x, dy = py - mousePoint.y, dz = pz - mousePoint.z;
      const d2 = dx*dx + dy*dy + dz*dz;
      if (d2 < 0.6) {
        const f = (0.6 - d2) * 8 * dt;
        const inv = 1 / Math.sqrt(d2 + 1e-4);
        velocities[ix] += dx * inv * f;
        velocities[iy] += dy * inv * f;
        velocities[iz] += dz * inv * f;
      }
    }

    // damping
    velocities[ix] *= 0.96; velocities[iy] *= 0.96; velocities[iz] *= 0.96;

    positions[ix] += velocities[ix];
    positions[iy] += velocities[iy];
    positions[iz] += velocities[iz];

    // tumbling rotation
    rotations[ix] += dt * 0.4;
    rotations[iy] += dt * 0.6;
  }

  writeMatrices();
  renderer.render(scene, camera);
  raf = requestAnimationFrame(tickHero);
}
cancelAnimationFrame(raf);
prev = performance.now();
raf = requestAnimationFrame(tickHero);
```

- [ ] **Step 2:** Reload. Expected: sphere starts compact, after ~1.5s starts dispersing outward; cursor in the hero zone pushes papers away.

- [ ] **Step 3:** Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): hero dispersion + mouse repulsion"
```

---

## Task 13: Hero end-pose — particles form "Mycroft" letterforms

**Files:**
- Modify: `prototypes/proto-13/index.html`

The end-pose is reached when the user scrolls below the hero. We sample target positions by rasterizing the brand SVG to a 2D canvas, then collecting alpha-positive pixels.

- [ ] **Step 1:** Add a helper that samples 2D points from text rendered to an offscreen canvas. Insert above the `tick` loop:

```js
function sampleTextPoints(text, fontFamily, fontSize, count) {
  const off = document.createElement('canvas');
  off.width = 1024; off.height = 256;
  const ctx = off.getContext('2d');
  ctx.fillStyle = '#000';
  ctx.font = `${fontSize}px ${fontFamily}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, off.width / 2, off.height / 2);
  const data = ctx.getImageData(0, 0, off.width, off.height).data;
  const pts = [];
  // rejection sample
  while (pts.length < count) {
    const x = Math.floor(Math.random() * off.width);
    const y = Math.floor(Math.random() * off.height);
    if (data[(y * off.width + x) * 4 + 3] > 128) {
      // map canvas coords to world coords (centered, ~3 units wide)
      const wx = (x / off.width - 0.5) * 3.0;
      const wy = -(y / off.height - 0.5) * 0.8;
      pts.push([wx, wy, 0]);
    }
  }
  return pts;
}

const heroEndTargets = sampleTextPoints('Mycroft', '"IM Fell English", serif', 200, COUNT);
```

- [ ] **Step 2:** Add a `heroSettleProgress` state (0..1) driven by scroll. Below the existing pointer handlers, insert:

```js
let heroSettle = 0; // 0 = dispersed cluster, 1 = letters formed
const heroEl = document.getElementById('hero');
function updateHeroSettle() {
  const rect = heroEl.getBoundingClientRect();
  // start settling when bottom of hero approaches top of viewport
  const p = 1 - Math.max(0, Math.min(1, (rect.bottom - 200) / (innerHeight - 200)));
  heroSettle = p;
}
addEventListener('scroll', updateHeroSettle, { passive: true });
updateHeroSettle();
```

- [ ] **Step 3:** Modify `tickHero` to lerp toward `heroEndTargets` proportional to `heroSettle`. In the for-loop, replace the velocity/position section with:

```js
    // outward drift after dispersion onset (only when not yet settling)
    if (heroSettle < 0.05) {
      const dist = Math.hypot(px, py, pz) || 0.001;
      velocities[ix] += (px / dist) * dispersion * 0.04 * dt;
      velocities[iy] += (py / dist) * dispersion * 0.04 * dt;
      velocities[iz] += (pz / dist) * dispersion * 0.04 * dt;
    }

    // mouse repulsion (hero only)
    if (mouseActive && heroSettle < 0.1) {
      const dx = px - mousePoint.x, dy = py - mousePoint.y, dz = pz - mousePoint.z;
      const d2 = dx*dx + dy*dy + dz*dz;
      if (d2 < 0.6) {
        const f = (0.6 - d2) * 8 * dt;
        const inv = 1 / Math.sqrt(d2 + 1e-4);
        velocities[ix] += dx * inv * f;
        velocities[iy] += dy * inv * f;
        velocities[iz] += dz * inv * f;
      }
    }

    velocities[ix] *= 0.96; velocities[iy] *= 0.96; velocities[iz] *= 0.96;

    if (heroSettle > 0.01) {
      // damp toward target letterform
      const tx = heroEndTargets[i][0], ty = heroEndTargets[i][1], tz = heroEndTargets[i][2];
      const k = 4 * dt * heroSettle;
      positions[ix] += (tx - px) * k;
      positions[iy] += (ty - py) * k;
      positions[iz] += (tz - pz) * k;
      // rotation flattens to face camera
      rotations[ix] += (0 - rotations[ix]) * k;
      rotations[iy] += (0 - rotations[iy]) * k;
      // freeze velocities
      velocities[ix] *= 0.6; velocities[iy] *= 0.6; velocities[iz] *= 0.6;
    } else {
      positions[ix] += velocities[ix];
      positions[iy] += velocities[iy];
      positions[iz] += velocities[iz];
      rotations[ix] += dt * 0.4;
      rotations[iy] += dt * 0.6;
    }
```

- [ ] **Step 4:** Hide the giant CSS `.brand-mark` text once particles are forming the letters (avoid visual collision). Add CSS:

```css
.hero .brand-mark { transition: opacity .4s ease; }
.hero.settled .brand-mark { opacity: 0; }
```

And in `updateHeroSettle`:

```js
heroEl.classList.toggle('settled', heroSettle > 0.4);
```

- [ ] **Step 5:** Reload. Scroll down slowly: papers gather and form the word "Mycroft". Scroll back up: they re-disperse. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): hero end-pose — letterform settling"
```

---

## Task 14: Browser-use review of Phase B

**Files:** none

- [ ] **Step 1:** Visual review.

```bash
bunx browser-use --url http://localhost:5180/ --task "Open the page. Wait 5 seconds. Take screenshot of hero. Scroll down 600px. Wait 1s. Take screenshot. Confirm: papers visible in hero, clearly forming the word 'Mycroft' as user scrolls. Report any errors."
```

- [ ] **Step 2:** Fix any reported issues, commit.

---

# PHASE C — Section pose state machine (Tasks 15–19)

The state machine: each section registers a target-position generator. An `IntersectionObserver` watches all sections; the most-visible section's target becomes active; particles lerp toward it.

## Task 15: State machine scaffold + section poses (clock, plugins-orbits, pricing, drift)

**Files:**
- Modify: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Add the pose registry. Insert after `heroEndTargets` declaration:

```js
const sectionTargets = new Float32Array(COUNT * 3);
let activePose = 'hero';
const POSE_BUILDERS = {
  hero: () => { /* hero handles itself */ },
  day: buildDayClock,
  plugins: buildPluginsOrbits,
  pricing: buildPricingCluster,
  privacy: buildPrivacyCube,
  drift: buildDrift,
  footer: buildFooterPile,
};

function buildDayClock() {
  // 4 clusters arranged in arc on the right side of viewport (in world space x≈+1.2)
  const centers = [
    [1.0, 0.7, 0], [1.4, 0.25, 0], [1.4, -0.25, 0], [1.0, -0.7, 0]
  ];
  for (let i = 0; i < COUNT; i++) {
    const c = centers[i % 4];
    const r = 0.18 * Math.sqrt(Math.random());
    const a = Math.random() * Math.PI * 2;
    sectionTargets[i*3+0] = c[0] + Math.cos(a) * r;
    sectionTargets[i*3+1] = c[1] + Math.sin(a) * r;
    sectionTargets[i*3+2] = c[2] + (Math.random() - 0.5) * 0.1;
  }
}

function buildPluginsOrbits() {
  // 4 orbits across viewport
  const centers = [[-0.9, 0.6, 0], [0.9, 0.6, 0], [-0.9, -0.6, 0], [0.9, -0.6, 0]];
  for (let i = 0; i < COUNT; i++) {
    const c = centers[i % 4];
    const r = 0.25 * Math.sqrt(Math.random());
    const a = Math.random() * Math.PI * 2;
    sectionTargets[i*3+0] = c[0] + Math.cos(a) * r;
    sectionTargets[i*3+1] = c[1] + Math.sin(a) * r;
    sectionTargets[i*3+2] = c[2] + (Math.random() - 0.5) * 0.15;
  }
}

function buildPricingCluster() {
  // calm cluster on the right side
  const c = [1.2, 0, 0];
  for (let i = 0; i < COUNT; i++) {
    const r = 0.6 * Math.sqrt(Math.random());
    const a = Math.random() * Math.PI * 2;
    const z = (Math.random() - 0.5) * 0.4;
    sectionTargets[i*3+0] = c[0] + Math.cos(a) * r * 0.6;
    sectionTargets[i*3+1] = c[1] + Math.sin(a) * r * 0.6;
    sectionTargets[i*3+2] = c[2] + z;
  }
}

function buildPrivacyCube() {
  // tight cube in the right portion
  for (let i = 0; i < COUNT; i++) {
    sectionTargets[i*3+0] = 1.0 + (Math.random() - 0.5) * 0.8;
    sectionTargets[i*3+1] = (Math.random() - 0.5) * 0.8;
    sectionTargets[i*3+2] = (Math.random() - 0.5) * 0.8;
  }
}

function buildDrift() {
  // sparse, viewport-wide upward drift; targets are above the viewport
  for (let i = 0; i < COUNT; i++) {
    sectionTargets[i*3+0] = (Math.random() - 0.5) * 4;
    sectionTargets[i*3+1] = 1.5 + Math.random() * 1.5;
    sectionTargets[i*3+2] = (Math.random() - 0.5) * 1.5;
  }
}

function buildFooterPile() {
  // pile at the bottom, world-y around -1.4
  for (let i = 0; i < COUNT; i++) {
    sectionTargets[i*3+0] = (Math.random() - 0.5) * 3.5;
    sectionTargets[i*3+1] = -1.4 + (Math.random() ** 4) * 0.6;
    sectionTargets[i*3+2] = (Math.random() - 0.5) * 0.6;
  }
}
```

- [ ] **Step 2:** Add the IntersectionObserver. After the pose builders:

```js
const SECTION_POSE = {
  'hero': 'hero',
  'day': 'day',
  'plugins': 'plugins',
  'pricing': 'pricing',
  'privacy': 'privacy',
  'trusted': 'drift',
  'studio': 'drift',
  'cta': 'drift',
};
const cta = document.querySelector('.cta-final'); cta?.setAttribute('id', 'cta');

const obs = new IntersectionObserver((entries) => {
  // pick the entry with the largest intersectionRatio
  let best = null;
  entries.forEach(e => {
    if (!best || e.intersectionRatio > best.intersectionRatio) best = e;
  });
  if (!best || best.intersectionRatio < 0.25) return;
  const id = best.target.id;
  const pose = SECTION_POSE[id] || 'drift';
  if (pose !== activePose) {
    activePose = pose;
    if (pose !== 'hero') (POSE_BUILDERS[pose] || (() => {}))();
  }
}, { threshold: [0, 0.25, 0.5, 0.75, 1] });

['hero','day','plugins','pricing','privacy','trusted','studio','cta'].forEach(id => {
  const el = document.getElementById(id);
  if (el) obs.observe(el);
});

// observe footer separately for the pile pose
const footerEl = document.querySelector('footer.site');
if (footerEl) {
  const fobs = new IntersectionObserver((es) => {
    if (es[0].isIntersecting) { activePose = 'footer'; buildFooterPile(); }
  }, { threshold: 0.05 });
  fobs.observe(footerEl);
}
```

- [ ] **Step 3:** Modify the `tickHero` function — extend it to handle non-hero poses. After the hero settling block in the for-loop, replace the `else` with a unified non-hero branch:

```js
    } else if (activePose === 'hero') {
      positions[ix] += velocities[ix];
      positions[iy] += velocities[iy];
      positions[iz] += velocities[iz];
      rotations[ix] += dt * 0.4;
      rotations[iy] += dt * 0.6;
    } else {
      // lerp toward sectionTargets
      const k = 2.5 * dt;
      positions[ix] += (sectionTargets[ix] - px) * k;
      positions[iy] += (sectionTargets[iy] - py) * k;
      positions[iz] += (sectionTargets[iz] - pz) * k;
      rotations[ix] += dt * 0.15;
      rotations[iy] += dt * 0.2;
    }
```

Rename the function from `tickHero` to `tickAll` (or keep the name; it now handles all poses) — find and replace the two `tickHero` references in the requestAnimationFrame call.

- [ ] **Step 4:** Reload, scroll the whole page slowly, verify particles re-arrange between sections (hero sphere → letterforms → 4 day clusters → 4 plugin orbits → pricing right cluster → privacy cube → drift → footer pile). Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): section pose state machine + 7 poses"
```

---

## Task 16: Camera follow — anchor camera to the active section

**Files:**
- Modify: `prototypes/proto-13/index.html`

The camera currently stays at z=4.6 facing origin; with `position: fixed` canvas, particles always render in the same on-screen region. We want each pose to feel anchored to its section in the page. We achieve this by translating the camera in world-y based on the active section's position relative to viewport.

- [ ] **Step 1:** Replace the simple resize handler region. Add a per-section camera target. After `obs` setup:

```js
const POSE_CAM = {
  hero:    { y: 0,    z: 4.6 },
  day:     { y: 0,    z: 4.0 },
  plugins: { y: 0,    z: 4.6 },
  pricing: { y: 0,    z: 4.2 },
  privacy: { y: 0,    z: 4.0 },
  drift:   { y: 0,    z: 5.5 },
  footer:  { y: -0.6, z: 4.0 },
};
let camTarget = POSE_CAM.hero;
```

- [ ] **Step 2:** In the IntersectionObserver callback after `activePose = pose;`, add:

```js
camTarget = POSE_CAM[pose] || POSE_CAM.drift;
```

- [ ] **Step 3:** In the tick loop, after the for-loop:

```js
camera.position.x += (0 - camera.position.x) * 2 * dt;
camera.position.y += (camTarget.y - camera.position.y) * 2 * dt;
camera.position.z += (camTarget.z - camera.position.z) * 2 * dt;
camera.lookAt(0, camTarget.y, 0);
```

- [ ] **Step 4:** Reload, scroll, verify the cluster gently re-frames at each section. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): camera follows active pose"
```

---

## Task 17: Plugin micro-behaviours (Spotlight beam, coJournalist tick, DataHound stack, Atelier silhouettes)

**Files:**
- Modify: `prototypes/proto-13/index.html`

Within the `plugins` pose, modulate the per-cluster behaviour. The 4 plugin cards are mapped to 4 quadrants (`i % 4`).

- [ ] **Step 1:** Add a per-frame plugin behaviour modulation. Inside the `tick` for-loop, replace the non-hero/non-letterform branch (the `else` branch) with a more specific block:

```js
    } else {
      const k = 2.5 * dt;
      let tx = sectionTargets[ix], ty = sectionTargets[iy], tz = sectionTargets[iz];

      if (activePose === 'plugins') {
        const bucket = i % 4;
        const t = now * 0.001;
        if (bucket === 0) { // Spotlight — sweep
          const sweep = Math.sin(t * 0.8 + (i * 0.001));
          tx += sweep * 0.04;
        } else if (bucket === 1) { // coJournalist — radial pulse every ~4s
          const pulse = 0.95 + 0.05 * Math.sin(t * (Math.PI * 2 / 4));
          const cx = 0.9, cy = 0.6;
          tx = cx + (sectionTargets[ix] - cx) * pulse;
          ty = cy + (sectionTargets[iy] - cy) * pulse;
        } else if (bucket === 2) { // DataHound — stack growing
          const phase = (t * 0.5) % 6; // 0..6
          const idx = (i / 4) | 0;
          ty = -0.8 + (idx % Math.ceil(phase * 5)) * 0.012;
          tx = -0.9 + ((idx % 6) - 3) * 0.04;
        } else { // Atelier — morph between shapes
          const cycle = Math.floor((t / 6) % 3);
          if (cycle === 0) { /* targets as is */ }
          else if (cycle === 1) { tx = 0.9 + Math.cos(i * 0.5) * 0.2; ty = -0.6 + Math.sin(i * 0.5) * 0.2; }
          else { tx = 0.9 + Math.cos(i) * 0.25; ty = -0.6 + Math.abs(Math.sin(i * 0.3)) * 0.3; }
        }
      }

      positions[ix] += (tx - px) * k;
      positions[iy] += (ty - py) * k;
      positions[iz] += (tz - pz) * k;
      rotations[ix] += dt * 0.15;
      rotations[iy] += dt * 0.2;
    }
```

(Note: `now` must be in scope; the tick function receives `now` as its argument.)

- [ ] **Step 2:** Reload. Scroll to the Plugins section. Verify each of the 4 quadrants exhibits a different, subtle motion. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): plugin micro-behaviours per quadrant"
```

---

## Task 18: Privacy frosted-glass effect (DOM overlay)

**Files:**
- Modify: `prototypes/proto-13/index.html`

The frosted vault is purely a CSS layer; the canvas already runs the cube pose. We add a frosted DOM rectangle anchored to the right column of the privacy section (mobile-safe) that hovers above the canvas.

- [ ] **Step 1:** Verify the existing `.privacy .vault` element from Task 9 already creates the frosted region. Confirm visually.

- [ ] **Step 2:** Adjust z-index so the cube pose is visible *behind* the frosted overlay. The canvas is at `z-index: 0`, content at `z-index: 1`. The vault div sits in the content layer and applies `backdrop-filter: blur(14px)` over the canvas — this is correct.

- [ ] **Step 3:** Reload, scroll to Privacy, verify the right block shows blurred paper movement. Commit if any tweaks were made.

---

## Task 19: Reduced-motion fallback + mobile fallback + button paper-burst

**Files:**
- Modify: `prototypes/proto-13/index.html`

- [ ] **Step 1:** Add reduced-motion early-out at the top of the script module (before scene creation):

```js
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const isMobile = innerWidth < 768;
```

- [ ] **Step 2:** When reduced motion is on, the tick should not animate transitions; pose changes snap. In the tick, scale the lerp coefficient `k` by an effective rate:

```js
const POSE_LERP = reducedMotion ? 999 : 2.5;
// then use:
const k = Math.min(1, POSE_LERP * dt);
```

And gate the hero dispersion / mouse repulsion with `if (!reducedMotion)`.

- [ ] **Step 3:** Mobile fallback — disable plugin micro-behaviour modulation and skip the hero physics smoothing (still build poses, but keep render frequency low):

```js
if (isMobile) sheetMat.flatShading = false; // cheaper
const TICK_INTERVAL = isMobile ? 1000 / 30 : 0;
let lastTick = 0;
// in tick:
if (now - lastTick < TICK_INTERVAL) { raf = requestAnimationFrame(tick); return; }
lastTick = now;
```

- [ ] **Step 4:** Button paper-burst (CSS-only DOM micro-interaction). Add CSS:

```css
.paper-burst { position: fixed; pointer-events: none; width: 8px; height: 6px; background: var(--paper-top); border: 1px solid var(--paper-bot); border-radius: 1px; z-index: 50; animation: burst .7s ease-out forwards; }
@keyframes burst { to { transform: translate(var(--dx,0), var(--dy,-90px)) rotate(var(--rot,12deg)); opacity: 0; } }
@media (prefers-reduced-motion: reduce) { .paper-burst { display: none; } }
```

And JS:

```js
document.addEventListener('click', (e) => {
  if (reducedMotion) return;
  const btn = e.target.closest('.btn');
  if (!btn) return;
  const r = btn.getBoundingClientRect();
  for (let i = 0; i < 5; i++) {
    const p = document.createElement('div');
    p.className = 'paper-burst';
    p.style.left = (r.right - 12) + 'px';
    p.style.top = (r.top + 6) + 'px';
    p.style.setProperty('--dx', (Math.random() * 40 - 20) + 'px');
    p.style.setProperty('--dy', (-60 - Math.random() * 60) + 'px');
    p.style.setProperty('--rot', (Math.random() * 60 - 30) + 'deg');
    document.body.appendChild(p);
    setTimeout(() => p.remove(), 750);
  }
});
```

- [ ] **Step 5:** Reload. Click any button — papers fly out. Toggle macOS Reduce Motion → reload, verify no animation. Resize to 360px → verify mobile fallback. Commit.

```bash
git add prototypes/proto-13/index.html
git commit -m "feat(proto-13): reduced-motion + mobile fallback + button paper-burst"
```

---

## Self-Review (run after writing the plan)

**Spec coverage check** (each spec section → task):
- Cellora structure adapted to Mycroft → Tasks 2–9 (covers all 11 layout blocks)
- Persistent particle scene + 8 poses → Tasks 11–17
- IntersectionObserver state machine → Task 15
- Frosted privacy cube → Task 18
- Hero proto-02 verbatim + letterform end-pose → Tasks 11–13
- Plugin micro-behaviours (Spotlight/coJournalist/DataHound/Atelier) → Task 17
- Footer pile + giant brand → Tasks 9 + 15
- Reduced-motion + mobile fallback → Task 19
- Performance budget (≤900 particles, RAF pause when idle) → Tasks 11, 20
- Strict Cellora-light palette (no red) → Task 1 (palette vars), enforced throughout
- Browser-use validation per user CLAUDE.md → Tasks 10, 14, 21

**Placeholder scan:**
- Task 7 visual zones in plugin cards are intentional placeholders (the canvas behind handles their content); no in-code TBD.
- Task 9 testimonials are explicit `data-placeholder="true"` per resolved decision.
- Task 17 plugin behaviours have concrete formulas (no "implement appropriately").

**Type/name consistency:**
- `tick` is the unified loop name from Task 15 onward (renamed from `tickHero`).
- `sectionTargets`, `heroEndTargets`, `velocities`, `positions`, `rotations` are stable across tasks.
- `activePose` is the single source of truth for pose state.
- `POSE_BUILDERS`, `POSE_CAM`, `SECTION_POSE` use consistent keys (`hero`, `day`, `plugins`, `pricing`, `privacy`, `drift`, `footer`).

Plan ready for execution.
