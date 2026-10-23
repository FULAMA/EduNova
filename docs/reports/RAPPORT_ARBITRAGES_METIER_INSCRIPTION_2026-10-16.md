# EduNova - Arbitrages metier de l'inscription

Date : 2026-10-16
Statut : preparation de decision, non validee

## Sources et faits techniques

Sources lues :

- `docs/reports/RAPPORT_VERIFICATION_CLASSES_OPTIONS_2026-10-16.md` ;
- `docs/reports/RAPPORT_RECONCILIATION_DECISIONS_INSCRIPTION_2026-10-16.md` ;
- `docs/reports/RAPPORT_CONCEPTION_DDD_INSCRIPTION_2026-10-16.md` ;
- `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md`.

Le registre existe sous le nom exact attendu. Les faits techniques verifies
sont : `AcademicPeriod` existe mais pas `AcademicYear`, les classes/options
sont tenant-scoped, aucune affectation eleve-classe n'existe, les routes
existantes utilisent `require_role("ADMIN")`, et la decision 45 est toujours
EN ATTENTE. Aucun code, registre, migration, dependance ou base reelle n'a
ete modifie ou utilise.

## Decisions deja confirmees

- Isolation multi-tenant et controle de portee : decision 13.
- Distinction annee scolaire / periode academique : decision 10.
- Historique et provenance obligatoires pour les transferts : decision 12.
- Decision 45 non tranchee : aucune strategie d'identite ou de deduplication
  ne doit etre figee.
- Les lectures actuelles des classes/options sont filtrees par tenant et les
  controles existants sont preserves, selon le rapport de verification.

## Arbitrages necessaires

| Decision | Options | Avantages / risques | Consequences domaine, droits, historique et tests | Recommandation non contraignante |
| --- | --- | --- | --- | --- |
| Modele et libelle de l'annee | A. libelle civil `2026-2027` avec dates ; B. libelle officiel configurable ; C. libelle + calendrier distinct | A est simple mais peut ne pas representer tous les calendriers. B respecte la decision 10 mais demande une configuration. C est flexible mais plus complexe. | `AcademicYear` nouveau dans tous les cas ; `AcademicPeriod` reste distinct. Tester dates, format, tenant et periode rattachee. | Examiner A comme valeur par defaut seulement si l'etablissement confirme le calendrier officiel. |
| Nombre d'annees actives | A. une seule active ; B. plusieurs ouvertes ; C. plusieurs creees mais une seule active | A simplifie l'interface et les contraintes. B couvre calendriers paralleles mais augmente les ambiguities. C separe creation future et activation. | Policy tenant et index/contrainte differents. Les roles d'ouverture/fermeture et les tests de transition dependent du choix. | C est le plus prudent pour permettre des annees futures sans les activer ; ce n'est pas une decision validee. |
| Unicite d'affectation active | A. une par `(tenant, student, year)` ; B. plusieurs avec une principale ; C. plusieurs sans principale | A est coherent avec la consultation quotidienne. B/C exigent une priorite et des regles de chevauchement. | Aggregate `StudentAssignment`, contrainte SQLite et controle de concurrence. Tests de doublon, cross-tenant et concurrence. | A est la plus petite regle testable, sous reserve d'approbation explicite. |
| Transfert | A. fermer l'ancienne puis activer la nouvelle dans une transaction ; B. creer une nouvelle puis basculer ; C. workflow en attente de validation | A respecte la formulation proposee et evite deux actifs. B facilite certaines reprises mais exige une contrainte temporaire. C ajoute une etape metier. | Historique immuable, auteur, motif, provenance, date et atomicite ; droits de transfert ; tests d'echec et rollback. | A est compatible avec la decision 12, mais l'ordre et les champs restent a approuver. |
| Roles inscription/transfert | A. `ADMIN` seul ; B. `ADMIN` + `DIRECTION`/`PROMOTEUR` habilite ; C. policy configurable par tenant | A correspond au code actuel. B correspond a la demande mais les roles ne sont pas definis. C suit la decision 13 mais demande une policy explicite. | `require_role` ou policy tenant, audit des actions, tests 401/403 et membership inactive. | B dans une policy configurable, avec noms et habilitations confirmes ; ne pas modifier l'autorisation avant arbitrage. |
| Option de classe | A. option obligatoire si `ClassOption` existe ; B. option facultative meme si la classe en propose ; C. regle configurable par classe | A evite les affectations incompletes mais peut bloquer des cas autorises. B est permissif mais peut perdre une information scolaire. C est flexible mais ajoute une configuration. | Validation de reference classe-option, champ nullable ou non, tests classe sans option, option valide et option cross-tenant. | C si l'organisation confirme des exceptions ; sinon A uniquement pour les classes marquees comme proposant des options. |
| Cycle d'inscription | A. `DRAFT -> ACTIVE` ; B. `DRAFT -> PENDING -> ACTIVE` ; C. creation directement active | A est simple. B trace mieux une validation mais ajoute un statut et une permission. C reduit le workflow mais perd la preparation. | Statut propre a `StudentAssignment`, transitions, conditions d'activation, audit et tests de transitions. Ne pas reutiliser `DRAFT/VALIDATED` du dossier academique. | A est le minimum coherent avec la demande, sous reserve de definir qui active et quelles conditions sont requises. |
| Decision 45 | A/B/C du registre, ou maintien de l'attente | Les options A/B/C modifient fortement l'identite et les doublons. Les choisir sans validation risquerait de fusionner des personnes. | Ne pas ajouter matricule, fusion, rejet automatique ou index d'identite. Tester seulement l'absence de contournement. | Maintenir l'attente ; aucune strategie ne doit bloquer la conception tenant-scoped de l'affectation existante. |

## Ce qui bloque reellement la persistance

Les decisions minimales bloquantes sont :

1. le contrat `AcademicYear` : dates, statut et distinction future/active/cloturee ;
2. l'unicite d'une affectation active par eleve et annee ;
3. le transfert atomique et les champs d'historique obligatoires ;
4. les roles exacts d'inscription et de transfert ;
5. les transitions de statut et la condition d'activation.

La decision 45 ne bloque pas une affectation qui reference un eleve deja
existant par identifiant technique et verifie son tenant, mais elle bloque
toute nouvelle politique d'identite, de matricule ou de deduplication.

La regle d'option est necessaire avant de rendre le champ obligatoire dans une
API, mais elle ne bloque pas la conception generale si l'option reste
explicitement nullable et si aucune contrainte metier n'est inventee.

## Elements techniques verifies versus hypotheses

### Verifies dans le code

- `AcademicClass`, `AcademicOption`, `ClassOption` et `ClassSubject` portent un
  `tenant_id`.
- `SQLiteAcademicClassRepository.list_by_tenant` filtre le tenant.
- `GET /classes` obtient le tenant du contexte authentifie et exige `ADMIN`.
- `Membership.role` est une chaine ; aucun enum `DIRECTION` ou `PROMOTEUR`
  n'est defini.
- `students` et les migrations existantes ne contiennent aucune affectation.
- `StudentAcademicRecord` utilise `DRAFT`/`VALIDATED` pour les resultats,
  pas pour les inscriptions.

### Hypotheses a confirmer

- Le format civil de l'annee est adapte a tous les etablissements.
- Une seule annee active est toujours suffisante.
- Une seule affectation active est toujours obligatoire.
- La fermeture avant activation est l'ordre metier officiel.
- `DRAFT -> ACTIVE` suffit sans validation intermediaire.
- L'option est obligatoire pour toute classe qui expose `ClassOption`.
- `DIRECTION` et `PROMOTEUR` sont les noms de roles metier exacts.

## Plus petit ensemble de decisions avant conception detaillee

Le proprietaire doit trancher, au minimum :

1. le modele/date/statut de `AcademicYear` et la cardinalite des annees
   actives ;
2. l'unicite d'une affectation active par eleve et annee ;
3. l'ordre et l'atomicite du transfert, avec les champs d'historique ;
4. les roles autorises et leur habilitation tenant ;
5. le cycle `DRAFT -> ACTIVE` et les conditions d'activation.

La regle d'option peut rester parametree ou nullable dans la premiere
conception, mais doit etre tranchee avant de rendre le formulaire strict.
La decision 45 reste explicitement hors de cette conception.

## Prochain jalon conseille

Organiser un arbitrage metier sur les cinq decisions bloquantes, puis consigner
les choix dans le registre sans supprimer son historique. Apres approbation,
concevoir uniquement `AcademicYear` et `StudentAssignment` sur une base de
test, avec contraintes tenant et tests d'atomicite ; ne pas commencer par le
formulaire frontend.

## Verdict

**PRET POUR ARBITRAGE METIER**

Le dossier contient les options, risques et consequences necessaires a une
decision humaine. Il n'est pas encore pret pour la conception detaillee de la
persistance tant que les cinq decisions minimales ne sont pas tranchees.
