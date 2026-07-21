#!/usr/bin/env bash
# Mycroft installer — buriedsignals/mycroft
#
# One static script for every install:
#   curl -fsSL https://mycroft.buriedsignals.com/install.sh | bash
#
# Phase 1 fetches the Mycroft repo, phase 2 opens a local configurator page
# in your browser (your choices and API keys go to a server on 127.0.0.1
# only — nothing leaves this machine), phase 3 installs and verifies.
set -euo pipefail

PUBLIC_BUNDLE_PHASE=0
if [ "${1:-}" = "--provision-from-public-bundle" ]; then
  PUBLIC_BUNDLE_PHASE=1
  shift
fi

if [ "$PUBLIC_BUNDLE_PHASE" = "0" ]; then
  PUBLIC_RELEASE_BASE="https://github.com/buriedsignals/mycroft/releases/download/v0.3.5"
  PUBLIC_BOOTSTRAP_SHA256="ebe0a8b707f4b891e2b9c87fe6b65da5e31f6a4140361faf0d99400c4f9a47a7"
  command -v curl >/dev/null 2>&1 || { echo "Mycroft installer: curl is required" >&2; exit 1; }
  command -v openssl >/dev/null 2>&1 || { echo "Mycroft installer: OpenSSL is required" >&2; exit 1; }
  PUBLIC_BOOTSTRAP_TMP="$(mktemp "${TMPDIR:-/tmp}/mycroft-public-bootstrap.XXXXXX")"
  trap 'rm -f "$PUBLIC_BOOTSTRAP_TMP"' EXIT HUP INT TERM
  curl -fL --proto '=https' --tlsv1.2 "$PUBLIC_RELEASE_BASE/bootstrap.sh" -o "$PUBLIC_BOOTSTRAP_TMP"
  PUBLIC_BOOTSTRAP_ACTUAL="$(openssl dgst -sha256 -r "$PUBLIC_BOOTSTRAP_TMP" | awk '{print $1}')"
  [ "$PUBLIC_BOOTSTRAP_ACTUAL" = "$PUBLIC_BOOTSTRAP_SHA256" ] || {
    echo "Mycroft installer: public bootstrap digest did not verify" >&2
    exit 1
  }
  bash "$PUBLIC_BOOTSTRAP_TMP" --product mycroft --release-base "$PUBLIC_RELEASE_BASE" --runtime goose
  exit $?
fi

TODAY="$(date +%F)"
MYCROFT_OS="${MYCROFT_OS:-$(uname -s)}"
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
# Website setup is already interactive in the loopback configurator. Keep
# Goose's first-run telemetry question from introducing a second terminal
# prompt; users can opt in later from Goose settings.
export GOOSE_TELEMETRY_ENABLED="${GOOSE_TELEMETRY_ENABLED:-false}"

XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
GOOSE_CONFIG="$XDG_CONFIG_HOME/goose"
MYCROFT_PROFILE_DIR="$GOOSE_CONFIG/mycroft"
MYCROFT_DATA_DIR="$XDG_DATA_HOME/goose/mycroft"
MYCROFT_DIR="$MYCROFT_DATA_DIR/source"
PLUGINS_DIR="$MYCROFT_DATA_DIR/plugins"
MYCROFT_SKILLS_DIR="$MYCROFT_DIR/skills"
MYCROFT_PROFILE_SKILLS_DIR="$MYCROFT_PROFILE_DIR/skills"
MYCROFT_SKILL_REGISTRY="$MYCROFT_PROFILE_DIR/skill-registry.json"
MYCROFT_ENV="$MYCROFT_PROFILE_DIR/.env"
MYCROFT_CONFIG="$MYCROFT_PROFILE_DIR/mycroft-config.json"
MYCROFT_GOOSE_INSTRUCTIONS="$MYCROFT_PROFILE_DIR/goose-mycroft.md"
MYCROFT_SOUL_FILE="$MYCROFT_PROFILE_DIR/SOUL.md"
PROVIDERS_DST="$GOOSE_CONFIG/custom_providers"
SPOTLIGHT_DIR="$PLUGINS_DIR/spotlight"
MYCROFT_GENERATED_RECIPES="$MYCROFT_PROFILE_DIR/generated-recipes"
MYCROFT_MORNING_BRIEF_CONFIG="$MYCROFT_PROFILE_DIR/morning-brief-config.md"
GOOSE_RECIPE_PATH_VALUE="$MYCROFT_DIR/recipes:$MYCROFT_GENERATED_RECIPES"

# Existing Obsidian/QMD state remains readable, while fresh installs also
# provision the OpenKnowledge CLI used by the generated Goose recipes.
MYCROFT_LEGACY_UPDATE=0
for legacy_marker in "$MYCROFT_ENV" "$MYCROFT_PROFILE_DIR/setup-config.env" \
  "$MYCROFT_SKILL_REGISTRY" "$HOME/.mycroft"; do
  if [ -e "$legacy_marker" ]; then
    MYCROFT_LEGACY_UPDATE=1
    break
  fi
done

# Sovereign stack: SearXNG search + Crawl4AI scrape run with zero API cost on the
# normal path; Firecrawl is an optional escape hatch. SearXNG serves its JSON API on
# this port; the Mycroft tools + provisioner default to the same URL (SEARXNG_URL).
# Container name / image / settings-path are the provisioner's concern (identical
# defaults there) — install.sh only needs the port, to write SEARXNG_URL.
SEARXNG_PORT="${SEARXNG_PORT:-8899}"
SEARXNG_URL_VALUE="http://localhost:$SEARXNG_PORT"

if   [ -f "$HOME/.zshrc" ];  then SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then SHELL_RC="$HOME/.bashrc"
else SHELL_RC="$HOME/.zshrc"; touch "$SHELL_RC"
fi

# Resolve external executables only. `command -v` also reports shell functions,
# which made the `ok()` status logger masquerade as the OpenKnowledge `ok` CLI.
have() { type -P "$1" >/dev/null 2>&1; }
say()  { printf "\n\033[1;34m>\033[0m %s\n" "$*"; }
ok()   { printf "  \033[1;32m+\033[0m %s\n" "$*"; }
warn() { printf "  \033[1;33m!\033[0m %s\n" "$*"; }

ensure_brew() {
  mycroft_ensure_brew
}

ensure_git() {
  if have git; then return 0; fi
  if [ "$(uname -s)" = "Darwin" ]; then
    xcode-select --install || true
    warn "Install Xcode Command Line Tools, then re-run this installer."
    exit 1
  fi
  warn "git is required. Install git with your package manager, then re-run."
  exit 1
}

ensure_goose() {
  [ "$INSTALL_GOOSE" = "1" ] || return 0
  if [ "$(uname -s)" = "Darwin" ]; then
    if [ ! -d "/Applications/Goose.app" ] && [ ! -d "/Applications/block-goose.app" ] && [ ! -d "$HOME/Applications/Goose.app" ] && [ ! -d "$HOME/Applications/block-goose.app" ]; then
      ensure_brew || { warn "Goose requires Homebrew on macOS; setup stopped before making a partial install."; exit 1; }
      brew install --cask block-goose && ok "Goose Desktop"
    else ok "Goose Desktop present"; fi
  fi
  if ! have goose; then
    curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash
    ok "Goose CLI"
  else ok "Goose CLI present"; fi
}

install_obsidian() {
  [ "$INSTALL_OBSIDIAN" = "1" ] || return 0
  if [ "$(uname -s)" = "Darwin" ]; then
    if [ -d "/Applications/Obsidian.app" ] || [ -d "$HOME/Applications/Obsidian.app" ]; then ok "Obsidian present"
    else
      ensure_brew || { warn "Obsidian requires Homebrew on macOS; setup stopped before making a partial install."; exit 1; }
      brew install --cask obsidian && ok "Obsidian"
    fi
    if ! have obsidian; then
      warn "Open Obsidian, then enable Settings -> General -> Advanced -> Command Line Interface."
      open -a Obsidian 2>/dev/null || true
    fi
  else
    warn "Install Obsidian manually on Linux and enable its CLI if your package includes it."
  fi
}

install_firecrawl() {
  # Firecrawl is the OPTIONAL escape hatch: scrape fallback for hard anti-bot targets
  # + optional search-union. Present = escape hatch enabled; absent = pure-sovereign.
  # Not on the default search/scrape path.
  [ "$INSTALL_FIRECRAWL" = "1" ] || { ok "firecrawl skipped (pure-sovereign mode)"; return 0; }
  if have firecrawl; then ok "firecrawl present (optional fallback)"; return 0; fi
  if ! have npm && [ "$MYCROFT_OS" = "Darwin" ]; then
    ensure_brew || { warn "Node.js requires Homebrew on macOS."; exit 1; }
    brew install node
  fi
  if have npm; then
    local pin
    pin="$(mycroft_catalog_dependency_pin "$MYCROFT_DIR/catalog/catalog.json" firecrawl-cli)"
    [ -n "$pin" ] || { warn "Signed catalog has no firecrawl-cli pin; refusing an unpinned install."; exit 1; }
    npm install -g "firecrawl-cli@$pin" && ok "firecrawl $pin (optional fallback)"
  else
    warn "npm missing; install firecrawl-cli manually."
  fi
}

ensure_qmd() {
  if have qmd; then ok "QMD CLI present"; return 0; fi
  if ! have npm && [ "$MYCROFT_OS" = "Darwin" ]; then
    ensure_brew || { warn "Node.js requires Homebrew on macOS."; exit 1; }
    brew install node
  fi
  if have npm; then
    local pin
    pin="$(mycroft_catalog_dependency_pin "$MYCROFT_DIR/catalog/catalog.json" @tobilu/qmd)"
    [ -n "$pin" ] || { warn "Signed catalog has no @tobilu/qmd pin; refusing an unpinned install."; exit 1; }
    npm install -g "@tobilu/qmd@$pin" && ok "QMD CLI $pin"
  else
    warn "npm missing; install QMD manually from the signed catalog pin."
  fi
}

ensure_openknowledge() {
  if have ok; then ok "OpenKnowledge CLI present"; return 0; fi
  if ! have npm; then
    warn "npm is required to install the OpenKnowledge CLI. Install Node.js and re-run."
    exit 1
  fi
  local pin
  pin="$(mycroft_catalog_dependency_pin "$MYCROFT_DIR/catalog/catalog.json" @inkeep/open-knowledge)"
  [ -n "$pin" ] || { warn "Release catalog has no @inkeep/open-knowledge pin; refusing an unpinned install."; exit 1; }
  npm install -g "@inkeep/open-knowledge@$pin" && ok "OpenKnowledge CLI $pin"
}

# --- Scoutpost CLI (scout) ---------------------------------------------------
# `scout` on PATH via npm, pinned to the vendored catalog.json (native-binary-via-
# npm, like firecrawl/qmd). CLI branch = macOS/Linux/WSL2 with npm; a host without
# npm/scout falls back to the REST API (SCOUTPOST_API_KEY + SCOUTPOST_API_BASE). The
# Public Supabase anon key is baked into the Scoutpost clients — it is not
# a per-user secret, so there is no form field to collect it.
SCOUTPOST_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdmbWR6aXBsdGljZm9ha2hyZnB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc2MDYzMjIsImV4cCI6MjA4MzE4MjMyMn0.Liz22BqK2qfHBcIsIJxGTT4VvMzfBE_yRFraVrUPKq4"

# Read the scoutpost-cli pin from the vendored catalog.json. New logic — no other
# installer idiom reads catalog.json; python3 is a hard prerequisite of this script.
scout_cli_pin() {
  mycroft_catalog_dependency_pin "$MYCROFT_DIR/catalog/catalog.json" scoutpost-cli
}

install_scout_cli() {
  [ "$ENABLE_SCOUTPOST" = "1" ] || return 0
  if have scout; then ok "scout CLI present"; return 0; fi
  if ! have npm && [ "$MYCROFT_OS" = "Darwin" ]; then
    ensure_brew || { warn "Node.js requires Homebrew on macOS."; exit 1; }
    brew install node
  fi
  if ! have npm; then
    warn "npm missing; Scoutpost will use the REST API. To enable the scout CLI later: npm install -g scoutpost-cli"
    return 0
  fi
  local pin; pin="$(scout_cli_pin)"
  if [ -n "$pin" ]; then
    npm install -g "scoutpost-cli@$pin" && ok "scout CLI ($pin)" || warn "scout CLI install failed; Scoutpost will use the REST API."
  else
    npm install -g scoutpost-cli && ok "scout CLI (unpinned — no catalog pin found)" || warn "scout CLI install failed; Scoutpost will use the REST API."
  fi
}

# Write ~/.scoutpost/config.json for the scout CLI (functions/v1 + baked public anon
# key + cj_ api_key), 0600, via a direct write with xtrace disabled so the key never
# enters a trace — never `scout config set` (that puts the key in argv). CLI branch
# only; the REST branch reads SCOUTPOST_API_KEY from the profile .env.
write_scout_config() {
  [ "$ENABLE_SCOUTPOST" = "1" ] || return 0
  have scout || return 0
  [ -n "${SCOUTPOST_API_KEY:-}" ] || { warn "Scoutpost enabled but no API key found; skipping scout config."; return 0; }
  local cfg="$HOME/.scoutpost/config.json" oldumask xtrace=0
  mkdir -p "$HOME/.scoutpost"; chmod 700 "$HOME/.scoutpost" 2>/dev/null || true
  case "$-" in *x*) xtrace=1; set +x;; esac
  oldumask="$(umask)"; umask 077
  cat > "$cfg" <<SCOUT_CFG_EOF
{
  "api_url": "https://scoutpost.ai/functions/v1",
  "supabase_anon_key": "$SCOUTPOST_ANON_KEY",
  "api_key": "$SCOUTPOST_API_KEY"
}
SCOUT_CFG_EOF
  chmod 600 "$cfg"
  umask "$oldumask"
  [ "$xtrace" = 1 ] && set -x
  ok "scout config (~/.scoutpost/config.json)"
}
# -----------------------------------------------------------------------------

configure_qmd() {
  if ! have qmd; then warn "QMD CLI missing; vault search and Spotlight query-vault will be unavailable until qmd is installed."; return 0; fi
  qmd collection add "$VAULT_PATH" --name mycroft >/dev/null 2>&1 || true
  if [ "$ENABLE_SPOTLIGHT" = "1" ]; then
    qmd collection add "$SPOTLIGHT_VAULT_PATH" --name spotlight >/dev/null 2>&1 || true
  fi
  qmd update >/dev/null 2>&1 || warn "QMD installed, but initial index update failed; run qmd update after setup."
  ok "QMD vault search configured"
}

update_repo() {
  local dir="$1" name="$2"
  if [ ! -d "$dir/.git" ]; then return 1; fi
  (
    cd "$dir"
    if ! git diff --quiet || ! git diff --cached --quiet; then
      warn "$name has local uncommitted changes; skipping automatic update at $dir"
      return 0
    fi
    git fetch origin main
    if git merge-base --is-ancestor HEAD origin/main; then
      git merge --ff-only origin/main && ok "$name updated"
    else
      warn "$name has local commits or divergent history; skipping automatic update at $dir"
    fi
  )
}

warn_legacy_layout() {
  if [ -d "$HOME/.mycroft" ] && [ "$HOME/.mycroft" != "$MYCROFT_DIR" ]; then
    warn "Found legacy ~/.mycroft. New installs use ~/.config/goose/mycroft and ~/.local/share/goose/mycroft; legacy files were not deleted."
  fi
}

install_or_update_mycroft() {
  if [ -d "$MYCROFT_DIR/.git" ]; then
    update_repo "$MYCROFT_DIR" "Mycroft"
    return
  fi
  if [ -d "$MYCROFT_DIR" ] && [ "$(find "$MYCROFT_DIR" -mindepth 1 -maxdepth 1 | head -n 1)" ]; then
    local tmp
    tmp="$(mktemp -d)"
    git clone https://github.com/buriedsignals/mycroft.git "$tmp/mycroft"
    (cd "$tmp/mycroft" && tar cf - .) | (cd "$MYCROFT_DIR" && tar xpf -)
    rm -rf "$tmp"
    ok "Mycroft installed into existing $MYCROFT_DIR"
  else
    git clone https://github.com/buriedsignals/mycroft.git "$MYCROFT_DIR"
    ok "Mycroft cloned"
  fi
}

install_mycroft_cli() {
  mkdir -p "$HOME/.local/bin"
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
  esac
  if [ -f "$MYCROFT_DIR/scripts/mycroft-fetch" ]; then
    chmod +x "$MYCROFT_DIR/scripts/mycroft-fetch" || true
    ln -sf "$MYCROFT_DIR/scripts/mycroft-fetch" "$HOME/.local/bin/mycroft-fetch"
    ok "mycroft-fetch CLI"
  else
    warn "mycroft-fetch missing from $MYCROFT_DIR/scripts"
  fi
  if [ -f "$MYCROFT_DIR/scripts/mycroft_safe.py" ]; then
    chmod +x "$MYCROFT_DIR/scripts/mycroft_safe.py" || true
    ln -sf "$MYCROFT_DIR/scripts/mycroft_safe.py" "$HOME/.local/bin/mycroft-safe"
    ok "mycroft-safe CLI (shell-safety validator)"
  else
    warn "mycroft_safe.py missing from $MYCROFT_DIR/scripts"
  fi
  if [ -f "$MYCROFT_DIR/scripts/mycroft-repair" ]; then
    chmod +x "$MYCROFT_DIR/scripts/mycroft-repair" || true
    ln -sf "$MYCROFT_DIR/scripts/mycroft-repair" "$HOME/.local/bin/mycroft-repair"
    ok "mycroft-repair CLI"
  else
    warn "mycroft-repair missing from $MYCROFT_DIR/scripts"
  fi
  # doctor + update are repo scripts symlinked here too, so `mycroft update` (a symlink)
  # delivers new wrapper/doctor logic on git ff — no reinstall for updater fixes.
  if [ -f "$MYCROFT_DIR/scripts/mycroft-doctor" ]; then
    chmod +x "$MYCROFT_DIR/scripts/mycroft-doctor" || true
    ln -sf "$MYCROFT_DIR/scripts/mycroft-doctor" "$HOME/.local/bin/mycroft-doctor"
    ok "mycroft-doctor CLI"
  else
    warn "mycroft-doctor missing from $MYCROFT_DIR/scripts"
  fi
  if [ -f "$MYCROFT_DIR/scripts/mycroft-update" ]; then
    chmod +x "$MYCROFT_DIR/scripts/mycroft-update" || true
    ln -sf "$MYCROFT_DIR/scripts/mycroft-update" "$HOME/.local/bin/mycroft-update"
    ok "mycroft-update CLI"
  else
    warn "mycroft-update missing from $MYCROFT_DIR/scripts"
  fi
  if [ -f "$MYCROFT_DIR/scripts/mycroft-uninstall" ]; then
    chmod +x "$MYCROFT_DIR/scripts/mycroft-uninstall" || true
    ln -sf "$MYCROFT_DIR/scripts/mycroft-uninstall" "$HOME/.local/bin/mycroft-uninstall"
    ok "mycroft-uninstall CLI"
  fi
  if [ -f "$MYCROFT_DIR/scripts/navigator-connect" ]; then
    chmod +x "$MYCROFT_DIR/scripts/navigator-connect" || true
    ln -sf "$MYCROFT_DIR/scripts/navigator-connect" "$HOME/.local/bin/mycroft-navigator"
    ok "mycroft-navigator reconnect CLI"
  fi
}

install_skill_registry() {
  mkdir -p "$MYCROFT_PROFILE_SKILLS_DIR" "$MYCROFT_SKILLS_DIR"
  # Scoutpost ships the authored, CLI/API-only skill from the repo (skills/scoutpost),
  # placed by the manifest loop below. No hosted-skill fetch — the hosted product skill
  # names MCP as a surface, and Mycroft is CLI-or-API only.
  if [ ! -f "$MYCROFT_SKILL_REGISTRY" ]; then
    warn "Missing $MYCROFT_SKILL_REGISTRY — the configurator did not finish; re-run the installer."
    exit 1
  fi
  # Surface skills where Goose discovers them: per-skill symlinks under
  # ~/.agents/skills/mycroft/<skill> (the shared <root>/<product>/<skill>
  # shape). Goose scans ~/.agents/skills recursively and does not read the
  # skill registry's "directory" pointer, so without these links the curated
  # skills are off its discovery path.
  mkdir -p "$HOME/.agents/skills/mycroft"
  local _sid skill_dir
  # Skill set = the release-resolved manifest vendored as skills.manifest. This
  # installs exactly the Goose-runtime-correct set and falls back to on-disk
  # skill dirs if the manifest is absent.
  if [ -s "$MYCROFT_DIR/skills.manifest" ]; then
    while IFS= read -r _sid; do
      { [ -n "$_sid" ] && [ -d "$MYCROFT_SKILLS_DIR/$_sid" ]; } || continue
      ln -sfn "$MYCROFT_SKILLS_DIR/$_sid" "$HOME/.agents/skills/mycroft/$_sid"
    done < "$MYCROFT_DIR/skills.manifest"
  else
    for skill_dir in "$MYCROFT_SKILLS_DIR"/*/; do
      [ -d "$skill_dir" ] || continue
      ln -sfn "$skill_dir" "$HOME/.agents/skills/mycroft/$(basename "$skill_dir")"
    done
  fi
  ok "Mycroft skill registry"
}

write_goose_instructions() {
  cat "$MYCROFT_DIR/instructions/journalism.md" > "$MYCROFT_GOOSE_INSTRUCTIONS"
  cat >> "$MYCROFT_GOOSE_INSTRUCTIONS" <<GOOSE_HINTS_EOF

## Mycroft Installed Context

- Mycroft repo: $MYCROFT_DIR
- Mycroft Goose profile: $MYCROFT_PROFILE_DIR
- Mycroft data dir: $MYCROFT_DATA_DIR
- Mycroft durable knowledge vault: $VAULT_PATH
- Mycroft recipes: $GOOSE_RECIPE_PATH_VALUE
- Mycroft skill registry: $MYCROFT_SKILL_REGISTRY
- Mycroft skills directory: $MYCROFT_SKILLS_DIR
- Mycroft generated scheduled recipes: $MYCROFT_GENERATED_RECIPES
- Morning brief monitoring profile: $MYCROFT_MORNING_BRIEF_CONFIG
- Mycroft persistent soul file: $MYCROFT_SOUL_FILE
- QMD vault search: qmd query, qmd search, qmd mcp
- Goose schedules: mycroft-morning-brief at 07:00, mycroft-vault-audit at 18:15
- Story work lives in: $VAULT_PATH/stories
- Durable wiki knowledge lives in: $VAULT_PATH/wiki
- Raw and processed sources live in: $VAULT_PATH/sources

Use Mycroft for durable knowledge, source records, wiki notes, story pitches, drafts, and published story packaging.
Use QMD for local markdown search before broad web search when the answer may already be in the Mycroft or Spotlight vault.
Do not use Mycroft as the active OSINT case workspace.

## Getting Started Route

When the user is new after install, asks how to start, or the vault contains only scaffold/example files, do not stop at "nothing found." Explain that Mycroft needs reporting context or source material, then offer:

1. Set up my beat.
2. Add to my knowledge base.
3. Create my morning brief.
4. Investigate a lead.
5. Set up scouts.
6. Show me a demo.

Prefer "Add to my knowledge base" when the user has links, files, newsletters, pasted notes, PDFs, or folders. Offer vault cleanup or an audit only when the user says they already have an existing note collection.

Use $MYCROFT_DIR/recipes/start.yaml as the broad first-run recipe. Use $MYCROFT_DIR/recipes/morning-brief-preflight.yaml only when the user specifically chooses the morning brief path.

## Fact-Checking Route

When the user asks to fact-check, verify, audit citations, inspect claims, or stress-test a draft, load the Mycroft fact-check skill first:

- $MYCROFT_SKILLS_DIR/fact-check/SKILL.md
- $MYCROFT_DIR/recipes/fact-check.yaml

Use the Mycroft fact-check path for drafts, quick checks, source assertions, and claim tables.
GOOSE_HINTS_EOF
  if [ "$ENABLE_SPOTLIGHT" = "1" ]; then
    cat >> "$MYCROFT_GOOSE_INSTRUCTIONS" <<GOOSE_SPOTLIGHT_EOF

## Spotlight Installed Context

- Spotlight repo: $SPOTLIGHT_DIR
- Spotlight vault: $SPOTLIGHT_VAULT_PATH
- Spotlight cases root: $SPOTLIGHT_VAULT_PATH/cases
- Spotlight ingest skill: $SPOTLIGHT_DIR/skills/ingest/SKILL.md
- Spotlight AGENTS runtime contract: $SPOTLIGHT_DIR/AGENTS.md
- Mycroft ingest target for Spotlight findings: $SPOTLIGHT_INGEST_TARGET

Use Spotlight for active OSINT casework, evidence trails, captures, and case briefs.
Use the Spotlight ingest skill to promote confirmed findings into the Mycroft vault.
For adversarial fact-checking, active case evidence trails, document/image-heavy OSINT, or an independent fact-checker loop, load:

- $SPOTLIGHT_DIR/AGENTS.md
- $SPOTLIGHT_DIR/agents/fact-checker.md
- $SPOTLIGHT_DIR/skills/spotlight/SKILL.md

Keep Spotlight's fact-checker independent from investigator reasoning. It should verify structured findings and write verdicts with evidence_for and evidence_against trails.
GOOSE_SPOTLIGHT_EOF
  fi
  if [ "$ENABLE_SCOUTPOST" = "1" ]; then
    cat >> "$MYCROFT_GOOSE_INSTRUCTIONS" <<'GOOSE_SCOUTPOST_EOF'

## Scoutpost Installed Context

Scoutpost is enabled. Use the installed Scoutpost skill from the Mycroft skill registry.
Prefer the scout CLI if installed, otherwise the hosted API with SCOUTPOST_API_KEY and SCOUTPOST_API_BASE. Do not use MCP.
Never print the API key.
GOOSE_SCOUTPOST_EOF
  fi
  cp "$MYCROFT_GOOSE_INSTRUCTIONS" "$GOOSE_CONFIG/.goosehints"
  ok "Goose global .goosehints"
}

sync_mycroft_profile() {
  mkdir -p "$MYCROFT_PROFILE_DIR"
  if [ -f "$MYCROFT_DIR/instructions/mycroft-soul.md" ]; then
    rm -f "$MYCROFT_SOUL_FILE"  # replace a stale symlink so cp can't hit "identical"
    cp "$MYCROFT_DIR/instructions/mycroft-soul.md" "$MYCROFT_SOUL_FILE"
  else
    cat > "$MYCROFT_SOUL_FILE" <<'SOUL_EOF'
# Mycroft Soul

You are Mycroft, a calm investigative assistant for journalists using Goose and Buried Signals tools.
SOUL_EOF
  fi
  ok "Mycroft Goose profile"
}

yaml_quote() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

set_goose_config_key() {
  local key="$1" value="$2" tmp escaped line
  mkdir -p "$GOOSE_CONFIG"
  [ -f "$GOOSE_CONFIG/config.yaml" ] || : > "$GOOSE_CONFIG/config.yaml"
  escaped="$(yaml_quote "$value")"
  line="$key: \"$escaped\""
  tmp="$(mktemp)"
  awk -v key="$key" -v line="$line" '
    index($0, key ":") == 1 { print line; seen = 1; next }
    { print }
    END { if (!seen) print line }
  ' "$GOOSE_CONFIG/config.yaml" > "$tmp"
  mv "$tmp" "$GOOSE_CONFIG/config.yaml"
}

store_goose_secret() {
  local name="$1" value="$2"
  [ -n "$value" ] || return 0
  if have goose && goose configure set-secret "$name" "$value" >/dev/null 2>&1; then
    ok "Goose secret $name"
  else
    warn "Could not store $name in Goose keychain; Goose Desktop may ask for it once."
  fi
}

install_local_model() {
  [ "$LOCAL_ONLY" = "1" ] || return 0
  [ -f "$MYCROFT_ENV" ] || { warn "MYCROFT_ENV missing; skipping local model download"; return 0; }
  set -a
  . "$MYCROFT_ENV"
  set +a
  [ -n "${MYCROFT_LOCAL_MODEL_REPO:-}" ] || { warn "MYCROFT_LOCAL_MODEL_REPO unset; cannot download model"; return 0; }
  [ -n "${MYCROFT_LOCAL_MODEL_FILE:-}" ] || { warn "MYCROFT_LOCAL_MODEL_FILE unset; cannot download model"; return 0; }

  local models_root="$HOME/models"
  local model_leaf
  model_leaf="$(basename "$MYCROFT_LOCAL_MODEL_REPO")"
  local model_dir="$models_root/$model_leaf"
  local model_path="$model_dir/$MYCROFT_LOCAL_MODEL_FILE"
  mkdir -p "$model_dir"

  if [ -f "$model_path" ]; then
    ok "local model already present ($model_path)"
  else
    say "Downloading $MYCROFT_LOCAL_MODEL_REPO/$MYCROFT_LOCAL_MODEL_FILE — this can take a while..."
    if have hf; then
      if hf download "$MYCROFT_LOCAL_MODEL_REPO" "$MYCROFT_LOCAL_MODEL_FILE" --local-dir "$model_dir" >/dev/null; then
        ok "local model downloaded via hf"
      else
        warn "hf download failed — retry later from Goose Desktop -> Settings -> Local Inference"
      fi
    elif have curl; then
      if curl -fL "https://huggingface.co/$MYCROFT_LOCAL_MODEL_REPO/resolve/main/$MYCROFT_LOCAL_MODEL_FILE" -o "$model_path"; then
        ok "local model downloaded via curl"
      else
        rm -f "$model_path"
        warn "curl download failed — retry later from Goose Desktop -> Settings -> Local Inference"
      fi
    else
      warn "Neither hf nor curl found; install one and rerun, or download from Goose Desktop"
    fi
  fi

  if [ -f "$model_path" ]; then
    register_local_model_in_goose "$model_path"
  else
    warn "Skipping Goose model registry write — model file not present. Add the model from Goose Desktop -> Settings -> Local Inference once you have it."
  fi
}

register_local_model_in_goose() {
  local model_path="$1"
  local registry_dir="$XDG_DATA_HOME/goose/models"
  local registry_file="$registry_dir/registry.json"
  mkdir -p "$registry_dir"
  [ -f "$registry_file" ] || printf '%s\n' '{"models":[]}' > "$registry_file"

  if ! have python3; then
    warn "python3 not found; cannot write Goose model registry. Open Goose Desktop -> Settings -> Local Inference and pick the model manually."
    return 0
  fi

  XDG_DATA_HOME="$XDG_DATA_HOME" \
  MYCROFT_LOCAL_MODEL_REPO="$MYCROFT_LOCAL_MODEL_REPO" \
  MYCROFT_LOCAL_MODEL_FILE="$MYCROFT_LOCAL_MODEL_FILE" \
  MYCROFT_LOCAL_MODEL_QUANT="$MYCROFT_LOCAL_MODEL_QUANT" \
  MYCROFT_LOCAL_MODEL_VISION="${MYCROFT_LOCAL_MODEL_VISION:-0}" \
  MYCROFT_LOCAL_MODEL_THINKING="${MYCROFT_LOCAL_MODEL_THINKING:-0}" \
  MODEL_PATH="$model_path" \
  python3 - <<'REGISTRY_PY'
import json, os, pathlib

repo = os.environ.get("MYCROFT_LOCAL_MODEL_REPO", "")
filename = os.environ.get("MYCROFT_LOCAL_MODEL_FILE", "")
quant = os.environ.get("MYCROFT_LOCAL_MODEL_QUANT", "")
vision = os.environ.get("MYCROFT_LOCAL_MODEL_VISION", "0") == "1"
thinking = os.environ.get("MYCROFT_LOCAL_MODEL_THINKING", "0") == "1"
local_path = os.environ.get("MODEL_PATH", "")
registry_path = pathlib.Path(os.environ["XDG_DATA_HOME"]) / "goose" / "models" / "registry.json"

if not (repo and filename and quant and local_path):
    raise SystemExit(0)

model_id = repo + ":" + quant
try:
    data = json.loads(registry_path.read_text() or "{}")
except json.JSONDecodeError:
    data = {}
size_bytes = os.path.getsize(local_path) if os.path.exists(local_path) else 0

entry = {
    "id": model_id,
    "repo_id": repo,
    "filename": filename,
    "quantization": quant,
    "local_path": local_path,
    "source_url": "https://huggingface.co/" + repo + "/resolve/main/" + filename,
    "settings": {
        "context_size": None,
        "max_output_tokens": None,
        "sampling": {"type": "Temperature", "temperature": 0.8, "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": None},
        "repeat_penalty": 1.0,
        "repeat_last_n": 64,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "n_batch": None,
        "n_gpu_layers": None,
        "use_mlock": False,
        "flash_attention": None,
        "n_threads": None,
        "native_tool_calling": True,
        "use_jinja": False,
        "enable_thinking": thinking,
        "vision_capable": vision,
        "image_token_estimate": 256,
        "mmproj_size_bytes": 0,
    },
    "size_bytes": size_bytes,
    "mmproj_size_bytes": 0,
    "shard_files": [],
}

models = [m for m in (data.get("models") or []) if m.get("id") != model_id]
models.append(entry)
data["models"] = models
tmp = registry_path.with_suffix(".tmp")
tmp.write_text(json.dumps(data, indent=2))
tmp.replace(registry_path)
REGISTRY_PY
  ok "Goose local-inference registry entry"
}

configure_goose_persistent_defaults() {
  [ -f "$MYCROFT_ENV" ] || return 0
  mkdir -p "$GOOSE_CONFIG"
  if [ -f "$GOOSE_CONFIG/config.yaml" ] && [ ! -f "$GOOSE_CONFIG/config.yaml.bak" ]; then
    cp "$GOOSE_CONFIG/config.yaml" "$GOOSE_CONFIG/config.yaml.bak"
  fi
  set -a
  . "$MYCROFT_ENV"
  set +a

  [ -n "${GOOSE_PROVIDER:-}" ] && set_goose_config_key GOOSE_PROVIDER "$GOOSE_PROVIDER"
  [ -n "${GOOSE_MODEL:-}" ] && set_goose_config_key GOOSE_MODEL "$GOOSE_MODEL"
  set_goose_config_key GOOSE_RECIPE_PATH "$GOOSE_RECIPE_PATH_VALUE"
  set_goose_config_key GOOSE_MOIM_MESSAGE_FILE "$MYCROFT_SOUL_FILE"

  store_goose_secret FIREWORKS_API_KEY "${FIREWORKS_API_KEY:-}"
  store_goose_secret FIRECRAWL_API_KEY "${FIRECRAWL_API_KEY:-}"
  store_goose_secret SCOUTPOST_API_KEY "${SCOUTPOST_API_KEY:-}"
  [ -n "${OSINT_NAV_API_KEY:-}" ] && store_goose_secret OSINT_NAV_API_KEY "$OSINT_NAV_API_KEY"

  # Scoutpost CLI config (if `scout` is installed): ~/.scoutpost/config.json from the
  # just-sourced key. REST-only hosts skip this and use SCOUTPOST_API_KEY from .env.
  write_scout_config

  ok "Goose default provider config"
}

write_if_missing() {
  local path="$1"
  if [ -e "$path" ]; then return 0; fi
  mkdir -p "$(dirname "$path")"
  # Seed-note heredocs are quoted so vault content never expands; the literal
  # token $TODAY is the one substitution they need.
  sed "s/\$TODAY/$TODAY/g" > "$path"
}

seed_mycroft_vault() {
  mkdir -p "$VAULT_PATH/_schema" "$VAULT_PATH/_audits" "$VAULT_PATH/context" "$VAULT_PATH/sources/raw" "$VAULT_PATH/sources/processed" "$VAULT_PATH/wiki/entities" "$VAULT_PATH/wiki/topics" "$VAULT_PATH/wiki/sources" "$VAULT_PATH/wiki/methods" "$VAULT_PATH/wiki/claims" "$VAULT_PATH/stories/pitches" "$VAULT_PATH/stories/drafts" "$VAULT_PATH/stories/published" "$VAULT_PATH/handoff/from-spotlight"
  write_if_missing "$VAULT_PATH/README.md" <<'VAULT_README_EOF'
---
type: vault-index
tags: [mycroft, index]
created: $TODAY
updated: $TODAY
---

# Mycroft Vault

This vault is the durable knowledge and story workspace Mycroft reads and writes through Goose recipes.

- _schema/ stores ingestion rules and note schemas.
- _audits/ stores scheduled vault audit reports.
- sources/raw/ stores immutable source material.
- sources/processed/ stores cleaned source extracts.
- wiki/ stores durable linked knowledge.
- stories/ stores publishable pitches, drafts, and finished work.
- handoff/from-spotlight/ stores findings promoted from Spotlight.
- context/ stores beat notes, source policy, and style guidance.
VAULT_README_EOF
  write_if_missing "$VAULT_PATH/START_HERE.md" <<'VAULT_START_EOF'
---
type: start-here
title: Start Here
description: First actions for a new Mycroft vault.
tags: [mycroft, start, onboarding]
created: $TODAY
updated: $TODAY
---

# Start Here

Ask Mycroft one of these:

- Set up my beat.
- Add these links/files/notes to my knowledge base: ...
- Create my morning brief.
- Investigate this lead: ...
- Set up scouts for these topics or pages: ...
- Show me a demo reporting workflow.

If the vault is still empty, start by adding material or defining your beat. Vault audits are useful later, after you have real notes.
VAULT_START_EOF
  write_if_missing "$VAULT_PATH/index.md" <<'VAULT_INDEX_EOF'
---
type: index
title: Mycroft Index
description: Entry point for the Mycroft knowledge vault.
tags: [mycroft, index]
created: $TODAY
updated: $TODAY
---

# Mycroft Index

- [[START_HERE]]

## Context

- [[context/beat-notes]]
- [[context/source-policy]]
- [[context/style-guide]]

## Knowledge

- Entities: wiki/entities/
- Topics: wiki/topics/
- Sources: wiki/sources/
- Methods: wiki/methods/
- Claims: wiki/claims/

## Stories

- Pitches: stories/pitches/
- Drafts: stories/drafts/
- Published: stories/published/

## Handoff

- Spotlight findings: handoff/from-spotlight/
VAULT_INDEX_EOF
  write_if_missing "$VAULT_PATH/log.md" <<'VAULT_LOG_EOF'
---
type: log
title: Mycroft Ingestion Log
description: Append-only log of durable knowledge ingestion.
tags: [mycroft, log]
created: $TODAY
updated: $TODAY
---

# Mycroft Ingestion Log

- $TODAY: Vault scaffold created.
VAULT_LOG_EOF
  write_if_missing "$VAULT_PATH/_schema/mycroft.md" <<'VAULT_SCHEMA_EOF'
---
type: schema
title: Mycroft Knowledge Schema
description: Rules for storing durable journalist knowledge in this vault.
tags: [mycroft, schema]
created: $TODAY
updated: $TODAY
---

# Mycroft Knowledge Schema

Use sources/raw for immutable source material, sources/processed for cleaned extracts, wiki for durable linked knowledge, and stories for publishable work.

Every durable note should include frontmatter, a clear title, confidence, source references, and links to related notes.
VAULT_SCHEMA_EOF
  write_if_missing "$VAULT_PATH/_schema/frontmatter.md" <<'VAULT_FRONTMATTER_EOF'
---
type: schema
title: Frontmatter
description: Minimum frontmatter fields for Mycroft notes.
tags: [mycroft, schema, frontmatter]
created: $TODAY
updated: $TODAY
---

# Frontmatter

Minimum fields:

title, description, type, created, updated, confidence, tags.
VAULT_FRONTMATTER_EOF
  write_if_missing "$VAULT_PATH/_schema/ingest-rules.md" <<'VAULT_INGEST_RULES_EOF'
---
type: schema
title: Ingest Rules
description: Rules for turning sources and Spotlight handoffs into durable knowledge.
tags: [mycroft, schema, ingest]
created: $TODAY
updated: $TODAY
---

# Ingest Rules

Preserve raw sources, create processed extracts, write atomic wiki notes, update index.md, and append log.md.

Spotlight handoffs should be promoted only after findings are confirmed or useful as durable knowledge.
VAULT_INGEST_RULES_EOF
  write_if_missing "$VAULT_PATH/context/source-policy.md" <<'VAULT_SOURCES_EOF'
---
type: context
name: Source Policy
tags: [mycroft, sources, context]
created: $TODAY
updated: $TODAY
---

# Source Policy

Use this note to define source-handling rules for this vault.

- Never paste confidential source identities into cloud tools unless explicitly cleared.
- Keep durable source records in wiki/sources/.
- Mark sensitive notes with sensitive: true in frontmatter.
VAULT_SOURCES_EOF
  write_if_missing "$VAULT_PATH/context/style-guide.md" <<'VAULT_STYLE_EOF'
---
type: context
name: Style Guide
tags: [mycroft, style, context]
created: $TODAY
updated: $TODAY
---

# Style Guide

- Lead with the verified point.
- Attribute factual claims.
- Separate evidence, inference, and unanswered questions.
VAULT_STYLE_EOF
  write_if_missing "$VAULT_PATH/context/beat-notes.md" <<'VAULT_BEAT_EOF'
---
type: context
name: Beat Notes
tags: [mycroft, beat, context]
created: $TODAY
updated: $TODAY
---

# Beat Notes

Add recurring beats, watchlists, and standing questions here.
VAULT_BEAT_EOF
  write_if_missing "$VAULT_PATH/stories/pitches/example-story-pitch.md" <<'VAULT_STORY_EOF'
---
type: story
title: Example Story Pitch
description: Placeholder showing how Spotlight findings can become a publishable story.
aliases: []
tags: [mycroft, story, pitch, example]
created: $TODAY
updated: $TODAY
confidence: unverified
---

# Example Story Pitch

## Angle

What is the publishable angle?

## Evidence

- Link confirmed findings and sources.

## Why Now

## Next Reporting

VAULT_STORY_EOF
  write_if_missing "$VAULT_PATH/wiki/entities/example-entity.md" <<'VAULT_ENTITY_EOF'
---
type: entity
title: Example Entity
description: Placeholder entity note.
aliases: []
tags: [mycroft, entity, example]
created: $TODAY
updated: $TODAY
confidence: unverified
---

# Example Entity

Replace this with a person, organisation, or place note.
VAULT_ENTITY_EOF
  write_if_missing "$VAULT_PATH/wiki/sources/example-source.md" <<'VAULT_SOURCE_EOF'
---
type: source
title: Example Source
description: Placeholder source note.
aliases: []
tags: [mycroft, source, example]
created: $TODAY
updated: $TODAY
confidence: unverified
sensitive: false
---

# Example Source

Use source notes for documents, URLs, interviews, datasets, and credibility assessments.
VAULT_SOURCE_EOF
  write_if_missing "$VAULT_PATH/wiki/methods/sift.md" <<'VAULT_SIFT_EOF'
---
type: methodology
title: SIFT
description: Stop, Investigate, Find, Trace verification method.
aliases: [Stop, Investigate, Find, Trace]
tags: [mycroft, methodology, verification]
created: $TODAY
updated: $TODAY
confidence: verified
---

# SIFT

- Stop.
- Investigate the source.
- Find better coverage.
- Trace claims to the original context.
VAULT_SIFT_EOF
  ok "Mycroft vault scaffold"
}

seed_spotlight_vault() {
  [ "$ENABLE_SPOTLIGHT" = "1" ] || return 0
  mkdir -p "$SPOTLIGHT_VAULT_PATH/cases/_template" "$SPOTLIGHT_VAULT_PATH/evidence" "$SPOTLIGHT_VAULT_PATH/captures" "$SPOTLIGHT_VAULT_PATH/briefs" "$SPOTLIGHT_VAULT_PATH/exports" "$SPOTLIGHT_VAULT_PATH/_schema"
  write_if_missing "$SPOTLIGHT_VAULT_PATH/README.md" <<'SPOTLIGHT_README_EOF'
---
type: spotlight-index
tags: [mycroft, spotlight, index]
created: $TODAY
updated: $TODAY
---

# Spotlight Vault

This vault is for OSINT casework and evidence trails. Keep durable knowledge in the Mycroft vault.

- cases/{project}/ stores active OSINT casework.
- evidence/ stores screenshots, captures, and chain-of-custody notes.
- captures/ stores raw browser captures and downloaded artefacts.
- briefs/ stores investigation briefings.
- exports/ stores reports and packaged outputs.
SPOTLIGHT_README_EOF
  write_if_missing "$SPOTLIGHT_VAULT_PATH/cases/_template/index.md" <<'SPOTLIGHT_TEMPLATE_EOF'
---
type: investigation-note
name: Spotlight Investigation Template
aliases: []
tags: [spotlight, investigation, template]
created: $TODAY
updated: $TODAY
project: _template
confidence: unverified
---

# Spotlight Investigation Template

## Objective

## Evidence Log

## Open Questions

## Promote To Mycroft

- Ask Mycroft to run the Spotlight ingest skill on approved findings; durable knowledge lands in the Mycroft vault.
SPOTLIGHT_TEMPLATE_EOF
  ok "Spotlight vault scaffold"
}

write_scheduled_recipes() {
  mkdir -p "$MYCROFT_GENERATED_RECIPES"
  cat > "$MYCROFT_GENERATED_RECIPES/morning-brief.scheduled.yaml" <<SCHEDULED_MORNING_EOF
version: "1.0.0"
title: "Mycroft scheduled morning brief"
description: "Generated by Mycroft setup. Runs the morning brief against the configured local vault paths."

instructions: |
  Load the Mycroft journalism instructions.
  Use the configured local monitoring profile and vault paths.
  Cite every item and write the brief into the Mycroft vault.

parameters: []

extensions:
  - type: builtin
    name: developer
  - type: stdio
    name: openknowledge
    cmd: ok
    args:
      - --cwd
      - $VAULT_PATH
      - mcp

prompt: |
  Run the Mycroft morning brief using these configured paths:

  - Mycroft vault: $VAULT_PATH
  - Knowledge logical space: mycroft
  - Monitoring profile: $MYCROFT_MORNING_BRIEF_CONFIG

  If the monitoring profile does not exist yet, continue with context/beat-notes.md and tell the user to run the Morning brief preflight recipe.

  Follow $MYCROFT_DIR/recipes/morning-brief.yaml exactly. Write the result to:

  $VAULT_PATH/stories/drafts/morning-brief-YYYY-MM-DD.md
SCHEDULED_MORNING_EOF

  cat > "$MYCROFT_GENERATED_RECIPES/vault-audit.scheduled.yaml" <<SCHEDULED_AUDIT_EOF
version: "1.0.0"
title: "Mycroft scheduled vault audit"
description: "Generated by Mycroft setup. Audits the configured Mycroft vault and optional Spotlight handoffs."

instructions: |
  Load the Mycroft journalism instructions and knowledge-primitives skill.
  Audit the configured vault paths. Do not rewrite user notes; write a dated report.

parameters: []

extensions:
  - type: builtin
    name: developer
  - type: stdio
    name: openknowledge
    cmd: ok
    args:
      - --cwd
      - $VAULT_PATH
      - mcp

prompt: |
  Run the Mycroft vault audit using these configured paths:

  - Mycroft vault: $VAULT_PATH
  - Spotlight vault: $SPOTLIGHT_VAULT_PATH
  - Report directory: $VAULT_PATH/_audits

  Follow $MYCROFT_DIR/recipes/vault-audit.yaml exactly. Write the result to:

  $VAULT_PATH/_audits/vault-audit-YYYY-MM-DD.md
SCHEDULED_AUDIT_EOF

  ok "generated scheduled Goose recipes"
}

install_goose_schedules() {
  [ "$INSTALL_GOOSE" = "1" ] || return 0
  have goose || { warn "Goose CLI not found; open Goose Scheduler and add Mycroft schedules manually."; return 0; }
  set -a
  . "$MYCROFT_ENV"
  set +a
  export GOOSE_RECIPE_PATH="$GOOSE_RECIPE_PATH_VALUE"

  goose schedule remove --schedule-id mycroft-morning-brief >/dev/null 2>&1 || true
  goose schedule remove --schedule-id mycroft-vault-audit >/dev/null 2>&1 || true

  if goose schedule add --schedule-id mycroft-morning-brief --cron "0 0 7 * * *" --recipe-source "$MYCROFT_GENERATED_RECIPES/morning-brief.scheduled.yaml" >/dev/null 2>&1; then
    ok "Goose schedule mycroft-morning-brief"
  else
    warn "Could not create Goose morning-brief schedule; use Goose Scheduler with $MYCROFT_GENERATED_RECIPES/morning-brief.scheduled.yaml"
  fi

  if goose schedule add --schedule-id mycroft-vault-audit --cron "0 15 18 * * *" --recipe-source "$MYCROFT_GENERATED_RECIPES/vault-audit.scheduled.yaml" >/dev/null 2>&1; then
    ok "Goose schedule mycroft-vault-audit"
  else
    warn "Could not create Goose vault-audit schedule; use Goose Scheduler with $MYCROFT_GENERATED_RECIPES/vault-audit.scheduled.yaml"
  fi
}

open_obsidian_vaults() {
  [ "$INSTALL_OBSIDIAN" = "1" ] || return 0
  if [ "$(uname -s)" = "Darwin" ]; then
    open -a Obsidian "$VAULT_PATH" 2>/dev/null || open -a Obsidian 2>/dev/null || true
    if [ "$ENABLE_SPOTLIGHT" = "1" ]; then open -a Obsidian "$SPOTLIGHT_VAULT_PATH" 2>/dev/null || true; fi
    ok "Obsidian opened"
  fi
}

open_goose_start() {
  [ "$INSTALL_GOOSE" = "1" ] || return 0
  if [ "$(uname -s)" = "Darwin" ]; then
    if have goose && [ ! -f "$MYCROFT_MORNING_BRIEF_CONFIG" ]; then
      goose recipe open "$MYCROFT_DIR/recipes/start.yaml" --param vault_path="$VAULT_PATH" --param vault_name="Mycroft" --param morning_brief_config_path="$MYCROFT_MORNING_BRIEF_CONFIG" >/dev/null 2>&1 || open -a Goose 2>/dev/null || open -a block-goose 2>/dev/null || true
    else
      open -a Goose 2>/dev/null || open -a block-goose 2>/dev/null || true
    fi
    ok "Goose opened"
  elif have goose; then
    if [ ! -f "$MYCROFT_MORNING_BRIEF_CONFIG" ]; then
      goose run --recipe "$MYCROFT_DIR/recipes/start.yaml" --interactive --params vault_path="$VAULT_PATH" --params vault_name="Mycroft" --params morning_brief_config_path="$MYCROFT_MORNING_BRIEF_CONFIG" || true
    else
      goose recipe list >/dev/null 2>&1 || true
    fi
    ok "Goose CLI ready"
  fi
}

say "Mycroft installer"
mkdir -p "$GOOSE_CONFIG" "$PROVIDERS_DST" "$MYCROFT_PROFILE_DIR" "$MYCROFT_DATA_DIR" "$PLUGINS_DIR"
warn_legacy_layout
ensure_git
if [ "$PUBLIC_BUNDLE_PHASE" = "0" ]; then
  install_or_update_mycroft
elif [ ! -d "$MYCROFT_DIR/.git" ]; then
  echo "Mycroft installer: the signed public bundle did not create the product checkout" >&2
  exit 1
fi

PREFLIGHT_HELPER="$MYCROFT_DIR/scripts/install-preflight.sh"
if [ ! -f "$PREFLIGHT_HELPER" ]; then
  warn "Installer preflight helper missing: $PREFLIGHT_HELPER"
  exit 1
fi
# shellcheck source=scripts/install-preflight.sh
. "$PREFLIGHT_HELPER"

# ── Configure: local page in your browser; keys stay on 127.0.0.1 ──
MYCROFT_SETUP_CONFIG="$MYCROFT_PROFILE_DIR/setup-config.env"
if ! have python3; then
  warn "python3 is required for the setup page. On macOS it arrives with the developer tools (installed alongside git); on Linux use your package manager. Then re-run this installer."
  exit 1
fi
say "Opening the Mycroft configurator in your browser"
echo "  Your choices and API keys go to a local server on 127.0.0.1 only and are"
echo "  written to $MYCROFT_PROFILE_DIR — nothing is uploaded anywhere."
python3 "$MYCROFT_DIR/install/setup_server.py" --profile-dir "$MYCROFT_PROFILE_DIR" --repo-dir "$MYCROFT_DIR" --legacy-only
if [ ! -f "$MYCROFT_SETUP_CONFIG" ]; then
  warn "Configuration was not completed; re-run the installer to try again."
  exit 1
fi
set -a
. "$MYCROFT_SETUP_CONFIG"
set +a

# Sovereign stack defaults: SearXNG search + Crawl4AI scrape install by
# default; Tor is opt-in opsec (off); Firecrawl is the optional escape hatch
# (off unless the configurator/env asks for it → absence = pure-sovereign).
INSTALL_CRAWL4AI="${INSTALL_CRAWL4AI:-1}"
INSTALL_SEARXNG="${INSTALL_SEARXNG:-1}"
INSTALL_TOR="${INSTALL_TOR:-0}"
INSTALL_FIRECRAWL="${INSTALL_FIRECRAWL:-0}"

# QMD is a core capability and installs native modules. Fix a root-owned npm
# prefix before the first global package write, and reject the incomplete Linux
# toolchain once with the complete dependency command instead of failing several
# minutes into npm's build.
if ! have qmd || [ "$INSTALL_FIRECRAWL" = "1" ] || [ "$ENABLE_SCOUTPOST" = "1" ] || \
   { [ "$ENABLE_SPOTLIGHT" = "1" ] && [ "${SPOT_DEVBROWSER:-1}" = "1" ]; }; then
  mycroft_prepare_npm_prefix || exit 1
fi
if ! have qmd; then
  mycroft_preflight_linux_build_tools || exit 1
fi

SPOTLIGHT_VAULT_PATH="$SPOTLIGHT_VAULT_INPUT"
if [ "$SPOTLIGHT_VAULT_PATH" = "$VAULT_PATH" ]; then
  SPOTLIGHT_VAULT_PATH="$VAULT_PATH/Spotlight"
fi
SPOTLIGHT_INGEST_TARGET="$VAULT_PATH"
if [ "$ENABLE_SPOTLIGHT" = "1" ]; then SPOTLIGHT_JSON=true; else SPOTLIGHT_JSON=false; fi
if [ "$ENABLE_SCOUTPOST" = "1" ]; then SCOUTPOST_JSON=true; else SCOUTPOST_JSON=false; fi
if [ "${SPOT_DEVBROWSER:-1}" = "1" ]; then DEVBROWSER_JSON=true; else DEVBROWSER_JSON=false; fi
if [ "${HAS_OSINT_NAVIGATOR:-0}" = "1" ]; then OSINT_NAVIGATOR_JSON=true; else OSINT_NAVIGATOR_JSON=false; fi
if [ "${HAS_JUNKIPEDIA:-0}" = "1" ]; then JUNKIPEDIA_JSON=true; else JUNKIPEDIA_JSON=false; fi

mkdir -p "$VAULT_PATH" && ok "Mycroft vault $VAULT_PATH"
ensure_goose
install_obsidian
# Sovereign stack first (default path) via the shared idempotent provisioner —
# the same script mycroft-update runs, so updates provision the backends too.
# Container/image/settings are left to the provisioner's own (identical) defaults;
# only the values install.sh needs elsewhere (port) or that key the settings path
# (profile dir) are forwarded.
INSTALL_CRAWL4AI="$INSTALL_CRAWL4AI" INSTALL_SEARXNG="$INSTALL_SEARXNG" INSTALL_TOR="$INSTALL_TOR" \
  SEARXNG_PORT="$SEARXNG_PORT" MYCROFT_PROFILE_DIR="$MYCROFT_PROFILE_DIR" \
  bash "$MYCROFT_DIR/scripts/provision-sovereign.sh" || true
# ...then the optional Firecrawl escape hatch (gated, off by default).
install_firecrawl
ensure_qmd
ensure_openknowledge
install_scout_cli
install_mycroft_cli
sync_mycroft_profile
seed_mycroft_vault
seed_spotlight_vault
configure_qmd

mkdir -p "$PROVIDERS_DST"
# Clean up obsolete custom providers: pre-2026-05 installers copied local-*
# shims (we now use Goose's built-in Local Inference); the Qwen/Together/
# OpenRouter cloud providers were retired for the single ZDR Fireworks GLM-5.2
# frontier, so drop any stale copies an upgrader still has.
rm -f "$PROVIDERS_DST/local-llama-server.json" "$PROVIDERS_DST/local-mlx.json" \
      "$PROVIDERS_DST/fireworks-qwen36plus.json" "$PROVIDERS_DST/together-qwen.json" \
      "$PROVIDERS_DST/openrouter-fallback.json"
if [ "$ENABLE_FIREWORKS" = "1" ]; then
  cp "$MYCROFT_DIR/providers/fireworks-glm52.json" "$PROVIDERS_DST/"
  ok "Fireworks — GLM-5.2 (ZDR)"
fi
install_skill_registry
write_goose_instructions

if [ ! -f "$MYCROFT_ENV" ]; then
  warn "Missing $MYCROFT_ENV — the configurator did not finish; re-run the installer."
  exit 1
fi
chmod 600 "$MYCROFT_ENV"
# Point the sovereign search tools at the provisioned SearXNG (the shell rc block
# and goose profile source this env). Tools default to the same URL if absent.
if ! grep -q '^SEARXNG_URL=' "$MYCROFT_ENV" 2>/dev/null; then
  printf 'SEARXNG_URL="%s"\n' "$SEARXNG_URL_VALUE" >> "$MYCROFT_ENV"
fi
ok "Mycroft environment $MYCROFT_ENV"
install_local_model
configure_goose_persistent_defaults

if [ "$ENABLE_SPOTLIGHT" = "1" ]; then
  mkdir -p "$PLUGINS_DIR"
  if [ -d "$SPOTLIGHT_DIR/.git" ]; then update_repo "$SPOTLIGHT_DIR" "Spotlight"; else git clone https://github.com/buriedsignals/spotlight.git "$SPOTLIGHT_DIR" && ok "Spotlight cloned"; fi
  mkdir -p "$SPOTLIGHT_VAULT_PATH" && ok "Spotlight vault $SPOTLIGHT_VAULT_PATH"
  if [ "${SPOT_DEVBROWSER:-1}" = "1" ]; then
    # dev-browser is Spotlight's primary browser-automation path (keyless).
    # Version pinned to Spotlight's VALIDATED_DEPENDENCIES.md.
    if ! have dev-browser; then
      if have npm; then
        npm install -g dev-browser@0.2.8 && ok "dev-browser CLI"
      else
        warn "npm missing; install dev-browser manually: npm install -g dev-browser@0.2.8"
      fi
    else
      ok "dev-browser present"
    fi
    if have dev-browser; then
      dev-browser install >/dev/null 2>&1 && ok "dev-browser Chromium" || warn "dev-browser Chromium download failed; run dev-browser install later"
    fi
  fi
  NOW_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  cat > "$SPOTLIGHT_DIR/.spotlight-config.json" <<CONFIG_EOF
{
  "search_library": "firecrawl",
  "vault_path": "$SPOTLIGHT_VAULT_PATH",
  "vault_type": "obsidian",
  "vault_app": "obsidian",
  "case_workspace_root": "$SPOTLIGHT_VAULT_PATH/cases",
  "cases_root": "$SPOTLIGHT_VAULT_PATH/cases",
  "install_path": "$SPOTLIGHT_DIR",
  "mode": "$([ "$LOCAL_ONLY" = "1" ] && echo local || echo cloud)",
  "runtime": "goose",
  "local_server": null,
  "agent": null,
  "opencode_provider": null,
  "installed_by": "mycroft",
  "mycroft_config": "$MYCROFT_CONFIG",
  "mycroft_vault_path": "$VAULT_PATH",
  "ingest_target": "$SPOTLIGHT_INGEST_TARGET",
  "integrations": {
    "osint_navigator": {"enabled": $OSINT_NAVIGATOR_JSON, "status": "unknown", "source": "mycroft-setup"},
    "junkipedia": {"enabled": $JUNKIPEDIA_JSON, "status": "unknown", "source": "mycroft-setup"},
    "dev_browser": {"enabled": $DEVBROWSER_JSON, "status": "unknown", "source": "mycroft-setup"},
    "unpaywall": {"enabled": false, "status": "unknown", "source": "mycroft-setup"},
    "rlm": {"enabled": false, "mode": "off", "model": null, "prefilter": false, "hybrid": false, "evidence_boundary": "lead-only; never verified or publishable"}
  },
  "created_at": "$NOW_UTC",
  "last_used": "$NOW_UTC"
}
CONFIG_EOF
  [ -f "$SPOTLIGHT_DIR/integrations/preflight.py" ] && (set -a; . "$MYCROFT_ENV"; set +a; python3 "$SPOTLIGHT_DIR/integrations/preflight.py" --text || true)
fi
if [ "$ENABLE_SCOUTPOST" = "1" ]; then
  ok "Scoutpost hosted API enabled"
fi

cat > "$MYCROFT_CONFIG" <<CONFIG_EOF
{
  "version": 1,
  "installed_by": "mycroft-setup",
  "paths": {
    "profile": "$MYCROFT_PROFILE_DIR",
    "data": "$MYCROFT_DATA_DIR",
    "source": "$MYCROFT_DIR",
    "plugins": "$PLUGINS_DIR",
    "env": "$MYCROFT_ENV"
  },
  "goose": {
    "config_dir": "$GOOSE_CONFIG",
    "custom_providers_dir": "$PROVIDERS_DST",
    "hints_file": "$GOOSE_CONFIG/.goosehints",
    "recipe_path": "$GOOSE_RECIPE_PATH_VALUE",
    "instructions_file": "$MYCROFT_GOOSE_INSTRUCTIONS",
    "soul_file": "$MYCROFT_SOUL_FILE",
    "generated_recipes": "$MYCROFT_GENERATED_RECIPES",
    "schedules": {
      "morning_brief": "mycroft-morning-brief",
      "vault_audit": "mycroft-vault-audit"
    }
  },
  "skills": {
    "registry": "$MYCROFT_SKILL_REGISTRY",
    "directory": "$MYCROFT_SKILLS_DIR"
  },
  "vaults": {
    "mycroft": "$VAULT_PATH",
    "spotlight": "$SPOTLIGHT_VAULT_PATH",
    "spotlight_ingest_target": "$SPOTLIGHT_INGEST_TARGET"
  },
  "sovereignty": {
    "default": "$SOVEREIGNTY",
    "local_only": "$LOCAL_ONLY",
    "local_model": "$LOCAL_MODEL"
  },
  "plugins": {
    "spotlight": {"enabled": $SPOTLIGHT_JSON, "path": "$SPOTLIGHT_DIR", "inherits_mycroft_sovereignty": true},
    "scoutpost": {"enabled": $SCOUTPOST_JSON, "mode": "hosted", "api_base": "https://www.scoutpost.ai/api/v1"}
  }
}
CONFIG_EOF
ok "Mycroft config $MYCROFT_CONFIG"

write_scheduled_recipes
install_goose_schedules

mkdir -p "$HOME/.local/bin" "$XDG_DATA_HOME/mycroft"


if [ "$(uname -s)" = "Darwin" ]; then
  legacy_plist="$HOME/Library/LaunchAgents/com.buriedsignals.mycroft.update.plist"
  if [ -f "$legacy_plist" ]; then
    launchctl unload "$legacy_plist" >/dev/null 2>&1 || true
    rm -f "$legacy_plist"
    ok "removed old Mycroft LaunchAgent"
  fi
  (crontab -l 2>/dev/null | grep -v 'mycroft-update'; printf '15 10 * * 1 %s/.local/bin/mycroft-update\n' "$HOME") | crontab - && ok "weekly updater cron"
elif have systemctl; then
  mkdir -p "$XDG_CONFIG_HOME/systemd/user"
  cat > "$XDG_CONFIG_HOME/systemd/user/mycroft-update.service" <<SERVICE_EOF
[Unit]
Description=Update Mycroft and bundled plugins

[Service]
Type=oneshot
ExecStart=%h/.local/bin/mycroft-update
SERVICE_EOF
  cat > "$XDG_CONFIG_HOME/systemd/user/mycroft-update.timer" <<TIMER_EOF
[Unit]
Description=Weekly Mycroft update

[Timer]
OnCalendar=Mon *-*-* 10:15:00
Persistent=true

[Install]
WantedBy=timers.target
TIMER_EOF
  systemctl --user daemon-reload >/dev/null 2>&1 || true
  systemctl --user enable --now mycroft-update.timer >/dev/null 2>&1 || warn "systemd timer written; enable it with systemctl --user enable --now mycroft-update.timer"
  ok "weekly updater systemd timer"
else
  (crontab -l 2>/dev/null | grep -v 'mycroft-update'; printf '15 10 * * 1 %s/.local/bin/mycroft-update\n' "$HOME") | crontab - && ok "weekly updater cron"
fi

open_obsidian_vaults
open_goose_start

MARKER_START='# === mycroft ==='
MARKER_END='# === /mycroft ==='
tmp_rc="$(mktemp)"
if [ -f "$SHELL_RC" ]; then
  awk -v start="$MARKER_START" -v end="$MARKER_END" '
    $0 == start {skip=1; next}
    $0 == end {skip=0; next}
    !skip {print}
  ' "$SHELL_RC" > "$tmp_rc"
else
  : > "$tmp_rc"
fi
{
  printf '\n%s\n' "$MARKER_START"
  printf 'export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"\n'
  printf 'export MYCROFT_DIR="%s"\n' "$MYCROFT_DIR"
  printf 'export MYCROFT_PROFILE_DIR="%s"\n' "$MYCROFT_PROFILE_DIR"
  printf 'export MYCROFT_DATA_DIR="%s"\n' "$MYCROFT_DATA_DIR"
  printf 'export MYCROFT_CONFIG="%s"\n' "$MYCROFT_CONFIG"
  printf 'export GOOSE_RECIPE_PATH="%s"\n' "$GOOSE_RECIPE_PATH_VALUE"
  printf '[ -f "%s" ] && set -a && . "%s" && set +a\n' "$MYCROFT_ENV" "$MYCROFT_ENV"
  printf 'mycroft() {\n'
  printf '  case "${1:-}" in\n'
  printf '    update) "$HOME/.local/bin/mycroft-update" ;;\n'
  printf '    uninstall) "$HOME/.local/bin/mycroft-uninstall" ;;\n'
  printf '    doctor) "$HOME/.local/bin/mycroft-doctor" ;;\n'
  printf '    *) goose recipe list ;;\n'
  printf '  esac\n'
  printf '}\n'
  printf '%s\n' "$MARKER_END"
} >> "$tmp_rc"
mv "$tmp_rc" "$SHELL_RC"

say "Verifying Mycroft installation"
if GOOSE_RECIPE_PATH="$GOOSE_RECIPE_PATH_VALUE" "$HOME/.local/bin/mycroft-doctor"; then
  ok "Mycroft doctor passed"
else
  warn "Mycroft doctor failed; setup is incomplete and the installer is exiting non-zero."
  exit 1
fi

GETTING_STARTED="$MYCROFT_PROFILE_DIR/getting-started.html"
if [ -f "$GETTING_STARTED" ]; then
  if [ "$(uname -s)" = "Darwin" ]; then
    open "$GETTING_STARTED" 2>/dev/null || true
  elif have xdg-open; then
    xdg-open "$GETTING_STARTED" >/dev/null 2>&1 || true
  fi
  ok "Getting-started guide: $GETTING_STARTED"
fi

say "Mycroft setup complete"
echo "Open a new terminal, then run: mycroft doctor"
echo "Manual update anytime: mycroft update"
echo "Getting-started guide: $GETTING_STARTED"
