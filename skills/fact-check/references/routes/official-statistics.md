# Route: official statistics

> Adapted from Big If True by Verso (verso.ink/big-if-true). "The browser" here means the `web-acquisition` skill; page fetches go through `mycroft-fetch`.


Population, unemployment, crime, migration, health, elections, budgets,
trade, emissions. Every country publishes these; the checker's job is to
reach the body that produces the number, in its own release, rather
than an aggregator's copy of it. (Market and macro series with an API —
yields, inflation, debt, GDP — are in markets-economy.md.)

## Where the number is produced

| Kind of figure | Producer |
|---|---|
| Labour, prices, GDP, trade (any country) | the national statistics office: BLS and BEA and Census (US), ONS (UK), Destatis, INSEE, ISTAT, INE, Statistics Canada, ABS, Stats NZ, e-Stat (Japan), NBS (China), MOSPI (India), IBGE (Brazil), Stats SA … search "<country> statistics office" |
| Cross-country comparisons | Eurostat (EU), OECD (members), World Bank Open Data (api.worldbank.org, no key), IMF WEO, UN Data, ILOSTAT — and cite which, because definitions differ |
| Elections | the electoral commission or ministry of the interior; for the US, state secretaries of state and the FEC; a wire service for race calls |
| Crime | FBI Crime Data Explorer (US), ONS/Home Office (England & Wales), Eurostat crime statistics; police "recorded crime" ≠ survey "experienced crime" |
| Migration, asylum | Eurostat migr_ datasets, UNHCR data portal, DHS/CBP (US), Home Office (UK) |
| Health | WHO GHO, OECD Health, national health ministries, CDC WONDER, ECDC |
| Climate, emissions, energy | EIA (US, `marketdata.py eia`), IEA, Our World in Data (a curated aggregator that names its source — follow the link), Copernicus, NOAA, national inventories to the UNFCCC |
| Public finance, budgets | the treasury or finance ministry, the budget office (CBO, OBR, IFS), Eurostat gov_ datasets |
| Development, poverty | World Bank PovcalNet/PIP, UNDP HDR |

## Method

1. Identify the exact statistic: the series, the period, the definition
   (headline vs core, seasonally adjusted or not, gross vs net, per
   capita or total). Most "wrong" numbers are a right number for a
   different definition.
2. Fetch the release page or the table; many offices publish CSV or an
   API (Eurostat and ECB via `marketdata.py`; World Bank at
   api.worldbank.org/v2/country/CODE/indicator/INDICATOR?format=json;
   most others as downloadable tables — the browser for interactive
   explorers).

## Traps

- Fiscal years, calendar years and rolling 12 months.
- Rankings ("the highest in Europe") depend on which countries the
  source includes; say which list.
- Data aggregators are convenient but secondary; when a verdict rests
  on a number, cite the producer.
- Percent vs percentage points.
