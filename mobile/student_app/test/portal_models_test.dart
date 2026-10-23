import 'package:flutter_test/flutter_test.dart';

import 'package:edunova_student/src/models/auth_models.dart';
import 'package:edunova_student/src/models/portal_models.dart';

void main() {
  test('resolves the role from the authenticated server response', () {
    final user = AuthenticatedUser.fromJson({
      'id': 'user-1',
      'email': 'student@example.test',
      'role': 'STUDENT',
      'is_active': true,
      'two_factor_enabled': false,
    });

    expect(user.role, 'STUDENT');
  });

  test(
    'decodes the student portal contract without client-side calculations',
    () {
      final profile = StudentPortalProfile.fromJson({
        'student': {
          'id': 'student-1',
          'first_name': 'Ada',
          'last_name': 'Lovelace',
          'email': 'ada@example.test',
          'active': true,
        },
        'assignment': {
          'id': 'assignment-1',
          'academic_year_id': 'year-1',
          'academic_class_id': 'class-1',
          'status': 'ACTIVE',
          'created_at': '2026-10-01T00:00:00Z',
        },
        'academic_year': {
          'id': 'year-1',
          'label': '2026-2027',
          'start_date': '2026-09-01',
          'end_date': '2027-06-30',
          'status': 'ACTIVE',
        },
      });

      expect(profile.firstName, 'Ada');
      expect(profile.assignment?.status, 'ACTIVE');
      expect(profile.academicYear?.label, '2026-2027');
    },
  );

  test('keeps server-provided academic values unchanged', () {
    final record = AcademicRecord.fromJson({
      'student_id': 'student-1',
      'academic_period_id': 'period-1',
      'general_average': 13.2,
      'failed_subjects': 1,
      'credits_obtained': 20,
      'total_credits': 30,
      'subject_results': [
        {
          'subject_id': 'math',
          'subject_name': 'Mathematiques',
          'average': 12.5,
          'coefficient': 2,
        },
      ],
      'status': 'VALIDATED',
      'version': 1,
    });

    expect(record.average, 13.2);
    expect(record.subjects.single.average, 12.5);
    expect(record.status, 'VALIDATED');
  });
}
