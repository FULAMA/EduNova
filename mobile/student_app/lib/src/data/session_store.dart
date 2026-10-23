abstract interface class SessionStore {
  String? get accessToken;
  String? get refreshToken;
  Future<void> saveAccessToken(String token);
  Future<void> saveRefreshToken(String token);
  Future<void> clear();
}

/// Replace this adapter with platform secure storage before production release.
class MemorySessionStore implements SessionStore {
  String? _token;
  String? _refreshToken;

  @override
  String? get accessToken => _token;

  @override
  String? get refreshToken => _refreshToken;

  @override
  Future<void> saveAccessToken(String token) async => _token = token;

  @override
  Future<void> saveRefreshToken(String token) async => _refreshToken = token;

  @override
  Future<void> clear() async {
    _token = null;
    _refreshToken = null;
  }
}
