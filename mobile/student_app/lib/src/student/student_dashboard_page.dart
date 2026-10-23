import 'package:flutter/material.dart';

import '../data/api_client.dart';
import '../data/session_store.dart';
import '../data/student_portal_repository.dart';
import '../models/portal_models.dart';

class StudentDashboardPage extends StatefulWidget {
  const StudentDashboardPage({
    super.key,
    required this.repository,
    required this.session,
  });

  final StudentPortalRepository repository;
  final SessionStore session;

  @override
  State<StudentDashboardPage> createState() => _StudentDashboardPageState();
}

class _StudentDashboardPageState extends State<StudentDashboardPage> {
  late Future<StudentPortalProfile> profile;
  List<AcademicPeriod> periods = const [];
  AcademicRecord? record;
  AttendanceSummary? attendance;
  List<ReportCardSummary> reports = const [];
  String? selectedPeriod;
  String? error;

  @override
  void initState() {
    super.initState();
    profile = widget.repository.profile();
    _loadPeriods();
    _loadReports();
  }

  Future<void> _loadPeriods() async {
    try {
      periods = await widget.repository.periods();
      if (mounted) setState(() {});
    } on ApiException catch (exception) {
      if (mounted) setState(() => error = exception.message);
    }
  }

  Future<void> _loadReports() async {
    try {
      reports = await widget.repository.reportCards();
      if (mounted) setState(() {});
    } on ApiException catch (exception) {
      if (mounted) setState(() => error = exception.message);
    }
  }

  Future<void> _selectPeriod(String? value) async {
    if (value == null) return;
    setState(() {
      selectedPeriod = value;
      record = null;
      attendance = null;
    });
    try {
      final values = await Future.wait([
        widget.repository.record(value),
        widget.repository.attendance(value),
      ]);
      if (mounted)
        setState(() {
          record = values[0] as AcademicRecord;
          attendance = values[1] as AttendanceSummary;
        });
    } on ApiException catch (exception) {
      if (mounted) setState(() => error = exception.message);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Mon espace eleve'),
      actions: [
        IconButton(
          onPressed: () async {
            await widget.session.clear();
            if (context.mounted) Navigator.of(context).pop();
          },
          icon: const Icon(Icons.logout),
        ),
      ],
    ),
    body: RefreshIndicator(
      onRefresh: () async {
        await _loadPeriods();
        await _loadReports();
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          FutureBuilder<StudentPortalProfile>(
            future: profile,
            builder: (context, snapshot) => Text(
              snapshot.hasData
                  ? 'Bonjour ${snapshot.data!.firstName} ${snapshot.data!.lastName}'
                  : 'Chargement du profil...',
            ),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            value: selectedPeriod,
            decoration: const InputDecoration(labelText: 'Periode'),
            items: periods
                .map(
                  (period) => DropdownMenuItem(
                    value: period.id,
                    child: Text(period.name ?? period.id),
                  ),
                )
                .toList(),
            onChanged: _selectPeriod,
          ),
          if (error != null)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Text(error!, style: const TextStyle(color: Colors.red)),
            ),
          if (record != null) ...[
            _section('Resultats'),
            Text('Moyenne : ${record!.average}'),
            Text('Matieres echouees : ${record!.failedSubjects}'),
            ...record!.subjects.map(
              (subject) => ListTile(
                title: Text(subject.name ?? 'Matiere'),
                trailing: Text('${subject.average}'),
              ),
            ),
          ],
          if (attendance != null) ...[
            _section('Presence'),
            Text('Taux : ${attendance!.rate ?? 'N/A'}'),
            Text('Absences : ${attendance!.absences}'),
            ...attendance!.records.map(
              (item) => ListTile(
                title: Text(item.status),
                subtitle: Text(item.date),
                trailing: item.justified ? const Text('Justifiee') : null,
              ),
            ),
          ],
          _section('Bulletins officiels'),
          if (reports.isEmpty)
            const Text('Aucun bulletin officiel disponible.'),
          ...reports.map(
            (report) => ListTile(
              title: Text('Bulletin v${report.version}'),
              subtitle: Text(report.issuedAt ?? 'Date indisponible'),
              trailing: IconButton(
                icon: const Icon(Icons.picture_as_pdf),
                onPressed: () async {
                  try {
                    final bytes = await widget.repository.reportCardPdf(
                      report.id,
                    );
                    if (context.mounted)
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('PDF recu (${bytes.length} octets).'),
                        ),
                      );
                  } on ApiException catch (exception) {
                    if (context.mounted)
                      setState(() => error = exception.message);
                  }
                },
              ),
            ),
          ),
        ],
      ),
    ),
  );

  Widget _section(String title) => Padding(
    padding: const EdgeInsets.only(top: 20, bottom: 8),
    child: Text(
      title,
      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
    ),
  );
}
