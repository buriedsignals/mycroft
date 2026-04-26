# Mycroft landing redesign — Plan 1 : Shared scaffolding

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up `/prototypes/` as a Bun + Vite + TypeScript workspace with all shared modules ready, so prototypes A/B/C can plug in. At the end, `bun run dev` opens a landing page that shows "Mycroft" rendered in Three.js (blackletter, grainy, on cool gray paper) plus a paper overlay (grain + folds), and exposes 3 stub routes for the prototypes.

**Architecture:** Standalone Vite project under `/prototypes/`, separate from the legacy single-file `index.html` at the repo root. Self-hosted fonts. Three.js title rendered with `troika-three-text` (MSDF) plus a custom displacement/noise shader. Paper overlay implemented as a layered SVG/canvas. Public-domain corpus stored as plain text. PRetext is **not** integrated in this plan — it lands in Plan 2.

**Tech Stack:**
- Bun (runtime + package manager + test runner)
- Vite (dev server + bundler)
- TypeScript (strict)
- Three.js + troika-three-text
- bun:test for unit tests
- Self-hosted fonts: UnifrakturMaguntia, Libre Caslon Text (Google Fonts, OFL)
- Public-domain corpus: Project Gutenberg + archive.org

**Spec reference:** `docs/superpowers/specs/2026-04-26-mycroft-landing-redesign-design.md` — §5 (Stack), §6 (Content corpus), §4 (Shared visual direction).

---

## File structure (created by this plan)

```
/prototypes/
  .gitignore
  README.md
  bunfig.toml
  package.json
  tsconfig.json
  vite.config.ts
  index.html                       (landing for /prototypes/, links a/b/c)
  src/
    main.ts                        (boots the demo on /prototypes/index.html)
    fonts.css                      (@font-face declarations)
    style.css                      (base reset, paper bg, body type)
  shared/
    palette.ts                     (color tokens)
    content.ts                     (Mycroft product copy, structured)
    fonts/                         (self-hosted woff2)
      UnifrakturMaguntia-Regular.woff2
      LibreCaslonText-Regular.woff2
      LibreCaslonText-Italic.woff2
      LibreCaslonText-Bold.woff2
    corpus/                        (public-domain archive texts)
      README.md
      bly-mad-house.txt
      wells-southern-horrors.txt
      riis-other-half.txt
      wwi-times.txt
    title/
      MycroftTitle.ts              (Three.js headline class)
      shaders/
        ink-displacement.vert
        ink-displacement.frag
    paper/
      PaperOverlay.ts              (grain + folds overlay)
  tests/
    palette.test.ts
    content.test.ts
    MycroftTitle.test.ts
    PaperOverlay.test.ts
```

Each file has one responsibility:
- `palette.ts` — color tokens, no logic
- `content.ts` — typed product copy, no logic
- `MycroftTitle.ts` — Three.js scene + text mesh + shader, exposes `mount(canvas)` / `dispose()`
- `PaperOverlay.ts` — DOM overlay, exposes `mount(target)` / `dispose()`
- shaders — GLSL only
- `main.ts` — wires the above into the demo page

---

## Task 1: Initialize Bun + Vite + TypeScript project under `/prototypes/`

**Files:**
- Create: `prototypes/package.json`
- Create: `prototypes/bunfig.toml`
- Create: `prototypes/tsconfig.json`
- Create: `prototypes/vite.config.ts`
- Create: `prototypes/.gitignore`
- Create: `prototypes/index.html`
- Create: `prototypes/src/main.ts`
- Create: `prototypes/src/style.css`

- [ ] **Step 1: Create directory and initial files**

```bash
mkdir -p prototypes/src prototypes/shared prototypes/tests
cd prototypes
```

- [ ] **Step 2: Write `prototypes/package.json`**

```json
{
  "name": "mycroft-prototypes",
  "private": true,
  "type": "module",
  "version": "0.0.1",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "bun test",
    "typecheck": "tsc --noEmit"
  },
  "devDependencies": {
    "@types/bun": "latest",
    "typescript": "^5.6.0",
    "vite": "^5.4.0"
  },
  "dependencies": {
    "three": "^0.169.0",
    "@types/three": "^0.169.0",
    "troika-three-text": "^0.52.0"
  }
}
```

- [ ] **Step 3: Write `prototypes/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "strict": true,
    "noImplicitAny": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "allowImportingTsExtensions": false,
    "skipLibCheck": true,
    "types": ["bun-types", "vite/client"],
    "isolatedModules": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": {
      "@shared/*": ["shared/*"]
    }
  },
  "include": ["src/**/*", "shared/**/*", "tests/**/*", "vite.config.ts"]
}
```

- [ ] **Step 4: Write `prototypes/vite.config.ts`**

```ts
import { defineConfig } from "vite";
import path from "node:path";

export default defineConfig({
  root: ".",
  resolve: {
    alias: {
      "@shared": path.resolve(__dirname, "shared"),
    },
  },
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "index.html"),
      },
    },
  },
  assetsInclude: ["**/*.txt", "**/*.glsl", "**/*.vert", "**/*.frag"],
});
```

- [ ] **Step 5: Write `prototypes/bunfig.toml`**

```toml
[install]
exact = false
```

- [ ] **Step 6: Write `prototypes/.gitignore`**

```
node_modules/
dist/
.DS_Store
*.log
.vite/
```

- [ ] **Step 7: Write `prototypes/src/style.css`** (base reset + paper background)

```css
:root {
  --paper: #e8e8e6;
  --ink: #0e0e0e;
  --ink-muted: #4a4a48;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; }
body {
  background: var(--paper);
  color: var(--ink);
  font-family: "Libre Caslon Text", Georgia, serif;
  font-size: 18px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
a { color: inherit; }
```

- [ ] **Step 8: Write `prototypes/index.html`** (placeholder landing with 3 prototype links)

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mycroft — prototypes</title>
<link rel="stylesheet" href="/src/style.css">
</head>
<body>
<main id="app">
  <canvas id="title" aria-hidden="true"></canvas>
  <h1 class="visually-hidden">Mycroft — landing prototypes</h1>
  <nav>
    <a href="/a-newspaper/">A — Living newspaper</a>
    <a href="/b-archives/">B — Archives that speak</a>
    <a href="/c-transmission/">C — The transmission</a>
  </nav>
</main>
<script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [ ] **Step 9: Write `prototypes/src/main.ts`** (skeleton — will mount Title + Paper later)

```ts
console.info("[mycroft prototypes] boot");
```

- [ ] **Step 10: Install dependencies and verify dev server**

```bash
cd prototypes
bun install
bun run dev
```

Expected: Vite reports a dev URL (e.g. `http://localhost:5173`). Open it: page shows the empty `<canvas>` and the 3 nav links. No console errors except (eventually) the 404s on the prototype routes.

- [ ] **Step 11: Verify typecheck passes**

```bash
cd prototypes
bun run typecheck
```

Expected: no output (no errors).

- [ ] **Step 12: Commit**

```bash
git add prototypes/.gitignore prototypes/README.md prototypes/bunfig.toml \
  prototypes/package.json prototypes/tsconfig.json prototypes/vite.config.ts \
  prototypes/index.html prototypes/src/
git commit -m "feat(prototypes): scaffold Bun + Vite + TS workspace"
```

(Note: `README.md` is created in Task 9 — don't worry if it's not present yet at this commit; just stage what exists.)

---

## Task 2: `palette.ts` — design tokens

**Files:**
- Create: `prototypes/shared/palette.ts`
- Create: `prototypes/tests/palette.test.ts`

- [ ] **Step 1: Write the failing test**

`prototypes/tests/palette.test.ts`:
```ts
import { describe, it, expect } from "bun:test";
import { palette } from "@shared/palette";

describe("palette", () => {
  it("should expose the cool gray paper background", () => {
    expect(palette.paper).toBe("#e8e8e6");
  });

  it("should expose the deep ink color", () => {
    expect(palette.ink).toBe("#0e0e0e");
  });

  it("should expose a muted ink for secondary text", () => {
    expect(palette.inkMuted).toBe("#4a4a48");
  });

  it("should freeze the palette object so tokens cannot be mutated", () => {
    expect(Object.isFrozen(palette)).toBe(true);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd prototypes
bun test tests/palette.test.ts
```

Expected: FAIL — `Cannot find module '@shared/palette'`.

- [ ] **Step 3: Write the minimal implementation**

`prototypes/shared/palette.ts`:
```ts
export const palette = Object.freeze({
  paper: "#e8e8e6",
  ink: "#0e0e0e",
  inkMuted: "#4a4a48",
} as const);

export type Palette = typeof palette;
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
cd prototypes
bun test tests/palette.test.ts
```

Expected: 4 pass.

- [ ] **Step 5: Commit**

```bash
git add prototypes/shared/palette.ts prototypes/tests/palette.test.ts
git commit -m "feat(prototypes): add shared palette tokens"
```

---

## Task 3: `content.ts` — structured product copy

**Files:**
- Create: `prototypes/shared/content.ts`
- Create: `prototypes/tests/content.test.ts`
- Read: `index.html` (current landing — copy source)

- [ ] **Step 1: Write the failing test**

`prototypes/tests/content.test.ts`:
```ts
import { describe, it, expect } from "bun:test";
import { content } from "@shared/content";

describe("content", () => {
  it("should expose the hero block", () => {
    expect(content.hero.eyebrow).toBe("AI for journalists");
    expect(content.hero.title).toContain("morning brief");
    expect(content.hero.lede).toContain("opinionated extension pack");
    expect(content.hero.ctas).toHaveLength(2);
    expect(content.hero.ctas[0]?.label).toBe("Set up Mycroft");
    expect(content.hero.meta).toHaveLength(3);
  });

  it("should expose the day-with section with 6 day cards", () => {
    expect(content.dayWith.title).toBe("A day with Mycroft");
    expect(content.dayWith.cards).toHaveLength(6);
    expect(content.dayWith.cards[0]?.time).toBe("7 am");
    expect(content.dayWith.cards[0]?.heading).toBe("Morning brief");
  });

  it("should expose the model section with 4 cards", () => {
    expect(content.model.title).toBe("A model trained on journalism");
    expect(content.model.cards).toHaveLength(4);
  });

  it("should expose privacy section with 6 items", () => {
    expect(content.privacy.title).toBe("Privacy by default");
    expect(content.privacy.items).toHaveLength(6);
  });

  it("should expose install section with 3 steps", () => {
    expect(content.install.title).toBe("Install in five minutes");
    expect(content.install.steps).toHaveLength(3);
  });

  it("should expose plugins section with 4 plugins", () => {
    expect(content.plugins.title).toBe("Plugins");
    expect(content.plugins.cards).toHaveLength(4);
    expect(content.plugins.cards[0]?.badge).toBe("at launch");
  });

  it("should expose studio section with membership and consulting", () => {
    expect(content.studio.title).toBe("From the team behind Mycroft");
    expect(content.studio.membership.heading).toBe("Pro Membership");
    expect(content.studio.consulting.heading).toBe("Consulting");
  });

  it("should expose CTA footer and site footer", () => {
    expect(content.ctaFooter.heading).toBe("Built by journalists, for journalists.");
    expect(content.footer.note).toContain("Buried Signals");
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd prototypes
bun test tests/content.test.ts
```

Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

Read `index.html` (repo root) for the source copy. Then write `prototypes/shared/content.ts`:

```ts
export type Cta = { label: string; href: string; primary: boolean };
export type DayCard = { time: string; heading: string; body: string };
export type ModelCard = { eyebrow: string; heading: string; body: string };
export type PrivacyItem = { heading: string; body: string };
export type InstallStep = { heading: string; body: string };
export type PluginCard = { badge: "at launch" | "May 2026"; heading: string; body: string };

export type Content = {
  hero: { eyebrow: string; title: string; lede: string; ctas: Cta[]; meta: string[] };
  dayWith: { title: string; lead: string; cards: DayCard[] };
  model: { title: string; lead: string; cards: ModelCard[] };
  privacy: { title: string; lead: string; items: PrivacyItem[] };
  install: { title: string; lead: string; steps: InstallStep[]; cta: Cta };
  plugins: { title: string; lead: string; cards: PluginCard[] };
  studio: {
    title: string;
    membership: {
      eyebrow: string;
      heading: string;
      sub: string;
      features: string[];
      price: string;
    };
    consulting: {
      heading: string;
      sub: string;
      services: { heading: string; body: string; clients?: string }[];
    };
  };
  ctaFooter: { heading: string; body: string; ctas: Cta[] };
  footer: { note: string; links: { label: string; href: string }[] };
};

export const content: Content = {
  hero: {
    eyebrow: "AI for journalists",
    title:
      "Your morning brief, before coffee\nYour fact-check, in minutes\nYour sources, kept private",
    lede:
      "Mycroft is an opinionated extension pack for Goose — the open-source agent runtime. It turns your laptop into a journalism workstation: daily digests from your beat, SIFT fact-checking, vault Q&A with citations, investigations via Spotlight, social scraping via Apify.",
    ctas: [
      { label: "Set up Mycroft", href: "/setup.html", primary: true },
      {
        label: "View on GitHub",
        href: "https://github.com/buriedsignals/mycroft",
        primary: false,
      },
    ],
    meta: [
      "~$6/month moderate use · $0 in local mode",
      "Zero data retention by default",
      "Open-weight models only",
    ],
  },
  dayWith: {
    title: "A day with Mycroft",
    lead:
      "Not a chatbot bolted on. Recipes designed for the way investigative journalists actually work — built into your vault, your beat sources, your writing flow.",
    cards: [
      {
        time: "7 am",
        heading: "Morning brief",
        body:
          "Open your laptop. A digest is in your vault: 8 items ranked by editorial value. Pulled from your X/Twitter bookmarks, your AgentMail newsletters, and overnight web coverage for your beat. Every claim cited, every source linked.",
      },
      {
        time: "10 am",
        heading: "Fact-check a draft",
        body:
          "Run fact-check on an article draft. Mycroft returns per-claim verdicts — verified, unverified, contradicted, mischaracterized — via SIFT methodology. Every quote traced to origin. Every statistic cited to the primary source.",
      },
      {
        time: "2 pm",
        heading: "Investigate a lead",
        body:
          "Tell Mycroft to investigate. Spotlight takes over: multi-phase OSINT research, adversarial SIFT fact-checking, evidence grounding, knowledge-vault ingestion. Full audit trail for editorial and legal defensibility.",
      },
      {
        time: "4 pm",
        heading: "Vault Q&A",
        body:
          "\"What do I already have on this topic?\" Mycroft answers from your own notes + live web in a single shot, with every claim cited to a vault path or URL. Reviewing three months of reporting takes minutes, not hours.",
      },
      {
        time: "Evening",
        heading: "Newsletter in, signal out",
        body:
          "A newsletter lands in your AgentMail inbox. Mycroft extracts the data points, names the sources, flags the unverified claims, and writes it into your vault with entity cross-references. You read the output, not the inbox.",
      },
      {
        time: "Ongoing",
        heading: "Monitored beat",
        body:
          "coJournalist runs 24/7 on its cloud backend — scheduled scouts watch the sources you care about (web pages, social handles, council calendars, court filings). New signal feeds tomorrow's morning brief.",
      },
    ],
  },
  model: {
    title: "A model trained on journalism",
    lead:
      "Most AI tools run on generalists — chatbots trained on web crawls, instruction-tuned to be agreeable. Mycroft ships with a fine-tuned, abliterated Qwen 3.5 trained specifically on investigative journalism methodology. Open-weight. Yours to own. Two sizes — 9B (16 GB+ laptops) and 35B (64 GB+ workstations).",
    cards: [
      {
        eyebrow: "What it knows",
        heading: "Methodology, not small talk",
        body:
          "SIFT framework for verification. 1000+ OSINT tools catalogued. Source protection protocols. Attribution rules. Evidence grounding. Chain of custody for investigative work.",
      },
      {
        eyebrow: "Where it runs",
        heading: "Your laptop. Your weights.",
        body:
          "llama-server (GGUF) on macOS, Linux, Windows. Zero network egress. Download the 9B from Hugging Face, audit the weights, run it forever. No vendor can take it away.",
      },
      {
        eyebrow: "What it costs",
        heading: "$0 after download",
        body:
          "No per-token billing, no subscription, no credits. Electricity and ~5 GB of SSD for the 9B (Q4_K_M). For investigative work at volume, local inference beats cloud on every axis — including cost.",
      },
      {
        eyebrow: "Why it matters",
        heading: "The right reflexes, baked in",
        body:
          "Abliterated — this model won't soft-refuse legitimate research requests the way stock Claude / GPT will. Trained instead to cite every claim, flag unverified assertions, and decline requests that would actually burn a source.",
      },
    ],
  },
  privacy: {
    title: "Privacy by default",
    lead: "Investigative journalism has a threat model. Mycroft is built to match it.",
    items: [
      {
        heading: "Zero Data Retention",
        body:
          "Only providers with ZDR (Fireworks, Together) are shipped defaults. No Claude, OpenAI, or Gemini — their retention policies aren't suitable. All models are open-weight. Hosted in the US or Europe.",
      },
      {
        heading: "Local-first mode",
        body:
          "Flip one toggle and every inference runs on your machine — a fine-tuned Qwen on MLX or llama-server. Zero network egress. $0/month. For sensitive sources and confidential documents.",
      },
      {
        heading: "Your keys, your machine",
        body:
          "The setup page runs entirely in your browser. API keys are embedded in the .command you download. Nothing passes through any server we own. The setup form has no backend.",
      },
      {
        heading: "Firecrawl only for the web",
        body:
          "Web fetching is the most-abused surface. Mycroft uses Firecrawl exclusively — no WebFetch, no surveillance-adjacent scraping middlemen. Your query patterns stay yours.",
      },
      {
        heading: "Your vault stays on disk",
        body:
          "Findings write to your Obsidian vault. Nothing syncs to our infrastructure. Local files, local search, local memory.",
      },
      {
        heading: "No telemetry",
        body:
          "No analytics, no crash reporting, no phone home. Mycroft and Goose are open-source; you can read every line.",
      },
    ],
  },
  install: {
    title: "Install in five minutes",
    lead:
      "No terminal-wrangling. The setup page generates a single script with your config baked in. One file, one run.",
    steps: [
      {
        heading: "Fill in the setup form",
        body:
          "Pick cloud or local mode, add your API keys (optional ones can be skipped), select the plugins you want. Everything stays in your browser.",
      },
      {
        heading: "Download mycroft-setup.command",
        body:
          "A bash script with your selections embedded. Review it first — nothing hidden, your keys are right there in plain sight.",
      },
      {
        heading: "Run it",
        body:
          "Double-click or paste ~/Downloads/mycroft-setup.command into Terminal. The script brew-installs Goose + Obsidian if missing, clones the pack, configures your shell. Open a new terminal and you're working.",
      },
    ],
    cta: { label: "Set up Mycroft →", href: "/setup.html", primary: true },
  },
  plugins: {
    title: "Plugins",
    lead: "Mycroft is the spine. Plugins clip in and ship on their own cadence.",
    cards: [
      {
        badge: "at launch",
        heading: "Spotlight",
        body:
          "OSINT investigation system. Multi-phase research, adversarial SIFT fact-checking, evidence grounding, knowledge-vault ingestion.",
      },
      {
        badge: "at launch",
        heading: "coJournalist",
        body:
          "Beat-monitoring engine. Scheduled scouts, change detection, relevance scoring. Web-hosted runs 24/7; self-host option available.",
      },
      {
        badge: "May 2026",
        heading: "DataHound",
        body:
          "Government and public-data API discovery with automated monitoring. Turn obscure open-data endpoints into queryable beats.",
      },
      {
        badge: "May 2026",
        heading: "Atelier",
        body:
          "Visual production — charts (Datawrapper, D3), maps (Maptiler), video, infographics, social cards. Data and narrative to publication-ready visuals.",
      },
    ],
  },
  studio: {
    title: "From the team behind Mycroft",
    membership: {
      eyebrow: "Launching May 2026",
      heading: "Pro Membership",
      sub: "Investigations with AI. The tools to run your own.",
      features: [
        "Collaborative investigations — shared leads, data, and methodology",
        "Live bootcamps, workshops, and events",
        "Hosted Pro tier of the agent extensions — coJournalist, Navigator, Spotlight, DataHound",
        "Investigation methodologies and AI techniques, in depth",
      ],
      price: "From $25/mo · 400+ journalists already reading",
    },
    consulting: {
      heading: "Consulting",
      sub: "I train newsrooms to investigate with AI.",
      services: [
        {
          heading: "Workshops & training",
          body:
            "I run hands-on sessions where journalists investigate live stories with AI.",
          clients: "Le Temps · MAZ Journalistenschule · Republik · 20 Minuten",
        },
        {
          heading: "Custom AI tooling",
          body:
            "I build AI systems into your editorial workflow — archive search, source monitoring, research agents, whatever the newsroom needs.",
          clients: "MediaStorm",
        },
        {
          heading: "Investigation collaborations",
          body: "Visual production and AI pipelines paired with your field reporting.",
          clients: "The New Humanitarian",
        },
      ],
    },
  },
  ctaFooter: {
    heading: "Built by journalists, for journalists.",
    body:
      "Open source. Self-hostable. No lock-in. No surveillance. Just the tool you wish you'd had three investigations ago.",
    ctas: [
      { label: "Set up Mycroft", href: "/setup.html", primary: true },
      {
        label: "View on GitHub",
        href: "https://github.com/buriedsignals/mycroft",
        primary: false,
      },
    ],
  },
  footer: {
    note: "Mycroft is a Buried Signals project.",
    links: [
      { label: "Source", href: "https://github.com/buriedsignals/mycroft" },
      { label: "Set up", href: "/setup.html" },
      { label: "Goose", href: "https://goose-docs.ai/" },
    ],
  },
};
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
cd prototypes
bun test tests/content.test.ts
```

Expected: 8 pass.

- [ ] **Step 5: Commit**

```bash
git add prototypes/shared/content.ts prototypes/tests/content.test.ts
git commit -m "feat(prototypes): structured Mycroft product copy"
```

---

## Task 4: Public-domain corpus — download and clean

**Files:**
- Create: `prototypes/shared/corpus/README.md`
- Create: `prototypes/shared/corpus/bly-mad-house.txt`
- Create: `prototypes/shared/corpus/wells-southern-horrors.txt`
- Create: `prototypes/shared/corpus/riis-other-half.txt`
- Create: `prototypes/shared/corpus/wwi-times.txt`
- Create: `prototypes/tests/corpus.test.ts`

- [ ] **Step 1: Look up Project Gutenberg IDs**

Open in a browser:
- Nellie Bly *Ten Days in a Mad-House* — search `https://www.gutenberg.org/ebooks/search/?query=ten+days+in+a+mad-house` → note the ebook ID (e.g. 1280)
- Ida B. Wells *Southern Horrors* — search `https://www.gutenberg.org/ebooks/search/?query=southern+horrors+wells` → note the ID
- Jacob Riis *How the Other Half Lives* — search `https://www.gutenberg.org/ebooks/search/?query=how+the+other+half+lives` → note the ID

Record the IDs you find. The plain-text URL pattern is `https://www.gutenberg.org/cache/epub/<ID>/pg<ID>.txt`.

For WWI Times of London dispatches (no PG), use archive.org: search `https://archive.org/details/?query=times+london+1914+dispatch` and pick a single representative reportage in plain text format.

- [ ] **Step 2: Download each corpus file**

Replace `<BLY_ID>`, `<WELLS_ID>`, `<RIIS_ID>` with the IDs from Step 1, and `<WWI_ARCHIVE_PATH>` with the chosen archive.org plaintext URL.

```bash
cd prototypes/shared/corpus
curl -sSL "https://www.gutenberg.org/cache/epub/<BLY_ID>/pg<BLY_ID>.txt" -o bly-mad-house.raw.txt
curl -sSL "https://www.gutenberg.org/cache/epub/<WELLS_ID>/pg<WELLS_ID>.txt" -o wells-southern-horrors.raw.txt
curl -sSL "https://www.gutenberg.org/cache/epub/<RIIS_ID>/pg<RIIS_ID>.txt" -o riis-other-half.raw.txt
curl -sSL "<WWI_ARCHIVE_PATH>" -o wwi-times.raw.txt
```

Verify each file is >50KB (typical PG novel-length text).

- [ ] **Step 3: Strip Project Gutenberg headers/footers**

PG files include a license header before the text and a license footer after. The body is delimited by lines starting with `*** START OF` and `*** END OF`. Run for each PG file:

```bash
cd prototypes/shared/corpus
for name in bly-mad-house wells-southern-horrors riis-other-half; do
  awk '/\*\*\* START OF .* \*\*\*/{flag=1; next} /\*\*\* END OF .* \*\*\*/{flag=0} flag' "$name.raw.txt" > "$name.txt"
done
# WWI from archive.org may not have these markers — copy as-is, then manually trim if needed:
cp wwi-times.raw.txt wwi-times.txt
rm *.raw.txt
```

Verify each cleaned file: `wc -l *.txt` — should be hundreds to thousands of lines. Open each in a text editor and confirm: starts with the actual chapter/text, no PG license boilerplate.

- [ ] **Step 4: Write `prototypes/shared/corpus/README.md`**

```markdown
# Corpus — public-domain journalism

Late 19th / early 20th century investigative journalism, used as background atmosphere in the Mycroft landing prototypes. All works are in the public domain in the United States.

| File | Author | Title | Year | Source |
|---|---|---|---|---|
| `bly-mad-house.txt` | Nellie Bly | Ten Days in a Mad-House | 1887 | Project Gutenberg #<BLY_ID> |
| `wells-southern-horrors.txt` | Ida B. Wells | Southern Horrors: Lynch Law in All Its Phases | 1892 | Project Gutenberg #<WELLS_ID> |
| `riis-other-half.txt` | Jacob Riis | How the Other Half Lives | 1890 | Project Gutenberg #<RIIS_ID> |
| `wwi-times.txt` | (anon., The Times of London) | WWI dispatches | 1914–1918 | archive.org — `<WWI_ARCHIVE_PATH>` |

Files are cleaned of license headers/footers so the text begins with the actual reportage.

## License

Public domain in the US. Project Gutenberg license terms only apply to PG-formatted distributions; cleaned plain-text bodies of public-domain works are not encumbered.
```

(Replace placeholders with the IDs / URLs you actually used.)

- [ ] **Step 5: Write a smoke test for the corpus**

`prototypes/tests/corpus.test.ts`:
```ts
import { describe, it, expect } from "bun:test";
import { readFile, stat } from "node:fs/promises";
import { resolve } from "node:path";

const CORPUS_DIR = resolve(import.meta.dir, "..", "shared", "corpus");

const FILES = [
  { name: "bly-mad-house.txt", keyword: "Bly" },
  { name: "wells-southern-horrors.txt", keyword: "lynch" },
  { name: "riis-other-half.txt", keyword: "tenement" },
  { name: "wwi-times.txt", keyword: "" },
];

describe("corpus files", () => {
  for (const { name, keyword } of FILES) {
    it(`${name} should exist and be substantial`, async () => {
      const path = resolve(CORPUS_DIR, name);
      const s = await stat(path);
      expect(s.size).toBeGreaterThan(20_000);
    });
    if (keyword) {
      it(`${name} should contain the expected keyword "${keyword}"`, async () => {
        const text = await readFile(resolve(CORPUS_DIR, name), "utf8");
        expect(text.toLowerCase()).toContain(keyword.toLowerCase());
      });
    }
  }
});
```

- [ ] **Step 6: Run the smoke test**

```bash
cd prototypes
bun test tests/corpus.test.ts
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add prototypes/shared/corpus/ prototypes/tests/corpus.test.ts
git commit -m "feat(prototypes): public-domain corpus (Bly, Wells, Riis, WWI Times)"
```

---

## Task 5: Self-hosted fonts

**Files:**
- Create: `prototypes/shared/fonts/UnifrakturMaguntia-Regular.woff2`
- Create: `prototypes/shared/fonts/LibreCaslonText-Regular.woff2`
- Create: `prototypes/shared/fonts/LibreCaslonText-Italic.woff2`
- Create: `prototypes/shared/fonts/LibreCaslonText-Bold.woff2`
- Create: `prototypes/src/fonts.css`
- Modify: `prototypes/index.html` (add fonts.css link)

- [ ] **Step 1: Download font files**

Use google-webfonts-helper (`https://gwfh.mranftl.com/fonts`) — paste each family name, select latin subset, woff2 format only, click "Download files".

Place the downloaded files in `prototypes/shared/fonts/` and rename to:
- `UnifrakturMaguntia-Regular.woff2`
- `LibreCaslonText-Regular.woff2`
- `LibreCaslonText-Italic.woff2`
- `LibreCaslonText-Bold.woff2`

(If google-webfonts-helper isn't accessible, alternative: open `https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&display=swap` in a browser, view source, copy the woff2 URLs and `curl` them.)

- [ ] **Step 2: Verify font files**

```bash
ls -la prototypes/shared/fonts/
file prototypes/shared/fonts/*.woff2
```

Expected: 4 files, each `Web Open Font Format (Version 2)`, each ~10–80 KB.

- [ ] **Step 3: Write `prototypes/src/fonts.css`**

```css
@font-face {
  font-family: "UnifrakturMaguntia";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url("/shared/fonts/UnifrakturMaguntia-Regular.woff2") format("woff2");
}
@font-face {
  font-family: "Libre Caslon Text";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url("/shared/fonts/LibreCaslonText-Regular.woff2") format("woff2");
}
@font-face {
  font-family: "Libre Caslon Text";
  font-style: italic;
  font-weight: 400;
  font-display: swap;
  src: url("/shared/fonts/LibreCaslonText-Italic.woff2") format("woff2");
}
@font-face {
  font-family: "Libre Caslon Text";
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url("/shared/fonts/LibreCaslonText-Bold.woff2") format("woff2");
}
```

- [ ] **Step 4: Wire fonts.css into the demo page**

Edit `prototypes/index.html` — add inside `<head>`, before the `style.css` link:

```html
<link rel="stylesheet" href="/src/fonts.css">
```

Then to verify visually, replace the `<nav>` block in `index.html` body temporarily with:

```html
<nav style="font-family: 'Libre Caslon Text', serif; padding: 2rem;">
  <p>Caslon body — the quick brown fox jumps over the lazy dog.</p>
  <p style="font-style: italic;">Caslon italic — the quick brown fox.</p>
  <p style="font-weight: 700;">Caslon bold — the quick brown fox.</p>
  <h2 style="font-family: 'UnifrakturMaguntia', serif; font-size: 4rem;">Mycroft</h2>
  <ul>
    <li><a href="/a-newspaper/">A — Living newspaper</a></li>
    <li><a href="/b-archives/">B — Archives that speak</a></li>
    <li><a href="/c-transmission/">C — The transmission</a></li>
  </ul>
</nav>
```

- [ ] **Step 5: Verify visually in dev server**

```bash
cd prototypes
bun run dev
```

Open the URL. Confirm: the 3 Caslon paragraphs render in proper Caslon (not the system serif fallback), and "Mycroft" renders in blackletter UnifrakturMaguntia. Open devtools Network tab → reload → confirm the 4 woff2 files load with status 200.

- [ ] **Step 6: Commit**

```bash
git add prototypes/shared/fonts/ prototypes/src/fonts.css prototypes/index.html
git commit -m "feat(prototypes): self-hosted Caslon + UnifrakturMaguntia fonts"
```

---

## Task 6: `PaperOverlay.ts` — grain + folds

**Files:**
- Create: `prototypes/shared/paper/PaperOverlay.ts`
- Create: `prototypes/tests/PaperOverlay.test.ts`

- [ ] **Step 1: Write the failing test**

`prototypes/tests/PaperOverlay.test.ts`:
```ts
import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { GlobalRegistrator } from "@happy-dom/global-registrator";

beforeEach(() => GlobalRegistrator.register());
afterEach(() => GlobalRegistrator.unregister());

describe("PaperOverlay", () => {
  it("should mount an SVG layer with grain and folds inside the target element", async () => {
    const { PaperOverlay } = await import("@shared/paper/PaperOverlay");
    const target = document.createElement("div");
    target.style.width = "1000px";
    target.style.height = "600px";
    document.body.appendChild(target);

    const overlay = new PaperOverlay({ folds: 4 });
    overlay.mount(target);

    const svg = target.querySelector("svg.paper-overlay");
    expect(svg).not.toBeNull();
    expect(svg?.querySelector("filter#paper-grain")).not.toBeNull();
    expect(svg?.querySelectorAll("line.fold").length).toBe(4);
  });

  it("should remove its DOM nodes on dispose", async () => {
    const { PaperOverlay } = await import("@shared/paper/PaperOverlay");
    const target = document.createElement("div");
    document.body.appendChild(target);
    const overlay = new PaperOverlay({ folds: 3 });
    overlay.mount(target);
    expect(target.querySelector("svg.paper-overlay")).not.toBeNull();
    overlay.dispose();
    expect(target.querySelector("svg.paper-overlay")).toBeNull();
  });
});
```

- [ ] **Step 2: Install happy-dom for DOM testing under bun:test**

```bash
cd prototypes
bun add -d @happy-dom/global-registrator
```

- [ ] **Step 3: Run the test to verify it fails**

```bash
cd prototypes
bun test tests/PaperOverlay.test.ts
```

Expected: FAIL — module not found.

- [ ] **Step 4: Write the implementation**

`prototypes/shared/paper/PaperOverlay.ts`:
```ts
const SVG_NS = "http://www.w3.org/2000/svg";

export type PaperOverlayOptions = {
  folds?: number;        // number of vertical fold lines
  grainOpacity?: number; // 0..1, default 0.18
  foldOpacity?: number;  // 0..1, default 0.05
};

export class PaperOverlay {
  private svg: SVGSVGElement | null = null;
  private opts: Required<PaperOverlayOptions>;

  constructor(opts: PaperOverlayOptions = {}) {
    this.opts = {
      folds: opts.folds ?? 4,
      grainOpacity: opts.grainOpacity ?? 0.18,
      foldOpacity: opts.foldOpacity ?? 0.05,
    };
  }

  mount(target: HTMLElement): void {
    if (this.svg) return;

    const svg = document.createElementNS(SVG_NS, "svg") as SVGSVGElement;
    svg.classList.add("paper-overlay");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("preserveAspectRatio", "none");
    svg.setAttribute("viewBox", "0 0 100 100");
    Object.assign(svg.style, {
      position: "absolute",
      inset: "0",
      width: "100%",
      height: "100%",
      pointerEvents: "none",
      mixBlendMode: "multiply",
    } as CSSStyleDeclaration);

    // Grain filter
    const defs = document.createElementNS(SVG_NS, "defs");
    const filter = document.createElementNS(SVG_NS, "filter");
    filter.id = "paper-grain";
    filter.setAttribute("x", "0%");
    filter.setAttribute("y", "0%");
    filter.setAttribute("width", "100%");
    filter.setAttribute("height", "100%");

    const turb = document.createElementNS(SVG_NS, "feTurbulence");
    turb.setAttribute("type", "fractalNoise");
    turb.setAttribute("baseFrequency", "0.9");
    turb.setAttribute("numOctaves", "2");
    turb.setAttribute("stitchTiles", "stitch");
    filter.appendChild(turb);

    const colorMatrix = document.createElementNS(SVG_NS, "feColorMatrix");
    colorMatrix.setAttribute("type", "saturate");
    colorMatrix.setAttribute("values", "0");
    filter.appendChild(colorMatrix);

    const componentTransfer = document.createElementNS(SVG_NS, "feComponentTransfer");
    const funcA = document.createElementNS(SVG_NS, "feFuncA");
    funcA.setAttribute("type", "linear");
    funcA.setAttribute("slope", String(this.opts.grainOpacity));
    componentTransfer.appendChild(funcA);
    filter.appendChild(componentTransfer);

    defs.appendChild(filter);
    svg.appendChild(defs);

    const grainRect = document.createElementNS(SVG_NS, "rect");
    grainRect.setAttribute("width", "100");
    grainRect.setAttribute("height", "100");
    grainRect.setAttribute("filter", "url(#paper-grain)");
    grainRect.setAttribute("fill", "#000");
    svg.appendChild(grainRect);

    // Vertical folds
    const stepX = 100 / (this.opts.folds + 1);
    for (let i = 1; i <= this.opts.folds; i++) {
      const line = document.createElementNS(SVG_NS, "line");
      line.classList.add("fold");
      line.setAttribute("x1", String(i * stepX));
      line.setAttribute("x2", String(i * stepX));
      line.setAttribute("y1", "0");
      line.setAttribute("y2", "100");
      line.setAttribute("stroke", "#000");
      line.setAttribute("stroke-width", "0.05");
      line.setAttribute("opacity", String(this.opts.foldOpacity));
      svg.appendChild(line);
    }

    target.style.position ||= "relative";
    target.appendChild(svg);
    this.svg = svg;
  }

  dispose(): void {
    this.svg?.remove();
    this.svg = null;
  }
}
```

- [ ] **Step 5: Run the test to verify it passes**

```bash
cd prototypes
bun test tests/PaperOverlay.test.ts
```

Expected: 2 pass.

- [ ] **Step 6: Visual smoke test in `index.html`**

Edit `prototypes/src/main.ts` to mount the overlay on the body:

```ts
import { PaperOverlay } from "@shared/paper/PaperOverlay";

console.info("[mycroft prototypes] boot");

const overlay = new PaperOverlay({ folds: 4, grainOpacity: 0.22, foldOpacity: 0.06 });
overlay.mount(document.body);
```

Reload the dev page. Expected: subtle grain texture visible across the whole background, 4 thin vertical fold lines spaced evenly. Background reads as paper, not flat color.

- [ ] **Step 7: Commit**

```bash
git add prototypes/shared/paper/ prototypes/tests/PaperOverlay.test.ts \
  prototypes/src/main.ts prototypes/package.json prototypes/bun.lockb
git commit -m "feat(prototypes): paper overlay (SVG grain + folds)"
```

---

## Task 7: `MycroftTitle.ts` — Three.js headline (plain MSDF)

**Files:**
- Create: `prototypes/shared/title/MycroftTitle.ts`
- Create: `prototypes/tests/MycroftTitle.test.ts`
- Modify: `prototypes/src/main.ts`

- [ ] **Step 1: Write the failing test**

`prototypes/tests/MycroftTitle.test.ts`:
```ts
import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { GlobalRegistrator } from "@happy-dom/global-registrator";

beforeEach(() => GlobalRegistrator.register());
afterEach(() => GlobalRegistrator.unregister());

describe("MycroftTitle", () => {
  it("should construct without throwing and expose mount/dispose", async () => {
    const { MycroftTitle } = await import("@shared/title/MycroftTitle");
    const title = new MycroftTitle({ text: "Mycroft" });
    expect(typeof title.mount).toBe("function");
    expect(typeof title.dispose).toBe("function");
  });

  it("should default text to 'Mycroft'", async () => {
    const { MycroftTitle } = await import("@shared/title/MycroftTitle");
    const title = new MycroftTitle();
    expect(title.text).toBe("Mycroft");
  });
});
```

(Note: we cannot meaningfully unit-test the Three.js render under happy-dom — there is no WebGL. Construction + API surface only. The visual check happens in Step 5.)

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd prototypes
bun test tests/MycroftTitle.test.ts
```

Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

`prototypes/shared/title/MycroftTitle.ts`:
```ts
import * as THREE from "three";
import { Text } from "troika-three-text";
import { palette } from "@shared/palette";

export type MycroftTitleOptions = {
  text?: string;
  fontUrl?: string; // path to UnifrakturMaguntia woff2/ttf
  color?: string;
};

const DEFAULT_FONT = "/shared/fonts/UnifrakturMaguntia-Regular.woff2";

export class MycroftTitle {
  readonly text: string;
  private readonly fontUrl: string;
  private readonly color: string;

  private renderer: THREE.WebGLRenderer | null = null;
  private scene: THREE.Scene | null = null;
  private camera: THREE.OrthographicCamera | null = null;
  private mesh: Text | null = null;
  private rafId: number | null = null;
  private resizeObserver: ResizeObserver | null = null;
  private canvas: HTMLCanvasElement | null = null;

  constructor(opts: MycroftTitleOptions = {}) {
    this.text = opts.text ?? "Mycroft";
    this.fontUrl = opts.fontUrl ?? DEFAULT_FONT;
    this.color = opts.color ?? palette.ink;
  }

  mount(canvas: HTMLCanvasElement): void {
    if (this.renderer) return;
    this.canvas = canvas;

    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      premultipliedAlpha: true,
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    camera.position.z = 1;

    const text = new Text();
    text.text = this.text;
    text.font = this.fontUrl;
    text.fontSize = 0.45;
    text.anchorX = "center";
    text.anchorY = "middle";
    text.color = this.color;
    text.sync();

    scene.add(text);

    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    this.mesh = text;

    this.handleResize();
    this.resizeObserver = new ResizeObserver(() => this.handleResize());
    this.resizeObserver.observe(canvas);

    this.loop();
  }

  private handleResize(): void {
    if (!this.renderer || !this.canvas || !this.camera) return;
    const w = this.canvas.clientWidth;
    const h = this.canvas.clientHeight;
    this.renderer.setSize(w, h, false);
    const aspect = w / h;
    this.camera.left = -aspect;
    this.camera.right = aspect;
    this.camera.top = 1;
    this.camera.bottom = -1;
    this.camera.updateProjectionMatrix();
  }

  private loop = (): void => {
    if (!this.renderer || !this.scene || !this.camera) return;
    this.renderer.render(this.scene, this.camera);
    this.rafId = requestAnimationFrame(this.loop);
  };

  dispose(): void {
    if (this.rafId !== null) cancelAnimationFrame(this.rafId);
    this.rafId = null;

    this.resizeObserver?.disconnect();
    this.resizeObserver = null;

    this.mesh?.dispose();
    this.mesh = null;
    this.scene = null;
    this.camera = null;

    this.renderer?.dispose();
    this.renderer = null;
    this.canvas = null;
  }
}
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
cd prototypes
bun test tests/MycroftTitle.test.ts
```

Expected: 2 pass.

- [ ] **Step 5: Wire MycroftTitle into the demo page**

Edit `prototypes/src/main.ts`:

```ts
import { PaperOverlay } from "@shared/paper/PaperOverlay";
import { MycroftTitle } from "@shared/title/MycroftTitle";

console.info("[mycroft prototypes] boot");

const overlay = new PaperOverlay({ folds: 4, grainOpacity: 0.22, foldOpacity: 0.06 });
overlay.mount(document.body);

const canvas = document.querySelector<HTMLCanvasElement>("#title");
if (canvas) {
  Object.assign(canvas.style, {
    display: "block",
    width: "100vw",
    height: "60vh",
  } as CSSStyleDeclaration);
  const title = new MycroftTitle();
  title.mount(canvas);
}
```

Also revert the temporary nav block in `prototypes/index.html` (replace the `<nav style="...">...</nav>` from Task 5 step 4 with the original simple nav from Task 1 step 8). The body becomes:

```html
<main id="app">
  <canvas id="title" aria-hidden="true"></canvas>
  <h1 class="visually-hidden">Mycroft — landing prototypes</h1>
  <nav>
    <a href="/a-newspaper/">A — Living newspaper</a>
    <a href="/b-archives/">B — Archives that speak</a>
    <a href="/c-transmission/">C — The transmission</a>
  </nav>
</main>
```

- [ ] **Step 6: Visual smoke test**

```bash
cd prototypes
bun run dev
```

Open the URL. Expected: "Mycroft" renders in blackletter, deep ink, centered, large, on the cool gray paper background. Grain and folds are visible. No console errors. Resize the window: the title scales to fit.

- [ ] **Step 7: Commit**

```bash
git add prototypes/shared/title/MycroftTitle.ts prototypes/tests/MycroftTitle.test.ts \
  prototypes/src/main.ts prototypes/index.html prototypes/package.json prototypes/bun.lockb
git commit -m "feat(prototypes): Three.js Mycroft headline (MSDF, blackletter)"
```

---

## Task 8: Ink-displacement shader — grain on the title mesh

**Files:**
- Create: `prototypes/shared/title/shaders/ink-displacement.vert`
- Create: `prototypes/shared/title/shaders/ink-displacement.frag`
- Modify: `prototypes/shared/title/MycroftTitle.ts`

troika-three-text exposes its underlying material; we customize via `text.material = ...` only at the cost of losing SDF rendering. Better: use troika's `customDepthMaterial` / shader injection hooks (`text.outlineColor`, etc.), or chain a post-process pass. For Plan 1 we take the simplest path that achieves grain: a **post-process pass** over the rendered scene that applies noise to dark fragments only.

- [ ] **Step 1: Write the vertex shader**

`prototypes/shared/title/shaders/ink-displacement.vert`:
```glsl
varying vec2 vUv;

void main() {
  vUv = uv;
  gl_Position = vec4(position, 1.0);
}
```

- [ ] **Step 2: Write the fragment shader**

`prototypes/shared/title/shaders/ink-displacement.frag`:
```glsl
precision highp float;

uniform sampler2D tDiffuse;
uniform vec2 uResolution;
uniform float uGrainStrength; // 0..1
uniform float uTime;

varying vec2 vUv;

// 2D hash → pseudo-random
float hash(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}

void main() {
  vec4 src = texture2D(tDiffuse, vUv);

  // Grain magnitude scaled by darkness of source (only ink takes grain)
  float darkness = 1.0 - max(max(src.r, src.g), src.b);
  float n = hash(vUv * uResolution + vec2(uTime * 0.01, 0.0));
  float grain = (n - 0.5) * uGrainStrength * darkness;

  vec3 col = clamp(src.rgb + grain, 0.0, 1.0);

  // Slightly bias dark areas darker for inkier look
  col = mix(col, col * 0.92, darkness * 0.4);

  gl_FragColor = vec4(col, src.a);
}
```

- [ ] **Step 3: Modify `MycroftTitle.ts` to apply the post-process**

Add the imports and field at the top of the class:

```ts
import inkVert from "./shaders/ink-displacement.vert?raw";
import inkFrag from "./shaders/ink-displacement.frag?raw";
```

Add a render-target + quad-pass setup. Replace the `loop` and add a `composer` private field. Full updated class shown below (replace the entire class body):

```ts
export class MycroftTitle {
  readonly text: string;
  private readonly fontUrl: string;
  private readonly color: string;

  private renderer: THREE.WebGLRenderer | null = null;
  private scene: THREE.Scene | null = null;
  private camera: THREE.OrthographicCamera | null = null;
  private mesh: Text | null = null;
  private rafId: number | null = null;
  private resizeObserver: ResizeObserver | null = null;
  private canvas: HTMLCanvasElement | null = null;

  // Post-process
  private renderTarget: THREE.WebGLRenderTarget | null = null;
  private postScene: THREE.Scene | null = null;
  private postCamera: THREE.OrthographicCamera | null = null;
  private postQuad: THREE.Mesh | null = null;
  private postUniforms: {
    tDiffuse: { value: THREE.Texture | null };
    uResolution: { value: THREE.Vector2 };
    uGrainStrength: { value: number };
    uTime: { value: number };
  } | null = null;

  constructor(opts: MycroftTitleOptions = {}) {
    this.text = opts.text ?? "Mycroft";
    this.fontUrl = opts.fontUrl ?? DEFAULT_FONT;
    this.color = opts.color ?? palette.ink;
  }

  mount(canvas: HTMLCanvasElement): void {
    if (this.renderer) return;
    this.canvas = canvas;

    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      premultipliedAlpha: true,
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    camera.position.z = 1;

    const text = new Text();
    text.text = this.text;
    text.font = this.fontUrl;
    text.fontSize = 0.45;
    text.anchorX = "center";
    text.anchorY = "middle";
    text.color = this.color;
    text.sync();
    scene.add(text);

    // Post-process scene
    const renderTarget = new THREE.WebGLRenderTarget(2, 2, {
      type: THREE.HalfFloatType,
      depthBuffer: false,
      stencilBuffer: false,
    });
    const postScene = new THREE.Scene();
    const postCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const uniforms = {
      tDiffuse: { value: renderTarget.texture },
      uResolution: { value: new THREE.Vector2(2, 2) },
      uGrainStrength: { value: 0.35 },
      uTime: { value: 0 },
    };
    const postMat = new THREE.ShaderMaterial({
      vertexShader: inkVert,
      fragmentShader: inkFrag,
      uniforms,
      transparent: true,
    });
    const postQuad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), postMat);
    postScene.add(postQuad);

    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    this.mesh = text;
    this.renderTarget = renderTarget;
    this.postScene = postScene;
    this.postCamera = postCamera;
    this.postQuad = postQuad;
    this.postUniforms = uniforms;

    this.handleResize();
    this.resizeObserver = new ResizeObserver(() => this.handleResize());
    this.resizeObserver.observe(canvas);

    this.loop();
  }

  private handleResize(): void {
    if (!this.renderer || !this.canvas || !this.camera || !this.renderTarget || !this.postUniforms) return;
    const w = this.canvas.clientWidth;
    const h = this.canvas.clientHeight;
    const dpr = this.renderer.getPixelRatio();
    this.renderer.setSize(w, h, false);
    this.renderTarget.setSize(Math.floor(w * dpr), Math.floor(h * dpr));
    this.postUniforms.uResolution.value.set(w * dpr, h * dpr);
    const aspect = w / h;
    this.camera.left = -aspect;
    this.camera.right = aspect;
    this.camera.top = 1;
    this.camera.bottom = -1;
    this.camera.updateProjectionMatrix();
  }

  private loop = (): void => {
    if (!this.renderer || !this.scene || !this.camera || !this.renderTarget
        || !this.postScene || !this.postCamera || !this.postUniforms) return;

    this.postUniforms.uTime.value = performance.now();

    this.renderer.setRenderTarget(this.renderTarget);
    this.renderer.clear();
    this.renderer.render(this.scene, this.camera);

    this.renderer.setRenderTarget(null);
    this.renderer.clear();
    this.renderer.render(this.postScene, this.postCamera);

    this.rafId = requestAnimationFrame(this.loop);
  };

  dispose(): void {
    if (this.rafId !== null) cancelAnimationFrame(this.rafId);
    this.rafId = null;

    this.resizeObserver?.disconnect();
    this.resizeObserver = null;

    this.mesh?.dispose();
    this.mesh = null;
    this.scene = null;
    this.camera = null;

    this.renderTarget?.dispose();
    this.renderTarget = null;

    if (this.postQuad) {
      this.postQuad.geometry.dispose();
      (this.postQuad.material as THREE.Material).dispose();
    }
    this.postQuad = null;
    this.postScene = null;
    this.postCamera = null;
    this.postUniforms = null;

    this.renderer?.dispose();
    this.renderer = null;
    this.canvas = null;
  }
}
```

- [ ] **Step 4: Re-run the unit test**

```bash
cd prototypes
bun test tests/MycroftTitle.test.ts
```

Expected: 2 pass (the API surface didn't change).

- [ ] **Step 5: Visual smoke test**

```bash
cd prototypes
bun run dev
```

Reload the page. Expected: "Mycroft" still renders in blackletter, but now with visible grain *on the dark strokes only* (the gray paper background remains clean). The grain should look static-ish but very subtly shimmer (uTime drives the noise seed).

If grain is too strong: lower `uGrainStrength.value` from `0.35` to `0.2` in `MycroftTitle.ts`.
If grain is invisible: raise to `0.5`.

- [ ] **Step 6: Commit**

```bash
git add prototypes/shared/title/shaders/ prototypes/shared/title/MycroftTitle.ts
git commit -m "feat(prototypes): ink displacement shader — grain on title strokes"
```

---

## Task 9: README for `/prototypes/`

**Files:**
- Create: `prototypes/README.md`

- [ ] **Step 1: Write `prototypes/README.md`**

```markdown
# Mycroft prototypes

Three parallel landing-page prototypes for Mycroft, sharing a Purgatoire-coded visual direction (cool gray paper, textured ink blackletter, massive negative space). Built with Bun + Vite + TypeScript + Three.js + PRetext.

See the design spec: `../docs/superpowers/specs/2026-04-26-mycroft-landing-redesign-design.md`.

## Run

```bash
bun install
bun run dev
```

Then open the URL printed by Vite (typically `http://localhost:5173/`). The landing page exposes 3 prototype routes:
- `/a-newspaper/` — Living newspaper
- `/b-archives/` — Archives that speak
- `/c-transmission/` — The transmission

(Routes 404 until each prototype lands in its own plan.)

## Test

```bash
bun test
bun run typecheck
```

## Layout

```
shared/
  palette.ts          color tokens (paper / ink / muted ink)
  content.ts          Mycroft product copy as typed structured data
  fonts/              self-hosted woff2 (UnifrakturMaguntia, Libre Caslon Text)
  corpus/             public-domain journalism (Bly, Wells, Riis, WWI Times)
  title/              Three.js Mycroft headline + ink displacement shader
  paper/              SVG grain + folds overlay
src/
  main.ts             demo page boot (mounts overlay + title)
  fonts.css           @font-face declarations
  style.css           paper background + body type
tests/                bun:test specs for shared modules
a-newspaper/          (Plan 3)
b-archives/           (Plan 4)
c-transmission/       (Plan 5)
```

## Conventions

- Code, identifiers, comments and commit messages in English (per `~/.claude/CLAUDE.md`).
- TDD where the test gives signal: yes for palette / content / overlay / API surface; smoke + visual for shaders / Three.js render.
- Each shared module exposes `mount(target)` and `dispose()` — no globals, no implicit lifecycles.
- No production polish until the winner is chosen. Prototypes are decision tools, not deploy targets.
```

- [ ] **Step 2: Commit**

```bash
git add prototypes/README.md
git commit -m "docs(prototypes): README — run, test, layout, conventions"
```

---

## Self-review (executed when this plan was written)

**Spec coverage:**
- §4 Shared visual direction — covered by Task 2 (palette), Task 5 (fonts), Task 6 (paper overlay), Task 7+8 (title with grain)
- §5 Stack — covered by Task 1 (Bun + Vite + TS + Three.js + troika)
- §5 Project layout — fully created across Tasks 1–8
- §6 Content corpus — Task 4 (archive corpus) + Task 3 (product copy)
- §7–9 Prototype-specific work — explicitly out of scope of this plan (handled in Plans 3–5)
- §10 Comparison matrix — informational, no implementation needed
- §11 Build order — this plan IS step 1
- §12 Accessibility — partial (paper overlay is `aria-hidden`, title has `aria-hidden` canvas + a `visually-hidden` `<h1>` fallback in index.html)
- §13 Open questions — PRetext packaging deferred to Plan 2; signature glyph and mobile fallback deferred to relevant prototype plans
- §14 Out of scope — respected (no setup.html change, no backend, no copy rewrite)

**Placeholder scan:** No "TBD"/"TODO"/"add appropriate" steps. The corpus task uses `<BLY_ID>` etc. as explicit lookup-required placeholders with the procedure to resolve them documented in Step 1 — these are external-data lookups, not plan placeholders.

**Type consistency:** `palette.paper`, `palette.ink`, `palette.inkMuted` used identically across palette.ts, MycroftTitle.ts, style.css. `content` shape used in tests matches the export. `MycroftTitle` API (`text` field, `mount(canvas)`, `dispose()`) consistent across Tasks 7 and 8.

---

## Execution choice

Plan complete and saved to `docs/superpowers/plans/2026-04-26-mycroft-landing-redesign-plan-1-shared-scaffolding.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
