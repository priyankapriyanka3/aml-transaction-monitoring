// Case types based on backend response shapes from handoff files

export interface CaseOverview {
  case_id: string;
  case_number: string;
  status: 'INVESTIGATING' | 'PENDING_INFORMATION' | 'REVIEW_READY' | 'SUBMITTED_FOR_REVIEW';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  assigned_user_id: string;
  assigned_user_name: string;
  recommendation_state: 'DRAFT' | 'SUBMITTED' | null;
  recommendation_outcome: 'SUBSTANTIATE' | 'NO_FURTHER_ACTION' | 'ESCALATE_FOR_REVIEW' | null;
  flagged_value_total: number;
  currency: string;
  linked_alert_count: number;
  open_information_request_count: number;
  overdue_information_request_count: number;
  recent_activity: ActivityEvent[];
  created_at: string;
  updated_at: string;
}

export interface ActivityEvent {
  event_id: string;
  event_type: string;
  occurred_at: string;
  actor_display: string;
  summary: string;
}

export interface CaseNote {
  note_id: string;
  case_id: string;
  note_type: string;
  stage: string;
  body: string;
  author_user_id: string;
  author_display_name: string;
  created_at: string;
  superseded_by_note_id: string | null;
}

export interface CaseNoteRequest {
  note_type: string;
  stage: string;
  body: string;
}

export interface StatusTransitionRequest {
  new_status: string;
  reason: string;
  trigger_event?: string;
}

export interface RecommendationRequest {
  recommendation_outcome: 'SUBSTANTIATE' | 'NO_FURTHER_ACTION' | 'ESCALATE_FOR_REVIEW';
  findings_summary: string;
  supporting_note_ids?: string[];
}
