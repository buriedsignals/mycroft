---
name: navigator
description: Route investigative research to Navigator when it needs OSINT tool discovery. Use for finding investigative tools and techniques for domains, usernames, images, maps, archives, networks, verification, geolocation, company intelligence, and country-specific research.
---

# Navigator

Navigator is a member service for OSINT tool discovery: it finds the right
investigative tool or technique.

Use the Navigator CLI first. It keeps authentication out of the agent
transcript. Do not construct direct upstream API calls. Navigator API calls
are a fallback only when the CLI is unavailable and the runtime has injected
an authenticated credential.

## When to Use Navigator

Use **OSINT tool discovery** for a technique or service you do not already
know: domains, usernames, images, maps, archives, networks, verification,
geolocation, company intelligence, or country-specific investigative tools.

Use ordinary web research for narrative reporting, current articles, source
pages, public records, and datasets. Navigator does not replace browser, search,
or archival work.

In a sensitive or offline investigation, do not contact Navigator unless the
operator explicitly authorizes network access. Record the skip and use local
research material or the available offline tool catalogue instead.

## Connection and Capability Checks

First check whether this installation is connected:

```bash
navigator auth status
```

If the command is unavailable or reports no verified connection, stop before
calling Navigator and tell the operator to reconnect: `bsig auth login` on an
Engine-managed install, otherwise `navigator auth login`. The base product and
this skill remain usable for discovery even while Navigator is locked.

The connection flow stores a revocable Navigator PAT in the OS keychain. Never
ask the user to paste that token into a prompt, file, argv, or command.

## CLI Workflow

```bash
navigator tools find "company registry Norway" --json
navigator tools show <tool-id> --json
```

Inspect the returned tool record before using it. Save the tool identifier,
retrieval time, and any documented limitations with the research plan.

## Evidence Rules

- Preserve tool IDs, search queries, timestamps, tool URLs, and documented
  limitations.
- Cite the underlying source URL when reporting a result. Navigator's response
  is a retrieval trail, not a substitute for verification.

## Recovery

- CLI unavailable: use permitted web or local research tools; use Navigator's
  authenticated API only where the runtime explicitly supports that fallback.
- Disconnected, expired, or revoked: ask the operator to run `bsig auth login`
  (Engine-managed install) or `navigator auth login`. Do not request a
  credential value.
