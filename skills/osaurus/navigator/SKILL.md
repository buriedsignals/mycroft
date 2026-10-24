---
name: navigator
description: Find OSINT tools and techniques with Navigator's tools in Osaurus. Use when the member needs a tool or method for domains, usernames, images, maps, archives, networks, verification, geolocation, company intelligence or country-specific research.
version: 1.0.0
author: Buried Signals
---

# Navigator

Navigator finds the right investigative tool or technique from thousands of community-curated OSINT tools. Use it for a technique or service you don't already know. It doesn't replace reading sources, records or the member's wiki.

Osaurus asks the member before Navigator calls. If Navigator isn't connected, tell the member to sign in to Navigator when Osaurus asks, then try again. Never ask for a token.

## Which tool

1. `navigator_search_tools` first. Pass the member's need in plain words, for example "company registry Norway" or "reverse image search for faces".
2. `navigator_search_tool_documentation` with a `tool_id` from those results, when the member wants to use one tool and needs its steps or limits.
3. `navigator_query` only when the member asks how to approach a task and wants a written method, not a list of tools. Pass `skip_cache: true` when the member wants a fresh answer or is refining an earlier one.

Don't call the same tool twice with the same query. If the results don't fit, rephrase once with more specific words.

## Answering

- Name each tool, what it does for this case, and its URL.
- Say what the tool can't do when its documentation lists limits.
- Keep the tool id with any tool the member decides to use, so it can be found again.
- A Navigator result is a pointer to a tool, not evidence. Findings still need their own source.
