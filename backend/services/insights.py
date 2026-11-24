"""
Indonesia Economic Intelligence — Auto-Insights Engine

Generates evidence-based analytical findings from loaded datasets.
"""
from typing import List, Dict, Any
import numpy as np
from backend.services.data_loader import get_loader


def _pct_change(a, b):
    if b and b != 0:
        return round((a - b) / abs(b) * 100, 2)
    return None


def generate_insights() -> List[Dict[str, Any]]:
    loader = get_loader()
    insights = []

    # 1. Latest GDP growth vs previous
    gdp = loader.get_gdp_annual()
    if len(gdp) >= 2:
        curr = gdp[-1]
        prev = gdp[-2]
        diff = round(curr["value"] - prev["value"], 2)
        direction = "meningkat" if diff > 0 else "menurun"
        insights.append({
            "id": "gdp_latest_change",
            "title": f"Pertumbuhan PDB {curr['period']}",
            "description": (
                f"Pertumbuhan PDB Indonesia tahun {curr['period']} sebesar {curr['value']}% (YoY), "
                f"{direction} {abs(diff)} poin persentase dibandingkan {prev['period']} ({prev['value']}%)."
            ),
            "indicator": "PDB",
            "period": curr["period"],
            "value": curr["value"],
            "comparison_value": prev["value"],
            "comparison_period": prev["period"],
            "source": "BPS",
            "category": "trend",
        })

    # 2. COVID impact on GDP
    gdp_2020 = next((x for x in gdp if x["period"] == "2020"), None)
    gdp_2019 = next((x for x in gdp if x["period"] == "2019"), None)
    if gdp_2020 and gdp_2019:
        insights.append({
            "id": "gdp_covid_impact",
            "title": "Dampak COVID-19 terhadap PDB",
            "description": (
                f"Pada tahun 2020, PDB Indonesia mengalami kontraksi sebesar {gdp_2020['value']}% "
                f"akibat pandemi COVID-19, turun drastis dari {gdp_2019['value']}% pada 2019. "
                f"Ini merupakan kontraksi pertama sejak krisis 1998."
            ),
            "indicator": "PDB",
            "period": "2020",
            "value": gdp_2020["value"],
            "comparison_value": gdp_2019["value"],
            "comparison_period": "2019",
            "source": "BPS",
            "category": "anomaly",
        })

    # 3. Latest inflation
    inf = loader.get_inflation_monthly()
    if len(inf) >= 2:
        curr_inf = inf[-1]
        prev_inf = inf[-2]
        insights.append({
            "id": "inflation_latest",
            "title": f"Inflasi {curr_inf['period']}",
            "description": (
                f"Inflasi tahunan (YoY) pada {curr_inf['period']} sebesar {curr_inf['yoy']}%, "
                f"{'turun' if curr_inf['yoy'] < prev_inf['yoy'] else 'naik'} dari {prev_inf['yoy']}% "
                f"bulan sebelumnya. Inflasi bulanan (MoM) sebesar {curr_inf['mom']}%."
            ),
            "indicator": "Inflasi",
            "period": curr_inf["period"],
            "value": curr_inf["yoy"],
            "comparison_value": prev_inf["yoy"],
            "comparison_period": prev_inf["period"],
            "source": "BPS",
            "category": "trend",
        })

    # 4. Peak inflation (2022 spike)
    yoy_values = [(x["period"], x["yoy"]) for x in inf]
    max_inf = max(yoy_values, key=lambda x: x[1])
    min_inf = min(yoy_values, key=lambda x: x[1])
    insights.append({
        "id": "inflation_peak",
        "title": "Puncak Inflasi Pasca-Pandemi",
        "description": (
            f"Inflasi tertinggi dalam dataset terjadi pada {max_inf[0]} sebesar {max_inf[1]}% (YoY), "
            f"didorong kenaikan harga energi dan pangan global. "
            f"Inflasi terendah tercatat pada {min_inf[0]} sebesar {min_inf[1]}% (YoY)."
        ),
        "indicator": "Inflasi",
        "period": max_inf[0],
        "value": max_inf[1],
        "source": "BPS",
        "category": "extreme",
    })

    # 5. Exchange rate high
    er = loader.get_exchange_rate()
    er_values = [(x["period"], x["usd_idr"]) for x in er]
    max_er = max(er_values, key=lambda x: x[1])
    latest_er = er_values[-1]
    insights.append({
        "id": "exchange_rate_high",
        "title": "Kurs USD/IDR Tertinggi",
        "description": (
            f"Kurs USD/IDR tertinggi dalam dataset terjadi pada {max_er[0]} sebesar Rp {max_er[1]:,}, "
            f"mencerminkan tekanan eksternal dan penguatan dolar AS. "
            f"Kurs terkini ({latest_er[0]}): Rp {latest_er[1]:,}."
        ),
        "indicator": "Kurs USD/IDR",
        "period": max_er[0],
        "value": max_er[1],
        "source": "Bank Indonesia",
        "category": "extreme",
    })

    # 6. BI Rate tightening cycle
    bi = loader.get_bi_rate()
    bi_2022 = next((x for x in bi if x["period"] == "2022-01"), None)
    bi_peak = max(bi, key=lambda x: x["rate"])
    if bi_2022 and bi_peak:
        insights.append({
            "id": "bi_rate_cycle",
            "title": "Siklus Pengetatan Moneter BI",
            "description": (
                f"Bank Indonesia menaikkan suku bunga acuan dari {bi_2022['rate']}% (Januari 2022) "
                f"ke puncak {bi_peak['rate']}% pada {bi_peak['period']}, "
                f"sebagai respons terhadap lonjakan inflasi global pasca-pandemi."
            ),
            "indicator": "BI Rate",
            "period": bi_peak["period"],
            "value": bi_peak["rate"],
            "comparison_value": bi_2022["rate"],
            "comparison_period": "2022-01",
            "source": "Bank Indonesia",
            "category": "trend",
        })

    # 7. Employment recovery
    emp = loader.get_employment()
    if len(emp) >= 2:
        latest_emp = emp[-1]
        covid_peak = max(emp, key=lambda x: x["tpt"])
        insights.append({
            "id": "employment_recovery",
            "title": "Pemulihan Ketenagakerjaan",
            "description": (
                f"TPT (Tingkat Pengangguran Terbuka) turun ke {latest_emp['tpt']}% "
                f"pada {latest_emp['period']}, dari puncak {covid_peak['tpt']}% pada {covid_peak['period']} "
                f"saat pandemi. Jumlah penduduk bekerja mencapai {latest_emp['employed_m']:.1f} juta orang."
            ),
            "indicator": "TPT",
            "period": latest_emp["period"],
            "value": latest_emp["tpt"],
            "comparison_value": covid_peak["tpt"],
            "comparison_period": covid_peak["period"],
            "source": "BPS",
            "category": "trend",
        })

    # 8. Poverty reduction
    pov = loader.get_poverty()
    if len(pov) >= 2:
        latest_pov = pov[-1]
        oldest_pov = pov[0]
        insights.append({
            "id": "poverty_reduction",
            "title": "Penurunan Tingkat Kemiskinan",
            "description": (
                f"Tingkat kemiskinan nasional turun dari {oldest_pov['rate']}% ({oldest_pov['period']}) "
                f"menjadi {latest_pov['rate']}% ({latest_pov['period']}), "
                f"mencerminkan kemajuan sosial-ekonomi selama periode tersebut. "
                f"Jumlah penduduk miskin: {latest_pov['population_m']:.2f} juta jiwa."
            ),
            "indicator": "Kemiskinan",
            "period": latest_pov["period"],
            "value": latest_pov["rate"],
            "comparison_value": oldest_pov["rate"],
            "comparison_period": oldest_pov["period"],
            "source": "BPS",
            "category": "trend",
        })

    # 9. Trade balance
    trade = loader.get_trade()
    if trade:
        latest_trade = trade[-1]
        balance = latest_trade["exports"] - latest_trade["imports"]
        surplus_months = sum(1 for t in trade if t["exports"] > t["imports"])
        insights.append({
            "id": "trade_balance",
            "title": "Neraca Perdagangan",
            "description": (
                f"Pada {latest_trade['period']}, Indonesia mencatat "
                f"{'surplus' if balance >= 0 else 'defisit'} perdagangan USD {abs(balance):,} juta "
                f"(ekspor USD {latest_trade['exports']:,} juta vs impor USD {latest_trade['imports']:,} juta). "
                f"Indonesia mencatat surplus pada {surplus_months} dari {len(trade)} bulan dalam dataset."
            ),
            "indicator": "Neraca Perdagangan",
            "period": latest_trade["period"],
            "value": balance,
            "source": "BPS",
            "category": "trend",
        })

    # 10. Regional disparity — GDP per capita
    reg = loader.get_regional_gdp()
    if reg:
        max_prov = max(reg, key=lambda x: x["gdp_per_capita_m_idr"])
        min_prov = min(reg, key=lambda x: x["gdp_per_capita_m_idr"])
        ratio = round(max_prov["gdp_per_capita_m_idr"] / min_prov["gdp_per_capita_m_idr"], 1)
        insights.append({
            "id": "regional_gdp_disparity",
            "title": "Kesenjangan PDB per Kapita Antarprovinsi",
            "description": (
                f"PDB per kapita tertinggi: {max_prov['province_name']} (Rp {max_prov['gdp_per_capita_m_idr']:.1f} juta). "
                f"Terendah: {min_prov['province_name']} (Rp {min_prov['gdp_per_capita_m_idr']:.1f} juta). "
                f"Rasio kesenjangan: {ratio}x — mencerminkan disparitas ekonomi regional yang signifikan."
            ),
            "indicator": "PDB per Kapita Regional",
            "period": "2023",
            "value": max_prov["gdp_per_capita_m_idr"],
            "comparison_value": min_prov["gdp_per_capita_m_idr"],
            "source": "BPS",
            "category": "regional",
        })

    return insights
