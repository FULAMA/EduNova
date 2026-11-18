# Matrice de traçabilité V1 — EduNova

> Baseline vérifiée dans le code le 2026-11-04 (branche `fix/mypy-test-double-contracts`).
> Chaque statut s’appuie sur une preuve concrète (fichier / route / test).

## État Git (LOT 1)

- Branche : `fix/mypy-test-double-contracts` (à jour avec `origin`)
- Working tree : clean au démarrage de la mission
- Bases permanentes `edunova.db` / `edunova_dev.db` : non modifiées

## Matrice

| Besoin | Backend | Frontend | Tests | Statut |
|---|---|---|---|---|
| Auth login / refresh / me | `POST /auth/login`, `/auth/refresh`, `GET /auth/me` (`routes/auth.py`) | Login + refresh client (`auth.service.ts`, `client.ts`) | `test_refresh_token_http.py`, `test_auth_me_http.py` | **OK** |
| Déconnexion serveur | Absent avant mission ; révocation refresh via `revoked_refresh_tokens` | `clearSession()` local seulement (`Topbar.tsx`) | Aucun test logout | **À compléter (LOT 2)** |
| CRUD élèves L/C/R | `GET/POST /students`, `GET /students/{id}` ; rôles finance | Pages élèves + création | `test_students_http.py` | **PARTIEL** — manque `PUT` |
| Mise à jour élève | Absent | Édition limitée / absente | Absent | **À compléter (LOT 3)** |
| Accès élèves PROF / PARENT / STUDENT directory | Pas de `require_role("PROF"\|"PARENT")` productif ; STUDENT via portail `/me/student` | Matrice FE refuse PARENT sur dashboard | Refus TEACHER 403 | **BLOQUÉ / PARTIEL** |
| Enregistrement paiement + résumé élève | `POST /billing/payments`, `GET .../summary` | Flux finance par élève | `test_billing_http.py` | **OK** |
| Liste globale paiements | Absent | Besoin documenté (`CONTRATS_API_MANQUANTS.md`) | Absent | **À compléter (LOT 4)** |
| Échéanciers / arriérés | `due_date` sur charges ; pas d’API arriérés | Dashboard sans soldes réels finance | Décision 22 VALIDÉE | **À compléter (LOT 5)** |
| Dashboard direction (finance) | Aucune route `/dashboard` | Agrégation client (élèves/classes/années) | `DashboardPage.test.tsx` | **PARTIEL** — stats scolaires FE ; finance API manquante (Déc. 23) |
| Portail enseignant | Aucun router / affectation professeur | Absent | TEACHER = 403 | **BLOQUÉ (LOT 7)** — pas de modèle d’affectation PROF |
| Portail parent | Propositions PAR-REL `BLOCKED` ; pas de modèle | Absent | Absent | **BLOQUÉ (LOT 8)** |
| Bulletins | `/report-cards` prepare/publish/correct/get/pdf | Consultation élève | `test_report_cards_http.py` | **OK partiel** — décisions BUL-TECH-02..06 ouvertes |
| Lien compte élève | `StudentUserLink` + `/me/student` | Portail élève | `test_student_portal_http.py` | **OK** (≠ parent-enfant) |
| Catalogue de frais | fee-types CRUD statut + assign | Catalogue FE | `test_billing_http.py` | **OK** |
| Corrections paiement auditées | `POST .../correction` + counter entries | — | `test_billing_http.py` | **OK** |

## Preuves clés

| Domaine | Preuve |
|---|---|
| Routers enregistrés | `src/presentation/api/app.py` L354–375 |
| Rôles finance | `FINANCE_ROLES` / `FINANCE_MANAGEMENT_ROLES` dans `dependencies/auth.py` |
| Révocation refresh | `SQLiteRefreshTokenRepository.revoke/consume` + table `revoked_refresh_tokens` |
| Pas de blacklist access | `get_current_user` décode JWT sans check jti |
| Parent bloqué | `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md` PAR-REL-* |
| Décision arriérés | Décision 22 VALIDÉE |
| Décision dashboard promoteur | Décision 23 VALIDÉE |

## Stratégie de session (constat LOT 2)

Architecture actuelle : JWT access (court) + JWT refresh (jti) avec liste de révocation SQLite.

Conséquence compatible :

- `POST /auth/logout` doit révoquer le **refresh** (empêche le renouvellement).
- L’access token reste valable jusqu’à expiration naturelle (pas de mécanisme de révocation access existant ; n’en inventer aucun incompatible).
