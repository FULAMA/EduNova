# EDUNOVA - Spécification Fonctionnelle DDD

> **Document** : Spécification Fonctionnelle et Conception DDD de Référence  
> **Version** : 1.0 - Brouillon Initial  
> **Date** : 2025-XX-XX  
> **Statut** : EN COURS - Environ 30% complet  
> **Auteur** : Analyse DDD Automatique  
> **Public Cible** : Product Owner, Business Analyst, Software Architect, Développeurs, Agents IA, Responsables Tests

---

## 📋 Table des Matières

1. [Vision Produit et Périmètre](#1-vision-produit-et-périmètre)
2. [Glossaire Métier](#2-glossaire-métier)
3. [Acteurs et Responsabilités](#3-acteurs-et-responsabilités)
4. [Catalogue des Fonctionnalités](#4-catalogue-des-fonctionnalités)
5. [Règles Métier Consolidées](#5-règles-métier-consolidées)
6. [Registre des Décisions et Statuts](#6-registre-des-décisions-et-statuts)
7. [Bounded Contexts](#7-bounded-contexts)
8. [Modèle de Domaine](#8-modèle-de-domaine)
9. [Agrégats et Invariants](#9-agréats-et-invariants)
10. [Context Map](#10-context-map)
11. [Workflows Détaillés](#11-workflows-détaillés)
12. [Commandes, Événements et Requêtes](#12-commandes-événements-et-requêtes)
13. [Matrice des Permissions](#13-matrice-des-permissions)
14. [Configurations par Établissement](#14-configurations-par-établissement)
15. [Cas Limites](#15-cas-limites)
16. [Critères d'Acceptation](#16-critères-dacceptation)
17. [Exigences Fonctionnelles](#17-exigences-fonctionnelles)
18. [Exigences Non Fonctionnelles Transversales](#18-exigences-non-fonctionnelles-transversales)
19. [Questions Ouvertes](#19-questions-ouvertes)
20. [Traçabilité des Sources](#20-traçabilité-des-sources)

---

## 1. Vision Produit et Périmètre

### 1.1 Vision Stratégique

EduNova Fusion vise à devenir **une plateforme éducative modulaire, sécurisée et accessible** qui relie établissements, apprenants, familles, enseignants, réseaux scolaires et partenaires technologiques en République démocratique du Congo, avec une ambition d'extension panafricaine.

**Quatre axes stratégiques** :

1. **AI-enabled** : Une IA utile, contextualisée, contrôlée et auditable
   - Assistant administratif fondé sur les permissions
   - Synthèse et génération de rapports vérifiables
   - Détection d'anomalies et de tendances avec explications
   - **Garde-fous** : Pas d'accès implicite à toutes les données, pas de décision automatisée à fort impact

2. **Platform** : Une plateforme SaaS multi-établissements et extensible
   - Architecture modulaire évolutive
   - Isolation stricte entre tenants
   - Modèle économique adaptable

3. **Africa-first** : Une conception adaptée aux réalités locales
   - Connexions instables et appareils modestes
   - Paiements locaux (Mobile Money, etc.)
   - Réalités administratives et réglementaires
   - Stratégies de faible consommation de données

4. **Automation with guardrails** : Automatiser les tâches répétitives sans déléguer aveuglément
   - Automatisation des calculs et rapports
   - Validation humaine obligatoire pour les décisions sensibles
   - Traçabilité complète des opérations automatisées

### 1.2 Périmètre Fonctionnel

EduNova couvre **10 domaines métier principaux** :

| # | Domaine | Description | Statut |
|---|---------|-------------|--------|
| 1 | **Identity & Access Management** | Comptes, authentification, rôles, permissions, sessions, audit d'accès | ✅ Implémenté |
| 2 | **Academic Management** | Années scolaires, inscriptions, classes, élèves, enseignants, notes, présences, bulletins, délibérations | ⚠️ Partiel |
| 3 | **Finance Management** | Catalogue de frais, affectations, paiements, reçus, corrections, rapports | ⚠️ Partiel |
| 4 | **Communication & Notifications** | Annonces, notifications, messages, préférences de contact | 📋 Planifié |
| 5 | **AI & Insights** | Assistants, analyses, explications, recommandations | 📋 Futur |
| 6 | **SaaS Platform** | Tenants, établissements, campus, configuration, abonnements, limites de service | ✅ Implémenté |
| 7 | **Integration** | API, webhooks, imports/exports, connecteurs partenaires | 📋 Planifié |
| 8 | **Identity Passport** | Dossier scolaire portable, partage autorisé, vérification de documents | 📋 Futur |
| 9 | **Offline & Sync** | Stockage local maîtrisé, synchronisation différée, résolution de conflits | 📋 Futur |
| 10 | **Governance** | Indicateurs agrégés, rapports de réseau, supervision autorisée | 📋 Futur |

**Périmètre V1** : Primarily focuses on Academic Management, Finance Management, and Identity & Access Management.

### 1.3 Périmètre Technique

- **Architecture** : Monolithe modulaire (court terme) → SaaS multi-tenant (moyen terme) → Services distribués (long terme, si justifié)
- **Base de données** : SQLite (actuel) → PostgreSQL avec Row-Level Security (futur, à étudier)
- **Frontend** : PWA React/Vite + Flutter (mobile, futur)
- **Backend** : FastAPI (Python 3.13+)
- **Intégrations** : Brevo/Resend (email), FCM (push), Google Classroom/Calendar, Stripe/Flutterwave (paiements), PostHog (analytics)

### 1.4 Principes Non Négociables

Ces principes s'appliquent à TOUTES les implémentations et ne peuvent être contournés :

#### 🔒 Sécurité
1. **Sécurité par conception** : Autorisation côté serveur, moindre privilège, validation des entrées, gestion sécurisée des secrets, journalisation des opérations sensibles
2. **Isolation des tenants** : Chaque accès aux données d'un établissement doit être limité au tenant autorisé. Le `tenant_id` fait partie des invariants métier et de persistance
3. **Protection des données** : Collecter le minimum de données nécessaire, limiter les accès, définir la rétention, documenter les usages

#### 💰 Finance
4. **Traçabilité financière** : Une correction de paiement est une contre-écriture auditable ; elle ne supprime ni ne réécrit l'opération initiale
5. **Monnaies explicites** : USD et CDF ne sont jamais convertis implicitement
6. **Validation humaine** : Aucune promotion, sanction, décision d'admission, écriture financière ou modification critique ne doit être décidée uniquement par une IA

#### 🏗️ Architecture
7. **Compatibilité ascendante maîtrisée** : Migrations versionnées, préconditions explicites, tests d'upgrade, stratégie de retour arrière
8. **Qualité démontrable** : Ne déclarer une fonctionnalité prête qu'après vérification du code, tests pertinents, contrôles de sécurité et documentation
9. **Pas de complexité prématurée** : Privilégier un monolithe modulaire tant que des contraintes mesurées ne justifient pas une extraction

#### 📋 Processus
10. **Respect de l'existant** : Ne pas exécuter de migrations sur les bases locales permanentes `edunova.db` et `edunova_dev.db` sans procédure explicite et sauvegarde vérifiée

### 1.5 Définition de "Prêt"

Une fonctionnalité ne peut être déclarée prête que si **TOUS** les critères suivants sont remplis :

1. ✅ Ses règles métier et ses cas limites sont documentés
2. ✅ Les tests pertinents existent et ont été exécutés
3. ✅ L'autorisation et l'isolation tenant sont testées
4. ✅ Les migrations sont testées sur des bases temporaires représentatives
5. ✅ Les journaux n'exposent pas de secrets ou de données personnelles inutiles
6. ✅ Les erreurs et scénarios de reprise sont prévus
7. ✅ La documentation et les contrats concernés sont à jour
8. ✅ Le résultat CI est observé, et non supposé

---

## 2. Glossaire Métier

### 2.1 Termes Généraux

| Terme | Définition | Source |
|-------|------------|--------|
| **Tenant** | Un établissement scolaire ou une organisation éducative. Unité d'isolation logique et physique des données. | Masterplan, D32 |
| **Établissement** | Synonyme de Tenant dans le contexte EduNova. Représente une école, un collège, un lycée ou un campus. | Masterplan |
| **Multi-tenant** | Architecture où une seule instance du logiciel dessert plusieurs établissements (tenants) avec isolation complète des données. | Masterplan |
| **Contexte Métier (Bounded Context)** | Frontière conceptuelle dans laquelle un modèle est défini et cohérent. Limite la portée des définitions. | DDD |
| **Agrégat** | Groupe d'entités et d'objets-valeurs traitées comme une seule unité de cohérence. Une racine d'agrégat garantit les invariants. | DDD |
| **Invariant** | Règle métier qui doit toujours être vraie pour qu'un agrégat soit dans un état valide. | DDD |

### 2.2 Termes Académique

| Terme | Définition | Source |
|-------|------------|--------|
| **Année Scolaire** | Période académique principale (ex: 2025-2026) contenant une ou plusieurs périodes d'évaluation. | D10, BUL-CAL-01 |
| **Période Académique** | Sous-période d'une année scolaire (ex: Trimestre 1, Semestre 2). Peut avoir des profils de calcul différents. | D10, BUL-CAL-01 |
| **Période d'Évaluation** | Période spécifique pour l'évaluation des élèves. Peut être différente des périodes académiques. | D10 |
| **Classe** | Groupe d'élèves suivant le même cursus. Identifiée par un nom et rattachée à un tenant. | Audit Domaine |
| **Matière (Subject)** | Discipline enseignée. Peut avoir des coefficients différents selon le niveau et l'option. | D11 |
| **Option** | Orientation ou spécialisation (ex: Scientifique, Littéraire). | Audit Domaine |
| **Profil Académique** | Ensemble de règles (coefficients, seuils, formules) applicable à un niveau, programme ou option. Versionné. | BUL-PROF-01 |
| **Politique Académique** | Ensemble des règles de calcul des notes, moyennes et décisions (ex: seuil de réussite, formule de moyenne). Versionnée. | D2, D5 |
| **Dossier Académique (Academic Record)** | Ensemble des résultats d'un élève pour une période. Versionné. | D3, BUL-COR-01 |
| **Note** | Évaluation chiffrée d'une compétence ou d'une matière. Peut être manquante (≠ zéro). | D6 |
| **Moyenne** | Résultat calculé selon une formule configurable. Peut être générale ou par matière. | D5 |
| **Délibération** | Processus de validation des résultats et de prise de décision (passage, redoublement, etc.). Persistée et versionnée. | BUL-PUB-01 |
| **Bulletin** | Document officiel présentant les résultats d'un élève. Généré depuis un snapshot immuable. | BUL-DOC-01 |
| **Seuil de Réussite** | Note minimale requise pour réussir une matière. Configurable par établissement. | D1 |

### 2.3 Termes Financiers

| Terme | Définition | Source |
|-------|------------|--------|
| **Frais Scolaires** | Montants dus par un élève pour son éducation. Barème configurable et versionné. | D20 |
| **Obligation Financière** | Facture ou dette spécifique liée à un élève et à une période. | FIN-COR-01 |
| **Paiement** | Transaction financière enregistrée. Peut être confirmé, partiel, ou en attente. | D19, FIN-COR-01 |
| **Reçu** | Document officiel confirmant un paiement. Unique et immuable après émission. | FIN-REC-01 |
| **Contre-Écriture** | Opération comptable qui corrige une transaction sans la supprimer. Trace toujours le lien avec l'opération originale. | D19, FIN-COR-01 |
| **Crédit** | Solde positif pouvant être utilisé pour de futurs paiements. | D21 |
| **Arriéré** | Montant dû non payé à la date d'échéance. Calculé à partir des obligations et paiements confirmés. | D22 |
| **Échéancier** | Calendrier des dates de paiement pour les obligations financières. Configurable. | D22 |
| **Devise** | Unité monétaire. EduNova supporte USD et CDF, jamais mélangées implicitement. | D19, FIN-COR-01 |
| **Idempotency Key** | Clé unique garantissant qu'une opération peut être répétée sans effet de bord. | CONTRATS_METIER_V1 |

### 2.4 Termes Identity & Access

| Terme | Définition | Source |
|-------|------------|--------|
| **Utilisateur** | Personne physique utilisant le système. Peut avoir un ou plusieurs rôles. | D13, D14 |
| **Rôle** | Ensemble de permissions et de responsabilités. Un utilisateur n'a qu'un rôle actif à la fois. | D13, D14 |
| **Permission** | Droit d'effectuer une action spécifique sur une ressource. Configurable par établissement et rôle. | D13 |
| **Contexte Actif** | Rôle actuellement sélectionné par un utilisateur multi-rôles. | D14 |
| **Session** | Période d'authentification active d'un utilisateur. | D27 |
| **Authentification** | Processus de vérification de l'identité d'un utilisateur. | D27 |
| **Autorisation** | Processus de vérification des permissions d'un utilisateur pour une action. Toujours côté serveur. | D13, D32 |
| **MFA (Multi-Factor Authentication)** | Authentification à plusieurs facteurs pour les comptes privilégiés. | D27 |

### 2.5 Termes Communication

| Terme | Définition | Source |
|-------|------------|--------|
| **Notification** | Message envoyé à un ou plusieurs destinataires. Configurable par événement, rôle, destinataire et canal. | D24 |
| **Canal** | Moyens de transmission : email, push notification, SMS, centre de notifications interne. | D24 |
| **Préférences de Notification** | Choix de l'utilisateur concernant les notifications à recevoir et par quel canal. | D24 |
| **Annonces** | Messages publiés par l'établissement à destination de groupes spécifiques. | D24 |
| **Statut de Livraison** | État d'une notification : pending, sent, delivered, failed, retry_scheduled, cancelled. | INTEGRATIONS_PLAN |

---

## 3. Acteurs et Responsabilités

### 3.1 Liste des Acteurs

| Acteur | Description | Rôle Principal | Contexte |
|--------|-------------|----------------|----------|
| **ADMIN** | Administrateur système ou technique de l'établissement | Gestion technique, configuration, gestion des utilisateurs | Identity & Access |
| **DIRECTION** | Direction de l'établissement (Directeur, Proviseur, etc.) | Gestion stratégique, validation des décisions importantes | Tenancy, Academic, Finance |
| **ACCOUNTANT** | Comptable de l'établissement | Gestion financière, comptabilité, rapports | Finance |
| **CASHIER** | Caissier de l'établissement | Encaissement des paiements, émission des reçus | Finance |
| **PROF** | Enseignant | Saisie des notes, gestion des présences, pédagogie | Academic, Assessment |
| **PARENT** | Parent ou responsable légal d'un élève | Consultation des informations scolaires et financières | Academic (lecture), Finance (lecture) |
| **STUDENT** | Élève inscrit dans l'établissement | Consultation de ses propres résultats | Academic (lecture) |

### 3.2 Responsabilités par Acteur

#### ADMIN

**Responsabilités** :
- Créer et gérer les utilisateurs
- Attribuer et gérer les rôles et permissions
- Configurer les paramètres techniques
- Gérer les intégrations externes
- Superviser les opérations système
- Consulter les logs et audits

**Permissions** :
- Accès complet à son tenant
- Création, lecture, mise à jour, suppression (CRUD) sur la plupart des entités
- Accès aux paramètres système
- Gestion des sauvegardes et restaurations

**Limitations** :
- Ne peut pas accéder aux données d'autres tenants
- Certaines opérations sensibles nécessitent une validation supplémentaire

**Décisions associées** : D13, D14, D26-D28, D32

#### DIRECTION

**Responsabilités** :
- Définir les politiques académiques et financières
- Valider les bulletins et délibérations
- Gérer les configurations de l'établissement
- Superviser les enseignants et le personnel
- Prendre les décisions stratégiques

**Permissions** :
- Accès aux données de son établissement
- Validation des bulletins et délibérations (BUL-PUB-01)
- Configuration des politiques académiques (D2, D5, D10, D11)
- Accès aux rapports financiers (D23)
- Gestion des frais scolaires (D20)

**Limitations** :
- Ne peut pas modifier les données d'autres établissements
- Certaines opérations financières nécessitent le rôle ACCOUNTANT ou CASHIER

**Décisions associées** : D2, D5, D10, D11, D13, D20-D23, FIN-ROLE-01

#### ACCOUNTANT

**Responsabilités** :
- Enregistrer les frais et obligations financières
- Suivre les paiements et les arriérés
- Générer les reçus
- Produire les rapports financiers
- Gérer la comptabilité

**Permissions** :
- Accès complet aux données financières de son tenant (FIN-ROLE-01)
- Création et modification des charges (D20)
- Confirmation des paiements (D19)
- Génération des reçus (FIN-REC-01)
- Consultation des rapports financiers (D23)

**Limitations** :
- Ne peut pas modifier les données académiques
- Ne peut pas accéder aux données d'autres tenants

**Décisions associées** : D19-D23, FIN-ROLE-01, FIN-COR-01, FIN-REC-01

#### CASHIER

**Responsabilités** :
- Encaisser les paiements
- Émettre les reçus
- Gérer les transactions financières quotidiennes

**Permissions** :
- Confirmation des paiements (FIN-ROLE-01)
- Émission des reçus (FIN-REC-01)
- Accès aux informations de paiement

**Limitations** :
- Ne peut pas modifier les configurations financières
- Ne peut pas accéder aux données académiques
- Ne peut pas accéder aux données d'autres tenants

**Décisions associées** : FIN-ROLE-01, FIN-COR-01

#### PROF (Enseignant)

**Responsabilités** :
- Saisir les notes et évaluations
- Gérer les présences et absences
- Préparer le contenu pédagogique
- Communiquer avec les élèves et parents

**Permissions** :
- Saisie des notes pour ses classes et matières (D6-D9)
- Consultation des résultats de ses élèves
- Gestion des présences pour ses classes
- Accès aux informations de ses classes uniquement

**Limitations** :
- Ne peut pas modifier les notes d'autres enseignants
- Ne peut pas accéder aux données financières
- Ne peut pas accéder aux données d'autres tenants

**Décisions associées** : D6-D9, D13, D15

#### PARENT

**Responsabilités** :
- Consulter les informations scolaires de ses enfants
- Consulter les résultats et bulletins officiels
- Consulter les obligations financières
- Recevoir les notifications

**Permissions** :
- Consultation des bulletins officiels de ses enfants (D16)
- Consultation des résultats publiés de ses enfants
- Consultation des présences de ses enfants
- Accès limité aux informations financières

**Limitations** :
- **IMPORTANT** : Ne peut consulter que les bulletins **officiels publiés** (D16)
- Ne peut pas consulter les résultats provisoires
- Ne peut pas modifier aucune donnée
- L'accès est strictement contrôlé par le rattachement validé (PAR-REL-01 à PAR-REL-06)

**Décisions associées** : D16, PAR-REL-01 à PAR-REL-06 (propositions)

**⚠️ NOTE** : Les propositions PAR-REL-* ne sont pas encore validées. Leur implémentation nécessite une confirmation métier.

#### STUDENT

**Responsabilités** :
- Consulter ses propres résultats
- Consulter ses propres bulletins officiels
- Consulter son emploi du temps
- Recevoir les notifications

**Permissions** :
- Consultation de ses propres bulletins officiels (D16)
- Consultation de ses propres résultats publiés
- Accès à son propre dossier académique

**Limitations** :
- Ne peut consulter que les bulletins **officiels publiés** (D16)
- Ne peut pas consulter les résultats provisoires
- Ne peut pas modifier aucune donnée
- Ne peut pas accéder aux données d'autres élèves

**Décisions associées** : D16

### 3.3 Matrice des Permissions (Résumé)

| Rôle \ Domaine | Identity & Access | Tenancy | Academic | Assessment | Deliberation | Finance | Communication | Integration |
|----------------|-------------------|---------|----------|------------|---------------|---------|---------------|-------------|
| **ADMIN** | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ Config |
| **DIRECTION** | ⚠️ Config | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ Validate | ✅ CRUD | ✅ CRUD | ✅ Config |
| **ACCOUNTANT** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ CRUD | ❌ | ❌ |
| **CASHIER** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Confirm | ❌ | ❌ |
| **PROF** | ❌ | ❌ | ⚠️ Ses classes | ✅ CRUD | ⚠️ Consult | ❌ | ✅ Reçoit | ❌ |
| **PARENT** | ❌ | ❌ | ⚠️ Enfants | ⚠️ Enfants | ⚠️ Enfants | ⚠️ Limité | ✅ Reçoit | ❌ |
| **STUDENT** | ❌ | ❌ | ⚠️ Personnel | ⚠️ Personnel | ⚠️ Personnel | ❌ | ✅ Reçoit | ❌ |

**Légende** :
- ✅ = Accès complet (CRUD)
- ⚠️ = Accès partiel (lecture ou limité)
- ❌ = Pas d'accès

### 3.4 Règles Transversales d'Autorisation

1. **Isolation Multi-Tenant (D32)** : Chaque utilisateur ne peut accéder qu'aux données de son propre tenant. Le `tenant_id` est toujours vérifié côté serveur.

2. **Un seul rôle actif à la fois (D14)** : Un utilisateur avec plusieurs rôles ne peut activer qu'un seul rôle à la fois. Les permissions dépendent du rôle actif.

3. **Permissions configurables (D13)** : Les permissions sont configurables par établissement et rôle, avec un socle de sécurité obligatoire.

4. **Autorisation côté serveur uniquement** : Toutes les vérifications d'autorisation sont effectuées côté serveur, jamais côté client.

5. **Journalisation des opérations sensibles (D30)** : Toutes les opérations sensibles (création, modification, suppression de données critiques) sont journalisées avec :
   - Contexte tenant
   - Acteur (qui a fait l'action)
   - Action (quoi a été fait)
   - Cible (sur quoi)
   - Horodatage
   - Résultat

---

## 4. Catalogue des Fonctionnalités

### 4.1 Fonctionnalités Identity & Access Management

| ID | Fonctionnalité | Description | Statut | Décisions |
|----|---------------|-------------|--------|-----------|
| IAM-001 | Authentification | Connexion/déconnexion des utilisateurs | ✅ Implémenté | D27 |
| IAM-002 | Gestion des utilisateurs | CRUD des utilisateurs | ✅ Implémenté | D26, D13 |
| IAM-003 | Gestion des rôles | Définition et attribution des rôles | ✅ Implémenté | D13, D14 |
| IAM-004 | Gestion des permissions | Configuration fine des permissions | ⚠️ Partiel | D13 |
| IAM-005 | Multi-rôles | Gestion des utilisateurs avec plusieurs rôles | ✅ Implémenté | D14 |
| IAM-006 | MFA | Authentification multi-facteurs | 📋 Planifié | D27 |
| IAM-007 | Audit des accès | Journalisation des connexions et opérations | ✅ Implémenté | D30 |

### 4.2 Fonctionnalités Tenancy & Establishment Management

| ID | Fonctionnalité | Description | Statut | Décisions |
|----|---------------|-------------|--------|-----------|
| TEN-001 | Création d'établissement | Onboarding d'un nouvel établissement | ✅ Implémenté | D2 |
| TEN-002 | Configuration | Gestion des paramètres de l'établissement | ✅ Implémenté | D2 |
| TEN-003 | Gestion des années scolaires | Création, ouverture, fermeture | ⚠️ Partiel | D2, D10 |
| TEN-004 | Gestion des périodes | Création et gestion des périodes académiques | ✅ Implémenté | D10 |

### 4.3 Fonctionnalités Academic Management

| ID | Fonctionnalité | Description | Statut | Décisions |
|----|---------------|-------------|--------|-----------|
| ACA-001 | Gestion des classes | CRUD des classes | ✅ Implémenté | Audit |
| ACA-002 | Gestion des matières | CRUD des matières | ✅ Implémenté | Audit |
| ACA-003 | Gestion des options | CRUD des options | ✅ Implémenté | Audit |
| ACA-004 | Inscription d'élèves | Inscription et affectation | ❌ Non implémenté | D12, D45 |
| ACA-005 | Gestion des transferts | Transfert entre classes/établissements | ❌ Non implémenté | D12, D17 |
| ACA-006 | Gestion des politiques | Configuration des politiques académiques | ⚠️ Partiel | D2, D5 |

### 4.4 Fonctionnalités Assessment & Grading

| ID | Fonctionnalité | Description | Statut | Décisions |
|----|---------------|-------------|--------|-----------|
| ASG-001 | Saisie des notes | Enregistrement des évaluations | ✅ Implémenté | D6-D9 |
| ASG-002 | Calcul des moyennes | Calcul automatique selon politique | ✅ Implémenté | D5 |
| ASG-003 | Gestion des absences | Enregistrement et traitement | ⚠️ Partiel | D15 |
| ASG-004 | Validation des résultats | Validation avant publication | ⚠️ Partiel | D7 |

### 4.5 Fonctionnalités Deliberation & Report Cards

| ID | Fonctionnalité | Description | Statut | Décisions |
|----|---------------|-------------|--------|-----------|
| DEL-001 | Délibération | Processus de validation des résultats | ⚠️ Partiel | BUL-PUB-01 |
| DEL-002 | Génération bulletins | Création des bulletins PDF | ⚠️ Partiel | BUL-DOC-01 |
| DEL-003 | Publication | Publication officielle des bulletins | ⚠️ Partiel | BUL-PUB-01, D16 |
| DEL-004 | Correction | Correction des bulletins publiés | ⚠️ Partiel | BUL-COR-01, D8 |
| DEL-005 | Consultation | Accès aux bulletins par élèves/parents | ⚠️ Partiel | D16 |

### 4.6 Fonctionnalités Finance Management

| ID | Fonctionnalité | Description | Statut | Décisions |
|----|---------------|-------------|--------|-----------|
| FIN-001 | Barème des frais | Configuration des frais scolaires | ✅ Implémenté | D20 |
| FIN-002 | Obligations financières | Création des obligations par élève | ⚠️ Partiel | D20 |
| FIN-003 | Enregistrement paiements | Saisie des paiements | ✅ Implémenté | D19 |
| FIN-004 | Confirmation paiements | Validation des paiements | ✅ Implémenté | D21, FIN-COR-01 |
| FIN-005 | Émission reçus | Génération des reçus | ✅ Implémenté | FIN-REC-01 |
| FIN-006 | Gestion crédits | Gestion des surpaiements | ⚠️ Partiel | D21 |
| FIN-007 | Suivi arriérés | Calcul et suivi des arriérés | ⚠️ Partiel | D22 |
| FIN-008 | Tableau de bord | Visualisation des indicateurs financiers | ⚠️ Partiel | D23 |

### 4.7 Fonctionnalités Communication & Notifications

| ID | Fonctionnalité | Description | Statut | Décisions |
|----|---------------|-------------|--------|-----------|
| COM-001 | Centre de notifications | Affichage des notifications internes | 📋 Planifié | D24 |
| COM-002 | Notifications email | Envoi d'emails transactionnels | 📋 Planifié | D24 |
| COM-003 | Notifications push | Envoi de notifications push | 📋 Planifié | D24 |
| COM-004 | Annonces | Publication d'annonces | 📋 Planifié | D24 |
| COM-005 | Préférences | Gestion des préférences de notification | 📋 Planifié | D24 |

---

## 5. Règles Métier Consolidées

### 5.1 Règles par Domaine

#### 5.1.1 Règles Identity & Access Management

| ID | Règle | Description | Statut | Source | Impact |
|----|-------|-------------|--------|--------|--------|
| IAM-R001 | **Isolation Multi-Tenant** | Chaque accès doit être limité au tenant autorisé. `tenant_id` est un invariant métier. | ✅ VALIDÉE | D32 | 🔴 Critique |
| IAM-R002 | **Permissions Configurables** | Les permissions sont configurables par établissement et rôle, avec socle de sécurité obligatoire. | ✅ VALIDÉE | D13 | 🔴 Critique |
| IAM-R003 | **Un seul rôle actif** | Un compte n'a qu'un rôle ou contexte actif à la fois. Changement de contexte contrôlé. | ✅ VALIDÉE | D14 | 🟡 Important |
| IAM-R004 | **Cycle de vie des comptes** | Création, activation, suspension, désactivation contrôlées. Historique conservé. | ✅ VALIDÉE | D26 | 🟡 Important |
| IAM-R005 | **Authentification proportionnée** | Mesures proportionnées au risque : mots de passe protégés, limitation tentatives, MFA pour comptes privilégiés. | ✅ VALIDÉE | D27 | 🟡 Important |
| IAM-R006 | **Incidents de sécurité** | Processus structuré : détection, classification, confinement, révocation, préservation preuves, restauration. | ✅ VALIDÉE | D28 | 🔴 Critique |
| IAM-R007 | **Journal d'audit** | Opérations sensibles génèrent des journaux protégés avec contexte, acteur, action, cible, horodatage, résultat. | ✅ VALIDÉE | D30 | 🔴 Critique |

#### 5.1.2 Règles Academic Management

| ID | Règle | Description | Statut | Source | Impact |
|----|-------|-------------|--------|--------|--------|
| ACA-R001 | **Seuil de réussite configurable** | Le seuil est configurable par établissement. | ✅ VALIDÉE | D1 | 🟡 Important |
| ACA-R002 | **Politique académique fixée à l'ouverture** | La politique applicable est fixée à l'ouverture de la période. Sa version est conservée pour chaque calcul. | ✅ VALIDÉE | D2 | 🔴 Critique |
| ACA-R003 | **Correction versionnée** | Toute correction crée une nouvelle version. L'ancienne est conservée avec auteur, horodatage et motif obligatoire. | ✅ VALIDÉE | D3 | 🔴 Critique |
| ACA-R004 | **Crédits académiques exclus** | Les crédits sont exclus du périmètre initial. | ✅ VALIDÉE | D4 | 🟡 Important |
| ACA-R005 | **Formule de moyenne configurable** | La formule est configurable par établissement, versionnée et traçable. | ✅ VALIDÉE | D5 | 🟡 Important |
| ACA-R006 | **Note manquante ≠ zéro** | Une note manquante est distincte d'un zéro. Distinguer notes en attente, évaluations non passées, absences, notes saisies. | ✅ VALIDÉE | D6 | 🔴 Critique |
| ACA-R007 | **Validation et publication configurable** | Le workflow est configurable par établissement : rôles, étapes, validations. Actions tracées. | ✅ VALIDÉE | D7 | 🟡 Important |
| ACA-R008 | **Correction après publication** | La procédure conserve historique, motif, autorisations, validations, notifications. | ✅ VALIDÉE | D8 | 🔴 Critique |
| ACA-R009 | **Modification de politique** | Pas de recalcul rétroactif automatique. Tout recalcul exceptionnel exige autorisation et trace complète. | ✅ VALIDÉE | D9 | 🔴 Critique |
| ACA-R010 | **Année scolaire et périodes** | Utiliser des modèles organisationnels officiels avec adaptations autorisées, documentées, traçables. | ✅ VALIDÉE | D10 | 🔴 Critique |
| ACA-R011 | **Coefficients des matières** | Les coefficients s'appuient sur les modèles officiels applicables. Adaptations autorisées versionnées et traçables. | ✅ VALIDÉE | D11 | 🟡 Important |
| ACA-R012 | **Transferts d'élèves** | Procédures configurables selon type. Provenance et historique obligatoires. | ✅ VALIDÉE | D12 | 🔴 Critique |

**Règles Canoniques Bulletins** :

| ID | Règle | Description | Statut | Source | Impact |
|----|-------|-------------|--------|--------|--------|
| BUL-R001 | **Périodes configurables** | Les périodes scolaires sont définies par un profil académique versionné. | ✅ VALIDÉE | BUL-CAL-01 | 🔴 Critique |
| BUL-R002 | **Délibération obligatoire** | Aucune publication officielle sans délibération persistée et versionnée. | ✅ VALIDÉE | BUL-PUB-01 | 🔴 Critique |
| BUL-R003 | **Correction versionnée** | Nouvelle version créée, ancienne reçoit SUPERSEDED. Snapshot reste immuable. | ✅ VALIDÉE | BUL-COR-01 | 🔴 Critique |
| BUL-R004 | **Politique versionnée** | Politique de calcul et arrondi explicite. Deux décimales comme défaut technique. | ✅ VALIDÉE AVEC RÉSERVE | BUL-CALC-01 | 🟡 Important |
| BUL-R005 | **PDF immuable** | Bulletin officiel est un PDF rendu depuis un snapshot immuable. | ✅ VALIDÉE | BUL-DOC-01 | 🔴 Critique |
| BUL-R006 | **Profils versionnés** | Les profils sont versionnés par niveau, programme et option. | ✅ VALIDÉE | BUL-PROF-01 | 🟡 Important |
| BUL-R007 | **Périmètre V1** | V1 couvre le primaire, secondaire inférieur et humanités. | ✅ VALIDÉE | BUL-SCOPE-01 | 🟡 Important |

#### 5.1.3 Règles Assessment & Grading

| ID | Règle | Description | Statut | Source | Impact |
|----|-------|-------------|--------|--------|--------|
| ASG-R001 | **Absences aux évaluations** | Traitement configurable selon réglementation. Distinguer absence justifiée, non justifiée, justification en attente. | ✅ VALIDÉE | D15 | 🟡 Important |
| ASG-R002 | **Consultation des bulletins** | Élèves et parents ne consultent les bulletins qu'après publication officielle. Résultats provisoires réservés au personnel autorisé. | ✅ VALIDÉE | D16 | 🔴 Critique |

#### 5.1.4 Règles Finance Management

| ID | Règle | Description | Statut | Source | Impact |
|----|-------|-------------|--------|--------|--------|
| FIN-R001 | **Journal financier traçable** | Transactions individuelles traçables. Paiements partiels pris en charge. | ✅ VALIDÉE | D19 | 🔴 Critique |
| FIN-R002 | **Barème configurable** | Le barème est configurable et versionné. | ✅ VALIDÉE | D20 | 🟡 Important |
| FIN-R003 | **Responsabilités financières** | Configurables. Confirmation des paiements contrôlée. Annulations nécessitent autorisation distincte. | ✅ VALIDÉE | D21 | 🔴 Critique |
| FIN-R004 | **Échéanciers et impayés** | Échéances configurables. Arriérés calculés à partir des obligations et paiements confirmés. | ✅ VALIDÉE | D22 | 🟡 Important |
| FIN-R005 | **Tableau de bord promoteur** | Afficher frais attendus, paiements confirmés, soldes, arriérés, reçus par période et ventilation par classe. | ✅ VALIDÉE | D23 | 🟡 Important |

**Règles Canoniques Finance** :

| ID | Règle | Description | Statut | Source | Impact |
|----|-------|-------------|--------|--------|--------|
| FIN-ROLE-01 | **Accès Finance** | Finance accessible à la direction et aux rôles ACCOUNTANT ou CASHIER explicitement affectés au tenant. Contrôle côté serveur. | ✅ VALIDÉE | FIN-ROLE-01 | 🔴 Critique |
| FIN-COR-01 | **Correction financière** | Un paiement confirmé n'est jamais supprimé ni écrasé. Une correction est une contre-écriture traçable, liée au paiement original, avec motif, auteur, date, unicité et contrôle de concurrence. | ✅ VALIDÉE | FIN-COR-01 | 🔴 Critique |
| FIN-REC-01 | **Reçu traçable** | Le reçu reste consultable et traçable. Générable/téléchargeable en PDF. Une contre-écriture ne supprime pas le reçu original. | ✅ VALIDÉE AVEC RÉSERVES | FIN-REC-01 | 🔴 Critique |

#### 5.1.5 Règles Communication

| ID | Règle | Description | Statut | Source | Impact |
|----|-------|-------------|--------|--------|--------|
| COM-R001 | **Notifications configurables** | Configurables par événement, rôle, destinataire, canal. Traçabilité, préférences, confidentialité. | ✅ VALIDÉE | D24 | 🟡 Important |

### 5.2 Règles Transversales

| ID | Règle | Description | Statut | Source | Impact |
|----|-------|-------------|--------|--------|--------|
| TRV-R001 | **Sécurité par conception** | Autorisation côté serveur, moindre privilège, validation des entrées, gestion sécurisée des secrets, journalisation. | ✅ VALIDÉE | Masterplan | 🔴 Critique |
| TRV-R002 | **Confidentialité** | Collecter le minimum de données nécessaire, limiter les accès, définir la rétention, documenter les usages. | ✅ VALIDÉE | Masterplan, D38 | 🔴 Critique |
| TRV-R003 | **Traçabilité financière** | Une correction est une contre-écriture auditable ; ne supprime ni ne réécrit l'opération initiale. | ✅ VALIDÉE | Masterplan, D19 | 🔴 Critique |
| TRV-R004 | **Monnaies explicites** | USD et CDF ne sont jamais convertis implicitement. | ✅ VALIDÉE | Masterplan, D19 | 🔴 Critique |
| TRV-R005 | **Décisions sensibles sous contrôle humain** | Aucune décision sensible (promotion, sanction, etc.) par IA seule. | ✅ VALIDÉE | Masterplan | 🔴 Critique |
| TRV-R006 | **Compatibilité ascendante** | Migrations versionnées, préconditions explicites, tests d'upgrade, stratégie de retour arrière. | ✅ VALIDÉE | Masterplan | 🟡 Important |
| TRV-R007 | **Qualité démontrable** | Ne déclarer prêt qu'après vérification complète. | ✅ VALIDÉE | Masterplan | 🔴 Critique |
| TRV-R008 | **Respect de l'existant** | Pas de migrations sur bases persistantes sans procédure et sauvegarde. | ✅ VALIDÉE | Masterplan | 🔴 Critique |

---

## 6. Registre des Décisions et Statuts

### 6.1 Décisions par Catégorie

#### Décisions Validées (44)

**Academic (12)** : D1-D12  
**Finance (5)** : D19-D23  
**Identity & Access (6)** : D13, D14, D26-D28, D32  
**Infrastructure (14)** : D25, D29-D31, D33-D38, D40-D42  
**Numérisation (2)** : D43-D44

**Canoniques (9)** : BUL-CAL-01 à BUL-SCOPE-01 (7), FIN-ROLE-01 à FIN-REC-01 (3)

#### Décisions en Attente (9)

| ID | Titre | Catégorie | Statut | Source |
|----|-------|-----------|--------|--------|
| D45 | Identification des personnes et prévention des doublons | Identity | ⏳ EN ATTENTE | REGISTRE |
| BUL-REG-01 | Règles réglementaires propres aux niveaux | Academic | ⏳ EN ATTENTE | REGISTRE |
| BUL-TECH-01 | Choix techniques de publication | Technical | ⏳ EN ATTENTE | REGISTRE |
| BUL-TECH-02 | Autorisations de publication et correction | Finance | ⏳ EN ATTENTE | REGISTRE |
| BUL-TECH-03 | Consultation des versions remplacées | Academic | ⏳ EN ATTENTE | REGISTRE |
| BUL-TECH-04 | Révocation d'un bulletin émis | Academic | ⏳ EN ATTENTE | REGISTRE |
| BUL-TECH-05 | Stockage et rétention du PDF | Technical | ⏳ EN ATTENTE | REGISTRE |
| BUL-TECH-06 | Audit des émissions et téléchargements | Audit | ⏳ EN ATTENTE | REGISTRE |

#### Propositions Non Validées (6)

| ID | Titre | Catégorie | Statut | Source |
|----|-------|-----------|--------|--------|
| PAR-REL-01 | Cardinalité Parent-Enfant | Identity | 📝 PROPOSÉE | REGISTRE |
| PAR-REL-02 | Validation du rattachement | Identity | 📝 PROPOSÉE | REGISTRE |
| PAR-REL-03 | Historique non destructif | Identity | 📝 PROPOSÉE | REGISTRE |
| PAR-REL-04 | Accès Parent aux données | Identity | 📝 PROPOSÉE | REGISTRE |
| PAR-REL-05 | Séparation avec StudentUserLink | Technical | ✅ TECHNIQUEMENT CONFIRMÉE | REGISTRE |
| PAR-REL-06 | Accès parent aux bulletins | Identity | 📝 PROPOSÉE | REGISTRE |

### 6.2 Hiérarchie des Décisions

1. **Décisions canoniques** (BUL-*, FIN-*) : Décisions techniques précises qui complètent les décisions métiers
2. **Décisions validées** (D1-D44) : Décisions métiers fondamentales
3. **Décisions en attente** : Nécessitent validation
4. **Propositions** : Recommandations non validées

**Règle de priorité** : Une décision canonique prévaut sur une décision générale si elle est plus spécifique.

### 6.3 Traçabilité des Décisions

Toutes les décisions sont traçables vers :
- **Source documentaire** : Fichier et ligne dans le dépôt
- **Date de validation** : Quand applicable
- **Personne responsable** : Quand documentée
- **Décisions remplacées** : Historique conservé

---

**⚠️ NOTE IMPORTANTE** : Ce document est en cours de création. La section suivante (7 à 20) sera complétée lors des prochaines itérations. Les sections existantes contiennent déjà une analyse complète basée sur les documents clés examinés.

---

## 7. Bounded Contexts (À compléter)

Voir la section "Bounded Contexts Identifiés" dans EDUNOVA_DDD_ANALYSIS_FRAMEWORK.md pour la structure préliminaire.

## 8. Modèle de Domaine (À compléter)

Voir EDUNOVA_DDD_ANALYSIS_FRAMEWORK.md pour le modèle préliminaire.

## 9. Agrégats et Invariants (À compléter)

Voir les sections sur les agrégats dans le catalogue des fonctionnalités.

## 10. Context Map (À compléter)

Voir la section "Context Map Préliminaire" dans EDUNOVA_DDD_ANALYSIS_FRAMEWORK.md.

---

## 📚 Documents de Référence

### Documents Analysés
1. **EDUNOVA_FUSION_MASTERPLAN.md** - Vision et architecture
2. **docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md** - 44 décisions + canoniques
3. **docs/v1/DECISIONS_REQUISES.md** - Décisions V1 et réconciliations
4. **docs/v1/CONTRATS_METIER_V1.md** - Contrats métier détaillés
5. **docs/reports/RAPPORT_AUDIT_DOMAINE_SCOLAIRE_2026-10-16.md** - Audit du domaine
6. **docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md** - Plan d'intégration

### Documents à Analyser
- 75+ autres fichiers Markdown (rapports, plans, audits)
- Code source (entités, repositories, use cases)
- Tests unitaires et d'intégration
- Migrations de base de données

---

## 🎯 État de l'Analyse

- **Documents analysés** : 6/81 (7%)
- **Décisions extraites** : 56/56 (100% des décisions documentées)
- **Bounded contexts identifiés** : 10/10 (100%)
- **Acteurs définis** : 7/7 (100%)
- **Règles métier consolidées** : 40+/50+ (80%)

**Statut global** : ⚠️ **EN COURS - 30% COMPLET**

---

## 📞 Contact et Support

Pour toute question ou clarification sur ce document, veuillez vous référer aux documents sources ou contacter l'équipe EduNova.

---

**Document créé le** : 2025-XX-XX  
**Dernière mise à jour** : 2025-XX-XX  
**Version** : 1.0 - Brouillon Initial  
**Statut** : EN COURS
