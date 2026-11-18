# EduNova - Cadre d'Analyse DDD

**Document** : Cadre de travail pour l'analyse DDD d'EduNova  
**Version** : 0.1 - En cours  
**Date** : 2025-XX-XX  
**Auteur** : Analyse DDD Automatique

---

## 🎯 Objectif

Ce document établit le cadre pour une analyse complète du domaine EduNova selon les principes du Domain-Driven Design. Il sert de base pour la production de la spécification fonctionnelle finale.

---

## 📚 Sources Documentaires Principales

### Niveau Stratégique (Vision & Architecture)
1. **EDUNOVA_FUSION_MASTERPLAN.md** ✅
   - Vision produit (AI-enabled, Platform, Africa-first, Automation with guardrails)
   - Principes non négociables (10 principes)
   - Domaines métier cibles (10 domaines)
   - Architecture cible (Monolithe modulaire → SaaS → Services distribués)
   - Programme d'innovation (AI, Africa-First, Identity Passport, Ecosystem, Governance)
   - Feuille de route (Étape 0-7)
   - Définition de "prêt" (8 critères)
   - Hors périmètre immédiat (10 points)

### Niveau Tactique (Décisions Métier)
2. **docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md** ✅
   - 44 décisions validées (D1-D44)
   - Décisions canoniques Bulletins (BUL-CAL-01 à BUL-SCOPE-01)
   - Décisions financières canoniques (FIN-ROLE-01, FIN-COR-01, FIN-REC-01)
   - Propositions Parent-Enfant (PAR-REL-01 à PAR-REL-06) - NON VALIDÉES
   - Décisions techniques Bulletins (BUL-TECH-01 à BUL-TECH-06) - EN ATTENTE

3. **docs/v1/DECISIONS_REQUISES.md** ✅
   - Décisions V1 (D1-D12)
   - Réconciliation canonique des bulletins
   - Clarifications Tranche 0.1

### Niveau Opérationnel (Contrats & Implémentation)
4. **docs/v1/CONTRATS_METIER_V1.md** ✅
   - Contrats métier pour :
     - Configuration d'établissement
     - Bulletin PDF
     - Paiements et reçus
   - Invariants par domaine
   - Cas d'usage et ports
   - Evenements et erreurs

5. **docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md** ⏳
   - Architecture d'intégration
   - 10 services externes (Brevo, Resend, Courier, FCM, Google Classroom, etc.)
   - Ports/contrats conceptuels
   - Sécurité et multi-tenant
   - Modèle d'exécution

### Niveau Audit & Rapports
6. **docs/reports/RAPPORT_AUDIT_DOMAINE_SCOLAIRE_2026-10-16.md** ✅
   - État initial du code
   - Analyse des entités existantes
   - Lacunes DDD démontrées
   - Risques identifiés
   - Tests requis
   - Ordre minimal recommandé

7. **Autres rapports v1.2** ⏳ (À examiner)
   - Rapports de phase 1-5
   - Rapports de sécurité
   - Rapports d'intégration

---

## 🏗️ Modèle DDD Préliminaire

### Bounded Contexts Identifiés

Basé sur les documents examinés, voici une première proposition de bounded contexts :

#### 1. **Identity & Access Management**
- **Responsabilité** : Gestion des identités, authentification, autorisation, sessions
- **Agrégats** : User, Role, Permission, Session, Tenant
- **Contexte** : central, partagé par tous les autres contextes
- **Ports** : AuthenticationService, AuthorizationService, UserRepository
- **Décisions liées** : D13, D14, D26-D28, D32

#### 2. **Tenancy & Establishment Management**
- **Responsabilité** : Gestion des établissements (tenants), configuration de base
- **Agrégats** : Tenant, Establishment, SchoolConfiguration
- **Contexte** : Fondation pour l'isolation multi-tenant
- **Ports** : TenantRepository, EstablishmentRepository
- **Décisions liées** : D2, D13, D32

#### 3. **Academic Management**
- **Responsabilité** : Gestion des années scolaires, périodes, classes, matières, inscriptions
- **Agrégats** : AcademicYear, AcademicPeriod, AcademicClass, Subject, Enrollment, StudentAssignment
- **Contexte** : Cœur du domaine éducatif
- **Ports** : AcademicYearRepository, AcademicPeriodRepository, ClassRepository, SubjectRepository, EnrollmentRepository
- **Décisions liées** : D1-D2, D10-D12, BUL-CAL-01, BUL-PROF-01, BUL-SCOPE-01

#### 4. **Student Management**
- **Responsabilité** : Gestion des élèves, leurs dossiers, historique
- **Agrégats** : Student, StudentAcademicRecord, AcademicDecision
- **Contexte** : Gestion des apprenants
- **Ports** : StudentRepository, StudentAcademicRecordRepository
- **Décisions liées** : D6, D12, D15-D18, BUL-COR-01, BUL-PUB-01

#### 5. **Assessment & Grading**
- **Responsabilité** : Saisie des notes, calcul des moyennes, gestion des évaluations
- **Agrégats** : Assessment, Grade, SubjectResult
- **Contexte** : Évaluation des apprentissages
- **Ports** : AssessmentRepository, GradeRepository
- **Décisions liées** : D5-D9, BUL-CALC-01, BUL-DOC-01

#### 6. **Deliberation & Report Cards**
- **Responsabilité** : Délibération, génération des bulletins, publication
- **Agrégats** : Deliberation, ReportCard
- **Contexte** : Production des documents officiels
- **Ports** : DeliberationRepository, ReportCardRepository, ReportCardRenderer
- **Décisions liées** : D4-D7, BUL-PUB-01, BUL-COR-01, BUL-DOC-01

#### 7. **Financial Management**
- **Responsabilité** : Gestion des frais, obligations, paiements, reçus
- **Agrégats** : FeeCatalogue, FeeObligation, Payment, Receipt, FinancialCredit
- **Contexte** : Gestion financière
- **Ports** : FeeCatalogueRepository, PaymentRepository, ReceiptRepository
- **Décisions liées** : D19-D23, FIN-ROLE-01, FIN-COR-01, FIN-REC-01

#### 8. **Communication & Notifications**
- **Responsabilité** : Notifications, annonces, préférences de communication
- **Agrégats** : Notification, Announcement, NotificationPreference
- **Contexte** : Communication interne
- **Ports** : NotificationRepository, NotificationService
- **Décisions liées** : D24

#### 9. **Integration & External Services**
- **Responsabilité** : Intégration avec services externes (email, push, calendrier, paiement)
- **Agrégats** : IntegrationConfiguration, ExternalServiceToken
- **Contexte** : Connexions avec l'extérieur
- **Ports** : EmailProvider, PushProvider, CalendarProvider, PaymentProvider
- **Décisions liées** : Voir EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md

#### 10. **Document Management**
- **Responsabilité** : Gestion des documents générés (bulletins, reçus)
- **Agrégats** : Document, DocumentVersion
- **Contexte** : Archivage et gestion des documents
- **Ports** : DocumentRepository, DocumentStorage
- **Décisions liées** : BUL-DOC-01, FIN-REC-01

---

## 👥 Acteurs Identifiés

### Acteurs Principaux

#### 1. **ADMIN**
- **Rôle** : Administrateur système/technique
- **Responsabilités** : Configuration technique, gestion des utilisateurs, gestion des permissions
- **Permissions** : Accès complet à son tenant
- **Décisions** : D13, D26-D28

#### 2. **DIRECTION**
- **Rôle** : Direction de l'établissement
- **Responsabilités** : Gestion stratégique, validation des décisions importantes
- **Permissions** : Accès aux données de son établissement, validation des bulletins, gestion financière
- **Décisions** : D13, D20-D23, FIN-ROLE-01

#### 3. **ACCOUNTANT**
- **Rôle** : Comptable
- **Responsabilités** : Gestion financière, comptabilité
- **Permissions** : Accès aux données financières, enregistrement des paiements, génération des reçus
- **Décisions** : FIN-ROLE-01, FIN-COR-01, FIN-REC-01

#### 4. **CASHIER**
- **Rôle** : Caissier
- **Responsabilités** : Encaissement des paiements
- **Permissions** : Confirmation des paiements, émission de reçus
- **Décisions** : FIN-ROLE-01, FIN-COR-01

#### 5. **PROF** (Enseignant)
- **Rôle** : Enseignant
- **Responsabilités** : Saisie des notes, gestion des présences, consultation des données de ses classes
- **Permissions** : Accès aux classes et matières qui lui sont affectées
- **Décisions** : D13, D6-D9

#### 6. **PARENT**
- **Rôle** : Parent/Responsable légal
- **Responsabilités** : Consultation des informations scolaires et financières de ses enfants
- **Permissions** : Accès aux bulletins officiels, résultats, présences de ses enfants (après validation du rattachement)
- **Décisions** : D16, PAR-REL-01 à PAR-REL-06 (propositions)

#### 7. **STUDENT**
- **Rôle** : Élève
- **Responsabilités** : Consultation de ses propres résultats et informations
- **Permissions** : Accès à ses propres bulletins officiels, résultats
- **Décisions** : D16

---

## 📋 Règles Métier Consolidées

### Règles Académique (VALIDÉES)

| ID | Règle | Statut | Source |
|----|-------|--------|--------|
| D1 | Seuil de réussite par matière configurable par établissement | VALIDÉE | REGISTRE |
| D2 | Politique académique fixée à l'ouverture de la période | VALIDÉE | REGISTRE |
| D3 | Correction crée nouvelle version, ancienne conservée | VALIDÉE | REGISTRE |
| D4 | Crédits académiques exclus du périmètre initial | VALIDÉE | REGISTRE |
| D5 | Formule de moyenne configurable par établissement | VALIDÉE | REGISTRE |
| D6 | Note manquante ≠ zéro | VALIDÉE | REGISTRE |
| D7 | Validation et publication configurable par établissement | VALIDÉE | REGISTRE |
| D8 | Correction après publication conserve historique | VALIDÉE | REGISTRE |
| D9 | Modification de politique : pas de recalcul rétroactif automatique | VALIDÉE | REGISTRE |
| D10 | Années scolaires et périodes : modèles officiels | VALIDÉE | REGISTRE |
| D11 | Coefficients basés sur modèles officiels | VALIDÉE | REGISTRE |
| D12 | Transferts : procédure configurable, historique obligatoire | VALIDÉE | REGISTRE |
| BUL-CAL-01 | Périodes configurables par profil académique | VALIDÉE | REGISTRE |
| BUL-PUB-01 | Délibération persistée avant publication | VALIDÉE | REGISTRE |
| BUL-COR-01 | Correction versionnée, ancienne en SUPERSEDED | VALIDÉE | REGISTRE |
| BUL-CALC-01 | Politique versionnée, arrondi explicite | VALIDÉE AVEC RÉSERVE | REGISTRE |
| BUL-DOC-01 | PDF depuis snapshot immuable | VALIDÉE | REGISTRE |
| BUL-PROF-01 | Profils académiques versionnés | VALIDÉE | REGISTRE |
| BUL-SCOPE-01 | V1 couvre primaire, secondaire inférieur, humanités | VALIDÉE | REGISTRE |

### Règles Finance (VALIDÉES)

| ID | Règle | Statut | Source |
|----|-------|--------|--------|
| D19 | Journal financier traçable | VALIDÉE | REGISTRE |
| D20 | Barème de frais configurable et versionné | VALIDÉE | REGISTRE |
| D21 | Responsabilités financières configurables | VALIDÉE | REGISTRE |
| D22 | Échéanciers configurables, arriérés calculés | VALIDÉE | REGISTRE |
| D23 | Tableau de bord : frais attendus, paiements confirmés, soldes | VALIDÉE | REGISTRE |
| FIN-ROLE-01 | Finance accessible à DIRECTION, ACCOUNTANT, CASHIER | VALIDÉE | REGISTRE |
| FIN-COR-01 | Correction par contre-écriture, jamais suppression | VALIDÉE | REGISTRE |
| FIN-REC-01 | Reçu consultable et traçable | VALIDÉE AVEC RÉSERVES | REGISTRE |

### Règles Identity & Access (VALIDÉES)

| ID | Règle | Statut | Source |
|----|-------|--------|--------|
| D13 | Permissions configurables par établissement et rôle | VALIDÉE | REGISTRE |
| D14 | Un compte = un rôle/contexte actif à la fois | VALIDÉE | REGISTRE |
| D26 | Cycle de vie des comptes contrôlé | VALIDÉE | REGISTRE |
| D27 | Authentification proportionnée au risque | VALIDÉE | REGISTRE |
| D28 | Incidents de sécurité : processus structuré | VALIDÉE | REGISTRE |
| D32 | Isolation multi-tenant à toutes les couches | VALIDÉE | REGISTRE |

### Règles Infrastructure (VALIDÉES)

| ID | Règle | Statut | Source |
|----|-------|--------|--------|
| D25 | Mode hors ligne limité aux fonctions autorisées | VALIDÉE | REGISTRE |
| D29 | Sauvegardes protégées et séparées | VALIDÉE | REGISTRE |
| D30 | Journaux d'audit pour opérations sensibles | VALIDÉE | REGISTRE |
| D31 | Cycle de vie des données par catégorie | VALIDÉE | REGISTRE |
| D33 | Gestion des erreurs uniforme et classée | VALIDÉE | REGISTRE |
| D34 | Stratégie de tests multi-niveaux | VALIDÉE | REGISTRE |
| D35 | Déploiement contrôlé avec retour arrière | VALIDÉE | REGISTRE |
| D36 | Environnements strictement séparés | VALIDÉE | REGISTRE |
| D37 | Dépendances inventoriées et verrouillées | VALIDÉE | REGISTRE |
| D38 | Protection de la vie privée | VALIDÉE | REGISTRE |
| D39 | Exports gouvernés par rôle et finalité | VALIDÉE | REGISTRE |
| D40 | Performance mesurée | VALIDÉE | REGISTRE |
| D41 | Observabilité complète | VALIDÉE | REGISTRE |
| D42 | Gouvernance des évolutions | VALIDÉE | REGISTRE |

---

## ⚠️ Points à Clarifier (EN ATTENTE)

### Décisions en Attente

1. **Décision 45** - Identification des personnes et prévention des doublons
   - Option A : Identifiant interne EduNova + matricules existants
   - Option B : Matricule officiel obligatoire
   - Option C : Nom + date de naissance + vérification manuelle
   - **Recommandation** : Option A

2. **BUL-REG-01** - Règles réglementaires propres aux niveaux
   - Programmes, matières, maxima, coefficients, périodes, repêchage, décisions de passage, mentions
   - **Statut** : EN ATTENTE DE CONFIRMATION

3. **BUL-TECH-01** - Choix techniques de publication
   - Stockage du PDF, rétention, identifiant légal
   - **Statut** : EN ATTENTE DE DÉCISION TECHNIQUE

4. **BUL-TECH-02** - Autorisations de publication et correction
   - Qui peut publier et corriger les bulletins ?
   - **Statut** : EN ATTENTE DE DÉCISION PRODUIT

5. **BUL-TECH-03** - Consultation des versions remplacées
   - Quels rôles peuvent consulter les versions SUPERSEDED ?
   - **Statut** : EN ATTENTE DE DÉCISION PRODUIT

6. **BUL-TECH-04** - Révocation d'un bulletin émis
   - Procédure, motifs, effets, autorisations
   - **Statut** : EN ATTENTE DE DÉCISION PRODUIT

7. **BUL-TECH-05** - Stockage et rétention du PDF
   - Archivage persistant vs rendu à la demande
   - **Statut** : EN ATTENTE DE DÉCISION TECHNIQUE

8. **BUL-TECH-06** - Audit des émissions et téléchargements
   - Événements obligatoires, données conservées
   - **Statut** : EN ATTENTE DE CONTRAT D'AUDIT

### Propositions Non Validées

1. **PAR-REL-01** - Cardinalité Parent-Enfant
   - Plusieurs parents par élève, plusieurs élèves par parent
   - **Statut** : PROPOSÉE

2. **PAR-REL-02** - Validation du rattachement
   - Création et validation par direction ou agent habilité
   - **Statut** : PROPOSÉE

3. **PAR-REL-03** - Historique non destructif
   - Conservation de l'auteur, date, motif, transitions
   - **Statut** : PROPOSÉE

4. **PAR-REL-04** - Accès Parent aux données
   - Consultation des bulletins, résultats, présences
   - **Statut** : PROPOSÉE

5. **PAR-REL-06** - Accès parent aux bulletins officiels
   - Vérification serveur du rattachement actif
   - **Statut** : PROPOSÉE

---

## 🔗 Context Map Préliminaire

```
┌─────────────────────────────────────────────────────────────────┐
│                        EDUNOVA SYSTEM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Identity   │    │   Tenancy    │    │  Academic    │   │
│  │   & Access   │◄──►│  & School    │◄──►│  Management  │   │
│  │  Management  │    │  Management  │    │              │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│           │                    │                   │            │
│           ▼                    ▼                   ▼            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  Communication│    │    Student   │    │Assessment & │   │
│  │  & Notif.    │    │  Management  │    │   Grading    │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│           │                    │                   │            │
│           └────────────────────┼───────────────────┘            │
│                                ▼                                   │
│                    ┌─────────────────────────────┐                │
│                    │    Deliberation & Report   │                │
│                    │         Cards              │                │
│                    └─────────────────────────────┘                │
│                                │                                   │
│           ┌────────────────────┴───────────────────┐            │
│           ▼                                         ▼            │
│  ┌──────────────┐                       ┌──────────────┐   │
│  │   Finance    │                       │  Integration │   │
│  │  Management  │                       │  & External  │   │
│  └──────────────┘                       └──────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Légende
- `◄──►` : Relation de collaboration (Downstream ↔ Upstream)
- `─►` : Relation de dépendance (Client → Service)
- **Identity & Access** : Contexte central, utilisé par tous
- **Tenancy & School** : Contexte de base pour l'isolation
- **Academic Management** : Contexte cœur métier
- **Student Management** : Contexte de gestion des apprenants
- **Assessment & Grading** : Contexte d'évaluation
- **Deliberation & Report Cards** : Contexte de production de documents
- **Finance Management** : Contexte financier
- **Communication & Notifications** : Contexte de communication
- **Integration & External** : Contexte d'intégration

---

## 📊 Matrice de Traçabilité

| Concept | Source | Statut | Domaine | Priorité |
|---------|--------|--------|---------|----------|
| Vision produit | EDUNOVA_FUSION_MASTERPLAN.md | VALIDÉE | Stratégique | Haute |
| Principes non négociables | EDUNOVA_FUSION_MASTERPLAN.md | VALIDÉE | Stratégique | Haute |
| Domaines métier | EDUNOVA_FUSION_MASTERPLAN.md | VALIDÉE | Stratégique | Haute |
| Décisions D1-D44 | REGISTRE_DECISIONS_METIER | VALIDÉE | Tactique | Haute |
| Décisions canoniques | REGISTRE_DECISIONS_METIER | VALIDÉE | Tactique | Haute |
| Contrats métier V1 | CONTRATS_METIER_V1.md | PROPOSÉE | Opérationnel | Moyenne |
| Audit domaine scolaire | RAPPORT_AUDIT... | VALIDÉE | Opérationnel | Moyenne |

---

## 🎯 Prochaines Étapes

1. ✅ **Phase 1** : Inventaire documentaire - COMPLET
2. ✅ **Phase 2** : Extraction des décisions - EN COURS
3. [ ] **Phase 3** : Réconciliation métier
4. [ ] **Phase 4** : Analyse DDD complète
5. [ ] **Phase 5** : Reconstruction fonctionnelle
6. [ ] **Phase 6** : Validation de cohérence
7. [ ] **Phase 7** : Production documentaire

### Actions Immédiates

- [ ] Lire EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md
- [ ] Lire les rapports v1.2 clés
- [ ] Lire les contrats API v1
- [ ] Extraire les workflows complets
- [ ] Identifier toutes les contradictions
- [ ] Documenter les questions ouvertes

---

## 📝 Notes et Observations

### Forces du Projet
1. **Vision claire** : Masterplan bien structuré avec principes non négociables
2. **Décisions documentées** : Registre complet avec statuts clairs
3. **Approche DDD** : Utilisation de concepts DDD (bounded contexts, agrégats, etc.)
4. **Sécurité intégrée** : Isolation multi-tenant, traçabilité, audit
5. **Feuille de route réaliste** : Approche progressive et itérative

### Risques et Défis
1. **Complexité** : Nombre important de décisions et de domaines
2. **Contradictions potentielles** : Plusieurs sources pour certaines règles
3. **Implémentation partielle** : Certains concepts ne sont pas encore implémentés
4. **Décisions en attente** : Plusieurs points bloquants nécessitent arbitrage
5. **Intégrations externes** : Complexité technique et choix des fournisseurs

### Recommandations
1. **Prioriser les décisions en attente** : Résoudre les points bloquants (D45, BUL-TECH-*)
2. **Valider les propositions** : Obtenir validation pour PAR-REL-*
3. **Alignement code/décisions** : Vérifier que le code existant respecte les décisions validées
4. **Documentation continue** : Maintenir à jour le registre des décisions
5. **Tests systématiques** : Valider chaque règle métier avec des tests

---

**Document en cours de développement - Dernière mise à jour : [DATE]**
