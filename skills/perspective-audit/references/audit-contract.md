# Perspective audit contract

Use this contract whenever the audit must be stored, validated, compared across runs, or handed to another editor.

## Data model

Emit one JSON object with `schema: perspective-audit-v1`.

### Corpus

Record:

- a plain-language corpus description;
- the evidence IDs available to the audit;
- included-source and included-passage counts;
- excluded material and reasons;
- sampling and deduplication notes;
- a representativeness statement.

Evidence references may include fragments such as `E-thread-01#comment-17`. The part before `#` must resolve to an evidence ID in the corpus and, when supplied, the evidence bundle.

### Perspectives

Use IDs such as `P-001`. Each perspective requires:

- a descriptive label and explanation;
- one or more stance axes, such as `cost versus public benefit`;
- direct evidence references;
- an observed source count;
- extraction confidence;
- `representativeness: corpus_only|unknown`;
- optional counterevidence references;
- a human-review state.

Source count describes distinct sources in the bounded corpus after deduplication. It is not a poll result.

### Summaries

Use IDs such as `S-001`. Store one sentence or auditable proposition per record. Link it to all contributing perspectives and evidence passages. Use `support_type` from Mycroft's grounding vocabulary:

- `direct`: evidence plainly supports all material summary elements;
- `indirect`: a short, explicit inference is required;
- `inferred`: synthesis depends on assumptions that an editor should inspect.

Record meaningful evidence omitted during compression.

### Draft sentences

Use IDs such as `D-001`. Preserve the exact draft sentence. Link it to summary, perspective, and evidence records. Empty links are allowed so unsupported text can be represented honestly.

Available flags are:

- `unsupported_assertion`
- `omitted_perspective`
- `overrepresented_perspective`
- `collapsed_disagreement`
- `attribution_drift`
- `certainty_inflation`
- `loaded_language`
- `stereotyping`
- `false_balance`
- `factual_disagreement_as_opinion`
- `other`

Optional model signals may retain a detector name, label, score, and explanation. Do not turn them into findings without an editorial rationale.

Suggested rewrites require the proposed sentence, the problem addressed, a rationale, `claim_meaning_changed`, and a human-review state. Never mark a suggestion as applied in this artifact.

### Lineage

Represent transformations as edges:

- evidence -> perspective: `supports`
- perspective -> summary: `summarized_as` or `merged_into`
- summary or perspective -> draft sentence: `propagates_to`
- any supported record -> another record: `contradicts`

Every declared evidence, perspective, and summary relationship must have a matching edge. Add a concise transformation note when compression, merging, or qualification changed the expression.

### Findings and gaps

Use findings for problems observed in the supplied draft. Each finding requires target records, evidence references when relevant, severity, rationale, and a suggested editorial action.

Use reporting gaps for voices or source types that may be missing. A gap must carry `observed_in_corpus: false`. It is a reporting lead, not an extracted perspective.

## Editor-facing Markdown

Render the JSON into this compact order:

1. `# Perspective audit: <topic>`
2. Corpus boundary and limitations
3. Perspective ledger table
4. Draft coverage table, if a draft was supplied
5. Findings ordered by severity
6. Reporting gaps
7. Suggested rewrites shown as before/after pairs
8. Human-review status

Do not reduce the report to a single diversity score. Counts can help navigation, but an editor needs the underlying evidence and transformation trail.

## Quality checks

Before delivery, confirm:

- every perspective is observed and evidence-linked;
- every summary preserves attribution and uncertainty;
- every draft sentence has explicit links or an unsupported flag;
- frequency is described only within the corpus;
- disagreements over facts are routed to fact-checking;
- rewrite suggestions preserve claims or disclose their semantic change;
- no suggestion has been applied automatically;
- all IDs resolve and the validator passes.

## Method note

AutoJourn demonstrates an interface for inspecting perspectives, stance summaries, generated copy, bias flags, and rewrites. This contract adopts that inspectability pattern but rejects two unsafe shortcuts in the demonstration prompts: generating viewpoints that were not found in the corpus and forcing all perspectives into an Agree/Disagree binary.

Paper: Himel Ghosh, Ahmed Mosharafa, and Georg Groh, “AutoJourn: Multi-Perspective Summarisation, Bias Detection and Bias Neutralisation for LLM-Generated News in Automated Journalism,” arXiv:2607.18983v1, 21 July 2026. https://arxiv.org/html/2607.18983v1
