const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ComponentHealth {
  status: "healthy" | "unhealthy" | "unknown";
  latency_ms: number;
  error?: string;
}

export interface DetailedHealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  services: {
    database: ComponentHealth;
    redis: ComponentHealth;
  };
}

export async function fetchLiveness(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/healthz`, {
    cache: "no-store",
    headers: {
      "Accept": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error(`Liveness probe failed with status ${res.status}`);
  }

  return res.json();
}

export async function fetchSystemHealth(): Promise<DetailedHealthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/health`, {
    cache: "no-store",
    headers: {
      "Accept": "application/json",
    },
  });

  if (!res.ok && res.status !== 503) {
    throw new Error(`Health probe failed with status ${res.status}`);
  }

  return res.json();
}
