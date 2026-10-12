#!/usr/bin/env python3
"""
Airbus ESOP Tracker & Strategy Simulator (España)
Programa de gestión patrimonial, simulación fiscal y optimización de compras/ventas
para empleados de Airbus con participación en el Employee Share Ownership Plan (ESOP).
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, date
from pathlib import Path

# Constantes y Rutas
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "portfolio.json"
CALENDAR_FILE = BASE_DIR / "airbus_esop_recordatorios.ics"
TICKER_AIRBUS = "AIR.PA"  # Airbus SE en Euronext París

# Paquetes habituales ofrecidos por Airbus en los ESOP
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

# Historial oficial de campañas Airbus ESOP (Precios de suscripción oficiales en España / Pure Registered)
ESOP_CAMPAIGNS = {
    2027: {
        "year": 2027,
        "price": None,
        "grant_date": "2027-05-15",
        "unlock_date": "2030-05-15",
        "status": "Próxima Campaña (Estimada)",
        "notes": "Precio según cotización en directo al cierre de referencia"
    },
    2026: {
        "year": 2026,
        "price": 167.90,
        "grant_date": "2026-05-15",
        "unlock_date": "2029-05-15",
        "status": "Oficial (Revisado abril 2026)",
        "notes": "Precio inicial 200,65 € ajustado a 167,90 € por cláusula de protección a la baja"
    },
    2025: {
        "year": 2025,
        "price": 162.78,
        "grant_date": "2025-05-15",
        "unlock_date": "2028-05-15",
        "status": "Oficial (Revisado marzo 2025)",
        "notes": "Precio inicial 168,92 € ajustado a 162,78 € por cláusula de protección (167,62 € PEG)"
    },
    2024: {
        "year": 2024,
        "price": 150.26,
        "grant_date": "2024-05-15",
        "unlock_date": "2027-05-15",
        "status": "Oficial",
        "notes": "Precio oficial Pure Registered 150,26 € (149,20 € PEG)"
    },
    2023: {
        "year": 2023,
        "price": 119.06,
        "grant_date": "2023-05-15",
        "unlock_date": "2026-05-15",
        "status": "Oficial",
        "notes": "Precio oficial Pure Registered 119,06 € (116,68 € PEG)"
    },
    2022: {
        "year": 2022,
        "price": 117.88,
        "grant_date": "2022-05-15",
        "unlock_date": "2025-05-15",
        "status": "Oficial",
        "notes": "Precio oficial suscripción 117,88 €"
    },
    2021: {
        "year": 2021,
        "price": 93.90,
        "grant_date": "2021-05-15",
        "unlock_date": "2024-05-15",
        "status": "Oficial",
        "notes": "Precio oficial Pure Registered 93,90 € (89,52 € PEG)"
    },
    2020: {
        "year": 2020,
        "price": 136.60,
        "grant_date": "2020-05-15",
        "unlock_date": "2023-05-15",
        "status": "Oficial (Campaña reducida)",
        "notes": "Precio fijado 136,60 € (campaña impactada por pandemia COVID)"
    },
    2019: {
        "year": 2019,
        "price": 134.40,
        "grant_date": "2019-05-15",
        "unlock_date": "2022-05-15",
        "status": "Oficial",
        "notes": "Precio oficial SIP / ESOP 2019 (134,40 €)"
    },
    2018: {
        "year": 2018,
        "price": 89.52,
        "grant_date": "2018-05-15",
        "unlock_date": "2021-05-15",
        "status": "Oficial",
        "notes": "Precio oficial suscripción ESOP 2018 (89,52 €)"
    },
    2017: {
        "year": 2017,
        "price": 67.24,
        "grant_date": "2017-05-15",
        "unlock_date": "2020-05-15",
        "status": "Oficial",
        "notes": "Precio oficial suscripción ESOP 2017 (67,24 € / 66,80 €)"
    },
    2016: {
        "year": 2016,
        "price": 54.30,
        "grant_date": "2016-05-15",
        "unlock_date": "2019-05-15",
        "status": "Oficial",
        "notes": "Precio oficial suscripción ESOP 2016 (54,30 €)"
    },
    2015: {
        "year": 2015,
        "price": 51.63,
        "grant_date": "2015-05-15",
        "unlock_date": "2018-05-15",
        "status": "Oficial",
        "notes": "Precio oficial suscripción ESOP 2015 (51,63 €)"
    }
}

# Paquetes oficiales ofrecidos en los planes Airbus ESOP
OFFICIAL_PACKAGES = [
    {"id": "15+12", "purchased": 15, "matching": 12, "total": 27, "tag": "⭐ Paquete Estrella (España)", "desc": "15 compradas + 12 gratis (27 total) • Máx. regalo proporcional (44.4% dto.)"},
    {"id": "18+12", "purchased": 18, "matching": 12, "total": 30, "tag": "⭐ Paquete Clásico (2025/2026)", "desc": "18 compradas + 12 gratis (30 total) • 40% dto."},
    {"id": "3+2", "purchased": 3, "matching": 2, "total": 5, "tag": "Básico", "desc": "3 compradas + 2 gratis (5 total) • 40% dto."},
    {"id": "6+4", "purchased": 6, "matching": 4, "total": 10, "tag": "Básico", "desc": "6 compradas + 4 gratis (10 total) • 40% dto."},
    {"id": "9+6", "purchased": 9, "matching": 6, "total": 15, "tag": "Intermedio", "desc": "9 compradas + 6 gratis (15 total) • 40% dto."},
    {"id": "30+20", "purchased": 30, "matching": 20, "total": 50, "tag": "Avanzado", "desc": "30 compradas + 20 gratis (50 total) • 40% dto."},
    {"id": "42+28", "purchased": 42, "matching": 28, "total": 70, "tag": "Avanzado", "desc": "42 compradas + 28 gratis (70 total) • 40% dto."},
    {"id": "54+36", "purchased": 54, "matching": 36, "total": 90, "tag": "Alto", "desc": "54 compradas + 36 gratis (90 total) • 40% dto."},
    {"id": "72+48", "purchased": 72, "matching": 48, "total": 120, "tag": "Alto", "desc": "72 compradas + 48 gratis (120 total) • 40% dto."},
    {"id": "99+66", "purchased": 99, "matching": 66, "total": 165, "tag": "Máximo", "desc": "99 compradas + 66 gratis (165 total) • 40% dto."},
]


def get_campaign_info(year, current_price=189.30):
    """Devuelve la información de la campaña ESOP para un año dado, con precio oficial o estimado."""
    if year in ESOP_CAMPAIGNS:
        info = ESOP_CAMPAIGNS[year].copy()
        info["is_official"] = info["price"] is not None
        if info["price"] is None:
            info["price"] = round(float(current_price), 2)
        return info
    else:
        return {
            "year": year,
            "price": round(float(current_price), 2),
            "grant_date": f"{year}-05-15",
            "unlock_date": f"{year+3}-05-15",
            "status": "Estimación (En vivo)" if year >= 2027 else "No registrado",
            "notes": f"Estimación basada en cotización de mercado actual ({current_price:.2f} €)" if year >= 2027 else "Precio manual",
            "is_official": False
        }

# Tramos IRPF Base del Ahorro (España)
# (Límite superior, tipo impositivo marginal)
IRPF_SAVINGS_BRACKETS = [
    (6000.0, 0.19),
    (50000.0, 0.21),
    (200000.0, 0.23), # de 50.000 a 200.000
    (300000.0, 0.27), # de 200.000 a 300.000
    (float("inf"), 0.28) # más de 300.000
]


def clear_screen():
    print("\033[H\033[J", end="")


def format_currency(amount):
    if amount is None:
        return "N/A"
    return f"{amount:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def fetch_live_price(ticker=TICKER_AIRBUS):
    """Obtiene la cotización en vivo de Airbus desde Yahoo Finance API sin dependencias externas."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            meta = data["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice")
            prev_close = meta.get("chartPreviousClose", price)
            currency = meta.get("currency", "EUR")
            change = price - prev_close if price and prev_close else 0.0
            pct_change = (change / prev_close * 100) if prev_close else 0.0
            return {
                "success": True,
                "price": round(float(price), 2),
                "change": round(change, 2),
                "pct_change": round(pct_change, 2),
                "currency": currency,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "price": 189.30,  # Precio de referencia reciente como fallback
            "timestamp": "Modo sin conexión"
        }


def load_portfolio():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        initial_data = {
            "lots": [],
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
    """Calcula la retención aproximada de IRPF para la base del ahorro en España."""
    if capital_gain <= 0:
        return 0.0
    
    tax = 0.0
    remaining = capital_gain

    # Tramo 1: 0 - 6.000 al 19%
    t1 = min(remaining, 6000.0)
    tax += t1 * 0.19
    remaining -= t1

    # Tramo 2: 6.000 - 50.000 al 21%
    if remaining > 0:
        t2 = min(remaining, 44000.0)
        tax += t2 * 0.21
        remaining -= t2

    # Tramo 3: 50.000 - 200.000 al 23%
    if remaining > 0:
        t3 = min(remaining, 150000.0)
        tax += t3 * 0.23
        remaining -= t3

    # Tramo 4: 200.000 - 300.000 al 27%
    if remaining > 0:
        t4 = min(remaining, 100000.0)
        tax += t4 * 0.27
        remaining -= t4

    # Tramo 5: > 300.000 al 28%
    if remaining > 0:
        tax += remaining * 0.28

    return tax


def show_portfolio_status(current_price):
    portfolio = load_portfolio()
    today = date.today()

    print("\n" + "="*70)
    print(" 📊 ESTADO ACTUAL DE TU CARTERA AIRBUS ESOP")
    print("="*70)
    print(f" Cotización Airbus ({TICKER_AIRBUS}): {format_currency(current_price)}")
    print(f" Fecha de hoy: {today.strftime('%d/%m/%Y')}")
    print("-" * 70)

    total_invested = 0.0
    total_market_val = 0.0
    total_shares_count = 0
    total_free_shares = 0

    lots = portfolio.get("lots", [])
    if not lots:
        print("\n   ℹ️  Tu cartera está vacía. No tienes ningún paquete registrado todavía.")
        print("   Usa la opción [5] del menú para registrar tu primera compra ESOP.\n")

    for lot in lots:
        unlock_d = datetime.strptime(lot["unlock_date"], "%Y-%m-%d").date()
        grant_d = datetime.strptime(lot["grant_date"], "%Y-%m-%d").date()
        days_left = (unlock_d - today).days

        total_shares = lot["total_shares"]
        paid = lot["total_paid"]
        market_val = total_shares * current_price
        gross_profit = market_val - paid
        profit_pct = (gross_profit / paid * 100) if paid > 0 else 0

        total_invested += paid
        total_market_val += market_val
        total_shares_count += total_shares
        total_free_shares += lot["matching_shares"]

        print(f"\n📦 LOTE: {lot['id']} (Campaña {lot['year']})")
        print(f"   • Acciones: {total_shares} ({lot['purchased_shares']} pagadas + {lot['matching_shares']} de REGALO)")
        print(f"   • Precio de compra: {format_currency(lot['purchase_price'])} / Coste real por acción: {format_currency(paid / total_shares)}")
        print(f"   • Inversión salida de tu bolsillo: {format_currency(paid)}")
        print(f"   • Valor actual en mercado:        {format_currency(market_val)}")
        print(f"   • Ganancia bruta acumulada:       \033[92m+{format_currency(gross_profit)} (+{profit_pct:.1f}%)\033[0m")
        
        if days_left > 0:
            print(f"   • Estado: \033[93m🔒 BLOQUEADO\033[0m (Quedan {days_left} días hasta el {unlock_d.strftime('%d/%m/%Y')})")
        else:
            print(f"   • Estado: \033[92m🔓 DESBLOQUEADO (Listo para vender sin penalización fiscal)\033[0m")

    total_profit = total_market_val - total_invested
    total_pct = (total_profit / total_invested * 100) if total_invested > 0 else 0

    print("\n" + "="*70)
    print(" 📈 RESUMEN PATRIMONIAL TOTAL")
    print(f"   • Acciones acumuladas: {total_shares_count} (de las cuales {total_free_shares} han sido regaladas)")
    print(f"   • Capital total aportado: {format_currency(total_invested)}")
    print(f"   • Valor actual de mercado: {format_currency(total_market_val)}")
    print(f"   • Plusvalía total:       \033[92m+{format_currency(total_profit)} (+{total_pct:.1f}%)\033[0m")
    print("="*70 + "\n")


def simulate_sale(current_price):
    portfolio = load_portfolio()
    lots = portfolio.get("lots", [])
    if not lots:
        print("\n❌ No tienes lotes registrados en cartera.")
        return

    print("\n" + "="*70)
    print(" 💰 SIMULADOR DE VENTA Y FISCALIDAD (IRPF ESPAÑA)")
    print("="*70)
    for idx, lot in enumerate(lots, start=1):
        print(f" [{idx}] {lot['id']} - {lot['total_shares']} acciones ({lot['year']})")
    
    choice = input("\nSelecciona el número del lote a simular (o Enter para el lote 2024): ").strip()
    idx = int(choice) - 1 if choice.isdigit() and 1 <= int(choice) <= len(lots) else 0
    lot = lots[idx]

    price_input = input(f"\nPrecio de venta por acción [Enter para usar cotización actual {format_currency(current_price)}]: ").strip()
    try:
        sell_price = float(price_input.replace(",", ".")) if price_input else current_price
    except ValueError:
        sell_price = current_price

    total_shares = lot["total_shares"]
    paid = lot["total_paid"]
    gross_proceeds = total_shares * sell_price
    capital_gain = gross_proceeds - paid

    # Verificación de los 3 años de tenencia
    unlock_d = datetime.strptime(lot["unlock_date"], "%Y-%m-%d").date()
    today = date.today()
    is_mature = today >= unlock_d

    tax = calculate_tax_spain(capital_gain)
    net_in_pocket = gross_proceeds - tax

    print("\n" + "-"*70)
    print(f" RESULTADO DE LA SIMULACIÓN PARA {lot['id']} A {format_currency(sell_price)}:")
    print("-" * 70)
    print(f" • Acciones vendidas:                 {total_shares} ({lot['purchased_shares']} compradas + {lot['matching_shares']} regaladas)")
    print(f" • Dinero bruto cobrado de la venta:  {format_currency(gross_proceeds)}")
    print(f" • Dinero que tú pusiste en su día:   {format_currency(paid)}")
    print(f" • Ganancia patrimonial bruta:        \033[92m+{format_currency(capital_gain)}\033[0m")
    print(f" • Estimación impuestos IRPF ahorro:  -{format_currency(tax)}")
    print(f" • \033[1mDINERO LIMPIO EN TU CUENTA:\033[0m         \033[1;92m{format_currency(net_in_pocket)}\033[0m")
    print("-" * 70)

    if is_mature:
        print(" ✅ \033[92mCUMPLE EL PLAZO DE 3 AÑOS:\033[0m Las 12 acciones regaladas están 100% exentas de IRPF.")
    else:
        days_left = (unlock_d - today).days
        print(f" ⚠️  \033[93mATENCIÓN:\033[0m Faltan {days_left} días para cumplir los 3 años (fecha: {unlock_d.strftime('%d/%m/%Y')}).")
        print("     Si vendieras antes de esa fecha perderías la exención de las acciones regaladas.")

    print(f"\n💡 \033[1mEstrategia Rueda 2027:\033[0m")
    print(f"   Con los {format_currency(net_in_pocket)} netos, puedes pagar el ESOP 2027 (~2.500 €) y te")
    print(f"   quedarán unos \033[92m{format_currency(net_in_pocket - 2500)}\033[0m limpios para ahorrar o diversificar.")
    print("="*70)

    execute_now = input("\n¿Deseas registrar esta venta en tu cartera real ahora mismo? (s/N): ").strip().lower()
    if execute_now == 's':
        register_sale(current_price, default_lot_id=lot['id'], default_sell_price=sell_price)


def register_sale(current_price, default_lot_id=None, default_sell_price=None):
    portfolio = load_portfolio()
    lots = portfolio.get("lots", [])
    if not lots:
        print("\n❌ No tienes lotes en cartera para vender.")
        return

    print("\n" + "="*70)
    print(" 💸 REGISTRAR VENTA REAL DE ACCIONES AIRBUS")
    print("="*70)

    for idx, l in enumerate(lots, start=1):
        unlock_d = datetime.strptime(l["unlock_date"], "%Y-%m-%d").date()
        status_lbl = "🔓 DESBLOQUEADO" if date.today() >= unlock_d else f"🔒 BLOQUEADO (hasta {unlock_d.strftime('%d/%m/%Y')})"
        print(f" [{idx}] {l['id']} - {l['total_shares']} acciones disponibles | {status_lbl}")

    if default_lot_id:
        matching_idx = next((i for i, l in enumerate(lots) if l['id'] == default_lot_id), 0)
        choice = input(f"\nSelecciona el lote a vender [Enter para {default_lot_id}]: ").strip()
        idx = int(choice) - 1 if choice.isdigit() and 1 <= int(choice) <= len(lots) else matching_idx
    else:
        choice = input("\nSelecciona el número del lote a vender (o 'c' para cancelar): ").strip()
        if choice.lower() == 'c':
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(lots)):
            print("❌ Selección no válida.")
            return
        idx = int(choice) - 1

    lot = lots[idx]
    max_shares = lot["total_shares"]

    # Cantidad de acciones
    shares_input = input(f"Número de acciones a vender [Enter para todas: {max_shares}]: ").strip()
    try:
        shares_to_sell = int(shares_input) if shares_input else max_shares
    except ValueError:
        shares_to_sell = max_shares

    if shares_to_sell <= 0 or shares_to_sell > max_shares:
        print(f"❌ La cantidad debe estar entre 1 y {max_shares} acciones.")
        return

    # Precio de venta
    default_p = default_sell_price if default_sell_price else current_price
    p_input = input(f"Precio real de venta por acción [Enter para {format_currency(default_p)}]: ").strip()
    try:
        real_sell_price = float(p_input.replace(",", ".")) if p_input else default_p
    except ValueError:
        real_sell_price = default_p

    # Fecha de venta
    today_str = date.today().strftime("%Y-%m-%d")
    date_input = input(f"Fecha de la operación (AAAA-MM-DD) [Enter para hoy: {today_str}]: ").strip()
    sale_date = date_input if date_input else today_str

    # Proporción vendida y coste base deducible
    fraction = shares_to_sell / max_shares
    purchased_sold = round(lot["purchased_shares"] * fraction, 2)
    matching_sold = round(lot["matching_shares"] * fraction, 2)
    cost_basis_sold = round(lot["total_paid"] * fraction, 2)

    gross_proceeds = round(shares_to_sell * real_sell_price, 2)
    capital_gain = round(gross_proceeds - cost_basis_sold, 2)
    tax = calculate_tax_spain(capital_gain)
    net_proceeds = round(gross_proceeds - tax, 2)

    unlock_d = datetime.strptime(lot["unlock_date"], "%Y-%m-%d").date()
    is_mature = datetime.strptime(sale_date, "%Y-%m-%d").date() >= unlock_d

    print("\n" + "-"*70)
    print(" RESUMEN DE LA OPERACIÓN DE VENTA:")
    print(f" • Lote de origen:          {lot['id']}")
    print(f" • Acciones vendidas:        {shares_to_sell} de {max_shares}")
    print(f" • Precio de venta:          {format_currency(real_sell_price)}")
    print(f" • Cobro bruto:              {format_currency(gross_proceeds)}")
    print(f" • Coste de compra original: {format_currency(cost_basis_sold)}")
    print(f" • Plusvalía patrimonial:    \033[92m+{format_currency(capital_gain)}\033[0m")
    print(f" • IRPF estimado (España):   -{format_currency(tax)}")
    print(f" • Neto limpio en banco:     \033[1;92m{format_currency(net_proceeds)}\033[0m")
    if is_mature:
        print(" • Cumple 3 años:            ✅ SÍ (Exención IRPF regalo consolidada)")
    else:
        print(" • Cumple 3 años:            ⚠️ NO (Venta anticipada, regalo no exento)")
    print("-" * 70)

    confirm = input("¿Confirmas la ejecución y registro de esta venta? (s/N): ").strip().lower()
    if confirm != 's':
        print("❌ Operación cancelada por el usuario.")
        return

    # Registrar en sales_history
    sale_record = {
        "id": f"SALE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "date": sale_date,
        "lot_id": lot["id"],
        "shares_sold": shares_to_sell,
        "sell_price": real_sell_price,
        "gross_proceeds": gross_proceeds,
        "cost_basis": cost_basis_sold,
        "capital_gain": capital_gain,
        "tax": tax,
        "net_proceeds": net_proceeds,
        "is_mature": is_mature,
        "notes": f"Venta de {shares_to_sell} acc de {lot['id']} a {real_sell_price:.2f} €"
    }

    if "sales_history" not in portfolio:
        portfolio["sales_history"] = []
    portfolio["sales_history"].insert(0, sale_record)

    # Actualizar o eliminar lote
    if shares_to_sell == max_shares:
        lots.pop(idx)
        print(f"\n✅ Lote {lot['id']} liquidado en su totalidad y retirado de cartera activa.")
    else:
        lot["total_shares"] -= shares_to_sell
        lot["purchased_shares"] = round(lot["purchased_shares"] - purchased_sold, 2)
        lot["matching_shares"] = round(lot["matching_shares"] - matching_sold, 2)
        lot["total_paid"] = round(lot["total_paid"] - cost_basis_sold, 2)
        print(f"\n✅ Lote {lot['id']} actualizado. Quedan {lot['total_shares']} acciones en cartera.")

    save_portfolio(portfolio)
    print(f"✅ Venta registrada en el historial con ID {sale_record['id']}.")
    print("="*70 + "\n")


def show_sales_history():
    portfolio = load_portfolio()
    sales = portfolio.get("sales_history", [])
    print("\n" + "="*75)
    print(" 📜 HISTORIAL DE VENTAS Y GANANCIAS PATRIMONIALES (IRPF)")
    print("="*75)
    if not sales:
        print(" No tienes ventas registradas hasta el momento.")
        print(" Puedes registrar una desde la opción [3] o simulando en [2].")
        print("="*75 + "\n")
        return

    total_gross = sum(s.get("gross_proceeds", 0) for s in sales)
    total_gain = sum(s.get("capital_gain", 0) for s in sales)
    total_tax = sum(s.get("tax", 0) for s in sales)
    total_net = sum(s.get("net_proceeds", 0) for s in sales)

    print(f"{'Fecha':<10} | {'Lote':<10} | {'Acc.':<5} | {'Precio':<9} | {'Cobro Bruto':<12} | {'Plusvalía':<12} | {'IRPF':<10} | {'Neto':<11}")
    print("-" * 75)
    for s in sales:
        d = s.get("date", "-")
        l_id = s.get("lot_id", "-")
        sh = s.get("shares_sold", 0)
        p = format_currency(s.get("sell_price", 0))
        gross = format_currency(s.get("gross_proceeds", 0))
        gain = f"+{format_currency(s.get('capital_gain', 0))}"
        tax = f"-{format_currency(s.get('tax', 0))}"
        net = format_currency(s.get("net_proceeds", 0))
        print(f"{d:<10} | {l_id:<10} | {sh:<5} | {p:<9} | {gross:<12} | {gain:<12} | {tax:<10} | {net:<11}")

    print("-" * 75)
    print(f" TOTALES ACUMULADOS EN VENTAS:")
    print(f" • Cobro bruto acumulado:     {format_currency(total_gross)}")
    print(f" • Plusvalía fiscal total:    +{format_currency(total_gain)}")
    print(f" • Impuestos IRPF estimados:  -{format_currency(total_tax)}")
    print(f" • \033[1;92mDINERO LIMPIO TOTAL COBRADO: {format_currency(total_net)}\033[0m")
    print("="*75 + "\n")


def optimize_esop_purchase(current_price):
    print("\n" + "="*70)
    print(" 🎯 CALCULADORA Y OPTIMIZADOR DE COMPRA ESOP 2027")
    print("="*70)
    print(" Airbus ofrece paquetes fijos con acciones de regalo (matching shares).")
    
    price_input = input(f"Cotización estimada de Airbus para 2027 [Enter para {format_currency(current_price)}]: ").strip()
    try:
        est_price = float(price_input.replace(",", ".")) if price_input else current_price
    except ValueError:
        est_price = current_price

    budget_input = input("Presupuesto que quieres destinar [Enter para 2.500 €]: ").strip()
    try:
        budget = float(budget_input.replace(",", ".")) if budget_input else 2500.0
    except ValueError:
        budget = 2500.0

    print("\n" + "-"*75)
    print(f"{'Paquete':<9} | {'Compradas':<9} | {'Regalo':<7} | {'Total':<6} | {'Coste (€)':<12} | {'Descuento (%)':<13} | {'Estado':<10}")
    print("-" * 75)

    best_pkg = None
    min_diff = float("inf")

    for pkg in DEFAULT_PACKAGES:
        cost = pkg["purchased"] * est_price
        discount_pct = (pkg["matching"] / pkg["total"]) * 100
        diff = abs(cost - budget)

        flag = ""
        if cost <= budget:
            flag = "En rango"
            if diff < min_diff:
                min_diff = diff
                best_pkg = pkg
        else:
            flag = "Supera"

        print(f"Paquete {pkg['id']:<1} | {pkg['purchased']:<9} | {pkg['matching']:<7} | {pkg['total']:<6} | {format_currency(cost):<12} | {discount_pct:>6.1f}%       | {flag:<10}")

    print("-" * 75)
    if best_pkg:
        cost_best = best_pkg["purchased"] * est_price
        val_best = best_pkg["total"] * est_price
        print(f"\n🌟 \033[1;92mPAQUETE RECOMENDADO:\033[0m Paquete {best_pkg['id']} ({best_pkg['purchased']} pagadas + {best_pkg['matching']} gratis = {best_pkg['total']} acciones)")
        print(f" • Coste a pagar:            {format_currency(cost_best)}")
        print(f" • Valor de mercado recibido: {format_currency(val_best)}")
        print(f" • Regalo directo de Airbus:  \033[92m+{format_currency(val_best - cost_best)}\033[0m")
        print(f" • Margen de tu presupuesto:  Te sobran {format_currency(budget - cost_best)}")
    print("="*70 + "\n")


def export_calendar_events():
    """Genera un archivo estándar .ics compatible con Mac Calendar, Google Calendar y Outlook."""
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Airbus ESOP Manager//ES
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
SUMMARY:✈️ Apertura Campaña Airbus ESOP 2027
DESCRIPTION:Revisar precios de referencia y paquetes en el portal de empleados (ESP/Equiniti) para suscribir el nuevo paquete anual.
DTSTART;VALUE=DATE:20270215
DTEND;VALUE=DATE:20270216
STATUS:CONFIRMED
TRANSP:TRANSPARENT
END:VEVENT
BEGIN:VEVENT
SUMMARY:🔓 Fin Bloqueo 3 Años ESOP 2024 (Venta disponible sin penalización fiscal)
DESCRIPTION:Se cumplen los 3 años de tenencia de las 27 acciones de 2024. Ya se pueden vender con exención total de las 12 acciones regaladas en IRPF.
DTSTART;VALUE=DATE:20270515
DTEND;VALUE=DATE:20270516
STATUS:CONFIRMED
TRANSP:TRANSPARENT
END:VEVENT
END:VCALENDAR
"""
    with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
        f.write(ics_content)

    print("\n" + "="*70)
    print(" 📅 RECORDATORIOS EXPORTADOS CON ÉXITO")
    print("="*70)
    print(f" Se ha generado el archivo:\n \033[1m{CALENDAR_FILE}\033[0m")
    print("\n Incluye:")
    print(" 1. Feb 2027: Apertura de suscripción al ESOP 2027.")
    print(" 2. 15 Mayo 2027: Fin de los 3 años de bloqueo del paquete 2024 (Listo para vender).")
    print("\n 👉 Para añadirlo a tu calendario en Mac, simplemente haz doble clic en el archivo.")
    print("="*70 + "\n")


def show_campaigns_history(current_price=189.30):
    """Muestra una tabla con el histórico de precios oficiales de suscripción de campañas ESOP."""
    print("\n" + "="*80)
    print(" 📋 HISTÓRICO OFICIAL DE PRECIOS DE CAMPAÑAS AIRBUS ESOP (ESPAÑA)")
    print("="*80)
    print(f" Cotización actual de Airbus (AIR.PA): {format_currency(current_price)}")
    print(" Los precios oficiales son fijados en febrero de cada año por el Consejo de Administración.")
    print("-" * 80)
    print(f" {'Año':<6} | {'Precio (€)':<12} | {'Entrega':<11} | {'Desbloqueo':<11} | {'Estado Legal':<13} | {'Detalles'}")
    print("-" * 80)

    today = date.today()
    for yr in sorted(ESOP_CAMPAIGNS.keys(), reverse=True):
        camp = ESOP_CAMPAIGNS[yr]
        unlock_d = datetime.strptime(camp["unlock_date"], "%Y-%m-%d").date()
        is_mature = today >= unlock_d
        status_str = "\033[92m🔓 LIBRE\033[0m" if is_mature else "\033[93m🔒 BLOQUEADO\033[0m"
        p_val = camp["price"]
        p_str = format_currency(p_val) if p_val is not None else f"~{format_currency(current_price)}*"
        print(f" {camp['year']:<6} | {p_str:<12} | {camp['grant_date']}  | {camp['unlock_date']}  | {status_str:<22} | {camp['notes']}")

    print("-" * 80)
    print(" ℹ️  Cláusula de protección: en 2025 y 2026, Airbus incluyó protección a la baja:")
    print("    si la acción cotizaba más baja en la fecha de entrega, se aplicaba el precio menor.")
    print("="*80 + "\n")


def add_or_edit_lot(current_price=189.30):
    print("\n" + "="*75)
    print(" ➕ REGISTRAR O EDITAR UN LOTE ESOP")
    print("="*75)
    portfolio = load_portfolio()
    
    # 1. Menú interactivo de Campañas / Años
    years_order = [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2027]
    print(" 📅 Selecciona el año de la campaña ESOP:")
    today = date.today()
    for idx, yr in enumerate(years_order, start=1):
        camp = ESOP_CAMPAIGNS.get(yr, {})
        p = camp.get("price")
        p_str = format_currency(p) if p else f"~{format_currency(current_price)} (estimado)"
        def_tag = " ⭐ [Recomendado / Habitual]" if yr == 2024 else ""
        unlock_d = datetime.strptime(camp.get("unlock_date", f"{yr+3}-05-15"), "%Y-%m-%d").date()
        status_tag = "🔓 Libre" if today >= unlock_d else f"🔒 Bloqueado hasta {unlock_d.strftime('%d/%m/%Y')}"
        print(f"   [{idx:>2}] Campaña {yr:<4} ➔  {p_str:<15} ({status_tag}){def_tag}")
    print("   [ O] Otro año no listado")

    choice_yr = input("\n Elige el número de campaña (1-13 o Enter para 2024 [opción 3]): ").strip().lower()
    if not choice_yr:
        selected_year = 2024
    elif choice_yr == 'o':
        manual_yr = input(" Introduce el año (ej. 2014): ").strip()
        selected_year = int(manual_yr) if manual_yr.isdigit() else 2024
    elif choice_yr.isdigit() and 1 <= int(choice_yr) <= len(years_order):
        selected_year = years_order[int(choice_yr) - 1]
    elif choice_yr.isdigit() and int(choice_yr) in ESOP_CAMPAIGNS:
        selected_year = int(choice_yr)
    else:
        selected_year = 2024

    camp_info = get_campaign_info(selected_year, current_price)
    auto_price = camp_info["price"] if camp_info.get("price") is not None else round(float(current_price), 2)
    auto_grant = camp_info["grant_date"]
    auto_unlock = camp_info["unlock_date"]

    print(f"\n ✔️  Año seleccionado: \033[1;92mESOP {selected_year}\033[0m")
    print(f"    • Precio suscripción oficial fijado: \033[1;92m{format_currency(auto_price)}\033[0m")
    print(f"    • Fecha de concesión: {auto_grant}  |  Desbloqueo legal: {auto_unlock}")
    if camp_info.get("notes"):
        print(f"    • Detalles: {camp_info['notes']}")

    # 2. Menú de Paquetes Oficiales Ofertados
    print("\n 📦 Selecciona el paquete ofertado por Airbus que compraste:")
    for idx, pkg in enumerate(OFFICIAL_PACKAGES, start=1):
        def_tag = " ⭐ [Por defecto]" if pkg["id"] == "15+12" else ""
        total_cost = pkg["purchased"] * auto_price
        print(f"   [{idx:>2}] {pkg['tag']:<12} : {pkg['purchased']:>2} compradas + {pkg['matching']:>2} gratis = {pkg['total']:>3} acc  (Coste: {format_currency(total_cost)}){def_tag}")
    print("   [ P] Paquete personalizado (introducir cantidades manuales)")

    choice_pkg = input("\n Elige el paquete (1-10 o Enter para Paquete Estrella 15+12): ").strip().lower()
    if not choice_pkg:
        chosen_pkg = OFFICIAL_PACKAGES[0] # 15+12
        purchased = chosen_pkg["purchased"]
        matching = chosen_pkg["matching"]
        notes = chosen_pkg["desc"]
    elif choice_pkg == 'p':
        p_in = input(" Número de acciones compradas de tu bolsillo: ").strip()
        m_in = input(" Número de acciones de regalo (matching shares): ").strip()
        purchased = int(p_in) if p_in.isdigit() else 15
        matching = int(m_in) if m_in.isdigit() else 12
        notes = f"Paquete personalizado {purchased} + {matching}"
    elif choice_pkg.isdigit() and 1 <= int(choice_pkg) <= len(OFFICIAL_PACKAGES):
        chosen_pkg = OFFICIAL_PACKAGES[int(choice_pkg) - 1]
        purchased = chosen_pkg["purchased"]
        matching = chosen_pkg["matching"]
        notes = chosen_pkg["desc"]
    else:
        chosen_pkg = OFFICIAL_PACKAGES[0]
        purchased = chosen_pkg["purchased"]
        matching = chosen_pkg["matching"]
        notes = chosen_pkg["desc"]

    # Cálculo automático completo
    total_shares = purchased + matching
    total_paid = round(purchased * auto_price, 2)
    grant_d = datetime.strptime(auto_grant, "%Y-%m-%d").date()
    unlock_d = datetime.strptime(auto_unlock, "%Y-%m-%d").date()
    is_mature = today >= unlock_d
    status = "UNLOCKED" if is_mature else "LOCKED"

    # Resumen interactivo
    print("\n" + "-"*75)
    print(" 🧾 RESUMEN DEL LOTE A GUARDAR:")
    print(f"    • Identificador:    ESOP-{selected_year}")
    print(f"    • Acciones pagadas: {purchased} acc. × {format_currency(auto_price)} = {format_currency(total_paid)}")
    print(f"    • Acciones regalo:  {matching} acc. (100% GRATIS por Airbus)")
    print(f"    • Total acciones:   {total_shares} acc.")
    print(f"    • Coste medio real: {format_currency(total_paid / total_shares)} / acc. (descuento efectivo: {(matching/total_shares*100):.1f}%)")
    val_mercado = round(total_shares * current_price, 2)
    ganancia = round(val_mercado - total_paid, 2)
    unlock_str = unlock_d.strftime("%d/%m/%Y")
    status_desc = "🔓 DESBLOQUEADO (Disponible para venta)" if is_mature else f"🔒 BLOQUEADO hasta {unlock_str}"
    print(f"    • Estado:           {status_desc}")
    print("-" * 75)

    confirm = input(" ¿Deseas guardar este lote? [Enter para SÍ / 'm' para modificar precio o fecha / 'c' para cancelar]: ").strip().lower()
    if confirm == 'c':
        print("❌ Registro cancelado.")
        return

    final_price = auto_price
    final_grant = auto_grant
    if confirm == 'm':
        p_edit = input(f" Precio de compra [Enter para {auto_price:.2f}]: ").strip()
        if p_edit:
            try:
                final_price = float(p_edit.replace(",", "."))
            except ValueError:
                pass
        g_edit = input(f" Fecha de concesión [Enter para {auto_grant}]: ").strip()
        if g_edit:
            try:
                grant_d = datetime.strptime(g_edit, "%Y-%m-%d").date()
                unlock_d = date(grant_d.year + 3, grant_d.month, grant_d.day)
                final_grant = grant_d.strftime("%Y-%m-%d")
                auto_unlock = unlock_d.strftime("%Y-%m-%d")
                status = "UNLOCKED" if today >= unlock_d else "LOCKED"
            except ValueError:
                pass
        total_paid = round(purchased * final_price, 2)

    new_lot = {
        "id": f"ESOP-{selected_year}",
        "year": selected_year,
        "grant_date": final_grant,
        "unlock_date": auto_unlock,
        "purchased_shares": purchased,
        "matching_shares": matching,
        "total_shares": total_shares,
        "purchase_price": final_price,
        "total_paid": total_paid,
        "status": status,
        "notes": f"Paquete {purchased} + {matching} ({notes})"
    }

    # Reemplazar si ya existe o añadir
    existing = [i for i, l in enumerate(portfolio["lots"]) if l["id"] == new_lot["id"]]
    if existing:
        portfolio["lots"][existing[0]] = new_lot
        print(f"\n✅ Lote {new_lot['id']} actualizado con éxito ({total_shares} acc a {format_currency(final_price)}).")
    else:
        portfolio["lots"].append(new_lot)
        print(f"\n✅ Lote {new_lot['id']} registrado con éxito ({total_shares} acc a {format_currency(final_price)}).")

    save_portfolio(portfolio)
    print("="*75 + "\n")


def delete_lot():
    print("\n" + "="*70)
    print(" 🗑️  ELIMINAR UN LOTE ESOP")
    print("="*70)
    portfolio = load_portfolio()
    lots = portfolio.get("lots", [])
    if not lots:
        print("❌ No hay lotes registrados para eliminar.")
        return

    for idx, lot in enumerate(lots, start=1):
        print(f" [{idx}] {lot['id']} - {lot['total_shares']} acciones (Año {lot['year']})")

    choice = input("\nIntroduce el número del lote a eliminar (o 'c' para cancelar): ").strip()
    if choice.lower() == 'c':
        return

    if choice.isdigit() and 1 <= int(choice) <= len(lots):
        del_lot = lots.pop(int(choice) - 1)
        save_portfolio(portfolio)
        print(f"\n✅ Lote {del_lot['id']} eliminado con éxito de data/portfolio.json.")
    else:
        print("❌ Selección no válida.")
    print("="*70 + "\n")


def show_faq():
    """Apartado de preguntas frecuentes, explicaciones detalladas y guía estratégica."""
    while True:
        print("\n" + "="*75)
        print(" ❓ PREGUNTAS FRECUENTES (FAQ) Y GUÍA ESTRATÉGICA AIRBUS ESOP")
        print("="*75)
        print(" [1] 🚨 ¿Por qué NO es bueno acumular acciones y SÍ venderlas al desbloquear?")
        print(" [2] 📖 Guía detallada de cada opción del programa (Opciones 1 a 5)")
        print(" [3] 💶 Fiscalidad en España: ¿Cómo tributan el regalo y la venta en el IRPF?")
        print(" [4] 🖥️ ¿Cómo se ejecutan las compras y ventas en la práctica (Equiniti)?")
        print(" [5] 📋 Histórico oficial de precios de campañas Airbus ESOP (2017 - 2026)")
        print(" [0] ↩️  Volver al menú principal")
        print("="*75)

        subchoice = input("\nElige una pregunta (0-5): ").strip()

        if subchoice == "0":
            break
        elif subchoice == "1":
            print("\n" + "-"*75)
            print(" 🚨 ¿POR QUÉ NO ES BUENO ACUMULAR ACCIONES Y SÍ VENDERLAS AL DESBLOQUEAR?")
            print("-" * 75)
            print("""
 1. EL RIESGO DE CONCENTRACIÓN (EL DOBLE PELIGRO):
    • Tu sueldo mensual ya depende al 100% de Airbus.
    • Si además vas acumulando acciones año tras año sin vender nunca, al cabo de
      unos años tendrás decenas de miles de euros metidos en la misma compañía.
    • Si el sector aeronáutico sufre una crisis profunda (pandemias, problemas
      graves de suministros, caída global de aerolíneas), pondrías en riesgo
      TU EMPLEO Y TUS AHORROS al mismo tiempo. No pongas todos los huevos en la
      misma cesta.

 2. EL BENEFICIO YA ESTÁ CAPTURADO CON EL REGALO (+44%):
    • Al comprar con un regalo de 12 acciones por cada 15 que pagas, tu coste
      medio es un ~44% inferior al precio de mercado.
    • El objetivo de un plan de acciones para empleados NO es especular en bolsa
      buscando "máximos históricos" impredecibles, sino RECOLECTAR EL DINERO GRATIS
      que te regala la empresa y asegurarlo.
    • Vender al cumplir los 3 años consolida ese beneficio en dinero real.

 3. NO TE PIERDES EL CRECIMIENTO FUTURO DE AIRBUS:
    • Vender el paquete maduro (ej. 2024) NO significa desvincularse de Airbus,
      porque con ese dinero compras el paquete nuevo del año en curso (ej. 2027).
    • ¡Sigues teniendo decenas de acciones de Airbus trabajando para ti! Pero
      vas retirando las ganancias consolidadas en vez de acumular riesgo.

 4. LA RUEDA DE AUTOFINANCIACIÓN:
    • Vender el lote de 2024 en 2027 te permite pagar íntegramente el ESOP 2027
      sin tocar ni un solo euro de tu nómina.
    • El dinero sobrante te permite diversificar en fondos indexados globales
      (como MSCI World o S&P 500) o amortizar hipoteca, blindando tu patrimonio.
""")
            input("Presiona Enter para volver a las FAQ...")
        elif subchoice == "2":
            print("\n" + "-"*75)
            print(" 📖 GUÍA DETALLADA DE CADA OPCIÓN DEL PROGRAMA (1 A 5)")
            print("-" * 75)
            print("""
 • [OPCIÓN 1] Ver estado de mi cartera ESOP:
   Conecta con la cotización oficial de Euronext París (AIR.PA) en directo.
   Calcula al instante cuánto valen hoy tus acciones, cuánto dinero pusiste,
   cuántas te regalaron, tu ganancia acumulada y cuántos días faltan exactamente
   para que el paquete quede libre de penalización fiscal.

 • [OPCIÓN 2] Simular venta y fiscalidad (IRPF España):
   Calcula cuánto dinero limpio en cuenta bancaria te quedaría tras vender.
   Descuenta automáticamente los impuestos del IRPF (base del ahorro al 19%-21%)
   y te avisa si el paquete ya ha cumplido los 3 años de exención fiscal o cuántos
   días le faltan para no perder la exención de las 12 acciones gratis.

 • [OPCIÓN 3] Optimizador de compra ESOP 2027:
   Compara los paquetes habituales de Airbus (3+2, 6+4, 15+12, etc.) con la
   cotización y tu presupuesto. Te recomienda qué paquete elegir para maximizar
   el regalo y calcula cuánto dinero sobrante de la venta de 2024 te queda libre.

 • [OPCIÓN 4] Exportar recordatorios a Calendario (.ics):
   Genera un archivo estándar que puedes abrir con doble clic en tu Mac o iPhone
   para agendar automáticamente las alertas:
   1) En Febrero 2027: Apertura de la suscripción al nuevo ESOP 2027.
   2) En Mayo 2027: Fin de los 3 años de bloqueo del paquete 2024 (apto para venta).

 • [OPCIÓN 5] Registrar nueva compra o editar lote:
   Es tu cuaderno de contabilidad con detección automática del precio oficial fijado
   por Airbus para cada campaña anual (ej. 2024 -> 150,26 €, 2025 -> 162,78 €).
""")
            input("Presiona Enter para volver a las FAQ...")
        elif subchoice == "3":
            print("\n" + "-"*75)
            print(" 💶 FISCALIDAD EN ESPAÑA: ¿CÓMO TRIBUTAN EL REGALO Y LA VENTA?")
            print("-" * 75)
            print("""
 1. EXENCIÓN DE LAS ACCIONES REGALADAS (MATCHING SHARES):
    • El Artículo 42.3.f de la Ley del IRPF establece que la entrega de acciones
      a trabajadores está EXENTA de tributar como retribución en especie hasta
      un límite de 12.000 € al año.
    • Requisito obligatorio: Mantener las acciones durante al menos 3 años.
    • Como tu regalo fue de ~1.800 €, NO pagas nada a Hacienda por el regalo,
      siempre que no las vendas antes de cumplir los 3 años.

 2. TRIBUTACIÓN CUANDO VENDES (BASE DEL AHORRO):
    • Cuando vendes tras los 3 años, tributas como ganancia patrimonial:
      Ganancia neta = Total cobrado de la venta - Lo que tú pagaste de tu bolsillo.
    • Tramos del ahorro en España:
      - Hasta 6.000 € de ganancia: 19%
      - De 6.000 € a 50.000 €: 21%
    • Ejemplo: Si pagaste 2.254 € y vendes las 27 acciones por 5.000 €, tu ganancia
      es de 2.746 €. Tributas el 19% (~521 €) y te quedan LIMPIOS unos 4.479 €.
""")
            input("Presiona Enter para volver a las FAQ...")
        elif subchoice == "4":
            print("\n" + "-"*75)
            print(" 🖥️ ¿CÓMO SE EJECUTAN LAS OPERACIONES REALES (EQUINITI / ESP)?")
            print("-" * 75)
            print("""
 • Las operaciones no se hacen dentro de este programa, sino en el portal oficial
   de custodia de Airbus para empleados (habitualmente Equiniti / ESP Portal).

 • Para comprar (Campaña anual en primavera):
   1. Entras con tus credenciales de empleado en el portal indicado por RRHH.
   2. Seleccionas el paquete elegido (ej. 15 compradas + 12 de regalo).
   3. Autorizas el cobro (descuento en nómina o transferencia).

 • Para vender (Al cumplirse los 3 años):
   1. Inicias sesión en Equiniti / ESP Portal.
   2. Verás que el lote de 2024 pasa del estado 'Locked/Bloqueado' a 'Available'.
   3. Seleccionas 'Sell / Vender' e introduces tu cuenta bancaria.
   4. El dinero de la venta se ingresa directamente en tu cuenta en 2-4 días hábiles.
""")
            input("Presiona Enter para volver a las FAQ...")
        elif subchoice == "5":
            show_campaigns_history()
            input("Presiona Enter para volver a las FAQ...")
        else:
            print("Opción no válida. Inténtalo de nuevo.")


def main():
    while True:
        # Obtenemos precio de Airbus
        quote_data = fetch_live_price()
        current_price = quote_data["price"]

        print("\n" + "="*70)
        print(" ✈️  AIRBUS ESOP - GESTOR Y SIMULADOR FINANCIERO")
        print("="*70)
        print(f" Cotización AIR.PA: {format_currency(current_price)} "
              f"({'+' if quote_data.get('change', 0) >= 0 else ''}{quote_data.get('change', 0):.2f} € / "
              f"{quote_data.get('pct_change', 0):.2f}%)  [{quote_data.get('timestamp')}]")
        print("-" * 70)
        print(" [1] 📊 Ver estado de mi cartera ESOP (valor actual, rentabilidad y bloqueo)")
        print(" [2] 💰 Simular venta de lote (cálculo IRPF y beneficio limpio)")
        print(" [3] 💸 Registrar venta real de acciones (descuenta cartera y guarda IRPF)")
        print(" [4] 📜 Historial de ventas y fiscalidad liquidada")
        print(" [5] 🎯 Optimizador de compra ESOP 2027 (recomendar paquete según presupuesto)")
        print(" [6] 📅 Exportar recordatorios a Calendario (.ics para Mac / Google Calendar)")
        print(" [7] ➕ Registrar nueva compra o editar lote (precio oficial automático)")
        print(" [8] 🗑️  Eliminar un lote")
        print(" [9] 📋 Ver histórico de precios de campañas ESOP (2017 - 2026)")
        print(" [10] ❓ Preguntas Frecuentes (FAQ) y Guía Estratégica")
        print(" [11] 🚪 Salir")
        print("="*70)

        choice = input("\nElige una opción (1-11): ").strip()

        if choice == "1":
            show_portfolio_status(current_price)
            input("Presiona Enter para continuar...")
        elif choice == "2":
            simulate_sale(current_price)
            input("Presiona Enter para continuar...")
        elif choice == "3":
            register_sale(current_price)
            input("Presiona Enter para continuar...")
        elif choice == "4":
            show_sales_history()
            input("Presiona Enter para continuar...")
        elif choice == "5":
            optimize_esop_purchase(current_price)
            input("Presiona Enter para continuar...")
        elif choice == "6":
            export_calendar_events()
            input("Presiona Enter para continuar...")
        elif choice == "7":
            add_or_edit_lot(current_price)
            input("Presiona Enter para continuar...")
        elif choice == "8":
            delete_lot()
            input("Presiona Enter para continuar...")
        elif choice == "9":
            show_campaigns_history(current_price)
            input("Presiona Enter para continuar...")
        elif choice == "10":
            show_faq()
        elif choice == "11":
            print("\n¡Hasta pronto! Que tengas buen día.\n")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        quote = fetch_live_price()
        show_portfolio_status(quote["price"])
    else:
        main()

