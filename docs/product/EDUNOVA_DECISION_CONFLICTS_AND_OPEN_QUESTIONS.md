# EDUNOVA - Contradictions de Décisions et Questions Ouvertes

> **Document** : Registre des Contradictions, Conflits et Questions Ouvertes  
> **Version** : 1.0 - Brouillon Initial  
> **Date** : 2025-XX-XX  
> **Statut** : EN COURS  
> **Public Cible** : Product Owner, Business Analyst, Software Architect, Développeurs

---

## 📋 Table des Matières

1. [Introduction](#1-introduction)
2. [Méthodologie](#2-méthodologie)
3. [Contradictions Détectées](#3-contradictions-détectées)
4. [Décisions Remplacées](#4-décisions-remplacées)
5. [Décisions Non Ratifiées](#5-décisions-non-ratifiées)
6. [Règles Ambiguës](#6-règles-ambiguës)
7. [Informations Manquantes](#7-informations-manquantes)
8. [Arbitrages Nécessaires](#8-arbitrages-nécessaires)
9. [Questions Ouvertes par Domaine](#9-questions-ouvertes-par-domaine)
10. [Impact des Décisions en Attente](#10-impact-des-décisions-en-attente)
11. [Recommandations](#11-recommandations)
12. [Annexes](#12-annexes)

---

## 1. Introduction

### 1.1 Objectif

Ce document identifie et documente :
- Les **contradictions** entre différentes sources de décisions
- Les **décisions remplacées** par des décisions plus récentes ou plus spécifiques
- Les **décisions non ratifiées** (propositions, options en attente)
- Les **règles ambiguës** nécessitant clarification
- Les **informations manquantes** pour une implémentation complète
- Les **arbitrages nécessaires** pour résoudre les blocages

### 1.2 Périmètre

Ce document couvre :
- Toutes les décisions documentées dans les fichiers Markdown du projet
- Les contradictions entre décisions validées
- Les écarts entre décisions et implémentation existante
- Les questions soulevées par les audits et rapports

### 1.3 Statut des Décisions

| Statut | Description | Action Requise |
|--------|-------------|-----------------|
| ✅ VALIDÉE | Décision explicitement approuvée | Implémenter selon la décision |
| ✅ VALIDÉE AVEC RÉSERVE | Décision approuvée avec condition | Implémenter avec respect des réserves |
| ⏳ EN ATTENTE | Aucune option validée | Attendre validation |
| 📝 PROPOSÉE | Proposition non validée | Ne pas implémenter sans validation |
| 🗑️ HISTORIQUE | Décision remplacée | Conserver pour traçabilité, ne pas utiliser |
| ❓ À CLARIFIER | Information insuffisante | Demander clarification |
| ⚠️ CONTRADICTOIRE | Conflit avec autre décision | Arbitrage nécessaire |

### 1.4 Principes de Réconciliation

Pour résoudre les contradictions, appliquer la hiérarchie suivante :

1. **Une décision explicitement ratifiée** par le propriétaire du produit prévaut sur une ancienne proposition
2. **Une décision métier explicitement validée** prévaut sur une recommandation non validée
3. **Les décisions spécifiques et plus récentes** complètent ou remplacent les anciennes lorsqu'elles le précisent
4. **Les documents historiques** doivent être conservés comme traces, pas interprétés comme des décisions actives lorsqu'ils ont été remplacés
5. **Le code existant ne prévaut pas** automatiquement sur une décision métier validée
6. **Si deux décisions validées sont incompatibles**, ne pas trancher arbitrairement : documenter le conflit et demander un arbitrage

---

## 2. Méthodologie

### 2.1 Processus d'Analyse

1. **Inventaire** : Lister tous les documents contenant des décisions
2. **Extraction** : Extraire chaque décision avec son statut et sa source
3. **Classement** : Classer les décisions par domaine et par statut
4. **Comparaison** : Identifier les contradictions et chevauchements
5. **Réconciliation** : Appliquer les principes de hiérarchie
6. **Documentation** : Documenter les conflits et questions ouvertes

### 2.2 Sources Analysées

| Source | Nombre de Décisions | Statut |
|--------|---------------------|--------|
| REGISTRE_DECISIONS_METIER_EDUNOVA.md | 44 validées + 9 canoniques + 6 propositions | ✅ Analysé |
| EDUNOVA_FUSION_MASTERPLAN.md | 10 principes + 10 domaines | ✅ Analysé |
| DECISIONS_REQUISES.md | 12 décisions V1 + réconciliations | ✅ Analysé |
| CONTRATS_METIER_V1.md | Contrats métier détaillés | ✅ Analysé |
| RAPPORT_AUDIT_DOMAINE_SCOLAIRE | Analyse des lacunes | ✅ Analysé |
| EDUNOVA_EXTERNAL_INTEGRATIONS | Plan d'intégration | ⚠️ Partiel |
| Autres rapports (75+) | À analyser | ❌ Non analysé |

### 2.3 Outils Utilisés

- Analyse manuelle des documents Markdown
- Comparaison systématique des décisions
- Vérification de la cohérence avec le code existant (partielle)
- Identification des écarts et contradictions

---

## 3. Contradictions Détectées

### 3.1 Contradictions entre Décisions Validées

**Aucune contradiction majeure détectée entre décisions validées** à ce stade de l'analyse.

Les décisions validées (D1-D44) et les décisions canoniques (BUL-*, FIN-*) semblent cohérentes entre elles. Cependant, certaines **potentielles contradictions** doivent être vérifiées :

#### Potentielle Contradiction #1 : D14 vs PAR-REL-01

| Décision | Description | Source | Statut |
|----------|-------------|--------|--------|
| **D14** | Un compte n'a qu'un rôle ou contexte actif à la fois | REGISTRE | ✅ VALIDÉE |
| **PAR-REL-01** | Plusieurs parents/responsables peuvent être associés à un élève | REGISTRE | 📝 PROPOSÉE |

**Analyse** :
- D14 limite un **compte utilisateur** à un seul rôle actif à la fois
- PAR-REL-01 propose qu'un **élève** puisse avoir plusieurs parents/responsables
- **Pas de contradiction directe** : D14 parle des comptes utilisateurs, PAR-REL-01 parle des associations parent-enfant
- **Clarification nécessaire** : Un parent peut-il avoir le rôle PARENT actif tout en étant associé à plusieurs élèves ?

**Recommandation** : ⚠️ **À CLARIFIER**
- Confirmer que D14 ne limite pas la cardinalité des associations parent-enfant
- Vérifier que le rôle PARENT peut être actif pour un utilisateur associé à plusieurs élèves

**Impact** : Si non clarifié, pourrait bloquer l'implémentation du modèle parent-enfant

#### Potentielle Contradiction #2 : D6 vs BUL-CALC-01

| Décision | Description | Source | Statut |
|----------|-------------|--------|--------|
| **D6** | Note manquante est distincte d'un zéro | REGISTRE | ✅ VALIDÉE |
| **BUL-CALC-01** | Politique versionnée et arrondi explicite (2 décimales par défaut) | REGISTRE | ✅ VALIDÉE AVEC RÉSERVE |

**Analyse** :
- D6 establish la distinction note manquante vs zéro
- BUL-CALC-01 define la précision des calculs
- **Pas de contradiction** : Ces décisions sont complémentaires
- **Clarification nécessaire** : Comment traiter une note manquante dans le calcul de la moyenne ?
  - Option A : Exclure la matière du calcul
  - Option B : Compter comme 0
  - Option C : Compter comme note minimale

**Recommandation** : ⚠️ **À CLARIFIER**
- Définir explicitement le comportement des notes manquantes dans les calculs
- Documenter ce comportement dans la politique académique

**Impact** : Sans clarification, risque d'incohérence dans les calculs de moyenne

### 3.2 Contradictions entre Décisions et Code

D'après **RAPPORT_AUDIT_DOMAINE_SCOLAIRE_2026-10-16.md** :

#### Contradiction #1 : Décision D10 vs Code Existant

| Décision | Description | Source | Statut | État Code |
|----------|-------------|--------|--------|------------|
| **D10** | Distinguer année scolaire, périodes académiques, périodes d'évaluation | REGISTRE | ✅ VALIDÉE | ❌ Non implémenté |

**Analyse** :
- D10 impose une distinction claire entre trois types de périodes
- Le code existant n'a pas d'entité `AcademicYear` (seulement `AcademicPeriod`)
- `AcademicPeriod` n'est pas rattaché à une année scolaire
- **Contradiction** : Le code ne respecte pas la décision D10

**Recommandation** : 🔴 **CONTRADICTION CONFIRMÉE**
- Implémenter l'entité `AcademicYear` et la lier à `AcademicPeriod`
- Mettre à jour les repositories et migrations
- Vérifier que les invariants D10 sont respectés

**Impact** : Bloque la conformité avec les décisions métiers

#### Contradiction #2 : Décision D12 vs Code Existant

| Décision | Description | Source | Statut | État Code |
|----------|-------------|--------|--------|------------|
| **D12** | Transferts : provenance et historique obligatoires | REGISTRE | ✅ VALIDÉE | ❌ Non implémenté |

**Analyse** :
- D12 impose de conserver l'historique des transferts
- Le code n'a pas d'entité d'inscription ou de transfert
- Aucune table ne stocke l'historique des changements de classe
- **Contradiction** : Impossibilité de respecter D12 avec le code actuel

**Recommandation** : 🔴 **CONTRADICTION CONFIRMÉE**
- Implémenter l'agrégat `Enrollment` avec historique
- Créer les repositories et migrations nécessaires
- Valider que D12 est respecté

**Impact** : Bloque l'implémentation des transferts conformément aux décisions

#### Contradiction #3 : Décision D32 vs Routes API

| Décision | Description | Source | Statut | État Code |
|----------|-------------|--------|--------|------------|
| **D32** | Isolation multi-tenant à toutes les couches | REGISTRE | ✅ VALIDÉE | ⚠️ Partiel |

**Analyse** :
- D32 impose l'isolation à toutes les couches (contexte, autorisation, requêtes, BD, tâches)
- Les routes API actuelles utilisent `get_tenant_context` et `require_role("ADMIN")`
- **Risque** : Si d'autres routes n'appliquent pas le filtre tenant, contradiction avec D32

**Recommandation** : ⚠️ **À VÉRIFIER**
- Auditer toutes les routes API pour vérifier l'application du filtre tenant
- Corriger les routes non conformes
- Ajouter des tests négatifs inter-tenants

**Impact** : Risque de fuite de données entre tenants

### 3.3 Résumé des Contradictions

| # | Type | Décision 1 | Décision 2/Code | Statut | Impact | Priorité |
|---|------|------------|----------------|--------|--------|----------|
| 1 | Potentielle | D14 | PAR-REL-01 | ⚠️ À CLARIFIER | Moyenne | Moyenne |
| 2 | Potentielle | D6 | BUL-CALC-01 | ⚠️ À CLARIFIER | Élevée | Haute |
| 3 | **Confirmée** | D10 | Code existant | 🔴 CONTRADICTION | Élevée | **Critique** |
| 4 | **Confirmée** | D12 | Code existant | 🔴 CONTRADICTION | Élevée | **Critique** |
| 5 | Potentielle | D32 | Routes API | ⚠️ À VÉRIFIER | Élevée | **Critique** |

---

## 4. Décisions Remplacées

### 4.1 Décisions V1 Remplacées par Décisions Canoniques

Les décisions historiques D4-D7 (de DECISIONS_REQUISES.md) ont été **remplacées** par des décisions canoniques :

| Décision Historique | Statut | Décision Canonique | Statut | Relation |
|---------------------|--------|-------------------|--------|-----------|
| D4 - Obligation de délibération | Historique | BUL-PUB-01 | ✅ VALIDÉE | Remplacée |
| D5 - Document émis | Historique | BUL-DOC-01 | ✅ VALIDÉE | Remplacée |
| D6 - Correction bulletin | Historique | BUL-COR-01 | ✅ VALIDÉE | Remplacée |
| D7 - Arrondi et pourcentage | Historique | BUL-CALC-01 | ✅ VALIDÉE AVEC RÉSERVE | Remplacée |

**Analyse** :
- Les décisions canoniques (BUL-*) **précisent** les décisions historiques
- Les décisions historiques sont **conservées pour traçabilité** mais ne doivent plus être utilisées
- Les implémentations doivent se baser sur les **décisions canoniques**

**Recommandation** : ✅ **CORRECT**
- Utiliser les identifiants canoniques (BUL-*) dans le code et la documentation
- Conserver les références historiques pour traçabilité
- Mettre à jour les commentaires de code pour référencer les décisions canoniques

### 4.2 Décisions D8-D12 Remplacées par FIN-*

| Décision Historique | Statut | Décision Canonique | Statut | Relation |
|---------------------|--------|-------------------|--------|-----------|
| D8 - Mode de paiement V1 | Historique | FIN-ROLE-01, FIN-COR-01, FIN-REC-01 | ✅ VALIDÉE | Complétée |
| D9 - Surpaiement | Historique | FIN-COR-01 | ✅ VALIDÉE | Complétée |
| D10 - Sequence des reçus | Historique | FIN-REC-01 | ✅ VALIDÉE | Complétée |
| D11 - Annulation financière | Historique | FIN-COR-01 | ✅ VALIDÉE | Complétée |
| D12 - Autorisations finance | Historique | FIN-ROLE-01 | ✅ VALIDÉE | Remplacée |

**Analyse** :
- Les décisions FIN-* **précisent et complètent** les décisions historiques D8-D12
- Les décisions historiques sont **obsolètes** pour le domaine Finance
- **Pas de contradiction**, mais les décisions FIN-* doivent être prioritaires

**Recommandation** : ✅ **CORRECT**
- Utiliser les identifiants FIN-* pour le domaine Finance
- Les décisions D8-D12 sont conservées pour historique uniquement

---

## 5. Décisions Non Ratifiées

### 5.1 Décisions en Attente de Validation (9)

| ID | Titre | Description | Catégorie | Statut | Impact | Priorité | Blocage ? |
|----|-------|-------------|-----------|--------|--------|----------|-----------|
| **D45** | Identification des personnes et prévention des doublons | 3 options proposées (A, B, C) | Identity | ⏳ EN ATTENTE | **Critique** | **Critique** | ✅ **OUI** |
| **BUL-REG-01** | Règles réglementaires propres aux niveaux | Programmes, matières, maxima, coefficients, etc. | Academic | ⏳ EN ATTENTE | Élevée | Haute | ⚠️ Partiel |
| **BUL-TECH-01** | Choix techniques de publication | Stockage PDF, rétention, identifiant légal | Technical | ⏳ EN ATTENTE | Moyenne | Moyenne | ⚠️ Partiel |
| **BUL-TECH-02** | Autorisations de publication et correction | Qui peut publier/corriger les bulletins ? | Academic | ⏳ EN ATTENTE | Élevée | Haute | ⚠️ Partiel |
| **BUL-TECH-03** | Consultation des versions remplacées | Quels rôles peuvent consulter SUPERSEDED ? | Academic | ⏳ EN ATTENTE | Moyenne | Moyenne | ⚠️ Partiel |
| **BUL-TECH-04** | Révocation d'un bulletin émis | Procédure, motifs, effets | Academic | ⏳ EN ATTENTE | Élevée | Haute | ⚠️ Partiel |
| **BUL-TECH-05** | Stockage et rétention du PDF | Archivage vs rendu à la demande | Technical | ⏳ EN ATTENTE | Moyenne | Moyenne | ⚠️ Partiel |
| **BUL-TECH-06** | Audit des émissions et téléchargements | Événements obligatoires, données conservées | Audit | ⏳ EN ATTENTE | Moyenne | Moyenne | ⚠️ Partiel |

**Analyse** :
- **D45** est la **plus critique** : bloque l'implémentation complète des élèves
- **BUL-TECH-02, BUL-TECH-04** bloquent partiellement l'implémentation des bulletins
- Les autres décisions en attente ont un impact moyen

### 5.2 Propositions Non Validées (6)

| ID | Titre | Description | Catégorie | Statut | Impact | Priorité | Blocage ? |
|----|-------|-------------|-----------|--------|--------|----------|-----------|
| **PAR-REL-01** | Cardinalité Parent-Enfant | Plusieurs parents/élèves | Identity | 📝 PROPOSÉE | **Critique** | **Critique** | ✅ **OUI** |
| **PAR-REL-02** | Validation du rattachement | Création/validation par direction | Identity | 📝 PROPOSÉE | **Critique** | **Critique** | ✅ **OUI** |
| **PAR-REL-03** | Historique non destructif | Conservation auteur, date, motif | Identity | 📝 PROPOSÉE | Élevée | Haute | ⚠️ Partiel |
| **PAR-REL-04** | Accès Parent aux données | Consultation bulletins, résultats, présences | Identity | 📝 PROPOSÉE | **Critique** | **Critique** | ✅ **OUI** |
| **PAR-REL-05** | Séparation avec StudentUserLink | Modèle distinct | Technical | ✅ TECHNIQUEMENT CONFIRMÉE | Moyenne | Moyenne | ❌ Non |
| **PAR-REL-06** | Accès parent aux bulletins | Vérification serveur du rattachement | Identity | 📝 PROPOSÉE | **Critique** | **Critique** | ✅ **OUI** |

**Analyse** :
- **PAR-REL-01 à PAR-REL-04 et PAR-REL-06** sont **critiques** pour l'implémentation de l'application parent
- **PAR-REL-05** est déjà techniquement confirmée, pas de blocage
- Sans validation de ces propositions, **l'application parent ne peut pas être implémentée**

### 5.3 Décisions Historiques (43-44)

**Note** : Les décisions D43 et D44 concernent la numérisation initiale et sont **VALIDÉES** (choix A pour les deux). Elles ne sont pas en attente.

Cependant, le document mentionne :
> "Une décision sur l'activation progressive des fonctionnalités (*feature flags*) avait été proposée sous le numéro 43 avant que la conversation passe à la numérisation."

**Analyse** :
- La numérotation a été réutilisée pour les décisions de numérisation
- La décision sur les *feature flags* **n'a jamais été validée**
- **Statut** : ❓ **À CLARIFIER**

**Recommandation** : ⚠️ **À CLARIFIER**
- Renuméroter proprement la décision sur les feature flags
- Valider ou invalider cette décision
- Mettre à jour le registre pour éviter la confusion

---

## 6. Règles Ambiguës

### 6.1 Ambiguïté #1 : Traitement des Notes Manquantes

**Source** : Décision D6 (Note manquante ≠ zéro)

**Problème** : La décision D6 establish que note manquante ≠ zéro, mais ne précise pas :
- Comment traiter une note manquante dans le calcul de la moyenne ?
- Une note manquante doit-elle être :
  - a) Exclue du calcul
  - b) Compter comme 0
  - c) Compter comme note minimale (ex: 20/100)
  - d) Bloquer la validation du dossier

**Impact** : Sans clarification, risque d'incohérence dans les calculs de moyenne et de délibération.

**Recommandation** : ⚠️ **À CLARIFIER**
- Définir explicitement le comportement dans la politique académique
- Documenter dans BUL-CALC-01 ou une nouvelle décision

**Priorité** : 🔴 **CRITIQUE** (impact sur les calculs académiques)

### 6.2 Ambiguïté #2 : Définition de "Publication Officielle"

**Source** : Décision D16 (Consultation des bulletins)

**Problème** : La décision D16 establish que "Les élèves et parents ne consultent les bulletins qu'après publication officielle", mais ne définit pas :
- Qui peut publier officiellement ? (BUL-TECH-02 en attente)
- Quel est le processus de publication ?
- Un bulletin peut-il être "dépublié" ?
- Comment identifier un bulletin officiel vs provisoire ?

**Impact** : Sans clarification, impossible d'implémenter correctement l'accès parent/élève.

**Recommandation** : ⚠️ **À CLARIFIER**
- Valider BUL-TECH-02 pour définir les autorisations
- Définir le processus de publication dans le workflow
- Implémenter un statut clair (ex: `DRAFT`, `PUBLISHED`)

**Priorité** : 🔴 **CRITIQUE** (bloque l'application parent/élève)

### 6.3 Ambiguïté #3 : "Résultats Provisoires"

**Source** : Décision D16

**Problème** : La décision mentionne "Les résultats provisoires restent réservés au personnel autorisé", mais ne définit pas :
- Quand un résultat est considéré comme provisoire ?
- Comment passer de provisoire à officiel ?
- Qui peut consulter les résultats provisoires ?

**Impact** : Sans définition claire, risque de confusion entre résultats provisoires et officiels.

**Recommandation** : ⚠️ **À CLARIFIER**
- Définir les critères d'un résultat provisoire
- Définir le processus de validation
- Clarifier les permissions d'accès

**Priorité** : 🟡 **HAUTE**

### 6.4 Ambiguïté #4 : "Politique Versionnée"

**Source** : Décisions D2, D5, BUL-CALC-01

**Problème** : Plusieurs décisions mentionnent des "politiques versionnées", mais ne précisent pas :
- Comment la version est stockée ?
- Comment la version est associée à un calcul ?
- Comment récupérer la version applicable à une période donnée ?
- Comment gérer les modifications de politique ?

**Impact** : Sans clarification, risque d'erreurs dans les calculs historiques.

**Recommandation** : ⚠️ **À CLARIFIER**
- Définir le modèle de versionnement des politiques
- Implémenter un mécanisme de stockage et de récupération
- Tester les calculs avec différentes versions

**Priorité** : 🟡 **HAUTE**

### 6.5 Ambiguïté #5 : "Provenance et Historique" pour les Transferts

**Source** : Décision D12

**Problème** : D12 impose "provenance et historique obligatoires" pour les transferts, mais ne précise pas :
- Quelles informations doivent être conservées ?
- Comment structurer l'historique ?
- Qui peut consulter l'historique ?

**Impact** : Sans clarification, l'implémentation peut être incomplète.

**Recommandation** : ⚠️ **À CLARIFIER**
- Définir le modèle de données pour l'historique des transferts
- Spécifier les champs obligatoires (date, provenance, motif, etc.)
- Définir les permissions d'accès à l'historique

**Priorité** : 🟡 **HAUTE**

---

## 7. Informations Manquantes

### 7.1 Définitions Manquantes

| Élément | Description | Source | Impact | Priorité |
|---------|-------------|--------|--------|----------|
| **Année Scolaire** | Définition officielle et modèle de données | D10 | Bloque l'implémentation | 🔴 **CRITIQUE** |
| **Période d'Évaluation** | Distinction avec Période Académique | D10 | Risque de confusion | 🟡 **HAUTE** |
| **Profil Académique** | Structure et contenu exact | BUL-PROF-01 | Bloque la configuration | 🟡 **HAUTE** |
| **Rôle PARENT** | Définition métier exacte | PAR-REL-* | Bloque l'application parent | 🔴 **CRITIQUE** |
| **Responsable Légal** | Différence avec Parent | PAR-REL-01 | Impact juridique | 🟡 **HAUTE** |
| **Garde Partagée** | Cas particulier à gérer | PAR-REL-01 | Impact juridique | 🟡 **HAUTE** |

### 7.2 Processus Manquants

| Processus | Description | Impact | Priorité |
|-----------|-------------|--------|----------|
| **Inscription d'un Élève** | Workflow complet d'inscription | Bloque la fonctionnalité | 🔴 **CRITIQUE** |
| **Affectation à une Classe** | Processus d'affectation | Bloque la fonctionnalité | 🔴 **CRITIQUE** |
| **Validation des Notes** | Qui, quand, comment | Risque d'erreurs | 🟡 **HAUTE** |
| **Publication des Bulletins** | Workflow complet | Bloque l'application parent | 🔴 **CRITIQUE** |
| **Correction des Bulletins** | Processus et autorisations | Risque d'incohérence | 🟡 **HAUTE** |

### 7.3 Règles Métier Manquantes

| Règle | Description | Impact | Priorité |
|-------|-------------|--------|----------|
| **Doublons d'Élèves** | Comment détecter et gérer | Risque de confusion | 🟡 **HAUTE** |
| **Fusion de Dossiers** | Processus de fusion | Impact sur l'historique | 🟡 **HAUTE** |
| **Changement de Classe** | Processus et validation | Bloque la gestion scolaire | 🔴 **CRITIQUE** |
| **Annulation de Paiement** | Processus complet | Impact financier | 🔴 **CRITIQUE** |
| **Remboursement** | Processus et conditions | Impact financier | 🟡 **HAUTE** |

---

## 8. Arbitrages Nécessaires

### 8.1 Arbitrage #1 : D45 - Identification des Personnes

**Décision** : D45 - Identification des personnes et prévention des doublons

**Options** :
- **Option A** : Attribuer un identifiant interne EduNova à chaque dossier, conserver les matricules existants comme références, signaler les correspondances possibles pour vérification humaine avant toute fusion
- **Option B** : Exiger un matricule existant ou attribué par l'école avant l'enregistrement définitif
- **Option C** : Utiliser le nom et la date de naissance comme critères principaux, avec vérification manuelle

**Recommandation du Registre** : Option A

**Analyse** :
- **Option A** : Permet de traiter les archives incomplètes sans inventer de matricule. Limite les fusions erronées.
- **Option B** : Plus simple, mais bloque si un élève n'a pas de matricule.
- **Option C** : Risque élevé de doublons (noms communs, erreurs de saisie).

**Impact de chaque option** :
| Option | Avantages | Inconvénients | Complexité | Risque |
|--------|-----------|---------------|------------|--------|
| A | Flexible, gère les archives | Nécessite vérification manuelle | Moyenne | Faible |
| B | Simple, pas de doublons | Bloque les élèves sans matricule | Faible | Moyen |
| C | Pas de matricule requis | Risque élevé de doublons | Faible | **Élevé** |

**Recommandation** : ✅ **CHOISIR OPTION A**
- Permet de gérer tous les cas
- Minimise les risques de fusion erronée
- Compatible avec la réalité des écoles en RDC

**Action Requise** : 🔴 **ARBITRAGE PROPRIÉTAIRE PRODUIT**

### 8.2 Arbitrage #2 : PAR-REL-01 - Cardinalité Parent-Enfant

**Proposition** : PAR-REL-01 - Plusieurs parents/responsables peuvent être associés à un élève, et un parent peut être associé à plusieurs élèves.

**Analyse** :
- **Cas d'usage** : Garde partagée, famille recomposée, tuteur légal différent du parent
- **Impact technique** : Modèle de données plus complexe (relation many-to-many)
- **Impact métier** : Permet de répondre aux réalités familiales

**Problème** : Cette proposition n'est pas validée et bloque l'implémentation de l'application parent.

**Recommandation** : ✅ **VALIDER PAR-REL-01**
- Correspond à la réalité sociale
- Compatible avec D13 (permissions configurables)
- Nécessaire pour l'application parent

**Action Requise** : 🔴 **ARBITRAGE PROPRIÉTAIRE PRODUIT**

### 8.3 Arbitrage #3 : PAR-REL-02 - Validation du Rattachement

**Proposition** : PAR-REL-02 - La création et la validation d'un rattachement sont réservées à la direction ou à un agent disposant d'une permission explicite.

**Analyse** :
- **Sécurité** : Évite les rattachements frauduleux
- **Responsabilité** : La direction valide les liens parent-enfant
- **Flexibilité** : Peut déléguer à un agent habilité

**Problème** : Cette proposition n'est pas validée.

**Recommandation** : ✅ **VALIDER PAR-REL-02**
- Essentiel pour la sécurité
- Compatible avec D13 et D32
- Nécessaire pour l'application parent

**Action Requise** : 🔴 **ARBITRAGE PROPRIÉTAIRE PRODUIT**

### 8.4 Arbitrage #4 : BUL-TECH-02 - Autorisations de Publication

**Proposition** : BUL-TECH-02 - L'implémentation actuelle réserve la publication et la correction au rôle ADMIN. Il reste à confirmer si un rôle de direction ou un rôle académique habilité doit être autorisé, et si les rôles de publication et de correction doivent être distincts.

**Analyse** :
- **Option A** : Seul ADMIN peut publier et corriger
- **Option B** : DIRECTION peut publier, ADMIN peut corriger
- **Option C** : DIRECTION peut publier et corriger
- **Option D** : Rôles distincts (PUBLISHER, CORRECTOR)

**Recommandation** : ⚠️ **À ARBITRER**
- **Option C** semble la plus appropriée (DIRECTION publie et corrige)
- Mais dépend de la structure organisationnelle de chaque établissement

**Action Requise** : 🔴 **ARBITRAGE PROPRIÉTAIRE PRODUIT**

### 8.5 Arbitrage #5 : BUL-TECH-04 - Révocation d'un Bulletin

**Proposition** : BUL-TECH-04 - La révocation reste distincte du remplacement. Il faut définir les rôles autorisés, les motifs obligatoires, l'effet sur la visibilité, la conservation du snapshot et le traitement d'une délibération ou d'une promotion déjà utilisée.

**Analyse** :
- **Révocation** : Annulation complète d'un bulletin (plus visible, plus valide)
- **Remplacement** : Nouvelle version, ancienne marquée SUPERSEDED (toujours visible)
- **Impact juridique** : La révocation peut avoir des conséquences légales

**Recommandation** : ⚠️ **À ARBITRER**
- Définir clairement la différence entre révocation et remplacement
- Spécifier les conditions de révocation
- Définir les rôles autorisés

**Action Requise** : 🔴 **ARBITRAGE PROPRIÉTAIRE PRODUIT**

---

## 9. Questions Ouvertes par Domaine

### 9.1 Domaine Academic

| # | Question | Source | Impact | Priorité | Statut |
|---|----------|--------|--------|----------|--------|
| ACA-Q001 | Comment traiter les notes manquantes dans le calcul de la moyenne ? | D6, BUL-CALC-01 | Élevée | 🔴 **CRITIQUE** | ❓ OUVERTE |
| ACA-Q002 | Quelle est la définition exacte de "publication officielle" ? | D16, BUL-PUB-01 | Élevée | 🔴 **CRITIQUE** | ❓ OUVERTE |
| ACA-Q003 | Comment définir et identifier les "résultats provisoires" ? | D16 | Moyenne | 🟡 **HAUTE** | ❓ OUVERTE |
| ACA-Q004 | Comment versionner et stocker les politiques académiques ? | D2, D5, BUL-CALC-01 | Moyenne | 🟡 **HAUTE** | ❓ OUVERTE |
| ACA-Q005 | Quelles informations conserver pour l'historique des transferts ? | D12 | Moyenne | 🟡 **HAUTE** | ❓ OUVERTE |
| ACA-Q006 | Quelles sont les règles réglementaires propres aux niveaux ? | BUL-REG-01 | Élevée | 🔴 **CRITIQUE** | ❓ OUVERTE |

### 9.2 Domaine Finance

| # | Question | Source | Impact | Priorité | Statut |
|---|----------|--------|--------|----------|--------|
| FIN-Q001 | Qui peut confirmer, annuler et consulter les données financières ? | D19-D21, FIN-ROLE-01 | Moyenne | 🟡 **HAUTE** | ⚠️ PARTIEL (FIN-ROLE-01) |
| FIN-Q002 | Comment gérer les paiements partiels ? | D22, FIN-COR-01 | Élevée | 🔴 **CRITIQUE** | ❓ OUVERTE |
| FIN-Q003 | Comment gérer les surpaiements ? | D21, FIN-COR-01 | Élevée | 🔴 **CRITIQUE** | ❓ OUVERTE |
| FIN-Q004 | Quel est le format de numérotation des reçus ? | D23, FIN-REC-01 | Moyenne | 🟡 **HAUTE** | ❓ OUVERTE |
| FIN-Q005 | Quelle est la politique de rétention des reçus ? | FIN-REC-01 | Moyenne | 🟡 **HAUTE** | ❓ OUVERTE |

### 9.3 Domaine Identity & Access

| # | Question | Source | Impact | Priorité | Statut |
|---|----------|--------|--------|----------|--------|
| IAM-Q001 | Comment gérer les doublons d'élèves ? | D45 | **Critique** | 🔴 **CRITIQUE** | ❓ OUVERTE |
| IAM-Q002 | Quelle est la définition exacte de "PARENT" ? | PAR-REL-01 | **Critique** | 🔴 **CRITIQUE** | ❓ OUVERTE |
| IAM-Q003 | Quelle est la définition de "Responsable Légal" ? | PAR-REL-01 | Élevée | 🟡 **HAUTE** | ❓ OUVERTE |
| IAM-Q004 | Comment gérer la garde partagée ? | PAR-REL-01 | Élevée | 🟡 **HAUTE** | ❓ OUVERTE |
| IAM-Q005 | Qui peut valider un rattachement parent-enfant ? | PAR-REL-02 | **Critique** | 🔴 **CRITIQUE** | ❓ OUVERTE |
| IAM-Q006 | Quelles données un parent peut-il consulter ? | PAR-REL-04 | **Critique** | 🔴 **CRITIQUE** | ❓ OUVERTE |

### 9.4 Domaine Technical

| # | Question | Source | Impact | Priorité | Statut |
|---|----------|--------|--------|----------|--------|
| TEC-Q001 | Comment stocker le PDF des bulletins ? | BUL-TECH-01, BUL-TECH-05 | Moyenne | 🟡 **HAUTE** | ❓ OUVERTE |
| TEC-Q002 | Quelle est la politique de rétention des PDF ? | BUL-TECH-05 | Moyenne | 🟡 **HAUTE** | ❓ OUVERTE |
| TEC-Q003 | Comment auditer les émissions de bulletins ? | BUL-TECH-06 | Moyenne | 🟡 **HAUTE** | ❓ OUVERTE |
| TEC-Q004 | Comment gérer les feature flags ? | D43 historique | Moyenne | 🟡 **HAUTE** | ❓ OUVERTE |

---

## 10. Impact des Décisions en Attente

### 10.1 Décisions Bloquantes (Impact Critique)

| Décision | Fonctionnalité Bloquée | Impact Utilisateur | Impact Technique | Priorité |
|----------|------------------------|--------------------|-------------------|----------|
| **D45** | Inscription des élèves | Impossible d'inscrire des élèves | Modèle de données incomplet | 🔴 **CRITIQUE** |
| **PAR-REL-01** | Application Parent | Impossible de lier parents et élèves | Modèle de données incomplet | 🔴 **CRITIQUE** |
| **PAR-REL-02** | Application Parent | Impossible de valider les rattachements | Workflow incomplet | 🔴 **CRITIQUE** |
| **PAR-REL-04** | Application Parent | Impossible de définir les permissions | Sécurité incomplète | 🔴 **CRITIQUE** |
| **PAR-REL-06** | Application Parent | Impossible d'implémenter l'accès parent | Autorisation incomplète | 🔴 **CRITIQUE** |
| **BUL-TECH-02** | Publication des bulletins | Impossible de publier officiellement | Workflow incomplet | 🔴 **CRITIQUE** |
| **BUL-TECH-04** | Correction des bulletins | Impossible de révoker un bulletin | Fonctionnalité incomplète | 🔴 **CRITIQUE** |

**Total** : 7 décisions bloquantes avec impact **CRITIQUE**

### 10.2 Décisions avec Impact Élevé

| Décision | Fonctionnalité Impactée | Impact | Priorité |
|----------|-------------------------|--------|----------|
| **BUL-REG-01** | Configuration académique | Impossible de configurer les règles par niveau | 🟡 **HAUTE** |
| **ACA-Q001** | Calcul des moyennes | Risque d'incohérence dans les notes | 🟡 **HAUTE** |
| **ACA-Q002** | Publication des bulletins | Risque de confusion provisoire/officiel | 🟡 **HAUTE** |
| **FIN-Q002** | Gestion financière | Impossible de gérer les paiements partiels | 🟡 **HAUTE** |
| **FIN-Q003** | Gestion financière | Impossible de gérer les surpaiements | 🟡 **HAUTE** |

**Total** : 5 décisions avec impact **ÉLEVÉ**

### 10.3 Décisions avec Impact Moyen

| Décision | Fonctionnalité Impactée | Impact | Priorité |
|----------|-------------------------|--------|----------|
| **BUL-TECH-01** | Publication des bulletins | Choix technique non optimal | 🟢 **MOYENNE** |
| **BUL-TECH-03** | Consultation des bulletins | Accès historique non défini | 🟢 **MOYENNE** |
| **BUL-TECH-05** | Archivage des bulletins | Stockage non optimisé | 🟢 **MOYENNE** |
| **BUL-TECH-06** | Audit des bulletins | Traçabilité incomplète | 🟢 **MOYENNE** |
| **TEC-Q001** | Archivage des documents | Stockage non optimisé | 🟢 **MOYENNE** |

**Total** : 5 décisions avec impact **MOYEN**

---

## 11. Recommandations

### 11.1 Priorités Immédiates (🔴 CRITIQUE)

**Action #1 : Valider D45 (Identification des personnes)**
- **Recommandation** : Choisir **Option A**
- **Impact** : Débloque l'implémentation complète des élèves
- **Urgence** : **MAXIMUM**
- **Responsable** : Propriétaire du Produit

**Action #2 : Valider PAR-REL-01 à PAR-REL-06 (Modèle parent-enfant)**
- **Recommandation** : Valider toutes les propositions
- **Impact** : Débloque l'application parent
- **Urgence** : **MAXIMUM**
- **Responsable** : Propriétaire du Produit

**Action #3 : Valider BUL-TECH-02 et BUL-TECH-04 (Publication des bulletins)**
- **Recommandation** : Valider avec **Option C** (DIRECTION publie et corrige)
- **Impact** : Débloque la publication officielle des bulletins
- **Urgence** : **MAXIMUM**
- **Responsable** : Propriétaire du Produit

**Action #4 : Clarifier ACA-Q001 (Traitement des notes manquantes)**
- **Recommandation** : Exclure du calcul ou compter comme 0 (à arbitrer)
- **Impact** : Évite les incohérences dans les calculs
- **Urgence** : **MAXIMUM**
- **Responsable** : Expert Métier Académique

### 11.2 Priorités à Court Terme (🟡 HAUTE)

**Action #5 : Clarifier ACA-Q002 (Définition de "Publication Officielle")**
- **Impact** : Évite la confusion entre provisoire et officiel
- **Urgence** : Haute

**Action #6 : Clarifier FIN-Q002 et FIN-Q003 (Paiements partiels et surpaiements)**
- **Impact** : Permet une gestion financière complète
- **Urgence** : Haute

**Action #7 : Clarifier BUL-REG-01 (Règles réglementaires)**
- **Impact** : Permet la configuration académique par niveau
- **Urgence** : Haute

### 11.3 Priorités à Moyen Terme (🟢 MOYENNE)

**Action #8 : Valider les décisions techniques (BUL-TECH-01, 03, 05, 06)**
- **Impact** : Optimisation technique
- **Urgence** : Moyenne

### 11.4 Processus Recommandé

1. **Réunion d'arbitrage** : Organiser une réunion avec le propriétaire du produit pour valider les décisions critiques
2. **Documentation** : Mettre à jour le registre des décisions avec les validations
3. **Communication** : Informer l'équipe technique des décisions validées
4. **Implémentation** : Commencer l'implémentation par ordre de priorité
5. **Tests** : Valider chaque implémentation avec des tests adaptés

---

## 12. Annexes

### 12.1 Références des Documents

| Document | Chemin | Date | Statut |
|----------|--------|------|--------|
| EDUNOVA_FUSION_MASTERPLAN.md | ./EDUNOVA_FUSION_MASTERPLAN.md | 2026-XX-XX | ✅ Analysé |
| REGISTRE_DECISIONS_METIER_EDUNOVA.md | ./docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md | 2026-10-22 | ✅ Analysé |
| DECISIONS_REQUISES.md | ./docs/v1/DECISIONS_REQUISES.md | 2026-XX-XX | ✅ Analysé |
| CONTRATS_METIER_V1.md | ./docs/v1/CONTRATS_METIER_V1.md | 2026-XX-XX | ✅ Analysé |
| RAPPORT_AUDIT_DOMAINE_SCOLAIRE | ./docs/reports/RAPPORT_AUDIT_DOMAINE_SCOLAIRE_2026-10-16.md | 2026-10-16 | ✅ Analysé |
| INTEGRATIONS_IMPLEMENTATION_PLAN | ./docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md | 2026-XX-XX | ⚠️ Partiel |

### 12.2 Glossaire des Statuts

| Statut | Signification | Action |
|--------|---------------|--------|
| ✅ VALIDÉE | Décision approuvée | Implémenter |
| ✅ VALIDÉE AVEC RÉSERVE | Décision approuvée avec conditions | Implémenter avec réserves |
| ⏳ EN ATTENTE | Aucune option validée | Attendre |
| 📝 PROPOSÉE | Proposition non validée | Ne pas implémenter |
| 🗑️ HISTORIQUE | Décision remplacée | Ne pas utiliser |
| ❓ OUVERTE | Question sans réponse | Clarifier |
| ⚠️ À CLARIFIER | Information insuffisante | Demander clarification |
| 🔴 CONTRADICTION | Conflit avec autre décision | Arbitrage nécessaire |

### 12.3 Légende des Priorités

| Priorité | Signification | Couleur |
|----------|---------------|--------|
| 🔴 **CRITIQUE** | Bloque une fonctionnalité majeure | Rouge |
| 🟡 **HAUTE** | Impact significatif sur une fonctionnalité | Orange |
| 🟢 **MOYENNE** | Impact limité ou optimisation | Vert |

---

## 📊 Résumé Exécutif

### États des Décisions

| Catégorie | Total | Validées | En Attente | Proposées | Contradictions | À Clarifier |
|-----------|-------|-----------|------------|-----------|----------------|--------------|
| **Décisions Numérotées** | 44 | 44 | 0 | 0 | 0 | 0 |
| **Décisions Canoniques** | 10 | 9 | 0 | 0 | 0 | 1 |
| **Décisions Techniques** | 6 | 0 | 6 | 0 | 0 | 0 |
| **Propositions Parent-Enfant** | 6 | 1 | 0 | 5 | 0 | 0 |
| **Questions Ouvertes** | 20+ | 0 | 0 | 0 | 0 | 20+ |
| **Contradictions** | 5 | 0 | 0 | 0 | 2 confirmées | 3 potentielles |

### Impact Global

- **7 décisions bloquantes** (Impact Critique) : bloquent des fonctionnalités majeures
- **5 décisions avec impact élevé** : impactent significativement les fonctionnalités
- **5+ décisions avec impact moyen** : optimisations ou clarifications nécessaires
- **2 contradictions confirmées** : écarts entre décisions et code
- **3 contradictions potentielles** : nécessitent vérification

### Recommandations Clés

1. **Valider D45** (Identification des personnes) - **URGENCE MAXIMUM**
2. **Valider PAR-REL-01 à PAR-REL-06** (Modèle parent-enfant) - **URGENCE MAXIMUM**
3. **Valider BUL-TECH-02 et BUL-TECH-04** (Publication des bulletins) - **URGENCE MAXIMUM**
4. **Clarifier ACA-Q001 et ACA-Q002** (Notes manquantes, publication) - **URGENCE MAXIMUM**
5. **Corriger les contradictions code/décisions** (D10, D12) - **URGENCE MAXIMUM**

---

## 🎯 Conclusion

Ce document identifie **12+ points nécessitant un arbitrage du propriétaire du produit** et **7 décisions bloquantes** qui empêchent l'implémentation complète de fonctionnalités critiques.

**Action Immédiate Requise** : Organiser une réunion d'arbitrage pour valider les décisions critiques et lever les blocages.

**Prochaine Étape** : Une fois les décisions validées, mettre à jour ce document et commencer l'implémentation par ordre de priorité.

---

**Document créé le** : 2025-XX-XX  
**Dernière mise à jour** : 2025-XX-XX  
**Version** : 1.0 - Brouillon Initial  
**Statut** : EN COURS  
**État de l'analyse** : Environ 30% complet (6 documents majeurs analysés sur 81+)
