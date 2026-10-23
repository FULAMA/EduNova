# Preparation E2E academique - 2026-10-16

## Conclusion

Le parcours HTTP de preparation est reproductible sur une base temporaire.
Le parcours navigateur reste non execute : aucun Playwright/Cypress n'est
installe et aucun navigateur automatisable n'est disponible dans cet
environnement.

Statut : **VALIDATION PARTIELLE**.

## Elements reutilisables

Les fixtures existantes couvrent deja les besoins sans duplication :

- `tests/conftest.py` fournit des bases SQLite en memoire et des conteneurs
  applicatifs isoles ;
- `tests/support/tenant.py` cree un tenant et un membership actif ;
- `tests/integration/test_students_http.py` cree des utilisateurs ADMIN,
  des eleves synthetiques et verifie l'isolation tenant ;
- `tests/integration/test_academic_record_http_sqlite.py` cree un dossier,
  une periode, des resultats, puis teste lecture, validation, correction et
  conflit de version ;
- `tests/presentation/test_academic_record_workflow.py` verifie les valeurs
  de matieres retournees par l'API ;
- `tests/unit/infrastructure/bootstrap/test_development_seed.py` confirme le
  compte de developpement et le tenant associe.

Le seed de developpement ne cree volontairement pas d'eleve ni de dossier.
Les donnees académiques doivent donc rester creees par les fixtures de test,
et non par un compte ou une base de production.

## Contrats confirmes

Les routes utilisees sont :

- `POST /auth/login` ;
- `GET /students` et `GET /students/{student_id}` ;
- `GET /academic-records/students/{student_id}/periods` ;
- `GET /academic-records/{student_id}/{academic_period_id}`.

Les lectures académiques exigent un membership actif avec rôle `ADMIN`. Le
tenant est derive du contexte d'authentification et les tests inter-tenant
verifient le refus côté serveur, pas seulement le filtrage frontend.

## Tests executes

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

Ces tests couvrent authentification, absence de résultats, chargement,
erreurs `401`/`403`, fiche élève, période, résultats, et appels protégés.

## Procedure HTTP reproductible

Depuis `F:\EduNova`, utiliser uniquement une base sous `%TEMP%` :

```powershell
$tempDb = Join-Path $env:TEMP "edunova-e2e\academic.db"
$env:EDUNOVA_ENVIRONMENT = "test"
$env:EDUNOVA_DATABASE_PATH = $tempDb
$env:EDUNOVA_JWT_SECRET = "secret-local-de-test-d-au-moins-32-caracteres"
$env:EDUNOVA_CORS_ALLOWED_ORIGINS = "http://127.0.0.1:5173"
$env:EDUNOVA_DEV_SEED = "true"
$env:EDUNOVA_DEV_SEED_EMAIL = "admin@edunova.com"
$env:EDUNOVA_DEV_SEED_PASSWORD = "<mot de passe de fixture de test>"
python -m uvicorn src.presentation.api.app:create_app --factory --host 127.0.0.1 --port 8033
```

Le frontend se lance dans un second terminal avec :

```powershell
Set-Location F:\EduNova\frontend
$env:VITE_API_URL = "http://127.0.0.1:8033"
npm run dev -- --host 127.0.0.1 --port 5173
```

Pour un parcours HTTP complet, reutiliser les donnees et assertions des
tests d'integration plutot que d'inscrire des donnees dans `edunova.db`.

## Strategie navigateur

Versions detectees : Node `v24.19.0`, npm `11.17.0`, Vitest `5.0.4`.
Playwright, Cypress et `@vitest/browser-playwright` ne sont pas presents.
Le fichier de verrouillage mentionne des adaptateurs Vitest optionnels, mais
aucun binaire navigateur n'est disponible.

Aucune installation n'a ete effectuee : elle modifierait les dependances et
ne permettrait pas de valider le scénario dans l'environnement courant sans
autorisation et sans donnees académiques persistées de demonstration.

## Scenarios prepares mais non executes dans un navigateur

1. Connexion du compte de developpement et redirection vers `/app`.
2. Chargement de `/app/students` et affichage de l'eleve synthetique.
3. Ouverture de `/app/students/{student_id}`.
4. Selection d'une periode et affichage des resultats API.
5. Etat vide sans dossier.
6. Erreurs reseau et `401`/`403`.
7. Tentative d'acces a un eleve d'un autre tenant.

## Protection

`edunova.db` n'a pas ete utilisee ni modifiee. Aucune migration, installation,
suppression, commit, push ou modification du registre métier n'a ete effectuee.
