---
name: fact-check
description: Fact-check drafts, claims, and source assertions through Mycroft's SIFT recipe, escalating to Spotlight for deeper adversarial review when available. Investigation-grade: emits the full grounding object per the grounding-provenance spec.
requires: [epistemic-grounding, shell-safety]
---

# Fact Check

Use this skill when the user asks to fact-check, verify claims, inspect citations, or stress-test a draft.

Load this skill before answering fact-checking requests. Do not rely on general chat behavior for verification work.

**Always load these skills before starting work:**
- `epistemic-grounding` — the 5-tier ladder, confidence caps, failure router. Mycroft fact-check is investigation-grade and must emit the full `grounding` object on every claim.
- `shell-safety` — every `mycroft-fetch`, `curl`, and verification command must use safe patterns. Validate URLs, slugs, and paths via `scripts/mycroft_safe.py` before passing to shell.

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

1. Extract discrete factual claims: names, dates, numbers, events, quotes, attributions, locations, causal claims, and cited-source assertions. Break each claim into material elements (actor, action, object, time, place, amount, relationship, status) per the `epistemic-grounding` skill.
2. Check prior local context first with QMD against the Mycroft and Spotlight collections when installed.
3. Apply SIFT before corroboration: stop, investigate the source, find better coverage, and trace claims to original context.
4. Acquire evidence via `mycroft-fetch` (preferred) or firecrawl through the shell-safety pattern. Every acquisition produces an evidence item — `mycroft-fetch` records the URL, acquisition method, accessed_at, sha256 of saved bytes, content_type, access_method, and the missing-source gate. See `docs/grounding-provenance-spec.md` for the schema.
5. Seek both supporting and contradicting evidence. Do not stop at the first source that agrees.
6. Prefer primary sources over secondary reporting. Record when access is only abstract, archive, excerpt, or inaccessible — these cap confidence at `low` per the cap table.
7. Separate evidence from inference and mark uncertainty formally via the `grounding` object below.

## Required Output Contract

Every fact-check claim must emit:

```json
{
  "claim_id": "claim-001",
  "claim_text": "specific factual statement",
  "verdict": "verified|partially_verified|unverified|contradicted|mischaracterized",
  "grounding": {
    "support_type": "direct|indirect|inferred|contradicted|insufficient",
    "grounding_strength": "full|partial|weak|none",
    "source_role": "primary|secondary|contextual",
    "quote_match": "exact|paraphrase|contextual|none",
    "claim_elements_checked": ["actor", "action", "date", "amount"],
    "missing_assumptions": [],
    "contradiction_search": "what was searched and found",
    "confidence_cap": "high|medium|low",
    "misgrounding_risk": "short risk statement",
    "assessment": "why this evidence does or does not ground the claim"
  },
  "evidence_refs": ["E1", "E2"],
  "human_review": "pending|approved|rejected"
}
```

The validator (`tools/validate-grounding.py`) must reject any claim whose stated confidence exceeds its `confidence_cap`, or whose `evidence_refs` do not resolve to evidence items in `data/evidence-bundle.json`.

## Verdict Rules

Use the closed SIFT verdict set:

- verified
- partially_verified
- unverified
- contradicted
- mischaracterized

Every verdict needs at least one `evidence_refs` entry or a clear `assessment` explaining why the claim could not be verified. `unverified` is a legitimate finding — do not conflate it with `contradicted` (per SOUL.md).

For Spotlight casework, preserve Spotlight's verdict taxonomy when writing `cases/{project}/data/fact-check.json`:

- verified
- unverified
- disputed
- false

Add a `grounding_assessment` field on Spotlight handoffs so the Spotlight fact-checker can independently audit how the Mycroft verifier grounded each claim.

## Safety

- Do not rewrite the user's draft unless asked.
- Do not fabricate sources.
- Keep confidential source identities out of cloud tools unless the user explicitly approves.
- Separate evidence from inference.
