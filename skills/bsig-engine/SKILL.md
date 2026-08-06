---
name: bsig-engine
description: Safely inspect and operate the local Indicator Labs `bsig` Engine for Mycroft, Spotlight, Navigator, and Scoutpost. Use when the user asks to diagnose installation health, inspect authentication or stored-key status, prepare or apply an Engine-managed install/update/uninstall, verify the installed stack, or repair an Engine-managed product. Do not use for ordinary journalism or to edit Engine-owned files manually.
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
