import type { Metadata } from "next";
import "./globals.css";
import QueryProvider from "@/providers/query-provider";
import { NavigationSidebar } from "@/components/Navigation";
import { Sparkles } from "lucide-react";

export const metadata: Metadata = {
  title: "Verified Lead Intelligence Platform",
  description: "Production-Grade Trust-First Lead Intelligence & Discovery Architecture",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-slate-50 text-slate-900 min-h-screen flex flex-col antialiased">
        <QueryProvider>
          <div className="flex min-h-screen">
            {/* Navigation Sidebar */}
            <NavigationSidebar />

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 bg-slate-50">
              {/* Top Navigation Header */}
              <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 z-10 shadow-xs">
                <div className="flex items-center gap-3">
                  <h2 className="text-sm font-bold text-slate-800 tracking-tight font-display">
                    Target Builder & Lead Intelligence Console
                  </h2>
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                    <Sparkles className="w-3 h-3 text-indigo-600" />
                    Phase 1D SaaS UI
                  </span>
                </div>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2 text-xs text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200 font-medium">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span>Environment: <strong className="text-slate-900 font-mono">development</strong></span>
                  </div>
                </div>
              </header>

              {/* Page Body */}
              <main className="flex-1 p-6 md:p-8 overflow-y-auto">
                {children}
              </main>
            </div>
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
