/**
 * Indonesia Economic Intelligence — Main Application
 * Routing, navigation, global state, initialization.
 */

// ============================================================
// App State
// ============================================================
const AppState = window.AppState = {
  currentPage: 'overview',
  loadedPages: new Set(),
};

// ============================================================
// Navigation
// ============================================================
const PAGES = {
  overview:     { title: 'Ikhtisar Ekonomi', load: () => window.ModuleOverview.loadOverview() },
  inflation:    { title: 'Analisis Inflasi', load: () => window.ModuleInflation.loadInflation() },
  gdp:          { title: 'Analisis PDB', load: () => window.ModuleGDP.loadGDP() },
  monetary:     { title: 'Analisis Moneter', load: () => window.ModuleMonetary.loadMonetary() },
  employment:   { title: 'Analisis Ketenagakerjaan', load: () => window.ModuleEmployment.loadEmployment() },
  poverty:      { title: 'Analisis Kemiskinan', load: () => window.ModulePoverty.loadPoverty() },
  regional:     { title: 'Analisis Regional', load: () => window.ModuleRegional.loadRegional() },
  trade:        { title: 'Analisis Perdagangan', load: () => window.ModuleTrade.loadTrade() },
  forecasting:  { title: 'Peramalan Ekonomi', load: () => window.ModuleForecasting.loadForecasting() },
  anomaly:      { title: 'Deteksi Anomali', load: () => window.ModuleAnomaly.loadAnomaly() },
  insights:     { title: 'Insight Ekonomi', load: () => window.ModuleInsights.loadInsights() },
  ai_analyst:   { title: 'AI Economic Analyst', load: () => window.ModuleAIAnalyst.loadAIAnalyst() },
  reports:      { title: 'Laporan Ekonomi AI', load: () => window.ModuleReports.loadReports() },
  data_explorer:{ title: 'Penjelajah Data', load: () => window.ModuleDataExplorer.loadDataExplorer() },
};


function navigateTo(pageId) {
  if (!PAGES[pageId]) return;

  // Update active navigation
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === pageId);
  });

  // Show target page
  document.querySelectorAll('.page').forEach(el => {
    el.classList.remove('active');
  });

  const target = document.getElementById(`page-${pageId}`);
  if (target) target.classList.add('active');

  // Replay chart animation when page is opened
requestAnimationFrame(() => {
  if (window.Charts?.animateChartsInPage) {
    window.Charts.animateChartsInPage(target);
  }
});

  // Update page title
  const titleEl = document.getElementById('topbar-page-title');
  if (titleEl) titleEl.textContent = PAGES[pageId].title;

  // Load page data only when needed
  if (!AppState.loadedPages.has(pageId)) {
    AppState.loadedPages.add(pageId);

    Promise.resolve()
      .then(() => PAGES[pageId].load())
      .catch(err => {
        AppState.loadedPages.delete(pageId);
        console.error(`Failed to load page ${pageId}:`, err);
      });
  }

  AppState.currentPage = pageId;

  // Close mobile sidebar
  if (window.innerWidth < 768) {
    document.getElementById('sidebar')?.classList.remove('open');
  }
}

// Allow forced reload of a page
window.reloadPage = function (pageId) {
  if (!PAGES[pageId]) return;

  AppState.loadedPages.delete(pageId);
  navigateTo(pageId);
};

function initSidebarToggle() {
  document.getElementById('menu-toggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', e => {
    if (window.innerWidth < 768) {
      const sidebar = document.getElementById('sidebar');
      const toggle = document.getElementById('menu-toggle');
      if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    }
  });
}

// ============================================================
// Status bar / health check
// ============================================================
async function checkHealth() {
  const statusEl = document.getElementById('api-status');
  try {
    const h = await window.API.health();
    if (h.status === 'ok') {
      statusEl.innerHTML = '<span class="badge badge-green">● API Online</span>';
    }
  } catch (_) {
    statusEl.innerHTML = '<span class="badge badge-red">● API Offline</span>';
  }
}

// ============================================================
// Init
// ============================================================
function init() {
  // Wire up nav clicks
  document.querySelectorAll('.nav-item[data-page]').forEach(el => {
    el.addEventListener('click', () => navigateTo(el.dataset.page));
  });

  initSidebarToggle();
  checkHealth();

  // Load default page
  navigateTo('overview');

  // Keyboard shortcut: Ctrl+K → focus search (if on data explorer)
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      navigateTo('data_explorer');
      setTimeout(() => document.getElementById('explorer-search')?.focus(), 100);
    }
  });

  // Set current year in footer
  const yearEl = document.getElementById('footer-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
}

document.addEventListener('DOMContentLoaded', init);
