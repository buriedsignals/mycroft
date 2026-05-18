# Grounding And Provenance Spec

Status: draft

This spec defines a Mycroft grounding and provenance layer for fact-checking,
source collection, and publication support. It adapts the stronger parts of the
Spotlight grounding/C2PA work while keeping Mycroft focused on durable newsroom
knowledge and draft verification.

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

## Open Questions

- Should Mycroft store source artifacts in `~/.mycroft/provenance` only, or in
  the durable vault under `sources/raw/` with metadata in `sources/processed/`?
- Should `mycroft-fetch search` create one evidence item for the search result
  page, or separate items only after selected result URLs are scraped?
- What exact Noosphere endpoint should Mycroft target: a shared
  `/api/provenance/sign`, a SIFT-specific route, or separate Spotlight/Mycroft
  routes with the same payload shape?
- Should editor verification state be separate from model-generated verdicts so
  a human can approve, reject, or mark a claim used in a story?
