# Scraping Migration: Firecrawl → Scrapling

Status: proposal (2026-07-03). Implementation is a separate session; this file records the
decision and the evidence.

## Recommendation

**Replace Firecrawl as the page-scraping service with
[Scrapling](https://github.com/D4Vinci/Scrapling) (`stealthy-fetch` mode) — open-source
(BSD-3), free, runs locally.** Alternate: [Crawl4AI](https://github.com/unclecode/crawl4ai)
where Markdown-shaped output for LLM pipelines matters more than latency.

## Why

Benchmarked 2026-07-03 in `tools/benchmarks` (report: `public/index.html`, data:
`results/combined-current.json`) across 8 hard civic/registry cases (Companies House,
Basel, Zurich, Lausanne, Bern, Bozeman, Madison, Zermatt):

- **Scrapling: 100%** coverage — the only tool besides Crawl4AI to clear a bot-protected US
  CivicPlus CMS (Bozeman), both Swiss cookie walls, and a cookie-check redirect chain.
  1.4–5.6s per fetch via a local Camoufox stealth browser. No API key, no credits.
- **Crawl4AI: 100%** — same coverage, Playwright-based, slower startup, native Markdown.
- **Firecrawl: 79%** — and on the Zermatt municipality homepage its `--only-main-content`
  extraction reduced the page to 437 bytes of image markdown while free tools captured it
  fully. Firecrawl is not a strict superset of the free options; it is a paid subset on
  this workload.

Caveats: Scrapling fetches from our own IP (no managed proxy pool — configure per-fetcher
proxies if a monitored source starts rate-limiting), and Firecrawl's `search`/`map`
endpoints are separate products, out of scope here.

## Firecrawl touchpoints in this repo (audit in the implementation session)

- `install/setup_server.py` (provisioning references Firecrawl)
- `instructions/journalism.md`, `instructions/mycroft-soul.md` (agent instructions naming
  Firecrawl as the fetch tool)
- `integration/sift-c2pa/DESIGN.md`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `CHANGELOG.md` (documentation references)
