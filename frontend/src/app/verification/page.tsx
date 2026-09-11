"use client";

import React, { useState, useEffect } from "react";
import { fetchVerificationStats, triggerBatchTargetVerification, VerificationStats } from "@/lib/verification-api";
import { fetchTargets, Target } from "@/lib/target-api";

export default function VerificationConsolePage() {
  const [stats, setStats] = useState<VerificationStats | null>(null);
  const [targets, setTargets] = useState<Target[]>([]);
  const [selectedTargetId, setSelectedTargetId] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [batchStatus, setBatchStatus] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [sData, tData] = await Promise.all([
        fetchVerificationStats(),
        fetchTargets(),
      ]);
      setStats(sData);
      setTargets(tData);
      if (tData.length > 0) {
        setSelectedTargetId(tData[0].id);
      }
    } catch (err) {
      console.error("Error loading verification console data:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleBatchVerify() {
    if (!selectedTargetId) return;
    try {
      setBatchStatus("Dispatching batch verification job...");
      const res = await triggerBatchTargetVerification(selectedTargetId);
      setBatchStatus(`✅ Batch Verification Dispatched: ${res.message}`);
      setTimeout(() => loadData(), 2000);
    } catch (err: any) {
      setBatchStatus(`❌ Batch Verification Failed: ${err.message}`);
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 md:p-10 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Phase 3 Engine
            </span>
            <span className="text-xs text-slate-400">Verification & Evidence Console</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-white">
            Lead Verification & Provenance Console
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Multi-source deterministic verification, staleness audit, and conflict detection.
          </p>
        </div>

        <button
          onClick={loadData}
          className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm transition-colors border border-slate-700 flex items-center justify-center space-x-2"
        >
          <span>🔄 Refresh Metrics</span>
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        <div className="p-5 rounded-2xl bg-slate-800/80 border border-slate-700/60 shadow-lg space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Discovered</span>
          <div className="text-3xl font-black text-white">{stats?.total_discovered ?? "-"}</div>
          <p className="text-[11px] text-slate-400">Raw leads ready for verification</p>
        </div>

        <div className="p-5 rounded-2xl bg-emerald-950/40 border border-emerald-800/60 shadow-lg space-y-2">
          <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Verified Leads</span>
          <div className="text-3xl font-black text-emerald-300">{stats?.total_verified ?? "-"}</div>
          <p className="text-[11px] text-emerald-400/80">Confirmed via deterministic evidence</p>
        </div>

        <div className="p-5 rounded-2xl bg-amber-950/40 border border-amber-800/60 shadow-lg space-y-2">
          <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Reverify Required</span>
          <div className="text-3xl font-black text-amber-300">{stats?.reverify_required ?? "-"}</div>
          <p className="text-[11px] text-amber-400/80">Stale timestamp or missing evidence</p>
        </div>

        <div className="p-5 rounded-2xl bg-purple-950/40 border border-purple-800/60 shadow-lg space-y-2">
          <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider">Human Review</span>
          <div className="text-3xl font-black text-purple-300">{stats?.human_review_required ?? "-"}</div>
          <p className="text-[11px] text-purple-400/80">Requires manual decision</p>
        </div>

        <div className="p-5 rounded-2xl bg-rose-950/40 border border-rose-800/60 shadow-lg space-y-2">
          <span className="text-xs font-semibold text-rose-400 uppercase tracking-wider">Conflicting Info</span>
          <div className="text-3xl font-black text-rose-300">{stats?.conflicting_records_count ?? "-"}</div>
          <p className="text-[11px] text-rose-400/80">Source discrepancy detected</p>
        </div>
      </div>

      {/* Batch Target Verification Card */}
      <div className="p-6 rounded-2xl bg-slate-800/60 border border-slate-700/60 shadow-xl space-y-6">
        <div>
          <h3 className="text-lg font-bold text-white">Batch Target Verification Engine</h3>
          <p className="text-slate-400 text-xs mt-0.5">
            Select a Target Campaign to execute Website reachability, Contact validation, and Social verification across all leads.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
          <select
            value={selectedTargetId}
            onChange={(e) => setSelectedTargetId(e.target.value)}
            className="flex-1 px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white font-medium text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          >
            {targets.length === 0 ? (
              <option value="">No active target campaigns found</option>
            ) : (
              targets.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name} ({t.geography}) - ID: {t.id.slice(0, 8)}...
                </option>
              ))
            )}
          </select>

          <button
            onClick={handleBatchVerify}
            disabled={!selectedTargetId}
            className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold text-sm shadow-lg transition-all"
          >
            ⚡ Run Batch Verification
          </button>
        </div>

        {batchStatus && (
          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-mono text-blue-400">
            {batchStatus}
          </div>
        )}
      </div>

      {/* Target Campaigns Quick Progress Table */}
      <div className="p-6 rounded-2xl bg-slate-800/60 border border-slate-700/60 shadow-xl space-y-4">
        <h3 className="text-lg font-bold text-white">Active Target Campaigns Overview</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/80 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th className="p-3.5">Campaign Name</th>
                <th className="p-3.5">Niche / Industry</th>
                <th className="p-3.5">Geography</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/60">
              {targets.map((t) => (
                <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5 font-bold text-white">{t.name}</td>
                  <td className="p-3.5">{t.niche}</td>
                  <td className="p-3.5 text-slate-400">{t.geography}</td>
                  <td className="p-3.5">
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {t.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-right">
                    <a
                      href={`/leads?target_id=${t.id}`}
                      className="text-xs font-semibold text-blue-400 hover:text-blue-300 underline"
                    >
                      View Discovered Leads →
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
