"use client";

import React from "react";
import { OpportunityItem } from "@/lib/opportunity-api";

interface OpportunityCardProps {
  opportunity: OpportunityItem;
  onOpenWhyThisLead?: () => void;
}

export const OpportunityCard: React.FC<OpportunityCardProps> = ({ opportunity, onOpenWhyThisLead }) => {
  const isHigh = opportunity.priority === "HIGH";
  const isMedium = opportunity.priority === "MEDIUM";

  const priorityBadgeClass = isHigh
    ? "bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border-rose-300 dark:border-rose-800"
    : isMedium
    ? "bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-800"
    : "bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-800";

  return (
    <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3 hover:border-blue-500/50 transition">
      <div className="flex items-center justify-between">
        <span className="font-extrabold text-xs uppercase tracking-wider text-blue-600 dark:text-blue-400">
          {opportunity.type.replace(/_/g, " ")}
        </span>
        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border ${priorityBadgeClass}`}>
          {opportunity.priority} PRIORITY ({Math.round(opportunity.confidence * 100)}% CONFIDENCE)
        </span>
      </div>

      <div>
        <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">
          {opportunity.recommended_service}
        </h4>
        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
          {opportunity.reason}
        </p>
      </div>

      {opportunity.recommended_angle && (
        <div className="p-2.5 rounded-lg bg-blue-50/60 dark:bg-blue-950/30 border border-blue-200/60 dark:border-blue-900/40 text-[11px] text-blue-900 dark:text-blue-200">
          <span className="font-bold uppercase tracking-wider text-[10px] block text-blue-600 dark:text-blue-400 mb-0.5">
            Recommended Sales Pitch Angle:
          </span>
          "{opportunity.recommended_angle}"
        </div>
      )}

      {onOpenWhyThisLead && (
        <div className="pt-1 flex justify-end">
          <button
            onClick={onOpenWhyThisLead}
            className="text-xs font-bold text-blue-600 dark:text-blue-400 hover:text-blue-500 hover:underline flex items-center gap-1"
          >
            <span>Why is this a lead?</span>
            <span>→</span>
          </button>
        </div>
      )}
    </div>
  );
};
