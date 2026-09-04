const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type TargetStatus = "DRAFT" | "ACTIVE" | "INACTIVE" | "CANCELLED";
export type TargetRunStatus = "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED";
export type OpportunityType = 
  | "NEW_WEBSITE"
  | "WEBSITE_REDESIGN"
  | "SEO"
  | "LOCAL_SEO"
  | "REDESIGN_PLUS_SEO"
  | "SOCIAL_TO_WEBSITE"
  | "CONVERSION_OPTIMIZATION"
  | "COMPETITOR_GAP"
  | "MANUAL_REVIEW";

export interface FilterDefinition {
  min_revenue?: number | null;
  max_revenue?: number | null;
  min_employees?: number | null;
  max_employees?: number | null;
  technologies?: string[];
  keywords?: string[];
}

export interface SourceConfiguration {
  enabled_sources?: string[];
  max_results_limit?: number;
  rate_limit_per_minute?: number;
  timeout_seconds?: number;
}

export interface TargetCreatePayload {
  name: string;
  niche: string;
  sub_niche?: string;
  geography: string;
  filters?: FilterDefinition;
  opportunity_types: OpportunityType[];
  source_configuration?: SourceConfiguration;
}

export interface TargetUpdatePayload {
  name?: string;
  niche?: string;
  sub_niche?: string;
  geography?: string;
  status?: TargetStatus;
  filters?: FilterDefinition;
  opportunity_types?: OpportunityType[];
  source_configuration?: SourceConfiguration;
}

export interface Target {
  id: string;
  name: string;
  niche: string;
  sub_niche?: string | null;
  geography: string;
  status: TargetStatus;
  filters: FilterDefinition;
  opportunity_types: OpportunityType[];
  source_configuration: SourceConfiguration;
  created_by_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TargetRun {
  id: string;
  target_id: string;
  status: TargetRunStatus;
  total_discovered: number;
  total_verified: number;
  total_qualified: number;
  total_human_review: number;
  total_outreach_ready: number;
  started_at?: string | null;
  completed_at?: string | null;
  error_log?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `HTTP Error ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        if (typeof errorData.detail === "string") {
          errorMsg = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMsg = errorData.detail.map((e: any) => e.msg || JSON.stringify(e)).join(", ");
        }
      }
    } catch {
      // Ignore JSON parse errors
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export async function fetchTargets(params?: { status?: string; search?: string }): Promise<Target[]> {
  const query = new URLSearchParams();
  if (params?.status && params.status !== "ALL") {
    query.append("status", params.status);
  }
  if (params?.search) {
    query.append("search", params.search);
  }
  
  const url = `${API_BASE_URL}/api/v1/targets${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, {
    cache: "no-store",
    headers: { "Accept": "application/json" }
  });
  return handleResponse<Target[]>(res);
}

export async function fetchTarget(id: string): Promise<Target> {
  const res = await fetch(`${API_BASE_URL}/api/v1/targets/${id}`, {
    cache: "no-store",
    headers: { "Accept": "application/json" }
  });
  return handleResponse<Target>(res);
}

export async function createTarget(payload: TargetCreatePayload): Promise<Target> {
  const res = await fetch(`${API_BASE_URL}/api/v1/targets`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return handleResponse<Target>(res);
}

export async function updateTarget(id: string, payload: TargetUpdatePayload): Promise<Target> {
  const res = await fetch(`${API_BASE_URL}/api/v1/targets/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return handleResponse<Target>(res);
}

export async function deleteTarget(id: string): Promise<{ message: string; target: Target }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/targets/${id}`, {
    method: "DELETE",
    headers: { "Accept": "application/json" }
  });
  return handleResponse<{ message: string; target: Target }>(res);
}

export async function triggerTargetRun(targetId: string): Promise<TargetRun> {
  const res = await fetch(`${API_BASE_URL}/api/v1/targets/${targetId}/runs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
  });
  return handleResponse<TargetRun>(res);
}

export async function fetchTargetRuns(targetId: string): Promise<TargetRun[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/targets/${targetId}/runs`, {
    cache: "no-store",
    headers: { "Accept": "application/json" }
  });
  return handleResponse<TargetRun[]>(res);
}

export async function fetchAllTargetRuns(): Promise<TargetRun[]> {
  // Utility for total runs metric across targets
  const targets = await fetchTargets({ status: "ALL" });
  const allRunsNested = await Promise.all(
    targets.map((t) => fetchTargetRuns(t.id).catch(() => []))
  );
  return allRunsNested.flat();
}
