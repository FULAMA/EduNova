import { beforeEach, describe, expect, it, vi } from 'vitest'

import { correctAttendance, getAttendanceStatistics, getStudentAcademicRisk, recordAttendance } from './attendance.service'

describe('attendance service', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('loads statistics through the authenticated API contract', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ total_sessions: 2, absences: 1, justified_absences: 0, unjustified_absences: 1, lates: 0, attendance_rate: 50 }), { status: 200 }),
    )

    await expect(getAttendanceStatistics('student-1', 'period/1')).resolves.toMatchObject({
      attendance_rate: 50,
    })

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/attendance/students/student-1/statistics?academic_period_id=period%2F1'),
      expect.objectContaining({ headers: expect.any(Headers) }),
    )
  })

  it('sends only the attendance input to the authenticated recording endpoint', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ id: 'attendance-1' }), { status: 201 }),
    )

    await recordAttendance({
      student_id: 'student-1', academic_class_id: 'class-1', academic_year_id: 'year-1',
      academic_period_id: 'period-1', attendance_date: '2026-10-19', status: 'ABSENT',
    })

    expect(JSON.parse(String(fetchMock.mock.calls[0][1]?.body))).toEqual({
      student_id: 'student-1', academic_class_id: 'class-1', academic_year_id: 'year-1',
      academic_period_id: 'period-1', attendance_date: '2026-10-19', status: 'ABSENT',
    })
  })

  it('loads the server-calculated academic risk with authentication', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ level: 'MEDIUM', score: 60, reasons: ['Présence insuffisante'] }), { status: 200 }),
    )

    await expect(getStudentAcademicRisk('student/1', 'period/1')).resolves.toEqual({
      level: 'MEDIUM', score: 60, reasons: ['Présence insuffisante'],
    })

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/academic-risk/students/student%2F1/periods/period%2F1'),
      expect.objectContaining({ headers: expect.any(Headers) }),
    )
  })

  it('sends the expected version and justification when correcting a record', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ id: 'attendance-1', version: 2 }), { status: 200 }),
    )

    await correctAttendance('attendance/1', 'ABSENT', true, 1)

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/attendance/attendance%2F1'),
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify({ status: 'ABSENT', justified: true, expected_version: 1 }),
      }),
    )
  })
})
