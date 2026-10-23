import { useEffect, useState } from 'react'

import { ApiError } from '../../shared/api/client'
import { assignFeeType, createFeeType, listFeeTypes, updateFeeTypeStatus, type FeeType } from './finance.service'
import { listStudents } from '../students/services/student.service'
import type { Student } from '../students/types/student.types'

export default function FeeCatalogPanel() {
  const [items, setItems] = useState<FeeType[]>([])
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState<'USD' | 'CDF'>('USD')
  const [error, setError] = useState('')
  const [students, setStudents] = useState<Student[]>([])
  const [studentId, setStudentId] = useState('')

  async function refresh() {
    try { setItems(await listFeeTypes()) } catch (reason) {
      setError(reason instanceof ApiError && reason.status === 403 ? 'Votre rôle ne permet pas de consulter le catalogue.' : 'Catalogue indisponible.')
    }
  }

  useEffect(() => {
    let mounted = true
    listFeeTypes().then((loaded) => {
      if (mounted) setItems(loaded)
    }).catch((reason: unknown) => {
      if (!mounted) return
      setError(reason instanceof ApiError && reason.status === 403 ? 'Votre rôle ne permet pas de consulter le catalogue.' : 'Catalogue indisponible.')
    })
    listStudents().then((loaded) => { if (mounted) setStudents(loaded) }).catch(() => undefined)
    return () => { mounted = false }
  }, [])

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('')
    try {
      await createFeeType({ name, category, amount, currency })
      setName(''); setCategory(''); setAmount(''); await refresh()
    } catch { setError('Le type de frais n’a pas pu être créé.') }
  }

  async function changeStatus(id: string, status: 'PUBLISHED' | 'ARCHIVED') {
    try { await updateFeeTypeStatus(id, status); await refresh() } catch { setError('Le statut du type de frais n’a pas pu être modifié.') }
  }

  async function assign(id: string) {
    if (!studentId) return
    try { await assignFeeType(id, studentId); setError(''); }
    catch { setError('Le tarif n’a pas pu être attribué à cet élève.') }
  }

  return <section aria-labelledby="fee-catalog-title">
    <h2 id="fee-catalog-title">Catalogue de frais</h2>
    {error ? <p role="alert">{error}</p> : null}
    <form onSubmit={submit}>
      <input required aria-label="Nom du frais" value={name} onChange={(event) => setName(event.target.value)} placeholder="Nom" />
      <input required aria-label="Catégorie du frais" value={category} onChange={(event) => setCategory(event.target.value)} placeholder="Catégorie" />
      <input required aria-label="Montant du frais" type="number" min="0.01" step="0.01" value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="Montant" />
      <select aria-label="Devise du frais" value={currency} onChange={(event) => setCurrency(event.target.value as 'USD' | 'CDF')}><option>USD</option><option>CDF</option></select>
      <button type="submit">Créer en brouillon</button>
    </form>
    {items.length === 0 ? <p role="status">Aucun type de frais configuré.</p> : <><label>Élève à facturer<select value={studentId} onChange={(event) => setStudentId(event.target.value)}><option value="">Choisir un élève</option>{students.map((student) => <option key={student.id} value={student.id}>{student.firstName} {student.lastName}</option>)}</select></label><ul>{items.map((item) => <li key={item.id}>{item.name} · {item.amount} {item.currency} · {item.status}{item.status === 'DRAFT' ? <button type="button" onClick={() => void changeStatus(item.id, 'PUBLISHED')}>Publier</button> : null}{item.status === 'PUBLISHED' ? <><button type="button" onClick={() => void assign(item.id)} disabled={!studentId}>Attribuer</button><button type="button" onClick={() => void changeStatus(item.id, 'ARCHIVED')}>Archiver</button></> : null}</li>)}</ul></>}
  </section>
}
