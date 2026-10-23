// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../../shared/api/client'
import { login } from '../services/auth.service'
import LoginPage from './LoginPage'

vi.mock('../services/auth.service', () => ({
  login: vi.fn(),
  loginWithGoogle: vi.fn(),
  saveSession: vi.fn(),
  verifyLoginTwoFactor: vi.fn(),
}))

vi.mock('../components/GoogleLoginButton', () => ({
  GoogleLoginButton: () => null,
}))

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const mockLogin = vi.mocked(login)
let root: Root
let host: HTMLDivElement

async function settle() {
  await act(async () => { await Promise.resolve(); await Promise.resolve() })
}

function setInputValue(input: HTMLInputElement, value: string) {
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
  setter?.call(input, value)
  input.dispatchEvent(new Event('input', { bubbles: true }))
  input.dispatchEvent(new Event('change', { bubbles: true }))
}

describe('LoginPage', () => {
  beforeEach(() => {
    host = document.createElement('div')
    document.body.append(host)
    root = createRoot(host)
  })

  afterEach(() => {
    act(() => root.unmount())
    host.remove()
    vi.resetAllMocks()
  })

  it.each([
    [401, 'Adresse e-mail ou mot de passe incorrect.'],
    [403, 'Votre compte n a pas acces a cet etablissement.'],
    [422, 'L identifiant de l etablissement doit etre un UUID valide.'],
    [0, 'Backend inaccessible. Demarrez l API puis reessayez.'],
  ])('shows the appropriate login error for HTTP/network status %i', async (status, message) => {
    mockLogin.mockRejectedValue(new ApiError(status, 'server detail'))
    act(() => root.render(createElement(MemoryRouter, null, createElement(LoginPage))))

    const inputs = host.querySelectorAll('input')
    await act(async () => {
      setInputValue(inputs[0] as HTMLInputElement, 'admin@edunova.com')
      setInputValue(inputs[1] as HTMLInputElement, 'DemoPassword@2026')
      setInputValue(inputs[2] as HTMLInputElement, '00000000-0000-0000-0000-000000000001')
      host.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
    })

    await settle()
    expect(host.querySelector('[role="alert"]')?.textContent).toContain(message)
  })
})
