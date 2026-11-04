import {
  clearSession,
  getSession,
  saveSession,
  SESSION_EXPIRED_EVENT,
} from '../../features/auth/services/auth.storage'

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
).replace(/\/$/, '')

const MSG_UNREACHABLE = 'Le serveur API est inaccessible.'
const MSG_SESSION_EXPIRED = 'La session a expiré. Veuillez vous reconnecter.'
const MSG_REFRESH_UNAVAILABLE =
  'Le renouvellement de session est temporairement indisponible.'
const MSG_SERVER_ERROR = 'Le serveur est indisponible. Réessayez plus tard.'

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

function validationMessage(payload: unknown): string | null {
  const detail = (payload as { detail?: unknown } | null)?.detail
  if (!Array.isArray(detail)) return null
  const messages = detail
    .map((item) => (item && typeof item === 'object' ? (item as { msg?: unknown }).msg : null))
    .filter((msg): msg is string => typeof msg === 'string')
  return messages.length > 0 ? `Données invalides : ${messages.join(' ; ')}` : null
}

function errorMessage(payload: unknown): string {
  if (
    payload &&
    typeof payload === 'object' &&
    typeof (payload as { detail?: unknown }).detail === 'string'
  ) {
    return (payload as { detail: string }).detail
  }

  return validationMessage(payload) ?? MSG_SERVER_ERROR
}

/**
 * Envoie la requête, tente un refresh sur 401 authentifié, rejoue une fois,
 * et lève ApiError si la réponse finale n'est pas OK.
 * Retourne une Response dont le corps n'a pas été consommé.
 */
async function authorizedFetch(
  path: string,
  options: ApiRequestOptions,
): Promise<Response> {
  const { authenticated = false, ...requestOptions } = options
  const send = async (): Promise<Response> => {
    try {
      return await fetch(`${API_BASE_URL}${path}`, {
        ...requestOptions,
        headers: requestHeaders(options, authenticated),
      })
    } catch {
      throw new ApiError(0, MSG_UNREACHABLE)
    }
  }

  let response = await send()

  if (response.status === 401 && authenticated) {
    const refreshResult = await refreshSession()
    if (refreshResult === 'refreshed') {
      response = await send()
    } else if (refreshResult === 'unavailable') {
      throw new ApiError(0, MSG_REFRESH_UNAVAILABLE)
    } else if (!getSession()) {
      throw new ApiError(401, MSG_SESSION_EXPIRED)
    }
  }

  if (!response.ok) {
    if (response.status === 401 && authenticated) {
      notifySessionExpired()
      throw new ApiError(401, MSG_SESSION_EXPIRED)
    }

    throw new ApiError(response.status, errorMessage(await parseResponse(response)))
  }

  return response
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const response = await authorizedFetch(path, options)
  return (await parseResponse(response)) as T
}

export async function apiRequestBlob(
  path: string,
  options: ApiRequestOptions = {},
): Promise<Blob> {
  const response = await authorizedFetch(path, options)
  return response.blob()
}