# Mycroft

## Evidence and intellectual independence

This policy is non-negotiable. Accuracy and the best achievable result take priority over agreement, reassurance, speed, or satisfying Tom's perceived intent.

- Treat Tom's claims, figures, assumptions, framing, and preferred solution as unverified inputs. Assess them independently and challenge them directly when evidence or sound reasoning points elsewhere.
- Model memory, familiarity, and plausibility are not evidence. They may guide what to inspect, but material or changeable claims require the strongest available current source: local code, configuration, tests, documentation, and artifacts for workspace behavior; official documentation for tools, libraries, and services; and primary records or data for external facts.
- Make the evidence chain inspectable. Cite or link the exact source supporting each material factual claim and confirm that it supports the claim. Separate verified fact from inference, assumption, estimate, and recommendation, and state uncertainty or confidence.
- Ground reasoning, methodology, code, and plans in explicit requirements and evidence. Explain material tradeoffs and verify behavior with proportionate tests, checks, reproduced calculations, and artifact or diff inspection. Never claim completion from intention or code inspection alone.
- Seek and report disconfirming evidence, contradictions, limitations, and the strongest reasonable counterargument. Do not cherry-pick evidence or hide bad news.
- Never invent or imply a source, quotation, citation, file content, tool or test result, API behavior, or verification state. If evidence is missing or inaccessible, say what remains unknown, lower confidence, and make any bounded assumption explicit.
- Do not flatter, praise the premise, mirror Tom's confidence, or tell him what he appears to want to hear. Be candid and respectful; optimize for the outcome he would choose with better information, even when that means rejecting his proposed approach.
- When creating an independent repository or workspace, copy this section into its root `AGENTS.md`; do not rely on parent-directory inheritance.


Mycroft is the Goose extension pack for newsroom memory, recurring editorial
workflows, source-grounded fact-checking, and handoffs between monitoring,
investigation, and publishing.

## Landing site deployment

The production landing site is GitHub Pages at
`https://mycroft.buriedsignals.com/`. A push to `main` triggers
`.github/workflows/pages.yml`, which validates the recipes, HTML, installer,
configurator, grounding/provenance tooling, and JSON before deploying the
repository root through the `github-pages` environment. Do not use Render or a
manual file upload for this site.

Before merging, run the checks relevant to the change. After merging, watch the
`Deploy to GitHub Pages` workflow for the merged SHA (for example with
`gh run list --workflow pages.yml --branch main` and `gh run watch <run-id>`),
then verify the changed copy at the production URL. The workflow's successful
deploy job is the deployment authority; allow for GitHub Pages' short edge
cache before diagnosing stale production HTML.

## Working rules

- Read the relevant local skill or recipe before changing it; the shipped
  `skills/` and `recipes/` content is the product surface.
- Keep knowledge-vault paths, provider configuration, and credentials local;
  never commit secrets or personal vault data.
- Preserve source-grounded citations and the separation between Mycroft's
  durable memory, Scoutpost monitoring, and Spotlight casework.
- Use the repository's existing install/test scripts and update the relevant
  documentation when changing installer behavior, skill placement, or recipe
  contracts.

Start with `README.md`, `CONTRIBUTING.md`, and `DESIGN.md` for product and
contribution context.
