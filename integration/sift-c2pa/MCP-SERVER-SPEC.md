# Noosphere MCP Server Specification

**Purpose**: Native Goose integration with the Noosphere digital integrity platform, eliminating curl-based API calls in favor of MCP tool invocations.

**Related**: `~/Sites/noosphere/github/code-signing-agent` — existing LangGraph agent with MCP transport support and Noosphere integration patterns.

## Production URLs

```json
{
  "noosphere": {
    "platform_url": "https://platform.noosphere.tech",
    "did_service_url": "https://did.noosphere.tech"
  }
}
```

## Local Development

```
C2PA Artifact Server: ~/Sites/noosphere/github/c2pa-artifact-merge
Default Port: 5002
```

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         MYCROFT (Goose)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Recipe: fact-check-c2pa.yaml                                  │
│       ↓                                                         │
│   MCP Tool Call: noosphere_pipeline_start                       │
│       ↓                                                         │
│   MCP Tool Call: noosphere_add_source (×N)                      │
│       ↓                                                         │
│   MCP Tool Call: noosphere_verify                               │
│       ↓                                                         │
│   MCP Tool Call: noosphere_publish                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ MCP Protocol (stdio)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    noosphere-mcp-server                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   TypeScript/Python MCP server                                  │
│   Env: NOOSPHERE_API_URL (default: http://localhost:5002)       │
│   Env: NOOSPHERE_API_KEY (optional, for prod)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Noosphere C2PA Artifact Server                     │
│         ~/Sites/noosphere/github/c2pa-artifact-merge            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   /api/sift/pipeline/start                                      │
│   /api/sift/pipeline/<id>/source                                │
│   /api/sift/pipeline/<id>/verify                                │
│   /api/sift/pipeline/<id>/publish                               │
│   /api/sift/pipeline/<id>/chain                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## MCP Tools

### 1. `noosphere_pipeline_start`

Start a new SIFT verification pipeline with draft content.

**Parameters:**
```json
{
  "draft_content": "string (required) - The article draft text",
  "title": "string (required) - Article title",
  "credential_id": "string (optional) - Signing credential, default: 'default'",
  "investigator": {
    "name": "string (optional) - Journalist name",
    "organization": "string (optional) - News organization",
    "did": "string (optional) - Decentralized identifier"
  }
}
```

**Returns:**
```json
{
  "pipeline_id": "uuid",
  "claim_id": "uuid",
  "stage": "draft",
  "timestamp": "ISO8601"
}
```

### 2. `noosphere_add_source`

Add a source to an existing pipeline. Creates a new claim in the chain.

**Parameters:**
```json
{
  "pipeline_id": "string (required) - From pipeline_start",
  "source": {
    "id": "string (required) - Provenance ID from mycroft-fetch",
    "url": "string (required) - Source URL",
    "content_hash": "string (required) - SHA-256 hash",
    "access_timestamp": "string (required) - ISO8601",
    "title": "string (optional) - Source title",
    "access_type": "string (optional) - full|partial|inaccessible",
    "sift_step": "string (optional) - trace_to_original|investigate_source|find_better_coverage",
    "is_primary": "boolean (optional) - Primary source flag"
  }
}
```

**Returns:**
```json
{
  "pipeline_id": "uuid",
  "claim_id": "uuid",
  "stage": "source",
  "source_count": 3,
  "parent_claim_id": "uuid"
}
```

### 3. `noosphere_verify`

Submit SIFT verification results (claims and verdicts).

**Parameters:**
```json
{
  "pipeline_id": "string (required)",
  "claims": [
    {
      "id": "string (required) - Claim identifier",
      "text": "string (required) - The factual claim",
      "verdict": "string (required) - verified|partially_verified|unverified|contradicted|mischaracterized",
      "sources": ["string"] (required) - Array of source IDs that support/refute",
      "notes": "string (optional) - Verification notes"
    }
  ],
  "summary": {
    "verified": "number",
    "partially_verified": "number",
    "unverified": "number",
    "contradicted": "number",
    "mischaracterized": "number",
    "total_claims": "number",
    "total_sources": "number"
  }
}
```

**Returns:**
```json
{
  "pipeline_id": "uuid",
  "claim_id": "uuid",
  "stage": "verify",
  "summary": { ... },
  "parent_claim_id": "uuid"
}
```

### 4. `noosphere_publish`

Finalize and sign the artifact for publication.

**Parameters:**
```json
{
  "pipeline_id": "string (required)",
  "publish_metadata": {
    "publisher": "string (optional) - Publishing organization",
    "published_url": "string (optional) - Final article URL"
  }
}
```

**Returns:**
```json
{
  "pipeline_id": "uuid",
  "claim_id": "uuid",
  "final_manifest_id": "uuid",
  "stage": "publish",
  "claim_chain": [ ... ],
  "signature": "string"
}
```

### 5. `noosphere_get_chain`

Retrieve the full claim chain for a pipeline.

**Parameters:**
```json
{
  "pipeline_id": "string (required)"
}
```

**Returns:**
```json
{
  "pipeline_id": "uuid",
  "claims": [
    {
      "claim_id": "uuid",
      "stage": "draft|source|verify|publish",
      "timestamp": "ISO8601",
      "parent_claim_id": "uuid|null",
      "content_hash": "string"
    }
  ],
  "current_stage": "string",
  "is_complete": "boolean"
}
```

### 6. `noosphere_get_verdicts`

Get available SIFT verdict types (utility tool).

**Parameters:** None

**Returns:**
```json
{
  "verdicts": {
    "verified": "Claim confirmed by multiple authoritative sources",
    "partially_verified": "Core claim accurate but details differ",
    "unverified": "Unable to confirm or deny",
    "contradicted": "Claim directly contradicted by evidence",
    "mischaracterized": "Facts accurate but context misleading"
  }
}
```

## Implementation

### Option A: TypeScript (Recommended)

```
noosphere-mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts          # MCP server entry point
│   ├── tools/
│   │   ├── pipeline.ts   # Pipeline tools
│   │   └── utils.ts      # Utility tools
│   └── client/
│       └── noosphere.ts  # HTTP client for C2PA API
└── README.md
```

**Dependencies:**
- `@modelcontextprotocol/sdk` — MCP SDK
- `zod` — Schema validation
- `node-fetch` or built-in fetch — HTTP client

### Option B: Python

```
noosphere-mcp-server/
├── pyproject.toml
├── src/
│   └── noosphere_mcp/
│       ├── __init__.py
│       ├── server.py     # MCP server
│       ├── tools.py      # Tool implementations
│       └── client.py     # HTTP client
└── README.md
```

**Dependencies:**
- `mcp` — MCP Python SDK
- `httpx` — Async HTTP client
- `pydantic` — Schema validation

## Goose Configuration

Add to `~/.config/goose/profiles/mycroft/goose.mcp.yaml`:

```yaml
noosphere:
  command: npx
  args:
    - -y
    - noosphere-mcp-server
  env:
    NOOSPHERE_API_URL: "http://localhost:5002"
    # NOOSPHERE_API_KEY: "${NOOSPHERE_API_KEY}"  # For prod
```

Or for Python:

```yaml
noosphere:
  command: uvx
  args:
    - noosphere-mcp-server
  env:
    NOOSPHERE_API_URL: "http://localhost:5002"
```

## Updated Recipe

`recipes/fact-check-c2pa.yaml` with MCP:

```yaml
name: fact-check-c2pa
description: SIFT fact-checking with Noosphere provenance signing
extensions:
  - firecrawl
  - noosphere  # NEW: MCP server

parameters:
  draft_text:
    type: string
    required: true
  credential_id:
    type: string
    default: "default"

steps:
  - name: Start pipeline
    tool: noosphere_pipeline_start
    params:
      draft_content: "{{ draft_text }}"
      title: "{{ title | default('Untitled Investigation') }}"
      credential_id: "{{ credential_id }}"

  # ... SIFT verification steps using mycroft-fetch ...

  - name: Add sources
    tool: noosphere_add_source
    for_each: "{{ sources }}"
    params:
      pipeline_id: "{{ pipeline_id }}"
      source: "{{ item }}"

  - name: Submit verdicts
    tool: noosphere_verify
    params:
      pipeline_id: "{{ pipeline_id }}"
      claims: "{{ claims }}"
      summary: "{{ summary }}"

  - name: Publish
    tool: noosphere_publish
    params:
      pipeline_id: "{{ pipeline_id }}"
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NOOSPHERE_API_URL` | No | `http://localhost:5002` | C2PA artifact server URL |
| `NOOSPHERE_API_KEY` | No | None | API key for authenticated requests |
| `NOOSPHERE_CREDENTIAL_ID` | No | `default` | Default signing credential |

## Obtaining an API Key

To use the Noosphere platform in production, you need an API key:

1. **Sign up / Log in** at [platform.noosphere.tech](https://platform.noosphere.tech)

2. **Navigate to Settings** → **API Keys**

3. **Create a new API key:**
   - Click "Create API Key"
   - Enter a name (e.g., "Mycroft SIFT Integration")
   - Select scopes:
     - `read` — Read pipelines and manifests
     - `write` — Create pipelines, add sources, publish
     - `sift` — Full SIFT pipeline access (recommended)
   - Set expiration (optional)
   - Click "Generate"

4. **Copy the key immediately** — it's only shown once:
   ```
   noosphere_a1b2c3d4e5f6789012345678901234ab
   ```

5. **Store securely:**
   ```bash
   # Add to your shell profile or .env file
   export NOOSPHERE_API_KEY="noosphere_..."
   ```

**Key format:** `noosphere_` + 32 hex characters

**Security notes:**
- API keys are hashed on the server — we cannot recover lost keys
- Keys can be revoked anytime from the Settings page
- Use separate keys for different environments (dev, staging, prod)
- Keys inherit your organization's signing credentials and policies

## Production Deployment

For production, the MCP server should point to the deployed Noosphere platform:

```yaml
noosphere:
  command: npx
  args:
    - -y
    - noosphere-mcp-server
  env:
    NOOSPHERE_API_URL: "https://platform.noosphere.tech"
    NOOSPHERE_API_KEY: "${NOOSPHERE_API_KEY}"
```

## Implementation Options

### Option 1: Extend code-signing-agent (Recommended)

The existing `code-signing-agent` already has:
- MCP transport support (`--transport stdio`)
- Noosphere integration patterns
- LangGraph workflow orchestration
- A2A protocol implementation

**Add SIFT skills to code-signing-agent:**

```python
# code_signing_agent/nodes/sift.py

async def sift_pipeline_start(state: AgentState) -> AgentState:
    """Start SIFT verification pipeline."""
    ...

async def sift_add_source(state: AgentState) -> AgentState:
    """Add source to pipeline."""
    ...

async def sift_verify(state: AgentState) -> AgentState:
    """Submit SIFT verdicts."""
    ...

async def sift_publish(state: AgentState) -> AgentState:
    """Publish final signed artifact."""
    ...
```

**Add to A2A agent card:**
```json
{
  "skills": [
    {"name": "sign", ...},
    {"name": "verify", ...},
    {"name": "sift-start", "description": "Start SIFT verification pipeline"},
    {"name": "sift-source", "description": "Add source to pipeline"},
    {"name": "sift-verify", "description": "Submit SIFT verdicts"},
    {"name": "sift-publish", "description": "Publish signed journalism artifact"}
  ]
}
```

### Option 2: Standalone noosphere-mcp-server

Lighter weight, focused only on SIFT/journalism use case. Better if code-signing-agent is too heavy for Mycroft's needs.

## Next Steps

1. **Decide implementation path** — Extend code-signing-agent or create standalone
2. **Implement MCP tools** — Python (matches code-signing-agent) or TypeScript
3. **Add to Mycroft extensions manifest** — Register as optional extension
4. **Update fact-check-c2pa recipe** — Replace curl with MCP tool calls
5. **Test locally** — Against c2pa-artifact-merge on localhost:5002
6. **Deploy** — PyPI (`noosphere-mcp`) or npm (`noosphere-mcp-server`)
