#!/usr/bin/env python3
"""Descarga la cotización de Airbus (ISIN NL0000235190) y escribe quote.json.

Se ejecuta desde GitHub Actions (.github/workflows/quote.yml) cada 10 minutos.

Orden de fuentes:
  1. Yahoo Finance, AIR.PA (Euronext París) — la referencia del ESOP.
  2. Boursorama, misma acción en Euronext París (HTML, sin clave).
  3. Börse Frankfurt, misma ISIN — sin clave y accesible desde cloud, se usa
     cuando las anteriores bloquean la IP del runner.
  4. Proxies CORS de Yahoo, último recurso.

Si ninguna responde, sale con 0 y NO toca quote.json: la web mostrará la última
cotización conocida marcada como caché en lugar de un número inventado.
"""
import datetime
import json
import re
import subprocess
import sys
import time
import urllib.parse

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/AIR.PA?interval=1d&range=1d"
YAHOO2 = "https://query2.finance.yahoo.com/v8/finance/chart/AIR.PA?interval=1d&range=1d"
BOURSORAMA = "https://www.boursorama.com/cours/1rPAIR/"
FRANKFURT = "https://api.boerse-frankfurt.de/v1/data/price_information?isin=NL0000235190"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
TIMEOUT = 20


def get_text(url):
    """Descarga con curl: urllib se atasca con el keep-alive de bolsa-frankfurt."""
    proc = subprocess.run(
        ["curl", "-sS", "--max-time", str(TIMEOUT), "--http2", "-H", f"User-Agent: {UA}", url],
        capture_output=True, text=True, timeout=TIMEOUT + 5,
    )
    out = proc.stdout or ""
    if not out.strip():
        raise ValueError(f"respuesta vacía (curl {proc.returncode}): {proc.stderr.strip()[:80]}")
    return out


def as_json(text):
    """Los endpoints JSON llegan limpios o con prefijo 'data:' (bolsa-frankfurt)."""
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("data:"):
            line = line[5:].strip()
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    raise ValueError("sin JSON utilizable")


def from_yahoo(text):
    meta = as_json(text)["chart"]["result"][0]["meta"]
    price = float(meta["regularMarketPrice"])
    if price <= 0:
        raise ValueError("precio no válido")
    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
    prev = float(prev) if prev else None
    mt = meta.get("regularMarketTime")
    when = (datetime.datetime.fromtimestamp(mt, datetime.timezone.utc).isoformat()
            if isinstance(mt, (int, float)) else mt)
    return {
        "price": round(price, 4),
        "prevClose": round(prev, 4) if prev else None,
        "change": round(price - prev, 4) if prev else 0,
        "pct": round((price / prev - 1) * 100, 4) if prev else 0,
        "marketTime": when,
        "currency": meta.get("currency") or "EUR",
        "exchange": "Euronext Paris",
        "source": "yahoo",
    }


def from_boursorama(text):
    """Euronext París vía la ficha de Boursorama. La página no publica la hora de
    la última negociación, así que se sella la hora de descarga."""
    m = (re.search(r'data-ist="1rPAIR".{0,500}?data-ist-last>([\d.,\s\u00a0]+)<', text, re.S)
         or re.search(r'data-ist-last>([\d.,\s\u00a0]+)<', text))
    if not m:
        raise ValueError("precio no encontrado en el HTML")
    price = float(re.sub(r"[\s\u00a0.]", "", m.group(1)).replace(",", "."))
    if price <= 0:
        raise ValueError("precio no válido")
    v = re.search(r'data-ist-variation>([+-]?[\d.,]+)\s*%', text)
    pct = float(re.sub(r"[.\s]", "", v.group(1)).replace(",", ".")) if v else None
    prev = round(price / (1 + pct / 100), 4) if pct not in (None, -100) else None
    return {
        "price": round(price, 4),
        "prevClose": prev,
        "change": round(price - prev, 4) if prev else 0,
        "pct": round(pct, 4) if pct is not None else 0,
        "marketTime": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "currency": "EUR",
        "exchange": "Euronext Paris (Boursorama)",
        "source": "boursorama",
    }


def from_frankfurt(text):
    raw = as_json(text)
    price = float(raw["lastPrice"])
    if price <= 0:
        raise ValueError("precio no válido")
    prev = raw.get("closingPricePrevTradingDay")
    prev = float(prev) if prev else None
    return {
        "price": round(price, 4),
        "prevClose": round(prev, 4) if prev else None,
        "change": round(price - prev, 4) if prev else 0,
        "pct": round((price / prev - 1) * 100, 4) if prev else 0,
        "marketTime": raw.get("timestampLastPrice"),
        "currency": "EUR",
        "exchange": "Börse Frankfurt (XETRA)",
        "source": "boerse-frankfurt",
    }


def blueprint():
    enc = urllib.parse.quote(YAHOO, safe="")
    return [
        ("yahoo", YAHOO, from_yahoo),
        ("boursorama", BOURSORAMA, from_boursorama),
        ("boerse-frankfurt", FRANKFURT, from_frankfurt),
        ("yahoo", YAHOO2, from_yahoo),
        ("yahoo (proxy)", f"https://api.allorigins.win/raw?url={enc}", from_yahoo),
        ("yahoo (proxy)", f"https://api.codetabs.com/v1/proxy?quest={enc}", from_yahoo),
    ]


def main(path="quote.json"):
    errors = []
    for attempt in (1, 2):
        for name, url, parser in blueprint():
            try:
                quote = parser(get_text(url))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{name}: {exc}")
                continue
            quote["fetchedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(quote, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            print(f"OK {name} -> {quote['price']} ({quote['exchange']})")
            print(json.dumps(quote, ensure_ascii=False))
            return 0
        if attempt == 1:
            time.sleep(5)
    print("AVISO: ninguna fuente devolvió cotización; quote.json intacto.")
    for err in errors:
        print("  -", err)
    return 0


if __name__ == "__main__":
    sys.exit(main())
