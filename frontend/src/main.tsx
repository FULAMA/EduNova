import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './shared/styles/tokens.css'
import './shared/styles/reset.css'
import './shared/styles/globals.css'
import '../styled-system/styles.css'

import App from './App'

if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    void navigator.serviceWorker.register('/sw.js', { scope: '/' })
  })
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
