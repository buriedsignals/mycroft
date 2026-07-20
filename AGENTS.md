# Mycroft

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
