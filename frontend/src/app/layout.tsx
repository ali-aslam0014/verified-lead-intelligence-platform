import type { Metadata } from "next";
import "./globals.css";
import QueryProvider from "@/providers/query-provider";
import { 
  ShieldCheck, 
  Activity, 
  Target, 
  Building2, 
  CheckCircle2, 
  FileSpreadsheet, 
  Layers,
  Sparkles
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
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 min-h-screen flex flex-col antialiased">
        <QueryProvider>
          <div className="flex min-h-screen">
            {/* Light SaaS Navigation Sidebar */}
            <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between p-4 z-20 hidden md:flex shadow-sm">
              <div>
                {/* Brand Header */}
                <div className="flex items-center space-x-3 px-3 py-4 mb-6 border-b border-slate-100">
                  <div className="bg-gradient-to-tr from-indigo-600 to-indigo-700 p-2.5 rounded-xl text-white shadow-md shadow-indigo-500/20">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                  <div>
                    <h1 className="font-bold text-base tracking-tight text-slate-900">
                      Lead Intelligence
                    </h1>
                    <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 uppercase tracking-wider bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                      Verified SaaS
                    </span>
                  </div>
                </div>

                {/* Navigation Links */}
                <nav className="space-y-1">
                  <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl bg-indigo-50 text-indigo-700 font-semibold text-sm border border-indigo-100 transition shadow-xs">
                    <Activity className="w-4 h-4 text-indigo-600" />
                    <span>System Status</span>
                  </a>
                  <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-50 text-sm font-medium transition cursor-not-allowed opacity-60">
                    <Target className="w-4 h-4" />
                    <span>Target Builder</span>
                  </a>
                  <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-50 text-sm font-medium transition cursor-not-allowed opacity-60">
                    <Building2 className="w-4 h-4" />
                    <span>Lead Directory</span>
                  </a>
                  <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-50 text-sm font-medium transition cursor-not-allowed opacity-60">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Verification Review</span>
                  </a>
                  <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-50 text-sm font-medium transition cursor-not-allowed opacity-60">
                    <FileSpreadsheet className="w-4 h-4" />
                    <span>Exports</span>
                  </a>
                </nav>
              </div>

              {/* Bottom Footer Info */}
              <div className="px-3 py-4 border-t border-slate-100 text-xs text-slate-500 space-y-2 bg-slate-50/50 rounded-xl">
                <div className="flex items-center justify-between text-slate-600 font-medium">
                  <span className="flex items-center gap-1.5"><Layers className="w-3.5 h-3.5 text-indigo-600"/> Modular Monolith</span>
                  <span className="text-[10px] text-slate-400 font-mono">v0.1.0</span>
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Trusted & Actionable Leads with Provenance.
                </p>
              </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 bg-slate-50">
              {/* Top Navigation Header */}
              <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 z-10 shadow-xs">
                <div className="flex items-center gap-3">
                  <h2 className="text-sm font-bold text-slate-800 tracking-tight">
                    Infrastructure & System Components
                  </h2>
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                    <Sparkles className="w-3 h-3 text-indigo-600" />
                    Premium Light SaaS
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
