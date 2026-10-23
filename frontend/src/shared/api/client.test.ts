import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError, apiRequest } from './client'
import {
  clearSession,
  getSession,
  saveSession,
  SESSION_EXPIRED_EVENT,
} from '../../features/auth/services/auth.storage'

const initialSession = {
  accessToken: 'access-old',
  refreshToken: 'refresh-old',
  email: 'user@example.test',
  tenantId: 'tenant-1',
}

function response(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function requestBody(call: unknown[]): Record<string, string> {
  return JSON.parse(String((call[1] as RequestInit).body)) as Record<string, string>
}

describe('apiRequest authentication refresh', () => {
  beforeEach(() => {
    sessionStorage.clear()
    saveSession(initialSession)
  })

  afterEach(() => {
    vi.restoreAllMocks()
    clearSession()
  })

  it('does not refresh a successful public request', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(response({ authenticated: true }))

    await expect(apiRequest('/auth/login', { method: 'POST' })).resolves.toEqual({
      authenticated: true,
    })

    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('refreshes and replays an authenticated request once', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(response({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(
        response({
          authenticated: true,
          access_token: 'access-new',
          refresh_token: 'refresh-new',
        }),
      )
      .mockResolvedValueOnce(response({ id: 'user-1' }))

    await expect(apiRequest('/auth/me', { authenticated: true })).resolves.toEqual({
      id: 'user-1',
    })

    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(getSession()).toMatchObject({
      accessToken: 'access-new',
      refreshToken: 'refresh-new',
    })
    const replayHeaders = new Headers(fetchMock.mock.calls[2][1]?.headers)
    expect(replayHeaders.get('Authorization')).toBe('Bearer access-new')
  })

  it('sends the current refresh token and atomically stores rotation', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(response({}, 401))
      .mockResolvedValueOnce(
        response({
          authenticated: true,
          access_token: 'access-rotated',
          refresh_token: 'refresh-rotated',
        }),
      )
      .mockResolvedValueOnce(response({ ok: true }))

    await apiRequest('/protected', { authenticated: true })

    expect(requestBody(fetchMock.mock.calls[1])).toEqual({
      refresh_token: 'refresh-old',
    })
    expect(getSession()).toEqual({
      ...initialSession,
      accessToken: 'access-rotated',
      refreshToken: 'refresh-rotated',
    })
  })

  it('shares one refresh between concurrent 401 responses', async () => {
    let releaseRefresh!: (value: Response) => void
    const refreshResponse = new Promise<Response>((resolve) => {
      releaseRefresh = resolve
    })
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      if (String(input).endsWith('/auth/refresh')) {
        return refreshResponse
      }
      const resourceCalls = fetchMock.mock.calls.filter(
        ([url]) => !String(url).endsWith('/auth/refresh'),
      )
      if (resourceCalls.length <= 2) {
        return Promise.resolve(response({}, 401))
      }
      return Promise.resolve(response({ ok: true }))
    })

    const first = apiRequest('/first', { authenticated: true })
    const second = apiRequest('/second', { authenticated: true })
    await new Promise((resolve) => setTimeout(resolve, 0))

    expect(
      fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/auth/refresh')),
    ).toHaveLength(1)
    releaseRefresh(
      response({
        authenticated: true,
        access_token: 'access-shared',
        refresh_token: 'refresh-shared',
      }),
    )

    await expect(Promise.all([first, second])).resolves.toEqual([
      { ok: true },
      { ok: true },
    ])
    expect(fetchMock).toHaveBeenCalledTimes(5)
  })

  it('clears the session and emits expiration when refresh is rejected', async () => {
    const expired = vi.fn()
    window.addEventListener(SESSION_EXPIRED_EVENT, expired)
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(response({}, 401))
      .mockResolvedValueOnce(response({ detail: 'invalid refresh' }, 401))

    await expect(apiRequest('/protected', { authenticated: true })).rejects.toMatchObject({
      status: 401,
    })

    expect(getSession()).toBeNull()
    expect(expired).toHaveBeenCalledTimes(1)
    window.removeEventListener(SESSION_EXPIRED_EVENT, expired)
  })

  it('does not loop after a second 401', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(response({}, 401))
      .mockResolvedValueOnce(
        response({
          authenticated: true,
          access_token: 'access-new',
          refresh_token: 'refresh-new',
        }),
      )
      .mockResolvedValueOnce(response({}, 401))

    await expect(apiRequest('/protected', { authenticated: true })).rejects.toBeInstanceOf(ApiError)

    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(getSession()).toBeNull()
  })

  it('does not refresh on 403 responses', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(response({ detail: 'forbidden' }, 403))

    await expect(apiRequest('/protected', { authenticated: true })).rejects.toMatchObject({
      status: 403,
    })

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(getSession()).not.toBeNull()
  })

  it('does not refresh login, 2FA verification, or refresh endpoints', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(response({}, 401))

    for (const path of ['/auth/login', '/auth/2fa/login', '/auth/refresh']) {
      await expect(apiRequest(path, { method: 'POST' })).rejects.toMatchObject({ status: 401 })
    }

    expect(fetchMock).toHaveBeenCalledTimes(3)
  })

  it('does not invalidate the session when refresh fails due to network', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(response({}, 401))
      .mockRejectedValueOnce(new TypeError('network unavailable'))

    await expect(apiRequest('/protected', { authenticated: true })).rejects.toMatchObject({
      status: 0,
    })

    expect(getSession()).toEqual(initialSession)
  })
})
