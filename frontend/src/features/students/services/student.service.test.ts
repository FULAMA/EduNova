import { afterEach, describe, expect, it, vi } from 'vitest'

import { clearSession, saveSession } from '../../auth/services/auth.storage'
import { addStudentSubjectResult, createStudentAcademicRecord, getStudent, getStudentAcademicRecord, getStudentDeliberation, listEligibleStudentPeriods, listEligibleStudentSubjects, listStudentAcademicPeriods, listStudents, validateStudentDeliberation } from './student.service'

describe('student service', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    clearSession()
  })

  it('calls the tenant-scoped endpoint as an authenticated request', async () => {
    saveSession({
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      email: 'admin@example.test',
      tenantId: 'tenant-1',
    })
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify([
          {
            id: 'student-1',
            first_name: 'Ada',
            last_name: 'Lovelace',
            email: 'ada@example.test',
            active: true,
          },
        ]),
        { status: 200 },
      ),
    )

    await expect(listStudents()).resolves.toEqual([
      {
        id: 'student-1',
        firstName: 'Ada',
        lastName: 'Lovelace',
        email: 'ada@example.test',
        status: 'active',
      },
    ])

    expect(fetchMock.mock.calls[0][0]).toContain('/students')
    expect(fetchMock.mock.calls[0][1]).toMatchObject({
      headers: expect.any(Headers),
    })
    expect(
      new Headers(fetchMock.mock.calls[0][1]?.headers).get('Authorization'),
    ).toBe('Bearer access-token')
  })

  it('requests a student detail with auth and maps the API contract', async () => {
    saveSession({ accessToken: 'access-token', refreshToken: 'refresh-token', email: 'admin@example.test', tenantId: 'tenant-1' })
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({
      id: 'student-1', first_name: 'Ada', last_name: 'Lovelace', email: null, active: false,
    }), { status: 200 }))

    await expect(getStudent('student-1')).resolves.toEqual({
      id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'inactive',
    })
    expect(fetchMock.mock.calls[0][0]).toContain('/students/student-1')
    expect(new Headers(fetchMock.mock.calls[0][1]?.headers).get('Authorization')).toBe('Bearer access-token')
  })

  it('loads academic periods and the existing record contract with auth', async () => {
    saveSession({ accessToken: 'access-token', refreshToken: 'refresh-token', email: 'admin@example.test', tenantId: 'tenant-1' })
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify([{ id: 'period-1', name: 'Trimestre 1' }]), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        student_id: 'student-1', academic_period_id: 'period-1', general_average: 14.5,
        failed_subjects: 1, credits_obtained: 12, total_credits: 24,
        subject_results: [{ subject_id: 'subject-1', average: 14.5, coefficient: 2 }],
      }), { status: 200 }))

    await expect(listStudentAcademicPeriods('student-1')).resolves.toEqual([{ id: 'period-1', name: 'Trimestre 1' }])
    await expect(getStudentAcademicRecord('student-1', 'period-1')).resolves.toMatchObject({
      general_average: 14.5, subject_results: [{ average: 14.5, coefficient: 2 }],
    })
    expect(fetchMock.mock.calls[0][0]).toContain('/academic-records/students/student-1/periods')
    expect(fetchMock.mock.calls[1][0]).toContain('/academic-records/student-1/period-1')
    expect(new Headers(fetchMock.mock.calls[0][1]?.headers).get('Authorization')).toBe('Bearer access-token')
    expect(new Headers(fetchMock.mock.calls[1][1]?.headers).get('Authorization')).toBe('Bearer access-token')
  })

  it('keeps forbidden responses available to the page', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Acces interdit.' }), {
        status: 403,
      }),
    )

    await expect(listStudents()).rejects.toMatchObject({
      status: 403,
    })
  })

  it('loads a server-calculated deliberation with authentication', async () => {
    saveSession({ accessToken: 'access-token', refreshToken: 'refresh-token', email: 'admin@example.test', tenantId: 'tenant-1' })
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({
      student_id: 'student-1', academic_period_id: 'period-1', record_version: 3,
      average: 12, failed_subjects: 0, decision: 'ADMITTED',
    }), { status: 200 }))

    await expect(getStudentDeliberation('student-1', 'period-1')).resolves.toMatchObject({
      decision: 'ADMITTED', record_version: 3,
    })
    expect(fetchMock.mock.calls[0][0]).toContain('/academic-records/student-1/period-1/deliberation')
    expect(new Headers(fetchMock.mock.calls[0][1]?.headers).get('Authorization')).toBe('Bearer access-token')
  })

  it('validates a deliberation with its expected version and authentication', async () => {
    saveSession({ accessToken: 'access-token', refreshToken: 'refresh-token', email: 'admin@example.test', tenantId: 'tenant-1' })
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({
      student_id: 'student-1', academic_period_id: 'period-1', record_version: 3,
      average: 12, failed_subjects: 0, decision: 'ADMITTED',
      deliberation_id: 'deliberation-1', deliberation_status: 'VALIDATED', deliberation_version: 2,
    }), { status: 200 }))

    await expect(validateStudentDeliberation('deliberation-1', 1)).resolves.toMatchObject({
      deliberation_status: 'VALIDATED', deliberation_version: 2,
    })
    expect(fetchMock.mock.calls[0][0]).toContain('/academic-records/deliberations/deliberation-1/validate')
    expect(JSON.parse(String(fetchMock.mock.calls[0][1]?.body))).toEqual({ expected_version: 1 })
    expect(new Headers(fetchMock.mock.calls[0][1]?.headers).get('Authorization')).toBe('Bearer access-token')
  })

  it('loads eligible periods and subjects and never sends a coefficient from the client', async () => {
    saveSession({ accessToken: 'access-token', refreshToken: 'refresh-token', email: 'admin@example.test', tenantId: 'tenant-1' })
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify([{ id: 'period-1', name: 'Trimestre 1', academic_year_id: 'year-1', has_record: false }]), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify([{ id: 'subject-1', name: 'Maths', coefficient: 3 }]), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({}), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({}), { status: 201 }))

    await expect(listEligibleStudentPeriods('student-1')).resolves.toMatchObject([{ id: 'period-1', has_record: false }])
    await expect(listEligibleStudentSubjects('student-1', 'period-1')).resolves.toEqual([{ id: 'subject-1', name: 'Maths', coefficient: 3 }])
    await createStudentAcademicRecord('student-1', 'period-1', 24)
    await addStudentSubjectResult('student-1', 'period-1', 'subject-1', 15)

    expect(fetchMock.mock.calls[0][0]).toContain('/available-periods')
    expect(fetchMock.mock.calls[1][0]).toContain('/periods/period-1/subjects')
    expect(JSON.parse(String(fetchMock.mock.calls[2][1]?.body))).toEqual({ student_id: 'student-1', academic_period_id: 'period-1', total_credits: 24 })
    expect(JSON.parse(String(fetchMock.mock.calls[3][1]?.body))).toEqual({ subject_id: 'subject-1', average: 15 })
  })
})
