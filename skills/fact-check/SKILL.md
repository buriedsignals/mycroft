---
name: fact-check
description: Fact-check drafts, claims, and source assertions through Mycroft's SIFT recipe, escalating to Spotlight for deeper adversarial review when available.
---

# Fact Check

Use this skill when the user asks to fact-check, verify claims, inspect citations, or stress-test a draft.

Load this skill before answering fact-checking requests. Do not rely on general chat behavior for verification work.

## Default Path

Use the Mycroft recipe first:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/fact-check.yaml --params draft_path="<path>"
```

If the user provides short pasted text instead of a file:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/fact-check.yaml --params draft_text="<text>"
```

## Spotlight Escalation

If Spotlight is installed and the request needs adversarial review, evidence grounding, document/image-heavy OSINT, or a case trail, load the Spotlight runtime contract and fact-checking path:

- `~/.local/share/goose/mycroft/plugins/spotlight/AGENTS.md`
- `~/.local/share/goose/mycroft/plugins/spotlight/agents/fact-checker.md`
- `~/.local/share/goose/mycroft/plugins/spotlight/skills/spotlight/SKILL.md`
- `~/.local/share/goose/mycroft/plugins/spotlight/skills/ingest/SKILL.md`
- Spotlight vault path from `~/.config/goose/mycroft/mycroft-config.json`

Use Spotlight for deeper casework. Keep the fact-checker independent from the investigator's reasoning: verify structured findings and evidence, not the narrative that produced them. Promote durable findings back into Mycroft through the Spotlight ingest path and preserve links to evidence.

## Method

1. Extract discrete factual claims: names, dates, numbers, events, quotes, attributions, locations, causal claims, and cited-source assertions.
2. Check prior local context first with QMD against the Mycroft and Spotlight collections when installed.
3. Apply SIFT before corroboration: stop, investigate the source, find better coverage, and trace claims to original context.
4. Seek both supporting and contradicting evidence. Do not stop at the first source that agrees.
5. Prefer primary sources over secondary reporting. Record when access is only abstract, archive, excerpt, or inaccessible.
6. Separate evidence from inference and mark uncertainty formally.

## Verdict Rules

Use the closed SIFT verdict set:

- verified
- partially verified
- unverified
- contradicted
- mischaracterized

Every verdict needs a citation or a clear note explaining why the claim could not be verified.

For Spotlight casework, preserve Spotlight's verdict taxonomy when writing `cases/{project}/data/fact-check.json`:

- verified
- unverified
- disputed
- false

## Safety

- Do not rewrite the user's draft unless asked.
- Do not fabricate sources.
- Keep confidential source identities out of cloud tools unless the user explicitly approves.
- Separate evidence from inference.
