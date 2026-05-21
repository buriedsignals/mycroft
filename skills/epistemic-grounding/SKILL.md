---
name: epistemic-grounding
description: Claim-to-evidence grounding discipline for Mycroft skills and recipes. Use when extracting findings, assigning confidence tags, fact-checking claims, ingesting vault notes, or deciding whether a piece of source material is a lead, a partially grounded claim, or a verifiable finding.
version: "1.0"
invocable_by: [recipe, skill, user]
---

# Epistemic Grounding

Use this skill whenever Mycroft turns source material into a claim or evaluates whether a claim is ready to file, brief, or publish.

The core question is:

> Does this exact evidence justify believing this exact claim?

A source is only an anchor. Grounding is the relationship between the claim and the anchor.

## Two Profiles

Mycroft uses this skill at two intensities:

- **default** — used by `morning-brief`, `vault-qa`, `obsidian-ingest`, `source-monitor`, `content-creator`, casual fact-checks. Apply the ladder and confidence-cap rubric in your head; emit only the `confidence: high|medium|low` tag mandated by `SOUL.md` plus a `source::` line. No required schema.
- **fact-check** — used by `fact-check`, `fact-check-c2pa`, draft-verification work, anything destined for publication or editor review. Emit the full `grounding` object per the schema in `tools/mycroft/docs/grounding-provenance-spec.md` and the `tools/mycroft/schemas/sift-manifest.schema.json`. See the fact-check skill for the contract.

The ladder, confidence caps, and failure router below are universal — they apply at both intensities.

## Grounding Ladder

Classify each candidate claim on this ladder:

1. **Unsourced signal** — interesting, but no source anchor yet.
2. **Source-adjacent lead** — a source mentions the topic, but does not support the claim.
3. **Partially grounded claim** — evidence supports some claim elements, but missing assumptions remain.
4. **Directly grounded claim** — source text directly supports all material claim elements.
5. **Independently verified finding** — direct grounding plus independent corroboration and no unresolved contradiction.

Only levels 4-5 can be tagged `confidence: high`. Levels 1-2 are leads, not findings — tag `confidence: low, unsourced` if you must surface them. Level 3 is at most `confidence: medium` and often `low`.

## Required Grounding Check

For every claim you intend to write, brief, or publish:

1. Break the claim into material elements: actor, action, object, time, place, amount, relationship, status.
2. Identify the exact quote, table row, record, image frame, metadata field, or document passage that supports each element.
3. Classify the source role:
   - `primary` — original record, document, direct statement, data source, filing, archived page, or observable artifact.
   - `secondary` — reporting, analysis, database aggregation, third-party summary.
   - `contextual` — useful background, but not evidence for the claim.
4. Classify support type:
   - `direct` — evidence states the claim elements plainly.
   - `indirect` — evidence supports the claim through a short, explicit inference.
   - `inferred` — evidence requires unstated assumptions or synthesis across sources.
   - `contradicted` — reliable evidence conflicts with the claim.
   - `insufficient` — source does not support the claim.
5. Name missing assumptions and misgrounding risks.
6. Search for contradictions before raising confidence.
7. Apply the confidence cap.

## Confidence Caps

Use these caps even if the claim sounds plausible:

| Condition | Maximum Confidence |
|---|---|
| No scraped local file | low |
| Search snippet only | low |
| Source is contextual or adjacent | low |
| Evidence is inaccessible, abstract-only, or materially redacted | low |
| Claim requires unstated assumptions | medium |
| Only secondary sources support the claim | medium |
| Single primary source, no contradiction search yet | medium |
| Direct primary source plus independent corroboration | high |
| Credible unresolved contradiction | low or disputed |
| Output came from a local LLM hallucination-prone for URLs (e.g. fine-tuned Qwen) without firecrawl verification | low |

Never upgrade a claim beyond the weakest material element. If the amount is directly supported but the date is inferred, the whole claim is only partially grounded.

## Mycroft-specific notes

- **Local-model output is a lead, not authority.** Mycroft's default model (fine-tuned Qwen3.5-9B per `SOUL.md`) hallucinates URLs, citations, statute IDs, and database paths. Any such atom in a model response is `confidence: low, unsourced` until verified via `firecrawl scrape` or `qmd` lookup. The fine-tune teaches style and domain vocabulary, not citation accuracy.
- **`unverified` ≠ `false`** (from `SOUL.md`). Evidence-absent is not the same as evidence-contradicts. When grounding is missing, name the gap rather than rewrite the claim into something the evidence supports.
- **Apply this skill at ingestion time, not just at fact-check time.** A note filed to the vault with a `confidence: high` tag becomes a citation source for future answers. Inflated confidence at ingest is load-bearing for downstream errors.

## When to use the full grounding object

The `fact-check` profile output schema (7-field `grounding` block, `evidence_refs`, `human_review` state) is **required only** for the `fact-check` skill (`tools/mycroft/skills/fact-check/SKILL.md`) and the `fact-check-c2pa.yaml` recipe. See `tools/mycroft/docs/grounding-provenance-spec.md` for the schema and `tools/mycroft/schemas/sift-manifest.schema.json` for the validator.

`default`-profile skills do not emit the full object — they apply the ladder and caps in-head and emit the lighter `confidence:` tag plus a `source::` line in vault frontmatter. Promoting routine outputs to the full schema is over-engineering for daily synthesis work.

## Failure Routing

When a claim feels wrong, do not patch the wording first. Diagnose the grounding failure:

- Evidence mentions the topic but not the claim: source-adjacent lead.
- Evidence supports a weaker claim: narrow the claim.
- Evidence supports only some elements: mark partial and name missing assumptions.
- Evidence depends on OCR/layout extraction: verify against the original document or image.
- Evidence chains through another citation: trace to the origin.
- Evidence conflicts with another reliable source: mark disputed and preserve both trails.
- Evidence comes only from a fine-tuned local model: re-fetch via firecrawl before raising confidence.

Read `references/failure-router.md` for deeper failure classes. Read `references/grounding-theory.md` when designing or revising grounding policy.
