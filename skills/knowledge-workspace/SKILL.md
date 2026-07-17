---
name: knowledge-workspace
description: Search, read, link, audit, and journal durable Mycroft or Spotlight knowledge through the storage-neutral Knowledge Workspace Port. Use for vault questions, durable knowledge writes, morning briefs, audits, Spotlight context lookup, approved Spotlight ingestion, OpenKnowledge health checks, legacy QMD/Obsidian migration, and any request that names a knowledge logical space.
---

# Knowledge Workspace

Treat portable Markdown and Spotlight JSON registries as durable authority. Use OpenKnowledge as the primary interface. Use direct Markdown only for explicit recovery reads or a journaled repair.

## Route deterministically

Require one logical space before every write:

- `knowledge` → project root
- `company` → `company/`
- `mycroft` → `mycroft/`
- `spotlight_verified` → `spotlight/`

Reject unknown spaces, absolute document paths, traversal, symlink escapes, the intelligence vault, journals, active Spotlight case directories as knowledge-workspace destinations, and prose-only destination guesses. Active cases may be read only through the direct case adapter below; they are never searched, indexed, or written through OpenKnowledge.

## Read

1. Check workspace health and search readiness.
2. Search through OpenKnowledge and retain each resolved path, backend, score, and readiness state.
3. Read cited documents exactly through OpenKnowledge `exec` before quoting them.
4. Use links for backlinks, forward links, dead links, and graph audits.
5. If OpenKnowledge is unavailable or unready, use exact read-only Markdown search, label results `markdown_fallback`, and report degraded state. Never turn an unready empty result into “not found.”

## Write

Require request ID, idempotency key, logical space, actor, source context, classification, expected version when editing, and a non-sensitive summary.

For one document, use OpenKnowledge `write` or bounded `edit`, then read it back and verify its content and links. For a multi-document package:

1. Validate every path and the complete package before writing.
2. Hash the exact package shown to the journalist.
3. Require approval of that hash.
4. Create an OpenKnowledge checkpoint and a durable pending journal.
5. Write the documents and registries through OpenKnowledge.
6. Reconcile paths, hashes, links, claim IDs, exclusions, and registries.
7. Mark the journal committed only after reconciliation.

Resume the same idempotent journal after interruption or restore its checkpoint. Never start an independent second ingest over partial state. Never fall back from a failed OpenKnowledge write to Obsidian or raw Markdown automatically.

## Spotlight boundary

Keep research, raw evidence, working claims, methodology, review artifacts, and active-case state outside the knowledge project. Write only human-approved and deterministically eligible durable records under `spotlight/`. Preserve excluded claims and reasons in the case-local receipt.

### Read an active case

Resolve the configured `case_workspace_root` from Spotlight's `.spotlight-config.json` (or the Engine-injected `SPOTLIGHT_CASES_ROOT`) and resolve the requested case slug beneath that root. Reject traversal and symlink escapes. Read case files directly and read-only; do not send case contents to OpenKnowledge or copy them into `mycroft/` or `spotlight/`.

Prefer the case's structured artifacts: `data/summary.json`, `data/findings.json`, `data/fact-check.json`, `data/ingestion.json`, and `summary.md`. Cite every case result as `case:<slug>/<relative-path>`. Raw research and evidence are opened only when the journalist explicitly requests them and the current model/provider is appropriate for the case's sensitivity.

### Trigger an investigation

Mycroft may prepare a Spotlight brief, but starting active casework is an explicit handoff. Confirm the lead, scope, jurisdiction, sensitivity, and the question to prove or disprove. Show the exact brief to the journalist and obtain approval, then launch the Engine-owned entry point `bsig spotlight run` and pass the approved brief using the configured harness's normal prompt/file mechanism. Never create a case by writing into the cases directory and never route the brief through OpenKnowledge.

If Spotlight is absent or its doctor fails, preserve the proposal as a Mycroft story/source plan and report that no investigation was started. After Spotlight completes and ingestion is approved, read durable results from logical space `spotlight_verified`; do not treat active-case output as durable knowledge.

## Local semantic policy

For the local profile, require an embeddings URL on loopback, the pinned model and dimensions, complete or explicitly reported coverage, and no external fallback. A lexical fallback is degraded operation, not semantic success.
