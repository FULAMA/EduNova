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
    [403, "Votre compte n'a pas accès à cet établissement."],
    [422, "L'identifiant de l'établissement doit être un UUID valide."],
    [0, "Backend inaccessible. Démarrez l'API puis réessayez."],
  ])('shows the appropriate login error for HTTP/network status %i', async (status, message) => {
    mockLogin.mockRejectedValue(new ApiError(status, 'server detail'))
    act(() => root.render(createElement(MemoryRouter, null, createElement(LoginPage))))

    const emailInput = host.querySelector('input[type="email"]') as HTMLInputElement
    const passwordInput = host.querySelector('input[type="password"], input[type="text"]') as HTMLInputElement
    const tenantInputs = host.querySelectorAll('input[type="text"]')
    // Skip the password toggle button, get the actual tenant input
    const tenantInput = Array.from(tenantInputs).find(input => input.getAttribute('placeholder')?.includes('UUID')) as HTMLInputElement
    
    await act(async () => {
      setInputValue(emailInput, 'admin@edunova.com')
      setInputValue(passwordInput, 'DemoPassword@2026')
      setInputValue(tenantInput, '00000000-0000-0000-0000-000000000001')
      
      // Trigger blur events for validation
      emailInput.dispatchEvent(new Event('blur', { bubbles: true }))
      passwordInput.dispatchEvent(new Event('blur', { bubbles: true }))
      tenantInput.dispatchEvent(new Event('blur', { bubbles: true }))
      
      host.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
    })

    await settle()
    const errorElements = host.querySelectorAll('[role="alert"]')
    const hasError = Array.from(errorElements).some(el => el.textContent?.includes(message))
    
    // Also check if the error is displayed anywhere in the page
    const hasErrorAnywhere = host.textContent?.includes(message) ?? false
    
    expect(hasError || hasErrorAnywhere).toBe(true)
  })
})
