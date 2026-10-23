class StudentPortalProfile {
  const StudentPortalProfile({
    required this.firstName,
    required this.lastName,
    this.email,
    this.assignment,
    this.academicYear,
  });

  final String firstName;
  final String lastName;
  final String? email;
  final Assignment? assignment;
  final AcademicYear? academicYear;

  factory StudentPortalProfile.fromJson(Map<String, dynamic> json) {
    final student = json['student'] as Map<String, dynamic>;
    return StudentPortalProfile(
      firstName: student['first_name'] as String,
      lastName: student['last_name'] as String,
      email: student['email'] as String?,
      assignment: json['assignment'] == null
          ? null
          : Assignment.fromJson(json['assignment'] as Map<String, dynamic>),
      academicYear: json['academic_year'] == null
          ? null
          : AcademicYear.fromJson(
              json['academic_year'] as Map<String, dynamic>,
            ),
    );
  }
}

class Assignment {
  const Assignment({required this.classId, required this.status});

  final String classId;
  final String status;

  factory Assignment.fromJson(Map<String, dynamic> json) => Assignment(
    classId: json['academic_class_id'] as String,
    status: json['status'] as String,
  );
}

class AcademicYear {
  const AcademicYear({required this.label, required this.status});

  final String label;
  final String status;

  factory AcademicYear.fromJson(Map<String, dynamic> json) => AcademicYear(
    label: json['label'] as String,
    status: json['status'] as String,
  );
}

class AcademicPeriod {
  const AcademicPeriod({required this.id, required this.name});

  final String id;
  final String? name;

  factory AcademicPeriod.fromJson(Map<String, dynamic> json) =>
      AcademicPeriod(id: json['id'] as String, name: json['name'] as String?);
}

class AcademicRecord {
  const AcademicRecord({
    required this.average,
    required this.failedSubjects,
    required this.status,
    required this.subjects,
  });

  final num average;
  final int failedSubjects;
  final String status;
  final List<SubjectResult> subjects;

  factory AcademicRecord.fromJson(Map<String, dynamic> json) => AcademicRecord(
    average: json['general_average'] as num,
    failedSubjects: json['failed_subjects'] as int,
    status: json['status'] as String,
    subjects: (json['subject_results'] as List<dynamic>)
        .map((item) => SubjectResult.fromJson(item as Map<String, dynamic>))
        .toList(growable: false),
  );
}

class SubjectResult {
  const SubjectResult({required this.name, required this.average});

  final String? name;
  final num average;

  factory SubjectResult.fromJson(Map<String, dynamic> json) => SubjectResult(
    name: json['subject_name'] as String?,
    average: json['average'] as num,
  );
}

class AttendanceSummary {
  const AttendanceSummary({
    required this.rate,
    required this.absences,
    required this.records,
  });

  final num? rate;
  final int absences;
  final List<AttendanceRecord> records;

  factory AttendanceSummary.fromJson(
    Map<String, dynamic> json, {
    List<AttendanceRecord> records = const [],
  }) => AttendanceSummary(
    rate: json['attendance_rate'] as num?,
    absences: json['absences'] as int,
    records: records,
  );
}

class AttendanceRecord {
  const AttendanceRecord({
    required this.date,
    required this.status,
    required this.justified,
  });

  final String date;
  final String status;
  final bool justified;

  factory AttendanceRecord.fromJson(Map<String, dynamic> json) =>
      AttendanceRecord(
        date: json['attendance_date'] as String,
        status: json['status'] as String,
        justified: json['justified'] as bool,
      );
}

class ReportCardSummary {
  const ReportCardSummary({
    required this.id,
    required this.version,
    required this.issuedAt,
  });

  final String id;
  final int version;
  final String? issuedAt;

  factory ReportCardSummary.fromJson(Map<String, dynamic> json) =>
      ReportCardSummary(
        id: json['id'] as String,
        version: json['report_version'] as int,
        issuedAt: json['issued_at'] as String?,
      );
}
