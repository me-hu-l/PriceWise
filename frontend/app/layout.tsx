import type { Metadata } from "next";
import Image from "next/image";
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
          <div className="mx-auto flex max-w-7xl items-center gap-4 px-6 py-3">
            <Image
              src="/pricewise-logo.svg"
              alt="PriceWise"
              width={1000}
              height={500}
              priority
              className="h-20 w-auto"
            />
            <div className="border-l border-slate-200 pl-4">
              <p className="text-sm font-medium text-slate-800">
                Material Price Intelligence
              </p>
              <p className="text-xs text-slate-500">
                Procurement Decision Engine
              </p>
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
