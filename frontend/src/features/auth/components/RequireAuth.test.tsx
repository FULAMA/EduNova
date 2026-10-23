// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../../shared/api/client'
import { clearSession, getCurrentUser, getSession } from '../services/auth.service'
import { RequireAuth } from './RequireAuth'
import { useCurrentUser } from './useCurrentUser'

vi.mock('../services/auth.service', () => ({
  clearSession: vi.fn(),
  getCurrentUser: vi.fn(),
  getSession: vi.fn(),
  SESSION_EXPIRED_EVENT: 'edunova:session-expired',
}))

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const currentUser = {
  id: 'user-1',
  email: 'marie@example.test',
  role: 'ADMIN',
  is_active: true,
  two_factor_enabled: true,
}

const session = {
  accessToken: 'access-token',
  refreshToken: 'refresh-token',
  email: 'local@example.test',
  tenantId: 'tenant-local',
}

const mockedGetCurrentUser = vi.mocked(getCurrentUser)
const mockedGetSession = vi.mocked(getSession)
const mockedClearSession = vi.mocked(clearSession)
let root: Root | undefined
let host: HTMLDivElement

function ProtectedContent() {
  const user = useCurrentUser()
  return <p>{user.email} — {user.role}</p>
}

function renderProtected() {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(
      createElement(
        MemoryRouter,
        { initialEntries: ['/app'] },
        createElement(
          Routes,
          null,
          createElement(Route, {
            path: '/app',
            element: createElement(RequireAuth, null, createElement(ProtectedContent)),
          }),
          createElement(Route, { path: '/login', element: <p>Connexion</p> }),
        ),
      ),
    )
  })
  return host
}

async function settle() {
  await act(async () => {
    await Promise.resolve()
    await Promise.resolve()
  })
}

beforeEach(() => {
  mockedGetSession.mockReturnValue(session)
  mockedGetCurrentUser.mockResolvedValue(currentUser)
})

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  root = undefined
  vi.clearAllMocks()
})

describe('RequireAuth account context', () => {
  it('shares the server-confirmed current user with protected pages', async () => {
    const page = renderProtected()
    await settle()

    expect(page.textContent).toContain('marie@example.test — ADMIN')
    expect(mockedGetCurrentUser).toHaveBeenCalledWith(session.accessToken)
  })

  it('keeps the local session on transient errors and lets the user retry', async () => {
    mockedGetCurrentUser
      .mockRejectedValueOnce(new ApiError(0, 'network unavailable'))
      .mockResolvedValueOnce(currentUser)
    const page = renderProtected()
    await settle()

    expect(page.textContent).toContain('Impossible de vérifier votre session')
    expect(mockedClearSession).not.toHaveBeenCalled()

    const retry = [...page.querySelectorAll('button')].find((button) => button.textContent === 'Réessayer')!
    await act(async () => retry.click())
    await settle()

    expect(page.textContent).toContain('marie@example.test — ADMIN')
    expect(mockedGetCurrentUser).toHaveBeenCalledTimes(2)
  })

  it('clears and redirects when the server confirms the session is expired', async () => {
    mockedGetCurrentUser.mockRejectedValue(new ApiError(401, 'expired'))
    const page = renderProtected()
    await settle()

    expect(page.textContent).toContain('Connexion')
    expect(mockedClearSession).toHaveBeenCalledOnce()
  })
})
