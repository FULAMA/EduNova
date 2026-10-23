import { useEffect, useRef } from 'react'

import './GoogleLoginButton.css'

type GoogleCredentialResponse = {
  credential: string
}

type GoogleLoginButtonProps = {
  onCredential: (credential: string) => void
}

type GoogleIdentityApi = {
  accounts: {
    id: {
      initialize: (options: {
        client_id: string
        callback: (response: GoogleCredentialResponse) => void
      }) => void
      renderButton: (
        element: HTMLElement,
        options: { theme: string; size: string; width: number },
      ) => void
    }
  }
}

declare global {
  interface Window {
    google?: GoogleIdentityApi
  }
}

const GOOGLE_SCRIPT_ID = 'google-identity-services'
const GOOGLE_SCRIPT_URL = 'https://accounts.google.com/gsi/client'

function GoogleMark() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="google-login-button__mark">
      <path fill="#4285F4" d="M21.35 12.23c0-.78-.07-1.53-.22-2.23H12v4.22h5.24a4.48 4.48 0 0 1-1.94 2.94v2.45h3.14c1.84-1.69 2.91-4.18 2.91-7.38Z" />
      <path fill="#34A853" d="M12 21.75c2.63 0 4.84-.87 6.45-2.36l-3.14-2.45c-.87.58-1.98.92-3.31.92-2.54 0-4.7-1.72-5.47-4.03H3.28v2.53A9.74 9.74 0 0 0 12 21.75Z" />
      <path fill="#FBBC05" d="M6.53 13.83a5.85 5.85 0 0 1 0-3.66V7.64H3.28a9.75 9.75 0 0 0 0 8.72l3.25-2.53Z" />
      <path fill="#EA4335" d="M12 6.14c1.43 0 2.71.49 3.72 1.46l2.79-2.79C16.84 3.25 14.63 2.25 12 2.25a9.74 9.74 0 0 0-8.72 5.39l3.25 2.53C7.3 7.86 9.46 6.14 12 6.14Z" />
    </svg>
  )
}

export function GoogleLoginButton({
  onCredential,
}: GoogleLoginButtonProps) {
  const buttonRef = useRef<HTMLDivElement>(null)
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined

  useEffect(() => {
    if (!clientId || !buttonRef.current) {
      return
    }

    const render = () => {
      if (!window.google || !buttonRef.current) {
        return
      }

      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: ({ credential }) => onCredential(credential),
      })
      buttonRef.current.replaceChildren()
      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: 'outline',
        size: 'large',
        width: 360,
      })
    }

    const existingScript = document.getElementById(GOOGLE_SCRIPT_ID)
    if (existingScript) {
      render()
      return
    }

    const script = document.createElement('script')
    script.id = GOOGLE_SCRIPT_ID
    script.src = GOOGLE_SCRIPT_URL
    script.async = true
    script.defer = true
    script.onload = render
    document.head.appendChild(script)
  }, [clientId, onCredential])

  if (!clientId) {
    return (
      <button
        type="button"
        className="google-login-button google-login-button--unavailable"
        disabled
        aria-label="Connexion avec Google indisponible"
        title="Configurez VITE_GOOGLE_CLIENT_ID pour activer Google"
      >
        <GoogleMark />
        <span>Continuer avec Google</span>
        <small>Non configure</small>
      </button>
    )
  }

  return <div ref={buttonRef} aria-label="Connexion avec Google" />
}
