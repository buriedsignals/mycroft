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

TODAY="$(date +%F)"

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

if   [ -f "$HOME/.zshrc" ];  then SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then SHELL_RC="$HOME/.bashrc"
else SHELL_RC="$HOME/.zshrc"; touch "$SHELL_RC"
fi

have() { command -v "$1" >/dev/null 2>&1; }
say()  { printf "\n\033[1;34m>\033[0m %s\n" "$*"; }
ok()   { printf "  \033[1;32m+\033[0m %s\n" "$*"; }
warn() { printf "  \033[1;33m!\033[0m %s\n" "$*"; }

ensure_brew() {
  if have brew; then return 0; fi
  if [ "$(uname -s)" != "Darwin" ]; then return 1; fi
  say "Homebrew is needed for macOS app installs. Install it now? [Y/n]"
  read -r ans || ans="Y"
  if [[ "$ans" =~ ^[Nn] ]]; then return 1; fi
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  [ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
  [ -x /usr/local/bin/brew ] && eval "$(/usr/local/bin/brew shellenv)"
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
      ensure_brew && brew install --cask block-goose && ok "Goose Desktop"
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
    else ensure_brew && brew install --cask obsidian && ok "Obsidian"; fi
    if ! have obsidian; then
      warn "Open Obsidian, then enable Settings -> General -> Advanced -> Command Line Interface."
      open -a Obsidian 2>/dev/null || true
    fi
  else
    warn "Install Obsidian manually on Linux and enable its CLI if your package includes it."
  fi
}

install_firecrawl() {
  [ "$INSTALL_FIRECRAWL" = "1" ] || return 0
  if have firecrawl; then ok "firecrawl present"; return 0; fi
  if ! have npm && [ "$(uname -s)" = "Darwin" ]; then ensure_brew && brew install node; fi
  if have npm; then npm install -g firecrawl-cli && ok "firecrawl"; else warn "npm missing; install firecrawl-cli manually."; fi
}

ensure_qmd() {
  if have qmd; then ok "QMD CLI present"; return 0; fi
  if ! have npm && [ "$(uname -s)" = "Darwin" ]; then ensure_brew && brew install node; fi
  if have npm; then npm install -g @tobilu/qmd && ok "QMD CLI"; else warn "npm missing; install QMD manually with: npm install -g @tobilu/qmd"; fi
}

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
}

install_skill_registry() {
  mkdir -p "$MYCROFT_PROFILE_SKILLS_DIR" "$MYCROFT_SKILLS_DIR"
  if [ "$ENABLE_SCOUTPOST" = "1" ] && have curl; then
    mkdir -p "$MYCROFT_PROFILE_SKILLS_DIR/scoutpost"
    curl -fsSL https://scoutpost.ai/skills/scoutpost.md -o "$MYCROFT_PROFILE_SKILLS_DIR/scoutpost/SKILL.md" || cp "$MYCROFT_SKILLS_DIR/scoutpost/SKILL.md" "$MYCROFT_PROFILE_SKILLS_DIR/scoutpost/SKILL.md" || warn "Using bundled Scoutpost skill; hosted product skill could not be fetched."
  fi
  if [ ! -f "$MYCROFT_SKILL_REGISTRY" ]; then
    warn "Missing $MYCROFT_SKILL_REGISTRY — the configurator did not finish; re-run the installer."
    exit 1
  fi
  # Surface skills where Goose discovers them: per-skill symlinks under
  # ~/.agents/skills/mycroft/<skill> (engine-matching <root>/<product>/<skill>
  # shape; Goose scans ~/.agents/skills recursively). Goose does not read the
  # skill registry's "directory" pointer, so without these links the curated
  # skills are off its discovery path.
  mkdir -p "$HOME/.agents/skills/mycroft"
  # Skill set = the engine-resolved manifest (generated by `bsig skills resolve`,
  # vendored as skills.manifest). The engine catalog is the source of truth; this
  # installs exactly the Goose-runtime-correct set. Falls back to the on-disk
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
  if [ "$ENABLE_SCOUTPOST" = "1" ] && [ -d "$MYCROFT_PROFILE_SKILLS_DIR/scoutpost" ]; then
    ln -sfn "$MYCROFT_PROFILE_SKILLS_DIR/scoutpost" "$HOME/.agents/skills/mycroft/scoutpost"
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
Prefer MCP if configured, then the scout CLI if installed, then the hosted API with SCOUTPOST_API_KEY and SCOUTPOST_API_BASE.
Never print the API key.
GOOSE_SCOUTPOST_EOF
  fi
  cp "$MYCROFT_GOOSE_INSTRUCTIONS" "$GOOSE_CONFIG/.goosehints"
  ok "Goose global .goosehints"
}

sync_mycroft_profile() {
  mkdir -p "$MYCROFT_PROFILE_DIR"
  if [ -f "$MYCROFT_DIR/instructions/mycroft-soul.md" ]; then
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
  store_goose_secret TOGETHER_API_KEY "${TOGETHER_API_KEY:-}"
  store_goose_secret FIRECRAWL_API_KEY "${FIRECRAWL_API_KEY:-}"
  store_goose_secret SCOUTPOST_API_KEY "${SCOUTPOST_API_KEY:-}"
  store_goose_secret OSINT_NAV_API_KEY "${OSINT_NAV_API_KEY:-}"

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

prompt: |
  Run the Mycroft morning brief using these configured paths:

  - Mycroft vault: $VAULT_PATH
  - Obsidian vault name: Mycroft
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
install_or_update_mycroft

# ── Configure: local page in your browser; keys stay on 127.0.0.1 ──
MYCROFT_SETUP_CONFIG="$MYCROFT_PROFILE_DIR/setup-config.env"
if ! have python3; then
  warn "python3 is required for the setup page. On macOS it arrives with the developer tools (installed alongside git); on Linux use your package manager. Then re-run this installer."
  exit 1
fi
say "Opening the Mycroft configurator in your browser"
echo "  Your choices and API keys go to a local server on 127.0.0.1 only and are"
echo "  written to $MYCROFT_PROFILE_DIR — nothing is uploaded anywhere."
python3 "$MYCROFT_DIR/install/setup_server.py" --profile-dir "$MYCROFT_PROFILE_DIR" --repo-dir "$MYCROFT_DIR"
if [ ! -f "$MYCROFT_SETUP_CONFIG" ]; then
  warn "Configuration was not completed; re-run the installer to try again."
  exit 1
fi
set -a
. "$MYCROFT_SETUP_CONFIG"
set +a

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
install_firecrawl
ensure_qmd
install_mycroft_cli
sync_mycroft_profile
seed_mycroft_vault
seed_spotlight_vault
configure_qmd

mkdir -p "$PROVIDERS_DST"
# Clean up obsolete custom providers (pre-2026-05 installer copied these; we now use Goose's built-in Local Inference)
rm -f "$PROVIDERS_DST/local-llama-server.json" "$PROVIDERS_DST/local-mlx.json"
if [ "$ENABLE_FIREWORKS" = "1" ]; then
  cp "$MYCROFT_DIR/providers/fireworks-qwen36plus.json" "$PROVIDERS_DST/"
  ok "Fireworks"
fi
if [ "$ENABLE_TOGETHER" = "1" ]; then
  cp "$MYCROFT_DIR/providers/together-qwen.json" "$PROVIDERS_DST/"
  ok "Together"
fi
install_skill_registry
write_goose_instructions

if [ ! -f "$MYCROFT_ENV" ]; then
  warn "Missing $MYCROFT_ENV — the configurator did not finish; re-run the installer."
  exit 1
fi
chmod 600 "$MYCROFT_ENV"
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
    "rlm": {"enabled": false, "mode": "off", "model": null, "prefilter": false, "hybrid": false, "evidence_boundary": "lead-only; never verified or publishable"},
    "scoutpost": {"enabled": $SCOUTPOST_JSON, "status": "unknown", "source": "mycroft-setup", "api_base": "https://www.scoutpost.ai/api/v1"}
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
cat > "$HOME/.local/bin/mycroft-doctor" <<'DOCTOR_EOF'
#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
fail=0
ok_check() { printf "OK    %s\n" "$*"; }
bad_check() { printf "FAIL  %s\n" "$*"; fail=1; }
check_path() {
  if [ -e "$1" ]; then ok_check "$2"; else bad_check "$2 missing: $1"; fi
}

GOOSE_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/goose"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
MYCROFT_PROFILE_DIR="${MYCROFT_PROFILE_DIR:-$GOOSE_CONFIG/mycroft}"
MYCROFT_DATA_DIR="${MYCROFT_DATA_DIR:-$XDG_DATA_HOME/goose/mycroft}"
MYCROFT_DIR="${MYCROFT_DIR:-$MYCROFT_DATA_DIR/source}"
MYCROFT_ENV="$MYCROFT_PROFILE_DIR/.env"
MYCROFT_CONFIG="${MYCROFT_CONFIG:-$MYCROFT_PROFILE_DIR/mycroft-config.json}"
MYCROFT_SKILL_REGISTRY="$MYCROFT_PROFILE_DIR/skill-registry.json"
MYCROFT_GOOSE_INSTRUCTIONS="$MYCROFT_PROFILE_DIR/goose-mycroft.md"
MYCROFT_SOUL_FILE="$MYCROFT_PROFILE_DIR/SOUL.md"
PROVIDERS_DST="$GOOSE_CONFIG/custom_providers"
RECIPE_PATH="$MYCROFT_DIR/recipes"
REQUIRED_ENV=""
if [ -f "$MYCROFT_PROFILE_DIR/setup-config.env" ]; then
  REQUIRED_ENV="$(. "$MYCROFT_PROFILE_DIR/setup-config.env" 2>/dev/null; printf '%s' "${REQUIRED_DOCTOR_ENV:-}")"
fi

check_path "$MYCROFT_DIR/.git" "Mycroft repo"
check_path "$MYCROFT_PROFILE_DIR" "Mycroft Goose profile"
check_path "$MYCROFT_CONFIG" "Mycroft config"
check_path "$MYCROFT_SKILL_REGISTRY" "Mycroft skill registry"
check_path "$MYCROFT_GOOSE_INSTRUCTIONS" "Mycroft Goose instructions"
check_path "$MYCROFT_SOUL_FILE" "Mycroft soul"
check_path "$MYCROFT_DIR/skills/knowledge-primitives/SKILL.md" "knowledge-primitives skill"
check_path "$MYCROFT_DIR/skills/qmd/SKILL.md" "QMD skill"
check_path "$MYCROFT_DIR/skills/obsidian-ingest/SKILL.md" "obsidian-ingest skill"
check_path "$MYCROFT_DIR/skills/fact-check/SKILL.md" "fact-check skill"
check_path "$MYCROFT_DIR/skills/copywriting/SKILL.md" "copywriting skill"
check_path "$MYCROFT_DIR/scripts/mycroft-fetch" "mycroft-fetch source"
check_path "$HOME/.local/bin/mycroft-fetch" "mycroft-fetch command"
check_path "$MYCROFT_DIR/scripts/mycroft_safe.py" "mycroft_safe.py source"
check_path "$HOME/.local/bin/mycroft-safe" "mycroft-safe command"
check_path "$MYCROFT_DIR/skills/shell-safety/SKILL.md" "shell-safety skill"
check_path "$MYCROFT_DIR/skills/epistemic-grounding/SKILL.md" "epistemic-grounding skill"
check_path "$RECIPE_PATH" "Mycroft recipes"
check_path "$MYCROFT_PROFILE_DIR/generated-recipes/morning-brief.scheduled.yaml" "scheduled morning brief recipe"
check_path "$MYCROFT_PROFILE_DIR/generated-recipes/vault-audit.scheduled.yaml" "scheduled vault audit recipe"
check_path "$GOOSE_CONFIG" "Goose config dir"
check_path "$PROVIDERS_DST" "Goose custom providers dir"
check_path "$GOOSE_CONFIG/config.yaml" "Goose config file"
check_path "$GOOSE_CONFIG/.goosehints" "Goose hints"
check_path "$MYCROFT_ENV" "Mycroft env"

if [ -f "$MYCROFT_ENV" ]; then
  set -a
  . "$MYCROFT_ENV"
  set +a
  for name in $REQUIRED_ENV; do
    if [ -n "${!name:-}" ]; then ok_check "$name present"; else bad_check "$name missing or empty"; fi
  done
fi

if [ -f "$GOOSE_CONFIG/config.yaml" ]; then
  if grep -q '^GOOSE_PROVIDER:' "$GOOSE_CONFIG/config.yaml"; then ok_check "Goose provider persisted"; else bad_check "GOOSE_PROVIDER missing from Goose config"; fi
  if grep -q '^GOOSE_MODEL:' "$GOOSE_CONFIG/config.yaml"; then ok_check "Goose model persisted"; else bad_check "GOOSE_MODEL missing from Goose config"; fi
  if grep -q '^GOOSE_MOIM_MESSAGE_FILE:' "$GOOSE_CONFIG/config.yaml"; then ok_check "Goose Mycroft soul persisted"; else bad_check "GOOSE_MOIM_MESSAGE_FILE missing from Goose config"; fi
fi

case ":${GOOSE_RECIPE_PATH:-}:" in
  *":$RECIPE_PATH:"*) ok_check "GOOSE_RECIPE_PATH includes $RECIPE_PATH" ;;
  *) bad_check "GOOSE_RECIPE_PATH missing $RECIPE_PATH" ;;
esac

if command -v goose >/dev/null 2>&1; then ok_check "Goose CLI"; else bad_check "Goose CLI missing"; fi
if command -v qmd >/dev/null 2>&1; then ok_check "QMD CLI"; else bad_check "QMD CLI missing"; fi
if command -v mycroft-fetch >/dev/null 2>&1; then ok_check "mycroft-fetch CLI"; else bad_check "mycroft-fetch CLI missing from PATH"; fi
if command -v mycroft-safe >/dev/null 2>&1; then
  if mycroft-safe validate-url "https://example.org/ok" >/dev/null 2>&1; then
    ok_check "mycroft-safe CLI"
  else
    bad_check "mycroft-safe CLI present but validator failed"
  fi
else
  bad_check "mycroft-safe CLI missing from PATH"
fi
if [ -d "$MYCROFT_DATA_DIR/plugins/spotlight" ]; then
  ok_check "Spotlight plugin"
  check_path "$MYCROFT_DATA_DIR/plugins/spotlight/.spotlight-config.json" "Spotlight config"
  check_path "$MYCROFT_DATA_DIR/plugins/spotlight/skills/ingest/SKILL.md" "Spotlight ingest skill"
fi

if [ "$fail" -eq 0 ]; then
  printf "\nMycroft doctor: OK\n"
else
  printf "\nMycroft doctor: failed\n"
fi
exit "$fail"
DOCTOR_EOF
chmod +x "$HOME/.local/bin/mycroft-doctor"

cat > "$HOME/.local/bin/mycroft-update" <<'UPDATE_EOF'
#!/usr/bin/env bash
set -euo pipefail
mode="${1:-scheduled}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
GOOSE_CONFIG="$XDG_CONFIG_HOME/goose"
MYCROFT_PROFILE_DIR="$GOOSE_CONFIG/mycroft"
MYCROFT_DATA_DIR="$XDG_DATA_HOME/goose/mycroft"
MYCROFT_SOURCE_DIR="$MYCROFT_DATA_DIR/source"
MYCROFT_PLUGINS_DIR="$MYCROFT_DATA_DIR/plugins"
log_dir="$MYCROFT_DATA_DIR/logs"
mkdir -p "$log_dir"
log="$log_dir/update.log"
exec >>"$log" 2>&1
echo ""
date
echo "mode: $mode"

repo_rev() {
  local dir="$1"
  [ -d "$dir/.git" ] || return 0
  (cd "$dir" && git rev-parse HEAD)
}

rollback_repo() {
  local dir="$1" name="$2" rev="$3"
  [ -n "$rev" ] || return 0
  [ -d "$dir/.git" ] || return 0
  echo "Rolling back $name to $rev"
  (cd "$dir" && git reset --hard "$rev")
}

update_repo_ff_only() {
  local dir="$1" name="$2" branch="main"
  [ -d "$dir/.git" ] || return 0
  echo "== $name =="
  (
    cd "$dir"
    if ! git diff --quiet || ! git diff --cached --quiet; then
      echo "$name has local uncommitted changes; skipping automatic update."
      return 0
    fi
    before="$(git rev-parse HEAD)"
    git fetch origin "$branch"
    if git merge-base --is-ancestor HEAD "origin/$branch"; then
      git merge --ff-only "origin/$branch"
      after="$(git rev-parse HEAD)"
      echo "$name $before -> $after"
    else
      echo "$name has local commits or divergent history; skipping automatic update."
    fi
  )
}

refresh_profile() {
  mkdir -p "$MYCROFT_PROFILE_DIR"
  mkdir -p "$HOME/.local/bin"
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
  esac
  if [ -f "$MYCROFT_SOURCE_DIR/scripts/mycroft-fetch" ]; then
    chmod +x "$MYCROFT_SOURCE_DIR/scripts/mycroft-fetch" || true
    ln -sf "$MYCROFT_SOURCE_DIR/scripts/mycroft-fetch" "$HOME/.local/bin/mycroft-fetch"
  fi
  if [ -f "$MYCROFT_SOURCE_DIR/scripts/mycroft_safe.py" ]; then
    chmod +x "$MYCROFT_SOURCE_DIR/scripts/mycroft_safe.py" || true
    ln -sf "$MYCROFT_SOURCE_DIR/scripts/mycroft_safe.py" "$HOME/.local/bin/mycroft-safe"
  fi
  if [ -d "$MYCROFT_SOURCE_DIR/providers" ]; then
    mkdir -p "$GOOSE_CONFIG/custom_providers"
    for src in "$MYCROFT_SOURCE_DIR"/providers/*.json; do
      [ -f "$src" ] || continue
      name="$(basename "$src")"
      if [ -f "$GOOSE_CONFIG/custom_providers/$name" ]; then
        cp "$src" "$GOOSE_CONFIG/custom_providers/$name"
      fi
    done
  fi
  if [ -f "$MYCROFT_SOURCE_DIR/instructions/mycroft-soul.md" ]; then
    cp "$MYCROFT_SOURCE_DIR/instructions/mycroft-soul.md" "$MYCROFT_PROFILE_DIR/SOUL.md"
  fi
  MYCROFT_DIR="$MYCROFT_SOURCE_DIR"
  MYCROFT_CONFIG="$MYCROFT_PROFILE_DIR/mycroft-config.json"
  MYCROFT_GENERATED_RECIPES="$MYCROFT_PROFILE_DIR/generated-recipes"
  GOOSE_RECIPE_PATH="$MYCROFT_SOURCE_DIR/recipes:$MYCROFT_GENERATED_RECIPES"
  export MYCROFT_PROFILE_DIR MYCROFT_DATA_DIR MYCROFT_SOURCE_DIR MYCROFT_DIR MYCROFT_CONFIG MYCROFT_GENERATED_RECIPES GOOSE_RECIPE_PATH
  if [ -f "$MYCROFT_PROFILE_DIR/.env" ]; then
    set -a
    . "$MYCROFT_PROFILE_DIR/.env"
    set +a
  fi
  if [ -f "$MYCROFT_SOURCE_DIR/instructions/journalism.md" ]; then
    cat "$MYCROFT_SOURCE_DIR/instructions/journalism.md" > "$MYCROFT_PROFILE_DIR/goose-mycroft.md"
    cat >> "$MYCROFT_PROFILE_DIR/goose-mycroft.md" <<PROFILE_EOF

## Mycroft Installed Context

- Mycroft Goose profile: $MYCROFT_PROFILE_DIR
- Mycroft source: $MYCROFT_SOURCE_DIR
- Mycroft plugins: $MYCROFT_PLUGINS_DIR
- Mycroft durable knowledge vault: ${MYCROFT_VAULT_PATH:-}
- Mycroft recipes: $MYCROFT_SOURCE_DIR/recipes:$MYCROFT_PROFILE_DIR/generated-recipes
- Mycroft persistent soul file: $MYCROFT_PROFILE_DIR/SOUL.md

Use Mycroft for durable knowledge, source records, wiki notes, story pitches, drafts, and published story packaging.
Use QMD for local markdown search before broad web search when the answer may already be in the Mycroft or Spotlight vault.

## Getting Started Route

When the user is new after install, asks how to start, or the vault contains only scaffold/example files, do not stop at "nothing found." Explain that Mycroft needs reporting context or source material, then offer:

1. Set up my beat.
2. Add to my knowledge base.
3. Create my morning brief.
4. Investigate a lead.
5. Set up scouts.
6. Show me a demo.

Prefer "Add to my knowledge base" when the user has links, files, newsletters, pasted notes, PDFs, or folders. Offer vault cleanup or an audit only when the user says they already have an existing note collection.

Use $MYCROFT_SOURCE_DIR/recipes/start.yaml as the broad first-run recipe. Use $MYCROFT_SOURCE_DIR/recipes/morning-brief-preflight.yaml only when the user specifically chooses the morning brief path.
PROFILE_EOF
    if [ -n "${SPOTLIGHT_DIR:-}" ] || [ -d "$MYCROFT_PLUGINS_DIR/spotlight" ]; then
      SPOTLIGHT_DIR="${SPOTLIGHT_DIR:-$MYCROFT_PLUGINS_DIR/spotlight}"
      cat >> "$MYCROFT_PROFILE_DIR/goose-mycroft.md" <<PROFILE_SPOTLIGHT_EOF

## Spotlight Installed Context

- Spotlight repo: $SPOTLIGHT_DIR
- Spotlight vault: ${SPOTLIGHT_VAULT_PATH:-}
- Spotlight cases root: ${SPOTLIGHT_VAULT_PATH:-}/cases
- Spotlight ingest skill: $SPOTLIGHT_DIR/skills/ingest/SKILL.md
- Spotlight AGENTS runtime contract: $SPOTLIGHT_DIR/AGENTS.md
- Mycroft ingest target for Spotlight findings: ${SPOTLIGHT_INGEST_TARGET:-}

Use Spotlight for active OSINT casework, evidence trails, captures, and case briefs.
Use the Spotlight ingest skill to promote confirmed findings into the Mycroft vault.
For adversarial fact-checking, active case evidence trails, document/image-heavy OSINT, or an independent fact-checker loop, load:

- $SPOTLIGHT_DIR/AGENTS.md
- $SPOTLIGHT_DIR/agents/fact-checker.md
- $SPOTLIGHT_DIR/skills/spotlight/SKILL.md

Keep Spotlight's fact-checker independent from investigator reasoning. It should verify structured findings and write verdicts with evidence_for and evidence_against trails.
PROFILE_SPOTLIGHT_EOF
    fi
    if [ -n "${SCOUTPOST_API_KEY:-}" ] || [ "${SPOTLIGHT_MONITORING_BACKEND:-}" = "scoutpost" ]; then
      cat >> "$MYCROFT_PROFILE_DIR/goose-mycroft.md" <<'PROFILE_SCOUTPOST_EOF'

## Scoutpost Installed Context

Scoutpost is enabled. Use the installed Scoutpost skill from the Mycroft skill registry.
Prefer MCP if configured, then the scout CLI if installed, then the hosted API with SCOUTPOST_API_KEY and SCOUTPOST_API_BASE.
Never print the API key.
PROFILE_SCOUTPOST_EOF
    fi
    cp "$MYCROFT_PROFILE_DIR/goose-mycroft.md" "$GOOSE_CONFIG/.goosehints"
  fi
}

mycroft_before="$(repo_rev "$MYCROFT_SOURCE_DIR" || true)"
spotlight_before="$(repo_rev "$MYCROFT_PLUGINS_DIR/spotlight" || true)"

update_repo_ff_only "$MYCROFT_SOURCE_DIR" "Mycroft source" || true
update_repo_ff_only "$MYCROFT_PLUGINS_DIR/spotlight" "Spotlight" || true
refresh_profile

if [ -x "$HOME/.local/bin/mycroft-doctor" ]; then
  if "$HOME/.local/bin/mycroft-doctor"; then
    echo "doctor passed"
  else
    echo "doctor failed after update; rolling back app checkouts"
    rollback_repo "$MYCROFT_SOURCE_DIR" "Mycroft source" "$mycroft_before"
    rollback_repo "$MYCROFT_PLUGINS_DIR/spotlight" "Spotlight" "$spotlight_before"
    refresh_profile
    exit 1
  fi
fi

echo "update complete"
UPDATE_EOF
chmod +x "$HOME/.local/bin/mycroft-update"

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
  printf 'export PATH="$HOME/.local/bin:$PATH"\n'
  printf 'export MYCROFT_DIR="%s"\n' "$MYCROFT_DIR"
  printf 'export MYCROFT_PROFILE_DIR="%s"\n' "$MYCROFT_PROFILE_DIR"
  printf 'export MYCROFT_DATA_DIR="%s"\n' "$MYCROFT_DATA_DIR"
  printf 'export MYCROFT_CONFIG="%s"\n' "$MYCROFT_CONFIG"
  printf 'export GOOSE_RECIPE_PATH="%s"\n' "$GOOSE_RECIPE_PATH_VALUE"
  printf '[ -f "%s" ] && set -a && . "%s" && set +a\n' "$MYCROFT_ENV" "$MYCROFT_ENV"
  printf 'mycroft() {\n'
  printf '  case "${1:-}" in\n'
  printf '    update) "$HOME/.local/bin/mycroft-update" ;;\n'
  printf '    doctor) "$HOME/.local/bin/mycroft-doctor" ;;\n'
  printf '    *) goose recipe list ;;\n'
  printf '  esac\n'
  printf '}\n'
  printf '%s\n' "$MARKER_END"
} >> "$tmp_rc"
mv "$tmp_rc" "$SHELL_RC"

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
