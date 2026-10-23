# Deblocage E2E academique - 2026-10-16

## Decision

Aucune dependance Playwright ou Cypress n'a ete ajoutee. La stack actuelle
utilise Vite, React et Vitest/jsdom; `frontend/package-lock.json` ne fournit
pas Playwright installe et aucun navigateur automatisable n'est disponible.
Une installation locale modifierait le lockfile et la stack sans permettre
de lancer le scenario dans cet environnement.

Le parcours HTTP reste la preparation executable et les tests navigateur sont
prets a etre ajoutes sur une machine disposant d'un navigateur.

## Etat initial

Le worktree etait deja fortement modifie et contenait de nombreux fichiers
non suivis. Aucun changement existant n'a ete reinitialise ou nettoye. Le
registre metier et `edunova.db` n'ont pas ete modifies.

Versions detectees :

```text
Node v24.19.0
npm 11.17.0
Vitest 5.0.4
Playwright absent
Cypress absent
@vitest/browser-playwright absent
```

Scripts frontend existants : `dev`, `build`, `lint`, `test`, `preview`.

## Fixtures et donnees synthetiques

Les fixtures existantes sont suffisantes et ont ete reutilisees sans
duplication :

- `tests/conftest.py` cree des bases SQLite en memoire et des conteneurs
  isoles ;
- `tests/support/tenant.py` cree un tenant et un membership ;
- `tests/integration/test_students_http.py` cree utilisateurs, eleves et
  cas inter-tenant ;
- `tests/integration/test_academic_record_http_sqlite.py` cree dossier,
  periode, resultats, puis validation et correction ;
- `tests/presentation/test_academic_record_workflow.py` verifie les valeurs
  renvoyees par l'API.

Le jeu de donnees est ephemere et reste dans une base `:memory:` de test.
Il contient un tenant, un utilisateur ADMIN, un eleve, une periode, un
dossier et des resultats. Aucune donnee n'est ecrite dans `edunova.db`.

## Garde-fou de configuration

Les tests existants construisent directement `ApplicationContainer` avec
`database_path=":memory:"` ou une fixture isolee. Le seed de developpement
est refuse en production par `Settings.from_environment`. La procedure
manuelle documentee impose `EDUNOVA_DATABASE_PATH` sous `%TEMP%` et utilise
`create_app --factory`.

Aucun nouveau script de seed n'a ete ajoute : il aurait dupliquer la logique
des fixtures sans fournir une garantie navigateur dans l'environnement
actuel. Pour une future procedure executable, le garde-fou devra refuser au
minimum le chemin exact `edunova.db`, un chemin hors `%TEMP%` et une base
partagee non explicitement temporaire avant toute initialisation.

## Tests executes pour ce lot

Backend cible :

```text
.venv\Scripts\pytest.exe -q --basetemp=F:\EduNova\.pytest-e2e-prep \
  tests/integration/test_students_http.py \
  tests/integration/test_academic_record_http_sqlite.py \
  tests/presentation/test_academic_record_workflow.py
19 passed in 3.17s
```

Frontend cible :

```text
npm run test -- --run \
  src/features/auth/services/auth.service.test.ts \
  src/features/students/pages/StudentsPage/StudentsPage.test.tsx \
  src/features/students/pages/StudentDetailPage/StudentDetailPage.test.tsx \
  src/features/students/services/student.service.test.ts
4 files passed
22 tests passed
```

Ces tests couvrent authentification, acces protege, etat vide, chargement,
erreurs `401`/`403`, fiche eleve, periode, resultats et isolation tenant.

## Scenario navigateur a executer sur une machine compatible

1. Installer Playwright comme dependance de developpement locale, apres
   validation de la modification du lockfile.
2. Installer uniquement le navigateur requis par Playwright.
3. Demarrer l'API avec une base sous `%TEMP%`, `EDUNOVA_ENVIRONMENT=test`,
   un secret local et le seed de developpement.
4. Demarrer Vite avec `VITE_API_URL` vers cette API.
5. Se connecter avec le compte de test existant.
6. Inserer ou charger le jeu synthetique via une fixture reservee aux tests.
7. Verifier liste, fiche, periode, resultats, erreurs et refus inter-tenant.
8. Verifier les appels reseau et la console du navigateur.
9. Arreter les deux processus et conserver les artefacts de test sans les
   confondre avec la base reelle.

## Controle de protection

`edunova.db` n'a pas ete utilisee. Aucune migration, installation, commit,
push, suppression ou modification du registre n'a ete effectuee.

Le controle global `git diff --check` signale toujours des lignes vides
finales dans des fichiers preexistants; aucun reformatage global n'a ete fait.

## Statut

**VALIDATION PARTIELLE** : les donnees et le parcours HTTP sont prets et
verifies, mais le parcours navigateur ne peut pas etre execute dans cet
environnement faute de navigateur et de dependance E2E installee.
