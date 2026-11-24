"""
Indonesia Economic Intelligence — Forecasting Service

Implements: Moving Average, Linear Regression, Exponential Smoothing, ARIMA
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def _mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - predicted)))


def _rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def moving_average(values: List[float], horizon: int, window: int = 3) -> Dict:
    """Simple moving-average forecast."""
    arr = np.array(values, dtype=float)
    if len(arr) < window + 1:
        return {"error": "Insufficient data for moving average"}

    # Last window values → forecast
    forecasts = []
    history = list(arr)
    for _ in range(horizon):
        f = float(np.mean(history[-window:]))
        forecasts.append(f)
        history.append(f)

    # In-sample residuals for metrics
    fitted = np.array([np.mean(arr[i:i+window]) for i in range(len(arr)-window)])
    actual_aligned = arr[window:]
    std_err = float(np.std(arr[-window:]))

    return {
        "method": "Moving Average",
        "window": window,
        "forecast": forecasts,
        "lower": [f - 1.96 * std_err for f in forecasts],
        "upper": [f + 1.96 * std_err for f in forecasts],
        "mae": _mae(actual_aligned, fitted),
        "rmse": _rmse(actual_aligned, fitted),
    }


def linear_regression(values: List[float], horizon: int) -> Dict:
    """Linear regression trend forecast."""
    arr = np.array(values, dtype=float)
    n = len(arr)
    if n < 4:
        return {"error": "Insufficient data for linear regression"}

    x = np.arange(n)
    coeffs = np.polyfit(x, arr, 1)
    slope, intercept = coeffs

    fitted = slope * x + intercept
    residuals = arr - fitted
    std_err = float(np.std(residuals))

    forecast = [float(slope * (n + i) + intercept) for i in range(horizon)]
    lower = [f - 1.96 * std_err for f in forecast]
    upper = [f + 1.96 * std_err for f in forecast]

    return {
        "method": "Linear Regression",
        "slope": float(slope),
        "intercept": float(intercept),
        "forecast": forecast,
        "lower": lower,
        "upper": upper,
        "mae": _mae(arr, fitted),
        "rmse": _rmse(arr, fitted),
    }


def exponential_smoothing(values: List[float], horizon: int, alpha: float = 0.3) -> Dict:
    """Single exponential smoothing (Holt's if trend present)."""
    arr = np.array(values, dtype=float)
    n = len(arr)
    if n < 4:
        return {"error": "Insufficient data"}

    # Simple exponential smoothing
    smoothed = [arr[0]]
    for i in range(1, n):
        smoothed.append(alpha * arr[i] + (1 - alpha) * smoothed[-1])

    last = smoothed[-1]
    trend_est = float(np.mean(np.diff(smoothed[-6:]))) if n > 6 else 0.0

    forecast = [last + trend_est * (i + 1) for i in range(horizon)]
    residuals = arr - np.array(smoothed)
    std_err = float(np.std(residuals))

    return {
        "method": "Exponential Smoothing",
        "alpha": alpha,
        "forecast": forecast,
        "lower": [f - 1.96 * std_err for f in forecast],
        "upper": [f + 1.96 * std_err for f in forecast],
        "mae": _mae(arr, np.array(smoothed)),
        "rmse": _rmse(arr, np.array(smoothed)),
    }


def arima_forecast(values: List[float], horizon: int) -> Dict:
    """ARIMA(1,1,1) forecast using statsmodels."""
    try:
        from statsmodels.tsa.arima.model import ARIMA as _ARIMA
        arr = np.array(values, dtype=float)
        if len(arr) < 12:
            return {"error": "Insufficient data for ARIMA (minimum 12 observations required)"}

        model = _ARIMA(arr, order=(1, 1, 1))
        result = model.fit()
        forecast_obj = result.get_forecast(steps=horizon)
        forecast = forecast_obj.predicted_mean.tolist()
        ci = forecast_obj.conf_int(alpha=0.05)
        lower = ci.iloc[:, 0].tolist()
        upper = ci.iloc[:, 1].tolist()

        fitted = result.fittedvalues
        # ARIMA fitted values start from index 1
        actual_aligned = arr[len(arr)-len(fitted):]
        return {
            "method": "ARIMA(1,1,1)",
            "forecast": forecast,
            "lower": lower,
            "upper": upper,
            "mae": _mae(actual_aligned, np.array(fitted)),
            "rmse": _rmse(actual_aligned, np.array(fitted)),
            "aic": float(result.aic),
        }
    except Exception as e:
        logger.warning(f"ARIMA failed: {e}")
        return {"error": f"ARIMA unavailable: {str(e)}"}


def run_all_methods(values: List[float], periods: List[str], horizon: int) -> Dict:
    """
    Run all forecasting methods and return consolidated results.
    Returns best available result + all method outputs.
    """
    if len(values) < 6:
        return {"error": "Insufficient historical data for forecasting (minimum 6 observations)"}

    results = {
        "moving_average": moving_average(values, horizon),
        "linear_regression": linear_regression(values, horizon),
        "exponential_smoothing": exponential_smoothing(values, horizon),
    }

    if len(values) >= 12:
        results["arima"] = arima_forecast(values, horizon)

    # Pick best method by RMSE
    best_method = None
    best_rmse = float("inf")
    for method_name, r in results.items():
        if "error" not in r and r.get("rmse", float("inf")) < best_rmse:
            best_rmse = r["rmse"]
            best_method = method_name

    return {
        "methods": results,
        "best_method": best_method,
        "horizon": horizon,
        "history_periods": periods,
        "history_values": values,
    }
