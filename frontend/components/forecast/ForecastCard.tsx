import type { ForecastResponse, InsufficientDataResponse } from "@/lib/types";

export function isInsufficientData(x: unknown): x is InsufficientDataResponse {
  return !!x && typeof x === "object" && (x as any).status === "insufficient_data";
}

const directionStyle: Record<string, string> = {
  INCREASING: "text-red-600",
  DECREASING: "text-green-600",
  STABLE: "text-slate-500",
};

const dataModeLabel: Record<string, string> = {
  LOW_DATA: "LOW DATA MODE",
  LIMITED_DATA: "LIMITED DATA",
  MODERATE: "MODERATE DATA",
  STRONG: "STRONG DATA",
};

export function ForecastCard({ forecast }: { forecast: ForecastResponse }) {
  if (isInsufficientData(forecast)) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-5">
        <h3 className="mb-1 text-sm font-semibold text-slate-500">Forecast</h3>
        <p className="text-sm text-slate-400">{forecast.reason}</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">
          Forecast ({forecast.horizon}, target {new Date(forecast.target_date).toLocaleDateString("en-GB", { timeZone: "UTC" })})
        </h3>
        {forecast.data_mode && forecast.data_mode !== "STRONG" && (
          <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-800">
            {dataModeLabel[forecast.data_mode]}
          </span>
        )}
      </div>

      {forecast.regime_change_detected && (
        <div className="mb-3 rounded-md border border-amber-300 bg-amber-50 p-2 text-xs text-amber-800">
          ⚠ Market regime changed — historical model reliability may be reduced.
        </div>
      )}

      <p className={`text-2xl font-semibold ${directionStyle[forecast.direction] ?? "text-slate-900"}`}>
        {forecast.point_forecast.toLocaleString("en-US", { maximumFractionDigits: 2 })}
      </p>
      <p className="text-sm text-slate-500">
        Range {forecast.lower_bound.toLocaleString("en-US", { maximumFractionDigits: 2 })} –{" "}
        {forecast.upper_bound.toLocaleString("en-US", { maximumFractionDigits: 2 })} · {forecast.direction}
      </p>
      <p className="mt-2 text-sm font-medium text-slate-700">
        Confidence: {forecast.confidence_score.toFixed(0)}%
      </p>
    </div>
  );
}
