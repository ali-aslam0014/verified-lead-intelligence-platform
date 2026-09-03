"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchSystemHealth, fetchLiveness, DetailedHealthResponse } from "@/lib/api-client";
import { 
  Database, 
  Server, 
  Cpu, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Activity, 
  Zap,
  Layers,
  Terminal,
  ShieldCheck,
  Check
} from "lucide-react";

export default function SystemStatusPage() {
  const {
    data: healthData,
    isLoading,
    isError,
    refetch,
    isFetching
  } = useQuery<DetailedHealthResponse>({
    queryKey: ["systemHealth"],
    queryFn: fetchSystemHealth,
    refetchInterval: 5000,
  });

  const { data: livenessData } = useQuery({
    queryKey: ["livenessProbe"],
    queryFn: fetchLiveness,
    refetchInterval: 5000,
  });

  const isSystemHealthy = healthData?.status === "healthy";
  const dbHealth = healthData?.services?.database;
  const redisHealth = healthData?.services?.redis;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Premium Light SaaS Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-indigo-50 to-emerald-50 rounded-full blur-2xl opacity-70 pointer-events-none"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200/80">
                Phase 1A Standardized
              </span>
              <span className="text-xs text-slate-500 font-medium">Architecture: <strong className="text-slate-900 font-semibold">FastAPI Modular Monolith</strong></span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
              Infrastructure & System Components
            </h1>
            <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
              Real-time component health probes monitoring FastAPI backend runtime, PostgreSQL database connectivity, and Redis task broker response latencies.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm transition shadow-md shadow-indigo-500/20 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Component Health</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        {/* Card 1: Overall System */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Overall System</span>
            <div className="flex items-center gap-2">
              {isLoading ? (
                <div className="h-6 w-24 bg-slate-100 animate-pulse rounded"></div>
              ) : isSystemHealthy ? (
                <span className="text-lg font-bold text-emerald-700 flex items-center gap-1.5">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" /> Operational
                </span>
              ) : (
                <span className="text-lg font-bold text-rose-700 flex items-center gap-1.5">
                  <XCircle className="w-5 h-5 text-rose-600" /> Degraded
                </span>
              )}
            </div>
          </div>
          <div className={`p-3 rounded-xl ${isSystemHealthy ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-rose-50 text-rose-700 border border-rose-200"}`}>
            <Activity className="w-6 h-6" />
          </div>
        </div>

        {/* Card 2: Liveness Probe */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">API Liveness</span>
            <div className="text-lg font-bold text-slate-900 flex items-center gap-2 font-mono">
              {livenessData?.status === "ok" ? (
                <span className="text-emerald-700 text-base flex items-center gap-1 font-sans">
                  <Check className="w-4 h-4 text-emerald-600" /> 200 OK
                </span>
              ) : (
                <span className="text-slate-400 text-base font-sans">Checking...</span>
              )}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200">
            <Zap className="w-6 h-6" />
          </div>
        </div>

        {/* Card 3: Postgres Latency */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Postgres Latency</span>
            <div className="text-lg font-bold text-slate-900 font-mono">
              {dbHealth?.latency_ms !== undefined ? (
                <span className="text-emerald-700">{dbHealth.latency_ms} ms</span>
              ) : (
                <span className="text-slate-400">--</span>
              )}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-blue-50 text-blue-700 border border-blue-200">
            <Database className="w-6 h-6" />
          </div>
        </div>

        {/* Card 4: Redis Latency */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card-sm flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Redis Latency</span>
            <div className="text-lg font-bold text-slate-900 font-mono">
              {redisHealth?.latency_ms !== undefined ? (
                <span className="text-emerald-700">{redisHealth.latency_ms} ms</span>
              ) : (
                <span className="text-slate-400">--</span>
              )}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-amber-50 text-amber-700 border border-amber-200">
            <Cpu className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Component Detailed Cards Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2 tracking-tight">
          <Layers className="w-5 h-5 text-indigo-600" />
          <span>System Component Cards</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Backend API */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm hover:shadow-card-hover transition-all duration-200 flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200">
                    <Server className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-base text-slate-900">Backend API</h4>
                    <span className="text-xs text-slate-500 font-medium">FastAPI Async Engine</span>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  Active
                </span>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">
                Processes API requests, manages request IDs (`X-Request-ID`), CORS controls, and executes database queries via SQLAlchemy 2.0.
              </p>
            </div>

            <div className="pt-4 border-t border-slate-100 space-y-2 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Liveness Probe:</span>
                <span className="text-emerald-700 font-mono font-semibold">/healthz (200 OK)</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Application API:</span>
                <span className="text-indigo-700 font-mono font-semibold">/api/v1/health</span>
              </div>
            </div>
          </div>

          {/* Card 2: PostgreSQL Database */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm hover:shadow-card-hover transition-all duration-200 flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-blue-50 text-blue-700 border border-blue-200">
                    <Database className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-base text-slate-900">PostgreSQL</h4>
                    <span className="text-xs text-slate-500 font-medium">Driver: asyncpg</span>
                  </div>
                </div>
                {dbHealth?.status === "healthy" ? (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    Healthy
                  </span>
                ) : (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                    Unhealthy
                  </span>
                )}
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">
                Relational persistence engine storing targets, businesses, verifications, audits, and audit trails with UUID primary keys.
              </p>
            </div>

            <div className="pt-4 border-t border-slate-100 space-y-2 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Connection Check:</span>
                <span className="text-slate-800 font-mono font-medium">SELECT 1</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Query Latency:</span>
                <span className="text-emerald-700 font-mono font-semibold">
                  {dbHealth?.latency_ms ? `${dbHealth.latency_ms} ms` : "Error"}
                </span>
              </div>
            </div>
          </div>

          {/* Card 3: Redis Cache & Worker Queue */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm hover:shadow-card-hover transition-all duration-200 flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-amber-50 text-amber-700 border border-amber-200">
                    <Cpu className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-base text-slate-900">Redis & Celery</h4>
                    <span className="text-xs text-slate-500 font-medium">Task Broker & Cache</span>
                  </div>
                </div>
                {redisHealth?.status === "healthy" ? (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    Healthy
                  </span>
                ) : (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                    Unhealthy
                  </span>
                )}
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">
                Asynchronous task queue broker backing Celery workers for discovery, entity resolution, web verification, and scoring.
              </p>
            </div>

            <div className="pt-4 border-t border-slate-100 space-y-2 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Ping Test:</span>
                <span className="text-slate-800 font-mono font-medium">REDIS PING</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Ping Latency:</span>
                <span className="text-emerald-700 font-mono font-semibold">
                  {redisHealth?.latency_ms ? `${redisHealth.latency_ms} ms` : "Error"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Live JSON Diagnostics Panel */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-900">
            <Terminal className="w-4 h-4 text-indigo-600" />
            <span>Live Health Response Payload (`/api/v1/health`)</span>
          </div>
          <span className="text-xs font-mono text-slate-500">
            Last Updated: {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleTimeString() : "--"}
          </span>
        </div>

        <pre className="bg-slate-900 p-4 rounded-xl text-xs text-emerald-400 font-mono overflow-x-auto border border-slate-800 leading-relaxed">
          {isLoading ? "// Querying health endpoint..." : JSON.stringify(healthData, null, 2)}
        </pre>
      </div>
    </div>
  );
}
