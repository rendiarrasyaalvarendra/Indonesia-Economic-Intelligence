/**
 * Trade Analysis Module
 */
async function loadTrade() {
  const { fmt, createLineChart, createBarChart, createDoughnutChart, CHART_COLORS } = window.Charts;

  let data;
  try {
    data = await window.API.trade();
  } catch (e) {
    document.getElementById('trade-content').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  const latest = data.latest;
  document.getElementById('trade-exports').textContent = `USD ${Number(latest.exports).toLocaleString('id-ID')} Juta`;
  document.getElementById('trade-imports').textContent = `USD ${Number(latest.imports).toLocaleString('id-ID')} Juta`;
  document.getElementById('trade-balance').textContent =
    `${latest.balance >= 0 ? '+' : ''}USD ${Number(latest.balance).toLocaleString('id-ID')} Juta`;
  document.getElementById('trade-balance').className =
    `stat-value ${latest.balance >= 0 ? 'badge-green' : 'badge-red'}`;
  document.getElementById('trade-period').textContent = latest.period;
  document.getElementById('trade-surplus-months').textContent =
    `${data.summary.surplus_months}/${data.summary.total_months} bulan`;

  const labels = data.data.map(d => d.period);

  // Exports/Imports trend
  createLineChart('chart-trade-trend', labels, [
    { label: 'Ekspor', data: data.data.map(d => d.exports), color: CHART_COLORS.green },
    { label: 'Impor', data: data.data.map(d => d.imports), color: CHART_COLORS.red },
  ], {
    scales: {
      y: { ticks: { callback: v => `$${(v/1000).toFixed(0)}B`, color: '#94a3b8', font: { size: 10 } } }
    },
  });

  // Trade balance bar
  createBarChart('chart-trade-balance', labels.slice(-24), [{
    label: 'Neraca (USD Juta)',
    data: data.data.slice(-24).map(d => d.balance),
    backgroundColor: data.data.slice(-24).map(d => d.balance >= 0 ? CHART_COLORS.green : CHART_COLORS.red),
  }], {
    plugins: { legend: { display: false } },
    scales: {
      y: { ticks: { callback: v => `$${(v/1000).toFixed(0)}B`, color: '#94a3b8', font: { size: 10 } } }
    },
  });

  // Top commodities
  if (data.top_export_commodities) {
    createDoughnutChart('chart-commodities',
      data.top_export_commodities.map(d => d.commodity),
      data.top_export_commodities.map(d => d.value_b),
      Object.values(CHART_COLORS).slice(0, data.top_export_commodities.length),
    );
  }

  // YoY growth
  if (data.yoy_growth.exports_growth_pct !== null) {
    document.getElementById('trade-exp-growth').textContent =
      `${data.yoy_growth.exports_growth_pct >= 0 ? '+' : ''}${fmt(data.yoy_growth.exports_growth_pct, 2)}% YoY`;
    document.getElementById('trade-imp-growth').textContent =
      `${data.yoy_growth.imports_growth_pct >= 0 ? '+' : ''}${fmt(data.yoy_growth.imports_growth_pct, 2)}% YoY`;
  }
}

window.ModuleTrade = { loadTrade };
