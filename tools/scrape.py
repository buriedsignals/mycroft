#!/usr/bin/env python3
"""Fetch a URL (or parse a local PDF) to clean markdown for Mycroft recipes.

    python3 "$MYCROFT_DIR/tools/scrape.py" <url>                 # markdown to stdout
    python3 "$MYCROFT_DIR/tools/scrape.py" <url> --format html
    python3 "$MYCROFT_DIR/tools/scrape.py" <file.pdf> --pdf

Sovereign default: Crawl4AI (open-source, no API key) via `uvx --from crawl4ai
crwl`. On a Crawl4AI failure the optional Firecrawl escape hatch is used *only*
if the `firecrawl` CLI is present (KTD4/KTD6 in tools/GOING_LOCAL.md). Local PDFs
go through pdftotext. The ladder is Crawl4AI -> (optional) Firecrawl.

Exit 0 on success; 3 on a fetch/parse failure with the error on stderr.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

CRAWL4AI_TIMEOUT = 90


def _crwl_cmd(url: str) -> list[str]:
    # crawl4ai CLI: `crwl crawl <url> -o markdown` (Playwright-rendered, markdown to
    # stdout). Prefer the installed `crwl` (uv tool, fast); fall back to a uvx
    # cold-start so it still works before install-time provisioning.
    base = ["crwl"] if shutil.which("crwl") else ["uvx", "--from", "crawl4ai", "crwl"]
    return base + ["crawl", url, "-o", "markdown"]


def crawl4ai(url: str, fmt: str) -> str:
    # crawl4ai's clean output is markdown; html/links are not first-class in the
    # CLI, so we always request markdown (the recipe default).
    proc = subprocess.run(_crwl_cmd(url), capture_output=True, text=True, timeout=CRAWL4AI_TIMEOUT)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError(proc.stderr.strip()[:400] or "crawl4ai returned empty")
    return proc.stdout


def firecrawl(url: str, fmt: str) -> str:
    proc = subprocess.run(
        ["firecrawl", "scrape", url, "--format", fmt],
        capture_output=True, text=True, timeout=CRAWL4AI_TIMEOUT,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:400] or "firecrawl non-zero exit")
    return proc.stdout


def parse_pdf(path: str) -> str:
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext not installed (poppler)")
    proc = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"], capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:400] or "pdftotext failed")
    return proc.stdout


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="scrape.py", description="Fetch a URL (or local PDF) to markdown (Crawl4AI default).")
    ap.add_argument("target", help="URL, or a local .pdf path with --pdf")
    ap.add_argument("--format", default="markdown", help="markdown (default) | html | links")
    ap.add_argument("--pdf", action="store_true", help="treat target as a local PDF path")
    args = ap.parse_args(argv)

    try:
        if args.pdf:
            out = parse_pdf(args.target)
        else:
            try:
                out = crawl4ai(args.target, args.format)
            except Exception as exc:  # noqa: BLE001 - crawl4ai failed/blocked
                if shutil.which("firecrawl"):
                    print(f"[crawl4ai failed: {exc}] falling back to firecrawl", file=sys.stderr)
                    out = firecrawl(args.target, args.format)
                else:
                    raise
    except Exception as exc:  # noqa: BLE001
        print(f"scrape failed: {exc}", file=sys.stderr)
        return 3

    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
