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
  Clock, 
  Activity, 
  Zap,
  Layers,
  ShieldAlert,
  Terminal
} from "lucide-react";

export default function SystemStatusPage() {
  const {
    data: healthData,
    isLoading,
    isError,
    error,
    refetch,
    isFetching
  } = useQuery<DetailedHealthResponse>({
    queryKey: ["systemHealth"],
    queryFn: fetchSystemHealth,
    refetchInterval: 5000, // Auto-refresh every 5 seconds
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
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-indigo-500/20 bg-gradient-to-r from-indigo-950/40 via-surface to-background relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                Phase 0 Verified
              </span>
              <span className="text-xs text-gray-400">Architecture: <strong className="text-gray-200">FastAPI Modular Monolith</strong></span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
              Infrastructure & System Components
            </h1>
            <p className="text-sm text-gray-400 max-w-2xl leading-relaxed">
              Real-time health probes monitoring backend API runtime, PostgreSQL persistent database connectivity, and Redis task broker latency.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition shadow-lg shadow-indigo-600/20 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Probes</span>
            </button>
          </div>
        </div>
      </div>

      {/* System Status Summary Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Overall Status Card */}
        <div className="glass-panel p-5 rounded-xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs text-gray-400 font-medium">Overall System</span>
            <div className="flex items-center gap-2">
              {isLoading ? (
                <div className="h-6 w-24 bg-gray-800 animate-pulse rounded"></div>
              ) : isSystemHealthy ? (
                <span className="text-lg font-bold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-5 h-5" /> Operational
                </span>
              ) : (
                <span className="text-lg font-bold text-rose-400 flex items-center gap-1.5">
                  <XCircle className="w-5 h-5" /> Degraded
                </span>
              )}
            </div>
          </div>
          <div className={`p-3 rounded-xl ${isSystemHealthy ? "bg-emerald-950/60 text-emerald-400" : "bg-rose-950/60 text-rose-400"}`}>
            <Activity className="w-6 h-6" />
          </div>
        </div>

        {/* Liveness Probe Card */}
        <div className="glass-panel p-5 rounded-xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs text-gray-400 font-medium">API Liveness (`/healthz`)</span>
            <div className="text-lg font-bold text-gray-100 flex items-center gap-2 font-mono">
              {livenessData?.status === "ok" ? (
                <span className="text-emerald-400 text-base">200 OK</span>
              ) : (
                <span className="text-gray-500 text-base">Checking...</span>
              )}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-indigo-950/60 text-indigo-400">
            <Zap className="w-6 h-6" />
          </div>
        </div>

        {/* Database Latency */}
        <div className="glass-panel p-5 rounded-xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs text-gray-400 font-medium">Postgres Latency</span>
            <div className="text-lg font-bold text-gray-100 font-mono">
              {dbHealth?.latency_ms !== undefined ? (
                <span className="text-emerald-400">{dbHealth.latency_ms} ms</span>
              ) : (
                <span className="text-gray-500">--</span>
              )}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-blue-950/60 text-blue-400">
            <Database className="w-6 h-6" />
          </div>
        </div>

        {/* Redis Latency */}
        <div className="glass-panel p-5 rounded-xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs text-gray-400 font-medium">Redis Latency</span>
            <div className="text-lg font-bold text-gray-100 font-mono">
              {redisHealth?.latency_ms !== undefined ? (
                <span className="text-emerald-400">{redisHealth.latency_ms} ms</span>
              ) : (
                <span className="text-gray-500">--</span>
              )}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-amber-950/60 text-amber-400">
            <Cpu className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Component Detailed Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-200 flex items-center gap-2">
          <Layers className="w-5 h-5 text-indigo-400" />
          <span>System Component Cards</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Backend API */}
          <div className="glass-panel glass-panel-hover p-6 rounded-2xl space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    <Server className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-base text-gray-100">Backend API</h4>
                    <span className="text-xs text-gray-400">FastAPI Async Engine</span>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800/50 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                  Active
                </span>
              </div>

              <p className="text-xs text-gray-400 leading-relaxed">
                Processes API requests, manages request IDs (`X-Request-ID`), CORS controls, and executes database queries via SQLAlchemy 2.0.
              </p>
            </div>

            <div className="pt-4 border-t border-gray-800 space-y-2 text-xs">
              <div className="flex justify-between text-gray-400">
                <span>Liveness Probe:</span>
                <span className="text-emerald-400 font-mono font-medium">/healthz (200 OK)</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Application API:</span>
                <span className="text-indigo-400 font-mono font-medium">/api/v1/health</span>
              </div>
            </div>
          </div>

          {/* Card 2: PostgreSQL Database */}
          <div className="glass-panel glass-panel-hover p-6 rounded-2xl space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    <Database className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-base text-gray-100">PostgreSQL</h4>
                    <span className="text-xs text-gray-400">Driver: asyncpg</span>
                  </div>
                </div>
                {dbHealth?.status === "healthy" ? (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800/50">
                    Healthy
                  </span>
                ) : (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-950 text-rose-400 border border-rose-800/50">
                    Unhealthy
                  </span>
                )}
              </div>

              <p className="text-xs text-gray-400 leading-relaxed">
                Relational persistence engine storing targets, businesses, verifications, audits, and audit trails with UUID primary keys.
              </p>
            </div>

            <div className="pt-4 border-t border-gray-800 space-y-2 text-xs">
              <div className="flex justify-between text-gray-400">
                <span>Connection Check:</span>
                <span className="text-gray-200 font-mono">SELECT 1</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Query Latency:</span>
                <span className="text-emerald-400 font-mono font-medium">
                  {dbHealth?.latency_ms ? `${dbHealth.latency_ms} ms` : "Error"}
                </span>
              </div>
            </div>
          </div>

          {/* Card 3: Redis Cache & Worker Queue */}
          <div className="glass-panel glass-panel-hover p-6 rounded-2xl space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    <Cpu className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-base text-gray-100">Redis & Celery</h4>
                    <span className="text-xs text-gray-400">Task Broker & Cache</span>
                  </div>
                </div>
                {redisHealth?.status === "healthy" ? (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800/50">
                    Healthy
                  </span>
                ) : (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-950 text-rose-400 border border-rose-800/50">
                    Unhealthy
                  </span>
                )}
              </div>

              <p className="text-xs text-gray-400 leading-relaxed">
                Asynchronous task queue broker backing Celery workers for discovery, entity resolution, web verification, and scoring.
              </p>
            </div>

            <div className="pt-4 border-t border-gray-800 space-y-2 text-xs">
              <div className="flex justify-between text-gray-400">
                <span>Ping Test:</span>
                <span className="text-gray-200 font-mono">REDIS PING</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Ping Latency:</span>
                <span className="text-emerald-400 font-mono font-medium">
                  {redisHealth?.latency_ms ? `${redisHealth.latency_ms} ms` : "Error"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Live Json Diagnostics Panel */}
      <div className="glass-panel p-6 rounded-2xl space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-200">
            <Terminal className="w-4 h-4 text-indigo-400" />
            <span>Live Health Response Payload (`/api/v1/health`)</span>
          </div>
          <span className="text-xs font-mono text-gray-500">
            Last Updated: {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleTimeString() : "--"}
          </span>
        </div>

        <pre className="bg-gray-950/80 p-4 rounded-xl text-xs text-emerald-400 font-mono overflow-x-auto border border-gray-800/80 leading-relaxed">
          {isLoading ? "// Querying health endpoint..." : JSON.stringify(healthData, null, 2)}
        </pre>
      </div>
    </div>
  );
}
