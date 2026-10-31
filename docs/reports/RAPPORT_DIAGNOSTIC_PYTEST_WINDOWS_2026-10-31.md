# Diagnostic pytest Windows — 2026-10-31

## Symptôme observé

L'exécution directe de :

```powershell
python -m pytest tests/unit/tools/edunova -q
```

a produit **450 tests passés et 55 erreurs de setup**. Les traces partagées convergent vers :

```text
PermissionError: [WinError 5] Accès refusé:
C:\Users\Ir FLM\AppData\Local\Temp\pytest-of-Ir FLM
```

Les erreurs surviennent lorsque pathlib/pytest tente de parcourir le répertoire temporaire Windows. Elles ne démontrent pas, à elles seules, 55 défauts fonctionnels dans EduNova.

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

**En attente de validation sur Windows.** La correction de configuration est publiée sur la branche de travail, mais le résultat des 55 tests doit être confirmé par une nouvelle exécution locale. Ne pas considérer la suite complète comme verte avant cette vérification.
