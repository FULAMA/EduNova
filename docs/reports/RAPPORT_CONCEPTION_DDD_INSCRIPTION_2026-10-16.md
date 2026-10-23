# EduNova - Conception DDD de l'inscription scolaire

Date : 2026-10-16
Statut : proposition soumise a examen, non validee

## Perimetre et preuves

Cette proposition est fondee sur :

- `docs/reports/RAPPORT_AUDIT_DOMAINE_SCOLAIRE_2026-10-16.md` ;
- `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md` ;
- `docs/v1/CONTRATS_METIER_V1.md` ;
- les entites, ports, repositories, migrations, routes et tests existants.

Aucun code, migration ou donnee n'a ete modifie ou execute. Seul ce rapport
est cree conformement au livrable.

## 1. Modele conceptuel

### Eleve et identite

`StudentSummary` et la table `students` fournissent aujourd'hui une lecture,
pas une entite metier complete : `src/academic/application/dto/student_summary.py:6`,
`src/academic/application/interfaces/student_repository.py:7-17` et
`src/infrastructure/repositories/sqlite_student_repository.py:14-61`.

Proposition : reutiliser l'identifiant eleve existant pour une affectation,
avec verification tenant, sans creer automatiquement une entite `Student`
riche. Une entite ou un aggregate d'identite ne doit etre ajoute que si ses
responsabilites sont validees. Aucun matricule, rapprochement, fusion ou
deduplication ne doit etre invente : la decision 45 est encore EN ATTENTE.

### Tenant et etablissement

Reutiliser `TenantContext`, `Membership`, `get_tenant_context` et
`require_role`. La decision 13 impose l'isolation tenant et le controle de
portee. Le tenant reste le perimetre de l'etablissement ; il ne faut pas
creer un second etablissement dans l'inscription.

### Annee scolaire et periodes

`AcademicPeriod` est reutilisable comme periode :
`src/academic/domain/entities/academic_period.py:6-30` et
`src/infrastructure/persistence/migrations/versions/migration_017_academic_catalogues.py:10-24`.
Il ne doit pas etre detourne comme annee scolaire.

`AcademicYear` est un modele propose dans `docs/v1/CONTRATS_METIER_V1.md:21-43`,
mais ce document est marque « proposition a valider avant implementation ».
La decision 10 impose de distinguer annee scolaire, periodes academiques et
periodes d'evaluation. Il faut donc creer `AcademicYear` seulement apres
validation de ses dates, statuts, cardinalite et roles.

### Classes, niveaux et options

Reutiliser `AcademicClass`, `AcademicOption`, `ClassOption` et `ClassSubject`.
`AcademicClass` porte actuellement `id`, `tenant_id`, `name` et `active`
(`src/academic/domain/entities/academic_class.py:5-17`). Il ne porte ni niveau
ni annee. `AcademicOption` et `ClassOption` sont deja tenant-scoped.

Ne pas ajouter niveau, filiere ou option obligatoire sans contrat scolaire
valide. `AssignSubjectToClass` fournit un precedent de validation des
references et du tenant (`src/academic/application/use_cases/assign_subject_to_class.py:20-101`),
mais il ne gere pas les inscriptions.

### Inscription et affectation

Le concept manquant est une affectation scolaire, ou inscription d'un eleve
pour une annee. Il devrait etre un nouveau modele, pas une colonne ajoutee a
`students` ou `academic_classes`, afin de conserver l'historique.

Champs candidats, a confirmer : `id`, `tenant_id`, `student_id`,
`academic_year_id`, `academic_class_id`, option eventuelle, statut, dates
d'effet, auteur, motif, provenance et version de concurrence.

L'option, le statut, les dates et l'identifiant officiel ne sont pas des
decisions prises par ce rapport.

## 2. Agregats et frontieres DDD

Proposition minimale a examiner :

1. `AcademicYear` comme racine du cycle de vie de l'annee, sans charger les
   eleves.
2. `StudentAssignment` comme racine de l'inscription et des changements de
   classe pour un eleve, un tenant et une annee.
3. L'identite eleve reste hors de l'aggregate d'affectation au depart et est
   verifiee par un port de lecture.
4. La configuration existante (`AcademicClass`, `AcademicOption`,
   `ClassOption`, `ClassSubject`) reste separee de l'affectation.
5. `StudentAcademicRecord` reste dedie aux resultats et a ses versions ; il
   ne devient pas l'historique de scolarite.

Invariants candidats, tous a confirmer sauf indication contraire :

- toutes les references d'une affectation ont le meme `tenant_id` ;
- l'annee, l'eleve et la classe appartiennent au tenant ;
- au plus une affectation active existe pour un eleve et une annee ;
- un transfert ferme l'ancienne affectation et conserve son historique ;
- une affectation historique n'est pas ecrasee silencieusement ;
- les doublons suivent la strategie de la decision 45.

Les seules obligations deja validees sont la tracabilite/provenance des
transferts (decision 12) et l'isolation/portee tenant (decision 13).

## 3. Ports, cas d'usage et evenements

Ports a introduire apres validation :

- `AcademicYearRepository` ;
- `StudentAssignmentRepository` avec courant, historique et concurrence ;
- `StudentReader` ou extension prudente de `StudentRepository` ;
- lecteurs de classe et d'option ;
- `TenantAccessPolicy` si les roles deviennent configurables.

Cas d'usage candidats :

- `CreateAcademicYear`, `OpenAcademicYear`, `CloseAcademicYear` ;
- `CreateAcademicPeriod` ou extension du cas existant ;
- `EnrollStudent` ou `AssignStudentToClass` ;
- `TransferStudent` ;
- `ListStudentAssignments` et `GetCurrentStudentAssignment`.

Evenements possibles, apres mutation acceptee et sauvegarde :
`AcademicYearOpened`, `AcademicYearClosed`, `StudentEnrolled`,
`StudentClassTransferred`, `StudentAssignmentEnded`. Les noms et payloads
restent a valider ; ils doivent respecter la redaction et ne contenir que les
donnees necessaires.

## 4. Transaction et isolation

Une inscription ou un transfert doit verifier les references, l'unicite active,
ecrire l'affectation et son historique dans une transaction, puis publier un
evenement selon le mecanisme fiable existant. Une simple verification frontend
ou un `SELECT` avant insertion ne suffit pas.

Si l'unicite active est validee, elle doit etre protegee par une contrainte
SQLite compatible avec le statut retenu, tenant-scoped. Les routes doivent
utiliser le tenant du token via `get_tenant_context`, jamais un tenant fourni
librement par le navigateur. Les references composees `(tenant_id, id)` sont
le precedent existant a reutiliser.

## 5. Regles et decisions

| Regle envisagee | Preuve existante | Statut | Consequence |
| --- | --- | --- | --- |
| Isolation par tenant | decision 13, contexte et repositories | Validee | Obligatoire dans tout use case |
| Annee distincte des periodes | decision 10, `AcademicPeriod` | Validee | Ne pas utiliser une periode comme annee |
| Historique des transferts | decision 12 | Validee | Ne pas ecraser l'affectation precedente |
| Une affectation active par eleve/annee | besoin de la mission | A confirmer | Cle d'unicite inconnue |
| Identifiant et deduplication | decision 45 | Bloquee | Aucun matricule ou fusion invente |
| Annees ouvertes simultanement | `CONTRATS_METIER_V1.md:50-55` | A confirmer | Cycle de vie non figable |
| Periode contenue dans une annee | contrat V1:27-33 | A confirmer | Contrainte de calendrier inconnue |
| Classe active obligatoire | champ `active` existant | A confirmer | Ne pas assimiler `active` a une regle metier |
| Option obligatoire ou facultative | `ClassOption` existant | A confirmer | Formulaire et validation inconnus |
| Roles d'inscription/transfert | routes actuelles ADMIN-only | A confirmer | Ne pas elargir les roles implicitement |
| Dates et statuts d'affectation | absents du code | A confirmer | Historique non definissable |

## 6. Tranches d'implementation

### Tranche 0 - Decisions et vocabulaire

Valider annee, affectation, transfert, doublons, champs et roles.
Livrable : contrat approuve et invariants classes par statut. Aucun code.

### Tranche 1 - Lecture et verification

Etendre prudemment les DTO/ports de lecture eleve, classe et periode, sans
persister d'inscription. Tester listes, details, cross-tenant et 401/403.
Risque : faire de `StudentSummary` une identite metier implicite.

### Tranche 2 - `AcademicYear`

Creer aggregate, ports, use cases et migration seulement apres validation.
Tester dates, statuts, tenant, periodes rattachees, idempotence et permissions.

### Tranche 3 - Affectation et historique

Creer `StudentAssignment`, repository, transaction, historique et concurrence.
Tester affectation valide, references cross-tenant, unicite active, transfert,
historique, echec atomique et conflit de version.

### Tranche 4 - API et frontend

Ajouter routes, autorisations et formulaire avec chargement, vide, erreurs,
double soumission et confirmation uniquement apres succes API. Valider HTTP et
frontend sur donnees synthetiques ; ne jamais utiliser `edunova.db`.

## 7. Decisions du proprietaire avant implementation

1. Quel est le modele officiel de l'annee et combien d'annees peuvent etre
   ouvertes simultanement ?
2. Une seule affectation active par eleve et annee est-elle la regle absolue ?
3. Quels sont les statuts, dates d'effet et procedures de transfert ?
4. Quels roles peuvent inscrire, modifier, transferer et consulter ?
5. Quelle option de la decision 45 est retenue pour les identifiants et
   doublons ?
6. L'option est-elle obligatoire et une classe peut-elle changer de
   configuration pendant l'annee ?

## Conclusion

La conception n'est pas validee. La premiere tranche de code realisable sans
inventer de regle est une extension de lecture et de verification tenant-scoped,
sans inscription persistante ni deduplication. Les tranches suivantes exigent
les decisions de la section 7 et une validation humaine explicite.
