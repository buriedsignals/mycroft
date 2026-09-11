#!/usr/bin/env python3
"""Validate the landing-page skills index's canonical metadata inputs."""

from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---(?:\s*\n|$)", text, re.DOTALL)
    assert match, f"{path}: missing YAML frontmatter"
    data = yaml.safe_load(match.group(1))
    assert isinstance(data, dict), f"{path}: frontmatter must be a mapping"
    return data


def main() -> None:
    skill_ids = [
        line.strip()
        for line in (ROOT / "skills.manifest").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert skill_ids, "skills.manifest is empty"
    assert len(skill_ids) == len(set(skill_ids)), "skills.manifest contains duplicate IDs"

    for skill_id in skill_ids:
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]*", skill_id), f"invalid skill ID: {skill_id}"
        path = ROOT / "skills" / skill_id / "SKILL.md"
        assert path.is_file(), f"missing skill file: {path}"
        data = frontmatter(path)
        assert data.get("name") == skill_id, f"{path}: name must match skills.manifest"
        description = data.get("description")
        assert isinstance(description, str) and description.strip(), f"{path}: description is required"
        description_line = re.search(r"^description:\s*(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
        assert description_line, f"{path}: description must be a single-line scalar for the website"
        assert re.search(r"^#\s+\S", path.read_text(encoding="utf-8"), re.MULTILINE), (
            f"{path}: a display heading is required for the website"
        )

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'data-dialog="dlg-skills"' in html, "skills-index trigger is missing"
    assert 'id="dlg-skills"' in html, "skills-index dialog is missing"
    assert "fetch('skills.manifest')" in html, "skills index must use skills.manifest"
    assert "fetch('skills/' + skillId + '/SKILL.md')" in html, "skills index must read SKILL.md metadata"
    assert "21 journalism skills" not in html, "hard-coded stale skill count remains"

    print(f"skills index: OK ({len(skill_ids)} skills)")


if __name__ == "__main__":
    main()
