import type { Metadata } from "next";
import "./globals.css";
import QueryProvider from "@/providers/query-provider";
import { 
  ShieldCheck, 
  Activity, 
  Target, 
  Database, 
  CheckCircle2, 
  Building2, 
  Search, 
  Sliders, 
  FileSpreadsheet, 
  Users, 
  Layers
} from "lucide-react";

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
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 min-h-screen flex flex-col antialiased">
        <QueryProvider>
          <div className="flex min-h-screen">
            {/* Sidebar */}
            <aside className="w-64 glass-panel border-r border-gray-800 flex flex-col justify-between p-4 z-20 hidden md:flex">
              <div>
                {/* Brand Header */}
                <div className="flex items-center space-x-3 px-3 py-4 mb-6 border-b border-gray-800">
                  <div className="bg-gradient-to-tr from-indigo-600 to-emerald-400 p-2 rounded-xl text-white shadow-lg shadow-indigo-500/20">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                  <div>
                    <h1 className="font-bold text-base tracking-wide bg-gradient-to-r from-white via-gray-200 to-indigo-300 bg-clip-text text-transparent">
                      Lead Intelligence
                    </h1>
                    <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-widest bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/40">
                      Verified Platform
                    </span>
                  </div>
                </div>

                {/* Navigation Links */}
                <nav className="space-y-1">
                  <a href="#" className="flex items-center space-x-3 px-3 py-2.5 rounded-lg bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-medium text-sm transition">
                    <Activity className="w-4 h-4" />
                    <span>System Status</span>
                  </a>
                  <a href="#" className="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800/50 text-sm font-medium transition opacity-60 cursor-not-allowed">
                    <Target className="w-4 h-4" />
                    <span>Target Builder</span>
                  </a>
                  <a href="#" className="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800/50 text-sm font-medium transition opacity-60 cursor-not-allowed">
                    <Building2 className="w-4 h-4" />
                    <span>Lead Directory</span>
                  </a>
                  <a href="#" className="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800/50 text-sm font-medium transition opacity-60 cursor-not-allowed">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Verification Review</span>
                  </a>
                  <a href="#" className="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800/50 text-sm font-medium transition opacity-60 cursor-not-allowed">
                    <FileSpreadsheet className="w-4 h-4" />
                    <span>Exports</span>
                  </a>
                </nav>
              </div>

              {/* Bottom Footer Info */}
              <div className="px-3 py-4 border-t border-gray-800/80 text-xs text-gray-500 space-y-2">
                <div className="flex items-center justify-between text-gray-400">
                  <span className="flex items-center gap-1.5"><Layers className="w-3.5 h-3.5 text-indigo-400"/> Modular Monolith</span>
                  <span className="text-[10px] text-gray-500">v0.1.0</span>
                </div>
                <p className="text-[11px] text-gray-500 leading-relaxed">
                  Trusted, Actionable Leads — Provenance Guaranteed.
                </p>
              </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0">
              {/* Top Navigation Bar */}
              <header className="h-16 glass-panel border-b border-gray-800 flex items-center justify-between px-6 z-10">
                <div className="flex items-center gap-4">
                  <h2 className="text-sm font-semibold text-gray-200 tracking-wide">
                    Infrastructure & System Components
                  </h2>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-gray-800 text-gray-300 border border-gray-700">
                    Phase 0 Foundation
                  </span>
                </div>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2 text-xs text-gray-400 bg-gray-900/60 px-3 py-1.5 rounded-lg border border-gray-800">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span>Environment: <strong className="text-gray-200 font-mono">development</strong></span>
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
