#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/home" "$tmp/bin"

HOME="$tmp/home" XDG_CONFIG_HOME="$tmp/home/.config" XDG_DATA_HOME="$tmp/home/.local/share" \
  SEARXNG_URL="http://127.0.0.1:1" PATH="/usr/bin:/bin" \
  bash scripts/mycroft-doctor >"$tmp/none.out" 2>&1 || true

grep -qF 'FAIL  scrape backend unavailable' "$tmp/none.out" \
  || fail "doctor did not fail when every scrape backend was absent"
grep -qF 'FAIL  search backend unavailable' "$tmp/none.out" \
  || fail "doctor did not fail when every search backend was absent"

cat > "$tmp/bin/firecrawl" <<'FIRECRAWL'
#!/usr/bin/env bash
[ "${1:-}" = "--version" ] && { echo 'firecrawl test'; exit 0; }
exit 2
FIRECRAWL
chmod +x "$tmp/bin/firecrawl"

HOME="$tmp/home" XDG_CONFIG_HOME="$tmp/home/.config" XDG_DATA_HOME="$tmp/home/.local/share" \
  FIRECRAWL_API_KEY="fc-test" SEARXNG_URL="http://127.0.0.1:1" \
  PATH="$tmp/bin:/usr/bin:/bin" bash scripts/mycroft-doctor >"$tmp/fallback.out" 2>&1 || true

grep -qF 'OK    scrape backend available (Firecrawl fallback)' "$tmp/fallback.out" \
  || fail "doctor did not accept the configured Firecrawl scrape fallback"
grep -qF 'OK    search backend available (Firecrawl fallback)' "$tmp/fallback.out" \
  || fail "doctor did not accept the configured Firecrawl search fallback"

echo "doctor backend checks passed"
