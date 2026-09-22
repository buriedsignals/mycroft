# Route: companies, filings and courts

> Adapted from Big If True by Verso (verso.ink/big-if-true). "The browser" here means the `web-acquisition` skill; page fetches go through `mycroft-fetch`.


Who owns what, who earned what, who was charged, sued, fined or
convicted. The record is a filing or a docket, and it is nearly always
public; the work is finding the right registry for the jurisdiction.

## Companies

- **US listed companies:** `python3 "$MYCROFT_DIR/tools/evidence-lookup.py" edgar '"exact phrase"' --from DATE`
  searches the full text of every SEC filing since 2001 and links the
  documents. For a company's own filings, its EDGAR page
  (sec.gov/cgi-bin/browse-edgar?company=NAME) and the XBRL "Financial
  Report" tabs. Revenue, headcount, executive pay and risk factors all
  live in the 10-K; material events in 8-Ks.
- **UK:** find-and-update.company-information.service.gov.uk (Companies
  House: officers, accounts, persons with significant control; free, no
  login). Charity Commission for charities.
- **EU:** national registers, many free (Germany handelsregister.de and
  bundesanzeiger.de for accounts; France infogreffe.fr and pappers.fr;
  Netherlands kvk.nl; Italy registroimprese.it). e-justice.europa.eu
  links every member state's register.
- **Elsewhere:** OpenCorporates (opencorporates.com, browser; API needs a
  key) indexes registries in 140+ jurisdictions and links to the source.
  Sanctions: OFAC sanctions list search, EU sanctions map, UK OFSI list.
- **Ownership and leaks:** ICIJ Offshore Leaks database
  (offshoreleaks.icij.org), OpenSanctions (opensanctions.org).
- **Private company figures** (valuation, revenue, layoffs) usually rest
  on the company's own statements or a reporter's sources; treat them as
  attributions, not facts.

## Courts

- **US federal:** `evidence-lookup.py courtlistener "party or phrase"` searches
  opinions (free key lifts the rate limit); dockets and filings via
  CourtListener's RECAP archive, and PACER in the browser (the user's
  account, paid per page). Supreme Court: supremecourt.gov.
- **US state:** each state's case search portal, browser; many are free.
- **UK:** bailii.org and the National Archives' caselaw.nationalarchives.gov.uk
  for judgments; judiciary.uk for sentencing remarks.
- **EU:** curia.europa.eu (CJEU), hudoc.echr.coe.int (ECHR), eur-lex.europa.eu
  for legislation.
- **International:** icj-cij.org, icc-cpi.int.
- **Elsewhere:** the court's own site; WorldLII (worldlii.org) indexes
  many. Search in the local language.

## Regulators, fines and enforcement

- SEC (sec.gov/litigation), DOJ (justice.gov/news), FTC, CFPB, FCA
  (fca.org.uk/news), the European Commission's competition press corner,
  national data-protection authorities for GDPR fines (enforcement
  tracker at enforcementtracker.com is a good index).

## Method and traps

- Charged, indicted, convicted, settled without admission, fined: these
  are different facts. Quote the document's own word.
- A lawsuit's allegations are allegations; the complaint proves they
  were made, nothing more.
- Company names: check the exact legal entity; subsidiaries and
  similarly named companies are a common source of error.
- Currency and fiscal-year definitions differ; a "record profit" needs
  the same basis on both sides of the comparison.
