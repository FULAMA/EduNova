import {
  clearSession,
  getSession,
  saveSession,
  SESSION_EXPIRED_EVENT,
} from '../../features/auth/services/auth.storage'

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
).replace(/\/$/, '')

export type ApiRequestOptions = RequestInit & {
  authenticated?: boolean
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type RefreshResponse = {
  authenticated: boolean
  access_token: string | null
  refresh_token: string | null
}

type RefreshResult = 'refreshed' | 'invalid' | 'unavailable'

let refreshPromise: Promise<RefreshResult> | null = null

function notifySessionExpired(): void {
  clearSession()

  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT))
  }
}

function requestHeaders(
  options: ApiRequestOptions,
  authenticated: boolean,
): Headers {
  const headers = new Headers(options.headers)
  headers.set('Accept', 'application/json')
  headers.set('Content-Type', 'application/json')

  if (authenticated) {
    const session = getSession()
    if (session) {
      headers.set('Authorization', `Bearer ${session.accessToken}`)
    }
  }

  return headers
}

async function parseResponse(response: Response): Promise<unknown> {
  return response.json().catch(() => null)
}

async function refreshSession(): Promise<RefreshResult> {
  if (refreshPromise) {
    return refreshPromise
  }

  const session = getSession()
  if (!session) {
    return 'invalid'
  }

  refreshPromise = (async () => {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: session.refreshToken }),
    })
    const payload = await parseResponse(response)

    if (!response.ok) {
      notifySessionExpired()
      return 'invalid'
    }

    if (
      !payload ||
      typeof payload !== 'object' ||
      !(payload as RefreshResponse).authenticated ||
      typeof (payload as RefreshResponse).access_token !== 'string' ||
      typeof (payload as RefreshResponse).refresh_token !== 'string'
    ) {
      notifySessionExpired()
      return 'invalid'
    }

    const refreshed = payload as RefreshResponse
    saveSession({
      ...session,
      accessToken: refreshed.access_token as string,
      refreshToken: refreshed.refresh_token as string,
    })
    return 'refreshed'
  })()

  try {
    return await refreshPromise
  } catch {
    // A network failure does not prove that the refresh token is invalid.
    return 'unavailable'
  } finally {
    refreshPromise = null
  }
}

function errorMessage(payload: unknown): string {
  if (
    payload &&
    typeof payload === 'object' &&
    typeof (payload as { detail?: unknown }).detail === 'string'
  ) {
    return (payload as { detail: string }).detail
  }

  return 'Le serveur est indisponible. Réessayez plus tard.'
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { authenticated = false, ...requestOptions } = options
  const request = async (): Promise<Response> => {
    try {
      return await fetch(`${API_BASE_URL}${path}`, {
        ...requestOptions,
        headers: requestHeaders(options, authenticated),
      })
    } catch {
      throw new ApiError(0, 'Le serveur API est inaccessible.')
    }
  }

  let response = await request()

  if (response.status === 401 && authenticated) {
    const refreshResult = await refreshSession()
    if (refreshResult === 'refreshed') {
      response = await request()
    } else if (refreshResult === 'unavailable') {
      throw new ApiError(
        0,
        'Le renouvellement de session est temporairement indisponible.',
      )
    } else if (!getSession()) {
      throw new ApiError(401, 'La session a expiré. Veuillez vous reconnecter.')
    }
  }

  const payload = await parseResponse(response)

  if (!response.ok) {
    if (response.status === 401 && authenticated) {
      notifySessionExpired()
      throw new ApiError(401, 'La session a expiré. Veuillez vous reconnecter.')
    }

    throw new ApiError(response.status, errorMessage(payload))
  }

  return payload as T
}

export async function apiRequestBlob(
  path: string,
  options: ApiRequestOptions = {},
): Promise<Blob> {
  const { authenticated = false, ...requestOptions } = options
  const request = async (): Promise<Response> => {
    try {
      return await fetch(`${API_BASE_URL}${path}`, {
        ...requestOptions,
        headers: requestHeaders(options, authenticated),
      })
    } catch {
      throw new ApiError(0, 'Le serveur API est inaccessible.')
    }
  }

  let response = await request()
  if (response.status === 401 && authenticated) {
    const refreshResult = await refreshSession()
    if (refreshResult === 'refreshed') response = await request()
    else if (refreshResult === 'unavailable') throw new ApiError(0, 'Le renouvellement de session est temporairement indisponible.')
    else if (!getSession()) throw new ApiError(401, 'La session a expire. Veuillez vous reconnecter.')
  }
  if (!response.ok) {
    const payload = await parseResponse(response)
    if (response.status === 401 && authenticated) {
      notifySessionExpired()
      throw new ApiError(401, 'La session a expire. Veuillez vous reconnecter.')
    }
    throw new ApiError(response.status, errorMessage(payload))
  }
  return response.blob()
}
