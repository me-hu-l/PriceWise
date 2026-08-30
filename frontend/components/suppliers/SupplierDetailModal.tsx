"use client";

import type { Material, Supplier, SupplierQuote } from "@/lib/types";

export function SupplierDetailModal({
  supplier,
  material,
  quotes,
  onClose,
}: {
  supplier: Supplier | null;
  material: Material;
  quotes: SupplierQuote[];
  onClose: () => void;
}) {
  if (!supplier) return null;

  const supplierQuotes = quotes.filter((q) => q.supplier_id === supplier.id);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-900/50 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl rounded-xl border border-slate-200 bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between border-b border-slate-100 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-slate-900">{supplier.name}</h3>
              <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-mono font-medium text-slate-600">
                {supplier.supplier_code}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              {supplier.country ?? "Global"} · Qualification:{" "}
              <span className="font-semibold text-slate-700">{supplier.qualification_status}</span>
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            aria-label="Close detail modal"
          >
            <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] font-medium text-slate-500">Lead Time</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">
              {supplier.lead_time_days ?? "—"} days
            </p>
          </div>
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] font-medium text-slate-500">Share of Supply</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">
              {supplier.share_of_supply != null
                ? `${(supplier.share_of_supply * 100).toFixed(0)}%`
                : "—"}
            </p>
          </div>
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] font-medium text-slate-500">Source Type</p>
            <p
              className={`mt-1 text-sm font-semibold ${
                supplier.single_source ? "text-red-700" : "text-slate-900"
              }`}
            >
              {supplier.single_source ? "Single Source" : "Dual / Multi Source"}
            </p>
          </div>
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] font-medium text-slate-500">Risk Score</p>
            <p
              className={`mt-1 text-sm font-semibold ${
                (supplier.risk_score ?? 0) >= 70
                  ? "text-red-700"
                  : (supplier.risk_score ?? 0) >= 40
                  ? "text-amber-700"
                  : "text-emerald-700"
              }`}
            >
              {supplier.risk_score != null ? `${supplier.risk_score.toFixed(0)} / 100` : "—"}
            </p>
          </div>
        </div>

        <div className="mt-6">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Historical Quotes for {material.name} ({material.material_code})
          </h4>
          {supplierQuotes.length === 0 ? (
            <p className="mt-3 text-xs text-slate-500 italic">
              No historical quote entries recorded in database for this supplier and material.
            </p>
          ) : (
            <div className="mt-3 max-h-48 overflow-x-auto rounded-lg border border-slate-200">
              <table className="w-full text-left text-xs text-slate-700">
                <thead className="bg-slate-50 font-semibold text-slate-600 border-b border-slate-200">
                  <tr>
                    <th className="px-3 py-2">Quote Date</th>
                    <th className="px-3 py-2">Quoted Price</th>
                    <th className="px-3 py-2">Prev. Price</th>
                    <th className="px-3 py-2">Claimed %</th>
                    <th className="px-3 py-2">Reason / Note</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {supplierQuotes.map((q) => (
                    <tr key={q.id} className="hover:bg-slate-50">
                      <td className="px-3 py-2 font-medium">{q.quote_date}</td>
                      <td className="px-3 py-2 font-semibold text-slate-900">
                        {q.currency} {q.quoted_price.toLocaleString()}
                      </td>
                      <td className="px-3 py-2 text-slate-500">
                        {q.previous_price != null ? `${q.currency} ${q.previous_price.toLocaleString()}` : "—"}
                      </td>
                      <td className="px-3 py-2 font-medium">
                        {q.claimed_change_pct != null
                          ? `${q.claimed_change_pct >= 0 ? "+" : ""}${q.claimed_change_pct.toFixed(1)}%`
                          : "—"}
                      </td>
                      <td className="px-3 py-2 text-slate-500 truncate max-w-xs">{q.reason ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
