#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

# shellcheck source=../scripts/install-preflight.sh
. scripts/install-preflight.sh

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/bin" "$tmp/home"

cat > "$tmp/catalog.json" <<'CATALOG'
{"dependencies":{"firecrawl-cli":"1.9.8","@tobilu/qmd":"2.5.3"}}
CATALOG
[ "$(mycroft_catalog_dependency_pin "$tmp/catalog.json" firecrawl-cli)" = "1.9.8" ] \
  || fail "catalog dependency pin lookup did not return firecrawl-cli's version"
[ "$(mycroft_catalog_dependency_pin "$tmp/catalog.json" @tobilu/qmd)" = "2.5.3" ] \
  || fail "catalog dependency pin lookup did not return QMD's version"
[ -z "$(mycroft_catalog_dependency_pin "$tmp/catalog.json" missing)" ] \
  || fail "missing catalog dependency unexpectedly returned a version"

cat > "$tmp/bin/npm" <<'NPM'
#!/usr/bin/env bash
case "$*" in
  "config get prefix") printf '/mycroft-test-root-owned\n' ;;
  "config set prefix "*) printf '%s\n' "$*" >> "$MYCROFT_NPM_TEST_LOG" ;;
  *) exit 2 ;;
esac
NPM
chmod +x "$tmp/bin/npm"

MYCROFT_NPM_TEST_LOG="$tmp/npm.log"
export MYCROFT_NPM_TEST_LOG
HOME="$tmp/home" PATH="$tmp/bin:/usr/bin:/bin" mycroft_prepare_npm_prefix

grep -qF "config set prefix $tmp/home/.npm-global" "$tmp/npm.log" \
  || fail "non-writable global npm prefix was not redirected to the user"

if MYCROFT_OS=Linux mycroft_preflight_linux_build_tools mycroft-test-missing-compiler 2>"$tmp/toolchain.err"; then
  fail "missing Linux build tool passed preflight"
fi
grep -qF 'sudo apt-get install -y curl git python3 python3-pip build-essential' "$tmp/toolchain.err" \
  || fail "Linux toolchain failure did not include the one-shot dependency command"

if MYCROFT_OS=Darwin MYCROFT_ASSUME_YES=0 PATH="/usr/bin:/bin" \
  mycroft_ensure_brew </dev/null 2>"$tmp/brew.err"; then
  fail "headless Homebrew preflight silently continued without explicit consent"
fi
grep -qF 'MYCROFT_ASSUME_YES=1' "$tmp/brew.err" \
  || fail "headless Homebrew refusal did not explain the opt-in"

echo "install preflight checks passed"
