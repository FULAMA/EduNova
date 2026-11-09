# EduNova — Plan directeur d'intégration des services externes

> **Statut :** spécification d'implémentation à exécuter par étapes  
> **Type :** plan technique + backlog agent  
> **Dépôt :** `FULAMA/EduNova`  
> **Branche documentaire :** `docs/education-integrations-implementation-plan`  
> **Périmètre :** backend FastAPI, frontend React/TypeScript, persistance SQLite actuelle  
> **Principe :** EduNova reste le système métier maître ; les fournisseurs externes sont des adaptateurs remplaçables.

---

## 0. Instruction impérative à l'agent

Ce document décrit une cible et un ordre de travail. **Il n'autorise pas une implémentation massive ou une réécriture de l'existant.**

Avant toute modification :

1. Lire ce document intégralement.
2. Examiner le dépôt et la branche réellement active ; ne jamais supposer que les chemins décrits ici existent.
3. Lire le masterplan, les ADR, les décisions métier et les modules Identity, Tenancy, Finance, Academic et Communication déjà présents.
4. Cartographier les capacités existantes, les contrats, les migrations, le container, les tests et les mécanismes de tâches de fond.
5. Identifier les intégrations déjà implémentées, même partiellement, afin de ne pas les dupliquer.
6. Présenter un rapport d'écart et un plan de fichiers avant de coder.
7. Implémenter une phase à la fois, avec tests et rapport de clôture.

### Garde-fous Git et données

- Ne jamais modifier directement `main`.
- Travailler sur une branche dédiée créée depuis la branche de travail autorisée et confirmée.
- Ne pas changer de branche si le répertoire contient des modifications locales non sauvegardées.
- Ne jamais exécuter `git reset --hard`, `git clean`, `git restore`, ni une opération destructive équivalente.
- Aucun commit, push, merge ou PR sans autorisation explicite.
- Ne jamais supprimer, réinitialiser ou migrer les bases persistantes `edunova.db` et `edunova_dev.db`.
- Les tests d'intégration et de migration utilisent exclusivement une base temporaire dédiée.
- Ne jamais afficher de secrets, tokens OAuth, clés API, mots de passe ou données personnelles dans les logs et rapports.

**Premier livrable obligatoire :** `docs/integrations/INTEGRATIONS_GAP_ANALYSIS.md`. Ne commencer aucune intégration fournisseur avant validation de ce rapport.

---

## 1. Objectif produit

Faire d'EduNova un ERP scolaire SaaS capable de fournir, de façon fiable et contrôlée :

1. des notifications transactionnelles aux utilisateurs ;
2. des notifications push sur les appareils compatibles ;
3. la synchronisation facultative des événements scolaires avec des calendriers externes ;
4. des connexions pédagogiques facultatives avec Google Classroom ou Moodle ;
5. des salles de classe virtuelles ;
6. des paiements numériques lorsque le fournisseur est effectivement disponible dans le pays et la devise concernés ;
7. des indicateurs d'usage du produit pour améliorer EduNova sans exposer les données scolaires sensibles.

Ces capacités doivent être utiles aux établissements de la RDC et rester compatibles avec une extension panafricaine.

### Principes non négociables

- **EduNova est le système de référence** pour les élèves, inscriptions, classes, frais, factures, paiements comptabilisés, notes et décisions scolaires.
- Un fournisseur externe ne devient jamais le propriétaire implicite des données métier EduNova.
- Toutes les opérations liées à un établissement sont strictement limitées à son `tenant_id`.
- Les appels externes sont exécutés côté serveur, sauf SDK explicitement conçu pour un usage client et sans secret.
- Les secrets ne sont jamais placés dans le frontend, dans le dépôt ou dans une réponse API.
- Les opérations asynchrones sont traçables, idempotentes, réessayables et observables.
- Une panne externe ne doit pas empêcher l'inscription, la consultation des dossiers ou les autres fonctions essentielles d'EduNova.
- Les intégrations sont optionnelles et désactivables par établissement.
- Pas de microservices, Redis ou nouvelle infrastructure distribuée sans justification mesurée. Réutiliser d'abord les mécanismes déjà présents.
- Les quotas gratuits sont des limites de démarrage, pas une garantie de coût nul à l'échelle SaaS.

---

## 2. Inventaire des dix services et stratégie de sélection

Les services ci-dessous ne sont pas dix dépendances obligatoires. Plusieurs sont des alternatives qui répondent au même besoin.

| Besoin | Service | Décision cible | Priorité |
|---|---|---|---|
| Email transactionnel | Brevo | Premier adaptateur email à évaluer | P1 |
| Email transactionnel | Resend | Adaptateur alternatif ou secours, pas une dépendance simultanée obligatoire | P2 |
| Orchestration multi-canal | Courier | Option ultérieure si le routage multi-fournisseur devient réellement nécessaire | P3 |
| Push mobile/web | Firebase Cloud Messaging (FCM) | Adaptateur push indépendant du fournisseur email | P1/P2 |
| Travail pédagogique | Google Classroom API | Connecteur optionnel avec consentement OAuth | P2 |
| Calendrier | Google Calendar API | Connecteur optionnel, synchronisation explicite | P2 |
| Classe virtuelle | Jitsi Meet / JaaS | Commencer par une abstraction de fournisseur ; choisir hébergé ou auto-hébergé après étude | P2 |
| LMS | Moodle Web Services | Connecteur optionnel, distinct de Google Classroom | P2 |
| Paiement | Stripe | Mode test seulement pour les tests techniques ; ne pas en faire le fournisseur RDC par défaut | P3 |
| Analytique produit | PostHog | Instrumentation minimale, respectueuse de la vie privée | P3 |

### Règles de sélection

- Brevo et Resend sont deux implémentations possibles d'un port `EmailProvider`. Ne pas créer deux systèmes de notification parallèles.
- Courier est une couche d'orchestration facultative. Ne pas ajouter Courier si le besoin est satisfait proprement par un dispatcher interne et un fournisseur.
- FCM concerne le push ; il ne remplace ni l'email ni le centre de notifications interne.
- Google Classroom et Moodle sont deux connecteurs pédagogiques différents. Un établissement choisit zéro, un ou plusieurs connecteurs selon son organisation.
- Jitsi doit être derrière un port `VideoMeetingProvider`; le choix JaaS / auto-hébergement dépendra du coût, de la capacité opérationnelle et des exigences de confidentialité.
- Stripe est utile pour des tests de flux de paiement et des marchés supportés, mais ne doit pas être présenté comme solution de production RDC.
- PostHog sert à l'analytique produit, pas au suivi des notes, paiements, dossiers médicaux ou autres données personnelles sensibles des élèves.

### Vérification pays/devise obligatoire pour les paiements

Ne pas déduire qu'un moyen de paiement est disponible en RDC parce qu'il est disponible en Afrique centrale ou dans un pays voisin. La documentation Flutterwave présente notamment des options de Mobile Money par région et pays, mais la prise en charge de la RDC, des opérateurs locaux et du CDF doit être confirmée contractuellement et techniquement avant toute activation.

Avant de choisir un PSP de production, établir une matrice vérifiée :
- pays d'enregistrement de l'établissement et du marchand ;
- pays du payeur ;
- devise de collecte et de règlement ;
- opérateurs réellement supportés (par exemple M-Pesa, Airtel Money, Orange Money, selon disponibilité contractuelle) ;
- frais, délais de règlement, remboursements et litiges ;
- exigences KYC/KYB ;
- disponibilité du sandbox et des webhooks signés.

Si aucun fournisseur vérifié ne supporte le scénario RDC, garder l'intégration désactivée et prévoir un adaptateur futur. Ne jamais simuler une confirmation de paiement en production.

---

## 3. Architecture cible — monolithe modulaire

Conserver le style architectural réel du dépôt. La structure ci-dessous est une cible conceptuelle, pas une instruction de déplacer massivement les packages existants.

### Bounded Context cible : Integration

Responsabilités :
- configuration et activation des connecteurs ;
- cycle de vie des autorisations externes ;
- routage vers les adaptateurs ;
- gestion des webhooks entrants ;
- suivi des synchronisations ;
- quotas et états de santé ;
- journalisation technique et audit des actions administratives.

Les domaines métier publient des intentions ou événements métier. Le contexte Integration orchestre les effets externes.

### Ports / contrats conceptuels

Définir uniquement les ports réellement nécessaires après audit :

- `EmailProvider`
  - `send_transactional(message)`
- `PushProvider`
  - `send_to_device(notification)`
- `CalendarProvider`
  - `create_or_update_event(event)`
  - `delete_event(external_id)`
- `ClassroomProvider`
  - opérations explicitement supportées par le cas d'usage retenu
- `LmsProvider`
  - opérations Moodle autorisées
- `VideoMeetingProvider`
  - `create_meeting(request)`
  - `revoke_meeting(external_id)`
- `PaymentProvider`
  - `create_payment_intent(request)`
  - `verify_webhook(headers, raw_body)`
  - `fetch_payment_status(external_reference)`
- `ProductAnalyticsProvider`
  - `capture(event)`

Ne pas construire un méga-port générique qui impose à tous les fournisseurs des méthodes inutiles.

### Modèle d'exécution recommandé

1. Un use case métier valide les règles et enregistre la transaction métier.
2. Si un effet externe est requis, il enregistre une tâche/événement dans une outbox persistée dans la même transaction lorsque l'infrastructure actuelle le permet.
3. Un dispatcher existant ou un worker contrôlé prend la tâche.
4. Il résout le fournisseur activé pour le tenant et le canal.
5. Il envoie la requête avec une clé d'idempotence.
6. Il enregistre le résultat sans exposer les données sensibles.
7. En cas d'échec temporaire, il applique un retry borné avec backoff ; après épuisement, il place la tâche en état d'échec terminal et la rend visible pour diagnostic.

Ne pas introduire une dépendance à Redis ou un broker externe uniquement pour cette fonctionnalité. Si aucune infrastructure de tâches de fond durable n'existe, proposer d'abord une solution compatible avec SQLite et le déploiement actuel, puis documenter ses limites multi-processus.

---

## 4. Sécurité, multi-tenant et confidentialité

### Isolation tenant

Chaque configuration, événement, abonnement, webhook, identifiant externe, tâche et résultat doit être rattaché au tenant concerné lorsque la ressource est tenant-scoped.

Contrôles requis :
- le tenant est dérivé du contexte authentifié côté serveur ;
- le client ne peut pas choisir arbitrairement un tenant ;
- toutes les lectures/écritures appliquent le scope tenant ;
- les identifiants externes ne sont jamais considérés comme des preuves d'autorisation ;
- tests négatifs entre deux tenants pour chaque nouveau use case.

### Secrets et OAuth

- Aucun secret dans `VITE_*`, code JavaScript, localStorage ou bundle frontend.
- Les clés globales de fournisseur sont fournies par configuration sécurisée d'environnement ou gestionnaire de secrets adapté au déploiement.
- Les tokens OAuth propres à un tenant/utilisateur doivent être chiffrés au repos si leur persistance est nécessaire.
- Stocker uniquement les scopes nécessaires ; demander le consentement explicite.
- Prévoir révocation, déconnexion et rotation.
- Ne jamais écrire les tokens, codes OAuth ou headers d'autorisation dans les logs.
- Ne jamais demander des scopes Google globaux si un scope en lecture seule suffit.

### Webhooks

Pour tout webhook entrant :
- vérifier la signature selon la documentation officielle du fournisseur ;
- vérifier l'horodatage et prévenir le rejeu si le fournisseur le permet ;
- enregistrer un identifiant d'événement unique ;
- traiter de manière idempotente ;
- rejeter les payloads invalides ;
- ne jamais faire confiance au seul statut renvoyé par le navigateur ;
- vérifier le statut côté serveur auprès du fournisseur si le protocole l'exige ;
- protéger les endpoints contre les abus et limiter leur débit ;
- conserver une trace d'audit sans stocker inutilement le payload personnel complet.

### Données scolaires et analytics

Ne pas transmettre à PostHog, Courier ou un autre outil d'analytics :
- noms d'élèves ou de parents ;
- emails ou numéros de téléphone ;
- notes, bulletins, absences nominatives ;
- soldes, factures ou détails de paiement ;
- identifiants scolaires directement ré-identifiants ;
- documents ou contenus pédagogiques privés.

Utiliser des événements agrégés ou pseudonymisés : `dashboard_viewed`, `notification_preferences_updated`, `integration_connected`, `report_exported`, avec tenant pseudonymisé si nécessaire et sans identifiant personnel direct. Documenter la finalité, la rétention et le consentement applicable.

---

## 5. Modules fonctionnels et use cases attendus

Les noms ci-dessous sont des propositions. L'agent doit vérifier les conventions existantes et les use cases déjà présents avant d'en créer.

### 5.1 Communication & Notifications — P1

**Valeur utilisateur :** informer les parents, élèves, enseignants et responsables au bon moment, sans spam ni perte de message.

Canaux :
- centre de notifications interne (source de vérité) ;
- email transactionnel (Brevo initialement, Resend comme alternative) ;
- push (FCM, lorsque les clients compatibles existent).

Use cases candidats :
- `CreateNotification`
- `DispatchNotification`
- `ManageNotificationPreferences`
- `RegisterDeviceToken`
- `RevokeDeviceToken`
- `RetryFailedNotification`
- `GetNotificationDeliveryStatus`

Événements métier candidats, à confirmer avec les règles métier existantes :
- inscription validée ;
- absence enregistrée ;
- résultat publié ;
- bulletin disponible ;
- facture émise ;
- paiement confirmé ;
- annonce publiée.

Règles :
- ne pas notifier un parent qui n'est pas lié à l'élève et autorisé à consulter son dossier ;
- respecter les préférences et les canaux activés ;
- ne pas envoyer un bulletin ou une note dans un email non sécurisé ; préférer un lien authentifié et à durée limitée ;
- dédupliquer les notifications ;
- limiter les relances ;
- tracer les états `pending`, `sent`, `delivered` si le fournisseur le confirme, `failed`, `retry_scheduled`, `cancelled` ;
- distinguer « accepté par API » et « livré au destinataire ».

Critères d'acceptation :
- une notification ne traverse jamais les tenants ;
- un événement rejoué ne provoque pas plusieurs envois ;
- une panne Brevo/Resend/FCM n'annule pas l'opération métier initiale ;
- l'état de livraison est consultable par un utilisateur autorisé ;
- les préférences sont appliquées ;
- les erreurs sont masquées côté utilisateur et détaillées dans des logs expurgés.

### 5.2 Push FCM — P1/P2

- Commencer par inventorier les clients réellement disponibles : PWA actuelle, navigateurs ciblés, application Flutter éventuelle plus tard.
- Ne pas supposer que le push web fonctionne sur tous les navigateurs/appareils.
- Enregistrer un token par installation/appareil, associé au compte et au tenant autorisé.
- Révoquer les tokens invalides et à la déconnexion selon la politique retenue.
- Le token FCM n'est pas un secret d'authentification mais reste une donnée technique à protéger.
- Ne pas embarquer de clé privée Firebase Admin dans le frontend.
- Documenter la configuration des domaines, service worker, clés web push et environnement de déploiement.
- Tester les permissions refusées, tokens expirés, appareils multiples et utilisateurs déconnectés.

### 5.3 Calendrier Google — P2

**Valeur :** permettre à un établissement ou un utilisateur de synchroniser des événements scolaires vers son calendrier externe.

Use cases candidats :
- `ConnectGoogleCalendar`
- `DisconnectGoogleCalendar`
- `SyncAcademicEventToCalendar`
- `RemoveSyncedCalendarEvent`
- `GetCalendarSyncStatus`

Règles :
- EduNova reste maître des événements scolaires.
- La synchronisation est opt-in, par établissement ou utilisateur selon le besoin.
- Commencer par une synchronisation unidirectionnelle EduNova → Google Calendar.
- Ne pas autoriser la modification d'une date d'examen dans Google à modifier silencieusement le calendrier officiel EduNova.
- Enregistrer l'identifiant externe et la version/hash synchronisée pour éviter les doublons.
- Gérer les erreurs OAuth, révocations et quotas par backoff.
- Utiliser les scopes OAuth les plus étroits possibles.
- Les dates, fuseaux horaires et événements récurrents doivent être testés.

### 5.4 Google Classroom — P2

**Valeur :** connecter les classes et activités Classroom d'un établissement qui utilise déjà Google Workspace for Education.

Avant de coder :
- confirmer le type de compte Google et les politiques de l'établissement ;
- examiner les conditions d'utilisation et la vérification OAuth applicables ;
- identifier les rôles autorisés à connecter le service ;
- définir précisément les objets synchronisés.

Règles de frontière :
- l'inscription et le roster officiel restent gérés par EduNova ;
- Classroom est un système externe, pas une base de données de référence EduNova ;
- ne synchroniser que les cours, devoirs, matériels ou résultats explicitement retenus ;
- aucune note externe ne doit modifier le dossier académique officiel sans validation et use case métier explicite ;
- ne jamais demander des scopes plus larges que nécessaire.

Commencer par un prototype en lecture seule et un seul flux métier. Les écritures bidirectionnelles sont hors périmètre initial.

### 5.5 Moodle — P2

- Traiter Moodle comme un connecteur LMS indépendant de Google Classroom.
- Utiliser les Web Services Moodle activés par l'administrateur du site.
- Ne pas stocker les tokens Moodle en clair.
- Vérifier la version Moodle, les fonctions web services autorisées et les permissions.
- Commencer par un test de connexion et une lecture limitée des cours.
- Définir les correspondances d'identifiants entre cours Moodle et structures EduNova.
- Éviter la synchronisation bidirectionnelle des notes dans la première version.
- Un établissement peut utiliser Moodle, Classroom, les deux ou aucun.

### 5.6 Classes virtuelles Jitsi — P2

Use cases candidats :
- `ScheduleVirtualClass`
- `CreateVirtualMeeting`
- `GetVirtualMeetingAccess`
- `CancelVirtualMeeting`

Règles :
- une réunion est rattachée à un cours, une classe ou un événement autorisé ;
- l'accès est accordé uniquement aux participants autorisés ;
- les URLs de réunion ne doivent pas être des secrets durables ;
- si JaaS est choisi, vérifier les quotas, coûts, domaines et mécanismes JWT ;
- si auto-hébergé, documenter la maintenance, capacité, mises à jour et sécurité ;
- aucune captation/enregistrement par défaut ;
- le lien de réunion ne doit pas contourner les autorisations EduNova.

Ne pas intégrer un serveur Jitsi auto-hébergé dans cette phase sans étude d'exploitation.

### 5.7 Paiements numériques — P1 pour l'architecture, activation fournisseur conditionnelle

**Règle absolue :** le module Finance et son registre de paiements restent la source de vérité. Un PSP ne fait que collecter ou rapporter un paiement.

Use cases candidats :
- `InitiateExternalPayment`
- `ReceivePaymentProviderWebhook`
- `VerifyExternalPayment`
- `ReconcileExternalPayment`
- `HandlePaymentFailure`
- `RequestPaymentRefund` (seulement si le domaine Finance le supporte et si la politique métier est ratifiée)

Règles :
- ne jamais marquer une facture payée sur la seule base du retour navigateur ;
- valider la signature du webhook et, si nécessaire, interroger l'API serveur du PSP ;
- l'identifiant transaction du PSP est unique dans le contexte fournisseur ;
- imposer l'idempotence sur l'initiation et la confirmation ;
- vérifier tenant, facture, montant, devise et bénéficiaire ;
- refuser tout mismatch montant/devise/référence ;
- enregistrer une preuve technique de confirmation et la référence externe ;
- comptabiliser le paiement via le use case Finance existant, jamais en écrivant directement dans les tables depuis le contrôleur webhook ;
- une transaction initiale ne doit pas être supprimée ou modifiée pour simuler un remboursement ; respecter le mécanisme de correction/contre-écriture existant ;
- USD et CDF restent des devises distinctes ; aucune conversion implicite ;
- ne jamais stocker de PAN/CVV ou données de carte.

**Sélection fournisseur :**
1. Stripe : sandbox uniquement tant que l'éligibilité du marchand RDC n'est pas établie.
2. Flutterwave : candidat à vérifier ; ne pas activer pour la RDC sur la seule base de la prise en charge de pays voisins ou de Mobile Money en XAF.
3. Agrégateur/opérateur local : rechercher et valider un fournisseur réellement contractable en RDC et prenant en charge les moyens demandés.

Aucun fournisseur de paiement de production n'est sélectionné par défaut dans ce document.

### 5.8 PostHog — P3

- Utiliser PostHog pour mesurer l'adoption et la qualité d'usage du produit, pas pour analyser les performances individuelles des élèves.
- Commencer par un petit catalogue d'événements produit.
- Éviter les propriétés contenant des informations directement identifiantes.
- Ne jamais envoyer le contenu de formulaires, URL avec données sensibles, tokens, emails, noms, notes ou montants individuels.
- Prévoir désactivation par environnement et, si nécessaire, par tenant.
- Respecter le consentement, les politiques de confidentialité et la durée de conservation.
- Le SDK frontend ne reçoit qu'une clé publique de projet conçue pour le navigateur ; aucune clé personnelle/admin.
- Les événements critiques ou administratifs ne doivent pas dépendre de PostHog pour leur persistance ou leur audit.

---

## 6. Expérience utilisateur Front-end

Ajouter les intégrations progressivement à l'interface existante sans refaire toute l'application.

### Écrans cibles

1. **Paramètres → Intégrations**
   - catalogue des connecteurs disponibles ;
   - statut : non configuré, connecté, action requise, désactivé, erreur ;
   - bouton connecter/déconnecter ;
   - permissions demandées, fournisseur, date de connexion ;
   - indicateur de santé et dernière synchronisation ;
   - quotas/consommation lorsqu'une donnée fiable existe.

2. **Communication → Notifications**
   - préférences par canal et catégorie ;
   - historique et statut des envois ;
   - filtres par période/type ;
   - retry réservé aux rôles autorisés.

3. **Calendrier scolaire**
   - événements EduNova ;
   - état de synchronisation Google ;
   - erreurs de synchronisation explicites ;
   - aucune édition externe silencieuse du calendrier officiel.

4. **Pédagogie → Connecteurs LMS**
   - statut Classroom/Moodle ;
   - correspondance des classes/cours ;
   - prévisualisation avant toute synchronisation ;
   - historique des imports/exports.

5. **Finance → Paiements en ligne**
   - moyens réellement activés dans le pays/devise ;
   - statut de transaction ;
   - référence PSP ;
   - aucun statut « payé » optimiste avant confirmation serveur.

6. **Cours → Classe virtuelle**
   - création et accès à la réunion ;
   - liste des participants autorisés ;
   - état de la salle.

### Design et ergonomie

- Réutiliser le Design System et les conventions déjà présents dans le frontend.
- Ne pas introduire une nouvelle bibliothèque UI sans audit et justification.
- Afficher les états loading, empty, success, partial failure et error.
- Prévoir les erreurs réseau et les connexions lentes.
- Responsive desktop/tablette/mobile.
- Le frontend masque les actions non autorisées pour l'UX, mais le backend reste l'autorité d'autorisation.

---

## 7. Configuration et gestion des coûts

Prévoir une configuration validée et documentée, sans secret commité.

Exemples de noms conceptuels à adapter aux conventions de configuration existantes :

- `EDUNOVA_EMAIL_PROVIDER`
- `BREVO_API_KEY`
- `RESEND_API_KEY`
- `FCM_PROJECT_ID`
- `FCM_SERVICE_ACCOUNT` (fichier secret ou mécanisme sécurisé, jamais valeur committée)
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `JITSI_BASE_URL`
- `JITSI_APP_ID`
- `JITSI_APP_SECRET`
- `POSTHOG_PROJECT_KEY`
- `POSTHOG_HOST`

Ces noms ne sont pas des contrats imposés : l'agent doit d'abord inspecter `Settings`, le container et les conventions d'environnement. Ne pas ajouter de variables inutilisées.

### Contrôle des coûts

Pour chaque fournisseur, suivre si possible :
- appels envoyés ;
- succès/échecs ;
- consommation de quota ;
- consommation par tenant ;
- estimation de coût lorsque le tarif est connu ;
- seuils d'alerte ;
- état du circuit en cas d'indisponibilité.

Les quotas fournisseurs peuvent être partagés au niveau du projet : afficher clairement cette réalité. Ne pas présenter un quota global comme un quota garanti pour chaque école.

---

## 8. Plan d'implémentation par phases

### Phase 0 — Audit et conception (obligatoire, sans code)

- Cartographier les domaines et use cases existants.
- Inventorier les mécanismes de tâches de fond, events, migrations, configuration, secrets, logs et tests.
- Vérifier les dépendances frontend et backend.
- Identifier les intégrations ou tables déjà existantes.
- Vérifier les décisions Finance et les contrats de paiement existants.
- Produire `INTEGRATIONS_GAP_ANALYSIS.md` et une proposition d'ADR.

**Sortie :** plan précis de fichiers, risques, choix à faire ratifier. Aucun code modifié.

### Phase 1 — Noyau Integration minimal

Après validation :
- définir les contrats réellement nécessaires ;
- enregistrer les intégrations et leur statut ;
- associer les configurations aux tenants ;
- sécuriser les secrets et tokens ;
- mettre en place l'idempotence et le suivi des opérations ;
- mettre en place outbox/dispatcher si nécessaire, selon l'infrastructure existante ;
- journaliser les opérations sans données sensibles ;
- créer les tests d'isolation tenant et de résilience.

**Sortie :** noyau testé sans dépendre d'un fournisseur payant.

### Phase 2 — Notifications email et centre de notifications

- implémenter le port email ;
- connecter un seul fournisseur initial (Brevo après validation de compte et de domaine) ;
- intégrer les événements métier approuvés ;
- préférences et historique ;
- retries, idempotence, tests et écran d'administration.

**Sortie :** notification transactionnelle réellement délivrable en sandbox/test puis environnement autorisé.

### Phase 3 — Push

- valider la compatibilité PWA/browser actuelle ;
- intégrer FCM ;
- gestion des tokens d'appareils ;
- tests permission, révocation, tenant et expiration.

**Sortie :** push réel sur les clients officiellement supportés.

### Phase 4 — Paiements numériques

- choisir le fournisseur RDC après vérification écrite de l'éligibilité et des moyens ;
- implémenter le port PSP ;
- webhooks signés, idempotence et réconciliation ;
- brancher sur les use cases Finance existants ;
- tests de doublons, montant/devise erronés, rejeu, paiement échoué et remboursement.

**Sortie :** sandbox complet et validation opérationnelle avant activation réelle.

### Phase 5 — Google Calendar

- OAuth minimal ;
- synchronisation unidirectionnelle ;
- gestion des conflits, quotas et révocation ;
- interface d'état de synchronisation.

### Phase 6 — Connecteurs pédagogiques

- commencer par un seul connecteur pilote, choisi avec un établissement ;
- lecture seule et mapping des cours ;
- prévisualisation ;
- écrire/synchroniser uniquement après validation métier ;
- Moodle et Classroom restent des adaptateurs distincts.

### Phase 7 — Classes virtuelles

- comparer JaaS et auto-hébergement ;
- valider coûts, sécurité, exploitation et capacité ;
- créer les use cases et l'interface ;
- tester accès, expiration et annulation.

### Phase 8 — Analytics produit

- catalogue d'événements minimal ;
- revue confidentialité ;
- activation progressive ;
- vérifier qu'aucune donnée scolaire sensible ne quitte EduNova.

Ne pas démarrer la phase suivante tant que les critères de sortie de la phase en cours ne sont pas satisfaits.

---

## 9. Stratégie de tests obligatoire

### Tests unitaires
- sélection du fournisseur ;
- validation des préférences ;
- règles d'idempotence ;
- mapping des payloads ;
- politique de retry ;
- validation montant/devise ;
- contrôle des transitions d'état.

### Tests d'intégration
- repository et migrations sur DB temporaire ;
- container et injection des ports ;
- outbox/dispatcher ;
- signature et déduplication des webhooks ;
- chiffrement/déchiffrement des credentials ;
- simulation d'indisponibilité fournisseur.

### Tests de sécurité
- accès inter-tenant refusé ;
- rôles insuffisants refusés ;
- token OAuth expiré/révoqué ;
- signature webhook invalide ;
- rejeu de webhook ;
- payload trop volumineux/invalide ;
- absence de secret dans logs et réponses ;
- SSRF : ne jamais accepter une URL arbitraire de callback ou webhook fournie par un utilisateur sans allowlist/validation stricte.

### Tests end-to-end
- administrateur connecte/déconnecte un service ;
- notification créée et visible ;
- notification délivrée ou échec expliqué ;
- calendrier synchronisé ;
- paiement confirmé par webhook et visible dans Finance ;
- un autre tenant ne peut voir ni manipuler l'intégration.

Les tests fournisseurs utilisent des mocks contractuels ou des sandboxes officielles. Ne pas faire dépendre la suite unitaire de l'accès réseau.

---

## 10. Observabilité et exploitation

Pour chaque intégration, fournir :
- statut de connexion ;
- dernière opération réussie ;
- dernière erreur expurgée ;
- nombre d'échecs consécutifs ;
- backlog des tâches en attente ;
- compteur de retries ;
- consommation de quota si disponible ;
- action de désactivation d'urgence réservée au rôle adéquat.

Prévoir des identifiants de corrélation entre use case, tâche outbox, appel fournisseur et webhook. Ne pas utiliser un identifiant personnel comme correlation ID.

---

## 11. Critères de fin de chaque phase

Une phase est terminée seulement si :

- les règles métier sont documentées ;
- les décisions DDD/ADR sont ratifiées ;
- les ports et adaptateurs respectent les frontières ;
- les contrôles tenant et RBAC sont testés ;
- les migrations sont testées sur DB temporaire ;
- les tests unitaires et intégration passent ;
- les tests frontend pertinents passent ;
- le build frontend passe ;
- les erreurs et logs sont sûrs ;
- le parcours réel a été vérifié lorsque le service externe le permet ;
- la documentation et le rapport de clôture sont à jour ;
- aucun changement non autorisé n'a été fait sur les données ou branches protégées.

Le nombre de tests réussis ne suffit pas à déclarer une phase prête : les parcours fonctionnels et les cas d'échec doivent aussi être démontrés.

---

## 12. Livrables documentaires

L'agent doit maintenir :

- `docs/integrations/INTEGRATIONS_GAP_ANALYSIS.md`
- `docs/decisions/ADR-INTEGRATION-PLATFORM.md`
- `docs/integrations/INTEGRATION_SECURITY_MODEL.md`
- `docs/integrations/PROVIDER_CONFIGURATION.md`
- `docs/integrations/INTEGRATION_OPERATIONS_RUNBOOK.md`
- un rapport de clôture par phase, par exemple `docs/integrations/PHASE_2_NOTIFICATIONS_REPORT.md`

Ne pas créer tous ces documents vides d'un coup. Les créer au moment où leur contenu est vérifié.

---

## 13. Sources officielles à consulter au moment de l'implémentation

Les quotas, tarifs, pays supportés, scopes et conditions évoluent. L'agent doit relire les pages officielles avant chaque intégration et consigner la date de vérification.

- Brevo pricing : https://help.brevo.com/hc/en-us/articles/208589409-About-Brevo-s-pricing-plans
- Resend pricing : https://resend.com/pricing
- Courier pricing : https://www.courier.com/pricing
- Firebase pricing / FCM : https://firebase.google.com/pricing
- Google Classroom API overview : https://developers.google.com/workspace/classroom
- Google Classroom scopes : https://developers.google.com/workspace/classroom/guides/auth
- Google Classroom quotas : https://developers.google.com/workspace/classroom/reference/limits
- Google Calendar API scopes : https://developers.google.com/workspace/calendar/api/auth
- Google Calendar quotas : https://developers.google.com/workspace/calendar/api/guides/quota
- Jitsi Meet : https://jitsi.github.io/handbook/
- JaaS : https://jaas.8x8.vc/
- Moodle Web Services : https://moodledev.io/docs/5.0/apis/subsystems/external
- Stripe availability : https://stripe.com/global
- Flutterwave payment methods : https://developer.flutterwave.com/docs/payment-methods
- Flutterwave mobile money support : https://flutterwave.com/us/support/payment-methods/payment-channels
- PostHog pricing : https://posthog.com/pricing

### Notes de vérification déjà identifiées

- Brevo documente actuellement une offre gratuite avec 300 envois email par jour ; cela ne constitue pas une capacité garantie par tenant.
- Firebase présente FCM parmi ses produits sans coût ; les autres produits Firebase et infrastructures associées peuvent avoir des coûts distincts.
- Google Classroom et Calendar imposent OAuth, scopes et quotas ; les utilisateurs/administrateurs doivent autoriser les accès.
- La disponibilité Stripe est pays-dépendante ; ne pas présumer qu'une société immatriculée en RDC peut ouvrir un compte marchand Stripe.
- Flutterwave liste des méthodes Mobile Money régionales, mais la disponibilité effective en RDC, en CDF et auprès des opérateurs locaux doit être confirmée avant tout choix.
- Ne pas recopier dans l'application des chiffres de quotas ou tarifs sans date de vérification et source officielle.

---

## 14. Première mission concrète de l'agent

**Mission : audit uniquement.**

1. Lire le masterplan et les ADR existants.
2. Inspecter les domaines Communication, Finance, Tenancy, Identity, Academic et le frontend.
3. Rechercher les intégrations, webhooks, tâches de fond, événements et repositories déjà présents.
4. Inspecter les dépendances et versions réelles du projet.
5. Vérifier la configuration et les conventions de secrets.
6. Cartographier les parcours utilisateur concernés.
7. Produire `docs/integrations/INTEGRATIONS_GAP_ANALYSIS.md`.
8. Proposer une séquence de phases et les ADR nécessaires.
9. Lister précisément les décisions qui requièrent l'arbitrage du propriétaire du produit.

**Interdiction pendant cette mission :** modifier le code, installer des packages, créer des tables/migrations, toucher aux fichiers `.env`, changer de branche, modifier des bases de données ou appeler un fournisseur externe réel.

### Format du rapport d'audit

Pour chaque capacité, indiquer :

| Champ | Contenu attendu |
|---|---|
| État | absent / partiel / existant / opérationnel / non vérifié |
| Preuve | chemins, classes, fonctions et tests réels |
| Réutilisation | ce qui peut être conservé |
| Écart | ce qui manque |
| Risque | sécurité, tenant, coût, disponibilité, données |
| Proposition | changement minimal recommandé |
| Tests | tests existants et tests à ajouter |
| Décision requise | oui/non, question précise |

**Ne jamais inventer un fichier, un use case, un test réussi ou une intégration opérationnelle.**

---

## Décision directrice

L'ordre recommandé est : **audit → noyau Integration → notifications → push → paiement local validé → calendrier → connecteurs pédagogiques → classes virtuelles → analytics**.

EduNova doit rester utilisable sans aucun de ces fournisseurs. Les intégrations ajoutent de la valeur ; elles ne doivent jamais devenir le cœur de l'ERP.
