#!/usr/bin/env bash
# Journalist install is Indicator Labs. The bash installer must fail closed.
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0
note() { printf 'FAIL  %s\n' "$1"; fail=1; }

bash -n install.sh || { echo "install.sh does not parse"; exit 1; }

includes() {
  grep -qF -- "$1" install.sh || note "missing fragment: $1"
}
excludes() {
  if grep -qF -- "$1" install.sh; then note "stale fragment present: $1"; fi
}
file_includes() {
  grep -qF -- "$2" "$1" || note "missing in $1: $2"
}
file_excludes() {
  if grep -qF -- "$2" "$1"; then note "stale fragment in $1: $2"; fi
}

includes 'https://buriedsignals.com/join'
includes 'Indicator Labs'
includes 'There is no localhost configure.html server'
includes 'Do not use Mycroft fact-check or Spotlight for software code'
includes "host's compound-engineering or code-review workflow."
excludes 'setup_server.py'
excludes 'engine_bridge.py'
excludes 'bootstrap.sh'
excludes 'PUBLIC_RELEASE_BASE'
excludes 'curl -fL'
excludes '__CFG__'
excludes 'ENV_EOF'

if [ -e install/configure.html ]; then note "install/configure.html must be deleted"; fi
if [ -e install/setup_server.py ]; then note "install/setup_server.py must be deleted"; fi
if [ -e install/engine_bridge.py ]; then note "install/engine_bridge.py must be deleted"; fi
if [ -e setup.html ]; then note "setup.html must be deleted"; fi

file_includes skills/fact-check/SKILL.md 'Do not use this skill for software code'
file_includes skills/fact-check/SKILL.md 'route those to compound-engineering.'
file_includes instructions/mycroft-soul.md 'Do not route software code'
file_includes instructions/mycroft-soul.md "Use the host's compound-engineering or code-review workflow."
file_excludes skills/fact-check/SKILL.md 'escalating to Spotlight for deeper adversarial review'
file_excludes skills/fact-check/SKILL.md 'If Spotlight is installed and the request needs adversarial review'
file_excludes instructions/mycroft-soul.md 'Escalate to Spotlight when the work needs adversarial review'

if ! bash install.sh >/tmp/mycroft-install-pointer.out 2>&1; then
  :
else
  note "install.sh must exit non-zero so old curl|bash pipes fail closed"
fi
if ! grep -qF 'https://buriedsignals.com/join' /tmp/mycroft-install-pointer.out; then
  note "install.sh output missing Indicator Labs join URL"
fi
rm -f /tmp/mycroft-install-pointer.out

[ "$fail" = "0" ] && echo "install.sh checks passed" || exit 1
