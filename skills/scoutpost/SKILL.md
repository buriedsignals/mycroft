---
name: scoutpost
description: Hosted Scoutpost API integration for scouts, monitoring requests, and beat signals.
---

# Scoutpost

Use this skill when Scoutpost was enabled in Mycroft setup.

## Configuration

Read:

- `SCOUTPOST_API_KEY` from Goose's secret store or fallback `~/.config/goose/mycroft/.env`
- `SCOUTPOST_API_BASE`, default `https://www.scoutpost.ai/api/v1`

The product skill source is:

```text
https://scoutpost.ai/skills/scoutpost.md
```

If the installed skill differs from the hosted product skill, prefer the hosted product skill when available.

## Capability Order

1. Use a Goose-compatible Scoutpost MCP server if it is installed and configured.
2. Use a `scout` CLI if present.
3. Use the hosted API directly with the configured API key.

If none are available, explain what is missing and offer to configure it.

## Use Cases

- Create scout requests from Spotlight monitoring recommendations.
- Query hosted beat-monitoring output.
- Turn recurring watch questions into Scoutpost scouts.
- Feed relevant scout results into Mycroft via `obsidian-ingest`.

## Safety

- Never print the API key.
- Do not send confidential source identities unless the user explicitly approves.
- Store durable scout findings in Mycroft, not Spotlight, unless they are part of an active case.
