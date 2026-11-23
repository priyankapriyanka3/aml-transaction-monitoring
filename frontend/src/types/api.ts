// API types matching backend schemas from handoff files

export interface User {
  user_id: string;
  display_name: string;
  email: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface AlertQueueItem {
  alert_id: string;
  alert_ref: string;
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  risk_score: number;
  status: string;
  owner_user_id: string | null;
  triggered_at_utc: string;
  transaction_amount: string;
  transaction_currency_code: string;
  source_country_code: string;
  destination_country_code: string;
  customer_id: string;
  customer_name: string;
}

export interface AlertQueueResponse {
  items: AlertQueueItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface AlertAssignmentResponse {
  alert_id: string;
  owner_user_id: string;
  assigned_at_utc: string;
}

export interface RuleSnapshotItem {
  snapshot_id: string;
  rule_code: string;
  rule_name: string;
  rule_version: string;
  outcome: 'MATCH' | 'PASS';
  condition_text: string;
  evaluated_from_utc: string;
  evaluated_to_utc: string;
}

export interface TransactionFacts {
  transaction_id: string;
  transaction_ref: string;
  amount: string;
  currency_code: string;
  source_country_code: string;
  destination_country_code: string;
  executed_at_utc: string;
}

export interface CustomerContext {
  customer_id: string;
  customer_name: string;
  pep_flag: boolean;
  country_code: string;
}

export interface AccountContext {
  account_id: string;
  account_ref: string;
  account_type: string;
}

export interface AlertEvidenceResponse {
  alert_id: string;
  alert_ref: string;
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  risk_score: number;
  status: string;
  triggered_at_utc: string;
  transaction: TransactionFacts;
  customer: CustomerContext;
  account: AccountContext;
  rule_snapshots: RuleSnapshotItem[];
}

export interface CaseCreatedResponse {
  case_id: string;
  case_ref: string;
  primary_alert_id: string;
  created_by_user_id: string;
  status: string;
  created_at_utc: string;
}

// Case Workspace Types (TASK-6)
export interface LinkedAlert {
  alert_id: string;
  alert_ref: string;
  is_primary: boolean;
  linked_at_utc: string;
}

export interface CaseNote {
  note_id: string;
  note_category: 'investigation' | 'recommendation' | 'information_request' | 'response' | 'closure';
  note_text: string;
  author_user_id: string;
  authored_at_utc: string;
}

export interface TimelineEntry {
  event_id: string;
  action_type: string;
  actor_user_id: string;
  occurred_at_utc: string;
  details_json: string;
}

export interface CaseWorkspaceResponse {
  case_id: string;
  case_ref: string;
  status: string;
  current_blocker_state: 'NONE' | 'OPEN_REQUESTS' | 'OVERDUE_REQUESTS';
  created_by_user_id: string;
  assigned_officer_user_id: string | null;
  created_at_utc: string;
  updated_at_utc: string;
  linked_alerts: {
    items: LinkedAlert[];
    total: number;
  };
  notes: {
    items: CaseNote[];
    total: number;
  };
  evidence_gaps: {
    items: unknown[];
    total: number;
  };
  timeline_entries: {
    items: TimelineEntry[];
    total: number;
  };
}

export interface AddNoteRequest {
  note_category: 'investigation' | 'recommendation' | 'information_request' | 'response' | 'closure';
  note_text: string;
}

export interface AddNoteResponse {
  note_id: string;
  case_id: string;
  note_category: string;
  note_text: string;
  author_user_id: string;
  authored_at_utc: string;
}

// Information Request Types (TASK-9)
export interface InformationRequestDetail {
  request_id: string;
  request_ref: string;
  case_id: string;
  gap_id: string;
  target_party: string;
  delivery_channel: string;
  reason_text: string;
  due_at_utc: string;
  status: 'OPEN' | 'OVERDUE' | 'RESPONDED' | 'RESOLVED';
  created_by_user_id: string;
  response_summary: string | null;
  response_received_at_utc: string | null;
  created_at_utc: string;
  updated_at_utc: string;
  blocker_state: 'NONE' | 'OPEN_REQUESTS' | 'OVERDUE_REQUESTS';
}

export interface RecordResponseRequest {
  response_summary: string;
  received_at_utc: string;
}

export interface RecordResponseResponse {
  request_id: string;
  status: string;
  response_summary: string;
  response_received_at_utc: string;
}

// Readiness Types (TASK-9, TASK-10)
export interface ReadinessChecklistItem {
  name: 'linked_evidence' | 'investigation_notes' | 'responses_reviewed' | 'no_open_requests';
  complete: boolean;
  details: string;
}

export interface PackageSummary {
  alert_count: number;
  note_count: number;
  request_count: number;
  evidence_count: number;
}

export interface EligibleOfficer {
  user_id: string;
  display_name: string;
  email: string;
}

export interface ReadinessProjection {
  checklist: ReadinessChecklistItem[];
  package_summary: PackageSummary;
  eligible_officers: EligibleOfficer[];
}

export interface AssignOfficerRequest {
  officer_user_id: string;
}

export interface AssignOfficerResponse {
  assignment_id: string;
  case_id: string;
  officer_user_id: string;
  assigned_by_user_id: string;
  assigned_at_utc: string;
}

export interface ShareForReviewResponse {
  case_id: string;
  status: string;
  shared_at_utc: string;
}

// Officer Review Types (TASK-10)
export interface OfficerReviewAlert {
  alert_id: string;
  alert_ref: string;
  is_primary: boolean;
}

export interface OfficerReviewNote {
  note_id: string;
  note_text: string;
  author_user_id: string;
  authored_at_utc: string;
}

export interface OfficerReviewRuleSnapshot {
  snapshot_id: string;
  rule_name: string;
  rule_version: string;
  outcome: 'MATCH' | 'PASS';
}

export interface OfficerReviewPackage {
  case_id: string;
  case_ref: string;
  status: string;
  blocker_state: 'NONE' | 'OPEN_REQUESTS' | 'OVERDUE_REQUESTS';
  is_conflicted_officer: boolean;
  linked_alerts: OfficerReviewAlert[];
  notes: OfficerReviewNote[];
  rule_snapshots: OfficerReviewRuleSnapshot[];
}

export interface RecordDecisionRequest {
  outcome: 'APPROVE' | 'REJECT' | 'ESCALATE' | 'FALSE_POSITIVE' | 'RETURN_FOR_INVESTIGATION';
  rationale_text: string;
}

export interface RecordDecisionResponse {
  decision_id: string;
  case_id: string;
  deciding_officer_user_id: string;
  outcome: string;
  rationale_text: string;
  rationale: string;
  recorded_at_utc: string;
  immutable_hash: string;
}

export interface ApiError {
  detail: string;
}
