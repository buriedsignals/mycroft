#!/usr/bin/env python3
"""SearXNG web search for Mycroft recipes — sovereign default (no API key, no vendor).

    python3 "$MYCROFT_DIR/tools/searxng-search.py" "<query>"           # numbered results
    python3 "$MYCROFT_DIR/tools/searxng-search.py" "<query>" --json    # JSON for parsing
    python3 "$MYCROFT_DIR/tools/searxng-search.py" "<query>" --limit 15 --categories news --time-range month

Queries a local, self-hosted SearXNG JSON endpoint (SEARXNG_URL, default
http://localhost:8899). Paginates past the first page so obscure/long-tail
sources stay reachable. If SearXNG is unreachable and the `firecrawl` CLI is
present, falls back to it (optional escape hatch; the default path is sovereign).

Exit 0 on success; 3 if no provider can return results.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

DEFAULT_URL = "http://localhost:8899"
DEFAULT_PAGES = 3


def searxng(query: str, limit: int, categories: str | None, time_range: str | None) -> list[dict]:
    base = os.environ.get("SEARXNG_URL", DEFAULT_URL).rstrip("/")
    hits: list[dict] = []
    seen: set[str] = set()
    for page in range(1, DEFAULT_PAGES + 1):
        params = {"q": query, "format": "json", "pageno": page}
        if categories:
            params["categories"] = categories
        if time_range:
            params["time_range"] = time_range
        url = base + "/search?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "mycroft-search/1.0"})
        try:
            data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception as exc:  # noqa: BLE001
            if page == 1:
                raise ConnectionError(f"SearXNG unreachable at {base}: {exc}") from exc
            break
        results = data.get("results") or []
        if not results:
            break
        for r in results:
            u = r.get("url")
            if not u or u in seen:
                continue
            seen.add(u)
            hits.append(
                {
                    "url": u,
                    "title": r.get("title", "") or "",
                    "snippet": (r.get("content") or "")[:300],
                    "date": r.get("publishedDate"),
                    "engine": r.get("engine"),
                }
            )
            if len(hits) >= limit:
                return hits
    return hits


def firecrawl(query: str, limit: int) -> list[dict]:
    proc = subprocess.run(
        ["firecrawl", "search", query, "--limit", str(limit), "--json"],
        capture_output=True, text=True, timeout=90,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:300] or "firecrawl non-zero exit")
    web = (json.loads(proc.stdout).get("data") or {}).get("web", []) or []
    return [
        {"url": r.get("url", ""), "title": r.get("title", "") or "",
         "snippet": (r.get("description") or "")[:300], "date": r.get("date"), "engine": "firecrawl"}
        for r in web if r.get("url")
    ][:limit]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="searxng-search.py", description="Sovereign web search (SearXNG default).")
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--categories", default=None, help="e.g. news")
    ap.add_argument("--time-range", dest="time_range", default=None, help="e.g. month")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a numbered list")
    args = ap.parse_args(argv)

    try:
        hits = searxng(args.query, args.limit, args.categories, args.time_range)
    except ConnectionError as exc:
        if shutil.which("firecrawl"):
            print(f"[searxng down: {exc}] falling back to firecrawl", file=sys.stderr)
            try:
                hits = firecrawl(args.query, args.limit)
            except Exception as fc_exc:  # noqa: BLE001
                print(f"search failed (searxng + firecrawl): {fc_exc}", file=sys.stderr)
                return 3
        else:
            print(f"search failed: {exc}", file=sys.stderr)
            return 3

    if args.json:
        print(json.dumps(hits, indent=2))
    else:
        for i, h in enumerate(hits, 1):
            date = f" ({h['date'][:10]})" if h.get("date") else ""
            print(f"{i}. {h['title']}{date}\n   {h['url']}")
            if h["snippet"]:
                print(f"   {h['snippet']}")
    if not hits:
        print("no results", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
