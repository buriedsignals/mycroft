---
name: fact-check
description: Fact-check a draft, a claim or a citation in Osaurus. Use when the member asks to verify reporting, check a source assertion or stress-test a story before publication. Lists every checkable claim, checks each against the member's wiki and the documents they supply, and says where the original record is for the rest.
version: 1.0.0
author: Buried Signals
attribution: "Claim extraction and evidence routes adapted from Big If True by Verso (verso.ink/big-if-true, MIT, Verso Lab LLC). Osaurus edition of Mycroft's fact-check skill by Buried Signals."
---

# Fact-checking

Use this skill when the member asks to verify reporting, inspect a citation or source assertion, or stress-test a story or draft before publication. Don't use it for software, engineering plans or security reviews.

## What you can and cannot check here

In Osaurus you have the member's wiki (`wiki_search`, `wiki_read`, `wiki_resolve_entity`), document extraction (`wiki_extract_document`, when listed) and what the member pastes into the chat. You have no web search, no browser and no shell.

So this skill does three things:

1. **Finds every checkable claim** in the text.
2. **Checks each claim against evidence you can actually read**: wiki notes, documents the member points you to, text they paste.
3. **Says where the original record is** for every claim you could not check, so the member or Spotlight can check it.

Never say you looked something up on the web. A claim you could not check is `unverified`, with the place to check it. For live web verification, source contact or image and video forensics, tell the member to run a Spotlight investigation.

## Method

### 1. Extract every claim first

Follow `references/extraction.md` before you check anything. Write the claim list in your reply, paragraph by paragraph, each claim anchored to the exact phrase that asserts it.

Each claim carries one checkable fact. A sentence with a name, a role and a date is three claims. A bundle gets one verdict, so a wrong figure rides along with two right ones; split, the wrong part is isolated and named.

State the draft's word count and your claim count. Above 20 words per claim, go back through the paragraphs with the fewest claims.

### 2. Search the wiki

For each claim, search the member's wiki for the people, organisations, figures and dates it names, and resolve named entities with `wiki_resolve_entity`. A wiki note is prior knowledge, not proof: cite its path, say what it states, and follow it to the source it cites when the note gives one. If the wiki tools fail, say "wiki unavailable" and continue with what the member supplies.

### 3. Read what the member supplies

Ask for the document, page or transcript behind a claim when one would settle it. Read a scan, PDF or photo with `wiki_extract_document` when it is listed. Quote the passage that supports or contradicts the claim, word for word.

### 4. Point to the original record

For a claim you cannot check, name the body that produces the record and what to look for there. The route files say where:

| Claim is about | Route |
|---|---|
| Unemployment, prices, population, elections, crime, health | `references/routes/official-statistics.md` |
| Market prices, rates, debt, company financial figures | `references/routes/markets-economy.md` |
| Companies, ownership, filings, lawsuits, rulings | `references/routes/companies-courts.md` |
| What someone said, and whether they said it | `references/routes/quotes-attribution.md` |
| Studies, papers, what "the research shows" | `references/routes/science-studies.md` |
| Web pages, social posts, deleted or changed content | `references/routes/web-social-archives.md` |

The routes name commands from the full Mycroft fact-check. You cannot run them here. Use each route for the producing body, the method and the traps.

### 5. Give each claim a verdict

| Verdict | When |
|---|---|
| `verified` | Every element of the claim is stated by one definitive source (the official record itself: a register, filing, court or statistical release) or by two independent sources, and you read them |
| `partially_verified` | Part of the claim is supported and part is not; say which part. Prefer splitting the claim |
| `unverified` | You could not check it either way. This is not "false" |
| `contradicted` | A source you read states something incompatible; cite it |
| `mischaracterized` | The source exists but the claim misstates it: a wider scope, a changed figure or date, an added cause, an allegation stated as fact |

Count sources by site, not by page. Two pages of one site, or a page and its archived copy, are one source. Two outlets repeating the same wire report or press release are one source: trace the claim to its origin.

Every `verified`, `contradicted` or `mischaracterized` verdict quotes its evidence and cites a wiki note path or the document the member supplied. With no source, write exactly `not found in available sources`.

## What to hand back

One row per claim, in the order of the text:

| # | Claim | Verdict | Evidence (quote and where it is) | Where to check, if unverified |
|---|---|---|---|---|

Then three short lists: claims that need a correction, claims the member must check themselves and where, and sentences you set aside as opinion, prediction or rhetoric.

Tag confidence high, medium or low on each verdict. A verdict resting on one source that is not the official record is at most medium.

## Suspect images, video and audio

You cannot run detectors here. Tell the member what to do, in this order:

1. **Provenance first.** Check Content Credentials at `contentcredentials.org/verify`. A valid manifest from a known signer is strong evidence, not proof. No manifest proves nothing: most real media is unsigned, and screenshots and platforms strip manifests.
2. **Two detectors minimum.** One tool's verdict is not evidence. Agreement between two caps the claim at medium confidence; disagreement means escalate.
3. **Eye and ear are triage only.** Current synthetic media has lost the classic tells.
4. **Escalate** anything a story depends on to Spotlight.

## Right of response

A claim that rates a named person or organisation `contradicted` or `mischaracterized` is not ready to publish until the subject has been offered the chance to respond: state the exact claim and give a reasonable deadline (24 to 48 hours is a common newsroom norm; obligations vary by jurisdiction and outlet). This is a decision for the member and their editor.

## Corrections

When an error surfaces in a fact-check you already delivered or in a published piece:

| Situation | Action |
|---|---|
| Factual error | Correct immediately; add a dated correction note |
| Missing context | Add context; a formal correction is optional |
| New information | Update; mark "Updated: [date]" |
| Subject disputes characterisation | Re-check the claim; correct only if the re-check warrants it |

Correction note format: "Correction [date]: an earlier version stated [error]. In fact, [correct information]."

## Rules

- Don't rewrite the member's draft unless asked.
- Don't invent sources, quotes, figures, URLs or dates.
- Never request or record a confidential source's identity. If the member names one, flag it and suggest redaction.
- Separate what a source states from what you infer.

---

## Credits

Claim extraction, the density check and the evidence routes are adapted from [Big If True](https://verso.ink/big-if-true/) by Verso (MIT, Verso Lab LLC). The verdict rule "two independent sources agree, or one definitive source settles it" is Verso's.

Suspect-media triage, the right-of-response gate and the corrections table are adapted from Joe Amditis's `source-verification` and `fact-check-workflow` skills (jamditis/claude-skills-journalism, MIT).

Checking one assertion at a time and counting sources by site also follow: Wilde et al., *NewsBench* (<https://arxiv.org/html/2610.33240v1>); Qazi, McCrae and Nasir, *Adversarial Robustness of Retrieval-Based Fact-Checking* (<https://arxiv.org/html/2611.02139v1>); Zhao et al., *AttriSwarm* (<https://arxiv.org/html/2611.04504v1>).

This is the Osaurus edition. The full edition, which fetched and stored evidence through a shell, is in this repository's history at commit `30434172`.
