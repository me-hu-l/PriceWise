"use client";

import { useMemo, useState } from "react";
import type { Material, Supplier } from "@/lib/types";

export function AddSupplierModal({
  isOpen,
  material,
  allSuppliers,
  existingSupplierIds,
  onAdd,
  onClose,
}: {
  isOpen: boolean;
  material: Material;
  allSuppliers: Supplier[];
  existingSupplierIds: number[];
  onAdd: (supplier: Supplier, customQuotePrice: number) => void;
  onClose: () => void;
}) {
  const [search, setSearch] = useState("");
  const [selectedSupplierId, setSelectedSupplierId] = useState<number | null>(null);
  const [customPrice, setCustomPrice] = useState<string>(material.current_price.toString());

  const availableSuppliers = useMemo(() => {
    return allSuppliers.filter((s) => !existingSupplierIds.includes(s.id));
  }, [allSuppliers, existingSupplierIds]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return availableSuppliers;
    return availableSuppliers.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.supplier_code.toLowerCase().includes(q) ||
        (s.country && s.country.toLowerCase().includes(q))
    );
  }, [availableSuppliers, search]);

  if (!isOpen) return null;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedSupplierId) return;
    const supplier = availableSuppliers.find((s) => s.id === selectedSupplierId);
    if (!supplier) return;
    const priceNum = Number(customPrice);
    onAdd(supplier, Number.isNaN(priceNum) || priceNum <= 0 ? material.current_price : priceNum);
    onClose();
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-900/50 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-lg rounded-xl border border-slate-200 bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Add Supplier to Comparison</h3>
            <p className="mt-1 text-xs text-slate-500">
              Select an existing supplier from database and set a quote for {material.name}.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
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

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-700">Search Suppliers</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, code, country..."
              className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:border-slate-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700">Select Supplier</label>
            <div className="mt-1 max-h-48 overflow-y-auto rounded-md border border-slate-200 divide-y divide-slate-100">
              {filtered.length === 0 ? (
                <p className="p-4 text-center text-xs text-slate-500">
                  {availableSuppliers.length === 0
                    ? "All suppliers are already in comparison table."
                    : "No matching suppliers found."}
                </p>
              ) : (
                filtered.map((supplier) => (
                  <label
                    key={supplier.id}
                    className={`flex items-center justify-between p-2.5 text-xs cursor-pointer hover:bg-slate-50 ${
                      selectedSupplierId === supplier.id ? "bg-teal-50/60 font-medium" : ""
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="supplier_selection"
                        value={supplier.id}
                        checked={selectedSupplierId === supplier.id}
                        onChange={() => {
                          setSelectedSupplierId(supplier.id);
                        }}
                        className="accent-teal-700"
                      />
                      <div>
                        <span className="font-semibold text-slate-900">{supplier.name}</span>
                        <span className="ml-2 text-[10px] text-slate-500">({supplier.country ?? "Global"})</span>
                      </div>
                    </div>
                    <span className="text-[11px] text-slate-500">
                      Risk: {supplier.risk_score ?? "—"}
                    </span>
                  </label>
                ))
              )}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700">
              Quoted Price ({material.currency} / {material.unit})
            </label>
            <input
              type="number"
              step="0.01"
              value={customPrice}
              onChange={(e) => setCustomPrice(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-slate-500 focus:outline-none"
              placeholder="Enter quote price"
              required
            />
          </div>

          <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!selectedSupplierId}
              className="rounded-md bg-slate-900 px-4 py-2 text-xs font-semibold text-white disabled:opacity-50"
            >
              Add to Comparison
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
