/**
 * Centralized API Client for AapadaOps
 * Connects React frontend directly to the FastAPI backend.
 * Handles JWT authentication, FormData multipart uploads, error parsing, and session expiry.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('aapadaops_token');

  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Only set Content-Type to application/json if body is not FormData
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 204) {
      return {} as T;
    }

    if (response.status === 401) {
      // Dispatch custom event for expired sessions
      window.dispatchEvent(new CustomEvent('aapadaops:auth_expired'));
    }

    const json = await response.json().catch(() => ({}));

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: Request failed`;
      if (typeof json?.detail === 'string') {
        errorMessage = json.detail;
      } else if (Array.isArray(json?.detail)) {
        errorMessage = json.detail
          .map((err: any) => `${err.loc?.filter((l: any) => l !== 'body').join('.') || 'field'}: ${err.msg}`)
          .join('; ');
      } else if (json?.message) {
        errorMessage = json.message;
      }
      throw new ApiError(response.status, errorMessage, json);
    }

    return json as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, (error as Error).message || 'Network connection failed. Verify backend service is running.');
  }
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, body?: any, options?: RequestInit) => {
    const isFormData = body instanceof FormData;
    return request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: isFormData ? body : body ? JSON.stringify(body) : undefined,
    });
  },

  patch: <T>(endpoint: string, body?: any, options?: RequestInit) => {
    const isFormData = body instanceof FormData;
    return request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: isFormData ? body : body ? JSON.stringify(body) : undefined,
    });
  },

  put: <T>(endpoint: string, body?: any, options?: RequestInit) => {
    const isFormData = body instanceof FormData;
    return request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: isFormData ? body : body ? JSON.stringify(body) : undefined,
    });
  },

  delete: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'DELETE' }),

  upload: <T>(endpoint: string, formData: FormData, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: formData,
    }),
};
