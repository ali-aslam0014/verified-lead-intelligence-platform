"use client";

import { useState, Suspense } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchAllAudits,
  triggerBusinessAudit,
  fetchBusinessAudit,
  AuditListItem,
  WebsiteAuditResult,
  AuditIssue,
} from "@/lib/audit-api";
import {
  Globe,
  Zap,
  Shield,
  ShieldOff,
  Smartphone,
  AlertTriangle,
  CheckCircle2,
  X,
  RefreshCw,
  ExternalLink,
  TrendingUp,
  Flame,
  Star,
  Copy,
  ChevronDown,
  ChevronUp,
  BarChart2,
  MessageSquare,
  Filter,
  Activity,
} from "lucide-react";

// ─────────────────────────────────────────────
// Score Gauge Component
// ─────────────────────────────────────────────
function ScoreGauge({ score, label }: { score: number | null; label: string }) {
  if (score === null) {
    return (
      <div className="flex flex-col items-center gap-1">
        <div className="w-16 h-16 rounded-full border-4 border-slate-200 flex items-center justify-center bg-slate-50">
          <span className="text-slate-400 text-xs font-mono">N/A</span>
        </div>
        <span className="text-[10px] text-slate-400 font-medium">{label}</span>
      </div>
    );
  }

  const color =
    score >= 90
      ? "#22c55e"
      : score >= 70
      ? "#84cc16"
      : score >= 50
      ? "#f59e0b"
      : "#ef4444";

  const pct = score / 100;
  const radius = 26;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - pct);

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative w-16 h-16">
        <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
          <circle cx="32" cy="32" r={radius} fill="none" stroke="#f1f5f9" strokeWidth="6" />
          <circle
            cx="32"
            cy="32"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: "stroke-dashoffset 0.6s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-extrabold" style={{ color }}>
            {score}
          </span>
        </div>
      </div>
      <span className="text-[10px] text-slate-500 font-medium">{label}</span>
    </div>
  );
}

// ─────────────────────────────────────────────
// Redesign Badge
// ─────────────────────────────────────────────
function RedesignBadge({ recommendation, score }: { recommendation: string; score: number }) {
  const config = {
    URGENT: {
      label: "🔴 URGENT Redesign",
      classes: "bg-rose-100 text-rose-800 border-rose-300",
      icon: <Flame className="w-3.5 h-3.5 text-rose-600" />,
    },
    RECOMMENDED: {
      label: "🟡 Redesign Recommended",
      classes: "bg-amber-100 text-amber-800 border-amber-300",
      icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />,
    },
    SEO_ONLY: {
      label: "🟢 SEO Improvements",
      classes: "bg-emerald-100 text-emerald-800 border-emerald-300",
      icon: <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />,
    },
    GOOD: {
      label: "✅ Website Healthy",
      classes: "bg-blue-100 text-blue-800 border-blue-300",
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />,
    },
    UNKNOWN: {
      label: "⏳ Pending",
      classes: "bg-slate-100 text-slate-600 border-slate-300",
      icon: <RefreshCw className="w-3.5 h-3.5 text-slate-400" />,
    },
  };

  const c = config[recommendation as keyof typeof config] || config.UNKNOWN;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${c.classes}`}
    >
      {c.icon}
      {c.label}
      <span className="text-[10px] opacity-70">({score}/16)</span>
    </span>
  );
}

// ─────────────────────────────────────────────
// Severity Badge
// ─────────────────────────────────────────────
function SeverityBadge({ severity }: { severity: string }) {
  const classes = {
    HIGH: "bg-rose-100 text-rose-800 border-rose-200",
    MEDIUM: "bg-amber-100 text-amber-800 border-amber-200",
    LOW: "bg-slate-100 text-slate-600 border-slate-200",
  };
  return (
    <span
      className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold border ${
        classes[severity as keyof typeof classes] || classes.LOW
      }`}
    >
      {severity}
    </span>
  );
}

// ─────────────────────────────────────────────
// Audit Detail Modal
// ─────────────────────────────────────────────
function AuditDetailModal({
  item,
  audit,
  onClose,
}: {
  item: AuditListItem;
  audit: WebsiteAuditResult | null | undefined;
  onClose: () => void;
}) {
  const [pitchCopied, setPitchCopied] = useState(false);
  const [issuesExpanded, setIssuesExpanded] = useState(true);

  const copyPitch = () => {
    if (audit?.sales_pitch) {
      navigator.clipboard.writeText(audit.sales_pitch);
      setPitchCopied(true);
      setTimeout(() => setPitchCopied(false), 2000);
    }
  };

  const auditData = audit || item;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 to-slate-50 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-lg text-slate-900 font-display">{item.business_name}</h3>
            <a
              href={item.website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-indigo-600 hover:underline flex items-center gap-1"
            >
              <Globe className="w-3 h-3" />
              {item.website_domain}
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-200 text-slate-500 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="overflow-y-auto p-6 space-y-6">
          {/* Redesign Score + PageSpeed Gauges */}
          <div className="bg-slate-50 rounded-xl border border-slate-200 p-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <RedesignBadge
                  recommendation={item.redesign_recommendation}
                  score={item.redesign_score}
                />
                <p className="text-xs text-slate-500 mt-2">
                  Redesign Priority Score: <strong>{item.redesign_score}/16 points</strong>
                </p>
              </div>
              <div className="flex items-center gap-6">
                <ScoreGauge score={item.pagespeed_mobile_score} label="Mobile Speed" />
                <ScoreGauge score={item.pagespeed_desktop_score} label="Desktop Speed" />
              </div>
            </div>
          </div>

          {/* Technical Checklist */}
          <div>
            <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-600" />
              Technical Checklist
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {[
                { label: "HTTPS / SSL", pass: item.https_enabled, icon: <Shield className="w-3.5 h-3.5" /> },
                { label: "Mobile Responsive", pass: item.responsive_mobile, icon: <Smartphone className="w-3.5 h-3.5" /> },
                { label: "CTA Button", pass: item.cta_visible, icon: <Zap className="w-3.5 h-3.5" /> },
                { label: "Schema Markup", pass: item.schema_markup_present, icon: <Star className="w-3.5 h-3.5" /> },
                {
                  label: "Response Speed",
                  pass: item.response_time_ms < 2000,
                  icon: <Activity className="w-3.5 h-3.5" />,
                  detail: item.response_time_ms > 0 ? `${(item.response_time_ms / 1000).toFixed(1)}s` : null,
                },
              ].map((chk) => (
                <div
                  key={chk.label}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium ${
                    chk.pass
                      ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                      : "bg-rose-50 border-rose-200 text-rose-800"
                  }`}
                >
                  {chk.pass ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  ) : (
                    <X className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                  )}
                  <span>{chk.label}</span>
                  {chk.detail && <span className="ml-auto opacity-70 font-mono">{chk.detail}</span>}
                </div>
              ))}
            </div>
          </div>

          {/* Issues Breakdown */}
          {item.issues && item.issues.length > 0 && (
            <div>
              <button
                onClick={() => setIssuesExpanded(!issuesExpanded)}
                className="w-full flex items-center justify-between text-sm font-bold text-slate-900 mb-2"
              >
                <span className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                  Issues Found ({item.issues.length})
                </span>
                {issuesExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {issuesExpanded && (
                <div className="space-y-2">
                  {item.issues.map((issue: AuditIssue, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs"
                    >
                      <SeverityBadge severity={issue.severity} />
                      <div className="flex-1 min-w-0">
                        <span className="font-mono text-slate-500 text-[10px] block">{issue.code}</span>
                        <span className="text-slate-800">{issue.description}</span>
                      </div>
                      {issue.points > 0 && (
                        <span className="text-[10px] font-bold text-rose-600 shrink-0">+{issue.points}pts</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* AI Sales Pitch */}
          {item.sales_pitch && (
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-bold text-indigo-900 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-indigo-600" />
                  Auto-Generated Sales Pitch
                </h4>
                <button
                  onClick={copyPitch}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition"
                >
                  <Copy className="w-3.5 h-3.5" />
                  {pitchCopied ? "Copied!" : "Copy Pitch"}
                </button>
              </div>
              <pre className="text-xs text-indigo-900 whitespace-pre-wrap font-sans leading-relaxed">
                {item.sales_pitch}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Main Page Content
// ─────────────────────────────────────────────
function AuditEngineContent() {
  const queryClient = useQueryClient();
  const [filterRec, setFilterRec] = useState<string>("ALL");
  const [selectedItem, setSelectedItem] = useState<AuditListItem | null>(null);
  const [auditingId, setAuditingId] = useState<string | null>(null);
  const [refreshingId, setRefreshingId] = useState<string | null>(null);

  const { data: audits = [], isLoading, refetch, isFetching } = useQuery<AuditListItem[]>({
    queryKey: ["audits", filterRec],
    queryFn: () =>
      fetchAllAudits({
        recommendation: filterRec === "ALL" ? undefined : filterRec,
        limit: 200,
      }),
  });

  const { data: selectedAudit } = useQuery<WebsiteAuditResult | null>({
    queryKey: ["auditDetail", selectedItem?.business_id],
    queryFn: () => fetchBusinessAudit(selectedItem!.business_id),
    enabled: !!selectedItem,
  });

  // Import fetchBusinesses to list Has-Website businesses not yet audited
  const { data: hasWebsiteBusinesses = [] } = useQuery({
    queryKey: ["businesses-has-website"],
    queryFn: async () => {
      const { fetchBusinesses } = await import("@/lib/business-api");
      return fetchBusinesses({ has_website: true, limit: 200 });
    },
  });

  const triggerMutation = useMutation({
    mutationFn: (businessId: string) => triggerBusinessAudit(businessId),
    onSuccess: (_, businessId) => {
      setAuditingId(null);
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["audits"] });
      }, 25000);
    },
    onError: () => setAuditingId(null),
  });

  const handleTriggerAudit = (businessId: string) => {
    setAuditingId(businessId);
    triggerMutation.mutate(businessId);
  };

  const urgentCount = audits.filter((a) => a.redesign_recommendation === "URGENT").length;
  const recommendedCount = audits.filter((a) => a.redesign_recommendation === "RECOMMENDED").length;
  const seoOnlyCount = audits.filter((a) => a.redesign_recommendation === "SEO_ONLY").length;
  const auditedIds = new Set(audits.map((a) => a.business_id));
  const unauditedBusinesses = hasWebsiteBusinesses.filter((b: any) => !auditedIds.has(b.id));

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-br from-violet-50/80 to-indigo-50/60 rounded-full blur-3xl opacity-70 pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-violet-50 text-violet-700 border border-violet-200">
                Phase 2B — Website Intelligence
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight font-display">
              Website Audit Engine
            </h1>
            <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
              Automatically audits websites for mobile speed, SEO issues, HTTPS, CTA presence, and Google PageSpeed scores.
              Generates a <strong>Redesign Score</strong> and personalized <strong>Sales Pitch</strong> for every lead.
            </p>
          </div>
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs border border-slate-200 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? "animate-spin" : ""}`} />
            Refresh Audits
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Total Audited</span>
          <div className="text-2xl font-extrabold text-slate-900 mt-1">{audits.length}</div>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-rose-200 shadow-card-sm">
          <span className="text-xs font-semibold text-rose-600 uppercase tracking-wider flex items-center gap-1">
            <Flame className="w-3.5 h-3.5" /> Urgent
          </span>
          <div className="text-2xl font-extrabold text-rose-700 mt-1">{urgentCount}</div>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-amber-200 shadow-card-sm">
          <span className="text-xs font-semibold text-amber-600 uppercase tracking-wider flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Recommended
          </span>
          <div className="text-2xl font-extrabold text-amber-700 mt-1">{recommendedCount}</div>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-emerald-200 shadow-card-sm">
          <span className="text-xs font-semibold text-emerald-600 uppercase tracking-wider flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> SEO Only
          </span>
          <div className="text-2xl font-extrabold text-emerald-700 mt-1">{seoOnlyCount}</div>
        </div>
      </div>

      {/* Un-audited Businesses Section */}
      {unauditedBusinesses.length > 0 && (
        <div className="bg-white rounded-2xl border border-violet-200 shadow-card-sm overflow-hidden">
          <div className="p-4 border-b border-violet-100 bg-violet-50/60 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-violet-600" />
              <span className="text-sm font-bold text-violet-900">
                Ready to Audit ({unauditedBusinesses.length} businesses with websites)
              </span>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-200">
                <tr>
                  <th className="p-3">Business</th>
                  <th className="p-3">City</th>
                  <th className="p-3">Website</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {unauditedBusinesses.slice(0, 20).map((b: any) => (
                  <tr key={b.id} className="hover:bg-slate-50 transition">
                    <td className="p-3 font-semibold text-slate-900">{b.name}</td>
                    <td className="p-3 text-slate-500">{b.city || "—"}</td>
                    <td className="p-3">
                      <a
                        href={b.website?.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:underline font-mono text-[11px] flex items-center gap-1"
                      >
                        {b.website?.domain || b.website?.url}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleTriggerAudit(b.id)}
                        disabled={auditingId === b.id}
                        className="px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 text-white font-bold text-[11px] transition disabled:opacity-60 flex items-center gap-1.5 ml-auto"
                      >
                        <BarChart2 className="w-3.5 h-3.5" />
                        {auditingId === b.id ? "Auditing..." : "Run Audit"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-card-sm">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 flex items-center gap-1 mr-2">
            <Filter className="w-3.5 h-3.5 text-indigo-600" />
            Filter by Recommendation:
          </span>
          {[
            { key: "ALL", label: "All Audits", color: "bg-slate-700 text-white" },
            { key: "URGENT", label: "🔴 Urgent", color: "bg-rose-600 text-white" },
            { key: "RECOMMENDED", label: "🟡 Recommended", color: "bg-amber-500 text-white" },
            { key: "SEO_ONLY", label: "🟢 SEO Only", color: "bg-emerald-600 text-white" },
            { key: "GOOD", label: "✅ Healthy", color: "bg-blue-600 text-white" },
          ].map((f) => (
            <button
              key={f.key}
              onClick={() => setFilterRec(f.key)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                filterRec === f.key
                  ? f.color + " shadow-sm"
                  : "bg-slate-100 hover:bg-slate-200 text-slate-700"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Audits Table */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white p-5 rounded-2xl border border-slate-200 animate-pulse h-16" />
          ))}
        </div>
      ) : audits.length === 0 ? (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-3">
          <BarChart2 className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="font-bold text-slate-700 font-display">No Audits Yet</h3>
          <p className="text-sm text-slate-500">
            Click &quot;Run Audit&quot; on any business with a website above to start the audit engine.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-card-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-200">
                <tr>
                  <th className="p-4">Business</th>
                  <th className="p-4">Website</th>
                  <th className="p-4">Redesign Score</th>
                  <th className="p-4">Mobile Speed</th>
                  <th className="p-4">Technical</th>
                  <th className="p-4">Issues</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {audits.map((a) => (
                  <tr key={a.audit_id} className="hover:bg-slate-50/80 transition">
                    <td className="p-4">
                      <div className="font-bold text-slate-900">{a.business_name}</div>
                      {a.business_city && <div className="text-slate-400 text-[11px]">{a.business_city}</div>}
                    </td>
                    <td className="p-4">
                      <a
                        href={a.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:underline font-mono text-[11px] flex items-center gap-1"
                      >
                        {a.website_domain}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                    <td className="p-4">
                      <RedesignBadge recommendation={a.redesign_recommendation} score={a.redesign_score} />
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <ScoreGauge score={a.pagespeed_mobile_score} label="" />
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-1.5">
                        {a.https_enabled ? (
                          <Shield className="w-4 h-4 text-emerald-600" title="HTTPS ✓" />
                        ) : (
                          <ShieldOff className="w-4 h-4 text-rose-500" title="No HTTPS ✗" />
                        )}
                        <Smartphone
                          className={`w-4 h-4 ${a.responsive_mobile ? "text-emerald-600" : "text-rose-500"}`}
                          title={a.responsive_mobile ? "Mobile Friendly ✓" : "Not Mobile Friendly ✗"}
                        />
                        <Zap
                          className={`w-4 h-4 ${a.cta_visible ? "text-emerald-600" : "text-amber-400"}`}
                          title={a.cta_visible ? "CTA Present ✓" : "No CTA ✗"}
                        />
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                        <AlertTriangle className="w-3 h-3" />
                        {a.issues_count} issues
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => setSelectedItem(a)}
                          className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-[11px] transition"
                        >
                          View Report
                        </button>
                        <button
                          onClick={() => handleTriggerAudit(a.business_id)}
                          disabled={auditingId === a.business_id}
                          className="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[11px] border border-slate-200 transition disabled:opacity-50"
                        >
                          {auditingId === a.business_id ? "..." : "Re-audit"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Audit Detail Modal */}
      {selectedItem && (
        <AuditDetailModal
          item={selectedItem}
          audit={selectedAudit}
          onClose={() => setSelectedItem(null)}
        />
      )}
    </div>
  );
}

export default function AuditEnginePage() {
  return (
    <Suspense
      fallback={
        <div className="p-8 text-center text-slate-500 font-medium">
          Loading Website Audit Engine...
        </div>
      }
    >
      <AuditEngineContent />
    </Suspense>
  );
}
