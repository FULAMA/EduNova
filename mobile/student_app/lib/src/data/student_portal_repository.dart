import 'api_client.dart';
import '../models/portal_models.dart';

class StudentPortalRepository {
  StudentPortalRepository(this.api);

  final ApiClient api;

  Future<StudentPortalProfile> profile() async =>
      StudentPortalProfile.fromJson(await api.getJson('/me/student'));

  Future<List<AcademicPeriod>> periods() async =>
      (await api.getList('/me/student/academic-periods'))
          .map((item) => AcademicPeriod.fromJson(item as Map<String, dynamic>))
          .toList(growable: false);

  Future<AcademicRecord> record(String periodId) async =>
      AcademicRecord.fromJson(
        await api.getJson('/me/student/academic-records/$periodId'),
      );

  Future<AttendanceSummary> attendance(String periodId) async {
    final data = await api.getJson('/me/student/attendance/$periodId');
    final records = (data['records'] as List<dynamic>)
        .map((item) => AttendanceRecord.fromJson(item as Map<String, dynamic>))
        .toList(growable: false);
    return AttendanceSummary.fromJson(
      data['statistics'] as Map<String, dynamic>,
      records: records,
    );
  }

  Future<List<int>> reportCardPdf(String reportCardId) =>
      api.getBytes('/report-cards/$reportCardId/pdf');

  Future<List<ReportCardSummary>> reportCards() async =>
      (await api.getList('/report-cards'))
          .map(
            (item) => ReportCardSummary.fromJson(item as Map<String, dynamic>),
          )
          .toList(growable: false);
}
