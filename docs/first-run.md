# First Run

The installer is designed to leave the user in Goose, ready to choose a first reporting action.
The default Mycroft workspace is `~/Documents/OpenKnowledge/Mycroft`; Spotlight remains a sibling workspace at `~/Documents/OpenKnowledge/Spotlight`.

After setup:

1. If Spotlight is already installed, Mycroft records its workspace and case paths so Goose can launch Spotlight or read cases read-only. Mycroft does not install Spotlight. Install Spotlight separately in Indicator Labs.
2. Goose opens the `start` recipe unless the user already has a morning brief monitoring profile.
3. The Mycroft knowledge project contains `START_HERE.md` with copy-paste starter prompts.

The `start` recipe offers:

- Set up my beat
- Add to my knowledge base
- Create my morning brief
- Investigate a lead
- Set up scouts
- Show me a demo

The "Add to my knowledge base" path is the best default when the wiki is empty and the journalist has links, files, newsletters, pasted notes, PDFs, or folders. Wiki cleanup and audits are later workflows for existing note collections.

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
- Spotlight launch triggers
- sensitivity rules

It writes the answers locally. Fallback script secrets stay in `~/.config/goose/mycroft/.env`; provider secrets should be stored through Goose. The monitoring profile should not contain API keys.

From CLI, launch the broad first-run menu:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/start.yaml --interactive \
  --params vault_path="$HOME/Documents/OpenKnowledge/Mycroft" \
  --params morning_brief_config_path="$HOME/.config/goose/mycroft/morning-brief-config.md"
```

## Re-running Preflight

From Goose, run the `morning-brief-preflight` recipe again when beats or monitoring priorities change.

From CLI:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/morning-brief-preflight.yaml --interactive \
  --params vault_path="$HOME/Documents/OpenKnowledge/Mycroft" \
  --params config_path="$HOME/.config/goose/mycroft/morning-brief-config.md"
```
