# Plugin Authoring

Mycroft plugins should be installable under:

```text
~/.local/share/goose/mycroft/plugins/<plugin-name>
```

A plugin should expose:

- a clear README or runtime contract
- optional `skills/*/SKILL.md` files
- any local config file it needs
- vault paths or handoff paths through `~/.config/goose/mycroft/mycroft-config.json`

Plugins should not assume the Mycroft vault and plugin vault are the same directory.

## Spotlight Pattern

Spotlight is the reference plugin shape:

- plugin repo: `~/.local/share/goose/mycroft/plugins/spotlight`
- casework vault: configured separately from the Mycroft vault
- handoff folder: `handoff-to-mycroft`
- durable ingest target: Mycroft vault

When a plugin creates durable knowledge, it should write a clean handoff and let a Mycroft ingest skill promote that material into `sources/`, `wiki/`, or `stories/`.
