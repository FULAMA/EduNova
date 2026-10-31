# Périmètre MyPy de la CI EduNova — 2026-10-31

## Constat

La configuration du projet et la documentation de la CLI EduNova définissent deux racines de code à vérifier par MyPy : `src` et `tools/edunova`.

La CI GitHub exécutait cependant uniquement :

```text
mypy --explicit-package-bases src
```

Cette commande ne vérifiait donc pas le code de la CLI d'ingénierie dont les doubles de test sont concernés par la PR.

## Correction appliquée

Le workflow `.github/workflows/edunova-ci.yml` exécute désormais :

```text
mypy --explicit-package-bases src tools/edunova
```

Cela aligne le contrôle MyPy CI sur le périmètre documenté de la commande qualité du projet.

## Périmètre des tests

Les tests ne sont volontairement pas ajoutés au périmètre MyPy dans ce changement. La CI conserve :

- Ruff sur `src tests` ;
- MyPy sur `src tools/edunova` ;
- pytest sur la suite complète.

Le typage des tests et des doubles fera l'objet d'une décision séparée, après analyse du volume d'erreurs et de la valeur de cette contrainte. Il ne faut pas confondre le passage des tests pytest avec une vérification MyPy des fichiers de tests.

## Validation

- Modification publiée sur la branche `fix/mypy-test-double-contracts`.
- Exécution CI déclenchée par le push : résultat à vérifier dans GitHub Actions.
- Aucune exécution MyPy distante n'est considérée comme réussie tant que le workflow n'a pas terminé.
- Les 505 tests locaux communiqués par le propriétaire du dépôt restent un résultat distinct.

## Protection

- Aucun changement métier, DDD, migration ou base de données.
- Aucune modification de `main`.
- PR #14 maintenue en brouillon jusqu'à validation CI et revue finale.
