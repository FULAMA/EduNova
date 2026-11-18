# EduNova — Architecture DDD, décisions métier et PWA des rôles

**Nature :** état d’implémentation et conception additive  
**Version :** 1.0  
**Portée :** backend FastAPI, frontend React/Vite, portails PWA Parent, Élève et Professeur  
**Autorité métier :** le registre `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md` reste la référence des décisions. Ce document ne ratifie aucune proposition.

## 1. État vérifié

EduNova est un monolithe modulaire multi-tenant. Les contextes Identité, Tenancy, Académique, Billing et Intégrations sont présents, avec FastAPI, des cas d’usage applicatifs, des interfaces de dépôts, des adaptateurs SQLite et des routes HTTP. Cette structure constitue une base DDD utile, mais l’architecture n’est pas encore cohérente partout.

Les décisions D13 (permissions par rôle et portée), D14 (un contexte actif à la fois) et D16 (bulletins accessibles aux parents et élèves après publication officielle) sont marquées `VALIDÉE` dans le registre.

Les sujets suivants restent bloqués ou contradictoires :

| Sujet | Registre canonique | Code ou document divergent | Traitement retenu |
|---|---|---|---|
| D45 — identité et déduplication des élèves | Validée le 2026-11-19 : ID interne, matricule facultatif ; avertissement non bloquant sur prénom/nom normalisés identiques dans le tenant, revue humaine, aucune fusion automatique | Intégration au cas d’usage, réponse API et avertissement UI ajoutés ; critères NFKC, casse et espaces documentés | La procédure de revue et l’éventuelle fusion restent à concevoir |
| PAR-REL — association parent-élève | Cardinalités N:M, lien immédiat créé par `ADMIN`/`DIRECTION` après vérification par l’établissement ; consultation limitée aux bulletins officiels | Le backend vérifie rôle parent, membership actif, élève actif et tenant ; création identifie l’acteur | Preuves à conserver, révocation et historique restent à définir ; résultats détaillés, présences et finances sont exclus |
| BUL-TECH-02 — qui publie et corrige | Validée le 2026-11-19 : `ADMIN` et `DIRECTION` pour préparer, publier et corriger | Routes déjà protégées par ces deux rôles et test d’intégration existant | La révocation reste distincte et ouverte sous BUL-TECH-04 |
| Rôle enseignant | Glossaire : `PROF` | Une partie de l’API et des jetons emploie `TEACHER` | `PROF` est accepté comme rôle canonique ; `TEACHER` reste accepté comme alias de compatibilité. Aucun rôle stocké n’est renommé automatiquement |

## 2. Carte des contextes et dépendances

| Contexte | Modèle central | Responsabilité | Dépendances autorisées |
|---|---|---|---|
| Identity | `User`, identités externes, 2FA, sessions | Authentifier et établir l’identité | Ports de dépôt, services cryptographiques |
| Tenancy | `Tenant`, `Membership`, contexte actif | Isolation de l’établissement et rôles | Identity, ports de persistance |
| Academic | `Student`, `AcademicYear`, affectations, dossiers et bulletins | Cycle scolaire et résultats | Tenancy par identifiant et interfaces |
| Billing | `Money`, frais, obligations et paiements | Ledger financier et soldes | Tenancy, passerelles de paiement via ports |
| Integrations | Ports et adaptateurs externes | Notifications, paiement, IA et fournisseurs | Contextes métier uniquement via contrats |
| Presentation | Routes, schémas HTTP, composants React | Traduire les requêtes et présenter les résultats | Cas d’usage et contrats d’application |

### Règles de dépendance

1. Le domaine ne dépend ni de SQLite, ni de FastAPI, ni de React.
2. L’application orchestre des cas d’usage par des ports ; elle ne construit pas de requêtes SQL.
3. Les adaptateurs d’infrastructure implémentent les ports et traduisent les erreurs du moteur.
4. Les routes HTTP contrôlent le transport et les permissions, puis délèguent au cas d’usage.
5. Toute lecture ou écriture tenant-scoped reçoit le `tenant_id` vérifié côté serveur.
6. Les identifiants et les références de portails sont vérifiés dans le tenant courant ; un UUID fourni par le client n’accorde aucun accès.

### Agrégats à maintenir

- `User` porte l’état d’authentification ; `Membership` porte le rôle actif dans un tenant. Les rôles ne se cumulent pas entre tenants.
- `Student` porte son identité interne EduNova. Le matricule facultatif reste une référence ; l’égalité de nom normalisé déclenche un avertissement, jamais une fusion automatique.
- `StudentAssignment` porte le rattachement de l’élève à une classe et une année scolaire.
- `StudentAcademicRecord` porte une version de résultats ; une correction conserve l’historique.
- `ReportCard` porte un snapshot officiel versionné. Seul l’état `ISSUED` est présenté dans les portails familiaux.
- `TeacherAssignment` borne les classes et matières attribuées à un enseignant.
- `Payment` et ses corrections forment un journal non destructif. Les montants USD et CDF restent séparés.

## 3. Portails PWA — périmètre produit

Il s’agit d’une seule PWA EduNova, installable, dont la page d’accueil dépend du rôle et du tenant actifs. Les écrans web ne remplacent jamais l’autorisation serveur.

| Profil | État frontend | Données affichées | Limites actuelles |
|---|---|---|---|
| Parent | Écran ajouté : liste des élèves associés et bulletins officiels téléchargeables | Liens retournés par le serveur ; bulletins publiés | Pas de création de lien dans le portail, de présence, de résultat détaillé, de donnée financière ou de décision de tutelle |
| Élève | Écran existant, raccordé à l’espace de rôle | Son profil, ses résultats, présences et bulletins fournis par l’API | Pas de consultation du dossier d’un autre élève |
| Professeur | Écran en lecture seule : affectations du tenant actif avec libellés classe, matière et année scolaire | Libellés issus des dépôts tenant-scoped ; date d’attribution | Pas de saisie de note, correction, présence ou publication |

Les écrans parent et professeur sont filtrés par rôle dans le frontend et protégés par les routes FastAPI. `PROF` et l’alias `TEACHER` ouvrent le portail enseignant. Les données sensibles ne sont pas stockées hors ligne.

## 4. Fonctionnement PWA et mode hors ligne

- Le manifeste existant conserve `/app` comme URL d’ouverture et les icônes EduNova.
- Le service worker précache le shell de production et les fichiers construits sous `/assets/`.
- Une navigation hors ligne retourne le shell React en cache ; les appels métier restent réseau uniquement.
- Les réponses API, bulletins PDF, jetons, dossiers d’élèves et données financières ne sont jamais ajoutés au cache.
- Le nettoyage du service worker supprime uniquement les anciennes caches `edunova-static-*`, jamais les caches d’autres applications de même origine.
- En mode hors ligne, les pages indiquent que les données ne peuvent pas être chargées. La PWA ne prétend pas synchroniser des modifications hors ligne.

La synchronisation différée, les notifications push et les opérations métier hors ligne ne sont pas implémentées. Elles nécessitent une stratégie de conflits, de révocation des sessions et de protection des données locales avant conception détaillée.

## 5. Écarts DDD et séquence de fermeture

### Traités dans le code de cette évolution

- Liaison Google : réauthentification EduNova, TOTP si activé, nonce serveur à usage unique et vérification du nonce dans le jeton.
- `SubmitGradeDispute` ne contient plus de SQL ; les contrôles de référence tenant-scoped sont portés par le dépôt.
- `RegisterEstablishment` ne dépend plus des exceptions SQLite ; l’adaptateur de persistance traduit les conflits.
- Portails PWA rôle-parent et rôle-enseignant raccordés aux contrats API existants ; aliases `PROF`/`TEACHER` harmonisés sans migration de données.
- Service worker limité au shell public et aux assets, avec fallback de navigation hors ligne.

### À achever sans changer de règles métier

1. Les entit?s de facturation sont dans `billing/domain/entities.py`; les DTO pagin?s restent en application. Extraire ensuite le port de d?p?t de facturation et r?duire le couplage entre `BillingService` et SQLite.
2. Continuer les contrôles d’architecture interdisant les imports SQLite/FastAPI dans les couches domaine et application.
3. Aligner les pages Markdown historiques sur le code observé, sans réécrire l’historique des décisions.
4. Aligner les pages Markdown historiques sur le code observé ; remplacer les pourcentages anciens par des statuts sourcés et datés, sans réécrire l’historique des décisions.

### Bloqués par un arbitrage produit

1. D45 : procédure de revue des alertes et conditions d’une éventuelle fusion manuelle.
2. PAR-REL : définition des catégories de responsables, preuves à conserver, révocation et historique.
3. BUL-TECH-03/04 : accès aux versions remplacées et révocation.
4. Fonctionnalités professeur : droits et workflow de saisie/correction des notes, gestion des absences et publication.
5. Fonctionnalités parent : éventuel accès ultérieur aux présences, notifications et gestion des représentants.

Aucune option de cette section ne devient validée par la présente conception.

## 6. Critères de livraison PWA

- Le rôle du JWT détermine le portail initial ; le backend refuse tout rôle ou tenant non autorisé.
- Parent : aucun élève non associé ne peut être listé ou consulté ; aucun bulletin non publié n’est visible ; le PDF est autorisé uniquement pour cet élève et ce parent.
- Élève : toutes les lectures restent limitées à l’élève lié à son compte dans le tenant courant.
- Professeur : seules ses affectations sont retournées ; les rôles non enseignants reçoivent un refus serveur.
- Hors ligne : le shell s’ouvre, un état hors connexion est visible et aucune donnée privée n’est servie depuis Cache Storage.
- Petite largeur : navigation et actions restent utilisables au clavier et sur écran mobile.
- Les liens du registre de décisions sont conservés dans les rapports et les tests ; aucun test ne dépend de `edunova.db`.

## 7. Sources à réconcilier

- `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md` — autorité des décisions métier.
- `docs/product/EDUNOVA_DOMAIN_GLOSSARY.md` — vocabulaire et rôles ; vérifier les statuts `PARENT` et `PROF`.
- `docs/product/EDUNOVA_FUNCTIONAL_DDD_SPECIFICATION.md` — brouillon historique annoncé à 30 %, à réviser contre le code actuel.
- `docs/product/EDUNOVA_DECISION_CONFLICTS_AND_OPEN_QUESTIONS.md` — propositions et questions qui doivent rester ouvertes jusqu’à arbitrage.
- `docs/v1.2/ANALYSE_DDD_DECISIONS_METIER_ET_IMPLEMENTATION.md` — analyse du 17 novembre contenant des statuts PAR-REL et BUL-TECH-02 incompatibles avec le registre canonique.
