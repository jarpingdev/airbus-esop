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

function buildLocalData(currentPrice, lots, sales) {
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
    }
  };
}

const data = buildLocalData(187.26, DEFAULT_INITIAL_LOTS, []);
console.log("Summary total shares:", data.summary.total_shares);
console.log("Summary total invested:", data.summary.total_invested);
console.log("Summary total market val:", data.summary.total_market_val);
console.log("Lots count:", data.lots.length);
