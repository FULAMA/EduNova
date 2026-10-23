# Rapport de validation navigateur - 2026-10-16

## Perimetre

Cette verification a porte uniquement sur le manque signale dans le rapport
de reprise : le parcours frontend/backend authentifie dans un navigateur.
Le registre metier n'a pas ete modifie. `edunova.db` n'a pas ete utilise.

## Outils disponibles

- Frontend : Vite, React, tests Vitest/jsdom.
- Routes frontend : `/login`, `/app/students` et `/app/students/:studentId`.
- Routes backend : `/auth/login`, `/students`, `/students/{student_id}`,
  `/academic-records/students/{student_id}/periods` et
  `/academic-records/{student_id}/{academic_period_id}`.
- Aucun repertoire Playwright ou Cypress n'a ete trouve.
- `frontend/node_modules/playwright` et `frontend/node_modules/@playwright`
  sont absents.
- L'outil navigateur disponible dans l'environnement ne fournit aucun
  navigateur; la creation d'un onglet `iab` a retourne
  `Browser is not available: iab`.

## Compte et donnees de test

Le seed de developpement fournit un compte `admin@edunova.com`, un tenant de
developpement fixe et un membership `ADMIN`. Le mot de passe est defini
explicitement uniquement dans la fixture de test du seed; aucun secret n'a
ete lu depuis `.env` ou la base reelle.

Le seed ne cree pas d'eleve, de periode academique ni de dossier. Il permet
donc de verifier l'authentification, mais pas d'afficher une fiche eleve ou un
resultat academique sans ajouter des donnees synthetiques supplementaires.

## Environnement isole

API lancee avec `src.presentation.api.app:create_app --factory` sur le port
`8032`, frontend Vite sur le port `5173`, et SQLite sous `%TEMP%`.
Variables de test utilisees : environnement `test`, chemin de base temporaire,
secret JWT local, origine CORS locale et seed de developpement.

Resultats HTTP observes :

```text
GET /health       200
POST /auth/login  200, authenticated=true
GET /students     200, liste vide
GET frontend /    200, conteneur React present
```

Les logs Uvicorn confirment les trois appels API sans erreur. Les logs Vite
confirment `Local: http://127.0.0.1:5173/`. Les processus d'API et frontend
ont ensuite ete arretes et les ports ne sont plus en ecoute.

## Parcours navigateur

Non execute. Aucun navigateur automatisable n'etait disponible et aucun outil
E2E existant n'a pu prendre le relais. Aucune capture d'ecran n'est donc
disponible.

Les etapes suivantes restent non observees dans un navigateur :

- rendu visuel de la connexion ;
- redirection apres connexion ;
- navigation vers la fiche eleve ;
- selection d'une periode ;
- affichage des resultats depuis l'API ;
- etats de chargement et erreurs JavaScript ;
- refus visuel d'un utilisateur non autorise.

## Protection du depot

Le statut Git a ete verifie avant et apres. Aucun fichier existant n'a ete
supprime, aucun commit, push, reset, nettoyage ou migration n'a ete effectue.
`edunova.db` conserve sa taille observee de `192512` octets et sa date de
modification du 16/10/2026 01:53:44.

## Prerequis pour terminer

1. Fournir un navigateur automatisable deja installe et accessible, ou
   installer Playwright apres validation explicite de cette dependance.
2. Ajouter un jeu de donnees de demonstration non reel contenant un eleve,
   une periode et un dossier academique, sans modifier la base de production.
3. Rejouer le scenario avec le compte de developpement et controler les
   reponses API, les redirections et la console navigateur.

## Statut

**VALIDATION PARTIELLE**. L'API, l'authentification et le chargement frontend
ont ete verifies par HTTP sur un environnement isole. Le parcours authentifie
dans un navigateur n'est pas valide faute d'outil navigateur et de donnees
academiques de demonstration.
