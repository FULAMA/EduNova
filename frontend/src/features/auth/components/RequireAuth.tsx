import type { ReactNode } from 'react'
import { useEffect, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { ApiError } from '../../../shared/api/client'
import { CurrentUserProvider } from './CurrentUserProvider'
import {
  clearSession,
  getCurrentUser,
  getSession,
  SESSION_EXPIRED_EVENT,
} from '../services/auth.service'

type RequireAuthProps = {
  children: ReactNode
}

export function RequireAuth({ children }: RequireAuthProps) {
  const location = useLocation()
  const [session, setSession] = useState(getSession)
  const [status, setStatus] = useState<'loading' | 'authenticated' | 'unauthenticated' | 'error'>(
    session ? 'loading' : 'unauthenticated',
  )
  const [user, setUser] = useState<Awaited<ReturnType<typeof getCurrentUser>> | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    let cancelled = false

    const handleSessionExpired = () => {
      clearSession()
      if (!cancelled) {
        setSession(null)
        setUser(null)
        setStatus('unauthenticated')
      }
    }

    window.addEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)

    if (!session) {
      return () => {
        cancelled = true
        window.removeEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
      }
    }

    getCurrentUser(session.accessToken)
      .then((currentUser) => {
        if (!cancelled) {
          setUser(currentUser)
          setStatus('authenticated')
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          if (reason instanceof ApiError && reason.status === 401) {
            clearSession()
            setSession(null)
            setUser(null)
            setStatus('unauthenticated')
          } else {
            setStatus('error')
          }
        }
      })

    return () => {
      cancelled = true
      window.removeEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
    }
  }, [session, retryCount])

  if (status === 'loading') {
    return <main aria-busy="true">Vérification de la session...</main>
  }

  if (status === 'error') {
    return (
      <main role="alert">
        <p>Impossible de vérifier votre session. Vérifiez votre connexion puis réessayez.</p>
        <button
          type="button"
          onClick={() => {
            setStatus('loading')
            setRetryCount((count) => count + 1)
          }}
        >
          Réessayer
        </button>
      </main>
    )
  }

  if (status !== 'authenticated' || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <CurrentUserProvider user={user}>{children}</CurrentUserProvider>
}
