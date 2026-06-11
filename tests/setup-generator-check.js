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
vm.runInContext(source + "\nthis.buildScript = buildScript; this.buildZipEntries = buildZipEntries; this.buildGettingStarted = buildGettingStarted; this.buildInstallerReadme = buildInstallerReadme; this.validateForm = validateForm;", context);

const base = {
  sovereignty: "cloud",
  targetOs: "mac",
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

// Getting-started guide bundled into the installer ZIP
const guide = context.buildGettingStarted(base);
if (!guide.includes("<!doctype html>") || !guide.includes("Getting started")) {
  console.error("Getting-started guide is not an HTML page.");
  process.exit(1);
}
for (const needle of ["~/Documents/Mycroft", "~/Documents/Spotlight", "mycroft doctor", "START_HERE.md", "CLI: ON", "Spotlight", "Fireworks"]) {
  if (!guide.includes(needle)) {
    console.error(`Getting-started guide missing: ${needle}`);
    process.exit(1);
  }
}
for (const secret of ["fw-test", "fc-test", "scout-test", "ont-test", "jk-test"]) {
  if (guide.includes(secret)) {
    console.error("Getting-started guide leaked a secret value.");
    process.exit(1);
  }
}
const localGuide = context.buildGettingStarted({ ...base, sovereignty: "local", localOnly: true, spotlight: false, scoutpost: false });
if (!localGuide.includes("Local-first") || localGuide.includes("Spotlight vault")) {
  console.error("Getting-started guide does not adapt to local/no-spotlight installs.");
  process.exit(1);
}

// The installer opens the bundled guide and keeps a copy in the profile
assertIncludes(script, 'GETTING_STARTED_SRC="$SETUP_BUNDLE_DIR/GETTING-STARTED.html"');
assertIncludes(script, 'GETTING_STARTED="$MYCROFT_PROFILE_DIR/getting-started.html"');
assertIncludes(script, 'open "$GETTING_STARTED"');

// README adapts run instructions to the selected OS
const macReadme = context.buildInstallerReadme(base);
if (!macReadme.includes("Double-click") || !macReadme.includes("GETTING-STARTED.html") || macReadme.includes("agent setup")) {
  console.error("macOS README is wrong.");
  process.exit(1);
}
const linuxReadme = context.buildInstallerReadme({ ...base, targetOs: "linux" });
if (!linuxReadme.includes("bash mycroft-setup.command") || linuxReadme.includes("Privacy & Security")) {
  console.error("Linux README is wrong.");
  process.exit(1);
}
const winReadme = context.buildInstallerReadme({ ...base, targetOs: "windows" });
if (!winReadme.includes("WSL2") || !winReadme.includes("bash mycroft-setup.command")) {
  console.error("Windows README is wrong.");
  process.exit(1);
}

// Hard validation: complete form passes, missing required fields block
if (context.validateForm(base).length !== 0) {
  console.error("validateForm rejected a complete form.");
  process.exit(1);
}
const checks = [
  [{ ...base, firecrawlKey: "" }, "firecrawl_key"],
  [{ ...base, fireworksKey: "" }, "fireworks_key"],
  [{ ...base, fireworks: false, together: false }, "fireworks_key"],
  [{ ...base, scoutpostKey: "" }, "scoutpost_api_key"],
  [{ ...base, vault: " " }, "vault_path"],
  [{ ...base, spotlightVaultPath: "" }, "spotlight_vault_path"],
];
for (const [form, field] of checks) {
  const errs = context.validateForm(form);
  if (!errs.some((e) => e.field === field)) {
    console.error(`validateForm missed required field: ${field}`);
    process.exit(1);
  }
}
if (context.validateForm({ ...base, sovereignty: "local", localOnly: true, fireworksKey: "", togetherKey: "" }).length !== 0) {
  console.error("validateForm requires provider keys in local-only mode.");
  process.exit(1);
}
if (context.validateForm({ ...base, scoutpost: false, scoutpostKey: "" }).length !== 0) {
  console.error("validateForm requires Scoutpost key with the plugin disabled.");
  process.exit(1);
}

console.log("setup generator: OK");
