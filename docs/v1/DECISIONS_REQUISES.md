# EduNova V1 - Decisions requises

Ces points bloquent l'implementation de production. Aucune valeur par defaut ne doit etre choisie silencieusement.

## Etablissement et calendrier

### D1 - Annees ouvertes

- Option A : une seule annee ouverte par tenant. Simple, evite les ambiguities.
- Option B : plusieurs annees ouvertes. Flexible, mais chaque operation doit porter l'annee explicitement.
- Consequence : contrainte SQL et API de selection differentes.

### D2 - Autorisations administratives

- Option A : `ADMIN` gere configuration et calendrier.
- Option B : role dedie `SCHOOL_ADMIN`/`ACADEMIC_ADMIN`.
- Consequence : migration de memberships et matrice d'autorisation.

### D3 - Periodes chevauchantes

- Option A : interdites dans un tenant.
- Option B : permises par calendrier ou programme.
- Consequence : modele de calendrier plus riche si B.

## Deliberation et bulletin

### D4 - Obligation de deliberation

- Option A : bulletin uniquement avec deliberation versionnee.
- Option B : bulletin de notes possible sans decision finale.
- Consequence : statut et autorisation de generation.

### D5 - Document emis

- Option A : PDF immuable stocke dans un stockage objet.
- Option B : PDF regenere depuis un snapshot immutable.
- Option C : contenu stocke en base.
- Consequence : cout, retention, disponibilite et audit differents.

### D6 - Correction d'un bulletin emis

- Option A : ancien bulletin `SUPERSEDED`, nouveau numero/version.
- Option B : revocation explicite puis regeneration.
- Consequence : audit, affichage historique et droits d'annulation.

### D7 - Arrondi et pourcentage

- Option A : deux decimales fixes conformes a `AcademicPolicy`.
- Option B : precision configurable par tenant.
- Consequence : reproductibilite et compatibilite des anciens documents.

## Finance

### D8 - Mode de paiement V1

- Option A : saisie interne uniquement, sans fournisseur.
- Option B : integration d'un fournisseur externe des V1.
- Consequence : secrets, webhooks, idempotence externe et tests d'integration.

### D9 - Surpaiement et paiement partiel

- Option A : surpaiement refuse, paiement partiel autorise.
- Option B : surpaiement transforme en credit.
- Option C : remboursement/contre-ecriture obligatoire.
- Consequence : aggregate de solde et evenements financiers.

### D10 - Sequence des recus

- Option A : sequence par tenant et par exercice.
- Option B : sequence globale.
- Consequence : isolation, concurrence et contraintes d'unicite.

### D11 - Annulation financiere

- Option A : annulation avec evenement compensatoire, jamais suppression.
- Option B : remboursement externe trace separement.
- Consequence : reconciliation et responsabilites operationnelles.

### D12 - Autorisations finance

- Option A : `ADMIN` confirme et annule.
- Option B : roles dedies caisse/comptabilite avec separation des fonctions.
- Consequence : matrice RBAC et tests de non-contournement.

### Réconciliation financière canonique

Les options D11 et D12 restent conservées comme historique. Les décisions applicables sont :

- `FIN-ROLE-01` : direction, `ACCOUNTANT` et `CASHIER` explicitement affectés au tenant, avec contrôle serveur ;
- `FIN-COR-01` : correction par contre-écriture liée, jamais suppression ou écrasement ;
- `FIN-REC-01` : reçu consultable et PDF téléchargeable, sans effacer le reçu original lors d'une correction.

Le stockage durable, la rétention et la conformité légale du PDF restent ouverts.

## Exploitation et livraison

### D13 - Migrations

- Option A : migrations lancees par un operateur avant demarrage.
- Option B : migrations au demarrage avec verrou et rollback documentes.
- Consequence : disponibilite et risque sur les bases persistantes.

### D14 - Frontend prioritaire

- Option A : parcours calendrier/dossier academique.
- Option B : consultation bulletin.
- Option C : consultation solde/recu.
- Consequence : ordre des taches et contrat API prioritaire.

## Regle de validation

Chaque decision doit indiquer un proprietaire, une date, une option retenue et les invariants associes. Tant qu'une decision est non resolue, le code correspondant reste au stade de contrat et de tests de domaine, sans migration ni fournisseur externe.

## Réconciliation canonique des décisions bulletins V1

Les références D4 à D7 sont conservées comme historique. Les identifiants canoniques sont :

| Identifiant | Décision | Statut | Référence historique |
|---|---|---|---|
| `BUL-CAL-01` | Périodes configurables par profil académique | VALIDÉE | D1, D3, registre 10 |
| `BUL-PUB-01` | Délibération persistée et versionnée avant publication | VALIDÉE | D4, option A retenue |
| `BUL-COR-01` | Nouvelle version et ancienne conservée en `SUPERSEDED` | VALIDÉE | D6, option A retenue |
| `BUL-CALC-01` | Politique versionnée et arrondi explicite | VALIDÉE AVEC RÉSERVE RÉGLEMENTAIRE | D7 |
| `BUL-DOC-01` | PDF depuis snapshot immuable | VALIDÉE | D5, option B retenue |
| `BUL-PROF-01` | Profils versionnés par niveau, programme et option | VALIDÉE | registre 10 et 11 |
| `BUL-SCOPE-01` | V1 primaire, secondaire inférieur et humanités | VALIDÉE | périmètre V1 |

Les programmes, matières, maxima, coefficients, périodes, repêchages, décisions de passage, mentions, rôles, rétention et identifiants officiels restent ouverts.

## Clarifications Tranche 0.1

Les options historiques restent affichées pour préserver la traçabilité. Les choix canoniques applicables aux bulletins sont explicités ici :

- D4-A est retenue sous `BUL-PUB-01` : la publication officielle exige une délibération persistée et versionnée.
- D5-B est retenue sous `BUL-DOC-01` : le document est rendu depuis un snapshot immuable. Le choix du stockage reste ouvert.
- D6-A est retenue sous `BUL-COR-01` pour le remplacement : l'ancienne version devient `SUPERSEDED` et une nouvelle version est créée.
- La révocation n'est pas assimilée à `SUPERSEDED`. Elle reste une décision distincte à définir : motif, autorité, statut, visibilité et conséquences.
- D7-A constitue le défaut technique de `BUL-CALC-01` avec deux décimales, sous réserve de validation réglementaire.

La Tranche 1 ne peut définir que la structure et le versionnement des profils. Elle ne peut pas fixer les matières, maxima, coefficients, périodes officielles, seuils, règles de passage, mentions ou repêchages.
