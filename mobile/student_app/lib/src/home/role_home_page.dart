import 'package:flutter/material.dart';

import '../data/api_client.dart';
import '../data/session_store.dart';
import '../data/student_portal_repository.dart';
import '../models/auth_models.dart';
import '../student/student_dashboard_page.dart';

class RoleHomePage extends StatefulWidget {
  const RoleHomePage({super.key, required this.api, required this.session});

  final ApiClient api;
  final SessionStore session;

  @override
  State<RoleHomePage> createState() => _RoleHomePageState();
}

class _RoleHomePageState extends State<RoleHomePage> {
  late Future<AuthenticatedUser> user;

  @override
  void initState() {
    super.initState();
    user = widget.api.currentUser();
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<AuthenticatedUser>(
    future: user,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const Scaffold(body: Center(child: CircularProgressIndicator()));
      }
      if (snapshot.hasError) {
        return _UnavailablePage(
          message: 'Session expiree ou profil indisponible.',
          session: widget.session,
        );
      }
      final currentUser = snapshot.data!;
      if (currentUser.role == 'STUDENT') {
        return StudentDashboardPage(
          repository: StudentPortalRepository(widget.api),
          session: widget.session,
        );
      }
      return _UnavailablePage(
        message:
            'Le portail mobile ${currentUser.role} n est pas encore expose par l API.',
        session: widget.session,
      );
    },
  );
}

class _UnavailablePage extends StatelessWidget {
  const _UnavailablePage({required this.message, required this.session});

  final String message;
  final SessionStore session;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('EduNova')),
    body: Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Text(message, textAlign: TextAlign.center),
      ),
    ),
    floatingActionButton: FloatingActionButton(
      onPressed: () async {
        await session.clear();
        if (context.mounted) Navigator.of(context).pop();
      },
      tooltip: 'Se deconnecter',
      child: const Icon(Icons.logout),
    ),
  );
}
