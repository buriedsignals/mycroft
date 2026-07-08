# SIFT × C2PA Integration Design

**Status**: Implemented — ready for production deployment
**Date**: 2026-05-09
**Target Launch**: Week of 2026-05-12

## Overview

This document describes how to encode SIFT fact-checking provenance as C2PA ingredients, creating a cryptographically verifiable chain from sources → verification → published article.

## Problem

Mycroft performs rigorous SIFT fact-checking, but the verification trail exists only as:
- Markdown tables in chat output
- Scattered vault notes
- No cryptographic binding between sources, verification, and final article

## Solution

Encode the SIFT process into C2PA manifests:

1. **Sources become ingredients** — Each consulted source is captured with a content hash at access time
2. **Verification becomes an assertion** — SIFT claims and verdicts are structured data in the manifest
3. **Article is signed** — Final artifact has cryptographic proof of its verification provenance

```
┌─────────────────────────────────────────────────────────────────┐
│                     Provenance Chain                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Source A ──┐                                                  │
│   (hash)     │                                                  │
│              ├──→  SIFT Verification  ──→  Signed Article       │
│   Source B ──┤     (assertion)             (C2PA manifest)      │
│   (hash)     │                                                  │
│              │                                                  │
│   Source C ──┘                                                  │
│   (hash)                                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Decision

**Sources are NOT signed independently.**

Signing every source would be:
- Computationally expensive (20+ sources per fact-check)
- Storage-heavy
- Unnecessary — the hash + timestamp + URL is sufficient provenance

Instead, sources are **referenced as ingredients with content hashes**. The hash proves "this is what the source said when I checked" — if disputed, anyone can:
1. Re-fetch the URL
2. Compare hashes
3. Check archive.org for that timestamp

## Components

### 1. `mycroft-fetch` CLI

Provenance-capturing fetch/search — sovereign default (Crawl4AI scrape / SearXNG
search), Firecrawl fallback — that records provenance metadata:

```bash
mycroft-fetch scrape https://example.com/article
```

Output:
```json
{
  "provenance": {
    "id": "prov-a1b2c3",
    "url": "https://example.com/article",
    "content_hash": "sha256:e3b0c44...",
    "access_timestamp": "2026-05-09T14:32:00Z"
  },
  "content": "# Article\n\nBody text..."
}
```

Provenance records are stored locally in `~/.mycroft/provenance/`.

### 2. SIFT Manifest

When fact-checking completes, Mycroft emits a structured manifest:

```json
{
  "schema": "sift-manifest-v1",
  "claims": [
    {
      "id": "claim-001",
      "text": "Company X reported $1M revenue",
      "verdict": "verified",
      "sources": ["prov-a1b2c3", "prov-d4e5f6"]
    }
  ],
  "sources": [
    {
      "id": "prov-a1b2c3",
      "url": "https://...",
      "content_hash": "sha256:...",
      "access_timestamp": "...",
      "sift_step": "trace_to_original"
    }
  ]
}
```

See `sift-manifest-schema.json` for full schema.

### 3. C2PA Integration

New endpoint in C2PA artifact service:

```
POST /api/process_sift
Content-Type: application/json

{
  "article_path": "/path/to/article.md",
  "sift_manifest": { ... },
  "credential_id": "journalist-key-001"
}
```

Creates:
- `c2pa.ingredient` assertions for each source (hash refs, not full content)
- `sift:verification` assertion with claims and verdicts
- Signed C2PA manifest for the article

### 4. New C2PA Assertion Type

```json
{
  "assertion_type": "sift:verification",
  "data": {
    "methodology": "SIFT",
    "methodology_version": "1.0",
    "timestamp": "2026-05-09T15:00:00Z",
    "investigator_did": "did:web:...",
    "claims": [...],
    "summary": {
      "verified": 3,
      "contradicted": 1,
      "total": 5
    }
  }
}
```

### 5. Journalism Policy Type

New artifact type and policy in C2PA:

```json
{
  "id": "sift-verification-policy",
  "name": "SIFT Fact-Check Policy",
  "artifactTypes": ["Journalism"],
  "settings": {
    "siftRequired": true,
    "assertions": {
      "sift:verification": true,
      "c2pa.ingredient": true
    }
  }
}
```

## Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         MYCROFT                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Journalist runs fact-check recipe                           │
│                                                                 │
│  2. Recipe uses mycroft-fetch (not raw firecrawl)               │
│     → Each fetch creates provenance record                      │
│                                                                 │
│  3. SIFT analysis produces claims + verdicts                    │
│                                                                 │
│  4. Recipe emits sift-manifest.json                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      C2PA ARTIFACT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  5. POST /api/process_sift with manifest                        │
│                                                                 │
│  6. Create source ingredients (hash refs only)                  │
│                                                                 │
│  7. Create sift:verification assertion                          │
│                                                                 │
│  8. Sign article with journalist's DID/credential               │
│                                                                 │
│  9. Return signed C2PA manifest                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Verification UX

When someone views a SIFT-verified article:

```
┌─────────────────────────────────────────────────────────────────┐
│  ✓ Content Credentials Verified                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Signed by: Jane Reporter (did:web:mycroft...)                  │
│  Organization: Independent News Collective                     │
│                                                                 │
│  SIFT Verification:                                             │
│  ├─ 3 claims verified                                           │
│  ├─ 1 claim partially verified                                  │
│  └─ 1 claim contradicted (corrected in article)                 │
│                                                                 │
│  Sources consulted: 5                                           │
│  └─ EPA, SEC, State records, Company filings                    │
│                                                                 │
│  [View full verification trail]                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Status

### Completed ✓

| Component | Location | Description |
|-----------|----------|-------------|
| `mycroft-fetch` CLI | `integration/sift-c2pa/mycroft-fetch` | Provenance-capturing fetch/search (Crawl4AI/SearXNG default, Firecrawl fallback) |
| SIFT manifest schema | `integration/sift-c2pa/sift-manifest-schema.json` | JSON Schema for structured output |
| SIFT routes | `c2pa-artifact/server/routes/sift_routes.py` | `/api/sift/process`, `/api/sift/verify`, `/api/sift/schema` |
| Journalism policy | `c2pa-artifact/server/config/policy_settings.json` | New artifact type + SIFT policy |
| SIFT viewer | `c2pa-artifact/client/src/components/SiftVerificationViewer.js` | React component for viewing SIFT results |
| C2PA recipe | `mycroft/recipes/fact-check-c2pa.yaml` | Updated recipe with mycroft-fetch + manifest emission |
| Test script | `integration/sift-c2pa/test-integration.sh` | End-to-end integration test |

### API Endpoints

#### Batch Processing (Single-step)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sift/process` | POST | Submit SIFT manifest, create signed C2PA artifact |
| `/api/sift/verify` | POST | Verify SIFT-signed manifest |
| `/api/sift/schema` | GET | Get SIFT manifest JSON schema |
| `/api/sift/verdicts` | GET | Get verdict types with descriptions |

#### Staged Pipeline (Multi-step)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sift/pipeline/start` | POST | Start pipeline with draft capture |
| `/api/sift/pipeline/<id>/source` | POST | Add source to pipeline |
| `/api/sift/pipeline/<id>/verify` | POST | Submit SIFT verdicts |
| `/api/sift/pipeline/<id>/publish` | POST | Final publication signature |
| `/api/sift/pipeline/<id>` | GET | Get pipeline status |
| `/api/sift/pipeline/<id>/chain` | GET | Get full claim chain |
| `/api/sift/pipelines` | GET | List all pipelines |

### Staged Pipeline Architecture

Each stage creates a new C2PA claim that references the previous claim via `parent_claim`, building a cryptographic provenance chain:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Claim Chain                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   DRAFT          → claim-001 (initial)                          │
│       ↓                                                         │
│   SOURCE 1       → claim-002 (parent: claim-001)                │
│       ↓                                                         │
│   SOURCE 2       → claim-003 (parent: claim-002)                │
│       ↓                                                         │
│   SOURCE N       → claim-00N (parent: claim-00N-1)              │
│       ↓                                                         │
│   VERIFY         → claim-V   (parent: last source claim)        │
│       ↓                                                         │
│   PUBLISH        → claim-P   (parent: verify claim) ← FINAL     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Each claim contains:
- `claim_id`: Unique identifier
- `timestamp`: ISO 8601 timestamp
- `content.hash`: SHA-256 hash of stage content
- `parent_claim`: Reference to previous claim (id, timestamp, hash)
- `assertions`: Stage-specific data (source info, verdicts, etc.)
- `signature`: Cryptographic signature

## Files in This Directory

```
sift-c2pa/
├── DESIGN.md                    # This document
├── mycroft-fetch                # CLI wrapper (Python, executable)
├── sift-manifest-schema.json    # JSON Schema for SIFT output
├── example-sift-manifest.json   # Example manifest
├── demo.sh                      # One-click demo (batch API)
├── demo-pipeline.sh             # Staged pipeline demo
└── test-integration.sh          # End-to-end test script
```

## Next Steps

1. **Mycroft side**:
   - Integrate `mycroft-fetch` into fact-check recipe
   - Modify recipe to emit `sift-manifest.json` on completion
   - Test with real fact-checking workflows

2. **C2PA side**:
   - Add `Journalism` artifact type
   - Implement `sift:verification` assertion handler
   - Create `/api/process_sift` endpoint
   - Add SIFT policy type

3. **Integration**:
   - Define handoff mechanism (file? API call? vault location?)
   - Test end-to-end flow
   - Build verification viewer for SIFT assertions

## Open Questions

1. **Handoff mechanism**: How does the SIFT manifest get to the C2PA service?
   - Option A: Mycroft calls C2PA API directly
   - Option B: Manifest saved to vault, separate signing step
   - Option C: MCP tool in Goose that calls C2PA

2. **Vault source provenance**: For sources from the Mycroft vault (not web), how do we capture provenance?
   - Hash the vault file content
   - Record vault path as "URL"

3. **Partial verification**: When sources are paywalled/unavailable, how do we represent that in the ingredient?
   - `access_type: inaccessible`
   - Note in SIFT assertion

4. **Re-verification**: If someone wants to verify the sources later, what tooling is needed?
   - Archive.org integration
   - Hash comparison tool
