"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type {
  AnalyzedSupplierQuote,
  Forecast,
  Material,
  MaterialDriverHistory,
  ScenarioComparison,
  Supplier,
  SupplierQuote,
  SupplierQuoteBatchAnalysisResponse,
} from "@/lib/types";
import { SupplierDetailModal } from "./SupplierDetailModal";
import { AddSupplierModal } from "./AddSupplierModal";

interface SupplierIntelligenceProps {
  material: Material;
  baseForecast: Forecast | null;
  histories: MaterialDriverHistory[];
  initialSuppliers: Supplier[];
  initialQuotes: SupplierQuote[];
  allCatalogSuppliers: Supplier[];
  activeDriverChanges?: Record<string, number>;
  activeScenarioComparison?: ScenarioComparison | null;
  onScenarioChange?: (driverChanges: Record<string, number>, comparison: ScenarioComparison | null) => void;
}

export function SupplierIntelligence({
  material,
  baseForecast,
  histories,
  initialSuppliers,
  initialQuotes,
  allCatalogSuppliers,
  activeDriverChanges,
  activeScenarioComparison,
  onScenarioChange,
}: SupplierIntelligenceProps) {
  // Scenario state
  const [driverChanges, setDriverChanges] = useState<Record<string, number>>(
    activeDriverChanges ??
      Object.fromEntries(
        histories.map((h) => [
          h.driver_name,
          h.projected_value && h.observations.length
            ? h.projected_value / h.observations[h.observations.length - 1].value - 1
            : 0,
        ])
      )
  );
  const [scenarioComparison, setScenarioComparison] = useState<ScenarioComparison | null>(
    activeScenarioComparison ?? null
  );
  const [isScenarioLabOpen, setIsScenarioLabOpen] = useState(false);
  const [runningScenario, setRunningScenario] = useState(false);

  // Supplier list in comparison
  const [comparisonSuppliers, setSupplierList] = useState<Supplier[]>(initialSuppliers);
  const [customQuotes, setCustomQuotes] = useState<Record<number, number>>(() => {
    const map: Record<number, number> = {};
    for (const q of initialQuotes) {
      map[q.supplier_id] = q.quoted_price;
    }
    for (const s of initialSuppliers) {
      if (map[s.id] === undefined) {
        map[s.id] = material.current_price;
      }
    }
    return map;
  });

  // Batch Analysis state
  const [analysisResponse, setAnalysisResponse] =
    useState<SupplierQuoteBatchAnalysisResponse | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  // Modal states
  const [selectedDetailSupplier, setSelectedDetailSupplier] = useState<Supplier | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const isScenarioActive = useMemo(() => {
    return (
      scenarioComparison !== null &&
      Object.values(driverChanges).some((val) => Math.abs(val) > 0.0001)
    );
  }, [scenarioComparison, driverChanges]);

  const activeForecastPrice = useMemo(() => {
    if (isScenarioActive && scenarioComparison) {
      return scenarioComparison.scenario.point_forecast;
    }
    return baseForecast?.point_forecast ?? material.current_price;
  }, [isScenarioActive, scenarioComparison, baseForecast, material.current_price]);

  const activeForecastDirection = useMemo(() => {
    if (isScenarioActive && scenarioComparison) {
      return scenarioComparison.scenario.direction;
    }
    return baseForecast?.direction ?? "STABLE";
  }, [isScenarioActive, scenarioComparison, baseForecast]);

  const activeConfidenceScore = useMemo(() => {
    if (isScenarioActive && scenarioComparison) {
      return scenarioComparison.scenario.confidence_score;
    }
    return baseForecast?.confidence_score ?? 80;
  }, [isScenarioActive, scenarioComparison, baseForecast]);

  const activeLowerBound = useMemo(() => {
    if (isScenarioActive && scenarioComparison) {
      return scenarioComparison.scenario.lower_bound;
    }
    return baseForecast?.lower_bound ?? material.current_price * 0.95;
  }, [isScenarioActive, scenarioComparison, baseForecast, material.current_price]);

  const activeUpperBound = useMemo(() => {
    if (isScenarioActive && scenarioComparison) {
      return scenarioComparison.scenario.upper_bound;
    }
    return baseForecast?.upper_bound ?? material.current_price * 1.05;
  }, [isScenarioActive, scenarioComparison, baseForecast, material.current_price]);

  const runAnalysis = useCallback(
    async (
      currentSuppliers: Supplier[] = comparisonSuppliers,
      currentQuotesMap: Record<number, number> = customQuotes,
      currentChanges: Record<string, number> = driverChanges,
      activeScenarioComp: ScenarioComparison | null = scenarioComparison
    ) => {
      setAnalyzing(true);
      setAnalysisError(null);
      try {
        const quotesPayload = currentSuppliers.map((s) => ({
          supplier_id: s.id,
          quoted_price: currentQuotesMap[s.id] ?? material.current_price,
        }));

        const isCustomScenario =
          activeScenarioComp !== null &&
          Object.values(currentChanges).some((v) => Math.abs(v) > 0.0001);

        const response = await api.analyzeSupplierQuotes(
          material.id,
          quotesPayload,
          isCustomScenario ? currentChanges : null
        );
        setAnalysisResponse(response);
      } catch (err) {
        setAnalysisError(
          err instanceof Error ? err.message : "Failed to analyze supplier quotes."
        );
      } finally {
        setAnalyzing(false);
      }
    },
    [comparisonSuppliers, customQuotes, driverChanges, scenarioComparison, material.id, material.current_price]
  );

  useEffect(() => {
    runAnalysis();
  }, [runAnalysis]);

  async function handleRunScenario() {
    setRunningScenario(true);
    try {
      const comp = await api.runScenario(material.id, driverChanges);
      setScenarioComparison(comp);
      if (onScenarioChange) {
        onScenarioChange(driverChanges, comp);
      }
      await runAnalysis(comparisonSuppliers, customQuotes, driverChanges, comp);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : "Failed to run scenario.");
    } finally {
      setRunningScenario(false);
    }
  }

  function handleResetScenario() {
    const reset = Object.fromEntries(histories.map((h) => [h.driver_name, 0]));
    setDriverChanges(reset);
    setScenarioComparison(null);
    if (onScenarioChange) {
      onScenarioChange(reset, null);
    }
    runAnalysis(comparisonSuppliers, customQuotes, reset, null);
  }

  function handleAddSupplier(newSupplier: Supplier, initialPrice: number) {
    const updatedSuppliers = [...comparisonSuppliers, newSupplier];
    const updatedQuotes = { ...customQuotes, [newSupplier.id]: initialPrice };
    setSupplierList(updatedSuppliers);
    setCustomQuotes(updatedQuotes);
    runAnalysis(updatedSuppliers, updatedQuotes);
  }

  function handleQuoteChange(supplierId: number, newPrice: number) {
    setCustomQuotes((prev) => ({ ...prev, [supplierId]: newPrice }));
  }

  // Derived Decision Summary metrics
  const decisionSummary = useMemo(() => {
    if (!analysisResponse || analysisResponse.analyzed_quotes.length === 0) return null;
    const quotes = analysisResponse.analyzed_quotes;

    const bestCommercial = [...quotes].sort((a, b) => a.quoted_price - b.quoted_price)[0];
    const bestUnderScenario = [...quotes].sort(
      (a, b) => a.quote_vs_forecast_gap_pct - b.quote_vs_forecast_gap_pct
    )[0];
    const highestRisk = [...quotes].sort((a, b) => (b.risk_score ?? 0) - (a.risk_score ?? 0))[0];
    const strongestNegotiation = [...quotes].sort(
      (a, b) => b.unexplained_change_pct - a.unexplained_change_pct
    )[0];

    return {
      bestCommercial,
      bestUnderScenario,
      highestRisk,
      strongestNegotiation,
    };
  }, [analysisResponse]);

  return (
    <div className="space-y-6">
      {/* 1. ACTIVE MARKET / SCENARIO CONTEXT */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div className="flex items-center gap-3">
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${
                isScenarioActive
                  ? "bg-teal-100 text-teal-800 ring-1 ring-teal-600/30"
                  : "bg-slate-100 text-slate-700"
              }`}
            >
              {isScenarioActive ? "Custom Driver Scenario Active" : "Base Market Scenario"}
            </span>
            <p className="text-xs text-slate-500">
              {isScenarioActive
                ? "Active context reflects custom what-if driver assumptions."
                : "Active context reflects baseline ensemble model forecast."}
            </p>
          </div>

          <div className="flex items-center gap-2">
            {isScenarioActive && (
              <button
                type="button"
                onClick={handleResetScenario}
                className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100"
              >
                Reset to Base Scenario
              </button>
            )}
            <button
              type="button"
              onClick={() => setIsScenarioLabOpen((prev) => !prev)}
              className="rounded-md bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800"
            >
              {isScenarioLabOpen ? "Close Scenario Lab" : "Edit Scenario / Open Scenario Lab"}
            </button>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-5">
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] font-medium text-slate-500">Base Forecast</p>
            <p className="mt-1 text-base font-semibold text-slate-900">
              {material.currency} {(baseForecast?.point_forecast ?? material.current_price).toLocaleString()}
            </p>
            <p className="text-[10px] text-slate-400">{baseForecast?.direction ?? "STABLE"}</p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-teal-50/50 p-3 ring-1 ring-teal-700/10">
            <p className="text-[11px] font-medium text-teal-800">Active Forecast</p>
            <p className="mt-1 text-base font-bold text-teal-950">
              {material.currency} {activeForecastPrice.toLocaleString()}
            </p>
            <p className="text-[10px] font-medium text-teal-700">{activeForecastDirection}</p>
          </div>

          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] font-medium text-slate-500">Forecast Change</p>
            <p className="mt-1 text-base font-semibold text-slate-900">
              {material.current_price
                ? `${
                    (activeForecastPrice / material.current_price - 1) >= 0 ? "+" : ""
                  }${((activeForecastPrice / material.current_price - 1) * 100).toFixed(1)}%`
                : "0.0%"}
            </p>
            <p className="text-[10px] text-slate-400">vs current price</p>
          </div>

          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] font-medium text-slate-500">Forecast Range</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">
              {activeLowerBound.toLocaleString()} - {activeUpperBound.toLocaleString()}
            </p>
            <p className="text-[10px] text-slate-400">{material.currency} interval</p>
          </div>

          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] font-medium text-slate-500">Confidence Score</p>
            <p className="mt-1 text-base font-semibold text-slate-900">
              {activeConfidenceScore.toFixed(0)} / 100
            </p>
            <p className="text-[10px] text-slate-400">model certainty</p>
          </div>
        </div>

        {isScenarioActive && (
          <div className="mt-4 rounded-lg bg-teal-50/60 p-3 text-xs border border-teal-200/60">
            <span className="font-semibold text-teal-900">Active Driver Changes: </span>
            {Object.entries(driverChanges)
              .filter(([_, val]) => Math.abs(val) > 0.0001)
              .map(([driver, val]) => (
                <span key={driver} className="ml-2 font-medium text-teal-800">
                  {driver}: <span className="font-bold">{val >= 0 ? "+" : ""}{(val * 100).toFixed(1)}%</span>
                </span>
              ))}
          </div>
        )}

        {/* Expandable Scenario Driver Sliders */}
        {isScenarioLabOpen && (
          <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4">
            <h4 className="text-xs font-semibold text-slate-800">
              Adjust Driver Assumptions (Next-Month What-If Scenario)
            </h4>
            <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {histories.map((h) => {
                const val = driverChanges[h.driver_name] ?? 0;
                return (
                  <div key={h.driver_id} className="rounded-md border border-slate-200 bg-white p-2.5 text-xs">
                    <div className="flex justify-between font-medium">
                      <span className="text-slate-700">{h.driver_name}</span>
                      <span className="font-semibold text-slate-900">
                        {val >= 0 ? "+" : ""}{(val * 100).toFixed(1)}%
                      </span>
                    </div>
                    <input
                      type="range"
                      min="-0.2"
                      max="0.2"
                      step="0.005"
                      value={val}
                      onChange={(e) =>
                        setDriverChanges((curr) => ({
                          ...curr,
                          [h.driver_name]: Number(e.target.value),
                        }))
                      }
                      className="mt-1.5 w-full accent-teal-700"
                    />
                  </div>
                );
              })}
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={handleResetScenario}
                className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100"
              >
                Reset Drivers
              </button>
              <button
                type="button"
                onClick={handleRunScenario}
                disabled={runningScenario}
                className="inline-flex items-center gap-1.5 rounded-md bg-teal-800 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-900 disabled:opacity-50"
              >
                {runningScenario ? "Recalculating Scenario..." : "Apply Driver Scenario"}
              </button>
            </div>
          </div>
        )}
      </section>

      {/* 2. SUPPLIER INTELLIGENCE OVERVIEW */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Supplier Overview</h3>
            <p className="text-xs text-slate-500">
              Available suppliers for {material.name} ({material.material_code}). Click any row for details.
            </p>
          </div>
          <span className="text-xs font-medium text-slate-500">
            {comparisonSuppliers.length} suppliers listed
          </span>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 font-semibold text-slate-600 border-b border-slate-200">
              <tr>
                <th className="px-3 py-2.5">Supplier Name</th>
                <th className="px-3 py-2.5">Location</th>
                <th className="px-3 py-2.5">Qualification</th>
                <th className="px-3 py-2.5">Lead Time</th>
                <th className="px-3 py-2.5">Share of Supply</th>
                <th className="px-3 py-2.5">Risk Score</th>
                <th className="px-3 py-2.5">Baseline Quote</th>
                <th className="px-3 py-2.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {comparisonSuppliers.map((supplier) => {
                const baseline = initialQuotes.find((q) => q.supplier_id === supplier.id);
                const baselinePrice = baseline ? baseline.quoted_price : material.current_price;
                return (
                  <tr
                    key={supplier.id}
                    onClick={() => setSelectedDetailSupplier(supplier)}
                    className="cursor-pointer hover:bg-slate-50 transition-colors"
                  >
                    <td className="px-3 py-3 font-semibold text-slate-900">
                      {supplier.name}
                      <p className="text-[10px] font-mono text-slate-400 font-normal">
                        {supplier.supplier_code}
                      </p>
                    </td>
                    <td className="px-3 py-3 text-slate-600">{supplier.country ?? "Global"}</td>
                    <td className="px-3 py-3">
                      <span className="rounded bg-emerald-50 px-2 py-0.5 font-medium text-emerald-800 border border-emerald-200/50">
                        {supplier.qualification_status}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-slate-900">{supplier.lead_time_days ?? "—"} days</td>
                    <td className="px-3 py-3 font-medium text-slate-900">
                      {supplier.share_of_supply != null
                        ? `${(supplier.share_of_supply * 100).toFixed(0)}%`
                        : "—"}
                    </td>
                    <td className="px-3 py-3">
                      <span
                        className={`rounded px-2 py-0.5 font-semibold text-[11px] ${
                          (supplier.risk_score ?? 0) >= 70
                            ? "bg-red-50 text-red-800 border border-red-200"
                            : (supplier.risk_score ?? 0) >= 40
                            ? "bg-amber-50 text-amber-800 border border-amber-200"
                            : "bg-emerald-50 text-emerald-800 border border-emerald-200"
                        }`}
                      >
                        {supplier.risk_score != null ? `${supplier.risk_score.toFixed(0)}/100` : "Low"}
                      </span>
                    </td>
                    <td className="px-3 py-3 font-semibold text-slate-900">
                      {material.currency} {baselinePrice.toLocaleString()}
                    </td>
                    <td className="px-3 py-3 text-right">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedDetailSupplier(supplier);
                        }}
                        className="rounded border border-slate-300 bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-700 hover:bg-slate-100"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* 3. DYNAMIC QUOTE ANALYSIS TABLE */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Dynamic Quote Analysis</h3>
            <p className="text-xs text-slate-500">
              Evaluates supplier quotes against the active market forecast (
              <span className="font-semibold text-slate-800">
                {material.currency} {activeForecastPrice.toLocaleString()}
              </span>
              ) and active driver scenario.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setIsAddModalOpen(true)}
              className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100"
            >
              + Add Supplier to Comparison
            </button>
            <button
              type="button"
              onClick={() => runAnalysis()}
              disabled={analyzing}
              className="inline-flex items-center gap-1.5 rounded-md bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
            >
              {analyzing ? "Analyzing Quotes..." : "Analyze Quotes"}
            </button>
          </div>
        </div>

        {analysisError && <p className="mt-3 text-xs text-red-700">{analysisError}</p>}

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 font-semibold text-slate-600 border-b border-slate-200">
              <tr>
                <th className="px-3 py-2.5">Supplier</th>
                <th className="px-3 py-2.5">Quoted Price ({material.currency})</th>
                <th className="px-3 py-2.5">Active Forecast ({material.currency})</th>
                <th className="px-3 py-2.5">Quote vs Forecast Gap</th>
                <th className="px-3 py-2.5">Risk Level</th>
                <th className="px-3 py-2.5">Recommendation</th>
                <th className="px-3 py-2.5">Decision Logic & Guidance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {comparisonSuppliers.map((supplier) => {
                const analyzed = analysisResponse?.analyzed_quotes.find(
                  (a) => a.supplier_id === supplier.id
                );
                const currentPriceVal = customQuotes[supplier.id] ?? material.current_price;

                const gap = analyzed
                  ? analyzed.quote_vs_forecast_gap_pct
                  : ((currentPriceVal - activeForecastPrice) / activeForecastPrice) * 100;

                const rec = analyzed?.recommendation ?? "ANALYZING";

                return (
                  <tr key={supplier.id} className="hover:bg-slate-50">
                    <td className="px-3 py-3 font-semibold text-slate-900">
                      {supplier.name}
                      <p className="text-[10px] text-slate-400 font-normal">
                        {supplier.country ?? "Global"} · Lead time {supplier.lead_time_days ?? "—"}d
                      </p>
                    </td>

                    {/* 4. CUSTOM SUPPLIER QUOTE INPUT */}
                    <td className="px-3 py-3">
                      <div className="flex items-center gap-1">
                        <span className="text-slate-400">{material.currency}</span>
                        <input
                          type="number"
                          step="0.01"
                          value={currentPriceVal}
                          onChange={(e) =>
                            handleQuoteChange(supplier.id, Number(e.target.value))
                          }
                          className="w-28 rounded-md border border-slate-300 bg-white px-2 py-1 text-xs font-semibold text-slate-900 focus:border-teal-700 focus:outline-none"
                        />
                      </div>
                    </td>

                    <td className="px-3 py-3 font-semibold text-slate-900">
                      {material.currency} {activeForecastPrice.toLocaleString()}
                    </td>

                    <td className="px-3 py-3">
                      <span
                        className={`font-semibold ${
                          gap <= 0
                            ? "text-emerald-700"
                            : gap <= 3
                            ? "text-amber-700"
                            : "text-red-700"
                        }`}
                      >
                        {gap >= 0 ? "+" : ""}
                        {gap.toFixed(1)}%
                      </span>
                    </td>

                    <td className="px-3 py-3">
                      <span
                        className={`rounded px-2 py-0.5 font-semibold text-[10px] ${
                          (supplier.risk_score ?? 0) >= 70
                            ? "bg-red-50 text-red-800"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {(supplier.risk_score ?? 0) >= 70 ? "HIGH RISK" : "MANAGEABLE"}
                      </span>
                    </td>

                    {/* 6. RECOMMENDATION BEHAVIOR */}
                    <td className="px-3 py-3">
                      <span
                        className={`inline-block rounded-md px-2.5 py-1 text-xs font-bold ${
                          rec === "ACCEPT"
                            ? "bg-emerald-100 text-emerald-900"
                            : rec === "NEGOTIATE"
                            ? "bg-amber-100 text-amber-900"
                            : rec === "DUAL_SOURCE"
                            ? "bg-purple-100 text-purple-900"
                            : rec === "REJECT"
                            ? "bg-red-100 text-red-900"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {rec}
                      </span>
                    </td>

                    <td className="px-3 py-3 text-slate-600 max-w-sm">
                      <p className="text-[11px] leading-snug">
                        {analyzed?.recommendation_reason ?? "Evaluating supplier quote..."}
                      </p>
                      {analyzed?.guidance && (
                        <p className="mt-1 text-[10px] text-slate-500 italic">
                          💡 {analyzed.guidance}
                        </p>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* 7. DECISION SUMMARY */}
      {decisionSummary && (
        <section className="rounded-xl border border-slate-200 bg-gradient-to-r from-slate-900 to-slate-800 p-5 text-white shadow-sm">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Strategic Procurement Decision Summary
          </h3>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border border-slate-700/60 bg-slate-800/80 p-3.5">
              <p className="text-[11px] font-medium text-emerald-400">🏆 Best Commercial Option</p>
              <p className="mt-1.5 text-sm font-semibold text-white">
                {decisionSummary.bestCommercial.supplier_name}
              </p>
              <p className="mt-0.5 text-xs text-slate-300">
                Quote: {material.currency} {decisionSummary.bestCommercial.quoted_price.toLocaleString()}
              </p>
              <p className="mt-1 text-[10px] text-slate-400">
                Gap: {decisionSummary.bestCommercial.quote_vs_forecast_gap_pct >= 0 ? "+" : ""}
                {decisionSummary.bestCommercial.quote_vs_forecast_gap_pct.toFixed(1)}%
              </p>
            </div>

            <div className="rounded-lg border border-slate-700/60 bg-slate-800/80 p-3.5">
              <p className="text-[11px] font-medium text-teal-400">
                🎯 Best Quote Under Active Scenario
              </p>
              <p className="mt-1.5 text-sm font-semibold text-white">
                {decisionSummary.bestUnderScenario.supplier_name}
              </p>
              <p className="mt-0.5 text-xs text-slate-300">
                Recommendation: {decisionSummary.bestUnderScenario.recommendation}
              </p>
              <p className="mt-1 text-[10px] text-slate-400">
                Gap: {decisionSummary.bestUnderScenario.quote_vs_forecast_gap_pct >= 0 ? "+" : ""}
                {decisionSummary.bestUnderScenario.quote_vs_forecast_gap_pct.toFixed(1)}% vs active forecast
              </p>
            </div>

            <div className="rounded-lg border border-slate-700/60 bg-slate-800/80 p-3.5">
              <p className="text-[11px] font-medium text-amber-400">⚠️ Highest Supply Risk</p>
              <p className="mt-1.5 text-sm font-semibold text-white">
                {decisionSummary.highestRisk.supplier_name}
              </p>
              <p className="mt-0.5 text-xs text-slate-300">
                Risk Score: {decisionSummary.highestRisk.risk_score ?? "—"} / 100
              </p>
              <p className="mt-1 text-[10px] text-slate-400">
                Lead Time: {decisionSummary.highestRisk.lead_time_days ?? "—"} days
              </p>
            </div>

            <div className="rounded-lg border border-slate-700/60 bg-slate-800/80 p-3.5">
              <p className="text-[11px] font-medium text-blue-400">
                💬 Strongest Negotiation Opportunity
              </p>
              <p className="mt-1.5 text-sm font-semibold text-white">
                {decisionSummary.strongestNegotiation.supplier_name}
              </p>
              <p className="mt-0.5 text-xs text-slate-300">
                Unexplained Gap: {decisionSummary.strongestNegotiation.unexplained_change_pct >= 0 ? "+" : ""}
                {decisionSummary.strongestNegotiation.unexplained_change_pct.toFixed(1)}%
              </p>
              <p className="mt-1 text-[10px] text-slate-400">
                Anchor Target: {material.currency} {decisionSummary.strongestNegotiation.active_forecast_price.toLocaleString()}
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Modals */}
      <SupplierDetailModal
        supplier={selectedDetailSupplier}
        material={material}
        quotes={initialQuotes}
        onClose={() => setSelectedDetailSupplier(null)}
      />

      <AddSupplierModal
        isOpen={isAddModalOpen}
        material={material}
        allSuppliers={allCatalogSuppliers}
        existingSupplierIds={comparisonSuppliers.map((s) => s.id)}
        onAdd={handleAddSupplier}
        onClose={() => setIsAddModalOpen(false)}
      />
    </div>
  );
}
