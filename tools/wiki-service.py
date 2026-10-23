#!/usr/bin/env python3
"""wiki-service.py — Mycroft's one way to call the Engine wiki service.

    python3 "$MYCROFT_DIR/tools/wiki-service.py" search <<'WIKI_ARGS'
    {"vault_path": "/Users/me/Documents/OpenKnowledge/Mycroft", "args": {"query": "..."}}
    WIKI_ARGS

Verbs: search, read, resolve, check (`bsig wiki`'s read-only tools), and
ok-audit (`ok --cwd <wiki root> audit --json`, OpenKnowledge's broken-link
audit; needs "vault_path").

Everything a recipe knows (the vault path, the query, a name, a claim)
travels on stdin as one JSON object inside a quoted heredoc, so no value is
ever part of shell source. This tool then:

- with "vault_path": requires an absolute, existing folder, resolves it
  (symlinks included), and walks up to the nearest folder holding
  `.ok/config.yml`, which is how OpenKnowledge finds its project. It refuses
  when there is none, and when that folder is the filesystem root or the
  home folder: a wiki rooted there would be the whole disk or home. The
  folder is passed to bsig as --workspace, so the wiki service and
  OpenKnowledge read the same wiki.
- without "vault_path": gives no --workspace, and bsig uses the workspace
  Engine recorded for Mycroft.
- sends "args" to `bsig --json wiki <verb>` on stdin and prints bsig's
  NDJSON as it is: the answer is `data.result` on the "event":"result" line.

Its own refusals are one NDJSON error line, `data.failure.id` being
`wiki-root` (exit 2) or, on an Engine without the wiki service,
`wiki-service-unavailable` (exit 3).
"""

import json
import os
import subprocess
import sys

VERBS = ("search", "read", "resolve", "check", "ok-audit")


def refuse(failure_id, message, code):
    print(json.dumps({"event": "error", "message": message, "data": {"failure": {"id": failure_id}}}))
    sys.exit(code)


def wiki_root(vault_path):
    if not isinstance(vault_path, str) or not vault_path or "\n" in vault_path or "\x00" in vault_path:
        refuse("wiki-root", "vault_path must be one absolute folder path", 2)
    if not os.path.isabs(vault_path):
        refuse("wiki-root", "vault_path is not an absolute path", 2)
    if not os.path.isdir(vault_path):
        refuse("wiki-root", "vault_path is not an existing folder", 2)
    root = os.path.realpath(vault_path)
    while not os.path.isfile(os.path.join(root, ".ok", "config.yml")):
        parent = os.path.dirname(root)
        if parent == root:
            refuse("wiki-root", "no OpenKnowledge project (.ok/config.yml) at or above vault_path", 2)
        root = parent
    home = os.path.realpath(os.path.expanduser("~"))
    if root == os.path.realpath(os.sep) or root == home:
        refuse("wiki-root", "the wiki root found is the filesystem root or the home folder; refusing to search it", 2)
    return root


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in VERBS:
        refuse("usage", "usage: wiki-service.py search|read|resolve|check, JSON on stdin", 2)
    verb = sys.argv[1]
    try:
        request = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except json.JSONDecodeError as exc:
        refuse("usage", f"stdin is not one JSON object: {exc}", 2)
    if not isinstance(request, dict):
        refuse("usage", "stdin is not one JSON object", 2)
    args = request.get("args", {})
    if not isinstance(args, dict):
        refuse("usage", '"args" must be a JSON object', 2)
    if verb == "ok-audit":
        if "vault_path" not in request:
            refuse("usage", "ok-audit needs vault_path", 2)
        try:
            proc = subprocess.run(["ok", "--cwd", wiki_root(request["vault_path"]), "audit", "--json"], capture_output=True, text=True, timeout=300)
        except FileNotFoundError:
            refuse("openknowledge-unavailable", "ok (OpenKnowledge) is not installed", 3)
        except subprocess.TimeoutExpired:
            refuse("openknowledge-timeout", "ok audit did not answer within 300 s", 3)
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    command = ["bsig", "--json", "wiki", verb]
    if "vault_path" in request:
        command += ["--workspace", wiki_root(request["vault_path"])]
    try:
        proc = subprocess.run(command, input=json.dumps(args), capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        refuse("wiki-service-unavailable", "bsig is not installed", 3)
    except subprocess.TimeoutExpired:
        refuse("wiki-service-timeout", "bsig wiki did not answer within 120 s", 3)
    if "unknown verb" in proc.stdout + proc.stderr:
        refuse("wiki-service-unavailable", "this Engine has no wiki service (bsig wiki)", 3)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
