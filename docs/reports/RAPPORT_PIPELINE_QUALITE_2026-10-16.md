# Finalisation du pipeline qualite - 2026-10-16

## Diagnostic

Les racines envoyees par `QualityCommand` sont `src` et `tools/edunova`,
conformement a `[tool.edunova].source_paths`. `.venv` n'etait donc pas un
chemin explicite du projet. Le fichier tiers corrompu etait atteint par le
suivi des imports externes de Mypy.

Le fichier `.venv\Lib\site-packages\charset_normalizer\version.py` contient
123 octets NUL. Il n'a pas ete modifie.

## Correction

Ajout dans `[tool.mypy]` de :

```toml
follow_imports = "skip"
```

Cette option ne retire pas `src` ni `tools/edunova` du perimetre. Ces racines
restent analysees; seules les implementations importees depuis les
dependances externes ne sont plus suivies jusqu'a leurs fichiers sources.
La commande conserve donc la verification du code du projet.

Aucune dependance n'a ete installee et `container.py` n'a pas ete modifie dans
cette mission; sa correction Mypy precedente a ete preservee.

## Commandes et resultats

Mypy sur le perimetre attendu :

```text
.venv\Scripts\python.exe -m mypy src tools/edunova
Success: no issues found in 307 source files
```

Tests de la commande qualite et de la configuration :

```text
20 passed in 0.87s
```

Commande officielle :

```text
.venv\Scripts\python.exe -m tools.edunova quality
Quality checks passed.
```

La commande officielle a donc execute Ruff sur les chemins source, Mypy sur
les 307 fichiers projet, puis pytest selon la configuration.

## Ruff

`ruff check src tests` reproduit toujours 21 erreurs historiques :

- `F401` imports inutilises dans `tests/integration/test_academic_catalogue_repository.py` ;
- `E402` et `F401` dans `tests/unit/domain/services/test_subject_average_calculator.py` ;
- `F811` dans `tests/unit/infrastructure/config/test_settings.py` ;
- `F401`, `E402` et `F811` dans les tests d'agents sous
  `tests/unit/tools/edunova/agents/` ;
- `F401` dans `tests/unit/tools/edunova/test_bootstrap_agent.py`.

Le Ruff de la commande officielle reste vert, car le pipeline qualite analyse
les chemins source configures et pytest execute les tests sans appliquer Ruff
aux tests. Les 21 diagnostics restent une dette distincte a traiter par lots,
sans suppression d'assertions ni reformatage global.

## Protection et diff

- `edunova.db` n'a pas ete utilisee ni modifiee ; taille observee : `192512`
  octets.
- Aucun nettoyage, reset, migration, installation, commit, push ou
  deploiement n'a ete effectue.
- `git diff --check` global signale des lignes vides finales dans plusieurs
  fichiers preexistants; le changement Mypy ne produit pas de nouvelle erreur
  de contenu.
- Les nombreuses modifications suivies et non suivies du worktree ont ete
  preservees.

## Fichier modifie par cette mission

- `pyproject.toml` : configuration Mypy `follow_imports = "skip"`.
- `docs/reports/RAPPORT_PIPELINE_QUALITE_2026-10-16.md` : ce rapport.

## Statut

Le pipeline qualite officiel est vert. Le controle Ruff global incluant les
tests reste non vert avec 21 erreurs historiques, qui ne sont pas masquees par
la correction du pipeline.
