---
name: shell-safety
description: Safe command construction for Mycroft skills and recipes. Use before any shell call that includes user, model, scraped, config, filesystem, or generated values; validates URLs, DOI identifiers, paths, timestamps, filenames, and destructive-operation probes.
version: "1.0"
invocable_by: [recipe, skill, user]
---

# Shell Safety

Use this skill before any shell operation that includes data from a user, model, scraped page, email body, social post, config file, filesystem path, or generated note.

Mycroft is an ambient assistant. Inbound material — AgentMail subjects, scraped articles, social posts, model output — is **untrusted input** by definition. A backtick in an email subject, `$(...)` in a tweet, or an unescaped quote in scraped markdown can break out of an unsafe shell command.

## Non-Negotiable Rules

1. Do not build shell commands by interpolating untrusted strings.
2. Prefer helper scripts that receive arguments as argv, stdin, environment variables, temp files, or structured JSON.
3. Validate values before command construction.
4. Do not let user input select flags, command separators, shell operators, or output paths outside the allowed base directory.
5. Treat copy, move, overwrite, delete, archive extraction, and lock cleanup as destructive.

## Validation Helper

Use `scripts/mycroft_safe.py` for reusable validation:

```text
python3 scripts/mycroft_safe.py validate-url "<url>"
python3 scripts/mycroft_safe.py validate-doi "<doi>"
python3 scripts/mycroft_safe.py resolve-path --base "<allowed-base>" --path "<candidate>"
python3 scripts/mycroft_safe.py destructive-probe --base "<allowed-base>" --path "<candidate>"
```

The helper rejects shell metacharacters in identifiers, invalid URL schemes, path traversal outside the allowed base, leading-dash path segments, NUL bytes, and unsafe destructive targets.

## Curl Guidance

Do not write examples like:

```text
curl "https://example.test?q={user_query}"
```

Use one of these instead:

- `curl --get --data-urlencode "q=<value>" https://example.test/search`
- a Python helper that serializes JSON with `json.dumps`
- a temp JSON file passed as `--data @file.json`

## CLI Argument Guidance

When passing untrusted strings as CLI arguments (e.g. `obsidian create ... content="<scraped markdown>"`), the shell still expands `$`, backticks, and quotes inside the double-quoted argument. Prefer:

- stdin: `printf '%s' "$content" | tool --content-stdin`
- temp file: `tool --content-file /tmp/note-<uuid>.md` (after validating the path with `resolve-path`)
- env var: `MYCROFT_CONTENT="$content" tool --content-env MYCROFT_CONTENT`

If the downstream tool only accepts a single quoted argument, the calling code must reject any value containing `\x00\r\n` `` ` `` `$;&|<>` before invocation — or document the tool as a known weak link.

## Destructive Operations

Before destructive work:

1. Resolve paths.
2. Confirm every path is inside the expected base.
3. Run `destructive-probe` or an equivalent non-destructive probe using the same resolved arguments.
4. Record the probe output.
5. Run the real operation only after the probe is inspected.
6. Record the real operation in the run log or evidence bundle.

Never provide one-shot destructive commands in skill or recipe instructions.

## Drift With Spotlight

This helper is mirrored from `spotlight_safe.py` in the Spotlight skill bundle. The two are functionally equivalent; bundles are kept separate so each public install (`spotlight@buriedsignals`, mycroft Goose pack) is self-contained. When the spotlight version changes, port the diff manually.
