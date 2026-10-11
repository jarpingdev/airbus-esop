#!/usr/bin/env python3
"""
Airbus ESOP Visual Web Dashboard
Servidor Flask que proporciona una interfaz gráfica moderna, visual e interactiva
para gestionar el plan de acciones, simular ventas, calcular IRPF y optimizar compras.
"""

import os
import json
import webbrowser
import threading
from datetime import datetime, date
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
import urllib.request
from airbus_esop import ESOP_CAMPAIGNS, get_campaign_info, OFFICIAL_PACKAGES

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "portfolio.json"
CALENDAR_FILE = BASE_DIR / "airbus_esop_recordatorios.ics"
TICKER_AIRBUS = "AIR.PA"

app = Flask(__name__)

DEFAULT_PACKAGES = [
    {"id": 1, "purchased": 3, "matching": 2, "total": 5},
    {"id": 2, "purchased": 6, "matching": 4, "total": 10},
    {"id": 3, "purchased": 9, "matching": 6, "total": 15},
    {"id": 4, "purchased": 15, "matching": 12, "total": 27},
    {"id": 5, "purchased": 18, "matching": 12, "total": 30},
    {"id": 6, "purchased": 30, "matching": 20, "total": 50},
    {"id": 7, "purchased": 42, "matching": 28, "total": 70},
    {"id": 8, "purchased": 54, "matching": 36, "total": 90},
]


def fetch_live_price():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{TICKER_AIRBUS}"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            meta = data["chart"]["result"][0]["meta"]
            price = float(meta.get("regularMarketPrice", 189.30))
            prev_close = float(meta.get("chartPreviousClose", price))
            change = price - prev_close
            pct_change = (change / prev_close * 100) if prev_close else 0.0
            return {
                "success": True,
                "price": round(price, 2),
                "change": round(change, 2),
                "pct_change": round(pct_change, 2),
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "price": 189.30,
            "change": 0.0,
            "pct_change": 0.0,
            "timestamp": "Modo sin conexión"
        }


def load_portfolio():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        initial_data = {
            "lots": [
                {
                    "id": "ESOP-2024",
                    "year": 2024,
                    "grant_date": "2024-05-15",
                    "unlock_date": "2027-05-15",
                    "purchased_shares": 15,
                    "matching_shares": 12,
                    "total_shares": 27,
                    "purchase_price": 150.26,
                    "total_paid": 2253.90,
                    "status": "LOCKED",
                    "notes": "Paquete 15 + 12 (descuento ~44.4%)"
                }
            ],
            "history": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        return initial_data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_portfolio(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_tax_spain(capital_gain):
    if capital_gain <= 0:
        return 0.0
    tax = 0.0
    remaining = capital_gain

    t1 = min(remaining, 6000.0)
    tax += t1 * 0.19
    remaining -= t1

    if remaining > 0:
        t2 = min(remaining, 44000.0)
        tax += t2 * 0.21
        remaining -= t2

    if remaining > 0:
        t3 = min(remaining, 150000.0)
        tax += t3 * 0.23
        remaining -= t3

    if remaining > 0:
        t4 = min(remaining, 100000.0)
        tax += t4 * 0.27
        remaining -= t4

    if remaining > 0:
        tax += remaining * 0.28

    return round(tax, 2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/standalone")
@app.route("/standalone.html")
@app.route("/Airbus_ESOP_Standalone.html")
@app.route("/airbus_esop.html")
@app.route("/offline")
def standalone_app():
    return send_file(BASE_DIR / "Airbus_ESOP_Standalone.html")


@app.route("/api/status")
def get_status():
    quote = fetch_live_price()
    current_price = quote["price"]
    portfolio = load_portfolio()
    today = date.today()

    lots_data = []
    total_invested = 0.0
    total_market_val = 0.0
    total_shares = 0
    total_gift_shares = 0

    for lot in portfolio.get("lots", []):
        grant_d = datetime.strptime(lot["grant_date"], "%Y-%m-%d").date()
        unlock_d = datetime.strptime(lot["unlock_date"], "%Y-%m-%d").date()
        days_left = max((unlock_d - today).days, 0)
        total_holding_days = (unlock_d - grant_d).days or 1095
        days_passed = max((today - grant_d).days, 0)
        progress_pct = min(round((days_passed / total_holding_days) * 100, 1), 100.0)

        shares = lot["total_shares"]
        paid = lot["total_paid"]
        mkt_val = round(shares * current_price, 2)
        profit = round(mkt_val - paid, 2)
        profit_pct = round((profit / paid * 100), 1) if paid > 0 else 0.0

        total_invested += paid
        total_market_val += mkt_val
        total_shares += shares
        total_gift_shares += lot["matching_shares"]

        lots_data.append({
            **lot,
            "market_value": mkt_val,
            "profit": profit,
            "profit_pct": profit_pct,
            "days_left": days_left,
            "progress_pct": progress_pct,
            "is_mature": today >= unlock_d,
            "effective_cost_per_share": round(paid / shares, 2) if shares > 0 else 0.0
        })

    total_profit = round(total_market_val - total_invested, 2)
    total_profit_pct = round((total_profit / total_invested * 100), 1) if total_invested > 0 else 0.0

    campaigns_list = []
    for yr in sorted(ESOP_CAMPAIGNS.keys(), reverse=True):
        c = ESOP_CAMPAIGNS[yr].copy()
        c["is_official"] = c["price"] is not None
        if c["price"] is None:
            c["price"] = current_price
        campaigns_list.append(c)

    sales_history = portfolio.get("sales_history", [])

    return jsonify({
        "quote": quote,
        "lots": lots_data,
        "sales_history": sales_history,
        "summary": {
            "total_shares": total_shares,
            "total_gift_shares": total_gift_shares,
            "total_invested": round(total_invested, 2),
            "total_market_val": round(total_market_val, 2),
            "total_profit": total_profit,
            "total_profit_pct": total_profit_pct,
            "total_sales_count": len(sales_history),
            "total_sales_net": round(sum(s.get("net_proceeds", 0) for s in sales_history), 2),
            "total_sales_gross": round(sum(s.get("gross_proceeds", 0) for s in sales_history), 2),
            "total_sales_tax": round(sum(s.get("tax", 0) for s in sales_history), 2),
            "total_sales_gain": round(sum(s.get("capital_gain", 0) for s in sales_history), 2),
        },
        "packages": OFFICIAL_PACKAGES,
        "campaigns": campaigns_list
    })


@app.route("/api/sell", methods=["POST"])
def execute_sale_api():
    data = request.json or {}
    lot_id = data.get("lot_id")
    if not lot_id:
        return jsonify({"error": "Debe especificar un lote"}), 400

    portfolio = load_portfolio()
    lots = portfolio.get("lots", [])
    lot_idx = next((i for i, l in enumerate(lots) if l["id"] == lot_id), None)
    if lot_idx is None:
        return jsonify({"error": "Lote no encontrado"}), 404

    lot = lots[lot_idx]
    max_shares = lot["total_shares"]
    try:
        shares_to_sell = int(data.get("shares_sold", max_shares))
    except (ValueError, TypeError):
        shares_to_sell = max_shares

    if shares_to_sell <= 0 or shares_to_sell > max_shares:
        return jsonify({"error": f"Cantidad no válida. Máximo disponible: {max_shares}"}), 400

    quote = fetch_live_price()
    default_price = quote["price"]
    try:
        sell_price = float(data.get("sell_price", default_price))
    except (ValueError, TypeError):
        sell_price = default_price

    sale_date = data.get("date") or date.today().strftime("%Y-%m-%d")

    fraction = shares_to_sell / max_shares
    purchased_sold = round(lot["purchased_shares"] * fraction, 2)
    matching_sold = round(lot["matching_shares"] * fraction, 2)
    cost_basis_sold = round(lot["total_paid"] * fraction, 2)

    gross_proceeds = round(shares_to_sell * sell_price, 2)
    capital_gain = round(gross_proceeds - cost_basis_sold, 2)
    tax = calculate_tax_spain(capital_gain)
    net_proceeds = round(gross_proceeds - tax, 2)

    unlock_d = datetime.strptime(lot["unlock_date"], "%Y-%m-%d").date()
    is_mature = datetime.strptime(sale_date, "%Y-%m-%d").date() >= unlock_d

    sale_record = {
        "id": f"SALE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "date": sale_date,
        "lot_id": lot["id"],
        "shares_sold": shares_to_sell,
        "sell_price": sell_price,
        "gross_proceeds": gross_proceeds,
        "cost_basis": cost_basis_sold,
        "capital_gain": capital_gain,
        "tax": tax,
        "net_proceeds": net_proceeds,
        "is_mature": is_mature,
        "notes": data.get("notes") or f"Venta de {shares_to_sell} acc de {lot['id']} a {sell_price:.2f} €"
    }

    if "sales_history" not in portfolio:
        portfolio["sales_history"] = []
    portfolio["sales_history"].insert(0, sale_record)

    if shares_to_sell == max_shares:
        lots.pop(lot_idx)
    else:
        lot["total_shares"] -= shares_to_sell
        lot["purchased_shares"] = round(lot["purchased_shares"] - purchased_sold, 2)
        lot["matching_shares"] = round(lot["matching_shares"] - matching_sold, 2)
        lot["total_paid"] = round(lot["total_paid"] - cost_basis_sold, 2)

    save_portfolio(portfolio)
    return jsonify({"success": True, "sale": sale_record})


@app.route("/api/sales/<sale_id>", methods=["DELETE"])
def delete_sale_api(sale_id):
    portfolio = load_portfolio()
    sales = portfolio.get("sales_history", [])
    new_sales = [s for s in sales if s.get("id") != sale_id]
    if len(new_sales) == len(sales):
        return jsonify({"error": "Venta no encontrada"}), 404
    portfolio["sales_history"] = new_sales
    save_portfolio(portfolio)
    return jsonify({"success": True, "deleted": sale_id})



@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.json or {}
    sell_price = float(data.get("price", 189.30))
    lot_id = data.get("lot_id", "ESOP-2024")
    reinvest_budget = float(data.get("reinvest_budget", 2500.0))

    portfolio = load_portfolio()
    lot = next((l for l in portfolio.get("lots", []) if l["id"] == lot_id), None)
    if not lot:
        return jsonify({"error": "Lote no encontrado"}), 404

    total_shares = lot["total_shares"]
    paid = lot["total_paid"]
    gross_proceeds = round(total_shares * sell_price, 2)
    capital_gain = round(gross_proceeds - paid, 2)
    tax = calculate_tax_spain(capital_gain)
    net_in_pocket = round(gross_proceeds - tax, 2)
    surplus_after_reinvest = round(net_in_pocket - reinvest_budget, 2)

    unlock_d = datetime.strptime(lot["unlock_date"], "%Y-%m-%d").date()
    is_mature = date.today() >= unlock_d

    return jsonify({
        "lot_id": lot["id"],
        "total_shares": total_shares,
        "purchased_shares": lot["purchased_shares"],
        "matching_shares": lot["matching_shares"],
        "sell_price": sell_price,
        "paid": paid,
        "gross_proceeds": gross_proceeds,
        "capital_gain": capital_gain,
        "tax": tax,
        "effective_tax_rate": round((tax / capital_gain * 100), 1) if capital_gain > 0 else 0.0,
        "net_in_pocket": net_in_pocket,
        "reinvest_budget": reinvest_budget,
        "surplus_after_reinvest": surplus_after_reinvest,
        "is_mature": is_mature,
        "unlock_date": lot["unlock_date"]
    })


@app.route("/api/lots", methods=["POST"])
def add_lot():
    data = request.json or {}
    year = int(data.get("year", 2024))
    camp_info = get_campaign_info(year)
    default_price = camp_info["price"] if camp_info.get("price") is not None else 189.30

    purchased = int(data.get("purchased_shares", 15))
    matching = int(data.get("matching_shares", 12))
    price_val = data.get("purchase_price")
    price = float(price_val) if price_val not in (None, "", 0) else default_price
    grant_date_str = data.get("grant_date") or camp_info["grant_date"]

    grant_d = datetime.strptime(grant_date_str, "%Y-%m-%d").date()
    unlock_d = date(grant_d.year + 3, grant_d.month, grant_d.day)
    today = date.today()
    status = "UNLOCKED" if today >= unlock_d else "LOCKED"

    notes = data.get("notes") or f"Paquete {purchased} + {matching} (Campaña {year}: {price:.2f} €/acc)"

    new_lot = {
        "id": f"ESOP-{year}",
        "year": year,
        "grant_date": grant_d.strftime("%Y-%m-%d"),
        "unlock_date": unlock_d.strftime("%Y-%m-%d"),
        "purchased_shares": purchased,
        "matching_shares": matching,
        "total_shares": purchased + matching,
        "purchase_price": price,
        "total_paid": round(purchased * price, 2),
        "status": status,
        "notes": notes
    }

    portfolio = load_portfolio()
    existing = [i for i, l in enumerate(portfolio["lots"]) if l["id"] == new_lot["id"]]
    if existing:
        portfolio["lots"][existing[0]] = new_lot
    else:
        portfolio["lots"].append(new_lot)

    save_portfolio(portfolio)
    return jsonify({"success": True, "lot": new_lot})


@app.route("/api/lots/<lot_id>", methods=["DELETE"])
def delete_lot_api(lot_id):
    portfolio = load_portfolio()
    lots = portfolio.get("lots", [])
    new_lots = [l for l in lots if l["id"] != lot_id]
    if len(new_lots) == len(lots):
        return jsonify({"error": "Lote no encontrado"}), 404
    portfolio["lots"] = new_lots
    save_portfolio(portfolio)
    return jsonify({"success": True, "deleted": lot_id})


@app.route("/download/calendar")
def download_calendar():
    if not CALENDAR_FILE.exists():
        from airbus_esop import export_calendar_events
        export_calendar_events()
    return send_file(CALENDAR_FILE, as_attachment=True, download_name="airbus_esop_recordatorios.ics")


def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def open_browser():
    webbrowser.open("http://127.0.0.1:5050")


if __name__ == "__main__":
    local_ip = get_local_ip()
    print("\n" + "="*70)
    print(" 🚀 INICIANDO AIRBUS ESOP DASHBOARD VISUAL (SINCRONIZADO)")
    print("="*70)
    print(" • En este Mac:                http://localhost:5050")
    print(f" • Desde tu tablet/móvil:      http://{local_ip}:5050")
    print(" • Datos compartidos en:       data/portfolio.json (Sincronizado al 100%)")
    print(" • Abriendo automáticamente en tu navegador...")
    print(" • Para detener el servidor, pulsa Ctrl + C en esta terminal.")
    print("="*70 + "\n")
    threading.Timer(1.0, open_browser).start()
    app.run(host="0.0.0.0", port=5050, debug=False)

