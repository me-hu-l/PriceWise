"""Economically interpretable driver model (roadmap section 8.2).

price_pct_change = intercept + sum(beta_i * driver_i_pct_change) + error,
fit with Ridge regression (L2 regularization keeps betas stable with few
monthly observations and correlated drivers).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge


@dataclass
class DriverModelResult:
    driver_names: list[str]
    betas: dict[str, float]
    intercept: float
    fitted_pct_change: np.ndarray  # in-sample fitted values, aligned to training rows
    projected_driver_changes: dict[str, float]  # next-period projection per driver
    forecast_pct_change: float


def _project_next_driver_changes(driver_df: pd.DataFrame, momentum_window: int = 3) -> dict[str, float]:
    """Naive momentum projection: mean of the last `momentum_window` monthly pct changes."""
    window = min(momentum_window, len(driver_df))
    if window == 0:
        return {col: 0.0 for col in driver_df.columns}
    return {col: float(driver_df[col].tail(window).mean()) for col in driver_df.columns}


def fit_driver_model(
    price_pct_change: pd.Series,
    driver_pct_change: pd.DataFrame,
    projected_driver_changes: dict[str, float] | None = None,
) -> DriverModelResult | None:
    """Fit on rows [1:] of both series (row 0 has no pct_change). Returns None if
    there are no relevant drivers or too few rows to fit anything meaningful."""
    if driver_pct_change.shape[1] == 0 or len(price_pct_change) < 3:
        return None

    y = price_pct_change.iloc[1:].reset_index(drop=True)
    X = driver_pct_change.iloc[1 : len(y) + 1].reset_index(drop=True).fillna(0.0)

    model = Ridge(alpha=1.0)
    model.fit(X.values, y.values)

    fitted = model.predict(X.values)
    projected = _project_next_driver_changes(X)
    if projected_driver_changes:
        projected.update(
            {
                name: float(value)
                for name, value in projected_driver_changes.items()
                if name in projected
            }
        )
    forecast_pct_change = float(model.intercept_) + sum(
        model.coef_[i] * projected[col] for i, col in enumerate(X.columns)
    )

    return DriverModelResult(
        driver_names=list(X.columns),
        betas={col: float(model.coef_[i]) for i, col in enumerate(X.columns)},
        intercept=float(model.intercept_),
        fitted_pct_change=fitted,
        projected_driver_changes=projected,
        forecast_pct_change=forecast_pct_change,
    )


def driver_contributions(result: DriverModelResult) -> list[dict]:
    """One row per driver: contribution_value = beta * projected_change, ranked by magnitude."""
    rows = []
    for name in result.driver_names:
        beta = result.betas[name]
        change = result.projected_driver_changes[name]
        rows.append(
            {
                "driver_name": name,
                "contribution_value": beta * change,
                "direction": "POSITIVE" if beta * change >= 0 else "NEGATIVE",
            }
        )
    total_abs = sum(abs(r["contribution_value"]) for r in rows) or 1.0
    rows.sort(key=lambda r: abs(r["contribution_value"]), reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
        row["contribution_pct"] = 100.0 * abs(row["contribution_value"]) / total_abs
    return rows
