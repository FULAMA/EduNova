# Rapport qualite statique et fiabilite - 2026-10-16

## Perimetre

Le worktree etait deja fortement modifie avant cette mission. Aucun reset,
nettoyage, suppression, installation, commit ou push n'a ete effectue.
`edunova.db` n'a pas ete utilisee ni modifiee et le registre metier n'a pas
ete touche.

## Mypy

La configuration declare les chemins projet `src` et `tools/edunova` dans
`[tool.edunova].source_paths`. La commande officielle construit donc :

```text
python -m mypy src tools/edunova
```

`.venv` n'est pas un chemin d'analyse configure. Mypy le lit indirectement
en suivant un import externe. Le fichier
`.venv\Lib\site-packages\charset_normalizer\version.py` contient 123 octets
NUL; il n'a pas ete modifie.

Avant correction :

```text
container.py:122: Argument 2 to "seed_development_data" has incompatible type
"str | None"; expected "str"
```

La configuration `Settings` valide deja que le mot de passe existe lorsque
le seed est active, mais son type reste optionnel pour representer le seed
desactive. `ApplicationContainer` narrait cette precondition sans la
materialiser pour Mypy.

Correction locale dans `src/presentation/api/container.py` : lorsque le seed
est active, la valeur est verifiee localement puis transmise comme `str`. Le
comportement de production et le contrat `Settings` restent inchanges.

Apres correction, Mypy direct sur le perimetre attendu avec le suivi des
imports externes neutralise pour le diagnostic de l'environnement retourne :

```text
Success: no issues found in 307 source files
```

La commande officielle `python -m tools.edunova quality` reste en echec avant
l'analyse du projet sur le fichier `.venv` corrompu. Aucun contournement n'a
ete ajoute a la configuration du projet.

## Ruff

`ruff check src tests` reproduit 21 erreurs, toutes dans des tests hors du
correctif Mypy :

- `tests/integration/test_academic_catalogue_repository.py:1:22` : `F401`
  (`datetime.date`) ;
- `tests/unit/domain/services/test_subject_average_calculator.py:85:1` :
  `E402`, et ligne 85:58 `F401` (`ScoreConverter`) ;
- `tests/unit/infrastructure/config/test_settings.py:84:5` : `F811`,
  doublon de `test_development_jwt_secret_is_stable` ;
- `tests/unit/tools/edunova/agents/test_agent_command.py` : trois `F401` ;
- `tests/unit/tools/edunova/agents/test_context_provider.py` : un `F401` ;
- `tests/unit/tools/edunova/agents/test_context_scanner.py` : un `F401` ;
- `tests/unit/tools/edunova/agents/test_context_scanner_architecture.py` :
  deux `E402` et un `F811` ;
- `tests/unit/tools/edunova/agents/test_conversational_agent.py` : un `F401` ;
- `tests/unit/tools/edunova/agents/test_executor.py` : deux `F401` ;
- `tests/unit/tools/edunova/agents/test_groq_adapter.py` : un `F401` ;
- `tests/unit/tools/edunova/agents/test_health_tracker.py` : un `F401` ;
- `tests/unit/tools/edunova/agents/test_orchestrated_agent_command.py` : un
  `F401` ;
- `tests/unit/tools/edunova/agents/test_provider_factory_registry.py` : deux
  `F401` ;
- `tests/unit/tools/edunova/test_bootstrap_agent.py` : un `F401`.

Le controle Ruff cible sur `src/presentation/api/container.py` et son test
de seed passe. Aucun des 21 diagnostics n'est dans la correction de cette
mission; ils sont conserves comme dette technique historique.

## Tests executes

Tests lies au correctif :

```text
18 passed in 1.34s
```

Ce groupe couvre le seed, la configuration, la commande qualite et les
en-tetes API.

Controles post-correction :

- Mypy direct : succes sur 307 fichiers ;
- Ruff cible : succes ;
- Ruff global : 21 erreurs historiques ;
- qualite CLI officielle : echec sur le fichier `.venv` contenant des NUL.

`git diff --check` sur `container.py` ne signale aucune erreur de contenu,
hors avertissement de conversion de fins de ligne Git deja present dans le
worktree.

## Fichiers modifies par cette mission

- `src/presentation/api/container.py` : narrowing explicite du mot de passe
  du seed avant appel du bootstrap ;
- `docs/reports/RAPPORT_QUALITE_STATIQUE_2026-10-16.md` : ce rapport.

Les autres modifications du worktree sont preexistantes et ont ete
preservees.

## Actions suivantes

1. Reparer l'installation de `charset-normalizer` dans l'environnement virtuel
   ou reconstruire `.venv`, sans modifier le fichier binaire manuellement.
2. Relancer `python -m tools.edunova quality` apres cette operation.
3. Traiter les 21 erreurs Ruff par lots separes, sans melanger la dette des
   tests avec le correctif Mypy.

## Statut

Le probleme Mypy du code projet est corrige et verifie. Les controles qualité
globaux ne sont pas tous verts : la commande officielle reste bloquee par la
dependance `.venv` corrompue et Ruff conserve 21 erreurs preexistantes.
