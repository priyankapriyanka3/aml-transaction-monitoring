// API client for AML Workbench backend
import type * as Types from '../types/api';

const API_BASE = import.meta.env.VITE_API_URL ?? '/api';

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token');
    }
    return this.token;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Merge any existing headers
    if (options.headers) {
      const existingHeaders = new Headers(options.headers);
      existingHeaders.forEach((value, key) => {
        headers[key] = value;
      });
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string): Promise<Types.LoginResponse> {
    const response = await this.request<Types.LoginResponse>('/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  async logout(): Promise<void> {
    try {
      await this.request('/v1/auth/logout', { method: 'POST' });
    } finally {
      this.setToken(null);
    }
  }

  async getMe(): Promise<Types.User> {
    return this.request<Types.User>('/v1/auth/me');
  }

  // Alerts
  async getAlertQueue(params: {
    priority?: string;
    ownership?: string;
    status?: string;
    search?: string;
    page?: number;
    page_size?: number;
  } = {}): Promise<Types.AlertQueueResponse> {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        query.append(key, String(value));
      }
    });
    const queryString = query.toString();
    return this.request<Types.AlertQueueResponse>(
      `/v1/alerts${queryString ? `?${queryString}` : ''}`
    );
  }

  async assignAlert(alertId: string): Promise<Types.AlertAssignmentResponse> {
    return this.request<Types.AlertAssignmentResponse>(`/v1/alerts/${alertId}/assign`, {
      method: 'POST',
      headers: {
        'X-Correlation-ID': `assign-${Date.now()}`,
      },
    });
  }

  async getAlertEvidence(alertId: string): Promise<Types.AlertEvidenceResponse> {
    return this.request<Types.AlertEvidenceResponse>(`/v1/alerts/${alertId}/evidence`);
  }

  // Cases
  async createCase(alertId: string): Promise<Types.CaseCreatedResponse> {
    return this.request<Types.CaseCreatedResponse>('/v1/cases', {
      method: 'POST',
      headers: {
        'X-Correlation-ID': `create-case-${Date.now()}`,
      },
      body: JSON.stringify({ alert_id: alertId }),
    });
  }

  async getCaseWorkspace(caseId: string): Promise<Types.CaseWorkspaceResponse> {
    return this.request<Types.CaseWorkspaceResponse>(`/v1/cases/${caseId}/workspace`);
  }

  async addCaseNote(caseId: string, note: Types.AddNoteRequest): Promise<Types.AddNoteResponse> {
    return this.request<Types.AddNoteResponse>(`/v1/cases/${caseId}/notes`, {
      method: 'POST',
      headers: {
        'X-Correlation-ID': `add-note-${Date.now()}`,
      },
      body: JSON.stringify(note),
    });
  }

  // Information Requests
  async getInformationRequest(caseId: string, requestId: string): Promise<Types.InformationRequestDetail> {
    return this.request<Types.InformationRequestDetail>(`/v1/cases/${caseId}/requests/${requestId}`);
  }

  async recordResponse(
    caseId: string,
    requestId: string,
    response: Types.RecordResponseRequest
  ): Promise<Types.RecordResponseResponse> {
    return this.request<Types.RecordResponseResponse>(`/v1/cases/${caseId}/requests/${requestId}/response`, {
      method: 'POST',
      headers: {
        'X-Correlation-ID': `record-response-${Date.now()}`,
      },
      body: JSON.stringify(response),
    });
  }

  // Readiness
  async getCaseReadiness(caseId: string): Promise<Types.ReadinessProjection> {
    return this.request<Types.ReadinessProjection>(`/v1/cases/${caseId}/readiness`);
  }

  async assignOfficer(caseId: string, officerUserId: string): Promise<Types.AssignOfficerResponse> {
    return this.request<Types.AssignOfficerResponse>(`/v1/cases/${caseId}/assign-officer`, {
      method: 'POST',
      headers: {
        'X-Correlation-ID': `assign-officer-${Date.now()}`,
      },
      body: JSON.stringify({ officer_user_id: officerUserId }),
    });
  }

  async shareForReview(caseId: string): Promise<Types.ShareForReviewResponse> {
    return this.request<Types.ShareForReviewResponse>(`/v1/cases/${caseId}/share-for-review`, {
      method: 'POST',
      headers: {
        'X-Correlation-ID': `share-review-${Date.now()}`,
      },
    });
  }

  // Officer Review
  async getOfficerReviewPackage(caseId: string): Promise<Types.OfficerReviewPackage> {
    return this.request<Types.OfficerReviewPackage>(`/v1/cases/${caseId}/officer-review`);
  }

  async recordDecision(caseId: string, decision: Types.RecordDecisionRequest): Promise<Types.RecordDecisionResponse> {
    return this.request<Types.RecordDecisionResponse>(`/v1/cases/${caseId}/decision`, {
      method: 'POST',
      headers: {
        'X-Correlation-ID': `record-decision-${Date.now()}`,
      },
      body: JSON.stringify(decision),
    });
  }
}

export const apiClient = new ApiClient();
