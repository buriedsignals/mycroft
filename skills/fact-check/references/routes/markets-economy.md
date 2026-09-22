# Route: markets and the economy

> Adapted from Big If True by Verso (verso.ink/big-if-true). "The browser" here means the `web-acquisition` skill; page fetches go through `mycroft-fetch`.


Yields, indices, oil, FX, inflation, debt, GDP. Every source below is
free and `marketdata.py` wraps all of them. This file maps which
source answers which claim, the series ids to pass, and the traps. Read
the section you need, not the whole file.

## Which source for which claim

| Claim in the text | Primary source | Command |
|---|---|---|
| US Treasury yield, same-day close (2y/10y/30y) | Treasury daily par yield curve (official, posted each afternoon) | `treasury`, `treasury --tenor BC_30YEAR` |
| US Treasury yield history, "highest since" | FRED (Fed H.15, next business day) | `fred DGS10 --above 4.79` |
| UK gilt yield, Bank Rate, sterling | Bank of England database (daily since the 1970s, ~3-day lag) | `boe IUDMNPY --above 5.26` |
| German Bund yield | Bundesbank (daily, same day) | `bundesbank` |
| Japan, France, Italy, any OECD 10-year yield (monthly) | OECD | `oecd JPN`, `oecd FRA` |
| Same-day index close, intraday high, futures, FX | the free chart endpoint the `yahoo` command wraps (unofficial) | `yahoo ^STOXX`, `yahoo ^TNX --field high`, `yahoo BZ=F` |
| S&P 500, Nasdaq, Dow, Nikkei history | FRED (licensed from S&P/Nikkei, next business day) | `fred SP500`, `fred NIKKEI225` |
| Brent / WTI spot | EIA (daily, ~1-week lag) or FRED mirror | `eia RBRTE`, `fred DCOILBRENTEU --change 2026-02-27` |
| US retail gasoline / diesel, Henry Hub gas | FRED weekly/daily | `fred GASREGW`, `fred GASDESW`, `fred DHHNGSP` |
| EUR/USD and other ECB reference rates, any date | Frankfurter (ECB data) | `fx EUR USD 2026-02-27` |
| Euro-area inflation (final monthly) | ECB Data Portal / Eurostat | `ecb`, `eurostat prc_hicp_manr geo=EA coicop=CP00` |
| Euro-area flash inflation (this month's) | Eurostat euro-indicators press release page (fetch it) | — |
| US CPI, PCE | FRED | `fred CPIAUCSL`, `fred PCEPI` |
| US gross national debt | Treasury Fiscal Data (daily) | `usdebt` |
| US nominal GDP (for debt-to-GDP) | FRED (quarterly, annualized) | `fred GDP` |
| US debt-to-GDP as published | FRED | `fred GFDEGDQ188S` |
| ECB deposit rate, Fed funds target | ECB Data Portal / FRED | `ecb FM/B.U2.EUR.4F.KR.DFR.LEV`, `fred DFEDTARU` |
| French, Japanese, UK debt and GDP totals | INSEE, MOF/Cabinet Office, ONS release pages (fetch) | — |

## Same-day prices

The `yahoo` command's chart endpoint is the one free source for
same-day index closes, intraday highs, front-month futures and spot FX.
It is unofficial: no docs, no guarantees, and bursts of requests get
HTTP 429 for a while. One symbol per call; if it fails twice, take the
figure from a wire service's or the exchange's own report and come back
later. A 429 is not evidence. Symbols: ^GSPC, ^DJI, ^IXIC,
^N225, ^STOXX (Stoxx Europe 600), ^GDAXI, ^FTSE, ^FCHI, ^HSI, ^TNX (US
10y yield, in percent), ^TYX (30y), BZ=F, CL=F, NG=F, GC=F, EURUSD=X,
USDJPY=X, GBPUSD=X. `--field high` for the intraday high, `--range 1y`
for a year. For yields prefer the official same-day feeds (Treasury,
Bundesbank) and use the chart endpoint only for the intraday high.

## Keys (optional, free, raise limits and use the documented endpoints)

- `FRED_API_KEY` — free at fred.stlouisfed.org/docs/api/api_key.html.
  With it, `fred` uses the `series/observations` API. Without it, the
  script downloads the same CSV the "Download" button on every series
  page serves, which works fine for a handful of pulls.
- `EIA_API_KEY` — free at eia.gov/opendata. Without it the script uses
  api.data.gov's shared `DEMO_KEY`, limited to 30 calls an hour and 50 a
  day per IP address; a registered key gets 1,000 an hour.

Everything else — Treasury XML and Fiscal Data, Bank of England, Bundesbank,
ECB, Eurostat, OECD, Frankfurter — is open: no key, no account. Fiscal
Data and OECD return HTTP 429 if hammered; a fact-check needs a handful
of calls, well under any limit.

## Series ids worth knowing

**FRED** (`fred SERIES`) — DGS2, DGS5, DGS10, DGS30 (Treasury constant
maturity); T10Y2Y (curve); DFEDTARU (fed funds upper target);
DCOILBRENTEU, DCOILWTICO (spot oil); GASREGW, GASDESW (weekly retail
gasoline/diesel); DHHNGSP (Henry Hub gas); DEXUSEU, DEXJPUS, DEXUSUK
(FX); CPIAUCSL, CPILFESL, PCEPI (US inflation); GDP (nominal, quarterly
annualized), GDPC1 (real); GFDEBTN (federal debt, quarterly);
GFDEGDQ188S (debt to GDP); IRLTLT01GBM156N, IRLTLT01DEM156N,
IRLTLT01JPM156N, IRLTLT01FRM156N, IRLTLT01ITM156N (monthly 10-year
yields); SP500, NASDAQCOM, DJIA, NIKKEI225 (daily, next-day); VIXCLS.

**Treasury** (`treasury [YYYYMM] --tenor X`) — BC_1MONTH, BC_3MONTH,
BC_6MONTH, BC_1YEAR, BC_2YEAR, BC_5YEAR, BC_10YEAR, BC_20YEAR, BC_30YEAR.
One month per call; pass the month for history.

**Bank of England** (`boe SERIES --start YEAR`) — IUDMNPY (10-year
nominal par gilt yield), IUDSNPY (5-year), IUDLNPY (20-year), IUDBEDR
(Bank Rate), XUDLUSS (USD per GBP), XUDLERS (EUR per GBP). The database
help page documents the CSV URL (Datefrom, Dateto=now, SeriesCodes up to
300, CSVF=TN, UsingCodes=Y).

**ECB Data Portal** (`ecb FLOW/KEY`) — ICP/M.U2.N.000000.4.ANR (HICP,
all items), ICP/M.U2.N.XEF000.4.ANR (core), EXR/D.USD.EUR.SP00.A (daily
EUR/USD reference), FM/B.U2.EUR.4F.KR.DFR.LEV (deposit facility rate).
Documented parameters: lastNObservations, startPeriod, endPeriod,
format=csvdata.

**Eurostat** (`eurostat DATASET k=v …`) — prc_hicp_manr with geo=EA (euro
area) or a country code and coicop=CP00; gov_10dd_edpt1 for government
debt (annual); namq_10_gdp for quarterly GDP. Documented parameter:
lastTimePeriod.

**OECD** (`oecd COUNTRY`) — three-letter codes: USA, GBR, DEU, FRA, ITA,
ESP, JPN, CAN, AUS; monthly average 10-year yield from the
DSD_STES@DF_FINMARK dataflow.

**EIA** (`eia SERIES`) — RBRTE (Brent spot), RWTC (WTI spot). JSON
responses cap at 5,000 rows; `--n` sets the count.

**Frankfurter** (`fx FROM TO [DATE]`) — v1 endpoints on
api.frankfurter.dev (`/v1/latest`, `/v1/YYYY-MM-DD`); ECB reference
rates, published around 16:00 CET on working days; no quotas.

## Traps

- **Lags differ.** The chart endpoint is live; Treasury and Bundesbank post the same day; FRED's H.15
  yields and index levels the next business day; the BoE database about
  three days behind; EIA spot prices about a week; ECB/Eurostat monthly
  series carry only final data, so this morning's flash estimate is not
  in them. Check the `latest:` line the script prints before writing "on
  Tuesday" into a rationale.
- **Par vs benchmark.** The BoE series and Treasury curve are fitted par
  yields; wire services and financial data vendors quote the benchmark
  bond. They differ by a few basis points, so a "highest since" verdict
  should rest on a clear gap, not a 2bp edge. Say which measure you used.
- **Percent vs ratio.** Debt-to-GDP needs nominal, annualized GDP for the
  same period (FRED `GDP`, quarterly); dividing by real GDP or by a
  monthly figure gives nonsense. FRED `GFDEGDQ188S` is the published
  ratio if you only need to confirm one.
- **Decimal commas** in Bundesbank CSVs; the script converts them.
- **User agents.** FRED refuses browser-style user agents from scripts;
  the BoE and Treasury refuse requests without one. The script handles
  this per source; if you fetch by hand, drop the User-Agent for FRED and
  add one elsewhere.
- **Prewar / pre-event baselines.** Pick the last trading day before the
  event and say so: `--change 2026-02-27` prints the base value so the
  rationale can quote it.

## What is not here

The IMF data portal and most quote sites are not wrapped: they don't
answer scripts. Index providers publish history files only behind a
login or a browser challenge; the browser reaches them if a same-day
official figure is needed. Paid terminal data is out of scope; if a
claim can only be settled with it (a specific intraday print, a
benchmark switch date) say so in the documents ask rather than
approximating.
