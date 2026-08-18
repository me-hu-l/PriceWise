"""Five-component confidence formula (roadmap section 13).

overall = 0.20*data + 0.25*driver + 0.25*model + 0.15*market + 0.15*stability,
clamped to 0-100. Weights are configurable via app.core.config.Settings. This
is a prototype decision-support heuristic, not a validated probability — the
UI must call it "forecast confidence score", never "probability correct".
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings

DATA_MODE_SCORES = {
    "LOW_DATA": 35.0,
    "LIMITED_DATA": 55.0,
    "MODERATE": 75.0,
    "STRONG": 90.0,
}

DISAGREEMENT_STABILITY_SCORES = {"LOW": 85.0, "MEDIUM": 65.0, "HIGH": 40.0}


@dataclass
class ConfidenceResult:
    data_score: float
    driver_score: float
    model_score: float
    market_score: float
    stability_score: float
    overall_score: float
    explanation: str


def classify_data_mode(n_observations: int, settings: Settings) -> str:
    if n_observations < settings.low_data_max_observations:
        return "LOW_DATA"
    if n_observations < settings.limited_data_max_observations:
        return "LIMITED_DATA"
    if n_observations < settings.moderate_data_max_observations:
        return "MODERATE"
    return "STRONG"


def _driver_score(edge_strengths_confidences: list[tuple[float, float]]) -> float:
    if not edge_strengths_confidences:
        return 40.0  # no known drivers — weak explanatory basis
    avg = sum(s * c for s, c in edge_strengths_confidences) / len(edge_strengths_confidences)
    return max(0.0, min(100.0, avg * 100))


def _model_score(best_candidate_metrics: dict | None) -> float:
    if best_candidate_metrics is None:
        return 50.0  # no backtest available — neutral default
    directional = best_candidate_metrics["directional_accuracy"]
    mape = best_candidate_metrics["mape"]
    mape_penalty = min(40.0, mape)  # cap penalty so a single bad fold can't zero it out
    score = 60.0 + 40.0 * directional - mape_penalty * 0.5
    return max(0.0, min(100.0, score))


def _market_score(event_confidences: list[float], directions: list[str]) -> float:
    if not event_confidences:
        return 60.0  # no active signals — moderate, neither boosts nor penalizes heavily
    avg_confidence = sum(event_confidences) / len(event_confidences)
    unique_directions = set(d for d in directions if d != "NEUTRAL")
    contradictory = len(unique_directions) > 1
    score = avg_confidence
    if contradictory:
        score -= 20.0
    return max(0.0, min(100.0, score))


def compute_confidence(
    settings: Settings,
    n_observations: int,
    edge_strengths_confidences: list[tuple[float, float]],
    best_candidate_metrics: dict | None,
    event_confidences: list[float],
    event_directions: list[str],
    disagreement_level: str,
    regime_change_detected: bool,
) -> ConfidenceResult:
    data_mode = classify_data_mode(n_observations, settings)
    data_score = DATA_MODE_SCORES[data_mode]
    driver_score = _driver_score(edge_strengths_confidences)
    model_score = _model_score(best_candidate_metrics)
    market_score = _market_score(event_confidences, event_directions)
    stability_score = DISAGREEMENT_STABILITY_SCORES[disagreement_level]
    if regime_change_detected:
        stability_score = max(0.0, stability_score - 20.0)

    overall = (
        settings.confidence_weight_data * data_score
        + settings.confidence_weight_driver * driver_score
        + settings.confidence_weight_model * model_score
        + settings.confidence_weight_market * market_score
        + settings.confidence_weight_stability * stability_score
    )
    overall = max(0.0, min(100.0, overall))

    explanation_parts = [
        f"Data quality {data_score:.0f}/100 ({data_mode.replace('_', ' ').title()}, {n_observations} observations).",
        f"Driver strength {driver_score:.0f}/100 (avg. knowledge-graph relationship strength × confidence).",
        f"Model performance {model_score:.0f}/100 (walk-forward backtest directional accuracy/MAPE).",
        f"Market signals {market_score:.0f}/100 ({'no active events' if not event_confidences else 'based on related market event confidence/agreement'}).",
        f"Stability {stability_score:.0f}/100 (model disagreement: {disagreement_level}"
        + (", ⚠ regime change detected" if regime_change_detected else "")
        + ").",
    ]
    explanation = " ".join(explanation_parts)

    return ConfidenceResult(
        data_score=data_score,
        driver_score=driver_score,
        model_score=model_score,
        market_score=market_score,
        stability_score=stability_score,
        overall_score=overall,
        explanation=explanation,
    )
