# Scraping Migration: Firecrawl → Crawl4AI (SHIPPED — superseded)

**Status: superseded / done (shipped 2026-07-08).** This file was a 2026-07-03 proposal
that recommended a Scrapling-primary scraper. The migration shipped differently; the
proposal is kept only as a breadcrumb.

**What actually shipped:**

- **Scrape → Crawl4AI** (Markdown-shaped output suits the LLM pipelines) — *not*
  Scrapling. The Scrapling middle rung was evaluated and dropped.
- **Search → SearXNG** (local, self-hosted).
- **Firecrawl** is retained only as an *optional* fallback, reached when
  `FIRECRAWL_API_KEY` is set and a sovereign tool can't do the job.

See the `2026-07-08` entry in [`CHANGELOG.md`](CHANGELOG.md) and the `web-acquisition`
skill (`skills/web-acquisition/SKILL.md`) for the current design.
