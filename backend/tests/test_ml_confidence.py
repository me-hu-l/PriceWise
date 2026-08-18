from app.core.config import Settings
from app.ml import confidence


def test_classify_data_mode_thresholds():
    settings = Settings()
    assert confidence.classify_data_mode(5, settings) == "LOW_DATA"
    assert confidence.classify_data_mode(15, settings) == "LIMITED_DATA"
    assert confidence.classify_data_mode(30, settings) == "MODERATE"
    assert confidence.classify_data_mode(60, settings) == "STRONG"


def test_compute_confidence_clamped_and_explainable():
    settings = Settings()
    result = confidence.compute_confidence(
        settings=settings,
        n_observations=60,
        edge_strengths_confidences=[(0.9, 0.9)],
        best_candidate_metrics={
            "mae": 1.0,
            "rmse": 1.2,
            "mape": 2.0,
            "directional_accuracy": 0.9,
            "n_folds": 10,
        },
        event_confidences=[90.0],
        event_directions=["UP"],
        disagreement_level="LOW",
        regime_change_detected=False,
    )
    assert 0 <= result.overall_score <= 100
    assert result.explanation  # must always be explainable, never a bare number


def test_regime_change_and_disagreement_reduce_stability():
    settings = Settings()
    stable = confidence.compute_confidence(
        settings=settings,
        n_observations=60,
        edge_strengths_confidences=[(0.9, 0.9)],
        best_candidate_metrics=None,
        event_confidences=[],
        event_directions=[],
        disagreement_level="LOW",
        regime_change_detected=False,
    )
    unstable = confidence.compute_confidence(
        settings=settings,
        n_observations=60,
        edge_strengths_confidences=[(0.9, 0.9)],
        best_candidate_metrics=None,
        event_confidences=[],
        event_directions=[],
        disagreement_level="HIGH",
        regime_change_detected=True,
    )
    assert unstable.stability_score < stable.stability_score
    assert unstable.overall_score < stable.overall_score
