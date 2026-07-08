#!/usr/bin/env bash
# Provision (idempotently) the Mycroft sovereign stack: Crawl4AI (scrape),
# poppler/pdftotext (PDF), SearXNG (search), and — opt-in — Tor (opsec).
#
# Run by install.sh on a fresh install AND by mycroft-update on every update, so
# an existing install that fast-forwards to the sovereign recipes also gains the
# SearXNG container + Crawl4AI backends instead of silently living on the
# Firecrawl fallback. Every step is best-effort and idempotent: a missing tool
# prints a warning and returns 0 — provisioning never aborts its caller or the
# unattended update.
#
# Config (all env-overridable):
#   INSTALL_CRAWL4AI / INSTALL_SEARXNG / INSTALL_TOR   1|0 (default 1/1/0)
#   SEARXNG_PORT (8899)  SEARXNG_CONTAINER (mycroft-searxng)
#   SEARXNG_IMAGE (searxng/searxng:latest)
#   SEARXNG_SETTINGS ($MYCROFT_PROFILE_DIR/searxng/settings.yml)
set -u

XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
MYCROFT_PROFILE_DIR="${MYCROFT_PROFILE_DIR:-$XDG_CONFIG_HOME/goose/mycroft}"
SEARXNG_PORT="${SEARXNG_PORT:-8899}"
SEARXNG_URL_VALUE="http://localhost:$SEARXNG_PORT"
SEARXNG_CONTAINER="${SEARXNG_CONTAINER:-mycroft-searxng}"
SEARXNG_IMAGE="${SEARXNG_IMAGE:-searxng/searxng:latest}"
SEARXNG_SETTINGS="${SEARXNG_SETTINGS:-$MYCROFT_PROFILE_DIR/searxng/settings.yml}"
INSTALL_CRAWL4AI="${INSTALL_CRAWL4AI:-1}"
INSTALL_SEARXNG="${INSTALL_SEARXNG:-1}"
INSTALL_TOR="${INSTALL_TOR:-0}"

have() { command -v "$1" >/dev/null 2>&1; }
ok()   { printf "  \033[1;32m+\033[0m %s\n" "$*"; }
warn() { printf "  \033[1;33m!\033[0m %s\n" "$*"; }

ensure_uv() {
  if have uv; then return 0; fi
  if have brew; then brew install uv >/dev/null 2>&1 && have uv && return 0; fi
  curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 || true
  export PATH="$HOME/.local/bin:$PATH"
  have uv
}

provision_crawl4ai() {
  # Sovereign scrape default (KTD5). scrape.py/mycroft-fetch prefer the installed
  # `crwl`; without it they cold-start via `uvx --from crawl4ai`. Installing it is a
  # best-effort speedup + browser-runtime provisioning, never a hard failure.
  [ "$INSTALL_CRAWL4AI" = "1" ] || return 0
  if have crwl; then
    ok "crawl4ai (crwl) present"
  elif ensure_uv; then
    uv tool install crawl4ai >/dev/null 2>&1 && ok "crawl4ai installed (uv tool)" \
      || warn "crawl4ai install failed; scrape will cold-start via uvx (or fall back to firecrawl)"
  else
    warn "uv unavailable; crawl4ai not installed. Scrape cold-starts via uvx if present."
  fi
  # Playwright chromium runtime crawl4ai renders with. crawl4ai-setup is a console
  # script `uv tool install crawl4ai` places on PATH; it is idempotent.
  if have crawl4ai-setup; then
    crawl4ai-setup >/dev/null 2>&1 && ok "crawl4ai browser runtime" \
      || warn "crawl4ai-setup failed; run 'crawl4ai-setup' manually if scraping fails"
  elif have crwl; then
    warn "crawl4ai-setup not on PATH; run it once to install the Playwright browser."
  fi
}

provision_poppler() {
  # pdftotext backs scrape.py --pdf and the civic-PDF recipe (replaces firecrawl-pdf).
  if have pdftotext; then ok "pdftotext present"; return 0; fi
  if have brew; then
    brew install poppler >/dev/null 2>&1 && ok "poppler (pdftotext)" \
      || warn "install poppler manually: brew install poppler"
  else
    warn "install poppler (pdftotext) via your package manager for PDF extraction"
  fi
}

provision_searxng() {
  # Sovereign search default (U5a). Runs a local SearXNG JSON endpoint on
  # $SEARXNG_PORT; the Mycroft search tools point at $SEARXNG_URL_VALUE. Needs
  # Docker — best-effort: absent Docker degrades to the Firecrawl search fallback
  # (if a key is present) rather than aborting.
  [ "$INSTALL_SEARXNG" = "1" ] || return 0
  if ! have docker; then
    warn "Docker not found — SearXNG (sovereign search) not provisioned. Install Docker, then re-run \`mycroft update\`; or point SEARXNG_URL at an existing instance. Search falls back to Firecrawl if a key is set."
    return 0
  fi
  mkdir -p "$(dirname "$SEARXNG_SETTINGS")"
  if [ ! -f "$SEARXNG_SETTINGS" ]; then
    local secret
    secret="$(head -c 32 /dev/urandom 2>/dev/null | od -An -tx1 | tr -d ' \n')"
    [ -n "$secret" ] || secret="mycroft_local_$$"
    cat > "$SEARXNG_SETTINGS" <<SXEOF
use_default_settings: true
server:
  secret_key: "$secret"
  limiter: false
  image_proxy: false
search:
  formats:
    - html
    - json
SXEOF
  fi
  if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^$SEARXNG_CONTAINER$"; then
    ok "SearXNG already running on $SEARXNG_URL_VALUE"
  elif docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^$SEARXNG_CONTAINER$"; then
    docker start "$SEARXNG_CONTAINER" >/dev/null 2>&1 && ok "SearXNG started on $SEARXNG_URL_VALUE" \
      || warn "SearXNG container present but failed to start; check 'docker logs $SEARXNG_CONTAINER'"
  elif docker run -d --name "$SEARXNG_CONTAINER" --restart unless-stopped \
        -p "$SEARXNG_PORT:8080" \
        -v "$SEARXNG_SETTINGS:/etc/searxng/settings.yml:ro" \
        "$SEARXNG_IMAGE" >/dev/null 2>&1; then
    ok "SearXNG on $SEARXNG_URL_VALUE"
  else
    warn "SearXNG container failed to start; check Docker and re-run."
  fi
}

provision_tor() {
  # Opt-in opsec (U7): the --tor fetch routes Crawl4AI through the local Tor SOCKS
  # proxy (9050). Off by default; enabled when the operator opts in.
  [ "$INSTALL_TOR" = "1" ] || return 0
  if have tor; then ok "tor present (SOCKS 9050)"; return 0; fi
  if have brew; then
    brew install tor >/dev/null 2>&1 && ok "tor (SOCKS 9050)" \
      || warn "install tor manually: brew install tor"
  else
    warn "install tor via your package manager for the opt-in --tor fetch (SOCKS 9050)"
  fi
}

provision_crawl4ai
provision_poppler
provision_searxng
provision_tor
exit 0
