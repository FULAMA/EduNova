# EduNova 2035 — Vision, Architecture & Innovation Blueprint

> **Statut :** document de vision et de cadrage stratégique  
> **Version :** 1.0 — 31 octobre 2026  
> **Périmètre :** vision cible à long terme. Les capacités décrites ne sont pas réputées implémentées.

## 1. Vision

EduNova ambitionne de devenir une infrastructure numérique éducative fiable, interopérable et accessible, conçue depuis les réalités des établissements africains et capable de servir des communautés éducatives à l'échelle internationale.

EduNova ne sera pas uniquement un logiciel de gestion scolaire. La plateforme doit connecter, dans un cadre de confiance, les établissements, apprenants, familles, enseignants, réseaux scolaires, institutions et fournisseurs de services éducatifs.

**Mission :** réduire la fragmentation administrative et pédagogique, améliorer la qualité des décisions éducatives et rendre les services numériques accessibles même lorsque la connectivité et les ressources sont limitées.

### Principes directeurs

1. L'éducation avant la technologie : chaque fonctionnalité répond à un besoin démontrable.
2. Privacy by design : minimiser les données collectées, les usages et les accès.
3. Security by design : intégrer la sécurité au métier, au code et aux opérations.
4. Offline-first : une coupure Internet ne doit pas bloquer les opérations essentielles.
5. Interoperability by design : API versionnées et formats documentés.
6. Responsabilité humaine : l'IA assiste, elle ne décide pas seule des parcours scolaires.
7. Modularité : des frontières métier explicites et des dépendances maîtrisées.
8. Souveraineté et portabilité : transparence sur le traitement et possibilité d'export contrôlé.
9. Complexité progressive : pas de technologie distribuée sans besoin mesuré.
10. Evidence over hype : chaque innovation est évaluée par des tests et des retours terrain.

## 2. Produits et domaines de l'écosystème

| Produit / domaine | Utilisateurs | Responsabilité |
|---|---|---|
| EduNova Core | Établissements | Référentiel métier et opérations scolaires |
| EduNova Identity | Élèves, familles, personnel | Identités, comptes, rôles, relations et consentements |
| EduNova Cloud | Promoteurs et réseaux | Provisionnement, tenants, campus, abonnements |
| EduNova Intelligence | Directions et enseignants | Recherche, analyses et recommandations explicables |
| EduNova Offline | Équipes de terrain | Opérations locales et synchronisation différée |
| EduNova Connect | Partenaires | API, webhooks, imports, exports et connecteurs |
| EduNova Trust | Établissements et vérificateurs | Authenticité des documents et acquis |
| EduNova Governance | Responsables habilités | Indicateurs agrégés et pilotage |
| EduNova Marketplace | Établissements et fournisseurs | Extensions et services validés |
| EduNova Developer | Développeurs | Documentation, SDK, sandbox et intégrations |
| EduNova Research | Équipe produit et chercheurs | Expérimentation et innovation responsable |

Ces noms décrivent une vision produit. Ils ne présument pas de dépôts, services ou applications séparés.

## 3. Architecture cible

### 3.1 Stratégie d'évolution

Le point de départ recommandé est un **monolithe modulaire** avec frontières métier explicites, contrats internes stables et séparation entre domaine, application, infrastructure et présentation.

Les microservices ne seront envisagés que lorsqu'un besoin mesuré le justifiera : charge indépendante, disponibilité distincte, déploiement autonome, frontière de sécurité ou contrainte organisationnelle. Toute extraction devra préserver les invariants métier et être précédée d'une analyse des coûts opérationnels.

### 3.2 Bounded contexts

- **Identity & Access :** comptes, authentification, autorisations, relations parent-enfant, sessions et audit.
- **Tenant & Organization :** établissements, réseaux, campus, configuration et abonnements.
- **Academic :** années, classes, inscriptions, matières, évaluations, notes, présences, bulletins et délibérations.
- **Finance :** frais, affectations, paiements, reçus, contre-écritures et rapprochements.
- **Communication :** annonces, notifications, messagerie et préférences.
- **Learning :** ressources, activités pédagogiques, parcours et acquis.
- **Trust & Credentials :** attestations, signatures, vérification et partage contrôlé.
- **Intelligence :** assistants, analyses, évaluations et gouvernance des modèles.
- **Integration :** API, webhooks, connecteurs et imports/exports.
- **Governance & Analytics :** indicateurs agrégés, tableaux de bord et rapports.

Chaque contexte possède ses règles et ses cas d'usage. Aucun autre contexte ne doit modifier ses données en contournant ses règles métier.

### 3.3 Multi-tenancy et isolation

- Toute donnée appartenant à un établissement est rattachée à un tenant explicite.
- Les contrôles d'accès vérifient le tenant côté serveur, indépendamment des identifiants fournis par le client.
- Les relations et requêtes sont tenant-scoped ; les contraintes de base de données renforcent les contrôles applicatifs.
- Les tests couvrent les accès croisés, identifiants devinés, tâches asynchrones et exports.
- Une future cible PostgreSQL pourra utiliser un schéma partagé avec Row-Level Security et contexte transactionnel SET LOCAL, après validation de la stratégie de connexion et des tests d'isolation.
- Les opérations de support plateforme sont limitées, justifiées et auditées.

**Règle : aucune optimisation de performance ne peut affaiblir l'isolation des tenants.**

### 3.4 Données et contrats

- Identifiants stables et propriété des données explicite.
- Dates, fuseaux horaires, périodes scolaires, langues, devises et formats locaux traités explicitement.
- Montants financiers en précision décimale avec devise obligatoire ; aucune conversion implicite USD/CDF.
- API versionnées, schémas documentés et compatibilité contrôlée.
- Événements métier utilisés lorsque cela apporte une valeur réelle.
- Migrations traçables et restauration testée.

## 4. Innovations structurantes

### 4.1 Passeport éducatif numérique

Un dossier portable retraçant les inscriptions, acquis, résultats et justificatifs vérifiés d'un apprenant.

Exigences : partage autorisé, accès limité dans le temps et au périmètre demandé, provenance vérifiable, corrections documentées, révocation, contestation et compatibilité avec des standards ouverts après étude.

Le passeport ne doit pas devenir un identifiant public universel ni exposer un historique scolaire à des tiers sans base légitime.

### 4.2 EduNova Offline

Les applications de terrain pourront enregistrer localement les opérations autorisées.

La conception devra traiter le chiffrement local, l'expiration et la révocation des sessions, la synchronisation idempotente, la résolution des conflits, l'horodatage, la provenance des modifications et la reprise après interruption.

Les opérations sensibles, notamment financières et les décisions académiques officielles, nécessiteront des règles de validation spécifiques.

### 4.3 EduNova Intelligence

Une couche IA connectée uniquement aux données et actions autorisées.

Capacités envisagées : recherche en langage naturel, synthèse de rapports, analyse des tendances d'absentéisme ou de résultats, prévisions budgétaires, assistance pédagogique et automatisation contrôlée.

Garde-fous obligatoires :
- autorisations du système source vérifiées à chaque requête ;
- minimisation et masquage des données ;
- provenance des réponses et indication de l'incertitude ;
- journalisation des actions et outils appelés ;
- validation humaine avant toute action à impact ;
- évaluation des biais, erreurs et hallucinations ;
- séparation stricte des données entre tenants ;
- règles explicites de conservation et de non-réutilisation.

Aucune décision automatisée d'exclusion, de sanction, de promotion ou d'orientation.

### 4.4 Digital Twin d'établissement

Un modèle analytique permettant de simuler des scénarios : évolution des effectifs, capacité des salles, besoins en enseignants, dépenses et répartition des ressources.

Les résultats seront présentés comme des estimations fondées sur des hypothèses, jamais comme des prédictions certaines. Les responsables pourront modifier les hypothèses et comparer plusieurs scénarios.

### 4.5 EduNova Trust

Vérification cryptographique des bulletins, attestations, certificats et diplômes. La priorité sera donnée aux signatures numériques, aux clés protégées, à la révocation et à la vérification simple. Une blockchain ne sera envisagée que si elle démontre un avantage réel par rapport à une architecture de confiance plus simple.

### 4.6 Developer Platform et Marketplace

À terme : API publique versionnée, OAuth2 / OpenID Connect selon les besoins, webhooks signés et idempotents, SDK maintenus, sandbox avec données synthétiques, permissions granulaires, revue de sécurité, quotas, observabilité, suspension et révocation des intégrations.

Aucune extension ne reçoit un accès global par défaut aux données d'un établissement.

## 5. Sécurité, confidentialité et confiance

La sécurité est une propriété transversale.

Socle attendu :
- modèle de menace maintenu et revu à chaque capacité majeure ;
- authentification robuste et MFA pour les rôles sensibles ;
- contrôle d'accès basé sur les rôles et attributs pertinents ;
- séparation des responsabilités ;
- chiffrement en transit et au repos ;
- gestion centralisée des secrets ;
- audit append-only pour les événements critiques ;
- sauvegardes chiffrées et restaurations testées ;
- protection contre les abus d'API ;
- gestion des vulnérabilités et dépendances ;
- procédure de réponse aux incidents ;
- politique de conservation, export et suppression conforme aux obligations applicables.

Les données scolaires des mineurs exigent une protection renforcée. Les obligations juridiques devront être vérifiées pays par pays avant tout déploiement.

## 6. Fiabilité et exploitation

- journaux structurés sans secrets ni données personnelles inutiles ;
- métriques techniques et métier ;
- traçage distribué lorsque cela se justifie ;
- alertes exploitables et procédures d'escalade ;
- objectifs de disponibilité définis par service ;
- sauvegardes et tests de restauration ;
- déploiements reproductibles et contrôlés ;
- migrations testées sur des copies représentatives ;
- inventaire des dépendances et versions supportées ;
- procédures d'exploitation documentées.

Les objectifs RPO/RTO seront définis avec les établissements pilotes.

## 7. Déploiement panafricain

EduNova doit être configurable sans être fragmenté.

Dimensions configurables : pays et juridiction, système éducatif, calendrier scolaire, langues, formats, devises, règles financières, documents réglementaires et modes de paiement.

La localisation des données, les transferts transfrontaliers, la fiscalité et la protection des mineurs seront évalués pour chaque marché. Les règles d'un pays ne seront jamais présumées applicables à un autre.

## 8. Feuille de route stratégique

| Horizon | Priorité | Résultat attendu |
|---|---|---|
| Maintenant | Stabilisation et maintenance | Socle fiable, tests et migrations sûrs |
| V1 | Produit scolaire opérationnel | Parcours essentiels élèves, enseignants, direction et finance validés |
| V1.x | Expérience mobile | Flutter élève et portail parent après validation des API |
| Étape suivante | Communication | Notifications, annonces et workflows fiables |
| Étape suivante | Cloud multi-établissements | Provisionnement, isolation, configuration et administration SaaS |
| Étape suivante | Offline-first | Synchronisation sécurisée et résilience terrain |
| Étape suivante | Intelligence responsable | Assistants et analyses évalués sur des cas réels |
| Étape suivante | Trust & Identity | Justificatifs vérifiables et dossier éducatif portable |
| Étape suivante | Developer Platform | API, SDK, sandbox et extensions contrôlées |
| Long terme | Governance, Marketplace, Research | Écosystème ouvert et innovation évaluée |

Les horizons calendaires dépendront des résultats, de la capacité de l'équipe, du financement et des retours des pilotes.

## 9. Indicateurs de réussite

Les indicateurs seront mesurés à partir d'une situation de référence :
- temps nécessaire aux opérations administratives courantes ;
- taux de réussite des synchronisations hors ligne ;
- taux d'erreurs et de conflits de synchronisation ;
- incidents d'accès inter-tenant (objectif : zéro) ;
- taux de restauration réussie des sauvegardes ;
- disponibilité des fonctions critiques ;
- adoption active par rôle ;
- délai de génération et de vérification des documents ;
- qualité des réponses IA évaluée sur des jeux de tests ;
- proportion d'actions sensibles validées par une personne habilitée ;
- satisfaction des établissements et familles.

Aucun indicateur ne doit inciter à surveiller excessivement les élèves ou à réduire leur parcours à un score algorithmique.

## 10. Gouvernance produit et technique

Toute capacité majeure suit ce processus :

1. problème utilisateur documenté ;
2. périmètre et utilisateurs autorisés définis ;
3. règles métier et invariants identifiés ;
4. analyse d'impact sur les données et la sécurité ;
5. décision d'architecture documentée (ADR) si nécessaire ;
6. tests unitaires, intégration, sécurité et isolation tenant ;
7. validation en environnement isolé ;
8. documentation et plan d'exploitation ;
9. pilote limité et collecte de retours ;
10. généralisation décidée sur preuves.

Les expérimentations seront isolées et ne mettront pas en danger les données de production.

## 11. Continuité du projet actuel

Ce blueprint ne remplace pas la feuille de route V1 et n'autorise pas une réécriture générale.

- préserver l'architecture et les fonctionnalités déjà livrées ;
- ne pas modifier la branche principale sans revue et validation ;
- conserver les bases locales existantes intactes ;
- ne pas exécuter de migration sur les bases locales ou de production sans procédure isolée et sauvegarde vérifiée ;
- ne pas migrer vers PostgreSQL avant stabilisation fonctionnelle de V1 ;
- maintenir l'API actuelle pendant la validation isolée du parcours bulletin ;
- conserver le travail PWA, sans le substituer à l'application Flutter élève ;
- ne pas déclencher automatiquement des frais lors d'une inscription ;
- préserver les corrections financières par contre-écritures traçables ;
- conserver les montants et devises sans conversion implicite.

## 12. Prochain incrément concret

1. terminer l'audit des migrations de facturation 032 et 033 ;
2. compléter les tests de contraintes, isolation tenant, idempotence et rollback ;
3. exécuter les tests en environnement isolé lorsque l'exécution est disponible ;
4. documenter les décisions d'architecture multi-tenant et de sécurité ;
5. définir les contrats API nécessaires au parcours bulletin ;
6. valider ce parcours sur une base temporaire et un port isolé ;
7. ensuite seulement, implémenter et valider l'application Flutter élève.

## Décision fondatrice

**EduNova sera une plateforme modulaire, sécurisée, interopérable et offline-capable, dont l'intelligence augmentera les capacités humaines sans remplacer la responsabilité des acteurs éducatifs.**

La réussite ne sera pas mesurée au nombre de technologies utilisées, mais à la confiance des établissements, à la qualité du service rendu et à la capacité d'évoluer sans compromettre les données ni les personnes.
