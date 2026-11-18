# Addendum Intégrations - Décisions, Contradictions et Questions Ouvertes

> **Document Parent** : EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md  
> **Source** : docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md  
> **Date** : 2025-XX-XX  
> **Statut** : EN COURS  

---

## 📋 Table des Matières

1. [Nouvelles Décisions Validées](#1-nouvelles-décisions-validées)
2. [Nouvelles Décisions en Attente](#2-nouvelles-décisions-en-attente)
3. [Potentielles Contradictions avec Décisions Existantes](#3-potentielles-contradictions-avec-décisions-existantes)
4. [Propositions Non Validées](#4-propositions-non-validées)
5. [Impact sur la Spécification DDD](#5-impact-sur-la-spécification-ddd)

---

## 1. Nouvelles Décisions Validées

### 1.1 Principes Non Négociables (INT-001 à INT-010)

Ces 10 principes sont **explicitement validés** et doivent être respectés dans toutes les implémentations :

| ID | Principe | Cohérence avec Décisions Existantes | Statut |
|----|----------|------------------------------------|--------|
| **INT-001** | EduNova = source de vérité | ✅ Cohérent avec D1-D44 (EduNova gère toutes les données métier) | ✅ VALIDÉE |
| **INT-002** | Pas de propriété externe | ✅ Cohérent avec D1-D44 | ✅ VALIDÉE |
| **INT-003** | Isolation multi-tenant stricte | ✅ **Cohérent avec D32** (Isolation à toutes les couches) | ✅ VALIDÉE |
| **INT-004** | Appels externes côté serveur | ✅ Cohérent avec D32, D13 | ✅ VALIDÉE |
| **INT-005** | Pas de secrets dans frontend | ✅ Cohérent avec les principes de sécurité | ✅ VALIDÉE |
| **INT-006** | Opérations asynchrones contrôlées | ✅ Cohérent avec les bonnes pratiques | ✅ VALIDÉE |
| **INT-007** | Résilience aux pannes externes | ✅ Cohérent avec la résilience attendue | ✅ VALIDÉE |
| **INT-008** | Intégrations optionnelles | ✅ Cohérent avec l'autonomie des établissements | ✅ VALIDÉE |
| **INT-009** | Pas de microservices non justifiés | ✅ Cohérent avec l'architecture monolithe | ✅ VALIDÉE |
| **INT-010** | Quotas gratuits = limites de démarrage | ✅ Nouveau principe | ✅ VALIDÉE |

**Analyse** : Toutes ces décisions sont **cohérentes** avec les décisions existantes et **renforcent** les principes DDD déjà validés.

### 1.2 Décisions Architecturales

| ID | Décision | Domaine | Statut |
|----|----------|---------|--------|
| **INT-ARC-001** | Conserver le style architectural réel (monolithe modulaire) | Architecture | ✅ VALIDÉE |
| **INT-ARC-002** | Créer un Bounded Context "Integration" | Architecture | ✅ VALIDÉE |
| **INT-EXEC-001** | Flux d'exécution avec outbox/idempotence | Integration | ✅ VALIDÉE |
| **INT-EXEC-002** | Pas de Redis sans justification | Integration | ✅ VALIDÉE |

**Analyse** : Ces décisions sont **cohérentes** avec l'architecture actuelle et les principes DDD.

### 1.3 Décisions de Sécurité (INT-SEC-001 à INT-SEC-031)

Toutes les **31 décisions de sécurité** sont **validées** et **renforcent** les principes existants :
- Isolation tenant (D32)
- Audit des opérations (D31)
- Protection des données sensibles

**Points clés** :
- **INT-SEC-001 à INT-SEC-006** : Isolation tenant stricte
- **INT-SEC-007 à INT-SEC-013** : Gestion sécurisée des secrets et OAuth
- **INT-SEC-014 à INT-SEC-022** : Sécurité des webhooks
- **INT-SEC-023 à INT-SEC-031** : Protection des données scolaires dans l'analytics

**Analyse** : Ces décisions **complètent** D31, D32 et renforcent la sécurité globale.

### 1.4 Décisions par Module

#### Communication & Notifications
- **7 use cases** (INT-COM-UC001 à INT-COM-UC007)
- **7 événements métier** (INT-COM-EVT001 à INT-COM-EVT007)
- **5 règles métier** (INT-COM-R001 à INT-COM-R005)
- **6 états de notification** (INT-COM-ST001 à INT-COM-ST006)
- **6 critères d'acceptation** (INT-COM-CA001 à INT-COM-CA006)

**Statut** : ✅ **TOUTES VALIDÉES**

#### Finance (Paiements)
- **12 règles critiques** (INT-PAY-000 à INT-PAY-011)
- Inclut la **règle absolue** : "Finance reste la source de vérité"

**Analyse** : Ces règles sont **cohérentes** avec FIN-ROLE-01, FIN-COR-01, FIN-REC-01.

**Point d'attention** : INT-PAY-008 (Comptabilisation via Finance) **renforce** la séparation des responsabilités.

#### Push, Calendrier, Classroom, Moodle, Classes Virtuelles
- **8 + 8 + 11 + 8 + 8 = 43 décisions** validées

**Analyse** : Toutes ces décisions sont **cohérentes** avec les principes DDD et les décisions existantes.

---

## 2. Nouvelles Décisions en Attente

### 2.1 Paiement RDC (🔴 CRITIQUE)

| ID | Décision | Description | Domaine | Impact | Priorité | Source |
|----|----------|-------------|---------|--------|----------|--------|
| **INT-AWAIT-001** | Flutterwave éligibilité RDC | Vérifier si Flutterwave supporte la RDC, le CDF et les opérateurs Mobile Money (M-Pesa, Airtel Money, Orange Money) | Finance | **Bloque les paiements en RDC** | 🔴 **CRITIQUE** | Section 5.7 |
| **INT-AWAIT-002** | Agrégateur local RDC | Rechercher et valider un fournisseur réellement contractable en RDC et prenant en charge les moyens demandés | Finance | **Bloque les paiements en RDC** | 🔴 **CRITIQUE** | Section 5.7 |

**Analyse** : Ces deux décisions sont **critiques** car elles bloquent l'activation des paiements numériques en production pour les établissements en RDC.

**Recommandation** : 🔴 **ARBITRAGE PROPRIÉTAIRE PRODUIT URGENT**
- Contacter Flutterwave pour confirmation officielle
- Identifier des agrégateurs locaux en RDC
- Valider la disponibilité du CDF et des opérateurs Mobile Money

**Conséquence si non résolu** : Impossible d'activer les paiements numériques en RDC.

### 2.2 Compatibilité FCM (⚠️ HAUTE)

| ID | Décision | Description | Domaine | Impact | Priorité | Source |
|----|----------|-------------|---------|--------|----------|--------|
| **INT-AWAIT-003** | Vérification compatibilité PWA | Vérifier la compatibilité de la PWA actuelle avec FCM | Integration | Bloque l'implémentation FCM | 🟡 **HAUTE** | Section 5.2 |
| **INT-AWAIT-004** | Vérification compatibilité navigateurs | Vérifier la compatibilité des navigateurs ciblés avec FCM | Integration | Bloque l'implémentation FCM | 🟡 **HAUTE** | Section 5.2 |

**Analyse** : Ces vérifications techniques sont nécessaires avant d'implémenter FCM.

**Recommandation** : ⚠️ **À VÉRIFIER** avant la Phase 3 (FCM)

**Conséquence si non résolu** : Implémentation FCM incompatible avec les clients existants.

---

## 3. Potentielles Contradictions avec Décisions Existantes

### 3.1 INT-003 vs D32

| Décision | Description | Source | Statut |
|----------|-------------|--------|--------|
| **INT-003** | Toutes les opérations liées à un établissement sont strictement limitées à son `tenant_id` | Intégrations | ✅ VALIDÉE |
| **D32** | Isolation multi-tenant à toutes les couches (contexte, autorisation, requêtes, BD, tâches) | REGISTRE | ✅ VALIDÉE |

**Analyse** : 
- INT-003 et D32 sont **complémentaires**, pas contradictoires
- INT-003 **précise** que l'isolation s'applique aussi aux **opérations externes** (appels API, webhooks, etc.)
- D32 couvre l'isolation **interne** (BD, requêtes, etc.)

**Conclusion** : ⚪ **PAS DE CONTRADICTION** - Ces décisions se renforcent mutuellement.

### 3.2 INT-004 vs D13

| Décision | Description | Source | Statut |
|----------|-------------|--------|--------|
| **INT-004** | Les appels externes sont exécutés côté serveur, sauf SDK explicitement conçu pour usage client sans secret | Intégrations | ✅ VALIDÉE |
| **D13** | Les permissions sont définies par rôle et peuvent être configurées par établissement | REGISTRE | ✅ VALIDÉE |

**Analyse** : 
- INT-004 **renforce** D13 en imposant que les appels externes (qui nécessitent souvent des permissions élevées) passent par le serveur
- Cela garantit que les **règles D13 sont appliquées côté serveur** avant tout appel externe

**Conclusion** : ⚪ **PAS DE CONTRADICTION** - Cohérence totale.

### 3.3 INT-005 vs INT-SEC-007

| Décision | Description | Source | Statut |
|----------|-------------|--------|--------|
| **INT-005** | Les secrets ne sont jamais placés dans le frontend | Intégrations | ✅ VALIDÉE |
| **INT-SEC-007** | Aucun secret dans VITE_*, code JavaScript, localStorage ou bundle frontend | Intégrations | ✅ VALIDÉE |

**Analyse** : 
- INT-SEC-007 **précise** les cas concrets où INT-005 s'applique
- Les deux décisions sont **cohérentes** et **complémentaires**

**Conclusion** : ⚪ **PAS DE CONTRADICTION**

### 3.4 INT-PAY-010 vs D24

| Décision | Description | Source | Statut |
|----------|-------------|--------|--------|
| **INT-PAY-010** | USD et CDF restent des devises distinctes ; aucune conversion implicite | Intégrations | ✅ VALIDÉE |
| **D24** | Séparation stricte des devises USD et CDF | REGISTRE | ✅ VALIDÉE |

**Analyse** : 
- INT-PAY-010 **confirme** D24 dans le contexte des intégrations de paiement
- Les deux décisions sont **identiques** dans leur intention

**Conclusion** : ⚪ **PAS DE CONTRADICTION** - Redondance positive.

### 3.5 INT-SEC-001 vs D32

| Décision | Description | Source | Statut |
|----------|-------------|--------|--------|
| **INT-SEC-001** | Chaque configuration, événement, abonnement, webhook, identifiant externe, tâche et résultat doit être rattaché au tenant | Intégrations | ✅ VALIDÉE |
| **D32** | Isolation multi-tenant à toutes les couches | REGISTRE | ✅ VALIDÉE |

**Analyse** : 
- INT-SEC-001 **applique** D32 spécifiquement aux intégrations
- Elle **étend** la portée de D32 aux ressources externes (webhooks, tâches, etc.)

**Conclusion** : ⚪ **PAS DE CONTRADICTION** - Application spécifique de D32.

### 3.6 INT-PAY-008 vs FIN-COR-01

| Décision | Description | Source | Statut |
|----------|-------------|--------|--------|
| **INT-PAY-008** | Comptabiliser le paiement via le use case Finance existant, jamais en écrivant directement dans les tables depuis le contrôleur webhook | Intégrations | ✅ VALIDÉE |
| **FIN-COR-01** | Mécanisme de correction/contre-écriture existant | REGISTRE | ✅ VALIDÉE |

**Analyse** : 
- INT-PAY-008 **applique** FIN-COR-01 dans le contexte des intégrations de paiement
- Elle **renforce** la séparation des responsabilités entre Integration et Finance

**Conclusion** : ⚪ **PAS DE CONTRADICTION** - Cohérence totale.

---

## 4. Propositions Non Validées

### 4.1 Use Cases Communication (7)

| ID | Use Case | Statut | Impact |
|----|----------|--------|--------|
| **INT-COM-UC001** | `CreateNotification` | 📝 PROPOSÉE | Moyenne |
| **INT-COM-UC002** | `DispatchNotification` | 📝 PROPOSÉE | Moyenne |
| **INT-COM-UC003** | `ManageNotificationPreferences` | 📝 PROPOSÉE | Moyenne |
| **INT-COM-UC004** | `RegisterDeviceToken` | 📝 PROPOSÉE | Moyenne |
| **INT-COM-UC005** | `RevokeDeviceToken` | 📝 PROPOSÉE | Moyenne |
| **INT-COM-UC006** | `RetryFailedNotification` | 📝 PROPOSÉE | Moyenne |
| **INT-COM-UC007** | `GetNotificationDeliveryStatus` | 📝 PROPOSÉE | Moyenne |

**Analyse** : Ces use cases sont **proposés** mais nécessitent une validation métier.

**Recommandation** : ⚠️ **À VALIDER** avec les experts métier Communication.

**Impact si non validés** : Bloque l'implémentation complète du module Communication.

### 4.2 Événements Métier (7)

| ID | Événement | Statut | Impact |
|----|-----------|--------|--------|
| **INT-COM-EVT001** | Inscription validée | 📝 PROPOSÉE | Moyenne |
| **INT-COM-EVT002** | Absence enregistrée | 📝 PROPOSÉE | Moyenne |
| **INT-COM-EVT003** | Résultat publié | 📝 PROPOSÉE | Moyenne |
| **INT-COM-EVT004** | Bulletin disponible | 📝 PROPOSÉE | Moyenne |
| **INT-COM-EVT005** | Facture émise | 📝 PROPOSÉE | Moyenne |
| **INT-COM-EVT006** | Paiement confirmé | 📝 PROPOSÉE | Moyenne |
| **INT-COM-EVT007** | Annonce publiée | 📝 PROPOSÉE | Moyenne |

**Analyse** : Ces événements doivent être **validés** avec les workflows métier existants.

**Recommandation** : ⚠️ **À VALIDER** avec les experts métier.

**Note** : Certains événements peuvent déjà exister dans le code (ex: bulletin disponible). Il faut vérifier avant de les dupliquer.

### 4.3 Use Cases Paiement (6)

| ID | Use Case | Statut | Impact |
|----|----------|--------|--------|
| `InitiateExternalPayment` | 📝 PROPOSÉE | Moyenne |
| `ReceivePaymentProviderWebhook` | 📝 PROPOSÉE | Moyenne |
| `VerifyExternalPayment` | 📝 PROPOSÉE | Moyenne |
| `ReconcileExternalPayment` | 📝 PROPOSÉE | Moyenne |
| `HandlePaymentFailure` | 📝 PROPOSÉE | Moyenne |
| `RequestPaymentRefund` | 📝 PROPOSÉE (sous réserve de FIN-COR-01) | Moyenne |

**Analyse** : Ces use cases sont **cohérents** avec FIN-COR-01 et les règles de paiement.

**Recommandation** : ✅ **POUVENT ÊTRE VALIDÉS** une fois que INT-AWAIT-001 et INT-AWAIT-002 sont résolues.

---

## 5. Impact sur la Spécification DDD

### 5.1 Nouveau Bounded Context : Integration

Le document d'intégrations **confirme** la création d'un **Bounded Context Integration** avec les responsabilités suivantes :

1. **Configuration et activation** des connecteurs
2. **Cycle de vie des autorisations externes** (OAuth, tokens)
3. **Routage** vers les adaptateurs
4. **Gestion des webhooks entrants**
5. **Suivi des synchronisations**
6. **Quotas et états de santé**
7. **Journalisation technique et audit**

**Ports identifiés** :
- `EmailProvider`
- `PushProvider`
- `CalendarProvider`
- `ClassroomProvider`
- `LmsProvider`
- `VideoMeetingProvider`
- `PaymentProvider`
- `ProductAnalyticsProvider`

**Recommandation** : ⚠️ **À INTÉGRER** dans la Section 7 (Bounded Contexts) de EDUNOVA_FUNCTIONAL_DDD_SPECIFICATION.md.

### 5.2 Context Map : Relations entre Contextes

Le document implique les relations suivantes entre Bounded Contexts :

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Academic       │──────▶│  Integration    │──────▶│   External      │
│                 │       │                 │       │   Services      │
└─────────────────┘       └─────────────────┘       └─────────────────┘
       ▲                                                                 
       │                                                                 
       ▼                                                                 
┌─────────────────┐       ┌─────────────────┐
│   Finance        │──────▶│  Integration    │
│                 │       │                 │
└─────────────────┘       └─────────────────┘
       ▲
       │
┌─────────────────┐
│ Communication   │
│                 │
└─────────────────┘
```

**Relations** :
- **Academic → Integration** : Academic publie des événements (ex: résultat publié) que Integration transmet aux services externes
- **Finance → Integration** : Finance utilise Integration pour les paiements externes
- **Communication → Integration** : Communication utilise Integration pour l'envoi d'emails et push
- **Integration → External Services** : Integration appelle les services externes via les ports

**Recommandation** : ⚠️ **À INTÉGRER** dans la Section 10 (Context Map) de EDUNOVA_FUNCTIONAL_DDD_SPECIFICATION.md.

### 5.3 Règles de Sécurité à Intégrer

Les **31 règles de sécurité** (INT-SEC-001 à INT-SEC-031) doivent être intégrées dans :
- Section 8 (Règles transversales non négociables)
- Section 4 (Acteurs et responsabilités) - pour les permissions
- Section 6 (Registre des décisions)

**Recommandation** : ⚠️ **À INTÉGRER** dans les sections appropriées.

### 5.4 Workflows à Compléter

Le document d'intégrations **propose** des workflows pour :
1. Notifications (création → dispatch → livraison)
2. Paiements (initiation → webhook → confirmation → comptabilisation)
3. Synchronisation calendrier (connect → sync → manage)

**Recommandation** : ⚠️ **À INTÉGRER** dans la Section 11 (Workflows détaillés).

---

## 📊 Synthèse

### Décisions Validées : 160+
- 10 principes non négociables
- 3 décisions architecturales
- 31 décisions de sécurité
- 43+ décisions par module fonctionnel
- 8 ports/contrats
- 6 décisions d'exécution
- 10 décisions techniques

### Décisions en Attente : 4
- 2 **CRITIQUES** (paiement RDC)
- 2 **HAUTES** (compatibilité FCM)

### Propositions : 20+
- 7 use cases Communication
- 7 événements métier
- 6 use cases Paiement

### Contradictions : 0
Toutes les décisions du document d'intégrations sont **cohérentes** avec les décisions existantes (D1-D44, FIN-*, BUL-*).

---

## 🎯 Actions Recommandées

### Priorité 🔴 CRITIQUE
1. **Résoudre INT-AWAIT-001 et INT-AWAIT-002** (Paiement RDC)
   - Contacter Flutterwave pour éligibilité RDC
   - Identifier agrégateurs locaux
   - Valider opérateurs Mobile Money

### Priorité 🟡 HAUTE
2. **Valider les use cases et événements Communication** (INT-COM-UC*, INT-COM-EVT*)
   - Vérifier avec les experts métier
   - Confirmer qu'ils ne dupliquent pas des fonctionnalités existantes

3. **Vérifier la compatibilité FCM** (INT-AWAIT-003, INT-AWAIT-004)
   - Tester avec la PWA actuelle
   - Vérifier les navigateurs ciblés

### Priorité 🟢 MOYENNE
4. **Intégrer le Bounded Context Integration** dans la spécification DDD
5. **Mettre à jour le Context Map**
6. **Ajouter les règles de sécurité** aux sections appropriées
7. **Compléter les workflows** avec les informations des intégrations

---

## 📝 Notes de Traçabilité

| Décision Intégrations | Décision Existante | Relation | Statut |
|-----------------------|--------------------|----------|--------|
| INT-003 | D32 | Complémentaire | ✅ Cohérent |
| INT-004 | D13 | Complémentaire | ✅ Cohérent |
| INT-010 | D24 | Identique | ✅ Cohérent |
| INT-SEC-001 | D32 | Application spécifique | ✅ Cohérent |
| INT-PAY-010 | FIN-COR-01 | Application spécifique | ✅ Cohérent |
| INT-PAY-008 | FIN-COR-01 | Renforcement | ✅ Cohérent |

**Conclusion** : Aucune contradiction détectée. Toutes les décisions du document d'intégrations sont **cohérentes** avec les décisions existantes.

---

**Document créé le** : 2025-XX-XX  
**Dernière mise à jour** : 2025-XX-XX  
**Version** : 1.0  
**Statut** : COMPLET pour ce document
