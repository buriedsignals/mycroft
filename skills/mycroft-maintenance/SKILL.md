---
name: mycroft-maintenance
description: Maintain the Goose-installed Mycroft profile, source checkout, plugins, schedules, and doctor/update wrappers.
---

# Mycroft Maintenance

Use this skill when the user asks how Mycroft is installed, how Goose loads Mycroft, how updates work, or how to repair the local setup.

## Layout

Mycroft is a Goose profile, not a separate app.

- Goose config: `~/.config/goose`
- Mycroft Goose profile: `~/.config/goose/mycroft`
- Mycroft source checkout: `~/.local/share/goose/mycroft/source`
- Mycroft plugin checkouts: `~/.local/share/goose/mycroft/plugins`
- Mycroft vault: user-selected, usually `~/Documents/Mycroft`
- Spotlight vault: user-selected, usually `~/Documents/Spotlight`

## Update Path

Automatic updates are deterministic shell work, not agent reasoning. Setup installs a weekly system job; Goose Desktop can trigger the same path through the `update-mycroft` recipe.

Run:

```sh
mycroft update
```

This calls `~/.local/bin/mycroft-update`, which fetches `origin main` and fast-forwards only:

- `~/.local/share/goose/mycroft/source`
- `~/.local/share/goose/mycroft/plugins/spotlight`, when installed

Source recipes and skills are loaded directly from the checkout, so recipe and skill changes apply after the update. After source updates, the updater refreshes `~/.config/goose/mycroft/SOUL.md`, regenerates `~/.config/goose/.goosehints` from the source instructions plus local install paths, refreshes provider JSON files that are already installed under Goose, and runs `mycroft doctor`.

If a checkout is dirty or divergent, the updater skips it. If doctor fails after an update, the updater rolls app checkouts back to their pre-update commits.

## Doctor

Run:

```sh
mycroft doctor
```

The doctor checks:

- Goose config paths
- persisted Goose provider/model
- Mycroft profile files
- Mycroft source checkout
- selected skills
- generated scheduled recipes
- QMD CLI
- Spotlight plugin, when installed

## Rules

- Do not edit user vault notes during maintenance unless explicitly asked.
- Do not print secrets from `~/.config/goose/mycroft/.env` or Goose's secret store.
- Do not dirty the source checkout with generated config. Generated files belong in `~/.config/goose/mycroft`.
- Do not put new source-controlled skills in the profile directory. Add reusable skills to `~/.local/share/goose/mycroft/source/skills` via the Mycroft repo.
