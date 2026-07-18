#!/usr/bin/env bash
# Static checks for the canonical installer (install.sh).
# Replaces the old setup-generator-check.js script assertions: install.sh is
# now a real file, so we lint it directly instead of string-building it in JS.
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

# Layout + profile contract
includes 'GOOSE_CONFIG="$XDG_CONFIG_HOME/goose"'
includes 'PROVIDERS_DST="$GOOSE_CONFIG/custom_providers"'
includes 'MYCROFT_PROFILE_DIR="$GOOSE_CONFIG/mycroft"'
includes 'MYCROFT_DATA_DIR="$XDG_DATA_HOME/goose/mycroft"'
includes 'MYCROFT_DIR="$MYCROFT_DATA_DIR/source"'
includes 'MYCROFT_SKILL_REGISTRY="$MYCROFT_PROFILE_DIR/skill-registry.json"'
includes 'MYCROFT_GENERATED_RECIPES="$MYCROFT_PROFILE_DIR/generated-recipes"'
includes 'GOOSE_RECIPE_PATH_VALUE="$MYCROFT_DIR/recipes:$MYCROFT_GENERATED_RECIPES"'

# Configurator phase: bootstrap fetches repo, local server collects config
includes 'python3 "$MYCROFT_DIR/install/setup_server.py" --profile-dir "$MYCROFT_PROFILE_DIR" --repo-dir "$MYCROFT_DIR"'
includes 'MYCROFT_SETUP_CONFIG="$MYCROFT_PROFILE_DIR/setup-config.env"'
includes 'if ! have bsig; then'
includes 'rm -f "$ENGINE_PLAN_MARKER"'
includes 'if [ -f "$ENGINE_PLAN_MARKER" ]; then'
includes 'no legacy Obsidian/QMD fallback was applied'
excludes 'reload to use the legacy installer'
# No keys or choices baked into the script itself
excludes '__CFG__'
excludes 'ENV_EOF'

# CLI + skills
includes 'ln -sf "$MYCROFT_DIR/scripts/mycroft-fetch" "$HOME/.local/bin/mycroft-fetch"'
includes 'ln -sf "$MYCROFT_DIR/scripts/mycroft_safe.py" "$HOME/.local/bin/mycroft-safe"'
includes 'ln -sf "$MYCROFT_DIR/scripts/mycroft-doctor" "$HOME/.local/bin/mycroft-doctor"'
includes 'ln -sf "$MYCROFT_DIR/scripts/mycroft-update" "$HOME/.local/bin/mycroft-update"'

# Tooling installs
includes '. "$PREFLIGHT_HELPER"'
includes 'mycroft_prepare_npm_prefix || exit 1'
includes 'mycroft_preflight_linux_build_tools || exit 1'
includes 'brew install --cask block-goose'
includes 'npm install -g "firecrawl-cli@$pin"'
includes 'npm install -g "@tobilu/qmd@$pin"'
includes 'qmd collection add "$VAULT_PATH" --name mycroft'
includes 'export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"'
includes 'GOOSE_RECIPE_PATH="$GOOSE_RECIPE_PATH_VALUE" "$HOME/.local/bin/mycroft-doctor"'
includes 'Mycroft doctor failed; setup is incomplete and the installer is exiting non-zero.'

# Goose configuration + schedules
includes 'configure_goose_persistent_defaults'
includes 'set_goose_config_key GOOSE_PROVIDER'
includes 'goose configure set-secret'
includes 'goose schedule add --schedule-id mycroft-morning-brief'
includes 'goose schedule add --schedule-id mycroft-vault-audit'
includes 'recipes/start.yaml'
includes 'morning-brief-preflight.yaml'
includes 'START_HERE.md'

# Local model path
includes 'install_local_model'
includes 'register_local_model_in_goose'
includes '$XDG_DATA_HOME/goose/models'

# Updater cron/timer (the updater logic itself now lives in scripts/mycroft-update)
includes 'git fetch origin main'
includes 'git merge --ff-only origin/main'
includes 'mycroft-update.timer'
includes '15 10 * * 1'

# CLI wrappers are repo scripts (symlinked, self-updating), so lint + contract-check
# them directly rather than as heredocs inside install.sh.
bash -n scripts/mycroft-doctor || note "scripts/mycroft-doctor does not parse"
bash -n scripts/mycroft-update || note "scripts/mycroft-update does not parse"
wincludes() { grep -qF -- "$2" "$1" || note "missing in $1: $2"; }
wincludes scripts/mycroft-doctor 'export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"'
wincludes scripts/mycroft-doctor '"shell-safety skill"'
wincludes scripts/mycroft-doctor '"epistemic-grounding skill"'
wincludes scripts/mycroft-update 'doctor failed after update; rolling back app checkouts'
wincludes scripts/mycroft-update 'provision-sovereign.sh'
wincludes scripts/mycroft-update 'git merge --ff-only'

# Getting-started guide written by configurator, opened at the end
includes 'GETTING_STARTED="$MYCROFT_PROFILE_DIR/getting-started.html"'
includes 'open "$GETTING_STARTED"'

# Spotlight contract (current spotlight repo: dev-browser primary, no handoff,
# canonical .spotlight-config.json, OSINT_NAV_API_KEY naming)
includes 'git clone https://github.com/buriedsignals/spotlight.git "$SPOTLIGHT_DIR"'
includes 'npm install -g dev-browser@0.2.8'
includes '"runtime": "goose"'
includes '"search_library": "firecrawl"'
includes '"case_workspace_root": "$SPOTLIGHT_VAULT_PATH/cases"'
includes '"dev_browser": {"enabled": $DEVBROWSER_JSON'
includes 'store_goose_secret OSINT_NAV_API_KEY'
includes 'integrations/preflight.py'
excludes 'handoff-to-mycroft'
excludes 'BROWSERUSE'
excludes 'OSINT_NAVIGATOR_API_KEY'
excludes 'browser_use'

# Seed-note dates: quoted heredocs rely on the writer substituting $TODAY
includes 'sed "s/\$TODAY/$TODAY/g" > "$path"'

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck -S error install.sh || fail=1
fi

[ "$fail" = "0" ] && echo "install.sh checks passed" || exit 1
