# Schedules

Mycroft uses two scheduling layers.

## Goose Recipe Schedules

Goose owns scheduled AI work. The installer creates generated recipe files with the user's selected vault paths:

- `~/.config/goose/mycroft/generated-recipes/morning-brief.scheduled.yaml`
- `~/.config/goose/mycroft/generated-recipes/wiki-audit.scheduled.yaml`

Then it asks Goose to schedule them:

```sh
goose schedule add --schedule-id mycroft-morning-brief --cron "0 0 7 * * *" --recipe-source ~/.config/goose/mycroft/generated-recipes/morning-brief.scheduled.yaml
goose schedule add --schedule-id mycroft-wiki-audit --cron "0 15 18 * * *" --recipe-source ~/.config/goose/mycroft/generated-recipes/wiki-audit.scheduled.yaml
```

Goose stores and runs these schedules. Use Goose Desktop's Scheduler page or the CLI to inspect them:

```sh
goose schedule list
goose schedule run-now --schedule-id mycroft-morning-brief
goose schedule run-now --schedule-id mycroft-wiki-audit
```

## Morning Brief Preflight

The first setup run opens the broader `start` recipe if `~/.config/goose/mycroft/morning-brief-config.md` does not exist. If the user chooses "Create my morning brief," that flow continues into `morning-brief-preflight`.

The preflight recipe asks what the brief should monitor and writes:

- `~/.config/goose/mycroft/morning-brief-config.md`
- `<Mycroft wiki>/context/morning-brief.md`

The scheduled morning brief reads those files before ranking overnight items.

## Repo Updater

Managed Mycroft updates are automated by Indicator Labs
(`https://buriedsignals.com/join`). Open-source installations use the signed
Engine path and `bsig plan update mycroft`; neither path uses a weekly public-installer job.

A leftover `~/.local/bin/mycroft-update` wrapper only fast-forwards a private
Splash-enabled git checkout. Without that marker it fails closed and points at
Indicator Labs. Desktop users with a private checkout can still trigger it from
Goose with the `update-mycroft` recipe:

```sh
~/.local/bin/mycroft-update --manual
```

The private updater fetches `origin main` and fast-forwards only:

- `~/.local/share/goose/mycroft/source`
- Spotlight is not updated by Mycroft; when installed, use `spotlight update`.

Source recipes and skills are loaded directly from the checkout, so recipe and skill changes apply after the update. After source updates, the updater refreshes `~/.config/goose/mycroft/SOUL.md`, regenerates `~/.config/goose/.goosehints` from the updated source instructions plus local install paths, refreshes provider JSON files that are already installed under Goose, and runs `mycroft doctor`.

If a checkout is dirty or divergent, the updater skips it. If `mycroft doctor` fails after an update, the updater rolls app checkouts back to their pre-update commits. It does not update Goose itself.
