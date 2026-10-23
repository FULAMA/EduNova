import { useCallback, useEffect, useState, type FormEvent } from 'react'

import { ApiError } from '../../shared/api/client'
import { createAcademicPeriod, createSubject, listAcademicPeriods, listSubjects, updateSubject, type AcademicPeriod, type Subject } from './academic-catalogue.service'
import { listAcademicYears, type AcademicYear } from '../enrollments/enrollment.service'
import './AcademicCataloguesPage.css'

function errorText(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) return 'Votre session a expiré. Reconnectez-vous.'
    if (error.status === 403) return 'Votre compte ne peut pas gérer les catalogues de cet établissement.'
    if (error.status === 404) return 'La matière demandée n’existe plus. Actualisez le catalogue.'
    if (error.status === 409) return error.message || 'Cette période existe déjà pour cette année scolaire.'
    if (error.status === 0) return 'Le serveur API est inaccessible.'
  }
  return 'Une erreur est survenue. Vérifiez les informations puis réessayez.'
}

export default function AcademicCataloguesPage() {
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [periods, setPeriods] = useState<AcademicPeriod[]>([])
  const [years, setYears] = useState<AcademicYear[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [editing, setEditing] = useState<string | null>(null)
  const [name, setName] = useState('')
  const [code, setCode] = useState('')
  const [coefficient, setCoefficient] = useState('1')
  const [periodYearId, setPeriodYearId] = useState('')
  const [periodName, setPeriodName] = useState('')
  const [periodStart, setPeriodStart] = useState('')
  const [periodEnd, setPeriodEnd] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [subjectRows, periodRows, yearRows] = await Promise.all([listSubjects(search), listAcademicPeriods(), listAcademicYears()])
      setSubjects(subjectRows)
      setPeriods(periodRows)
      setYears(yearRows)
      setPeriodYearId((current) => current || yearRows.find((year) => year.status !== 'CLOSED')?.id || '')
      setLoadError(false)
    } catch (reason) { setLoadError(true); setError(errorText(reason)) } finally { setLoading(false) }
  }, [search])

  useEffect(() => { void Promise.resolve().then(load) }, [load])

  const resetForm = () => { setEditing(null); setName(''); setCode(''); setCoefficient('1') }
  const edit = (subject: Subject) => {
    setEditing(subject.id); setName(subject.name); setCode(subject.code); setCoefficient(String(subject.coefficient)); setNotice('')
  }
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(''); setNotice('')
    const data = { name: name.trim(), code: code.trim(), coefficient: Number(coefficient) }
    try {
      if (editing) await updateSubject(editing, { name: data.name, code: data.code })
      else await createSubject(data)
      resetForm(); setNotice(editing ? 'Matière modifiée.' : 'Matière créée.')
      await load()
    } catch (reason) { setError(errorText(reason)) }
  }
  const submitPeriod = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(''); setNotice('')
    try {
      await createAcademicPeriod({ academic_year_id: periodYearId, name: periodName.trim(), start_date: periodStart, end_date: periodEnd })
      setPeriodName(''); setPeriodStart(''); setPeriodEnd('')
      setNotice('Période académique créée et rattachée à son année scolaire.')
      await load()
    } catch (reason) { setError(errorText(reason)) }
  }

  return <main className="catalogues-page">
    <header><p className="catalogues-page__eyebrow">Établissement</p><h1>Configuration scolaire</h1><p>Gérez le catalogue des matières et consultez les périodes enregistrées.</p></header>
    <section className="catalogues-card" aria-labelledby="subjects-title">
      <div className="catalogues-card__heading"><div><h2 id="subjects-title">Matières</h2><p>Les modifications sont enregistrées dans le catalogue de votre établissement.</p></div></div>
      <label className="catalogues-search">Rechercher une matière<input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Nom de matière" /></label>
      {error && <div className="catalogues-message catalogues-message--error" role="alert"><p>{error}</p><button type="button" onClick={() => void load()}>Réessayer</button></div>}
      {notice && <p className="catalogues-message" role="status">{notice}</p>}
      {loading ? <p role="status" aria-busy="true">Chargement du catalogue…</p> : subjects.length ? <div className="catalogues-table-scroll"><table><thead><tr><th>Nom</th><th>Code</th><th>Coefficient</th><th>État</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{subjects.map((subject) => <tr key={subject.id}><td>{subject.name}</td><td>{subject.code}</td><td>{subject.coefficient}</td><td>{subject.active ? 'Active' : 'Inactive'}</td><td><button type="button" onClick={() => edit(subject)}>Modifier</button></td></tr>)}</tbody></table></div> : !loadError ? <p className="catalogues-empty">{search.trim() ? 'Aucune matière ne correspond à la recherche.' : 'Aucune matière n’est enregistrée dans le catalogue.'}</p> : null}
      <form className="catalogues-form" onSubmit={(event) => void submit(event)}>
        <h3>{editing ? 'Modifier une matière' : 'Ajouter une matière'}</h3>
        <label>Nom<input required minLength={1} value={name} onChange={(event) => setName(event.target.value)} /></label>
        <label>Code<input required minLength={1} value={code} onChange={(event) => setCode(event.target.value)} /></label>
        <label>Coefficient<input required type="number" min="0.01" step="any" value={coefficient} readOnly={Boolean(editing)} onChange={(event) => setCoefficient(event.target.value)} aria-describedby={editing ? 'coefficient-help' : undefined} /></label>
        {editing ? <span id="coefficient-help" className="catalogues-help">Le coefficient existant est conservé lors de la modification.</span> : null}
        <div className="catalogues-form__actions"><button type="submit">{editing ? 'Enregistrer' : 'Créer la matière'}</button>{editing && <button type="button" className="catalogues-secondary" onClick={resetForm}>Annuler</button>}</div>
      </form>
    </section>
    <section className="catalogues-card" aria-labelledby="periods-title">
      <div className="catalogues-card__heading"><div><h2 id="periods-title">Périodes académiques</h2><p>Les périodes nouvelles sont rattachées explicitement à une année scolaire. Les données historiques sans rattachement restent inchangées.</p></div></div>
      {loading ? <p role="status" aria-busy="true">Chargement des périodes…</p> : periods.length ? <div className="catalogues-table-scroll"><table><thead><tr><th>Libellé</th><th>Année scolaire</th><th>Début</th><th>Fin</th></tr></thead><tbody>{periods.map((period) => <tr key={period.id}><td>{period.name}</td><td>{years.find((year) => year.id === period.academic_year_id)?.label ?? 'Historique non rattaché'}</td><td>{period.start_date}</td><td>{period.end_date}</td></tr>)}</tbody></table></div> : !loadError ? <p className="catalogues-empty">Aucune période n’est enregistrée.</p> : null}
      <form className="catalogues-form" onSubmit={(event) => void submitPeriod(event)}>
        <h3>Créer une période</h3>
        <label>Année scolaire<select required value={periodYearId} onChange={(event) => setPeriodYearId(event.target.value)}><option value="">Sélectionner une année</option>{years.filter((year) => year.status !== 'CLOSED').map((year) => <option key={year.id} value={year.id}>{year.label}</option>)}</select></label>
        <label>Libellé<input required value={periodName} onChange={(event) => setPeriodName(event.target.value)} placeholder="Trimestre 1" /></label>
        <label>Date de début<input required type="date" value={periodStart} onChange={(event) => setPeriodStart(event.target.value)} /></label>
        <label>Date de fin<input required type="date" value={periodEnd} onChange={(event) => setPeriodEnd(event.target.value)} /></label>
        <div className="catalogues-form__actions"><button type="submit" disabled={!periodYearId}>Créer la période</button></div>
      </form>
    </section>
  </main>
}
