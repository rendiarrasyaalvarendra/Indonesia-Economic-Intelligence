/**
 * Data Explorer Module
 */
let _explorerState = {
  page: 1, pageSize: 50, sortBy: 'period', sortDir: 'desc',
  indicator: '', source: '', frequency: '', region: '', search: '',
  yearStart: '', yearEnd: '',
};
let _explorerFilters = null;

async function loadDataExplorer() {
  // Load filter options
  try {
    const initial = await window.API.dataExplore({ page: 1, page_size: 1 });
    _explorerFilters = initial.filters;
    populateFilters(_explorerFilters);
  } catch (e) {}

  // Event listeners
  document.getElementById('explorer-search').addEventListener('input', debounce(() => {
    _explorerState.search = document.getElementById('explorer-search').value;
    _explorerState.page = 1;
    fetchExplorer();
  }, 400));

  document.getElementById('explorer-indicator-sel').addEventListener('change', e => {
    _explorerState.indicator = e.target.value;
    _explorerState.page = 1;
    fetchExplorer();
  });

  document.getElementById('explorer-source-sel').addEventListener('change', e => {
    _explorerState.source = e.target.value;
    _explorerState.page = 1;
    fetchExplorer();
  });

  document.getElementById('explorer-freq-sel').addEventListener('change', e => {
    _explorerState.frequency = e.target.value;
    _explorerState.page = 1;
    fetchExplorer();
  });

  document.getElementById('explorer-year-start').addEventListener('change', e => {
    _explorerState.yearStart = e.target.value;
    _explorerState.page = 1;
    fetchExplorer();
  });

  document.getElementById('explorer-year-end').addEventListener('change', e => {
    _explorerState.yearEnd = e.target.value;
    _explorerState.page = 1;
    fetchExplorer();
  });

  document.getElementById('explorer-reset-btn').addEventListener('click', () => {
    _explorerState = { page: 1, pageSize: 50, sortBy: 'period', sortDir: 'desc', indicator: '', source: '', frequency: '', region: '', search: '', yearStart: '', yearEnd: '' };
    document.getElementById('explorer-search').value = '';
    document.getElementById('explorer-indicator-sel').value = '';
    document.getElementById('explorer-source-sel').value = '';
    document.getElementById('explorer-freq-sel').value = '';
    document.getElementById('explorer-year-start').value = '';
    document.getElementById('explorer-year-end').value = '';
    fetchExplorer();
  });

  document.getElementById('explorer-export-csv').addEventListener('click', () => {
    const url = window.API.dataExportUrl({ ..._explorerState, export_format: 'csv' });
    window.open(url, '_blank');
  });

  document.getElementById('explorer-export-json').addEventListener('click', () => {
    const url = window.API.dataExportUrl({ ..._explorerState, export_format: 'json' });
    window.open(url, '_blank');
  });

  fetchExplorer();
}

function populateFilters(filters) {
  const indSel = document.getElementById('explorer-indicator-sel');
  indSel.innerHTML = '<option value="">Semua Indikator</option>' +
    filters.available_indicators.map(i => `<option value="${i}">${i}</option>`).join('');
}

async function fetchExplorer() {
  document.getElementById('explorer-table-wrapper').innerHTML =
    '<div class="loading-spinner"><div class="spinner"></div> Memuat data...</div>';

  const params = {
    indicator: _explorerState.indicator || undefined,
    source: _explorerState.source || undefined,
    frequency: _explorerState.frequency || undefined,
    search: _explorerState.search || undefined,
    year_start: _explorerState.yearStart || undefined,
    year_end: _explorerState.yearEnd || undefined,
    page: _explorerState.page,
    page_size: _explorerState.pageSize,
    sort_by: _explorerState.sortBy,
    sort_dir: _explorerState.sortDir,
  };

  let data;
  try {
    data = await window.API.dataExplore(params);
  } catch (e) {
    document.getElementById('explorer-table-wrapper').innerHTML =
      `<div class="error-state">⚠️ ${e.message}</div>`;
    return;
  }

  renderExplorerTable(data);
}

function renderExplorerTable(data) {
  if (!data.data.length) {
    document.getElementById('explorer-table-wrapper').innerHTML =
      '<div class="empty-state"><div class="empty-icon">📭</div><p>Tidak ada data yang sesuai filter.</p></div>';
    document.getElementById('explorer-pagination').innerHTML = '';
    document.getElementById('explorer-count').textContent = '0 data';
    return;
  }

  document.getElementById('explorer-count').textContent = `${data.total.toLocaleString('id-ID')} data`;

  const headers = ['indicator', 'source', 'unit', 'frequency', 'region', 'period', 'value'];
  const headerLabels = { indicator: 'Indikator', source: 'Sumber', unit: 'Satuan', frequency: 'Frekuensi', region: 'Wilayah', period: 'Periode', value: 'Nilai' };

  const html = `
    <table class="data-table">
      <thead>
        <tr>
          ${headers.map(h => `<th onclick="sortExplorer('${h}')" title="Klik untuk sort">
            ${headerLabels[h]} ${_explorerState.sortBy === h ? (_explorerState.sortDir === 'asc' ? '↑' : '↓') : ''}
          </th>`).join('')}
        </tr>
      </thead>
      <tbody>
        ${data.data.map(row => `
          <tr>
            <td>${row.indicator}</td>
            <td><span class="badge badge-blue">${row.source}</span></td>
            <td style="color:var(--color-muted)">${row.unit}</td>
            <td><span class="badge badge-gray">${row.frequency}</span></td>
            <td>${row.region}</td>
            <td>${row.period}</td>
            <td style="text-align:right;font-weight:600">${row.value !== null ? Number(row.value).toLocaleString('id-ID', { maximumFractionDigits: 4 }) : 'N/A'}</td>
          </tr>`).join('')}
      </tbody>
    </table>`;

  document.getElementById('explorer-table-wrapper').innerHTML = html;

  // Pagination
  const totalPages = data.total_pages;
  const page = data.page;
  let paginationHtml = `<span>Halaman ${page} dari ${totalPages} (${data.total.toLocaleString('id-ID')} total)</span>`;
  paginationHtml += `<button class="btn btn-ghost btn-sm" onclick="goExplorerPage(1)" ${page <= 1 ? 'disabled' : ''}>«</button>`;
  paginationHtml += `<button class="btn btn-ghost btn-sm" onclick="goExplorerPage(${page - 1})" ${page <= 1 ? 'disabled' : ''}>‹ Prev</button>`;
  paginationHtml += `<button class="btn btn-ghost btn-sm" onclick="goExplorerPage(${page + 1})" ${page >= totalPages ? 'disabled' : ''}>Next ›</button>`;
  paginationHtml += `<button class="btn btn-ghost btn-sm" onclick="goExplorerPage(${totalPages})" ${page >= totalPages ? 'disabled' : ''}>»</button>`;
  document.getElementById('explorer-pagination').innerHTML = paginationHtml;
}

window.sortExplorer = function (field) {
  if (_explorerState.sortBy === field) {
    _explorerState.sortDir = _explorerState.sortDir === 'asc' ? 'desc' : 'asc';
  } else {
    _explorerState.sortBy = field;
    _explorerState.sortDir = 'asc';
  }
  fetchExplorer();
};

window.goExplorerPage = function (p) {
  _explorerState.page = p;
  fetchExplorer();
};

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

window.ModuleDataExplorer = { loadDataExplorer };
