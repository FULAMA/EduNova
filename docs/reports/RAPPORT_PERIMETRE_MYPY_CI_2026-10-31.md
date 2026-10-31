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

## Validation CI

Le workflow GitHub Actions #281, associé au commit `b6ea6a9f4e93584ab036b6551d0cbc3728c50dfc`, est terminé avec la conclusion **success**.

Étapes confirmées réussies :

- Compilation ;
- MyPy sur `src tools/edunova` ;
- Ruff ;
- Bandit ;
- pip-audit (étape non bloquante) ;
- Tests complets ;
- Détection des changements domaine/migrations.

Workflow : https://github.com/FULAMA/EduNova/actions/runs/41250482987

## Protection

- Aucun changement métier, DDD, migration ou base de données.
- Aucune modification de `main`.
- PR #14 maintenue en brouillon jusqu'à revue finale et approbation.
