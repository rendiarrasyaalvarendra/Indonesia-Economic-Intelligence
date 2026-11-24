/**
 * Employment & Poverty Modules
 */

async function loadEmployment() {
  const { fmt, createLineChart, createBarChart, CHART_COLORS } = window.Charts;

  let data;
  try {
    data = await window.API.employment();
  } catch (e) {
    document.getElementById('employment-content').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  const latest = data.latest;
  document.getElementById('emp-tpt').textContent = `${fmt(latest.tpt, 2)}%`;
  document.getElementById('emp-tpak').textContent = `${fmt(latest.tpak, 2)}%`;
  document.getElementById('emp-employed').textContent = `${fmt(latest.employed_m, 2)} Juta`;
  document.getElementById('emp-unemployed').textContent = `${fmt(latest.unemployed_m, 2)} Juta`;
  document.getElementById('emp-period').textContent = latest.period;

  const labels = data.data.map(d => d.period);

  // TPT Trend
  createLineChart('chart-tpt', labels, [{
    label: 'TPT (%)', data: data.data.map(d => d.tpt),
    color: CHART_COLORS.red, fill: true, bgColor: 'rgba(239,68,68,0.08)',
    pointRadius: 5,
  }], {
    plugins: { legend: { display: false } },
    scales: { y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } } },
  });

  // Employment numbers
  createLineChart('chart-employment-trend', labels, [
    { label: 'Bekerja (Juta)', data: data.data.map(d => d.employed_m), color: CHART_COLORS.green },
    { label: 'Menganggur (Juta)', data: data.data.map(d => d.unemployed_m), color: CHART_COLORS.red },
  ], {
    scales: { y: { ticks: { callback: v => v + 'J', color: '#94a3b8', font: { size: 10 } } } },
  });

  // TPAK
  createLineChart('chart-tpak', labels, [{
    label: 'TPAK (%)', data: data.data.map(d => d.tpak),
    color: CHART_COLORS.cyan,
  }], {
    plugins: { legend: { display: false } },
    scales: {
      y: {
        min: 60, max: 75,
        ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } }
      }
    },
  });
}

async function loadPoverty() {
  const { fmt, createLineChart, createBarChart, CHART_COLORS } = window.Charts;

  let data;
  try {
    data = await window.API.poverty();
  } catch (e) {
    document.getElementById('poverty-content').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  const latest = data.latest;
  document.getElementById('pov-rate').textContent = `${fmt(latest.rate, 2)}%`;
  document.getElementById('pov-population').textContent = `${fmt(latest.population_m, 2)} Juta`;
  document.getElementById('pov-line').textContent = `Rp ${Number(latest.poverty_line).toLocaleString('id-ID')}`;
  document.getElementById('pov-period').textContent = latest.period;

  const ur = data.urban_rural;
  if (ur) {
    document.getElementById('pov-urban').textContent = `${fmt(ur.urban.rate, 2)}%`;
    document.getElementById('pov-rural').textContent = `${fmt(ur.rural.rate, 2)}%`;
  }

  const labels = data.data.map(d => d.period);

  // Poverty rate trend
  createLineChart('chart-poverty-rate', labels, [{
    label: 'Tingkat Kemiskinan (%)', data: data.data.map(d => d.rate),
    color: CHART_COLORS.orange, fill: true, bgColor: 'rgba(249,115,22,0.08)',
    pointRadius: 5,
  }], {
    plugins: { legend: { display: false } },
    scales: { y: { ticks: { callback: v => v + '%', color: '#94a3b8', font: { size: 10 } } } },
  });

  // Population bar
  createBarChart('chart-poverty-pop', labels, [{
    label: 'Penduduk Miskin (Juta)', data: data.data.map(d => d.population_m),
    color: CHART_COLORS.orange,
  }], {
    plugins: { legend: { display: false } },
    scales: { y: { ticks: { callback: v => v + 'J', color: '#94a3b8', font: { size: 10 } } } },
  });

  // Poverty line trend
  createLineChart('chart-poverty-line', labels, [{
    label: 'Garis Kemiskinan (Rp/kap/bln)', data: data.data.map(d => d.poverty_line),
    color: CHART_COLORS.yellow,
  }], {
    plugins: { legend: { display: false } },
    scales: {
      y: { ticks: { callback: v => `Rp ${(v/1000).toFixed(0)}K`, color: '#94a3b8', font: { size: 10 } } }
    },
  });
}

window.ModuleEmployment = { loadEmployment };
window.ModulePoverty = { loadPoverty };
