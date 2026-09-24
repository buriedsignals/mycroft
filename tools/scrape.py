#!/usr/bin/env python3
"""Fetch a URL (or parse a local PDF) to clean markdown for Mycroft recipes.

    python3 "$MYCROFT_DIR/tools/scrape.py" <url>                 # markdown to stdout
    python3 "$MYCROFT_DIR/tools/scrape.py" <url> --format html
    python3 "$MYCROFT_DIR/tools/scrape.py" <file.pdf> --pdf

The installed acquisition policy selects Crawl4AI or Firecrawl directly. Local
acquisition uses Firecrawl only when fallback is explicitly enabled. Standalone
tools without an installed config default to local-only. PDFs use pdftotext.

Exit 0 on success; 3 on a fetch/parse failure with the error on stderr.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from acquisition_policy import load_acquisition

FETCH_TIMEOUT = 90  # seconds; shared budget for the crawl4ai and firecrawl subprocesses


def _crwl_cmd(url: str) -> list[str]:
    # crawl4ai CLI: `crwl crawl <url> -o markdown` (Playwright-rendered, markdown to
    # stdout). Prefer the installed `crwl` (uv tool, fast); fall back to a uvx
    # cold-start so it still works before install-time provisioning.
    base = ["crwl"] if shutil.which("crwl") else ["uvx", "--from", "crawl4ai", "crwl"]
    return base + ["crawl", url, "-o", "markdown"]


def crawl4ai(url: str, fmt: str) -> str:
    # crawl4ai's clean output is markdown; html/links are not first-class in the
    # CLI, so we always request markdown (the recipe default).
    proc = subprocess.run(_crwl_cmd(url), capture_output=True, text=True, timeout=FETCH_TIMEOUT)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError(proc.stderr.strip()[:400] or "crawl4ai returned empty")
    return proc.stdout


def firecrawl(url: str, fmt: str) -> str:
    proc = subprocess.run(
        ["firecrawl", "scrape", url, "--format", fmt],
        capture_output=True, text=True, timeout=FETCH_TIMEOUT,
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
    ap = argparse.ArgumentParser(prog="scrape.py", description="Fetch a URL using the configured acquisition backend, or parse a local PDF.")
    ap.add_argument("target", help="URL, or a local .pdf path with --pdf")
    ap.add_argument("--format", default="markdown", help="markdown (default) | html | links")
    ap.add_argument("--pdf", action="store_true", help="treat target as a local PDF path")
    args = ap.parse_args(argv)

    try:
        if args.pdf:
            out = parse_pdf(args.target)
        else:
            policy = load_acquisition()
            if policy["scrape"] == "firecrawl":
                out = firecrawl(args.target, args.format)
            else:
                try:
                    out = crawl4ai(args.target, args.format)
                except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
                    if policy["firecrawl"] != "fallback":
                        raise
                    print(f"[crawl4ai failed: {exc}] falling back to firecrawl", file=sys.stderr)
                    out = firecrawl(args.target, args.format)
    except Exception as exc:  # noqa: BLE001
        print(f"scrape failed: {exc}", file=sys.stderr)
        return 3

    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
