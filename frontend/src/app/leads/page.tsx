"use client";

import { useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetchBusinesses, fetchBusinessDetail, DiscoveredBusiness } from "@/lib/business-api";
import { fetchBusinessVerificationSummary, fetchBusinessEvidence, triggerBusinessVerification, EvidenceItem, VerificationSummary } from "@/lib/verification-api";
import { fetchBusinessOpportunities, triggerBusinessOpportunityAnalysis, OpportunityItem } from "@/lib/opportunity-api";
import { EvidenceDrawer } from "@/components/verification/EvidenceDrawer";
import { ConflictBanner } from "@/components/verification/ConflictBanner";
import { WhyThisLeadModal } from "@/components/opportunities/WhyThisLead";
import { 
  Building2, 
  Search, 
  Globe, 
  Phone, 
  MapPin, 
  RefreshCw, 
  AlertTriangle, 
  ShieldCheck, 
  Database, 
  ExternalLink,
  X,
  Code,
  Star,
  Flame,
  Linkedin,
  Facebook,
  Instagram,
  Filter,
  Target as TargetIcon,
  CheckCircle2,
  HelpCircle,
  AlertCircle,
  Lightbulb,
  Zap
} from "lucide-react";

function LeadDirectoryContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const initialTargetId = searchParams.get("target_id") || "";
  const initialSearch = searchParams.get("search") || "";
  const initialCity = searchParams.get("city") || "";

  const [targetIdFilter, setTargetIdFilter] = useState(initialTargetId);
  const [search, setSearch] = useState(initialSearch);
  const [cityFilter, setCityFilter] = useState(initialCity);
  const [opportunityFilter, setOpportunityFilter] = useState<"ALL" | "NO_WEBSITE" | "HAS_WEBSITE" | "TOP_RATED">("ALL");
  const [selectedBusinessId, setSelectedBusinessId] = useState<string | null>(null);

  const [evidenceDrawerOpen, setEvidenceDrawerOpen] = useState(false);
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([]);
  const [activeEvidenceBizName, setActiveEvidenceBizName] = useState("");
  const [verifyingBizId, setVerifyingBizId] = useState<string | null>(null);

  // Phase 4 Opportunity State
  const [whyThisLeadOpen, setWhyThisLeadOpen] = useState(false);
  const [activeWhyThisLeadBiz, setActiveWhyThisLeadBiz] = useState<{ id: string; name: string; city?: string; verifiedAt?: string } | null>(null);
  const [activeWhyThisLeadOpps, setActiveWhyThisLeadOpps] = useState<OpportunityItem[]>([]);
  const [analyzingBizId, setAnalyzingBizId] = useState<string | null>(null);

  // Businesses Query
  const {
    data: businesses,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useQuery<DiscoveredBusiness[]>({
    queryKey: ["businesses", search, cityFilter, targetIdFilter, opportunityFilter],
    queryFn: () => {
      const params: any = { search, city: cityFilter, target_id: targetIdFilter };
      if (opportunityFilter === "NO_WEBSITE") params.has_website = false;
      if (opportunityFilter === "HAS_WEBSITE") params.has_website = true;
      return fetchBusinesses(params);
    },
  });

  // Business Detail & Provenance Query (for active modal)
  const { data: businessDetail, isLoading: detailLoading } = useQuery<DiscoveredBusiness>({
    queryKey: ["businessDetail", selectedBusinessId],
    queryFn: () => fetchBusinessDetail(selectedBusinessId!),
    enabled: !!selectedBusinessId,
  });

  const { data: verSummary } = useQuery<VerificationSummary>({
    queryKey: ["verSummary", selectedBusinessId],
    queryFn: () => fetchBusinessVerificationSummary(selectedBusinessId!),
    enabled: !!selectedBusinessId,
  });

  async function handleOpenEvidence(bizId: string, bizName: string) {
    try {
      setActiveEvidenceBizName(bizName);
      const items = await fetchBusinessEvidence(bizId);
      setEvidenceItems(items);
      setEvidenceDrawerOpen(true);
    } catch (err) {
      console.error("Error opening evidence drawer:", err);
    }
  }

  async function handleRunSingleVerify(bizId: string) {
    try {
      setVerifyingBizId(bizId);
      await triggerBusinessVerification(bizId);
      await refetch();
    } catch (err) {
      console.error("Error verifying business:", err);
    } finally {
      setVerifyingBizId(null);
    }
  }

  async function handleOpenWhyThisLead(bizId: string, bizName: string, city?: string | null, verifiedAt?: string | null) {
    try {
      setActiveWhyThisLeadBiz({ id: bizId, name: bizName, city: city || undefined, verifiedAt: verifiedAt || undefined });
      const opps = await fetchBusinessOpportunities(bizId);
      setActiveWhyThisLeadOpps(opps);
      setWhyThisLeadOpen(true);
    } catch (err) {
      console.error("Error opening Why This Lead modal:", err);
    }
  }

  async function handleAnalyzeOpps(bizId: string) {
    try {
      setAnalyzingBizId(bizId);
      await triggerBusinessOpportunityAnalysis(bizId);
      await refetch();
    } catch (err) {
      console.error("Error analyzing opportunities:", err);
    } finally {
      setAnalyzingBizId(null);
    }
  }

  // Filtered Leads Client Processing for TOP_RATED tab
  const filteredBusinesses = (businesses || []).filter((b) => {
    if (opportunityFilter === "TOP_RATED") {
      return (b.rating || 0) >= 4.5;
    }
    return true;
  });

  // KPI Calculations
  const totalBusinesses = businesses?.length || 0;
  const noWebsitesCount = businesses?.filter((b) => !b.has_website && !b.website?.url).length || 0;
  const websitesFound = businesses?.filter((b) => b.has_website || b.website?.url).length || 0;
  const phonesFound = businesses?.filter((b) => b.phone).length || 0;
  const totalSources = businesses?.reduce((acc, b) => acc + (b.source_records_count || 0), 0) || 0;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Directory Page Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-indigo-50/80 to-emerald-50/50 rounded-full blur-3xl opacity-60 pointer-events-none"></div>

        <div className="space-y-2 relative z-10">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              Live Google My Business Console
            </span>
            <span className="text-xs text-slate-500 font-medium">Real-World Lead Discovery</span>

            {targetIdFilter && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 animate-pulse">
                <TargetIcon className="w-3.5 h-3.5 text-emerald-600" />
                <span>Campaign Filter Active (ID: {targetIdFilter.slice(0, 8)}...)</span>
                <button
                  onClick={() => {
                    setTargetIdFilter("");
                    setCityFilter("");
                    setSearch("");
                    router.push("/leads");
                  }}
                  className="hover:bg-emerald-200/50 p-0.5 rounded transition ml-1"
                  title="Clear Campaign Filter"
                >
                  <X className="w-3.5 h-3.5 text-emerald-700" />
                </button>
              </span>
            )}
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight font-display">
            Discovered Lead Directory
          </h1>
          <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
            Real-world lead intelligence engine. Extracts business names, phone numbers, Google ratings, website status (Yes/No), and social links with full provenance.
          </p>
        </div>

        <div className="flex items-center gap-3 relative z-10">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs border border-slate-200 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? "animate-spin" : ""}`} />
            <span>Refresh Directory</span>
          </button>
        </div>
      </div>

      {/* Statistics KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        {/* KPI 1: Total Discovered */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Leads</span>
            <div className="text-2xl font-bold text-slate-900 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : totalBusinesses}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200">
            <Building2 className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 2: No Website Opportunities (HOT LEADS) */}
        <div className="bg-white p-5 rounded-2xl border border-rose-200 shadow-card-sm flex items-center justify-between relative overflow-hidden">
          <div className="space-y-1 z-10">
            <span className="text-xs font-semibold text-rose-600 uppercase tracking-wider flex items-center gap-1">
              <Flame className="w-3.5 h-3.5 text-rose-600" />
              <span>No Website Leads</span>
            </span>
            <div className="text-2xl font-bold text-rose-700 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : noWebsitesCount}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 z-10">
            <Flame className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 3: Phone Contacts */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Phone Numbers</span>
            <div className="text-2xl font-bold text-blue-700 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : phonesFound}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-blue-50 text-blue-700 border border-blue-200">
            <Phone className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 4: Provenance Records */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Provenance Sources</span>
            <div className="text-2xl font-bold text-purple-700 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : totalSources}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-purple-50 text-purple-700 border border-purple-200">
            <Database className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Filter and Opportunity Tabs */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-card-sm space-y-4">
        {/* Opportunity Filter Tabs */}
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3">
          <span className="text-xs font-semibold text-slate-500 mr-2 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5 text-indigo-600" />
            <span>Opportunity Signal:</span>
          </span>

          <button
            onClick={() => setOpportunityFilter("ALL")}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
              opportunityFilter === "ALL"
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-slate-100 hover:bg-slate-200 text-slate-700"
            }`}
          >
            All Leads ({totalBusinesses})
          </button>

          <button
            onClick={() => setOpportunityFilter("NO_WEBSITE")}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 ${
              opportunityFilter === "NO_WEBSITE"
                ? "bg-rose-600 text-white shadow-sm"
                : "bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200"
            }`}
          >
            <Flame className="w-3.5 h-3.5" />
            <span>🔴 No Website Only ({noWebsitesCount})</span>
          </button>

          <button
            onClick={() => setOpportunityFilter("HAS_WEBSITE")}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 ${
              opportunityFilter === "HAS_WEBSITE"
                ? "bg-emerald-600 text-white shadow-sm"
                : "bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200"
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>🟢 Has Website ({websitesFound})</span>
          </button>

          <button
            onClick={() => setOpportunityFilter("TOP_RATED")}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 ${
              opportunityFilter === "TOP_RATED"
                ? "bg-amber-500 text-white shadow-sm"
                : "bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200"
            }`}
          >
            <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
            <span>⭐ Top Rated (4.5+)</span>
          </button>
        </div>

        {/* Search Inputs */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative w-full md:w-96">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by business name, city, phone..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
            />
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <input
              type="text"
              placeholder="Filter by city..."
              value={cityFilter}
              onChange={(e) => setCityFilter(e.target.value)}
              className="px-3.5 py-2 rounded-xl border border-slate-200 bg-white text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm animate-pulse space-y-3">
              <div className="h-5 w-48 bg-slate-200 rounded"></div>
              <div className="h-4 w-32 bg-slate-100 rounded"></div>
            </div>
          ))}
        </div>
      )}

      {/* Error State */}
      {isError && !isLoading && (
        <div className="bg-rose-50 border border-rose-200 p-6 rounded-2xl text-rose-900 space-y-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-rose-600 shrink-0" />
            <div>
              <h3 className="font-bold text-base font-display">Failed to Load Lead Directory</h3>
              <p className="text-xs text-rose-700">{(error as any)?.message || "Error fetching business leads."}</p>
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

      {/* Empty State */}
      {!isLoading && !isError && filteredBusinesses.length === 0 && (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 shadow-card-sm text-center space-y-4 max-w-xl mx-auto my-8">
          <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100 flex items-center justify-center mx-auto">
            <Building2 className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-xl font-bold text-slate-900 font-display">No Discovered Businesses Found</h3>
            <p className="text-sm text-slate-500">
              {search || cityFilter || opportunityFilter !== "ALL"
                ? "No lead records match your current filter settings."
                : "Trigger a discovery run from Target Directory to discover real Google Business listings."}
            </p>
          </div>
        </div>
      )}

      {/* Business Leads List / Table */}
      {!isLoading && !isError && filteredBusinesses.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-card-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-500 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="p-4">Business & Google Rating</th>
                  <th className="p-4">Address / Location</th>
                  <th className="p-4">Phone Number</th>
                  <th className="p-4">Verification Status</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredBusinesses.map((b) => {
                  const hasWebsite = b.has_website || !!b.website?.url;
                  const socialLinks = b.social_links || {};
                  const isVerifying = verifyingBizId === b.id;

                  return (
                    <tr key={b.id} className="hover:bg-slate-50/80 transition">
                      {/* Title & Rating */}
                      <td className="p-4">
                        <div className="space-y-1">
                          <span className="font-bold text-slate-900 text-sm font-display block">
                            {b.name}
                          </span>
                          <div className="flex items-center gap-2">
                            <span className="inline-block px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                              {b.category || "General Business"}
                            </span>
                            {b.rating && (
                              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                                <Star className="w-3 h-3 text-amber-500 fill-amber-500" />
                                {b.rating} ({b.review_count || 0} reviews)
                              </span>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Location */}
                      <td className="p-4">
                        <div className="flex items-center gap-1.5 text-slate-600">
                          <MapPin className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                          <span className="font-medium text-slate-800">
                            {b.address || b.city || "Location Recorded"}
                          </span>
                        </div>
                      </td>

                      {/* Phone */}
                      <td className="p-4 font-mono">
                        {b.phone ? (
                          <a
                            href={`tel:${b.phone}`}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 font-semibold transition text-xs"
                          >
                            <Phone className="w-3.5 h-3.5 shrink-0 text-blue-600" />
                            <span>{b.phone}</span>
                          </a>
                        ) : (
                          <span className="text-slate-400 italic">No Phone Listed</span>
                        )}
                      </td>

                      {/* Website Opportunity Status */}
                      <td className="p-4">
                        {!hasWebsite ? (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold bg-rose-100 text-rose-800 border border-rose-300 shadow-xs animate-pulse">
                            <Flame className="w-3.5 h-3.5 text-rose-600" />
                            <span>🔴 No Website (Hot Lead!)</span>
                          </span>
                        ) : (
                          <a
                            href={b.website?.url || "#"}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-200 font-mono text-[11px] font-semibold transition"
                          >
                            <Globe className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                            <span className="truncate max-w-[130px]">{b.website?.domain || "Website Live"}</span>
                            <ExternalLink className="w-3 h-3 text-emerald-500" />
                          </a>
                        )}
                      </td>

                      {/* Social Accounts */}
                      <td className="p-4">
                        <div className="flex items-center gap-1.5">
                          {socialLinks.linkedin && (
                            <a
                              href={socialLinks.linkedin}
                              target="_blank"
                              rel="noreferrer"
                              className="p-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 transition"
                              title="LinkedIn Profile"
                            >
                              <Linkedin className="w-3.5 h-3.5" />
                            </a>
                          )}
                          {socialLinks.facebook && (
                            <a
                              href={socialLinks.facebook}
                              target="_blank"
                              rel="noreferrer"
                              className="p-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-800 border border-blue-200 transition"
                              title="Facebook Page"
                            >
                              <Facebook className="w-3.5 h-3.5" />
                            </a>
                          )}
                          {socialLinks.instagram && (
                            <a
                              href={socialLinks.instagram}
                              target="_blank"
                              rel="noreferrer"
                              className="p-1.5 rounded-lg bg-pink-50 hover:bg-pink-100 text-pink-700 border border-pink-200 transition"
                              title="Instagram Account"
                            >
                              <Instagram className="w-3.5 h-3.5" />
                            </a>
                          )}
                          {!socialLinks.linkedin && !socialLinks.facebook && !socialLinks.instagram && (
                            <span className="text-slate-400 text-[11px] italic">None listed</span>
                          )}
                        </div>
                      </td>

                      {/* Phase 3 Verification Status */}
                      <td className="p-4">
                        {b.lifecycle_status === "VERIFIED" && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            <span>VERIFIED</span>
                          </span>
                        )}
                        {b.lifecycle_status === "HUMAN_REVIEW" && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-purple-100 text-purple-800 border border-purple-300">
                            <AlertCircle className="w-3.5 h-3.5 text-purple-600" />
                            <span>HUMAN REVIEW</span>
                          </span>
                        )}
                        {b.lifecycle_status === "REVERIFY_REQUIRED" && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                            <span>REVERIFY</span>
                          </span>
                        )}
                        {b.lifecycle_status !== "VERIFIED" && b.lifecycle_status !== "HUMAN_REVIEW" && b.lifecycle_status !== "REVERIFY_REQUIRED" && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                            <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                            <span>DISCOVERED</span>
                          </span>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="p-4 text-right">
                        <div className="flex items-center justify-end gap-1.5 flex-wrap">
                          <button
                            onClick={() => handleOpenWhyThisLead(b.id, b.name, b.city, b.updated_at)}
                            className="px-2.5 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 font-semibold text-[11px] border border-amber-200 transition flex items-center gap-1"
                            title="Why is this a lead? View Sales Intelligence Pitch Brief"
                          >
                            <Lightbulb className="w-3.5 h-3.5 text-amber-600" />
                            <span>Why Lead?</span>
                          </button>
                          <button
                            onClick={() => handleAnalyzeOpps(b.id)}
                            disabled={analyzingBizId === b.id}
                            className="px-2.5 py-1 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-700 font-semibold text-[11px] border border-purple-200 transition disabled:opacity-50 flex items-center gap-1"
                            title="Run Phase 4 Opportunity Intelligence Engine"
                          >
                            <Zap className="w-3.5 h-3.5 text-purple-600" />
                            <span>{analyzingBizId === b.id ? "Analyzing..." : "Analyze"}</span>
                          </button>
                          <button
                            onClick={() => handleRunSingleVerify(b.id)}
                            disabled={isVerifying}
                            className="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold text-[11px] border border-blue-200 transition disabled:opacity-50"
                            title="Run Phase 3 Verification Engine"
                          >
                            {isVerifying ? "Verifying..." : "⚡ Verify"}
                          </button>
                          <button
                            onClick={() => handleOpenEvidence(b.id, b.name)}
                            className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[11px] border border-slate-200 transition"
                            title="View Raw Evidence Log"
                          >
                            📋 Log
                          </button>
                          <button
                            onClick={() => setSelectedBusinessId(b.id)}
                            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-semibold text-[11px] transition"
                            title="View Full Audit Payload"
                          >
                            Audit
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Raw Provenance Audit Modal */}
      {selectedBusinessId && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-3xl w-full max-h-[85vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-slate-900 font-display">
                    {businessDetail?.name || "Business Provenance Audit"}
                  </h3>
                  <span className="text-xs text-slate-500 font-mono">
                    ID: {selectedBusinessId}
                  </span>
                </div>
              </div>

              <button
                onClick={() => setSelectedBusinessId(null)}
                className="p-1.5 rounded-lg hover:bg-slate-200 text-slate-500 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6">
              {detailLoading ? (
                <div className="space-y-3 py-8 text-center text-slate-500 text-sm">
                  <RefreshCw className="w-6 h-6 animate-spin mx-auto text-indigo-600" />
                  <span>Loading raw provenance payloads...</span>
                </div>
              ) : (
                <>
                  {/* Phase 3 Conflict Banner */}
                  {verSummary?.summary?.conflicts && verSummary.summary.conflicts.length > 0 && (
                    <ConflictBanner conflicts={verSummary.summary.conflicts} />
                  )}

                  {/* Canonical Summary */}
                  <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
                    <div>
                      <span className="text-slate-500 font-semibold block">Canonical Title:</span>
                      <span className="font-bold text-slate-900">{businessDetail?.name}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 font-semibold block">Normalized Name:</span>
                      <span className="font-mono text-slate-800">{businessDetail?.normalized_name}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 font-semibold block">Phone Number:</span>
                      <span className="font-mono text-slate-800">{businessDetail?.phone || "None"}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 font-semibold block">Website Status:</span>
                      <span className="font-semibold text-slate-800">
                        {businessDetail?.has_website ? `🟢 ${businessDetail?.website?.domain || "Website Live"}` : "🔴 No Website (Hot Lead)"}
                      </span>
                    </div>
                  </div>

                  {/* Verbatim Source Records JSON */}
                  <div className="space-y-3">
                    <h4 className="font-bold text-sm text-slate-900 font-display flex items-center gap-2">
                      <Code className="w-4 h-4 text-indigo-600" />
                      <span>Verbatim Provider API Source Records ({businessDetail?.source_records?.length || 0})</span>
                    </h4>

                    {(businessDetail?.source_records || []).map((sr: any, idx: number) => (
                      <div key={sr.id || idx} className="bg-slate-900 rounded-xl p-4 border border-slate-800 space-y-2">
                        <div className="flex justify-between items-center text-xs border-b border-slate-800 pb-2">
                          <span className="font-mono text-emerald-400 font-bold">
                            Source: {sr.source_name} ({sr.source_identifier})
                          </span>
                          <span className="text-slate-400 text-[10px] font-mono">
                            Observed: {new Date(sr.observed_at).toLocaleString()}
                          </span>
                        </div>
                        <pre className="text-xs text-indigo-300 font-mono overflow-x-auto pt-2 leading-relaxed">
                          {JSON.stringify(sr.raw_data, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Phase 3 Evidence Slide-over Drawer */}
      <EvidenceDrawer
        isOpen={evidenceDrawerOpen}
        onClose={() => setEvidenceDrawerOpen(false)}
        businessName={activeEvidenceBizName}
        evidenceItems={evidenceItems}
      />

      {/* Phase 4 Why This Lead Pitch Brief Modal */}
      <WhyThisLeadModal
        isOpen={whyThisLeadOpen}
        onClose={() => setWhyThisLeadOpen(false)}
        businessName={activeWhyThisLeadBiz?.name || "Business"}
        city={activeWhyThisLeadBiz?.city}
        verifiedAt={activeWhyThisLeadBiz?.verifiedAt}
        opportunities={activeWhyThisLeadOpps}
      />
    </div>
  );
}

export default function LeadDirectoryPage() {
  return (
    <Suspense
      fallback={
        <div className="p-8 text-center text-slate-500 font-medium font-sans">
          Loading Lead Directory Console...
        </div>
      }
    >
      <LeadDirectoryContent />
    </Suspense>
  );
}
