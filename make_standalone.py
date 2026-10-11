import re
from pathlib import Path

BASE_DIR = Path("/Users/joseantonio/Developer/airbus_esop")
INDEX_PATH = BASE_DIR / "index.html"
OUT_DESKTOP = Path("/Users/joseantonio/Desktop/Airbus_ESOP.html")
OUT_DEV = BASE_DIR / "Airbus_ESOP_Standalone.html"
OUT_DEV_ALIAS = BASE_DIR / "airbus_esop.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Get HTML up to <script>
split_marker = "  <!-- SCRIPT LÓGICA FRONTEND -->"
if split_marker not in content:
    idx = content.rfind("<script>")
    html_layout = content[:idx]
else:
    idx = content.find(split_marker)
    html_layout = content[:idx]

# In footer, add local export/import/reset buttons
footer_new = """  <!-- FOOTER -->
  <footer class="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-6 mt-8 text-center text-xs text-slate-400 dark:text-slate-500 safe-bottom">
    <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
      <div>Airbus ESOP Calculadora Patrimonial • Diseñado para empleados en España</div>
      <div class="flex items-center space-x-3 text-slate-500 dark:text-slate-400">
        <button onclick="exportData()" class="hover:underline">💾 Guardar Copia (.json)</button>
        <span>•</span>
        <button onclick="importData()" class="hover:underline">📂 Cargar Copia</button>
        <span>•</span>
        <button onclick="resetData()" class="text-rose-500 hover:underline">🔄 Restablecer 3 Paquetes</button>
      </div>
    </div>
  </footer>"""

html_layout = re.sub(r'(<!-- FOOTER -->\s*)?<footer.*?</footer>', footer_new, html_layout, flags=re.DOTALL)

script_body = """  <!-- SCRIPT LÓGICA FRONTEND STANDALONE (100% OFFLINE, ROBUSTO Y AUTÓNOMO) -->
  <script>
    // ICONOS INLINE (SVG Nativos, Cero dependencias externas)
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

    // CONFIGURACIÓN DE ALMACENAMIENTO V4
    const STORAGE_KEY = "airbus_esop_portfolio_v4";
    const SALES_STORAGE_KEY = "airbus_esop_sales_v4";
    const THEME_KEY = "airbus_esop_theme_mode";
    const TAB_KEY = "airbus_esop_active_tab";
    const PRICE_KEY = "airbus_esop_custom_price";

    // LOS 3 PAQUETES INTEGRADOS
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

    const HISTORICAL_CAMPAIGNS = {
      2027: { year: 2027, price: null, grant_date: "2027-05-15", unlock_date: "2030-05-15", label: "2027 — Estimado en vivo (~187 €)", is_official: false, notes: "Estimación según cotización de mercado" },
      2026: { year: 2026, price: 167.90, grant_date: "2026-05-15", unlock_date: "2029-05-15", label: "2026 — 167,90 € (Oficial)", is_official: true, notes: "Precio oficial Pure Registered fijado por Airbus" },
      2025: { year: 2025, price: 162.78, grant_date: "2025-05-15", unlock_date: "2028-05-15", label: "2025 — 162,78 € (Oficial)", is_official: true, notes: "Precio oficial Pure Registered fijado por Airbus" },
      2024: { year: 2024, price: 150.26, grant_date: "2024-05-15", unlock_date: "2027-05-15", label: "2024 — 150,26 € (Oficial)", is_official: true, notes: "Precio oficial Pure Registered fijado por Airbus" },
      2023: { year: 2023, price: 119.06, grant_date: "2023-05-15", unlock_date: "2026-05-15", label: "2023 — 119,06 € (Oficial)", is_official: true, notes: "Precio oficial Pure Registered fijado por Airbus" },
      2022: { year: 2022, price: 117.88, grant_date: "2022-05-15", unlock_date: "2025-05-15", label: "2022 — 117,88 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" },
      2021: { year: 2021, price: 93.90, grant_date: "2021-05-15", unlock_date: "2024-05-15", label: "2021 — 93,90 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" },
      2020: { year: 2020, price: 136.60, grant_date: "2020-05-15", unlock_date: "2023-05-15", label: "2020 — 136,60 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" },
      2019: { year: 2019, price: 134.40, grant_date: "2019-05-15", unlock_date: "2022-05-15", label: "2019 — 134,40 € (Oficial)", is_official: true, notes: "Precio oficial fijado por Airbus" }
    };

    const OFFICIAL_PACKAGES_MAP = {
      "15+12": { purchased: 15, matching: 12, total: 27, desc: "⭐ Paquete Estrella (15 + 12 = 27 acc • 44.4% regalo)" },
      "18+12": { purchased: 18, matching: 12, total: 30, desc: "⭐ Paquete Clásico (18 + 12 = 30 acc • 40% regalo)" },
      "30+20": { purchased: 30, matching: 20, total: 50, desc: "⭐ Paquete Amplio (30 + 20 = 50 acc • 40% regalo)" },
      "3+2": { purchased: 3, matching: 2, total: 5, desc: "3 + 2 = 5 acc" },
      "6+4": { purchased: 6, matching: 4, total: 10, desc: "6 + 4 = 10 acc" },
      "9+6": { purchased: 9, matching: 6, total: 15, desc: "9 + 6 = 15 acc" },
      "42+28": { purchased: 42, matching: 28, total: 70, desc: "42 + 28 = 70 acc" },
      "54+36": { purchased: 54, matching: 36, total: 90, desc: "54 + 36 = 90 acc" }
    };

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
    let globalStatus = null;
    let currentSimPrice = 187.26;

    function formatEuro(val) {
      if (isNaN(val) || val === null || val === undefined) val = 0;
      return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(val);
    }

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

    function buildLocalData(currentPrice) {
      const lots = getStoredLots();
      const sales = getStoredSales();
      const today = new Date();
      today.setHours(0,0,0,0);
      const msPerDay = 1000 * 60 * 60 * 24;

      let totalShares = 0;
      let totalGiftShares = 0;
      let totalInvested = 0;
      let totalMarketVal = 0;

      const lotsData = lots.map(lot => {
        const grantD = new Date(lot.grant_date);
        const unlockD = new Date(lot.unlock_date);
        const daysLeft = Math.max(0, Math.ceil((unlockD - today) / msPerDay));
        const totalHoldingDays = Math.max(1, Math.ceil((unlockD - grantD) / msPerDay));
        const daysPassed = Math.max(0, Math.ceil((today - grantD) / msPerDay));
        const progressPct = Math.min(100, Math.round((daysPassed / totalHoldingDays) * 1000) / 10);
        const isMature = today >= unlockD;

        const shares = lot.total_shares;
        const paid = lot.total_paid;
        const mktVal = Math.round(shares * currentPrice * 100) / 100;
        const profit = Math.round((mktVal - paid) * 100) / 100;
        const profitPct = paid > 0 ? Math.round((profit / paid * 1000) / 10) : 0;
        const effCost = shares > 0 ? Math.round((paid / shares) * 100) / 100 : 0;

        totalShares += shares;
        totalGiftShares += lot.matching_shares;
        totalInvested += paid;
        totalMarketVal += mktVal;

        return {
          ...lot,
          market_value: mktVal,
          profit: profit,
          profit_pct: profitPct,
          days_left: daysLeft,
          progress_pct: progressPct,
          is_mature: isMature,
          effective_cost_per_share: effCost
        };
      });

      const totalProfit = Math.round((totalMarketVal - totalInvested) * 100) / 100;
      const totalProfitPct = totalInvested > 0 ? Math.round((totalProfit / totalInvested * 1000) / 10) : 0;

      return {
        quote: {
          price: currentPrice,
          change: 1.80,
          pct_change: 0.97,
          timestamp: new Date().toLocaleTimeString('es-ES')
        },
        lots: lotsData,
        sales_history: sales,
        summary: {
          total_shares: totalShares,
          total_gift_shares: totalGiftShares,
          total_invested: Math.round(totalInvested * 100) / 100,
          total_market_val: Math.round(totalMarketVal * 100) / 100,
          total_profit: totalProfit,
          total_profit_pct: totalProfitPct,
          total_sales_count: sales.length,
          total_sales_net: Math.round(sales.reduce((acc, s) => acc + (s.net_proceeds || 0), 0) * 100) / 100,
          total_sales_gross: Math.round(sales.reduce((acc, s) => acc + (s.gross_proceeds || 0), 0) * 100) / 100,
          total_sales_tax: Math.round(sales.reduce((acc, s) => acc + (s.tax || 0), 0) * 100) / 100,
          total_sales_gain: Math.round(sales.reduce((acc, s) => acc + (s.capital_gain || 0), 0) * 100) / 100,
        },
        packages: DEFAULT_PACKAGES
      };
    }

    function loadData() {
      try {
        const data = buildLocalData(currentLivePrice);
        globalStatus = data;

        // Header
        const hp = document.getElementById('headerPrice');
        if (hp) hp.textContent = formatEuro(data.quote.price);
        const hc = document.getElementById('headerChange');
        if (hc) hc.textContent = (data.quote.change >= 0 ? '+' : '') + data.quote.pct_change + '%';
        const lu = document.getElementById('lastUpdated');
        if (lu) lu.textContent = data.quote.timestamp;

        // KPIs Cartera
        const kmv = document.getElementById('kpiMarketVal');
        if (kmv) kmv.textContent = formatEuro(data.summary.total_market_val);
        const kpt = document.getElementById('kpiProfitText');
        if (kpt) kpt.textContent = `+${formatEuro(data.summary.total_profit)} (+${data.summary.total_profit_pct}%)`;
        const ki = document.getElementById('kpiInvested');
        if (ki) ki.textContent = formatEuro(data.summary.total_invested);
        const kst = document.getElementById('kpiSharesTotal');
        if (kst) kst.textContent = data.summary.total_shares;

        // Badges
        const carteraBadge = document.getElementById('badge-summary-cartera');
        if (carteraBadge) {
          carteraBadge.textContent = `${formatEuro(data.summary.total_market_val)} (+${data.summary.total_profit_pct}%)`;
        }

        const ventasBadge = document.getElementById('badge-summary-ventas');
        if (ventasBadge) {
          ventasBadge.textContent = `${data.summary.total_sales_count || 0} ventas • Neto: ${formatEuro(data.summary.total_sales_net || 0)}`;
        }

        // KPIs de ventas
        const kpiSalesGross = document.getElementById('kpiSalesGross');
        if (kpiSalesGross) kpiSalesGross.textContent = formatEuro(data.summary.total_sales_gross || 0);
        const kpiSalesGain = document.getElementById('kpiSalesGain');
        if (kpiSalesGain) kpiSalesGain.textContent = '+' + formatEuro(data.summary.total_sales_gain || 0);
        const kpiSalesTax = document.getElementById('kpiSalesTax');
        if (kpiSalesTax) kpiSalesTax.textContent = '-' + formatEuro(data.summary.total_sales_tax || 0);
        const kpiSalesNet = document.getElementById('kpiSalesNet');
        if (kpiSalesNet) kpiSalesNet.textContent = formatEuro(data.summary.total_sales_net || 0);

        const lockedLots = data.lots.filter(l => !l.is_mature && l.days_left > 0).sort((a,b) => a.days_left - b.days_left);
        const targetLot = lockedLots.length > 0 ? lockedLots[0] : (data.lots[0] || null);
        const kec = document.getElementById('kpiEffectiveCost');
        const kdl = document.getElementById('kpiDaysLeft');
        const kpb = document.getElementById('kpiProgressBar');
        if (targetLot) {
          if (kec) kec.textContent = formatEuro(targetLot.effective_cost_per_share);
          if (kdl) kdl.textContent = targetLot.days_left;
          if (kpb) kpb.style.width = targetLot.progress_pct + '%';
        } else {
          if (kec) kec.textContent = formatEuro(0);
          if (kdl) kdl.textContent = '-';
          if (kpb) kpb.style.width = '0%';
        }

        // Renderizado de Lotes e Historial
        renderLotsTable(data.lots);
        renderSalesHistory(data.sales_history || []);

        // Slider Inicial
        const slider = document.getElementById('priceSlider');
        if (slider && !slider.dataset.userMoved) {
          slider.value = Math.round(currentLivePrice);
          const slbl = document.getElementById('sliderPriceLabel');
          if (slbl) slbl.textContent = formatEuro(currentLivePrice);
        }
        runSimulation(currentLivePrice);

        // Paquetes
        renderPackages(data.packages, currentLivePrice, 2500);

      } catch (err) {
        console.error('Error cargando datos:', err);
      }
    }

    function renderLotsTable(lots) {
      const tbody = document.getElementById('lotsTableBody');
      const mobileContainer = document.getElementById('lotsCardsMobile');
      const simSelect = document.getElementById('simLotSelect');
      const saleSelect = document.getElementById('saleLotSelect');

      if (tbody) tbody.innerHTML = '';
      if (mobileContainer) mobileContainer.innerHTML = '';

      // Actualizar selectores
      if (simSelect) {
        const prevSimVal = simSelect.value;
        simSelect.innerHTML = '';
        if (lots && lots.length > 0) {
          lots.forEach(l => {
            const opt = document.createElement('option');
            opt.value = l.id;
            opt.textContent = `${l.id} (${l.total_shares} acc - Campaña ${l.year})`;
            simSelect.appendChild(opt);
          });
          if (prevSimVal && lots.some(l => l.id === prevSimVal)) {
            simSelect.value = prevSimVal;
          } else {
            simSelect.value = lots[0].id;
          }
        } else {
          const opt = document.createElement('option');
          opt.value = '';
          opt.textContent = 'Sin lotes en cartera';
          simSelect.appendChild(opt);
        }
      }

      if (saleSelect) {
        const prevSaleVal = saleSelect.value;
        saleSelect.innerHTML = '';
        if (lots && lots.length > 0) {
          lots.forEach(l => {
            const opt = document.createElement('option');
            opt.value = l.id;
            opt.textContent = `${l.id} • ${l.total_shares} acc disp. (${l.is_mature ? '🔓 Desbloqueado' : '🔒 Bloqueado'})`;
            saleSelect.appendChild(opt);
          });
          if (prevSaleVal && lots.some(l => l.id === prevSaleVal)) {
            saleSelect.value = prevSaleVal;
          } else {
            saleSelect.value = lots[0].id;
          }
        } else {
          const opt = document.createElement('option');
          opt.value = '';
          opt.textContent = 'Sin lotes en cartera';
          saleSelect.appendChild(opt);
        }
      }

      if (!lots || lots.length === 0) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400">No hay lotes en cartera. ¡Registra tu primera compra con el botón superior!</td></tr>`;
        if (mobileContainer) mobileContainer.innerHTML = `<div class="p-4 text-center text-xs text-slate-400 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">No hay lotes registrados.</div>`;
        return;
      }

      lots.forEach(lot => {
        if (tbody) {
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
              <button onclick="deleteLot('${lot.id}')" class="px-2.5 py-1 text-xs font-semibold text-slate-500 hover:text-slate-700 dark:text-slate-400 rounded-lg border border-slate-200 dark:border-slate-700 transition">
                Eliminar
              </button>
            </td>
          `;
          tbody.appendChild(tr);
        }

        if (mobileContainer) {
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
                <span class="text-slate-500 dark:text-slate-400 block text-[10px] uppercase font-semibold">Invertido</span>
                <span class="font-bold text-slate-900 dark:text-white text-sm">${formatEuro(lot.total_paid)}</span>
                <span class="text-[11px] text-slate-500 dark:text-slate-400 block">a ${formatEuro(lot.purchase_price)}</span>
              </div>
              <div class="bg-slate-50 dark:bg-slate-900/60 p-2 rounded-lg border border-slate-100 dark:border-slate-800">
                <span class="text-slate-500 dark:text-slate-400 block text-[10px] uppercase font-semibold">Valor Mercado</span>
                <span class="font-bold text-slate-900 dark:text-white text-sm">${formatEuro(lot.market_value)}</span>
              </div>
              <div class="bg-slate-50 dark:bg-slate-900/60 p-2 rounded-lg border border-slate-100 dark:border-slate-800">
                <span class="text-slate-500 dark:text-slate-400 block text-[10px] uppercase font-semibold">Beneficio</span>
                <span class="font-bold text-emerald-600 dark:text-emerald-400 text-sm">+${formatEuro(lot.profit)}</span>
                <span class="text-[11px] text-emerald-500 font-medium block">+${lot.profit_pct}%</span>
              </div>
            </div>
            <div class="pt-2 flex items-center justify-between border-t border-slate-100 dark:border-slate-700/60">
              <span class="text-[11px] text-slate-400">Coste medio: ${formatEuro(lot.effective_cost_per_share)}</span>
              <div class="space-x-2">
                <button onclick="openSaleModalForLot('${lot.id}')" class="text-xs font-bold text-rose-600 hover:text-rose-700 dark:text-rose-400 hover:underline">
                  Vender
                </button>
                <button onclick="deleteLot('${lot.id}')" class="text-xs text-slate-400 hover:text-rose-500">
                  Eliminar
                </button>
              </div>
            </div>
          `;
          mobileContainer.appendChild(card);
        }
      });
      if (typeof window !== "undefined" && window.lucide && window.lucide.createIcons) {
        window.lucide.createIcons();
      }
    }

    function onSimLotChange() {
      const select = document.getElementById('simLotSelect');
      if (select) {
        runSimulation(currentSimPrice);
      }
    }

    function runSimulation(price) {
      currentSimPrice = price !== undefined ? price : currentLivePrice;
      const simSelect = document.getElementById('simLotSelect');
      const lots = getStoredLots();
      const lotId = simSelect && simSelect.value ? simSelect.value : (lots.length > 0 ? lots[0].id : null);
      const lot = lotId ? (lots.find(l => l.id === lotId) || lots[0]) : null;

      const simSharesEl = document.getElementById('simSharesCountText');
      const simGrossEl = document.getElementById('simGrossProceeds');
      const simCostEl = document.getElementById('simCostBasis');
      const simGainEl = document.getElementById('simCapitalGain');
      const simTaxEl = document.getElementById('simTax') || document.getElementById('simTaxSpain');
      const simNetEl = document.getElementById('simNetInPocket');

      if (!lot) {
        if (simSharesEl) simSharesEl.textContent = '0';
        if (simGrossEl) simGrossEl.textContent = formatEuro(0);
        if (simCostEl) simCostEl.textContent = formatEuro(0);
        if (simGainEl) simGainEl.textContent = formatEuro(0);
        if (simTaxEl) simTaxEl.textContent = formatEuro(0);
        if (simNetEl) simNetEl.textContent = formatEuro(0);
        const statusEl = document.getElementById('simLotMatureStatus');
        if (statusEl) {
          statusEl.className = 'text-xs font-bold text-slate-400';
          statusEl.textContent = '-';
        }
        const surpEl = document.getElementById('simSurplus') || document.getElementById('simWheelSurplus');
        if (surpEl) {
          surpEl.textContent = formatEuro(0);
          surpEl.className = 'font-black text-slate-400';
        }
        const badgeSim = document.getElementById('badge-summary-simulador');
        if (badgeSim) badgeSim.textContent = `Neto: ~${formatEuro(0)}`;
        return;
      }

      const shares = lot.total_shares;
      const costBasis = lot.total_paid;
      const gross = Math.round(shares * currentSimPrice * 100) / 100;
      const gain = Math.max(Math.round((gross - costBasis) * 100) / 100, 0);
      const tax = calculateTaxSpain(gain);
      const net = Math.round((gross - tax) * 100) / 100;

      const today = new Date(); today.setHours(0,0,0,0);
      const isMature = today >= new Date(lot.unlock_date);

      if (simSharesEl) simSharesEl.textContent = shares;
      if (simGrossEl) simGrossEl.textContent = formatEuro(gross);
      if (simCostEl) simCostEl.textContent = '-' + formatEuro(costBasis);
      if (simGainEl) simGainEl.textContent = '+' + formatEuro(gain);
      if (simTaxEl) simTaxEl.textContent = '-' + formatEuro(tax);
      if (simNetEl) simNetEl.textContent = formatEuro(net);

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

      const surplus = net - 2500;
      const surpEl = document.getElementById('simSurplus') || document.getElementById('simWheelSurplus');
      if (surpEl) {
        surpEl.textContent = (surplus >= 0 ? '+' : '') + formatEuro(surplus);
        surpEl.className = surplus >= 0 ? 'font-black text-emerald-600 dark:text-emerald-400' : 'font-black text-rose-500';
      }

      const badgeSim = document.getElementById('badge-summary-simulador');
      if (badgeSim) badgeSim.textContent = `Neto: ~${formatEuro(net)}`;
    }

    function onPriceSliderChange(val) {
      const slider = document.getElementById('priceSlider');
      if (slider) slider.dataset.userMoved = "true";
      const num = parseFloat(val);
      const sLabel = document.getElementById('sliderPriceLabel');
      if (sLabel) sLabel.textContent = formatEuro(num);
      runSimulation(num);
    }

    function onBudgetChange(val) {
      const bLabel = document.getElementById('budgetLabel') || document.getElementById('budgetSliderLabel');
      if (bLabel) bLabel.textContent = formatEuro(parseFloat(val));
      if (globalStatus && globalStatus.packages) {
        renderPackages(globalStatus.packages, currentLivePrice, parseFloat(val));
      }
    }

    function renderPackages(packages, price, budget) {
      const container = document.getElementById('packagesContainer') || document.getElementById('packagesGrid');
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

      if (bestPkg) {
        const costBest = bestPkg.purchased * price;
        const giftVal = bestPkg.matching * price;
        const banner = document.getElementById('recommendedPkgBanner');
        if (banner) {
          banner.innerHTML = `
            <div class="flex items-center justify-between mb-1 gap-2">
              <span class="text-xs font-bold text-indigo-900 dark:text-indigo-200 uppercase truncate">Paquete Sugerido: ${bestPkg.purchased} + ${bestPkg.matching} (Pqte ${bestPkg.id})</span>
              <span class="text-xs font-bold text-indigo-600 dark:text-indigo-300 bg-white dark:bg-slate-900 px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800 flex-shrink-0">
                Descuento ~${((bestPkg.matching/bestPkg.total)*100).toFixed(0)}%
              </span>
            </div>
            <p class="text-xs text-indigo-700 dark:text-indigo-300">
              Pagas ${bestPkg.purchased} acciones (~${formatEuro(costBest)}) y te regalan ${bestPkg.matching} acciones valoradas en ~${formatEuro(giftVal)}.
            </p>
          `;
        }
        const optBadge = document.getElementById('badge-summary-optimizador');
        if (optBadge) {
          optBadge.textContent = `Sugerido: ${bestPkg.purchased}+${bestPkg.matching}`;
        }
      }
    }

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

    function onLotYearChange() {
      const yr = parseInt(document.getElementById('lotYearSelect').value);
      const camp = HISTORICAL_CAMPAIGNS[yr] || { price: currentLivePrice, grant_date: `${yr}-05-15`, is_official: false };
      const p = (camp.price !== null && camp.price !== undefined) ? camp.price : currentLivePrice;
      const lotPriceEl = document.getElementById('lotPrice');
      const lotDateEl = document.getElementById('lotDate');
      if (lotPriceEl) lotPriceEl.value = p.toFixed(2);
      if (lotDateEl) lotDateEl.value = camp.grant_date || `${yr}-05-15`;
      
      const badge = document.getElementById('lotYearBadge');
      if (badge) {
        badge.textContent = camp.is_official ? 'Oficial Airbus' : 'Estimación en Vivo';
        badge.className = camp.is_official ? 'text-[11px] font-semibold text-emerald-600 dark:text-emerald-400' : 'text-[11px] font-semibold text-amber-600 dark:text-amber-400';
      }

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
          const lp = document.getElementById('lotPurchased');
          const lm = document.getElementById('lotMatching');
          if (lp) lp.value = pkg.purchased;
          if (lm) lm.value = pkg.matching;
        }
      }
      updateLotPreview();
    }

    function toggleManualLotFields() {
      const area = document.getElementById('manualFieldsArea');
      if (area) area.classList.toggle('hidden');
    }

    function updateLotPreview() {
      const yr = parseInt(document.getElementById('lotYearSelect')?.value || 2026);
      const purchased = parseInt(document.getElementById('lotPurchased')?.value) || 0;
      const matching = parseInt(document.getElementById('lotMatching')?.value) || 0;
      const totalShares = purchased + matching;
      const price = parseFloat(document.getElementById('lotPrice')?.value) || 0;
      const totalPaid = Math.round(purchased * price * 100) / 100;

      const livePrice = currentLivePrice || 189.30;
      const marketVal = Math.round(totalShares * livePrice * 100) / 100;
      const gain = Math.round((marketVal - totalPaid) * 100) / 100;

      const campPriceEl = document.getElementById('previewCampaignPrice');
      if (campPriceEl) campPriceEl.textContent = formatEuro(price);

      const totalCostEl = document.getElementById('previewTotalCost');
      if (totalCostEl) totalCostEl.textContent = formatEuro(totalPaid);

      const sharesBreakdownEl = document.getElementById('previewSharesBreakdown');
      if (sharesBreakdownEl) {
        sharesBreakdownEl.textContent = `${totalShares} acc (${purchased} pagadas + ${matching} gratis)`;
      }

      const hintEl = document.getElementById('lotPackageSharesHint');
      if (hintEl) {
        hintEl.textContent = `${totalShares} acc totales (${matching} gratis)`;
      }

      // Legacy fallback IDs if present
      const pPurch = document.getElementById('previewLotPurchased');
      if (pPurch) pPurch.textContent = purchased;
      const pMatch = document.getElementById('previewLotMatching');
      if (pMatch) pMatch.textContent = matching;
      const pTot = document.getElementById('previewLotTotal');
      if (pTot) pTot.textContent = totalShares;
      const pInv = document.getElementById('previewLotInvested');
      if (pInv) pInv.textContent = formatEuro(totalPaid);
      const pMkt = document.getElementById('previewLotMktVal');
      if (pMkt) pMkt.textContent = formatEuro(marketVal);
      const pProf = document.getElementById('previewLotProfit');
      if (pProf) pProf.textContent = '+' + formatEuro(gain);
    }

    function openLotModal() {
      document.getElementById('lotYearSelect').value = '2024';
      document.getElementById('lotPackageSelect').value = '15+12';
      onLotYearChange();
      onLotPackageChange();
      document.getElementById('lotModal').classList.remove('hidden');
    }

    function closeLotModal() {
      document.getElementById('lotModal').classList.add('hidden');
    }

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
      const today = new Date(); today.setHours(0,0,0,0);
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
      const existingIdx = lots.findIndex(l => l.id === newLot.id);
      if (existingIdx >= 0) {
        lots[existingIdx] = newLot;
      } else {
        lots.push(newLot);
      }
      lots.sort((a,b) => a.year - b.year);
      saveStoredLots(lots);
      closeLotModal();
      loadData();
    }

    function deleteLot(lotId) {
      if (!confirm(`¿Estás seguro de que deseas eliminar el lote ${lotId}?`)) return;
      const lots = getStoredLots().filter(l => l.id !== lotId);
      saveStoredLots(lots);
      loadData();
    }

    function renderSalesHistory(sales) {
      const tbody = document.getElementById('salesTableBody');
      const mobileContainer = document.getElementById('salesCardsMobile');
      if (!tbody) return;

      tbody.innerHTML = '';
      if (mobileContainer) mobileContainer.innerHTML = '';

      if (!sales || sales.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="text-center py-6 text-slate-400">No hay ventas registradas todavía. Puedes simular y ejecutar una venta en cualquier momento.</td></tr>`;
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
            <button onclick="deleteSale('${s.id}')" class="px-2 py-0.5 text-[11px] font-semibold text-rose-600 hover:text-rose-700 dark:text-rose-400">
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
              <span class="font-bold text-slate-900 dark:text-white">${s.lot_id} • ${s.shares_sold} acc</span>
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
      if (typeof window !== "undefined" && window.lucide && window.lucide.createIcons) {
        window.lucide.createIcons();
      }
    }

    function openSaleModal() {
      const lots = getStoredLots();
      if (!lots || lots.length === 0) {
        alert('No tienes lotes registrados en cartera para vender.');
        return;
      }
      renderLotsTable(lots);
      onSaleLotChange();
      document.getElementById('saleDate').value = new Date().toISOString().slice(0, 10);
      document.getElementById('saleModal').classList.remove('hidden');
    }

    function openSaleModalForLot(lotId) {
      const lots = getStoredLots();
      if (!lots || lots.length === 0) {
        alert('No tienes lotes registrados en cartera para vender.');
        return;
      }
      openSaleModal();
      const select = document.getElementById('saleLotSelect');
      if (select) {
        select.value = lotId;
        onSaleLotChange();
      }
    }

    function openSaleModalFromSim() {
      const lots = getStoredLots();
      if (!lots || lots.length === 0) {
        alert('No tienes lotes registrados en cartera para vender.');
        return;
      }
      const simSelect = document.getElementById('simLotSelect');
      const lotId = simSelect && simSelect.value ? simSelect.value : (lots[0]?.id);
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

      const lots = getStoredLots();
      const lotIdx = lots.findIndex(l => l.id === lotId);
      if (lotIdx === -1) {
        alert("Lote no encontrado");
        return;
      }
      const lot = lots[lotIdx];
      const maxShares = lot.total_shares;
      if (shares <= 0 || shares > maxShares) {
        alert(`Cantidad no válida. Máximo disponible: ${maxShares}`);
        return;
      }

      const fraction = shares / maxShares;
      const purchasedSold = Math.round(lot.purchased_shares * fraction * 100) / 100;
      const matchingSold = Math.round(lot.matching_shares * fraction * 100) / 100;
      const costBasisSold = Math.round(lot.total_paid * fraction * 100) / 100;

      const grossProceeds = Math.round(shares * price * 100) / 100;
      const capitalGain = Math.round((grossProceeds - costBasisSold) * 100) / 100;
      const tax = calculateTaxSpain(capitalGain);
      const netProceeds = Math.round((grossProceeds - tax) * 100) / 100;

      const unlockD = new Date(lot.unlock_date);
      const isMature = new Date(date) >= unlockD;

      const saleRecord = {
        id: "SALE-" + Date.now(),
        date: date,
        lot_id: lot.id,
        shares_sold: shares,
        sell_price: price,
        gross_proceeds: grossProceeds,
        cost_basis: costBasisSold,
        capital_gain: capitalGain,
        tax: tax,
        net_proceeds: netProceeds,
        is_mature: isMature,
        notes: `Venta de ${shares} acc de ${lot.id} a ${price.toFixed(2)} €`,
        snapshot_lot: JSON.parse(JSON.stringify(lot))
      };

      const sales = getStoredSales();
      sales.unshift(saleRecord);
      saveStoredSales(sales);

      if (shares === maxShares) {
        lots.splice(lotIdx, 1);
      } else {
        lot.total_shares -= shares;
        lot.purchased_shares = Math.round((lot.purchased_shares - purchasedSold) * 100) / 100;
        lot.matching_shares = Math.round((lot.matching_shares - matchingSold) * 100) / 100;
        lot.total_paid = Math.round((lot.total_paid - costBasisSold) * 100) / 100;
      }

      saveStoredLots(lots);
      closeSaleModal();
      loadData();
      switchTab('ventas');
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
      loadData();
    }

    async function fetchLivePrice() {
      try {
        const res = await fetch('https://query1.finance.yahoo.com/v8/finance/chart/AIR.PA?interval=1d', { mode: 'cors' });
        if (res.ok) {
          const d = await res.json();
          const meta = d.chart.result[0].meta;
          currentLivePrice = parseFloat(meta.regularMarketPrice);
          loadData();
          return;
        }
      } catch (e) {}
    }

    function refreshData() {
      fetchLivePrice();
      loadData();
    }

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
              loadData();
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
      loadData();
      alert('Cartera restablecida con los 3 paquetes.');
    }

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
        loadData();
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

full_content = html_layout + script_body

for path in [OUT_DESKTOP, OUT_DEV, OUT_DEV_ALIAS]:
    with open(path, "w", encoding="utf-8") as f:
        f.write(full_content)
    print(f"Generated: {path} ({len(full_content)} bytes)")
