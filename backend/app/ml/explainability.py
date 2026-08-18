"""Combined economic driver + ML residual + market-event explanation (roadmap section 12).

SHAP decomposes the ML residual component specifically; it is never the sole
explanation. Powers the forecast waterfall chart and the "Why?" panel. Rule-based
(no LLM needed), consistent with "system must work without LLM access".
"""

from __future__ import annotations

ML_RESIDUAL_DRIVER_NAME = "ML Residual"


def shap_breakdown_for_ml_component(residual_result) -> list[dict]:
    """Best-effort SHAP decomposition of the ML residual's engineered features.
    Returns [] if shap isn't available or fails for any reason — the ML residual
    total is still shown, just without this extra sub-breakdown."""
    if residual_result is None:
        return []
    try:
        import shap

        explainer = shap.TreeExplainer(residual_result.model)
        shap_values = explainer.shap_values(residual_result.latest_features)[0]
        rows = [
            {"feature": name, "shap_value": float(value)}
            for name, value in zip(residual_result.feature_names, shap_values)
        ]
        rows.sort(key=lambda r: abs(r["shap_value"]), reverse=True)
        return rows[:5]
    except Exception:
        return []


def build_waterfall(driver_contributions: list[dict], ml_pct_change: float | None) -> list[dict]:
    """Driver contributions + a single "ML Residual" line, ranked and with each
    row's share of the total explained move (contribution_pct sums to ~100)."""
    rows = [
        {
            "label": row["driver_name"],
            "contribution_value": row["contribution_value"],
            "direction": row["direction"],
        }
        for row in driver_contributions
    ]
    if ml_pct_change is not None and abs(ml_pct_change) > 1e-6:
        driver_sum = sum(r["contribution_value"] for r in driver_contributions)
        ml_only = ml_pct_change - driver_sum
        rows.append(
            {
                "label": ML_RESIDUAL_DRIVER_NAME,
                "contribution_value": ml_only,
                "direction": "POSITIVE" if ml_only >= 0 else "NEGATIVE",
            }
        )

    total_abs = sum(abs(r["contribution_value"]) for r in rows) or 1.0
    rows.sort(key=lambda r: abs(r["contribution_value"]), reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
        row["contribution_pct"] = 100.0 * abs(row["contribution_value"]) / total_abs
    return rows


def build_narrative(
    material_name: str, forecast_pct_change: float, waterfall: list[dict], data_mode: str
) -> str:
    direction_word = "increase" if forecast_pct_change >= 0 else "decrease"
    top = sorted(waterfall, key=lambda r: abs(r["contribution_value"]), reverse=True)[:3]
    top_desc = ", ".join(f"{r['label']} ({r['contribution_value'] * 100:+.1f}%)" for r in top)
    narrative = (
        f"{material_name} is forecast to {direction_word} {abs(forecast_pct_change) * 100:.1f}% "
        f"next month. Largest contributors: {top_desc}."
    )
    if data_mode in ("LOW_DATA", "LIMITED_DATA"):
        narrative += (
            f" This material has {data_mode.replace('_', ' ').lower()} — "
            "the forecast leans more heavily on the driver model than historical ML patterns."
        )
    return narrative
