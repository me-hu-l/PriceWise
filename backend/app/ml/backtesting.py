"""Walk-forward validation (roadmap section 26) — never a random train/test split.

Produces per-fold, per-candidate one-step-ahead predictions using only data
available strictly before the target date, so downstream metrics (MAE, RMSE,
MAPE, directional accuracy, prediction-interval coverage — section 27) and
ensemble weights are leakage-free.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.ml import baselines
from app.ml.driver_model import fit_driver_model
from app.ml.residual_model import fit_residual_model

MIN_TRAIN_SIZE = 6


def run_walk_forward(price_df: pd.DataFrame, driver_df: pd.DataFrame) -> list[dict]:
    """One fold per t in [MIN_TRAIN_SIZE, n-1]: train on rows [0:t], predict row t."""
    n = len(price_df)
    folds: list[dict] = []
    min_train = min(MIN_TRAIN_SIZE, max(3, n - 1))

    for t in range(min_train, n):
        prices_train = price_df["price"].iloc[:t].tolist()
        prev_price = price_df["price"].iloc[t - 1]
        actual_price = price_df["price"].iloc[t]
        actual_pct = (actual_price - prev_price) / prev_price

        baseline_price = baselines.exponential_smoothing(prices_train)
        baseline_pct = baseline_price / prev_price - 1

        driver_pct = None
        ml_pct = None
        driver_result = fit_driver_model(
            price_df["pct_change"].iloc[:t], driver_df.iloc[:t]
        )
        if driver_result is not None:
            driver_pct = driver_result.forecast_pct_change
            residual_result = fit_residual_model(
                price_df.iloc[:t], driver_df.iloc[:t], driver_result.fitted_pct_change
            )
            if residual_result is not None:
                ml_pct = driver_pct + residual_result.forecast_residual_pct

        folds.append(
            {
                "prev_price": prev_price,
                "actual_price": actual_price,
                "actual_pct": actual_pct,
                "baseline_pct": baseline_pct,
                "driver_pct": driver_pct,
                "ml_pct": ml_pct,
            }
        )
    return folds


def _metrics_for_candidate(folds: list[dict], key: str) -> dict | None:
    usable = [f for f in folds if f[key] is not None]
    if not usable:
        return None
    errors_price = []
    errors_pct = []
    directional_hits = 0
    for f in usable:
        predicted_price = f["prev_price"] * (1 + f[key])
        errors_price.append(predicted_price - f["actual_price"])
        errors_pct.append(f[key] - f["actual_pct"])
        if np.sign(f[key]) == np.sign(f["actual_pct"]) or (f[key] == 0 and f["actual_pct"] == 0):
            directional_hits += 1

    errors_price = np.array(errors_price)
    actual_prices = np.array([f["actual_price"] for f in usable])
    mae = float(np.mean(np.abs(errors_price)))
    rmse = float(np.sqrt(np.mean(errors_price**2)))
    mape = float(np.mean(np.abs(errors_price) / actual_prices) * 100)
    directional_accuracy = directional_hits / len(usable)
    return {
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "directional_accuracy": directional_accuracy,
        "n_folds": len(usable),
        "pct_errors": errors_pct,
    }


def candidate_metrics(folds: list[dict]) -> dict[str, dict | None]:
    return {
        "baseline": _metrics_for_candidate(folds, "baseline_pct"),
        "driver": _metrics_for_candidate(folds, "driver_pct"),
        "ml": _metrics_for_candidate(folds, "ml_pct"),
    }
