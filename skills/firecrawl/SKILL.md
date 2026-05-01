---
name: firecrawl
description: Firecrawl usage for web search, scrape, and source preservation in Mycroft and Spotlight workflows.
---

# Firecrawl

Use Firecrawl when selected in setup and `FIRECRAWL_API_KEY` is available.

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
