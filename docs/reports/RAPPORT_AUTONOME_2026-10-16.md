# Rapport autonome EduNova — 2026-10-16

## A. Résumé exécutif

La branche `main` était déjà fortement modifiée avant cette mission. Le registre métier existe et confirme les règles de versionnement académique, de traçabilité, d'isolation tenant et de publication contrôlée. La décision 45 sur l'identification des personnes et les doublons reste `EN ATTENTE`.

Le problème « Backend inaccessible » était partiellement trompeur : le endpoint `/health` répondait, mais le factory FastAPI ignorait `EDUNOVA_DATABASE_PATH` lorsque son défaut `:memory:` était utilisé. Une correction locale a été appliquée pour que le factory lise cette variable, sans changer le comportement mémoire lorsque la variable est absente.

Résultat final : correction vérifiée sur une base temporaire, tests ciblés passants, frontend validé par tests/lint/build. La suite qualité complète reste non verte à cause de l'environnement Mypy et d'erreurs Ruff préexistantes dans des tests.

## B. État Git

- Branche : `main`.
- Nombreux fichiers suivis modifiés avant la mission.
- Nombreux fichiers non suivis préexistants, notamment artefacts `.pytest-*`, `frontend`, extensions CLI, migrations et rapports.
- Aucun reset, nettoyage, commit, push ou suppression massive effectué.
- Le registre `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md` n'a pas été modifié.
- `edunova.db` n'a pas été ouvert en écriture et aucune entrée Git ne signale sa modification.

## C. Problème backend/frontend

### Cause confirmée

`src/presentation/api/app.py:create_app()` utilisait `:memory:` par défaut et transmettait directement ce chemin à `ApplicationContainer`. Une exécution Uvicorn avec `EDUNOVA_DATABASE_PATH` répondait donc à `/health`, mais ne créait pas la base au chemin configuré.

### Correctif

Lorsque `database_path == ":memory:"`, le factory consulte désormais `EDUNOVA_DATABASE_PATH`. Sans cette variable, le comportement mémoire reste inchangé pour les tests.

### Vérification isolée

Commande exécutée via un sous-processus temporaire Uvicorn :

```powershell
python -m uvicorn src.presentation.api.app:create_app --factory --host 127.0.0.1 --port 8028
```

Variables utilisées uniquement dans le sous-processus : environnement `test`, chemin SQLite temporaire, secret local de test et origine CORS locale.

Résultat observé :

- `isolated_health=200`
- `isolated_db_exists=True`
- `process_stopped=True`

La base temporaire a été utilisée ; `edunova.db` n'a pas été utilisée.

## D. Sécurité et architecture

### Vérifications

- Les routes académiques utilisent le contexte tenant issu du JWT.
- Les contrôles `ADMIN` et membership actif sont présents sur le périmètre actuel.
- Les tests négatifs multi-tenant existent pour étudiants, catalogues et dossiers.
- Les corrections académiques utilisent `expected_version`.
- Les politiques métier validées du registre n'ont pas été modifiées.

### Risques restant ouverts

- Les appels legacy à `save(record)` peuvent contourner le contrôle de version.
- L'historique académique ne contient pas encore systématiquement l'auteur et le motif exigés par le registre.
- La politique académique n'est pas persistée ni associée à chaque calcul.
- `AcademicPolicy.minimum_subject_average` vaut `8`, tandis que `StudentAcademicRecord` utilise encore `< 10` pour compter les matières échouées.
- Finance, publication, notifications et synchronisation hors ligne ne sont pas livrés comme parcours complets.

## E. Tests et contrôles

### Contrôles passants

- `python -m pytest -q --basetemp=F:\EduNova\.pytest-night-audit-target ...` : `49 passed`.
- `pytest` ciblé après correction factory et contrats API : `17 passed`.
- `ruff check` sur les fichiers modifiés de cette mission : succès.
- `python -m tools.edunova --help` : succès, commandes affichées.
- `python -m tools.edunova security` : Bandit réussi.
- Frontend `npm run lint` : succès.
- Frontend `npm run test -- --run` : `8` fichiers, `38` tests passants.
- Frontend `npm run build` : succès Vite/TypeScript.

### Contrôles non verts

- `python -m tools.edunova quality` : échec Mypy avant analyse du projet, sur `.venv\Lib\site-packages\charset_normalizer\version.py` contenant des octets NUL.
- `mypy --explicit-package-bases src` : même blocage environnemental.
- `ruff check src tests` : `21` erreurs, principalement dans des tests préexistants non liés au correctif factory.

Aucune dépendance n'a été installée ou mise à jour.

## F. Modifications de cette mission

### `src/presentation/api/app.py`

Le factory utilise `EDUNOVA_DATABASE_PATH` uniquement quand son chemin par défaut est `:memory:`. Cela corrige le lancement Uvicorn par factory sans modifier les conteneurs injectés ni les tests mémoire explicites.

### `tests/presentation/test_factory_database_config.py`

Nouveau test de régression vérifiant qu'un chemin temporaire configuré par environnement est réellement créé.

### `tests/presentation/test_api.py`

Adaptation du faux repository et des assertions au contrat académique actuel incluant `status` et `version`.

### `tests/unit/shared/application/events/test_subject_result_event_flow.py`

Adaptation du faux repository à la signature étendue de `save()`, sans changement du comportement testé.

### `docs/reports/RAPPORT_AUTONOME_2026-10-16.md`

Rapport de reprise créé selon la mission. Le registre métier officiel n'a pas été modifié.

## G. Décisions en attente

- Décision 45 : choisir une stratégie officielle d'identification et de prévention des doublons.
- Définir les valeurs numériques de la politique académique par établissement.
- Définir la politique persistée, sa version et sa date d'application.
- Définir l'auteur et le motif obligatoires des corrections dans le modèle technique.
- Définir les règles de crédits avant toute implémentation, bien qu'elles soient hors pilote.

Aucune de ces décisions n'a été choisie ou modifiée automatiquement.

## H. Prochaines actions

### P0

- Aligner le calcul des matières échouées sur la politique validée, après confirmation de la valeur officielle.
- Ajouter auteur, motif et politique versionnée aux calculs et corrections.
- Fermer les chemins legacy de sauvegarde non conditionnels.

### P1

- Implémenter l'année scolaire et les périodes selon les décisions du registre.
- Construire le workflow de délibération versionnée et de publication.
- Ajouter les tests de migration `019` et les contrats de chaîne jusqu'à `019`.

### P2

- Corriger les erreurs Ruff des tests existants par lots séparés.
- Réparer l'environnement Mypy ou exclure proprement les dépendances externes corrompues sans masquer les erreurs du projet.

### P3

- Préparer les domaines finance, notifications et hors ligne seulement après validation de leurs contrats métier.

## I. Procédure de reprise

```powershell
Set-Location F:\EduNova
git status --short
Get-Content docs\reports\RAPPORT_AUTONOME_2026-10-16.md
```

Tests backend ciblés :

```powershell
python -m pytest -q --basetemp=F:\EduNova\.pytest-night-audit-target tests\integration\test_academic_record_http_sqlite.py tests\integration\test_students_http.py
```

Frontend :

```powershell
Set-Location F:\EduNova\frontend
npm run lint
npm run test -- --run
npm run build
```

Lancement API isolé recommandé : définir `EDUNOVA_ENVIRONMENT=test`, `EDUNOVA_DATABASE_PATH` vers un fichier temporaire, un `EDUNOVA_JWT_SECRET` local de test et `EDUNOVA_CORS_ALLOWED_ORIGINS`, puis lancer depuis `F:\EduNova` :

```powershell
python -m uvicorn src.presentation.api.app:create_app --factory --host 127.0.0.1 --port 8017
```

Ne pas utiliser `src.presentation.api.main:app` ni `edunova.db` pour un test de reprise tant que la base réelle n'a pas fait l'objet d'une procédure de migration approuvée.

## Confirmation finale

Aucun fichier préexistant n'a été volontairement écrasé. Aucune base persistante réelle n'a été modifiée. `edunova.db` n'a pas été ouverte en écriture. Aucun commit ni push n'a été effectué.
