// Handoff and review types matching backend schema

export interface HandoffPackage {
  case_id: string;
  case_number: string;
  recommendation_outcome: string | null;
  findings_summary: string | null;
  linked_alerts: LinkedAlertSummary[];
  key_evidence_summary: string[];
  information_request_summary: InformationRequestSummary[];
  unresolved_issues: string[];
  readiness: ReadinessCheck;
  officer_assignment: OfficerAssignment;
}

export interface LinkedAlertSummary {
  alert_id: string;
  priority: string;
  risk_score: number;
}

export interface InformationRequestSummary {
  information_request_id: string;
  status: string;
  due_at: string;
  resolved_at: string | null;
}

export interface ReadinessCheck {
  is_ready: boolean;
  checklist_items: ReadinessChecklistItem[];
}

export interface ReadinessChecklistItem {
  code: string;
  label: string;
  passed: boolean;
  detail: string;
}

export interface OfficerAssignment {
  officer_user_id: string | null;
  officer_display_name: string | null;
}

export interface HandoffSubmitRequest {
  officer_user_id: string;
  submission_comment?: string;
}

export interface HandoffSubmitResponse {
  case_id: string;
  status: string;
  handoff_submitted_at: string;
  handoff_submitted_by_user_id: string;
  officer_user_id: string;
  readiness_passed: boolean;
}
