# EduNova - Classes et inscription des élèves

## Périmètre réalisé

L'inspection a confirmé que le dépôt contient déjà `AcademicClass`,
`AcademicOption`, `ClassOption`, `ClassSubject`, leurs migrations tenant-scoped
et une route d'affectation de matières aux classes. Le dépôt ne contient pas,
en revanche, de modèle d'année scolaire ni de table/use case d'affectation
élève-classe.

La tranche livrée reste donc volontairement limitée à la consultation des
classes existantes :

- repository `list_by_tenant`, avec filtre tenant et tri stable ;
- use case `ListAcademicClasses` ;
- endpoint authentifié `GET /classes`, réservé au rôle `ADMIN` ;
- page frontend `/app/classes`, avec chargement, état vide, erreur et reprise ;
- appel frontend explicitement authentifié ;
- test de non-mélange entre tenants.

## Décision de périmètre

Le formulaire d'inscription n'a pas été implémenté. Une implémentation serait
incohérente avec le modèle actuel, car aucune relation élève-classe historisée
et aucune année scolaire ne sont persistées. Ajouter arbitrairement ces champs
ou décider d'une règle d'inscription contournerait les décisions métier
existantes, notamment la décision 10 sur les modèles scolaires et la décision
45 encore en attente sur l'identification/déduplication.

Les règles suivantes restent donc à décider ou à modéliser avant la suite :

- définition officielle de l'année scolaire et son lien avec une affectation ;
- relation d'inscription élève-classe, avec une seule affectation active par
  élève et année ;
- stratégie d'historisation et de transfert ;
- champs obligatoires du formulaire et règles de dédoublonnage.

## Fichiers ajoutés ou modifiés pour cette tranche

- `src/academic/application/interfaces/academic_class_repository.py` : ajout
  du contrat de lecture par tenant.
- `src/infrastructure/repositories/sqlite_academic_class_repository.py` :
  lecture tenant-scoped triée.
- `src/academic/application/use_cases/list_academic_classes.py` : use case
  applicatif minimal.
- `src/presentation/api/schemas/academic_class.py` : réponse API publique sans
  exposer de données d'un autre tenant.
- `src/presentation/api/dependencies/__init__.py` et
  `src/presentation/api/container.py` : branchement DI.
- `src/presentation/api/routes/classes.py` et `src/presentation/api/app.py` :
  endpoint `GET /classes`, avec authentification, rôle et contexte tenant.
- `tests/integration/test_sqlite_academic_class_repository.py` : test de tri et
  d'isolation tenant.
- `frontend/src/features/classes/classes.service.ts` : client API authentifié.
- `frontend/src/features/classes/ClassesPage.tsx` : consultation frontend.
- `frontend/src/features/classes/classes.service.test.ts` : contrat du client.
- `frontend/src/app/router/routes.tsx` : route `/app/classes`.

Le dépôt était déjà fortement modifié avant cette mission, avec notamment de
nombreux fichiers suivis modifiés et des fichiers non suivis dans `frontend/`,
`docs/`, `src/` et `tests/`. Ces changements ont été préservés.

## Contrôles exécutés

- `python -m pytest tests/integration/test_sqlite_academic_class_repository.py tests/presentation/test_container.py tests/integration/test_assign_subject_http_sqlite.py -q`
  : **13 passed**.
- `python -m mypy` sur les fichiers backend concernés : **Success: no issues
  found in 7 source files**.
- `python -m ruff check` sur les fichiers backend concernés : **aucune erreur**.
- `npm test -- --run src/features/classes/classes.service.test.ts` depuis
  `frontend/` : **1 test file, 1 test passed**.
- `npm run lint` depuis `frontend/` : **réussi**.
- `npm run build` depuis `frontend/` : **réussi**, build Vite terminé.
- `git diff --check` : des erreurs de lignes blanches finales préexistantes
  sont signalées dans plusieurs fichiers non liés ; aucune correction globale
  n'a été appliquée.

Une première commande `npm` a été lancée par erreur depuis `F:\EduNova` et a
échoué uniquement parce que ce répertoire ne contient pas `package.json`. Les
contrôles frontend ont ensuite été relancés depuis `F:\EduNova\frontend` et
ont réussi.

## Sécurité et limites

- Aucune migration n'a été exécutée.
- `edunova.db` n'a pas été ouverte ni modifiée.
- Aucun parallélisme, commit, push, reset, nettoyage ou installation de
  dépendance n'a été effectué.
- L'endpoint de classes reste limité au rôle `ADMIN` et utilise le tenant issu
  du contexte d'authentification ; le repository filtre également par tenant.
- Aucun test navigateur n'a été exécuté.
- La création de classe et l'inscription restent hors de cette tranche : le
  contrat de création et les règles de rattachement à une année scolaire ne
  sont pas établis dans le code actuel.

## Statut

**VALIDATION PARTIELLE**

La consultation des classes existantes est livrée et testée. La fonctionnalité
complète « formulaire d'inscription » nécessite d'abord une décision métier et
un modèle persistant explicite pour l'année scolaire et l'historique des
affectations.
