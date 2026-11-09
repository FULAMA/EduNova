# RAPPORT D'ÉTAPE 4 — ENDPOINTS HTTP, VALIDATION PYDANTIC ET RATE LIMITING

**Date :** 2026-11-09  
**Auteur :** Antigravity Pair Programmer  
**Statut :** Terminé — En attente de validation client pour l'Étape 5  
**Branche Git :** `fix/mypy-test-double-contracts` (sans commit, sans push, sans modification de bases de données de prod/dev)

---

## 1. Rappel des objectifs de l'Étape 4

L'Étape 4 avait pour but d'exposer de manière sécurisée les use cases de Self-Service Registration et de résolution de tenant via les routes HTTP FastAPI de la plateforme EduNova, en garantissant :
1. Une validation stricte des entrées via des schémas Pydantic (`extra="forbid"` pour interdire l'injection de champs non prévus comme `role`, `tenant_id`, ou des permissions).
2. L'implémentation de `POST /auth/register-establishment` avec rate limiting (5 req / 15 min / IP).
3. L'évolution de `POST /auth/login` (prise en charge du `tenant_id` optionnel, retour de l'état `tenant_selection_required: true` et du jeton temporaire pour les utilisateurs multi-établissements).
4. L'implémentation de `POST /auth/select-tenant` avec rate limiting (10 req / min / IP).
5. Le durcissement anti-rejeu du `tenant_selection_token` : persistance SQLite atomique (`consumed_tokens`) résistante aux concurrences multi-workers et aux redémarrages de processus.
6. La protection contre le spoofing d'adresses IP via l'en-tête `X-Forwarded-For` par filtrage des proxys de confiance (`_TRUSTED_PROXIES`).
7. La mise à jour de la documentation d'API frontend (`frontend/docs/CONTRATS_API_MANQUANTS.md`).
8. La couverture par 15 tests d'intégration HTTP complets.

---

## 2. Réalisations architecturales & techniques

### 2.1 Schémas Pydantic durcis (`extra="forbid"`)

Tous les modèles de requête ont été configurés avec `model_config = ConfigDict(extra="forbid")` afin d'empêcher formellement toute tentative d'injection de propriétés réservées côté client :

- `RegisterEstablishmentRequest` (`src/presentation/api/schemas/register_establishment_request.py`) :
  - `school_name`: str (min 2, max 200)
  - `admin_name`: str (min 2, max 150)
  - `email`: str (min 5, max 255)
  - `password`: str (min 8, max 128)
- `RegisterEstablishmentResponse` (`src/presentation/api/schemas/register_establishment_response.py`) :
  - Renvoie `tenant_id`, `tenant_name`, `tenant_slug`, `user_id`, `admin_name`, `email`, `role`.
  - Ne divulgue aucun hash, mot de passe ni secret interne.
- `LoginUserRequest` (`src/presentation/api/schemas/login_user_request.py`) :
  - `email`: str
  - `password`: str
  - `tenant_id`: UUID | None = None (optionnel)
- `LoginUserResponse` (`src/presentation/api/schemas/login_user_response.py`) :
  - Enrichi avec `tenant_selection_required: bool`, `tenant_selection_token: str | None`, `available_tenants: list[TenantOptionSchema]`.
- `SelectTenantRequest` (`src/presentation/api/schemas/select_tenant_request.py`) :
  - `tenant_selection_token`: str (min 10)
  - `tenant_id`: UUID

---

### 2.2 Durcissement anti-rejeu persistant (`consumed_tokens`)

Conformément à l'audit préalable et aux contraintes architecturales (aucun composant Redis ou PostgreSQL n'étant disponible), la protection anti-rejeu en mémoire seule était insuffisante face aux architectures multi-workers ou aux redémarrages serveur.

1. **Migration & Schéma SQLite :**
   - Création de la migration `migration_039_consumed_tokens.py` créant la table :
     ```sql
     CREATE TABLE IF NOT EXISTS consumed_tokens (
         jti TEXT PRIMARY KEY,
         consumed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
     );
     ```
2. **Interface & Repository :**
   - `ConsumedTokenRepository` (`src/identity/application/interfaces/consumed_token_repository.py`) avec `consume(jti: str) -> bool`.
   - `SQLiteConsumedTokenRepository` (`src/infrastructure/repositories/sqlite_consumed_token_repository.py`) utilisant un test-and-set atomique SQLite :
     ```sql
     INSERT OR IGNORE INTO consumed_tokens (jti) VALUES (?);
     ```
     La requête retourne `True` si et seulement si `cursor.rowcount == 1`. En cas de collision concurrente ou de rejeu ultérieur, `rowcount == 0` et l'opération retourne `False`.
3. **Comportement :**
   - Si un jeton est rejoué, le use case `SelectTenantContext` et la route HTTP retournent immédiatement une erreur `HTTP 409 Conflict` ("Ce jeton de selection a deja ete consomme.").
   - Les jetons consommés restent enregistrés même si le serveur redémarre ou si deux requêtes concurrentes frappent deux workers distincts au même instant.

---

### 2.3 Protection réseau et Rate Limiting

1. **Anti-spoofing `X-Forwarded-For` :**
   - La fonction `get_client_ip(request: Request)` n'accepte la valeur de l'en-tête `X-Forwarded-For` que si l'IP client directe appartient à l'ensemble `_TRUSTED_PROXIES = {"127.0.0.1", "::1", "localhost", "testclient"}`. Tout client direct non approuvé se voit attribuer son IP réelle, empêchant tout contournement du limiteur de requêtes.
2. **Politiques de limitation appliquées :**
   - `POST /auth/register-establishment` : Limité à **5 requêtes par tranche de 15 minutes par IP**. En-tête `Retry-After: <secondes>` fourni en cas de dépassement (HTTP 429).
   - `POST /auth/login` : Double barrière :
     - 15 tentatives / minute par IP (anti-déni de service distribué).
     - 5 tentatives / minute par couple `(IP, email)` (anti brute-force ciblé), réinitialisé en cas d'authentification réussie.
   - `POST /auth/select-tenant` : Limité à **10 requêtes par minute par IP** (HTTP 429 avec `Retry-After`).

---

### 2.4 Endpoints HTTP implémentés dans `src/presentation/api/routes/auth.py`

1. **`POST /auth/register-establishment` :**
   - Validation de schéma Pydantic (`extra="forbid"`).
   - Rate limiting IP.
   - Délégation au use case `RegisterEstablishment`.
   - Codes retournés : `201 Created`, `400 Bad Request`, `409 Conflict` (si l'email existe déjà), `422 Unprocessable Content`, `429 Too Many Requests`.
2. **`POST /auth/login` :**
   - Accepte `tenant_id` optionnel.
   - Mono-tenant sans tenant_id : authentifie et émet directement `access_token` et `refresh_token` (`tenant_selection_required=False`).
   - Multi-tenant sans tenant_id : émet `tenant_selection_token`, liste les `available_tenants` et positionne `tenant_selection_required=True` (sans tokens d'accès).
   - Mono ou multi-tenant avec `tenant_id` explicite : authentifie directement si l'appartenance existe.
   - Respecte intégralement le 2FA (`two_factor_required=True`, `two_factor_token`).
3. **`POST /auth/select-tenant` :**
   - Consomme le `tenant_selection_token` via `ConsumedTokenRepository`.
   - Vérifie la signature cryptographique du jeton, le type `tenant_selection`, et l'expiration.
   - Vérifie côté serveur l'appartenance de l'utilisateur au tenant demandé.
   - Émet les tokens de session (`access_token` et `refresh_token`).
   - Codes retournés : `200 OK`, `400 Bad Request` (jeton expiré/invalide), `403 Forbidden` (adhésion refusée), `409 Conflict` (jeton déjà consommé), `429 Too Many Requests`.

---

## 3. Suite de tests d'intégration HTTP (`tests/integration/test_auth_self_service_http.py`)

Une suite de tests d'intégration dédiée a été conçue et exécutée via FastAPI `TestClient`, couvrant les 15 scénarios obligatoires :

| N° | Scénario testé | Statut | Résultat |
|:---|:---|:---:|:---|
| 1 | Inscription valide d'un établissement (`POST /auth/register-establishment`) | **PASS** | HTTP 201 Created, tenant et premier admin créés, slug auto-généré |
| 2 | Inscription avec email dupliqué | **PASS** | HTTP 409 Conflict avec message explicite |
| 3 | Données d'inscription invalides ou injection de champs interdits (`role`) | **PASS** | HTTP 400 ou 422 Unprocessable Content (rejet `extra="forbid"`) |
| 4 | Rate limiting sur l'inscription (6e tentative dans la fenêtre) | **PASS** | HTTP 429 Too Many Requests avec en-tête `Retry-After > 0` |
| 5 | Connexion mono-tenant sans fournir `tenant_id` | **PASS** | HTTP 200 OK, `authenticated=True`, tokens d'accès délivrés |
| 6 | Connexion multi-tenant sans fournir `tenant_id` | **PASS** | HTTP 200 OK, `tenant_selection_required=True`, jeton temporaire et liste d'établissements |
| 7 | Sélection autorisée d'un établissement (`POST /auth/select-tenant`) | **PASS** | HTTP 200 OK, `authenticated=True`, tokens d'accès délivrés pour le tenant choisi |
| 8 | Sélection d'un établissement auquel l'utilisateur n'appartient pas | **PASS** | HTTP 403 Forbidden ("Acces tenant refuse.") |
| 9 | Sélection avec un jeton expiré | **PASS** | HTTP 400 Bad Request ("Le jeton de selection est invalide ou expire.") |
| 10 | Rejeu d'un jeton de sélection déjà consommé | **PASS** | HTTP 409 Conflict ("Ce jeton de selection a deja ete consomme.") |
| 11 | Deux requêtes concurrentes consommant le même jeton au même instant | **PASS** | Concurrence `ThreadPoolExecutor` : exactement un HTTP 200 et un HTTP 409 |
| 12 | Persistance anti-rejeu après redémarrage du processus | **PASS** | Rejet HTTP 409 sur une seconde instance container connectée à la même base |
| 13 | Connexion et sélection avec utilisateur ayant activé le 2FA | **PASS** | Préservation intégrale de `two_factor_required=True` et `two_factor_token` |
| 14 | Non-régression des flux `/auth/login`, `/auth/refresh`, `/auth/logout` | **PASS** | Révocation effective du refresh token lors du logout |
| 15 | Isolation multi-tenant stricte (cross-tenant prevented) | **PASS** | Tentative de connexion sur un tenant tiers refusée en HTTP 403 Forbidden |

**Résultat d'exécution pytest :**
```text
============================= 15 passed in 4.23s ==============================
```

Ensemble des tests unitaires Identity & Tenancy :
```text
127 passed in 4.63s
```

---

## 4. Validation qualité du code

- **Linter Ruff :**
  ```bash
  .\.venv\Scripts\ruff.exe check src/presentation/api/routes/auth.py src/presentation/api/container.py src/presentation/api/dependencies/__init__.py tests/integration/test_auth_self_service_http.py
  ```
  *Résultat : 0 erreur, code 100% conforme.*

- **Type Checker Mypy :**
  ```bash
  .\.venv\Scripts\mypy.exe src/presentation/api/routes/auth.py src/presentation/api/container.py src/presentation/api/dependencies/__init__.py
  ```
  *Résultat : Success: no issues found in 3 source files.*

---

## 5. Documentation Frontend mise à jour

Le document `frontend/docs/CONTRATS_API_MANQUANTS.md` a été mis à jour avec :
- Les spécifications précises des 3 endpoints (`/auth/register-establishment`, `/auth/login`, `/auth/select-tenant`).
- Les interfaces TypeScript correspondantes pour les requêtes et réponses.
- Les codes d'erreurs et en-têtes HTTP (`Retry-After`).

---

## 6. Prochaine étape : Étape 5 (Composants et pages Frontend)

Conformément aux directives, **aucune modification du code frontend pour l'Étape 5 n'a été entreprise** dans ce tour.

L'Étape 5 consistera à :
1. Créer la page d'inscription `/register-establishment` avec le formulaire réactif (nom de l'établissement, responsable, email, mot de passe).
2. Adapter la page de connexion existante (`/login`) pour rendre le champ "Identifiant établissement" optionnel.
3. Intégrer la boîte de dialogue modale de sélection d'établissement en cas de compte rattaché à plusieurs écoles (`tenant_selection_required: true`).
4. Couvrir ces interfaces avec les tests unitaires frontend (React Testing Library / Vitest).

**L'Étape 5 sera démarrée dès votre approbation de ce rapport.**
