---
name: Bug report
about: Report a bug in Mycroft
labels: bug
---

**What happened**
<!-- What did you expect to happen, and what actually happened? -->

**Reproduce**
<!--
Steps to trigger the bug. Include the recipe, the command, or the page URL.
For setup.html bugs: attach (or redact) the generated mycroft-setup.command excerpt.
-->

**Environment**
- macOS / Linux version:
- Goose version: `goose --version`
- Mycroft commit: `(cd ~/.mycroft && git rev-parse --short HEAD)`
- Provider(s) configured: Fireworks / Together / Goose Local Inference (built-in llama.cpp) / other
- Sovereignty mode: cloud / local

**Logs / output**
```
<!-- Paste any terminal output, error messages, or failing recipe output here. Redact API keys. -->
```

**Security-sensitive?**
If this bug touches API key handling, vault contents, or source identity leaks, **stop** — email buriedsignals@agentmail.com instead. Don't open a public issue.
