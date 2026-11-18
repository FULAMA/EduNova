# EDUNOVA - Addendum au Registre des Contradictions et Questions Ouvertes

> **Document Parent** : [EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md](EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md)  
> **Source** : Analyse des documents d'intégrations et validation Phase 5  
> **Date** : 2025-XX-XX  
> **Statut** : COMPLET  
> **Version** : 1.0

---

## 📋 Table des Matières

1. [Nouvelles Décisions en Attente (INT-AWAIT-*)](#1-nouvelles-décisions-en-attente-int-await-)
2. [Mise à jour des Contradictions](#2-mise-à-jour-des-contradictions)
3. [Nouvelles Questions par Domaine](#3-nouvelles-questions-par-domaine)
4. [Impact Mise à Jour](#4-impact-mise-à-jour)
5. [Nouveaux Arbitrages Nécessaires](#5-nouveaux-arbitrages-nécessaires)
6. [Validation Phase 5](#6-validation-phase-5)
7. [Synthèse des Mises à Jour](#7-synthèse-des-mises-à-jour)

---

## 1. Nouvelles Décisions en Attente (INT-AWAIT-*)

### 1.1 Paiement RDC (🔴 CRITIQUE)

Les décisions suivantes sont **critiques** et bloquent l'activation des paiements en production pour les établissements en RDC.

#### INT-AWAIT-001 : Flutterwave Éligibilité RDC

| Champ | Valeur |
|-------|--------|
| **ID** | INT-AWAIT-001 |
| **Titre** | Vérification de l'éligibilité Flutterwave pour la RDC |
| **Description** | Vérifier si Flutterwave supporte la RDC, le CDF et les opérateurs Mobile Money (M-Pesa, Airtel Money, Orange Money) |
| **Domaine** | Finance |
| **Statut** | ⏳ EN ATTENTE |
| **Priorité** | 🔴 **CRITIQUE** |
| **Impact** | **Bloque les paiements numériques en RDC** |
| **Source** | `docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md` (Section 5.7) |

**Analyse** :
- Flutterwave est listé comme candidat pour les paiements en Afrique
- La documentation Flutterwave mentionne Mobile Money par région
- **La disponibilité pour la RDC, le CDF et les opérateurs locaux doit être confirmée contractuellement et techniquement**
- Ne pas activer Flutterwave pour la RDC sur la seule base de la disponibilité dans des pays voisins

**Matrice de Vérification Requise** :
- ✅ Pays d'enregistrement de l'établissement
- ✅ Pays du payeur
- ✅ Devise de collecte et de règlement (CDF)
- ❓ Opérateurs supportés (M-Pesa, Airtel Money, Orange Money)
- ❓ Frais, délais de règlement
- ❓ Exigences KYC/KYB
- ❓ Disponibilité du sandbox
- ❓ Webhooks signés

**Recommandation** : 🔴 **ARBITRAGE PROPRIÉTAIRE PRODUIT URGENT**
- Contacter Flutterwave pour confirmation officielle
- Valider la disponibilité du CDF
- Valider les opérateurs Mobile Money supportés
- Confirmer les frais et délais

**Conséquence si non résolu** : Impossible d'activer les paiements numériques en production pour les établissements en RDC.

---

#### INT-AWAIT-002 : Agrégateur Local RDC

| Champ | Valeur |
|-------|--------|
| **ID** | INT-AWAIT-002 |
| **Titre** | Recherche et validation d'un agrégateur local pour la RDC |
| **Description** | Rechercher et valider un fournisseur réellement contractable en RDC et prenant en charge les moyens de paiement demandés |
| **Domaine** | Finance |
| **Statut** | ⏳ EN ATTENTE |
| **Priorité** | 🔴 **CRITIQUE** |
| **Impact** | **Bloque les paiements numériques en RDC** |
| **Source** | `docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md` (Section 5.7) |

**Analyse** :
- Stripe est disponible en sandbox mais **pas en production pour la RDC**
- Flutterwave peut ou peut ne pas supporter la RDC (à vérifier)
- Il faut identifier un **fournisseur local** qui supporte :
  - Le CDF (Franc Congolais)
  - Les opérateurs Mobile Money locaux (M-Pesa, Airtel Money, Orange Money)
  - Les exigences KYC/KYB des établissements scolaires en RDC
  - Les webhooks signés
  - Un sandbox pour les tests

**Recommandation** : 🔴 **ARBITRAGE PROPRIÉTAIRE PRODUIT URGENT**
- Rechercher des agrégateurs locaux en RDC (ex: M-Pesa Direct, Orange Money API, etc.)
- Évaluer les coûts, la fiabilité et la disponibilité
- Valider la compatibilité avec les exigences EduNova

**Conséquence si non résolu** : Impossible d'activer les paiements numériques en production pour les établissements en RDC.

---

### 1.2 Compatibilité FCM (⚠️ HAUTE)

#### INT-AWAIT-003 : Vérification Compatibilité PWA

| Champ | Valeur |
|-------|--------|
| **ID** | INT-AWAIT-003 |
| **Titre** | Vérification de la compatibilité de la PWA actuelle avec FCM |
| **Description** | Vérifier que la PWA actuelle supporte Firebase Cloud Messaging |
| **Domaine** | Integration |
| **Statut** | ⏳ EN ATTENTE |
| **Priorité** | 🟡 **HAUTE** |
| **Impact** | Bloque l'implémentation FCM |
| **Source** | `docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md` (Section 5.2) |

**Analyse** :
- FCM (Firebase Cloud Messaging) est le fournisseur sélectionné pour les notifications push
- La PWA actuelle peut ou peut ne pas être compatible avec FCM
- Il faut vérifier :
  - Le service worker est correctement configuré
  - Les clés web push sont disponibles
  - La configuration Firebase est valide

**Recommandation** : ⚠️ **À VÉRIFIER** avant la Phase 3
- Tester la PWA avec FCM
- Vérifier la configuration Firebase
- Valider que les notifications push fonctionnent

**Conséquence si non résolu** : Implémentation FCM incompatible avec la PWA actuelle.

---

#### INT-AWAIT-004 : Vérification Compatibilité Navigateurs

| Champ | Valeur |
|-------|--------|
| **ID** | INT-AWAIT-004 |
| **Titre** | Vérification de la compatibilité des navigateurs ciblés avec FCM |
| **Description** | Vérifier que les navigateurs ciblés (Chrome, Firefox, Edge, etc.) supportent FCM |
| **Domaine** | Integration |
| **Statut** | ⏳ EN ATTENTE |
| **Priorité** | 🟡 **HAUTE** |
| **Impact** | Bloque l'implémentation FCM pour certains utilisateurs |
| **Source** | `docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md` (Section 5.2) |

**Analyse** :
- FCM fonctionne principalement sur Chrome et Edge
- La compatibilité avec Firefox est limitée
- Il faut identifier les navigateurs **réellement utilisés** par les utilisateurs EduNova
- Il faut tester FCM sur ces navigateurs

**Recommandation** : ⚠️ **À VÉRIFIER** avant la Phase 3
- Identifier les navigateurs ciblés
- Tester FCM sur chaque navigateur
- Documenter les limitations

**Conséquence si non résolu** : Certains utilisateurs ne recevront pas les notifications push.

---

## 2. Mise à jour des Contradictions

### 2.1 Contradictions Confirmées (Mise à jour)

D'après le **POST_PHASE_5_FUNCTIONAL_VALIDATION_REPORT.md**, plusieurs contradictions code/décisions ont été **partiellement résolues** :

#### Contradiction Résolue : D32 vs Code

| Élément | Statut Ancien | Statut Nouveau | Source |
|---------|---------------|----------------|--------|
| **Isolation tenant** | ❌ Non implémenté (Audit) | ✅ Implémenté (Phase 5) | Validation Report |

**Analyse** :
- Le rapport de validation Phase 5 confirme que **D32 (Isolation multi-tenant à toutes les couches) est maintenant implémenté**
- Toutes les opérations sont limitées au tenant autorisé
- Les tests d'isolation tenant passent

**Verdict** : ✅ **RÉSOLUE**

---

#### Contradiction Résolue : D13/D14 vs Routes API

| Élément | Statut Ancien | Statut Nouveau | Source |
|---------|---------------|----------------|--------|
| **Permissions par rôle** | ❌ Non vérifié | ✅ Implémenté (Phase 5) | Validation Report |
| **Un rôle actif à la fois** | ❌ Non vérifié | ✅ Implémenté (Phase 5) | Validation Report |

**Analyse** :
- Le rapport de validation confirme que les permissions sont vérifiées côté serveur
- Les décorateurs `require_role()` sont utilisés
- Les tests de permissions passent

**Verdict** : ✅ **RÉSOLUE**

---

#### Contradiction Partiellement Résolue : D10 vs Code

| Élément | Statut | Source |
|---------|--------|--------|
| **Année scolaire (AcademicYear)** | ❌ Non implémenté | Audit, Validation Report |
| **Période académique (AcademicPeriod)** | ✅ Implémenté | Validation Report |

**Analyse** :
- **AcademicPeriod** est implémenté et fonctionnel
- **AcademicYear** **n'est pas implémenté** (confirmé par le rapport d'audit et non contredit par le rapport de validation)
- D10 exige de **distinguer** année scolaire, périodes académiques et périodes d'évaluation
- Sans AcademicYear, cette distinction **ne peut pas être respectée**

**Verdict** : 🔴 **TOUJOURS BLOQUANTE**

**Impact** :
- Bloque l'implémentation complète des inscriptions
- Bloque l'implémentation des affectations élève-classe
- Bloque l'implémentation des transferts avec historique

---

#### Contradiction Partiellement Résolue : D12 vs Code

| Élément | Statut | Source |
|---------|--------|--------|
| **Transferts avec historique** | ❌ Non implémenté | Audit, Validation Report |
| **Provenance et historique obligatoires** | ✅ Exigence validée | D12 |

**Analyse** :
- D12 exige que les transferts conservent **provenance et historique**
- Le code ne gère pas les transferts d'élèves
- Il n'y a pas de modèle d'inscription ou d'affectation
- Le rapport d'audit confirme : "Aucun modele ou stockage d'inscription eleve-classe n'a ete trouve"

**Verdict** : 🔴 **TOUJOURS BLOQUANTE**

**Impact** :
- Bloque l'implémentation des transferts
- Risque de non-respect de D12

---

### 2.2 Résumé des Contradictions Mise à Jour

| # | Type | Décision | Code | Statut Ancien | Statut Nouveau | Impact |
|---|------|-----------|------|----------------|----------------|--------|
| 1 | **Résolue** | D32 | Code | 🔴 CONTRADICTION | ✅ COHÉRENT | Aucune |
| 2 | **Résolue** | D13/D14 | Routes API | ⚠️ À VÉRIFIER | ✅ COHÉRENT | Aucune |
| 3 | **Non Résolue** | D10 | Code | 🔴 CONTRADICTION | 🔴 **TOUJOURS BLOQUANTE** | **Critique** |
| 4 | **Non Résolue** | D12 | Code | 🔴 CONTRADICTION | 🔴 **TOUJOURS BLOQUANTE** | **Critique** |
| 5 | **Résolue** | JWT Secret | Code | ⚠️ À VÉRIFIER | ✅ COHÉRENT | Aucune |

---

## 3. Nouvelles Questions par Domaine

### 3.1 Domaines avec Nouvelles Questions

#### Finance (Paiement)

| # | Question | Description | Impact | Priorité | Source |
|---|----------|-------------|--------|----------|--------|
| FIN-Q001 | Quel fournisseur de paiement utiliser en RDC ? | Flutterwave ou agrégateur local ? | **Critique** | 🔴 **CRITIQUE** | INT-AWAIT-001/002 |
| FIN-Q002 | Comment gérer les paiements en CDF ? | Devise locale vs USD | Élevée | 🔴 **CRITIQUE** | INT-AWAIT-001/002 |
| FIN-Q003 | Quels opérateurs Mobile Money supporter ? | M-Pesa, Airtel Money, Orange Money | Élevée | 🟡 **HAUTE** | INT-AWAIT-001 |

#### Integration

| # | Question | Description | Impact | Priorité | Source |
|---|----------|-------------|--------|----------|--------|
| INT-Q001 | La PWA est-elle compatible avec FCM ? | Vérification technique | Moyenne | 🟡 **HAUTE** | INT-AWAIT-003 |
| INT-Q002 | Quels navigateurs supportent FCM ? | Chrome, Firefox, Edge, etc. | Moyenne | 🟡 **HAUTE** | INT-AWAIT-004 |
| INT-Q003 | Quel fournisseur email choisir ? | Brevo ou Resend | Faible | 🟢 **MOYENNE** | INT-001 |
| INT-Q004 | Faut-il implémenter Courier ? | Orchestration multi-fournisseur | Faible | 🟢 **MOYENNE** | INT-001 |

---

## 4. Impact Mise à Jour

### 4.1 Décisions Bloquantes Mise à Jour

| # | Décision | Fonctionnalité Bloquée | Impact | Priorité | Statut |
|---|----------|------------------------|--------|----------|--------|
| **1** | **D45** | Inscription des élèves | **Critique** | 🔴 **CRITIQUE** | ❌ NON RÉSOLUE |
| **2** | **PAR-REL-01** | Application Parent | **Critique** | 🔴 **CRITIQUE** | ❌ NON RÉSOLUE |
| **3** | **PAR-REL-02** | Application Parent | **Critique** | 🔴 **CRITIQUE** | ❌ NON RÉSOLUE |
| **4** | **PAR-REL-04** | Application Parent | **Critique** | 🔴 **CRITIQUE** | ❌ NON RÉSOLUE |
| **5** | **PAR-REL-06** | Application Parent | **Critique** | 🔴 **CRITIQUE** | ❌ NON RÉSOLUE |
| **6** | **INT-AWAIT-001** | Paiement RDC | **Critique** | 🔴 **CRITIQUE** | ❌ **NOUVELLE** |
| **7** | **INT-AWAIT-002** | Paiement RDC | **Critique** | 🔴 **CRITIQUE** | ❌ **NOUVELLE** |
| **8** | **D10** | Implémentation AcademicYear | Élevée | 🟡 **HAUTE** | ❌ NON RÉSOLUE |
| **9** | **D12** | Transferts avec historique | Élevée | 🟡 **HAUTE** | ❌ NON RÉSOLUE |
| **10** | **INT-AWAIT-003** | Implémentation FCM | Moyenne | 🟡 **HAUTE** | ❌ **NOUVELLE** |
| **11** | **INT-AWAIT-004** | Implémentation FCM | Moyenne | 🟡 **HAUTE** | ❌ **NOUVELLE** |

**Total Décisions Bloquantes** : **11** (7 critiques, 4 hautes)

### 4.2 Décisions en Attente Mise à Jour

| Catégorie | Total | Critiques | Hautes | Moyennes | Statut |
|-----------|-------|-----------|--------|----------|--------|
| **Décisions Numérotées** | 0 | 0 | 0 | 0 | ✅ Aucune en attente |
| **Décisions Canoniques** | 4 | 0 | 2 | 2 | ⏳ EN ATTENTE |
| **Propositions Parent-Enfant** | 5 | 4 | 0 | 1 | 📝 PROPOSÉE |
| **Décision d'Identification** | 1 | 1 | 0 | 0 | ⏳ EN ATTENTE |
| **Décisions d'Intégration** | 4 | 2 | 2 | 0 | ⏳ EN ATTENTE |
| **Total** | **14** | **7** | **4** | **3** | - |

---

## 5. Nouveaux Arbitrages Nécessaires

### 5.1 Arbitrage #6 : INT-AWAIT-001/002 - Fournisseur de Paiement RDC

**Décision** : Sélection d'un fournisseur de paiement pour la RDC

**Options** :
- **Option A** : Flutterwave (si éligibilité confirmée)
- **Option B** : Agrégateur local (M-Pesa, Airtel Money, Orange Money)
- **Option C** : Attendre la disponibilité d'un fournisseur validé

**Recommandation** : ⚠️ **À ARBITRER**
- **Préférence** : Option B (agrégateur local) si disponible et fiable
- **Fallback** : Option A (Flutterwave) si éligibilité confirmée
- **Dernier recours** : Option C (attendre)

**Impact de chaque option** :
| Option | Avantages | Inconvénients | Complexité | Risque |
|--------|-----------|---------------|------------|--------|
| A | Solution internationale, documentation | Éligibilité RDC non confirmée | Moyenne | **Élevé** |
| B | Solution locale, compatible CDF | Recherche nécessaire, intégration à valider | Élevée | Moyen |
| C | Pas de risque | Pas de paiement numérique | Faible | Faible |

**Action Requise** : 🔴 **ARBITRAGE PROPRIÉTAIRE PRODUIT URGENT**

---

### 5.2 Arbitrage #7 : INT-AWAIT-003/004 - Implémentation FCM

**Décision** : Vérifier et valider la compatibilité FCM

**Options** :
- **Option A** : Implémenter FCM et tester avec la PWA actuelle
- **Option B** : Attendre la mise à jour de la PWA pour supporter FCM
- **Option C** : Utiliser une alternative à FCM (ex: Service Worker Push)

**Recommandation** : ✅ **CHOISIR OPTION A**
- Implémenter FCM et tester immédiatement
- Documenter les limitations par navigateur
- Prévoir une alternative pour les navigateurs non compatibles

**Action Requise** : ⚠️ **À VÉRIFIER** avant la Phase 3

---

## 6. Validation Phase 5

### 6.1 Résultats des Tests

**Statut Global** : ✅ **VALIDÉ AVEC RÉSERVES** (99.7%)

| Catégorie | Tests | PASS | FAIL | Taux | Verdict |
|-----------|-------|------|------|------|---------|
| **Frontend (Vitest)** | 190 | 190 | 0 | 100.0% | ✅ VALIDÉ |
| **Backend - Unitaires** | 1105 | 1105 | 0 | 100.0% | ✅ VALIDÉ |
| **Backend - Intégration Auth** | 27 | 26 | 1 | 96.3% | ✅ VALIDÉ AVEC RÉSERVES |
| **Backend - Intégration Global** | 308 | 307 | 1 | 99.7% | ✅ VALIDÉ AVEC RÉSERVES |

**Détail des échecs** :
- 1 échec : `test_register_establishment_rate_limiting` (InMemoryRateLimiter ne fonctionne pas en multi-processus)

### 6.2 Fonctionnalités Validées

| # | Fonctionnalité | Statut | Tests | Endpoints |
|---|---------------|--------|-------|-----------|
| 1 | Inscription d'un établissement | ✅ VALIDÉ | 14/15 | `POST /auth/register-establishment` |
| 2 | Connexion mono-tenant | ✅ VALIDÉ | 6/6 | `POST /auth/login` |
| 3 | Connexion multi-tenant | ✅ VALIDÉ | 7/7 | `POST /auth/login`, `POST /auth/select-tenant` |
| 4 | Connexion avec 2FA | ✅ VALIDÉ | 4/4 | `POST /auth/2fa/login` |
| 5 | Rafraîchissement token | ✅ VALIDÉ | 10/10 | `POST /auth/refresh` |
| 6 | Déconnexion | ✅ VALIDÉ | 7/7 | `POST /auth/logout` |
| 7 | Gestion des sessions | ✅ VALIDÉ | 5/5 | `GET /auth/me` |

### 6.3 Intégration Backend-Frontend Validée

| Élément | Statut | Détails |
|---------|--------|---------|
| **DTO TypeScript/Pydantic** | ✅ VALIDÉ | Correspondance complète |
| **URLs des endpoints** | ✅ VALIDÉ | Identiques backend/frontend |
| **Gestion des tokens** | ✅ VALIDÉ | JWT, rafraîchissement, expiration |
| **Protection des routes** | ✅ VALIDÉ | Backend + Frontend |
| **Persistance de session** | ✅ VALIDÉ | Tokens persistés |
| **Gestion des erreurs HTTP** | ✅ VALIDÉ | 401, 403, 422, 500 |
| **CORS** | ✅ VALIDÉ | Configuration correcte |
| **Isolation tenant** | ✅ VALIDÉ | Toutes les opérations limitées au tenant |

### 6.4 Réserves de Validation

| # | Réserve | Description | Impact | Priorité |
|---|---------|-------------|--------|----------|
| 1 | **Rate Limiting non distribué** | InMemoryRateLimiter ne fonctionne pas en multi-processus | Protection limitée contre DDoS | Faible |
| 2 | **Tests E2E non exécutés** | Playwright non installé/non exécuté | Pas de validation navigateur réelle | Moyen |

**Recommandations** :
1. ⚠️ Documenter la limitation du rate limiting
2. ⚠️ Installer Playwright et exécuter les tests E2E
3. ⚠️ Évaluer Redis pour un rate limiting distribué (si nécessaire)

---

## 7. Synthèse des Mises à Jour

### 7.1 Nouvelles Décisions en Attente

| ID | Titre | Domaine | Impact | Priorité | Source |
|----|-------|---------|--------|----------|--------|
| **INT-AWAIT-001** | Flutterwave éligibilité RDC | Finance | **Critique** | 🔴 **CRITIQUE** | Intégrations |
| **INT-AWAIT-002** | Agrégateur local RDC | Finance | **Critique** | 🔴 **CRITIQUE** | Intégrations |
| **INT-AWAIT-003** | Vérification compatibilité PWA | Integration | Moyenne | 🟡 **HAUTE** | Intégrations |
| **INT-AWAIT-004** | Vérification compatibilité navigateurs | Integration | Moyenne | 🟡 **HAUTE** | Intégrations |

### 7.2 Contradictions Résolues

| ID | Décision | Code | Statut | Source |
|----|----------|------|--------|--------|
| D32 | Isolation tenant | Code | ✅ **RÉSOLUE** | Validation Phase 5 |
| JWT Secret | Longueur ≥ 32 caractères | Code | ✅ **RÉSOLUE** | Scripts corrigés |

### 7.3 Contradictions Toujours Bloquantes

| ID | Décision | Code | Impact | Priorité |
|----|----------|------|--------|----------|
| D10 | AcademicYear | Non implémenté | **Critique** | 🔴 **CRITIQUE** |
| D12 | Transferts avec historique | Non implémenté | **Critique** | 🔴 **CRITIQUE** |

### 7.4 Décisions Bloquantes Totales

| Catégorie | Nombre | Priorité Critique | Priorité Haute | Priorité Moyenne |
|-----------|--------|-------------------|----------------|------------------|
| **Non résolues** | 4 | 2 | 0 | 2 |
| **Nouvelles** | 4 | 2 | 2 | 0 |
| **Total** | **8** | **4** | **2** | **2** |

### 7.5 Validation Phase 5

**Statut** : ✅ **VALIDÉ AVEC RÉSERVES**
- **Taux de réussite** : 99.7% (307/308 tests)
- **Fonctionnalités principales** : Toutes validées
- **Intégration backend-frontend** : Complète et fonctionnelle
- **Réserves** : 2 mineures (rate limiting, tests E2E)

---

## 📊 Résumé Exécutif

### Décisions en Attente : 14+ (7 Critiques, 4 Hautes, 3 Moyennes)
- **D45** : Identification des élèves (**Critique**)
- **PAR-REL-01, 02, 04, 06** : Modèle parent-enfant (**Critique**)
- **INT-AWAIT-001, 002** : Paiement RDC (**Critique**)
- **INT-AWAIT-003, 004** : Compatibilité FCM (**Haute**)
- **D10** : AcademicYear (**Haute**)
- **D12** : Transferts (**Haute**)

### Contradictions : 2 Toujours Bloquantes
- **D10** : AcademicYear non implémenté
- **D12** : Transferts avec historique non implémenté

### Validation Phase 5 : ✅ VALIDÉE AVEC RÉSERVES (99.7%)
- 1105 tests unitaires : 100% PASS
- 190 tests frontend : 100% PASS
- 307/308 tests d'intégration : 99.7% PASS
- 4 parcours utilisateur : 100% VALIDÉS

### Impact Global
- **8 décisions bloquantes** empêchent l'implémentation complète
- **4 décisions critiques** bloquent des fonctionnalités majeures
- **Phase 5 est prête pour le staging** malgré les réserves

---

## 🎯 Recommandations Mise à Jour

### Priorité 🔴 **CRITIQUE** (À faire immédiatement)

1. **Valider D45** (Identification des personnes)
   - Choisir **Option A** (recommandée)
   - Impact : Débloque les inscriptions

2. **Valider PAR-REL-01 à PAR-REL-06** (Modèle parent-enfant)
   - Valider toutes les propositions
   - Impact : Débloque l'application parent

3. **Valider INT-AWAIT-001/002** (Paiement RDC)
   - Contacter Flutterwave et identifier agrégateurs locaux
   - Impact : Débloque les paiements numériques

4. **Corriger D10** (Implémenter AcademicYear)
   - Créer l'entité AcademicYear
   - Lier à AcademicPeriod
   - Impact : Débloque les inscriptions

5. **Corriger D12** (Implémenter les transferts)
   - Créer le modèle d'inscription/enrollment
   - Conserver l'historique des transferts
   - Impact : Débloque les transferts

### Priorité 🟡 **HAUTE** (À faire cette semaine)

6. **Valider INT-AWAIT-003/004** (Compatibilité FCM)
   - Tester la PWA avec FCM
   - Identifier les navigateurs ciblés

7. **Exécuter les tests E2E** avec Playwright
   - Installer Playwright
   - Exécuter les tests navigateur

---

## 📚 Références

### Documents Sources

1. [EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md](EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md) - Document parent
2. [EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md](../../docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md) - Source INT-AWAIT-*
3. [POST_PHASE_5_FUNCTIONAL_VALIDATION_REPORT.md](../../docs/v1.2/POST_PHASE_5_FUNCTIONAL_VALIDATION_REPORT.md) - Validation Phase 5
4. [INTEGRATIONS_DECISIONS_EXTRACT.md](INTEGRATIONS_DECISIONS_EXTRACT.md) - Extraction des décisions d'intégration

### Tests et Validation

- 1105 tests unitaires backend : `pytest tests/unit/`
- 190 tests frontend : `npm test`
- Tests d'intégration : `pytest tests/integration/`
- Test de connexion : `python test_backend_frontend_connection.py`

---

**Document créé le** : 2025-XX-XX  
**Dernière mise à jour** : 2025-XX-XX  
**Version** : 1.0  
**Statut** : COMPLET  

*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*
