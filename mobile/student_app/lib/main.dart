import 'package:flutter/material.dart';

import 'src/data/api_client.dart';
import 'src/data/session_store.dart';
import 'src/data/student_portal_repository.dart';
import 'src/models/portal_models.dart';
import 'src/home/role_home_page.dart';

void main() {
  final session = MemorySessionStore();
  final api = ApiClient(
    baseUrl: const String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://10.0.2.2:8017',
    ),
    session: session,
  );
  runApp(EduNovaStudentApp(api: api, session: session));
}

class EduNovaStudentApp extends StatelessWidget {
  const EduNovaStudentApp({
    super.key,
    required this.api,
    required this.session,
  });

  final ApiClient api;
  final SessionStore session;

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'EduNova Eleve',
    theme: ThemeData(
      colorSchemeSeed: const Color(0xff0b5d4b),
      useMaterial3: true,
    ),
    home: LoginPage(api: api, session: session),
  );
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key, required this.api, required this.session});

  final ApiClient api;
  final SessionStore session;

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController();
  final password = TextEditingController();
  final tenant = TextEditingController();
  String? error;
  bool loading = false;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('EduNova')),
    body: ListView(
      padding: const EdgeInsets.all(24),
      children: [
        const Text(
          'Portail eleve',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 24),
        TextField(
          controller: email,
          decoration: const InputDecoration(labelText: 'Adresse e-mail'),
        ),
        TextField(
          controller: password,
          obscureText: true,
          decoration: const InputDecoration(labelText: 'Mot de passe'),
        ),
        TextField(
          controller: tenant,
          decoration: const InputDecoration(
            labelText: 'Identifiant de l etablissement',
          ),
        ),
        if (error != null)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Text(error!, style: const TextStyle(color: Colors.red)),
          ),
        const SizedBox(height: 24),
        FilledButton(
          onPressed: loading ? null : _login,
          child: loading
              ? const CircularProgressIndicator()
              : const Text('Connexion'),
        ),
      ],
    ),
  );

  Future<void> _login() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final twoFactorToken = await widget.api.login(
        email: email.text.trim(),
        password: password.text,
        tenantId: tenant.text.trim(),
      );
      if (!mounted) return;
      if (twoFactorToken != null) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => TwoFactorPage(
              api: widget.api,
              session: widget.session,
              token: twoFactorToken,
            ),
          ),
        );
        return;
      }
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) =>
              RoleHomePage(api: widget.api, session: widget.session),
        ),
      );
    } on ApiException catch (exception) {
      if (mounted) setState(() => error = exception.message);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }
}

class TwoFactorPage extends StatefulWidget {
  const TwoFactorPage({
    super.key,
    required this.api,
    required this.session,
    required this.token,
  });

  final ApiClient api;
  final SessionStore session;
  final String token;

  @override
  State<TwoFactorPage> createState() => _TwoFactorPageState();
}

class _TwoFactorPageState extends State<TwoFactorPage> {
  final code = TextEditingController();
  String? error;
  bool loading = false;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Verification 2FA')),
    body: ListView(
      padding: const EdgeInsets.all(24),
      children: [
        const Text('Saisissez le code de verification.'),
        TextField(
          controller: code,
          keyboardType: TextInputType.number,
          maxLength: 6,
          decoration: const InputDecoration(labelText: 'Code 2FA'),
        ),
        if (error != null)
          Text(error!, style: const TextStyle(color: Colors.red)),
        FilledButton(
          onPressed: loading ? null : _verify,
          child: loading
              ? const CircularProgressIndicator()
              : const Text('Valider'),
        ),
      ],
    ),
  );

  Future<void> _verify() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      await widget.api.verifyLoginTwoFactor(
        token: widget.token,
        code: code.text,
      );
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) =>
              RoleHomePage(api: widget.api, session: widget.session),
        ),
      );
    } on ApiException catch (exception) {
      if (mounted) setState(() => error = exception.message);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({
    super.key,
    required this.repository,
    required this.session,
  });

  final StudentPortalRepository repository;
  final SessionStore session;

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
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
      title: const Text('Mon espace'),
      actions: [
        IconButton(
          onPressed: () async {
            await widget.session.clear();
            if (mounted)
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(
                  builder: (_) => LoginPage(
                    api: widget.repository.api,
                    session: widget.session,
                  ),
                ),
              );
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
                tooltip: 'Telecharger le PDF',
                onPressed: () async {
                  try {
                    final bytes = await widget.repository.reportCardPdf(
                      report.id,
                    );
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('PDF recu (${bytes.length} octets).'),
                        ),
                      );
                    }
                  } on ApiException catch (exception) {
                    if (mounted) setState(() => error = exception.message);
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
