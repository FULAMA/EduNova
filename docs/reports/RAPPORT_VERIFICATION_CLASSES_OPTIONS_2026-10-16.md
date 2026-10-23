# EduNova - Verification tenant-scoped des classes et options

Date : 2026-10-16

## Fichiers inspectes

- `src/academic/application/interfaces/academic_class_repository.py`
- `src/infrastructure/repositories/sqlite_academic_class_repository.py`
- `src/presentation/api/routes/classes.py`
- `src/presentation/api/dependencies/auth.py`
- `src/academic/domain/entities/academic_class.py`
- `src/academic/domain/entities/academic_option.py`
- `src/academic/domain/entities/class_option.py`
- `src/academic/domain/entities/class_subject.py`
- `frontend/src/features/classes/ClassesPage.tsx`
- `frontend/src/features/classes/classes.service.ts`
- repositories SQLite, migrations et tests associes.

## Resultats

### Lecture des classes

`SQLiteAcademicClassRepository.list_by_tenant` execute une requete avec
`WHERE tenant_id = ?` et recoit le tenant depuis `ListAcademicClasses`.
L'endpoint `GET /classes` obtient ce tenant par `get_tenant_context` et ne
lit aucun tenant fourni dans la requete ou le corps.

La route est protegee par `require_role("ADMIN")`, qui verifie a la fois le
token, le membership actif et le role du membership dans le tenant. Le client
frontend appelle uniquement `/classes` avec `authenticated: true`.

### Relations options et matieres

`AcademicOption`, `ClassOption` et `ClassSubject` portent un `tenant_id`.
Les repositories et `AssignSubjectToClass` verifient les classes, matieres et
associations avec le tenant courant. Une classe ou une association d'un autre
tenant n'est donc pas retournee par ces lectures.

La relation `ClassOption` ne permet pas de conclure qu'une option est
obligatoire. Aucun changement n'a ete apporte a cette regle, qui reste a
arbitrer.

### Cas inconnus et erreurs

La lecture par identifiant du repository retourne `None` si la classe est
inconnue ou si son tenant ne correspond pas. Le cas d'utilisation existant
transforme alors l'absence en erreur metier pour l'affectation de matiere,
sans exposer les donnees de l'autre tenant.

La page frontend traite le chargement, l'etat vide, les erreurs API 401/403,
l'indisponibilite reseau et la reprise. Elle n'accepte ni tenant ni option
depuis l'interface.

## Tests executes

- `python -m pytest tests/integration/test_sqlite_academic_class_repository.py tests/integration/test_sqlite_class_option_repository.py tests/integration/test_sqlite_class_subject_repository.py tests/integration/test_sqlite_class_subject_integrity.py tests/integration/test_assign_subject_http_sqlite.py tests/integration/test_authorization_http.py tests/integration/test_students_http.py tests/presentation/test_api_hardening.py -q`
  : **47 passed in 5.04s**.
- `npm test -- --run src/features/classes/classes.service.test.ts` depuis
  `frontend/` : **1 test file, 1 test passed**.
- `npm run lint` depuis `frontend/` : **reussi**.

Les tests utilisent des bases SQLite de test ou en memoire. Aucun test n'a
utilise `edunova.db`. Aucune migration n'a ete executee.

## Corrections

Aucun defaut reproductible n'a ete confirme. Aucun fichier de code n'a donc
ete modifie et aucun nouveau test n'etait justifie par un regression.

Le worktree comporte toujours de nombreuses modifications preexistantes et
fichiers non suivis. Seul ce rapport est ajoute pour cette verification.

## Risques residuels

- L'endpoint de consultation est actuellement reserve a `ADMIN`; aucun role
  direction/promoteur n'a ete ajoute sans arbitrage.
- Il n'existe toujours pas de modele d'annee scolaire, d'inscription ou
  d'affectation historisee.
- Les repositories d'options et de matieres doivent continuer a recevoir le
  tenant dans toute future route d'ecriture.
- La regle d'option obligatoire reste indeterminee.
- La couverture directe de `GET /classes` par un test HTTP dedie pourrait etre
  ajoutee dans une tranche ulterieure, sans que l'audit ait demontre une fuite.

## Verdict

**VALIDE AVEC RESERVES**

Les lectures existantes sont tenant-scoped et les controles d'autorisation
restent effectifs. Les reserves concernent uniquement les modeles et decisions
metier encore absents du perimetre, pas une fuite de donnees demontrable dans
la tranche verifiee.
