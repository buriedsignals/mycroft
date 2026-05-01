# First Run

The installer is designed to leave the user in Goose, ready to configure the morning brief.

After setup:

1. Obsidian opens the Mycroft vault.
2. If Spotlight is enabled, Obsidian also opens the Spotlight vault.
3. Goose opens the `morning-brief-preflight` recipe unless a monitoring profile already exists.

The preflight recipe asks for:

- beats
- watchlists
- priority sources
- ignored sources
- time window
- story triggers
- Spotlight handoff triggers
- sensitivity rules

It writes the answers locally. Fallback script secrets stay in `~/.config/goose/mycroft/.env`; provider secrets should be stored through Goose. The monitoring profile should not contain API keys.

## What To Do Next

Start chatting with Mycroft in Goose to set up your morning brief.

Then create a folder for investigations in the Spotlight vault and ask Mycroft to Spotlight it. Spotlight is the active casework space; Mycroft is the durable knowledge and publishing space.

## Re-running Preflight

From Goose, run the `morning-brief-preflight` recipe again when beats or monitoring priorities change.

From CLI:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/morning-brief-preflight.yaml --interactive \
  --params vault_path="$HOME/Documents/Mycroft" \
  --params vault_name="Mycroft" \
  --params config_path="$HOME/.config/goose/mycroft/morning-brief-config.md"
```
