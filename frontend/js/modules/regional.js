/**
 * Regional Economic Analysis Module
 */
async function loadRegional() {
  const { fmt, createBarChart, CHART_COLORS } = window.Charts;

  let currentIndicator = 'gdp';
  let selectedProvince = null;

  async function fetchAndRender(indicator) {
    document.getElementById('regional-loading').style.display = 'flex';
    document.getElementById('regional-chart-wrapper').style.display = 'none';

    let data;
    try {
      data = await window.API.regional(indicator);
    } catch (e) {
      document.getElementById('regional-loading').innerHTML =
        `<div class="error-state">⚠️ ${e.message}</div>`;
      return;
    }

    document.getElementById('regional-loading').style.display = 'none';
    document.getElementById('regional-chart-wrapper').style.display = 'block';

    // Stats
    document.getElementById('regional-highest').textContent =
      `${data.highest?.province_name}: ${fmt(data.highest?.[data.field], 2)}`;
    document.getElementById('regional-lowest').textContent =
      `${data.lowest?.province_name}: ${fmt(data.lowest?.[data.field], 2)}`;
    document.getElementById('regional-avg').textContent =
      `${fmt(data.national_avg, 2)}`;
    document.getElementById('regional-label').textContent = data.indicator;

    // Bar chart — top 15
    const top = data.ranked.slice(0, 15);
    createBarChart('chart-regional', top.map(d => d.province_name.replace('Kepulauan', 'Kep.').substring(0, 18)), [{
      label: data.indicator,
      data: top.map(d => d[data.field]),
      backgroundColor: top.map((_, i) => i < 5 ? CHART_COLORS.blue : (i < 10 ? CHART_COLORS.cyan : CHART_COLORS.slate)),
    }], {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { maxRotation: 60, font: { size: 9 }, color: '#94a3b8' } },
        y: { ticks: { color: '#94a3b8', font: { size: 10 } } },
      },
    });

    // Province list
    const listEl = document.getElementById('province-list');
    listEl.innerHTML = data.data.map(d => `
      <div class="province-bar" style="cursor:pointer" onclick="selectProvince('${d.province_code}')">
        <div class="province-name">${d.province_name}</div>
        <div class="province-bar-fill">
          <div class="province-bar-inner" style="width:${Math.min(100, Math.abs(d[data.field] / (data.national_avg * 2)) * 100)}%"></div>
        </div>
        <div class="province-value">${fmt(d[data.field], 1)}</div>
      </div>
    `).join('');
  }

  // Indicator toggle buttons
  document.getElementById('regional-indicator-btns').addEventListener('click', e => {
    const btn = e.target.closest('[data-indicator]');
    if (!btn) return;
    document.querySelectorAll('[data-indicator]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentIndicator = btn.dataset.indicator;
    fetchAndRender(currentIndicator);
  });

  // Province detail
  window.selectProvince = async function (code) {
    let detail;
    try {
      detail = await window.API.provinceDetail(code);
    } catch (e) {
      return;
    }

    const panel = document.getElementById('province-detail-panel');
    panel.innerHTML = `
      <div class="card-header">
        <div>
          <h3 class="card-title">🏛 ${detail.province_name}</h3>
          <p class="card-subtitle">Kode: ${detail.province_code}</p>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="document.getElementById('province-detail-panel').innerHTML=''">✕</button>
      </div>
      <div class="grid-2" style="gap:12px;margin-top:12px">
        ${detail.gdp ? `<div class="stat-row"><span class="stat-label">PDB Growth (2023)</span><span class="stat-value">${fmt(detail.gdp.gdp_growth, 2)}%</span></div>` : ''}
        ${detail.unemployment ? `<div class="stat-row"><span class="stat-label">TPT (2024-02)</span><span class="stat-value">${fmt(detail.unemployment.tpt, 2)}%</span></div>` : ''}
        ${detail.poverty ? `<div class="stat-row"><span class="stat-label">Kemiskinan (2024-03)</span><span class="stat-value">${fmt(detail.poverty.rate, 2)}%</span></div>` : ''}
        ${detail.inflation ? `<div class="stat-row"><span class="stat-label">Inflasi (2024-12)</span><span class="stat-value">${fmt(detail.inflation.yoy, 2)}%</span></div>` : ''}
      </div>
      <p style="font-size:0.72rem;color:var(--color-muted);margin-top:8px">Sumber: BPS</p>`;
  };

  fetchAndRender(currentIndicator);
}

window.ModuleRegional = { loadRegional };
