# Schedules

## Morning brief

These recipes require an Engine build that supports `bsig brief`. Publishing or
updating Mycroft alone does not install that Engine build. If the command is not
recognized, setup stops with an update-required message; the new background
workflow is unavailable until a compatible Engine release is installed.

Ask Mycroft in Goose: “Help me set up my morning brief.” Setup collects the beat,
watchlist, specific sources and their collection/disclosure permissions, days,
local start time, IANA timezone, and destination. It has no default authority to
collect private mail, subscribe to newsletters, or send email.

Engine owns this one local background job. Goose and Indicator Labs may be
closed. The chosen time is the earliest start; Engine checks every five minutes,
so generation normally starts around that time, not at an exact minute.
The computer must be on and the user logged in; after sleep it catches
up on the latest eligible slot instead of sending a backlog. It cannot deliver
while the computer is powered off. Local provider services and protected
credentials must also be available in the background.

Every completed brief has a wiki copy and a named saved Goose conversation,
separate from the setup chat. Optional email uses AgentMail and the explicitly
confirmed destination. Native notifications are a convenience; denied or
unsupported notifications do not erase the saved result.

Use these typed controls from Mycroft or a terminal:

```sh
bsig brief status --json
bsig brief history --json
bsig brief open-result --json
bsig brief source-coverage RUN_ID --json
bsig brief pause --json
bsig brief resume --json
bsig brief remove --json
```

For a run with partial inputs, `source-coverage` returns a private `coverage_file`
with source outcomes. Mycroft reads that file to explain missing inputs; article
text and source labels are not printed into Engine's audit stream. Sources whose
disclosure was not approved retain opaque excluded-source labels.

`resume` requires verified settings and delivery. `remove` disables this job
and removes its exact owned notification helpers; it preserves the wiki,
Goose history, private run receipts and AgentMail inbox. Product uninstall also
preserves reporting data unless a separate data-removal choice is made.

Setup remains paused until a real background verification saves the first
result. Goose-only then activates under the original Enable approval; email
also needs the journalist's receipt confirmation. Inspect `recovery_action`
when verification fails. Public AI and subscription CLI providers are not
supported by the background generation path in this version.

## Existing Goose morning-brief schedules

New installs never create `mycroft-morning-brief` in Goose. The install option
`enable_schedules` now applies only to the separate `mycroft-vault-audit` job;
that job remains Goose-owned and is not migrated here.

Engine detects the exact old morning-brief ID or an install receipt for it.
An ID alone is not ownership proof: edited or foreign jobs are never deleted
automatically. Unreadable/malformed scheduler storage also blocks the new path.
Old installer-profile preferences are copied into a private inactive
`legacy-preferences.md` draft. The previous conversational default at
`~/.mycroft/morning-brief-config.md` is retained separately as
`legacy-conversation-preferences.md`. `bsig brief legacy-draft-show --json`
returns the available paths. Neither draft authorizes source access or email.

When status reports `legacy_handover_required`:

1. In Goose's existing schedule controls, pause the old morning-brief job,
   wait for any running invocation to finish, then delete that job. Preserve
   its recipe and editorial preferences. Do not touch the wiki-audit job.
2. On macOS, quit every Goose window and Goose CLI/background process, then
   run `bsig brief complete-legacy-handover --json` in Terminal. Engine checks
   the native process table twice around strict persisted schedule absence.
   A process-query error or any Goose process leaves the handover blocked.
3. Reopen Goose and resume setup. The new configuration remains paused and
   requires fresh background verification before activation.

Windows and Linux handover completion is unavailable until equivalent native
quiescence checks are validated. Keep the new path paused on those platforms.
Never clear Engine's handover record manually or recreate the old job as a
repair. Goose 1.50's CLI `schedule list` starts a scheduler and its `remove`
command cannot stop another resident scheduler; neither is a handover proof.
Engine therefore performs no automatic Goose deletion or rollback that could
silently re-enable a paused old schedule.

## Updates

Mycroft product updates refresh the owned Engine executable transactionally.
Normal Indicator Labs startup also calls the typed `brief refresh-runtime`
operation after app-only updates. It refreshes only an existing owned job,
refuses a running job, preserves configuration/history, and retries on the next
startup if busy. It never creates a first job or enables recurrence. This
protects the notification host path when Squirrel retires an old version
folder. A standalone Engine has no packaged Labs notification host; saved
Goose/wiki results remain available.

Native end-to-end acceptance of credentials, model execution, saved-session
opening, delivery, sleep and notification clicks is still required for each
release platform. Unit tests and cross-compilation are not that evidence.

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
