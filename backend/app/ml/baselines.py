"""Benchmark forecast models (roadmap section 8.1) — the floor of the ensemble.

Each function takes a 1-D sequence of historical prices (oldest first) and
returns a one-step-ahead forecast price. Kept dependency-free (no statsmodels).
"""

from __future__ import annotations


def last_value(prices: list[float]) -> float:
    return prices[-1]


def moving_average(prices: list[float], window: int = 3) -> float:
    window = min(window, len(prices))
    return sum(prices[-window:]) / window


def exponential_smoothing(prices: list[float], alpha: float = 0.3) -> float:
    """Simple (non-seasonal) exponential smoothing, recursively applied in-sample."""
    level = prices[0]
    for p in prices[1:]:
        level = alpha * p + (1 - alpha) * level
    return level


def seasonal_naive(prices: list[float], season_length: int = 12) -> float:
    if len(prices) > season_length:
        return prices[-season_length]
    return last_value(prices)


def all_baselines(prices: list[float]) -> dict[str, float]:
    return {
        "last_value": last_value(prices),
        "moving_average": moving_average(prices),
        "exponential_smoothing": exponential_smoothing(prices),
        "seasonal_naive": seasonal_naive(prices),
    }
