# Grounding And Provenance Spec

Status: v1 (2026-05-21)

This spec defines a Mycroft grounding and provenance layer for fact-checking,
source collection, and publication support. It adapts the stronger parts of the
Spotlight grounding/C2PA work while keeping Mycroft focused on durable newsroom
knowledge and draft verification.

Scope is deliberate: this spec applies to the **investigation-grade** profile
of the `epistemic-grounding` skill (the `fact-check` skill and the
`fact-check-c2pa.yaml` recipe). Routine Mycroft skills — `morning-brief`,
`vault-qa`, `obsidian-ingest`, `source-monitor`, `content-creator` — use the
**newsroom-light** profile: the ladder and confidence caps applied in-head plus
the lighter `confidence:` tag from `SOUL.md`. See
`skills/epistemic-grounding/SKILL.md` for the profile boundary.

## Goals

- Preserve how each source was acquired, stored, hashed, and used.
- Test whether exact evidence supports exact claims, not just whether a source
  exists.
- Keep unverified material clearly separated from editor-approved facts.
- Produce a portable provenance package that can be signed with C2PA/Noosphere.
- Make the review trail useful to journalists without implying that signatures
  certify truth.

## Non-Goals

- Do not sign every source fetch as an independent artifact.
- Do not treat C2PA as fact verification.
- Do not store signing credentials, bearer tokens, cookies, or private keys in
  the Mycroft vault.
- Do not make browser automation the default acquisition path. Use it only when
  static fetching fails or visual interaction is material to the evidence.

## Core Concepts

### Evidence Item

An evidence item is an acquisition record. It describes how Mycroft obtained a
source artifact and where the local copy lives.

Required fields:

```json
{
  "id": "E1",
  "source_url": "https://example.org/report",
  "acquisition_method": "firecrawl|browser|manual|api|vault",
  "accessed_at": "2026-05-18T12:00:00Z",
  "raw_path": "sources/raw/example-report.md",
  "sha256": "64 lowercase hex chars",
  "content_type": "text/markdown",
  "access_method": "full_text|open_access|archive_copy|abstract_only|inaccessible",
  "archive_url": "https://web.archive.org/...",
  "human_verification_required": false,
  "missing_source_gate": {
    "requested_source": "primary document requested",
    "returned_artifact": "what was actually acquired",
    "missing": "material gaps",
    "fallback_required": false,
    "confidence_effect": "none|cap_medium|cap_low|human_verification_required"
  }
}
```

Rules:

- The fetch wrapper computes `sha256` from the bytes actually written to
  `raw_path`. Agents do not invent or transcribe hashes.
- If `raw_path`, `screenshot_path`, or `downloaded_document_path` exists, the
  validator recomputes hashes before a provenance manifest can be signed.
- Search result pages can be evidence items, but search snippets alone cap
  claim confidence at `low`.

### Claim Grounding

Grounding is the relationship between a claim and evidence. A source is only an
anchor.

Every checked claim gets:

```json
{
  "claim_id": "claim-001",
  "claim_text": "specific factual statement",
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
  "evidence_refs": ["E1"]
}
```

Confidence caps:

- No local source file: `low`
- Search snippet only: `low`
- Contextual or source-adjacent evidence: `low`
- Inaccessible, abstract-only, materially redacted evidence: `low`
- Any material unstated assumption: `medium`
- Only secondary sources: `medium`
- Single primary source without contradiction search: `medium`
- Direct primary source plus independent corroboration and no unresolved
  contradiction: `high`

The validator must reject or warn when a claim's stated confidence exceeds its
`confidence_cap`.

### SIFT Manifest

The SIFT manifest is the claim-centered fact-check output. It references
evidence items rather than duplicating acquisition details.

Required top-level files for a fact-check package:

- `data/evidence-bundle.json`
- `data/sift-manifest.json`
- `data/provenance-manifest.json`

The existing `sift-manifest-v1` should be revised to:

- require 64-character SHA-256 hashes,
- require every claim source/evidence ref to resolve to an evidence item,
- require summary counts to match the claims array,
- distinguish `verified`, `partially_verified`, `unverified`,
  `contradicted`, and `mischaracterized`,
- include `grounding` for each claim.

### Provenance Manifest

The provenance manifest is package-centered. It makes the verification trail
tamper-evident.

It hashes:

- draft input when available,
- evidence bundle,
- SIFT manifest,
- local source files,
- generated review/report artifact when present.

It records:

- claims and verdicts,
- grounding strength,
- evidence refs,
- source acquisition method,
- archive URLs,
- human-verification flags,
- signing status.

Signing states:

- `unsigned`: manifest built locally and ready for inspection.
- `signed`: signer returned a receipt and receipt path is recorded.
- `signing_failed`: unsigned manifest remains usable; error is preserved.

Correct report language:

- "The verification package was signed and can be checked for later tampering."

Incorrect report language:

- "C2PA proves this story is true."

## Fetch Wrapper Requirements

`mycroft-fetch` should become an installed Mycroft command, not only an
integration demo file.

Installer/update requirements:

- install or symlink `mycroft-fetch` into `~/.local/bin`,
- add it to the shell startup block if needed,
- check it in `mycroft doctor`,
- preserve `MYCROFT_PROV_DIR` and `MYCROFT_VAULT_PATH` config.

Runtime requirements:

- write local source artifacts atomically,
- compute hashes from saved bytes,
- output machine-readable JSON by default for recipes,
- support `scrape`, `search`, and `provenance list/show`,
- include `access_method`, `archive_url`, `content_type`, and acquisition
  method,
- never shell-interpolate URLs or file paths.

## Review UX

Mycroft review output should show:

- each claim,
- verdict,
- grounding strength,
- confidence cap,
- missing assumptions,
- contradiction-search status,
- evidence item refs,
- local source file paths,
- source hashes,
- provenance/C2PA signing status.

The UI should make incomplete provenance visible without blocking editorial
review.

## Implementation Plan

1. Create schemas:
   - `schemas/evidence-bundle.schema.json`
   - `schemas/sift-manifest.schema.json`
   - `schemas/provenance-manifest.schema.json`

2. Promote `mycroft-fetch`:
   - move it from `integration/sift-c2pa/` into a supported script location,
   - install it through setup,
   - add doctor coverage,
   - add unit tests with a fake Firecrawl binary.

3. Add validators:
   - schema validation,
   - evidence ref resolution,
   - summary count checks,
   - confidence cap checks,
   - recomputed file-hash checks.

4. Update recipes:
   - `fact-check-c2pa.yaml` should use evidence bundle IDs, not free-form
     provenance IDs only,
   - keep C2PA signing opt-in,
   - fail clearly when `mycroft-fetch` is missing.

5. Add manifest builder:
   - build unsigned package manifests locally,
   - optionally POST to a configured Noosphere C2PA signer,
   - store receipts separately from private signing material.

6. Add review output:
   - render grounding and provenance state in markdown first,
   - later add an HTML review panel if Mycroft grows a report artifact.

## Resolved Decisions

Three of the four open questions from the draft are resolved in this v1. The
Noosphere endpoint remains open and is tracked below.

### Artifact storage — two-tier

Source artifacts live in **two locations** with a clear promotion gate:

- **Working tier** — `~/.mycroft/provenance/` (the current `mycroft-fetch`
  default). Every fetch lands here as an evidence item with its sha256, metadata,
  and raw file. Working-tier items can be garbage-collected after their case is
  closed or after a retention window.
- **Durable tier** — vault `sources/raw/<source-id>/` with the matching metadata
  in `sources/processed/<source-id>.md`. An evidence item is promoted to the
  durable tier when a fact-check elevates it (verdict published, evidence cited
  in a vault note, or human reviewer marks `human_review: approved` and tags
  the item for archive).

The promotion script must copy bytes (not symlink) and recompute the sha256 in
the durable tier so the durable record is self-contained.

### Search evidence model

`mycroft-fetch search` creates **one evidence item for the search result
page** (the SERP). When a selected result URL is then scraped, that scrape is
**a separate evidence item** with its own id, sha256, and acquisition method.
The SERP item and the scrape item are linked via `parent_evidence_id` on the
scrape so the chain is auditable.

This matches Spotlight's pattern and prevents claims from being grounded on a
SERP snippet alone — snippets cap confidence at `low` per the cap table; only
a full-text scrape can unlock `medium` or `high`.

### Editor verification state

Editor verification state is **separate from model-generated verdicts** so a
human can approve, reject, or revise the model's call without overwriting it.

Every claim gets a `human_review` field alongside `verdict`:

```json
{
  "verdict": "partially_verified",      // model output
  "human_review": "pending|approved|rejected|revised",
  "human_review_note": "optional editor comment",
  "human_reviewer": "optional reviewer id",
  "human_review_at": "ISO timestamp when reviewed"
}
```

Publishing a story or filing to the durable vault tier **requires** every
referenced claim to be `human_review: approved`. The validator must enforce
this for any output marked `publication_ready: true`.

When `human_review: rejected` or `revised`, preserve the original model
`verdict` and `grounding` for audit — do not overwrite them. Add the corrected
verdict in a separate `human_revised_verdict` field if applicable.

## Open Questions

- What exact Noosphere endpoint should Mycroft target: a shared
  `/api/provenance/sign`, a SIFT-specific route, or separate Spotlight/Mycroft
  routes with the same payload shape? Decision deferred until Noosphere's API
  contract stabilises; in the meantime `mycroft-fetch` stays signing-agnostic
  and the manifest builder produces `unsigned` manifests by default.
