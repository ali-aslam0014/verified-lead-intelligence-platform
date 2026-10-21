const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1"
    ? "https://backend-sooty-one-32.vercel.app"
    : "http://localhost:8000");

export interface AuditIssue {
  code: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  points: number;
  description: string;
}

export interface WebsiteAuditResult {
  id: string;
  business_id: string;
  audit_status: string;

  // Technical
  https_enabled: boolean;
  responsive_mobile: boolean;
  cta_visible: boolean;
  contact_visible: boolean;
  schema_markup_present: boolean;
  response_time_ms: number;

  // PageSpeed
  pagespeed_mobile_score: number | null;
  pagespeed_desktop_score: number | null;
  first_contentful_paint_ms: number | null;
  largest_contentful_paint_ms: number | null;
  cumulative_layout_shift: number | null;
  total_blocking_time_ms: number | null;
  speed_index_ms: number | null;

  // Redesign Intelligence
  redesign_score: number;
  redesign_recommendation: "URGENT" | "RECOMMENDED" | "SEO_ONLY" | "GOOD" | "UNKNOWN";
  issues: AuditIssue[];
  sales_pitch: string | null;

  updated_at: string;
}

export interface AuditListItem {
  audit_id: string;
  business_id: string;
  business_name: string;
  business_city: string | null;
  website_url: string;
  website_domain: string;
  audit_status: string;
  redesign_score: number;
  redesign_recommendation: string;
  pagespeed_mobile_score: number | null;
  pagespeed_desktop_score: number | null;
  https_enabled: boolean;
  responsive_mobile: boolean;
  cta_visible: boolean;
  schema_markup_present: boolean;
  response_time_ms: number;
  issues_count: number;
  issues: AuditIssue[];
  sales_pitch: string | null;
  updated_at: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `HTTP Error ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errorMsg = typeof errorData.detail === "string"
          ? errorData.detail
          : JSON.stringify(errorData.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export async function triggerBusinessAudit(businessId: string): Promise<{ message: string; business_id: string; website_url: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/businesses/${businessId}/audit`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  return handleResponse(res);
}

export async function fetchBusinessAudit(businessId: string): Promise<WebsiteAuditResult | null> {
  const res = await fetch(`${API_BASE_URL}/api/v1/businesses/${businessId}/audit`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (res.status === 404 || res.status === 200) {
    const data = await res.json();
    return data || null;
  }
  return handleResponse(res);
}

export async function fetchAllAudits(params?: {
  recommendation?: string;
  min_score?: number;
  limit?: number;
}): Promise<AuditListItem[]> {
  const query = new URLSearchParams();
  if (params?.recommendation) query.append("recommendation", params.recommendation);
  if (params?.min_score !== undefined) query.append("min_score", String(params.min_score));
  if (params?.limit) query.append("limit", String(params.limit));

  const url = `${API_BASE_URL}/api/v1/audits?${query.toString()}`;
  const res = await fetch(url, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  return handleResponse<AuditListItem[]>(res);
}
