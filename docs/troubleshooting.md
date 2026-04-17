# Troubleshooting

Common failure modes. If none fit, [open an issue](https://github.com/buriedsignals/mycroft/issues) (or email `buriedsignals@agentmail.com` if it touches keys / vault / sources).

## Install / setup

### `brew: command not found`

You don't have Homebrew. Install it first:
```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Then re-run your `mycroft-setup.command`.

### `npm: command not found`

Install Node.js:
```sh
brew install node
```
Then re-run the `.command`. This only matters if you asked the setup to install Firecrawl CLI via npm.

### `mycroft-setup.command` won't run — "unidentified developer"

macOS Gatekeeper is blocking an unsigned script. Two paths:
- **Right-click → Open** once; confirm in the dialog. After the first time, subsequent runs are permitted.
- Or from Terminal: `bash ~/Downloads/mycroft-setup.command` — Gatekeeper doesn't apply when you invoke bash explicitly.

### Script ran but `goose` isn't in my PATH

Open a **new terminal window**. The script appends to `~/.zshrc` (or `.bashrc`); existing terminals don't see the update until they reload. Or run `source ~/.zshrc`.

## Obsidian + recipes

### `morning-brief` / `vault-sync` fail silently — no note written

Obsidian Desktop must be **running** when the recipe fires. The Obsidian CLI (`obsidian`) talks to the live app over local IPC; if the app is closed, writes silently fail.

Also: open Obsidian → **Settings → General → Advanced → Command Line Interface** and toggle it **ON**. Obsidian 1.12+ ships the CLI but the toggle is off by default.

### `obsidian: command not found`

You need Obsidian 1.12 or newer. `brew install --cask obsidian` installs the latest. Verify: `obsidian --version`.

## Recipes

### Recipe uses Firecrawl but fails with 401 / no key

```sh
export FIRECRAWL_API_KEY=...
```
The setup script writes this to your shell rc if you entered a key. If you skipped it then: either re-run setup with the key, or edit `~/.zshrc` to add the export.

### Apify actor returns empty results

- Check `APIFY_API_TOKEN` is set (`echo $APIFY_API_TOKEN`).
- Some actors rate-limit aggressively (LinkedIn especially). Retry in 10-30 min.
- For Instagram comments specifically: verify the URL is a **post** URL (`/p/ABC/` or `/reel/ABC/`), not a profile URL.

### `ft-preflight` says "install claude or codex CLI"

`ft classify` needs an LLM CLI to generate proposed categories:
```sh
npm install -g @anthropic-ai/claude-code   # for claude
# or
npm install -g @openai/codex                # for codex
```

## Providers

### Goose doesn't list my provider

Provider JSONs go to `~/.config/goose/custom_providers/`. Check:
```sh
ls ~/.config/goose/custom_providers/
```
If your chosen provider's JSON isn't there, the setup likely didn't copy it. Re-run setup or copy manually from `~/.mycroft/providers/`.

### Together returns responses that smell logged

Enable Zero Data Retention in your Together dashboard — two toggles on the privacy page must be set to **No**. Together doesn't enforce ZDR by default; this is opt-in.

## Sovereign mode

### `sovereign on` doesn't change which model Goose uses

Check `echo $MYCROFT_LOCAL_ONLY`. If it's not `1`, the setup didn't record local-first preference. Re-run setup and pick **Local-first** in the Sovereignty preference block.

Also: your local server (`mlx_lm.server` or `llama-server`) must be running on the port the provider JSON expects (`:8081` for MLX, `:8080` for llama-server). Start it first.

### The Qwen fine-tune HF page returns 404

The 9B is at [`tomvaillant/qwen3.5-9b-abliterated-journalist-GGUF`](https://huggingface.co/tomvaillant/qwen3.5-9b-abliterated-journalist-GGUF). The 35B (`tomvaillant/qwen3.5-35b-abliterated-journalist-GGUF`) is training — 404 is expected until it ships. Use the 9B in the meantime, or point `local-llama-server.json` at any stock Qwen GGUF you already have.

### Which quantization to download?

- **Q4_K_M** — best size/quality balance for the 9B (~5-6 GB). Works on 16 GB unified memory.
- **Q5_K_M / Q6_K** — higher quality, more memory. For 24 GB+ systems.
- **Q8_0** — near-lossless, ~10 GB. For 32 GB+ systems.
- For the 35B: start with Q4_K_M (~20 GB). Needs 48-64 GB unified memory.

Use `hf download ... --include "*Q4_K_M.gguf"` to skip other quantizations during download.

## Deploy / hosted setup page

### OG preview image isn't showing

`assets/og/mycroft-og.svg` is SVG; some platforms (Slack, LinkedIn) don't render SVG OG images. For best compatibility, generate a PNG version (1200×630 px) and update `<meta property="og:image">` in `index.html`.

### CSP blocks Google Fonts

If you change the CSP meta tag and forget `fonts.googleapis.com` / `fonts.gstatic.com` in `style-src` / `font-src`, IM Fell won't load and the logo falls back to Georgia. Verify the meta tag in both `index.html` and `setup.html`.

## When all else fails

Post a redacted transcript to an issue. Strip any API keys, source names, or unpublished investigation content before pasting.
