import { useCallback, useEffect, useState, type FormEvent } from 'react'

import { ApiError } from '../../shared/api/client'
import { createAcademicCalendar, createAcademicPeriod, createSubject, listAcademicCalendars, listAcademicPeriods, listSubjects, updateSubject, type AcademicCalendar, type AcademicPeriod, type Subject } from './academic-catalogue.service'
import { listAcademicYears, type AcademicYear } from '../enrollments/enrollment.service'
import './AcademicCataloguesPage.css'

function errorText(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) return 'Votre session a expiré. Reconnectez-vous.'
    if (error.status === 403) return 'Votre compte ne peut pas gérer les catalogues de cet établissement.'
    if (error.status === 404) return 'La matière demandée n’existe plus. Actualisez le catalogue.'
    if (error.status === 400 || error.status === 409) return error.message || 'La demande ne peut pas être traitée.'
    if (error.status === 0) return 'Le serveur API est inaccessible.'
  }
  return 'Une erreur est survenue. Vérifiez les informations puis réessayez.'
}

export default function AcademicCataloguesPage() {
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [periods, setPeriods] = useState<AcademicPeriod[]>([])
  const [calendars, setCalendars] = useState<AcademicCalendar[]>([])
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
  const [periodCalendarId, setPeriodCalendarId] = useState('')
  const [calendarName, setCalendarName] = useState('')
  const [calendarDescription, setCalendarDescription] = useState('')
  const [periodName, setPeriodName] = useState('')
  const [periodStart, setPeriodStart] = useState('')
  const [periodEnd, setPeriodEnd] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [subjectRows, periodRows, yearRows, calendarRows] = await Promise.all([listSubjects(search), listAcademicPeriods(), listAcademicYears(), listAcademicCalendars()])
      setSubjects(subjectRows)
      setPeriods(periodRows)
      setYears(yearRows)
      setCalendars(calendarRows)
      setPeriodYearId((current) => current || yearRows.find((year) => year.status !== 'CLOSED')?.id || '')
      setPeriodCalendarId((current) => current || calendarRows.find((calendar) => calendar.is_active)?.id || '')
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
  const submitCalendar = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(''); setNotice('')
    try {
      await createAcademicCalendar({ name: calendarName.trim(), description: calendarDescription.trim() || null })
      setCalendarName(''); setCalendarDescription('')
      setNotice('Calendrier académique créé.')
      await load()
    } catch (reason) { setError(errorText(reason)) }
  }
  const submitPeriod = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(''); setNotice('')
    try {
      await createAcademicPeriod({ academic_year_id: periodYearId, academic_calendar_id: periodCalendarId, name: periodName.trim(), start_date: periodStart, end_date: periodEnd })
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
    <section className="catalogues-card" aria-labelledby="calendars-title">
      <div className="catalogues-card__heading"><div><h2 id="calendars-title">Calendriers académiques</h2><p>Créez des calendriers indépendants par cycle ou programme. Les périodes d’un même calendrier ne peuvent pas se chevaucher ; deux calendriers distincts peuvent suivre des dates différentes.</p></div></div>
      {loading ? <p role="status" aria-busy="true">Chargement des calendriers…</p> : calendars.length ? <div className="catalogues-table-scroll"><table><thead><tr><th>Nom</th><th>Description</th><th>État</th></tr></thead><tbody>{calendars.map((calendar) => <tr key={calendar.id}><td>{calendar.name}</td><td>{calendar.description || '—'}</td><td>{calendar.is_active ? 'Actif' : 'Inactif'}</td></tr>)}</tbody></table></div> : !loadError ? <p className="catalogues-empty">Aucun calendrier n’est enregistré.</p> : null}
      <form className="catalogues-form" onSubmit={(event) => void submitCalendar(event)}>
        <h3>Créer un calendrier</h3>
        <label>Nom du calendrier<input required minLength={1} maxLength={120} value={calendarName} onChange={(event) => setCalendarName(event.target.value)} placeholder="Cycle primaire" /></label>
        <label>Description (facultative)<input maxLength={500} value={calendarDescription} onChange={(event) => setCalendarDescription(event.target.value)} placeholder="Organisation des périodes du cycle" /></label>
        <div className="catalogues-form__actions"><button type="submit">Créer le calendrier</button></div>
      </form>
    </section>
    <section className="catalogues-card" aria-labelledby="periods-title">
      <div className="catalogues-card__heading"><div><h2 id="periods-title">Périodes académiques</h2><p>Les périodes nouvelles sont rattachées explicitement à une année scolaire. Les données historiques sans rattachement restent inchangées.</p></div></div>
      {loading ? <p role="status" aria-busy="true">Chargement des périodes…</p> : periods.length ? <div className="catalogues-table-scroll"><table><thead><tr><th>Libellé</th><th>Année scolaire</th><th>Calendrier</th><th>Début</th><th>Fin</th></tr></thead><tbody>{periods.map((period) => <tr key={period.id}><td>{period.name}</td><td>{years.find((year) => year.id === period.academic_year_id)?.label ?? 'Historique non rattaché'}</td><td>{calendars.find((calendar) => calendar.id === period.academic_calendar_id)?.name ?? 'Historique non classé'}</td><td>{period.start_date}</td><td>{period.end_date}</td></tr>)}</tbody></table></div> : !loadError ? <p className="catalogues-empty">Aucune période n’est enregistrée.</p> : null}
      <form className="catalogues-form" onSubmit={(event) => void submitPeriod(event)}>
        <h3>Créer une période</h3>
        <label>Année scolaire<select required value={periodYearId} onChange={(event) => setPeriodYearId(event.target.value)}><option value="">Sélectionner une année</option>{years.filter((year) => year.status !== 'CLOSED').map((year) => <option key={year.id} value={year.id}>{year.label}</option>)}</select></label>
        <label>Calendrier<select required value={periodCalendarId} onChange={(event) => setPeriodCalendarId(event.target.value)}><option value="">Sélectionner un calendrier</option>{calendars.filter((calendar) => calendar.is_active).map((calendar) => <option key={calendar.id} value={calendar.id}>{calendar.name}</option>)}</select></label>
        <label>Libellé<input required value={periodName} onChange={(event) => setPeriodName(event.target.value)} placeholder="Trimestre 1" /></label>
        <label>Date de début<input required type="date" value={periodStart} onChange={(event) => setPeriodStart(event.target.value)} /></label>
        <label>Date de fin<input required type="date" value={periodEnd} onChange={(event) => setPeriodEnd(event.target.value)} /></label>
        <div className="catalogues-form__actions"><button type="submit" disabled={!periodYearId || !periodCalendarId}>Créer la période</button></div>
      </form>
    </section>
  </main>
}
