import { describe, it, expect } from 'vitest';
import { server } from '../../mocks/server';
import { http, HttpResponse } from 'msw';
import { adminLogin } from '../auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

describe('Auth API Integration', () => {
  it('adminLogin successfully returns a token', async () => {
    server.use(
      http.post(`${API_BASE_URL}/api/v1/auth/admin/login`, () => {
        return HttpResponse.json({
          success: true,
          data: {
            access_token: 'fake-token-123',
            token_type: 'bearer',
            user: {
              id: '1',
              email: 'admin@campuscopies.com',
              role: 'super_admin',
            },
          },
        });
      })
    );

    const result = await adminLogin('admin@campuscopies.com', 'password123');

    expect(result.access_token).toBe('fake-token-123');
    expect(result.user.email).toBe('admin@campuscopies.com');
  });

  it('adminLogin throws ApiError on invalid credentials', async () => {
    server.use(
      http.post(`${API_BASE_URL}/api/v1/auth/admin/login`, () => {
        return HttpResponse.json(
          {
            success: false,
            error: {
              code: 'UNAUTHORIZED',
              message: 'Invalid credentials',
            },
          },
          { status: 401 }
        );
      })
    );

    await expect(adminLogin('admin@campuscopies.com', 'wrong')).rejects.toThrow(
      'Invalid credentials'
    );
  });
});
