# EduNova - Travail en Cours : Spécification Fonctionnelle DDD

**Date de début** : 2025-XX-XX  
**Statut** : En cours d'analyse  
**Mission** : Réconciliation fonctionnelle et conception DDD d'EduNova

---

## 📋 État de l'Analyse

### Phase 1 : Inventaire Documentaire ✅
**81 fichiers Markdown identifiés** comme pertinents pour l'analyse.

#### Documents Principaux (Priorité Haute)
- [ ] `EDUNOVA_FUSION_MASTERPLAN.md` - Vision, principes, architecture ✅ LU
- [ ] `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md` - 44 décisions validées ✅ LU
- [ ] `docs/v1/DECISIONS_REQUISES.md` - Décisions V1 et réconciliations
- [ ] `docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md` - Plan d'intégration

#### Documents V1.2 (À examiner)
- [ ] `docs/v1.2/AUTH_TOTP_PERSISTENT_ANTI_REPLAY_REPORT.md`
- [ ] `docs/v1.2/SELF_SERVICE_REGISTRATION_STEP_4_REVIEW.md`
- [ ] `docs/v1.2/SELF_SERVICE_REGISTRATION_SECURITY_CLOSURE_REPORT.md`
- [ ] `docs/v1.2/PHASE_1_CONTAINER_INTEGRATION_REPORT.md`
- [ ] Plusieurs rapports de phase

#### Documents V1 (À examiner)
- [ ] `docs/v1/CONTRATS_API_AUTH_LOGOUT.md`
- [ ] `docs/v1/CONTRATS_API_BILLING_PAYMENTS_ARREARS.md`
- [ ] `docs/v1/CONTRATS_METIER_V1.md`
- [ ] `docs/v1/MATRICE_TRACABILITE_V1.md`
- [ ] `docs/v1/PLAN_IMPLEMENTATION_V1.md`
- [ ] `docs/v1/SUIVI_MISSION_V1.md`

#### Rapports (À examiner)
- [ ] `docs/reports/RAPPORT_*` (15+ rapports)

---

## 📚 Extraits Clés

### EDUNOVA_FUSION_MASTERPLAN.md

#### Vision
- **AI-enabled** : IA utile, contextualisée, contrôlée et auditable
- **Platform** : SaaS multi-établissements et extensible
- **Africa-first** : Conception adaptée aux connexions instables, appareils modestes, réalités locales
- **Automation with guardrails** : Automatiser sans déléguer les décisions sensibles

#### Principes Non Négociables
1. **Sécurité par conception**
   - Autorisation côté serveur
   - Moindre privilège
   - Validation des entrées
   - Gestion sécurisée des secrets
   - Journalisation des opérations sensibles

2. **Isolation des tenants**
   - Chaque accès limité au tenant autorisé
   - `tenant_id` est un invariant métier et de persistance

3. **Confidentialité**
   - Collecte minimale de données
   - Limitation des accès
   - Définition de la rétention
   - Documentation des usages

4. **Traçabilité financière**
   - Correction de paiement = contre-écriture auditable
   - Ne supprime ni ne réécrit l'opération initiale

5. **Monnaies explicites**
   - USD et CDF jamais convertis implicitement

6. **Décisions sensibles sous contrôle humain**
   - Pas de promotion, sanction, décision d'admission, écriture financière ou modification critique par IA seule

7. **Compatibilité ascendante maîtrisée**
   - Migrations versionnées
   - Préconditions explicites
   - Tests d'upgrade
   - Stratégie de retour arrière

8. **Qualité démontrable**
   - Ne déclarer prêt qu'après vérification du code, tests, contrôles de sécurité et documentation

9. **Pas de complexité prématurée**
   - Privilégier un monolithe modulaire

10. **Respect de l'existant**
    - Pas de migrations sur `edunova.db` et `edunova_dev.db` sans procédure et sauvegarde

#### Domaines Métier Cibles
| Domaine | Responsabilités |
|---------|----------------|
| Identity & Access | Comptes, authentification, rôles, permissions, sessions, audit |
| Academic | Années scolaires, inscriptions, classes, élèves, enseignants, notes, présences, bulletins, délibérations |
| Finance | Catalogue de frais, affectations, paiements, reçus, corrections, rapports |
| Communication | Annonces, notifications, messages, préférences |
| AI & Insights | Assistants, analyses, explications, recommandations |
| SaaS Platform | Tenants, établissements, campus, configuration, abonnements, limites |
| Integration | API, webhooks, imports/exports, connecteurs |
| Identity Passport | Dossier scolaire portable, partage autorisé, vérification |
| Offline & Sync | Stockage local, synchronisation différée, résolution de conflits |
| Governance | Indicateurs agrégés, rapports de réseau, supervision |

#### Architecture Cible
- **Court terme** : Monolithe modulaire
- **Évolution SaaS** : Validation avant ouverture commerciale
- **Services distribués** : Extraction uniquement si contrainte mesurée le justifie

#### Programme d'Innovation
- EduNova AI (Assistant administratif, synthèse, détection d'anomalies)
- EduNova Africa-First/Edge (Mobile optimisé, mode hors ligne)
- EduNova Identity Passport (Dossier scolaire portable)
- EduNova Ecosystem (API, webhooks, SDK, extensions)
- EduNova Governance (Indicateurs, supervision)

#### Feuille de Route
- **Étape 0** : Fiabiliser le socle actuel
- **Étape 1** : Stabiliser la V1 scolaire
- **Étape 2** : Valider les contrats d'API
- **Étape 3** : Applications élève et parent
- **Étape 4** : Communication et IA encadrée
- **Étape 5** : Préparation commerciale SaaS
- **Étape 6** : Interopérabilité et identité éducative
- **Étape 7** : Écosystème et gouvernance

#### Définition de "Prêt"
1. Règles métier et cas limites documentés
2. Tests pertinents existants et exécutés
3. Autorisation et isolation tenant testées
4. Migrations testées sur bases temporaires
5. Journaux sans secrets ou données personnelles
6. Erreurs et scénarios de reprise prévus
7. Documentation et contrats à jour
8. Résultat CI observé, non supposé

#### Hors Périmètre Immédiat
- Pas de migration PostgreSQL précipitée
- Pas de microservices par effet de mode
- Pas d'IA autorisée à effectuer librement des écritures métier
- Pas de blockchain sans cas d'usage démontré
- Pas de marketplace avant sécurité des API
- Pas d'automatisation des frais à l'inscription
- Pas de cache privé hors ligne sans politique de sécurité

---

### REGISTRE_DECISIONS_METIER_EDUNOVA.md

#### Instructions Impératives
1. Lire ce document avant toute tâche concernant les règles métier
2. Considérer uniquement les décisions marquées `VALIDÉE` comme adoptées
3. Ne jamais considérer une recommandation comme validée
4. En cas de contradiction avec le code, inspecter et signaler
5. Ne pas effectuer de refactorisation implicite
6. Préserver architecture, tests, traçabilité, isolation multi-tenant
7. Une décision enregistrée ≠ autorisation d'implémenter
8. Toute implémentation nécessite demande explicite et validation
9. Ne jamais supprimer l'historique des décisions modifiées
10. Ce registre est une référence, pas une source de vérité technique

#### Décisions Validées (1-44)

**Décision 1** - Seuil de réussite par matière
- **Statut** : VALIDÉE
- **Description** : Configurable par établissement. Valeur numérique du pilote à définir.

**Décision 2** - Politique académique à l'ouverture d'une période
- **Statut** : VALIDÉE
- **Description** : Politique fixée à l'ouverture, version conservée pour chaque calcul.

**Décision 3** - Correction d'un dossier académique validé
- **Statut** : VALIDÉE
- **Description** : Toute correction crée une nouvelle version. Ancienne conservée avec auteur, horodatage, motif obligatoire.

**Décision 4** - Crédits académiques
- **Statut** : VALIDÉE
- **Description** : Exclus du périmètre initial jusqu'à clarification de l'utilité et des règles.

**Décision 5** - Formule de moyenne générale
- **Statut** : VALIDÉE
- **Description** : Configurable par établissement, versionnée et traçable pour chaque calcul.

**Décision 6** - Notes manquantes et zéros
- **Statut** : VALIDÉE
- **Description** : Note manquante ≠ zéro. Distinguer notes en attente, évaluations non passées, absences, notes saisies.

**Décision 7** - Validation et publication des résultats
- **Statut** : VALIDÉE
- **Description** : Workflow configurable par établissement : rôles, étapes, validations. Actions tracées.

**Décision 8** - Correction après publication officielle
- **Statut** : VALIDÉE
- **Description** : Procédure configurable, conserve historique, motif, autorisations, validations, notifications.

**Décision 9** - Modification d'une politique en cours de période
- **Statut** : VALIDÉE
- **Description** : Traitement dépend de la nature, autorité, date d'effet, périmètre, traçabilité. Pas de recalcul rétroactif automatique.

**Décision 10** - Année scolaire et périodes
- **Statut** : VALIDÉE
- **Description** : Modèles organisationnels officiels avec adaptations autorisées, documentées, traçables.

**Décision 11** - Coefficients des matières
- **Statut** : VALIDÉE
- **Description** : Basés sur modèles officiels, versionnés et traçables.

**Décision 12** - Transferts d'élèves
- **Statut** : VALIDÉE
- **Description** : Procédures configurables selon type de transfert. Provenance et historique obligatoires.

**Décision 13** - Permissions par rôle
- **Statut** : VALIDÉE
- **Description** : Configurables par établissement et rôle, avec socle de sécurité obligatoire.

**Décision 14** - Comptes multi-rôles
- **Statut** : VALIDÉE
- **Description** : Un compte = un rôle/contexte actif à la fois. Changement de contexte contrôlé.

**Décision 15** - Absences aux évaluations
- **Statut** : VALIDÉE
- **Description** : Traitement configurable selon réglementation. Distinguer absence justifiée/non justifiée/en attente.

**Décision 16** - Consultation des bulletins
- **Statut** : VALIDÉE
- **Description** : Élèves et parents consultent après publication officielle. Résultats provisoires réservés au personnel autorisé.

**Décision 17** - Transfert interétablissements
- **Statut** : VALIDÉE
- **Description** : Importer dossier sans modifier résultats d'origine. Reconnaissance suit procédure autorisée.

**Décision 18** - Contestation d'une note
- **Statut** : VALIDÉE
- **Description** : Procédure formelle de réclamation, révision autorisée, décision motivée.

**Décision 19** - Journal financier
- **Statut** : VALIDÉE
- **Description** : Transactions individuelles traçables. Paiements partiels pris en charge. Corrections par contre-écriture.

**Décision 20** - Frais scolaires
- **Statut** : VALIDÉE
- **Description** : Barème configurable et versionné. Obligations individualisées par élève.

**Décision 21** - Responsabilités financières
- **Statut** : VALIDÉE
- **Description** : Configurables. Confirmation des paiements contrôlée. Annulations nécessitent autorisation distincte.

**Décision 22** - Échéanciers et impayés
- **Statut** : VALIDÉE
- **Description** : Échéances configurables. Arriérés calculés à partir des obligations et paiements confirmés.

**Décision 23** - Tableau de bord promoteur
- **Statut** : VALIDÉE
- **Description** : Afficher frais attendus, paiements confirmés, soldes, arriérés, reçus par période et ventilation par classe.

**Décision 24** - Notifications
- **Statut** : VALIDÉE
- **Description** : Configurables par événement, rôle, destinataire, canal. Traçabilité, préférences, confidentialité.

**Décision 25** - Mode hors ligne
- **Statut** : VALIDÉE
- **Description** : Limité aux fonctions autorisées. Synchronisation contrôlée avec détection de conflits.

**Décision 26** - Cycle de vie des comptes
- **Statut** : VALIDÉE
- **Description** : Création, activation, suspension, désactivation contrôlées. Historique conservé.

**Décision 27** - Authentification
- **Statut** : VALIDÉE
- **Description** : Mesures proportionnées au risque : mots de passe protégés, limitation tentatives, MFA pour comptes privilégiés.

**Décision 28** - Incidents de sécurité
- **Statut** : VALIDÉE
- **Description** : Processus structuré : détection, classification, confinement, révocation, préservation preuves, restauration.

**Décision 29** - Sauvegardes
- **Statut** : VALIDÉE
- **Description** : Protégées et séparées. Intégrité vérifiée. Restaurations testées.

**Décision 30** - Journaux d'audit
- **Statut** : VALIDÉE
- **Description** : Opérations sensibles génèrent journaux protégés avec contexte, acteur, action, cible, horodatage, résultat.

**Décision 31** - Cycle de vie des données
- **Statut** : VALIDÉE
- **Description** : Par catégorie : finalités, minimisation, durées de conservation, archivage, suppression/anonymisation.

**Décision 32** - Isolation multi-tenant
- **Statut** : VALIDÉE
- **Description** : Isolation à toutes les couches : contexte, autorisation, requêtes, base de données, tâches en arrière-plan.

**Décision 33** - Gestion des erreurs
- **Statut** : VALIDÉE
- **Description** : Gestion uniforme et classifiée : messages adaptés, journaux techniques protégés, identifiants de corrélation.

**Décision 34** - Stratégie de tests
- **Statut** : VALIDÉE
- **Description** : Multi-niveaux selon risque : unitaires, intégration, E2E, sécurité, isolation multi-tenant, non-régression.

**Décision 35** - Déploiement et retour arrière
- **Statut** : VALIDÉE
- **Description** : Déploiement contrôlé avec validation, sauvegardes, déploiement progressif, supervision, procédure de retour arrière.

**Décision 36** - Environnements
- **Statut** : VALIDÉE
- **Description** : Séparation stricte dev/test/préprod/prod. Données de test synthétiques ou anonymisées.

**Décision 37** - Dépendances
- **Statut** : VALIDÉE
- **Description** : Inventaire, verrouillage versions, scan vulnérabilités, limiter dépendances inutiles.

**Décision 38** - Protection de la vie privée
- **Statut** : VALIDÉE
- **Description** : Minimisation, finalités, obligations légales RDC, encadrement sous-traitants, gestion violations.

**Décision 39** - Exports
- **Statut** : VALIDÉE
- **Description** : Gouvernés par rôle, contexte, établissement, finalité. Champs et volumes contrôlés.

**Décision 40** - Performance
- **Statut** : VALIDÉE
- **Description** : Mesurer parcours critiques. Optimisations fondées sur mesures.

**Décision 41** - Observabilité
- **Statut** : VALIDÉE
- **Description** : Journaux, métriques, traces, identifiants de corrélation, alertes.

**Décision 42** - Gouvernance des évolutions produit
- **Statut** : VALIDÉE
- **Description** : Prioriser selon valeur, impact, risque, coût. Spécification, tests, version, communication.

**Décision 43** - Responsabilité de la numérisation initiale
- **Statut** : VALIDÉE — choix A
- **Description** : Équipe EduNova prend en charge avec participation de l'école.

**Décision 44** - Priorité de numérisation
- **Statut** : VALIDÉE — choix A
- **Description** : Priorité à l'année en cours, puis archives progressives.

#### Décisions Canoniques Bulletins
- **BUL-CAL-01** : Périodes configurables par profil académique - VALIDÉE
- **BUL-PUB-01** : Délibération persistée avant publication - VALIDÉE
- **BUL-COR-01** : Correction versionnée, ancienne en SUPERSEDED - VALIDÉE
- **BUL-CALC-01** : Politique versionnée, arrondi explicite - VALIDÉE AVEC RÉSERVE RÉGLEMENTAIRE
- **BUL-DOC-01** : PDF depuis snapshot immuable - VALIDÉE
- **BUL-PROF-01** : Profils académiques versionnés - VALIDÉE
- **BUL-SCOPE-01** : V1 couvre primaire, secondaire inférieur, humanités - VALIDÉE
- **BUL-REG-01** : Règles réglementaires propres aux niveaux - EN ATTENTE
- **BUL-TECH-01** : Choix techniques de publication - EN ATTENTE

#### Décisions Financières Canoniques
- **FIN-ROLE-01** : Finance accessible à direction, ACCOUNTANT, CASHIER - VALIDÉE
- **FIN-COR-01** : Correction par contre-écriture liée, jamais suppression - VALIDÉE
- **FIN-REC-01** : Reçu consultable et traçable - VALIDÉE AVEC RÉSERVES

#### Propositions Parent-Enfant (Non Validées)
- **PAR-REL-01** : Cardinalité parent-enfant - PROPOSÉE
- **PAR-REL-02** : Validation du rattachement - PROPOSÉE
- **PAR-REL-03** : Historique non destructif - PROPOSÉE
- **PAR-REL-04** : Accès parent aux données - PROPOSÉE
- **PAR-REL-05** : Séparation avec StudentUserLink - TECHNIQUEMENT CONFIRMÉE
- **PAR-REL-06** : Accès parent aux bulletins - PROPOSÉE

#### Décisions Techniques Bulletins (En Attente)
- **BUL-TECH-02** : Autorisations de publication et correction - EN ATTENTE
- **BUL-TECH-03** : Consultation des versions remplacées - EN ATTENTE
- **BUL-TECH-04** : Révocation d'un bulletin émis - EN ATTENTE
- **BUL-TECH-05** : Stockage et rétention du PDF - EN ATTENTE
- **BUL-TECH-06** : Audit des émissions et téléchargements - EN ATTENTE

---

## 🎯 Prochaines Étapes

1. ✅ Lire EDUNOVA_FUSION_MASTERPLAN.md
2. ✅ Lire REGISTRE_DECISIONS_METIER_EDUNOVA.md
3. [ ] Lire DECISIONS_REQUISES.md
4. [ ] Lire EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md
5. [ ] Lire les documents v1.2 (AUDIT, REPORTS)
6. [ ] Lire les documents v1 (CONTRATS, MATRICE)
7. [ ] Extraire toutes les règles métier
8. [ ] Identifier contradictions et decisions validées
9. [ ] Construire le modèle DDD
10. [ ] Produire la spécification finale

---

## 📝 Notes de Travail

### Catégories de Décisions Identifiées

1. **Academic** (D1-D18, BUL-*)
   - Seuil de réussite
   - Politiques académiques
   - Corrections
   - Notes et bulletins
   - Transferts
   - Absences

2. **Finance** (D19-D23, FIN-*)
   - Journal financier
   - Frais scolaires
   - Responsabilités
   - Échéanciers
   - Tableau de bord

3. **Identity & Access** (D13-D14, D26-D28, D32)
   - Permissions par rôle
   - Comptes multi-rôles
   - Cycle de vie des comptes
   - Authentification
   - Isolation multi-tenant

4. **Communication** (D24)
   - Notifications

5. **Infrastructure** (D25, D29-D31, D33-D38, D40-D42)
   - Mode hors ligne
   - Sauvegardes
   - Journaux d'audit
   - Gestion des erreurs
   - Tests
   - Déploiement
   - Environnements
   - Dépendances
   - Vie privée
   - Exports
   - Performance
   - Observabilité
   - Gouvernance

6. **Numérisation** (D43-D44)
   - Responsabilité
   - Priorité

---

## ⚠️ Points à Clarifier

1. Quelles sont les différences entre les décisions V1 et les décisions du registre ?
2. Comment les décisions canoniques (BUL-*, FIN-*) s'articulent-elles avec les décisions numérotées ?
3. Quelles décisions sont prioritaires pour l'implémentation actuelle ?
4. Comment gérer les propositions non validées (PAR-REL-*) ?
5. Quels sont les liens entre les documents v1.2 et les décisions métier ?
