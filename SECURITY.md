# Security policy

Mycroft is built for journalists handling sensitive material. Security bugs matter.

## Reporting a vulnerability

**Do not open a public issue.** Report privately to:

- **Email:** buriedsignals@agentmail.com
- **Signal:** on request — email first for a secure number

Please include:

- A clear description of the issue and its impact
- Steps to reproduce, or a proof-of-concept
- Affected version / commit hash
- Your preferred credit attribution (or request anonymity)

## Response target

- **Acknowledgement:** within 72 hours
- **Triage + remediation plan:** within 7 days for high-severity, 14 days for medium
- **Fix + disclosure:** coordinated with the reporter; typical window 30-90 days depending on severity and scope

## Scope

In-scope:

- The landing page (`index.html`)
- Indicator Lab / Engine key collection for Mycroft secrets
- Skills, agent instructions, and the Osaurus bundle
- The pinned Analyst runtime and its wiki integration
- Install contract schemas, templates and signed catalogue handling

Out-of-scope (report upstream):

- Osaurus itself — https://github.com/osaurus-ai/osaurus/security
- Connected cloud providers and services — their own disclosure channels
- User-provided API keys handling on cloud provider sides

## Threat model summary

Mycroft's privacy posture:

- API keys are stored through Engine's operating-system credential broker. Managed users enter them through Indicator Lab's protected prompt; manual users use Engine's protected `bsig` stdin/keychain flow and enter values through a private operating-system or terminal prompt outside agent chat. Keys never belong in argv, shell history, repository files, a hosted page, or a localhost Mycroft form.
- Mycroft's model runs locally in Osaurus. Navigator and Scoutpost are hosted services; calls that send text to them require approval. Local inference does not mean that connected tools work offline.
- Watson is a separate cloud research path with no wiki access. The Analyst proposes wiki writes for confirmation rather than silently changing notes.

We treat as security-relevant: any path that could cause API keys, vault contents, or source identities to leak beyond the user's machine or the cloud providers they explicitly configured.
