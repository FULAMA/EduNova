# EduNova V1.2 — Rapport d'Exécution : Étape 1 (Persistance et Interfaces Tenancy)

**Date d'exécution :** 8 novembre 2026  
**Auteur :** Antigravity (Advanced Agentic Coding)  
**Lot :** Self-Service Registration & Tenant Provisioning — Étape 1  
**Statut :** RÉALISÉ — 100 % DES TESTS VALIDÉS — PRÊT POUR VALIDATION

---

## 1. Synthèse des Travaux Réalisés

L'Étape 1 prépare le socle de persistance et les abstractions de domaine/infrastructure nécessaires à la création autonome d'établissements dans EduNova. 

Toutes les exigences fixées ont été rigoureusement satisfaites :
1. Extension de `TenantRepository` et de son implémentation `SQLiteTenantRepository` avec les méthodes `save(tenant)` et `find_by_slug(slug)`.
2. Création d'un service de domaine dédié `TenantSlugService` pour la normalisation ASCII URL-safe et la gestion déterministe des collisions.
3. Alignement du modèle `Membership` pour conférer le rôle `ADMIN` au premier utilisateur sans introduire de rôle global arbitraire dans `User`.
4. Mise en place d'une persistance transactionnelle atomique via `EstablishmentProvisioningUnitOfWork` et `SQLiteEstablishmentProvisioningUnitOfWork`, garantissant le rollback intégral (zéro orphelin) en cas d'erreur.
5. Création et validation d'une suite de 16 tests unitaires ciblés sur base SQLite temporaire, avec non-régression validée sur les 1066 tests unitaires du projet, et conformité stricte aux linters Ruff et Mypy.

---

## 2. Fichiers Créés et Modifiés

### 2.1. Fichiers Modifiés
* `src/tenancy/application/interfaces/tenant_repository.py` : Ajout des méthodes abstraites `save(tenant)` et `find_by_slug(slug)`.
* `src/tenancy/infrastructure/repositories/sqlite_tenant_repository.py` : Implémentation SQL des méthodes `save`, `find_by_slug` et support de transaction via argument optionnel `connection`.
* `src/tenancy/infrastructure/repositories/sqlite_membership_repository.py` : Ajout du support de transaction partagée via `connection: sqlite3.Connection | None = None` dans `save`.
* `src/infrastructure/repositories/sqlite_user_repository.py` : Ajout du support de transaction partagée via `connection: sqlite3.Connection | None = None` dans `save`.
* `tests/unit/infrastructure/repositories/test_sqlite_tenant_repository.py` : Refonte et enrichissement des tests de persistance tenant (recherche par ID, recherche par slug, refus des doublons).

### 2.2. Fichiers Créés
* `src/tenancy/domain/services/tenant_slug_service.py` : Service de domaine pour la normalisation de nom d'établissement et l'évitement des collisions de slugs.
* `src/tenancy/application/interfaces/establishment_provisioning_unit_of_work.py` : Contrat applicatif de l'Unit of Work pour le provisionnement atomique d'établissement.
* `src/tenancy/infrastructure/persistence/sqlite_establishment_provisioning_uow.py` : Implémentation SQLite de l'Unit of Work orchestrant `Tenant`, `User` et `Membership` dans un bloc `with connection:` unique.
* `tests/unit/tenancy/domain/services/test_tenant_slug_service.py` : Tests unitaires de normalisation et de collision de slug.
* `tests/unit/tenancy/infrastructure/persistence/test_sqlite_establishment_provisioning_uow.py` : Tests d'intégrité transactionnelle, atomicité, rollback sur violation de contrainte et cascade relationnelle.

---

## 3. Détail des Interfaces et Composants

### 3.1. `TenantRepository`
```python
class TenantRepository(ABC):
    @abstractmethod
    def save(self, tenant: Tenant) -> None: ...

    @abstractmethod
    def find_by_id(self, tenant_id: UUID) -> Tenant | None: ...

    @abstractmethod
    def find_by_slug(self, slug: str) -> Tenant | None: ...
```

### 3.2. `TenantSlugService` (Domaine)
* **Normalisation :**
  * Décomposition Unicode (NFKD) et élimination des diacritiques (accents français).
  * Nettoyage des caractères non alphanumériques transformés en `-`.
  * Suppression des tirets consécutifs et aux extrémités.
  * Repli de sécurité vers `"etablissement"` si la chaîne résultante est vide.
* **Gestion des collisions :**
  * Vérification via `is_slug_taken: Callable[[str], bool]`.
  * Incrémentation séquentielle (`-2`, `-3`...) puis suffixe hexadécimal si saturation.

### 3.3. `EstablishmentProvisioningUnitOfWork` & Implémentation SQLite
* **Principe :** Une seule et unique connexion SQLite est ouverte pour l'ensemble du cycle de provisionnement.
* **Gestion transactionnelle :** Utilisation du context manager `with connection:` natif de Python :
  ```python
  with self._database.connect() as connection:
      with connection:
          self._tenant_repo.save(tenant, connection=connection)
          self._user_repo.save(user, connection=connection)
          self._membership_repo.save(membership, connection=connection)
  ```
* **Garantie d'atomicité :** Si une `sqlite3.IntegrityError` (email doublon, slug doublon, clé étrangère manquante) ou toute exception survient à n'importe quel moment, SQLite applique immédiatement un `ROLLBACK`. Aucune ligne partielle n'est écrite en base.

---

## 4. Contraintes de Persistance et Intégrité

| Contrainte | Niveau | Règle appliquée | Validation |
|---|---|---|---|
| **Unicité du Slug** | Base de données | `slug TEXT NOT NULL UNIQUE` sur table `tenants` | Validé par `test_duplicate_slug_raises_integrity_error` |
| **Unicité de l'ID Tenant** | Base de données | `id TEXT PRIMARY KEY` sur table `tenants` | Validé par `test_duplicate_id_raises_integrity_error` |
| **Unicité de l'Email** | Base de données | `email TEXT NOT NULL UNIQUE` sur table `users` | Validé par `test_provision_establishment_rollback_on_user_duplicate_email` |
| **Unicité de l'Affiliation** | Base de données | `UNIQUE(user_id, tenant_id)` sur table `memberships` | Validé par schéma de migration 013 |
| **Clés Étrangères & Cascade** | Base de données | `PRAGMA foreign_keys = ON` avec `ON DELETE CASCADE` | Validé par `test_relational_cascade_on_tenant_deletion` |
| **Rôle Autoritatif** | Application / RBAC | Le rôle `ADMIN` est assigné dans `Membership(user_id, tenant_id, role="ADMIN")` | Conforme aux Décisions 13 et 14 |

---

## 5. Résultats des Tests et Contrôles Qualité

### 5.1. Tests Ciblés Étape 1 (16 tests)
* `tests/unit/infrastructure/repositories/test_sqlite_tenant_repository.py` : 6 tests (save, find by id, find by slug case-insensitive, none on missing, duplicate slug integrity error, duplicate id integrity error) -> **PASSED**.
* `tests/unit/tenancy/domain/services/test_tenant_slug_service.py` : 6 tests (accents, punctuation, empty fallback, unique slug nominal, collision -2, collisions multiples -5) -> **PASSED**.
* `tests/unit/tenancy/infrastructure/persistence/test_sqlite_establishment_provisioning_uow.py` : 4 tests (création atomique complète, rollback sur email doublon, rollback sur erreur membership, suppression cascade tenant) -> **PASSED**.

### 5.2. Non-Régression Globale
* **Suite unitaire complète :** `1066 passed in 26.64s` (100 % de succès).
* **Bases de production :** `edunova.db` et `edunova_dev.db` n'ont pas été touchées.

### 5.3. Contrôles Qualité Statiques
* **Ruff :** `ruff check src/tenancy/ src/infrastructure/repositories/sqlite_user_repository.py` -> **0 erreur**.
* **Mypy :** `mypy src/tenancy/ src/infrastructure/repositories/sqlite_user_repository.py` -> **Success: no issues found in 22 source files**.

---

## 6. Risques Identifiés et Limitations Restantes

1. **Étape 2 (Use Case Applicatif) :**
   * Le use case `RegisterEstablishment` doit encore être développé pour orchestrer la validation des DTOs, la politique de complexité des mots de passe avec `PasswordHasher` (Argon2id), l'appel au `TenantSlugService` et au `EstablishmentProvisioningUnitOfWork`.
2. **Étape 3 (Authentification) :**
   * Le use case `LoginUser` requiert toujours actuellement `tenant_id: UUID`. Son assouplissement avec auto-résolution mono-tenant et sélection multi-tenant sera réalisé lors de l'Étape 3.
3. **Protection HTTP & Rate Limiting :**
   * L'exposition de la route API `POST /auth/register-establishment` avec son rate limit strict sera réalisée lors de l'Étape 4.

---

## 7. Recommandation pour l'Étape 2

Le socle de persistance, de domaine et de transactionnalité étant validé et sécurisé, l'équipe est prête pour la mise en œuvre de :
**Étape 2 : Use Case Applicatif `RegisterEstablishment` et DTOs associés**.
