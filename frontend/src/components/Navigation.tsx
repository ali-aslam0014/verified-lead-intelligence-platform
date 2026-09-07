"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  ShieldCheck, 
  Activity, 
  Target, 
  PlusCircle, 
  Building2, 
  CheckCircle2, 
  FileSpreadsheet, 
  Layers 
} from "lucide-react";

export function NavigationSidebar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    if (path === "/" && pathname === "/") return true;
    if (path !== "/" && pathname.startsWith(path)) return true;
    return false;
  };

  const navItems = [
    {
      name: "System Status",
      href: "/",
      icon: Activity,
      enabled: true,
    },
    {
      name: "Target Directory",
      href: "/targets",
      icon: Target,
      enabled: true,
    },
    {
      name: "Target Builder",
      href: "/targets/builder",
      icon: PlusCircle,
      enabled: true,
    },
    {
      name: "Lead Directory",
      href: "/leads",
      icon: Building2,
      enabled: true,
    },
    {
      name: "Verification Review",
      href: "/verifications",
      icon: CheckCircle2,
      enabled: false,
      badge: "Phase 3",
    },
    {
      name: "Exports",
      href: "/exports",
      icon: FileSpreadsheet,
      enabled: false,
      badge: "Phase 4",
    },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between p-4 z-20 hidden md:flex shadow-xs">
      <div>
        {/* Brand Header */}
        <div className="flex items-center space-x-3 px-3 py-4 mb-6 border-b border-slate-100">
          <div className="bg-gradient-to-tr from-indigo-600 to-indigo-700 p-2.5 rounded-xl text-white shadow-md shadow-indigo-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight text-slate-900 font-display">
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
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = item.enabled && isActive(item.href);

            if (!item.enabled) {
              return (
                <div
                  key={item.name}
                  className="flex items-center justify-between px-3.5 py-2.5 rounded-xl text-slate-400 text-sm font-medium opacity-60 cursor-not-allowed select-none"
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-4 h-4 text-slate-400" />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] bg-slate-100 text-slate-500 font-mono px-1.5 py-0.5 rounded border border-slate-200">
                      {item.badge}
                    </span>
                  )}
                </div>
              );
            }

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                  active
                    ? "bg-indigo-50 text-indigo-700 border border-indigo-100 shadow-xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-transparent"
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? "text-indigo-600" : "text-slate-500"}`} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Footer Info */}
      <div className="px-3 py-4 border-t border-slate-100 text-xs text-slate-500 space-y-2 bg-slate-50/50 rounded-xl">
        <div className="flex items-center justify-between text-slate-600 font-medium">
          <span className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-indigo-600" /> Modular Monolith
          </span>
          <span className="text-[10px] text-slate-400 font-mono">v0.1.0</span>
        </div>
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Trusted & Actionable Leads with Provenance.
        </p>
      </div>
    </aside>
  );
}
