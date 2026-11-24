/**
 * Indonesia Economic Intelligence — Chart.js Helpers
 * All chart creation goes through this module.
 */

const CHART_COLORS = {
  blue: '#3b82f6',
  green: '#10b981',
  yellow: '#f59e0b',
  red: '#ef4444',
  purple: '#8b5cf6',
  cyan: '#06b6d4',
  orange: '#f97316',
  pink: '#ec4899',
  slate: '#94a3b8',
};

const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 600, easing: 'easeOutQuart' },
  plugins: {
    legend: {
      position: 'top',
      labels: {
        color: '#94a3b8',
        font: { size: 11 },
        boxWidth: 12,
        padding: 12,
      },
    },
    tooltip: {
      backgroundColor: '#1e293b',
      titleColor: '#f1f5f9',
      bodyColor: '#94a3b8',
      borderColor: '#334155',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 8,
    },
  },
  scales: {
    x: {
      ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 45 },
      grid: { color: 'rgba(51,65,85,0.5)', drawBorder: false },
    },
    y: {
      ticks: { color: '#94a3b8', font: { size: 10 } },
      grid: { color: 'rgba(51,65,85,0.5)', drawBorder: false },
    },
  },
};

const _charts = new Map();

function destroyChart(id) {
  if (_charts.has(id)) {
    _charts.get(id).destroy();
    _charts.delete(id);
  }
}

function createLineChart(canvasId, labels, datasets, opts = {}) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const chart = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: datasets.map((ds, i) => ({
        fill: ds.fill ?? false,
        tension: 0.4,
        pointRadius: ds.pointRadius ?? 3,
        borderWidth: ds.borderWidth ?? 2,
        borderColor: ds.color || Object.values(CHART_COLORS)[i],
        backgroundColor: ds.bgColor || hexToRgba(Object.values(CHART_COLORS)[i], 0.08),
        ...ds,
      })),
    },
    options: deepMerge(CHART_DEFAULTS, opts),
  });
  _charts.set(canvasId, chart);
  return chart;
}

// Replay chart animations when a page is opened again
function animateChartsInPage(pageElement) {
  if (!pageElement) return;

  _charts.forEach(chart => {
    if (pageElement.contains(chart.canvas)) {
      chart.stop();
      chart.reset();
      chart.update();
    }
  });
}


function createBarChart(canvasId, labels, datasets, opts = {}) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const chart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: datasets.map((ds, i) => ({
        borderRadius: 4,
        borderWidth: 0,
        backgroundColor: ds.color || Object.values(CHART_COLORS)[i],
        ...ds,
      })),
    },
    options: deepMerge(CHART_DEFAULTS, opts),
  });
  _charts.set(canvasId, chart);
  return chart;
}

function createDoughnutChart(canvasId, labels, data, colors, opts = {}) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const chart = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors || Object.values(CHART_COLORS).slice(0, data.length),
        borderWidth: 2,
        borderColor: '#1e293b',
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600 },
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#94a3b8', font: { size: 10 }, boxWidth: 10, padding: 8 },
        },
        tooltip: CHART_DEFAULTS.plugins.tooltip,
      },
      ...opts,
    },
  });
  _charts.set(canvasId, chart);
  return chart;
}

function createHorizontalBarChart(canvasId, labels, data, color, opts = {}) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const chart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: color || CHART_COLORS.blue,
        borderRadius: 4,
        borderWidth: 0,
      }],
    },
    options: deepMerge(CHART_DEFAULTS, {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      ...opts,
    }),
  });
  _charts.set(canvasId, chart);
  return chart;
}

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function deepMerge(target, source) {
  const result = { ...target };
  for (const key of Object.keys(source || {})) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      result[key] = deepMerge(target[key] || {}, source[key]);
    } else {
      result[key] = source[key];
    }
  }
  return result;
}

// Format numbers for display
function fmt(val, decimals = 2, suffix = '') {
  if (val === null || val === undefined) return 'N/A';
  return Number(val).toLocaleString('id-ID', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }) + (suffix ? ` ${suffix}` : '');
}

function fmtCurrency(val, currency = 'Rp') {
  if (val === null || val === undefined) return 'N/A';
  return `${currency} ${Number(val).toLocaleString('id-ID')}`;
}

window.Charts = {
  createLineChart, createBarChart, createDoughnutChart, createHorizontalBarChart,
  destroyChart, animateChartsInPage,
  fmt, fmtCurrency, CHART_COLORS, hexToRgba,
};