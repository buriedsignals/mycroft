# Troubleshooting

## macOS Says It Cannot Verify The Installer

Managed journalists install Mycroft through Indicator Labs
(`https://buriedsignals.com/join`). Open-source and agent-led users follow the
signed Engine path in the README. Neither path uses a ZIP or `curl | bash`.

## Mycroft Update Appears As A Login Item

Older generated installers created a LaunchAgent named `com.buriedsignals.mycroft.update`.

Unload and delete it in Finder, or from a terminal you already trust:

```text
~/Library/LaunchAgents/com.buriedsignals.mycroft.update.plist
```

Do not replace it with a weekly crontab. Indicator Labs automates managed
updates; open-source installations use `bsig plan update mycroft`. A leftover
`mycroft-update` wrapper only fast-forwards a private Splash-enabled git checkout.

## Goose Schedules Are Missing

Check Goose schedule support:

```sh
goose schedule list
```

If schedules are missing, add them manually:

```sh
goose schedule add --schedule-id mycroft-morning-brief --cron "0 0 7 * * *" --recipe-source ~/.config/goose/mycroft/generated-recipes/morning-brief.scheduled.yaml
goose schedule add --schedule-id mycroft-wiki-audit --cron "0 15 18 * * *" --recipe-source ~/.config/goose/mycroft/generated-recipes/wiki-audit.scheduled.yaml
```

## Morning Brief Has No Beat

Run the preflight recipe:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/morning-brief-preflight.yaml --interactive
```

It writes `~/.config/goose/mycroft/morning-brief-config.md`.

## Manual Desktop Update

Ask Goose to run the `update-mycroft` recipe. It uses the installed updater, fetches `origin main`, fast-forwards only, runs `mycroft doctor`, and reports the update log path.

## OpenKnowledge Is Missing

Rerun the Mycroft installer. It installs the catalog-pinned OpenKnowledge CLI,
and `mycroft doctor` treats a missing `ok` command as an incomplete install.

## Fact-check Needs Deeper Investigation

Start with Mycroft's SIFT recipe:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/fact-check.yaml --params draft_path="./draft.md"
```

If the work needs adversarial OSINT, evidence grounding, or case trails, use Spotlight and preserve findings back into Mycroft through the Spotlight ingest path.
