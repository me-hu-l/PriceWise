import pytest

from app.ml import backtesting, preprocessing
from app.ml.driver_model import fit_driver_model


def test_driver_model_recovers_positive_relationship(db_session, material_with_history):
    """The fixture constructs price ~ 0.8 * driver_pct_change + noise, so the
    fitted beta for the (only) driver must come out positive."""
    price_df = preprocessing.build_price_series(db_session, material_with_history.id)
    dates = price_df["date"].tolist()
    driver_df = preprocessing.build_driver_pct_change_matrix(
        db_session, material_with_history.id, dates
    )

    result = fit_driver_model(price_df["pct_change"], driver_df)

    assert result is not None
    assert len(result.betas) == 1
    beta = next(iter(result.betas.values()))
    assert beta > 0


def test_walk_forward_backtest_uses_no_future_data(db_session, material_with_history):
    """Perturbing only the final rows must leave earlier folds' predictions unchanged."""
    price_df = preprocessing.build_price_series(db_session, material_with_history.id)
    dates = price_df["date"].tolist()
    driver_df = preprocessing.build_driver_pct_change_matrix(
        db_session, material_with_history.id, dates
    )

    folds_original = backtesting.run_walk_forward(price_df, driver_df)

    perturbed_price_df = price_df.copy()
    perturbed_price_df.loc[perturbed_price_df.index[-3:], "price"] *= 5
    perturbed_price_df["pct_change"] = perturbed_price_df["price"].pct_change()
    perturbed_driver_df = driver_df.copy()
    perturbed_driver_df.iloc[-3:] = perturbed_driver_df.iloc[-3:] * 5

    folds_perturbed = backtesting.run_walk_forward(perturbed_price_df, perturbed_driver_df)

    assert len(folds_original) == len(folds_perturbed)
    safe_fold_count = max(0, len(folds_original) - 4)  # leave a safety margin
    for i in range(safe_fold_count):
        assert folds_original[i]["baseline_pct"] == pytest.approx(
            folds_perturbed[i]["baseline_pct"]
        )
        if folds_original[i]["driver_pct"] is not None:
            assert folds_original[i]["driver_pct"] == pytest.approx(
                folds_perturbed[i]["driver_pct"], rel=1e-6
            )
