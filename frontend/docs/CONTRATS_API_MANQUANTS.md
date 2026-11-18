# Contrats API — écarts frontend (mise à jour 2026-11-09)

| Besoin | État actuel | Impact frontend |
|---|---|---|
| Déconnexion avec révocation du refresh token | `POST /auth/logout` + `logout()` FE | Déconnexion locale + révocation refresh |
| Création / modification d'un élève | `POST /students`, `PUT /students/{id}` (ADMIN/DIRECTION) | Création OK ; brancher l’édition FE sur PUT |
| Recherche d'élève pour les rôles financiers | `GET /students` ouvert aux rôles finance | Choix d’élève pour paiements possible |
| Liste globale des paiements | `GET /billing/payments` (pagination + filtres) | Brancher l’écran journal global |
| Arriérés | `GET /billing/arrears` | Brancher la vue impayés |
| Dashboard direction finance | `GET /dashboard/direction` | Remplacer l’agrégation locale pour les indicateurs finance |
| Rôles PROF et PARENT | Toujours absents côté backend productif | Portails enseignant / parent bloqués (décisions métier) |

---

## Inscription & Provisioning autonome d'établissement (Phase 2 — Étape 4 Terminée)

| Besoin | État actuel | Impact frontend (Étape 5) |
|---|---|---|
| Inscription autonome d'un établissement | Endpoint `POST /auth/register-establishment` validé et testé | Formulaire `RegisterEstablishmentPage` avec redirection / confirmation |
| Connexion sans `tenant_id` obligatoire | Endpoint `POST /auth/login` mis à jour (support `tenant_id` optionnel) | Champ "Identifiant établissement" optionnel sur `LoginPage` |
| Sélection de tenant pour compte multi-établissements | Endpoint `POST /auth/select-tenant` validé et testé | Modal / dialogue de choix d'établissement lorsque `tenant_selection_required: true` |

---

### 1. Spécification `POST /auth/register-establishment`

Permet à un responsable d'inscrire son établissement et de créer automatiquement le tenant, le compte utilisateur et l'appartenance avec le rôle `ADMIN`.

- **URL :** `/auth/register-establishment`
- **Méthode :** `POST`
- **Authentification requise :** Non (endpoint public)
- **Rate Limiting :** 5 requêtes / 15 minutes par adresse IP (`Retry-After` fourni en cas de dépassement)
- **Protection injection de privilèges :** Pydantic `extra="forbid"` (rejet 422 si des champs non prévus sont injectés)

#### Corps de la requête (`application/json`)

```typescript
export interface RegisterEstablishmentRequest {
  school_name: string; // min: 2, max: 200
  admin_name: string;  // min: 2, max: 150
  email: string;       // min: 5, max: 255 (format email valide)
  password: string;    // min: 8, max: 128
}
```

#### Réponses HTTP

- **201 Created :**
  ```typescript
  export interface RegisterEstablishmentResponse {
    tenant_id: string;   // UUID
    tenant_name: string;
    tenant_slug: string;
    user_id: string;     // UUID
    admin_name: string;
    email: string;
    role: string;        // Toujours "ADMIN"
  }
  ```
- **400 Bad Request :** Règles métier non respectées (mot de passe invalide, nom vide, format email rejeté par le domaine).
- **409 Conflict :** L'adresse email est déjà enregistrée sur la plateforme.
- **422 Unprocessable Entity :** Validation de schéma Pydantic en échec (champs obligatoires manquants, longueurs non conformes, ou champs interdits transmis).
- **429 Too Many Requests :** Limite de requêtes dépassée par IP. En-tête `Retry-After: <secondes>` présent.

---

### 2. Spécification `POST /auth/login` (Évolué)

Supporte la connexion avec ou sans `tenant_id`, la détection mono-tenant vs multi-tenant, et le 2FA.

- **URL :** `/auth/login`
- **Méthode :** `POST`
- **Authentification requise :** Non
- **Rate Limiting :** 
  - 15 tentatives / minute par IP
  - 5 tentatives / minute par couple `(IP, email)` (réinitialisé en cas de succès)
- **Protection :** Pydantic `extra="forbid"`

#### Corps de la requête (`application/json`)

```typescript
export interface LoginUserRequest {
  email: string;
  password: string;
  tenant_id?: string | null; // UUID optionnel
}
```

#### Réponses HTTP

- **200 OK — Scénario A : Mono-tenant ou tenant_id fourni (accès direct) :**
  ```json
  {
    "authenticated": true,
    "two_factor_required": false,
    "two_factor_token": null,
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "email": "user@edunova.com",
    "tenant_selection_required": false,
    "tenant_selection_token": null,
    "available_tenants": []
  }
  ```
- **200 OK — Scénario B : Multi-tenant sans tenant_id (sélection requise) :**
  ```json
  {
    "authenticated": false,
    "two_factor_required": false,
    "two_factor_token": null,
    "access_token": null,
    "refresh_token": null,
    "email": "user@edunova.com",
    "tenant_selection_required": true,
    "tenant_selection_token": "eyJhbGciOi...",
    "available_tenants": [
      {
        "tenant_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "tenant_name": "Lycée d'Excellence",
        "tenant_slug": "lycee-dexcellence",
        "role": "ADMIN"
      },
      {
        "tenant_id": "1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed",
        "tenant_name": "Collège Moderne",
        "tenant_slug": "college-moderne",
        "role": "TEACHER"
      }
    ]
  }
  ```
- **401 Unauthorized :** Identifiants invalides ou compte inactif.
- **403 Forbidden :** L'utilisateur n'appartient pas au tenant demandé ou aucun tenant actif.
- **429 Too Many Requests :** Limite de tentatives atteinte. En-tête `Retry-After` inclus.

---

### 3. Spécification `POST /auth/select-tenant`

Permet de finaliser l'authentification en échangeant un `tenant_selection_token` à usage unique contre les jetons d'accès du tenant sélectionné.

- **URL :** `/auth/select-tenant`
- **Méthode :** `POST`
- **Authentification requise :** Non (sécurisé par le `tenant_selection_token`)
- **Rate Limiting :** 10 requêtes / minute par IP
- **Protection anti-rejeu :** Table SQLite `consumed_tokens` avec `jti` unique (résistant aux concurrences multi-workers et aux redémarrages de l'application).
- **Protection :** Pydantic `extra="forbid"`

#### Corps de la requête (`application/json`)

```typescript
export interface SelectTenantRequest {
  tenant_selection_token: string;
  tenant_id: string; // UUID
}
```

#### Réponses HTTP

- **200 OK :**
  ```json
  {
    "authenticated": true,
    "two_factor_required": false,
    "two_factor_token": null,
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "email": "user@edunova.com",
    "tenant_selection_required": false,
    "tenant_selection_token": null,
    "available_tenants": []
  }
  ```
- **400 Bad Request :** Jeton expiré, altéré, ou type de jeton incorrect (différent de `tenant_selection`).
- **403 Forbidden :** L'utilisateur ne possède pas d'adhésion active au tenant spécifié.
- **409 Conflict :** Le jeton de sélection a déjà été consommé (rejeu détecté).
- **429 Too Many Requests :** Limite de requêtes atteinte. En-tête `Retry-After` inclus.
