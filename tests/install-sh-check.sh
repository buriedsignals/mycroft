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
file_includes() {
  grep -qF -- "$2" "$1" || note "missing in $1: $2"
}
file_excludes() {
  if grep -qF -- "$2" "$1"; then note "stale fragment in $1: $2"; fi
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

# Configurator phase: the public path uses the product writer directly.
includes 'python3 "$MYCROFT_DIR/install/setup_server.py" --profile-dir "$MYCROFT_PROFILE_DIR" --repo-dir "$MYCROFT_DIR" --legacy-only'
includes 'MYCROFT_SETUP_CONFIG="$MYCROFT_PROFILE_DIR/setup-config.env"'
includes '. "$MYCROFT_SETUP_CONFIG"'
includes 'ensure_openknowledge'
includes 'npm install -g "@inkeep/open-knowledge@$pin"'
includes 'have() { type -P "$1" >/dev/null 2>&1; }'
includes 'export GOOSE_TELEMETRY_ENABLED="${GOOSE_TELEMETRY_ENABLED:-false}"'
excludes 'have() { command -v "$1" >/dev/null 2>&1; }'
includes 'navigator'
excludes 'bootstrap_engine'
excludes 'minisign -Vm'
excludes '"$ENGINE_BINARY"'
excludes 'BSIG_BIN'
excludes 'buriedsignals/engine'
excludes 'engine_bridge.py'
includes 'public bootstrap digest did not verify'
includes '--provision-from-private-source'
includes 'if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then'
includes 'if [ -n "$PRIVATE_INSTALLER_SOURCE" ] && [ -d "$PRIVATE_INSTALLER_SOURCE/.git" ]; then'
includes 'git clone --no-local "$PRIVATE_INSTALLER_SOURCE" "$PRIVATE_MYCROFT_DIR"'
includes 'Mycroft installer: Python 3 is required'
includes '${CHOICES_ARGS[@]+"${CHOICES_ARGS[@]}"}'
includes '${ACTION_ARGS[@]+"${ACTION_ARGS[@]}"}'
includes 'wslview "$GETTING_STARTED"'
# No keys or choices baked into the script itself
excludes '__CFG__'
excludes 'ENV_EOF'

# Editorial routing boundary: engineering drafts and adversarial reviews belong
# to compound-engineering/code review, not Mycroft fact-check or Spotlight.
includes 'Do not use Mycroft fact-check or Spotlight for software code'
includes "host's compound-engineering or code-review workflow."
file_includes skills/fact-check/SKILL.md 'Do not use this skill for software code'
file_includes skills/fact-check/SKILL.md 'route those to compound-engineering.'
file_includes instructions/mycroft-soul.md 'Do not route software code'
file_includes instructions/mycroft-soul.md "Use the host's compound-engineering or code-review workflow."
file_excludes skills/fact-check/SKILL.md 'escalating to Spotlight for deeper adversarial review'
file_excludes skills/fact-check/SKILL.md 'If Spotlight is installed and the request needs adversarial review'
file_excludes instructions/mycroft-soul.md 'Escalate to Spotlight when the work needs adversarial review'
file_excludes install.sh 'or stress-test a draft'

# CLI + skills
includes 'ln -sf "$MYCROFT_DIR/scripts/mycroft-fetch" "$HOME/.local/bin/mycroft-fetch"'
includes 'ln -sf "$MYCROFT_DIR/scripts/mycroft_safe.py" "$HOME/.local/bin/mycroft-safe"'
includes 'ln -sf "$MYCROFT_DIR/scripts/mycroft-doctor" "$HOME/.local/bin/mycroft-doctor"'
includes 'ln -sf "$MYCROFT_DIR/scripts/mycroft-update" "$HOME/.local/bin/mycroft-update"'
includes 'ln -sf "$MYCROFT_DIR/scripts/navigator-connect" "$HOME/.local/bin/mycroft-navigator"'

# Tooling installs
includes '. "$PREFLIGHT_HELPER"'
includes 'mycroft_prepare_npm_prefix || exit 1'
includes 'brew install --cask block-goose'
includes 'OpenRouter ZDR enforcement requires Goose 1.41 or newer.'
includes 'npm install -g "firecrawl-cli@$pin"'
excludes 'npm install -g "@tobilu/qmd@$pin"'
excludes 'qmd collection add'
includes 'install_private_splash'
includes 'git clone https://github.com/buriedsignals/mycroft.git "$PRIVATE_MYCROFT_DIR"'
includes 'git clone https://github.com/buriedsignals/splash.git "$SPLASH_DIR"'
includes '--skill-namespace splash'
includes '"path": f"~/.agents/skills/splash/{skill_dir.name}/SKILL.md"'
includes 'private-splash.enabled'
includes 'export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"'
includes 'GOOSE_RECIPE_PATH="$GOOSE_RECIPE_PATH_VALUE" "$HOME/.local/bin/mycroft-doctor"'
includes 'Mycroft doctor failed; setup is incomplete and the installer is exiting non-zero.'

# Goose configuration + schedules
includes 'configure_goose_persistent_defaults'
includes 'set_goose_config_key GOOSE_PROVIDER'
includes 'goose configure set-secret'
includes 'store_goose_secret OPENROUTER_API_KEY'
includes 'set_goose_config_key OPENROUTER_PARAMETERS'
includes 'OpenRouter — GLM-5.2 (per-request ZDR enforced)'
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
includes 'git merge --ff-only origin/main'
includes 'mycroft-update.timer'
includes '15 10 * * 1'

# CLI wrappers are repo scripts (symlinked, self-updating), so lint + contract-check
# them directly rather than as heredocs inside install.sh.
bash -n scripts/mycroft-doctor || note "scripts/mycroft-doctor does not parse"
bash -n scripts/mycroft-update || note "scripts/mycroft-update does not parse"
bash -n scripts/mycroft-uninstall || note "scripts/mycroft-uninstall does not parse"
[ -x scripts/mycroft-uninstall ] || note "scripts/mycroft-uninstall must be executable so install does not dirty the checkout"
wincludes() { grep -qF -- "$2" "$1" || note "missing in $1: $2"; }
wincludes scripts/mycroft-doctor 'export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"'
wincludes scripts/mycroft-doctor '"shell-safety skill"'
wincludes scripts/mycroft-doctor '"epistemic-grounding skill"'
wincludes scripts/mycroft-doctor '"OpenRouter per-request ZDR enforced"'
wincludes scripts/mycroft-doctor '"Private Splash plugin"'
wincludes scripts/mycroft-doctor '"Splash namespaced skills"'
wincludes scripts/mycroft-update 'doctor failed after update; rolling back app checkouts'
wincludes scripts/mycroft-update 'provision-sovereign.sh'
wincludes scripts/mycroft-update 'latest signed public bundle'
wincludes scripts/mycroft-update 'releases/latest/download'
wincludes scripts/mycroft-update 'config.get("plugins", {}).get("scoutpost", {}).get("enabled") is True'
wincludes scripts/mycroft-update 'replace_splash_skills'
wincludes scripts/mycroft-update 'refresh_splash_registry'
wincludes scripts/mycroft-update 'Private Mycroft + Splash checkouts updated'
if grep -qF -- 'SPOTLIGHT_MONITORING_BACKEND' scripts/mycroft-update; then note 'legacy Spotlight-owned Scoutpost marker remains in updater'; fi
if grep -qF -- 'SPOTLIGHT_SCOUT_REQUESTS' scripts/mycroft-update; then note 'legacy Spotlight scout-request marker remains in updater'; fi

# Getting-started guide written by configurator, opened at the end
includes 'GETTING_STARTED="$MYCROFT_PROFILE_DIR/getting-started.html"'
includes 'open "$GETTING_STARTED"'

# Spotlight remains a Mycroft setup choice, but its signed public installer owns
# every Spotlight runtime/config/update detail.
includes 'install_spotlight_product'
includes '[ "$ENABLE_SPOTLIGHT" = "1" ] || return 0'
includes 'https://spotlight.buriedsignals.com/install-spotlight.sh'
includes 'Spotlight installed by its canonical signed installer'
excludes 'git clone https://github.com/buriedsignals/spotlight.git "$SPOTLIGHT_DIR"'
excludes 'npm install -g dev-browser@0.2.8'
excludes '"runtime": "goose"'
excludes '"search_library": "firecrawl"'
excludes '"case_workspace_root": "$SPOTLIGHT_VAULT_PATH/cases"'
excludes '"dev_browser": {"enabled": $DEVBROWSER_JSON'
excludes 'SPOT_DEVBROWSER'

# Seed-note dates: quoted heredocs rely on the writer substituting $TODAY
includes 'sed "s/\$TODAY/$TODAY/g" > "$path"'

# macOS /bin/bash 3.2 treats empty "${arr[@]}" as unbound under `set -u`.
# The published v0.3.5 bootstrap still uses that form; install.sh rewrites it
# to the nounset-safe expansion after digest verification.
if ! /bin/bash -c 'set -u; CHOICES_ARGS=(); : "${CHOICES_ARGS[@]}"' >/dev/null 2>&1; then
  /bin/bash -c 'set -u; CHOICES_ARGS=(); ACTION_ARGS=(); : "${CHOICES_ARGS[@]+"${CHOICES_ARGS[@]}"}"; : "${ACTION_ARGS[@]+"${ACTION_ARGS[@]}"}"' \
    || note "nounset-safe empty-array expansion failed under /bin/bash"
fi

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck -S error install.sh || fail=1
fi

[ "$fail" = "0" ] && echo "install.sh checks passed" || exit 1
