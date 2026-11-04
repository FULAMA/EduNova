# Diagnostic pytest Windows — 2026-10-31

## Symptôme observé

L'exécution directe de :

```powershell
python -m pytest tests/unit/tools/edunova -q
```

avait produit **450 tests passés et 55 erreurs de setup**. Les traces partagées convergeaient vers :

```text
PermissionError: [WinError 5] Accès refusé:
C:\Users\Ir FLM\AppData\Local\Temp\pytest-of-Ir FLM
```

Les erreurs survenaient lors de l'accès au répertoire temporaire Windows. Elles ne démontraient pas, à elles seules, 55 défauts fonctionnels dans EduNova.

## Analyse du dépôt

- `pytest.ini` définissait les chemins et conventions de découverte, mais aucun répertoire temporaire explicite.
- `.gitignore` exclut déjà `.pytest-work/`.
- Les commandes internes EduNova `run_tests` et `quality` utilisent déjà `--basetemp=<racine-projet>/.pytest-work`.
- L'exécution directe de pytest contournait ce garde-fou et retombait sur le répertoire temporaire du profil Windows.

## Correction appliquée

Ajout dans `pytest.ini` :

```ini
addopts = --basetemp=.pytest-work
```

Les lancements directs de pytest utilisent maintenant le répertoire temporaire local au projet. Les commandes du CLI peuvent continuer à fournir leur propre `--basetemp` explicite.

## Périmètre et sécurité

- Aucun code métier, agrégat, invariant DDD, migration ou donnée applicative n'a été modifié.
- Aucun fichier de base de données n'a été touché.
- Le répertoire `.pytest-work/` est déjà ignoré par Git.
- Aucun changement n'a été poussé sur `main`.

## Validation

- Validation locale Windows communiquée par le propriétaire : `python -m pytest tests/unit/tools/edunova -q` → **505 passed in 11.73s**.
- Le workflow GitHub Actions #281 a également exécuté la suite complète avec succès sur Windows : compilation, MyPy, Ruff, Bandit, pip-audit et tests complets.
- La CI utilise explicitement `--basetemp=.pytest_tmp` pour son exécution complète ; le test local ciblé valide séparément la configuration pytest du projet.
- La réussite ciblée locale et la réussite de la suite complète en CI sont deux validations distinctes.

Workflow : https://github.com/FULAMA/EduNova/actions/runs/41250482987
