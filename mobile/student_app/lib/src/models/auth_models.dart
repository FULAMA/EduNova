class AuthenticatedUser {
  const AuthenticatedUser({required this.email, required this.role});

  final String email;
  final String role;

  factory AuthenticatedUser.fromJson(Map<String, dynamic> json) =>
      AuthenticatedUser(
        email: json['email'] as String,
        role: json['role'] as String,
      );
}
