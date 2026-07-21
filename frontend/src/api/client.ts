/**
 * Campus Copies ERP - Centralized API Fetch Client
 * Grounding: docs/FrontendSpecification.md §8, docs/SecuritySpecification.md §4
 */

import { ApiResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface RequestOptions extends RequestInit {
  token?: string | null;
  timeoutMs?: number;
}

export class ApiError extends Error {
  code: string;
  status: number;
  details?: unknown;

  constructor(message: string, code: string, status: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

/**
 * Execute HTTP fetch request with timeout and Authorization header.
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { token, timeoutMs = 30000, headers = {}, ...customConfig } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(headers as Record<string, string>),
  };

  if (token) {
    requestHeaders['Authorization'] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...customConfig,
      headers: requestHeaders,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const json: ApiResponse<T> = await response.json();

    if (!response.ok || !json.success) {
      const errorCode = json.error?.code || 'HTTP_ERROR';
      const errorMessage = json.error?.message || response.statusText || 'An unexpected API error occurred';
      
      if (response.status === 401 && typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('unauthorized_session'));
      }

      throw new ApiError(errorMessage, errorCode, response.status, json.error?.details);
    }

    return json.data as T;
  } catch (error: unknown) {
    clearTimeout(timeoutId);
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError('Request timed out', 'TIMEOUT_ERROR', 408);
    }
    throw new ApiError(
      error instanceof Error ? error.message : 'Network request failed',
      'NETWORK_ERROR',
      0
    );
  }
}
