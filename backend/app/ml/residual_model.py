"""LightGBM residual model (roadmap section 8.3).

Trains on residual = actual_pct_change - driver_model_fitted_pct_change, so the
ML component only explains what the economic driver model could not. Skipped
entirely (returns None) when there isn't enough history to train meaningfully —
this is what drives LOW_DATA materials to rely on the driver model + baseline.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor

MIN_OBSERVATIONS_FOR_ML = 18


@dataclass
class ResidualModelResult:
    forecast_residual_pct: float
    feature_names: list[str]
    latest_features: np.ndarray
    model: LGBMRegressor


def _build_features(price_df: pd.DataFrame, driver_df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=price_df.index)
    features["lag1_pct_change"] = price_df["pct_change"].shift(1)
    features["rolling_mean_3"] = price_df["pct_change"].rolling(3).mean()
    features["rolling_vol_3"] = price_df["pct_change"].rolling(3).std()
    features["month_sin"] = np.sin(2 * np.pi * pd.to_datetime(price_df["date"]).dt.month / 12)
    features["month_cos"] = np.cos(2 * np.pi * pd.to_datetime(price_df["date"]).dt.month / 12)
    for col in driver_df.columns:
        features[f"driver_{col}"] = driver_df[col].values
    return features


def fit_residual_model(
    price_df: pd.DataFrame, driver_df: pd.DataFrame, driver_fitted_pct_change: np.ndarray
) -> ResidualModelResult | None:
    n = len(price_df)
    if n < MIN_OBSERVATIONS_FOR_ML:
        return None

    features = _build_features(price_df, driver_df)
    # driver_fitted_pct_change is aligned to rows [1:], pad row 0 with 0
    driver_fitted_full = np.concatenate([[0.0], driver_fitted_pct_change])
    residual = price_df["pct_change"].fillna(0.0).values - driver_fitted_full

    train_mask = features.notna().all(axis=1)
    train_mask.iloc[0] = False  # row 0 has no pct_change / lag
    if train_mask.sum() < 6:
        return None

    X_train = features[train_mask].reset_index(drop=True)
    y_train = residual[train_mask.values]

    model = LGBMRegressor(
        n_estimators=50, max_depth=3, num_leaves=7, min_child_samples=2, verbose=-1
    )
    model.fit(X_train.values, y_train)

    latest_features = features.iloc[[-1]].fillna(0.0).values
    forecast_residual_pct = float(model.predict(latest_features)[0])

    return ResidualModelResult(
        forecast_residual_pct=forecast_residual_pct,
        feature_names=list(features.columns),
        latest_features=latest_features,
        model=model,
    )
