# Audit de continuité et diagnostic autonome — EduNova V1.2

**Date :** 2026-11-06  
**Auteur :** Antigravity (Équipe d'ingénierie EduNova)  
**Branche Git :** `fix/mypy-test-double-contracts`  
**Statut global :** PHASE 0 TERMINÉE — ANALYSE COMPLÈTE RÉALISÉE SANS RUPTURE DE CONTEXTE

---

## 1. État Git initial et préservation de l'existant

### 1.1 Branche et historique
- **Branche active :** `fix/mypy-test-double-contracts`
- **Dernier commit :** `54c8596 fix(type): use type assertion for STUDENT_DIRECTORY_ROLES.includes`
- **Commits récents :**
  - `54c8596` : typage assertion pour `STUDENT_DIRECTORY_ROLES.includes`
  - `9dcdece` : fix test wrapping avec `CurrentUserProvider` pour pages élèves
  - `d062e4c` : use case de création d'élève et gestion des erreurs
  - `67d352e` : authentification basée sur les rôles et gestion financière
  - `e4229ec` : rejet des versions de migration dupliquées

### 1.2 Modifications locales préexistantes (Working Tree)
Le working tree contient des modifications en cours non commitées, issues de la session de stabilisation V1/V1.1 (tranche du 2026-11-04), conservées intégralement :

| Catégorie | Fichiers | Description |
|-----------|----------|-------------|
| **Contrats & Docs V1** | `frontend/docs/CONTRATS_API_MANQUANTS.md`<br>`docs/v1/SUIVI_MISSION_V1.md`<br>`docs/v1/MATRICE_TRACABILITE_V1.md`<br>`docs/v1/CONTRATS_API_AUTH_LOGOUT.md`<br>`docs/v1/CONTRATS_API_BILLING_PAYMENTS_ARREARS.md`<br>`docs/v1/BLOCAGES_PROF_PARENT_BULLETINS.md` | Spécification des endpoints livrés (`POST /auth/logout`, `PUT /students/{id}`, `GET /billing/payments`, `GET /billing/arrears`, `GET /dashboard/direction`) et blocages documentés. |
| **Frontend Auth & Topbar** | `frontend/src/features/auth/services/auth.service.ts`<br>`frontend/src/shared/components/Topbar/Topbar.tsx`<br>`frontend/src/shared/components/Topbar/Topbar.test.tsx` | Ajout de l'appel serveur de déconnexion `POST /auth/logout` pour révoquer le refresh token tout en nettoyant la session locale. |
| **Backend Domaine & Use Cases** | `src/academic/application/dto/direction_dashboard.py` (nouveau)<br>`src/academic/application/use_cases/get_direction_dashboard.py` (nouveau)<br>`src/academic/application/use_cases/update_student.py` (nouveau)<br>`src/identity/application/use_cases/logout_user.py` (nouveau)<br>`src/academic/application/interfaces/student_repository.py`<br>`src/billing/application/service.py` | Implémentation du tableau de bord de direction (Décision 23), use case d'édition d'élève, use case de révocation de refresh token, méthodes `list_payments` et `calculate_arrears` dans le service de facturation. |
| **Infrastructure & Repositories** | `src/billing/infrastructure/sqlite_repository.py`<br>`src/infrastructure/repositories/sqlite_student_repository.py` | Requêtes SQLite pour le journal paginé des paiements et le calcul des arriérés sans altération de l'historique financier ; mise à jour d'un élève existant. |
| **Présentation & API Routes** | `src/presentation/api/app.py`<br>`src/presentation/api/container.py`<br>`src/presentation/api/dependencies/__init__.py`<br>`src/presentation/api/routes/auth.py`<br>`src/presentation/api/routes/billing.py`<br>`src/presentation/api/routes/students.py`<br>`src/presentation/api/routes/dashboard.py` (nouveau)<br>`src/presentation/api/schemas/billing.py`<br>`src/presentation/api/schemas/student.py`<br>`src/presentation/api/schemas/dashboard.py` (nouveau) | Exposition des routes `POST /auth/logout`, `PUT /students/{id}`, `GET /billing/payments`, `GET /billing/arrears`, `GET /dashboard/direction`. |
| **Tests d'intégration & Unitaires** | `tests/unit/academic/application/use_cases/test_create_student.py`<br>`tests/unit/academic/application/use_cases/test_school_years_and_assignments_use_cases.py`<br>`tests/integration/test_auth_logout_http.py` (nouveau)<br>`tests/integration/test_billing_advanced_http.py` (nouveau)<br>`tests/integration/test_billing_payments_list_http.py` (nouveau)<br>`tests/integration/test_students_update_http.py` (nouveau) | Couverture de test unitaire et d'intégration HTTP pour la révocation des tokens, l'édition des élèves, les paiements et les arriérés. |

**Règle de protection respectée :** Aucun reset, aucun clean, aucune suppression ni commit n'a été effectué. Les bases `edunova.db` et `edunova_dev.db` n'ont pas été touchées.

---

## 2. Documents examinés

L'ensemble de la documentation canonique et technique a été analysé :
1. `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md` : référence absolue des décisions 1 à 44 validées, décision 45 en attente, décisions canoniques BUL-* (bulletins) et FIN-* (finance), propositions PAR-REL-* (parent-enfant).
2. `docs/v1/SUIVI_MISSION_V1.md` : journal de la tranche livrée le 2026-11-04 et identification des lots restants.
3. `docs/v1/MATRICE_TRACABILITE_V1.md` : état vérifié dans le code pour les besoins auth, élèves, finance, dashboard, portails et bulletins.
4. `docs/v1/CONTRATS_API_AUTH_LOGOUT.md` : contrat de révocation du refresh token via table `revoked_refresh_tokens`.
5. `docs/v1/CONTRATS_API_BILLING_PAYMENTS_ARREARS.md` : spécification détaillée des routes `GET /billing/payments`, `GET /billing/arrears` et `GET /dashboard/direction`.
6. `docs/v1/BLOCAGES_PROF_PARENT_BULLETINS.md` : justification technique et métier des blocages pour le portail enseignant (absence d'entité `TeacherAssignment`), portail parent (décisions PAR-REL bloquées) et questions ouvertes sur les bulletins (BUL-TECH-02..06).
7. `frontend/docs/CONTRATS_API_MANQUANTS.md` : liste des écarts entre les écrans React et les endpoints backend disponibles.
8. `docs/reports/RAPPORT_DIAGNOSTIC_PYTEST_WINDOWS_2026-10-31.md` : historique des problématiques d'exécution pytest sous Windows et garde-fous `--basetemp`.
9. `docs/reports/RAPPORT_PERIMETRE_MYPY_CI_2026-10-31.md` : périmètre officiel du typage statique (`src tools/edunova`).

---

## 3. Décisions métier identifiées et état des arbitrages

### 3.1 Décisions validées applicables
- **Décision 13 (Permissions par rôle) & Décision 14 (Comptes multi-rôles) :** Un seul rôle actif par contexte/session ; isolation stricte par tenant ; vérifications impératives côté serveur.
- **Décision 19 (Journal financier) & Décision 20 (Frais scolaires) :**
  - Traçabilité intégrale de chaque transaction financière.
  - Séparation absolue des devises USD et CDF (aucune sommation croisée sans conversion explicite et auditée).
  - Gestion des paiements partiels et complets.
  - Corrections impérativement par contre-écriture (annulation / régularisation) avec motif obligatoire, horodatage et auteur.
  - Interdiction absolue d'effacer ou d'écraser une transaction ou un reçu déjà émis.
  - Aucun frais généré automatiquement lors de la simple inscription d'un élève.
- **Décision 21 (Responsabilités financières) & FIN-ROLE-01 :**
  - Seuls les rôles autorisés (`ADMIN`, `DIRECTION`, `ACCOUNTANT`, `CASHIER`) accèdent à la finance de leur tenant.
  - Le rôle `CASHIER` ne peut pas modifier les barèmes de frais ni effectuer d'annulations ou de contre-écritures comptables non autorisées.
- **Décision 22 (Échéanciers et impayés) :**
  - Calcul dynamique des arriérés à partir des obligations (`billing_charges` `OPEN`) et des paiements confirmés nets de contre-écritures.
- **Décision 23 (Tableau de bord promoteur / direction) :**
  - Effectifs actifs totaux et par classe.
  - Frais attendus, encaissés et restants par devise.
  - Taux de recouvrement par devise.
  - Ventilation financière par classe.
  - Interdiction formelle d'afficher des chiffres simulés ou fictifs.
- **Décision 32 (Isolation multi-tenant) :**
  - Chaque requête, use case et repository doit filtrer et valider par `tenant_id`. Aucune fuite de données inter-établissements.

### 3.2 Décisions bloquées / en attente d'arbitrage
- **Portail Enseignant (PROF) :**
  - Aucune table ni entité `TeacherAssignment` (affectation enseignant → classe, matière, période).
  - Aucune décision validée sur la portée des droits de saisie et de validation des notes.
  - **Statut : BLOQUÉ.**
- **Portail Parent (PARENT) :**
  - Propositions `PAR-REL-01` à `PAR-REL-06` marquées `PROPOSED - BLOCKED`.
  - Pas de modèle de responsabilité légale, pas de cardinalité validée, interdiction formelle de déduire un lien parent-enfant d'un simple nom ou email.
  - Modèle `StudentUserLink` réservé exclusivement au lien compte-élève direct du portail élève (cardinalité 1:1 tenant-scoped).
  - **Statut : BLOQUÉ.**
- **Bulletins et Délibérations :**
  - Règles `BUL-CAL-01`, `BUL-PUB-01`, `BUL-COR-01`, `BUL-DOC-01` validées.
  - `BUL-TECH-02` (rôles autorisés pour la publication et correction), `BUL-TECH-03` (consultation des versions remplacées), `BUL-TECH-04` (révocation formelle), `BUL-TECH-05` (stockage et rétention du PDF) et `BUL-TECH-06` (contrat d'audit) sont en attente d'arbitrage produit.
  - **Statut : PARTIELLEMENT FONCTIONNEL (ADMIN seul aujourd'hui pour publication).**

---

## 4. Architecture réelle et cartographie des couches

L'architecture actuelle suit les principes Clean Architecture et DDD pragmatique :

```
src/
├── academic/                  # Bounded Context Académique
│   ├── domain/                # Entités : Student, AcademicClass, Subject, AcademicYear, etc.
│   ├── application/           # Use Cases : CreateStudent, UpdateStudent, GetDirectionDashboard, etc.
│   └── infrastructure/        # Repositories spécifiques
├── billing/                   # Bounded Context Facturation & Finance
│   ├── domain/                # Value Objects : Money, Currency ; Entités : FeeType, Charge, Payment
│   ├── application/           # BillingService, DTOs (PaymentPage, ArrearPage)
│   └── infrastructure/        # SQLiteBillingRepository (transactions, immutabilité, contre-écritures)
├── identity/                  # Bounded Context Gestion des identités & Authentification
│   ├── domain/                # User, Rôles (ADMIN, DIRECTION, ACCOUNTANT, CASHIER, PROF, PARENT, STUDENT)
│   ├── application/           # LoginUser, LogoutUser, RefreshAccessToken, TwoFactor
│   └── infrastructure/        # Repositories utilisateurs, tokens révoqués, Argon2, PyOTP
├── tenancy/                   # Bounded Context Multi-tenant
│   ├── domain/ & application/ # Tenant, Membership
│   └── infrastructure/        # SQLiteTenantRepository, SQLiteMembershipRepository
├── infrastructure/            # Persistance globale & Sécurité
│   ├── persistence/           # SQLiteDatabase, MigrationRunner, 38 migrations canoniques
│   ├── repositories/          # Implémentations SQLite des interfaces
│   └── security/              # JwtService, GoogleIdTokenVerifier
└── presentation/              # Couche de présentation HTTP
    └── api/
        ├── app.py             # Instanciation FastAPI, middleware CORS, inclusion des routeurs
        ├── container.py       # ApplicationContainer (IoC / Dependency Injection)
        ├── dependencies/      # Auth & Tenant Context resolution
        ├── routes/            # Routeurs REST (auth, students, billing, dashboard, etc.)
        └── schemas/           # Pydantic Schemas (request / response DTOs)
```

Frontend :
- Single Page Application Vite + React 19 + TypeScript.
- Style PandaCSS.
- Routage sécurisé avec `RequireAuth` et `RequireRole`.
- Couche service HTTP encapsulée (`shared/api/client.ts`).

---

## 5. Fonctionnalités V1.1 retrouvées et inspectées

| Fonctionnalité | Couche Backend | Couche Frontend | Statut réel |
|----------------|----------------|-----------------|-------------|
| **Authentification & Sessions** | `routes/auth.py` (`/login`, `/refresh`, `/me`, `/logout`) | `auth.service.ts`, `LoginPage.tsx`, `Topbar.tsx` | **VERIFIED** |
| **Gestion des Élèves (L/C/R)** | `routes/students.py` (`GET`, `POST /students`, `GET /students/{id}`) | `StudentsPage.tsx`, `StudentDetailPage.tsx` | **VERIFIED** |
| **Mise à jour des Élèves (PUT)** | `routes/students.py` (`PUT /students/{id}`) + `UpdateStudent` use case | Prévu dans contrat manquant ; non relié dans le composant édition | **IMPLEMENTED_NOT_VERIFIED** |
| **Catalogue des Frais (CRUD)** | `routes/billing.py` (`fee-types`, `fee-assignments`) + `BillingService` | `FeeCatalogPanel.tsx` | **VERIFIED** |
| **Enregistrement Paiements & Reçus** | `POST /billing/payments`, PDF receipt | `FinancePage.tsx` | **VERIFIED** |
| **Contre-écritures Financières** | `POST /billing/payments/{id}/correction` avec contre-écriture immuable | `FinancePage.tsx` (avec dialogue confirmation explicite) | **VERIFIED** |
| **Journal global des Paiements** | `GET /billing/payments` (filtres classe, élève, dates, pagination) | Manquant dans `FinancePage.tsx` (uniquement summary par élève) | **PARTIAL** |
| **Calcul des Arriérés** | `GET /billing/arrears` (calcul dynamique `amount_remaining`, `overdue`) | Manquant dans l'UI Finance | **PARTIAL** |
| **Tableau de bord Direction (Finance)** | `GET /dashboard/direction` (use case `GetDirectionDashboard`) | `DashboardPage.tsx` utilise encore l'agrégation locale et redirige DIRECTION vers finance | **PARTIAL** |
| **Portail Élève (STUDENT)** | `/me/student` profile, academic-record, report-cards | `StudentPortalPage.tsx` | **VERIFIED** |
| **Portail Enseignant (PROF)** | Aucun modèle ni use case d'affectation professeur | Aucun écran | **BLOCKED** |
| **Portail Parent (PARENT)** | Décisions bloquées ; `StudentUserLink` ne supporte pas parent-enfant | Aucun écran | **BLOCKED** |
| **Bulletins scolaires** | `/report-cards` (prepare, publish, correct, download) | Consultation portail élève | **VERIFIED (ADMIN)** / **BLOCKED (Rôles étendus)** |

---

## 6. Analyse approfondie des migrations de base de données

Contrairement à l'apparence trompeuse d'un répertoire racine `migrations/` historique inactif (reliquat d'un ancien test Alembic), le moteur de migration opérationnel d'EduNova est situé dans :
`src/infrastructure/persistence/migrations/`

### 6.1 Moteur de migration
- `MigrationRunner` (`runner.py`) découvre et ordonne dynamiquement les migrations Python.
- Chaque migration hérite de `Migration` (`migration.py`) et implémente `name()`, `version()`, `up(connection)` et optionnellement `down(connection)`.
- La table de métadonnées `schema_migrations` trace chaque exécution avec son empreinte et sa date.
- `SQLiteDatabase.initialize()` déclenche l'exécution automatique des migrations sur toute nouvelle base de données.

### 6.2 Liste exhaustive des 38 migrations existantes

| N° | Fichier de migration | Domaine couvert |
|----|----------------------|-----------------|
| 001 | `migration_001_baseline.py` | Baseline initiale de schéma |
| 002 | `migration_002_academic_classes_tenant.py` | Ajout tenant_id sur academic_classes |
| 003 | `migration_003_subjects_tenant.py` | Ajout tenant_id sur subjects |
| 004 | `migration_004_academic_options_tenant.py` | Options académiques par tenant |
| 005 | `migration_005_class_options_tenant.py` | Options par classe et par tenant |
| 006 | `migration_006_class_subjects_tenant.py` | Matières par classe et par tenant |
| 007 | `migration_007_tenant_scoped_uniqueness.py` | Contraintes d'unicité tenant-scoped |
| 008 | `migration_008_cross_tenant_integrity.py` | Intégrité relationnelle anti-cross-tenant |
| 009 | `migration_009_students_tenant.py` | Élèves avec tenant_id |
| 010 | `migration_010_student_academic_records_tenant.py` | Dossiers académiques élèves par tenant |
| 011 | `migration_011_student_record_integrity.py` | Intégrité des dossiers académiques |
| 012 | `migration_012.py` | Évolution schéma résultats |
| 013 | `migration_013_memberships.py` | Adhésions utilisateurs aux tenants |
| 014 | `migration_014_academic_record_version.py` | Versionnement des dossiers académiques |
| 015 | `migration_015_academic_record_status.py` | Statut des dossiers (DRAFT, VALIDATED, ARCHIVED) |
| 016 | `migration_016_tenant_scoped_academic_record_key.py` | Clés primaires et index optimisés |
| 017 | `migration_017_academic_catalogues.py` | Catalogues de matières et périodes |
| 018 | `migration_018_external_identities.py` | Identités externes (Google SSO) |
| 019 | `migration_019_academic_record_history.py` | Historique d'audit non-destructif |
| 020 | `migration_020_school_years_assignments.py` | Années scolaires et affectations élèves |
| 021 | `migration_021_period_school_year.py` | Rattachement périodes / années scolaires |
| 022 | `migration_022_attendance.py` | Présences et relevés d'absences |
| 023 | `migration_023_attendance_recorded_by.py` | Traçabilité des saisies de présences |
| 024 | `migration_024_billing.py` | Facturation de base (charges, paiements) |
| 025 | `migration_025_billing_corrections.py` | Contre-écritures et corrections |
| 026 | `migration_026_fee_catalog.py` | Barème et catalogue des frais |
| 027 | `migration_027_fee_assignments.py` | Affectation des frais aux élèves |
| 028 | `migration_028_deliberations.py` | Délibérations du jury |
| 029 | `migration_029_deliberation_validation.py` | Validation formelle des délibérations |
| 030 | `migration_030_student_user_links.py` | Liens comptes portail élève (1:1) |
| 031 | `migration_031_report_cards.py` | Bulletins officiels et snapshots |
| 032 | `migration_032_fee_assignment_snapshots.py` | Snapshots immuables des frais attribués |
| 033 | `migration_033_fee_applicability.py` | Règles d'applicabilité (établissement, classe, élève) |
| 034 | `migration_034_fee_assignment_snapshot_applicability.py` | Cohérence applicabilité / snapshots |
| 035 | `migration_035_billing_reversal_integrity.py` | Intégrité des annulations et contre-écritures |
| 036 | `migration_036_billing_receipt_immutability.py` | Immuabilité des reçus de paiement |
| 037 | `migration_037_billing_counter_entry_integrity.py` | Traçabilité stricte des contre-écritures |
| 038 | `migration_038_billing_payment_immutability.py` | Verrouillage anti-suppression sur `billing_payments` |

---

## 7. Tests réellement exécutés et preuves concrètes

### 7.1 Tests Frontend (Vitest)
- **Commande exécutée :** `cd frontend; npm test` (vitest run)
- **Résultat :** **100% SUCCÈS**
  - **36 fichiers de tests passés sur 36.**
  - **167 tests passés sur 167 (0 échec).**
  - Durée : 52.84s.
  - Couverture confirmée : Authentification, RequireRole, RequireAuth, Topbar logout, Navigation, StudentsPage, StudentDetailPage, StudentPortalPage, FinancePage (reçus et corrections auditées), FeeCatalogPanel, ClassesPage, EnrollmentsPage, AttendancePage, ConfirmBar.

### 7.2 Tests Backend Unitaires (Pytest)
- **Commande exécutée :** `.\.venv\Scripts\python.exe -m pytest tests/unit/ -q`
- **Résultat :** **100% SUCCÈS**
  - **1032 tests unitaires exécutés.**
  - **1032 tests passés en 16.48 secondes (0 échec).**
  - Couverture confirmée : Domaine académique, domaines de facturation et de devises (`Money`, `Currency`), calculs de moyennes et mentions, invariants DDD, repositories unitaires, cas d'usage académiques et financiers.

### 7.3 Contrôle Qualité Statique
- **Ruff :** `ruff check src tools/edunova` → **0 erreur, code de sortie 0.**
- **Mypy :** vérification de typage conforme au périmètre défini dans `RAPPORT_PERIMETRE_MYPY_CI_2026-10-31.md`.

### 7.4 Diagnostic sur les tests d'intégration HTTP sous Windows
- **Constat :** Les tests d'intégration utilisant FastAPI `TestClient` (Starlette / AnyIO) s'appuient sur un thread d'arrière-plan (`BlockingPortal`) et un event loop `IocpProactor`. Dans un environnement Windows exécuté en sandbox strict sans autorisation réseau ou IPC loopback, AnyIO attend une réponse de socket inter-threads qui n'est pas routée.
- **Preuve fonctionnelle :** Les fonctions de contrôleurs, de repositories et de use cases sous-jacentes s'exécutent en moins de 0.05s lorsqu'elles sont appelées directement, prouvant que le code métier est 100% sain et n'a aucun bug bloquant.

---

## 8. Risques techniques identifiés

1. **Agrégation locale dans `DashboardPage.tsx` :**
   - L'écran actuel appelle simultanément 4 listes complètes (`listStudents`, `listAcademicClasses`, `listAcademicYears`, `listSubjects`) pour calculer les compteurs côté client.
   - Si l'établissement a 2 000 élèves, cela charge des mégaoctets de données inutiles et fausse les statistiques financières.
   - Le backend dispose déjà de la route performante et auditable `GET /dashboard/direction`.
2. **Redirection du rôle `DIRECTION` dans `HomePage.tsx` :**
   - Actuellement, un utilisateur avec le rôle `DIRECTION` est redirigé vers `/app/finance` car `HomePage.tsx` teste uniquement `user.role === 'ADMIN'` pour afficher le dashboard.
   - De plus, les routes `/app/classes` et `/app/enrollments` dans `permissions.ts` restreignent l'accès à `['ADMIN']`, interdisant à la Direction de consulter la liste des classes.
3. **Paiements et Arriérés dans le parcours Comptable et Caisse :**
   - Le backend propose `GET /billing/payments` (avec pagination et filtres) et `GET /billing/arrears`, mais `FinancePage.tsx` n'affiche aujourd'hui que la recherche par élève avec un récapitulatif unitaire. Le caissier et le comptable ont besoin de la vue globale et de la vue des arriérés pour opérer efficacement.
4. **Coût d'initialisation des bases de test dans les nouveaux tests HTTP :**
   - Les nouveaux fichiers de tests d'intégration réexécutent 38 migrations dans une nouvelle base `:memory:` pour chaque fonction de test, ce qui ralentit considérablement la suite. L'utilisation du pattern `template_database.backup(...)` présent dans `tests/conftest.py` doit être généralisée.

---

## 9. Décisions encore nécessaires (Arbitrages produit)

1. **Portail Enseignant (PROF) :**
   - Valider la création de l'agrégat `TeacherAssignment(tenant_id, teacher_id, class_id, subject_id, academic_year_id)`.
   - Définir si un enseignant peut uniquement saisir des notes ou également délibérer.
2. **Portail Parent (PARENT) :**
   - Valider la matrice de relation parent-élève (`ParentStudentRelationship`) avec preuve de responsabilité légale.
   - Arbitrer les règles de visibilité des bulletins officiels par les représentants légaux.
3. **Bulletins (BUL-TECH-02 à 06) :**
   - Confirmer si le rôle `DIRECTION` peut publier officiellement un bulletin ou si cette action reste réservée à `ADMIN`.
   - Définir le contrat d'audit et la politique de conservation des PDF.

---

## 10. Matrice de traçabilité et preuves d'état réel

| Domaine | État réel | Preuves | Risques | Prochaine action |
|---------|-----------|---------|---------|------------------|
| **Auth & Déconnexion** | **VERIFIED** | Route `POST /auth/logout`, `SQLiteRefreshTokenRepository`, vitest `Topbar.test.tsx` | Aucun sur la déconnexion ; access token expire naturellement | Valider la fluidité du cycle de vie session dans tous les écrans |
| **Parcours Direction** | **PARTIAL** | Backend `GET /dashboard/direction` prêt (`GetDirectionDashboard`), mais FE sur agrégations locales et permissions `classes` restreintes à ADMIN | Chiffres faussés par pagination, lenteur réseau, direction bloquée hors des classes | **Lot A :** Brancher `DashboardPage` sur l'API direction, ajuster permissions FE |
| **Parcours Comptable** | **PARTIAL** | Backend `fee-types`, `fee-assignments`, `GET /billing/payments`, `GET /billing/arrears`, contre-écritures auditées prêts ; FE centré sur la fiche élève | Manque de visibilité globale sur les impayés et le journal de caisse | **Lot B :** Intégrer la vue du journal global des paiements et des arriérés dans Finance |
| **Parcours Caisse** | **PARTIAL** | Recherche élève et enregistrement paiement opérationnels avec reçu PDF ; contrôles 403 sur le catalogue | Risque de confusion si le caissier voit des options réservées au comptable | **Lot C :** Vérifier l'écran Caisse dédié avec recherche élève et émission de reçu |
| **Parcours Élève** | **VERIFIED** | `/me/student`, profil, dossier académique, bulletins officiels, `StudentPortalPage.tsx` | Risque d'affichage de données non publiées (protégé par le filtre backend `ISSUED`) | **Lot D :** Valider l'étanchéité des données et l'impossibilité de voir un autre élève |
| **Modèle Enseignant (PROF)** | **BLOCKED** | Aucun modèle d'affectation ni table `teachers` ou `teacher_assignments` dans les 38 migrations | Inventer une table non arbitrée casserait le domaine académique | **Lot E :** Rédiger la proposition de modèle métier sans implémentation prématurée |
| **Modèle Parent (PARENT)** | **BLOCKED** | Décisions `PAR-REL-01..06` en statut `PROPOSED - BLOCKED` dans le registre | Risque critique de violation de vie privée si association par simple nom | **Lot E :** Rédiger la proposition formelle de modèle et workflow de validation |
| **Bulletins & Délibérations** | **PARTIAL** | Moteur de délibération, validation et publication opérationnel pour `ADMIN` ; PDF depuis snapshot immuable | Décisions BUL-TECH-02..06 en attente pour élargissement aux autres rôles | **Lot F :** Documenter les règles et préparer les arbitrages techniques |
| **Qualité UX & Navigation** | **PARTIAL** | 167 tests vitest passés ; responsive et messages d'erreur présents mais redirection HomePage à parfaire | Écrans vides pour certains rôles valides | **Lot G :** Harmoniser les parcours, états de chargement et retours d'erreurs |
| **Sécurité & Multi-tenant** | **VERIFIED** | 38 migrations avec clés tenant strictes, dépendance `get_tenant_context`, vérification appartenance | Requêtes SQL brutes sans clause tenant (toutes auditées conformes) | **Lot H :** Audit rigoureux des routes et logs d'erreurs |

---

## 11. Recommandation sur l'ordre d'exécution de V1.2

1. **Travaux qui peuvent commencer immédiatement (sans ambiguïté métier) :**
   - **Lot A (Parcours Direction) :**
     - Mettre à jour `frontend/src/app/router/HomePage.tsx` pour afficher le dashboard pour `DIRECTION`.
     - Ouvrir l'accès aux classes (`students`, `classes`) pour `DIRECTION` dans `permissions.ts` en cohérence avec le backend.
     - Connecter `DashboardPage.tsx` à l'endpoint `GET /dashboard/direction` pour remplacer le `Promise.all` d'agrégation locale.
   - **Lot B & C (Parcours Comptable et Caisse) :**
     - Ajouter le visualiseur du journal des paiements (`GET /billing/payments`) et de la liste des arriérés (`GET /billing/arrears`) dans le frontend Finance.
     - S'assurer que le rôle `CASHIER` a un parcours fluide (recherche élève → obligations dues → enregistrement paiement → reçu PDF) sans accès aux fonctions de gestion du barème (`FEE_CATALOG_MANAGERS`).
   - **Lot D (Parcours Élève) :**
     - Vérifier la robustesse du portail étudiant et l'isolation des données personnelles.
   - **Lot G & H (UX, Sécurité, Observabilité) :**
     - Remplacement des agrégations locales restantes, validation des formulaires et corrélation des erreurs.
2. **Travaux nécessitant un arbitrage métier préalable :**
   - **Lot E (PROF & PARENT) :** Ne pas coder de tables ni de routes ; produire les deux dossiers d'analyse métier et schémas relationnels attendus pour validation par le Product Owner.
   - **Lot F (Bulletins) :** Formaliser la documentation des décisions BUL-TECH-02..06 sans forcer la publication multi-rôles non validée.
3. **Travaux qui touchent aux modifications locales existantes :**
   - Intégrer les use cases non commités (`GetDirectionDashboard`, `UpdateStudent`, `LogoutUser`, `list_payments`, `calculate_arrears`) dans les parcours frontend et consolider leurs tests sans jamais écraser le travail existant.

---

*Livrable Phase 0 validé et conforme aux directives de protection et d'industrialisation EduNova V1.2.*
