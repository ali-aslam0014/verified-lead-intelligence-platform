const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface VerificationStats {
  total_discovered: number;
  total_verified: number;
  reverify_required: number;
  human_review_required: number;
  conflicting_records_count: number;
}

export interface VerificationCheckResult {
  id?: string;
  check_type: string;
  result: "PASS" | "FAIL" | "NOT_FOUND" | "UNKNOWN" | "CONFLICT" | "ERROR";
  confidence: number;
  reason?: string;
  evidence: Record<string, any>;
  source?: string;
  observed_at?: string;
}

export interface VerificationSummary {
  business_id: string;
  name: string;
  lifecycle_status: string;
  verified_at?: string;
  summary: {
    total_checks?: number;
    pass_count?: number;
    fail_count?: number;
    conflict_count?: number;
    not_found_count?: number;
    website_reachable?: boolean;
    has_https?: boolean;
    has_conflicts?: boolean;
    conflicts?: Array<{ field: string; values: Record<string, string>; message: string }>;
    verified_at?: string;
  };
  check_results: VerificationCheckResult[];
}

export interface EvidenceItem {
  id: string;
  business_id: string;
  source: string;
  source_url_or_id?: string;
  observed_at: string;
  status: string;
  evidence_type: string;
  data: Record<string, any>;
}

export async function fetchVerificationStats(): Promise<VerificationStats> {
  const res = await fetch(`${API_BASE_URL}/api/v1/verification/console/stats`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error("Failed to fetch verification console stats");
  return res.json();
}

export async function fetchBusinessVerificationSummary(businessId: string): Promise<VerificationSummary> {
  const res = await fetch(`${API_BASE_URL}/api/v1/verification/businesses/${businessId}/summary`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`Failed to fetch verification summary for business ${businessId}`);
  return res.json();
}

export async function triggerBusinessVerification(businessId: string): Promise<VerificationSummary> {
  const res = await fetch(`${API_BASE_URL}/api/v1/verification/businesses/${businessId}/verify`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`Failed to trigger verification for business ${businessId}`);
  return res.json();
}

export async function fetchBusinessEvidence(businessId: string): Promise<EvidenceItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/verification/businesses/${businessId}/evidence`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`Failed to fetch evidence for business ${businessId}`);
  return res.json();
}

export async function triggerBatchTargetVerification(targetId: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/verification/targets/${targetId}/batch`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`Failed to trigger batch verification for target ${targetId}`);
  return res.json();
}
