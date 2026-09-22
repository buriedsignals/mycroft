# Route: studies, papers and scientific claims

> Adapted from Big If True by Verso (verso.ink/big-if-true). "The browser" here means the `web-acquisition` skill; page fetches go through `mycroft-fetch`.


"A study found…" hides four separate claims: the study exists, it says
what the text says, it is the kind of study the text implies (peer
reviewed? preprint? industry-funded? on mice?), and the number quoted is
the study's number and not a press release's rounding of it.

## Find the paper

- `python3 "$MYCROFT_DIR/tools/evidence-lookup.py" crossref "title words or topic"` returns
  DOIs, journals, dates and authors. `evidence-lookup.py doi 10.xxxx/…` resolves
  a DOI the text or a press release gives.
- Medicine and life sciences: `evidence-lookup.py pubmed "query"` (PMIDs, open at
  pubmed.ncbi.nlm.nih.gov/PMID). Preprints: `evidence-lookup.py arxiv "query"`;
  bioRxiv/medRxiv via search or browser.
- Clinical trials: clinicaltrials.gov (registration, endpoints, sponsor)
  and the EU CTR. A trial's registered primary endpoint versus the one
  reported is a classic finding.
- Retractions: retractiondatabase.org (Retraction Watch; browser) and the
  Crossref record's `update-to` field. A retracted or corrected paper
  cited as live is mischaracterized.
- Nothing found in Crossref, PubMed or the preprint servers, and the
  outlet names no journal: the "study" may be a survey, a company white
  paper or a press release. Say so.

## Read the paper, not the coverage

- Open the paper (DOI link; the browser if the journal blocks fetch; the
  user's institutional login if they have one). Read the abstract, the
  methods paragraph, and the table the number comes from.
- Check: sample size and population, effect size with its interval,
  relative versus absolute risk ("doubles the risk" from 1 in 10,000 to
  2 in 10,000), correlation versus causation in the paper's own words,
  animal or in-vitro versus human, funding and conflict statements.
- Press releases (distribution services, university newsrooms) are the
  usual source of exaggeration; a claim that matches the release but
  not the paper is a finding.

## Expert quotes

- Confirm the person exists and holds the stated position (university
  page, ORCID at orcid.org, Google Scholar, `evidence-lookup.py wikidata`). "Scientists say" with no
  names is not checkable; note it.

## Official science and health bodies

- WHO, ECDC, CDC, EMA, FDA publish the record on their own sites;
  prefer them over coverage. Statistics: see official-statistics.md.

## Traps

- Journal names that mimic real ones; check the publisher and the ISSN
  in the Crossref record.
- Old studies presented as new; the Crossref date settles it.
- A meta-analysis and one of the studies inside it are not two sources.
