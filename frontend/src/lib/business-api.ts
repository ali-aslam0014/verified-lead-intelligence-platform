const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface WebsiteData {
  id: string;
  url: string;
  domain: string;
  status: string;
}

export interface ContactData {
  id: string;
  type: string;
  value: string;
  normalized_value: string;
  validity_status: string;
  confidence: number;
}

export interface SourceRecordData {
  id: string;
  source_name: string;
  source_identifier: string;
  raw_data: Record<string, any>;
  observed_at: string;
}

export interface DiscoveredBusiness {
  id: string;
  name: string;
  normalized_name: string;
  category?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  postal_code?: string | null;
  phone?: string | null;
  lifecycle_status: string;
  business_confidence: number;
  website?: WebsiteData | null;
  contacts: ContactData[];
  source_records_count: number;
  source_records?: SourceRecordData[];
  created_at: string;
  updated_at: string;
}

export interface TargetRunProgress {
  run_id: string;
  target_id: string;
  status: "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED";
  progress_percentage: number;
  step_message: string;
  total_discovered: number;
  total_verified: number;
  started_at?: string | null;
  completed_at?: string | null;
  error_log?: Record<string, any>;
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
      // Ignore JSON parse error
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export async function fetchBusinesses(params?: { search?: string; city?: string; status?: string }): Promise<DiscoveredBusiness[]> {
  const query = new URLSearchParams();
  if (params?.search) query.append("search", params.search);
  if (params?.city) query.append("city", params.city);
  if (params?.status) query.append("status", params.status);

  const url = `${API_BASE_URL}/api/v1/businesses${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  return handleResponse<DiscoveredBusiness[]>(res);
}

export async function fetchBusinessDetail(id: string): Promise<DiscoveredBusiness> {
  const res = await fetch(`${API_BASE_URL}/api/v1/businesses/${id}`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  return handleResponse<DiscoveredBusiness>(res);
}

export async function fetchRunProgress(targetId: string, runId: string): Promise<TargetRunProgress> {
  const res = await fetch(`${API_BASE_URL}/api/v1/targets/${targetId}/runs/${runId}/progress`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  return handleResponse<TargetRunProgress>(res);
}
