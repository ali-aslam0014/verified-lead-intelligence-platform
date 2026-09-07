"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchBusinesses, fetchBusinessDetail, DiscoveredBusiness } from "@/lib/business-api";
import { 
  Building2, 
  Search, 
  Globe, 
  Phone, 
  MapPin, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2, 
  FileText, 
  ShieldCheck, 
  Database, 
  Layers, 
  ExternalLink,
  X,
  Code,
  Sparkles
} from "lucide-react";

export default function LeadDirectoryPage() {
  const [search, setSearch] = useState("");
  const [cityFilter, setCityFilter] = useState("");
  const [selectedBusinessId, setSelectedBusinessId] = useState<string | null>(null);

  // Businesses Query
  const {
    data: businesses,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useQuery<DiscoveredBusiness[]>({
    queryKey: ["businesses", search, cityFilter],
    queryFn: () => fetchBusinesses({ search, city: cityFilter }),
  });

  // Business Detail & Provenance Query (for active modal)
  const { data: businessDetail, isLoading: detailLoading } = useQuery<DiscoveredBusiness>({
    queryKey: ["businessDetail", selectedBusinessId],
    queryFn: () => fetchBusinessDetail(selectedBusinessId!),
    enabled: !!selectedBusinessId,
  });

  // KPI Calculations
  const totalBusinesses = businesses?.length || 0;
  const websitesFound = businesses?.filter((b) => b.website?.url).length || 0;
  const phonesFound = businesses?.filter((b) => b.phone).length || 0;
  const totalSources = businesses?.reduce((acc, b) => acc + (b.source_records_count || 0), 0) || 0;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Directory Page Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-indigo-50/80 to-emerald-50/50 rounded-full blur-3xl opacity-60 pointer-events-none"></div>

        <div className="space-y-2 relative z-10">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              Phase 2 Discovery Console
            </span>
            <span className="text-xs text-slate-500 font-medium">Canonical Business Records</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight font-display">
            Discovered Lead Directory
          </h1>
          <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
            Real multi-source lead entity directory. Stores deduplicated business entities, immutable source evidence, and domain metadata.
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
        {/* KPI 1: Discovered Entities */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Discovered Entities</span>
            <div className="text-2xl font-bold text-slate-900 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : totalBusinesses}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200">
            <Building2 className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 2: Websites Found */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Official Domains</span>
            <div className="text-2xl font-bold text-emerald-700 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : websitesFound}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200">
            <Globe className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 3: Verified Phones */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Phone Contacts</span>
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
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Provenance Evidence</span>
            <div className="text-2xl font-bold text-purple-700 font-display">
              {isLoading ? <span className="h-6 w-12 bg-slate-100 animate-pulse rounded inline-block"></span> : totalSources}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-purple-50 text-purple-700 border border-purple-200">
            <Database className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-card-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search leads by business name, city, phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
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
      {!isLoading && !isError && businesses?.length === 0 && (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 shadow-card-sm text-center space-y-4 max-w-xl mx-auto my-8">
          <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100 flex items-center justify-center mx-auto">
            <Building2 className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-xl font-bold text-slate-900 font-display">No Discovered Businesses Found</h3>
            <p className="text-sm text-slate-500">
              {search || cityFilter
                ? "No lead records match your search query. Try clearing search filters."
                : "Trigger a discovery run from Target Directory to discover real businesses with immutable provenance."}
            </p>
          </div>
        </div>
      )}

      {/* Business Leads List / Table */}
      {!isLoading && !isError && businesses && businesses.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-card-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-500 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="p-4">Business & Niche</th>
                  <th className="p-4">Location</th>
                  <th className="p-4">Phone / Contact</th>
                  <th className="p-4">Official Website</th>
                  <th className="p-4">Lifecycle Status</th>
                  <th className="p-4">Provenance Evidence</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {businesses.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-50/80 transition">
                    {/* Title */}
                    <td className="p-4">
                      <div className="space-y-1">
                        <span className="font-bold text-slate-900 text-sm font-display block">
                          {b.name}
                        </span>
                        <span className="inline-block px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                          {b.category || "General Business"}
                        </span>
                      </div>
                    </td>

                    {/* Location */}
                    <td className="p-4">
                      <div className="flex items-center gap-1.5 text-slate-600">
                        <MapPin className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span>
                          {b.city ? `${b.city}${b.state ? `, ${b.state}` : ""}` : b.address || "Location Recorded"}
                        </span>
                      </div>
                    </td>

                    {/* Phone */}
                    <td className="p-4 font-mono">
                      {b.phone ? (
                        <a href={`tel:${b.phone}`} className="flex items-center gap-1.5 text-indigo-600 hover:underline font-medium">
                          <Phone className="w-3.5 h-3.5 shrink-0" />
                          <span>{b.phone}</span>
                        </a>
                      ) : (
                        <span className="text-slate-400">No phone</span>
                      )}
                    </td>

                    {/* Website */}
                    <td className="p-4">
                      {b.website?.url ? (
                        <a
                          href={b.website.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-emerald-700 hover:underline font-mono text-[11px] font-semibold"
                        >
                          <Globe className="w-3.5 h-3.5 shrink-0 text-emerald-600" />
                          <span className="truncate max-w-[140px]">{b.website.domain}</span>
                          <ExternalLink className="w-3 h-3 text-slate-400" />
                        </a>
                      ) : (
                        <span className="text-slate-400 text-[11px] italic">Missing Website</span>
                      )}
                    </td>

                    {/* Status */}
                    <td className="p-4">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
                        {b.lifecycle_status}
                      </span>
                    </td>

                    {/* Provenance */}
                    <td className="p-4">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-purple-50 text-purple-700 border border-purple-200">
                        <ShieldCheck className="w-3 h-3 text-purple-600" />
                        {b.source_records_count} Records
                      </span>
                    </td>

                    {/* Action */}
                    <td className="p-4 text-right">
                      <button
                        onClick={() => setSelectedBusinessId(b.id)}
                        className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-700 font-semibold text-xs border border-slate-200 transition"
                      >
                        Provenance Audit
                      </button>
                    </td>
                  </tr>
                ))}
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
                      <span className="text-slate-500 font-semibold block">Official Domain:</span>
                      <span className="font-mono text-slate-800">{businessDetail?.website?.domain || "None"}</span>
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
    </div>
  );
}
