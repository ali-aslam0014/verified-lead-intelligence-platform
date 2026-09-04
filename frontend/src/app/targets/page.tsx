"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  fetchTargets, 
  deleteTarget, 
  triggerTargetRun, 
  fetchAllTargetRuns,
  Target, 
  TargetStatus,
  OpportunityType 
} from "@/lib/target-api";
import { 
  Target as TargetIcon, 
  Plus, 
  Search, 
  Play, 
  Archive, 
  Eye, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2, 
  MapPin, 
  Layers, 
  Building, 
  BarChart3, 
  HelpCircle,
  Filter,
  Sparkles
} from "lucide-react";

export default function TargetDirectoryPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Targets Query
  const {
    data: targets,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useQuery<Target[]>({
    queryKey: ["targets", statusFilter, search],
    queryFn: () => fetchTargets({ status: statusFilter, search }),
  });

  // All Runs Query for KPI calculation
  const { data: allRuns } = useQuery({
    queryKey: ["allTargetRuns"],
    queryFn: fetchAllTargetRuns,
  });

  // Soft Delete Mutation
  const archiveMutation = useMutation({
    mutationFn: (id: string) => deleteTarget(id),
    onSuccess: (data) => {
      setNotification({
        type: "success",
        message: `Target "${data.target.name}" archived successfully (Status set to CANCELLED).`,
      });
      queryClient.invalidateQueries({ queryKey: ["targets"] });
    },
    onError: (err: any) => {
      setNotification({
        type: "error",
        message: err.message || "Failed to archive target.",
      });
    },
  });

  // Trigger Run Mutation
  const triggerRunMutation = useMutation({
    mutationFn: (id: string) => triggerTargetRun(id),
    onSuccess: (run) => {
      setNotification({
        type: "success",
        message: `Execution Run Queued (ID: ${run.id.slice(0, 8)}...). Status: QUEUED`,
      });
      queryClient.invalidateQueries({ queryKey: ["targetRuns"] });
      queryClient.invalidateQueries({ queryKey: ["allTargetRuns"] });
    },
    onError: (err: any) => {
      setNotification({
        type: "error",
        message: err.message || "Failed to queue target run.",
      });
    },
  });

  // Calculate real KPI metrics
  const totalCampaigns = targets?.length || 0;
  const activeTargets = targets?.filter((t) => t.status === "ACTIVE").length || 0;
  const completedRuns = allRuns?.filter((r) => r.status === "COMPLETED").length || 0;

  const getStatusBadge = (status: TargetStatus) => {
    switch (status) {
      case "ACTIVE":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            ACTIVE
          </span>
        );
      case "DRAFT":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
            DRAFT
          </span>
        );
      case "INACTIVE":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            INACTIVE
          </span>
        );
      case "CANCELLED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            ARCHIVED
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
        className="px-2 py-0.5 rounded text-[11px] font-medium bg-indigo-50 text-indigo-700 border border-indigo-100"
      >
        {labels[type] || type}
      </span>
    );
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
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

      {/* Directory Page Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-indigo-50/80 to-purple-50/50 rounded-full blur-3xl opacity-60 pointer-events-none"></div>
        
        <div className="space-y-2 relative z-10">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              Phase 1D Directory
            </span>
            <span className="text-xs text-slate-500 font-medium">Target Campaigns</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight font-display">
            Target Directory
          </h1>
          <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
            Configure niche target profiles, view active lead-generation parameters, launch queued discovery runs, and manage lead criteria.
          </p>
        </div>

        <div className="flex items-center gap-3 relative z-10">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs border border-slate-200 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>

          <Link
            href="/targets/builder"
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm transition shadow-md shadow-indigo-500/20"
          >
            <Plus className="w-4 h-4" />
            <span>New Target Campaign</span>
          </Link>
        </div>
      </div>

      {/* Real Statistics KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        {/* KPI 1: Total Campaigns */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Campaigns</span>
            <div className="text-2xl font-bold text-slate-900 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : totalCampaigns}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200">
            <TargetIcon className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 2: Active Targets */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Targets</span>
            <div className="text-2xl font-bold text-emerald-700 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : activeTargets}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 3: Completed Runs */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Completed Runs</span>
            <div className="text-2xl font-bold text-slate-900 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : completedRuns}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-blue-50 text-blue-700 border border-blue-200">
            <BarChart3 className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 4: Discovered Leads (User Rule: Strictly NO fabricated data!) */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between relative overflow-hidden">
          <div className="space-y-1 z-10">
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Discovered Leads</span>
              <span className="group relative cursor-pointer text-slate-400 hover:text-slate-600">
                <HelpCircle className="w-3.5 h-3.5" />
              </span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-lg font-bold text-slate-400 font-mono">0</span>
              <span className="text-[11px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                Phase 2 Discovery Engine
              </span>
            </div>
          </div>
          <div className="p-3 rounded-xl bg-slate-100 text-slate-500 border border-slate-200">
            <Building className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-card-sm flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search target by title, niche, geography..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
          />
        </div>

        {/* Status Filter Dropdown */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span>Filter Status:</span>
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3.5 py-2 rounded-xl border border-slate-200 bg-white text-sm text-slate-800 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active Only</option>
            <option value="DRAFT">Draft</option>
            <option value="INACTIVE">Inactive</option>
            <option value="CANCELLED">Archived</option>
          </select>
        </div>
      </div>

      {/* Main Targets Content */}
      {/* 1. Loading State */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm animate-pulse space-y-4">
              <div className="flex justify-between items-start">
                <div className="space-y-2">
                  <div className="h-5 w-48 bg-slate-200 rounded"></div>
                  <div className="h-4 w-32 bg-slate-100 rounded"></div>
                </div>
                <div className="h-6 w-20 bg-slate-200 rounded-full"></div>
              </div>
              <div className="h-10 w-full bg-slate-100 rounded-xl"></div>
            </div>
          ))}
        </div>
      )}

      {/* 2. Error State */}
      {isError && !isLoading && (
        <div className="bg-rose-50 border border-rose-200 p-6 rounded-2xl text-rose-900 space-y-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-rose-600 shrink-0" />
            <div>
              <h3 className="font-bold text-base">Failed to Load Target Campaigns</h3>
              <p className="text-xs text-rose-700">{(error as any)?.message || "Network error occurred while fetching targets."}</p>
            </div>
          </div>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs transition"
          >
            Retry Loading
          </button>
        </div>
      )}

      {/* 3. Empty State */}
      {!isLoading && !isError && targets?.length === 0 && (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 shadow-card-sm text-center space-y-4 max-w-xl mx-auto my-8">
          <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100 flex items-center justify-center mx-auto">
            <TargetIcon className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-xl font-bold text-slate-900 font-display">No Target Campaigns Found</h3>
            <p className="text-sm text-slate-500">
              {search || statusFilter !== "ALL"
                ? "No target campaigns match your search criteria or status filter. Try clearing filters."
                : "Create your first lead-generation target profile to start configuring discovery parameters."}
            </p>
          </div>
          <div className="pt-2">
            <Link
              href="/targets/builder"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm transition shadow-md shadow-indigo-500/20"
            >
              <Plus className="w-4 h-4" />
              <span>Create First Target Campaign</span>
            </Link>
          </div>
        </div>
      )}

      {/* 4. Target List Display */}
      {!isLoading && !isError && targets && targets.length > 0 && (
        <div className="space-y-4">
          {targets.map((target) => (
            <div
              key={target.id}
              className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm hover:shadow-card-hover transition-all duration-200 flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
            >
              {/* Left Column: Details */}
              <div className="space-y-3 flex-1 min-w-0">
                <div className="flex items-center gap-3 flex-wrap">
                  <h3 className="text-lg font-bold text-slate-900 tracking-tight font-display">
                    {target.name}
                  </h3>
                  {getStatusBadge(target.status)}
                </div>

                {/* Tags row */}
                <div className="flex items-center gap-4 text-xs text-slate-600 flex-wrap">
                  <div className="flex items-center gap-1.5 font-medium bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
                    <Layers className="w-3.5 h-3.5 text-indigo-600" />
                    <span>Niche: <strong>{target.niche}</strong></span>
                    {target.sub_niche && <span className="text-slate-400">({target.sub_niche})</span>}
                  </div>

                  <div className="flex items-center gap-1.5 font-medium bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
                    <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Location: <strong>{target.geography}</strong></span>
                  </div>
                </div>

                {/* Opportunity Types */}
                <div className="flex items-center gap-1.5 flex-wrap pt-1">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Opportunities:</span>
                  {target.opportunity_types.map(getOpportunityPill)}
                </div>
              </div>

              {/* Right Column: Actions */}
              <div className="flex items-center gap-2.5 shrink-0 w-full md:w-auto pt-4 md:pt-0 border-t md:border-t-0 border-slate-100">
                {/* Launch Run CTA */}
                <button
                  onClick={() => triggerRunMutation.mutate(target.id)}
                  disabled={triggerRunMutation.isPending || target.status === "CANCELLED"}
                  className="flex-1 md:flex-none flex items-center justify-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition shadow-sm shadow-indigo-500/20 disabled:opacity-50"
                  title="Queue new execution run"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Launch Run</span>
                </button>

                {/* View Details */}
                <Link
                  href={`/targets/${target.id}`}
                  className="flex-1 md:flex-none flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs border border-slate-200 transition"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Details</span>
                </Link>

                {/* Soft Delete Archive */}
                {target.status !== "CANCELLED" && (
                  <button
                    onClick={() => {
                      if (confirm(`Archive target campaign "${target.name}"? Status will be updated to CANCELLED.`)) {
                        archiveMutation.mutate(target.id);
                      }
                    }}
                    disabled={archiveMutation.isPending}
                    className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 border border-slate-200 transition disabled:opacity-50"
                    title="Archive target campaign (Soft delete)"
                  >
                    <Archive className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
