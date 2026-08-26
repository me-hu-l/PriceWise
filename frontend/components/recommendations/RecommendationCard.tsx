import type { RecommendationResponse } from "@/lib/types";
import { isInsufficientData } from "@/components/forecast/ForecastCard";

export function RecommendationCard({ recommendation }: { recommendation: RecommendationResponse }) {
  if (isInsufficientData(recommendation)) {
    return (
      <section className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-5">
        <h3 className="mb-1 text-sm font-semibold text-slate-500">Recommendation</h3>
        <p className="text-sm text-slate-400">{recommendation.reason}</p>
      </section>
    );
  }

  const direction = recommendation.forecast_change_pct >= 0 ? "increase" : "decrease";

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-700">Recommendation</h3>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
          {recommendation.action}
        </span>
      </div>
      <p className="text-sm font-medium text-slate-900">
        Conviction {recommendation.conviction.toFixed(0)}% · {recommendation.recommended_duration}
      </p>
      <div className="mt-3 grid grid-cols-3 gap-2 border-y border-slate-100 py-3 text-center">
        <div>
          <p className="text-xs text-slate-500">Forecast</p>
          <p className="text-sm font-semibold text-slate-900">
            {recommendation.forecast_change_pct >= 0 ? "+" : ""}
            {recommendation.forecast_change_pct.toFixed(1)}%
          </p>
          <p className="text-xs text-slate-500">{recommendation.forecast_direction}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Confidence</p>
          <p className="text-sm font-semibold text-slate-900">{recommendation.confidence_score.toFixed(0)}/100</p>
          <p className="text-xs text-slate-500">forecast score</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Supply risk</p>
          <p className="text-sm font-semibold text-slate-900">{recommendation.supply_risk}</p>
          <p className="text-xs text-slate-500">{recommendation.supply_risk_factors.length ? "constrained" : "manageable"}</p>
        </div>
      </div>
      <p className="mt-3 text-sm font-medium text-slate-800">
        Decision logic: prices are forecast to {direction} by {Math.abs(recommendation.forecast_change_pct).toFixed(1)}%; {recommendation.decision_rule.toLowerCase()}
      </p>
      <p className="mt-2 text-sm text-slate-600">{recommendation.reason}</p>
      <ul className="mt-4 space-y-2 border-t border-slate-100 pt-3 text-xs text-slate-500">
        {recommendation.evidence.map((item) => (
          <li key={item.id}>
            <span className="font-medium text-slate-700">{item.title}:</span> {item.description}
          </li>
        ))}
      </ul>
    </section>
  );
}