/**
 * Anomaly Detection Module
 */
async function loadAnomaly() {
  const { fmt, createLineChart, CHART_COLORS, hexToRgba } = window.Charts;

  let availableList;
  try {
    availableList = await window.API.anomalyList();
  } catch (e) {
    document.getElementById('anomaly-content').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  const sel = document.getElementById('anomaly-indicator-sel');
  sel.innerHTML = Object.entries(availableList.indicator_labels)
    .map(([k, v]) => `<option value="${k}">${v}</option>`).join('');

  async function runAnomaly() {
    const indicator = document.getElementById('anomaly-indicator-sel').value;
    const zThreshold = parseFloat(document.getElementById('anomaly-z-threshold').value) || 2.5;

    document.getElementById('anomaly-result').innerHTML =
      '<div class="loading-spinner"><div class="spinner"></div> Mendeteksi anomali...</div>';

    let data;
    try {
      data = await window.API.anomaly(indicator, { z_threshold: zThreshold });
    } catch (e) {
      document.getElementById('anomaly-result').innerHTML =
        `<div class="error-state">⚠️ ${e.message}</div>`;
      return;
    }

    if (data.note) {
      document.getElementById('anomaly-result').innerHTML =
        `<div class="empty-state"><p>${data.note}</p></div>`;
      return;
    }

    const anomalySet = new Set(data.anomalies.map(a => a.period));
    const labels = data.all_values.map(d => d.period);
    const values = data.all_values.map(d => d.value);
    const pointColors = data.all_values.map(d =>
      anomalySet.has(d.period) ? CHART_COLORS.red : CHART_COLORS.blue
    );
    const pointRadii = data.all_values.map(d => anomalySet.has(d.period) ? 8 : 3);

    // Result container
    document.getElementById('anomaly-result').innerHTML = `
      <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px">
        <div class="card" style="flex:1;min-width:140px">
          <div class="kpi-label">Total Observasi</div>
          <div class="kpi-value" style="font-size:1.5rem;color:var(--color-text)">${data.total_observations}</div>
        </div>
        <div class="card" style="flex:1;min-width:140px">
          <div class="kpi-label">Anomali Terdeteksi</div>
          <div class="kpi-value" style="font-size:1.5rem;color:var(--color-danger)">${data.total_anomalies}</div>
        </div>
        <div class="card" style="flex:1;min-width:140px">
          <div class="kpi-label">Rata-rata</div>
          <div class="kpi-value" style="font-size:1.5rem;color:var(--color-text)">${fmt(data.mean, 2)}</div>
        </div>
        <div class="card" style="flex:1;min-width:140px">
          <div class="kpi-label">Standar Deviasi</div>
          <div class="kpi-value" style="font-size:1.5rem;color:var(--color-text)">${fmt(data.std, 2)}</div>
        </div>
      </div>
      <div class="chart-wrapper tall"><canvas id="chart-anomaly"></canvas></div>
      ${data.total_anomalies > 0 ? `
      <h4 style="margin:16px 0 8px">Detail Anomali yang Terdeteksi</h4>
      <div class="table-wrapper">
        <table class="data-table">
          <thead><tr><th>Periode</th><th>Nilai</th><th>Z-Score</th><th>IQR Flag</th><th>MA Dev</th><th>Metode</th></tr></thead>
          <tbody>
            ${data.anomalies.map(a => `
              <tr class="anomaly-row">
                <td><span class="anomaly-badge"></span>${a.period}</td>
                <td>${fmt(a.value, 2)} ${data.unit}</td>
                <td>${fmt(a.z_score, 2)}</td>
                <td>${a.iqr_flag ? '⚠️ Ya' : '—'}</td>
                <td>${fmt(a.ma_deviation, 2)}</td>
                <td><small style="color:var(--color-muted)">${a.method}</small></td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <p style="font-size:0.75rem;color:var(--color-muted);margin-top:8px">
        ⚠️ Anomali statistik tidak otomatis berarti krisis ekonomi. Interpretasikan dalam konteks yang lebih luas.
      </p>` : `<div class="empty-state" style="margin-top:16px"><div class="empty-icon">✅</div><p>Tidak ada anomali terdeteksi dengan threshold saat ini.</p></div>`}
    `;

    // Render chart
    const ctx = document.getElementById('chart-anomaly');
    if (ctx) {
      window.Charts.destroyChart('chart-anomaly');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: `${data.indicator} (${data.unit})`,
            data: values,
            borderColor: CHART_COLORS.blue,
            backgroundColor: hexToRgba(CHART_COLORS.blue, 0.06),
            fill: true,
            tension: 0.3,
            borderWidth: 2,
            pointBackgroundColor: pointColors,
            pointBorderColor: pointColors,
            pointRadius: pointRadii,
          }],
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#1e293b', titleColor: '#f1f5f9', bodyColor: '#94a3b8',
              borderColor: '#334155', borderWidth: 1,
              callbacks: {
                label: ctx => {
                  const p = ctx.label;
                  const anomaly = data.anomalies.find(a => a.period === p);
                  return anomaly ? ` ${fmt(ctx.parsed.y, 2)} ⚠️ ANOMALI` : ` ${fmt(ctx.parsed.y, 2)}`;
                }
              }
            },
          },
          scales: {
            x: { ticks: { color: '#94a3b8', font: { size: 9 }, maxRotation: 45 }, grid: { color: 'rgba(51,65,85,0.5)' } },
            y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(51,65,85,0.5)' } },
          },
        },
      });
    }
  }

  document.getElementById('anomaly-run-btn').addEventListener('click', runAnomaly);
  runAnomaly();
}

window.ModuleAnomaly = { loadAnomaly };
