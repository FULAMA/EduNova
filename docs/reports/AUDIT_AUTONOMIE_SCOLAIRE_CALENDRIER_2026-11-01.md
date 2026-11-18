# Audit ciblé — Autonomie scolaire et calendrier

- Date : 2026-11-01
- Base d'audit : branche `main` au commit observé pendant la mission
- Statut : audit statique du code et des migrations ; aucun test local n'a été exécuté par cette mission.
- Objectif : préparer la Tranche 1 sans modifier de base persistante ni introduire une règle implicite.

## 1. Années scolaires — D1-A

**État : PARTIELLEMENT CONFORME / GARDE-FOU DÉJÀ PRÉSENT**

Éléments observés :
- `AcademicYearStatus` utilise `DRAFT`, `ACTIVE`, `CLOSED`.
- `ChangeAcademicYearStatus.activate` refuse l'activation si une autre année est déjà `ACTIVE` pour le tenant.
- La migration `020` crée déjà l'index unique partiel `uq_academic_year_active` sur `tenant_id` pour les lignes `ACTIVE`.
- La route est tenant-contextualisée et limitée actuellement à `ADMIN`.

Conséquence :
- La décision D1-A est déjà largement matérialisée ; ne pas créer une migration redondante.
- Les noms canoniques de statut restent `ACTIVE` (pas `OPEN`) pour préserver la compatibilité.
- La vérification applicative seule n'est pas la garantie de concurrence : l'index unique doit rester la protection finale.

## 2. Autorisations — D2-C

**État : ÉCART À TRAITER**

Éléments observés :
- Les routes `academic-years` observées utilisent `require_role("ADMIN")`.
- Le modèle de décision ratifié distingue administration technique de la plateforme et responsabilités métier de l'établissement.
- Les fichiers inspectés ne démontrent pas encore une matrice de permissions scolaires granulaire appliquée à ces opérations.

Conséquence :
- Ne pas élargir les rôles par simple ajout d'une liste dans les routes.
- Définir un contrat d'autorisation par permission, tenant et contexte actif, puis le faire appliquer côté serveur.
- Préserver les contrôles `ADMIN` existants jusqu'à ce que le modèle RBAC soit implémenté et testé.

## 3. Calendriers et périodes — D3-B

**État : NON IMPLÉMENTÉ**

Éléments observés :
- `AcademicPeriod` porte `tenant_id` et un `academic_year_id` optionnel.
- La migration `021` ajoute l'année scolaire et une unicité de nom par année.
- Aucun identifiant de calendrier ou programme n'apparaît dans l'entité, le repository ou la migration inspectés.
- Le cas d'usage `CreateAcademicPeriod` vérifie l'appartenance à l'année et l'inclusion des dates, mais ne vérifie pas les chevauchements.

Conséquence :
- D3-B ne peut pas être implémentée correctement en ajoutant seulement un test de chevauchement : le domaine ne sait pas distinguer les calendriers/programmes.
- La Tranche 1 doit d'abord introduire un concept explicite de calendrier (tenant-scoped) et une relation déterministe période-calendrier.
- Règle cible : chevauchement interdit dans un même calendrier ; chevauchement possible entre calendriers/programmes distincts.
- Les périodes historiques sans calendrier ne doivent pas être rattachées arbitrairement. Elles restent non classées jusqu'à une opération de migration documentée et contrôlée.

## 4. Architecture et données

- `Tenant` est un agrégat distinct ; le profil d'établissement ne doit pas créer un second tenant.
- `AcademicPolicy` est aujourd'hui une dataclass de règles de calcul avec valeurs par défaut techniques. L'audit n'établit pas encore comment elle est chargée, versionnée ou liée aux calculs persistés.
- Les migrations `020` et `021` montrent des protections tenant utiles, mais elles ne suffisent pas à établir un versionnement général des politiques.
- Les repositories SQLite sont les adaptateurs de persistance actuels pour les années et périodes.

## 5. Plan de correction ordonné

1. Définir `AcademicCalendar` comme concept métier tenant-scoped, sans confondre calendrier, programme et année scolaire.
2. Définir le contrat de liaison d'une période à un calendrier et à une année, en conservant la compatibilité des périodes historiques non classées.
3. Ajouter invariants de dates, cohérence tenant, unicité fonctionnelle et absence de chevauchement au sein d'un même calendrier.
4. Ajouter ports, cas d'usage, adaptateurs SQLite et API ; toutes les routes doivent dériver le tenant du contexte authentifié.
5. Définir l'autorisation métier granulaire (D2-C) avant de remplacer les contrôles actuels.
6. Ajouter tests domaine, repository sur base temporaire, API multi-tenant, accès interdit et cas de concurrence.
7. Ajouter une migration additive seulement après validation des tests sur base temporaire et revue du diff.

## 6. Hors périmètre de cette tranche

- Aucune modification des bases `edunova.db` ou `edunova_dev.db`.
- Aucun backfill automatique des calendriers historiques.
- Aucune valeur réglementaire de programme, matière, coefficient, maximum ou seuil.
- Aucun élargissement de permissions non testé.
- Aucun changement de statut `ACTIVE` vers `OPEN`.
- Aucun passage à PostgreSQL.
