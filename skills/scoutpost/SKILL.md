---
name: scoutpost
description: Scoutpost integration for scouts, monitoring, and beat signals via the scout CLI or REST API.
---

# Scoutpost

Use this skill when Scoutpost was enabled in Mycroft setup. Scoutpost is a monitoring platform for journalists: scheduled scouts watch pages, beats, social profiles, and councils, and extract source-linked information units.

## Surfaces (in order)

Mycroft talks to Scoutpost over **two** surfaces — never MCP:

1. **`scout` CLI** — if the `scout` binary is on `$PATH`, prefer it. Commands stay visible in the transcript. Its config lives at `~/.scoutpost/config.json`.
2. **REST API** — if `scout` is not installed (for example a host with no CLI build), call the hosted API directly.

If neither is available, explain what is missing and offer to configure it.

## Configuration

- **CLI:** `~/.scoutpost/config.json` (`api_url`, `supabase_anon_key`, `api_key`) is written by the installer. Run `scout` directly; never print the key.
- **REST:** read `SCOUTPOST_API_KEY` from Goose's secret store or the fallback `~/.config/goose/mycroft/.env`. Call `https://scoutpost.ai/functions/v1`. Send the key as `Authorization: Bearer cj_…` **and** the public anon key as the `apikey:` header — the Edge Functions front door rejects bare bearer tokens.

## Usage semantics

The canonical, product-maintained guide — scout types, verification policy, credit rules — is the hosted product skill:

```text
https://scoutpost.ai/skills/scoutpost.md
```

Read it for how to operate scouts correctly. This file governs only *which surfaces* Mycroft uses (CLI or REST — not MCP).

## Use Cases

- Create scout requests from Spotlight monitoring recommendations.
- Query hosted beat-monitoring output.
- Turn recurring watch questions into Scoutpost scouts.
- Feed relevant scout results through `knowledge-workspace` into logical space `mycroft`.

## Safety

- Never print the API key.
- Do not send confidential source identities unless the user explicitly approves.
- Confirm before creating or running anything that spends credits.
- Treat unverified units as leads, not publishable facts; always include source URLs when summarizing.
- Store durable scout findings in Mycroft, not Spotlight, unless they are part of an active case.
