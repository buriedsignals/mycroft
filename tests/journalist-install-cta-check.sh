#!/usr/bin/env bash
# Public Pages must send journalists to join/desktop, not curl|bash.
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0
note() { printf 'FAIL  %s\n' "$1"; fail=1; }

if [ -e setup.html ]; then
  note "setup.html must be deleted; do not leave a curl|bash stub"
fi

JOIN='https://buriedsignals.com/join'
GITHUB='https://github.com/buriedsignals/mycroft'

if ! grep -qF "$JOIN" index.html; then
  note "index.html missing Set up href $JOIN"
fi
if ! grep -qF "$GITHUB" index.html; then
  note "index.html missing GitHub link"
fi
if grep -qE 'href=["'"'"'][^"'"'"']*setup\.html' index.html; then
  note "index.html still links to setup.html"
fi
if grep -qE 'curl .*mycroft\.buriedsignals\.com/install\.sh' index.html; then
  note "index.html still advertises curl|bash install.sh"
fi
if grep -qF 'mycroft.buriedsignals.com/setup.html' sitemap.xml; then
  note "sitemap.xml still lists setup.html"
fi

[ "$fail" = "0" ] && echo "journalist install CTA checks passed" || exit 1
