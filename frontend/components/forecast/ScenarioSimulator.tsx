"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { MaterialDriverHistory, ScenarioComparison, ScenarioForecast } from "@/lib/types";

function ForecastSnapshot({ title, snapshot }: { title: string; snapshot?: ScenarioForecast }) {
  if (!snapshot) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        {title} data is unavailable.
      </div>
    );
  }

  return (
    <div className="rounded-md border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <h4 className="text-sm font-semibold text-slate-800">{title}</h4>
        <span className="text-xs font-semibold text-slate-600">{snapshot.recommendation_action}</span>
      </div>
      <p className="mt-3 text-2xl font-semibold text-slate-900">{snapshot.point_forecast.toLocaleString()}</p>
      <p className="text-xs text-slate-500">{snapshot.direction} · range {snapshot.lower_bound.toLocaleString()} - {snapshot.upper_bound.toLocaleString()}</p>
      <p className="mt-2 text-sm font-medium text-slate-700">Confidence {snapshot.confidence_score.toFixed(0)}/100</p>
      <p className="mt-2 text-xs text-slate-600">{snapshot.recommendation_reason}</p>
      {Object.keys(snapshot.driver_weights).length > 0 && (
        <p className="mt-2 text-[11px] text-slate-500">
          Model mix: {Object.entries(snapshot.driver_weights).map(([model, weight]) => `${model} ${(weight * 100).toFixed(0)}%`).join(" · ")}
        </p>
      )}
      <div className="mt-3 space-y-1 border-t border-slate-100 pt-2">
        {snapshot.contributions.slice(0, 4).map((row) => (
          <div key={row.label} className="flex justify-between gap-2 text-xs text-slate-600">
            <span>{row.label}</span>
            <span className="font-medium">{row.contribution_value >= 0 ? "+" : ""}{(row.contribution_value * 100).toFixed(2)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function RecommendationComparison({ comparison }: { comparison: ScenarioComparison }) {
  const options = [
    { title: "Normal forecast", snapshot: comparison.normal },
    { title: "What-if scenario", snapshot: comparison.scenario },
  ];

  return (
    <div className="mt-4 border-t border-slate-200 pt-4 lg:col-span-2">
      <h4 className="text-sm font-semibold text-slate-800">Recommendation comparison</h4>
      <div className="mt-3 grid gap-3 lg:grid-cols-2">
        {options.map(({ title, snapshot }) => (
          <div key={title} className="rounded-md border border-slate-200 bg-white p-3">
            <p className="text-xs font-medium text-slate-500">{title}</p>
            <p className="mt-1 text-base font-semibold text-slate-900">
              {snapshot.recommendation_action}
              <span className="text-xs font-normal text-slate-500"> · {snapshot.recommendation_duration}</span>
            </p>
            <p className="mt-1 text-sm font-medium text-slate-900">
              Conviction {snapshot.recommendation_conviction.toFixed(0)}%
            </p>
            <div className="mt-3 grid grid-cols-3 gap-2 border-y border-slate-100 py-3 text-center">
              <div>
                <p className="text-xs text-slate-500">Forecast</p>
                <p className="text-sm font-semibold text-slate-900">
                  {snapshot.forecast_change_pct >= 0 ? "+" : ""}{snapshot.forecast_change_pct.toFixed(1)}%
                </p>
                <p className="text-xs text-slate-500">{snapshot.direction}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Confidence</p>
                <p className="text-sm font-semibold text-slate-900">{snapshot.confidence_score.toFixed(0)}/100</p>
                <p className="text-xs text-slate-500">forecast score</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Supply risk</p>
                <p className="text-sm font-semibold text-slate-900">{snapshot.supply_risk}</p>
                <p className="text-xs text-slate-500">{snapshot.supply_risk_factors.length ? "constrained" : "manageable"}</p>
              </div>
            </div>
            <p className="mt-3 text-xs leading-5 text-slate-600">Decision logic: {snapshot.decision_rule}</p>
            <p className="mt-2 text-xs leading-5 text-slate-600">{snapshot.recommendation_reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ScenarioSimulator({ materialId, histories }: { materialId: number; histories: MaterialDriverHistory[] }) {
  const [expanded, setExpanded] = useState(true);
  const [changes, setChanges] = useState<Record<string, number>>(
    Object.fromEntries(histories.map((history) => [history.driver_name, history.projected_value && history.observations.length ? history.projected_value / history.observations[history.observations.length - 1].value - 1 : 0]))
  );
  const [comparison, setComparison] = useState<ScenarioComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      setComparison(await api.runScenario(materialId, changes));
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Scenario could not be calculated.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-slate-50 p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-800">What-if driver simulator</h3>
          <p className="mt-1 text-xs text-slate-500">Set each driver&apos;s next-month change, then compare it with the normal forecast.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setExpanded((value) => !value)}
            aria-expanded={expanded}
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100"
          >
            {expanded ? "Hide simulator" : "Show simulator"}
          </button>
          <button type="button" onClick={run} disabled={loading || histories.length === 0} className="rounded-md bg-slate-900 px-3 py-2 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50">
            {loading ? "Calculating..." : "Run scenario"}
          </button>
        </div>
      </div>
      {expanded && <>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        {histories.map((history) => {
          const value = changes[history.driver_name] ?? 0;
          return (
            <label key={history.driver_id} className="rounded-md border border-slate-200 bg-white p-3">
              <div className="flex justify-between gap-3 text-xs">
                <span className="font-medium text-slate-700">{history.driver_name}</span>
                <span className="font-semibold text-slate-900">{value >= 0 ? "+" : ""}{(value * 100).toFixed(1)}%</span>
              </div>
              <input type="range" min="-0.2" max="0.2" step="0.005" value={value} onChange={(event) => setChanges((current) => ({ ...current, [history.driver_name]: Number(event.target.value) }))} className="mt-2 w-full accent-teal-700" />
              <div className="mt-1 flex justify-between text-[10px] text-slate-400"><span>-20%</span><span>0%</span><span>+20%</span></div>
            </label>
          );
        })}
      </div>
      {error && <p className="mt-3 text-xs text-red-700">{error}</p>}
      {comparison && (
        <div className="mt-5 grid gap-4 border-t border-slate-200 pt-4 lg:grid-cols-2">
          <ForecastSnapshot title="Normal forecast (same model)" snapshot={comparison.normal} />
          <ForecastSnapshot title="What-if scenario" snapshot={comparison.scenario} />
          <RecommendationComparison comparison={comparison} />
        </div>
      )}
      </>}
    </section>
  );
}
