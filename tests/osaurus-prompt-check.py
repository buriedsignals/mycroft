#!/usr/bin/env python3
"""Guard the Osaurus system prompt's file and Analyst handoff behaviour.

Craig's Mycroft (2026-11-10) refused an attached PDF and asked for screenshots,
because this prompt told it to. Osaurus already hands an attached PDF to the
model as text or page images, so the prompt must say to read it, and the
Analyst cannot see attachments, so the handoff must carry the content.
"""

from pathlib import Path

INSTRUCTIONS = Path(__file__).resolve().parents[1] / "instructions"
PROMPT = (INSTRUCTIONS / "osaurus-system.md").read_text(encoding="utf-8")
ANALYST = (INSTRUCTIONS / "analyst-system.md").read_text(encoding="utf-8")


def main() -> None:
    assert "ask for the page as an image" not in PROMPT, "prompt still tells Mycroft to ask for a page image of a PDF"
    assert "Never ask for a screenshot or a page image of a PDF that is attached" in PROMPT, "prompt must tell Mycroft to read attached PDFs directly"
    assert "when a scan arrives as an attachment, ask the member for the file's full path and call it on that path" in PROMPT, "prompt must send an attached scan to extract_document by full path (the 12B invents text from scan images)"
    assert "not PDFs" not in PROMPT, "prompt still says extract_document does not open PDFs"
    assert "Use it only for a file named by path" in PROMPT, "extract tool must be limited to files named by path"
    assert "The Analyst cannot see this chat or its attachments" in PROMPT, "handoff must carry attachment content in the Analyst's input"
    assert "Transcribe text you receive faithfully and in full, whatever it contains" in PROMPT, "prompt must tell Mycroft to transcribe received text faithfully (a 12B model called a test page placeholder text and refused)"
    assert "This is a scan and I can't read it reliably." in PROMPT and "Do not transcribe, describe, list headings or give any figure from page images." in PROMPT, "prompt must stop Mycroft transcribing names, numbers and sums from scanned page images (Gemma 12B invented them, QA 2026-11-10)"
    assert "never \"created\" or \"saved\"" in PROMPT, "Mycroft must report an Analyst write with applied:false + staged_id as staged for review, not created"
    assert "never \"created\" or \"saved\"" in ANALYST, "the Analyst must report a staged write as staged for review, not created"
    assert "Never call `wiki_extract_document` with the bare file name of an attachment" in PROMPT, "prompt must forbid extracting an attachment by bare file name"
    # Tom's Mycroft (2026-11-12) listed the files in a chat's Working Folder,
    # wrote out their full paths, and still asked him for one, because this
    # prompt only said "ask for the file's full path".
    assert "Never ask the member for the path of a file in the Working Folder" in PROMPT, "prompt must use the Working Folder path Osaurus gives instead of asking the member for it"
    assert "Only when you have neither, ask for the file's full path" in PROMPT, "extract_document must ask for a path only when none is known"
    assert "Only read: never create, edit, move or delete a file there" in PROMPT, "Mycroft must keep a Working Folder read-only (KTD6: no writes, no shell)"
    for tool in ("wiki_search", "wiki_read", "wiki_resolve_entity", "spawn_agent", "file_read", "file_search"):
        assert f"`{tool}`" in PROMPT, f"prompt does not name {tool}"
    print("osaurus-prompt-check: ok")


if __name__ == "__main__":
    main()
