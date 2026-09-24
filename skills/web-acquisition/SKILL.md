---
name: web-acquisition
description: Configured local (SearXNG + Crawl4AI) or API (Firecrawl) web search, scrape, and source preservation for Mycroft.
---

# Web Acquisition

Mycroft acquires sources using the installed acquisition policy:

- **Search** → `python3 "$MYCROFT_DIR/tools/searxng-search.py" "<query>"` (SearXNG or Firecrawl). Add `--limit N`; `--categories news` and `--time-range month` apply to SearXNG.
- **Scrape** → `python3 "$MYCROFT_DIR/tools/scrape.py" <url>` (Crawl4AI or Firecrawl → clean markdown). Local PDFs: `python3 "$MYCROFT_DIR/tools/scrape.py" <file.pdf> --pdf` (pdftotext).
- **Domain URL discovery** → `python3 "$MYCROFT_DIR/tools/sitemap.py" <domain>` (robots.txt / sitemap.xml enumeration).
- **Provenance-captured fetch/search** (chain of custody for fact-check) → `mycroft-fetch scrape <url>` / `mycroft-fetch search "<query>"` — writes an evidence record with `acquisition_method` (`crawl4ai` / `searxng` / `firecrawl`), a SHA-256, and the access timestamp.

**Local acquisition** selects SearXNG search and Crawl4AI scrape, without an API key or vendor account. Firecrawl is used only after a local failure and only when `acquisition.firecrawl` is `fallback`. CLI presence or an API key alone never enables cloud fallback.

**API-only acquisition** selects Firecrawl for both search and scrape and requires `FIRECRAWL_API_KEY`. It never probes SearXNG or starts/provisions Crawl4AI or Chromium. Content and queries are sent to Firecrawl; do not describe this route as local or sovereign.

Tools load `MYCROFT_CONFIG` when set; otherwise they use `MYCROFT_PROFILE_DIR/mycroft-config.json`. The default profile is `<Goose config>/mycroft`: on Unix, `${XDG_CONFIG_HOME}/goose` when XDG is absolute, otherwise `~/.config/goose`; on Windows, `%APPDATA%/Block/goose/config` (or `~/AppData/Roaming/Block/goose/config`). Invalid config, an explicitly selected missing config/profile, or a missing config in an existing profile fails without contacting a provider. Only unmanaged tools with no default profile retain a local-only default; configure cloud fallback explicitly.

## Use Cases

- Search for source material.
- Scrape known URLs into Markdown.
- Preserve raw web text under `sources/raw/`.
- Feed cleaned extracts into the `knowledge-workspace` write flow under Mycroft's namespace and verify every resulting document by reading it back.

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
