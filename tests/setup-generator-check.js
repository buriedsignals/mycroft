#!/usr/bin/env node
const fs = require("fs");
const { spawnSync } = require("child_process");
const vm = require("vm");

const html = fs.readFileSync("setup.html", "utf8");
const match = html.match(/function shq\(s\)[\s\S]*?\nfunction refreshPreview\(\)/);
if (!match) {
  console.error("Could not extract setup generator helpers.");
  process.exit(1);
}

const source = match[0].replace(/\nfunction refreshPreview\(\)$/, "");
const context = { TextEncoder, Uint8Array, Uint32Array, DataView, Date };
vm.createContext(context);
vm.runInContext(source + "\nthis.buildScript = buildScript; this.buildZipEntries = buildZipEntries; this.buildAgentManifest = buildAgentManifest; this.buildAgentPrompt = buildAgentPrompt;", context);

const base = {
  sovereignty: "cloud",
  localOnly: false,
  vault: "~/Documents/Mycroft",
  installGoose: true,
  installObsidian: true,
  installFirecrawl: true,
  fireworks: true,
  together: false,
  localModel: "qwen9b",
  spotlight: true,
  scoutpost: true,
  fireworksKey: "fw-test",
  togetherKey: "",
  firecrawlKey: "fc-test",
  apifyToken: "",
  agentmailKey: "",
  scoutpostKey: "scout-test",
  spotlightVaultPath: "~/Documents/Spotlight",
  osintNavigatorKey: "ont-test",
  spotBrowseruse: true,
  acledKey: "",
  acledEmail: "",
  junkipediaKey: "jk-test",
};

function assertIncludes(script, needle) {
  if (!script.includes(needle)) {
    console.error(`Missing expected fragment: ${needle}`);
    process.exit(1);
  }
}

function assertExcludes(script, needle) {
  if (script.includes(needle)) {
    console.error(`Unexpected fragment present: ${needle}`);
    process.exit(1);
  }
}

const script = context.buildScript(base);
let syntax = spawnSync("bash", ["-n"], { input: script, encoding: "utf8" });
if (syntax.status !== 0) {
  console.error(syntax.stderr);
  process.exit(syntax.status || 1);
}
assertIncludes(script, 'GOOSE_CONFIG="$XDG_CONFIG_HOME/goose"');
assertIncludes(script, 'PROVIDERS_DST="$GOOSE_CONFIG/custom_providers"');
assertIncludes(script, 'write_goose_instructions');
assertIncludes(script, 'MYCROFT_PROFILE_DIR="$GOOSE_CONFIG/mycroft"');
assertIncludes(script, 'MYCROFT_DATA_DIR="$XDG_DATA_HOME/goose/mycroft"');
assertIncludes(script, 'MYCROFT_DIR="$MYCROFT_DATA_DIR/source"');
assertIncludes(script, 'MYCROFT_DIR="$MYCROFT_SOURCE_DIR"');
assertIncludes(script, 'ln -sf "$MYCROFT_DIR/scripts/mycroft-fetch" "$HOME/.local/bin/mycroft-fetch"');
assertIncludes(script, 'ln -sf "$MYCROFT_SOURCE_DIR/scripts/mycroft-fetch" "$HOME/.local/bin/mycroft-fetch"');
assertIncludes(script, 'command -v mycroft-fetch');
assertIncludes(script, 'ln -sf "$MYCROFT_DIR/scripts/mycroft_safe.py" "$HOME/.local/bin/mycroft-safe"');
assertIncludes(script, 'ln -sf "$MYCROFT_SOURCE_DIR/scripts/mycroft_safe.py" "$HOME/.local/bin/mycroft-safe"');
assertIncludes(script, 'command -v mycroft-safe');
assertIncludes(script, 'export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"');
assertIncludes(script, '"shell-safety skill"');
assertIncludes(script, '"epistemic-grounding skill"');
assertIncludes(script, 'MYCROFT_SKILL_REGISTRY="$MYCROFT_PROFILE_DIR/skill-registry.json"');
assertIncludes(script, 'SPOTLIGHT_INGEST_TARGET="$VAULT_PATH"');
assertIncludes(script, 'mkdir -p "$MYCROFT_PROFILE_SKILLS_DIR/scoutpost"');
assertIncludes(script, 'MYCROFT_GENERATED_RECIPES="$MYCROFT_PROFILE_DIR/generated-recipes"');
assertIncludes(script, 'MYCROFT_MORNING_BRIEF_CONFIG="$MYCROFT_PROFILE_DIR/morning-brief-config.md"');
assertIncludes(script, 'GOOSE_MOIM_MESSAGE_FILE="$MYCROFT_PROFILE_DIR/SOUL.md"');
assertIncludes(script, 'GOOSE_RECIPE_PATH="$MYCROFT_DIR/recipes:$MYCROFT_GENERATED_RECIPES"');
assertIncludes(script, "## Fact-Checking Route");
assertIncludes(script, "$MYCROFT_SKILLS_DIR/fact-check/SKILL.md");
assertIncludes(script, "$SPOTLIGHT_DIR/agents/fact-checker.md");
assertIncludes(script, "configure_goose_persistent_defaults");
assertIncludes(script, "set_goose_config_key GOOSE_PROVIDER");
assertIncludes(script, "goose configure set-secret");
assertIncludes(script, "npm install -g @tobilu/qmd");
assertIncludes(script, 'qmd collection add "$VAULT_PATH" --name mycroft');
assertIncludes(script, 'goose schedule add --schedule-id mycroft-morning-brief');
assertIncludes(script, 'goose schedule add --schedule-id mycroft-vault-audit');
assertIncludes(script, 'recipes/start.yaml');
assertIncludes(script, 'morning-brief-preflight.yaml');
assertIncludes(script, 'START_HERE.md');
assertIncludes(script, "brew install --cask block-goose");
assertIncludes(script, "curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh");
assertIncludes(script, 'git fetch origin "$branch"');
assertIncludes(script, 'git merge --ff-only "origin/$branch"');
assertIncludes(script, 'update_repo_ff_only "$MYCROFT_SOURCE_DIR" "Mycroft source"');
assertIncludes(script, "export MYCROFT_PROFILE_DIR MYCROFT_DATA_DIR MYCROFT_SOURCE_DIR MYCROFT_DIR MYCROFT_CONFIG MYCROFT_GENERATED_RECIPES GOOSE_RECIPE_PATH");
assertIncludes(script, "PROFILE_SPOTLIGHT_EOF");
assertIncludes(script, "PROFILE_SCOUTPOST_EOF");
assertIncludes(script, "doctor failed after update; rolling back app checkouts");
assertIncludes(script, 'cp "$MYCROFT_PROFILE_DIR/goose-mycroft.md" "$GOOSE_CONFIG/.goosehints"');
assertIncludes(script, "mycroft-update.timer");
assertIncludes(script, "removed old Mycroft LaunchAgent");
assertIncludes(script, "weekly updater cron");
assertIncludes(script, "15 10 * * 1");
assertIncludes(script, "OnCalendar=Mon *-*-* 10:15:00");
assertIncludes(script, "mycroft-setup");
assertIncludes(script, "Run this .command/.sh file from any folder");
assertIncludes(script, "Privacy & Security -> Open Anyway");
assertIncludes(script, "SCOUTPOST_API_KEY='scout-test'");
assertIncludes(script, "SPOTLIGHT_MONITORING_BACKEND=scoutpost");
assertIncludes(script, "SPOTLIGHT_SCOUT_REQUESTS=scoutpost");
assertIncludes(script, "Spotlight ingest skill");
assertIncludes(script, "open_goose_start");
assertIncludes(script, '"mycroft": "$VAULT_PATH"');
assertIncludes(script, '"spotlight": "$SPOTLIGHT_VAULT_PATH"');
assertIncludes(script, '"local_model": "qwen9b"');
assertExcludes(script, "scoutpost_mode");
assertExcludes(script, "self-host");

const localScript = context.buildScript({
  ...base,
  sovereignty: "local",
  localOnly: true,
  localModel: "qwen27b",
  fireworks: false,
  scoutpost: false,
  scoutpostKey: "",
  spotlightVaultPath: "~/Documents/Mycroft",
});
syntax = spawnSync("bash", ["-n"], { input: localScript, encoding: "utf8" });
if (syntax.status !== 0) {
  console.error(syntax.stderr);
  process.exit(syntax.status || 1);
}
assertIncludes(localScript, "GOOSE_PROVIDER=local");
assertIncludes(localScript, "GOOSE_MODEL=tomvaillant/qwen3.6-27b-abliterated-journalist-GGUF:Q4_K_M");
assertIncludes(localScript, "MYCROFT_LOCAL_MODEL_REPO=tomvaillant/qwen3.6-27b-abliterated-journalist-GGUF");
assertIncludes(localScript, "MYCROFT_LOCAL_MODEL_FILE=qwen3.6-27b-abliterated-journalist-Q4_K_M.gguf");
assertIncludes(localScript, "MYCROFT_LOCAL_MODEL_QUANT=Q4_K_M");
assertIncludes(localScript, "install_local_model");
assertIncludes(localScript, "register_local_model_in_goose");
assertIncludes(localScript, "$XDG_DATA_HOME/goose/models");
assertIncludes(localScript, "sed 's/\\\\/\\\\\\\\/g; s/\"/\\\\\"/g'");
assertExcludes(localScript, "GOOSE_PROVIDER=local-llama-server");
// providers should be *removed* by the new installer, not *copied* — assert no cp of the JSONs
assertExcludes(localScript, 'cp "$MYCROFT_DIR/providers/local-llama-server.json"');
assertExcludes(localScript, 'cp "$MYCROFT_DIR/providers/local-mlx.json"');
assertIncludes(localScript, 'SPOTLIGHT_VAULT_PATH="$VAULT_PATH/Spotlight"');
assertIncludes(localScript, 'SPOTLIGHT_INGEST_TARGET="$VAULT_PATH"');
assertExcludes(localScript, "SCOUTPOST_API_KEY=");
assertExcludes(localScript, "SPOTLIGHT_MONITORING_BACKEND=scoutpost");

const zip = context.buildZipEntries([
  { filename: "one.txt", contents: "one\n", executable: false },
  { filename: "two.sh", contents: "#!/bin/sh\n", executable: true },
]);
if (!(zip instanceof Uint8Array) || zip[0] !== 0x50 || zip[1] !== 0x4b) {
  console.error("ZIP builder did not produce a ZIP payload.");
  process.exit(1);
}

const manifest = context.buildAgentManifest(base);
if (manifest.env.values.FIREWORKS_API_KEY !== "fw-test" || manifest.env.values.SCOUTPOST_API_KEY !== "scout-test") {
  console.error("Agent manifest missing local secret values.");
  process.exit(1);
}
if (manifest.env.defaults.GOOSE_PROVIDER !== "fireworks-qwen36plus" || manifest.env.defaults.SPOTLIGHT_SCOUT_REQUESTS !== "scoutpost") {
  console.error("Agent manifest missing env defaults.");
  process.exit(1);
}
if (!manifest.source_repo || !manifest.installer.providers.includes("fireworks-qwen36plus")) {
  console.error("Agent manifest missing setup instructions.");
  process.exit(1);
}
if (!manifest.vault_scaffold.mycroft_notes.includes("START_HERE.md") || !manifest.vault_scaffold.mycroft_notes.includes("_schema/mycroft.md") || !manifest.vault_scaffold.mycroft_notes.includes("stories/pitches/example-story-pitch.md") || !manifest.vault_scaffold.spotlight_notes.includes("cases/_template/index.md")) {
  console.error("Agent manifest missing vault scaffold instructions.");
  process.exit(1);
}
if (!manifest.skills.skills.some((s) => s.id === "spotlight-ingest") || !manifest.skills.skills.some((s) => s.id === "copywriting") || !manifest.skills.skills.some((s) => s.id === "fact-check") || !manifest.skills.skills.some((s) => s.id === "qmd") || !manifest.skills.skills.some((s) => s.id === "mycroft-maintenance")) {
  console.error("Agent manifest missing skill registry entries.");
  process.exit(1);
}
if (!manifest.goose.schedules.some((s) => s.id === "mycroft-morning-brief") || !manifest.goose.schedules.some((s) => s.id === "mycroft-vault-audit")) {
  console.error("Agent manifest missing Goose schedules.");
  process.exit(1);
}
const agentPrompt = context.buildAgentPrompt(manifest);
if (!agentPrompt.includes("## Setup") || !agentPrompt.includes("Handle the setup for the user") || !agentPrompt.includes("env.defaults") || !agentPrompt.includes("env.values")) {
  console.error("Agent prompt missing setup instructions.");
  process.exit(1);
}
if (!agentPrompt.includes("Create the Obsidian vault scaffold") || !agentPrompt.includes("Open Obsidian") || !agentPrompt.includes("skill registry")) {
  console.error("Agent prompt missing vault scaffold/open instructions.");
  process.exit(1);
}
if (!agentPrompt.includes("Register Goose-native schedules") || !agentPrompt.includes("morning-brief-preflight")) {
  console.error("Agent prompt missing schedule/preflight instructions.");
  process.exit(1);
}
if (!agentPrompt.includes("recipes/start.yaml") || !agentPrompt.includes("START_HERE.md") || !agentPrompt.includes("choose a first action")) {
  console.error("Agent prompt missing first-run start instructions.");
  process.exit(1);
}
if (!agentPrompt.includes("GOOSE_MOIM_MESSAGE_FILE") || !agentPrompt.includes("Tell The User Next")) {
  console.error("Agent prompt missing soul/next-step instructions.");
  process.exit(1);
}
if (!agentPrompt.includes("GOOSE_PROVIDER") || !agentPrompt.includes("goose configure set-secret")) {
  console.error("Agent prompt missing persistent Goose provider setup.");
  process.exit(1);
}
if (!agentPrompt.includes("mycroft-update") || !agentPrompt.includes("Do not use Goose schedules for repo updates")) {
  console.error("Agent prompt missing deterministic updater instructions.");
  process.exit(1);
}
if (agentPrompt.includes("fw-test") || agentPrompt.includes("scout-test")) {
  console.error("Agent prompt printed secret values.");
  process.exit(1);
}
if (!agentPrompt.includes("mycroft doctor")) {
  console.error("Agent prompt missing verification command.");
  process.exit(1);
}

console.log("setup generator: OK");
