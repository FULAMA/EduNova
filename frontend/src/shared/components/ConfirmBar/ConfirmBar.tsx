import { useEffect, useId, useRef } from 'react'

import './ConfirmBar.css'

type ConfirmBarProps = {
  message: string
  confirmLabel: string
  cancelLabel?: string
  busy?: boolean
  onConfirm: () => void
  onCancel: () => void
}

/** Confirmation en ligne pour une action irréversible ou à effet métier. Le focus démarre sur « Annuler ». */
export function ConfirmBar({
  message,
  confirmLabel,
  cancelLabel = 'Annuler',
  busy = false,
  onConfirm,
  onCancel,
}: ConfirmBarProps) {
  const messageId = useId()
  const cancelRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    cancelRef.current?.focus()
  }, [])

  return (
    <div
      className="confirm-bar"
      role="alertdialog"
      aria-labelledby={messageId}
      onKeyDown={(event) => {
        if (event.key === 'Escape') onCancel()
      }}
    >
      <p id={messageId} className="confirm-bar__message">{message}</p>
      <div className="confirm-bar__actions">
        <button type="button" className="confirm-bar__confirm" disabled={busy} onClick={onConfirm}>
          {confirmLabel}
        </button>
        <button ref={cancelRef} type="button" className="confirm-bar__cancel" disabled={busy} onClick={onCancel}>
          {cancelLabel}
        </button>
      </div>
    </div>
  )
}