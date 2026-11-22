// Alert types based on backend response shapes from handoff files

export interface Alert {
  alert_id: string;
  transaction_id: string;
  customer_id: string;
  status: 'NEW' | 'UNDER_REVIEW' | 'ESCALATED_TO_CASE' | 'CLOSED_NON_ACTIONABLE' | 'MERGED_INTO_EXISTING_CASE';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  risk_score: number;
  matched_rule_codes_json: string;
  generation: string;
  assigned_user_id: string | null;
  triage_outcome: 'INVESTIGATE' | 'CLOSE_NON_ACTIONABLE' | 'MERGE_EXISTING_CASE' | null;
  triage_rationale: string | null;
  triaged_by_user_id: string | null;
  triaged_at: string | null;
  created_at: string;
  updated_at: string;
  // Enrichment fields from backend
  customer_name: string | null;
  transaction_amount: number | null;
  transaction_currency: string | null;
  assigned_user_name: string | null;
}

export interface AlertQueueFilters {
  status?: string;
  priority?: string;
  assignee_id?: string;
  risk_score_min?: number;
  risk_score_max?: number;
  generation?: string;
  search?: string;
  sort_by?: 'priority' | 'risk_score' | 'created_at' | 'status';
  sort_direction?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export interface AlertQueueResponse {
  items: Alert[];
  total_count: number;
  limit: number;
  offset: number;
}

export interface ClaimRequest {
  assignee_user_id: string;
  assignment_reason?: string | null;
}

export interface ClaimResponse {
  alert_id: string;
  status: string;
  assigned_user_id: string;
  assigned_user_name: string;
  assigned_at: string;
  assigned_by_user_id: string;
}

export interface TriageDispositionRequest {
  outcome: 'INVESTIGATE' | 'CLOSE_NON_ACTIONABLE' | 'MERGE_EXISTING_CASE';
  rationale: string;
  existing_case_id?: string | null;
}

export interface TriageDispositionResponse {
  alert_id: string;
  status: string;
  triage_outcome: string;
  triage_rationale: string;
  triaged_by_user_id: string;
  triaged_at: string;
}
