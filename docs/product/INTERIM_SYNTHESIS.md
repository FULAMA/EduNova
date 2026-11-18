# EduNova - Synthèse Intérim de l'Analyse DDD

**Date** : 2025-XX-XX  
**Statut** : Analyse en cours (environ 30% complète)  
**Documents analysés** : 4/81 fichiers Markdown clés

---

## 📊 Résumé de l'État Actuel

### Documents Complètement Analysés
1. ✅ **EDUNOVA_FUSION_MASTERPLAN.md** (100% lu)
2. ✅ **docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md** (100% lu)
3. ✅ **docs/v1/DECISIONS_REQUISES.md** (100% lu)
4. ✅ **docs/v1/CONTRATS_METIER_V1.md** (100% lu)
5. ⏳ **docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md** (50% lu)
6. ⏳ **docs/reports/RAPPORT_AUDIT_DOMAINE_SCOLAIRE_2026-10-16.md** (100% lu)

### Documents Restants à Analyser
- 75 fichiers Markdown (rapports, plans de phase, audits, etc.)
- Code source (entités, repositories, use cases, migrations, tests)

---

## 🎯 Vision et Périmètre (d'après EDUNOVA_FUSION_MASTERPLAN.md)

### Vision Stratégique
EduNova Fusion vise à devenir une **plateforme éducative modulaire, sécurisée et accessible** avec 4 axes :
1. **AI-enabled** : IA utile, contextualisée, contrôlée et auditable
2. **Platform** : SaaS multi-établissements et extensible
3. **Africa-first** : Adaptée aux connexions instables, appareils modestes, réalités locales
4. **Automation with guardrails** : Automatiser sans déléguer les décisions sensibles

### Périmètre Fonctionnel
10 domaines métier identifiés :
- Identity & Access Management
- Academic Management
- Finance Management
- Communication & Notifications
- AI & Insights
- SaaS Platform (Tenancy & Establishments)
- Integration (API, webhooks, connecteurs)
- Identity Passport (Dossier scolaire portable)
- Offline & Sync
- Governance (Indicateurs, supervision)

### Architecture Cible
- **Court terme** : Monolithe modulaire avec couches claires
- **Moyen terme** : Validation SaaS avant ouverture commerciale
- **Long terme** : Extraction en services uniquement si contrainte mesurée le justifie

### Feuille de Route (7 Étapes)
1. **Étape 0** : Fiabiliser le socle actuel
2. **Étape 1** : Stabiliser la V1 scolaire
3. **Étape 2** : Valider les contrats d'API
4. **Étape 3** : Applications élève et parent
5. **Étape 4** : Communication et IA encadrée
6. **Étape 5** : Préparation commerciale SaaS
7. **Étape 6** : Interopérabilité et identité éducative
8. **Étape 7** : Écosystème et gouvernance

---

## 📋 Décisions Métier Validées (44/44 du Registre)

### 🎓 Domaine Académique (12 décisions)

| ID | Décision | Impact | Statut |
|----|----------|--------|--------|
| D1 | Seuil de réussite par matière configurable par établissement | Permet adaptation locale | ✅ VALIDÉE |
| D2 | Politique académique fixée à l'ouverture de la période | Garantit stabilité des calculs | ✅ VALIDÉE |
| D3 | Correction crée nouvelle version + historique | Traçabilité complète | ✅ VALIDÉE |
| D4 | Crédits académiques exclus du périmètre initial | Focus sur l'essentiel | ✅ VALIDÉE |
| D5 | Formule de moyenne configurable par établissement | Flexibilité pédagogique | ✅ VALIDÉE |
| D6 | Note manquante ≠ zéro | Distinction importante | ✅ VALIDÉE |
| D7 | Validation et publication configurable | Workflow adaptable | ✅ VALIDÉE |
| D8 | Correction après publication conserve historique | Audit complet | ✅ VALIDÉE |
| D9 | Modification de politique : pas de recalcul rétroactif automatique | Prévention des erreurs | ✅ VALIDÉE |
| D10 | Années scolaires et périodes : modèles officiels | Conformité réglementaire | ✅ VALIDÉE |
| D11 | Coefficients basés sur modèles officiels | Précision académique | ✅ VALIDÉE |
| D12 | Transferts : procédure configurable, historique obligatoire | Traçabilité des mouvements | ✅ VALIDÉE |

**Décisions Canoniques Bulletins** :
- **BUL-CAL-01** : Périodes configurables par profil académique ✅
- **BUL-PUB-01** : Délibération persistée avant publication ✅
- **BUL-COR-01** : Correction versionnée, ancienne en SUPERSEDED ✅
- **BUL-CALC-01** : Politique versionnée, arrondi explicite ✅ AVEC RÉSERVE
- **BUL-DOC-01** : PDF depuis snapshot immuable ✅
- **BUL-PROF-01** : Profils académiques versionnés ✅
- **BUL-SCOPE-01** : V1 couvre primaire, secondaire inférieur, humanités ✅

### 💰 Domaine Financier (5 décisions + 3 canoniques)

| ID | Décision | Impact | Statut |
|----|----------|--------|--------|
| D19 | Journal financier traçable | Audit complet des transactions | ✅ VALIDÉE |
| D20 | Barème de frais configurable et versionné | Flexibilité tarifaire | ✅ VALIDÉE |
| D21 | Responsabilités financières configurables | Adaptation aux rôles | ✅ VALIDÉE |
| D22 | Échéanciers configurables, arriérés calculés | Gestion des impayés | ✅ VALIDÉE |
| D23 | Tableau de bord financier complet | Visibilité pour la direction | ✅ VALIDÉE |

**Décisions Canoniques Finance** :
- **FIN-ROLE-01** : Finance accessible à DIRECTION, ACCOUNTANT, CASHIER ✅
- **FIN-COR-01** : Correction par contre-écriture, jamais suppression ✅
- **FIN-REC-01** : Reçu consultable et traçable ✅ AVEC RÉSERVES

### 👤 Domaine Identity & Access (6 décisions)

| ID | Décision | Impact | Statut |
|----|----------|--------|--------|
| D13 | Permissions configurables par établissement et rôle | RBAC flexible | ✅ VALIDÉE |
| D14 | Un compte = un rôle/contexte actif à la fois | Sécurité renforcée | ✅ VALIDÉE |
| D26 | Cycle de vie des comptes contrôlé | Gestion des accès | ✅ VALIDÉE |
| D27 | Authentification proportionnée au risque | Sécurité adaptative | ✅ VALIDÉE |
| D28 | Incidents de sécurité : processus structuré | Réponse aux incidents | ✅ VALIDÉE |
| D32 | Isolation multi-tenant à toutes les couches | Sécurité fondamentale | ✅ VALIDÉE |

### 🏗️ Domaine Infrastructure (14 décisions)

| ID | Décision | Catégorie | Statut |
|----|----------|-----------|--------|
| D25 | Mode hors ligne limité aux fonctions autorisées | Offline | ✅ VALIDÉE |
| D29 | Sauvegardes protégées et séparées | Résilience | ✅ VALIDÉE |
| D30 | Journaux d'audit pour opérations sensibles | Audit | ✅ VALIDÉE |
| D31 | Cycle de vie des données par catégorie | RGPD | ✅ VALIDÉE |
| D33 | Gestion des erreurs uniforme et classée | Fiabilité | ✅ VALIDÉE |
| D34 | Stratégie de tests multi-niveaux | Qualité | ✅ VALIDÉE |
| D35 | Déploiement contrôlé avec retour arrière | DevOps | ✅ VALIDÉE |
| D36 | Environnements strictement séparés | Sécurité | ✅ VALIDÉE |
| D37 | Dépendances inventoriées et verrouillées | Maintenance | ✅ VALIDÉE |
| D38 | Protection de la vie privée | RGPD | ✅ VALIDÉE |
| D39 | Exports gouvernés par rôle et finalité | Sécurité | ✅ VALIDÉE |
| D40 | Performance mesurée | Observabilité | ✅ VALIDÉE |
| D41 | Observabilité complète | Monitoring | ✅ VALIDÉE |
| D42 | Gouvernance des évolutions | Product | ✅ VALIDÉE |

### 📝 Domaine Numérisation (2 décisions)

| ID | Décision | Impact | Statut |
|----|----------|--------|--------|
| D43 | EduNova prend en charge la numérisation avec participation de l'école | Responsabilité claire | ✅ VALIDÉE (Choix A) |
| D44 | Priorité à l'année scolaire en cours, puis archives | Ordre de traitement | ✅ VALIDÉE (Choix A) |

---

## ⚠️ Décisions en Attente et Propositions

### ❌ En Attente de Validation (9 items)

| ID | Décision | Catégorie | Statut |
|----|----------|-----------|--------|
| D45 | Identification des personnes et prévention des doublons | Identity | ⏳ EN ATTENTE |
| BUL-REG-01 | Règles réglementaires propres aux niveaux | Academic | ⏳ EN ATTENTE |
| BUL-TECH-01 | Choix techniques de publication | Technical | ⏳ EN ATTENTE |
| BUL-TECH-02 | Autorisations de publication et correction | Finance | ⏳ EN ATTENTE |
| BUL-TECH-03 | Consultation des versions remplacées | Academic | ⏳ EN ATTENTE |
| BUL-TECH-04 | Révocation d'un bulletin émis | Academic | ⏳ EN ATTENTE |
| BUL-TECH-05 | Stockage et rétention du PDF | Technical | ⏳ EN ATTENTE |
| BUL-TECH-06 | Audit des émissions et téléchargements | Audit | ⏳ EN ATTENTE |
| D1-D12 (V1) | Décisions historiques | Various | ⚠️ Remplacées par canoniques |

### 📋 Propositions Non Validées (6 items)

| ID | Proposition | Catégorie | Statut |
|----|-------------|-----------|--------|
| PAR-REL-01 | Cardinalité parent-enfant (plusieurs parents/élèves) | Identity | 📝 PROPOSÉE |
| PAR-REL-02 | Validation du rattachement par direction | Identity | 📝 PROPOSÉE |
| PAR-REL-03 | Historique non destructif des rattachements | Identity | 📝 PROPOSÉE |
| PAR-REL-04 | Accès parent aux données scolaires | Identity | 📝 PROPOSÉE |
| PAR-REL-05 | Séparation avec StudentUserLink | Technical | ✅ TECHNIQUEMENT CONFIRMÉE |
| PAR-REL-06 | Accès parent aux bulletins officiels | Identity | 📝 PROPOSÉE |

---

## 🏗️ Modèle DDD Préliminaire

### Bounded Contexts Identifiés (10)

#### 1. **Identity & Access Management**
- **Responsabilité** : Gestion des identités, authentification, autorisation
- **Agrégats** : User, Role, Permission, Session, Tenant
- **Contexte** : Central, partagé
- **Décisions** : D13, D14, D26-D28, D32

#### 2. **Tenancy & Establishment Management**
- **Responsabilité** : Gestion des établissements (tenants)
- **Agrégats** : Tenant, Establishment, SchoolConfiguration
- **Contexte** : Fondation pour l'isolation
- **Décisions** : D2, D13, D32

#### 3. **Academic Management**
- **Responsabilité** : Années, périodes, classes, matières, inscriptions
- **Agrégats** : AcademicYear, AcademicPeriod, AcademicClass, Subject, Enrollment
- **Contexte** : Cœur éducatif
- **Décisions** : D1, D2, D10-D12, BUL-CAL-01, BUL-PROF-01, BUL-SCOPE-01

#### 4. **Student Management**
- **Responsabilité** : Gestion des élèves et dossiers
- **Agrégats** : Student, StudentAcademicRecord, AcademicDecision
- **Contexte** : Gestion des apprenants
- **Décisions** : D6, D12, D15-D18

#### 5. **Assessment & Grading**
- **Responsabilité** : Saisie des notes, calcul des moyennes
- **Agrégats** : Assessment, Grade, SubjectResult
- **Contexte** : Évaluation
- **Décisions** : D5-D9, BUL-CALC-01

#### 6. **Deliberation & Report Cards**
- **Responsabilité** : Délibération, génération bulletins
- **Agrégats** : Deliberation, ReportCard
- **Contexte** : Production de documents
- **Décisions** : D4, D7, D8, BUL-PUB-01, BUL-COR-01, BUL-DOC-01

#### 7. **Financial Management**
- **Responsabilité** : Frais, obligations, paiements, reçus
- **Agrégats** : FeeCatalogue, FeeObligation, Payment, Receipt, FinancialCredit
- **Contexte** : Gestion financière
- **Décisions** : D19-D23, FIN-ROLE-01, FIN-COR-01, FIN-REC-01

#### 8. **Communication & Notifications**
- **Responsabilité** : Notifications, annonces, préférences
- **Agrégats** : Notification, Announcement, NotificationPreference
- **Contexte** : Communication
- **Décisions** : D24

#### 9. **Integration & External Services**
- **Responsabilité** : Connexions avec services externes
- **Agrégats** : IntegrationConfiguration, ExternalServiceToken
- **Contexte** : Intégrations
- **Source** : EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md

#### 10. **Document Management**
- **Responsabilité** : Archivage des documents générés
- **Agrégats** : Document, DocumentVersion
- **Contexte** : Gestion des documents
- **Décisions** : BUL-DOC-01, FIN-REC-01

---

## 👥 Acteurs et Rôles

### Acteurs Principaux (7)

| Rôle | Description | Permissions Clés | Décisions |
|------|-------------|------------------|-----------|
| **ADMIN** | Administrateur système | Accès complet à son tenant | D13, D26-D28 |
| **DIRECTION** | Direction établissement | Gestion stratégique, validation | D13, D20-D23, FIN-ROLE-01 |
| **ACCOUNTANT** | Comptable | Gestion financière | FIN-ROLE-01, FIN-COR-01 |
| **CASHIER** | Caissier | Encaissement | FIN-ROLE-01, FIN-COR-01 |
| **PROF** | Enseignant | Saisie notes, présences | D13, D6-D9 |
| **PARENT** | Parent/Responsable | Consultation enfants | D16, PAR-REL-* (propositions) |
| **STUDENT** | Élève | Consultation personnelle | D16 |

### Matrice des Permissions (Préliminaire)

| Rôle \ Domaine | Identity | Academic | Finance | Communication | Integration |
|----------------|----------|----------|---------|---------------|-------------|
| ADMIN | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ Config |
| DIRECTION | ⚠️ Config | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ Config |
| ACCOUNTANT | ❌ | ❌ | ✅ CRUD | ❌ | ❌ |
| CASHIER | ❌ | ❌ | ✅ Confirm | ❌ | ❌ |
| PROF | ❌ | ✅ Ses classes | ❌ | ✅ Reçoit | ❌ |
| PARENT | ❌ | ✅ Enfants | ⚠️ Limité | ✅ Reçoit | ❌ |
| STUDENT | ❌ | ✅ Personnel | ❌ | ✅ Reçoit | ❌ |

**Légende** : ✅ = Accès complet, ⚠️ = Accès partiel, ❌ = Pas d'accès

---

## 📋 Contrats Métier (d'après CONTRATS_METIER_V1.md)

### A. Configuration d'Établissement

**Agrégat** : `SchoolConfiguration`
- **Racine** : SchoolConfiguration (`tenant_id`, identité, adresse, contacts, devise(s), statut, version)
- **Entités** : AcademicYear, AcademicPeriod
- **Value Objects** : SchoolIdentity, DateRange, CurrencyCode, AcademicYearStatus

**Invariants** :
1. Une configuration et un exercice appartiennent à un seul tenant
2. Les dates de l'exercice sont ordonnées
3. Les périodes d'un tenant ne se chevauchent pas sans règle explicite
4. Une classe, option ou matière ne peut être liée qu'à des objets du même tenant
5. Un exercice `CLOSED` n'accepte plus de modification ordinaire
6. Une modification administrative est versionnée
7. Les codes fonctionnels sont uniques dans le tenant

**Cas d'usage** :
- `CreateSchoolConfiguration`
- `UpdateSchoolConfiguration`
- `OpenAcademicYear`
- `CloseAcademicYear`
- `CreateAcademicPeriod`
- `UpdateAcademicPeriod`

### B. Bulletin PDF

**Agrégat** : `ReportCard`
- **Racine** : ReportCard (`tenant_id`, `student_id`, `academic_period_id`, `record_version`, `report_version`, statut, hash, date)
- **Value Objects** : ReportCardNumber, Percentage, ReportCardStatus, DocumentContent

**Règles de génération** :
1. Le dossier doit être `VALIDATED`
2. Version du dossier et période stables pendant la génération
3. Chaque ligne contient : note obtenue, maximum, note normalisée, coefficient, moyenne retenue
4. Total et moyenne suivent `AcademicPolicy`
5. Pourcentage = Score.value / Score.maximum * 100
6. Décision de délibération affichée seulement si délibération calculée pour la même version
7. Une correction produit un nouveau bulletin

**Statuts** : `DRAFT`, `GENERATING`, `ISSUED`, `SUPERSEDED`, `FAILED`

### C. Paiements et Reçus

**Agrégat** : `StudentAccount` / `BillingAccount`
- **Racine** : StudentAccount (`tenant_id`, `student_id`, statut)
- **Entités** : Charge, Payment, Receipt
- **Value Objects** : Money(amount, currency), CurrencyCode (USD/CDF), ReceiptNumber, IdempotencyKey

**Invariants Financiers** :
1. USD et CDF sont des devises distinctes ; aucune conversion implicite
2. Un montant est décimalisé avec précision définie par devise, jamais `float`
3. Un paiement ne peut être appliqué qu'au compte et tenant correspondants
4. Le montant alloué ne dépasse pas le solde disponible
5. Un paiement confirmé n'est pas supprimé ; correction par contre-écriture
6. Un reçu est unique dans le tenant et immuable après émission
7. Même IdempotencyKey renvoie le même résultat
8. Autorisation métier et tenant obligatoires

**Cas d'usage** :
- `CreateCharge`
- `RecordPayment`
- `ConfirmPayment`
- `CancelPayment`
- `IssueReceipt`
- `GetStudentBalance`

---

## 🔍 Analyse des Lacunes (d'après RAPPORT_AUDIT_DOMAINE_SCOLAIRE)

### État Actuel du Code

**Existant** :
- ✅ AcademicClass (nom, tenant, activation)
- ✅ AcademicOption (nom, code, tenant)
- ✅ AcademicPeriod (période datée tenant)
- ✅ ClassOption / ClassSubject (configuration de classe)
- ✅ StudentSummary (DTO de lecture)
- ✅ StudentAcademicRecord (résultats versionnés)
- ✅ Repositories SQLite avec filtre tenant
- ✅ Routes students/classes avec rôle ADMIN

**Manquant** :
- ❌ AcademicYear (modèle officiel)
- ❌ Enrollment (affectation élève-classe)
- ❌ Historique des changements de classe
- ❌ Gestion des doublons (D45 non résolue)
- ❌ Rattachement parent-enfant (PAR-REL-* non validé)

### Lacunes DDD Démontrées

1. **Contexte académique** : Gère la configuration mais pas l'agrégat d'inscription
2. **Élève** : DTO de lecture, pas un modèle métier complet
3. **AcademicPeriod** : N'est pas rattaché à une AcademicYear
4. **Intégrité** : Aucune contrainte ne garantit l'intégrité d'une affectation inexistante
5. **Frontend** : Consultation uniquement, pas de gestion

### Risques Identifiés

1. **Doublons** : Inventer un matricule ou fusion avant D45 pourrait confondre deux personnes
2. **Historique** : Ne conserver que la classe courante perdrait les transferts (contraire à D12)
3. **Année/Période** : Utiliser une période comme année violerait D10
4. **Tenant** : Référence simple vers `students.id` ne prouve pas la cohérence tenant
5. **Autorisation** : Routes actuelles ADMIN-only ; rôles d'inscription à confirmer

---

## 🚀 Prochaines Étapes

### Priorité Haute (À faire immédiatement)

1. **Compléter l'analyse**
   - Lire les 75 documents Markdown restants
   - Extraire toutes les règles métier
   - Identifier contradictions et écrasements de décisions

2. **Analyser le code source**
   - Examiner les entités, repositories, use cases existants
   - Comparer avec les décisions validées
   - Identifier les écarts

3. **Produire les documents finaux**
   - EDUNOVA_FUNCTIONAL_DDD_SPECIFICATION.md
   - EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md
   - EDUNOVA_DOMAIN_GLOSSARY.md

### Priorité Moyenne (À faire ensuite)

1. **Valider les contradictions**
   - Créer une matrice de cohérence
   - Identifier les décisions en conflit
   - Proposer des arbitrages

2. **Détailler les workflows**
   - Inscription d'un élève
   - Saisie et validation des notes
   - Délibération et publication
   - Paiement et émission de reçu

3. **Définir les cas limites**
   - Élève déjà inscrit
   - Note manquante
   - Paiement partiel
   - Transfert entre établissements

---

## 📊 Métriques de l'Analyse

| Catégorie | Total | Validées | En Attente | Proposées | Contradictions |
|-----------|-------|-----------|------------|-----------|----------------|
| Décisions | 56 | 44 | 9 | 6 | 0 (pour l'instant) |
| Domaines | 10 | 10 | 0 | 0 | 0 |
| Acteurs | 7 | 7 | 0 | 0 | 0 |
| Bounded Contexts | 10 | 10 | 0 | 0 | 0 |
| Documents analysés | 81 | 6 | 75 | 0 | 0 |

---

## ⚠️ Points Critiques à Résoudre

### Urgents (Bloquants)

1. **Décision 45** : Identification des personnes et prévention des doublons
   - Bloque l'implémentation des élèves
   - 3 options proposées, aucune validée
   - **Recommandation** : Valider Option A (identifiant interne + matricules existants)

2. **PAR-REL-01 à PAR-REL-06** : Modèle parent-enfant
   - Bloque la consultation parent
   - Propositions techniques confirmées mais non validées métier
   - **Impact** : Application parent non réalisable

### Importants (À clarifier)

3. **BUL-TECH-02 à BUL-TECH-06** : Décisions techniques bulletins
   - Stockage PDF, autorisations, révocation
   - Impact sur l'architecture et la conformité

4. **D1-D12 V1** : Décisions historiques
   - Certaines remplacées par des décisions canoniques
   - Vérifier que toutes les références sont mises à jour

5. **Contrats API** : Valider que les contrats implémentent les décisions
   - Vérifier la cohérence entre CONTRATS_METIER_V1.md et le code

---

## 🎯 Verdict Préliminaire

**Statut** : ⚠️ **EN COURS - 30% COMPLET**

### ✅ Ce qui est clair
- Vision produit solide et bien documentée
- 44 décisions métier validées et cohérentes
- Architecture DDD bien structurée
- Principes non négociables clairement définis
- Feuille de route réaliste

### ⚠️ Ce qui doit être clarifié
- 9 décisions en attente de validation
- 6 propositions parent-enfant non validées
- Intégration des décisions canoniques dans le code
- Cohérence entre les différents documents

### ❌ Ce qui manque
- Analyse complète de tous les documents (75 restants)
- Audit du code source par rapport aux décisions
- Identification de toutes les contradictions
- Définition complète des workflows
- Documentation des cas limites

---

**Document en cours - Dernière mise à jour : [DATE]**
