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

// Por defecto, la cartera inicial está en blanco
const DEFAULT_INITIAL_LOTS = [];

function buildLocalData(currentPrice, lots, sales) {
  const today = new Date();
  today.setHours(0,0,0,0);
  const msPerDay = 1000 * 60 * 60 * 24;

  let totalShares = 0;
  let totalGiftShares = 0;
  let totalInvested = 0;
  let totalMarketVal = 0;

  const lotsData = (lots || []).map(lot => {
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
    sales_history: sales || [],
    summary: {
      total_shares: totalShares,
      total_gift_shares: totalGiftShares,
      total_invested: Math.round(totalInvested * 100) / 100,
      total_market_val: Math.round(totalMarketVal * 100) / 100,
      total_profit: totalProfit,
      total_profit_pct: totalProfitPct,
      total_sales_count: (sales || []).length,
      total_sales_net: Math.round((sales || []).reduce((acc, s) => acc + (s.net_proceeds || 0), 0) * 100) / 100,
      total_sales_gross: Math.round((sales || []).reduce((acc, s) => acc + (s.gross_proceeds || 0), 0) * 100) / 100,
      total_sales_tax: Math.round((sales || []).reduce((acc, s) => acc + (s.tax || 0), 0) * 100) / 100,
      total_sales_gain: Math.round((sales || []).reduce((acc, s) => acc + (s.capital_gain || 0), 0) * 100) / 100,
    }
  };
}

// 1. Test Cartera Vacía (Por Defecto)
const emptyData = buildLocalData(187.26, DEFAULT_INITIAL_LOTS, []);
console.log("--- TEST ESTADO EN BLANCO ---");
console.log("Summary total shares:", emptyData.summary.total_shares);
console.log("Summary total invested:", emptyData.summary.total_invested);
console.log("Summary total market val:", emptyData.summary.total_market_val);
console.log("Lots count:", emptyData.lots.length);
if (emptyData.lots.length !== 0 || emptyData.summary.total_shares !== 0) {
  throw new Error("El estado por defecto debe estar en blanco (0 paquetes)");
}
console.log("✅ Cartera vacía verificada correctamente.");

// 2. Test Registro de Paquete Personalizado y Eliminación
const customLot = {
  id: "ESOP-2024",
  year: 2024,
  grant_date: "2024-05-15",
  unlock_date: "2027-05-15",
  purchased_shares: 15,
  matching_shares: 12,
  total_shares: 27,
  purchase_price: 150.26,
  total_paid: 2253.90,
  status: "LOCKED"
};
const populatedData = buildLocalData(187.26, [customLot], []);
console.log("\n--- TEST PAQUETE PERSONALIZADO ---");
console.log("Summary total shares:", populatedData.summary.total_shares);
console.log("Summary total invested:", populatedData.summary.total_invested);
console.log("Lots count:", populatedData.lots.length);
if (populatedData.lots.length !== 1 || populatedData.summary.total_shares !== 27) {
  throw new Error("El paquete personalizado no se calculó correctamente");
}

// Simular eliminación
const deletedData = buildLocalData(187.26, [], []);
if (deletedData.lots.length !== 0 || deletedData.summary.total_shares !== 0) {
  throw new Error("Fallo al eliminar el paquete");
}
console.log("✅ Registro y eliminación verificados con éxito.");
