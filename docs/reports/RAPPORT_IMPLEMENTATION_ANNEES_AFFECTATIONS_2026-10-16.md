# EduNova - Implementation controlee des annees et affectations

## Perimetre

Cette tranche implemente les annees scolaires tenant-scoped et les affectations
eleve-classe historisees dans le perimetre d'une base. La decision 45 n'a pas
ete modifiee. La base reelle `edunova.db` n'a pas ete ouverte ni modifiee et la
migration 020 n'y a pas ete executee.

## Etat initial et preservation

Le depot etait deja fortement modifie avant cette mission: fichiers suivis
modifies et nombreux fichiers non suivis, notamment sous `docs/`, `frontend/`,
`src/` et `tests/`. Aucun reset, nettoyage, commit ou push n'a ete effectue.
Les modifications preexistantes ont ete conservees.

## Changements de cette tranche

- `src/academic/domain/entities/academic_year.py`: agregat d'annee scolaire,
  statuts `DRAFT`, `ACTIVE`, `CLOSED`, validation du libelle et transitions
  immuables.
- `src/academic/domain/entities/student_assignment.py`: affectation
  immuable et transitions `DRAFT`, `ACTIVE`, `CLOSED`, `CANCELLED`.
- Interfaces, cas d'utilisation et repositories SQLite pour la creation, la
  lecture tenant-scoped et les changements de statut.
- `src/infrastructure/persistence/migrations/versions/migration_020_school_years_assignments.py`:
  tables additives, cles composites tenant-scoped, index unique d'une seule
  annee active par tenant et d'une seule affectation active par eleve/annee.
- Schemas et routes API `/academic-years` et `/student-assignments`.
- Integration du conteneur et de l'application API.
- `frontend/src/features/enrollments/`: service authentifie et ecran minimal
  de preparation d'annees et d'affectations brouillon.
- Tests d'integration HTTP, tests de domaine et tests du service frontend.

Toutes les routes de cette tranche utilisent le role effectivement disponible
dans le code (`ADMIN`). Les roles direction/promoteur ne sont pas ajoutes sans
un contrat de roles existant.

## Regles appliquees

- Toutes les recherches et mutations exigent le `tenant_id` issu du contexte
  authentifie; le client ne fournit pas le tenant.
- Les references eleve, classe, annee et option sont verifiees dans le meme
  tenant.
- Une option est facultative. Lorsqu'elle est fournie, elle doit appartenir au
  tenant et etre associee a la classe. Aucune obligation supplementaire n'est
  inventee.
- Une affectation active est protegee par contrainte unique. La mise a jour de
  statut utilise un controle compare-et-change sous `BEGIN IMMEDIATE` afin de
  refuser une modification concurrente silencieuse.
- Une affectation fermee ou annulee ne peut pas etre reactivee; une nouvelle
  affectation est necessaire.
- Une annee active unique par tenant est protegee par index partiel.

## Decisions non implementees volontairement

- La decision 45 concernant l'identite et la deduplication reste en attente.
- Le transfert inter-etablissements n'est pas implemente: le depot ne fournit
  pas d'orchestrateur durable ou de transaction distribuee entre bases.
- La route de fermeture d'une annee n'est pas exposee. La politique de
  fermeture des affectations actives lors de la cloture d'une annee reste a
  confirmer; exposer cette action maintenant pourrait produire un etat metier
  ambigu.
- Aucun role direction/promoteur n'est suppose, car les roles actuellement
  reconnus par l'API sont des chaines de membership et les permissions
  existantes utilisent `ADMIN`.

## Tests executes

- `python -m pytest tests/integration/test_school_years_assignments_http.py tests/presentation/test_container.py tests/integration/test_academic_catalogues_http.py -q`
  -> `14 passed in 1.89s`.
- `python -m pytest tests/unit/test_school_year_and_assignment_domain.py tests/integration/test_school_years_assignments_http.py -q`
  -> `6 passed in 0.92s`.
- `python -m mypy` sur les 16 nouveaux modules backend -> `Success: no issues found in 16 source files`.
- `Set-Location F:\EduNova\frontend; npm test -- --run` -> `10 test files,
  41 tests passed`.
- `Set-Location F:\EduNova\frontend; npm run lint` -> succes.
- `Set-Location F:\EduNova\frontend; npm run build` -> succes.
- `git diff --check` -> code `2`: il signale des lignes vides finales dans des
  fichiers preexistants hors de cette tranche (`pyproject.toml`, plusieurs
  tests et `tools/edunova/bootstrap.py`). Les avertissements de conversion de
  fin de ligne concernent egalement des fichiers preexistants. Aucun de ces
  fichiers n'a ete modifie pour cette mission.

Les tests backend utilisent le conteneur en memoire ou des bases de test
gerees par les fixtures. Aucun test n'a vise `edunova.db`.

## Risques residuels

- La migration 020 est additive mais reste a appliquer sur chaque base cible
  via la procedure de migration normale, apres validation et sauvegarde; cette
  operation n'a pas ete executee dans cette mission.
- La transaction d'activation couvre la mise a jour de l'affectation, mais le
  depot ne fournit pas encore une transaction multi-agregats pour coordonner
  une cloture d'annee et des affectations existantes.
- Le parcours frontend est relie aux endpoints, mais aucune validation
  navigateur n'a ete executee dans cette tranche.
- Les transferts inter-etablissements et la politique de fin d'annee exigent
  encore une decision et un mecanisme d'orchestration approprie.

## Conclusion

La tranche intra-etablissement est implementee et couverte par des tests
cibles. Elle est prete pour revue humaine et pour arbitrage des points ouverts,
mais ne constitue pas une livraison complete des transferts inter-
etablissements ni de la cloture d'annee.
