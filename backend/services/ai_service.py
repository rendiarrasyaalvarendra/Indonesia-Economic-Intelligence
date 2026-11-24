"""
Indonesia Economic Intelligence — AI Service (OpenAI integration)

All AI responses are grounded in real loaded datasets.
API key is handled server-side only.
"""
import json
import logging
from typing import List, Dict, Any, Optional

from backend.config import settings
from backend.services.data_loader import get_loader

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Anda adalah Analis Ekonomi AI yang ahli untuk platform Indonesia Economic Intelligence.

Tugas Anda:
- Menjawab pertanyaan pengguna tentang kondisi ekonomi Indonesia secara akurat.
- Menggunakan data ekonomi resmi yang tersedia (BPS, Bank Indonesia) sebagai dasar analisis.
- Menyebutkan angka, periode, dan sumber data secara eksplisit.
- Menjelaskan tren, perubahan signifikan, dan hubungan antar indikator.
- Mengidentifikasi anomali atau pola yang menarik dalam data.
- Memberikan konteks ekonomi yang relevan.

Batasan penting:
- Jangan mengarang statistik atau data yang tidak ada dalam dataset.
- Jangan menginterpretasikan korelasi sebagai kausalitas tanpa bukti.
- Jangan menyebut anomali statistik sebagai "krisis" tanpa bukti yang cukup.
- Jika data tidak tersedia, jelaskan keterbatasannya dengan jujur.
- Selalu sebutkan sumber data (BPS/Bank Indonesia) dan periode yang relevan.
- Gunakan Bahasa Indonesia yang profesional namun mudah dipahami.

Format respons:
- Gunakan paragraf yang terstruktur dan mudah dibaca.
- Sertakan angka spesifik untuk mendukung setiap pernyataan.
- Jika relevan, sebutkan konteks historis atau perbandingan.
"""


def _build_data_context(loader) -> str:
    """Build a concise data summary to inject into the system context."""
    kpis = loader.get_latest_kpis()
    gdp = loader.get_gdp_annual()
    inf = loader.get_inflation_monthly()
    er = loader.get_exchange_rate()
    bi = loader.get_bi_rate()
    emp = loader.get_employment()
    pov = loader.get_poverty()
    trade = loader.get_trade()

    latest_inf = inf[-1] if inf else {}
    latest_er = er[-1] if er else {}
    latest_bi = bi[-1] if bi else {}
    latest_emp = emp[-1] if emp else {}
    latest_pov = pov[-1] if pov else {}
    latest_trade = trade[-1] if trade else {}

    gdp_last5 = gdp[-5:] if len(gdp) >= 5 else gdp

    ctx = f"""
=== DATA EKONOMI INDONESIA (RINGKASAN) ===

PDB (Pertumbuhan Tahunan, % YoY):
{json.dumps(gdp_last5, ensure_ascii=False)}

Inflasi Terbaru ({latest_inf.get('period','N/A')}):
  - MoM: {latest_inf.get('mom','N/A')}%
  - YoY: {latest_inf.get('yoy','N/A')}%
  - CPI: {latest_inf.get('cpi','N/A')}

Kurs USD/IDR ({latest_er.get('period','N/A')}): Rp {latest_er.get('usd_idr','N/A'):,}
BI Rate ({latest_bi.get('period','N/A')}): {latest_bi.get('rate','N/A')}%

Ketenagakerjaan ({latest_emp.get('period','N/A')}):
  - TPT: {latest_emp.get('tpt','N/A')}%
  - TPAK: {latest_emp.get('tpak','N/A')}%
  - Bekerja: {latest_emp.get('employed_m','N/A')} juta
  - Menganggur: {latest_emp.get('unemployed_m','N/A')} juta

Kemiskinan ({latest_pov.get('period','N/A')}):
  - Tingkat: {latest_pov.get('rate','N/A')}%
  - Jumlah: {latest_pov.get('population_m','N/A')} juta jiwa

Perdagangan ({latest_trade.get('period','N/A')}):
  - Ekspor: USD {latest_trade.get('exports','N/A'):,} juta
  - Impor: USD {latest_trade.get('imports','N/A'):,} juta

Sumber: BPS (bps.go.id) dan Bank Indonesia (bi.go.id)
"""
    return ctx.strip()


async def chat(message: str, history: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Send a message to the AI and return the response."""
    if not settings.openai_api_key:
        # Fallback: rule-based response when no API key
        return _fallback_response(message)

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)

        loader = get_loader()
        data_ctx = _build_data_context(loader)

        full_system = SYSTEM_PROMPT + "\n\n" + data_ctx

        messages = [{"role": "system", "content": full_system}]
        if history:
            for h in history[-8:]:  # last 8 turns for context window
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            max_tokens=1200,
            temperature=0.3,
        )

        reply = response.choices[0].message.content
        return {
            "reply": reply,
            "sources": ["BPS (bps.go.id)", "Bank Indonesia (bi.go.id)"],
            "charts": [],
        }

    except Exception as e:
        logger.error(f"AI chat error: {e}")
        return {
            "reply": f"Maaf, terjadi kesalahan pada layanan AI: {str(e)}. Silakan periksa konfigurasi API key.",
            "sources": [],
            "charts": [],
        }


def _fallback_response(message: str) -> Dict[str, Any]:
    """Rule-based fallback when OpenAI key is not configured."""
    loader = get_loader()
    kpis = loader.get_latest_kpis()
    msg_lower = message.lower()

    if any(w in msg_lower for w in ["pdb", "gdp", "pertumbuhan ekonomi"]):
        kpi = kpis["gdp_growth"]
        reply = (
            f"Pertumbuhan PDB Indonesia tahun {kpi['period']} sebesar **{kpi['value']}%** (YoY), "
            f"{'naik' if kpi['change'] >= 0 else 'turun'} {abs(kpi['change'])} poin persentase "
            f"dibandingkan {kpi['previous_period']} ({kpi['previous_value']}%). "
            f"Sumber: {kpi['source']}."
        )
    elif any(w in msg_lower for w in ["inflasi", "inflation", "harga", "cpi"]):
        kpi = kpis["inflation"]
        reply = (
            f"Inflasi Indonesia pada {kpi['period']} sebesar **{kpi['value']}%** (YoY), "
            f"{'meningkat' if kpi['change'] >= 0 else 'menurun'} {abs(kpi['change'])} poin "
            f"dari {kpi['previous_period']} ({kpi['previous_value']}%). "
            f"Sumber: {kpi['source']}."
        )
    elif any(w in msg_lower for w in ["kurs", "dollar", "usd", "rupiah", "idr"]):
        kpi = kpis["exchange_rate"]
        reply = (
            f"Kurs USD/IDR pada {kpi['period']}: **Rp {kpi['value']:,.0f}**, "
            f"{'melemah' if kpi['change'] >= 0 else 'menguat'} Rp {abs(kpi['change']):,.0f} "
            f"dari bulan sebelumnya. Sumber: {kpi['source']}."
        )
    elif any(w in msg_lower for w in ["bi rate", "suku bunga", "bunga acuan", "interest rate"]):
        kpi = kpis["bi_rate"]
        reply = (
            f"BI Rate pada {kpi['period']}: **{kpi['value']}%**, "
            f"{'naik' if kpi['change'] >= 0 else 'turun'} {abs(kpi['change'])} poin "
            f"dari bulan sebelumnya. Sumber: {kpi['source']}."
        )
    elif any(w in msg_lower for w in ["pengangguran", "tenaga kerja", "kerja", "tpt", "tpak"]):
        emp = loader.get_employment()[-1]
        reply = (
            f"Data ketenagakerjaan Indonesia ({emp['period']}): "
            f"TPT **{emp['tpt']}%**, TPAK {emp['tpak']}%, "
            f"penduduk bekerja {emp['employed_m']:.1f} juta jiwa. Sumber: BPS."
        )
    elif any(w in msg_lower for w in ["kemiskinan", "miskin", "poverty"]):
        pov = loader.get_poverty()[-1]
        reply = (
            f"Tingkat kemiskinan Indonesia ({pov['period']}): **{pov['rate']}%**, "
            f"setara {pov['population_m']:.2f} juta jiwa. "
            f"Garis kemiskinan: Rp {pov['poverty_line']:,}/kapita/bulan. Sumber: BPS."
        )
    elif any(w in msg_lower for w in ["ekspor", "impor", "perdagangan", "trade", "neraca"]):
        t = loader.get_trade()[-1]
        balance = t["exports"] - t["imports"]
        reply = (
            f"Neraca perdagangan Indonesia ({t['period']}): "
            f"Ekspor USD {t['exports']:,} juta, Impor USD {t['imports']:,} juta, "
            f"{'Surplus' if balance >= 0 else 'Defisit'} USD {abs(balance):,} juta. Sumber: BPS."
        )
    else:
        reply = (
            "Halo! Saya adalah Analis Ekonomi AI Indonesia Economic Intelligence. "
            "Anda dapat menanyakan tentang: PDB/GDP, inflasi, kurs USD/IDR, BI Rate, "
            "ketenagakerjaan, kemiskinan, atau perdagangan internasional Indonesia. "
            "\n\n*Catatan: Untuk analisis mendalam, konfigurasikan OPENAI_API_KEY di file .env.*"
        )

    return {
        "reply": reply,
        "sources": ["BPS (bps.go.id)", "Bank Indonesia (bi.go.id)"],
        "charts": [],
    }
