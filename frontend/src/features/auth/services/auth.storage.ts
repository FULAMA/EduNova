export type AuthSession = {
  accessToken: string
  refreshToken: string
  email: string
  tenantId: string
}

export const SESSION_EXPIRED_EVENT = 'edunova:session-expired'

const SESSION_KEY = 'edunova.auth.session'

export function saveSession(session: AuthSession): void {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function getSession(): AuthSession | null {
  const rawSession = sessionStorage.getItem(SESSION_KEY)

  if (!rawSession) {
    return null
  }

  try {
    const session = JSON.parse(rawSession) as Partial<AuthSession>

    if (
      typeof session.accessToken !== 'string' ||
      typeof session.refreshToken !== 'string' ||
      typeof session.email !== 'string' ||
      typeof session.tenantId !== 'string'
    ) {
      return null
    }

    return session as AuthSession
  } catch {
    return null
  }
}

export function clearSession(): void {
  sessionStorage.removeItem(SESSION_KEY)
}
