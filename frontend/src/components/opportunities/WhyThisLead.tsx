"use client";

import React from "react";
import { OpportunityItem } from "@/lib/opportunity-api";

interface WhyThisLeadModalProps {
  isOpen: boolean;
  onClose: () => void;
  businessName: string;
  city?: string;
  verifiedAt?: string;
  opportunities: OpportunityItem[];
}

export const WhyThisLeadModal: React.FC<WhyThisLeadModalProps> = ({
  isOpen,
  onClose,
  businessName,
  city,
  verifiedAt,
  opportunities,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in duration-150">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-900/50">
          <div className="flex items-center space-x-2">
            <span className="text-xl">💡</span>
            <div>
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-blue-600 dark:text-blue-400">
                Sales Intelligence Pitch Brief
              </span>
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                Why is "{businessName}" a Lead?
              </h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Verified Lead Context Card */}
          <div className="p-4 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/40 space-y-2 text-xs">
            <div className="flex items-center justify-between font-semibold text-emerald-800 dark:text-emerald-300">
              <span className="flex items-center space-x-1.5">
                <span>✓ Verified Lead Fact:</span>
                <span className="font-bold">{businessName}</span>
              </span>
              <span>{city || "Verified Location"}</span>
            </div>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              This business is a verified lead because multi-layer empirical analysis identified concrete sales opportunities supported by verified evidence collected on {verifiedAt ? new Date(verifiedAt).toLocaleDateString() : "recent verification pass"}.
            </p>
          </div>

          {/* Detected Opportunities Breakdown */}
          {opportunities.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-sm">
              No evidence-backed opportunities analyzed yet for this lead. Click "Analyze Opportunities" to run the engine.
            </div>
          ) : (
            <div className="space-y-4">
              <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">
                Evidence-Backed Opportunities ({opportunities.length})
              </h4>

              {opportunities.map((opp, idx) => (
                <div
                  key={opp.id || idx}
                  className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300">
                      Recommended Service: {opp.recommended_service}
                    </span>
                    <span className="text-xs font-extrabold text-amber-600 dark:text-amber-400">
                      Evidence Strength: {Math.round(opp.confidence * 100)}% ({opp.priority})
                    </span>
                  </div>

                  <p className="text-xs text-slate-700 dark:text-slate-300">
                    <span className="font-bold">Reasoning:</span> {opp.reason}
                  </p>

                  {opp.recommended_angle && (
                    <div className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-800 dark:text-slate-200">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 block mb-1">
                        Outreach Pitch Angle:
                      </span>
                      "{opp.recommended_angle}"
                    </div>
                  )}

                  {opp.evidence?.supporting_signals && (
                    <div className="flex items-center gap-1.5 flex-wrap pt-1">
                      <span className="text-[10px] text-slate-400 font-semibold uppercase">Supporting Signals:</span>
                      {opp.evidence.supporting_signals.map((sig: string) => (
                        <span key={sig} className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                          {sig}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white font-bold text-xs hover:bg-blue-500 transition"
          >
            Close Pitch Brief
          </button>
        </div>
      </div>
    </div>
  );
};
