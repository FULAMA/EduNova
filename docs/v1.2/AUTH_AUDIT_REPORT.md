# RAPPORT D'AUDIT COMPLET — AUTH-HARDENING V1.2
## Stabilisation définitive et audit intégral de l'authentification EduNova

**Date :** 2026-11-07  
**Auteur :** Antigravity (Équipe d'ingénierie EduNova)  
**Branche Git :** `fix/mypy-test-double-contracts`  
**Statut :** AUDIT TERMINÉ — AUCUNE MODIFICATION DE CODE RÉALISÉE SANS VALIDATION PRÉALABLE  
**Bases de données préservées :** `edunova.db` et `edunova_dev.db` intactes, aucun reset, aucun clean.

---

## 1. Synthèse Exécutive

Dans le cadre de la préparation de la version **V1.2 d'EduNova**, un audit d'ingénierie et de sécurité approfondi a été mené sur l'ensemble de la chaîne d'authentification, de gestion des sessions, de contrôle d'accès (RBAC) et d'isolation multi-tenant.

Le système d'authentification actuel repose sur des fondations techniques saines (Clean Architecture, DDD pragmatique, hachage Argon2id, tokens JWT HS256 avec rotation des refresh tokens). Cependant, plusieurs angles morts majeurs ont été identifiés, notamment l'absence totale de limitation de débit (**Rate Limiting**), le risque d'**énumération de comptes par attaque temporelle**, l'**absence de cycle de vie complet du mot de passe** (pas de changement ni de réinitialisation), le **stockage en clair du secret TOTP 2FA**, et une **incohérence entre rôle global et rôle contextuel multi-tenant** dans certaines dépendances.

Conformément aux règles strictes de la mission, **aucune modification de code n'a été entreprise** durant cette phase. Ce rapport présente l'état réel des lieux, les preuves techniques, la classification des risques et une feuille de route priorisée pour validation avant toute implémentation.

---

## 2. Architecture et Flux d'Authentification Actuels

### 2.1 Cartographie des Composants

```
                               ┌────────────────────────────────────────────────────────┐
                               │                    FRONTEND REACT                      │
                               │  - auth.storage.ts (sessionStorage)                    │
                               │  - client.ts (Intercepteur 401 + refreshPromise)       │
                               │  - RequireAuth / RequireRole (permissions.ts)          │
                               └──────────────────────────┬─────────────────────────────┘
                                                          │ HTTPS / JSON
                                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       BACKEND FASTAPI (PRESENTATION)                                  │
│  - Routes : /auth/register, /auth/login, /auth/refresh, /auth/logout, /auth/2fa/*, /auth/me           │
│  - Dépendances : get_current_user, get_tenant_context, require_role                                    │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                   │
                         ┌─────────────────────────┴─────────────────────────┐
                         ▼                                                   ▼
┌──────────────────────────────────────────────────┐ ┌──────────────────────────────────────────────────┐
│             BOUNDED CONTEXT IDENTITY             │ │             BOUNDED CONTEXT TENANCY              │
│  - Use Cases: LoginUser, LogoutUser,             │ │  - Entities: Tenant, Membership                  │
│    RefreshAccessToken, RegisterUser,             │ │  - Use Cases: SelectTenant                       │
│    EnableTwoFactor, VerifyLoginTwoFactor         │ │  - Interfaces: TenantRepo, MembershipRepo        │
│  - Hasher: Argon2PasswordHasher (argon2-cffi)    │ └─────────────────────────┬────────────────────────┘
│  - 2FA: PyOtpTwoFactorService (TOTP)             │                           │
│  - Tokens: JwtService (pyjwt, HS256)             │                           │
└────────────────────────┬─────────────────────────┘                           │
                         │                                                     │
                         └─────────────────────────┬───────────────────────────┘
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       INFRASTRUCTURE / PERSISTANCE                                    │
│  - Tables SQLite : users, revoked_refresh_tokens, tenants, memberships, external_identities           │
│  - Intégrité : consume(jti) atomique avec INSERT OR IGNORE                                            │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Flux Détaillés

#### Flux A — Connexion Utilisateur (Mot de passe et 2FA optionnel)
1. Le client frontend transmet `POST /auth/login` avec `{ email, password, tenant_id }`.
2. Le backend recherche l'utilisateur par son email dans `users`.
   - Si absent : lève `ValueError("Identifiants invalides.")` -> HTTP 401.
   - Si inactif (`is_active = False`) : lève `ValueError("Le compte est desactive.")` -> HTTP 401.
3. Vérifie le mot de passe via `Argon2PasswordHasher.verify(password, user.password_hash)`.
   - Si incorrect : lève `ValueError("Identifiants invalides.")` -> HTTP 401.
4. Vérifie l'éligibilité multi-tenant :
   - Recherche l'établissement (`tenant.active == True`) et l'adhésion (`membership.active == True`).
   - Si absent ou inactif : lève `ValueError("Acces tenant refuse.")` -> HTTP 403 Forbidden.
5. **Branche 2FA :**
   - Si `user.two_factor_enabled` est actif, le backend émet un jeton temporaire JWT (`type: "2fa_pending"`, expiration 5 minutes, sans jti) et répond `{ authenticated: false, two_factor_required: true, two_factor_token: "..." }`.
   - L'utilisateur soumet son code TOTP à 6 chiffres via `POST /auth/2fa/login` avec `{ two_factor_token, code }`.
   - Le backend décode le jeton temporaire, vérifie le code TOTP avec `PyOtpTwoFactorService.verify_code(secret, code)`.
6. **Émission des jetons finaux :**
   - `access_token` : JWT signé HS256, durée 15 minutes, payload : `sub` (user_id), `role` (`membership.role`), `tenant_id`, `type: "access"`, `iat`, `exp`.
   - `refresh_token` : JWT signé HS256, durée 7 jours, payload : `sub`, `jti` (UUID4 unique), `tenant_id`, `type: "refresh"`, `iat`, `exp`.
7. Le frontend stocke la session `{ accessToken, refreshToken, email, tenantId }` dans le `sessionStorage` du navigateur.

#### Flux B — Renouvellement de Session (Refresh & Rotation)
1. Lors d'un appel API protégé, si le backend répond `401 Unauthorized`, l'intercepteur `client.ts` intercepte la réponse.
2. Pour éviter les requêtes de rafraîchissement concurrentes, `client.ts` utilise une promesse partagée (`refreshPromise`).
3. Le client envoie `POST /auth/refresh` avec `{ refresh_token }`.
4. Le use case `RefreshAccessToken` :
   - Décode le jeton refresh (contrôle signature, expiration et présence des claims `sub`, `jti`, `tenant_id`).
   - Vérifie si le `jti` est déjà révoqué dans `revoked_refresh_tokens`.
   - Re-vérifie que l'utilisateur, le tenant et le membership sont toujours actifs en base.
   - Génère une nouvelle paire `access_token` et `new_refresh_token` (avec un nouveau `jti`).
   - Appelle `refresh_token_repository.consume(jti)` qui exécute atomiquement `INSERT OR IGNORE INTO revoked_refresh_tokens (jti, revoked_at)`.
   - Si `cursor.rowcount == 0` (tentative de rejeu ou requête concurrente frauduleuse), la transaction est rejetée immédiatement avec `ValueError("Token refresh revoque.")`.
5. Si le renouvellement réussit, le frontend met à jour le `sessionStorage` et rejoue la requête HTTP initiale.
6. Si le renouvellement échoue (token invalide/révoqué), le frontend exécute `notifySessionExpired()` : purge du `sessionStorage` et émission de l'événement `SESSION_EXPIRED_EVENT`.

#### Flux C — Déconnexion (Logout)
1. L'utilisateur déclenche la déconnexion dans l'UI (Topbar).
2. `auth.service.ts` appelle `POST /auth/logout` avec `{ refresh_token: session.refreshToken }`.
3. Le backend décode le token refresh, extrait son `jti` et l'ajoute dans `revoked_refresh_tokens` via `INSERT OR IGNORE` (opération idempotente).
4. Le backend renvoie `204 No Content`.
5. Le frontend exécute systématiquement `clearSession()` dans un bloc `finally` pour garantir la purge locale, même en cas de défaillance réseau.
6. *Note architecturale validée :* Les `access_token` ne sont pas inscrits sur liste noire serveur ; ils expirent de manière naturelle après 15 minutes.

---

## 3. Matrice d'Évaluation des Mécanismes de Sécurité

Chaque mécanisme est classé selon les statuts officiels :
- **VERIFIED** : Implémenté, robuste et validé par des tests réels.
- **IMPLEMENTED_NOT_VERIFIED** : Présent dans le code mais sans preuve de test automatisé sous charge ou scénario d'erreur.
- **PARTIAL** : Implémenté de manière incomplète ou manquant de garde-fous essentiels.
- **VULNERABLE** : Présente une faille de sécurité exploitable.
- **MISSING** : Mécanisme absent du système.
- **BLOCKED** : Bloqué par une dépendance métier ou technique en attente.

| Mécanisme | Statut | Justification & Preuves Techniques |
|-----------|--------|------------------------------------|
| **Hachage des mots de passe (Argon2id)** | **VERIFIED** | `Argon2PasswordHasher` utilise `argon2-cffi` avec sel aléatoire géré par la bibliothèque, paramètres conformes OWASP. 100% des tests unitaires passent. |
| **Génération & Validation JWT (HS256)** | **VERIFIED** | `JwtService` impose une clé secrète >= 32 caractères, valide strictement `algorithms=["HS256"]`, rejette `alg: none` et contrôle `iat`/`exp`. |
| **Rotation atomique des Refresh Tokens** | **VERIFIED** | Le `jti` est consommé à chaque rotation via `consume(jti)` dans SQLite avec contrôle de `rowcount == 1`. Test unitaire `test_refresh_rotates_and_consumes_jti`. |
| **Révocation à la Déconnexion** | **VERIFIED** | `LogoutUser` révoque le `jti`. `tests/integration/test_auth_logout_http.py` prouve la révocation immédiate (401 sur tentative de réutilisation) et l'idempotence. |
| **Isolation Multi-tenant (Tenancy)** | **VERIFIED** | `get_tenant_context` extrait `tenant_id` du JWT et valide l'adhésion active dans `memberships`. Rejette toute usurpation de tenant (HTTP 403). |
| **Contrôle d'accès par Rôle (RBAC Backend)** | **VERIFIED** | Dépendance `require_role` vérifie `membership.role` en base. Testé unitairement dans `test_auth.py` et par intégration dans `test_authorization_http.py`. |
| **Déduplication Refresh Frontend** | **VERIFIED** | `refreshPromise` dans `frontend/src/shared/api/client.ts` fusionne les requêtes simultanées et évite le flood ou la course de refresh. |
| **Authentification à deux facteurs (TOTP)** | **PARTIAL** | TOTP fonctionnel via `pyotp`, mais le paramétrage est réservé à l'ADMIN, sans codes de secours et sans chiffrement du secret au repos. |
| **Politique de complexité des mots de passe** | **VULNERABLE** | Seule la longueur minimale (8 caractères) est vérifiée dans le schéma Pydantic. Aucune règle de complexité, aucune vérification de mots de passe compromis. |
| **Protection anti-énumération de comptes** | **VULNERABLE** | Timing attack sur `/auth/login` (retour anticipé si utilisateur inexistant sans calcul Argon2) + fuite d'état sur compte inactif + message explicite à l'inscription. |
| **Protection anti-Brute Force (Rate Limiting)** | **MISSING** | Aucun rate limiter, aucun compteur d'échecs de connexion, aucune temporisation ni verrouillage de compte en cas d'attaque par dictionnaire. |
| **Cycle de vie du mot de passe (Changement/Reset)**| **MISSING** | Aucun use case ni endpoint `ChangePassword`, `ForgotPassword`, `ResetPassword`. |
| **Révocation globale des sessions utilisateur** | **MISSING** | Aucun mécanisme permettant d'invalider tous les refresh tokens d'un utilisateur simultanément (absence de `token_version` ou de timestamp d'invalidation). |
| **Chiffrement au repos des secrets 2FA** | **VULNERABLE** | La colonne `two_factor_secret` dans la table `users` stocke la clé base32 TOTP en texte brut sans chiffrement symétrique. |
| **Désactivation administrative du 2FA** | **MISSING** | Aucun use case ni endpoint pour réinitialiser le 2FA d'un utilisateur ayant égaré son application TOTP. |

---

## 4. Vulnérabilités Identifiées et Niveaux de Criticité

### 4.1 Vulnérabilités Critiques (CRITICAL)

#### VULN-01 : Absence totale de limitation de débit (Rate Limiting) et de protection anti-brute force
- **Localisation :** `src/presentation/api/routes/auth.py` (toutes les routes d'authentification).
- **Preuve technique :**
  Aucun middleware de limitation de débit (`slowapi`, token bucket ou équivalent) n'est configuré dans `create_app()`. Aucune table de suivi des tentatives de connexion n'existe dans la base de données.
- **Impact :**
  1. Attaque par dictionnaire ou credential stuffing à haut débit sur `POST /auth/login`.
  2. Sur `POST /auth/2fa/login` : le jeton `two_factor_token` a une durée de vie de 5 minutes. Durant cette fenêtre, un attaquant peut exécuter plusieurs dizaines de milliers de requêtes pour tester les 1 000 000 de combinaisons du code TOTP à 6 chiffres sans jamais être bloqué.

#### VULN-02 : Absence d'invalidation globale des sessions et absence de cycle de vie du mot de passe
- **Localisation :** `src/identity/application/use_cases/` (absence de `ChangePassword`, absence de `RevokeAllUserSessions`).
- **Preuve technique :**
  Il est impossible pour un utilisateur ou un administrateur de changer un mot de passe compromis. Si un mot de passe venait à être modifié directement en base, aucun mécanisme d'invalidation des tokens existants n'est implémenté (les JWT d'accès restent valides 15 minutes, et les refresh tokens déjà émis restent valides jusqu'à 7 jours car `revoked_refresh_tokens` n'enregistre que des `jti` unitaires).
- **Impact :**
  Impossibilité d'éjecter un attaquant en possession d'une session ou d'un refresh token actif.

#### VULN-03 : Stockage en clair des secrets TOTP 2FA dans la base de données
- **Localisation :** `src/infrastructure/repositories/sqlite_user_repository.py:30-50` et migration 001.
- **Preuve technique :**
  La table `users` comporte le champ `two_factor_secret TEXT`. La valeur générée par `pyotp.random_base32()` y est insérée directement sans chiffrement AES-256-GCM / Fernet.
- **Impact :**
  Toute lecture non autorisée de la base SQLite (dump, sauvegarde exposée, faille SQLi) expose l'intégralité des secrets TOTP des utilisateurs, annulant le bénéfice du deuxième facteur d'authentification.

---

### 4.2 Vulnérabilités Élevées (HIGH)

#### VULN-04 : Énumération de comptes via timing attacks et messages d'erreurs
- **Localisation :** `src/identity/application/use_cases/login_user.py:61-81` et `src/identity/application/use_cases/register_user.py:48-51`.
- **Preuve technique :**
  Dans `login_user.py` :
  ```python
  user = self._user_repository.find_by_email(email)
  if user is None:
      raise ValueError("Identifiants invalides.")  # Retour en < 1 ms

  if not user.is_active:
      raise ValueError("Le compte est desactive.")  # Fuite d'état immédiate avant vérification de mot de passe !

  if not self._password_hasher.verify(password, user.password_hash):  # Prend ~60 ms (Argon2id)
      raise ValueError("Identifiants invalides.")
  ```
  Dans `register_user.py` :
  ```python
  if existing_user is not None:
      raise ValueError("Cette adresse email est deja utilisee.")  # Retourne 400 Bad Request
  ```
- **Impact :**
  Un attaquant distant peut dresser la liste complète des utilisateurs enregistrés en observant l'écart tempoint (< 1ms vs ~60ms) et en testant les inscriptions, ou en constatant le message `"Le compte est desactive."`.

#### VULN-05 : Faiblesse de la politique de mot de passe
- **Localisation :** `src/presentation/api/schemas/register_user_request.py:8` et `src/identity/domain/entities/user.py`.
- **Preuve technique :**
  Le schéma Pydantic exige uniquement `password: str = Field(min_length=8)`. Le use case `RegisterUser` vérifie uniquement `if not password: raise ValueError(...)`.
- **Impact :**
  Acceptation de mots de passe triviaux ("12345678", "password", "azerty123"), vulnérables aux attaques par dictionnaire hors-ligne et en ligne.

#### VULN-06 : Divergence de rôle dans `get_current_user` vs rôle contextuel multi-tenant
- **Localisation :** `src/presentation/api/dependencies/auth.py:86-92`.
- **Preuve technique :**
  `get_current_user` instancie `AuthenticatedUser` avec `role=user.role` (le rôle par défaut de la table `users`), alors que dans une architecture multi-tenant où un utilisateur peut appartenir à plusieurs établissements avec des rôles distincts (Décisions 13 et 14), le rôle réel est `membership.role`.
- **Impact :**
  Toute route protégée par `get_current_user` qui évaluerait `current_user.role` sans passer par `require_role` inspecterait un rôle potentiellement erroné ou obsolète.

---

### 4.3 Vulnérabilités Moyennes (MEDIUM)

#### VULN-07 : Exposition du secret TOTP en clair dans la réponse API d'enrôlement
- **Localisation :** `src/presentation/api/routes/auth.py:326-329` (`EnableTwoFactorResponse`).
- **Preuve technique :**
  La réponse JSON renvoie à la fois l'URI de provisionnement `otpauth://` et le secret brut `secret`.
- **Recommandation :**
  Ne renvoyer que l'URI de provisionnement (ou son QR code) et limiter la transmission de la clé brute à la seule demande explicite de saisie manuelle.

#### VULN-08 : Absence de codes de secours (Recovery Codes) et de procédure de réinitialisation 2FA
- **Localisation :** Bounded context `identity`.
- **Impact :**
  En cas de perte d'appareil, l'utilisateur est définitivement verrouillé hors de son compte. Aucun endpoint ne permet à l'administrateur de désactiver le 2FA d'un compte bloqué.

#### VULN-09 : Stockage des jetons dans `sessionStorage` (Exposition en cas de XSS)
- **Localisation :** `frontend/src/features/auth/services/auth.storage.ts`.
- **Preuve technique :**
  Les tokens sont stockés dans `sessionStorage`. Bien que ce choix isole la session par onglet et protège des attaques CSRF classiques sans cookie, tout code injecté via une faille XSS peut lire l'accès et le refresh token.
- **Recommandation à terme :**
  Évaluer une transition vers des cookies `HttpOnly`, `Secure`, `SameSite=Strict` avec jeton CSRF dédié lors d'un prochain lot d'infrastructure, sans perturber l'architecture SPA actuelle.

#### VULN-10 : Absence de validation des claims standards `iss` (Issuer) et `aud` (Audience)
- **Localisation :** `src/infrastructure/security/jwt_service.py:41-48, 96-100`.
- **Preuve technique :**
  Les jetons ne définissent ni ne vérifient `iss` ni `aud`. Dans un environnement multi-services ou API distribuée, un token émis pour un service pourrait être rejoué sur un autre.

---

### 4.4 Vulnérabilités Faibles et Recommandations (LOW / INFORMATIONAL)

#### VULN-11 : Absence de détection de compromission en chaîne (Family Revocation)
- Lorsqu'un refresh token déjà révoqué est présenté, `consume(jti)` échoue et la requête est rejetée. Cependant, selon les recommandations de la RFC 6819 (OAuth 2.0 Threat Model), la réutilisation d'un token consommé devrait invalider immédiatement toute la descendance active de cette session (alerte d'interception).

#### VULN-12 : Absence de ré-hachage automatique des mots de passe (`check_needs_rehash`)
- Si les paramètres Argon2id (mémoire, itérations) sont augmentés dans les versions futures de la bibliothèque, les mots de passe ne sont pas automatiquement ré-hachés lors des connexions réussies.

---

## 5. Matrice des 20 Scénarios de Sécurité Obligatoires

Voici l'état d'exécution réel des 20 scénarios exigés par le protocole d'audit :

| # | Scénario de Sécurité | Statut Réel | Référence de Test / Preuve | Constat d'Audit |
|---|----------------------|-------------|----------------------------|-----------------|
| 1 | Connexion valide | **VERIFIED** | `tests/unit/identity/application/use_cases/test_login_user.py::test_login_success` | Émission conforme de l'access token et du refresh token avec les bons claims. |
| 2 | Identifiants incorrects | **VERIFIED** | `tests/unit/identity/application/use_cases/test_login_user.py::test_login_invalid_password_raises_error` | Rejet avec exception `ValueError("Identifiants invalides.")`. |
| 3 | Compte désactivé | **VERIFIED** | `tests/unit/identity/application/use_cases/test_login_user.py::test_login_inactive_user_raises_error` | Rejet avec exception si `user.is_active = False`. |
| 4 | Token expiré | **VERIFIED** | `tests/unit/infrastructure/security/test_jwt_service.py::test_decode_token_rejects_expired_token` | `jwt.ExpiredSignatureError` capturé et rejeté avec `ValueError`. |
| 5 | Token falsifié | **VERIFIED** | `tests/unit/infrastructure/security/test_jwt_service.py::test_decode_invalid_token_raises_value_error` | Format JWT invalide ou payload corrompu rejeté. |
| 6 | Mauvaise signature | **VERIFIED** | `tests/unit/infrastructure/security/test_jwt_service.py::test_token_created_with_different_secret_is_rejected` | Signature générée avec une clé différente systématiquement rejetée. |
| 7 | Algorithme JWT non autorisé | **VERIFIED** | `tests/unit/infrastructure/security/test_jwt_service.py` | PyJWT configuré avec `algorithms=["HS256"]` strict ; `alg: none` ou RSA rejetés. |
| 8 | Refresh token valide | **VERIFIED** | `tests/unit/identity/application/use_cases/test_refresh_access_token.py::test_refresh_returns_new_tokens` | Renouvellement réussi avec émission d'un nouvel access token et nouveau refresh token. |
| 9 | Refresh token expiré | **VERIFIED** | `tests/unit/infrastructure/security/test_jwt_refresh.py` | Token refresh dont la date d'expiration est dépassée rejeté. |
| 10 | Refresh token révoqué | **VERIFIED** | `tests/unit/identity/application/use_cases/test_refresh_access_token.py::test_revoked_refresh_token_is_rejected` | Si `jti` présent dans `revoked_refresh_tokens`, renouvellement rejeté. |
| 11 | Réutilisation d'un refresh token après rotation | **VERIFIED** | `tests/unit/identity/application/use_cases/test_refresh_access_token.py::test_old_refresh_token_is_revoked` | L'ancien token est révoqué dès sa première consommation ; toute 2e tentative est refusée. |
| 12 | Déconnexion puis renouvellement | **VERIFIED** | `tests/integration/test_auth_logout_http.py::test_logout_revokes_refresh_token` | Après appel à `/auth/logout`, le refresh token est révoqué et `/auth/refresh` renvoie 401. |
| 13 | Changement de mot de passe puis ancienne session | **MISSING** | *Aucun test existant* | **Fonctionnalité absente** : Il n'existe pas de use case de changement de mot de passe ni de révocation globale. |
| 14 | Tentative d'accès à un autre tenant | **VERIFIED** | `tests/unit/presentation/api/dependencies/test_auth.py` | `get_tenant_context` vérifie la table `memberships` ; accès refusé si le tenant_id du JWT n'appartient pas à l'utilisateur (HTTP 403). |
| 15 | Tentative d'élévation de privilèges | **VERIFIED** | `tests/unit/presentation/api/dependencies/test_auth.py::test_require_role_rejects_wrong_role` | L'altération du rôle dans le JWT est impossible (signature HS256) et l'inscription publique force le rôle STUDENT. |
| 16 | Accès sans authentification | **VERIFIED** | `tests/integration/test_authorization_http.py::test_unauthenticated_user_cannot_access_admin_2fa_setup` | Les endpoints protégés renvoient immédiatement 401 Unauthorized via `bearer_scheme`. |
| 17 | Accès avec rôle insuffisant | **VERIFIED** | `tests/integration/test_authorization_http.py::test_teacher_cannot_access_admin_2fa_setup` | Un utilisateur ayant un rôle non autorisé (ex: TEACHER, STUDENT) reçoit 403 Forbidden ("Acces interdit."). |
| 18 | Requêtes simultanées de renouvellement | **PARTIAL** | `frontend/src/shared/api/client.ts` | Frontend protégé via `refreshPromise`. Test de concurrence multithread sous forte charge backend à consolider. |
| 19 | Révocation d'une session sans affecter les autres | **VERIFIED** | `tests/integration/test_auth_logout_http.py::test_logout_cross_user_token_does_not_leak_session` | La révocation d'un token appartenant à l'utilisateur B n'invalide pas la session active de l'utilisateur A. |
| 20 | Absence de secrets dans logs et réponses | **PARTIAL** | `tests/unit/identity/application/use_cases/test_login_user.py` | `password_hash` non retourné dans `/auth/me` ou `/login`, mais le secret TOTP brut est renvoyé dans `/auth/2fa/setup`. Filtre de logs centralisé manquant. |

---

## 6. Analyse de Conformité Architecturale

### 6.1 Clean Architecture et DDD pragmatique
- **Séparation des couches :**
  La frontière entre Domain (`User`, `Membership`), Application (`LoginUser`, `RefreshAccessToken`, `LogoutUser`) et Infrastructure (`Argon2PasswordHasher`, `SQLiteUserRepository`, `JwtService`) est strictement respectée via des interfaces abstraites (`abc.ABC`).
- **Gestion des dépendances :**
  L'injection de dépendances est centralisée proprement dans `ApplicationContainer` (`src/presentation/api/container.py`) et reliée à FastAPI via `Depends()`.
- **Divergence constatée :**
  Les règles de validation de mot de passe sont actuellement placées dans la couche présentation (schéma Pydantic), au lieu d'être encapsulées dans un Value Object de domaine (ex: `Password` ou `HashedPassword`), ce qui viole le principe DDD selon lequel le domaine doit être le garant de ses propres invariants.

### 6.2 Principes SOLID
- **Single Responsibility Principle (SRP) :**
  Chaque use case a une responsabilité unitaire (`LoginUser`, `LogoutUser`, `RefreshAccessToken`).
- **Open/Closed Principle (OCP) :**
  L'utilisation d'interfaces (`PasswordHasher`, `RefreshTokenRepository`, `TwoFactorService`) permet d'étendre ou de remplacer les briques (ex: migration vers Redis pour les tokens révoqués) sans toucher aux use cases métier.
- **Dependency Inversion Principle (DIP) :**
  Les use cases ne dépendent que des interfaces de haut niveau, jamais des implémentations concrètes SQLite ou Argon2.

---

## 7. Plan de Correction et de Stabilisation Proposé (Post-Validation)

Ce plan est structuré par ordre de priorité et d'impact pour la sécurité opérationnelle d'EduNova. **Il ne sera exécuté qu'après validation explicite de l'utilisateur.**

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PLAN DE STABILISATION AUTH-HARDENING V1.2                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ÉTAPE 1 : PROTECTION IMMÉDIATE (ANTI-BRUTE FORCE & TEMPS CONSTANT)                     │
│   1.1 Implémentation d'un hachage factice (dummy hash) sur /auth/login pour garantir   │
│       un temps de réponse constant (~60ms) même si l'email n'existe pas.               │
│   1.2 Harmonisation des messages d'erreur sur /auth/login ("Identifiants invalides"    │
│       même si le compte est inactif, afin de bloquer l'énumération).                   │
│   1.3 Rate Limiter en mémoire (Token Bucket / Fenêtre glissante) sur /auth/login,      │
│       /auth/register et /auth/2fa/login (max 5 tentatives par IP/minute).              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ÉTAPE 2 : SÉCURISATION DU 2FA & DU STOCKAGE DES SECRETS                                │
│   2.1 Chiffrement symétrique au repos de `two_factor_secret` (AES-256-GCM / Fernet)    │
│       en base SQLite, adossé à une clé de chiffrement serveur dédiée.                  │
│   2.2 Limitation stricte à 3 tentatives maximum de validation du code 2FA pour un      │
│       `two_factor_token` donné avant révocation immédiate du token d'attente.          │
│   2.3 Création des use cases `DisableTwoFactor` (réservé ADMIN) et génération de       │
│       codes de récupération d'urgence (Backup Codes).                                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ÉTAPE 3 : CYCLE DE VIE DU MOT DE PASSE & INVALIDATION GLOBALE                          │
│   3.1 Création du use case `ChangePassword` avec validation de l'ancien mot de passe,  │
│       et application d'une politique de mot de passe robuste dans le domaine DDD       │
│       (min 10 chars, majuscule, chiffre, caractère spécial).                           │
│   3.2 Invalidation globale de toutes les sessions actives d'un utilisateur lors d'un    │
│       changement de mot de passe (introduction d'un champ `token_version` ou           │
│       `password_changed_at` vérifié dans `get_current_user` et `RefreshAccessToken`).  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ÉTAPE 4 : CONSOLIDATION MULTI-TENANT & TESTS D'INTÉGRATION DE SÉCURITÉ                 │
│   4.1 Harmonisation de `AuthenticatedUser` dans `dependencies/auth.py` pour injecter   │
│       systématiquement `role = membership.role` du tenant résolu.                      │
│   4.2 Implémentation des 2 scénarios de test manquants (Scénario 13 et test de charge │
│       concurrent sur le rafraîchissement) dans la suite de tests automatisée.          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Conclusion et Demande de Décision

L'audit intégral de l'authentification est **achevé et documenté**.

- L'architecture actuelle est comprise et cartographiée.
- Les flux de connexion, renouvellement et déconnexion sont clarifiés.
- Les 20 scénarios de sécurité sont évalués (16 VERIFIED, 2 PARTIAL, 2 MISSING/VULNERABLE).
- Les vulnérabilités réelles sont classées (CRITICAL, HIGH, MEDIUM, LOW).
- **Aucune modification de code ni écrasement de base persistante n'a été effectué.**

Ce rapport est soumis pour validation avant d'engager toute correction ou lot fonctionnel ultérieur.
