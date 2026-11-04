import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError, apiRequestBlob } from './client'
import {
  clearSession,
  getSession,
  saveSession,
} from '../../features/auth/services/auth.storage'

const session = {
  accessToken: 'access-old',
  refreshToken: 'refresh-old',
  email: 'user@example.test',
  tenantId: 'tenant-1',
}

describe('apiRequestBlob', () => {
  beforeEach(() => {
    sessionStorage.clear()
    saveSession(session)
  })

  afterEach(() => {
    vi.restoreAllMocks()
    clearSession()
  })

  it('returns the binary body of a successful response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('%PDF-1.4', { status: 200 }),
    )

    const blob = await apiRequestBlob('/report-cards/1/pdf', { authenticated: true })

    expect(await blob.text()).toBe('%PDF-1.4')
  })

  it('refreshes once and replays the download after a 401', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 401 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            authenticated: true,
            access_token: 'access-new',
            refresh_token: 'refresh-new',
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response('PDF', { status: 200 }))

    const blob = await apiRequestBlob('/x/pdf', { authenticated: true })

    expect(await blob.text()).toBe('PDF')
    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(getSession()?.accessToken).toBe('access-new')
  })

  it('raises the backend detail on a business error', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Reçu introuvable.' }), { status: 404 }),
    )

    await expect(apiRequestBlob('/x/pdf', { authenticated: true })).rejects.toMatchObject({
      status: 404,
      message: 'Reçu introuvable.',
    })
  })

  it('reports an unreachable server with status 0', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('offline'))

    const failure = apiRequestBlob('/x/pdf', { authenticated: true })

    await expect(failure).rejects.toBeInstanceOf(ApiError)
    await expect(failure).rejects.toMatchObject({ status: 0 })
  })
})