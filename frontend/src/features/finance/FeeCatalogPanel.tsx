import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import { Badge, type BadgeVariant } from '../../shared/components/Badge/Badge'
import { formatMoney } from '../../shared/utils/format'
import { listStudents } from '../students/services/student.service'
import type { Student } from '../students/types/student.types'
import { describeFinanceError } from './finance.errors'
import {
  assignFeeType,
  createFeeType,
  listFeeTypes,
  updateFeeTypeStatus,
  type Currency,
  type FeeType,
} from './finance.service'

import './FinancePage.css'

type FeeCatalogPanelProps = {
  canManage: boolean
  onAssigned?: (studentId: string) => void
}

type PendingAction = { id: string; kind: 'assign' | 'archive' }

const STATUS: Record<string, { label: string; variant: BadgeVariant }> = {
  DRAFT: { label: 'Brouillon', variant: 'default' },
  PUBLISHED: { label: 'Publié', variant: 'success' },
  ARCHIVED: { label: 'Archivé', variant: 'warning' },
}

export default function FeeCatalogPanel({ canManage, onAssigned }: FeeCatalogPanelProps) {
  const [items, setItems] = useState<FeeType[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [students, setStudents] = useState<Student[]>([])
  const [studentId, setStudentId] = useState('')
  const [pending, setPending] = useState<PendingAction | null>(null)

  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState<Currency>('USD')

  const refresh = useCallback(async () => {
    try {
      setItems(await listFeeTypes())
    } catch (reason) {
      setError(describeFinanceError(reason, 'Catalogue indisponible.'))
    }
  }, [])

  useEffect(() => {
    let active = true
    listFeeTypes()
      .then((loaded) => { if (active) setItems(loaded) })
      .catch((reason: unknown) => {
        if (active) setError(describeFinanceError(reason, 'Catalogue indisponible.'))
      })
      .finally(() => { if (active) setLoading(false) })
    if (canManage) {
      listStudents()
        .then((loaded) => { if (active) setStudents(loaded) })
        .catch(() => undefined)
    }
    return () => { active = false }
  }, [canManage])

  const student = students.find((item) => item.id === studentId)
  const studentName = student ? `${student.firstName} ${student.lastName}` : ''

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true); setError(''); setNotice('')
    try {
      const created = await createFeeType({ name, category, amount, currency, description })
      setNotice(`Frais « ${created.name} » créé en brouillon. Publiez-le avant de l’attribuer.`)
      setName(''); setCategory(''); setDescription(''); setAmount('')
      await refresh()
    } catch (reason) {
      setError(describeFinanceError(reason, 'Le type de frais n’a pas pu être créé.'))
    } finally {
      setBusy(false)
    }
  }

  async function publish(id: string) {
    setBusy(true); setError(''); setNotice('')
    try {
      const updated = await updateFeeTypeStatus(id, 'PUBLISHED')
      setNotice(`Frais « ${updated.name} » publié.`)
      await refresh()
    } catch (reason) {
      setError(describeFinanceError(reason, 'Le frais n’a pas pu être publié.'))
    } finally {
      setBusy(false)
    }
  }

  async function confirmPending() {
    if (!pending) return
    const { id, kind } = pending
    setBusy(true); setError(''); setNotice('')
    try {
      if (kind === 'archive') {
        const updated = await updateFeeTypeStatus(id, 'ARCHIVED')
        setNotice(`Frais « ${updated.name} » archivé.`)
        await refresh()
      } else {
        const assignment = await assignFeeType(id, studentId)
        setNotice(`Frais attribué à ${studentName} : ${formatMoney(assignment.amount, assignment.currency)}.`)
        onAssigned?.(studentId)
      }
    } catch (reason) {
      setError(describeFinanceError(
        reason,
        kind === 'archive' ? 'Le frais n’a pas pu être archivé.' : 'Le frais n’a pas pu être attribué.',
      ))
    } finally {
      setPending(null)
      setBusy(false)
    }
  }

  return (
    <section className="finance-card" aria-labelledby="fee-catalog-title">
      <div className="finance-card__heading">
        <h2 id="fee-catalog-title">Catalogue de frais</h2>
        <p className="finance-card__hint">
          {canManage
            ? 'Un frais créé en brouillon doit être publié avant d’être attribué à un élève.'
            : 'Consultation seule : la gestion du catalogue est réservée à l’administration et à la direction.'}
        </p>
      </div>

      {notice ? <p className="finance-notice" role="status">{notice}</p> : null}
      {error ? <p className="finance-error" role="alert">{error}</p> : null}

      {canManage ? (
        <form className="finance-form" aria-label="Créer un type de frais" onSubmit={submit}>
          <label className="finance-field">Nom
            <input required maxLength={120} value={name} onChange={(event) => setName(event.target.value)} />
          </label>
          <label className="finance-field">Catégorie
            <input required maxLength={80} value={category} onChange={(event) => setCategory(event.target.value)} />
          </label>
          <label className="finance-field">Montant
            <input required type="number" min="0.01" step="0.01" value={amount} onChange={(event) => setAmount(event.target.value)} />
          </label>
          <label className="finance-field">Devise
            <select value={currency} onChange={(event) => setCurrency(event.target.value as Currency)}>
              <option value="USD">USD</option>
              <option value="CDF">CDF</option>
            </select>
          </label>
          <label className="finance-field finance-field--wide">Description (facultatif)
            <input maxLength={500} value={description} onChange={(event) => setDescription(event.target.value)} />
          </label>
          <button type="submit" className="finance-button" disabled={busy}>Créer en brouillon</button>
        </form>
      ) : null}

      {canManage && items.length > 0 ? (
        <label className="finance-field finance-field--narrow">Élève concerné par l’attribution
          <select value={studentId} onChange={(event) => { setStudentId(event.target.value); setPending(null) }}>
            <option value="">Choisir un élève</option>
            {students.map((item) => (
              <option key={item.id} value={item.id}>{item.firstName} {item.lastName}</option>
            ))}
          </select>
        </label>
      ) : null}

      {loading ? (
        <p role="status" aria-busy="true">Chargement du catalogue…</p>
      ) : items.length === 0 ? (
        <p className="finance-empty" role="status">Aucun type de frais configuré.</p>
      ) : (
        <div className="finance-table-scroll">
          <table className="finance-table">
            <thead>
              <tr>
                <th scope="col">Frais</th>
                <th scope="col">Catégorie</th>
                <th scope="col" className="finance-table__amount">Montant</th>
                <th scope="col">Statut</th>
                {canManage ? <th scope="col">Actions</th> : null}
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const state = STATUS[item.status] ?? { label: item.status, variant: 'default' as BadgeVariant }
                const active = pending?.id === item.id ? pending : null
                return (
                  <tr key={item.id}>
                    <td>{item.name}</td>
                    <td>{item.category}</td>
                    <td className="finance-table__amount">{formatMoney(item.amount, item.currency)}</td>
                    <td><Badge variant={state.variant}>{state.label}</Badge></td>
                    {canManage ? (
                      <td className="finance-table__actions">
                        {active ? (
                          <span className="finance-confirm">
                            <span>{active.kind === 'assign' ? `Attribuer à ${studentName} ?` : 'Archiver ce frais ?'}</span>
                            <button type="button" className="finance-button finance-button--small" disabled={busy} onClick={() => void confirmPending()}>Confirmer</button>
                            <button type="button" className="finance-button finance-button--secondary finance-button--small" disabled={busy} onClick={() => setPending(null)}>Annuler</button>
                          </span>
                        ) : item.status === 'DRAFT' ? (
                          <button type="button" className="finance-button finance-button--secondary finance-button--small" disabled={busy} onClick={() => void publish(item.id)}>Publier</button>
                        ) : item.status === 'PUBLISHED' ? (
                          <>
                            <button type="button" className="finance-button finance-button--secondary finance-button--small" disabled={busy || !studentId} onClick={() => setPending({ id: item.id, kind: 'assign' })}>Attribuer</button>
                            <button type="button" className="finance-button finance-button--secondary finance-button--small" disabled={busy} onClick={() => setPending({ id: item.id, kind: 'archive' })}>Archiver</button>
                          </>
                        ) : null}
                      </td>
                    ) : null}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}