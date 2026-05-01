---
name: qmd
description: Search the Mycroft and Spotlight markdown vaults with QMD before using broader web search.
---

# QMD

Use QMD for local markdown search across the journalist's vaults.

## Configuration

Setup installs the QMD CLI:

```sh
npm install -g @tobilu/qmd
```

Setup also registers collections:

```sh
qmd collection add "$MYCROFT_VAULT_PATH" --name mycroft
qmd collection add "$SPOTLIGHT_VAULT_PATH" --name spotlight
qmd update
```

QMD can expose an MCP server with:

```sh
qmd mcp
```

## Search Order

Before broad web search, use local QMD search when the answer may already be in the user's notes, sources, story drafts, or Spotlight casework.

Useful commands:

```sh
qmd query "question"
qmd search "keywords"
qmd query --collection mycroft "source handling policy"
qmd query --collection spotlight "case evidence for <entity>"
qmd get "#docid"
qmd multi-get "wiki/entities/*.md" -l 40
```

## Spotlight

Spotlight's `query-vault` verb is backed by:

```sh
BUN_INSTALL="" qmd query
```

If Spotlight is enabled, QMD must be available for local vault search and sensitive local-only research phases.

## Safety

- Prefer local QMD search over web search for source-sensitive material.
- Do not index private vaults outside the paths selected during setup unless the user asks.
- Do not print secrets from `~/.config/goose/mycroft/.env` or Goose's secret store.
