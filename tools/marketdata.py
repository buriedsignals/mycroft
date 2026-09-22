#!/usr/bin/env python3
"""marketdata.py — pull market and economic series from free, keyless APIs.

Every subcommand prints plain rows `date<TAB>value` (oldest first) and, when
asked, answers the two questions fact-checks keep needing:

  --above VALUE     last date the series exceeded VALUE ("highest since …")
  --change FROM     percent change from the FROM date's value to the latest

No key is required. Two optional free keys raise limits and use the
official endpoints: FRED_API_KEY (api.stlouisfed.org) and EIA_API_KEY
(otherwise the shared DEMO_KEY: 30 calls/hour, 50/day per IP). Stdlib only.

  --evidence    also store every raw API response in MYCROFT_PROV_DIR as a
                Mycroft evidence item (E-*.json + artifact, sha256 from the
                saved bytes) and print its id, so the pull can be cited in
                data/evidence-bundle.json. Use it whenever a verdict will
                rest on the series.

Sources (see skills/fact-check/references/routes/markets-economy.md for
series ids and caveats):
  fred SERIES              FRED (DGS10, DCOILBRENTEU, GDP, GFDEBTN, SP500 …)
  treasury [YYYYMM]        US Treasury daily par yield curve (same-day, official)
  yahoo SYMBOL             Yahoo Finance daily OHLC, same day (^GSPC, ^STOXX, BZ=F …)
  boe SERIES               Bank of England daily (IUDMNPY = 10y gilt yield)
  bundesbank               Bundesbank daily 10y Bund yield
  ecb FLOW/KEY             ECB Data Portal (ICP/M.U2.N.000000.4.ANR = HICP)
  eurostat DATASET k=v …   Eurostat JSON API (prc_hicp_manr geo=EA coicop=CP00)
  oecd COUNTRY             OECD monthly long-term interest rate
  fx FROM TO [DATE]        ECB reference FX via Frankfurter (api.frankfurter.dev)
  eia SERIES               EIA daily spot (RBRTE = Brent, RWTC = WTI)
  usdebt                   US Treasury debt to the penny

Adapted from Big If True by Verso (verso.ink/big-if-true).
"""
import argparse, csv, datetime as dt, io, json, os, re, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evidence_record  # noqa: E402

EVIDENCE = False
RECORDS = []
TASK = ""


def mask(url):
    """Keys travel in the query string; never store or print them."""
    for var in ("FRED_API_KEY", "EIA_API_KEY"):
        key = os.environ.get(var)
        if key:
            url = url.replace(key, "<key>")
    return url

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}


def get(url, retries=2, sleep=3, browser_ua=True):
    """FRED refuses browser user agents from scripts; most other hosts refuse
    non-browser ones. Each source picks."""
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA if browser_ua else {})
            body = urllib.request.urlopen(req, timeout=60).read()
            if EVIDENCE:
                RECORDS.append(evidence_record.write_api_evidence(
                    source_url=mask(url), body=body, query_or_task=TASK,
                    command="marketdata.py " + " ".join(sys.argv[1:])))
            return body.decode("utf-8", "replace")
        except Exception as e:  # noqa
            last = e
            if i < retries:
                time.sleep(sleep * (i + 1))
    # URLs carry API keys in the query and may carry logins; the exception text
    # can echo the URL. Keep the host, the path and the HTTP status only.
    u = urllib.parse.urlsplit(url)
    sys.exit(f"fetch failed: {u.hostname}{u.path}\n  {type(last).__name__} {getattr(last, 'code', '')}".rstrip())


def num(s):
    s = str(s).strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


# ---------- sources: each returns (url, [(date_str, value)]) ----------

def src_fred(a):
    key = os.environ.get("FRED_API_KEY")
    if key:
        # Official API (docs: fred.stlouisfed.org/docs/api). Terms require the
        # notice: "This product uses the FRED API but is not endorsed or
        # certified by the Federal Reserve Bank of St. Louis."
        url = (f"https://api.stlouisfed.org/fred/series/observations?series_id={a.series}"
               f"&api_key={key}&file_type=json")
        d = json.loads(get(url, browser_ua=False))
        cite = url.replace(key, "<key>")
        return cite, [(o["date"], num(o["value"])) for o in d["observations"] if num(o["value"]) is not None]
    # Keyless fallback: the same CSV the "Download" button on every FRED
    # series page serves. Undocumented as an API; keep usage light.
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={a.series}"
    rows = list(csv.reader(io.StringIO(get(url, browser_ua=False))))[1:]
    return url, [(d, num(v)) for d, v in rows if num(v) is not None]


def src_treasury(a):
    """Daily par yield curve, published by Treasury each afternoon (official,
    same-day close). Columns: BC_1MONTH … BC_2YEAR, BC_10YEAR, BC_30YEAR."""
    month = a.month or dt.date.today().strftime("%Y%m")
    url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
           f"?data=daily_treasury_yield_curve&field_tdr_date_value_month={month}")
    x = get(url)
    out = []
    for entry in re.findall(r"<m:properties>(.*?)</m:properties>", x, re.S):
        d = re.search(r"<d:NEW_DATE[^>]*>(\d{4}-\d{2}-\d{2})", entry)
        v = re.search(rf"<d:{a.tenor}[^>]*>([\d.]+)<", entry)
        if d and v:
            out.append((d.group(1), float(v.group(1))))
    return url, out


def src_yahoo(a):
    """Unofficial chart endpoint; the only free same-day source for index
    closes, intraday highs and front-month futures. Rate-limits bursts
    (HTTP 429) — one symbol per call, and let it back off."""
    url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(a.symbol)}"
           f"?range={a.range}&interval=1d")
    d = json.loads(get(url, retries=3, sleep=15))
    r = d["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    out = []
    for t, v in zip(r["timestamp"], q[a.field]):
        if v is not None:
            out.append((dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat(), float(v)))
    return url, out


def src_boe(a):
    url = ("https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes"
           f"&Datefrom=01/Jan/{a.start}&Dateto=now&SeriesCodes={a.series}&CSVF=TN&UsingCodes=Y")
    out = []
    for line in get(url).splitlines()[1:]:
        if "," not in line:
            continue
        d, v = line.split(",")[:2]
        if num(v) is None:
            continue
        out.append((dt.datetime.strptime(d.strip(), "%d %b %Y").date().isoformat(), num(v)))
    return url, out


def src_bundesbank(a):
    key = "BBSIS/D.I.ZAR.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A"
    url = f"https://api.statistiken.bundesbank.de/rest/data/{key}?lastNObservations={a.n}&format=csv"
    out = []
    for line in get(url).splitlines():
        p = line.split(";")
        if len(p) >= 2 and len(p[0]) == 10 and p[0][4] == "-" and num(p[1]) is not None:
            out.append((p[0], num(p[1])))
    return url, out


def src_ecb(a):
    url = f"https://data-api.ecb.europa.eu/service/data/{a.key}?lastNObservations={a.n}&format=csvdata"
    rows = list(csv.DictReader(io.StringIO(get(url))))
    return url, [(r["TIME_PERIOD"], num(r["OBS_VALUE"])) for r in rows if num(r.get("OBS_VALUE")) is not None]


def src_eurostat(a):
    q = "&".join(a.filters)
    url = (f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{a.dataset}"
           f"?{q}&lastTimePeriod={a.n}")
    d = json.loads(get(url))
    idx = d["dimension"]["time"]["category"]["index"]
    inv = {str(i): t for t, i in idx.items()}
    return url, sorted((inv[k], float(v)) for k, v in d["value"].items())


def src_oecd(a):
    url = ("https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/"
           f"{a.country}.M.IRLT.PA.....?lastNObservations={a.n}&format=csvfilewithlabels")
    rows = list(csv.DictReader(io.StringIO(get(url))))
    return url, sorted((r["TIME_PERIOD"], num(r["OBS_VALUE"])) for r in rows if num(r.get("OBS_VALUE")) is not None)


def src_fx(a):
    when = a.date or "latest"
    url = f"https://api.frankfurter.dev/v1/{when}?base={a.frm}&symbols={a.to}"
    d = json.loads(get(url))
    return url, [(d["date"], float(d["rates"][a.to]))]


def src_eia(a):
    key = os.environ.get("EIA_API_KEY", "DEMO_KEY")  # DEMO_KEY: 30/hour, 50/day per IP
    url = (f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={key}&frequency=daily"
           "&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=" + a.series +
           "&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=desc&length=" + str(a.n))
    d = json.loads(get(url))
    cite = url.replace(key, "<key>") if key != "DEMO_KEY" else url
    return cite, sorted((r["period"], num(r["value"])) for r in d["response"]["data"] if num(r["value"]) is not None)


def src_usdebt(a):
    url = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny"
           f"?sort=-record_date&page%5Bsize%5D={a.n}")
    d = json.loads(get(url))
    return url, sorted((r["record_date"], float(r["tot_pub_debt_out_amt"])) for r in d["data"])


# ---------- analysis ----------

def report(url, rows, a):
    if not rows:
        sys.exit("no data returned")
    rows.sort()
    if a.since:
        rows = [r for r in rows if r[0] >= a.since]
    shown = rows[-a.last:] if a.last else rows
    for d, v in shown:
        print(f"{d}\t{v:g}")
    latest_d, latest_v = rows[-1]
    print(f"\nlatest: {latest_d} = {latest_v:g}")
    print(f"max in range: {max(rows, key=lambda r: r[1])[1]:g} on {max(rows, key=lambda r: r[1])[0]}")
    if a.above is not None:
        prior = [r for r in rows if r[1] > a.above and r[0] < latest_d]
        if prior:
            print(f"last date above {a.above:g} (before {latest_d}): {prior[-1][0]} = {prior[-1][1]:g}")
        else:
            print(f"no date in range above {a.above:g} before {latest_d}")
    if a.change:
        base = [r for r in rows if r[0] <= a.change]
        if not base:
            sys.exit(f"no observation on or before {a.change}")
        bd, bv = base[-1]
        print(f"change from {bd} ({bv:g}) to {latest_d} ({latest_v:g}): {100 * (latest_v / bv - 1):+.1f}%")
    print(f"\nsource: {mask(url)}")
    if RECORDS:
        print()
        evidence_record.print_records(RECORDS)


def main():
    global EVIDENCE, TASK
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--since", help="drop rows before this ISO date")
    p.add_argument("--last", type=int, default=15, help="rows to print (0 = all); analysis uses the full range")
    p.add_argument("--above", type=float, help="report the last date the series exceeded this value")
    p.add_argument("--change", metavar="DATE", help="percent change from DATE's value to the latest")
    p.add_argument("--evidence", action="store_true", help="store each raw response as a Mycroft evidence item")
    p.add_argument("--task", default="", help="claim id or note to record as query_or_task with --evidence")
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("fred"); x.add_argument("series"); x.set_defaults(f=src_fred)
    x = s.add_parser("treasury"); x.add_argument("month", nargs="?", help="YYYYMM (default: this month)")
    x.add_argument("--tenor", default="BC_10YEAR", help="BC_2YEAR, BC_10YEAR, BC_30YEAR …"); x.set_defaults(f=src_treasury)
    x = s.add_parser("yahoo"); x.add_argument("symbol"); x.add_argument("--range", default="3mo")
    x.add_argument("--field", default="close", choices=["open", "high", "low", "close"]); x.set_defaults(f=src_yahoo)
    x = s.add_parser("boe"); x.add_argument("series", nargs="?", default="IUDMNPY"); x.add_argument("--start", default="1990"); x.set_defaults(f=src_boe)
    x = s.add_parser("bundesbank"); x.add_argument("--n", type=int, default=60); x.set_defaults(f=src_bundesbank)
    x = s.add_parser("ecb"); x.add_argument("key", nargs="?", default="ICP/M.U2.N.000000.4.ANR"); x.add_argument("--n", type=int, default=36); x.set_defaults(f=src_ecb)
    x = s.add_parser("eurostat"); x.add_argument("dataset"); x.add_argument("filters", nargs="*"); x.add_argument("--n", type=int, default=36); x.set_defaults(f=src_eurostat)
    x = s.add_parser("oecd"); x.add_argument("country"); x.add_argument("--n", type=int, default=24); x.set_defaults(f=src_oecd)
    x = s.add_parser("fx"); x.add_argument("frm"); x.add_argument("to"); x.add_argument("date", nargs="?"); x.set_defaults(f=src_fx)
    x = s.add_parser("eia"); x.add_argument("series", nargs="?", default="RBRTE"); x.add_argument("--n", type=int, default=60); x.set_defaults(f=src_eia)
    x = s.add_parser("usdebt"); x.add_argument("--n", type=int, default=10); x.set_defaults(f=src_usdebt)
    a = p.parse_args()
    EVIDENCE = a.evidence
    TASK = a.task or f"{a.cmd} series"
    url, rows = a.f(a)
    report(url, rows, a)


if __name__ == "__main__":
    main()
