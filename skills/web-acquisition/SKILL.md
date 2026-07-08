---
name: web-acquisition
description: Sovereign web search, scrape, and source preservation (SearXNG + Crawl4AI) for Mycroft and Spotlight workflows; Firecrawl is an optional fallback.
---

# Web Acquisition

Mycroft acquires web sources **sovereign by default** — no API key, no vendor account:

- **Search** → `python3 "$MYCROFT_DIR/tools/searxng-search.py" "<query>"` (local SearXNG JSON API). Add `--limit N`, `--categories news`, or `--time-range month`.
- **Scrape** → `python3 "$MYCROFT_DIR/tools/scrape.py" <url>` (Crawl4AI → clean markdown). Local PDFs: `python3 "$MYCROFT_DIR/tools/scrape.py" <file.pdf> --pdf` (pdftotext).
- **Domain URL discovery** → `python3 "$MYCROFT_DIR/tools/sitemap.py" <domain>` (robots.txt / sitemap.xml enumeration).
- **Provenance-captured fetch/search** (chain of custody for fact-check) → `mycroft-fetch scrape <url>` / `mycroft-fetch search "<query>"` — writes an evidence record with `acquisition_method` (`crawl4ai` / `searxng` / `firecrawl`), a SHA-256, and the access timestamp.

**Firecrawl is the optional escape hatch**, reached only when `FIRECRAWL_API_KEY` is set and the sovereign tool can't do the job — a hard anti-bot target that defeats Crawl4AI (scrape), or an exhaustive search union. With no key, Mycroft runs pure-sovereign; the tools fall back to Firecrawl automatically when it is present.

## Use Cases

- Search for source material.
- Scrape known URLs into Markdown.
- Preserve raw web text under `sources/raw/`.
- Feed cleaned extracts into `obsidian-ingest`.

## Rules

- Keep the original URL in frontmatter.
- Record access date.
- Prefer primary sources over summaries.
- Do not treat scraped content as verified by default.

## Storage

For Mycroft durable knowledge:

- raw scrape: `sources/raw/`
- cleaned extract: `sources/processed/`
- durable notes: `wiki/`

For Spotlight casework:

- raw case scrape: `cases/{project}/research/`
- preserved evidence: `evidence/` or `captures/`
