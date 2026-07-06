---
name: fact-check
description: Fact-check drafts, claims, and source assertions through Mycroft's SIFT recipe, escalating to Spotlight for deeper adversarial review when available. Uses the fact-check profile of epistemic-grounding — emits the full grounding object per the spec.
requires: [epistemic-grounding, shell-safety]
---

# Fact Check

Use this skill when the user asks to fact-check, verify claims, inspect citations, or stress-test a draft.

Load this skill before answering fact-checking requests. Do not rely on general chat behavior for verification work.

**Always load these skills before starting work:**
- `epistemic-grounding` — the 5-tier ladder, confidence caps, failure router, claim-decomposition discipline. This skill uses the `fact-check` profile and must emit the full `grounding` object on every claim.
- `shell-safety` — every `mycroft-fetch`, `curl`, and verification command must use safe patterns. Validate URLs, slugs, and paths via `scripts/mycroft_safe.py` before passing to shell.

## Default Path

Use the Mycroft recipe first. The default fact-check path attempts provenance
capture and unsigned manifest generation for every run, but it does not require
Noosphere/C2PA signing.

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/fact-check.yaml --params draft_path="<path>"
```

If the user provides short pasted text instead of a file:

```sh
goose run --recipe ~/.local/share/goose/mycroft/source/recipes/fact-check.yaml --params draft_text="<text>"
```

For newsroom workflows where provenance must be complete before delivery, pass
`strict_provenance=true`. To request live Noosphere/C2PA signing, pass
`c2pa_sign=true`; signing remains opt-in and fact-check verdicts remain
editorial outputs, not C2PA truth claims.

## Spotlight Escalation

If Spotlight is installed and the request needs adversarial review, evidence grounding, document/image-heavy OSINT, or a case trail, load the Spotlight runtime contract and fact-checking path:

- `~/.local/share/goose/mycroft/plugins/spotlight/AGENTS.md`
- `~/.local/share/goose/mycroft/plugins/spotlight/agents/fact-checker.md`
- `~/.local/share/goose/mycroft/plugins/spotlight/skills/spotlight/SKILL.md`
- `~/.local/share/goose/mycroft/plugins/spotlight/skills/ingest/SKILL.md`
- Spotlight vault path from `~/.config/goose/mycroft/mycroft-config.json`

Use Spotlight for deeper casework. Keep the fact-checker independent from the investigator's reasoning: verify structured findings and evidence, not the narrative that produced them. Promote durable findings back into Mycroft through the Spotlight ingest path and preserve links to evidence.

## Method

Apply the `epistemic-grounding` skill (claim decomposition, support classification, confidence caps, failure router) to every claim. This skill adds three fact-check-specific moves:

1. **Local context first.** Check Mycroft and Spotlight QMD collections before any web fetch — surface what's already known, link to it, don't re-verify.
2. **SIFT acquisition.** Stop, investigate the source, find better coverage, trace to origin. Acquire evidence via `mycroft-fetch` first. Every acquisition should produce an evidence item: `mycroft-fetch` records URL, acquisition method, accessed_at, sha256 of saved bytes, content_type, access_method, and the missing-source gate. If provenance tooling is unavailable, continue the fact-check only as a cited editorial review output and report `provenance incomplete` unless `strict_provenance=true`. See `docs/grounding-provenance-spec.md`.
3. **Verdict mapping.** Translate the grounding analysis to the closed verdict set (below) and emit the output contract.

### Suspect media triage

For images, video, or audio whose authenticity is in question, triage before escalating:

1. **Provenance first.** Check Content Credentials at `contentcredentials.org/verify` (C2PA manifest: signer, capture device, edit history, AI involvement). A valid manifest from a known signer is strong positive provenance — but signing keys get compromised (Nikon Z6 III, 2025), so treat it as evidence, not proof. Absence of a manifest proves nothing: most legitimate media is unsigned, and screenshots or platform re-encoding strip manifests.
2. **Two detectors minimum.** A single-tool verdict is not evidence. Run at least two (Reality Defender has a free tier; AI or Not for fast triage; Hive for volume). TrueMedia.org shut down January 2025 — do not cite it. Detector agreement caps the claim at `medium` confidence; disagreement means escalate, not average.
3. **Eye and ear are triage only.** Current diffusion-class output has eliminated the classic tells; voice cloning is past the indistinguishable threshold for casual listeners, so voice-only verification fails. Remaining leaks: boundary regions (hairlines, glasses edges), shadow physics, catchlight mismatches, phoneme-lip drift, uniform noise texture.
4. **Escalate.** Anything load-bearing goes to Spotlight for forensic casework and source contact. Record each detector run as an evidence item (tool, date, verdict).

This consumes C2PA manifests on incoming media. It is independent of the sift-c2pa signing pipeline, which signs Mycroft's own outputs.

## Required Output Contract

Every fact-check claim must emit:

```json
{
  "claim_id": "claim-001",
  "claim_text": "specific factual statement",
  "verdict": "verified|partially_verified|unverified|contradicted|mischaracterized",
  "grounding": {
    "support_type": "direct|indirect|inferred|contradicted|insufficient",
    "source_role": "primary|secondary|contextual",
    "claim_elements_checked": ["actor", "action", "date", "amount"],
    "missing_assumptions": [],
    "confidence_cap": "high|medium|low",
    "misgrounding_risk": "short risk statement",
    "assessment": "why this evidence does or does not ground the claim; include the contradiction-search outcome here"
  },
  "evidence_refs": ["E1", "E2"],
  "human_review": "unreviewed|approved|rejected"
}
```

Evidence items in `data/evidence-bundle.json` may use `linked_evidence_ids: [...]` to chain related acquisitions (SERP→scrape, scrape+screenshot, scrape+web-archive). See `docs/grounding-provenance-spec.md` § Search evidence model.

The validator (`tools/validate-grounding.py`) must reject any claim whose stated confidence exceeds its `confidence_cap`, or whose `evidence_refs` do not resolve to evidence items in `data/evidence-bundle.json`. Publication-ready outputs (`publication_ready: true`) additionally require every referenced claim to be `human_review: approved`.

**Right of response.** A claim that rates a named person or organization `contradicted` or `mischaracterized` is not `publication_ready` until the subject has been offered a chance to respond — state the exact claim, give a reasonable deadline (24-48h is a common newsroom norm; deadlines and legal obligations vary by jurisdiction and outlet) — and the response or non-response is logged as an evidence item. This is an editorial gate for the human reviewer, not a validator check.

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

## Corrections

When an error surfaces in an already-delivered fact-check or published draft:

| Situation | Action |
|---|---|
| Factual error | Correct immediately; append a dated correction note |
| Missing context | Add context; formal correction optional |
| New information | Update; mark "Updated: [date]" |
| Subject disputes characterization | Re-run the claim through the recipe; correct only if the re-check warrants it |

Re-emit the corrected claim object with the new verdict, reset `human_review` to `unreviewed`, and add the correction to the evidence bundle so the trail preserves both states. If the output was C2PA-signed, the correction is a new claim in the chain — never mutate a signed manifest.

Correction note format: "Correction [date]: an earlier version stated [error]. In fact, [correct information]."

## Safety

- Do not rewrite the user's draft unless asked.
- Do not fabricate sources.
- Keep confidential source identities out of cloud tools unless the user explicitly approves.
- Separate evidence from inference.

---

*Suspect-media triage, right-of-response gate, and corrections protocol adapted (one-off, 2026-07-06) from Joe Amditis's `source-verification` and `fact-check-workflow` skills (jamditis/claude-skills-journalism, MIT).*
