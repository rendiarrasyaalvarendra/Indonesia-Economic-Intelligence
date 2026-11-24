/**
 * Monetary Analysis Module
 */
async function loadMonetary() {
  const { fmt, createLineChart, CHART_COLORS, hexToRgba } = window.Charts;

  let data;
  try {
    data = await window.API.monetary();
  } catch (e) {
    document.getElementById('monetary-content').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  const { exchange_rate, bi_rate } = data;
  const erLatest = exchange_rate.latest;
  const biLatest = bi_rate.latest;

  document.getElementById('er-latest').textContent = `Rp ${Number(erLatest.usd_idr).toLocaleString('id-ID')}`;
  document.getElementById('er-period').textContent = erLatest.period;
  document.getElementById('er-mean').textContent = `Rata-rata: Rp ${Number(exchange_rate.stats.mean).toLocaleString('id-ID')}`;
  document.getElementById('er-range').textContent = `Range: Rp ${Number(exchange_rate.stats.min).toLocaleString('id-ID')} – ${Number(exchange_rate.stats.max).toLocaleString('id-ID')}`;

  document.getElementById('bi-latest').textContent = `${fmt(biLatest.rate, 2)}%`;
  document.getElementById('bi-period').textContent = biLatest.period;
  document.getElementById('bi-mean').textContent = `Rata-rata: ${fmt(bi_rate.stats.mean, 2)}%`;
  document.getElementById('bi-range').textContent = `Range: ${fmt(bi_rate.stats.min, 2)}% – ${fmt(bi_rate.stats.max, 2)}%`;

  const erLabels = exchange_rate.data.map(d => d.period);
  const erValues = exchange_rate.data.map(d => d.usd_idr);

  // Exchange rate chart
  createLineChart('chart-exchange-rate', erLabels, [{
    label: 'USD/IDR (Rp)', data: erValues,
    color: CHART_COLORS.green, fill: true, bgColor: hexToRgba(CHART_COLORS.green, 0.08),
  }], {
    plugins: { legend: { display: false }, tooltip: { callbacks: {
      label: ctx => ` Rp ${Number(ctx.parsed.y).toLocaleString('id-ID')}`
    } } },
    scales: {
      y: { ticks: { callback: v => `Rp ${(v/1000).toFixed(0)}K`, color: '#94a3b8', font: { size: 10 } } }
    },
  });

  // BI Rate chart (stepped)
  const biLabels = bi_rate.data.map(d => d.period);
  createLineChart('chart-bi-rate', biLabels, [{
    label: 'BI Rate (%)', data: bi_rate.data.map(d => d.rate),
    color: CHART_COLORS.purple, stepped: true,
  }], {
    plugins: { legend: { display: false }, tooltip: { callbacks: {
      label: ctx => ` ${fmt(ctx.parsed.y, 2)}%`
    } } },
    scales: { y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } } },
  });

  // Combined dual-axis chart
  const combined = exchange_rate.data.filter(d =>
    bi_rate.data.some(b => b.period === d.period)
  );
  if (combined.length > 0) {
    createLineChart('chart-monetary-combined', combined.map(d => d.period), [
      { label: 'USD/IDR', data: combined.map(d => d.usd_idr), color: CHART_COLORS.green, yAxisID: 'y' },
      {
        label: 'BI Rate (%)',
        data: combined.map(d => {
          const b = bi_rate.data.find(b => b.period === d.period);
          return b ? b.rate : null;
        }),
        color: CHART_COLORS.purple, yAxisID: 'y1', stepped: true,
      },
    ], {
      scales: {
        y: {
          type: 'linear', position: 'left',
          ticks: { callback: v => `Rp ${(v/1000).toFixed(0)}K`, color: '#94a3b8', font: { size: 10 } },
        },
        y1: {
          type: 'linear', position: 'right',
          ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } },
          grid: { drawOnChartArea: false },
        },
      },
    });
  }
}

window.ModuleMonetary = { loadMonetary };
