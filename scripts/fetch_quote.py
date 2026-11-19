#!/usr/bin/env python3
"""Descarga la cotización de AIR.PA y escribe quote.json junto al index.html.

Se ejecuta desde GitHub Actions (.github/workflows/quote.yml) cada 10 minutos.
Estrategia: varias fuentes en orden, con reintentos. Sale con código 0 y sin
tocar quote.json si ninguna fuente responde, para no romper la web.
"""
import datetime
import json
import sys
import time
import urllib.parse
import urllib.request

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/AIR.PA?interval=1d&range=1d"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")


def sources():
    enc = urllib.parse.quote(YAHOO, safe="")
    return [
        YAHOO,
        "https://query2.finance.yahoo.com/v8/finance/chart/AIR.PA?interval=1d&range=1d",
        f"https://api.allorigins.win/raw?url={enc}",
        f"https://api.codetabs.com/v1/proxy?quest={enc}",
    ]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def parse_chart(raw):
    meta = raw["chart"]["result"][0]["meta"]
    price = float(meta["regularMarketPrice"])
    if price <= 0:
        raise ValueError("precio no válido")
    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
    prev = float(prev) if prev else None
    mt = meta.get("regularMarketTime")
    if isinstance(mt, (int, float)):
        when = datetime.datetime.fromtimestamp(mt, datetime.timezone.utc).isoformat()
    else:
        when = mt
    return {
        "price": round(price, 4),
        "prevClose": round(prev, 4) if prev else None,
        "change": round(price - prev, 4) if prev else 0,
        "pct": round((price / prev - 1) * 100, 4) if prev else 0,
        "marketTime": when,
        "currency": meta.get("currency"),
        "exchange": meta.get("fullExchangeName") or meta.get("exchangeName"),
        "source": "yahoo",
        "fetchedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def main(path="quote.json"):
    last_err = None
    for attempt in range(1, 4):
        for url in sources():
            try:
                quote = parse_chart(fetch(url))
            except Exception as exc:  # noqa: BLE001
                last_err = f"{url} -> {exc}"
                continue
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(quote, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            print("OK", url)
            print(json.dumps(quote, ensure_ascii=False))
            return 0
        time.sleep(attempt * 5)
    print(f"AVISO: ninguna fuente devolvió cotización ({last_err}); quote.json intacto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
