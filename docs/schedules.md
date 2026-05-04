# Schedules

Mycroft uses two scheduling layers.

## Goose Recipe Schedules

Goose owns scheduled AI work. The installer creates generated recipe files with the user's selected vault paths:

- `~/.config/goose/mycroft/generated-recipes/morning-brief.scheduled.yaml`
- `~/.config/goose/mycroft/generated-recipes/vault-audit.scheduled.yaml`

Then it asks Goose to schedule them:

```sh
goose schedule add --schedule-id mycroft-morning-brief --cron "0 0 7 * * *" --recipe-source ~/.config/goose/mycroft/generated-recipes/morning-brief.scheduled.yaml
goose schedule add --schedule-id mycroft-vault-audit --cron "0 15 18 * * *" --recipe-source ~/.config/goose/mycroft/generated-recipes/vault-audit.scheduled.yaml
```

Goose stores and runs these schedules. Use Goose Desktop's Scheduler page or the CLI to inspect them:

```sh
goose schedule list
goose schedule run-now --schedule-id mycroft-morning-brief
goose schedule run-now --schedule-id mycroft-vault-audit
```

## Morning Brief Preflight

The first setup run opens the broader `start` recipe if `~/.config/goose/mycroft/morning-brief-config.md` does not exist. If the user chooses "Create my morning brief," that flow continues into `morning-brief-preflight`.

The preflight recipe asks what the brief should monitor and writes:

- `~/.config/goose/mycroft/morning-brief-config.md`
- `<Mycroft vault>/context/morning-brief.md`

The scheduled morning brief reads those files before ranking overnight items.

## Repo Updater

Mycroft repo updates are not Goose schedules. They are plain system jobs that run weekly:

```sh
~/.local/bin/mycroft-update
```

On macOS, setup uses a user crontab entry rather than a LaunchAgent/Login Item. Rerunning setup removes the old `com.buriedsignals.mycroft.update.plist` LaunchAgent if it exists.

Desktop users can trigger the same updater manually from Goose with the `update-mycroft` recipe. The recipe calls:

```sh
~/.local/bin/mycroft-update --manual
```

The updater fetches `origin main` and fast-forwards only:

- `~/.local/share/goose/mycroft/source`
- `~/.local/share/goose/mycroft/plugins/spotlight`

Source recipes and skills are loaded directly from the checkout, so recipe and skill changes apply after the update. After source updates, the updater refreshes `~/.config/goose/mycroft/SOUL.md`, regenerates `~/.config/goose/.goosehints` from the updated source instructions plus local install paths, refreshes provider JSON files that are already installed under Goose, and runs `mycroft doctor`.

If a checkout is dirty or divergent, the updater skips it. If `mycroft doctor` fails after an update, the updater rolls app checkouts back to their pre-update commits. It does not update Goose itself.
