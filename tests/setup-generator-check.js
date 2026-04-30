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
  cojournalist: true,
  fireworksKey: "fw-test",
  togetherKey: "",
  firecrawlKey: "fc-test",
  apifyToken: "",
  agentmailKey: "",
  cojournalistKey: "coj-test",
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
assertIncludes(script, 'cp "$MYCROFT_DIR/instructions/journalism.md" "$GOOSE_CONFIG/.goosehints"');
assertIncludes(script, "brew install --cask block-goose");
assertIncludes(script, "curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh");
assertIncludes(script, "git pull --no-rebase --autostash origin main");
assertIncludes(script, "com.buriedsignals.mycroft.update.plist");
assertIncludes(script, "mycroft-update.timer");
assertIncludes(script, "mycroft-setup");
assertIncludes(script, "Move this .command/.sh file");
assertIncludes(script, "COJOURNALIST_API_KEY='coj-test'");
assertIncludes(script, "SPOTLIGHT_MONITORING_BACKEND=cojournalist");
assertIncludes(script, "SPOTLIGHT_SCOUT_REQUESTS=cojournalist");
assertIncludes(script, '"mycroft": "$VAULT_PATH"');
assertIncludes(script, '"spotlight": "$SPOTLIGHT_VAULT_PATH"');
assertIncludes(script, '"local_model": "qwen9b"');
assertExcludes(script, "cojournalist_mode");
assertExcludes(script, "self-host");

const localScript = context.buildScript({
  ...base,
  sovereignty: "local",
  localOnly: true,
  localModel: "qwen35b",
  fireworks: false,
  cojournalist: false,
  cojournalistKey: "",
  spotlightVaultPath: "~/Documents/Mycroft",
});
syntax = spawnSync("bash", ["-n"], { input: localScript, encoding: "utf8" });
if (syntax.status !== 0) {
  console.error(syntax.stderr);
  process.exit(syntax.status || 1);
}
assertIncludes(localScript, "GOOSE_PROVIDER=local-llama-server");
assertIncludes(localScript, "GOOSE_MODEL=qwen3.5-35b-abliterated-journalist");
assertIncludes(localScript, 'SPOTLIGHT_VAULT_PATH="$VAULT_PATH/Spotlight"');
assertExcludes(localScript, "COJOURNALIST_API_KEY=");
assertExcludes(localScript, "SPOTLIGHT_MONITORING_BACKEND=cojournalist");

const zip = context.buildZipEntries([
  { filename: "one.txt", contents: "one\n", executable: false },
  { filename: "two.sh", contents: "#!/bin/sh\n", executable: true },
]);
if (!(zip instanceof Uint8Array) || zip[0] !== 0x50 || zip[1] !== 0x4b) {
  console.error("ZIP builder did not produce a ZIP payload.");
  process.exit(1);
}

const manifest = context.buildAgentManifest(base);
if (manifest.env.required.includes("coj-test") || JSON.stringify(manifest).includes("fw-test")) {
  console.error("Agent manifest leaked a secret value.");
  process.exit(1);
}
if (!context.buildAgentPrompt(manifest).includes("mycroft doctor")) {
  console.error("Agent prompt missing verification command.");
  process.exit(1);
}

console.log("setup generator: OK");
