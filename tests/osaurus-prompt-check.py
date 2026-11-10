#!/usr/bin/env python3
"""Guard the Osaurus system prompt's file and Analyst handoff behaviour.

Craig's Mycroft (2026-11-10) refused an attached PDF and asked for screenshots,
because this prompt told it to. Osaurus already hands an attached PDF to the
model as text or page images, so the prompt must say to read it, and the
Analyst cannot see attachments, so the handoff must carry the content.
"""

from pathlib import Path

PROMPT = (Path(__file__).resolve().parents[1] / "instructions" / "osaurus-system.md").read_text(encoding="utf-8")


def main() -> None:
    assert "ask for the page as an image" not in PROMPT, "prompt still tells Mycroft to ask for a page image of a PDF"
    assert "Never ask for a screenshot or a page image of a PDF that is attached" in PROMPT, "prompt must tell Mycroft to read attached PDFs directly"
    assert "Use it only for a file named by path" in PROMPT, "extract tool must be limited to files named by path"
    assert "The Analyst cannot see this chat or its attachments" in PROMPT, "handoff must carry attachment content in the Analyst's input"
    for tool in ("wiki_search", "wiki_read", "wiki_resolve_entity", "spawn_agent"):
        assert f"`{tool}`" in PROMPT, f"prompt does not name {tool}"
    print("osaurus-prompt-check: ok")


if __name__ == "__main__":
    main()
