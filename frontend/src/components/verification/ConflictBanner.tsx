"use client";

import React from "react";

interface ConflictItem {
  field: string;
  values: Record<string, string>;
  message: string;
}

interface ConflictBannerProps {
  conflicts: ConflictItem[];
}

export const ConflictBanner: React.FC<ConflictBannerProps> = ({ conflicts }) => {
  if (!conflicts || conflicts.length === 0) return null;

  return (
    <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700/60 space-y-3">
      <div className="flex items-center space-x-2.5 text-amber-800 dark:text-amber-300">
        <span className="text-xl">⚠️</span>
        <h4 className="font-bold text-sm tracking-wide">
          Conflicting Information Detected Across Sources
        </h4>
      </div>

      <div className="space-y-3 pt-1">
        {conflicts.map((c, idx) => (
          <div
            key={idx}
            className="p-3 rounded-lg bg-white dark:bg-slate-900/80 border border-amber-200 dark:border-amber-800/50 space-y-2 text-xs"
          >
            <div className="font-semibold text-slate-800 dark:text-slate-200 capitalize">
              Field: <span className="text-amber-600 dark:text-amber-400 font-mono">{c.field}</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
              {Object.entries(c.values).map(([source, val]) => (
                <div key={source} className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex justify-between items-center">
                  <span className="text-slate-500 dark:text-slate-400 font-medium capitalize">{source}:</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-slate-100">{val || "None"}</span>
                </div>
              ))}
            </div>
            <p className="text-slate-500 dark:text-slate-400 text-[11px] italic">
              {c.message} (No automatic overwrite performed. Sent to Human Review).
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
