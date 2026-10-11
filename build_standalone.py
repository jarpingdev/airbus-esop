import re
import os
from pathlib import Path

BASE_DIR = Path("/Users/joseantonio/Developer/airbus_esop")
INDEX_PATH = BASE_DIR / "index.html"
OUT_DESKTOP = Path("/Users/joseantonio/Desktop/Airbus_ESOP.html")
OUT_DEV = BASE_DIR / "Airbus_ESOP_Standalone.html"
OUT_DEV_ALIAS = BASE_DIR / "airbus_esop.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    index_content = f.read()

# 1. Extract HTML layout up to the main script tag
split_marker = "  <!-- SCRIPT LÓGICA FRONTEND -->"
if split_marker not in index_content:
    split_marker = "<script>"
    idx = index_content.rfind("<script>")
    html_layout = index_content[:idx]
else:
    idx = index_content.find(split_marker)
    html_layout = index_content[:idx]

# Check if backup/restore buttons are in header, if not we add export/import buttons to header or footer
# In index.html, let's see what is in footer:
footer_search = '<footer class="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-6 mt-8 text-center text-xs text-slate-400 dark:text-slate-500 safe-bottom">'
footer_replacement = """<footer class="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-6 mt-8 text-center text-xs text-slate-400 dark:text-slate-500 safe-bottom">
    <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
      <div>Airbus ESOP Calculadora Patrimonial • Diseñado para empleados en España</div>
      <div class="flex items-center space-x-3 text-slate-500 dark:text-slate-400">
        <button onclick="exportData()" class="hover:underline">💾 Guardar Copia (.json)</button>
        <span>•</span>
        <button onclick="importData()" class="hover:underline">📂 Cargar Copia</button>
        <span>•</span>
        <button onclick="resetData()" class="text-rose-500 hover:underline">🔄 Restablecer 3 Paquetes</button>
      </div>
    </div>"""

if footer_search in html_layout:
    html_layout = html_layout.replace(footer_search, footer_replacement)

# 2. Build the complete standalone script
standalone_script = """  <!-- SCRIPT LÓGICA FRONTEND STANDALONE (100% OFFLINE, ROBUSTO Y AUTÓNOMO) -->
  <script>
    // ICONOS INLINE (Cero dependencias externas ni CDN)
    const INLINE_ICONS = {
      "plane":"<path d=\\"M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z\\"></path>",
      "wallet":"<path d=\\"M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1\\"></path><path d=\\"M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4\\"></path>",
      "credit-card":"<rect width=\\"20\\" height=\\"14\\" x=\\"2\\" y=\\"5\\" rx=\\"2\\"></rect><line x1=\\"2\\" x2=\\"22\\" y1=\\"10\\" y2=\\"10\\"></line><path d=\\"M6 14h2\\"></path>",
      "layers":"<path d=\\"M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z\\"></path><path d=\\"M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12\\"></path><path d=\\"M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17\\"></path>",
      "lock":"<rect width=\\"18\\" height=\\"11\\" x=\\"3\\" y=\\"11\\" rx=\\"2\\" ry=\\"2\\"></rect><path d=\\"M7 11V7a5 5 0 0 1 10 0v4\\"></path>",
      "calculator":"<rect width=\\"16\\" height=\\"20\\" x=\\"4\\" y=\\"2\\" rx=\\"2\\"></rect><line x1=\\"8\\" x2=\\"16\\" y1=\\"6\\" y2=\\"6\\"></line><line x1=\\"16\\" x2=\\"16\\" y1=\\"14\\" y2=\\"18\\"></line><path d=\\"M16 10h.01\\"></path><path d=\\"M12 10h.01\\"></path><path d=\\"M8 10h.01\\"></path><path d=\\"M12 14h.01\\"></path><path d=\\"M8 14h.01\\"></path><path d=\\"M12 18h.01\\"></path><path d=\\"M8 18h.01\\"></path>",
      "target":"<circle cx=\\"12\\" cy=\\"12\\" r=\\"10\\"></circle><circle cx=\\"12\\" cy=\\"12\\" r=\\"6\\"></circle><circle cx=\\"12\\" cy=\\"12\\" r=\\"2\\"></circle>",
      "help-circle":"<circle cx=\\"12\\" cy=\\"12\\" r=\\"10\\"></circle><path d=\\"M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3\\"></path><path d=\\"M12 17h.01\\"></path>",
      "calendar":"<path d=\\"M8 2v3\\"></path><path d=\\"M16 2v3\\"></path><rect x=\\"3\\" y=\\"3\\" width=\\"18\\" height=\\"18\\" rx=\\"2\\"></rect><path d=\\"M3 9h18\\"></path>",
      "plus-circle":"<circle cx=\\"12\\" cy=\\"12\\" r=\\"10\\"></circle><path d=\\"M8 12h8\\"></path><path d=\\"M12 8v8\\"></path>",
      "chevron-down":"<path d=\\"m6 9 6 6 6-6\\"></path>",
      "clock":"<circle cx=\\"12\\" cy=\\"12\\" r=\\"10\\"></circle><path d=\\"M12 6v6l4 2\\"></path>",
      "refresh-cw":"<path d=\\"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8\\"></path><path d=\\"M21 3v5h-5\\"></path><path d=\\"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16\\"></path><path d=\\"M8 16H3v5\\"></path>",
      "list":"<path d=\\"M3 5h.01\\"></path><path d=\\"M3 12h.01\\"></path><path d=\\"M3 19h.01\\"></path><path d=\\"M8 5h13\\"></path><path d=\\"M8 12h13\\"></path><path d=\\"M8 19h13\\"></path>",
      "layout-grid":"<rect width=\\"7\\" height=\\"7\\" x=\\"3\\" y=\\"3\\" rx=\\"1\\"></rect><rect width=\\"7\\" height=\\"7\\" x=\\"14\\" y=\\"3\\" rx=\\"1\\"></rect><rect width=\\"7\\" height=\\"7\\" x=\\"14\\" y=\\"14\\" rx=\\"1\\"></rect><rect width=\\"7\\" height=\\"7\\" x=\\"3\\" y=\\"14\\" rx=\\"1\\"></rect>",
      "trending-up":"<path d=\\"M16 7h6v6\\"></path><path d=\\"m22 7-8.5 8.5-5-5L2 17\\"></path>",
      "x":"<path d=\\"M18 6 6 18\\"></path><path d=\\"m6 6 12 12\\"></path>"
    };

    window.lucide = {
      createIcons: function() {
        document.querySelectorAll('[data-lucide]').forEach(el => {
          const name = el.getAttribute('data-lucide');
          const inner = INLINE_ICONS[name];
          if (!inner) return;
          const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
          svg.setAttribute('viewBox', '0 0 24 24');
          svg.setAttribute('fill', 'none');
          svg.setAttribute('stroke', 'currentColor');
          svg.setAttribute('stroke-width', '2');
          svg.setAttribute('stroke-linecap', 'round');
          svg.setAttribute('stroke-linejoin', 'round');
          if (el.getAttribute('class')) svg.setAttribute('class', el.getAttribute('class'));
          if (el.getAttribute('id')) svg.setAttribute('id', el.getAttribute('id'));
          svg.innerHTML = inner;
          el.replaceWith(svg);
        });
      }
    };

    // PERSISTENCIA Y CONFIGURACIÓN CLIENT-SIDE
    const STORAGE_KEY = "airbus_esop_user_lots_v3";
    const SALES_STORAGE_KEY = "airbus_esop_user_sales_v3";
    const THEME_KEY = "airbus_esop_theme_mode";
    const TAB_KEY = "airbus_esop_active_tab";
    const PRICE_KEY = "airbus_esop_custom_price";

    // LOS 3 PAQUETES INTEGRADOS POR DEFECTO
    const DEFAULT_INITIAL_LOTS = [
      {
        id: "ESOP-2023",
        year: 2023,
        grant_date: "2023-05-15",
        unlock_date: "2026-05-15",
        purchased_shares: 18,
        matching_shares: 12,
        total_shares: 30,
        purchase_price: 119.06,
        total_paid: 2143.08,
        status: "UNLOCKED",
        notes: "Paquete 18 + 12 (18 compradas + 12 gratis • Descuento 40%)"
      },
      {
        id: "ESOP-2024",
        year: 2024,
        grant_date: "2024-05-15",
        unlock_date: "2027-05-15",
        purchased_shares: 30,
        matching_shares: 20,
        total_shares: 50,
        purchase_price: 150.26,
        total_paid: 4507.80,
        status: "LOCKED",
        notes: "Paquete 30 + 20 (30 compradas + 20 gratis • Descuento 40%)"
      },
      {
        id: "ESOP-2025",
        year: 2025,
        grant_date: "2025-05-15",
        unlock_date: "2028-05-15",
        purchased_shares: 9,
        matching_shares: 6,
        total_shares: 15,
        purchase_price: 162.78,
        total_paid: 1465.02,
        status: "LOCKED",
        notes: "Paquete 9 + 6 (9 compradas + 6 gratis • Descuento 40%)"
      }
    ];

    const HISTORICAL_CAMPAIGNS = {
      2027: { year: 2027, price: null, grant_date: "2027-05-15", unlock_date: "2030-05-15", label: "2027 — Estimado en vivo (~187 €)", is_official: false, notes: "Estimación según cotización de mercado" },
      2026: { year: 2026, price: 167.90, grant_date: "2026-05-15", unlock_date: "2029-05-15", label: "2026 — 167,90 € (Oficial)", is_official: true, notes: "Precio oficial Pure Registered fijado por Airbus" },
      2025: { year: 2025, price: 162.78, grant_date: "2025-05-15", unlock_date: "2028-05-15", label: "2025 — 162,78 € (Oficial)", is_official: true, notes: "Precio oficial Pure Registered fijado por Airbus" },
      2024: { year: 2024, price: 150.26, grant_date: "2024-05-15", unlock_date: "2027-05-15", label: "2024 — 150,26 € (Oficial)", is_official: true, notes: "Precio oficial Pure Registered fijado por Airbus" },
      2023: { year: 2023, price: 119.06, grant_date: "2023-05-15", unlock_date: "2026-05-15", label: "2023 — 119,06 € (Oficial)", is_official: true, notes: "Precio oficial Pure Registered fijado por Airbus" },
      2022: { year: 2022, price: 117.88, grant_date: "2022-05-15", unlock_date: "2025-05-15", label: "2022 — 117,88 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" },
      2021: { year: 2021, price: 93.90, grant_date: "2021-05-15", unlock_date: "2024-05-15", label: "2021 — 93,90 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" },
      2020: { year: 2020, price: 136.60, grant_date: "2020-05-15", unlock_date: "2023-05-15", label: "2020 — 136,60 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" },
      2019: { year: 2019, price: 134.40, grant_date: "2019-05-15", unlock_date: "2022-05-15", label: "2019 — 134,40 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" },
      2018: { year: 2018, price: 89.52, grant_date: "2018-05-15", unlock_date: "2021-05-15", label: "2018 — 89,52 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" },
      2017: { year: 2017, price: 67.24, grant_date: "2017-05-15", unlock_date: "2020-05-15", label: "2017 — 67,24 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" }
    };

    const OFFICIAL_PACKAGES_MAP = {
      "15+12": { purchased: 15, matching: 12, total: 27, desc: "⭐ Paquete Estrella (15 + 12 = 27 acc • 44.4% regalo)" },
      "18+12": { purchased: 18, matching: 12, total: 30, desc: "⭐ Paquete Clásico (18 + 12 = 30 acc • 40% regalo)" },
      "30+20": { purchased: 30, matching: 20, total: 50, desc: "⭐ Paquete Amplio (30 + 20 = 50 acc • 40% regalo)" },
      "3+2": { purchased: 3, matching: 2, total: 5, desc: "3 + 2 = 5 acc" },
      "6+4": { purchased: 6, matching: 4, total: 10, desc: "6 + 4 = 10 acc" },
      "9+6": { purchased: 9, matching: 6, total: 15, desc: "9 + 6 = 15 acc" },
      "42+28": { purchased: 42, matching: 28, total: 70, desc: "42 + 28 = 70 acc" },
      "54+36": { purchased: 54, matching: 36, total: 90, desc: "54 + 36 = 90 acc" },
      "72+48": { purchased: 72, matching: 48, total: 120, desc: "72 + 48 = 120 acc" }
    };

    const DEFAULT_PACKAGES = [
      { id: 1, purchased: 3, matching: 2, total: 5 },
      { id: 2, purchased: 6, matching: 4, total: 10 },
      { id: 3, purchased: 9, matching: 6, total: 15 },
      { id: 4, purchased: 15, matching: 12, total: 27 },
      { id: 5, purchased: 18, matching: 12, total: 30 },
      { id: 6, purchased: 30, matching: 20, total: 50 },
      { id: 7, purchased: 42, matching: 28, total: 70 },
      { id: 8, purchased: 54, matching: 36, total: 90 }
    ];

    const memStorage = {};
    let isLocalStorageWorking = false;
    try {
      const testKey = '__test_ls__';
      window.localStorage.setItem(testKey, testKey);
      window.localStorage.removeItem(testKey);
      isLocalStorageWorking = true;
    } catch (e) {
      isLocalStorageWorking = false;
    }

    function safeGetItem(key) {
      if (isLocalStorageWorking) {
        try {
          return window.localStorage.getItem(key);
        } catch (e) {}
      }
      return memStorage[key] !== undefined ? memStorage[key] : null;
    }

    function safeSetItem(key, val) {
      if (isLocalStorageWorking) {
        try {
          window.localStorage.setItem(key, val);
          return;
        } catch (e) {}
      }
      memStorage[key] = val;
    }

    function getStoredLots() {
      try {
        const raw = safeGetItem(STORAGE_KEY);
        if (raw !== null && raw !== undefined) {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) return parsed;
        }
      } catch (e) {}
      saveStoredLots(DEFAULT_INITIAL_LOTS);
      return JSON.parse(JSON.stringify(DEFAULT_INITIAL_LOTS));
    }

    function saveStoredLots(lots) {
      safeSetItem(STORAGE_KEY, JSON.stringify(lots));
    }

    function getStoredSales() {
      try {
        const raw = safeGetItem(SALES_STORAGE_KEY);
        if (raw !== null && raw !== undefined) {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) return parsed;
        }
      } catch (e) {}
      return [];
    }

    function saveStoredSales(sales) {
      safeSetItem(SALES_STORAGE_KEY, JSON.stringify(sales));
    }

    let currentLivePrice = parseFloat(safeGetItem(PRICE_KEY)) || 187.26;
    let currentTab = safeGetItem(TAB_KEY) || 'cartera';
    let editingLotId = null;
    let currentSimLotId = 'ESOP-2023';

    function formatEuro(val) {
      if (isNaN(val) || val === null || val === undefined) val = 0;
      return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(val);
    }

    // CÁLCULO FISCAL IRPF EN ESPAÑA (Tramos base del ahorro)
    function calculateTaxSpain(capitalGain) {
      if (capitalGain <= 0) return 0;
      let tax = 0;
      let remaining = capitalGain;

      const t1 = Math.min(remaining, 6000);
      tax += t1 * 0.19;
      remaining -= t1;

      if (remaining > 0) {
        const t2 = Math.min(remaining, 44000);
        tax += t2 * 0.21;
        remaining -= t2;
      }
      if (remaining > 0) {
        const t3 = Math.min(remaining, 150000);
        tax += t3 * 0.23;
        remaining -= t3;
      }
      if (remaining > 0) {
        const t4 = Math.min(remaining, 100000);
        tax += t4 * 0.27;
        remaining -= t4;
      }
      if (remaining > 0) {
        tax += remaining * 0.28;
      }
      return Math.round(tax * 100) / 100;
    }

    // GESTIÓN DE PESTAÑAS Y ACORDEONES
    function switchTab(tabId) {
      currentTab = tabId;
      safeSetItem(TAB_KEY, tabId);
      updateTabsUI();
    }

    function updateTabsUI() {
      const tabs = ['cartera', 'simulador', 'ventas', 'optimizador', 'guia', 'all'];
      tabs.forEach(t => {
        const btn = document.getElementById('tabBtn-' + t);
        if (!btn) return;
        if (currentTab === t) {
          btn.className = 'tab-btn px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-xl font-semibold text-xs flex items-center space-x-1.5 whitespace-nowrap transition bg-blue-600 text-white shadow-sm border border-blue-600';
        } else {
          btn.className = 'tab-btn px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-xl font-semibold text-xs flex items-center space-x-1.5 whitespace-nowrap transition bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white';
        }
      });

      const panels = ['cartera', 'simulador', 'ventas', 'optimizador', 'guia'];
      panels.forEach(p => {
        const panel = document.getElementById('panel-' + p);
        if (!panel) return;
        if (currentTab === 'all' || currentTab === p) {
          panel.classList.remove('hidden');
          if (currentTab === p) {
            setPanelExpanded(p, true);
          }
        } else {
          panel.classList.add('hidden');
        }
      });
    }

    function togglePanel(panelId) {
      const content = document.getElementById('content-' + panelId);
      if (!content) return;
      const isHidden = content.classList.contains('hidden');
      setPanelExpanded(panelId, isHidden);
    }

    function setPanelExpanded(panelId, expand) {
      const content = document.getElementById('content-' + panelId);
      const chevron = document.getElementById('chevron-' + panelId);
      if (!content) return;
      if (expand) {
        content.classList.remove('hidden');
        if (chevron) chevron.classList.remove('-rotate-90');
      } else {
        content.classList.add('hidden');
        if (chevron) chevron.classList.add('-rotate-90');
      }
    }

    // COTIZACIÓN EN VIVO AIRBUS
    function refreshData() {
      fetchLivePrice();
    }

    async function fetchLivePrice() {
      try {
        const res = await fetch('https://query1.finance.yahoo.com/v8/finance/chart/AIR.PA?interval=1d', { mode: 'cors' });
        if (res.ok) {
          const d = await res.json();
          const meta = d.chart.result[0].meta;
          currentLivePrice = parseFloat(meta.regularMarketPrice);
          const prev = parseFloat(meta.chartPreviousClose || currentLivePrice);
          const chg = currentLivePrice - prev;
          const pct = (chg / prev) * 100;
          updateStockHeader(currentLivePrice, chg, pct, new Date().toLocaleTimeString('es-ES'));
          recalculateDashboard();
          return;
        }
      } catch (e) {}

      const savedPrice = parseFloat(safeGetItem(PRICE_KEY));
      currentLivePrice = (!isNaN(savedPrice) && savedPrice > 0) ? savedPrice : 187.26;
      updateStockHeader(currentLivePrice, 1.80, 0.97, 'En tiempo real');
      recalculateDashboard();
    }

    function updateStockHeader(price, change, pctChange, timestamp) {
      const pEl = document.getElementById('headerPrice');
      if (pEl) pEl.textContent = formatEuro(price);
      const cEl = document.getElementById('headerChange');
      if (cEl) cEl.textContent = (change >= 0 ? '+' : '') + pctChange.toFixed(2) + '%';
      const uEl = document.getElementById('lastUpdated');
      if (uEl) uEl.textContent = timestamp;
      const rEl = document.getElementById('sliderRefPriceText');
      if (rEl) rEl.textContent = Math.round(price) + ' €';
    }

    // MOTOR PRINCIPAL DE CÁLCULO
    function recalculateDashboard() {
      const rawLots = getStoredLots();
      const sales = getStoredSales();
      const today = new Date();
      today.setHours(0,0,0,0);
      const msPerDay = 1000 * 60 * 60 * 24;

      let totalShares = 0;
      let totalGiftShares = 0;
      let totalInvested = 0;
      let totalMarketVal = 0;

      const lots = rawLots.map(l => {
        const grantD = new Date(l.grant_date);
        const unlockD = new Date(l.unlock_date);
        const daysLeft = Math.max(0, Math.ceil((unlockD - today) / msPerDay));
        const totalHoldingDays = Math.max(1, Math.ceil((unlockD - grantD) / msPerDay));
        const daysPassed = Math.max(0, Math.ceil((today - grantD) / msPerDay));
        const progressPct = Math.min(100, Math.round((daysPassed / totalHoldingDays) * 1000) / 10);
        const isMature = today >= unlockD;

        const shares = l.total_shares;
        const paid = l.total_paid;
        const mktVal = Math.round(shares * currentLivePrice * 100) / 100;
        const profit = Math.round((mktVal - paid) * 100) / 100;
        const profitPct = paid > 0 ? Math.round((profit / paid * 1000) / 10) : 0;
        const effectiveCost = shares > 0 ? Math.round((paid / shares) * 100) / 100 : 0;

        totalShares += shares;
        totalGiftShares += l.matching_shares;
        totalInvested += paid;
        totalMarketVal += mktVal;

        return {
          ...l,
          market_value: mktVal,
          profit: profit,
          profit_pct: profitPct,
          days_left: daysLeft,
          progress_pct: progressPct,
          is_mature: isMature,
          effective_cost_per_share: effectiveCost
        };
      });

      const totalProfit = Math.round((totalMarketVal - totalInvested) * 100) / 100;
      const totalProfitPct = totalInvested > 0 ? Math.round((totalProfit / totalInvested * 1000) / 10) : 0;

      // Actualizar KPIs de Cartera Viva
      document.getElementById('kpiMarketVal').textContent = formatEuro(totalMarketVal);
      document.getElementById('kpiProfitText').textContent = `${totalProfit >= 0 ? '+' : ''}${formatEuro(totalProfit)} (${totalProfitPct >= 0 ? '+' : ''}${totalProfitPct}%)`;
      document.getElementById('kpiInvested').textContent = formatEuro(totalInvested);
      document.getElementById('kpiInvestedSub').textContent = `${totalShares - totalGiftShares} acciones compradas`;
      document.getElementById('kpiSharesTotal').textContent = totalShares;
      document.getElementById('kpiGiftBadge').textContent = `${totalGiftShares} REGALADAS`;

      const carteraBadge = document.getElementById('badge-summary-cartera');
      if (carteraBadge) {
        carteraBadge.textContent = totalShares > 0 ? `${formatEuro(totalMarketVal)} (+${totalProfitPct}%)` : '0,00 €';
      }

      const lockedLots = lots.filter(l => !l.is_mature && l.days_left > 0).sort((a,b) => a.days_left - b.days_left);
      const avgEffectiveCost = totalShares > 0 ? Math.round((totalInvested / totalShares) * 100) / 100 : 0;
      document.getElementById('kpiEffectiveCost').textContent = formatEuro(avgEffectiveCost);

      if (lockedLots.length > 0) {
        const nextLot = lockedLots[0];
        document.getElementById('kpiDaysLeft').textContent = nextLot.days_left;
        document.getElementById('kpiDaysLeftLabel').textContent = `días (${nextLot.id})`;
        document.getElementById('kpiProgressBar').style.width = nextLot.progress_pct + '%';
        document.getElementById('kpiUnlockDateText').textContent = 'Próximo desbloqueo: ' + nextLot.unlock_date;
      } else if (lots.length > 0) {
        document.getElementById('kpiDaysLeft').textContent = '0';
        document.getElementById('kpiDaysLeftLabel').textContent = 'Desbloqueado';
        document.getElementById('kpiProgressBar').style.width = '100%';
        document.getElementById('kpiUnlockDateText').textContent = 'Todos los lotes listos para vender';
      } else {
        document.getElementById('kpiDaysLeft').textContent = '-';
        document.getElementById('kpiDaysLeftLabel').textContent = 'Sin lotes';
        document.getElementById('kpiProgressBar').style.width = '0%';
        document.getElementById('kpiUnlockDateText').textContent = 'Sin lotes registrados';
      }

      // KPIs de Ventas Liquidadas
      const totalSalesGross = Math.round(sales.reduce((acc, s) => acc + (s.gross_proceeds || 0), 0) * 100) / 100;
      const totalSalesGain = Math.round(sales.reduce((acc, s) => acc + (s.capital_gain || 0), 0) * 100) / 100;
      const totalSalesTax = Math.round(sales.reduce((acc, s) => acc + (s.tax || 0), 0) * 100) / 100;
      const totalSalesNet = Math.round(sales.reduce((acc, s) => acc + (s.net_proceeds || 0), 0) * 100) / 100;

      const salesBadge = document.getElementById('badge-summary-ventas');
      if (salesBadge) {
        salesBadge.textContent = `${sales.length} ventas • Neto: ${formatEuro(totalSalesNet)}`;
      }
      const kpiSG = document.getElementById('kpiSalesGross');
      if (kpiSG) kpiSG.textContent = formatEuro(totalSalesGross);
      const kpiSGa = document.getElementById('kpiSalesGain');
      if (kpiSGa) kpiSGa.textContent = '+' + formatEuro(totalSalesGain);
      const kpiST = document.getElementById('kpiSalesTax');
      if (kpiST) kpiST.textContent = '-' + formatEuro(totalSalesTax);
      const kpiSN = document.getElementById('kpiSalesNet');
      if (kpiSN) kpiSN.textContent = formatEuro(totalSalesNet);

      // Actualizar selectores de lotes para simulador y venta
      updateLotSelectors(lots);

      renderLots(lots);
      renderSalesHistory(sales);

      // Slider Inicial
      const slider = document.getElementById('priceSlider');
      if (!slider.dataset.userMoved) {
        slider.value = Math.round(currentLivePrice);
        document.getElementById('sliderPriceLabel').textContent = formatEuro(currentLivePrice);
      }
      runSimulation();

      // Paquetes optimizador
      renderPackages(DEFAULT_PACKAGES, currentLivePrice, parseFloat(document.getElementById('budgetSlider').value || 2500));
    }

    function updateLotSelectors(lots) {
      const simSelect = document.getElementById('simLotSelect');
      const saleSelect = document.getElementById('saleLotSelect');

      if (simSelect) {
        const curVal = simSelect.value;
        simSelect.innerHTML = '';
        lots.forEach(l => {
          const opt = document.createElement('option');
          opt.value = l.id;
          opt.textContent = `${l.id} (${l.total_shares} acc • ${l.is_mature ? '🔓 Libre' : '🔒 Bloqueado'})`;
          simSelect.appendChild(opt);
        });
        if (lots.some(l => l.id === curVal)) {
          simSelect.value = curVal;
        } else if (lots.length > 0) {
          simSelect.value = lots[0].id;
        }
      }

      if (saleSelect) {
        const curVal = saleSelect.value;
        saleSelect.innerHTML = '';
        lots.forEach(l => {
          const opt = document.createElement('option');
          opt.value = l.id;
          opt.textContent = `${l.id} (${l.total_shares} acc • ${formatEuro(l.total_paid)} invertidos)`;
          saleSelect.appendChild(opt);
        });
        if (lots.some(l => l.id === curVal)) {
          saleSelect.value = curVal;
        } else if (lots.length > 0) {
          saleSelect.value = lots[0].id;
        }
      }
    }

    function renderLots(lots) {
      const tbody = document.getElementById('lotsTableBody');
      const mobileContainer = document.getElementById('lotsCardsMobile');
      const desktopWrapper = document.getElementById('lotsDesktopWrapper');
      const emptyState = document.getElementById('lotsEmptyState');

      tbody.innerHTML = '';
      mobileContainer.innerHTML = '';

      if (lots.length === 0) {
        desktopWrapper.classList.add('hidden');
        mobileContainer.classList.add('hidden');
        emptyState.classList.remove('hidden');
        return;
      }

      emptyState.classList.add('hidden');
      desktopWrapper.classList.remove('hidden');
      mobileContainer.classList.remove('hidden');

      lots.forEach(lot => {
        // Desktop
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/60 bg-white dark:bg-slate-900/60 transition border-b border-slate-100 dark:border-slate-800/80';
        tr.innerHTML = `
          <td class="py-3 px-4 font-semibold text-slate-800 dark:text-slate-200">
            ${lot.id} <span class="text-xs text-slate-400 dark:text-slate-500 block font-normal">${lot.grant_date}</span>
          </td>
          <td class="py-3 px-4">
            <span class="font-bold text-slate-900 dark:text-white">${lot.total_shares}</span>
            <span class="text-xs text-indigo-600 dark:text-indigo-400 block font-medium">(${lot.purchased_shares} + ${lot.matching_shares} gratis)</span>
          </td>
          <td class="py-3 px-4 text-slate-600 dark:text-slate-300 font-medium">${formatEuro(lot.purchase_price)}</td>
          <td class="py-3 px-4 font-medium text-slate-700 dark:text-slate-300">${formatEuro(lot.total_paid)}</td>
          <td class="py-3 px-4 font-semibold text-slate-900 dark:text-white">${formatEuro(lot.market_value)}</td>
          <td class="py-3 px-4 font-bold text-emerald-600 dark:text-emerald-400">+${formatEuro(lot.profit)}</td>
          <td class="py-3 px-4">
            ${lot.is_mature 
              ? '<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300/40">🔓 Desbloqueado</span>'
              : `<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300/40">🔒 Bloqueado (${lot.days_left} d)</span>`
            }
          </td>
          <td class="py-3 px-4 text-right space-x-1.5 whitespace-nowrap">
            <button onclick="openSaleModalForLot('${lot.id}')" class="px-2.5 py-1 text-xs font-semibold text-rose-600 bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/40 dark:text-rose-400 rounded-lg border border-rose-200 dark:border-rose-900/60 transition">
              Vender
            </button>
            <button onclick="openLotModal('${lot.id}')" class="px-2.5 py-1 text-xs font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/40 dark:text-blue-400 rounded-lg border border-blue-200 dark:border-blue-900/60 transition">
              Editar
            </button>
            <button onclick="deleteLot('${lot.id}')" class="px-2.5 py-1 text-xs font-semibold text-slate-600 hover:text-rose-600 dark:text-slate-400 dark:hover:text-rose-400 rounded-lg transition">
              Eliminar
            </button>
          </td>
        `;
        tbody.appendChild(tr);

        // Mobile
        const card = document.createElement('div');
        card.className = 'bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl p-3.5 space-y-2.5 shadow-sm';
        const statusBadge = lot.is_mature
          ? '<span class="px-2 py-0.5 text-[11px] font-semibold rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300/40">🔓 Desbloqueado</span>'
          : `<span class="px-2 py-0.5 text-[11px] font-semibold rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300/40">🔒 Bloqueado (${lot.days_left} d)</span>`;

        card.innerHTML = `
          <div class="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-700/60">
            <div>
              <span class="font-bold text-slate-900 dark:text-white text-sm">${lot.id}</span>
              <span class="text-[11px] text-slate-400 dark:text-slate-500 block">Concesión: ${lot.grant_date}</span>
            </div>
            <div>${statusBadge}</div>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="bg-slate-50 dark:bg-slate-900/60 p-2 rounded-lg border border-slate-100 dark:border-slate-800">
              <span class="text-slate-500 dark:text-slate-400 block text-[10px] uppercase font-semibold">Acciones</span>
              <span class="font-bold text-slate-900 dark:text-white text-sm">${lot.total_shares}</span>
              <span class="text-[11px] text-indigo-500 dark:text-indigo-400 font-medium block">(${lot.purchased_shares} + ${lot.matching_shares} reg.)</span>
            </div>
            <div class="bg-slate-50 dark:bg-slate-900/60 p-2 rounded-lg border border-slate-100 dark:border-slate-800">
              <span class="text-slate-500 dark:text-slate-400 block text-[10px] uppercase font-semibold">Valor Actual</span>
              <span class="font-bold text-slate-900 dark:text-white text-sm">${formatEuro(lot.market_value)}</span>
              <span class="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold block">+${formatEuro(lot.profit)}</span>
            </div>
          </div>
          <div class="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-700/60 text-xs">
            <span class="text-slate-400">Invertido: ${formatEuro(lot.total_paid)}</span>
            <div class="space-x-2">
              <button onclick="openSaleModalForLot('${lot.id}')" class="text-rose-600 dark:text-rose-400 font-bold hover:underline">
                Vender
              </button>
              <button onclick="openLotModal('${lot.id}')" class="text-blue-600 dark:text-blue-400 font-semibold hover:underline">
                Editar
              </button>
              <button onclick="deleteLot('${lot.id}')" class="text-slate-400 hover:text-rose-500">
                Eliminar
              </button>
            </div>
          </div>
        `;
        mobileContainer.appendChild(card);
      });
      if (typeof window !== "undefined" && window.lucide) window.lucide.createIcons();
    }

    // GESTIÓN DE HISTORIAL DE VENTAS
    function renderSalesHistory(sales) {
      const tbody = document.getElementById('salesTableBody');
      const mobileContainer = document.getElementById('salesCardsMobile');
      if (!tbody) return;

      tbody.innerHTML = '';
      if (mobileContainer) mobileContainer.innerHTML = '';

      if (!sales || sales.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="text-center py-6 text-slate-400">No hay ventas registradas todavía. Puedes simular y vender acciones sueltas en cualquier momento.</td></tr>`;
        if (mobileContainer) {
          mobileContainer.innerHTML = `<div class="p-4 text-center text-xs text-slate-400 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">Sin ventas registradas.</div>`;
        }
        return;
      }

      sales.forEach(s => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/60 bg-white dark:bg-slate-900/60 transition border-b border-slate-100 dark:border-slate-800/80';
        tr.innerHTML = `
          <td class="py-2.5 px-3 font-semibold text-slate-800 dark:text-slate-200">${s.date}</td>
          <td class="py-2.5 px-3 font-medium text-slate-700 dark:text-slate-300">${s.lot_id}</td>
          <td class="py-2.5 px-3 font-bold text-slate-900 dark:text-white">${s.shares_sold} acc</td>
          <td class="py-2.5 px-3 text-slate-600 dark:text-slate-300 font-medium">${formatEuro(s.sell_price)}</td>
          <td class="py-2.5 px-3 font-semibold text-slate-900 dark:text-white">${formatEuro(s.gross_proceeds)}</td>
          <td class="py-2.5 px-3 font-bold text-emerald-600 dark:text-emerald-400">+${formatEuro(s.capital_gain)}</td>
          <td class="py-2.5 px-3 font-semibold text-rose-500">-${formatEuro(s.tax)}</td>
          <td class="py-2.5 px-3 font-extrabold text-blue-600 dark:text-blue-400">${formatEuro(s.net_proceeds)}</td>
          <td class="py-2.5 px-3 text-right">
            <button onclick="deleteSale('${s.id}')" class="px-2 py-0.5 text-[11px] font-semibold text-rose-600 hover:text-rose-700 dark:text-rose-400" title="Anular venta y restaurar acciones">
              Deshacer
            </button>
          </td>
        `;
        tbody.appendChild(tr);

        if (mobileContainer) {
          const card = document.createElement('div');
          card.className = 'bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl p-3 space-y-2 text-xs shadow-sm';
          card.innerHTML = `
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-700/60">
              <span class="font-bold text-slate-900 dark:text-white">${s.lot_id} • ${s.shares_sold} acc vendidas</span>
              <span class="text-slate-400 text-[11px]">${s.date}</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <span class="text-slate-400 text-[10px] uppercase block">Cobro Bruto</span>
                <span class="font-semibold text-slate-800 dark:text-slate-200">${formatEuro(s.gross_proceeds)} (a ${formatEuro(s.sell_price)})</span>
              </div>
              <div>
                <span class="text-slate-400 text-[10px] uppercase block">Plusvalía</span>
                <span class="font-bold text-emerald-600 dark:text-emerald-400">+${formatEuro(s.capital_gain)}</span>
              </div>
              <div>
                <span class="text-slate-400 text-[10px] uppercase block">Retención IRPF</span>
                <span class="font-semibold text-rose-500">-${formatEuro(s.tax)}</span>
              </div>
              <div>
                <span class="text-slate-400 text-[10px] uppercase block">Neto Limpio</span>
                <span class="font-extrabold text-blue-600 dark:text-blue-400 text-sm">${formatEuro(s.net_proceeds)}</span>
              </div>
            </div>
            <div class="pt-1 flex items-center justify-between border-t border-slate-100 dark:border-slate-700/60 text-[11px]">
              <span class="${s.is_mature ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'} font-medium">
                ${s.is_mature ? '✅ Exención 3 años aplicada' : '⚠️ Venta antes de 3 años'}
              </span>
              <button onclick="deleteSale('${s.id}')" class="text-rose-600 hover:text-rose-700 font-semibold">
                Deshacer
              </button>
            </div>
          `;
          mobileContainer.appendChild(card);
        }
      });
      if (typeof window !== "undefined" && window.lucide) window.lucide.createIcons();
    }

    // MODAL Y EJECUCIÓN DE VENTA REAL
    function openSaleModal() {
      const lots = getStoredLots();
      if (!lots || lots.length === 0) {
        alert('No tienes lotes registrados en cartera para vender.');
        return;
      }
      updateLotSelectors(lots);
      onSaleLotChange();
      document.getElementById('saleDate').value = new Date().toISOString().slice(0, 10);
      document.getElementById('saleModal').classList.remove('hidden');
    }

    function openSaleModalForLot(lotId) {
      openSaleModal();
      const select = document.getElementById('saleLotSelect');
      if (select) {
        select.value = lotId;
        onSaleLotChange();
      }
    }

    function openSaleModalFromSim() {
      const simSelect = document.getElementById('simLotSelect');
      const lotId = simSelect && simSelect.value ? simSelect.value : (getStoredLots()[0]?.id);
      openSaleModalForLot(lotId);
      const sliderPrice = parseFloat(document.getElementById('priceSlider').value) || currentLivePrice;
      document.getElementById('salePrice').value = sliderPrice.toFixed(2);
      updateSalePreview();
    }

    function closeSaleModal() {
      document.getElementById('saleModal').classList.add('hidden');
    }

    function onSaleLotChange() {
      const lots = getStoredLots();
      const lotId = document.getElementById('saleLotSelect').value;
      const lot = lots.find(l => l.id === lotId);
      if (!lot) return;

      document.getElementById('saleShares').max = lot.total_shares;
      document.getElementById('saleShares').value = lot.total_shares;
      document.getElementById('saleMaxSharesHint').textContent = `(Disponibles: ${lot.total_shares})`;
      document.getElementById('salePrice').value = currentLivePrice.toFixed(2);
      updateSalePreview();
    }

    function updateSalePreview() {
      const lots = getStoredLots();
      const lotId = document.getElementById('saleLotSelect').value;
      const lot = lots.find(l => l.id === lotId);
      if (!lot) return;

      const sharesToSell = parseInt(document.getElementById('saleShares').value) || 0;
      const sellPrice = parseFloat(document.getElementById('salePrice').value) || currentLivePrice;
      const saleDateStr = document.getElementById('saleDate').value || new Date().toISOString().slice(0, 10);

      const maxShares = lot.total_shares || 1;
      const fraction = Math.min(Math.max(sharesToSell / maxShares, 0), 1);
      const costBasis = Math.round(lot.total_paid * fraction * 100) / 100;
      const gross = Math.round(sharesToSell * sellPrice * 100) / 100;
      const gain = Math.max(Math.round((gross - costBasis) * 100) / 100, 0);
      const tax = calculateTaxSpain(gain);
      const net = Math.round((gross - tax) * 100) / 100;

      const isMature = new Date(saleDateStr) >= new Date(lot.unlock_date);

      document.getElementById('previewSaleGross').textContent = formatEuro(gross);
      document.getElementById('previewSaleCost').textContent = '-' + formatEuro(costBasis);
      document.getElementById('previewSaleGain').textContent = '+' + formatEuro(gain);
      document.getElementById('previewSaleTax').textContent = '-' + formatEuro(tax);
      document.getElementById('previewSaleNet').textContent = formatEuro(net);

      const noteEl = document.getElementById('previewSaleStatusNote');
      if (noteEl) {
        if (isMature) {
          noteEl.className = 'text-[11px] text-emerald-600 dark:text-emerald-400 pt-1';
          noteEl.textContent = '✅ Cumple 3 años: Las acciones regaladas están 100% exentas de IRPF.';
        } else {
          noteEl.className = 'text-[11px] text-amber-600 dark:text-amber-400 pt-1';
          noteEl.textContent = `⚠️ Faltan días para cumplir 3 años (${lot.unlock_date}). Venta anticipada sin exención completa.`;
        }
      }
    }

    function submitSale(e) {
      e.preventDefault();
      const lotId = document.getElementById('saleLotSelect').value;
      const shares = parseInt(document.getElementById('saleShares').value);
      const price = parseFloat(document.getElementById('salePrice').value);
      const date = document.getElementById('saleDate').value;

      if (!shares || shares <= 0) {
        alert('Introduce un número válido de acciones');
        return;
      }

      if (!confirm(`¿Confirmas la venta de ${shares} acciones de ${lotId} a ${formatEuro(price)}?`)) return;

      const success = executeSale(lotId, shares, price, date);
      if (success) {
        closeSaleModal();
        switchTab('ventas');
      }
    }

    function executeSale(lotId, sharesSold, sellPrice, saleDate, notes) {
      const lots = getStoredLots();
      const lotIdx = lots.findIndex(l => l.id === lotId);
      if (lotIdx === -1) {
        alert("Lote no encontrado");
        return false;
      }
      const lot = lots[lotIdx];
      const maxShares = lot.total_shares;
      if (sharesSold <= 0 || sharesSold > maxShares) {
        alert(`Cantidad no válida. Máximo disponible: ${maxShares}`);
        return false;
      }

      const fraction = sharesSold / maxShares;
      const purchasedSold = Math.round(lot.purchased_shares * fraction * 100) / 100;
      const matchingSold = Math.round(lot.matching_shares * fraction * 100) / 100;
      const costBasisSold = Math.round(lot.total_paid * fraction * 100) / 100;

      const grossProceeds = Math.round(sharesSold * sellPrice * 100) / 100;
      const capitalGain = Math.round((grossProceeds - costBasisSold) * 100) / 100;
      const tax = calculateTaxSpain(capitalGain);
      const netProceeds = Math.round((grossProceeds - tax) * 100) / 100;

      const unlockD = new Date(lot.unlock_date);
      const isMature = new Date(saleDate) >= unlockD;

      const saleRecord = {
        id: "SALE-" + Date.now(),
        date: saleDate,
        lot_id: lot.id,
        shares_sold: sharesSold,
        sell_price: sellPrice,
        gross_proceeds: grossProceeds,
        cost_basis: costBasisSold,
        capital_gain: capitalGain,
        tax: tax,
        net_proceeds: netProceeds,
        is_mature: isMature,
        notes: notes || `Venta de ${sharesSold} acc de ${lot.id} a ${sellPrice.toFixed(2)} €`,
        snapshot_lot: JSON.parse(JSON.stringify(lot))
      };

      const sales = getStoredSales();
      sales.unshift(saleRecord);
      saveStoredSales(sales);

      if (sharesSold === maxShares) {
        lots.splice(lotIdx, 1);
      } else {
        lot.total_shares -= sharesSold;
        lot.purchased_shares = Math.round((lot.purchased_shares - purchasedSold) * 100) / 100;
        lot.matching_shares = Math.round((lot.matching_shares - matchingSold) * 100) / 100;
        lot.total_paid = Math.round((lot.total_paid - costBasisSold) * 100) / 100;
      }

      saveStoredLots(lots);
      recalculateDashboard();
      return true;
    }

    function deleteSale(saleId) {
      if (!confirm("¿Deseas anular este registro de venta y restaurar las acciones a la cartera?")) return;
      const sales = getStoredSales();
      const sIdx = sales.findIndex(s => s.id === saleId);
      if (sIdx === -1) return;
      const sale = sales[sIdx];
      const lots = getStoredLots();
      const lotIdx = lots.findIndex(l => l.id === sale.lot_id);

      if (lotIdx >= 0) {
        const lot = lots[lotIdx];
        lot.total_shares += sale.shares_sold;
        if (sale.snapshot_lot) {
          lot.purchased_shares = Math.round((lot.purchased_shares + (sale.snapshot_lot.purchased_shares - (lot.purchased_shares - sale.shares_sold * 0.6))) * 100) / 100;
          lot.matching_shares = lot.total_shares - lot.purchased_shares;
        }
        lot.total_paid = Math.round((lot.total_paid + sale.cost_basis) * 100) / 100;
      } else if (sale.snapshot_lot) {
        lots.push(sale.snapshot_lot);
        lots.sort((a,b) => a.year - b.year);
      }

      sales.splice(sIdx, 1);
      saveStoredSales(sales);
      saveStoredLots(lots);
      recalculateDashboard();
    }

    // SIMULADOR INTERACTIVO
    function onSimLotChange() {
      const select = document.getElementById('simLotSelect');
      if (select) currentSimLotId = select.value;
      runSimulation();
    }

    function onPriceSliderChange(val) {
      const slider = document.getElementById('priceSlider');
      slider.dataset.userMoved = "true";
      const num = parseFloat(val);
      document.getElementById('sliderPriceLabel').textContent = formatEuro(num);
      runSimulation(num);
    }

    function runSimulation(price) {
      const sliderPrice = price !== undefined ? price : (parseFloat(document.getElementById('priceSlider').value) || currentLivePrice);
      const lots = getStoredLots();
      const lot = lots.find(l => l.id === currentSimLotId) || lots[0];

      if (!lot) {
        document.getElementById('simSharesCountText').textContent = '0';
        document.getElementById('simGrossProceeds').textContent = formatEuro(0);
        document.getElementById('simCostBasis').textContent = formatEuro(0);
        document.getElementById('simCapitalGain').textContent = formatEuro(0);
        document.getElementById('simTaxSpain').textContent = formatEuro(0);
        document.getElementById('simNetInPocket').textContent = formatEuro(0);
        return;
      }

      const today = new Date();
      today.setHours(0,0,0,0);
      const isMature = today >= new Date(lot.unlock_date);
      const statusEl = document.getElementById('simLotMatureStatus');
      if (statusEl) {
        if (isMature) {
          statusEl.className = 'text-xs font-bold text-emerald-600 dark:text-emerald-400';
          statusEl.textContent = '🔓 Desbloqueado';
        } else {
          statusEl.className = 'text-xs font-bold text-amber-600 dark:text-amber-400';
          statusEl.textContent = '🔒 Bloqueado';
        }
      }

      const shares = lot.total_shares;
      const costBasis = lot.total_paid;
      const gross = Math.round(shares * sliderPrice * 100) / 100;
      const gain = Math.max(Math.round((gross - costBasis) * 100) / 100, 0);
      const tax = calculateTaxSpain(gain);
      const net = Math.round((gross - tax) * 100) / 100;

      document.getElementById('simSharesCountText').textContent = shares;
      document.getElementById('simGrossProceeds').textContent = formatEuro(gross);
      document.getElementById('simCostBasis').textContent = '-' + formatEuro(costBasis);
      document.getElementById('simCapitalGain').textContent = '+' + formatEuro(gain);
      document.getElementById('simTaxSpain').textContent = '-' + formatEuro(tax);
      document.getElementById('simNetInPocket').textContent = formatEuro(net);

      const reinvestBudget = 2500;
      const surplus = net - reinvestBudget;
      const surpEl = document.getElementById('simWheelSurplus');
      if (surpEl) {
        surpEl.textContent = (surplus >= 0 ? '+' : '') + formatEuro(surplus);
        surpEl.className = surplus >= 0 ? 'font-black text-emerald-600 dark:text-emerald-400' : 'font-black text-rose-500';
      }

      const badgeSim = document.getElementById('badge-summary-simulador');
      if (badgeSim) badgeSim.textContent = `Neto: ~${formatEuro(net)}`;
    }

    // OPTIMIZADOR DE PAQUETES
    function onBudgetSliderChange(val) {
      document.getElementById('budgetSliderLabel').textContent = formatEuro(parseFloat(val));
      renderPackages(DEFAULT_PACKAGES, currentLivePrice, parseFloat(val));
    }

    function renderPackages(packages, price, budget) {
      const container = document.getElementById('packagesGrid');
      if (!container) return;
      container.innerHTML = '';

      let bestPkg = null;
      let maxDiscount = -1;

      packages.forEach(pkg => {
        const cost = Math.round(pkg.purchased * price * 100) / 100;
        const discountPct = Math.round((pkg.matching / pkg.total) * 1000) / 10;
        if (cost <= budget && discountPct > maxDiscount) {
          maxDiscount = discountPct;
          bestPkg = pkg;
        }
      });

      packages.forEach(pkg => {
        const cost = Math.round(pkg.purchased * price * 100) / 100;
        const mktVal = Math.round(pkg.total * price * 100) / 100;
        const freeVal = Math.round(pkg.matching * price * 100) / 100;
        const discountPct = Math.round((pkg.matching / pkg.total) * 1000) / 10;
        const isAffordable = cost <= budget;
        const isBest = bestPkg && bestPkg.id === pkg.id;

        const card = document.createElement('div');
        card.className = `p-3 sm:p-4 rounded-xl border transition-all relative ${
          isBest
            ? 'border-indigo-500 bg-indigo-50/80 dark:bg-indigo-950/40 shadow-sm ring-1 ring-indigo-500/30'
            : isAffordable
            ? 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/80'
            : 'border-slate-200/60 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40 opacity-60'
        }`;

        card.innerHTML = `
          ${isBest ? '<div class="absolute -top-2.5 right-3 bg-indigo-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">Óptimo para ti</div>' : ''}
          <div class="flex justify-between items-start mb-2">
            <div>
              <h4 class="font-bold text-slate-900 dark:text-white text-sm">${pkg.purchased} + ${pkg.matching} (${pkg.total} acc)</h4>
              <span class="text-[11px] text-slate-500 dark:text-slate-400 font-medium">Regalo: ${discountPct}%</span>
            </div>
            <span class="font-extrabold text-sm ${isAffordable ? 'text-slate-900 dark:text-white' : 'text-slate-400'}">${formatEuro(cost)}</span>
          </div>
          <div class="space-y-1 text-[11px] text-slate-600 dark:text-slate-300 pt-1 border-t border-slate-100 dark:border-slate-700/60">
            <div class="flex justify-between">
              <span>Valor mercado total:</span>
              <span class="font-semibold text-slate-800 dark:text-slate-200">${formatEuro(mktVal)}</span>
            </div>
            <div class="flex justify-between">
              <span>Regalo de Airbus:</span>
              <span class="font-bold text-emerald-600 dark:text-emerald-400">+${formatEuro(freeVal)}</span>
            </div>
          </div>
        `;
        container.appendChild(card);
      });
    }

    // MODAL DE AÑADIR / EDITAR LOTE
    function openLotModal(lotId) {
      editingLotId = lotId || null;
      const lots = getStoredLots();
      const modalTitle = document.getElementById('lotModalTitle');
      const modalSub = document.getElementById('lotModalSubtitle');
      const submitBtn = document.getElementById('lotSubmitBtn');

      if (lotId) {
        const lot = lots.find(l => l.id === lotId);
        if (lot) {
          if (modalTitle) modalTitle.textContent = `Editar Lote: ${lot.id}`;
          if (modalSub) modalSub.textContent = 'Modifica las acciones o el precio de este lote.';
          if (submitBtn) submitBtn.textContent = 'Actualizar Lote';

          document.getElementById('lotYearSelect').value = lot.year || '2024';
          const area = document.getElementById('manualFieldsArea');
          if (area) area.classList.remove('hidden');

          document.getElementById('lotPurchased').value = lot.purchased_shares;
          document.getElementById('lotMatching').value = lot.matching_shares;
          document.getElementById('lotPrice').value = lot.purchase_price.toFixed(2);
          document.getElementById('lotDate').value = lot.grant_date;
          updateLotPreview();
        }
      } else {
        if (modalTitle) modalTitle.textContent = 'Registrar Compra ESOP';
        if (modalSub) modalSub.textContent = 'Selecciona la campaña y el paquete adquirido.';
        if (submitBtn) submitBtn.textContent = 'Guardar Lote';

        document.getElementById('lotYearSelect').value = '2024';
        document.getElementById('lotPackageSelect').value = '15+12';
        const area = document.getElementById('manualFieldsArea');
        if (area) area.classList.add('hidden');
        onLotYearChange();
        onLotPackageChange();
      }

      document.getElementById('lotModal').classList.remove('hidden');
    }

    function closeLotModal() {
      editingLotId = null;
      document.getElementById('lotModal').classList.add('hidden');
    }

    function onLotYearChange() {
      const yr = parseInt(document.getElementById('lotYearSelect').value);
      const camp = HISTORICAL_CAMPAIGNS[yr];
      const p = camp && camp.price ? camp.price : currentLivePrice;
      document.getElementById('lotPrice').value = p.toFixed(2);
      document.getElementById('lotDate').value = camp ? camp.grant_date : `${yr}-05-15`;
      updateLotPreview();
    }

    function onLotPackageChange() {
      const val = document.getElementById('lotPackageSelect').value;
      const area = document.getElementById('manualFieldsArea');
      if (val === 'custom') {
        if (area) area.classList.remove('hidden');
      } else {
        if (area) area.classList.add('hidden');
        const pkg = OFFICIAL_PACKAGES_MAP[val];
        if (pkg) {
          document.getElementById('lotPurchased').value = pkg.purchased;
          document.getElementById('lotMatching').value = pkg.matching;
        }
      }
      updateLotPreview();
    }

    function updateLotPreview() {
      const purchased = parseInt(document.getElementById('lotPurchased').value) || 0;
      const matching = parseInt(document.getElementById('lotMatching').value) || 0;
      const price = parseFloat(document.getElementById('lotPrice').value) || 0;
      const total = purchased + matching;
      const paid = purchased * price;
      const mkt = total * currentLivePrice;
      const profit = mkt - paid;

      document.getElementById('previewLotPurchased').textContent = purchased;
      document.getElementById('previewLotMatching').textContent = matching;
      document.getElementById('previewLotTotal').textContent = total;
      document.getElementById('previewLotInvested').textContent = formatEuro(paid);
      document.getElementById('previewLotMktVal').textContent = formatEuro(mkt);
      document.getElementById('previewLotProfit').textContent = '+' + formatEuro(profit);
    }

    function submitLot(e) {
      e.preventDefault();
      const yr = parseInt(document.getElementById('lotYearSelect').value);
      const purchased = parseInt(document.getElementById('lotPurchased').value);
      const matching = parseInt(document.getElementById('lotMatching').value);
      const price = parseFloat(document.getElementById('lotPrice').value);
      const grantDate = document.getElementById('lotDate').value;
      const pkgSelectVal = document.getElementById('lotPackageSelect').value;
      const notes = pkgSelectVal !== 'custom' && OFFICIAL_PACKAGES_MAP[pkgSelectVal]
        ? OFFICIAL_PACKAGES_MAP[pkgSelectVal].desc
        : `Paquete ${purchased} + ${matching}`;

      const parts = grantDate.split('-').map(Number);
      const gy = parts[0] || yr;
      const gm = parts[1] || 5;
      const gd = parts[2] || 15;
      const unlockDateStr = `${gy + 3}-${String(gm).padStart(2, '0')}-${String(gd).padStart(2, '0')}`;
      const unlockD = new Date(gy + 3, gm - 1, gd);

      const today = new Date();
      today.setHours(0,0,0,0);
      const isMature = today >= unlockD;

      const newLot = {
        id: `ESOP-${gy}`,
        year: gy,
        grant_date: grantDate,
        unlock_date: unlockDateStr,
        purchased_shares: purchased,
        matching_shares: matching,
        total_shares: purchased + matching,
        purchase_price: price,
        total_paid: Math.round(purchased * price * 100) / 100,
        status: isMature ? "UNLOCKED" : "LOCKED",
        notes: notes
      };

      const lots = getStoredLots();
      const targetId = editingLotId || newLot.id;
      const existingIdx = lots.findIndex(l => l.id === targetId);
      if (existingIdx >= 0) {
        lots[existingIdx] = newLot;
      } else {
        lots.push(newLot);
      }
      lots.sort((a,b) => a.year - b.year);

      saveStoredLots(lots);
      editingLotId = null;
      closeLotModal();
      recalculateDashboard();
    }

    function deleteLot(lotId) {
      if (!confirm(`¿Estás seguro de que deseas eliminar el lote ${lotId}?`)) return;
      const lots = getStoredLots().filter(l => l.id !== lotId);
      saveStoredLots(lots);
      recalculateDashboard();
    }

    // DESCARGA DE CALENDARIO RFC 5545
    function downloadCalendar() {
      const lots = getStoredLots();
      let events = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Airbus ESOP//Calculadora Patrimonial//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
      ];

      lots.forEach(lot => {
        const d = lot.unlock_date.replace(/-/g, '');
        events.push(
          "BEGIN:VEVENT",
          `UID:unlock-${lot.id}@airbus-esop.app`,
          `DTSTAMP:${new Date().toISOString().replace(/[-:]/g, '').slice(0, 15)}Z`,
          `DTSTART;VALUE=DATE:${d}`,
          `SUMMARY:🔓 Airbus ${lot.id} Desbloqueado (100% Exento IRPF)`,
          `DESCRIPTION:Hoy se cumplen 3 años de tu compra ESOP ${lot.year}. Ya puedes vender tus ${lot.total_shares} acciones manteniendo la exención fiscal completa de las ${lot.matching_shares} regaladas.`,
          "STATUS:CONFIRMED",
          "BEGIN:VALARM",
          "ACTION:DISPLAY",
          "DESCRIPTION:Recordatorio desbloqueo acciones Airbus ESOP",
          "TRIGGER:-P1D",
          "END:VALARM",
          "END:VEVENT"
        );
      });

      // Evento Campaña Anual en Abril
      events.push(
        "BEGIN:VEVENT",
        "UID:campaign-2027@airbus-esop.app",
        `DTSTAMP:${new Date().toISOString().replace(/[-:]/g, '').slice(0, 15)}Z`,
        "DTSTART;VALUE=DATE:20270415",
        "SUMMARY:✈️ Apertura Campaña Anual Airbus ESOP 2027",
        "DESCRIPTION:Apertura de la suscripción para el plan de compra de acciones de empleados Airbus ESOP 2027. Consulta el optimizador en la aplicación.",
        "STATUS:CONFIRMED",
        "END:VEVENT"
      );

      events.push("END:VCALENDAR");
      const icsBlob = new Blob([events.join("\\r\\n")], { type: "text/calendar;charset=utf-8" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(icsBlob);
      link.download = "airbus_esop_recordatorios.ics";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    // COPIA DE SEGURIDAD / EXPORTACIÓN E IMPORTACIÓN
    function exportData() {
      const data = {
        lots: getStoredLots(),
        sales_history: getStoredSales(),
        exported_at: new Date().toISOString()
      };
      const jsonBlob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(jsonBlob);
      link.download = `airbus_esop_backup_${new Date().toISOString().slice(0,10)}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    function importData() {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.json,application/json';
      input.onchange = e => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = ev => {
          try {
            const data = JSON.parse(ev.target.result);
            if (Array.isArray(data.lots)) {
              saveStoredLots(data.lots);
              if (Array.isArray(data.sales_history)) {
                saveStoredSales(data.sales_history);
              }
              recalculateDashboard();
              alert('Copia de seguridad restaurada con éxito.');
            } else {
              alert('Formato de archivo inválido.');
            }
          } catch (err) {
            alert('Error al leer el archivo JSON.');
          }
        };
        reader.readAsText(file);
      };
      input.click();
    }

    function resetData() {
      if (!confirm('¿Deseas restablecer la cartera inicial con los 3 paquetes (2023 18+12, 2024 30+20 y 2025 9+6)?')) return;
      saveStoredLots(DEFAULT_INITIAL_LOTS);
      saveStoredSales([]);
      recalculateDashboard();
      alert('Cartera restablecida con los 3 paquetes.');
    }

    // FAQ Y ACORDEÓN
    function toggleFaq(id) {
      const el = document.getElementById('content-' + id);
      const icon = document.getElementById('icon-' + id);
      if (!el) return;
      const isHidden = el.classList.contains('hidden');
      if (isHidden) {
        el.classList.remove('hidden');
        if (icon) icon.classList.add('rotate-180');
      } else {
        el.classList.add('hidden');
        if (icon) icon.classList.remove('rotate-180');
      }
    }

    // TEMA CLARO / OSCURO
    function applyTheme(theme) {
      const isDark = theme === 'dark';
      if (isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      safeSetItem(THEME_KEY, theme);
      document.querySelectorAll('.themeIcon').forEach(el => {
        el.textContent = isDark ? '☀️' : '🌙';
      });
      updateTabsUI();
    }

    function initTheme() {
      const savedTheme = safeGetItem(THEME_KEY);
      const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      const theme = savedTheme ? savedTheme : (systemPrefersDark ? 'dark' : 'light');
      applyTheme(theme);
    }

    function toggleTheme() {
      const isDark = document.documentElement.classList.contains('dark');
      applyTheme(isDark ? 'light' : 'dark');
    }

    function initApp() {
      try {
        initTheme();
        updateTabsUI();
        recalculateDashboard();
        fetchLivePrice();
        if (typeof window !== "undefined" && window.lucide && window.lucide.createIcons) {
          window.lucide.createIcons();
        }
      } catch (err) {
        console.error("Initialization error:", err);
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initApp);
    } else {
      initApp();
    }

    window.addEventListener('load', () => {
      try {
        if (typeof window !== "undefined" && window.lucide && window.lucide.createIcons) {
          window.lucide.createIcons();
        }
      } catch (e) {}
    });
  </script>
</body>
</html>
"""

full_content = html_layout + standalone_script

# Write to Desktop and to developer folder
with open(OUT_DESKTOP, "w", encoding="utf-8") as f:
    f.write(full_content)

with open(OUT_DEV, "w", encoding="utf-8") as f:
    f.write(full_content)

with open(OUT_DEV_ALIAS, "w", encoding="utf-8") as f:
    f.write(full_content)

print(f"Successfully generated standalone file at:")
print(f"  1. {OUT_DESKTOP} ({len(full_content)} bytes)")
print(f"  2. {OUT_DEV}")
print(f"  3. {OUT_DEV_ALIAS}")
