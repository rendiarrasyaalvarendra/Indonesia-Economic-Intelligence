/**
 * Indonesia Economic Intelligence — API Client
 * All backend communication goes through this module.
 */

const API_BASE = '/api';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const err = await res.json();
        detail = err.detail || detail;
      } catch (_) {}
      throw new ApiError(detail, res.status);
    }
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) return res.json();
    return res.text();
  } catch (e) {
    if (e instanceof ApiError) throw e;
    throw new ApiError(`Network error: ${e.message}`, 0);
  }
}

function get(path, params = {}) {
  const q = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v !== null && v !== undefined))
  ).toString();
  return request(q ? `${path}?${q}` : path);
}

function post(path, body) {
  return request(path, { method: 'POST', body: JSON.stringify(body) });
}

// ---- Specific API calls ----

const API = {
  health: () => fetch('/health').then(r => r.json()),
  overview: () => get('/overview'),
  kpis: () => get('/overview/kpis'),

  gdp: (params = {}) => get('/gdp', params),
  gdpSector: () => get('/gdp/sector'),
  gdpExpenditure: () => get('/gdp/expenditure'),

  inflation: (params = {}) => get('/inflation', params),
  inflationProvincial: () => get('/inflation/provincial'),

  monetary: (params = {}) => get('/monetary', params),

  employment: () => get('/employment'),

  poverty: () => get('/poverty'),

  regional: (indicator = 'gdp') => get('/regional', { indicator }),
  provinceDetail: (code) => get(`/regional/province/${code}`),

  trade: (params = {}) => get('/trade', params),

  forecasting: (indicator, horizon = 6) => get(`/forecasting/${indicator}`, { horizon }),
  forecastingList: () => get('/forecasting'),

  anomaly: (indicator, params = {}) => get(`/anomaly/${indicator}`, params),
  anomalyList: () => get('/anomaly'),

  insights: (params = {}) => get('/insights', params),

  chat: (message, history = []) => post('/ai/chat', { message, history }),

  reportPreview: () => request('/reports/preview'),
  generateReport: (body) => post('/reports/generate', body),

  dataExplore: (params = {}) => get('/data/explore', params),
  dataExportUrl: (params = {}) => {
    const q = new URLSearchParams(Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== null && v !== undefined)
    )).toString();
    return `${API_BASE}/data/explore?${q}`;
  },
};

window.API = API;
