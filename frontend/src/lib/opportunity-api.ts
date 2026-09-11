const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1"
    ? "https://backend-sooty-one-32.vercel.app"
    : "http://localhost:8000");

export interface OpportunityItem {
  id: string;
  business_id: string;
  type: string;
  status: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  confidence: number;
  recommended_service: string;
  recommended_angle?: string;
  reason: string;
  evidence: Record<string, any>;
  evidence_ids: Record<string, any>;
  created_at: string;
}

export async function fetchBusinessOpportunities(businessId: string): Promise<OpportunityItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/opportunities/businesses/${businessId}/opportunities`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`Failed to fetch opportunities for business ${businessId}`);
  return res.json();
}

export async function triggerBusinessOpportunityAnalysis(businessId: string): Promise<{ opportunity_count: number; max_confidence: number }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/opportunities/businesses/${businessId}/opportunities/analyze`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`Failed to analyze opportunities for business ${businessId}`);
  return res.json();
}

export async function triggerBatchTargetOpportunityAnalysis(targetId: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/opportunities/targets/${targetId}/opportunities/analyze`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`Failed to analyze batch opportunities for target ${targetId}`);
  return res.json();
}

export async function reviewOpportunity(opportunityId: string, status: "CONFIRMED" | "REJECTED" | "NEEDS_REVIEW"): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/opportunities/${opportunityId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(`Failed to review opportunity ${opportunityId}`);
  return res.json();
}
