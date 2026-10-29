# Contributing to Mycroft

Mycroft is a set of local agents and skills for investigative journalists, built on [Osaurus](https://osaurus.ai/) with an [OpenKnowledge](https://openknowledge.ai/) wiki. Contributions welcome: skills, agent instructions, documentation and bug fixes.

## Before you start

- Read [`README.md`](README.md) for the agents and the skills the Osaurus install ships.
- Read [`instructions/osaurus-system.md`](instructions/osaurus-system.md) for the editorial rules every skill must respect.
- Check open issues to avoid duplicate work.

## Development setup

```sh
git clone https://github.com/buriedsignals/mycroft.git
cd mycroft
python3 -m http.server 8765   # preview the landing page at http://127.0.0.1:8765/
python3 tests/skills-index-check.py
```

No build step. The repo is static files: HTML, JSON, SVG and Markdown.

## Adding a skill

1. Add `skills/<id>/SKILL.md` with `name` and a single-line `description` in its frontmatter, plus a `#` heading.
2. Add the id to [`skills.manifest`](skills.manifest).
3. Engine decides which skills the Osaurus install ships (`osaurusSkills` in Engine's Mycroft module), so add it there too.
4. Run `python3 tests/skills-index-check.py`.

## Commits

Conventional style appreciated:

- `feat(skills): add records-appeal skill`
- `fix(setup): correct shell escape in vault-path echo`
- `docs(architecture): clarify plugin install order`

## PR checklist

- [ ] `python3 tests/skills-index-check.py` passes
- [ ] HTML and journalist CTAs validate (`bash tests/install-sh-check.sh && bash tests/journalist-install-cta-check.sh`)
- [ ] No API keys, no PII, no secrets in the diff
- [ ] `CHANGELOG.md` updated under `[Unreleased]` if user-visible
- [ ] For plugin integration changes, [`docs/plugin-authoring.md`](docs/plugin-authoring.md) updated

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

## License

By contributing, you agree your work is licensed under the project's [MIT License](LICENSE).
