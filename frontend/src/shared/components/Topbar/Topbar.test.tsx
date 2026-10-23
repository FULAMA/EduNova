// @vitest-environment jsdom
import { act, createElement, Fragment } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { CurrentUserProvider } from '../../../features/auth/components/CurrentUserProvider'
import type { AuthenticatedUser } from '../../../features/auth/services/auth.service'
import { Topbar } from './Topbar'

vi.mock('../../../features/auth/services/auth.service', () => ({
  clearSession: vi.fn(),
}))

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const currentUser: AuthenticatedUser = {
  id: 'user-1',
  email: 'marie@example.test',
  role: 'ADMIN',
  is_active: true,
  two_factor_enabled: true,
}

let root: Root | undefined
let host: HTMLDivElement

function LocationLabel() {
  return <output data-testid="location">{useLocation().pathname}</output>
}

function renderTopbar() {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(
      createElement(
        MemoryRouter,
        { initialEntries: ['/app'] },
        createElement(
          CurrentUserProvider,
          { user: currentUser },
          createElement(Fragment, null, createElement(Topbar), createElement(LocationLabel)),
        ),
      ),
    )
  })
  return host
}

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  root = undefined
  vi.clearAllMocks()
})

describe('Topbar account controls', () => {
  it('shows verified account details and no placeholder notifications', () => {
    const page = renderTopbar()

    expect(page.textContent).toContain('marie@example.test')
    expect(page.textContent).toContain('ADMIN')
    expect(page.querySelector('[aria-label="Notifications"]')).toBeNull()
  })

  it('opens an accessible account disclosure and closes it with Escape', () => {
    const page = renderTopbar()
    const accountButton = page.querySelector('button[aria-controls="topbar-account-menu"]') as HTMLButtonElement

    act(() => accountButton.click())
    expect(accountButton.getAttribute('aria-expanded')).toBe('true')
    expect(page.textContent).toContain('Se déconnecter')

    act(() => accountButton.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })))
    expect(accountButton.getAttribute('aria-expanded')).toBe('false')
  })

  it('clears the local session and navigates to login on sign out', async () => {
    const { clearSession } = await import('../../../features/auth/services/auth.service')
    const page = renderTopbar()
    const accountButton = page.querySelector('button[aria-controls="topbar-account-menu"]') as HTMLButtonElement
    act(() => accountButton.click())
    const signOutButton = [...page.querySelectorAll('button')].find((button) => button.textContent === 'Se déconnecter')!

    await act(async () => signOutButton.click())

    expect(clearSession).toHaveBeenCalledOnce()
    expect(page.querySelector('[data-testid="location"]')?.textContent).toBe('/login')
  })
})
