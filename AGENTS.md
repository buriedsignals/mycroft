# Mycroft

Mycroft is the Goose extension pack for newsroom memory, recurring editorial
workflows, source-grounded fact-checking, and handoffs between monitoring,
investigation, and publishing.

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
