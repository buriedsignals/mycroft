#!/usr/bin/env bash
# Mycroft is installed through Indicator Labs. This file remains so old
# curl|bash pipes fail closed instead of fetching a public-installer bundle
# or opening a localhost configure page.
set -euo pipefail

JOIN='https://buriedsignals.com/join'

cat <<EOF
Mycroft is installed in Indicator Labs, not by this script.

Journalists: $JOIN
Contributors: clone this repository and install Mycroft from Indicator Labs
against the local checkout.

There is no localhost configure.html server and no curl|bash public installer.
Do not paste API keys into a terminal, a chat, or a web form.

Do not use Mycroft fact-check or Spotlight for software code, architecture,
PRDs, or threat models. Use the host's compound-engineering or code-review workflow.
EOF
exit 1
