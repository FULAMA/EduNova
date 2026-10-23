# EduNova - Audit du domaine scolaire avant inscription

Date : 2026-10-16
Statut : lecture seule, aucune implementation lancee

## Etat initial

Le depot etait deja fortement modifie avant cet audit. `git status --short`
montre de nombreuses modifications suivies et non suivies dans `src/`, `tests/`,
`frontend/` et `docs/`. Rien n'a ete supprime, reinitialise ou nettoye.

Le rapport de reference est `docs/reports/RAPPORT_CLASSES_INSCRIPTION_2026-10-16.md`.
Les migrations n'ont pas ete executees et `edunova.db` n'a pas ete ouverte en
ecriture ni modifiee. Aucune dependance n'a ete installee.

## Reponses aux questions

### 1. Existe-t-il une entite eleve ?

**Partiellement.** Il existe une table et un modele de lecture, mais pas
d'entite de domaine `Student` avec invariants ou comportement metier.

- `src/academic/application/dto/student_summary.py:6` definit `StudentSummary`.
- `src/academic/application/interfaces/student_repository.py:7-17` expose
  seulement `list_by_tenant` et `get_by_id_and_tenant`.
- `src/infrastructure/repositories/sqlite_student_repository.py:10-61`
  implemente ces lectures avec `WHERE tenant_id = ?`.
- `src/presentation/api/routes/students.py:19-64` expose liste et detail,
  reserves au role `ADMIN`.
- `src/infrastructure/persistence/migrations/versions/migration_009_students_tenant.py:43-50`
  definit les colonnes de `students`.

### 2. Existe-t-il une annee ou une periode reutilisable ?

**Periode : oui. Annee scolaire : non trouvee dans le code livre.**

- `src/academic/domain/entities/academic_period.py:6-30` definit
  `AcademicPeriod` avec tenant, nom, dates et ordre des dates.
- `src/academic/application/interfaces/academic_period_repository.py` et
  `src/infrastructure/repositories/sqlite_academic_period_repository.py`
  fournissent la lecture tenant-scoped.
- `src/infrastructure/persistence/migrations/versions/migration_017_academic_catalogues.py:10-24`
  cree `academic_periods` avec cle `(tenant_id, id)`.
- Aucune classe, interface, repository, table ou migration `AcademicYear` ou
  `school_year` n'a ete trouvee.
- `docs/v1/CONTRATS_METIER_V1.md:21-24` decrit `AcademicYear` comme modele
  **propose**, pas comme implementation.
- La decision 10 du registre (`docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md:67-70`)
  impose de distinguer annee scolaire, periodes academiques et periodes
  d'evaluation, sans inventer le modele officiel.

### 3. Comment les classes sont-elles rattachees a un etablissement ?

`AcademicClass` est une dataclass immutable identifiee par `id` et `tenant_id`.
Elle porte un nom et `active`.

- `src/academic/domain/entities/academic_class.py:5-17` verifie tenant non nul
  et nom non vide.
- `src/infrastructure/persistence/migrations/versions/migration_002_academic_classes_tenant.py:42-47`
  cree `academic_classes(id, tenant_id, name)`.
- `src/infrastructure/repositories/sqlite_academic_class_repository.py`
  persiste et lit les classes, et `list_by_tenant` filtre le tenant.
- `src/presentation/api/routes/classes.py:31-47` expose la consultation avec
  `get_tenant_context` et `require_role("ADMIN")`.

Les options et associations sont aussi tenant-scoped :
`AcademicOption` (`academic_option.py:5-21`), `ClassOption`
(`class_option.py:5-15`) et migration 005 (`:43-53`).

**Limites demontrees :** la classe n'a ni niveau ni annee scolaire ; l'option
est une association separee. L'unicite du nom de classe n'est pas imposee.

### 4. Existe-t-il une relation eleve-classe ?

**Non trouvee.**

- `src/infrastructure/persistence/database.py:211-222` montre que `students`
  ne contient ni classe ni annee.
- Les migrations 001 a 019 inspectees ne creent aucune table d'inscription,
  d'affectation ou de transfert eleve-classe.
- `src/academic/application/use_cases/assign_subject_to_class.py:20-101`
  affecte une matiere a une classe ; ce n'est pas une inscription d'eleve.
- Aucun use case, port ou endpoint d'inscription n'a ete trouve.

### 5. L'historique des changements de classe est-il conserve ?

**Non.** La migration 019 (`migration_019_academic_record_history.py:10-32`)
historise les dossiers academiques, pas les affectations scolaires. Les
versions de `StudentAcademicRecord` concernent uniquement les resultats.

La decision 12 du registre exige pourtant provenance et historique pour les
transferts ; aucune implementation correspondante n'a ete trouvee.

### 6. Quelles regles d'inscription et de doublons existent ?

Regles etablies : isolation tenant et portee (decision 13), provenance et
historique des transferts (decision 12), distinction annee/periodes (decision
10). La decision 45 sur l'identification et les doublons est **EN ATTENTE**.

Non demontrees pour une inscription : une affectation active par eleve/annee,
dates d'effet, compatibilite option-classe-eleve, transfert, fusion ou
deduplication. Les contraintes de doublon observees concernent seulement la
configuration, par exemple `UNIQUE(academic_class_id, academic_option_id)` en
migration 005 et les matieres d'une classe.

### 7. Decisions restantes du proprietaire

Il faut valider :

1. le modele et le calendrier de l'annee scolaire ;
2. la cardinalite des annees ouvertes et les roles autorises ;
3. le modele d'affectation, ses dates, statuts et transferts ;
4. la regle d'une affectation active par eleve et annee ;
5. les champs obligatoires du formulaire ;
6. la strategie de doublon de la decision 45 ;
7. les roles de creation, modification, transfert et consultation.

Les points 1 et 2 sont aussi listes comme decisions requises dans
`docs/v1/CONTRATS_METIER_V1.md:50-55`.

### 8. Lacunes DDD demontrees

- Le contexte academique gere la configuration, mais pas l'aggregate
  d'inscription.
- L'eleve est un DTO de lecture et non un modele metier complet.
- `AcademicPeriod` n'est rattache a aucune `AcademicYear`.
- Les contraintes tenant existent sur les tables actuelles, mais aucune ne
  peut garantir l'integrite d'une affectation inexistante.
- Le frontend ne fait que consulter les classes :
  `frontend/src/app/router/routes.tsx:45-48` et
  `frontend/src/features/classes/ClassesPage.tsx:15-71`.

Ces constats sont des contrats manquants, pas la preuve d'une violation d'une
regle d'inscription deja implementee.

## Cartographie

| Composant | Responsabilite | Etat |
| --- | --- | --- |
| `AcademicClass` | nom, tenant, activation | implemente, invariants minimaux |
| `AcademicOption` | nom, code, tenant | implemente, partiel |
| `AcademicPeriod` | periode datee tenant | implemente, sans annee |
| `ClassOption` / `ClassSubject` | configuration de classe | implemente |
| `StudentSummary` | lecture d'un eleve | partiel, pas d'entite metier |
| `StudentAcademicRecord` | resultats versionnes | implemente, hors affectation |
| repositories SQLite | persistance des composants existants | implemente selon contrat |
| routes students/classes | consultation et matieres | partiel |
| frontend students/classes | consultation | partiel |

La separation domaine/application/infrastructure/presentation est visible,
mais une affectation necessitera un port, un modele explicite, un repository,
des contraintes SQLite et des routes reutilisant tenant et role.

## Risques

- **Eleve : eleve.** Inventer un matricule ou une fusion avant decision 45
  pourrait confondre deux personnes.
- **Historique : eleve.** Ne conserver que la classe courante perdrait les
  transferts, contrairement a la decision 12.
- **Annee/periode : eleve.** Utiliser une periode comme annee violerait la
  distinction de la decision 10.
- **Tenant : eleve.** Une reference simple vers `students.id` ne prouverait
  pas la coherence tenant ; le precedent a reutiliser est la cle composee
  `(tenant_id, id)`.
- **Autorisation : moyen.** Les routes actuelles sont ADMIN-only ; les roles
  d'inscription restent a confirmer.

## Tests requis pour la prochaine tranche

Sur base temporaire uniquement :

1. annee et periodes rattachees ;
2. refus periode hors tenant ou hors annee ;
3. affectation valide avec date d'effet ;
4. refus des references cross-tenant ;
5. refus de deux affectations actives pour le meme eleve et annee ;
6. transfert avec historique conserve ;
7. concurrence ou conflit de version si retenu ;
8. permissions et refus 401/403 ;
9. doublons selon la decision 45 apres validation ;
10. frontend : chargement, vide, erreurs, double soumission et confirmation
    seulement apres succes API.

## Ordre minimal recommande

1. Faire approuver annee, affectation/transfert et decision 45.
2. Implementer `AcademicYear` et ses ports, sans confondre `AcademicPeriod`.
3. Implementer l'affectation tenant-scoped, son historique et ses contraintes.
4. Ajouter use cases, autorisations et API.
5. Ajouter le formulaire frontend et ses etats.
6. Valider HTTP/frontend sur donnees synthetiques.

## Faits verifies

- Classes, options, periodes, matieres et associations de configuration existent.
- Eleves et classes sont lus avec filtre tenant.
- Les routes de consultation exigent actuellement `ADMIN`.
- Les migrations 002, 004, 005, 009 et 017 couvrent les donnees existantes ;
  019 couvre l'historique des dossiers academiques.
- Aucun modele ou stockage d'inscription eleve-classe n'a ete trouve.
- Decision 10 validee ; decision 45 en attente.

## Inconnues restantes

Modele officiel de l'annee, roles d'inscription, champs obligatoires, statuts,
dates d'effet, transferts et strategie de doublon.

## Prochaine tranche et criteres

La prochaine tranche recommandee est la validation du contrat metier
`AcademicYear` + affectation, avant le formulaire frontend.

Elle sera validee lorsque les decisions seront approuvees, que le schema
temporaire preserve tenant/annee/eleve/classe/option/historique, que les tests
multi-tenant, permissions, doublons et concurrence passent, et qu'aucun test
n'a utilise `edunova.db`.
