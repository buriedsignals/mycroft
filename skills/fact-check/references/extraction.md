# Claim extraction — find every claim before you verify anything

> Adapted from Big If True by Verso (verso.ink/big-if-true).

These are the complete extraction rules for step 1 of a Mycroft fact-check.
Your entire job in this step is the claims file these rules describe.
Verification is out of scope until the file is written.

The goal is the complete, source-ordered list of atomic, externally checkable
factual claims. **Completeness is the top priority: a missed fact is a
failure; one extra small claim is not.**

**Write the extraction down before you verify anything.** Create
`claims.md` in the fact-check package directory and work through the text
one paragraph at a time, writing each paragraph's claims, anchored to their
exact quotes, before moving to the next. If a paragraph yields nothing,
write "no checkable claims" under its heading. This is not bookkeeping:
extraction done mentally gets silently compressed by the pull toward
verification, because every claim feels like a future search to pay for.
Writing the list first, with verification out of scope, is what keeps the
sweep honest. Extraction is cheap, and in verification one good search
typically serves a whole cluster of claims, so a far larger claim list costs
only modestly more retrieval. Never drop a claim at extraction time because
it seems minor, obvious, or expensive to check.

**Keep a discard log.** When you pass over a sentence as unextractable, note
it in the claims file with a one-word reason: *opinion*, *prediction without
factual content*, *rhetorical*, *hypothetical*. A silent skip is invisible;
a logged skip can be audited. Most extraction failures are not misjudged
sentences but sentences never consciously judged at all.

- **Atomic, because bundles launder errors.** Split compound statements so
  each claim carries exactly one checkable fact, keeping its material
  qualifiers and conditions. A sentence citing three numbers is three
  claims; role + name, date + place, claim + magnitude split the same way.
  The reason is verdict resolution, not tidiness: a bundle gets one verdict,
  so a wrong figure rides along with two right ones and the whole thing is
  waved through as "roughly accurate". Split, the wrong part is isolated and
  named while its neighbours are cleared.
- **Self-contained.** Resolve pronouns with the minimum needed name so each
  claim stands alone. Preserve exact names, numbers, units, and quotations.
- **Attribution vs. substance.** Create an attribution claim for every
  quotation or attributed statement (said, announced, denied, believed,
  feared, expected, alleged): the claim is that X said it. Do not turn the
  object of a belief, fear, expectation, allegation, warning, hope, plan, or
  promise into a substantive fact unless the text independently asserts it
  as fact. Tag each claim `[attribution]` or `[fact]` as you extract.
- **Genre check: whose voice carries the text?** The attribution rule
  exists for reported pieces, where the article's own voice relays what
  third parties say. In an interview, op-ed, column, or first-person essay,
  the speaker's factual assertions ARE the text's substance: the reader
  takes them as claims about the world, and they get `[fact]` treatment. In
  those genres the attribution rule applies one level down, to what the
  speaker attributes to others (a study, a paper, a named person). An
  interview handled under the reported-piece rule collapses into almost
  nothing checkable. That is the single largest source of missed claims.
- **Extract these; they are where the errors live.** Classes that feel
  skippable but consistently produce findings:
  - *Quantified generalisations*: "almost every", "all", "nobody", "always".
    Checkable against data, and often the text's weakest claims.
  - *Absolutes doing argumentative work*: "every article ever written is in
    there". A literally false absolute matters precisely because the
    argument leans on its scale.
  - *Definitions*: "X is called Y", "X means Z". A wrong definition
    misinforms as effectively as a wrong number.
  - *Hedged speculation*: "the supposition is that…", "could have…". Extract
    it with the hedge preserved in the claim text; the verdict may well be
    `unverified`, and an unverifiable link presented as the likely
    explanation is itself worth surfacing.
  - *Claims inside questions*: an interviewer's premises (a film's plot, a
    study's setup, "a rumour arose that…") are asserted to the reader too.
  - *Background and common-knowledge facts*: cheap to verify, and their
    presence in the list is what proves the sweep was complete.
- **Identity facts in passing.** "Company spokesperson Maria Chen" claims
  that Maria Chen is a company spokesperson. Extract it.
- **The user's framing never narrows extraction.** A request to "check the
  predictions" or "focus on the numbers" shapes which findings you emphasise
  in the summary. It does not shrink the extraction. Extraction is
  framing-invariant: the same text always yields the same list.
- **The article's apparatus isn't claims.** Byline, author title, dateline,
  timestamps, outlet name, section labels, photo credits, "updated" notes:
  these describe the article, not the world. Capture the byline and date as
  manifest metadata; never extract or verify them.
- **Source order, no duplicates, no outside knowledge, no verifying yet.**

One sentence, two claims:

> "The plant opened in 1998 and employs 1,200 people."
> → [fact] The plant opened in 1998.
> → [fact] The plant employs 1,200 people.

A quotation, and the role fact stated in passing:

> "“We never tested this product on animals,” said Orion Labs
> spokesperson Dana Reyes."
> → [attribution] Orion Labs spokesperson Dana Reyes said the company never
>   tested the product on animals.
> → [fact] Dana Reyes is a spokesperson for Orion Labs.

Three numbers, three claims, and why it matters:

> "Group A scored 74 percent, group B 76 percent, and the model 95
> percent."
> → three separate claims. If the study actually reported 74 / 76 / 90, the
> split isolates one clean `mischaracterized` on the 95 while the others
> are `verified`. Bundled, the likely verdict is a single soft "numbers are
> roughly right", and the one real error never surfaces.

Keep each claim together with the exact phrase of the text that asserts it;
that phrase becomes `claim_text`'s anchor and lets an editor find the passage.

**Audit by density, not by re-reading.** A re-read by the mind that just
pruned tends to confirm the pruning. Check the numbers instead: thorough
extraction of assertive news and interview prose runs about one claim per
12 to 15 words. A 1,000-word news piece is an 80-claim text, not a 40-claim
text. Run the gate before verifying:

```sh
python3 "$MYCROFT_DIR/tools/claim-density.py" <draft file> <claim count>
```

Above 20 words per claim it exits 1 and tells you to reopen extraction:
re-walk the paragraphs with the fewest claims, discard log in hand, and ask
of each skipped sentence: is there a quantifier, a definition, a premise, or
an absolute in here? For a genuinely thin text (heavy rhetoric, lists,
captions) say why in the manifest notes and proceed.
