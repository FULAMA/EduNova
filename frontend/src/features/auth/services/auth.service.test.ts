import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  getCurrentUser,
  linkGoogleIdentity,
  login,
  verifyLoginTwoFactor,
} from './auth.service'
import { clearSession, saveSession } from './auth.storage'

function response(payload: unknown): Response {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('auth service request classification', () => {
  beforeEach(() => {
    sessionStorage.clear()
    saveSession({
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      email: 'user@example.test',
      tenantId: 'tenant-1',
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    clearSession()
  })

  it('does not mark login or 2FA verification as authenticated', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(response({ authenticated: true }))
      .mockResolvedValueOnce(
        response({
          authenticated: true,
          access_token: 'access-token',
          refresh_token: 'refresh-token',
        }),
      )

    await login({
      email: 'user@example.test',
      password: 'password',
      tenant_id: 'tenant-1',
    })
    await verifyLoginTwoFactor('two-factor-token', '123456')

    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock.mock.calls[0][0]).toContain('/auth/login')
    expect(fetchMock.mock.calls[1][0]).toContain('/auth/2fa/login')
    expect(fetchMock.mock.calls[0][1]?.headers).not.toHaveProperty('Authorization')
    expect(fetchMock.mock.calls[1][1]?.headers).not.toHaveProperty('Authorization')
  })

  it('sends the exact email, password, and tenant ID in the login request', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      response({
        authenticated: true,
        two_factor_required: false,
        two_factor_token: null,
        access_token: 'access-token',
        refresh_token: 'refresh-token',
      }),
    )

    await login({
      email: 'admin@edunova.com',
      password: 'DevPassword@2026',
      tenant_id: '00000000-0000-0000-0000-000000000001',
    })

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(fetchMock.mock.calls[0][0]).toContain('/auth/login')
    expect(fetchMock.mock.calls[0][1]?.method).toBe('POST')
    expect(JSON.parse(String(fetchMock.mock.calls[0][1]?.body))).toEqual({
      email: 'admin@edunova.com',
      password: 'DevPassword@2026',
      tenant_id: '00000000-0000-0000-0000-000000000001',
    })
  })

  it('marks the current-user request as authenticated', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(response({ id: 'user-1' }))

    await getCurrentUser('access-token')

    const headers = new Headers(fetchMock.mock.calls[0][1]?.headers)
    expect(fetchMock.mock.calls[0][0]).toContain('/auth/me')
    expect(headers.get('Authorization')).toBe('Bearer access-token')
  })

  it('uses the authenticated link endpoint without exposing the token in headers', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(response({ linked: true }))

    await expect(linkGoogleIdentity('google-id-token')).resolves.toEqual({
      linked: true,
    })

    expect(fetchMock.mock.calls[0][0]).toContain('/auth/google/link')
    expect(fetchMock.mock.calls[0][1]?.headers).toBeInstanceOf(Headers)
    expect(JSON.parse(String(fetchMock.mock.calls[0][1]?.body))).toEqual({
      id_token: 'google-id-token',
    })
  })
})
