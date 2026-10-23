# EduNova - Reconciliation des decisions d'inscription

Date : 2026-10-16
Statut : audit documentaire et code, sans implementation

## Sources et etat

Sources inspectees :

- `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md` ;
- `docs/reports/RAPPORT_AUDIT_DOMAINE_SCOLAIRE_2026-10-16.md` ;
- `docs/reports/RAPPORT_CONCEPTION_DDD_INSCRIPTION_2026-10-16.md` ;
- entites, ports, repositories, migrations, routes, autorisations et tests
  sous `src/` et `tests/`.

Le registre indique que les decisions 1 a 44 sont validees et que la decision
45 est en attente. Les rapports de conception ne sont pas des decisions
metier. Aucun code, registre, migration ou base n'a ete modifie ; aucun test
n'a ete execute ; `edunova.db` n'a pas ete utilisee.

## Reconciliation des huit decisions

### 1. Annee libellee par annees civiles, par exemple `2026-2027`

- **Texte existant :** decision 10 : utiliser les modeles organisationnels
  officiels, distinguer annee scolaire et periodes, et ne pas inventer le
  modele avant verification.
- **Preuves :** `src/academic/domain/entities/academic_period.py:6-30`
  modelise seulement une periode ; `migration_017_academic_catalogues.py:10-24`
  persiste seulement `academic_periods`. Le contrat V1 propose `AcademicYear`
  en `docs/v1/CONTRATS_METIER_V1.md:21-24`, mais le document est marque a
  valider.
- **Statut :** **partiellement couvert**. La distinction est compatible, mais
  le format civil et le modele concret ne sont ni dans le registre ni dans le
  code.
- **DDD :** un aggregate `AcademicYear` ou une entite de configuration doit
  porter libelle, dates, tenant et statut ; `AcademicPeriod` doit rester
  distinct.
- **Tests :** format valide/invalide, bornes de dates, tenant, periode
  contenue dans l'annee et creation d'une annee future non active.

### 2. Une seule annee active par etablissement

- **Texte existant :** la decision 10 ne tranche pas la cardinalite. Le contrat
  V1 demande explicitement : une ou plusieurs annees ouvertes par tenant,
  `docs/v1/CONTRATS_METIER_V1.md:50-55`.
- **Preuves :** aucune table, entite ou repository `AcademicYear` ; aucun index
  d'unicite d'annee active.
- **Statut :** **non verifiable**, avec une question documentaire explicite.
  Ce n'est pas un conflit de code, mais la proposition recente ajoute une
  contrainte non approuvee par le registre.
- **DDD :** l'invariant appartiendrait a `AcademicYear` ou a une policy de
  tenant ; une creation future doit etre differente d'une activation.
- **Tests :** deux annees futures, activation de la premiere, refus de la
  seconde si la regle est approuvee, et creation future sans activation.

### 3. Au plus une affectation active par eleve, etablissement et annee

- **Texte existant :** aucune decision du registre ne fixe cette unicite. La
  decision 13 impose seulement isolation et controle de portee ; la decision
  12 impose l'historique des transferts.
- **Preuves :** `students` ne contient pas d'affectation
  (`src/infrastructure/persistence/database.py:211-222`) ; aucune migration
  001-019 ne cree cette relation ; aucun repository ou use case d'inscription
  n'existe.
- **Statut :** **non verifiable** et a confirmer.
- **DDD :** l'affectation devrait avoir son propre aggregate/repository et une
  contrainte tenant-scoped, probablement une unicite conditionnelle sur le
  statut actif. Ne pas mettre la classe courante dans `students`.
- **Tests :** doublon actif, affectations historiques multiples, isolation
  entre tenants, concurrence et garantie de contrainte en base.

### 4. Transferts historises, fermeture avant activation

- **Texte existant :** decision 12 : les transferts sont configurables, la
  provenance et l'historique sont obligatoires ; decision 17 preserve la
  provenance interetablissement.
- **Preuves :** `migration_019_academic_record_history.py:10-32` historise les
  dossiers academiques, pas les affectations. `StudentAcademicRecord` et
  `CorrectAcademicRecord` concernent les notes, pas les classes.
- **Statut :** **partiellement couvert** : l'obligation generale d'historique
  est validee, mais l'ordre fermeture/activation et l'atomicite ne sont pas
  implementes ni demontres.
- **DDD :** `TransferStudent` doit fermer l'ancienne affectation et creer la
  nouvelle dans une transaction unique, avec auteur, motif, date et provenance.
- **Tests :** succes, echec avant commit, absence de chevauchement actif,
  historique conserve, concurrence et evenement publie seulement apres commit.

### 5. Inscription/transfert pour ADMIN et direction/promoteur habilite

- **Texte existant :** decision 13 rend les permissions configurables par
  etablissement et role, et mentionne la direction ; decision 14 impose un
  contexte actif unique.
- **Preuves :** `src/presentation/api/dependencies/auth.py:131-159` compare
  les roles autorises ; les routes students/classes utilisent
  `require_role("ADMIN")` (`students.py:19-23`, `classes.py:31-35`).
  `Membership.role` est une chaine libre (`src/tenancy/domain/entities/membership.py:5-15`)
  et aucun role `DIRECTION` ou `PROMOTEUR` n'est defini par enum/policy.
- **Statut :** **partiellement couvert**, et **conflit potentiel** avec le
  comportement actuel si la decision recente est consideree comme immediate.
  La direction est mentionnee dans le registre, mais le code ne l'autorise pas
  explicitement.
- **DDD :** definir une policy d'autorisation tenant-scoped, sans accepter un
  role client arbitraire. Le nom exact `DIRECTION`/`PROMOTEUR` doit etre
  arbitre.
- **Tests :** ADMIN autorise, direction/promoteur habilite autorise, enseignant
  refuse, membership inactive refusee, cross-tenant refuse.

### 6. Decision 45 toujours en attente

- **Texte existant :** la section 3 du registre declare la decision 45 EN
  ATTENTE, sans option validee ; les options A, B et C sont des propositions.
- **Preuves :** aucun champ matricule ou mecanisme de deduplication dans
  `StudentSummary`, `students` ou les migrations ; le rapport d'audit confirme
  l'absence de relation d'inscription.
- **Statut :** **compatible et utilisable** : la decision recente conserve
  correctement l'attente.
- **DDD :** l'inscription peut referencer un eleve existant et verifier son
  tenant, mais ne doit pas fusionner, generer un matricule ou rejeter selon un
  critere non valide.
- **Tests :** aucune strategie de doublon ne doit etre presumee ; tester que
  l'API ne cree pas de fusion ou d'identifiant implicite.

### 7. Option obligatoire seulement pour les classes qui proposent des options

- **Texte existant :** aucun texte du registre ne fixe cette regle. La decision
  11 concerne les coefficients selon niveau/option, pas l'obligation de saisir
  une option.
- **Preuves :** `AcademicOption` et `ClassOption` existent ; la migration 005
  impose l'unicite d'une association classe-option. `AssignSubjectToClass`
  accepte une option facultative, mais ce cas d'usage concerne les matieres.
- **Statut :** **partiellement couvert** : le concept de classe proposant une
  option existe, mais la regle d'obligation dans une inscription n'est pas
  codee.
- **DDD :** la validation devrait interroger la configuration de classe et
  refuser une option hors classe ; elle ne doit pas rendre l'option globale-
  ment obligatoire.
- **Tests :** classe sans option accepte sans option, classe avec options
  refuse sans option si la regle est confirmée, option valide acceptee,
  option d'un autre tenant ou d'une autre classe refusee.

### 8. Cycle d'inscription : brouillon puis active

- **Texte existant :** le registre valide des workflows configurables pour les
  resultats (decision 7), mais ne definit pas le cycle d'inscription.
- **Preuves :** `StudentAcademicRecord` ne porte que `DRAFT` et `VALIDATED`
  (`src/academic/domain/entities/student_academic_record.py:8-10`) ; ces
  statuts concernent les dossiers de notes. Aucune affectation ou statut
  `ACTIVE` d'inscription n'existe.
- **Statut :** **non verifiable** et a confirmer. Reutiliser les statuts du
  dossier academique serait une confusion de bounded context.
- **DDD :** le statut appartiendrait a `StudentAssignment`, avec transitions
  explicites, autorisations et conditions d'activation. Le brouillon ne doit
  pas etre compte comme affectation active.
- **Tests :** transitions autorisees, activation incomplete refusee, double
  activation refusee, brouillon invisible aux usages exigeant une affectation
  active, et audit des changements.

## Verdicts synthetiques

### Decisions confirmees et utilisables

- La decision 45 reste en attente et aucune strategie d'identification ou de
  deduplication ne doit etre figee.
- La separation entre annee scolaire et periode est compatible avec la
  decision 10, mais son modele concret reste a valider.
- L'historique et la provenance des transferts sont obligatoires selon la
  decision 12.
- L'isolation tenant et les controles de portee sont obligatoires selon la
  decision 13.

### Conflits explicites ou risques a arbitrer

- La limitation a une seule annee active n'est pas decidee ; le contrat V1
  demande encore de choisir entre une ou plusieurs annees ouvertes.
- L'autorisation direction/promoteur n'est pas refletee par le code actuel,
  qui utilise `ADMIN` pour les routes existantes.
- La fermeture de l'affectation ancienne avant activation de la nouvelle et
  son atomicite ne sont pas garanties par le schema actuel.
- Le cycle `DRAFT -> ACTIVE` n'est pas le cycle du dossier academique et ne
  doit pas reutiliser `DRAFT/VALIDATED`.

### Questions encore ouvertes

- Format exact du libelle et dates de l'annee.
- Nombre d'annees ouvertes et distinction future/active/cloturee.
- Unicite des affectations actives et regle de concurrence.
- Roles exacts et habilitation de la direction/promoteur.
- Dates, motifs, statuts et provenance des transferts.
- Conditions d'une classe proposant des options.
- Conditions de passage de brouillon a active.

## Plus petite tranche implementable sans decision en attente

La tranche la plus sure est une **extension de lecture et de verification
tenant-scoped**, sans persistance d'inscription :

1. verifier l'existence tenant-scoped d'un eleve, d'une classe et d'une
   option ;
2. exposer les donnees de configuration deja existantes ;
3. ajouter les tests cross-tenant et 401/403 ;
4. ne creer ni `AcademicYear`, ni statut d'inscription, ni contrainte
   d'unicite, ni deduplication.

Toute tranche d'ecriture d'inscription attend l'arbitrage des decisions
signalees ci-dessus. Aucun code, migration, dependance ou donnee reelle n'a
ete modifie dans cet audit.
