from bs4 import BeautifulSoup
import re
from pathlib import Path

BASE_DIR = Path("/Users/joseantonio/Developer/airbus_esop")
INDEX_PATH = BASE_DIR / "index.html"
OUT_DESKTOP = Path("/Users/joseantonio/Desktop/Airbus_ESOP.html")

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

panel_ventas = soup.find(id="panel-ventas")
panel_simulador = soup.find(id="panel-simulador")
panel_optimizador = soup.find(id="panel-optimizador")
panel_guia = soup.find(id="panel-guia")

# Extract panel_ventas from wherever it is
if panel_ventas:
    panel_ventas.extract()
    # Insert panel_ventas right after panel_simulador
    panel_simulador.insert_after(panel_ventas)

# Renumber section headings
# 1. Cartera
# 2. Simulador
# 3. Ventas
# 4. Optimizador
# 5. Guia
h2_ventas = panel_ventas.find("h2") if panel_ventas else None
if h2_ventas:
    h2_ventas.string = "3. Historial de Ventas y Liquidación Fiscal"

h2_opt = panel_optimizador.find("h2") if panel_optimizador else None
if h2_opt:
    h2_opt.string = "4. Optimizador de Compra ESOP 2027"

h2_guia = panel_guia.find("h2") if panel_guia else None
if h2_guia:
    h2_guia.string = "5. Guía Estratégica y Preguntas Frecuentes"

# Check parent of panel_ventas now
print("New parent of panel_ventas:", panel_ventas.parent.name, panel_ventas.parent.get("class"))

# Add prominent "Registrar Venta" button in Header Desktop & Mobile
header = soup.find("header")
if header:
    # Desktop actions
    header_desktop_actions = header.find("div", class_=lambda c: c and "sm:justify-end" in c)
    if header_desktop_actions:
        existing_sale_btn = header_desktop_actions.find("button", onclick="openSaleModal()")
        if not existing_sale_btn:
            btn_html = '''<button onclick="openSaleModal()" class="hidden sm:inline-flex items-center space-x-1.5 text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white px-3.5 py-2 rounded-xl shadow-sm transition">
              <i data-lucide="wallet" class="w-3.5 h-3.5"></i>
              <span>💸 Registrar Venta</span>
            </button>'''
            btn_tag = BeautifulSoup(btn_html, "html.parser").find("button")
            # insert before "Registrar Lote"
            lote_btn = header_desktop_actions.find("button", onclick="openLotModal()")
            if lote_btn:
                lote_btn.insert_before(btn_tag)
            else:
                header_desktop_actions.append(btn_tag)

    # Mobile actions
    mobile_actions = header.find("div", class_=lambda c: c and "sm:hidden" in c)
    if mobile_actions:
        existing_mobile_btn = mobile_actions.find("button", onclick="openSaleModal()")
        if not existing_mobile_btn:
            m_btn_html = '''<button onclick="openSaleModal()" class="inline-flex items-center space-x-1 text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white px-2.5 py-1.5 rounded-xl shadow-sm transition">
              <i data-lucide="wallet" class="w-3.5 h-3.5"></i>
              <span>+ Venta</span>
            </button>'''
            m_btn_tag = BeautifulSoup(m_btn_html, "html.parser").find("button")
            lote_m_btn = mobile_actions.find("button", onclick="openLotModal()")
            if lote_m_btn:
                lote_m_btn.insert_before(m_btn_tag)
            else:
                mobile_actions.append(m_btn_tag)

# Add prominent "Registrar Venta" button above the lots table in panel-cartera
panel_cartera = soup.find(id="panel-cartera")
if panel_cartera:
    fifo_badge = panel_cartera.find("span", string=re.compile("Criterio FIFO"))
    if fifo_badge and fifo_badge.parent:
        existing_table_sale_btn = panel_cartera.find("button", onclick="openSaleModal()")
        if not existing_table_sale_btn:
            btn_wrapper_html = '''<div class="flex items-center space-x-2">
              <button onclick="openLotModal()" class="px-2.5 py-1 text-xs font-semibold bg-blue-50 hover:bg-blue-100 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400 rounded-lg border border-blue-200 dark:border-blue-900/60 transition">
                + Añadir Lote
              </button>
              <button onclick="openSaleModal()" class="px-2.5 py-1 text-xs font-bold bg-rose-600 hover:bg-rose-500 text-white rounded-lg shadow-sm transition inline-flex items-center space-x-1">
                <i data-lucide="wallet" class="w-3 h-3"></i>
                <span>💸 Registrar Venta</span>
              </button>
              <span class="hidden sm:inline-block text-[11px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium px-2 py-0.5 rounded-lg border border-slate-200 dark:border-slate-700">Criterio FIFO</span>
            </div>'''
            btn_wrapper = BeautifulSoup(btn_wrapper_html, "html.parser").find("div")
            fifo_badge.replace_with(btn_wrapper)

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Successfully restructured index.html!")
