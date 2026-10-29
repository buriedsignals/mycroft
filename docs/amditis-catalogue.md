# Journalism skill provenance

Four installed skills are adapted from
[Joe Amditis's claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism)
under the MIT licence, pinned at commit
`2097d218c6f38a8e7be77ce5f0ff6c2e39671f13`.
Their upstream paths are `journalism-core/skills/<id>/`.

| Skill | Local adaptation |
|---|---|
| `foia-requests` | Explicit US scope; statute tables and tracker moved to `reference.md`; deadline calculation corrected to count business days. |
| `interview-prep` | Recording-consent guidance identifies its US scope and flags other jurisdictions. |
| `story-pitch` | Mycroft integration and attribution. |
| `ai-writing-detox` | Optional upstream hook identified as harness-dependent; style guidance distinguished from universal rules. |

Each skill retains attribution frontmatter and a Credits section. See
[NOTICE.md](../NOTICE.md) for the notice and [skills.manifest](../skills.manifest)
for the installed set. The website shows three of these skills; writing cleanup
remains installed but is not featured.

`photo-metadata` was part of an earlier selection and is no longer shipped.
The earlier selection notes and Goose-specific integration checklists remain
in version history, not in the current setup documentation.

The fact-checking card is a separate, archived Mycroft method reference credited
to Verso and Buried Signals. It is not an Amditis skill and is not installed.
Its pinned source is in [featured-skills.json](../catalog/featured-skills.json).
