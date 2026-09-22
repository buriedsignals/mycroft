#!/usr/bin/env python3
"""claim-density.py — the Pass 1 gate for Mycroft fact-checks.

    python3 "$MYCROFT_DIR/tools/claim-density.py" SOURCE.txt CLAIM_COUNT

Thorough extraction of assertive news and interview prose runs about one
claim per 12-15 words. Run this after writing the claims file and before
verifying anything: a thin list is cheapest to fix while a re-walk of the
text is still cheap. Exit 0 within the band, 1 when the list is too thin
(above 20 words per claim), 2 on bad input.

Scripts without word spaces (Chinese, Japanese, Thai, Khmer, Lao, Burmese)
would count as a handful of "words"; a CJK/Thai character counts as half a
word, the usual rough conversion.

Adapted from Big If True by Verso (verso.ink/big-if-true).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_NOSPACE = re.compile(
    r"[぀-ヿ㐀-䶿一-鿿豈-﫿ｦ-ﾟ"
    r"฀-๿຀-໿ក-៿က-႟]"
)

THOROUGH = (12, 15)   # words per claim of a thorough sweep
GATE = 20             # above this the list is thin: reopen Pass 1


def word_count(text: str) -> int:
    nospace = len(_NOSPACE.findall(text))
    rest = _NOSPACE.sub(" ", text)
    return len(rest.split()) + nospace // 2


def assess(words: int, claims: int) -> tuple[int, str]:
    if claims <= 0:
        return 1, f"density: {words} words, 0 claims. Reopen Pass 1: every paragraph gets a claim or a logged discard."
    wpc = round(words / claims)
    line = f"density: {wpc} words per claim ({words} words, {claims} claims)"
    if wpc > GATE:
        return 1, (f"{line}\nTHIN: above {GATE} words per claim. Re-walk the paragraphs with the fewest "
                   "claims, discard log in hand: quantifiers, definitions, premises, absolutes, identity "
                   "facts in passing. If the text is genuinely thin (lists, captions, rhetoric), say why "
                   "in the report's notes.")
    if wpc > THOROUGH[1]:
        return 0, f"{line}\nOK but light: thorough sweeps run {THOROUGH[0]}-{THOROUGH[1]}. Worth one more pass over the sparsest paragraphs."
    return 0, f"{line}\nOK: within the {THOROUGH[0]}-{THOROUGH[1]} words-per-claim band of thorough extraction."


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    try:
        text = Path(argv[1]).read_text(encoding="utf-8")
        claims = int(argv[2])
    except (OSError, ValueError) as exc:
        print(f"claim-density: {exc}", file=sys.stderr)
        return 2
    code, message = assess(word_count(text), claims)
    print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
