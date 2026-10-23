import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:edunova_student/src/data/api_client.dart';
import 'package:edunova_student/src/data/session_store.dart';

void main() {
  const token = 'access-token';

  test('stores the access and refresh tokens after login', () async {
    final session = MemorySessionStore();
    final client = _client((request) async {
      expect(request.method, 'POST');
      expect(request.url.path, '/auth/login');
      expect(request.headers['content-type'], 'application/json');
      expect(jsonDecode(request.body)['tenant_id'], 'tenant-1');
      return _json({'access_token': token, 'refresh_token': 'refresh-token'});
    }, session: session);

    await client.login(
      email: 'student@example.test',
      password: 'password',
      tenantId: 'tenant-1',
    );

    expect(session.accessToken, token);
    expect(session.refreshToken, 'refresh-token');
  });

  test('maps an HTTP 401 and clears an authenticated session', () async {
    final session = MemorySessionStore();
    await session.saveAccessToken(token);
    final client = _client(
      (_) async => http.Response('', 401),
      session: session,
    );

    await expectLater(
      client.getJson('/auth/me'),
      throwsA(isA<ApiException>().having((e) => e.statusCode, 'status', 401)),
    );
    expect(session.accessToken, isNull);
  });

  test('adds the bearer token to authenticated requests', () async {
    final session = MemorySessionStore();
    await session.saveAccessToken(token);
    final client = _client((request) async {
      expect(request.headers['authorization'], 'Bearer $token');
      return _json({'role': 'STUDENT'});
    }, session: session);

    final response = await client.getJson('/auth/me');

    expect(response['role'], 'STUDENT');
  });

  test('rejects an authenticated request without a session', () async {
    final client = _client((_) async => fail('request must not be sent'));

    await expectLater(
      client.getJson('/auth/me'),
      throwsA(isA<ApiException>().having((e) => e.statusCode, 'status', 401)),
    );
  });

  test('maps a network failure', () async {
    final session = MemorySessionStore();
    await session.saveAccessToken(token);
    final client = _client((_) async {
      throw http.ClientException('offline');
    }, session: session);

    await expectLater(
      client.getJson('/auth/me'),
      throwsA(isA<ApiException>().having((e) => e.statusCode, 'status', 0)),
    );
  });

  test('maps malformed JSON to an API error', () async {
    final session = MemorySessionStore();
    await session.saveAccessToken(token);
    final client = _client(
      (_) async => http.Response('not-json', 200),
      session: session,
    );

    await expectLater(
      client.getJson('/auth/me'),
      throwsA(isA<ApiException>().having((e) => e.statusCode, 'status', 0)),
    );
  });

  test('supports the two-factor login response', () async {
    final client = _client(
      (_) async => _json({'access_token': token, 'refresh_token': 'refresh'}),
    );

    await client.verifyLoginTwoFactor(token: '2fa-token', code: '123456');

    expect(client.session.accessToken, token);
    expect(client.session.refreshToken, 'refresh');
  });

  test('downloads PDF bytes with authentication', () async {
    final session = MemorySessionStore();
    await session.saveAccessToken(token);
    final client = _client((request) async {
      expect(request.headers['authorization'], 'Bearer $token');
      return http.Response.bytes([37, 80, 68, 70], 200);
    }, session: session);

    expect(await client.getBytes('/report-cards/card-1/pdf'), [37, 80, 68, 70]);
  });
}

ApiClient _client(
  Future<http.Response> Function(http.Request) handler, {
  SessionStore? session,
}) => ApiClient(
  baseUrl: 'https://api.example.test',
  session: session ?? MemorySessionStore(),
  client: MockClient(handler),
);

http.Response _json(Map<String, dynamic> value) => http.Response(
  jsonEncode(value),
  200,
  headers: {'content-type': 'application/json'},
);
