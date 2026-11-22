// Information request types matching backend schema

export interface InformationRequest {
  information_request_id: string;
  case_id: string;
  recipient_channel: string;
  requested_summary: string;
  rationale: string;
  status: 'OPEN' | 'RESPONDED' | 'CLOSED';
  due_at: string;
  days_remaining: number | null;
  is_overdue: boolean;
  response_summary: string | null;
  response_channel: string | null;
  response_received_at: string | null;
  created_by_user_id: string;
  created_at: string;
  updated_at: string;
}

export interface InformationRequestCreateRequest {
  case_id: string;
  recipient_channel: string;
  requested_summary: string;
  rationale: string;
  due_at: string;
}

export interface InformationRequestCreateResponse {
  information_request_id: string;
  case_id: string;
  status: string;
  due_at: string;
  created_at: string;
  case_status_after_create: string;
}

export interface RecordResponseRequest {
  response_summary: string;
  received_at: string;
  response_channel: string;
}

export interface RecordResponseResponse {
  information_request_id: string;
  status: string;
  response_received_at: string;
  case_status_after_response: string;
}
