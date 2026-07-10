#!/usr/bin/env bash
# Fresh-machine checks shared by install.sh and their isolated regression test.
# This file is sourced after the Mycroft checkout exists.

mycroft_have() { command -v "$1" >/dev/null 2>&1; }

mycroft_catalog_dependency_pin() {
  local catalog="$1" dependency="$2"
  [ -f "$catalog" ] || return 0
  python3 - "$catalog" "$dependency" <<'PIN_PY' 2>/dev/null
import json
import sys

try:
    print(json.load(open(sys.argv[1])).get("dependencies", {}).get(sys.argv[2], ""))
except Exception:
    pass
PIN_PY
}

mycroft_writable_prefix() {
  local path="$1" parent
  while [ ! -e "$path" ]; do
    parent="$(dirname "$path")"
    [ "$parent" = "$path" ] && break
    path="$parent"
  done
  [ -d "$path" ] && [ -w "$path" ]
}

mycroft_prepare_npm_prefix() {
  if ! mycroft_have npm; then
    printf 'npm is required for QMD. Install Node.js 22+ and re-run Mycroft.\n' >&2
    return 1
  fi

  local prefix user_prefix
  prefix="$(npm config get prefix 2>/dev/null)" || {
    printf 'Could not read the npm global prefix. Repair npm, then re-run Mycroft.\n' >&2
    return 1
  }
  [ -n "$prefix" ] || {
    printf 'npm returned an empty global prefix. Repair npm, then re-run Mycroft.\n' >&2
    return 1
  }

  if ! mycroft_writable_prefix "$prefix"; then
    user_prefix="$HOME/.npm-global"
    mkdir -p "$user_prefix/bin"
    npm config set prefix "$user_prefix"
    prefix="$user_prefix"
    printf 'Using user-writable npm prefix: %s\n' "$prefix"
  fi

  case ":$PATH:" in
    *":$prefix/bin:"*) ;;
    *) export PATH="$prefix/bin:$PATH" ;;
  esac
}

mycroft_preflight_linux_build_tools() {
  [ "${MYCROFT_OS:-$(uname -s)}" = "Linux" ] || return 0
  [ "$#" -gt 0 ] || set -- make cc c++

  local tool missing=""
  for tool in "$@"; do
    mycroft_have "$tool" || missing="$missing $tool"
  done
  [ -z "$missing" ] && return 0

  printf 'Missing Linux build tools:%s\n' "$missing" >&2
  printf 'Install the complete Mycroft dependency floor, then re-run:\n' >&2
  printf '  sudo apt-get update && sudo apt-get install -y curl git python3 python3-pip build-essential\n' >&2
  return 1
}

mycroft_ensure_brew() {
  mycroft_have brew && return 0
  [ "${MYCROFT_OS:-$(uname -s)}" = "Darwin" ] || return 1

  if [ "${MYCROFT_ASSUME_YES:-0}" != "1" ]; then
    if [ ! -t 0 ]; then
      printf 'Homebrew is required, but this installer has no interactive stdin.\n' >&2
      printf 'Install Homebrew first, or re-run with MYCROFT_ASSUME_YES=1 to authorize its installer.\n' >&2
      return 1
    fi
    printf 'Homebrew is needed for macOS app installs. Install it now? [Y/n] ' >&2
    local answer
    read -r answer || return 1
    case "$answer" in [Nn]*) return 1 ;; esac
  fi

  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [ -x /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
  mycroft_have brew || {
    printf 'Homebrew installation did not put brew on PATH. Fix Homebrew, then re-run Mycroft.\n' >&2
    return 1
  }
}
