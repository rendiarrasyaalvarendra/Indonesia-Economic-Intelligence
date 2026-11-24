/**
 * Economic Insights Module
 */
async function loadInsights() {
  let data;
  try {
    data = await window.API.insights({ limit: 20 });
  } catch (e) {
    document.getElementById('insights-content').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  renderInsights(data.insights, 'all');

  // Category filter
  document.getElementById('insights-filter-btns').addEventListener('click', e => {
    const btn = e.target.closest('[data-category]');
    if (!btn) return;
    document.querySelectorAll('#insights-filter-btns [data-category]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const cat = btn.dataset.category;
    renderInsights(cat === 'all' ? data.insights : data.insights.filter(i => i.category === cat), cat);
  });
}

function renderInsights(insights, category) {
  const container = document.getElementById('insights-list');
  if (!insights.length) {
    container.innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div><p>Tidak ada insight untuk kategori ini.</p></div>';
    return;
  }

  container.innerHTML = insights.map(ins => {
    const catLabel = { trend: 'Tren', extreme: 'Ekstrem', anomaly: 'Anomali', regional: 'Regional', comparative: 'Komparatif' }[ins.category] || ins.category;
    const catClass = `badge-${ins.category === 'trend' ? 'blue' : ins.category === 'extreme' ? 'yellow' : ins.category === 'anomaly' ? 'red' : ins.category === 'regional' ? 'purple' : 'gray'}`;

    return `
    <div class="insight-card ${ins.category}" style="margin-bottom:12px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
        <div class="insight-title">${ins.title}</div>
        <span class="badge ${catClass}">${catLabel}</span>
      </div>
      <div class="insight-desc">${ins.description}</div>
      <div class="insight-meta">
        <span>📊 ${ins.indicator}</span>
        <span>📅 ${ins.period}</span>
        <span>🏛 ${ins.source}</span>
        ${ins.value !== null && ins.value !== undefined ? `<span>📈 ${Number(ins.value).toLocaleString('id-ID', { maximumFractionDigits: 2 })}</span>` : ''}
      </div>
    </div>`;
  }).join('');
}

window.ModuleInsights = { loadInsights };
