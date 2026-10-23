# EduNova V1 - Plan d'implementation

Statut : plan soumis a validation humaine. Aucun code de production n'est implemente par cette mission.

## Tache 0 - Decisions et garde-fous

- Objectif : valider les choix listes dans [DECISIONS_REQUISES.md](F:/EduNova/docs/v1/DECISIONS_REQUISES.md).
- Reutiliser : `tenant_id`, `TenantContext`, `AcademicPolicy`, statuts acadmiques existants.
- Acceptance : decisions documentees, roles, devises, retention et stockage approuves.
- Tests : aucun code ; revue de contrat.
- Commande : revue manuelle uniquement.
- Decision humaine : oui.

## Tache 1 - Configuration d'etablissement et annees

- Objectif : fournir un parcours complet de configuration et de periode pour un tenant.
- Fichiers a reutiliser : `src/academic/domain/entities/academic_period.py`, entites classes/options/matieres, repositories SQLite tenant-scoped, dependances auth.
- Fichiers a creer : value objects et aggregates dans `src/academic/domain`, ports dans `src/academic/application/interfaces`, use cases, schemas/routes et repositories correspondants.
- Acceptance : creation, ouverture et fermeture d'une annee ; periode validee ; aucune reference cross-tenant ; modification interdite apres fermeture.
- Tests : domaine, repositories SQLite sur `tmp_path`, API avec deux tenants, roles autorises/refuses.
- Commandes : test cible, Ruff, Mypy, puis suite complete.
- Decision humaine : seulement les choix de Tache 0.

## Tache 2 - Deliberation versionnee

- Objectif : rendre la deliberation exploitable avec un record valide et une version explicite.
- Fichiers a reutiliser : `StudentAcademicRecord`, `AcademicPolicy`, `DeliberationEngine`, `Deliberation`.
- Fichiers a creer : port de lecture de politique/record, use case de deliberation, evenement et persistence si necessaire.
- Acceptance : decision deterministe, version du record capturee, aucune deliberation sur record DRAFT, correction produisant une nouvelle version.
- Tests : seuils, arrondi, versions, tenant, erreurs et propagation d'evenement apres sauvegarde.
- Commandes : `pytest` cible, Ruff, Mypy.
- Decision humaine : confirmer si une deliberation est obligatoire pour un bulletin.

## Tache 3 - Bulletin derive et renderer injectable

- Objectif : generer un bulletin versionne depuis des sources academiques validees.
- Fichiers a reutiliser : record, periode, politique, deliberation et configuration de Tache 1.
- Fichiers a creer : aggregate `ReportCard`, ports, use case, renderer abstrait, adaptateur PDF seulement apres choix de dependance.
- Acceptance : generation refusee si record non valide ; notes/maxima/coefficient/moyennes/pourcentages coherents ; nouvelle version apres correction ; ancien document immuable.
- Tests : domaine, renderer fake, API, absence de fuite, tenant et erreurs de stockage.
- Commandes : tests cibles, Ruff, Mypy, build frontend seulement si integration ajoutee.
- Decision humaine : stockage, format, retention, bibliotheque PDF et droits.

## Tache 4 - Paiement interne USD/CDF sans fournisseur

- Objectif : couvrir la saisie interne idempotente et la generation de recu sans integration externe.
- Fichiers a creer : bounded context `src/billing`, entities/value objects, ports, use cases et adaptateurs SQLite.
- Acceptance : `Money` decimal, USD/CDF distincts, solde coherent, idempotence, recu unique et immuable, annulation tracee.
- Tests : domaine, transactions, repositories tenant-scoped, concurrence limitee par contraintes SQLite, API et controles de role.
- Commandes : tests cibles, Ruff, Mypy, suite complete.
- Decision humaine : autorisations, surpaiement, affectations multiples, format de recu.

### Complément canonique finance

La correction d'un paiement confirmé doit utiliser `FIN-COR-01` et préserver le reçu initial. `FIN-ROLE-01` impose les contrôles tenant-scoped pour la direction et les rôles caisse/comptabilité explicitement affectés. `FIN-REC-01` ajoute la consultation et le rendu PDF ; stockage, rétention et conformité restent des prérequis ouverts.

## Tache 5 - Frontend contractuel

- Objectif : connecter un seul parcours valide de bout en bout, sans logique metier dans React.
- Fichiers a reutiliser : router et composants existants de `frontend/src`, schemas API et dependances auth.
- Fichiers a creer : client API, gestion session, types de reponse, etats loading/error, ecrans uniquement pour le parcours approuve.
- Acceptance : token non expose dans les logs, tenant transmis par le contrat serveur, erreurs mappees, donnees non simulees pour le parcours choisi.
- Tests : TypeScript build, tests de client si framework ajoute autorise, verification manuelle locale.
- Commandes : `npm run build`.
- Decision humaine : parcours UI prioritaire et strategie de session.

## Tache 6 - Validation finale

- Objectif : confirmer le contrat et les limites avant livraison.
- Acceptance : suite complete verte, Ruff/Mypy/Bandit verts, build frontend vert, migration non executee sur base persistante, diff revu.
- Tests : integration, securite multi-tenant, contrats de codes de sortie CLI existants.
- Commandes : suite complete avec `--basetemp` controle, `ruff`, `mypy`, `bandit`, build frontend.
- Decision humaine : go/no-go de livraison.

## Ordre recommande

Commencer par Tache 0, puis Tache 1 et Tache 2. Le premier parcours complet recommande est : configurer une annee et une periode, creer/valider un dossier, calculer une deliberation, puis exposer un resultat API. Le bulletin et la finance restent bloques par leurs decisions metier respectives.

## Risques de regression

- Extension des schemas SQLite sans migration approuvee.
- Oubli de `tenant_id` dans un port ou une contrainte SQL.
- Modification accidentelle des seuils existants de `AcademicPolicy`.
- Generation de documents a partir d'un record DRAFT.
- Usage de `float` pour les montants.
- Appel fournisseur externe non idempotent.
- Couplage frontend direct a des repositories ou regles metier.

## Réconciliation canonique des bulletins V1

Les références D4 à D7 restent conservées pour l'historique. Le plan utilise les identifiants `BUL-CAL-01`, `BUL-PUB-01`, `BUL-COR-01`, `BUL-CALC-01`, `BUL-DOC-01`, `BUL-PROF-01` et `BUL-SCOPE-01`.

### Tranches réconciliées

1. `BUL-CAL-01` et `BUL-PROF-01` : définir les profils versionnés et leurs périodes, sans inventer de valeurs réglementaires.
2. `BUL-PUB-01` : persister une délibération liée au dossier, à sa version, à la politique et au profil.
3. `BUL-DOC-01` : créer `ReportCard`, snapshot immuable et renderer injectable.
4. `BUL-COR-01` : persister les versions, l'historique et `SUPERSEDED`.
5. `BUL-SCOPE-01` : exposer l'API et le frontend multi-niveaux sans calcul officiel côté client.

Chaque tranche exige des tests tenant-scoped, de versionnement, d'autorisation et de concurrence avant migration ou rendu réel.

## Clarifications Tranche 0.1

Les choix canoniques sont désormais : `BUL-PUB-01` (D4-A), `BUL-DOC-01` (D5-B), `BUL-COR-01` (D6-A pour le remplacement) et `BUL-CALC-01` (D7-A comme défaut technique sous réserve réglementaire).

La révocation est distincte du remplacement `SUPERSEDED` et ne doit pas être implémentée avant définition de son contrat.

### Critères obligatoires de la Tranche 1

- définir uniquement les types de profils, versions, dates d'effet, niveaux, programmes et options ;
- vérifier l'isolation tenant et l'absence de références croisées ;
- permettre des périodes configurables sans imposer un calendrier réglementaire ;
- utiliser des profils synthétiques dans les tests ;
- ne fixer aucune matière, maximum, coefficient, seuil, règle de passage, mention ou repêchage officiel ;
- ne créer aucune migration de bulletin ni émission officielle.
