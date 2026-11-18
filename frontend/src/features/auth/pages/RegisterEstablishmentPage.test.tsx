// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../../shared/api/client'
import { registerEstablishment } from '../services/auth.service'
import RegisterEstablishmentPage from './RegisterEstablishmentPage'

vi.mock('../services/auth.service', () => ({
  registerEstablishment: vi.fn(),
}))

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const mockRegisterEstablishment = vi.mocked(registerEstablishment)
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

function getInputByName(container: HTMLElement, name: string): HTMLInputElement | null {
  return container.querySelector(`input[name="${name}"]`) as HTMLInputElement | null
}

describe('RegisterEstablishmentPage', () => {
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

  it('renders the registration form', async () => {
    act(() => {
      root.render(createElement(MemoryRouter, null, createElement(RegisterEstablishmentPage)))
    })
    await settle()

    const heading = host.querySelector('h1')
    expect(heading?.textContent).toBe('Créer un établissement')

    const schoolNameInput = getInputByName(host, 'school_name')
    const adminNameInput = getInputByName(host, 'admin_name')
    const emailInput = getInputByName(host, 'email')
    const passwordInputs = host.querySelectorAll('input[type="password"]')

    expect(schoolNameInput).not.toBeNull()
    expect(adminNameInput).not.toBeNull()
    expect(emailInput).not.toBeNull()
    expect(passwordInputs.length).toBeGreaterThanOrEqual(2)
  })

  it('shows validation errors when form is submitted with empty fields', async () => {
    act(() => {
      root.render(createElement(MemoryRouter, null, createElement(RegisterEstablishmentPage)))
    })
    await settle()

    const form = host.querySelector('form')
    expect(form).not.toBeNull()

    await act(async () => {
      form?.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
    })

    await settle()

    const errorElements = host.querySelectorAll('.register-form__field-error')
    expect(errorElements.length).toBeGreaterThan(0)
  })

  it('calls registerEstablishment with correct data on valid form submission', async () => {
    mockRegisterEstablishment.mockResolvedValue({
      tenant_id: '00000000-0000-0000-0000-000000000001',
      tenant_name: 'Test School',
      tenant_slug: 'test-school',
      user_id: '00000000-0000-0000-0000-000000000002',
      admin_name: 'Test Admin',
      email: 'test@example.com',
      role: 'ADMIN',
    })

    act(() => {
      root.render(createElement(MemoryRouter, null, createElement(RegisterEstablishmentPage)))
    })
    await settle()

    const schoolNameInput = getInputByName(host, 'school_name')
    const adminNameInput = getInputByName(host, 'admin_name')
    const emailInput = getInputByName(host, 'email')
    const passwordInput = getInputByName(host, 'password')
    const confirmPasswordInput = getInputByName(host, 'confirm_password')
    const form = host.querySelector('form')

    expect(schoolNameInput).not.toBeNull()
    expect(adminNameInput).not.toBeNull()
    expect(emailInput).not.toBeNull()
    expect(passwordInput).not.toBeNull()
    expect(confirmPasswordInput).not.toBeNull()

    await act(async () => {
      setInputValue(schoolNameInput!, 'Test School')
      setInputValue(adminNameInput!, 'Test Admin')
      setInputValue(emailInput!, 'test@example.com')
      setInputValue(passwordInput!, 'password123')
      setInputValue(confirmPasswordInput!, 'password123')
      
      form?.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
    })

    await settle()

    expect(mockRegisterEstablishment).toHaveBeenCalledWith({
      school_name: 'Test School',
      admin_name: 'Test Admin',
      email: 'test@example.com',
      password: 'password123',
    })
  })

  it('shows success message on successful registration', async () => {
    mockRegisterEstablishment.mockResolvedValue({
      tenant_id: '00000000-0000-0000-0000-000000000001',
      tenant_name: 'Test School',
      tenant_slug: 'test-school',
      user_id: '00000000-0000-0000-0000-000000000002',
      admin_name: 'Test Admin',
      email: 'test@example.com',
      role: 'ADMIN',
    })

    act(() => {
      root.render(createElement(MemoryRouter, null, createElement(RegisterEstablishmentPage)))
    })
    await settle()

    const schoolNameInput = getInputByName(host, 'school_name')
    const adminNameInput = getInputByName(host, 'admin_name')
    const emailInput = getInputByName(host, 'email')
    const passwordInput = getInputByName(host, 'password')
    const confirmPasswordInput = getInputByName(host, 'confirm_password')
    const form = host.querySelector('form')

    expect(schoolNameInput).not.toBeNull()

    await act(async () => {
      setInputValue(schoolNameInput!, 'Test School')
      setInputValue(adminNameInput!, 'Test Admin')
      setInputValue(emailInput!, 'test@example.com')
      setInputValue(passwordInput!, 'password123')
      setInputValue(confirmPasswordInput!, 'password123')
      
      form?.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
    })

    await settle()

    const successMessage = host.querySelector('.register-form__success')
    expect(successMessage?.textContent).toContain('Inscription réussie')
  })

  it('shows error message on API error', async () => {
    mockRegisterEstablishment.mockRejectedValue(new ApiError(409, 'Cette adresse email est déjà utilisée.'))

    act(() => {
      root.render(createElement(MemoryRouter, null, createElement(RegisterEstablishmentPage)))
    })
    await settle()

    const schoolNameInput = getInputByName(host, 'school_name')
    const adminNameInput = getInputByName(host, 'admin_name')
    const emailInput = getInputByName(host, 'email')
    const passwordInput = getInputByName(host, 'password')
    const confirmPasswordInput = getInputByName(host, 'confirm_password')
    const form = host.querySelector('form')

    expect(schoolNameInput).not.toBeNull()

    await act(async () => {
      setInputValue(schoolNameInput!, 'Test School')
      setInputValue(adminNameInput!, 'Test Admin')
      setInputValue(emailInput!, 'test@example.com')
      setInputValue(passwordInput!, 'password123')
      setInputValue(confirmPasswordInput!, 'password123')
      
      form?.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
    })

    await settle()

    const errorMessage = host.querySelector('.register-form__error')
    expect(errorMessage?.textContent).toContain('déjà utilisée')
  })

  it('shows loading state during submission', async () => {
    mockRegisterEstablishment.mockImplementation(() => new Promise(() => {}))

    act(() => {
      root.render(createElement(MemoryRouter, null, createElement(RegisterEstablishmentPage)))
    })
    await settle()

    const schoolNameInput = getInputByName(host, 'school_name')
    const adminNameInput = getInputByName(host, 'admin_name')
    const emailInput = getInputByName(host, 'email')
    const passwordInput = getInputByName(host, 'password')
    const confirmPasswordInput = getInputByName(host, 'confirm_password')
    const form = host.querySelector('form')
    const submitButton = host.querySelector('.register-form__submit')

    expect(schoolNameInput).not.toBeNull()

    await act(async () => {
      setInputValue(schoolNameInput!, 'Test School')
      setInputValue(adminNameInput!, 'Test Admin')
      setInputValue(emailInput!, 'test@example.com')
      setInputValue(passwordInput!, 'password123')
      setInputValue(confirmPasswordInput!, 'password123')
      
      form?.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
    })

    await settle()

    expect(submitButton?.textContent).toContain('Inscription en cours')
  })

  it('has a link to login page', async () => {
    act(() => {
      root.render(createElement(MemoryRouter, null, createElement(RegisterEstablishmentPage)))
    })
    await settle()

    const loginLink = host.querySelector('.register-form__login-link--action')
    expect(loginLink).not.toBeNull()
    expect(loginLink?.getAttribute('href')).toBe('/login')
  })
})
