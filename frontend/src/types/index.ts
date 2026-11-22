// Core types matching backend schemas

export interface User {
  user_id: string;
  username: string;
  display_name: string;
  roles: string[];
  primary_role: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  auth_token: string;
  token_type: string;
  session_id: string;
  user: User;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface CaseOverview {
  case_id: string;
  case_number: string;
  status: string;
  priority: string;
  assigned_user_id: string;
  assigned_user_name: string | null;
  customer_id: string;
  source_alert_id: string;
  flagged_value_total: number;
  linked_alert_count: number;
  open_information_request_count: number;
  overdue_information_request_count: number;
  recent_activity: RecentActivityItem[];
  created_at: string;
  updated_at: string;
}

export interface RecentActivityItem {
  audit_event_id: string;
  occurred_at: string;
  action_type: string;
  summary: string;
}
