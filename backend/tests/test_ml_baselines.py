import pytest

from app.ml import baselines


def test_last_value():
    assert baselines.last_value([1.0, 2.0, 3.0]) == 3.0


def test_moving_average():
    assert baselines.moving_average([1.0, 2.0, 3.0], window=3) == pytest.approx(2.0)


def test_exponential_smoothing_stays_within_range():
    v = baselines.exponential_smoothing([10.0, 20.0, 30.0])
    assert 10.0 <= v <= 30.0


def test_seasonal_naive_falls_back_when_history_too_short():
    assert baselines.seasonal_naive([1.0, 2.0, 3.0], season_length=12) == 3.0


def test_seasonal_naive_uses_season_length_when_available():
    prices = [float(i) for i in range(1, 15)]  # 14 months
    assert baselines.seasonal_naive(prices, season_length=12) == prices[-12]
