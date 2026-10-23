#!/usr/bin/env python3
"""Checks tools/wiki-service.py (Mycroft's one way to call `bsig wiki`) and
that recipes and skills route wiki reads through it consistently.

Runs the tool against a fake `bsig` on PATH that records its argv and stdin.
"""

import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "wiki-service.py"
FAKE_BSIG = """#!/bin/sh
printf '%s\\n' "$@" > "$FAKE_LOG.argv"
cat > "$FAKE_LOG.stdin"
if [ -n "$FAKE_UNKNOWN" ]; then echo 'error: unknown verb "wiki"' >&2; exit 4; fi
echo '{"event":"result","message":"wiki search","data":{"result":{"hits":[]},"tool":"search"}}'
"""

failures = []


def check(name, ok, detail=""):
    if not ok:
        failures.append(f"{name}: {detail}")


def run(tmp, request, verb="search", env_extra=None):
    env = dict(os.environ, PATH=f"{tmp}/bin:/usr/bin:/bin", FAKE_LOG=f"{tmp}/log", HOME=f"{tmp}/home")
    env.update(env_extra or {})
    for suffix in (".argv", ".stdin"):
        pathlib.Path(f"{tmp}/log{suffix}").unlink(missing_ok=True)
    body = request if isinstance(request, str) else json.dumps(request)
    return subprocess.run([sys.executable, "-I", str(TOOL), verb], input=body, capture_output=True, text=True, env=env, timeout=60)


def failure_id(proc):
    try:
        return json.loads(proc.stdout.splitlines()[0])["data"]["failure"]["id"]
    except (IndexError, KeyError, json.JSONDecodeError):
        return None


with tempfile.TemporaryDirectory() as raw:
    tmp = os.path.realpath(raw)
    os.makedirs(f"{tmp}/bin")
    os.makedirs(f"{tmp}/home")
    pathlib.Path(f"{tmp}/bin/bsig").write_text(FAKE_BSIG)
    os.chmod(f"{tmp}/bin/bsig", 0o755)
    wiki = f"{tmp}/wiki"
    os.makedirs(f"{wiki}/.ok")
    pathlib.Path(f"{wiki}/.ok/config.yml").write_text("")
    os.makedirs(f"{wiki}/mycroft/deep")
    os.symlink(f"{wiki}/mycroft", f"{tmp}/vault-link")

    # The wiki root is the nearest .ok project above the vault, symlinks
    # resolved, passed as --workspace; the args reach bsig on stdin as given.
    hostile = 'acme"; $(touch ' + tmp + '/pwned) `id` \'quote'
    proc = run(tmp, {"vault_path": f"{tmp}/vault-link/deep", "args": {"query": hostile}})
    argv = pathlib.Path(f"{tmp}/log.argv").read_text().split("\n") if proc.returncode == 0 else []
    check("root found", proc.returncode == 0 and argv[:6] == ["--json", "wiki", "search", "--workspace", wiki, ""], f"rc={proc.returncode} argv={argv} out={proc.stdout}{proc.stderr}")
    check("args on stdin", proc.returncode == 0 and json.loads(pathlib.Path(f"{tmp}/log.stdin").read_text()) == {"query": hostile}, "stdin differs")
    check("no shell expansion", not os.path.exists(f"{tmp}/pwned"), "a command in the query ran")
    check("result passed through", '"event":"result"' in proc.stdout, proc.stdout)

    # Without vault_path, bsig uses the workspace Engine recorded.
    proc = run(tmp, {"args": {"name": "Acme", "type": "company"}}, verb="resolve")
    argv = pathlib.Path(f"{tmp}/log.argv").read_text().split("\n")
    check("recorded workspace", "--workspace" not in argv, f"argv={argv}")

    # Refusals before bsig runs.
    for name, request in {
        "relative path": {"vault_path": "Documents/Mycroft"},
        "dot": {"vault_path": "."},
        "empty": {"vault_path": ""},
        "missing folder": {"vault_path": f"{tmp}/nowhere"},
        "newline": {"vault_path": f"{wiki}/mycroft\nWIKI_ARGS"},
        "no project above": {"vault_path": f"{tmp}/bin"},
        "not JSON": "vault_path=/x",
    }.items():
        proc = run(tmp, request)
        check(f"refuses {name}", proc.returncode == 2 and not os.path.exists(f"{tmp}/log.argv"), f"rc={proc.returncode} out={proc.stdout}")

    # A project rooted at the home folder is the whole home: refused.
    os.makedirs(f"{tmp}/home/.ok", exist_ok=True)
    pathlib.Path(f"{tmp}/home/.ok/config.yml").write_text("")
    os.makedirs(f"{tmp}/home/Documents/Mycroft", exist_ok=True)
    proc = run(tmp, {"vault_path": f"{tmp}/home/Documents/Mycroft"})
    check("refuses the home folder", proc.returncode == 2 and failure_id(proc) == "wiki-root", f"rc={proc.returncode} out={proc.stdout}")

    # An Engine without the wiki service is reported as such.
    proc = run(tmp, {"vault_path": f"{wiki}/mycroft"}, env_extra={"FAKE_UNKNOWN": "1"})
    check("older Engine", proc.returncode == 3 and failure_id(proc) == "wiki-service-unavailable", f"rc={proc.returncode} out={proc.stdout}")

    # ok-audit runs OpenKnowledge's audit on the same root, with no shell.
    pathlib.Path(f"{tmp}/bin/ok").write_text('#!/bin/sh\nprintf \'%s\\n\' "$@" > "$FAKE_LOG.argv"\necho \'{"files":[]}\'\n')
    os.chmod(f"{tmp}/bin/ok", 0o755)
    proc = run(tmp, {"vault_path": f"{wiki}/mycroft"}, verb="ok-audit")
    argv = pathlib.Path(f"{tmp}/log.argv").read_text().split("\n") if os.path.exists(f"{tmp}/log.argv") else []
    check("ok-audit", proc.returncode == 0 and argv[:4] == ["--cwd", wiki, "audit", "--json"], f"rc={proc.returncode} argv={argv}")

# A recipe's vault_path is a template value: it must never sit inside shell
# source (an inline command such as root="{{ vault_path }}" or
# ok --cwd "{{ vault_path }}"), where a crafted value would run. It travels
# in the wiki tool's JSON on stdin, or as a YAML argv entry.
SHELLISH = ('="', "$(", "--cwd", ";", "cd ", "| ", "while ")
for path in sorted(list((ROOT / "recipes").glob("*.yaml")) + list((ROOT / "skills").glob("*/SKILL.md"))):
    for span in re.findall(r"`([^`\n]*)`", path.read_text()):
        if re.search(r"\{\{\s*vault_path\s*\}\}", span) and any(marker in span for marker in SHELLISH):
            check(f"{path.relative_to(ROOT)} vault_path in shell", False, span)

# Recipes and skills that read through the wiki service must not also call
# OpenKnowledge the primary wiki interface, and must not hand bsig wiki
# values on its command line.
for path in sorted(list((ROOT / "recipes").glob("*.yaml")) + list((ROOT / "skills").glob("*/SKILL.md"))):
    text = path.read_text()
    if "wiki-service.py" not in text:
        continue
    lowered = text.lower()
    for phrase in ("openknowledge as the primary", "primary wiki interface", "use openknowledge as the primary interface"):
        check(f"{path.relative_to(ROOT)} consistent", phrase not in lowered, f"says {phrase!r} but reads through wiki-service.py")
    check(f"{path.relative_to(ROOT)} no direct bsig wiki", "bsig --json wiki " not in text, "calls bsig wiki directly instead of tools/wiki-service.py")

if failures:
    print("wiki-service checks FAILED:")
    for failure in failures:
        print("  -", failure)
    sys.exit(1)
print("wiki-service checks passed")
