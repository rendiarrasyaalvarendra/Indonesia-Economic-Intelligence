/**
 * GDP Analysis Module
 */
async function loadGDP() {
  const { fmt, createLineChart, createBarChart, createDoughnutChart, CHART_COLORS } = window.Charts;

  let annual, quarterly, sector, expenditure;
  try {
    [annual, quarterly, sector, expenditure] = await Promise.all([
      window.API.gdp({ frequency: 'annual' }),
      window.API.gdp({ frequency: 'quarterly' }),
      window.API.gdpSector(),
      window.API.gdpExpenditure(),
    ]);
  } catch (e) {
    document.getElementById('gdp-content').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  const latest = annual.data[annual.data.length - 1];
  const prev = annual.data[annual.data.length - 2];
  document.getElementById('gdp-latest-value').textContent = `${fmt(latest.value, 2)}%`;
  document.getElementById('gdp-latest-period').textContent = latest.period;
  document.getElementById('gdp-prev-value').textContent = `${fmt(prev.value, 2)}% (${prev.period})`;

  // Annual trend
  createLineChart('chart-gdp-annual', annual.data.map(d => d.period), [{
    label: 'Pertumbuhan PDB (% YoY)', data: annual.data.map(d => d.value),
    color: CHART_COLORS.blue, fill: true, bgColor: 'rgba(59,130,246,0.08)',
    pointRadius: 5, pointHoverRadius: 7,
  }], {
    plugins: {
      annotation: {
        annotations: {
          zeroLine: { type: 'line', yMin: 0, yMax: 0, borderColor: 'rgba(239,68,68,0.5)', borderWidth: 1, borderDash: [4, 4] }
        }
      }
    },
    scales: { y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } } },
  });

  // Quarterly trend
  createBarChart('chart-gdp-quarterly', quarterly.data.slice(-16).map(d => d.period), [{
    label: 'PDB Kuartalan (% YoY)',
    data: quarterly.data.slice(-16).map(d => d.value),
    backgroundColor: quarterly.data.slice(-16).map(d => d.value >= 0 ? CHART_COLORS.blue : CHART_COLORS.red),
  }], {
    plugins: { legend: { display: false } },
    scales: { y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } } },
  });

  // Sector breakdown
  const sData = sector.data.slice(0, 8);
  createDoughnutChart('chart-gdp-sector',
    sData.map(d => d.sector),
    sData.map(d => d.share),
    Object.values(CHART_COLORS).slice(0, sData.length),
    {
      plugins: {
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${fmt(ctx.parsed, 1)}%` } }
      }
    }
  );

  // Sector growth bar
  createBarChart('chart-sector-growth',
    sData.map(d => d.sector.substring(0, 20)),
    [{
      label: 'Pertumbuhan (%)',
      data: sData.map(d => d.growth),
      color: CHART_COLORS.cyan,
    }],
    {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { maxRotation: 45, font: { size: 9 }, color: '#94a3b8' } },
        y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } },
      },
    }
  );

  // Expenditure table
  const expTable = document.getElementById('gdp-expenditure-table');
  expTable.innerHTML = `<thead><tr><th>Komponen</th><th>Share (%)</th><th>Pertumbuhan (%)</th></tr></thead>
  <tbody>
    ${expenditure.data.map(d => `
      <tr>
        <td>${d.component}</td>
        <td>${fmt(Math.abs(d.share), 1)}%</td>
        <td>${d.growth !== null ? fmt(d.growth, 2) + '%' : 'N/A'}</td>
      </tr>`).join('')}
  </tbody>`;
}

window.ModuleGDP = { loadGDP };
