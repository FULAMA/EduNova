import { apiRequest } from '../../../shared/api/client'
import {
  clearSession,
  getSession,
  saveSession,
  SESSION_EXPIRED_EVENT,
} from './auth.storage'

export {
  clearSession,
  getSession,
  saveSession,
  SESSION_EXPIRED_EVENT,
}
export type { AuthSession } from './auth.storage'

export type RegisterEstablishmentRequest = {
  school_name: string
  admin_name: string
  email: string
  password: string
}

export type RegisterEstablishmentResponse = {
  tenant_id: string
  tenant_name: string
  tenant_slug: string
  user_id: string
  admin_name: string
  email: string
  role: string
}

export type TenantOption = {
  tenant_id: string
  tenant_name: string
  tenant_slug: string
  role: string
}

export type SelectTenantRequest = {
  tenant_selection_token: string
  tenant_id: string
}

export type LoginRequest = {
  email: string
  password: string
  tenant_id?: string
}

export type LoginResponse = {
  authenticated: boolean
  two_factor_required: boolean
  two_factor_token: string | null
  access_token: string | null
  refresh_token: string | null
  email?: string | null
  tenant_selection_required?: boolean
  tenant_selection_token?: string | null
  available_tenants?: TenantOption[]
}

export type VerifyLoginTwoFactorResponse = {
  authenticated: boolean
  access_token: string
  refresh_token: string
}

export type GoogleLoginResponse = LoginResponse

export type GoogleLinkResponse = {
  linked: boolean
}

export async function issueGoogleNonce(): Promise<string> {
  const response = await apiRequest<{ nonce: string }>('/auth/google/nonce', {
    method: 'POST',
  })
  return response.nonce
}

export type AuthenticatedUser = {
  id: string
  email: string
  role: string
  is_active: boolean
  two_factor_enabled: boolean
}

export async function login(
  request: LoginRequest,
): Promise<LoginResponse> {
  return apiRequest<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function verifyLoginTwoFactor(
  twoFactorToken: string,
  code: string,
): Promise<VerifyLoginTwoFactorResponse> {
  return apiRequest<VerifyLoginTwoFactorResponse>('/auth/2fa/login', {
    method: 'POST',
    body: JSON.stringify({
      two_factor_token: twoFactorToken,
      code,
    }),
  })
}

export async function loginWithGoogle(
  idToken: string,
  tenantId: string,
  nonce: string,
): Promise<GoogleLoginResponse> {
  return apiRequest<GoogleLoginResponse>('/auth/google', {
    method: 'POST',
    body: JSON.stringify({
      id_token: idToken,
      tenant_id: tenantId,
      nonce,
    }),
  })
}

export async function linkGoogleIdentity(
  idToken: string,
  nonce: string,
  password: string,
  totpCode?: string,
): Promise<GoogleLinkResponse> {
  return apiRequest<GoogleLinkResponse>('/auth/google/link', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({
      id_token: idToken,
      nonce,
      password,
      totp_code: totpCode,
    }),
  })
}

export async function getCurrentUser(
  accessToken: string,
): Promise<AuthenticatedUser> {
  return apiRequest<AuthenticatedUser>('/auth/me', {
    authenticated: true,
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
}

/**
 * Revokes the refresh token on the server when possible, then clears the
 * local session. Local cleanup always runs, even if the API call fails
 * (expired/invalid refresh, network error).
 */
export async function logout(): Promise<void> {
  const session = getSession()
  if (session?.refreshToken) {
    const apiBaseUrl = (
      import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8017'
    ).replace(/\/$/, '')
    try {
      await fetch(`${apiBaseUrl}/auth/logout`, {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: session.refreshToken }),
      })
    } catch {
      // Server revocation is best-effort; local session must still clear.
    }
  }
  clearSession()
}

export async function registerEstablishment(
  request: RegisterEstablishmentRequest,
): Promise<RegisterEstablishmentResponse> {
  return apiRequest<RegisterEstablishmentResponse>('/auth/register-establishment', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function selectTenant(
  request: SelectTenantRequest,
): Promise<LoginResponse> {
  return apiRequest<LoginResponse>('/auth/select-tenant', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
