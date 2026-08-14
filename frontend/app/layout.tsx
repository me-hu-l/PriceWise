import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PriceWise — Material Price Intelligence",
  description: "Material Price Intelligence & Procurement Decision Engine",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="border-b border-slate-200 bg-white">
          <div className="mx-auto max-w-7xl px-6 py-4">
            <h1 className="text-xl font-semibold tracking-tight text-slate-900">
              PRICEWISE
            </h1>
            <p className="text-sm text-slate-500">
              Material Price Intelligence &amp; Procurement Decision Engine
            </p>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
