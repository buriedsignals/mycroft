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

JOIN='https://indicator.media/indicator-lab'
GITHUB='https://github.com/buriedsignals/mycroft'

if ! grep -qF "$JOIN" index.html; then
  note "index.html missing Install href $JOIN"
fi
# Check the public link text and destination, independent of CSS class names.
if ! python3 - "$JOIN" <<'PYCTA'
from html.parser import HTMLParser
from pathlib import Path
import sys

class InstallLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.current = [dict(attrs).get('href'), []]
    def handle_data(self, data):
        if self.current is not None:
            self.current[1].append(data)
    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            href, parts = self.current
            label = ' '.join(''.join(parts).split()).rstrip('→').strip()
            if label in ('Install', 'Join Indicator Lab', 'Install with Indicator Lab'):
                self.links.append((label, href))
            self.current = None

parser = InstallLinks()
parser.feed(Path('index.html').read_text())
assert parser.links, 'No installation links found'
assert all(href == sys.argv[1] for _, href in parser.links), parser.links
assert any(label == 'Install with Indicator Lab' for label, _ in parser.links), parser.links
assert not any(label == 'Join Indicator Lab' for label, _ in parser.links), parser.links
PYCTA
then
  note "Installation links must say Install with Indicator Lab and use $JOIN"
fi
if ! grep -qF "$GITHUB" index.html; then
  note "index.html missing GitHub link"
fi
if grep -rF '/api/artifacts/' README.md docs llms.txt index.html install.sh; then
  note "Public installation guidance must not expose private artifact endpoints"
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
