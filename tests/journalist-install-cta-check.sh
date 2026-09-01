#!/usr/bin/env bash
# Public Pages keep managed join CTAs while README documents the shared Engine path.
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0
note() { printf 'FAIL  %s\n' "$1"; fail=1; }

if [ -e setup.html ]; then
  note "setup.html must be deleted; do not leave a curl|bash stub"
fi
if [ -e install/configure.html ]; then
  note "install/configure.html must be deleted; both credential paths use Engine outside Mycroft"
fi

JOIN='https://buriedsignals.com/join'
GITHUB='https://github.com/buriedsignals/mycroft'
BOOTSTRAP='https://navigator.indicator.media/api/artifacts/bootstrap/bsig/<platform>'

if ! grep -qF "$JOIN" index.html; then
  note "index.html missing Install href $JOIN"
fi
if ! grep -qF "$GITHUB" index.html; then
  note "index.html missing GitHub link"
fi
if ! grep -qF "$BOOTSTRAP" README.md; then
  note "README.md missing public Engine bootstrap descriptor"
fi
if ! grep -qF 'bsig configure plan mycroft' README.md; then
  note "README.md missing the single Engine planning path"
fi
if ! grep -qF 'bsig keys list' README.md; then
  note "README.md missing open-source credential ID discovery"
fi
if ! grep -qF 'protected bsig stdin/keychain path' index.html; then
  note "index.html missing the open-source credential path"
fi
if grep -qF 'setup.html' llms.txt || grep -qF 'local configurator' llms.txt; then
  note "llms.txt still describes the retired localhost credential collector"
fi
if grep -qF "$BOOTSTRAP" install.sh; then
  note "install.sh must remain a fail-closed pointer, not a second bootstrap path"
fi
if grep -qE 'href=["'"'"'][^"'"'"']*(setup|configure)\.html' index.html; then
  note "index.html still links to setup.html or configure.html"
fi
if grep -qE 'curl .*install\.sh' index.html; then
  note "index.html still advertises curl|bash install.sh"
fi
if grep -qF 'mycroft.buriedsignals.com/setup.html' sitemap.xml; then
  note "sitemap.xml still lists setup.html"
fi
if grep -qF 'configure.html' sitemap.xml; then
  note "sitemap.xml still lists configure.html"
fi

[ "$fail" = "0" ] && echo "journalist install CTA checks passed" || exit 1
