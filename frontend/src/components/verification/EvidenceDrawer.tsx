"use client";

import React from "react";
import { EvidenceItem } from "@/lib/verification-api";

interface EvidenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  businessName: string;
  evidenceItems: EvidenceItem[];
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  isOpen,
  onClose,
  businessName,
  evidenceItems,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/60 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-xl bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 flex flex-col h-full animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="p-6 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-900/50">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-blue-400">
              Provenance Audit Trail
            </span>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
              Evidence Log: {businessName}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Evidence List Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {evidenceItems.length === 0 ? (
            <div className="text-center py-12 text-slate-500 dark:text-slate-400">
              No detailed evidence records stored yet for this business.
            </div>
          ) : (
            evidenceItems.map((item, idx) => (
              <div
                key={item.id || idx}
                className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">
                    Source: {item.source}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {new Date(item.observed_at).toLocaleString()}
                  </span>
                </div>

                {item.source_url_or_id && (
                  <div className="text-xs font-mono text-slate-600 dark:text-slate-300 truncate">
                    URL/ID: <a href={item.source_url_or_id} target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">{item.source_url_or_id}</a>
                  </div>
                )}

                <div className="bg-slate-900 text-slate-100 p-3.5 rounded-lg text-xs font-mono overflow-x-auto border border-slate-800">
                  <pre>{JSON.stringify(item.data, null, 2)}</pre>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-medium text-sm transition-colors"
          >
            Close Evidence Drawer
          </button>
        </div>
      </div>
    </div>
  );
};
