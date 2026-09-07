"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  fetchTarget, 
  fetchTargetRuns, 
  triggerTargetRun, 
  deleteTarget, 
  Target, 
  TargetRun,
  TargetRunStatus,
  OpportunityType 
} from "@/lib/target-api";
import { 
  ArrowLeft, 
  Play, 
  Archive, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  MapPin, 
  Sparkles, 
  Globe, 
  Clock, 
  BarChart2, 
  Building
} from "lucide-react";

export default function TargetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const targetId = params.id as string;
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Target Query
  const {
    data: target,
    isLoading: targetLoading,
    isError: targetError,
    error: targetErrObj,
    refetch: refetchTarget,
  } = useQuery<Target>({
    queryKey: ["target", targetId],
    queryFn: () => fetchTarget(targetId),
    enabled: !!targetId,
  });

  // Target Runs Query
  const {
    data: runs,
    isLoading: runsLoading,
    refetch: refetchRuns,
    isFetching: runsFetching,
  } = useQuery<TargetRun[]>({
    queryKey: ["targetRuns", targetId],
    queryFn: () => fetchTargetRuns(targetId),
    enabled: !!targetId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data && data.some((r) => r.status === "QUEUED" || r.status === "RUNNING")) {
        return 2000; // Poll every 2s while discovery runs are active
      }
      return false;
    },
  });

  // Trigger Run Mutation
  const triggerRunMutation = useMutation({
    mutationFn: () => triggerTargetRun(targetId),
    onSuccess: (newRun) => {
      setNotification({
        type: "success",
        message: `Execution Run Queued (ID: ${newRun.id.slice(0, 8)}...). Status: QUEUED`,
      });
      queryClient.invalidateQueries({ queryKey: ["targetRuns", targetId] });
    },
    onError: (err: any) => {
      setNotification({
        type: "error",
        message: err.message || "Failed to queue execution run.",
      });
    },
  });

  // Archive Target Mutation
  const archiveMutation = useMutation({
    mutationFn: () => deleteTarget(targetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["targets"] });
      router.push("/targets");
    },
    onError: (err: any) => {
      setNotification({
        type: "error",
        message: err.message || "Failed to archive target.",
      });
    },
  });

  const getRunStatusBadge = (status: TargetRunStatus) => {
    switch (status) {
      case "QUEUED":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
            QUEUED
          </span>
        );
      case "RUNNING":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-spin"></span>
            RUNNING
          </span>
        );
      case "COMPLETED":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            COMPLETED
          </span>
        );
      case "FAILED":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            FAILED
          </span>
        );
    }
  };

  const getOpportunityPill = (type: OpportunityType) => {
    const labels: Record<OpportunityType, string> = {
      NEW_WEBSITE: "Missing Website",
      WEBSITE_REDESIGN: "Redesign Needed",
      SEO: "SEO Opportunity",
      LOCAL_SEO: "Local Maps SEO",
      REDESIGN_PLUS_SEO: "Redesign + SEO",
      SOCIAL_TO_WEBSITE: "Social to Web",
      CONVERSION_OPTIMIZATION: "Conversion Gap",
      COMPETITOR_GAP: "Competitor Gap",
      MANUAL_REVIEW: "Manual Review",
    };
    return (
      <span
        key={type}
        className="px-2.5 py-1 rounded-lg text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100"
      >
        {labels[type] || type}
      </span>
    );
  };

  if (targetLoading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm animate-pulse space-y-4">
          <div className="h-6 w-64 bg-slate-200 rounded"></div>
          <div className="h-4 w-40 bg-slate-100 rounded"></div>
        </div>
      </div>
    );
  }

  if (targetError || !target) {
    return (
      <div className="bg-rose-50 border border-rose-200 p-8 rounded-2xl text-rose-900 space-y-4 max-w-xl mx-auto my-8 text-center">
        <AlertTriangle className="w-8 h-8 text-rose-600 mx-auto" />
        <div>
          <h3 className="font-bold text-lg font-display">Target Campaign Not Found</h3>
          <p className="text-xs text-rose-700 mt-1 font-mono">
            {(targetErrObj as any)?.message || "The requested target campaign ID does not exist or has been deleted."}
          </p>
        </div>
        <button
          onClick={() => router.push("/targets")}
          className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs transition"
        >
          Back to Target Directory
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Toast Notification Banner */}
      {notification && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between shadow-card-sm ${
            notification.type === "success"
              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
              : "bg-rose-50 border-rose-200 text-rose-800"
          }`}
        >
          <div className="flex items-center gap-3">
            {notification.type === "success" ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
            )}
            <span className="text-sm font-medium">{notification.message}</span>
          </div>
          <button
            onClick={() => setNotification(null)}
            className="text-xs font-semibold px-2 py-1 rounded hover:bg-black/5"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Target Details Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm space-y-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => router.push("/targets")}
            className="flex items-center gap-2 text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Directory</span>
          </button>

          <span className="text-xs text-slate-400 font-mono">
            ID: {target.id}
          </span>
        </div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pt-2">
          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-extrabold text-slate-900 font-display tracking-tight">
                {target.name}
              </h1>
              <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                {target.status}
              </span>
            </div>

            <div className="flex items-center gap-4 text-xs text-slate-600 flex-wrap">
              <span className="flex items-center gap-1 font-medium">
                <Layers className="w-3.5 h-3.5 text-indigo-600" />
                Niche: <strong>{target.niche}</strong> {target.sub_niche && `(${target.sub_niche})`}
              </span>
              <span className="flex items-center gap-1 font-medium">
                <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                Geography: <strong>{target.geography}</strong>
              </span>
              <span className="flex items-center gap-1 font-medium">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                Created: <strong>{new Date(target.created_at).toLocaleDateString()}</strong>
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => triggerRunMutation.mutate()}
              disabled={triggerRunMutation.isPending || target.status === "CANCELLED"}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition shadow-md shadow-indigo-500/20 disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{triggerRunMutation.isPending ? "Queuing Run..." : "Launch Run"}</span>
            </button>

            {target.status !== "CANCELLED" && (
              <button
                onClick={() => {
                  if (confirm(`Archive target campaign "${target.name}"?`)) {
                    archiveMutation.mutate();
                  }
                }}
                disabled={archiveMutation.isPending}
                className="p-2.5 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 border border-slate-200 transition disabled:opacity-50"
                title="Archive Target Campaign"
              >
                <Archive className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Target Parameters Overview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: Opportunities & Sources */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 font-display flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            <span>Opportunity Signals & Sources</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-slate-500 font-medium block mb-1.5">Selected Sales Signals:</span>
              <div className="flex gap-2 flex-wrap">
                {target.opportunity_types.map(getOpportunityPill)}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100">
              <span className="text-slate-500 font-medium block mb-1.5">Enabled Source Adapters:</span>
              <div className="flex gap-2 flex-wrap">
                {(target.source_configuration?.enabled_sources || []).map((src: string) => (
                  <span key={src} className="px-2.5 py-1 rounded bg-slate-100 text-slate-700 font-mono text-[11px] border border-slate-200">
                    {src}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Card 2: Filter Specification */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 font-display flex items-center gap-2">
            <Globe className="w-4 h-4 text-indigo-600" />
            <span>Lead Demographic Filters</span>
          </h3>

          <div className="grid grid-cols-2 gap-4 text-xs">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium block">Revenue Bounds</span>
              <span className="font-bold text-slate-900 mt-1 block">
                {target.filters?.min_revenue ? `$${target.filters.min_revenue}` : "No min"} - {target.filters?.max_revenue ? `$${target.filters.max_revenue}` : "No max"}
              </span>
            </div>

            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium block">Headcount Bounds</span>
              <span className="font-bold text-slate-900 mt-1 block">
                {target.filters?.min_employees ? `${target.filters.min_employees} emp` : "No min"} - {target.filters?.max_employees ? `${target.filters.max_employees} emp` : "No max"}
              </span>
            </div>

            <div className="col-span-2 space-y-1">
              <span className="text-slate-500 font-medium block">Technology Stack Tags:</span>
              <div className="flex gap-1.5 flex-wrap">
                {(target.filters?.technologies || []).map((tech: string) => (
                  <span key={tech} className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 font-mono text-[11px] border border-purple-100">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Target Run History Table */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-indigo-600" />
            <h3 className="font-bold text-base text-slate-900 font-display">Run History Log</h3>
            <span className="text-xs text-slate-400 font-mono">({runs?.length || 0} runs)</span>
          </div>

          <button
            onClick={() => refetchRuns()}
            disabled={runsFetching}
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${runsFetching ? "animate-spin" : ""}`} />
            <span>Refresh Runs</span>
          </button>
        </div>

        {/* Loading State for Runs */}
        {runsLoading && (
          <div className="space-y-2 py-4">
            {[1, 2].map((i) => (
              <div key={i} className="h-10 bg-slate-100 rounded-xl animate-pulse"></div>
            ))}
          </div>
        )}

        {/* Empty Runs State */}
        {!runsLoading && runs?.length === 0 && (
          <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200/80 space-y-2">
            <Building className="w-8 h-8 text-slate-400 mx-auto" />
            <h4 className="font-bold text-sm text-slate-800 font-display">No Execution Runs Triggered</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Click &quot;Launch Run&quot; above to trigger a new backend execution run.
            </p>
          </div>
        )}

        {/* Runs Table */}
        {!runsLoading && runs && runs.length > 0 && (
          <div className="overflow-x-auto border border-slate-200 rounded-xl">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-500 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="p-3">Run ID</th>
                  <th className="p-3">Backend Status</th>
                  <th className="p-3">Discovered Leads</th>
                  <th className="p-3">Verified Leads</th>
                  <th className="p-3">Started At</th>
                  <th className="p-3">Created At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {runs.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-50/80 transition font-mono">
                    <td className="p-3 font-semibold text-slate-900">
                      {run.id.slice(0, 8)}...
                    </td>
                    <td className="p-3 font-sans">{getRunStatusBadge(run.status)}</td>
                    <td className="p-3">{run.total_discovered}</td>
                    <td className="p-3">{run.total_verified}</td>
                    <td className="p-3 text-slate-500">
                      {run.started_at ? new Date(run.started_at).toLocaleTimeString() : "--"}
                    </td>
                    <td className="p-3 text-slate-500">
                      {new Date(run.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
