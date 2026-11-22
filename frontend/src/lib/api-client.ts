// Centralized API client with auth token handling and error normalization
import sharedConfig from '../../../shared_config.json';

// Only place /api is written on frontend - relative base URL for same-origin API
const API_BASE = import.meta.env.VITE_API_URL ?? '/api';
const API_PREFIX = sharedConfig.api_base_path;
const TOKEN_KEY = sharedConfig.auth.storage_key;

export interface ApiError {
  detail: string;
  status_code: number;
}

class ApiClient {
  private getAuthToken(): string | null {
    return sessionStorage.getItem(TOKEN_KEY);
  }

  private setAuthToken(token: string): void {
    sessionStorage.setItem(TOKEN_KEY, token);
  }

  public clearAuthToken(): void {
    sessionStorage.removeItem(TOKEN_KEY);
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    // Handle 401 - clear token and redirect to login
    if (response.status === 401) {
      this.clearAuthToken();
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    // Handle non-ok responses with standardized error shape
    if (!response.ok) {
      let errorDetail = 'Request failed';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || errorDetail;
      } catch {
        errorDetail = await response.text() || errorDetail;
      }

      const apiError: ApiError = {
        detail: errorDetail,
        status_code: response.status,
      };
      throw apiError;
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null as T;
    }

    // Parse and return JSON response
    return response.json() as Promise<T>;
  }

  async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getAuthToken();
    const headers = new Headers(options.headers);

    // Attach auth token if available
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    // Set content-type for JSON bodies
    if (options.body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    // Build full URL: /api + /v1 + path
    const url = `${API_BASE}${API_PREFIX}${path}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      // Re-throw ApiError objects as-is
      if (error && typeof error === 'object' && 'status_code' in error) {
        throw error;
      }

      // Wrap other errors in ApiError shape
      const apiError: ApiError = {
        detail: error instanceof Error ? error.message : 'Network error',
        status_code: 0,
      };
      throw apiError;
    }
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'GET' });
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' });
  }

  // Expose token methods for auth context
  public storeToken(token: string): void {
    this.setAuthToken(token);
  }

  public hasToken(): boolean {
    return this.getAuthToken() !== null;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
