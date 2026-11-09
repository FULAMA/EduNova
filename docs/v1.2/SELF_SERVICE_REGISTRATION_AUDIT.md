# EduNova V1.2 — Audit Architectural : Self-Service Registration & Tenant Provisioning

**Date d'audit :** 8 novembre 2026  
**Auteur :** Antigravity (Advanced Agentic Coding)  
**Périmètre :** Inscription autonome des établissements, provisionnement multi-tenant, cycle d'authentification et compatibilité AUTH-HARDENING.  
**Statut :** AUDITÉ — PRÊT POUR VALIDATION

---

## 1. Introduction et Contexte

Dans le cadre de l'évolution SaaS d'EduNova pour les établissements scolaires en RDC, l'accueil d'un nouvel établissement doit pouvoir se faire en libre-service (*self-service registration*) sans intervention manuelle de l'administrateur de plateforme.

Lorsqu'un administrateur d'école s'inscrit :
1. Un **Tenant** (établissement) doit être créé avec son nom et son slug unique.
2. Un compte **User** (administrateur de l'école) doit être créé avec des identifiants sécurisés (Argon2id).
3. Une relation **Membership** doit associer de manière stricte cet utilisateur au tenant avec le rôle `ADMIN`.
4. L'opération doit être **strictement atomique** : aucun tenant ou utilisateur orphelin ne doit pouvoir subsister en cas d'échec partiel.
5. Le flux de connexion doit être fluidifié pour éviter d'imposer la saisie manuelle d'un UUID complexe (`tenant_id`) lorsque l'utilisateur n'appartient qu'à un seul établissement.

Cet audit analyse l'existant documentaire, métier, applicatif, persistance et sécurité, et répertorie les écarts techniques à combler.

---

## 2. Conformité aux Décisions Métier et DDD

### 2.1. Décisions Métier du Registre (`REGISTRE_DECISIONS_METIER_EDUNOVA.md`)

| Réf. Décision | Intitulé & Règle | Statut | Impact sur le Self-Service |
|---|---|---|---|
| **Décision 13** | **Permissions par rôle** : Socle de sécurité obligatoire, contrôle de portée et isolation des tenants. L'accès administrateur est restreint aux données de son propre établissement. | `VALIDÉE` | Le premier utilisateur reçoit le rôle `ADMIN` cantonné à son tenant via la table `memberships`. |
| **Décision 14** | **Comptes multi-rôles & multi-contextes** : Un compte n'a qu'un rôle ou contexte actif à la fois. Le changement de contexte est contrôlé ; pas de cumul implicite de permissions. | `VALIDÉE` | Si un utilisateur a plusieurs rattachements (`memberships`), le login sans `tenant_id` doit exiger une sélection explicite de l'établissement actif pour éviter toute ambiguïté contextuelle. |
| **Décision 32** | **Isolation multi-tenant** : Contexte et autorisation côté serveur, requêtes limitées au `tenant_id`, tests négatifs inter-tenants obligatoires. | `VALIDÉE` | Tout accès sans `membership` actif sur le tenant ciblé doit retourner une interdiction formelle (`HTTP 403 Forbidden`). |
| **FIN-ROLE-01** | Portée des opérations financières et administratives cantonnée aux acteurs affectés explicitement au tenant. | `VALIDÉE` | L'association `Membership(user_id, tenant_id, role='ADMIN')` constitue la clé de voûte de toute autorisation ultérieure. |

### 2.2. Modèle DDD Actuel

Le projet applique une séparation par contextes délimités (*Bounded Contexts*) :
- **Bounded Context `identity`** : Gère les identités globales (`User`), les identifiants, le hachage des mots de passe (Argon2id), le 2FA (TOTP) et l'émission des tokens JWT.
- **Bounded Context `tenancy`** : Gère les établissements (`Tenant`) et les affiliations (`Membership`).
- **Bounded Context `academic`** : Gère les cycles, classes, options, élèves et années scolaires (`academic_years`).

---

## 3. Audit des Modules Existants

### 3.1. Entités et Interfaces du Domaine

#### A. Entité `User` (`src/identity/domain/entities/user.py`)
```python
@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    role: str
    is_active: bool = True
    two_factor_enabled: bool = False
    two_factor_secret: str | None = None
```
- **Constat :** L'entité `User` actuelle ne stocke **aucun champ de nom** (`full_name`, `first_name`, `last_name`). Elle porte uniquement les données d'authentification et un rôle générique.
- **Écart :** Pour l'inscription d'un établissement, la demande exige de recueillir le "Nom complet de l'administrateur". Deux choix d'architecture sont analysés :
  - *Option 1 :* Étendre `User` avec un champ optionnel `full_name: str | None = None` (avec migration de schéma).
  - *Option 2 :* Enregistrer le nom complet dans les métadonnées de création / journal d'audit et créer une table/profil d'administrateur sans casser les entités existantes.
  - *Recommandation :* Option 1 retenue avec rétrocompatibilité (`full_name: str | None = None` dans `User` et ajout d'une colonne `full_name TEXT` en base SQLite).

#### B. Entité `Tenant` (`src/tenancy/domain/entities/tenant.py`)
```python
@dataclass(frozen=True)
class Tenant:
    id: UUID
    name: str
    slug: str
    active: bool = True
```
- **Constat :** L'entité est immutable (`frozen=True`) et valide que `name` et `slug` ne sont pas vides.
- **Conformité :** Conforme aux attentes du self-service.

#### C. Entité `Membership` (`src/tenancy/domain/entities/membership.py`)
```python
@dataclass(frozen=True)
class Membership:
    id: UUID
    user_id: UUID
    tenant_id: UUID
    role: str
    active: bool = True
```
- **Constat :** Lie de manière univoque un utilisateur à un tenant avec un rôle donné (`ADMIN`).
- **Conformité :** Conforme aux attentes.

---

### 3.2. Repositories et Implémentations

#### A. `TenantRepository` (`src/tenancy/application/interfaces/tenant_repository.py`)
```python
class TenantRepository(ABC):
    @abstractmethod
    def find_by_id(self, tenant_id: UUID) -> Tenant | None:
        raise NotImplementedError
```
- **Écart Majeur :** L'interface actuelle ne fournit **que** `find_by_id`.
  - Manque la méthode `save(self, tenant: Tenant) -> None`.
  - Manque la méthode `find_by_slug(self, slug: str) -> Tenant | None`.
- **Impact :** `SQLiteTenantRepository` n'implémente actuellement que la lecture par `id`. Il est impossible d'insérer un nouveau tenant sans enrichir ce repository.

#### B. `MembershipRepository` (`src/tenancy/application/interfaces/membership_repository.py`)
- Fournit déjà :
  - `save(self, membership: Membership) -> None`
  - `find_by_id(self, membership_id: UUID) -> Membership | None`
  - `find_by_user(self, user_id: UUID) -> list[Membership]`
  - `find_by_user_and_tenant(self, user_id: UUID, tenant_id: UUID) -> Membership | None`
- `SQLiteMembershipRepository` implémente déjà l'insertion et les requêtes nécessaires.

#### C. `UserRepository` (`src/identity/application/interfaces/user_repository.py`)
- Fournit :
  - `save(self, user: User) -> None`
  - `find_by_id(self, user_id: UUID) -> User | None`
  - `find_by_email(self, email: str) -> User | None`
- `SQLiteUserRepository` gère déjà l'insertion et la mise à jour par `id` ou `email`.

---

## 4. Audit de la Base de Données et des Migrations

### 4.1. Schéma des Tables Concernees

1. **Table `tenants`** (`migration_013_memberships.py`) :
   ```sql
   CREATE TABLE IF NOT EXISTS tenants (
       id TEXT PRIMARY KEY,
       name TEXT NOT NULL,
       slug TEXT NOT NULL UNIQUE,
       active INTEGER NOT NULL
   );
   ```
   - Contrainte `UNIQUE` sur `slug` : toute collision lève une violation de contrainte SQLite.
   
2. **Table `users`** (`src/infrastructure/persistence/database.py`) :
   ```sql
   CREATE TABLE IF NOT EXISTS users (
       id TEXT PRIMARY KEY,
       email TEXT NOT NULL UNIQUE,
       password_hash TEXT NOT NULL,
       role TEXT NOT NULL,
       is_active INTEGER NOT NULL,
       two_factor_enabled INTEGER NOT NULL,
       two_factor_secret TEXT
   );
   ```
   - Contrainte `UNIQUE` sur `email` : un email ne peut être enregistré deux fois.
   
3. **Table `memberships`** (`migration_013_memberships.py`) :
   ```sql
   CREATE TABLE IF NOT EXISTS memberships (
       id TEXT PRIMARY KEY,
       user_id TEXT NOT NULL,
       tenant_id TEXT NOT NULL,
       role TEXT NOT NULL,
       active INTEGER NOT NULL,
       UNIQUE (user_id, tenant_id),
       FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
       FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
   );
   ```
   - Clés étrangères actives avec cascade.

4. **Table `academic_years`** (`migration_020_school_years_assignments.py`) :
   ```sql
   CREATE TABLE IF NOT EXISTS academic_years (
       id TEXT NOT NULL,
       tenant_id TEXT NOT NULL,
       label TEXT NOT NULL,
       start_date TEXT NOT NULL,
       end_date TEXT NOT NULL,
       status TEXT NOT NULL,
       PRIMARY KEY (tenant_id, id),
       UNIQUE (tenant_id, label)
   );
   ```

### 4.2. Transactionnalité et Rollback
- Dans les repositories actuels (`SQLiteUserRepository`, `SQLiteTenantRepository`, `SQLiteMembershipRepository`), chaque méthode effectue son propre `with self._database.connect() as connection:`.
- **Risque d'intégrité identifié :** Si un use case orchestre séquentiellement `tenant_repo.save(tenant)`, puis `user_repo.save(user)`, puis `membership_repo.save(membership)`, un plantage à l'étape 3 laisserait un tenant et un utilisateur orphelins en base.
- **Exigence d'industrialisation :** Le provisioning d'établissement doit s'exécuter dans un bloc transactionnel atomique (`BEGIN TRANSACTION` ... `COMMIT` / `ROLLBACK`).

---

## 5. Audit des Endpoints API Existants

### 5.1. Inscription Actuelle (`POST /auth/register`)
- **Fichier :** `src/presentation/api/routes/auth.py`
- **Comportement actuel :**
  ```python
  application_request = ApplicationRegisterUserRequest(
      email=request.email,
      password=request.password,
      role="STUDENT",  # Rôle codé en dur pour inscription publique individuelle
  )
  ```
- **Constat :** `/auth/register` est expressément conçu pour l'inscription d'élèves individuels sans tenant. Il ne peut et ne doit pas être détourné pour provisionner une école.
- **Décision d'architecture :** Créer un endpoint dédié `POST /auth/register-establishment` pour le provisioning autonome d'établissement scolaire.

### 5.2. Connexion Actuelle (`POST /auth/login`)
- **Fichier :** `src/presentation/api/routes/auth.py` et `src/identity/application/use_cases/login_user.py`
- **Contrat actuel :**
  - Le schéma Pydantic `LoginUserRequest` exige obligatoirement `tenant_id: UUID`.
  - Le frontend `LoginPage.tsx` force la saisie d'un UUID sous peine d'erreur de formulaire.
- **Problème UX / SaaS :**
  - Les utilisateurs finaux ne connaissent pas leur `tenant_id` (UUID 128-bit).
  - Dans un SaaS moderne, l'utilisateur s'identifie par son email et mot de passe.
  - Si l'utilisateur appartient à un seul tenant actif, le backend doit automatiquement identifier ce tenant.
  - Si l'utilisateur appartient à plusieurs tenants actifs, le backend doit renvoyer la liste des tenants disponibles pour permettre à l'utilisateur de sélectionner son contexte de travail.
  - La compatibilité avec l'envoi explicite d'un `tenant_id` doit être conservée à 100 %.

---

## 6. Audit de la Sécurité et Compatibilité AUTH-HARDENING (Phase 1)

Les protections de sécurité renforcées lors de la Phase 1 doivent être strictement préservées :

1. **Rate Limiting (`InMemoryRateLimiter`) :**
   - L'endpoint `/auth/register` dispose d'un rate limit IP de 5 requêtes par 60 secondes.
   - Le nouvel endpoint `/auth/register-establishment` devra appliquer un rate limit strict (ex: 3 inscriptions par IP par heure, ou 5 par fenêtre de 15 minutes) avec réponse `HTTP 429 Too Many Requests` et en-tête `Retry-After`.
2. **Anti-Énumération et Attaques Temporelles :**
   - En cas d'email déjà enregistré, l'API ne doit pas permettre de balayer les emails scolaires sans restriction.
   - Les réponses d'erreur doivent être calibrées sans fuiter d'informations sensibles sur l'infrastructure interne.
3. **Complexité des Mots de Passe & Argon2id :**
   - Le mot de passe de l'administrateur doit obligatoirement respecter les règles de robustesse (min 8 caractères, mix de classes de caractères).
   - Le hachage utilise Argon2id via `PasswordHasher`.
4. **Validation de l'Unicité du Slug :**
   - Le slug doit être nettoyé (caractères alphanumériques minuscules et tirets).
   - En cas de collision (ex: deux écoles portant le nom "Institut Lumumba"), l'algorithme doit générer un suffixe déterministe ou aléatoire court (ex: `institut-lumumba-4a2f`) pour garantir le succès de l'inscription tout en préservant l'unicité.

---

## 7. Audit Frontend

### 7.1. État Actuel de l'Interface
- `frontend/src/features/auth/pages/LoginPage.tsx` :
  - Champs présents : `email`, `password`, `tenantId`.
  - Validation stricte regex sur `tenantId` (UUID requis).
  - Aucun composant ou page d'inscription n'existe actuellement dans le frontend (absence de `RegisterPage` ou `RegisterEstablishmentPage`).
- `frontend/src/app/router/routes.tsx` :
  - Seule la route `/login` est exposée publiquement.
  - Il n'existe pas de route `/register` ou `/register-establishment`.

### 7.2. Besoins Frontend pour le Self-Service
- Création d'une page `RegisterEstablishmentPage.tsx` avec les champs :
  - Nom de l'établissement
  - Nom complet du responsable / administrateur
  - Email professionnel
  - Mot de passe fort
  - Confirmation du mot de passe
- Gestion d'état claire : saisie, validation temps réel, indicateur de chargement, affichage d'erreur.
- Écran ou modal de succès post-création affichant le `tenant_id` et le `slug` générés avec bouton "Copier", et proposition de redirection automatique vers `/login` avec l'email pré-renseigné.
- Allègement de `LoginPage.tsx` pour rendre le champ `tenant_id` optionnel ou masqué en mode par défaut.

---

## 8. Synthèse des Écarts et Risques

| Élément | État Actuel | État Requis | Risque / Criticité |
|---|---|---|---|
| **`TenantRepository`** | Seule `find_by_id` existe | Ajouter `save(tenant)` et `find_by_slug(slug)` | **Bloquant** pour la création |
| **`SQLiteTenantRepository`** | Lecture seule | Implémenter l'écriture SQL | **Bloquant** pour la persistance |
| **Transactionnalité** | Opérations unitaires isolées | Transaction atomique multi-entités | **Élevé** (risque d'orphelins) |
| **Endpoint Inscription** | `/auth/register` (STUDENT seul) | `/auth/register-establishment` dédié | **Bloquant** pour le self-service |
| **Flux de Connexion** | `tenant_id` obligatoire | `tenant_id` optionnel avec auto-résolution | **Moyen / UX** |
| **Attribut Nom Administrateur** | Absent de `User` | Stockage nom admin | **Moyen** |
| **Composant UI Inscription** | Inexistant | `RegisterEstablishmentPage.tsx` | **Bloquant** pour le parcours utilisateur |
| **Rate Limiting Inscription** | Seul `/auth/register` est bridé | Appliquer au nouveau endpoint | **Sécurité** |

---

## 9. Conclusion de l'Audit

L'architecture existante d'EduNova (Clean Architecture, Bounded Contexts étanches, tables `tenants` et `memberships` préexistantes) est saine et parfaitement adaptée pour accueillir le self-service registration. 

Les compléments à apporter se situent au niveau de l'orchestration applicative (nouveau Use Case `RegisterEstablishment`), de la persistance (méthodes `save` et `find_by_slug` sur `TenantRepository`), de la gestion transactionnelle unifiée, de l'évolution souple du `LoginUser`, et de la création de l'interface utilisateur dédiée.

Le document d'accompagnement `docs/v1.2/SELF_SERVICE_REGISTRATION_PLAN.md` détaille l'ensemble du plan technique d'implémentation.
