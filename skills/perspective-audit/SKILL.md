---
name: perspective-audit
description: Trace observed viewpoints from source material through stance summaries and publication drafts, producing an editor-inspectable perspective ledger with evidence links, coverage gaps, framing findings, and reviewable rewrite suggestions. Use for editorial viewpoint-diversity reviews, representation audits, framing checks, source-to-draft lineage, social-discussion analysis, or requests to show which perspectives were found, omitted, compressed, merged, or over-weighted. Do not use as a substitute for factual verification or to invent opposing views.
---

# Perspective audit

Treat viewpoint diversity as inspectable data. Produce a perspective ledger that preserves this lineage:

`source passage -> perspective -> summary sentence -> draft sentence`

Keep factual verification separate. Load `epistemic-grounding` before auditing. Load `shell-safety` before any shell operation involving supplied paths or source content. Load `fact-check` only when the user also asks whether claims are true.

Read [references/audit-contract.md](references/audit-contract.md) before producing a structured audit.

## Bound the audit

1. Identify the editorial question and the exact corpus in scope.
2. Assign or preserve stable evidence IDs for every source passage used.
3. Record exclusions, inaccessible material, duplicate handling, and sampling decisions.
4. State that corpus frequency is not population prevalence. Set perspective `representativeness` to `corpus_only` or `unknown`.
5. Keep confidential source material local unless the journalist explicitly approves another provider posture.

If the user supplies URLs rather than captured material, use Mycroft's `web-acquisition` path and `mycroft-fetch` so evidence receives stable IDs and local artifacts. Do not acquire unrelated sources merely to manufacture balance.

## Extract observed perspectives

Extract positions actually expressed in the corpus. A perspective may contain a claim, value, priority, proposed action, uncertainty, or lived experience.

- Require at least one `evidence_ref` for every perspective.
- Preserve qualifications and material disagreement within a cluster.
- Use descriptive labels rather than `Agree` and `Disagree` unless the source question is genuinely binary.
- Separate perspective identity from speaker identity: one source may express several perspectives and several sources may share one.
- Record harmful or extreme viewpoints without presenting them as endorsements.
- Put plausible but unobserved viewpoints under `reporting_gaps`; never present them as extracted perspectives.

Do not infer importance from repetition alone. Coordinated posting, duplicate text, platform demographics, moderation, and collection choices can distort counts.

## Summarize with lineage

Create a concise summary for each perspective. Give every summary sentence its own ID, `perspective_refs`, and `evidence_refs`.

When merging perspectives:

- preserve meaningful disagreement;
- identify common ground only when the evidence supports it;
- record omitted evidence;
- avoid false equivalence between unequally supported claims;
- retain attribution, uncertainty, and scope.

Never add historical context, background, or factual assertions unless separately sourced.

## Map an optional draft

Split the draft into stable sentence units. Map each sentence to the summaries, perspectives, and evidence it carries. Leave reference arrays empty when no support can be established and flag the sentence as `unsupported_assertion`.

Use the lineage graph to identify:

- omitted perspectives;
- disproportionate prominence;
- incompatible positions collapsed into one;
- attribution drift;
- certainty inflation;
- loaded or stereotyping language;
- fringe claims granted false equivalence;
- factual disagreements presented as matters of opinion.

Treat classifier labels and probabilities as model signals, not editorial verdicts.

## Suggest revisions

Offer `suggested_rewrites`, not "neutral versions." For each suggestion:

1. Name the exact problem being addressed.
2. Preserve factual content, attribution, and uncertainty.
3. State whether the claim meaning changed.
4. Show the proposal separately from the draft.
5. Leave `human_review` as `unreviewed` until an editor acts.

Never replace text automatically. Neutrality is contextual and may erase warranted clarity or create false balance.

## Deliver the audit

Return a short editor-facing report containing:

1. corpus boundary and limitations;
2. perspective ledger;
3. coverage and lineage table;
4. sentence-level findings;
5. reporting gaps;
6. reviewable rewrite suggestions.

When structured files are requested, emit `perspective-audit.json` conforming to `schemas/perspective-audit.schema.json` and a rendered `perspective-audit.md`. Reuse IDs from an existing `evidence-bundle.json` when present.

Resolve every supplied input and output path against the journalist-approved base directory before reading or writing it. Pass resolved paths to tools as argv; never interpolate supplied paths or source text into shell command strings.

Validate JSON before delivery:

```sh
python3 skills/perspective-audit/scripts/validate_perspective_audit.py perspective-audit.json
```

When an evidence bundle is available:

```sh
python3 skills/perspective-audit/scripts/validate_perspective_audit.py \
  perspective-audit.json --evidence-bundle data/evidence-bundle.json
```

Report validation failures rather than silently repairing evidence links.

## Editorial boundaries

- Do not call a viewpoint representative of a population from a bounded discussion corpus.
- Do not equate viewpoint diversity with factual accuracy.
- Do not create an opposing view solely to make a story appear balanced.
- Do not convert a factual contradiction into two equally valid perspectives.
- Do not expose protected source identities in the ledger.
- Do not write the ledger into durable knowledge without the journalist's approval and the `knowledge-workspace` write contract.

This workflow adapts the inspectable perspective-to-draft pattern described in AutoJourn while requiring source-grounded extraction rather than generated opinions: https://arxiv.org/html/2607.18983v1
