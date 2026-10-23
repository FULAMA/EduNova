import 'dart:convert';

import 'package:http/http.dart' as http;

import 'session_store.dart';
import '../models/auth_models.dart';

class ApiException implements Exception {
  const ApiException(this.statusCode, this.message);

  final int statusCode;
  final String message;
}

class ApiClient {
  ApiClient({
    required this.baseUrl,
    required this.session,
    http.Client? client,
  }) : _client = client ?? http.Client();

  final String baseUrl;
  final SessionStore session;
  final http.Client _client;

  Future<Map<String, dynamic>> getJson(String path) async {
    final response = await _request('GET', path);
    return _decodeObject(response);
  }

  Future<List<dynamic>> getList(String path) async {
    final response = await _request('GET', path);
    try {
      final decoded = jsonDecode(response);
      if (decoded is List<dynamic>) {
        return decoded;
      }
    } on FormatException {
      // Convert malformed server responses to the public API error below.
    }
    throw const ApiException(0, 'Reponse serveur invalide.');
  }

  Future<AuthenticatedUser> currentUser() async =>
      AuthenticatedUser.fromJson(await getJson('/auth/me'));

  Future<List<int>> getBytes(String path) async {
    try {
      final token = session.accessToken;
      if (token == null) throw const ApiException(401, 'Session expiree.');
      final response = await _send(
        'GET',
        path,
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode < 200 || response.statusCode >= 300) {
        if (response.statusCode == 401) await session.clear();
        throw ApiException(response.statusCode, 'Le PDF est indisponible.');
      }
      return response.bodyBytes;
    } on http.ClientException {
      throw const ApiException(0, 'Serveur inaccessible.');
    }
  }

  Future<String?> login({
    required String email,
    required String password,
    required String tenantId,
  }) async {
    final response = await _request(
      'POST',
      '/auth/login',
      body: {'email': email, 'password': password, 'tenant_id': tenantId},
      authenticated: false,
    );
    final payload = _decodeObject(response);
    if (payload['two_factor_required'] == true) {
      return payload['two_factor_token'] as String?;
    }
    final token = payload['access_token'] as String?;
    if (token == null || token.isEmpty) {
      throw const ApiException(401, 'Authentification impossible.');
    }
    await session.saveAccessToken(token);
    final refreshToken = payload['refresh_token'] as String?;
    if (refreshToken != null) await session.saveRefreshToken(refreshToken);
    return null;
  }

  Future<void> verifyLoginTwoFactor({
    required String token,
    required String code,
  }) async {
    final response = await _request(
      'POST',
      '/auth/2fa/login',
      body: {'two_factor_token': token, 'code': code},
      authenticated: false,
    );
    final payload = _decodeObject(response);
    await session.saveAccessToken(payload['access_token'] as String);
    await session.saveRefreshToken(payload['refresh_token'] as String);
  }

  Future<String> _request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    bool authenticated = true,
  }) async {
    try {
      final headers = <String, String>{'Content-Type': 'application/json'};
      if (authenticated) {
        final token = session.accessToken;
        if (token == null) throw const ApiException(401, 'Session expiree.');
        headers['Authorization'] = 'Bearer $token';
      }
      final response = await _send(
        method,
        path,
        headers: headers,
        body: body == null ? null : jsonEncode(body),
      );
      if (response.statusCode < 200 || response.statusCode >= 300) {
        if (response.statusCode == 401 && authenticated) await session.clear();
        throw ApiException(response.statusCode, 'La requete a echoue.');
      }
      return response.body;
    } on http.ClientException {
      throw const ApiException(0, 'Serveur inaccessible.');
    }
  }

  Future<http.Response> _send(
    String method,
    String path, {
    Map<String, String>? headers,
    String? body,
  }) async {
    final request = http.Request(method, Uri.parse('$baseUrl$path'));
    if (headers != null) request.headers.addAll(headers);
    if (body != null) request.body = body;
    return http.Response.fromStream(await _client.send(request));
  }

  static Map<String, dynamic> _decodeObject(String response) {
    try {
      final decoded = jsonDecode(response);
      if (decoded is Map<String, dynamic>) {
        return decoded;
      }
    } on FormatException {
      // Convert malformed server responses to the public API error below.
    }
    throw const ApiException(0, 'Reponse serveur invalide.');
  }
}
