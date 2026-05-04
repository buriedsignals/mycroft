# First Run

The installer is designed to leave the user in Goose, ready to choose a first reporting action.

After setup:

1. Obsidian opens the Mycroft vault.
2. If Spotlight is enabled, Obsidian also opens the Spotlight vault.
3. Goose opens the `start` recipe unless the user already has a morning brief monitoring profile.
4. The Mycroft vault contains `START_HERE.md` with copy-paste starter prompts.

The `start` recipe offers:

- Set up my beat
- Add to my knowledge base
- Create my morning brief
- Investigate a lead
- Set up scouts
- Show me a demo

The "Add to my knowledge base" path is the best default when the vault is empty and the journalist has links, files, newsletters, pasted notes, PDFs, or folders. Vault cleanup and audits are later workflows for existing note collections.

## What To Do Next

Start chatting with Mycroft in Goose and pick one first action. If you know your beat, start there. If you already have material, add it to the knowledge base. If you want daily monitoring, choose the morning brief path.

Then create a folder for investigations in the Spotlight vault and ask Mycroft to Spotlight it. Spotlight is the active casework space; Mycroft is the durable knowledge and publishing space.

## Morning Brief Preflight

The morning brief path runs the `morning-brief-preflight` questions:

- beats
- watchlists
- priority sources
- ignored sources
- time window
- story triggers
- Spotlight handoff triggers
- sensitivity rules

It writes the answers locally. Fallback script secrets stay in `~/.config/goose/mycroft/.env`; provider secrets should be stored through Goose. The monitoring profile should not contain API keys.

From CLI, launch the broad first-run menu:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/start.yaml --interactive \
  --params vault_path="$HOME/Documents/Mycroft" \
  --params vault_name="Mycroft" \
  --params morning_brief_config_path="$HOME/.config/goose/mycroft/morning-brief-config.md"
```

## Re-running Preflight

From Goose, run the `morning-brief-preflight` recipe again when beats or monitoring priorities change.

From CLI:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/morning-brief-preflight.yaml --interactive \
  --params vault_path="$HOME/Documents/Mycroft" \
  --params vault_name="Mycroft" \
  --params config_path="$HOME/.config/goose/mycroft/morning-brief-config.md"
```
