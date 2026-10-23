import { apiRequest } from '../../../shared/api/client'

export {
  clearSession,
  getSession,
  saveSession,
  SESSION_EXPIRED_EVENT,
} from './auth.storage'
export type { AuthSession } from './auth.storage'

export type LoginRequest = {
  email: string
  password: string
  tenant_id: string
}

export type LoginResponse = {
  authenticated: boolean
  two_factor_required: boolean
  two_factor_token: string | null
  access_token: string | null
  refresh_token: string | null
  email?: string | null
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
): Promise<GoogleLoginResponse> {
  return apiRequest<GoogleLoginResponse>('/auth/google', {
    method: 'POST',
    body: JSON.stringify({
      id_token: idToken,
      tenant_id: tenantId,
    }),
  })
}

export async function linkGoogleIdentity(
  idToken: string,
): Promise<GoogleLinkResponse> {
  return apiRequest<GoogleLinkResponse>('/auth/google/link', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ id_token: idToken }),
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
