/**
 * Economic Forecasting Module
 */
async function loadForecasting() {
  const { fmt, createLineChart, CHART_COLORS, hexToRgba } = window.Charts;

  let availableIndicators;
  try {
    availableIndicators = await window.API.forecastingList();
  } catch (e) {
    document.getElementById('forecasting-content').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  // Populate selector
  const sel = document.getElementById('forecast-indicator-sel');
  sel.innerHTML = Object.entries(availableIndicators.indicator_labels)
    .map(([k, v]) => `<option value="${k}">${v}</option>`).join('');

  async function runForecast() {
    const indicator = document.getElementById('forecast-indicator-sel').value;
    const horizon = parseInt(document.getElementById('forecast-horizon-sel').value);

    document.getElementById('forecast-result').innerHTML =
      '<div class="loading-spinner"><div class="spinner"></div> Menghitung forecast...</div>';

    let data;
    try {
      data = await window.API.forecasting(indicator, horizon);
    } catch (e) {
      document.getElementById('forecast-result').innerHTML =
        `<div class="error-state">⚠️ ${e.message}</div>`;
      return;
    }

    const best = data.best_method;
    const methods = data.methods;
    const bestResult = methods[best];

    if (!bestResult || bestResult.error) {
      document.getElementById('forecast-result').innerHTML =
        `<div class="error-state">⚠️ ${bestResult?.error || 'Forecast tidak tersedia'}</div>`;
      return;
    }

    // Build chart data: history + forecast
    const histLabels = data.history_periods;
    const histValues = data.history_values;

    // Generate future period labels
    const lastPeriod = histLabels[histLabels.length - 1];
    const futurePeriods = generatePeriodLabels(lastPeriod, horizon);

    const allLabels = [...histLabels, ...futurePeriods];
    const allHistValues = [...histValues, ...Array(horizon).fill(null)];
    const allForecastValues = [...Array(histValues.length).fill(null), ...bestResult.forecast];
    const lowerBound = [...Array(histValues.length).fill(null), ...(bestResult.lower || [])];
    const upperBound = [...Array(histValues.length).fill(null), ...(bestResult.upper || [])];

    createLineChart('chart-forecast', allLabels, [
      {
        label: 'Data Historis', data: allHistValues,
        color: CHART_COLORS.blue, pointRadius: 2,
      },
      {
        label: `Forecast (${bestResult.method || best})`, data: allForecastValues,
        color: CHART_COLORS.yellow, borderDash: [6, 3], pointRadius: 4,
      },
      {
        label: 'Batas Bawah', data: lowerBound,
        color: CHART_COLORS.slate, borderDash: [3, 3], borderWidth: 1,
        pointRadius: 0, fill: false,
      },
      {
        label: 'Batas Atas', data: upperBound,
        color: CHART_COLORS.slate, borderDash: [3, 3], borderWidth: 1,
        pointRadius: 0, fill: '-1', bgColor: 'rgba(148,163,184,0.08)',
      },
    ], {
      scales: { x: { ticks: { maxRotation: 60, font: { size: 9 } } } },
    });

    // Method comparison table
    let tableHtml = `<table class="data-table" style="margin-top:12px">
      <thead><tr><th>Metode</th><th>MAE</th><th>RMSE</th><th>Status</th></tr></thead><tbody>`;
    for (const [mkey, mdata] of Object.entries(methods)) {
      const isError = !!mdata.error;
      const isBest = mkey === best;
      tableHtml += `<tr class="${isBest ? 'anomaly-row' : ''}">
        <td>${mdata.method || mkey}</td>
        <td>${isError ? '—' : fmt(mdata.mae, 4)}</td>
        <td>${isError ? '—' : fmt(mdata.rmse, 4)}</td>
        <td>${isError ? `<span class="badge badge-red">Error</span>` : (isBest ? '<span class="badge badge-green">Terbaik</span>' : '<span class="badge badge-gray">OK</span>')}</td>
      </tr>`;
    }
    tableHtml += '</tbody></table>';

    document.getElementById('forecast-result').innerHTML = `
      <div style="margin-bottom:12px">
        <strong>Indikator:</strong> ${data.indicator} &nbsp;|&nbsp;
        <strong>Metode Terbaik:</strong> ${bestResult.method || best} &nbsp;|&nbsp;
        <strong>Horizon:</strong> ${horizon} periode
      </div>
      <div class="chart-wrapper tall"><canvas id="chart-forecast"></canvas></div>
      <div class="forecast-legend" style="margin-top:8px">
        <div class="legend-item"><div class="legend-dot" style="background:${CHART_COLORS.blue}"></div> Data Historis</div>
        <div class="legend-item"><div class="legend-dot" style="background:${CHART_COLORS.yellow}"></div> Forecast</div>
        <div class="legend-item"><div class="legend-dot" style="background:${CHART_COLORS.slate}"></div> Interval Kepercayaan 95%</div>
      </div>
      <p style="font-size:0.75rem;color:var(--color-muted);margin-top:8px">
        ⚠️ Forecast adalah perkiraan statistik, bukan prediksi resmi. Perlu diinterpretasikan dengan hati-hati.
      </p>
      <h4 style="margin:16px 0 8px">Perbandingan Metode</h4>
      ${tableHtml}
    `;

    // Re-create chart after innerHTML was set
    setTimeout(() => {
      createLineChart('chart-forecast', allLabels, [
        { label: 'Data Historis', data: allHistValues, color: CHART_COLORS.blue, pointRadius: 2 },
        { label: `Forecast (${bestResult.method || best})`, data: allForecastValues, color: CHART_COLORS.yellow, borderDash: [6, 3], pointRadius: 4 },
        { label: 'Batas Bawah', data: lowerBound, color: CHART_COLORS.slate, borderDash: [3, 3], borderWidth: 1, pointRadius: 0 },
        { label: 'Batas Atas', data: upperBound, color: CHART_COLORS.slate, borderDash: [3, 3], borderWidth: 1, pointRadius: 0, fill: '-1', bgColor: 'rgba(148,163,184,0.08)' },
      ], { scales: { x: { ticks: { maxRotation: 60, font: { size: 9 } } } } });
    }, 50);
  }

  document.getElementById('forecast-run-btn').addEventListener('click', runForecast);
  runForecast(); // Initial run
}

function generatePeriodLabels(lastPeriod, n) {
  const labels = [];
  // Detect format: YYYY, YYYY-QN, YYYY-MM
  if (/^\d{4}$/.test(lastPeriod)) {
    let year = parseInt(lastPeriod);
    for (let i = 1; i <= n; i++) labels.push(String(year + i));
  } else if (/^\d{4}-Q\d$/.test(lastPeriod)) {
    let [y, q] = lastPeriod.split('-Q').map(Number);
    for (let i = 0; i < n; i++) {
      q++;
      if (q > 4) { q = 1; y++; }
      labels.push(`${y}-Q${q}`);
    }
  } else if (/^\d{4}-\d{2}$/.test(lastPeriod)) {
    let [y, m] = lastPeriod.split('-').map(Number);
    for (let i = 0; i < n; i++) {
      m++;
      if (m > 12) { m = 1; y++; }
      labels.push(`${y}-${String(m).padStart(2, '0')}`);
    }
  } else {
    for (let i = 1; i <= n; i++) labels.push(`t+${i}`);
  }
  return labels;
}

window.ModuleForecasting = { loadForecasting };
