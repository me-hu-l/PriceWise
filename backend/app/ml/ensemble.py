"""Weighted ensemble of baseline + driver + ML residual (roadmap section 8.4).

Weights come from walk-forward backtest performance (inverse MAE), never a
random split. Falls back to fixed, driver-model-favoring weights (roadmap
section 10) when there isn't enough history to backtest at all.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.ml import backtesting, baselines
from app.ml.driver_model import driver_contributions, fit_driver_model
from app.ml.residual_model import fit_residual_model

DISAGREEMENT_MEDIUM_THRESHOLD = 0.01  # 1 percentage point spread
DISAGREEMENT_HIGH_THRESHOLD = 0.03  # 3 percentage points spread
INTERVAL_Z = 1.28  # ~80% two-sided normal interval
DRIVER_WEIGHT_BOOST = 0.25


@dataclass
class EnsembleResult:
    ensemble_pct_change: float
    baseline_pct_change: float | None
    driver_pct_change: float | None
    ml_pct_change: float | None
    disagreement_level: str
    weights: dict[str, float]
    contributions: list[dict]
    backtest_metrics: dict
    interval_std_pct: float
    residual_result: object | None = None


def _fallback_weights(driver_available: bool, driver_weight_boost: float = 0.0) -> dict[str, float]:
    """No backtest possible (too little history) — favor the driver model per section 10."""
    if driver_available:
        driver_weight = min(0.95, 0.7 + driver_weight_boost)
        return {"baseline": 1.0 - driver_weight, "driver": driver_weight, "ml": 0.0}
    return {"baseline": 1.0, "driver": 0.0, "ml": 0.0}


def _weights_from_backtest(metrics: dict[str, dict | None]) -> dict[str, float]:
    inverse_mae = {}
    for key, m in metrics.items():
        if m is not None and m["mae"] > 0:
            inverse_mae[key] = 1.0 / m["mae"]
        elif m is not None:
            inverse_mae[key] = 1.0 / 1e-6  # near-perfect backtest fit
    total = sum(inverse_mae.values())
    if total == 0:
        return _fallback_weights(driver_available=metrics.get("driver") is not None)
    return {k: v / total for k, v in inverse_mae.items()}


def _disagreement_level(pct_changes: list[float]) -> str:
    if len(pct_changes) < 2:
        return "LOW"
    spread = max(pct_changes) - min(pct_changes)
    if spread >= DISAGREEMENT_HIGH_THRESHOLD:
        return "HIGH"
    if spread >= DISAGREEMENT_MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def build_ensemble(
    price_df: pd.DataFrame,
    driver_df: pd.DataFrame,
    projected_driver_changes: dict[str, float] | None = None,
    driver_weight_boost: float = 0.0,
) -> EnsembleResult:
    prices = price_df["price"].tolist()
    baseline_pct = baselines.exponential_smoothing(prices) / prices[-1] - 1

    driver_result = fit_driver_model(
        price_df["pct_change"], driver_df, projected_driver_changes=projected_driver_changes
    )
    driver_pct = driver_result.forecast_pct_change if driver_result else None
    contributions = driver_contributions(driver_result) if driver_result else []

    ml_pct = None
    residual_result = None
    if driver_result is not None:
        residual_result = fit_residual_model(price_df, driver_df, driver_result.fitted_pct_change)
        if residual_result is not None:
            ml_pct = driver_pct + residual_result.forecast_residual_pct

    folds = backtesting.run_walk_forward(price_df, driver_df)
    metrics = backtesting.candidate_metrics(folds)

    if folds and any(m is not None for m in metrics.values()):
        weights = _weights_from_backtest(metrics)
    else:
        weights = _fallback_weights(
            driver_available=driver_result is not None,
            driver_weight_boost=driver_weight_boost,
        )

    if driver_weight_boost and driver_result is not None and folds:
        weights["driver"] = weights.get("driver", 0.0) + driver_weight_boost
        total_weight = sum(weights.values()) or 1.0
        weights = {key: value / total_weight for key, value in weights.items()}

    candidates = {"baseline": baseline_pct, "driver": driver_pct, "ml": ml_pct}
    available = {k: v for k, v in candidates.items() if v is not None}
    active_weights = {k: weights.get(k, 0.0) for k in available}
    weight_sum = sum(active_weights.values()) or 1.0
    active_weights = {k: w / weight_sum for k, w in active_weights.items()}

    ensemble_pct = sum(available[k] * active_weights[k] for k in available)
    disagreement = _disagreement_level(list(available.values()))

    # Approximate prediction-interval width from backtest ensemble errors (fold-by-fold,
    # reusing the same weights — a standard practical simplification, documented).
    fold_errors = []
    for f in folds:
        fold_candidates = {
            "baseline": f["baseline_pct"],
            "driver": f["driver_pct"],
            "ml": f["ml_pct"],
        }
        fold_available = {k: v for k, v in fold_candidates.items() if v is not None}
        if not fold_available:
            continue
        fold_weight_sum = sum(weights.get(k, 0.0) for k in fold_available) or 1.0
        fold_pred = sum(
            fold_available[k] * weights.get(k, 0.0) / fold_weight_sum for k in fold_available
        )
        fold_errors.append(fold_pred - f["actual_pct"])

    interval_std_pct = float(np.std(fold_errors)) if len(fold_errors) >= 2 else abs(ensemble_pct) * 0.5 + 0.02

    return EnsembleResult(
        ensemble_pct_change=ensemble_pct,
        baseline_pct_change=baseline_pct,
        driver_pct_change=driver_pct,
        ml_pct_change=ml_pct,
        disagreement_level=disagreement,
        weights=active_weights,
        contributions=contributions,
        backtest_metrics=metrics,
        interval_std_pct=interval_std_pct,
        residual_result=residual_result,
    )
