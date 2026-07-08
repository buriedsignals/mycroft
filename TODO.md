# TODO — bring the standalone installer's skill handling in line with the engine

**Status:** notes only (unstaged). Context: the Indicator Labs engine (`buriedsignals/engine`)
is now the canonical installer and ships a smarter way to make skills discoverable by Goose.
This repo's own `install/` path still uses the old approach and should be ported to match.

## The problem
`install/setup_server.py:build_skill_registry` writes `<profile>/skill-registry.json`, and
`install.sh` only *checks that it exists*. **Goose ignores `skill-registry.json`** — it
discovers skills by scanning `SKILL.md` files (recursively, no depth limit) under
`~/.agents/skills/`, `~/.agents/plugins/*/skills/`, project `.agents/skills/`, and builtins.
So a standalone `install.sh` of Mycroft leaves Goose with **none** of these skills available
(the exact bug the engine hit and fixed in the field).

## The fix (port from the engine — smarter system)
Make the enabled skills discoverable by **symlinking them into a per-product namespace**:

- For each enabled skill, create `~/.agents/skills/mycroft/<id>` → the skill's source dir
  (`~/.local/share/goose/mycroft/source/skills/<id>`, and the Spotlight cross-over skills
  from `~/.local/share/spotlight/skills/<id>`).
- Create `~/.agents/skills/mycroft/` (a per-product subdir) — not flat at the top level — so:
  the engine never collides with the user's own skills; it's one `.gitignore` entry when
  `~/.agents/skills` is a symlink into a repo (a common dev setup); and uninstall removes it
  as a single unit.
- Skip a name already occupied by foreign content (don't clobber).
- Keep `skill-registry.json` only if some other legacy consumer still reads it; it is inert
  for Goose discovery.

## Reference implementation (engine, commit `cce76bbf`)
- `internal/products/mycroft/module.go` → `skillSymlinkSteps` (the symlink + dir steps).
- `internal/products/mycroft/skill_registry.go` → `curatedSkills` (the enabled set: 7 mycroft
  skills, obsidian gated; + 7 Spotlight cross-overs when present).
- `internal/doctor/checks.go` → `CheckSkillsRegistered` (verifies each link resolves to a SKILL.md).
- Uninstall removes the `~/.agents/skills/mycroft/` dir + links (engine widens the owned-roots
  for it).

## Verify
`goose skills list` should show the Mycroft skills resolving under `~/.agents/skills/mycroft/`
after a standalone install; uninstall removes them.
