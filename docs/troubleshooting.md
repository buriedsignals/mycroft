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

## Morning Brief Is Missing

Run `bsig brief status --json` and follow its `recovery_action`. Use
`bsig brief history --json` for save/delivery stages and
`bsig brief open-result --json` for the last saved Goose conversation and wiki
location. A proposed next slot while paused does not mean recurrence is active.

Do not repair this by creating a Goose morning-brief schedule. For
`legacy_handover_required`, follow [the supported handover](schedules.md#existing-goose-morning-brief-schedules).
For a changed beat or destination, ask Mycroft in Goose to change the morning
brief settings. Background verification resumes from durable checkpoints;
never regenerate an already saved digest just to retry email.

The separate wiki-audit schedule remains Goose-owned. Inspect it through Goose's
existing schedule controls; changing it does not repair morning-brief delivery.

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
