#!/usr/bin/env bash
# Both Engine paths are documented; the legacy bash installer remains fail closed.
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
includes 'Open-source and agent-led users'
includes 'bsig'
includes 'stdin/keychain flow'
excludes 'curl -fL'

bash -n scripts/mycroft-update || { echo "scripts/mycroft-update does not parse"; exit 1; }
bash -n scripts/mycroft-uninstall || { echo "scripts/mycroft-uninstall does not parse"; exit 1; }
file_excludes scripts/mycroft-update 'public-installer/mycroft'
file_excludes scripts/mycroft-update 'applicator.py'
file_excludes scripts/mycroft-update 'bootstrap.sh'
file_includes scripts/mycroft-update 'bsig plan update mycroft'
file_excludes scripts/mycroft-update 'mycroft.buriedsignals.com/install.sh'
file_includes scripts/mycroft-update 'https://buriedsignals.com/join'
file_includes scripts/mycroft-update 'Indicator Labs'
file_excludes scripts/mycroft-uninstall 'bootstrap.sh'
file_includes scripts/mycroft-uninstall 'bsig plan uninstall mycroft'
file_excludes scripts/mycroft-uninstall 'applicator.py'
file_includes scripts/mycroft-uninstall 'https://buriedsignals.com/join'
file_includes scripts/mycroft-uninstall 'Indicator Labs'

if bash scripts/mycroft-uninstall >/tmp/mycroft-uninstall-pointer.out 2>&1; then
  note "mycroft-uninstall must exit non-zero; product uninstall is Indicator Labs"
else
  :
fi
if ! grep -qF 'https://buriedsignals.com/join' /tmp/mycroft-uninstall-pointer.out; then
  note "mycroft-uninstall output missing Indicator Labs join URL"
fi
rm -f /tmp/mycroft-uninstall-pointer.out

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
