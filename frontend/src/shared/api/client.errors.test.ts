import { afterEach, describe, expect, it, vi } from 'vitest'

import { apiRequest } from './client'

function failure(payload: unknown, status: number): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('apiRequest error messages', () => {
  it('shows validation messages for a 422 with a list of details', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      failure({ detail: [{ msg: 'Le montant doit être positif', loc: ['body', 'amount'] }] }, 422),
    )

    await expect(apiRequest('/x', { method: 'POST' })).rejects.toMatchObject({
      status: 422,
      message: 'Données invalides : Le montant doit être positif',
    })
  })

  it('keeps a string detail as is', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(failure({ detail: 'Accès interdit.' }, 403))

    await expect(apiRequest('/x')).rejects.toMatchObject({ message: 'Accès interdit.' })
  })

  it('falls back to the generic message when there is no usable detail', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(failure({}, 500))

    await expect(apiRequest('/x')).rejects.toMatchObject({
      status: 500,
      message: 'Le serveur est indisponible. Réessayez plus tard.',
    })
  })
})