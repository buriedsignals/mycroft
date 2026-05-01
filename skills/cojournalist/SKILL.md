---
name: cojournalist
description: Hosted coJournalist API integration for scouts, monitoring requests, and beat signals.
---

# coJournalist

Use this skill when coJournalist was enabled in Mycroft setup.

## Configuration

Read:

- `COJOURNALIST_API_KEY` from Goose's secret store or fallback `~/.config/goose/mycroft/.env`
- `COJOURNALIST_API_BASE`, default `https://www.cojournalist.ai/api/v1`

The product skill source is:

```text
https://cojournalist.ai/skills/cojournalist.md
```

If the installed skill differs from the hosted product skill, prefer the hosted product skill when available.

## Capability Order

1. Use a Goose-compatible coJournalist MCP server if it is installed and configured.
2. Use a `cojo` CLI if present.
3. Use the hosted API directly with the configured API key.

If none are available, explain what is missing and offer to configure it.

## Use Cases

- Create scout requests from Spotlight monitoring recommendations.
- Query hosted beat-monitoring output.
- Turn recurring watch questions into coJournalist scouts.
- Feed relevant scout results into Mycroft via `obsidian-ingest`.

## Safety

- Never print the API key.
- Do not send confidential source identities unless the user explicitly approves.
- Store durable scout findings in Mycroft, not Spotlight, unless they are part of an active case.
