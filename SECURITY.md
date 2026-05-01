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

- The setup page (`index.html`, `setup.html`) including the client-side bash generator
- Recipe YAML files and any executable paths they invoke
- Provider configuration JSONs
- The generated `mycroft-setup.command` installer
- Anything under `tools/`, `extensions/`, `scripts/`

Out-of-scope (report upstream):

- Goose itself — https://github.com/aaif-goose/goose/security
- Firecrawl, Apify, AgentMail, Fireworks, Together, OpenRouter — their own disclosure channels
- User-provided API keys handling on cloud provider sides

## Threat model summary

Mycroft's privacy posture:

- API keys are embedded client-side into the downloaded `.command` and agent setup manifest — they **never transit Buried Signals infrastructure**.
- Setup page is deployed static; no backend receives form data.
- Recipes call user-provided cloud APIs directly; prompts are not proxied through us.
- Local-first mode routes LLM inference to the user's machine; zero network egress for that component.

We treat as security-relevant: any path that could cause API keys, vault contents, or source identities to leak beyond the user's machine or the cloud providers they explicitly configured.
