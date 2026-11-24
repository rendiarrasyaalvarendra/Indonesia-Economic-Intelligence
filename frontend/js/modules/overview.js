/**
 * Overview & KPI Cards Module
 */

async function loadOverview() {
  const { fmt, fmtCurrency, createLineChart, CHART_COLORS } = window.Charts;

  // Loading state
  document.getElementById('kpi-grid').innerHTML = Array(4).fill(
    `<div class="kpi-card"><div class="loading-spinner"><div class="spinner"></div></div></div>`
  ).join('');

  let data;
  try {
    data = await window.API.overview();
  } catch (e) {
    document.getElementById('kpi-grid').innerHTML =
      `<div class="error-state" style="grid-column:1/-1">⚠️ ${e.message}</div>`;
    return;
  }

  const { kpis, gdp_trend, inflation_trend, exchange_rate_trend, bi_rate_trend } = data;

  // ---- KPI Cards ----
  const kpiConfig = [
    {
      key: 'gdp_growth', cls: 'gdp', icon: '📈', valCls: 'gdp',
      format: v => `${fmt(v, 2)}%`,
      changeFmt: c => `${c >= 0 ? '+' : ''}${fmt(c, 2)} pp`,
    },
    {
      key: 'inflation', cls: 'inflation', icon: '🏷️', valCls: 'inflation',
      format: v => `${fmt(v, 2)}%`,
      changeFmt: c => `${c >= 0 ? '+' : ''}${fmt(c, 2)} pp`,
    },
    {
      key: 'exchange_rate', cls: 'exchange', icon: '💱', valCls: 'exchange',
      format: v => `Rp ${Number(v).toLocaleString('id-ID')}`,
      changeFmt: c => `${c >= 0 ? '+' : ''}${Number(c).toLocaleString('id-ID')}`,
    },
    {
      key: 'bi_rate', cls: 'birate', icon: '🏦', valCls: 'birate',
      format: v => `${fmt(v, 2)}%`,
      changeFmt: c => `${c >= 0 ? '+' : ''}${fmt(c, 2)} pp`,
    },
  ];

  const kpiHtml = kpiConfig.map(cfg => {
    const kpi = kpis[cfg.key];
   const isPositive = cfg.key === 'gdp_growth';

const isFavorable = isPositive
  ? kpi.trend === 'up'
  : kpi.trend === 'down';

const trendClass = kpi.trend === 'stable'
  ? 'stable'
  : isFavorable ? 'positive' : 'negative';

const trendArrow = kpi.trend === 'up'
  ? '↑'
  : kpi.trend === 'down' ? '↓' : '→';
    return `
      <div class="kpi-card ${cfg.cls}">
        <span class="kpi-source-badge">${kpi.source}</span>
        <div class="kpi-label">${kpi.indicator}</div>
        <div class="kpi-value ${cfg.valCls}">${cfg.format(kpi.value)}</div>
        <div class="kpi-change ${trendClass}">
          <span class="arrow">${trendArrow}</span>
          <span>${cfg.changeFmt(kpi.change)} dari ${kpi.previous_period}</span>
        </div>
        <div class="kpi-period">📅 ${kpi.period}</div>
      </div>`;
  }).join('');

  document.getElementById('kpi-grid').innerHTML = kpiHtml;

  // ---- Trend Charts ----
  const gdpLabels = gdp_trend.map(d => d.period);
  const gdpValues = gdp_trend.map(d => d.value);
  createLineChart('chart-gdp-trend', gdpLabels, [{
    label: 'PDB (% YoY)', data: gdpValues, color: CHART_COLORS.blue,
    fill: true, bgColor: 'rgba(59,130,246,0.08)',
    pointRadius: 4,
  }], {
    plugins: { legend: { display: false }, tooltip: { callbacks: {
      label: ctx => ` ${fmt(ctx.parsed.y, 2)}% YoY`
    } } },
    scales: {
      y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } },
    },
  });

  const infLabels = inflation_trend.map(d => d.period);
  createLineChart('chart-inflation-trend', infLabels, [{
    label: 'Inflasi YoY (%)', data: inflation_trend.map(d => d.yoy),
    color: CHART_COLORS.yellow, fill: true, bgColor: 'rgba(245,158,11,0.08)',
  }], {
    plugins: { legend: { display: false } },
    scales: { y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } } },
  });

  createLineChart('chart-er-trend', exchange_rate_trend.map(d => d.period), [{
    label: 'USD/IDR', data: exchange_rate_trend.map(d => d.usd_idr),
    color: CHART_COLORS.green,
  }], {
    plugins: { legend: { display: false } },
    scales: { y: { ticks: { callback: v => `Rp ${(v/1000).toFixed(0)}K`, color: '#94a3b8', font: { size: 10 } } } },
  });

  createLineChart('chart-bi-trend', bi_rate_trend.map(d => d.period), [{
    label: 'BI Rate (%)', data: bi_rate_trend.map(d => d.rate),
    color: CHART_COLORS.purple, stepped: true,
  }], {
    plugins: { legend: { display: false } },
    scales: { y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } } },
  });

  // ---- Data sources ----
  if (data.data_sources) {
    document.getElementById('overview-sources').innerHTML = data.data_sources.map(s =>
      `<span class="badge badge-blue">${s.name}</span>`
    ).join(' ');
  }
}

window.ModuleOverview = { loadOverview };
