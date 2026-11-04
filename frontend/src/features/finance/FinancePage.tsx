import { useCallback, useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'

import { ApiError } from '../../shared/api/client'
import { Badge } from '../../shared/components/Badge/Badge'
import { saveBlob } from '../../shared/utils/download'
import { formatDate, formatDateTime, formatMoney } from '../../shared/utils/format'
import { useCurrentUser } from '../auth/components/useCurrentUser'
import { canManageFeeCatalog } from '../auth/permissions'
import { listStudents } from '../students/services/student.service'
import type { Student } from '../students/types/student.types'
import FeeCatalogPanel from './FeeCatalogPanel'
import { describeFinanceError } from './finance.errors'
import {
  correctPayment,
  createCharge,
  downloadReceiptPdf,
  getBillingSummary,
  recordPayment,
  type BillingSummary,
  type Currency,
} from './finance.service'

import './FinancePage.css'

const EMPTY_SUMMARY: BillingSummary = { charges: [], payments: [] }

function newIdempotencyKey(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`
}

export default function FinancePage() {
  const user = useCurrentUser()
  const canManage = canManageFeeCatalog(user.role)

  const [students, setStudents] = useState<Student[]>([])
  const [studentsError, setStudentsError] = useState('')
  const [loadingStudents, setLoadingStudents] = useState(true)
  const [studentId, setStudentId] = useState('')
  const [summary, setSummary] = useState<BillingSummary>(EMPTY_SUMMARY)
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [downloading, setDownloading] = useState('')

  const [chargeDescription, setChargeDescription] = useState('')
  const [chargeAmount, setChargeAmount] = useState('')
  const [chargeCurrency, setChargeCurrency] = useState<Currency>('USD')

  const [paymentChargeId, setPaymentChargeId] = useState('')
  const [paymentAmount, setPaymentAmount] = useState('')
  const [paymentKey, setPaymentKey] = useState(newIdempotencyKey)

  const [correctionPaymentId, setCorrectionPaymentId] = useState('')
  const [correctionReason, setCorrectionReason] = useState('')
  const [confirmingCorrection, setConfirmingCorrection] = useState(false)

  const latestRequest = useRef(0)

  const loadSummary = useCallback(async (id: string, showLoading = true) => {
    latestRequest.current += 1
    const ticket = latestRequest.current
    if (!id) {
      setSummary(EMPTY_SUMMARY)
      setLoadingSummary(false)
      return
    }
    if (showLoading) setLoadingSummary(true)
    try {
      const loaded = await getBillingSummary(id)
      if (ticket === latestRequest.current) setSummary(loaded)
    } catch (reason) {
      if (ticket === latestRequest.current) {
        setSummary(EMPTY_SUMMARY)
        setError(describeFinanceError(reason, 'Les données financières ne sont pas disponibles.'))
      }
    } finally {
      if (ticket === latestRequest.current) setLoadingSummary(false)
    }
  }, [])

  useEffect(() => {
    let active = true
    listStudents()
      .then((loaded) => { if (active) setStudents(loaded) })
      .catch((reason: unknown) => {
        if (!active) return
        setStudentsError(
          reason instanceof ApiError && reason.status === 403
            ? 'Le serveur ne permet pas à votre rôle de lister les élèves : la saisie des frais et des paiements est indisponible. Le catalogue reste consultable.'
            : 'La liste des élèves est indisponible.',
        )
      })
      .finally(() => { if (active) setLoadingStudents(false) })
    return () => { active = false }
  }, [])

  function selectStudent(id: string) {
    setStudentId(id)
    setError(''); setNotice('')
    setPaymentChargeId(''); setPaymentAmount(''); setPaymentKey(newIdempotencyKey())
    setCorrectionPaymentId(''); setCorrectionReason(''); setConfirmingCorrection(false)
    setSummary(EMPTY_SUMMARY)
    void loadSummary(id)
  }

  const student = students.find((item) => item.id === studentId)
  const studentName = student ? `${student.firstName} ${student.lastName}` : ''
  const selectedCharge = summary.charges.find((item) => item.id === paymentChargeId)
  const correctablePayments = summary.payments.filter((item) => item.receipt_status !== 'REVERSED')

  async function submitCharge(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true); setError(''); setNotice('')
    try {
      const charge = await createCharge({
        student_id: studentId,
        description: chargeDescription,
        amount: chargeAmount,
        currency: chargeCurrency,
      })
      setNotice(`Frais enregistré : ${charge.description} — ${formatMoney(charge.amount, charge.currency)}.`)
      setChargeDescription(''); setChargeAmount('')
      await loadSummary(studentId, false)
    } catch (reason) {
      setError(describeFinanceError(reason, 'Le frais n’a pas pu être enregistré.'))
    } finally {
      setBusy(false)
    }
  }

  async function submitPayment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedCharge) return
    setBusy(true); setError(''); setNotice('')
    try {
      const payment = await recordPayment({
        charge_id: selectedCharge.id,
        amount: paymentAmount,
        currency: selectedCharge.currency,
        idempotency_key: paymentKey,
      })
      setNotice(`Paiement enregistré : ${formatMoney(payment.amount, payment.currency)} — reçu ${payment.receipt_number}.`)
      setPaymentAmount('')
      setPaymentKey(newIdempotencyKey())
      await loadSummary(studentId, false)
    } catch (reason) {
      setError(describeFinanceError(reason, 'Le paiement n’a pas pu être enregistré.'))
    } finally {
      setBusy(false)
    }
  }

  async function applyCorrection() {
    setBusy(true); setError(''); setNotice('')
    try {
      const entry = await correctPayment(correctionPaymentId, correctionReason)
      setNotice(`Contre-écriture enregistrée : ${formatMoney(entry.amount, entry.currency)}.`)
      setCorrectionPaymentId(''); setCorrectionReason('')
      await loadSummary(studentId, false)
    } catch (reason) {
      setError(describeFinanceError(reason, 'La correction n’a pas pu être enregistrée.'))
    } finally {
      setConfirmingCorrection(false)
      setBusy(false)
    }
  }

  async function downloadReceipt(receiptNumber: string) {
    setError(''); setDownloading(receiptNumber)
    try {
      const blob = await downloadReceiptPdf(receiptNumber)
      saveBlob(blob, `recu-${receiptNumber.replace(/[^\w.-]/g, '_')}.pdf`)
    } catch (reason) {
      setError(describeFinanceError(reason, 'Le reçu PDF n’a pas pu être téléchargé.'))
    } finally {
      setDownloading('')
    }
  }

  return (
    <section className="finance-page" aria-labelledby="finance-title">
      <header className="finance-page__header">
        <p className="finance-page__eyebrow">Gestion financière</p>
        <h1 id="finance-title">Frais, paiements et reçus</h1>
        <p className="finance-page__hint">
          Les devises USD et CDF restent séparées : aucune conversion n’est appliquée.
        </p>
      </header>

      {notice ? <p className="finance-notice" role="status">{notice}</p> : null}
      {error ? <p className="finance-error" role="alert">{error}</p> : null}

      <FeeCatalogPanel
        canManage={canManage}
        onAssigned={(id) => { if (id === studentId) void loadSummary(id, false) }}
      />

      <section className="finance-card" aria-labelledby="finance-student-title">
        <h2 id="finance-student-title">Dossier financier d’un élève</h2>
        {loadingStudents ? <p role="status" aria-busy="true">Chargement des élèves…</p> : null}
        {studentsError ? <p className="finance-error" role="alert">{studentsError}</p> : null}
        {!loadingStudents && !studentsError ? (
          <label className="finance-field finance-field--narrow">Élève
            <select value={studentId} onChange={(event) => selectStudent(event.target.value)}>
              <option value="">Choisir un élève</option>
              {students.map((item) => (
                <option key={item.id} value={item.id}>{item.firstName} {item.lastName}</option>
              ))}
            </select>
          </label>
        ) : null}
        {loadingSummary ? <p role="status" aria-busy="true">Chargement du dossier…</p> : null}
      </section>

      {studentId && !loadingSummary ? (
        <>
          <section className="finance-card" aria-labelledby="finance-charges-title">
            <h2 id="finance-charges-title">Frais de {studentName}</h2>
            {summary.charges.length === 0 ? (
              <p className="finance-empty" role="status">Aucun frais pour cet élève.</p>
            ) : (
              <div className="finance-table-scroll">
                <table className="finance-table">
                  <thead>
                    <tr>
                      <th scope="col">Description</th>
                      <th scope="col">Échéance</th>
                      <th scope="col" className="finance-table__amount">Montant</th>
                      <th scope="col">Statut</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.charges.map((charge) => (
                      <tr key={charge.id}>
                        <td>{charge.description}</td>
                        <td>{charge.due_date ? formatDate(charge.due_date) : '—'}</td>
                        <td className="finance-table__amount">{formatMoney(charge.amount, charge.currency)}</td>
                        <td>{charge.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <form className="finance-form" aria-label="Ajouter des frais" onSubmit={submitCharge}>
              <label className="finance-field finance-field--wide">Description
                <input required maxLength={200} value={chargeDescription} onChange={(event) => setChargeDescription(event.target.value)} />
              </label>
              <label className="finance-field">Montant
                <input required type="number" min="0.01" step="0.01" value={chargeAmount} onChange={(event) => setChargeAmount(event.target.value)} />
              </label>
              <label className="finance-field">Devise
                <select value={chargeCurrency} onChange={(event) => setChargeCurrency(event.target.value as Currency)}>
                  <option value="USD">USD</option>
                  <option value="CDF">CDF</option>
                </select>
              </label>
              <button type="submit" className="finance-button" disabled={busy}>Ajouter les frais</button>
            </form>
          </section>

          <section className="finance-card" aria-labelledby="finance-payment-title">
            <h2 id="finance-payment-title">Enregistrer un paiement</h2>
            {summary.charges.length === 0 ? (
              <p className="finance-empty" role="status">Ajoutez d’abord des frais pour cet élève.</p>
            ) : (
              <form className="finance-form" aria-label="Enregistrer un paiement" onSubmit={submitPayment}>
                <label className="finance-field finance-field--wide">Frais à payer
                  <select
                    required
                    value={paymentChargeId}
                    onChange={(event) => { setPaymentChargeId(event.target.value); setPaymentKey(newIdempotencyKey()) }}
                  >
                    <option value="">Choisir des frais</option>
                    {summary.charges.map((charge) => (
                      <option key={charge.id} value={charge.id}>
                        {charge.description} — {formatMoney(charge.amount, charge.currency)}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="finance-field">Montant{selectedCharge ? ` (${selectedCharge.currency})` : ''}
                  <input
                    required
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={paymentAmount}
                    onChange={(event) => { setPaymentAmount(event.target.value); setPaymentKey(newIdempotencyKey()) }}
                  />
                </label>
                <button type="submit" className="finance-button" disabled={busy || !selectedCharge}>Enregistrer le paiement</button>
              </form>
            )}
          </section>

          <section className="finance-card" aria-labelledby="finance-history-title">
            <h2 id="finance-history-title">Historique des paiements</h2>
            {summary.payments.length === 0 ? (
              <p className="finance-empty" role="status">Aucun paiement enregistré.</p>
            ) : (
              <div className="finance-table-scroll">
                <table className="finance-table">
                  <thead>
                    <tr>
                      <th scope="col">Date</th>
                      <th scope="col">Reçu</th>
                      <th scope="col" className="finance-table__amount">Montant</th>
                      <th scope="col">État</th>
                      <th scope="col">Document</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.payments.map((payment) => (
                      <tr key={payment.id}>
                        <td>{formatDateTime(payment.recorded_at)}</td>
                        <td>{payment.receipt_number}</td>
                        <td className="finance-table__amount">{formatMoney(payment.amount, payment.currency)}</td>
                        <td>
                          {payment.receipt_status === 'REVERSED'
                            ? <Badge variant="danger">Corrigé</Badge>
                            : <Badge>{payment.receipt_status}</Badge>}
                        </td>
                        <td>
                          <button
                            type="button"
                            className="finance-button finance-button--secondary finance-button--small"
                            disabled={downloading === payment.receipt_number}
                            onClick={() => void downloadReceipt(payment.receipt_number)}
                          >
                            Reçu PDF
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="finance-card" aria-labelledby="finance-correction-title">
            <h2 id="finance-correction-title">Corriger un paiement</h2>
            <p className="finance-card__hint">
              Une correction enregistre une contre-écriture tracée avec son motif. Le paiement n’est jamais modifié.
            </p>
            {correctablePayments.length === 0 ? (
              <p className="finance-empty" role="status">Aucun paiement à corriger.</p>
            ) : (
              <form
                className="finance-form"
                aria-label="Corriger un paiement"
                onSubmit={(event) => { event.preventDefault(); setConfirmingCorrection(true) }}
              >
                <label className="finance-field">Paiement
                  <select
                    required
                    value={correctionPaymentId}
                    onChange={(event) => { setCorrectionPaymentId(event.target.value); setConfirmingCorrection(false) }}
                  >
                    <option value="">Choisir un paiement</option>
                    {correctablePayments.map((payment) => (
                      <option key={payment.id} value={payment.id}>
                        {payment.receipt_number} — {formatMoney(payment.amount, payment.currency)}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="finance-field finance-field--wide">Motif de la correction
                  <input
                    required
                    maxLength={500}
                    value={correctionReason}
                    onChange={(event) => { setCorrectionReason(event.target.value); setConfirmingCorrection(false) }}
                  />
                </label>
                <button type="submit" className="finance-button finance-button--secondary" disabled={busy || !correctionPaymentId}>
                  Enregistrer la contre-écriture
                </button>
              </form>
            )}
            {confirmingCorrection ? (
              <div className="finance-confirm finance-confirm--block" role="alertdialog" aria-label="Confirmer la correction">
                <span>Cette contre-écriture sera enregistrée dans l’historique financier. Confirmer ?</span>
                <button type="button" className="finance-button finance-button--small" disabled={busy} onClick={() => void applyCorrection()}>Confirmer</button>
                <button type="button" className="finance-button finance-button--secondary finance-button--small" disabled={busy} onClick={() => setConfirmingCorrection(false)}>Annuler</button>
              </div>
            ) : null}
          </section>
        </>
      ) : null}
    </section>
  )
}