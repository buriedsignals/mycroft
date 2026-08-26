# Troubleshooting

## macOS Says It Cannot Verify The Installer

This only happens with the ZIP path (`install.command`): right-click the file, choose **Open**, then **Open** again. The recommended `curl … | bash` command never triggers Gatekeeper.

Do not require journalists to run `xattr`, `chmod`, or other shell commands for normal installation.

## Mycroft Update Appears As A Login Item

Older generated installers created a LaunchAgent named `com.buriedsignals.mycroft.update`.

Rerun a current installer. It unloads and removes:

```text
~/Library/LaunchAgents/com.buriedsignals.mycroft.update.plist
```

Then it installs the Mycroft repo updater as a weekly user crontab entry instead.

You can also remove the old LaunchAgent manually from Finder by deleting:

```text
~/Library/LaunchAgents/com.buriedsignals.mycroft.update.plist
```

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
