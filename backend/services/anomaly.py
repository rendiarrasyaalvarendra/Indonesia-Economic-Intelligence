"""
Indonesia Economic Intelligence — Anomaly Detection Service

Methods: Z-Score, IQR, Moving Average Deviation
"""
import numpy as np
from typing import List, Dict, Any, Optional


def _zscore(arr: np.ndarray) -> np.ndarray:
    mu = np.mean(arr)
    sigma = np.std(arr)
    if sigma == 0:
        return np.zeros(len(arr))
    return (arr - mu) / sigma


def _iqr_bounds(arr: np.ndarray, multiplier: float = 1.5):
    q1 = np.percentile(arr, 25)
    q3 = np.percentile(arr, 75)
    iqr = q3 - q1
    return q1 - multiplier * iqr, q3 + multiplier * iqr


def _ma_deviation(arr: np.ndarray, window: int = 6) -> np.ndarray:
    """Deviation from centered moving average, in units of rolling std."""
    deviations = np.zeros(len(arr))
    for i in range(len(arr)):
        start = max(0, i - window)
        end = min(len(arr), i + window + 1)
        segment = arr[start:end]
        ma = np.mean(segment)
        std = np.std(segment) if np.std(segment) > 0 else 1
        deviations[i] = (arr[i] - ma) / std
    return deviations


def detect_anomalies(
    values: List[float],
    periods: List[str],
    indicator: str,
    unit: str,
    source: str,
    z_threshold: float = 2.5,
    iqr_multiplier: float = 1.5,
    ma_threshold: float = 2.0,
) -> Dict[str, Any]:
    """
    Detect anomalies using three complementary methods.
    Returns combined results.
    """
    arr = np.array(values, dtype=float)
    n = len(arr)
    if n < 6:
        return {
            "indicator": indicator,
            "unit": unit,
            "source": source,
            "anomalies": [],
            "total_observations": n,
            "total_anomalies": 0,
            "note": "Insufficient data for anomaly detection (minimum 6 observations)",
        }

    zscores = _zscore(arr)
    iqr_lo, iqr_hi = _iqr_bounds(arr, iqr_multiplier)
    ma_devs = _ma_deviation(arr)

    anomalies = []
    for i, (period, value) in enumerate(zip(periods, values)):
        z = float(zscores[i])
        iqr_flag = bool(value < iqr_lo or value > iqr_hi)
        ma_dev = float(ma_devs[i])

        is_anomaly = abs(z) > z_threshold or iqr_flag or abs(ma_dev) > ma_threshold
        methods_triggered = []
        if abs(z) > z_threshold:
            methods_triggered.append(f"Z-Score={z:.2f}")
        if iqr_flag:
            direction = "below IQR lower bound" if value < iqr_lo else "above IQR upper bound"
            methods_triggered.append(f"IQR ({direction})")
        if abs(ma_dev) > ma_threshold:
            methods_triggered.append(f"MA Deviation={ma_dev:.2f}")

        if is_anomaly:
            desc = (
                f"Value {value:,.2f} {unit} in {period} flagged by: "
                + "; ".join(methods_triggered)
                + f". Mean={np.mean(arr):.2f}, Std={np.std(arr):.2f}."
            )
            anomalies.append({
                "period": period,
                "value": float(value),
                "z_score": z,
                "iqr_flag": iqr_flag,
                "ma_deviation": ma_dev,
                "is_anomaly": True,
                "method": " | ".join(methods_triggered),
                "description": desc,
            })

    return {
        "indicator": indicator,
        "unit": unit,
        "source": source,
        "anomalies": anomalies,
        "total_observations": n,
        "total_anomalies": len(anomalies),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "z_threshold": z_threshold,
        "iqr_lower": float(iqr_lo),
        "iqr_upper": float(iqr_hi),
        "all_values": [
            {
                "period": p,
                "value": float(v),
                "z_score": float(zscores[i]),
                "is_anomaly": any(
                    a["period"] == p for a in anomalies
                ),
            }
            for i, (p, v) in enumerate(zip(periods, values))
        ],
    }
