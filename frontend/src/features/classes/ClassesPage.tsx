import { useCallback, useEffect, useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '../../shared/api/client'
import { listSubjects, type Subject } from '../academic-catalogues/academic-catalogue.service'
import { assignSubjectToClass, listAcademicClasses, type AcademicClass, type ClassSubject } from './classes.service'
import './ClassesPage.css'

const assignmentSchema = z.object({
  classId: z.string().min(1, 'Sélectionnez une classe.'),
  subjectId: z.string().min(1, 'Sélectionnez une matière.'),
  coefficient: z.string()
    .min(1, 'Le coefficient est obligatoire.')
    .refine((value) => value.trim() !== '' && Number.isFinite(Number(value)), 'Saisissez un coefficient numérique valide.')
    .transform(Number)
    .pipe(z.number().finite('Le coefficient doit être un nombre fini.').positive('Le coefficient doit être strictement supérieur à zéro.')),
})

type AssignmentFormValues = z.input<typeof assignmentSchema>

function errorText(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) return 'Votre session a expiré. Reconnectez-vous.'
    if (error.status === 403) return 'Votre compte ne peut pas gérer les classes de cet établissement.'
    if (error.status === 404) {
      return error.message || 'La classe ou la matière demandée n’existe pas.'
    }
    if (error.status === 409) {
      return error.message || 'Cette matière est déjà assignée à cette classe.'
    }
    if (error.status === 400) {
      return error.message || 'La requête est invalide.'
    }
    if (error.status === 0) return 'Le serveur API est inaccessible.'
  }
  return 'Une erreur est survenue lors de l’opération.'
}

export default function ClassesPage() {
  const [classes, setClasses] = useState<AcademicClass[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [recentAssignments, setRecentAssignments] = useState<Array<ClassSubject & { className: string; subjectName: string }>>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [loadError, setLoadError] = useState(false)
  const [notice, setNotice] = useState('')
  const { register, handleSubmit, setValue, reset, getValues, watch, formState: { errors, isSubmitting } } = useForm<AssignmentFormValues, unknown, z.output<typeof assignmentSchema>>({
    resolver: zodResolver(assignmentSchema),
    defaultValues: { classId: '', subjectId: '', coefficient: '1' },
  })
  const selectedClassId = watch('classId')
  const selectedSubjectId = watch('subjectId')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [loadedClasses, loadedSubjects] = await Promise.all([
        listAcademicClasses(),
        listSubjects(),
      ])
      setClasses(loadedClasses)
      setSubjects(loadedSubjects)
      setLoadError(false)
      const firstClassId = loadedClasses[0]?.id || ''
      const firstSubject = loadedSubjects[0]
      const currentValues = getValues()
      reset({
        classId: currentValues.classId || firstClassId,
        subjectId: currentValues.subjectId || firstSubject?.id || '',
        coefficient: currentValues.coefficient === '1' && firstSubject?.coefficient ? String(firstSubject.coefficient) : currentValues.coefficient,
      })
    } catch (reason) {
      setLoadError(true)
      setError(errorText(reason))
    } finally {
      setLoading(false)
    }
  }, [getValues, reset])

  useEffect(() => {
    void Promise.resolve().then(load)
  }, [load])

  const handleAssignSubject = async ({ classId, subjectId, coefficient }: z.output<typeof assignmentSchema>) => {
    setError('')
    setNotice('')

    try {
      const result = await assignSubjectToClass(classId, {
        subject_id: subjectId,
        coefficient,
      })

      const targetClass = classes.find((c) => c.id === classId)
      const targetSubject = subjects.find((s) => s.id === subjectId)
      const className = targetClass?.name || classId
      const subjectName = targetSubject?.name || subjectId

      setRecentAssignments((prev) => [
        { ...result, className, subjectName },
        ...prev,
      ])
      setNotice(`Matière "${subjectName}" assignée avec succès à la classe "${className}".`)
    } catch (reason) {
      setError(errorText(reason))
    }
  }

  return (
    <main className="classes-page">
      <header className="classes-page__header">
        <p>Établissement</p>
        <h1>Classes</h1>
        <p>Consultez les classes configurées pour votre établissement et associez leurs matières.</p>
      </header>

      {loading ? <p role="status" aria-busy="true">Chargement des données…</p> : null}
      {error ? (
        <div role="alert">
          <p>{error}</p>
          <button type="button" onClick={() => void load()}>Réessayer</button>
        </div>
      ) : null}
      {notice ? <p role="status">{notice}</p> : null}

      <section className="classes-page__section" aria-labelledby="classes-list-title">
        <h2 id="classes-list-title">Liste des classes</h2>
        {!loading && !loadError && classes.length === 0 ? (
          <p>Aucune classe n'est disponible.</p>
        ) : null}
        {!loading && classes.length > 0 ? (
          <div className="classes-page__table-scroll">
          <table className="classes-page__table">
            <thead>
              <tr><th scope="col">Nom</th><th scope="col">État</th></tr>
            </thead>
            <tbody>
              {classes.map((academicClass) => (
                <tr key={academicClass.id}>
                  <td>{academicClass.name}</td>
                  <td>{academicClass.active ? 'Active' : 'Inactive'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        ) : null}
      </section>

      <section className="classes-page__section" aria-labelledby="assign-subject-title">
        <h2 id="assign-subject-title">Assigner une matière à une classe</h2>
        <form className="classes-page__form" onSubmit={handleSubmit(handleAssignSubject)} noValidate>
          <div className="classes-page__field">
          <label htmlFor="assignment-class">Classe</label>
          <select id="assignment-class" aria-invalid={Boolean(errors.classId)} aria-describedby={errors.classId ? 'assignment-class-error' : undefined}
            {...register('classId')} disabled={isSubmitting || classes.length === 0}>
              <option value="">Sélectionnez une classe</option>
              {classes.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
          </select>
          {errors.classId ? <p id="assignment-class-error">{errors.classId.message}</p> : null}
          </div>

          <div className="classes-page__field">
          <label htmlFor="assignment-subject">Matière</label>
          <select id="assignment-subject" aria-invalid={Boolean(errors.subjectId)} aria-describedby={errors.subjectId ? 'assignment-subject-error' : undefined}
            {...register('subjectId', { onChange: (e) => {
              const subj = subjects.find((s) => s.id === e.target.value)
              if (subj?.coefficient) setValue('coefficient', String(subj.coefficient), { shouldValidate: true })
            } })} disabled={isSubmitting || subjects.length === 0}>
              <option value="">Sélectionnez une matière</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
              ))}
          </select>
          {errors.subjectId ? <p id="assignment-subject-error">{errors.subjectId.message}</p> : null}
          </div>

          <div className="classes-page__field">
          <label htmlFor="assignment-coefficient">Coefficient</label>
          <input id="assignment-coefficient" type="number" step="any" aria-invalid={Boolean(errors.coefficient)}
            aria-describedby={errors.coefficient ? 'assignment-coefficient-error' : undefined}
            {...register('coefficient')} disabled={isSubmitting} />
          {errors.coefficient ? <p id="assignment-coefficient-error">{errors.coefficient.message}</p> : null}
          </div>

          <button className="classes-page__submit"
            type="submit"
            disabled={isSubmitting || !selectedClassId || !selectedSubjectId || classes.length === 0 || subjects.length === 0}
          >
            {isSubmitting ? 'Assignation en cours…' : 'Assigner la matière'}
          </button>
        </form>

        {recentAssignments.length > 0 ? (
          <div className="classes-page__recent">
            <h3>Assignations effectuées durant la session</h3>
            <ul>
              {recentAssignments.map((a) => (
                <li key={a.id}>
                  {a.subjectName} assignée à {a.className} (coeff. {a.coefficient})
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </section>
    </main>
  )
}
