# EduNova Fusion — Masterplan stratégique et architectural

> **Statut :** document directeur proposé — version 1.0  
> **Dépôt :** FULAMA/EduNova  
> **Branche de travail :** `maintenance/edunova-mypy-cleanup`  
> **Horizon :** évolution progressive vers une infrastructure éducative numérique panafricaine  
> **Principe directeur :** comprendre avant de construire, construire avant d'optimiser, optimiser avant de complexifier.

## 1. Vision

EduNova Fusion vise à devenir une plateforme éducative modulaire, sécurisée et accessible qui relie établissements, apprenants, familles, enseignants, réseaux scolaires et partenaires technologiques.

La vision associe quatre axes :
1. **AI-enabled** : une IA utile, contextualisée, contrôlée et auditable.
2. **Platform** : une plateforme SaaS multi-établissements et extensible.
3. **Africa-first** : une conception adaptée aux connexions instables, aux appareils modestes, aux réalités administratives locales et aux paiements locaux.
4. **Automation with guardrails** : automatiser les tâches répétitives sans déléguer aveuglément les décisions sensibles.

Cette vision est une direction stratégique, pas une affirmation que ces capacités existent déjà.

## 2. Principes non négociables

- **Sécurité par conception** : autorisation côté serveur, moindre privilège, validation des entrées, gestion sécurisée des secrets et journalisation des opérations sensibles.
- **Isolation des tenants** : chaque accès aux données d'un établissement doit être limité au tenant autorisé. Le `tenant_id` fait partie des invariants métier et de persistance.
- **Confidentialité** : collecter le minimum de données nécessaire, limiter les accès, définir la rétention et documenter les usages.
- **Traçabilité financière** : une correction de paiement est une contre-écriture auditable ; elle ne supprime ni ne réécrit l'opération initiale.
- **Monnaies explicites** : USD et CDF ne sont jamais convertis implicitement.
- **Décisions sensibles sous contrôle humain** : aucune promotion, sanction, décision d'admission, écriture financière ou modification critique ne doit être décidée uniquement par une IA.
- **Compatibilité ascendante maîtrisée** : migrations versionnées, préconditions explicites, tests d'upgrade et stratégie de retour arrière adaptée.
- **Qualité démontrable** : ne déclarer une fonctionnalité prête qu'après vérification du code, tests pertinents, contrôles de sécurité et documentation.
- **Pas de complexité prématurée** : privilégier un monolithe modulaire tant que des contraintes mesurées ne justifient pas une extraction en services.
- **Respect de l'existant** : ne pas exécuter de migrations sur les bases locales permanentes `edunova.db` et `edunova_dev.db` sans procédure explicite et sauvegarde vérifiée.

## 3. Domaines métier cibles

| Domaine | Responsabilités principales |
|---|---|
| Identity & Access | Comptes, authentification, rôles, permissions, sessions et audit d'accès |
| Academic | Années scolaires, inscriptions, classes, élèves, enseignants, notes, présences, bulletins et délibérations |
| Finance | Catalogue de frais, affectations, paiements, reçus, corrections et rapports |
| Communication | Annonces, notifications, messages et préférences de contact |
| AI & Insights | Assistants, analyses, explications et recommandations fondées sur des données autorisées |
| SaaS Platform | Tenants, établissements, campus, configuration, abonnements et limites de service |
| Integration | API, webhooks, imports/exports et connecteurs partenaires |
| Identity Passport | Dossier scolaire portable, partage autorisé et vérification de documents |
| Offline & Sync | Stockage local maîtrisé, synchronisation différée et résolution de conflits |
| Governance | Indicateurs agrégés, rapports de réseau et supervision autorisée |

Les domaines sont des frontières conceptuelles. Ils ne doivent pas automatiquement devenir des microservices ou des packages séparés avant que le code existant ait été audité.

## 4. Architecture cible progressive

### 4.1 Court terme : monolithe modulaire

- Conserver les couches de présentation, application, domaine et infrastructure lorsque la structure existante les supporte.
- Garder la logique métier hors des contrôleurs et des détails de persistance.
- Définir des interfaces claires entre domaines.
- Utiliser des transactions explicites pour les opérations multi-écritures.
- Prévoir des tests unitaires, d'intégration, de migration et d'autorisation.
- Documenter les dépendances autorisées entre modules.

### 4.2 Évolution SaaS

Avant l'ouverture commerciale, valider :
- création et configuration d'un tenant ;
- isolation des données à chaque frontière d'accès ;
- permissions et séparation des rôles ;
- quotas et limites de ressources ;
- sauvegardes et restauration testée ;
- observabilité, alertes et gestion des incidents ;
- politiques de rétention, export et suppression autorisée des données ;
- procédures de déploiement et de migration.

PostgreSQL avec Row-Level Security peut être évalué comme cible, mais aucune migration de base de données ne doit être entreprise avant stabilisation de la V1, étude de compatibilité et plan de migration validé.

### 4.3 Services distribués

N'extraire un domaine en service séparé que si une contrainte mesurée le justifie : charge indépendante, isolation opérationnelle, équipe autonome, besoin de disponibilité distinct ou frontière de sécurité spécifique. Chaque extraction doit inclure contrats, observabilité, sécurité, stratégie de données et tests de résilience.

## 5. Programme d'innovation

### A. EduNova AI

- Assistant administratif fondé sur les permissions de l'utilisateur.
- Synthèse et génération de rapports vérifiables.
- Détection d'anomalies et de tendances, avec explications et limites connues.
- Assistant pédagogique pour préparer des ressources.
- Recherche dans les documents autorisés.
- Traçabilité des requêtes et des actions de l'IA, avec protection des données sensibles.

**Garde-fous :** pas d'accès implicite à toutes les données, pas d'exécution arbitraire de commandes, pas de décision automatisée à fort impact, sorties présentées comme recommandations et mécanisme de validation humaine.

### B. EduNova Africa-First / Edge

- Applications mobiles optimisées pour appareils modestes.
- Mode hors ligne pour des fonctions explicitement définies.
- Synchronisation différée et idempotente.
- Détection et présentation des conflits plutôt que remplacement silencieux.
- Protection des données locales, expiration des sessions et effacement contrôlé.
- Stratégies de faible consommation de données.

Le mode hors ligne ne doit pas mettre en cache des données privées d'API sans justification, contrôle d'accès local et politique d'expiration.

### C. EduNova Identity Passport

- Dossier scolaire portable avec partage explicite et limité.
- Historique de provenance et journal des accès.
- Vérification de documents et prévention des falsifications.
- Processus de transfert entre établissements avec validation et possibilité de correction.
- Minimisation des données exposées.

L'identifiant éducatif ne doit pas être conçu comme un identifiant public universel permettant le suivi non autorisé d'une personne.

### D. EduNova Ecosystem

- API versionnées et documentées.
- Authentification adaptée aux intégrations, permissions minimales et rotation des clés.
- Webhooks signés, réessais et protection contre les doublons.
- Environnement de test/sandbox.
- Catalogue d'extensions soumis à validation de sécurité.
- Contrats de compatibilité et politique de dépréciation.

### E. EduNova Governance

- Indicateurs agrégés par période, classe et établissement selon les droits.
- Définitions documentées des métriques.
- Protection contre la ré-identification dans les petits groupes.
- Accès institutionnel explicitement autorisé et audité.
- Aucun partage de dossiers individuels par défaut.

## 6. Feuille de route et critères de sortie

### Étape 0 — Fiabiliser le socle actuel
**Travail :** terminer la maintenance, auditer les migrations récentes, exécuter les tests disponibles et vérifier les contrôles de sécurité.

**Sortie attendue :** résultats de tests reproductibles, défauts connus consignés, état CI vérifié, aucune modification destructive des bases locales.

### Étape 1 — Stabiliser la V1 scolaire
**Travail :** vérifier les parcours critiques d'identité, inscriptions, classes, notes, présences, bulletins, délibérations et finances.

**Sortie attendue :** scénarios de bout en bout documentés, permissions testées, invariants métier validés et procédures de correction auditable.

### Étape 2 — Valider les contrats d'API
**Travail :** examiner les API nécessaires à l'application élève, en environnement isolé, sans changer le service existant par défaut.

**Sortie attendue :** contrats documentés, tests d'autorisation et de tenant, erreurs prévisibles et schémas stables.

### Étape 3 — Applications élève et parent
**Travail :** construire Flutter Student après validation des API ; développer le portail parent avec relations tuteur-enfant validées.

**Sortie attendue :** accès limité aux dossiers autorisés, tests de session et de permissions, expérience utilisable sur appareils modestes.

### Étape 4 — Communication et IA encadrée
**Travail :** notifications, annonces, assistant limité aux outils autorisés et analyses explicables.

**Sortie attendue :** journalisation, limites d'accès, tests d'abus et validation humaine des opérations sensibles.

### Étape 5 — Préparation commerciale SaaS
**Travail :** onboarding des établissements, configuration, abonnements, quotas, sauvegardes, restauration, supervision et réponse aux incidents.

**Sortie attendue :** tests d'isolation inter-tenant, restauration démontrée, procédures d'exploitation et modèle de coûts documentés.

### Étape 6 — Interopérabilité et identité éducative
**Travail :** API partenaires, import/export, vérification de documents et transferts autorisés.

**Sortie attendue :** contrats versionnés, consentements/permissions définis, traçabilité et tests de sécurité.

### Étape 7 — Écosystème et gouvernance
**Travail :** webhooks, SDK, extensions, statistiques agrégées et outils de pilotage.

**Sortie attendue :** processus d'approbation des extensions, politiques de données et contrôle d'accès institutionnel testés.

## 7. Définition de « prêt »

Une fonctionnalité ne peut être déclarée prête que si :
1. ses règles métier et ses cas limites sont documentés ;
2. les tests pertinents existent et ont été exécutés ;
3. l'autorisation et l'isolation tenant sont testées ;
4. les migrations sont testées sur des bases temporaires représentatives ;
5. les journaux n'exposent pas de secrets ou de données personnelles inutiles ;
6. les erreurs et scénarios de reprise sont prévus ;
7. la documentation et les contrats concernés sont à jour ;
8. le résultat CI est observé, et non supposé.

## 8. Gouvernance technique

- Les changements se font sur une branche de travail, pas directement sur `main`.
- Les commits doivent être petits, cohérents et descriptifs.
- Aucun merge vers `main` sans revue des changements et validation des contrôles convenus.
- Les tests non exécutés doivent être signalés comme tels.
- Les migrations ne sont jamais lancées sur des données persistantes de production ou locales sans sauvegarde et plan explicites.
- Toute nouvelle intégration externe doit être évaluée selon ses permissions, sa disponibilité, son coût et le traitement des données.
- Les fonctionnalités ambitieuses doivent commencer par un ADR (Architecture Decision Record) lorsqu'elles modifient durablement les frontières, les données ou la sécurité.

## 9. Hors périmètre immédiat

Tant que la V1 n'est pas stable :
- pas de migration PostgreSQL précipitée ;
- pas de microservices par effet de mode ;
- pas d'IA autorisée à effectuer librement des écritures métier ;
- pas de blockchain sans cas d'usage démontré supérieur à des signatures et journaux classiques ;
- pas de marketplace publique avant la sécurité des API et la gouvernance des extensions ;
- pas d'automatisation des frais à l'inscription ;
- pas de cache privé hors ligne sans politique de sécurité explicite.

## 10. Prochaines actions

1. Auditer l'état réel de la branche de maintenance et des contrôles CI.
2. Vérifier l'état des tests des migrations 032 et 033, sans toucher aux bases persistantes.
3. Identifier les écarts entre l'architecture actuelle et ce masterplan.
4. Établir une liste priorisée de travaux techniques fondée sur les preuves du dépôt.
5. Mettre à jour ce document par des décisions explicites, pas par des hypothèses.

---

**Règle de pilotage :** l'ambition définit la direction ; les preuves, les tests et la sécurité déterminent ce qui peut être livré.
