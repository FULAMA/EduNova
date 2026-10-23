# Audit de robustesse du pipeline qualite - 2026-10-16

## Perimetre

Audit realise sans modification du comportement metier, sans installation,
migration, nettoyage Git, commit ou push. Le worktree etait deja fortement
modifie; ces changements ont ete preserves.

`edunova.db` n'a pas ete utilisee ni modifiee. Sa taille observee reste
`192512` octets, avec la meme date de modification.

## Configuration effective

`ProjectConfig.load()` lit `pyproject.toml` et transmet les chemins
`source_paths = ["src", "tools/edunova"]` a `QualityCommand`.
`QualityCommand` execute dans cet ordre :

1. Ruff sur ces chemins source ;
2. Mypy sur ces memes chemins ;
3. pytest sur `tests`, avec `.pytest-work` controle par le CLI.

Le constructeur Mypy produit effectivement :

```text
python -m mypy src tools/edunova
```

La configuration `[tool.mypy]` contient maintenant
`follow_imports = "skip"`. Cette option ne retire aucune racine projet du
perimetre : les 307 fichiers `src` et `tools/edunova` restent des racines
analysees. Elle empeche seulement le suivi des sources d'imports externes,
dont le fichier `.venv\Lib\site-packages\charset_normalizer\version.py`
contenant 123 octets NUL.

Ce choix ne masque pas les modules du projet: ils font partie des chemins
explicitement transmis a Mypy. Le diagnostic Mypy direct reussit sur les 307
fichiers.

## Commandes executees

Pipeline officiel :

```text
.venv\Scripts\python.exe -m tools.edunova quality
Quality checks passed.
```

Mypy direct :

```text
.venv\Scripts\python.exe -m mypy src tools/edunova
Success: no issues found in 307 source files
```

Tests de configuration et de commande qualite :

```text
20 passed in 0.77s
```

Ruff global :

```text
Found 21 errors.
```

`git diff --check` a ete execute. Il signale des lignes vides finales dans
plusieurs fichiers deja modifies du worktree, dont `pyproject.toml`; aucune
nouvelle erreur de contenu specifique au changement Mypy n'a ete observee.

## Ruff global

Les 21 diagnostics sont les memes que ceux des rapports precedents :

- `F401` dans `tests/integration/test_academic_catalogue_repository.py` ;
- `E402` et `F401` dans `tests/unit/domain/services/test_subject_average_calculator.py` ;
- `F811` dans `tests/unit/infrastructure/config/test_settings.py` ;
- `F401`, `E402` et `F811` dans les tests d'agents ;
- `F401` dans `tests/unit/tools/edunova/test_bootstrap_agent.py`.

Aucune erreur Ruff n'est apparue dans `pyproject.toml`, `container.py` ou les
fichiers du pipeline. La commande officielle n'applique pas Ruff a `tests`;
les 21 erreurs sont donc une dette hors du perimetre Ruff officiel, mais
restent visibles avec `ruff check src tests`.

## Fichiers modifies

- `pyproject.toml` : configuration Mypy `follow_imports = "skip"`, changement
  preexistant a cette mission et audite ici ;
- `docs/reports/RAPPORT_AUDIT_ROBUSTESSE_PIPELINE_2026-10-16.md` : ce rapport.

Aucun fichier de production ou test n'a ete modifie pendant cet audit.

## Limites et risques residuels

- Le pipeline officiel est vert pour son perimetre configure.
- Ruff global reste non vert avec 21 erreurs historiques.
- `follow_imports = "skip"` reduit l'analyse des implementations de
  dependances externes; il ne remplace pas une verification de leurs versions
  ou de leur integrite.
- `git diff --check` global reste bruite par des fins de fichier preexistantes.

## Verdict

**VALIDÉ AVEC RÉSERVES** : le pipeline officiel est reproductible et fiable
sur son perimetre configure; la dette Ruff globale et les artefacts de diff
preexistants restent a traiter separement.
