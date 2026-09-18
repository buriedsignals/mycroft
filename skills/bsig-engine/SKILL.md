---
name: bsig-engine
description: Safely inspect and operate the local Indicator Labs `bsig` Engine for Mycroft, Spotlight, Navigator, and Scoutpost. Use when the user asks to diagnose installation health, inspect authentication or stored-key status, prepare or apply an Engine-managed install/update/uninstall, verify the installed stack, or repair an Engine-managed product, or set up and control a morning brief and its selected newsletter handoffs. Do not use for ordinary journalism or to edit Engine-owned files manually.
---

# Indicator Engine

Use the installed `bsig` executable as the only control surface. Prefer read-only diagnosis, prepare
sealed plans before mutations, and keep protected values out of the conversation and command line.

## Invariants

- Run `bsig` directly. Do not recreate its behavior with shell scripts or edit its manifests,
  plans, Goose configuration, product checkouts, or credential stores by hand.
- Add `--json` to every agent-run command and parse stdout as NDJSON. Treat `data` as authoritative;
  `message` is for people. Unknown event types are diagnostics, not permission to guess state.
- Never use `--allow-file-secrets`, `sudo bsig`, or pass a secret in argv, chat, a plan, a file, or an
  environment variable.
- Never invoke `bsig run mycroft` from inside Mycroft; that recursively launches the current
  runtime. Run another product only when the user explicitly asks.
- A packaged Engine may refuse mutations when its signed release is unpublished, paused, revoked,
  or stale. Report that gate; never bypass or downgrade it.
- Exit `1` can accompany useful doctor/test findings. Exit `2` means rollback was incomplete,
  `3` means entitlement denied, and `4` means the command was malformed. Do not blindly retry.

## Diagnose first

1. Confirm the executable is available with `command -v bsig`. If absent, direct the user to
   Indicator Labs; do not download an unverified replacement.
2. Read Engine-owned lifecycle state:

   ```sh
   bsig products --json
   bsig doctor --product mycroft --json
   ```

   Use `--product spotlight` when that is the requested target. An unscoped `bsig doctor --json`
   is appropriate for a whole-machine diagnosis.
3. Summarize failing finding IDs, their details, and their emitted `repair_hint`. Do not infer a
   repair that conflicts with the hint.
4. Run `bsig test stack --json` only when the user asks for full functional verification or after
   an approved repair. It is broader and may exercise installed tools.

## Authentication and keys

- Inspect without hydrating secret values:

  ```sh
  bsig auth status --json
  bsig keys list --json
  bsig keys validate <KEY_ID> --json
  ```

- For login, ask for the account email, then run `bsig auth login <email> --json` and relay the
  emitted device-authorization instructions. Do not request or handle the resulting PAT.
- For a new provider key, tell the user to use Indicator Labs' protected key prompt or a private
  Terminal stdin flow such as `pbpaste | bsig keys set <KEY_ID> --json`. Never ask them to paste the
  value into chat, and never run a command containing the value.
- Require explicit confirmation before `bsig auth logout --json` or
  `bsig keys remove <KEY_ID> --json`; both remove authority.

## Change an Engine-managed product

1. Identify the exact product and requested operation. Supported products are `mycroft`,
   `spotlight`, `navigator`, and `scoutpost`.
2. Prepare only a sealed plan:

   ```sh
   bsig plan update mycroft --json
   bsig plan uninstall mycroft --json
   ```

   For a new install, collect every requested product choice first and pass only supported
   `--options`. Prefer Indicator Labs when choices are incomplete; do not invent provider, runtime,
   vault, data-removal, or integration choices.
3. From the final result event, present the exact `plan_path`, `body_sha256`, step summaries, and
   every `diff_preview`. A generated plan has made no system change.
4. Ask for explicit approval to apply that exact path and digest. Regenerate rather than editing a
   plan if the user changes a choice.
5. After approval, run `bsig apply <plan_path> --json`. Do not substitute another path. If an apply
   is already running, report the lock instead of racing it.
6. Re-run the scoped doctor and summarize the result.

Uninstall preserves data-bearing artifacts by default. Use
`--options remove_data_bearing=true` only after a separate, explicit confirmation that names the
data that will be removed. If rollback is partial, stop and surface the rollback failures.

## Repair boundaries

- Apply only a repair represented by a newly generated Engine plan or a documented `bsig` verb.
- Do not adopt foreign installations, delete retained vaults, rewrite provider files, change
  Keychain ACLs, or replace a pinned runtime unless the user explicitly requests the corresponding
  supported Engine workflow.
- If the finding has no supported Engine repair, explain the boundary and leave the machine
  unchanged.
- Finish with what was checked, what changed, the post-change doctor result, and any remaining
  manual action. Never claim success from command exit alone.

## Morning brief in Goose

Use this skill for “Help me set up my morning brief”, “Where is today's brief?”,
“Pause my brief” and changes to brief settings. Follow `recipes/morning-brief-preflight.yaml`
for setup and `recipes/newsletter-setup.yaml` for separately authorized newsletter handoffs.
There is no Morning brief management section in Indicator Labs.

- `bsig brief status --json` returns schedule, verification step, next eligible start,
  timezone, last run, last saved result and recovery_action. A next_run while paused
  is a proposed slot, not a promise of execution. Show per-stage and partial-source status.
- `bsig brief setup-draft --json` saves incomplete editorial choices from stdin
  without execution authority. `bsig brief setup-draft-show --json` returns its
  private draft_file for resuming an account/key handoff; status reports
  setup_draft_available. Use the recipe schema; never store keys or confirmation URLs.
- `bsig brief config --json` returns a private config_file. Read it to resume a new
  chat or make changes; never manually edit Engine state. `bsig brief plan --json`
  reads nonsecret configuration JSON on stdin and returns a private plan_file plus
  plan_id. Review that exact plan with the journalist. `bsig brief apply PLAN_ID --json`
  saves it paused and invalidates prior verification. Do not interpolate user text
  into executable shell; use structured stdin or a safely quoted nonsecret here-document.
- After one explicit Enable of the displayed plan, `bsig brief verify --enable --json`
  starts real OS-background verification. The journalist may close Goose. Goose-only
  activates automatically after verified saves; email waits for the journalist's
  receipt report. `bsig brief confirm-email received --json` activates it;
  `bsig brief confirm-email not-received --json` keeps it paused. Provider acceptance
  alone is not receipt. After repair, `bsig brief verify --json` resumes the authorized
  setup; an explicit pause or settings change needs fresh authorization.
- `bsig brief open-result --json` returns the latest saved Goose conversation link and
  wiki location. Check its date against today: if today's run failed, label an older
  result as older. No arbitrary active-chat injection. Notifications may be denied;
  the saved conversation and wiki are still available through this command.
- On explicit requests use `bsig brief run-now --json`, `bsig brief pause --json`,
  `bsig brief resume --json`, `bsig brief remove --json`, `bsig brief history --json`,
  or `bsig brief retry-delivery RUN_ID --json`. Run-now is bounded but can take up to
  20 minutes. Pause suppresses new sends, not already submitted mail. Remove preserves
  results and the AgentMail inbox; it does not unsubscribe publications.
- Status may require model, knowledge, source, mail or OS-background repair. Follow
  the returned action and scoped doctor findings; do not claim support for Public AI
  or subscription CLI providers, or bypass a failed background proof. If status reports
  legacy_handover_required, follow that recovery guidance before enabling anything.

For AgentMail, `bsig keys validate AGENTMAIL_API_KEY --json` checks the saved key without
reading it into chat. The existing Mycroft product's **Integrations → AgentMail inbox →
Enter API key…** control in Indicator Labs opens the protected OS prompt. **Get an API
key from AgentMail** points to `https://console.agentmail.to/dashboard/api-keys`; the
journalist can sign in/create an account there. Return to the saved setup afterward.
No new Labs UI is needed. Users without Labs can operate the private stdin key flow
in their own Terminal; the agent never handles the key.

With explicit inbox-creation authorization, `bsig brief inbox-create PROFILE --json`
returns a verified identity/address. For an existing inbox use
`bsig brief inbox-resolve INBOX_ID --json`. Show the returned address; never assume
`default` or infer an address from its ID. Newsletter collection is independent of
email delivery. Changing to Goose-only clears only delivery fields and preserves
editorial choices and individually approved newsletter sources.

`bsig brief newsletter-list --json` returns a private newsletters_file; read it to
resume publication-specific human handoffs. `bsig brief newsletter-record --json`
reads one evidence object on stdin and persists submitted, confirmation_pending,
active, human_action_required or failed status. It never performs a subscription,
follows a link or changes collection/disclosure consent. Only record observed or
explicitly user-reported evidence; form submission is not activation. Do not store
confirmation tokens. Use the newsletter recipe's exact schema and evidence kinds.
