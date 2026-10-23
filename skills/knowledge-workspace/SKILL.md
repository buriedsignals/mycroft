---
name: knowledge-workspace
description: Search, read, link, audit, and maintain durable Mycroft knowledge through OpenKnowledge. Use for knowledge questions, durable Mycroft writes, morning briefs, audits, approved Spotlight-result lookup, OpenKnowledge health checks, and Markdown migration.
---

# Knowledge Workspace

Treat portable Markdown as durable authority. Read through the wiki service (`bsig wiki`, via `tools/wiki-service.py`), with OpenKnowledge as its fallback; write through OpenKnowledge. Use direct Markdown only for explicit recovery reads.

## Route deterministically

Mycroft may write only inside the configured Mycroft OpenKnowledge project root. Use document paths relative to that root; do not add a second `mycroft/` prefix.

Spotlight owns a separate configured OpenKnowledge workspace. Its approved `spotlight/` projection is read-only to Mycroft. Reject writes targeting that workspace, absolute document paths, traversal, symlink escapes, the intelligence vault, journals, active Spotlight case directories, and prose-only destination guesses. Active cases may be read only through the direct case adapter below; they are never searched, indexed, or written through OpenKnowledge.

## Read

1. Search with the wiki service's `search`, read cited documents exactly with its `read` before quoting them, and look up people, organisations, companies, places and contacts in the entity register with `resolve`, all through Mycroft's wiki tool. Retain each resolved path and score.
   - Never build a command line from a value. Send one JSON object on stdin in a quoted heredoc: `python3 "$MYCROFT_DIR/tools/wiki-service.py" search <<'WIKI_ARGS'`, then `{"vault_path": "<the recipe's vault_path>", "args": {"query": "..."}}`, then `WIKI_ARGS`. Leave out `vault_path` when there is none, and the wiki Engine recorded is used. A vault path with a line break: stop.
   - The tool finds the wiki root (the OpenKnowledge project at or above the vault) and refuses a relative or missing path, `.`, and a root at `/` or the home folder; on a `wiki-root` error, stop.
   - The answer is `data.result` on the `"event":"result"` line. `resolve` answers `linked` (use its `entity_id`), `candidates` (similar names to judge, never a match) or `unknown`. Protected-source names come back as `[protected]`; that is expected.
2. On `wiki-service-unavailable` (an older Engine), check OpenKnowledge's health and search readiness, search through OpenKnowledge, and read documents exactly through its `exec`.
3. Use OpenKnowledge links for backlinks, forward links, dead links, and graph audits.
4. If neither is available or ready, use exact read-only Markdown search, label results `markdown_fallback`, and report degraded state. Never turn an unready empty result into “not found.”

## Write

Validate every destination path before writing. Use OpenKnowledge `write` for new documents or a bounded `edit` after reading the current document. Read every changed document back through OpenKnowledge and verify its content and links before reporting success.

For several documents, show the proposed file list to the journalist, obtain approval, write one document at a time, and report exactly which writes succeeded or failed. OpenKnowledge 0.54.3 does not expose a transaction, checkpoint, conditional-write, or durable-outbox contract, so never claim those guarantees. Never fall back from a failed OpenKnowledge write to raw Markdown automatically.

## Spotlight boundary

Keep research, raw evidence, working claims, methodology, review artifacts, and active-case state outside Mycroft's knowledge project. Spotlight alone projects human-approved durable records under `spotlight/` in its configured workspace; Mycroft may search and read that workspace but may not write to it. Excluded claims and reasons remain in Spotlight's case-local receipt.

### Read an active case

Resolve the configured `case_workspace_root` from Spotlight's `.spotlight-config.json` (or the Engine-injected `SPOTLIGHT_CASES_ROOT`) and resolve the requested case slug beneath that root. Reject traversal and symlink escapes. Read case files directly and read-only; do not send case contents to OpenKnowledge or copy them into `mycroft/` or `spotlight/`.

Prefer the case's structured artifacts: `data/summary.json`, `data/findings.json`, `data/fact-check.json`, `data/ingestion.json`, and `summary.md`. Cite every case result as `case:<slug>/<relative-path>`. Raw research and evidence are opened only when the journalist explicitly requests them and the current model/provider is appropriate for the case's sensitivity.

### Trigger an investigation

If Spotlight is installed and the lead needs active OSINT casework, launch Spotlight and stop. Confirm the lead in one short line (who/what, jurisdiction if known, sensitivity if stated). Do not draft a Mycroft brief and do not run a Mycroft approval gate — Spotlight owns the brief and methodology gates. For a public install, run `spotlight doctor` and launch with `spotlight`; for an Engine-managed install, use `bsig spotlight run`. Pass only the lead through the configured harness's normal entrypoint. Never create a case by writing into the cases directory and never route active case material through OpenKnowledge.

If Spotlight is absent or its doctor fails, preserve the proposal as a Mycroft story/source plan and report that no investigation was started. After Spotlight completes and projection is approved, Mycroft may read durable results under `spotlight/`; it must not create, edit, or delete them. Do not treat active-case output as durable knowledge.

## Local semantic policy

For the local profile, require an embeddings URL on loopback, the pinned model and dimensions, complete or explicitly reported coverage, and no external fallback. A lexical fallback is degraded operation, not semantic success.
