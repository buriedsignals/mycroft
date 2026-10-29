# Contributing to Mycroft

Contributions can improve the website, agent instructions, skills or documentation.
Read the [README](README.md) and the [Mycroft system instructions](instructions/osaurus-system.md)
first. For visual changes, follow [DESIGN.md](DESIGN.md).

## Preview the website

```sh
git clone https://github.com/buriedsignals/mycroft.git
cd mycroft
python3 -m http.server 8765
```

Open `http://127.0.0.1:8765/`. The site is static HTML, JavaScript, CSS and media;
there is no build or npm install step. The `analyst/package.json` belongs to
the installed Analyst runtime, not the website.

## Change a skill

1. Add `skills/<id>/SKILL.md` with `name` and a single-line `description` in its
   frontmatter, plus a `#` heading. Preserve upstream attribution and licences.
2. For an installed skill, add the id to [`skills.manifest`](skills.manifest)
   and coordinate the matching `osaurusSkills` change in Engine's Mycroft module.
   Osaurus-specific connector copies live in `skills/osaurus/` and use Engine's
   `osaurusSkillOverrides` mapping.
3. The public website filters out `navigator`, `scoutpost` and `ai-writing-detox`.
   Website-only references belong in [`catalog/featured-skills.json`](catalog/featured-skills.json),
   with an explicit status, source link and credits. A listing does not install a skill.
4. Run the skills-index check below.

Do not hand-edit signed catalogue content or its signature. Engine owns release
pins, model selection and install plans. Contract edits under `install/contracts/`
also require coordinated Engine validation and updated contract digests.

## Checks

Run the checks relevant to your change; these are the website's CI checks:

```sh
python3 tests/skills-index-check.py
bash tests/journalist-install-cta-check.sh
bash tests/install-sh-check.sh
node tests/feedback-widget-check.js
```

For scroll/rendering changes, run the browser regression check against the local
preview server. It checks phone/tablet scrolling independently of animation
frames, overflow, desktop paper controls, resizing and reduced motion:

```sh
npm install --prefix /tmp/mycroft-browser-qa playwright@1.58.2
/tmp/mycroft-browser-qa/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/mycroft-browser-qa/node_modules node tests/mobile-scroll-check.cjs
```

Set `SITE_URL` for another preview URL, or `CHROME_PATH` to use an existing
Chrome executable. Screenshots are written to `/tmp/mycroft-*.png`.

CI also parses `index.html` and catalogue/install-contract JSON. For layout
changes, inspect desktop and phone widths, keyboard focus and reduced motion.
Do not submit real feedback or newsletter forms as a test.

## Pull requests

Explain the user-visible change and what you checked. Include screenshots for
layout changes, preserve source-protection rules, and update [CHANGELOG.md](CHANGELOG.md)
for user-visible changes. Never include keys, private wiki content or confidential
source identities. Report vulnerabilities through [SECURITY.md](SECURITY.md).

The [GitHub Pages workflow](.github/workflows/pages.yml) validates pull requests;
a push to `main` validates and deploys the repository root to
`https://mycroft.buriedsignals.com/`. Deployment does not publish a new Engine
catalogue or update installed agents. After a site release, check the workflow
and the changed production page.

Contributions are covered by the [MIT licence](LICENSE) and
[Code of Conduct](CODE_OF_CONDUCT.md).
