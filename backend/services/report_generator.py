"""
Indonesia Economic Intelligence — Report Generator

Generates structured HTML and PDF economic reports.
"""
import io
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.services.data_loader import get_loader
from backend.services.insights import generate_insights

logger = logging.getLogger(__name__)


def _fmt_num(v, decimals=2):
    if v is None:
        return "N/A"
    return f"{v:,.{decimals}f}"


def generate_html_report(
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    indicators: Optional[List[str]] = None,
) -> str:
    loader = get_loader()
    kpis = loader.get_latest_kpis()
    gdp = loader.get_gdp_annual()
    inf = loader.get_inflation_monthly()
    er = loader.get_exchange_rate()
    bi = loader.get_bi_rate()
    emp = loader.get_employment()
    pov = loader.get_poverty()
    trade = loader.get_trade()
    insights = generate_insights()

    gen_time = datetime.now().strftime("%d %B %Y, %H:%M WIB")
    latest_inf = inf[-1] if inf else {}
    latest_er = er[-1] if er else {}
    latest_bi = bi[-1] if bi else {}
    latest_emp = emp[-1] if emp else {}
    latest_pov = pov[-1] if pov else {}
    latest_trade = trade[-1] if trade else {}
    latest_gdp = gdp[-1] if gdp else {}

    # Build insights HTML
    insights_html = ""
    for ins in insights[:6]:
        insights_html += f"""
        <div class="insight-item">
            <h4>{ins['title']}</h4>
            <p>{ins['description']}</p>
            <small>Sumber: {ins['source']} | Periode: {ins['period']}</small>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Laporan Ekonomi Indonesia — {gen_time}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; color: #1f2328; background: #fff; }}
  .cover {{ background: #0f172a; color: white; padding: 60px 40px; text-align: center; }}
  .cover h1 {{ font-size: 2.2em; margin-bottom: 10px; }}
  .cover p {{ color: #94a3b8; font-size: 1.1em; }}
  .section {{ padding: 30px 40px; border-bottom: 1px solid #e5e7eb; max-width: 900px; margin: 0 auto; }}
  h2 {{ color: #0f172a; border-left: 4px solid #3b82f6; padding-left: 12px; }}
  h3 {{ color: #374151; }}
  table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 0.95em; }}
  th {{ background: #f1f5f9; padding: 10px; text-align: left; border-bottom: 2px solid #e2e8f0; }}
  td {{ padding: 9px 10px; border-bottom: 1px solid #f1f5f9; }}
  tr:hover td {{ background: #f8fafc; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 20px 0; }}
  .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; }}
  .kpi-value {{ font-size: 2em; font-weight: bold; color: #0f172a; }}
  .kpi-label {{ color: #64748b; font-size: 0.9em; margin-top: 4px; }}
  .insight-item {{ background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 14px 18px; margin-bottom: 14px; border-radius: 4px; }}
  .insight-item h4 {{ margin: 0 0 8px; color: #0369a1; }}
  .insight-item p {{ margin: 0 0 6px; }}
  .insight-item small {{ color: #64748b; }}
  .footer {{ text-align: center; padding: 24px; background: #f8fafc; color: #94a3b8; font-size: 0.85em; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.82em; font-weight: 600; }}
  .badge-up {{ background: #dcfce7; color: #16a34a; }}
  .badge-down {{ background: #fee2e2; color: #dc2626; }}
  @media print {{
    .section {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>

<div class="cover">
  <h1>🇮🇩 Laporan Ekonomi Indonesia</h1>
  <p>Indonesia Economic Intelligence Platform</p>
  <p>Digenerate: {gen_time}</p>
  <p>Sumber Data: BPS (bps.go.id) &amp; Bank Indonesia (bi.go.id)</p>
</div>

<!-- 1. Ringkasan Eksekutif -->
<div class="section">
  <h2>1. Ringkasan Eksekutif</h2>
  <p>Laporan ini menyajikan kondisi ekonomi Indonesia berdasarkan data resmi dari Badan Pusat Statistik (BPS) dan Bank Indonesia (BI). Periode data yang dicakup hingga data terbaru yang tersedia.</p>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-value">{_fmt_num(kpis['gdp_growth']['value'], 2)}%</div>
      <div class="kpi-label">Pertumbuhan PDB ({kpis['gdp_growth']['period']})</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value">{_fmt_num(kpis['inflation']['value'], 2)}%</div>
      <div class="kpi-label">Inflasi YoY ({kpis['inflation']['period']})</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value">Rp {kpis['exchange_rate']['value']:,.0f}</div>
      <div class="kpi-label">Kurs USD/IDR ({kpis['exchange_rate']['period']})</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value">{_fmt_num(kpis['bi_rate']['value'], 2)}%</div>
      <div class="kpi-label">BI Rate ({kpis['bi_rate']['period']})</div>
    </div>
  </div>
</div>

<!-- 2. Analisis PDB -->
<div class="section">
  <h2>2. Analisis PDB</h2>
  <p>Pertumbuhan Produk Domestik Bruto (PDB) Indonesia menunjukkan ketahanan ekonomi pasca pandemi. Pada {latest_gdp.get('period','N/A')}, PDB tumbuh {_fmt_num(latest_gdp.get('value'), 2)}% (YoY).</p>
  <h3>Tren Pertumbuhan PDB Tahunan (5 Tahun Terakhir)</h3>
  <table>
    <tr><th>Tahun</th><th>Pertumbuhan PDB (% YoY)</th></tr>
    {''.join(f"<tr><td>{r['period']}</td><td>{_fmt_num(r['value'], 2)}%</td></tr>" for r in gdp[-8:])}
  </table>
</div>

<!-- 3. Analisis Inflasi -->
<div class="section">
  <h2>3. Analisis Inflasi</h2>
  <p>Inflasi Indonesia pada {latest_inf.get('period','N/A')} sebesar {_fmt_num(latest_inf.get('yoy'), 2)}% (YoY) dan {_fmt_num(latest_inf.get('mom'), 2)}% (MoM). CPI: {_fmt_num(latest_inf.get('cpi'), 2)}.</p>
  <h3>Inflasi Bulanan (12 Bulan Terakhir)</h3>
  <table>
    <tr><th>Periode</th><th>MoM (%)</th><th>YoY (%)</th><th>CPI</th></tr>
    {''.join(f"<tr><td>{r['period']}</td><td>{_fmt_num(r['mom'], 2)}</td><td>{_fmt_num(r['yoy'], 2)}</td><td>{_fmt_num(r['cpi'], 2)}</td></tr>" for r in inf[-12:])}
  </table>
</div>

<!-- 4. Analisis Moneter -->
<div class="section">
  <h2>4. Analisis Moneter</h2>
  <p>BI Rate saat ini: <strong>{_fmt_num(latest_bi.get('rate'), 2)}%</strong> ({latest_bi.get('period','N/A')}). Kurs USD/IDR: <strong>Rp {latest_er.get('usd_idr', 0):,.0f}</strong> ({latest_er.get('period','N/A')}).</p>
  <h3>BI Rate & Kurs USD/IDR (12 Bulan Terakhir)</h3>
  <table>
    <tr><th>Periode</th><th>BI Rate (%)</th><th>USD/IDR (Rp)</th></tr>
    {''.join(f"<tr><td>{b['period']}</td><td>{_fmt_num(b['rate'], 2)}</td><td>{next((e['usd_idr'] for e in er if e['period']==b['period']), 'N/A'):,}</td></tr>" for b in bi[-12:])}
  </table>
</div>

<!-- 5. Analisis Ketenagakerjaan & Kemiskinan -->
<div class="section">
  <h2>5. Ketenagakerjaan &amp; Kemiskinan</h2>
  <p><strong>Ketenagakerjaan ({latest_emp.get('period','N/A')}):</strong> TPT {_fmt_num(latest_emp.get('tpt'), 2)}%, TPAK {_fmt_num(latest_emp.get('tpak'), 2)}%, Penduduk bekerja {_fmt_num(latest_emp.get('employed_m'), 1)} juta.</p>
  <p><strong>Kemiskinan ({latest_pov.get('period','N/A')}):</strong> Tingkat {_fmt_num(latest_pov.get('rate'), 2)}%, Jumlah {_fmt_num(latest_pov.get('population_m'), 2)} juta jiwa, Garis kemiskinan Rp {latest_pov.get('poverty_line', 0):,}/kapita/bulan.</p>
</div>

<!-- 6. Analisis Perdagangan -->
<div class="section">
  <h2>6. Analisis Perdagangan Internasional</h2>
  <p>Pada {latest_trade.get('period','N/A')}: Ekspor USD {latest_trade.get('exports', 0):,} juta, Impor USD {latest_trade.get('imports', 0):,} juta.</p>
  <h3>Neraca Perdagangan (12 Bulan Terakhir)</h3>
  <table>
    <tr><th>Periode</th><th>Ekspor (USD Juta)</th><th>Impor (USD Juta)</th><th>Neraca</th></tr>
    {''.join(f"<tr><td>{t['period']}</td><td>{t['exports']:,}</td><td>{t['imports']:,}</td><td class=\"{'badge badge-up' if t['exports']>=t['imports'] else 'badge badge-down'}\">{'+' if t['exports']>=t['imports'] else ''}{t['exports']-t['imports']:,}</td></tr>" for t in trade[-12:])}
  </table>
</div>

<!-- 7. Insight Ekonomi -->
<div class="section">
  <h2>7. Insight &amp; Temuan Analitis</h2>
  {insights_html}
</div>

<!-- 8. Sumber & Metodologi -->
<div class="section">
  <h2>8. Sumber Data &amp; Metodologi</h2>
  <table>
    <tr><th>Sumber</th><th>Indikator</th><th>URL</th></tr>
    <tr><td>BPS (Badan Pusat Statistik)</td><td>PDB, Inflasi, CPI, Ketenagakerjaan, Kemiskinan, Perdagangan, Regional</td><td>https://bps.go.id</td></tr>
    <tr><td>Bank Indonesia</td><td>Kurs USD/IDR, BI Rate, Kebijakan Moneter</td><td>https://bi.go.id</td></tr>
  </table>
  <p><small>Catatan: Data yang ditampilkan bersumber dari publikasi resmi BPS dan Bank Indonesia. Proyeksi/forecast menggunakan metode statistik standar dan bukan merupakan prediksi resmi pemerintah.</small></p>
</div>

<div class="footer">
  <p>Indonesia Economic Intelligence Platform | Digenerate: {gen_time}</p>
  <p>Data resmi dari BPS (bps.go.id) dan Bank Indonesia (bi.go.id)</p>
</div>

</body>
</html>"""
    return html


def generate_pdf_report(**kwargs) -> bytes:
    """Generate PDF from the HTML report using reportlab."""
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        loader = get_loader()
        kpis = loader.get_latest_kpis()
        gdp = loader.get_gdp_annual()
        inf = loader.get_inflation_monthly()
        emp = loader.get_employment()
        pov = loader.get_poverty()

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle("Title", parent=styles["Title"],
                                     textColor=colors.HexColor("#0f172a"), fontSize=20)
        h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
                                   textColor=colors.HexColor("#1e40af"), fontSize=14)
        body_style = styles["BodyText"]
        body_style.fontSize = 10
        body_style.leading = 16

        story.append(Paragraph("Laporan Ekonomi Indonesia", title_style))
        story.append(Paragraph(f"Indonesia Economic Intelligence Platform", styles["Heading3"]))
        story.append(Paragraph(f"Digenerate: {datetime.now().strftime('%d %B %Y, %H:%M WIB')}", styles["Normal"]))
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph("1. Ringkasan Eksekutif", h2_style))
        kpi_data = [
            ["Indikator", "Nilai", "Periode", "Sumber"],
            ["Pertumbuhan PDB", f"{kpis['gdp_growth']['value']}% YoY", kpis['gdp_growth']['period'], "BPS"],
            ["Inflasi YoY", f"{kpis['inflation']['value']}%", kpis['inflation']['period'], "BPS"],
            ["Kurs USD/IDR", f"Rp {kpis['exchange_rate']['value']:,.0f}", kpis['exchange_rate']['period'], "Bank Indonesia"],
            ["BI Rate", f"{kpis['bi_rate']['value']}%", kpis['bi_rate']['period'], "Bank Indonesia"],
        ]
        t = Table(kpi_data, colWidths=[5*cm, 4*cm, 3.5*cm, 4*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4*cm))

        story.append(Paragraph("2. Tren PDB Tahunan", h2_style))
        gdp_data = [["Tahun", "Pertumbuhan PDB (% YoY)"]] + \
                   [[r["period"], f"{r['value']}%"] for r in gdp[-10:]]
        t2 = Table(gdp_data, colWidths=[8*cm, 8.5*cm])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t2)
        story.append(Spacer(1, 0.4*cm))

        story.append(Paragraph("3. Inflasi (12 Bulan Terakhir)", h2_style))
        inf_data = [["Periode", "MoM (%)", "YoY (%)", "CPI"]] + \
                   [[r["period"], f"{r['mom']}%", f"{r['yoy']}%", f"{r['cpi']}"] for r in inf[-12:]]
        t3 = Table(inf_data, colWidths=[4*cm, 3.5*cm, 3.5*cm, 5.5*cm])
        t3.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(t3)

        story.append(Spacer(1, 0.4*cm))
        story.append(Paragraph("Sumber Data: BPS (bps.go.id) dan Bank Indonesia (bi.go.id)", styles["Normal"]))

        doc.build(story)
        return buf.getvalue()
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise
