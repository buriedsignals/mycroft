# Contributing to Mycroft

Mycroft is an extension pack for [Goose](https://goose-docs.ai/) built for investigative journalists. Contributions welcome — recipes, plugin integrations, documentation, bug fixes.

## Before you start

- Read [`docs/architecture.md`](docs/architecture.md) — how the pack fits together.
- Read [`instructions/journalism.md`](instructions/journalism.md) — the editorial posture recipes must respect.
- Check open issues — avoid duplicate work.

## Development setup

```sh
git clone https://github.com/buriedsignals/mycroft.git
cd mycroft

# Preview the setup page locally
open index.html       # landing
open setup.html       # install landing page

# Validate all recipes + configs
python3 tools/validate-recipes.py
```

No build step. The repo is static files — HTML, YAML, JSON, SVG, Markdown.

## Adding a recipe

1. Drop a new `.yaml` file under `recipes/` (or `recipes/apify-social/` for social scrapers).
2. Follow the [Goose Recipe reference](https://goose-docs.ai/docs/guides/recipes/recipe-reference).
3. Required fields: `version`, `title`, `description`, and at least one of `instructions` / `prompt`.
4. Run `python3 tools/validate-recipes.py` — commit only if it passes.

## Adding a plugin

See [`docs/plugin-authoring.md`](docs/plugin-authoring.md) for the full pattern (separate repo, `AGENTS.md`, install hooks, configurator integration).

## Recipe style

- Instructions must reference the journalism posture (SIFT, attribution, no fabrication) — not re-declare it.
- Prefer explicit CLI invocations (`firecrawl scrape`, `hf download`) over model-chosen shell. Reduces variance across frontier vs local models.
- Cite every user-facing claim in the prompt's output format.
- Keep recipes under 150 lines where possible. Long recipes mean the work should be a plugin.

## Commits

Conventional style appreciated:

- `feat(recipes): add newsletter-triage recipe`
- `fix(setup): correct shell escape in vault-path echo`
- `docs(architecture): clarify plugin install order`

## PR checklist

- [ ] `python3 tools/validate-recipes.py` passes
- [ ] HTML validates (`bash tests/install-sh-check.sh && python3 tests/setup-server-check.py`)
- [ ] No API keys, no PII, no secrets in the diff
- [ ] `CHANGELOG.md` updated under `[Unreleased]` if user-visible
- [ ] For plugin integration changes, [`docs/plugin-authoring.md`](docs/plugin-authoring.md) updated

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

## License

By contributing, you agree your work is licensed under the project's [MIT License](LICENSE).
