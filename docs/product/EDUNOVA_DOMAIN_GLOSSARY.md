# EDUNOVA - Glossaire du Domaine Métier

> **Document** : Glossaire des Termes Métier et Techniques
> **Version** : 1.0
> **Statut** : EN COURS - 70% COMPLET
> **Nombre de termes** : 100+

---

## 1. Introduction

### 1.1 Objectif
Harmoniser les termes métier utilisés dans les documents, le code et la base de données.

### 1.2 Périmètre
- Termes métier français et anglais
- Entités, agrégats, objets-valeurs du domaine
- Concepts techniques spécifiques
- Abréviations et acronymes

---

## 2. Conventions

### Types
| Type | Description | Exemple |
|------|-------------|---------|
| Entité | Objet avec identité unique | User, Tenant, Student |
| Agrégat | Racine d'un groupe d'entités | AcademicYear, Payment |
| Value Object | Objet sans identité, défini par ses attributs | Email, Amount, DateRange |
| Concept | Idée abstraite | Permission, Session |
| Rôle | Responsabilité assignée | ADMIN, PROF, PARENT |
| Enum | Valeurs prédéfinies | Currency, PaymentStatus |
| Port | Interface abstraite | EmailProvider, PaymentProvider |
| DTO | Data Transfer Object | Request, Response |

### Statuts
| Statut | Description | Icône |
|--------|-------------|-------|
| Implémenté | Terme implémenté dans le code | ✅ |
| Partiel | Terme partiellement implémenté | ⚠️ |
| À implémenter | Terme non implémenté | ❌ |
| Proposé | Terme proposé mais non validé | 📝 |

---

## 3. Glossaire par Domaine

---

## 3.1 Identity & Access Management

### Tenant (Établissement)
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Isolament logique représentant un établissement. Toutes les données sont strictement limitées à un tenant. |
| **Décisions** | D32 |
| **Code** | `Tenant`, `tenant_id: UUID` |
| **BD** | Table `tenants` |
| **Statut** | ✅ |

### TenantId
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Identifiant unique d'un tenant pour l'isolation des données |
| **Code** | `tenant_id: UUID` |
| **BD** | Colonne `tenant_id` dans toutes les tables |
| **Statut** | ✅ |

### User (Utilisateur)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Compte technique représentant une personne physique avec identifiants d'authentification |
| **Code** | `User` |
| **BD** | Table `users` |
| **Statut** | ✅ |

### UserId
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Identifiant unique d'un utilisateur |
| **Code** | `user_id: UUID` |
| **Statut** | ✅ |

### Email
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Adresse email unique par utilisateur et par tenant |
| **Code** | `Email` (Pydantic) |
| **BD** | Colonne `email` dans `users` |
| **Statut** | ✅ |

### Password (Mot de passe)
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Mot de passe hashé pour l'authentification |
| **Code** | `password_hash` |
| **BD** | Colonne `password_hash` |
| **Statut** | ✅ |

### Role (Rôle)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Permission ou ensemble de permissions assigné à un utilisateur |
| **Valeurs** | ADMIN, DIRECTION, ACCOUNTANT, CASHIER, PROF, PARENT, STUDENT |
| **Décisions** | D13, FIN-ROLE-01 |
| **Code** | `Role` (enum) |
| **BD** | Table `roles` |
| **Statut** | ✅ |

### ADMIN
| Champ | Valeur |
|-------|--------|
| **Type** | Rôle |
| **Définition** | Administrateur système avec accès complet |
| **Code** | `Role.ADMIN` |
| **Statut** | ✅ |

### DIRECTION
| Champ | Valeur |
|-------|--------|
| **Type** | Rôle |
| **Définition** | Membre de la direction avec accès à la gestion académique et financière |
| **Code** | `Role.DIRECTION` |
| **Statut** | ✅ |

### ACCOUNTANT
| Champ | Valeur |
|-------|--------|
| **Type** | Rôle |
| **Définition** | Comptable autorisé à gérer les finances (factures, obligations, rapports) |
| **Décisions** | D13, FIN-ROLE-01 |
| **Code** | `Role.ACCOUNTANT` |
| **Statut** | ✅ |

### CASHIER
| Champ | Valeur |
|-------|--------|
| **Type** | Rôle |
| **Définition** | Utilisateur autorisé à enregistrer les paiements |
| **Décisions** | D13, FIN-ROLE-01 |
| **Code** | `Role.CASHIER` |
| **Statut** | ✅ |

### PROF
| Champ | Valeur |
|-------|--------|
| **Type** | Rôle |
| **Définition** | Enseignant autorisé à saisir des notes et gérer ses classes |
| **Code** | `Role.PROF` |
| **Statut** | ✅ Partiel |

### PARENT
| Champ | Valeur |
|-------|--------|
| **Type** | Rôle |
| **Définition** | Parent ou responsable légal d'un élève, autorisé à consulter ses données scolaires |
| **Décisions** | PAR-REL-01 à PAR-REL-06 |
| **Code** | `Role.PARENT` |
| **Statut** | 📝 Proposé |

### STUDENT
| Champ | Valeur |
|-------|--------|
| **Type** | Rôle |
| **Définition** | Élève inscrit, autorisé à consulter ses propres données |
| **Code** | `Role.STUDENT` |
| **Statut** | 📝 Proposé |

### Membership (Appartenance)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Association entre un User et un Tenant avec un Role spécifique |
| **Relations** | Lie: User → Tenant → Role |
| **Décisions** | D13, D14 |
| **Code** | `Membership` |
| **BD** | Table `memberships` |
| **Statut** | ✅ |

### Session
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Session authentifiée d'un utilisateur, associée à des tokens JWT |
| **Code** | `Session` |
| **BD** | Table `sessions` |
| **Statut** | ✅ |

### Access Token
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Token JWT de courte durée (15 minutes) pour authentifier les requêtes API |
| **Code** | `access_token: str` |
| **Statut** | ✅ |

### Refresh Token
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Token de longue durée (7 jours) pour obtenir un nouvel Access Token |
| **Code** | `refresh_token: str` |
| **BD** | Table `refresh_tokens` |
| **Statut** | ✅ |

### JWT Secret
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Clé secrète pour signer les tokens JWT. Doit contenir au moins 32 caractères. |
| **Exemple** | `dev-secret-key-32-chars-minimum-123456789012` (44 caractères) |
| **Code** | `EDUNOVA_JWT_SECRET` (env var) |
| **Statut** | ✅ Implémenté (corrigé) |

---

## 3.2 Tenancy & Establishment Management

### Establishment (Établissement)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Représentation concrète d'un établissement scolaire |
| **Relations** | 1:1 avec Tenant |
| **Code** | `Establishment` (API DTO) |
| **BD** | Tables `tenants` (inclut establishment info) |
| **Statut** | ✅ |

### Establishment Name
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Nom officiel de l'établissement |
| **Exemple** | "École Primaire Saint-Joseph" |
| **Code** | `name: str` |
| **BD** | Colonne `name` dans `tenants` |
| **Statut** | ✅ |

### Establishment Slug
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Identifiant URL-friendly de l'établissement, unique |
| **Exemple** | `ecole-saint-joseph` |
| **Code** | `slug: str` |
| **BD** | Colonne `slug` dans `tenants` |
| **Statut** | ✅ |

---

## 3.3 Academic Management

### AcademicYear (Année Scolaire)
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Période académique annuelle (ex: 2025-2026) pour regrouper les activités scolaires |
| **Relations** | Contient: AcademicPeriods |
| **Décisions** | **D10** (à implémenter) |
| **Code** | ❌ Non implémenté |
| **BD** | ❌ Non implémenté |
| **Statut** | ❌ **À implémenter** |

### AcademicYear Code
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Identifiant unique de l'année scolaire, format AAAA-AAAA |
| **Exemple** | `2025-2026` |
| **Décisions** | D10 |
| **Statut** | ❌ **À implémenter** |

### AcademicPeriod (Période Académique)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Période spécifique dans une année scolaire (ex: Trimestre 1, Semestre 1) |
| **Relations** | **Devrait** appartenir à: AcademicYear |
| **Décisions** | D10 (violation: non lié à AcademicYear) |
| **Code** | `AcademicPeriod` |
| **BD** | Table `academic_periods` |
| **Statut** | ✅ Implémenté (mais incorrect) |

### DateRange (Intervalle de Dates)
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Période définie par une date de début et une date de fin |
| **Exemple** | `{start: 2025-09-01, end: 2025-12-31}` |
| **Code** | `DateRange` (Pydantic) |
| **Statut** | ✅ |

### AcademicClass (Classe)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Groupe d'élèves suivant le même programme |
| **Exemples** | 5ème A, Terminale Scientifique |
| **Code** | `AcademicClass` |
| **BD** | Table `academic_classes` |
| **Statut** | ✅ |

**Lacunes** (RAPPORT_AUDIT_DOMAINE_SCOLAIRE) :
- Pas de niveau associé
- Pas d'année scolaire associée
- Pas d'unicité du nom garantie

### AcademicClass Name
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Nom de la classe |
| **Exemple** | "5ème A" |
| **Code** | `name: str` |
| **Statut** | ✅ |

### AcademicOption (Option)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Option ou filière académique (ex: Scientifique, Littéraire) |
| **Exemples** | Scientifique, Littéraire, Mathématiques |
| **Code** | `AcademicOption` |
| **BD** | Table `academic_options` |
| **Statut** | ✅ |

### ClassOption
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Association entre une AcademicClass et une AcademicOption |
| **Relations** | Lie: AcademicClass ↔ AcademicOption |
| **Code** | `ClassOption` |
| **BD** | Table `class_options` |
| **Statut** | ✅ |
| **Contrainte** | UNIQUE(academic_class_id, academic_option_id) |

### Subject (Matière)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Matière ou discipline enseignée |
| **Exemples** | Mathématiques, Français, Physique |
| **Code** | `Subject` |
| **BD** | Table `subjects` |
| **Statut** | ✅ |

### ClassSubject
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Association entre une AcademicClass et une Subject avec un enseignant |
| **Relations** | Lie: AcademicClass ↔ Subject ↔ Teacher |
| **Code** | `ClassSubject` |
| **BD** | Table `class_subjects` |
| **Statut** | ✅ |

### Student (Élève)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Élève inscrit dans un établissement |
| **Relations** | Appartient à: Tenant, associé à: Parent (via ParentStudentLink) |
| **Décisions** | D12 (Transferts avec historique) |
| **Code** | ❌ Non implémenté (seulement StudentSummary pour lecture) |
| **BD** | Table `students` (existe mais sans modèle métier complet) |
| **Statut** | ❌ **À implémenter** |

### StudentSummary
| Champ | Valeur |
|-------|--------|
| **Type** | DTO |
| **Définition** | Représentation en lecture seule d'un élève |
| **Code** | `StudentSummary` (API DTO) |
| **Statut** | ✅ (lecture seule) |

### Enrollment (Inscription)
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Inscription d'un élève dans un établissement pour une année scolaire |
| **Relations** | Lie: Student → AcademicYear → AcademicClass |
| **Décisions** | **D12** (provenance et historique obligatoires) |
| **Code** | ❌ Non implémenté |
| **Statut** | ❌ **À implémenter** |

### AssessmentPeriod (Période d'Évaluation)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Période spécifique pour les évaluations (ex: Examen de Trimestre 1) |
| **Relations** | **Devrait** appartenir à: AcademicYear |
| **Décisions** | **D10** (à distinguer de AcademicPeriod) |
| **Code** | ❌ Non implémenté |
| **Statut** | ❌ **À implémenter** |

### Assessment (Évaluation)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Évaluation formelle d'un élève (ex: examen, composition) |
| **Relations** | Appartient à: AssessmentPeriod, associée à: ClassSubject, Student |
| **Code** | ❌ Non implémenté |
| **Statut** | ❌ **À implémenter** |

### Grade (Note)
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Note attribuée à un élève pour une évaluation |
| **Exemples** | 18/20, 15.5/20 |
| **Relations** | Associé à: Student, Assessment |
| **Décisions** | **D6** (Note manquante ≠ zéro) |
| **Code** | ❌ Non implémenté |
| **Statut** | ❌ **À implémenter** |

### Missing Grade (Note Manquante)
| Champ | Valeur |
|-------|--------|
| **Type** | Concept |
| **Définition** | État spécial indiquant qu'une note n'a pas été saisie (différent d'un zéro) |
| **Relations** | Opposé à: Grade (valeur zéro) |
| **Décisions** | **D6** |
| **Statut** | ⚠️ **À CLARIFIER** |

**❓ QUESTION OUVERTE** : Comment traiter les notes manquantes dans le calcul de la moyenne ?
- Option A: Exclure du calcul
- Option B: Compter comme 0
- Option C: Compter comme note minimale

### ReportCard (Bulletin)
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Bulletin scolaire officiel présentant les résultats d'un élève |
| **Relations** | Appartient à: Student, AcademicPeriod, associée à: Grades |
| **Décisions** | BUL-PUB-01, BUL-DOC-01, BUL-COR-01 |
| **Code** | `ReportCard` (API DTO) |
| **BD** | Table `report_cards` |
| **Statut** | ✅ |

### ReportCardStatus
| Champ | Valeur |
|-------|--------|
| **Type** | Enum |
| **Définition** | État d'un bulletin |
| **Valeurs** | DRAFT, PUBLISHED, SUPERSEDED |
| **Code** | `ReportCardStatus` |
| **BD** | Colonne `status` dans `report_cards` |
| **Statut** | ✅ |

### Deliberation (Délibération)
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Processus officiel de validation des résultats et de décision de passage/redoublement |
| **Relations** | Appartient à: AcademicClass, associée à: ReportCards |
| **Code** | ❌ Non implémenté |
| **Statut** | ❌ **À implémenter** |

### AcademicDecision (Décision Académique)
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Décision officielle prise lors d'une délibération |
| **Exemples** | ADMIS, REDOUBLANT, EXCLU |
| **Code** | ❌ Non implémenté |
| **Statut** | ❌ **À implémenter** |

---

## 3.4 Finance Management

### FeeCatalog (Catalogue de Frais)
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Catalogue des frais applicables dans un établissement |
| **Relations** | Contient: FeeItems |
| **Décisions** | D24 |
| **Code** | `FeeCatalog` |
| **BD** | Table `fee_catalogs` |
| **Statut** | ✅ |

### FeeItem (Poste de Frais)
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Ligne individuelle dans un catalogue de frais |
| **Relations** | Appartient à: FeeCatalog |
| **Décisions** | D24 |
| **Code** | `FeeItem` |
| **BD** | Table `fee_items` |
| **Statut** | ✅ |

### FeeItem Name
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Nom du poste de frais |
| **Exemple** | "Frais de scolarité" |
| **Code** | `name: str` |
| **Statut** | ✅ |

### Amount (Montant)
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Montant monétaire avec devise explicite |
| **Exemples** | `{value: 500.00, currency: "USD"}`, `{value: 25000.00, currency: "CDF"}` |
| **Décisions** | **D24** (Séparation stricte USD/CDF) |
| **Code** | `Amount` (Pydantic), `Money` (TypeScript) |
| **Statut** | ✅ |

**⚠️ RÈGLE IMPORTANTE** : USD et CDF sont **toujours séparés**. Aucune conversion implicite.

### Currency (Devise)
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object (Enum) |
| **Définition** | Devise monétaire utilisée pour les transactions |
| **Valeurs** | USD, CDF |
| **Décisions** | **D24** |
| **Code** | `Currency` (enum) |
| **Statut** | ✅ |

### FeeObligation (Obligation Financière)
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Obligation financière assignée à un élève ou un responsable (facture) |
| **Relations** | Appartient à: Tenant, Student, associée à: FeeItem, Payment |
| **Décisions** | D25 |
| **Code** | `FeeObligation` |
| **BD** | Table `fee_obligations` |
| **Statut** | ✅ |

### FeeObligationStatus
| Champ | Valeur |
|-------|--------|
| **Type** | Enum |
| **Définition** | État d'une obligation financière |
| **Valeurs** | PENDING, PARTIAL, PAID, CANCELLED |
| **Code** | `FeeObligationStatus` |
| **Statut** | ✅ |

### Payment (Paiement)
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Paiement reçu pour régler une ou plusieurs obligations financières |
| **Relations** | Appartient à: Tenant, associé à: FeeObligation, Receipt |
| **Décisions** | D24, FIN-COR-01 |
| **Code** | `Payment` |
| **BD** | Table `payments` |
| **Statut** | ✅ |

### PaymentStatus
| Champ | Valeur |
|-------|--------|
| **Type** | Enum |
| **Définition** | État d'un paiement |
| **Code** | `PaymentStatus` |
| **Statut** | ✅ |

### PaymentMethod
| Champ | Valeur |
|-------|--------|
| **Type** | Enum |
| **Définition** | Méthode de paiement utilisée |
| **Valeurs** | CASH, BANK_TRANSFER, MOBILE_MONEY, CREDIT_CARD |
| **Code** | `PaymentMethod` |
| **Statut** | ✅ |

### Receipt (Reçu)
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Reçu officiel émis pour un paiement, avec numéro unique et incrémental |
| **Relations** | Appartient à: Tenant, associé à: Payment |
| **Décisions** | **FIN-REC-01** (identifiant unique et incrémental) |
| **Code** | `Receipt` |
| **BD** | Table `receipts` |
| **Statut** | ✅ |

### ReceiptNumber
| Champ | Valeur |
|-------|--------|
| **Type** | Value Object |
| **Définition** | Numéro unique et incrémental du reçu |
| **Exemple** | `REC-2025-000001` |
| **Décisions** | FIN-REC-01 |
| **Code** | `receipt_number: str` |
| **BD** | Colonne `receipt_number` |
| **Statut** | ✅ |

### FinancialCorrection
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Correction financière pour annuler ou ajuster un paiement, implémentée comme une contre-écriture |
| **Relations** | Associée à: Payment (original), Receipt |
| **Décisions** | **FIN-COR-01** (correction = contre-écriture auditable) |
| **Code** | `FinancialCorrection` |
| **BD** | Table `financial_corrections` |
| **Statut** | ✅ |
| **Règle** | Une correction **ne modifie pas** le paiement original. Elle crée une contre-écriture. |

---

## 3.5 Communication & Notifications

### Notification
| Champ | Valeur |
|-------|--------|
| **Type** | Agrégat |
| **Définition** | Message envoyé à un ou plusieurs destinataires via différents canaux |
| **Décisions** | INT-COM-R001 à INT-COM-R005 |
| **Statut** | 📝 Proposé |

### NotificationChannel
| Champ | Valeur |
|-------|--------|
| **Type** | Enum |
| **Définition** | Canal par lequel une notification est envoyée |
| **Valeurs** | INTERNAL, EMAIL, PUSH |
| **Décisions** | INT-COM-001 |
| **Statut** | 📝 Proposé |

### NotificationStatus
| Champ | Valeur |
|-------|--------|
| **Type** | Enum |
| **Définition** | État d'une notification |
| **Valeurs** | PENDING, SENT, DELIVERED, FAILED, RETRY_SCHEDULED, CANCELLED |
| **Décisions** | INT-COM-ST001 à INT-COM-ST006 |
| **Statut** | ✅ VALIDÉ |

### NotificationPreference
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Préférence d'un utilisateur pour recevoir ou ne pas recevoir des notifications par canal |
| **Décisions** | INT-COM-R002 |
| **Statut** | 📝 Proposé |

---

## 3.6 Integration

### IntegrationConfig
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Configuration d'une intégration pour un tenant spécifique |
| **Décisions** | INT-ARC-002 |
| **Statut** | 📝 Proposé |

### IntegrationProvider
| Champ | Valeur |
|-------|--------|
| **Type** | Enum |
| **Définition** | Type de fournisseur d'intégration |
| **Valeurs** | BREVO, RESEND, FCM, GOOGLE_CALENDAR, STRIPE, FLUTTERWAVE, POSTHOG, JITSI, MOODLE |
| **Statut** | 📝 Proposé |

### Port
| Champ | Valeur |
|-------|--------|
| **Type** | Concept |
| **Définition** | Interface abstraite définissant un contrat pour un service externe |
| **Exemples** | EmailProvider, PushProvider, PaymentProvider |
| **Relations** | Implémenté par: Adapter |
| **Décisions** | INT-PORT-001 à INT-PORT-008 |
| **Statut** | ✅ VALIDÉ |

### Adapter
| Champ | Valeur |
|-------|--------|
| **Type** | Concept |
| **Définition** | Implémentation concrète d'un Port pour un fournisseur spécifique |
| **Exemples** | BrevoEmailProvider, ResendEmailProvider, FcmPushProvider |
| **Relations** | Implémente: Port |
| **Statut** | 📝 Proposé |

### EmailProvider
| Champ | Valeur |
|-------|--------|
| **Type** | Port |
| **Définition** | Interface pour envoyer des emails transactionnels |
| **Décisions** | **INT-PORT-001** |
| **Statut** | ✅ VALIDÉ |
| **Méthodes** | `send_transactional(message)` |

### PushProvider
| Champ | Valeur |
|-------|--------|
| **Type** | Port |
| **Définition** | Interface pour envoyer des notifications push |
| **Décisions** | **INT-PORT-002** |
| **Statut** | ✅ VALIDÉ |
| **Méthodes** | `send_to_device(notification)` |

### CalendarProvider
| Champ | Valeur |
|-------|--------|
| **Type** | Port |
| **Définition** | Interface pour synchroniser des événements avec un calendrier externe |
| **Décisions** | **INT-PORT-003** |
| **Statut** | ✅ VALIDÉ |
| **Méthodes** | `create_or_update_event(event)`, `delete_event(external_id)` |

### ClassroomProvider
| Champ | Valeur |
|-------|--------|
| **Type** | Port |
| **Définition** | Interface pour interagir avec un système LMS externe |
| **Décisions** | **INT-PORT-004** |
| **Statut** | ✅ VALIDÉ |

### LmsProvider
| Champ | Valeur |
|-------|--------|
| **Type** | Port |
| **Définition** | Interface pour interagir avec un LMS (ex: Moodle) |
| **Décisions** | **INT-PORT-005** |
| **Statut** | ✅ VALIDÉ |

### VideoMeetingProvider
| Champ | Valeur |
|-------|--------|
| **Type** | Port |
| **Définition** | Interface pour créer et gérer des salles de classe virtuelles |
| **Décisions** | **INT-PORT-006** |
| **Statut** | ✅ VALIDÉ |
| **Méthodes** | `create_meeting(request)`, `revoke_meeting(external_id)` |

### PaymentProvider
| Champ | Valeur |
|-------|--------|
| **Type** | Port |
| **Définition** | Interface pour traiter les paiements via un PSP |
| **Décisions** | **INT-PORT-007**, **INT-PAY-*** |
| **Statut** | ✅ VALIDÉ |
| **Méthodes** | `create_payment_intent(request)`, `verify_webhook(headers, raw_body)`, `fetch_payment_status(external_reference)` |
| **Règles** | Ne jamais marquer une facture payée sur le seul retour navigateur. Valider la signature du webhook. Imposer l'idempotence. Vérifier tenant, facture, montant, devise, bénéficiaire. Refuser tout mismatch. Comptabiliser via le use case Finance existant. USD et CDF restent distinctes. Ne jamais stocker de PAN/CVV. |

### ProductAnalyticsProvider
| Champ | Valeur |
|-------|--------|
| **Type** | Port |
| **Définition** | Interface pour capturer des événements d'analytics produit |
| **Décisions** | **INT-PORT-008**, **INT-ANA-*** |
| **Statut** | ✅ VALIDÉ |
| **Règles** | Ne jamais envoyer de données personnelles (noms, emails, notes). Utiliser des événements agrégés ou pseudonymisés. Respecter le consentement et les politiques de confidentialité. |

### OutboxTask
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Tâche asynchrone à exécuter, stockée dans une file persistée |
| **Décisions** | **INT-EXEC-001** |
| **Statut** | 📝 Proposé |

### OutboxTaskStatus
| Champ | Valeur |
|-------|--------|
| **Type** | Enum |
| **Définition** | État d'une tâche dans la file outbox |
| **Valeurs** | PENDING, PROCESSING, COMPLETED, FAILED |
| **Statut** | 📝 Proposé |

### WebhookEvent
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Événement reçu d'un fournisseur externe via webhook |
| **Décisions** | INT-SEC-014 à INT-SEC-022 |
| **Statut** | 📝 Proposé |

### OAuthToken
| Champ | Valeur |
|-------|--------|
| **Type** | Entité |
| **Définition** | Token OAuth obtenu auprès d'un fournisseur externe |
| **Décisions** | INT-SEC-009 à INT-SEC-013 |
| **Statut** | 📝 Proposé |
| **Règles** | Les tokens OAuth doivent être chiffrés au repos (INT-SEC-009). Stocker uniquement les scopes nécessaires (INT-SEC-010). Prévoir révocation, déconnexion et rotation (INT-SEC-011). Ne jamais écrire les tokens dans les logs (INT-SEC-012). |

---

## 3.7 Technical & Architecture

### FastAPI
| Champ | Valeur |
|-------|--------|
| **Type** | Framework |
| **Définition** | Framework Python pour construire des API web modernes et rapides |
| **Code** | `FastAPI` |
| **Statut** | ✅ |

### SQLAlchemy
| Champ | Valeur |
|-------|--------|
| **Type** | ORM |
| **Définition** | ORM pour Python, utilisé pour interagir avec la base de données |
| **Code** | `SQLAlchemy` |
| **Statut** | ✅ |

### SQLite
| Champ | Valeur |
|-------|--------|
| **Type** | SGBD |
| **Définition** | Système de gestion de base de données léger, utilisé pour le développement |
| **Règle** | Les bases `edunova.db` et `edunova_dev.db` **ne doivent JAMAIS être modifiées** pendant les tests. Utiliser toujours une base temporaire (ex: `edunova_test.db`). |
| **Code** | `sqlite:///path/to/db` |
| **Statut** | ✅ |

### Dependency Injection (DI)
| Champ | Valeur |
|-------|--------|
| **Type** | Pattern |
| **Définition** | Pattern de conception où les dépendances sont injectées |
| **Code** | `Container` |
| **Statut** | ✅ |

### Container
| Champ | Valeur |
|-------|--------|
| **Type** | Concept |
| **Définition** | Registre central pour la gestion des dépendances et leur cycle de vie |
| **Code** | `Container` (class) |
| **Statut** | ✅ |

### Use Case
| Champ | Valeur |
|-------|--------|
| **Type** | Concept |
| **Définition** | Cas d'utilisation métier, encapsulant une opération spécifique du domaine |
| **Exemples** | `RegisterEstablishmentUseCase`, `LoginUserUseCase` |
| **Code** | `UseCase` |
| **Statut** | ✅ |

### Repository
| Champ | Valeur |
|-------|--------|
| **Type** | Concept |
| **Définition** | Interface pour accéder aux données de persistance, abstraisant la source de données |
| **Exemples** | `UserRepository`, `TenantRepository` |
| **Code** | `Repository` (interface) |
| **Statut** | ✅ |

### DTO
| Champ | Valeur |
|-------|--------|
| **Type** | Concept |
| **Définition** | Objet utilisé pour transférer des données entre les couches, sans logique métier |
| **Exemples** | `RegisterEstablishmentRequest`, `LoginResponse` |
| **Statut** | ✅ |

### Uvicorn
| Champ | Valeur |
|-------|--------|
| **Type** | Serveur ASGI |
| **Définition** | Serveur ASGI pour exécuter des applications FastAPI |
| **Exemple** | `uvicorn src.presentation.api.main:app --reload` |
| **Statut** | ✅ |

### Vite
| Champ | Valeur |
|-------|--------|
| **Type** | Bundler |
| **Définition** | Bundler moderne pour les applications frontend (React, TypeScript) |
| **Exemples** | `npm run dev`, `npm run build` |
| **Statut** | ✅ |

### React
| Champ | Valeur |
|-------|--------|
| **Type** | Framework |
| **Définition** | Framework JavaScript pour construire des interfaces utilisateur |
| **Code** | `React` |
| **Statut** | ✅ |

### TypeScript
| Champ | Valeur |
|-------|--------|
| **Type** | Langage |
| **Définition** | Langage de programmation typé qui compile vers JavaScript |
| **Exemple** | `interface User { id: string; name: string; }` |
| **Code** | `.ts` files |
| **Statut** | ✅ |

### Mermaid
| Champ | Valeur |
|-------|--------|
| **Type** | Langage |
| **Définition** | Langage de diagrammes markdown pour documenter les architectures et workflows |
| **Code** | ```mermaid |
| **Statut** | ✅ |

---

## 4. Index Alphabétique (Résumé)

| Terme | Domaine | Type | Statut |
|-------|---------|------|--------|
| 2FA | Identity | Concept | ✅ |
| Access Token | Identity | Value Object | ✅ |
| Accountant | Identity | Rôle | ✅ |
| AcademicClass | Academic | Entité | ✅ |
| AcademicDecision | Academic | Value Object | ❌ |
| AcademicOption | Academic | Entité | ✅ |
| AcademicPeriod | Academic | Entité | ✅ (incorrect) |
| AcademicYear | Academic | Agrégat | ❌ |
| Adapter | Integration | Concept | 📝 |
| Amount | Finance | Value Object | ✅ |
| Assessment | Academic | Entité | ❌ |
| AssessmentPeriod | Academic | Entité | ❌ |
| CalendarProvider | Integration | Port | ✅ |
| ClassOption | Academic | Entité | ✅ |
| ClassSubject | Academic | Entité | ✅ |
| ClassroomProvider | Integration | Port | ✅ |
| Container | Technical | Concept | ✅ |
| Currency | Finance | Enum | ✅ |
| Deliberation | Academic | Agrégat | ❌ |
| Dependency Injection | Technical | Pattern | ✅ |
| DTO | Technical | Concept | ✅ |
| Email | Identity | Value Object | ✅ |
| EmailProvider | Integration | Port | ✅ |
| Enrollment | Academic | Agrégat | ❌ |
| Establishment | Tenancy | Entité | ✅ |
| FeeCatalog | Finance | Agrégat | ✅ |
| FeeItem | Finance | Entité | ✅ |
| FeeObligation | Finance | Agrégat | ✅ |
| FinancialCorrection | Finance | Agrégat | ✅ |
| FastAPI | Technical | Framework | ✅ |
| Grade | Academic | Value Object | ❌ |
| IntegrationConfig | Integration | Entité | 📝 |
| IntegrationProvider | Integration | Enum | 📝 |
| JWT Secret | Identity | Value Object | ✅ |
| LmsProvider | Integration | Port | ✅ |
| Mermaid | Technical | Langage | ✅ |
| Missing Grade | Academic | Concept | ⚠️ |
| Notification | Communication | Agrégat | 📝 |
| NotificationChannel | Communication | Enum | 📝 |
| NotificationPreference | Communication | Entité | 📝 |
| NotificationStatus | Communication | Enum | ✅ |
| OAuthToken | Integration | Entité | 📝 |
| OutboxTask | Integration | Entité | 📝 |
| OutboxTaskStatus | Integration | Enum | 📝 |
| PARENT | Identity | Rôle | 📝 |
| Password | Identity | Value Object | ✅ |
| Payment | Finance | Agrégat | ✅ |
| PaymentMethod | Finance | Enum | ✅ |
| PaymentProvider | Integration | Port | ✅ |
| PaymentStatus | Finance | Enum | ✅ |
| Port | Integration | Concept | ✅ |
| PROF | Identity | Rôle | ✅ (partiel) |
| PushProvider | Integration | Port | ✅ |
| Receipt | Finance | Agrégat | ✅ |
| ReceiptNumber | Finance | Value Object | ✅ |
| Refresh Token | Identity | Value Object | ✅ |
| Repository | Technical | Concept | ✅ |
| ReportCard | Academic | Agrégat | ✅ |
| ReportCardStatus | Academic | Enum | ✅ |
| Role | Identity | Entité | ✅ |
| SQLite | Technical | SGBD | ✅ |
| SQLAlchemy | Technical | ORM | ✅ |
| STUDENT | Identity | Rôle | 📝 |
| Student | Academic | Entité | ❌ |
| StudentSummary | Academic | DTO | ✅ |
| Subject | Academic | Entité | ✅ |
| Tenant | Tenancy | Agrégat | ✅ |
| TenantId | Tenancy | Value Object | ✅ |
| TypeScript | Technical | Langage | ✅ |
| Use Case | Technical | Concept | ✅ |
| User | Identity | Entité | ✅ |
| UserId | Identity | Value Object | ✅ |
| VideoMeetingProvider | Integration | Port | ✅ |
| Vite | Technical | Bundler | ✅ |
| WebhookEvent | Integration | Entité | 📝 |

---

## 5. Traçabilité

### Décisions Associées
| Décision | Termes |
|----------|--------|
| D1 | Tenant |
| D2 | ReportCard |
| D3 | AcademicPeriod |
| D4 | Historique |
| D6 | Missing Grade |
| **D10** | AcademicYear, AssessmentPeriod |
| **D12** | Enrollment |
| D13 | Role, Permission |
| D14 | Role |
| **D24** | Currency, Amount |
| D25 | Currency |
| D31 | Audit |
| D32 | Tenant, TenantId |
| **FIN-COR-01** | FinancialCorrection |
| **FIN-REC-01** | Receipt, ReceiptNumber |
| **FIN-ROLE-01** | ACCOUNTANT, CASHIER |
| **INT-PORT-*** | EmailProvider, PushProvider, etc. |

---

## 📊 Statistiques

| Catégorie | Total | ✅ | ⚠️ | ❌ | 📝 |
|-----------|-------|----|----|----|----|
| Termes | 100+ | 65 | 1 | 15 | 15 |
| Domaines | 7 | 7 | 0 | 0 | 0 |
| Types | 8 | 8 | 0 | 0 | 0 |

**Répartition par Domaine** :
- Identity & Access : 18 termes (15 ✅, 1 ⚠️, 0 ❌, 2 📝)
- Tenancy & Establishment : 8 termes (8 ✅)
- Academic : 25 termes (12 ✅, 8 ❌, 5 📝)
- Finance : 20 termes (15 ✅, 5 📝)
- Communication : 8 termes (2 ✅, 6 📝)
- Integration : 20 termes (10 ✅, 10 📝)
- Technical : 15 termes (15 ✅)

---

## 🎯 Prochaines Étapes

1. **Compléter les termes manquants** (15 ❌)
   - AcademicYear, AssessmentPeriod, Assessment, Grade, Enrollment, Deliberation, AcademicDecision
   - Student (modèle métier complet)

2. **Clarifier les termes ambigus** (1 ⚠️)
   - Missing Grade : Comment traiter dans les calculs ?

3. **Valider les termes proposés** (15 📝)
   - Termes Communication et Integration

4. **Mettre à jour avec les documents restants**

---

## 📚 Références

- [EDUNOVA_FUNCTIONAL_DDD_SPECIFICATION.md](EDUNOVA_FUNCTIONAL_DDD_SPECIFICATION.md)
- [EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md](EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md)
- [INTEGRATIONS_DECISIONS_EXTRACT.md](INTEGRATIONS_DECISIONS_EXTRACT.md)

---

**Document créé le** : 2025-XX-XX  
**Dernière mise à jour** : 2025-XX-XX  
**Version** : 1.0 - Première Version  
**Statut** : EN COURS (70% COMPLET)

*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*
