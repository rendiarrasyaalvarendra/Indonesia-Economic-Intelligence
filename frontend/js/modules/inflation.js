/**
 * Inflation Analysis Module
 */
async function loadInflation() {
  const { fmt, createLineChart, createBarChart, CHART_COLORS, hexToRgba } = window.Charts;

  let data, provincial;
  try {
    [data, provincial] = await Promise.all([
      window.API.inflation(),
      window.API.inflationProvincial(),
    ]);
  } catch (e) {
    document.getElementById('inflation-content').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  // Latest stats
  const latest = data.latest;
  document.getElementById('inf-latest-yoy').textContent = `${fmt(latest.yoy, 2)}%`;
  document.getElementById('inf-latest-mom').textContent = `${fmt(latest.mom, 2)}%`;
  document.getElementById('inf-latest-cpi').textContent = fmt(latest.cpi, 2);
  document.getElementById('inf-latest-ytd').textContent = data.ytd !== null ? `${fmt(data.ytd, 2)}%` : 'N/A';
  document.getElementById('inf-latest-period').textContent = latest.period;

  const months = data.data.slice(-24);
  const labels = months.map(d => d.period);

  // YoY Chart
  createLineChart('chart-inf-yoy', labels, [{
    label: 'Inflasi YoY (%)', data: months.map(d => d.yoy),
    color: CHART_COLORS.yellow, fill: true, bgColor: hexToRgba(CHART_COLORS.yellow, 0.08),
  }], {
    plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ` ${fmt(ctx.parsed.y, 2)}%` } } },
    scales: { y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } } },
  });

  // MoM Chart
  createBarChart('chart-inf-mom', labels.slice(-12), [{
    label: 'Inflasi MoM (%)',
    data: months.slice(-12).map(d => d.mom),
    backgroundColor: months.slice(-12).map(d => d.mom >= 0 ? CHART_COLORS.blue : CHART_COLORS.red),
  }], {
    plugins: { legend: { display: false } },
    scales: { y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } } },
  });

  // CPI Chart
  createLineChart('chart-cpi', labels, [{
    label: 'CPI (IHK)', data: months.map(d => d.cpi),
    color: CHART_COLORS.cyan,
  }], {
    plugins: { legend: { display: false } },
    scales: { y: { ticks: { color: '#94a3b8', font: { size: 10 } } } },
  });

  // Provincial inflation bar chart
  const topProv = provincial.data.slice(0, 15);
  createBarChart('chart-inf-provincial', topProv.map(d => d.province_name.replace('Kepulauan', 'Kep.')), [{
    label: 'Inflasi YoY (%)',
    data: topProv.map(d => d.yoy),
    backgroundColor: topProv.map((_, i) => i < 5 ? CHART_COLORS.red : (i < 10 ? CHART_COLORS.yellow : CHART_COLORS.blue)),
  }], {
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { maxRotation: 60, font: { size: 9 }, color: '#94a3b8' } },
      y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } },
    },
  });

  // Highest / lowest
  document.getElementById('inf-prov-highest').textContent =
    `${provincial.highest?.province_name}: ${fmt(provincial.highest?.yoy, 2)}%`;
  document.getElementById('inf-prov-lowest').textContent =
    `${provincial.lowest?.province_name}: ${fmt(provincial.lowest?.yoy, 2)}%`;
}

window.ModuleInflation = { loadInflation };
