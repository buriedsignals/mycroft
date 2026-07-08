#!/usr/bin/env python3
"""Enumerate a domain's URL space for Mycroft recipes — the sovereign replacement
for `firecrawl map` (SearXNG is keyword search and cannot enumerate a domain).

    python3 "$MYCROFT_DIR/tools/sitemap.py" example.com
    python3 "$MYCROFT_DIR/tools/sitemap.py" example.com --match news --limit 500

Strategy: robots.txt `Sitemap:` entries -> sitemap.xml (index + urlset, gzip-aware)
-> URL list, same-registrable-domain only. Falls back to the common
`/sitemap.xml` path. Optional `--match` substring filter. Discovery only; use
the scrape recipe to fetch a page.

Exit 0 on success (even with 0 URLs); 3 on a hard fetch failure.
"""
from __future__ import annotations

import argparse
import gzip
import re
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "mycroft-sitemap/1.0"}
LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.I)


def _norm_domain(d: str) -> str:
    d = d.strip()
    if "://" not in d:
        d = "https://" + d
    return urllib.parse.urlparse(d).netloc.lower()


def _registrable(host: str) -> str:
    parts = host.replace("www.", "", 1).split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def _fetch(url: str) -> bytes:
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
    if url.endswith(".gz") or raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except Exception:  # noqa: BLE001
            pass
    return raw


def _sitemaps_from_robots(base: str) -> list[str]:
    try:
        txt = _fetch(base + "/robots.txt").decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        return []
    return [ln.split(":", 1)[1].strip() for ln in txt.splitlines() if ln.lower().startswith("sitemap:")]


def crawl_sitemaps(domain: str, limit: int, match: str | None) -> list[str]:
    host = _norm_domain(domain)
    base = "https://" + host
    reg = _registrable(host)
    queue = _sitemaps_from_robots(base) or [base + "/sitemap.xml"]
    seen_maps: set[str] = set()
    urls: list[str] = []
    seen_urls: set[str] = set()
    while queue and len(urls) < limit:
        sm = queue.pop(0)
        if sm in seen_maps:
            continue
        seen_maps.add(sm)
        try:
            body = _fetch(sm).decode("utf-8", "ignore")
        except Exception:  # noqa: BLE001
            continue
        for loc in LOC.findall(body):
            if loc.endswith(".xml") or loc.endswith(".xml.gz"):  # nested sitemap index
                queue.append(loc)
                continue
            if _registrable(urllib.parse.urlparse(loc).netloc.lower()) != reg:
                continue
            if match and match.lower() not in loc.lower():
                continue
            if loc in seen_urls:
                continue
            seen_urls.add(loc)
            urls.append(loc)
            if len(urls) >= limit:
                break
    return urls


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sitemap.py", description="Enumerate a domain's URLs via robots.txt/sitemap.xml.")
    ap.add_argument("domain")
    ap.add_argument("--match", default=None, help="only URLs containing this substring")
    ap.add_argument("--limit", type=int, default=1000)
    args = ap.parse_args(argv)

    try:
        urls = crawl_sitemaps(args.domain, args.limit, args.match)
    except Exception as exc:  # noqa: BLE001
        print(f"sitemap enumeration failed: {exc}", file=sys.stderr)
        return 3
    for u in urls:
        print(u)
    print(f"{len(urls)} URLs" + (" (no sitemap found — try the scrape recipe on the homepage and harvest links)"
                                 if not urls else ""), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
