import { useEffect, useState } from 'react'

import { ApiError } from '../../shared/api/client'
import { listStudents } from '../students/services/student.service'
import type { Student } from '../students/types/student.types'
import { correctPayment, createCharge, getBillingSummary, recordPayment, type BillingSummary, type Currency } from './finance.service'

import './FinancePage.css'
import FeeCatalogPanel from './FeeCatalogPanel'

function errorText(reason: unknown): string {
  if (reason instanceof ApiError && reason.status === 403) return 'Votre compte ne peut pas gérer les finances de cet établissement.'
  if (reason instanceof ApiError && reason.status === 409) return 'Le paiement est en conflit avec le solde ou une opération précédente.'
  if (reason instanceof ApiError && reason.status === 401) return 'Votre session a expiré. Reconnectez-vous.'
  return 'Les données financières ne sont pas disponibles.'
}

export default function FinancePage() {
  const [students, setStudents] = useState<Student[]>([])
  const [studentId, setStudentId] = useState('')
  const [summary, setSummary] = useState<BillingSummary>({ charges: [], payments: [] })
  const [description, setDescription] = useState('')
  const [chargeAmount, setChargeAmount] = useState('')
  const [chargeCurrency, setChargeCurrency] = useState<Currency>('USD')
  const [paymentChargeId, setPaymentChargeId] = useState('')
  const [paymentAmount, setPaymentAmount] = useState('')
  const [paymentKey, setPaymentKey] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [correctionPaymentId, setCorrectionPaymentId] = useState('')
  const [correctionReason, setCorrectionReason] = useState('')

  async function loadSummary(id: string) {
    if (!id) { setSummary({ charges: [], payments: [] }); return }
    setSummary(await getBillingSummary(id))
  }

  useEffect(() => {
    void listStudents().then((loaded) => {
      setStudents(loaded)
      const first = loaded[0]?.id ?? ''
      setStudentId(first)
      return loadSummary(first)
    }).catch((reason: unknown) => setError(errorText(reason))).finally(() => setLoading(false))
  }, [])

  async function submitCharge(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSubmitting(true); setError('')
    try {
      await createCharge({ student_id: studentId, description, amount: chargeAmount, currency: chargeCurrency })
      setDescription(''); setChargeAmount(''); await loadSummary(studentId)
    } catch (reason) { setError(errorText(reason)) } finally { setSubmitting(false) }
  }

  async function submitPayment(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSubmitting(true); setError('')
    try {
      const charge = summary.charges.find((item) => item.id === paymentChargeId)
      if (!charge) throw new Error('charge')
      await recordPayment({ charge_id: paymentChargeId, amount: paymentAmount, currency: charge.currency, idempotency_key: paymentKey })
      setPaymentAmount(''); setPaymentKey(''); await loadSummary(studentId)
    } catch (reason) { setError(errorText(reason)) } finally { setSubmitting(false) }
  }

  async function submitCorrection(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSubmitting(true); setError('')
    try { await correctPayment(correctionPaymentId, correctionReason); setCorrectionPaymentId(''); setCorrectionReason(''); await loadSummary(studentId) }
    catch (reason) { setError(errorText(reason)) } finally { setSubmitting(false) }
  }

  return <main className="finance-page">
    <FeeCatalogPanel />
    <header><p>Gestion financière</p><h1>Frais, paiements et reçus</h1><p>Les devises USD et CDF restent séparées, sans conversion automatique.</p></header>
    {loading ? <p role="status" aria-busy="true">Chargement des élèves...</p> : null}
    {error ? <p role="alert">{error}</p> : null}
    <label className="finance-page__student">Élève<select required value={studentId} onChange={(event) => { setStudentId(event.target.value); void loadSummary(event.target.value) }}>{students.map((student) => <option key={student.id} value={student.id}>{student.firstName} {student.lastName}</option>)}</select></label>
    <section><h2>Créer des frais</h2><form onSubmit={submitCharge}><input required aria-label="Description" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description" /><input required aria-label="Montant des frais" type="number" min="0.01" step="0.01" value={chargeAmount} onChange={(event) => setChargeAmount(event.target.value)} /><select aria-label="Devise des frais" value={chargeCurrency} onChange={(event) => setChargeCurrency(event.target.value as Currency)}><option>USD</option><option>CDF</option></select><button disabled={submitting || !studentId}>Créer</button></form></section>
    <section><h2>Enregistrer un paiement</h2>{summary.charges.length === 0 ? <p role="status">Aucun frais pour cet élève.</p> : <form onSubmit={submitPayment}><select required aria-label="Frais" value={paymentChargeId} onChange={(event) => setPaymentChargeId(event.target.value)}><option value="">Choisir des frais</option>{summary.charges.map((charge) => <option key={charge.id} value={charge.id}>{charge.description} - {charge.amount} {charge.currency}</option>)}</select><input required aria-label="Montant du paiement" type="number" min="0.01" step="0.01" value={paymentAmount} onChange={(event) => setPaymentAmount(event.target.value)} /><input required aria-label="Clé d idempotence" value={paymentKey} onChange={(event) => setPaymentKey(event.target.value)} placeholder="Référence unique" /><button disabled={submitting || !paymentChargeId}>Enregistrer</button></form>}</section>
    <section><h2>Historique des paiements</h2>{summary.payments.length === 0 ? <p role="status">Aucun paiement enregistré.</p> : <ul>{summary.payments.map((payment) => <li key={payment.id}>{payment.amount} {payment.currency} · reçu {payment.receipt_number}</li>)}</ul>}</section>
    <form onSubmit={submitCorrection}><label>Paiement à corriger<select required value={correctionPaymentId} onChange={(event) => setCorrectionPaymentId(event.target.value)}><option value="">Choisir un paiement</option>{summary.payments.filter((payment) => payment.receipt_status !== 'REVERSED').map((payment) => <option key={payment.id} value={payment.id}>{payment.receipt_number}</option>)}</select></label><label>Motif de correction<input required value={correctionReason} onChange={(event) => setCorrectionReason(event.target.value)} /></label><button disabled={submitting || !correctionPaymentId}>Enregistrer la contre-écriture</button></form>
  </main>
}

