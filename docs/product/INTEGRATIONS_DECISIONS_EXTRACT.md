# Extrait des Décisions du Document EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md

> **Date d'extraction** : 2025-XX-XX  
> **Source** : `docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md`  
> **Objectif** : Extraire et classer les décisions, principes et règles métier pour intégration dans la spécification DDD globale.

---

## 📋 Table des Matières

1. [Décisions Explicites et Principes Non Négociables](#1-décisions-explicites-et-principes-non-négociables)
2. [Décisions Architecturales](#2-décisions-architecturales)
3. [Décisions par Module Fonctionnel](#3-décisions-par-module-fonctionnel)
4. [Décisions de Sécurité et Conformité](#4-décisions-de-sécurité-et-conformité)
5. [Décisions Techniques et d'Implémentation](#5-décisions-techniques-et-dimplémentation)
6. [Décisions de Tests et Qualité](#6-décisions-de-tests-et-qualité)
7. [Décisions en Attente de Validation](#7-décisions-en-attente-de-validation)
8. [Références et Priorités](#8-références-et-priorités)

---

## 1. Décisions Explicites et Principes Non Négociables

### 1.1 Principes Non Négociables (INT-001 à INT-010)

| ID | Principe | Description | Domaine | Statut | Priorité | Source |
|----|----------|-------------|---------|--------|----------|--------|
| **INT-001** | **EduNova comme source de vérité** | EduNova reste le système de référence pour tous les données métier (élèves, inscriptions, classes, frais, factures, paiements comptabilisés, notes, décisions scolaires) | Integration | ✅ **VALIDÉE** | **Critique** | Section 1.1 |
| **INT-002** | **Pas de propriété externe** | Un fournisseur externe ne devient jamais propriétaire des données métier EduNova | Integration | ✅ **VALIDÉE** | **Critique** | Section 1.1 |
| **INT-003** | **Isolation multi-tenant stricte** | Toutes les opérations liées à un établissement sont strictement limitées à son `tenant_id` | Integration | ✅ **VALIDÉE** | **Critique** | Section 1.1 |
| **INT-004** | **Appels externes côté serveur** | Les appels externes sont exécutés côté serveur, sauf SDK explicitement conçu pour usage client sans secret | Integration | ✅ **VALIDÉE** | **Critique** | Section 1.1 |
| **INT-005** | **Pas de secrets dans le frontend** | Les secrets ne sont jamais placés dans le frontend, dans le dépôt ou dans une réponse API | Integration | ✅ **VALIDÉE** | **Critique** | Section 1.1 |
| **INT-006** | **Opérations asynchrones contrôlées** | Les opérations asynchrones sont traçables, idempotentes, réessayables et observables | Integration | ✅ **VALIDÉE** | **Critique** | Section 1.1 |
| **INT-007** | **Résilience aux pannes externes** | Une panne externe ne doit pas empêcher l'inscription, la consultation des dossiers ou les autres fonctions essentielles | Integration | ✅ **VALIDÉE** | **Critique** | Section 1.1 |
| **INT-008** | **Integrations optionnelles** | Les intégrations sont optionnelles et désactivables par établissement | Integration | ✅ **VALIDÉE** | **Critique** | Section 1.1 |
| **INT-009** | **Pas de microservices non justifiés** | Pas de microservices, Redis ou nouvelle infrastructure distribuée sans justification mesurée. Réutiliser les mécanismes existants | Integration | ✅ **VALIDÉE** | **Critique** | Section 1.1 |
| **INT-010** | **Quotas gratuits = limites de démarrage** | Les quotas gratuits sont des limites de démarrage, pas une garantie de coût nul à l'échelle SaaS | Integration | ✅ **VALIDÉE** | Moyenne | Section 1.1 |

**Analyse** : Ces 10 principes sont **VALIDÉS** et constituent la **base non négociable** pour toutes les intégrations. Ils sont cohérents avec les décisions existantes, notamment :
- D32 (Isolation multi-tenant à toutes les couches)
- D13 (Permissions configurables par rôle)
- D31 (Audit des opérations sensibles)

**Impact** : Ces principes doivent être respectés dans toutes les implémentations futures.

---

## 2. Décisions Architecturales

### 2.1 Architecture Globale

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-ARC-001** | **Conserver le style architectural réel** | Conserver le monolithe modulaire existant. La structure cible est conceptuelle, pas une instruction de déplacer massivement les packages | Architecture | ✅ **VALIDÉE** | Section 3 |
| **INT-ARC-002** | **Bounded Context Integration** | Créer un Bounded Context "Integration" avec responsabilités : configuration, cycle de vie des autorisations, routage, webhooks, synchronisations, quotas, santé, journalisation | Architecture | ✅ **VALIDÉE** | Section 3.1 |

### 2.2 Ports / Contrats

| ID | Port | Méthodes | Domaine | Statut | Source |
|----|------|----------|---------|--------|--------|
| **INT-PORT-001** | `EmailProvider` | `send_transactional(message)` | Communication | ✅ **VALIDÉE** | Section 3.3 |
| **INT-PORT-002** | `PushProvider` | `send_to_device(notification)` | Communication | ✅ **VALIDÉE** | Section 3.3 |
| **INT-PORT-003** | `CalendarProvider` | `create_or_update_event(event)`, `delete_event(external_id)` | Academic | ✅ **VALIDÉE** | Section 3.3 |
| **INT-PORT-004** | `ClassroomProvider` | Opérations explicitement supportées | Academic | ✅ **VALIDÉE** | Section 3.3 |
| **INT-PORT-005** | `LmsProvider` | Opérations Moodle autorisées | Academic | ✅ **VALIDÉE** | Section 3.3 |
| **INT-PORT-006** | `VideoMeetingProvider` | `create_meeting(request)`, `revoke_meeting(external_id)` | Academic | ✅ **VALIDÉE** | Section 3.3 |
| **INT-PORT-007** | `PaymentProvider` | `create_payment_intent(request)`, `verify_webhook(headers, raw_body)`, `fetch_payment_status(external_reference)` | Finance | ✅ **VALIDÉE** | Section 3.3 |
| **INT-PORT-008** | `ProductAnalyticsProvider` | `capture(event)` | Analytics | ✅ **VALIDÉE** | Section 3.3 |

**Recommandation** : ⚠️ **À INTÉGRER** dans la spécification DDD comme ports du Bounded Context Integration.

### 2.3 Modèle d'Exécution

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-EXEC-001** | **Flux d'exécution** | 1. Use case valide règles + enregistre transaction. 2. Enregistre tâche/événement dans outbox persistée. 3. Dispatcher prend la tâche. 4. Résout le fournisseur activé. 5. Envoie requête avec clé d'idempotence. 6. Enregistre résultat. 7. En cas d'échec : retry borné avec backoff, puis état échec terminal | Integration | ✅ **VALIDÉE** | Section 3.4 |
| **INT-EXEC-002** | **Pas de Redis sans justification** | Si aucune infrastructure de tâches de fond durable n'existe, proposer d'abord une solution compatible avec SQLite et le déploiement actuel | Integration | ✅ **VALIDÉE** | Section 3.4 |
| **INT-EXEC-003** | **Documenter les limites multi-processus** | Si solution SQLite, documenter ses limites multi-processus | Integration | ✅ **VALIDÉE** | Section 3.4 |

**Analyse** : Ces décisions sont cohérentes avec l'architecture actuelle et les contraintes du projet.

---

## 3. Décisions par Module Fonctionnel

### 3.1 Communication & Notifications (P1)

**Objectif** : Informer les parents, élèves, enseignants et responsables au bon moment, sans spam ni perte de message.

#### Canaux
| ID | Décision | Description | Statut | Source |
|----|----------|-------------|--------|--------|
| **INT-COM-001** | **Centre de notifications interne = source de vérité** | Le centre de notifications interne est la source de vérité | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-002** | **Email comme canal secondaire** | Email transactionnel via Brevo initialement, Resend comme alternative | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-003** | **Push comme canal tertiaire** | Push via FCM, lorsque les clients compatibles existent | ✅ **VALIDÉE** | Section 5.1 |

#### Use Cases (à confirmer avec règles métier existantes)
| ID | Use Case | Description | Statut | Source |
|----|----------|-------------|--------|--------|
| **INT-COM-UC001** | `CreateNotification` | Créer une notification | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-UC002** | `DispatchNotification` | Dispatcher une notification | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-UC003** | `ManageNotificationPreferences` | Gérer les préférences de notification | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-UC004** | `RegisterDeviceToken` | Enregistrer un token d'appareil | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-UC005** | `RevokeDeviceToken` | Révoquer un token d'appareil | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-UC006** | `RetryFailedNotification` | Réessayer une notification échouée | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-UC007** | `GetNotificationDeliveryStatus` | Obtenir le statut de livraison | 📝 PROPOSÉE | Section 5.1 |

#### Événements Métier (à confirmer)
| ID | Événement | Description | Statut | Source |
|----|-----------|-------------|--------|--------|
| **INT-COM-EVT001** | Inscription validée | Notification à envoyer | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-EVT002** | Absence enregistrée | Notification à envoyer | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-EVT003** | Résultat publié | Notification à envoyer | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-EVT004** | Bulletin disponible | Notification à envoyer | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-EVT005** | Facture émise | Notification à envoyer | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-EVT006** | Paiement confirmé | Notification à envoyer | 📝 PROPOSÉE | Section 5.1 |
| **INT-COM-EVT007** | Annonce publiée | Notification à envoyer | 📝 PROPOSÉE | Section 5.1 |

#### Règles Métier
| ID | Règle | Description | Statut | Source |
|----|-------|-------------|--------|--------|
| **INT-COM-R001** | **Pas de notification non autorisée** | Ne pas notifier un parent qui n'est pas lié à l'élève et autorisé à consulter son dossier | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-R002** | **Respect des préférences** | Respecter les préférences et les canaux activés | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-R003** | **Pas de données sensibles dans les notifications** | Ne pas envoyer un bulletin ou une note dans un email non sécurisé ; préférer un lien authentifié et à durée limitée | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-R004** | **Déduplication** | Dédupliquer les notifications | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-R005** | **Limiter les relances** | Limiter les relances | ✅ **VALIDÉE** | Section 5.1 |

#### États de Notification
| ID | État | Description | Statut | Source |
|----|------|-------------|--------|--------|
| **INT-COM-ST001** | `pending` | En attente | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-ST002** | `sent` | Envoyé | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-ST003** | `delivered` | Livré (si fournisseur le confirme) | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-ST004** | `failed` | Échec | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-ST005** | `retry_scheduled` | Réessai programmé | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-ST006** | `cancelled` | Annulé | ✅ **VALIDÉE** | Section 5.1 |

**Note** : Distinguer « accepté par API » et « livré au destinataire » (INT-COM-R007)

#### Critères d'Acceptation
| ID | Critère | Description | Statut | Source |
|----|---------|-------------|--------|--------|
| **INT-COM-CA001** | **Isolation tenant** | Une notification ne traverse jamais les tenants | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-CA002** | **Idempotence** | Un événement rejoué ne provoque pas plusieurs envois | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-CA003** | **Résilience** | Une panne Brevo/Resend/FCM n'annule pas l'opération métier initiale | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-CA004** | **Visibilité du statut** | L'état de livraison est consultable par un utilisateur autorisé | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-CA005** | **Application des préférences** | Les préférences sont appliquées | ✅ **VALIDÉE** | Section 5.1 |
| **INT-COM-CA006** | **Gestion des erreurs** | Les erreurs sont masquées côté utilisateur et détaillées dans des logs expurgés | ✅ **VALIDÉE** | Section 5.1 |

### 3.2 Push FCM (P1/P2)

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-PUSH-001** | **Inventorier les clients** | Commencer par inventorier les clients réellement disponibles : PWA actuelle, navigateurs ciblés, application Flutter | Integration | ✅ **VALIDÉE** | Section 5.2 |
| **INT-PUSH-002** | **Pas de supposition de compatibilité** | Ne pas supposer que le push web fonctionne sur tous les navigateurs/appareils | Integration | ✅ **VALIDÉE** | Section 5.2 |
| **INT-PUSH-003** | **Token par installation** | Enregistrer un token par installation/appareil, associé au compte et au tenant autorisé | Integration | ✅ **VALIDÉE** | Section 5.2 |
| **INT-PUSH-004** | **Révocation des tokens** | Révoquer les tokens invalides et à la déconnexion selon la politique retenue | Integration | ✅ **VALIDÉE** | Section 5.2 |
| **INT-PUSH-005** | **Token FCM = donnée technique** | Le token FCM n'est pas un secret d'authentification mais reste une donnée technique à protéger | Integration | ✅ **VALIDÉE** | Section 5.2 |
| **INT-PUSH-006** | **Pas de clé privée Firebase dans frontend** | Ne pas embarquer de clé privée Firebase Admin dans le frontend | Integration | ✅ **VALIDÉE** | Section 5.2 |
| **INT-PUSH-007** | **Documentation de configuration** | Documenter la configuration des domaines, service worker, clés web push et environnement | Integration | ✅ **VALIDÉE** | Section 5.2 |
| **INT-PUSH-008** | **Tests complets** | Tester les permissions refusées, tokens expirés, appareils multiples et utilisateurs déconnectés | Integration | ✅ **VALIDÉE** | Section 5.2 |

### 3.3 Calendrier Google (P2)

**Objectif** : Permettre à un établissement ou un utilisateur de synchroniser des événements scolaires vers son calendrier externe.

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-CAL-001** | **EduNova reste maître** | EduNova reste maître des événements scolaires | Academic | ✅ **VALIDÉE** | Section 5.3 |
| **INT-CAL-002** | **Opt-in** | La synchronisation est opt-in, par établissement ou utilisateur | Academic | ✅ **VALIDÉE** | Section 5.3 |
| **INT-CAL-003** | **Synchronisation unidirectionnelle** | Commencer par une synchronisation unidirectionnelle EduNova → Google Calendar | Academic | ✅ **VALIDÉE** | Section 5.3 |
| **INT-CAL-004** | **Pas de modification silencieuse** | Ne pas autoriser la modification d'une date d'examen dans Google à modifier silencieusement le calendrier officiel EduNova | Academic | ✅ **VALIDÉE** | Section 5.3 |
| **INT-CAL-005** | **Identifiant externe et version** | Enregistrer l'identifiant externe et la version/hash synchronisée pour éviter les doublons | Academic | ✅ **VALIDÉE** | Section 5.3 |
| **INT-CAL-006** | **Gestion des erreurs** | Gérer les erreurs OAuth, révocations et quotas par backoff | Academic | ✅ **VALIDÉE** | Section 5.3 |
| **INT-CAL-007** | **Scopes OAuth minimaux** | Utiliser les scopes OAuth les plus étroits possibles | Academic | ✅ **VALIDÉE** | Section 5.3 |
| **INT-CAL-008** | **Tests des cas spéciaux** | Les dates, fuseaux horaires et événements récurrents doivent être testés | Academic | ✅ **VALIDÉE** | Section 5.3 |

**Use Cases** :
- `ConnectGoogleCalendar`
- `DisconnectGoogleCalendar`
- `SyncAcademicEventToCalendar`
- `RemoveSyncedCalendarEvent`
- `GetCalendarSyncStatus`

### 3.4 Google Classroom (P2)

**Objectif** : Connecter les classes et activités Classroom d'un établissement qui utilise déjà Google Workspace for Education.

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-CLS-001** | **Vérification préalable** | Avant de coder : confirmer le type de compte Google et les politiques de l'établissement | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-002** | **Examiner les conditions** | Examiner les conditions d'utilisation et la vérification OAuth applicables | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-003** | **Identifier les rôles autorisés** | Identifier les rôles autorisés à connecter le service | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-004** | **Définir les objets synchronisés** | Définir précisément les objets synchronisés | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-005** | **EduNova = source de vérité** | L'inscription et le roster officiel restent gérés par EduNova | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-006** | **Classroom = système externe** | Classroom est un système externe, pas une base de données de référence EduNova | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-007** | **Synchronisation contrôlée** | Ne synchroniser que les cours, devoirs, matériels ou résultats explicitement retenus | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-008** | **Pas de modification automatique** | Aucune note externe ne doit modifier le dossier académique officiel sans validation et use case métier explicite | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-009** | **Scopes OAuth minimaux** | Ne jamais demander des scopes plus larges que nécessaire | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-010** | **Prototype lecture seule** | Commencer par un prototype en lecture seule et un seul flux métier | Academic | ✅ **VALIDÉE** | Section 5.4 |
| **INT-CLS-011** | **Pas de bidirectionnel initial** | Les écritures bidirectionnelles sont hors périmètre initial | Academic | ✅ **VALIDÉE** | Section 5.4 |

### 3.5 Moodle (P2)

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-MDL-001** | **Connecteur indépendant** | Traiter Moodle comme un connecteur LMS indépendant de Google Classroom | Academic | ✅ **VALIDÉE** | Section 5.5 |
| **INT-MDL-002** | **Web Services Moodle** | Utiliser les Web Services Moodle activés par l'administrateur du site | Academic | ✅ **VALIDÉE** | Section 5.5 |
| **INT-MDL-003** | **Pas de tokens en clair** | Ne pas stocker les tokens Moodle en clair | Academic | ✅ **VALIDÉE** | Section 5.5 |
| **INT-MDL-004** | **Vérification version** | Vérifier la version Moodle, les fonctions web services autorisées et les permissions | Academic | ✅ **VALIDÉE** | Section 5.5 |
| **INT-MDL-005** | **Test de connexion** | Commencer par un test de connexion et une lecture limitée des cours | Academic | ✅ **VALIDÉE** | Section 5.5 |
| **INT-MDL-006** | **Correspondances d'identifiants** | Définir les correspondances d'identifiants entre cours Moodle et structures EduNova | Academic | ✅ **VALIDÉE** | Section 5.5 |
| **INT-MDL-007** | **Éviter la synchronisation bidirectionnelle** | Éviter la synchronisation bidirectionnelle des notes dans la première version | Academic | ✅ **VALIDÉE** | Section 5.5 |
| **INT-MDL-008** | **Choix par établissement** | Un établissement peut utiliser Moodle, Classroom, les deux ou aucun | Academic | ✅ **VALIDÉE** | Section 5.5 |

### 3.6 Classes Virtuelles Jitsi (P2)

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-VM-001** | **Rattachement à une entité** | Une réunion est rattachée à un cours, une classe ou un événement autorisé | Academic | ✅ **VALIDÉE** | Section 5.6 |
| **INT-VM-002** | **Accès contrôlé** | L'accès est accordé uniquement aux participants autorisés | Academic | ✅ **VALIDÉE** | Section 5.6 |
| **INT-VM-003** | **URLs non durables** | Les URLs de réunion ne doivent pas être des secrets durables | Academic | ✅ **VALIDÉE** | Section 5.6 |
| **INT-VM-004** | **Vérification JaaS** | Si JaaS est choisi, vérifier les quotas, coûts, domaines et mécanismes JWT | Academic | ✅ **VALIDÉE** | Section 5.6 |
| **INT-VM-005** | **Documentation auto-hébergé** | Si auto-hébergé, documenter la maintenance, capacité, mises à jour et sécurité | Academic | ✅ **VALIDÉE** | Section 5.6 |
| **INT-VM-006** | **Pas de captation par défaut** | Aucune captation/enregistrement par défaut | Academic | ✅ **VALIDÉE** | Section 5.6 |
| **INT-VM-007** | **Respect des autorisations** | Le lien de réunion ne doit pas contourner les autorisations EduNova | Academic | ✅ **VALIDÉE** | Section 5.6 |
| **INT-VM-008** | **Pas d'auto-hébergé sans étude** | Ne pas intégrer un serveur Jitsi auto-hébergé dans cette phase sans étude d'exploitation | Academic | ✅ **VALIDÉE** | Section 5.6 |

**Use Cases** :
- `ScheduleVirtualClass`
- `CreateVirtualMeeting`
- `GetVirtualMeetingAccess`
- `CancelVirtualMeeting`

### 3.7 Paiements Numériques (P1 architecture, activation conditionnelle)

**Règle Absolue** : **INT-PAY-000** - Le module Finance et son registre de paiements restent la source de vérité. Un PSP ne fait que collecter ou rapporter un paiement.

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-PAY-001** | **Pas de confirmation côté client** | Ne jamais marquer une facture payée sur la seule base du retour navigateur | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-002** | **Validation webhook** | Valider la signature du webhook et, si nécessaire, interroger l'API serveur du PSP | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-003** | **Idempotence PSP** | L'identifiant transaction du PSP est unique dans le contexte fournisseur | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-004** | **Idempotence globale** | Imposer l'idempotence sur l'initiation et la confirmation | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-005** | **Validation complète** | Vérifier tenant, facture, montant, devise et bénéficiaire | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-006** | **Refus des mismatches** | Refuser tout mismatch montant/devise/référence | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-007** | **Preuve technique** | Enregistrer une preuve technique de confirmation et la référence externe | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-008** | **Comptabilisation via Finance** | Comptabiliser le paiement via le use case Finance existant, jamais en écrivant directement dans les tables depuis le contrôleur webhook | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-009** | **Pas de modification directe** | Une transaction initiale ne doit pas être supprimée ou modifiée pour simuler un remboursement ; respecter le mécanisme de correction/contre-écriture existant | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-010** | **Devises distinctes** | USD et CDF restent des devises distinctes ; aucune conversion implicite | Finance | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-011** | **Pas de données de carte** | Ne jamais stocker de PAN/CVV ou données de carte | Finance | ✅ **VALIDÉE** | Section 5.7 |

**Use Cases** :
- `InitiateExternalPayment`
- `ReceivePaymentProviderWebhook`
- `VerifyExternalPayment`
- `ReconcileExternalPayment`
- `HandlePaymentFailure`
- `RequestPaymentRefund` (seulement si le domaine Finance le supporte et si la politique métier est ratifiée)

#### Sélection Fournisseur
| ID | Fournisseur | Statut | Notes | Source |
|----|-------------|--------|-------|--------|
| **INT-PAY-PSP001** | Stripe | Sandbox uniquement pour les tests techniques | ✅ **VALIDÉE** | Section 5.7 |
| **INT-PAY-PSP002** | Flutterwave | Candidat à vérifier - éligibilité RDC non confirmée | ⚠️ À VÉRIFIER | Section 5.7 |
| **INT-PAY-PSP003** | Agrégateur/opérateur local | À rechercher et valider pour la RDC | ⚠️ À VÉRIFIER | Section 5.7 |

**Note** : Aucun fournisseur de paiement de production n'est sélectionné par défaut dans ce document.

**Vérification obligatoire pour la RDC** :
- Pays d'enregistrement de l'établissement et du marchand
- Pays du payeur
- Devise de collecte et de règlement
- Opérateurs réellement supportés (M-Pesa, Airtel Money, Orange Money)
- Frais, délais de règlement, remboursements et litiges
- Exigences KYC/KYB
- Disponibilité du sandbox et des webhooks signés

### 3.8 PostHog Analytics (P3)

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-ANA-001** | **Analytique produit uniquement** | Utiliser PostHog pour mesurer l'adoption et la qualité d'usage du produit, pas pour analyser les performances individuelles des élèves | Analytics | ✅ **VALIDÉE** | Section 5.8 |
| **INT-ANA-002** | **Catalogue minimal** | Commencer par un petit catalogue d'événements produit | Analytics | ✅ **VALIDÉE** | Section 5.8 |
| **INT-ANA-003** | **Éviter les données identifiantes** | Éviter les propriétés contenant des informations directement identifiantes | Analytics | ✅ **VALIDÉE** | Section 5.8 |
| **INT-ANA-004** | **Pas de données scolaires sensibles** | Ne jamais envoyer : noms, emails, numéros, notes, bulletins, absences, soldes, factures, détails de paiement, identifiants scolaires, documents, contenus pédagogiques | Analytics | ✅ **VALIDÉE** | Section 5.8 |
| **INT-ANA-005** | **Événements agrégés** | Utiliser des événements agrégés ou pseudonymisés : `dashboard_viewed`, `notification_preferences_updated`, `integration_connected`, `report_exported` | Analytics | ✅ **VALIDÉE** | Section 5.8 |
| **INT-ANA-006** | **Désactivation possible** | Prévoir désactivation par environnement et, si nécessaire, par tenant | Analytics | ✅ **VALIDÉE** | Section 5.8 |
| **INT-ANA-007** | **Respect du consentement** | Respecter le consentement, les politiques de confidentialité et la durée de conservation | Analytics | ✅ **VALIDÉE** | Section 5.8 |
| **INT-ANA-008** | **Clé publique frontend** | Le SDK frontend ne reçoit qu'une clé publique de projet conçue pour le navigateur ; aucune clé personnelle/admin | Analytics | ✅ **VALIDÉE** | Section 5.8 |
| **INT-ANA-009** | **Pas de dépendance critique** | Les événements critiques ou administratifs ne doivent pas dépendre de PostHog pour leur persistance ou leur audit | Analytics | ✅ **VALIDÉE** | Section 5.8 |

---

## 4. Décisions de Sécurité et Conformité

### 4.1 Isolation Tenant

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-SEC-001** | **Rattachement tenant obligatoire** | Chaque configuration, événement, abonnement, webhook, identifiant externe, tâche et résultat doit être rattaché au tenant concerné | Security | ✅ **VALIDÉE** | Section 4.1 |
| **INT-SEC-002** | **Tenant dérivé du contexte** | Le tenant est dérivé du contexte authentifié côté serveur | Security | ✅ **VALIDÉE** | Section 4.1 |
| **INT-SEC-003** | **Pas de choix arbitraire** | Le client ne peut pas choisir arbitrairement un tenant | Security | ✅ **VALIDÉE** | Section 4.1 |
| **INT-SEC-004** | **Scope tenant sur toutes les opérations** | Toutes les lectures/écritures appliquent le scope tenant | Security | ✅ **VALIDÉE** | Section 4.1 |
| **INT-SEC-005** | **Identifiants externes ≠ preuve d'autorisation** | Les identifiants externes ne sont jamais considérés comme des preuves d'autorisation | Security | ✅ **VALIDÉE** | Section 4.1 |
| **INT-SEC-006** | **Tests négatifs obligatoires** | Tests négatifs entre deux tenants pour chaque nouveau use case | Security | ✅ **VALIDÉE** | Section 4.1 |

### 4.2 Secrets et OAuth

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-SEC-007** | **Pas de secrets dans VITE_*** | Aucun secret dans `VITE_*`, code JavaScript, localStorage ou bundle frontend | Security | ✅ **VALIDÉE** | Section 4.2 |
| **INT-SEC-008** | **Clés globales sécurisées** | Les clés globales de fournisseur sont fournies par configuration sécurisée d'environnement ou gestionnaire de secrets | Security | ✅ **VALIDÉE** | Section 4.2 |
| **INT-SEC-009** | **Tokens OAuth chiffrés** | Les tokens OAuth propres à un tenant/utilisateur doivent être chiffrés au repos si leur persistance est nécessaire | Security | ✅ **VALIDÉE** | Section 4.2 |
| **INT-SEC-010** | **Scopes minimaux** | Stocker uniquement les scopes nécessaires ; demander le consentement explicite | Security | ✅ **VALIDÉE** | Section 4.2 |
| **INT-SEC-011** | **Prévoir révocation** | Prévoir révocation, déconnexion et rotation | Security | ✅ **VALIDÉE** | Section 4.2 |
| **INT-SEC-012** | **Pas de tokens dans les logs** | Ne jamais écrire les tokens, codes OAuth ou headers d'autorisation dans les logs | Security | ✅ **VALIDÉE** | Section 4.2 |
| **INT-SEC-013** | **Scopes Google minimaux** | Ne jamais demander des scopes Google globaux si un scope en lecture seule suffit | Security | ✅ **VALIDÉE** | Section 4.2 |

### 4.3 Webhooks

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-SEC-014** | **Vérification signature** | Pour tout webhook entrant : vérifier la signature selon la documentation officielle du fournisseur | Security | ✅ **VALIDÉE** | Section 4.3 |
| **INT-SEC-015** | **Vérification horodatage** | Vérifier l'horodatage et prévenir le rejeu si le fournisseur le permet | Security | ✅ **VALIDÉE** | Section 4.3 |
| **INT-SEC-016** | **Identifiant événement unique** | Enregistrer un identifiant d'événement unique | Security | ✅ **VALIDÉE** | Section 4.3 |
| **INT-SEC-017** | **Traitement idempotent** | Traiter de manière idempotente | Security | ✅ **VALIDÉE** | Section 4.3 |
| **INT-SEC-018** | **Rejet payloads invalides** | Rejeter les payloads invalides | Security | ✅ **VALIDÉE** | Section 4.3 |
| **INT-SEC-019** | **Ne pas faire confiance au statut navigateur** | Ne jamais faire confiance au seul statut renvoyé par le navigateur | Security | ✅ **VALIDÉE** | Section 4.3 |
| **INT-SEC-020** | **Vérification statut côté serveur** | Vérifier le statut côté serveur auprès du fournisseur si le protocole l'exige | Security | ✅ **VALIDÉE** | Section 4.3 |
| **INT-SEC-021** | **Protection contre les abus** | Protéger les endpoints contre les abus et limiter leur débit | Security | ✅ **VALIDÉE** | Section 4.3 |
| **INT-SEC-022** | **Traçabilité webhook** | Conserver une trace d'audit sans stocker inutilement le payload personnel complet | Security | ✅ **VALIDÉE** | Section 4.3 |

### 4.4 Données Scolaires et Analytics

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-SEC-023** | **Interdiction données élèves** | Ne pas transmettre à PostHog, Courier ou un autre outil d'analytics : noms d'élèves ou de parents | Security | ✅ **VALIDÉE** | Section 4.4 |
| **INT-SEC-024** | **Interdiction contacts** | Ne pas transmettre : emails ou numéros de téléphone | Security | ✅ **VALIDÉE** | Section 4.4 |
| **INT-SEC-025** | **Interdiction données académiques** | Ne pas transmettre : notes, bulletins, absences nominatives | Security | ✅ **VALIDÉE** | Section 4.4 |
| **INT-SEC-026** | **Interdiction données financières** | Ne pas transmettre : soldes, factures ou détails de paiement | Security | ✅ **VALIDÉE** | Section 4.4 |
| **INT-SEC-027** | **Interdiction identifiants directs** | Ne pas transmettre : identifiants scolaires directement ré-identifiants | Security | ✅ **VALIDÉE** | Section 4.4 |
| **INT-SEC-028** | **Interdiction documents** | Ne pas transmettre : documents ou contenus pédagogiques privés | Security | ✅ **VALIDÉE** | Section 4.4 |
| **INT-SEC-029** | **Événements autorisés** | Utiliser uniquement : `dashboard_viewed`, `notification_preferences_updated`, `integration_connected`, `report_exported` | Security | ✅ **VALIDÉE** | Section 4.4 |
| **INT-SEC-030** | **Tenant pseudonymisé** | Tenant pseudonymisé si nécessaire et sans identifiant personnel direct | Security | ✅ **VALIDÉE** | Section 4.4 |
| **INT-SEC-031** | **Documentation analytique** | Documenter la finalité, la rétention et le consentement applicable | Security | ✅ **VALIDÉE** | Section 4.4 |

---

## 5. Décisions Techniques et d'Implémentation

### 5.1 Configuration

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-TECH-001** | **Configuration validée** | Prévoir une configuration validée et documentée, sans secret commité | Integration | ✅ **VALIDÉE** | Section 7 |
| **INT-TECH-002** | **Adaptation aux conventions** | Les noms de configuration doivent être adaptés aux conventions existantes | Integration | ✅ **VALIDÉE** | Section 7 |
| **INT-TECH-003** | **Pas de variables inutilisées** | Ne pas ajouter de variables inutilisées | Integration | ✅ **VALIDÉE** | Section 7 |

**Exemples de noms (non imposés)** :
- `EDUNOVA_EMAIL_PROVIDER`
- `BREVO_API_KEY`
- `RESEND_API_KEY`
- `FCM_PROJECT_ID`
- `FCM_SERVICE_ACCOUNT`
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `JITSI_BASE_URL`
- `JITSI_APP_ID`
- `JITSI_APP_SECRET`
- `POSTHOG_PROJECT_KEY`
- `POSTHOG_HOST`

### 5.2 Contrôle des Coûts

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-TECH-004** | **Suivi des appels** | Pour chaque fournisseur, suivre si possible : appels envoyés, succès/échecs | Integration | ✅ **VALIDÉE** | Section 7.2 |
| **INT-TECH-005** | **Suivi consommation** | Suivre la consommation de quota | Integration | ✅ **VALIDÉE** | Section 7.2 |
| **INT-TECH-006** | **Suivi par tenant** | Suivre la consommation par tenant | Integration | ✅ **VALIDÉE** | Section 7.2 |
| **INT-TECH-007** | **Estimation de coût** | Suivre l'estimation de coût lorsque le tarif est connu | Integration | ✅ **VALIDÉE** | Section 7.2 |
| **INT-TECH-008** | **Seuils d'alerte** | Prévoir des seuils d'alerte | Integration | ✅ **VALIDÉE** | Section 7.2 |
| **INT-TECH-009** | **État du circuit** | Prévoir l'état du circuit en cas d'indisponibilité | Integration | ✅ **VALIDÉE** | Section 7.2 |
| **INT-TECH-010** | **Quotas partagés** | Afficher clairement que les quotas fournisseurs peuvent être partagés au niveau du projet | Integration | ✅ **VALIDÉE** | Section 7.2 |

---

## 6. Décisions de Tests et Qualité

### 6.1 Types de Tests

| ID | Type | Description | Domaine | Statut | Source |
|----|------|-------------|---------|--------|--------|
| **INT-TEST-001** | **Tests unitaires** | Sélection du fournisseur, validation des préférences, règles d'idempotence, mapping des payloads, politique de retry, validation montant/devise, contrôle des transitions d'état | Integration | ✅ **VALIDÉE** | Section 9.1 |
| **INT-TEST-002** | **Tests d'intégration** | Repository et migrations sur DB temporaire, container et injection des ports, outbox/dispatcher, signature et déduplication des webhooks, chiffrement/déchiffrement des credentials, simulation d'indisponibilité fournisseur | Integration | ✅ **VALIDÉE** | Section 9.2 |
| **INT-TEST-003** | **Tests de sécurité** | Accès inter-tenant refusé, rôles insuffisants refusés, token OAuth expiré/révoqué, signature webhook invalide, rejeu de webhook, payload trop volumineux/invalide, absence de secret dans logs et réponses, SSRF | Integration | ✅ **VALIDÉE** | Section 9.3 |
| **INT-TEST-004** | **Tests end-to-end** | Administrateur connecte/déconnecte un service, notification créée et visible, notification délivrée ou échec expliqué, calendrier synchronisé, paiement confirmé par webhook et visible dans Finance, un autre tenant ne peut voir ni manipuler l'intégration | Integration | ✅ **VALIDÉE** | Section 9.4 |

### 6.2 Règles de Tests

| ID | Règle | Description | Domaine | Statut | Source |
|----|-------|-------------|---------|--------|--------|
| **INT-TEST-005** | **Mocks contractuels** | Les tests fournisseurs utilisent des mocks contractuels ou des sandboxes officielles | Integration | ✅ **VALIDÉE** | Section 9 |
| **INT-TEST-006** | **Pas de dépendance réseau** | Ne pas faire dépendre la suite unitaire de l'accès réseau | Integration | ✅ **VALIDÉE** | Section 9 |

---

## 7. Décisions en Attente de Validation

### 7.1 Sélection Fournisseur Paiement pour RDC

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-AWAIT-001** | **Flutterwave éligibilité RDC** | Vérifier si Flutterwave supporte la RDC, le CDF et les opérateurs locaux (M-Pesa, Airtel Money, Orange Money) | Finance | ⏳ EN ATTENTE | Section 5.7 |
| **INT-AWAIT-002** | **Agrégateur local RDC** | Rechercher et valider un fournisseur réellement contractable en RDC et prenant en charge les moyens demandés | Finance | ⏳ EN ATTENTE | Section 5.7 |

**Analyse** : Ces décisions sont **critiques** pour l'activation des paiements en RDC. Sans validation, impossible d'activer un PSP de production.

**Recommandation** : 🔴 **ARBITRAGE URGENT**
- Contacter Flutterwave pour confirmer l'éligibilité RDC
- Rechercher des agrégateurs locaux en RDC
- Valider les opérateurs Mobile Money supportés

### 7.2 Compatibilité PWA/FCM

| ID | Décision | Description | Domaine | Statut | Source |
|----|----------|-------------|---------|--------|--------|
| **INT-AWAIT-003** | **Vérification compatibilité PWA** | Vérifier la compatibilité de la PWA actuelle avec FCM | Integration | ⏳ EN ATTENTE | Section 5.2 |
| **INT-AWAIT-004** | **Vérification compatibilité navigateurs** | Vérifier la compatibilité des navigateurs ciblés avec FCM | Integration | ⏳ EN ATTENTE | Section 5.2 |

**Analyse** : Ces vérifications sont nécessaires avant d'implémenter FCM.

**Recommandation** : ⚠️ **À VÉRIFIER** avant la Phase 3.

---

## 8. Références et Priorités

### 8.1 Tableau de Priorité des Modules

| Module | Priorité | Phase | Statut |
|--------|----------|-------|--------|
| **Audit et Conception** | P0 | Phase 0 | ✅ **VALIDÉE** |
| **Noyau Integration** | P1 | Phase 1 | ✅ **VALIDÉE** |
| **Notifications Email** | P1 | Phase 2 | ✅ **VALIDÉE** |
| **Push FCM** | P1/P2 | Phase 3 | ✅ **VALIDÉE** |
| **Paiements Numériques** | P1 (architecture) | Phase 4 | ⚠️ **EN ATTENTE FOURNISSEUR** |
| **Google Calendar** | P2 | Phase 5 | ✅ **VALIDÉE** |
| **Google Classroom** | P2 | Phase 6 | ✅ **VALIDÉE** |
| **Moodle** | P2 | Phase 6 | ✅ **VALIDÉE** |
| **Classes Virtuelles** | P2 | Phase 7 | ✅ **VALIDÉE** |
| **PostHog Analytics** | P3 | Phase 8 | ✅ **VALIDÉE** |

### 8.2 Sélection Fournisseur par Besoin

| Besoin | Fournisseur Principal | Fournisseur Alternatif | Statut |
|--------|----------------------|------------------------|--------|
| Email transactionnel | Brevo | Resend | ✅ **VALIDÉE** |
| Orchestration multi-canal | - | Courier | P3 |
| Push mobile/web | FCM | - | ✅ **VALIDÉE** |
| Travail pédagogique | Google Classroom API | - | ✅ **VALIDÉE** |
| Calendrier | Google Calendar API | - | ✅ **VALIDÉE** |
| Classe virtuelle | Jitsi Meet / JaaS | - | ✅ **VALIDÉE** |
| LMS | Moodle Web Services | - | ✅ **VALIDÉE** |
| Paiement | - | Stripe (sandbox), Flutterwave (à vérifier) | ⚠️ **EN ATTENTE** |
| Analytique produit | PostHog | - | ✅ **VALIDÉE** |

**Règles de sélection** :
- Brevo et Resend sont deux implémentations possibles d'un port `EmailProvider`. Ne pas créer deux systèmes de notification parallèles.
- Courier est une couche d'orchestration facultative. Ne pas ajouter Courier si le besoin est satisfait proprement par un dispatcher interne et un fournisseur.
- FCM concerne le push ; il ne remplace ni l'email ni le centre de notifications interne.
- Google Classroom et Moodle sont deux connecteurs pédagogiques différents. Un établissement choisit zéro, un ou plusieurs connecteurs selon son organisation.
- Jitsi doit être derrière un port `VideoMeetingProvider`; le choix JaaS / auto-hébergement dépendra du coût, de la capacité opérationnelle et des exigences de confidentialité.
- Stripe est utile pour des tests de flux de paiement et des marchés supportés, mais ne doit pas être présenté comme solution de production RDC.

### 8.3 Vérification Pays/Devise Obligatoire

**Ne pas déduire qu'un moyen de paiement est disponible en RDC parce qu'il est disponible en Afrique centrale ou dans un pays voisin.**

Avant de choisir un PSP de production, établir une matrice vérifiée :
- Pays d'enregistrement de l'établissement et du marchand
- Pays du payeur
- Devise de collecte et de règlement
- Opérateurs réellement supportés (par exemple M-Pesa, Airtel Money, Orange Money)
- Frais, délais de règlement, remboursements et litiges
- Exigences KYC/KYB
- Disponibilité du sandbox et des webhooks signés

---

## 📊 Résumé des Décisions

### Décisions Validées

| Type | Total | Détails |
|------|-------|----------|
| **Principes non négociables** | 10 | INT-001 à INT-010 |
| **Décisions architecturales** | 3 | INT-ARC-001 à INT-ARC-002, INT-EXEC-001 à INT-EXEC-003 |
| **Ports/Contrats** | 8 | INT-PORT-001 à INT-PORT-008 |
| **Communication & Notifications** | 28 | INT-COM-* (use cases, événements, règles, états, critères) |
| **Push FCM** | 8 | INT-PUSH-001 à INT-PUSH-008 |
| **Calendrier Google** | 8 | INT-CAL-001 à INT-CAL-008 |
| **Google Classroom** | 11 | INT-CLS-001 à INT-CLS-011 |
| **Moodle** | 8 | INT-MDL-001 à INT-MDL-008 |
| **Classes Virtuelles** | 8 | INT-VM-001 à INT-VM-008 |
| **Paiements** | 12 | INT-PAY-000 à INT-PAY-011 + PSP |
| **PostHog** | 9 | INT-ANA-001 à INT-ANA-009 |
| **Sécurité** | 31 | INT-SEC-001 à INT-SEC-031 |
| **Tests** | 6 | INT-TEST-001 à INT-TEST-006 |
| **Technique/Configuration** | 10 | INT-TECH-001 à INT-TECH-010 |
| **Total Validées** | **160+** | | |

### Décisions en Attente

| Type | Total | Détails |
|------|-------|----------|
| **Paiement RDC** | 2 | INT-AWAIT-001, INT-AWAIT-002 |
| **Compatibilité FCM** | 2 | INT-AWAIT-003, INT-AWAIT-004 |
| **Total En Attente** | **4** | | |

### Propositions (à valider)

| Type | Total | Détails |
|------|-------|----------|
| **Use Cases Communication** | 7 | INT-COM-UC001 à INT-COM-UC007 |
| **Événements Métier** | 7 | INT-COM-EVT001 à INT-COM-EVT007 |
| **Use Cases Paiement** | 6 | INT-PAY-UC* |
| **Total Propositions** | **20+** | | |

---

## 🎯 Prochaines Étapes

1. **Intégrer ces décisions** dans `EDUNOVA_FUNCTIONAL_DDD_SPECIFICATION.md`
   - Ajouter le Bounded Context **Integration**
   - Ajouter les ports et contrats
   - Ajouter les règles de sécurité
   - Ajouter les use cases par module

2. **Mettre à jour** `EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md`
   - Ajouter les décisions en attente (INT-AWAIT-*)
   - Vérifier les contradictions potentielles avec les décisions existantes

3. **Vérifier la cohérence** avec les autres documents
   - Vérifier que ces décisions ne contredisent pas D1-D44
   - Vérifier la cohérence avec les principes DDD

4. **Créer le glossaire** `EDUNOVA_DOMAIN_GLOSSARY.md`
   - Extraire les termes métier de ce document

5. **Continuer l'analyse** des 75+ documents restants

---

**Document extrait le** : 2025-XX-XX  
**Statut** : EN COURS  
**État** : 100% du document analysé, extraction complète des décisions
