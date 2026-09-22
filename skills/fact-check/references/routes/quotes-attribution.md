# Route: quotes and attribution

> Adapted from Big If True by Verso (verso.ink/big-if-true). "The browser" here means the `web-acquisition` skill; page fetches go through `mycroft-fetch`.


"X said Y" is the most common claim type and the most often garbled:
words tightened, context dropped, the wrong venue, the wrong date, or a
line that was never said. The verdict has two parts and both need
settling: were these words said (or written), and by this person in
this setting?

## Where the record is

Go to the recording or transcript, not to other outlets quoting it
(the independence rule in the fact-check the fact-check SKILL.md sets the bar). When it stays
unverified, name the recording or notes that would settle it.

| Speaker / setting | Primary record |
|---|---|
| US president, White House | whitehouse.gov/briefings-statements (transcripts); the public-affairs video archive of proceedings, searchable and timestamped |
| US Congress hearings, floor | congress.gov (Congressional Record), committee video channels |
| Federal Reserve | federalreserve.gov/newsevents (speeches with full text, press-conference transcripts) |
| US Treasury, agencies | home.treasury.gov/news, the agency's newsroom |
| UK Parliament | hansard.parliament.uk (searchable, same day); parliamentlive.tv |
| UK government | gov.uk/government/speeches |
| EU institutions | ec.europa.eu/commission/presscorner; ecb.europa.eu/press (speeches, press conferences, verbatim) |
| Other parliaments | most publish verbatim records: Bundestag (dip.bundestag.de), Assemblée nationale (assemblee-nationale.fr/dyn/comptes-rendus), Diet (kokkai.ndl.go.jp), Lok Sabha (sansad.in) |
| Central banks, ministries elsewhere | the institution's own site, in its language; search in that language |
| Court statements | the opinion or docket (see companies-courts.md) |
| Company executives | earnings-call transcripts (the company's IR page; SEC 8-K exhibits via `evidence-lookup.py edgar`), press releases |
| Social media posts | see web-social-archives.md — the post itself, or its archive |
| Donald Trump on Truth Social | trumpstruth.org (searchable archive); proves a post exists, never that it is true |
| TV and radio interviews | the broadcaster's own clip or transcript page; the browser is usually needed |
| Podcasts, YouTube | the episode, opened in the browser, at the timestamp |
| Analyst notes, research reports | not public; the quote rests on the reporter — unverified, say so plainly |
| Interviews conducted by the reporter | rest on the reporter — unverified, say so plainly |

## Method

1. Search the exact quoted words, in quotation marks, plus the name.
   Then search a distinctive four-word fragment — paraphrase drifts at the
   edges and a fragment survives it.
2. When the record is found, read around the quote: was it hedged,
   conditional, a question, or a quote of someone else? Cut context is a
   mischaracterized finding even when the words are exact.
3. Match the setting: the text's venue, date and format ("told reporters",
   "in a television interview", "wrote in a note", "said on X")
   are claims too. A right quote in the wrong venue is a finding.
4. Titles and affiliations are separate claims, checked against the
   person's own record — their page at the institution, their bio,
   `evidence-lookup.py wikidata "name"` for a first fix, LinkedIn as a last
   resort — never by whether other outlets repeat the label. A current
   affiliation the text leaves out, or a former title stated as current,
   is a finding when it changes how a reader would weigh the quote. A
   past role, a fellowship, a board seat, or a loose field label
   ("economist", "analyst") is not.
5. Translated quotes: find the original-language record and judge the
   translation, not the English retelling.

## Traps

- Quote-aggregator sites are not evidence.
- A transcript from a third party is weaker than the institution's own;
  say which you used.
- "Said last week" with no venue: find the venue first, then the words.
