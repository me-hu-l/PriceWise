"""Phase 2 TODO: driver model + ML residual model + ensemble (roadmap section 8).

Phase 1 deliberately does not fabricate forecasts. Callers should render the
returned NotImplementedResponse instead of a point/range forecast.
"""

from app.schemas.common import NotImplementedResponse


def get_forecast(material_id: int) -> NotImplementedResponse:
    return NotImplementedResponse(
        feature="forecast",
        phase="Phase 2 — Core intelligence",
        reason="Driver model / ML residual / ensemble forecasting is not implemented yet.",
    )


def get_forecast_explanation(material_id: int) -> NotImplementedResponse:
    return NotImplementedResponse(
        feature="forecast_explanation",
        phase="Phase 2 — Core intelligence",
        reason="SHAP + driver contribution waterfall requires a trained forecast first.",
    )
