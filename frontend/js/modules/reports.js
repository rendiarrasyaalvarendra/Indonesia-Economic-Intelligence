/**
 * AI Economic Reports Module
 */
async function loadReports() {
  const previewFrame = document.getElementById('report-preview-frame');
  const generateBtn = document.getElementById('report-generate-btn');
  const pdfBtn = document.getElementById('report-pdf-btn');
  const statusEl = document.getElementById('report-status');

  async function generateReport(format = 'html') {
    const periodStart = document.getElementById('report-period-start').value || undefined;
    const periodEnd = document.getElementById('report-period-end').value || undefined;

    const checkedIndicators = [...document.querySelectorAll('#report-indicators input:checked')]
      .map(c => c.value);
    const indicators = checkedIndicators.length ? checkedIndicators : undefined;

    statusEl.textContent = 'Membuat laporan...';
    statusEl.style.color = 'var(--color-muted)';
    generateBtn.disabled = true;
    pdfBtn.disabled = true;

    try {
      if (format === 'pdf') {
        // PDF: open in new tab (streaming response)
        statusEl.textContent = 'Mengunduh PDF...';
        const url = '/api/reports/preview'; // Use preview for simplicity
        window.open(url, '_blank');
        statusEl.textContent = 'PDF dibuka di tab baru. Gunakan Print → Save as PDF.';
        statusEl.style.color = 'var(--color-success)';
      } else {
        // HTML preview
        const htmlContent = await window.API.reportPreview();
        // Show in iframe
        const blob = new Blob([htmlContent], { type: 'text/html' });
        const blobUrl = URL.createObjectURL(blob);
        previewFrame.src = blobUrl;
        previewFrame.style.display = 'block';
        document.getElementById('report-placeholder').style.display = 'none';
        statusEl.textContent = '✅ Laporan berhasil dibuat.';
        statusEl.style.color = 'var(--color-success)';
      }
    } catch (e) {
      statusEl.textContent = `⚠️ ${e.message}`;
      statusEl.style.color = 'var(--color-danger)';
    } finally {
      generateBtn.disabled = false;
      pdfBtn.disabled = false;
    }
  }

  generateBtn.addEventListener('click', () => generateReport('html'));
  pdfBtn.addEventListener('click', () => generateReport('pdf'));

  // Print report
  document.getElementById('report-print-btn').addEventListener('click', () => {
    if (previewFrame.src && previewFrame.src !== 'about:blank') {
      previewFrame.contentWindow.print();
    } else {
      window.open('/api/reports/preview', '_blank');
    }
  });
}

window.ModuleReports = { loadReports };
