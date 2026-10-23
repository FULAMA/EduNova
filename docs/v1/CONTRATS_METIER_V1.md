# EduNova V1 - Contrats metier

Statut : proposition a valider avant implementation.
Perimetre : configuration d'etablissement, bulletin PDF et paiements/recus.

## Principes communs

- Chaque aggregate metier porte `tenant_id` ou est resolu dans un contexte tenant authentifie.
- Les routes restent des adaptateurs : elles construisent des DTO et traduisent les erreurs, sans regle metier.
- Les cas d'usage dependent de ports applicatifs ; SQLite reste un adaptateur interchangeable.
- Une operation financiere ou academique publie un evenement seulement apres une transaction reussie.
- Une correction ne supprime pas l'historique : elle cree une nouvelle version ou un evenement compensatoire.
- Aucun montant, token, secret ou donnees personnelles inutiles ne doit etre journalise dans les evenements techniques.

## A. Configuration d'etablissement

### Modele propose

Bounded context `academic` et `tenancy` restent separes. L'etablissement est le profil metier du tenant, pas un second tenant.

- Aggregate root : `SchoolConfiguration` (`tenant_id`, identite, adresse, contacts, devise(s), statut, version).
- Entite : `AcademicYear` (`id`, `tenant_id`, libelle, dates, statut DRAFT/OPEN/CLOSED).
- Entite existante reutilisee : `AcademicPeriod` avec `tenant_id`, dates et nom.
- Entites existantes rattachees par `tenant_id` : `AcademicClass`, `AcademicOption`, `Subject`, `ClassOption`, `ClassSubject`.
- Value objects a introduire apres validation : `SchoolIdentity`, `DateRange`, `CurrencyCode`, `AcademicYearStatus`.

### Invariants minimaux

1. Une configuration et un exercice appartiennent a un seul tenant.
2. Les dates de l'exercice sont ordonnees ; une periode est contenue dans un seul exercice.
3. Les periodes d'un tenant ne se chevauchent pas sans regle explicite d'autorisation.
4. Une classe, option ou matiere ne peut etre liee qu'a des objets du meme tenant.
5. Un exercice `CLOSED` n'accepte plus de modification ordinaire.
6. Une modification administrative est versionnee et autorisee par un role tenant explicite.
7. Les codes fonctionnels sont uniques dans le tenant, jamais globalement par accident.

### Cas d'usage et ports

- `CreateSchoolConfiguration`, `UpdateSchoolConfiguration`.
- `OpenAcademicYear`, `CloseAcademicYear`.
- `CreateAcademicPeriod`, `UpdateAcademicPeriod`.
- Ports : `SchoolConfigurationRepository`, `AcademicYearRepository`, `AcademicPeriodRepository`, `TenantAccessPolicy`, `Clock`.
- Adaptateur initial : SQLite avec contraintes tenant et index d'unicite tenant-scopes.

### Evenements et erreurs

- `SchoolConfigurationUpdated`, `AcademicYearOpened`, `AcademicYearClosed`, `AcademicPeriodCreated`.
- Erreurs : `TenantAccessDenied`, `AcademicYearAlreadyClosed`, `OverlappingAcademicPeriod`, `CrossTenantReference`, `DuplicateFunctionalCode`.

### Decisions requises

- Une seule annee ouverte par tenant ou plusieurs annees ouvertes ?
- Les periodes peuvent-elles se chevaucher pour des calendriers differents ?
- Quels roles peuvent ouvrir/fermer une annee et modifier l'identite ?
- Quelles devises sont acceptees au niveau etablissement : USD, CDF, les deux, ou une devise principale ?

## B. Bulletin PDF

### Source et aggregate

Le bulletin est un document derive, jamais la source de verite des notes. Il lit un `StudentAcademicRecord` valide, ses `SubjectResult`, la `AcademicPeriod`, la politique academique et la `Deliberation`.

- Aggregate root propose : `ReportCard` avec `tenant_id`, `student_id`, `academic_period_id`, `record_version`, `report_version`, statut, hash du contenu, date de generation.
- Value objects : `ReportCardNumber`, `Percentage`, `ReportCardStatus`, `DocumentContent`.
- Port : `ReportCardRepository`, `ReportCardRenderer`, `StudentAcademicRecordReader`, `DeliberationReader`, `SchoolConfigurationReader`.
- Adaptateur initial : rendu PDF injecte ; aucune bibliotheque n'est ajoutee avant decision et autorisation.

### Regles de generation

1. Le dossier doit etre `VALIDATED`.
2. La version du dossier et la periode doivent etre stables pendant la generation.
3. Chaque ligne contient note obtenue, maximum, note normalisee, coefficient et moyenne retenue.
4. Le total et la moyenne suivent `AcademicPolicy`; aucun arrondi implicite hors politique.
5. Le pourcentage est derive de `Score.value / Score.maximum * 100` et conserve sa precision contractuelle.
6. La decision de deliberation est affichee seulement si la deliberation est calculee pour la meme version.
7. Une correction produit un nouveau bulletin ; un ancien bulletin reste consultable et non modifiable.

### Statuts et erreurs

- Statuts proposes : `DRAFT`, `GENERATING`, `ISSUED`, `SUPERSEDED`, `FAILED`.
- Erreurs : `AcademicRecordNotValidated`, `MissingAcademicPeriod`, `MissingSchoolIdentity`, `DeliberationVersionMismatch`, `RendererUnavailable`, `ReportCardAlreadyIssued`.
- Un echec de rendu ne valide ni ne publie le bulletin.

### Decisions requises

- Un bulletin `ISSUED` peut-il etre revoque ou seulement supersede ?
- Le PDF est-il stocke en base, dans un stockage objet, ou regenere a la demande ?
- Quel format numerique officiel doit etre affiche : deux decimales fixes ou politique configurable ?
- La deliberation est-elle obligatoire pour emettre le bulletin ?
- Qui peut emettre, telecharger et annuler un bulletin ?
- Quel identifiant et quelle retention legale sont requis ?

## C. Paiements et recus

### Modele propose

Bounded context `billing`, distinct de `academic` et `identity`.

- Aggregate root `StudentAccount` ou `BillingAccount` (`tenant_id`, `student_id`, statut).
- Entite `Charge` : frais attendus, montant, devise, echeance, statut.
- Entite `Payment` : montant, devise, moyen, reference externe optionnelle, statut, idempotency key.
- Entite `Receipt` : numero, paiement, montant, devise, date, statut, version.
- Value objects : `Money(amount, currency)`, `CurrencyCode` limite a USD/CDF, `ReceiptNumber`, `IdempotencyKey`.

### Invariants financiers

1. USD et CDF sont des devises distinctes ; aucune conversion implicite.
2. Un montant est decimalise avec une precision definie par devise, jamais `float`.
3. Un paiement ne peut etre applique qu'au compte et au tenant correspondants.
4. Le montant alloue ne depasse pas le solde disponible, sauf decision explicite de credit/surpaiement.
5. Un paiement confirme n'est pas supprime ; une correction passe par annulation/contre-ecriture tracee.
6. Un recu est unique dans le tenant et immuable apres emission.
7. Une meme `IdempotencyKey` renvoie le meme resultat pour le meme tenant et la meme operation ; une reutilisation avec un montant different est refusee.
8. Une autorisation metier et une autorisation tenant sont obligatoires avant confirmation ou annulation.

### Cas d'usage et ports

- `CreateCharge`, `RecordPayment`, `ConfirmPayment`, `CancelPayment`, `IssueReceipt`, `GetStudentBalance`.
- Ports : `ChargeRepository`, `PaymentRepository`, `ReceiptRepository`, `PaymentGateway` optionnel, `ReceiptNumberGenerator`, `UnitOfWork`, `Clock`.
- Adaptateur initial recommande : paiement interne enregistre, sans fournisseur externe ; le gateway externe reste une decision separee.

### Evenements et erreurs

- `ChargeCreated`, `PaymentRecorded`, `PaymentConfirmed`, `PaymentCancelled`, `ReceiptIssued`.
- Erreurs : `CurrencyMismatch`, `InsufficientBalance`, `DuplicateIdempotencyKey`, `PaymentAlreadyFinalized`, `ReceiptAlreadyIssued`, `CrossTenantReference`, `PaymentAuthorizationDenied`.

### Decisions requises

- Le paiement est-il une simple saisie interne ou doit-il integrer un fournisseur externe en V1 ?
- Le surpaiement est-il interdit, transforme en credit, ou rembourse ?
- Les frais peuvent-ils etre modifies apres paiement ?
- Format de numerotation du recu, sequence par tenant ou globale, et politique de retention ?
- Qui peut confirmer, annuler et consulter les donnees financieres ?
- Faut-il supporter les paiements partiels et les affectations a plusieurs charges ?

### Décisions financières canoniques

`FIN-ROLE-01` impose une autorisation serveur tenant-scoped pour `ADMIN`, `DIRECTION`, `ACCOUNTANT` et `CASHIER` lorsque ces rôles sont explicitement affectés. `FIN-COR-01` impose une contre-écriture unique et auditée, sans mutation destructive du paiement confirmé. `FIN-REC-01` impose la conservation du reçu consultable et un rendu PDF ; la politique de stockage et de rétention reste à définir.

## Contrats de test communs

- Tests domaine des invariants et des transitions de statut.
- Tests tenant : objet d'un autre tenant toujours invisible ou refuse.
- Tests d'idempotence et de concurrence au niveau repository/unit of work.
- Tests API de traduction des erreurs sans divulguer de secrets ni de details internes.
- Tests d'evenements : evenement apres commit, payload minimal et version correcte.
- Tests de regression des invariants existants de `StudentAcademicRecord` et `AcademicPeriod`.

## Réconciliation canonique des bulletins V1

Les décisions D4 à D7 restent conservées comme historique. Les contrats utilisent les identifiants `BUL-CAL-01`, `BUL-PUB-01`, `BUL-COR-01`, `BUL-CALC-01`, `BUL-DOC-01`, `BUL-PROF-01` et `BUL-SCOPE-01`.

### Prérequis d'émission officielle

1. Dossier académique validé et version identifiée.
2. Délibération persistée, versionnée et liée au dossier.
3. Profil et politique utilisés identifiés.
4. Snapshot immuable et hash calculé.
5. Autorisation tenant-scoped et action auditée.
6. Rendu réussi.
7. Règles réglementaires applicables confirmées pour le niveau.

Les matières, maxima, coefficients, périodes, repêchages, décisions de passage, mentions, rôles détaillés, rétention, stockage du PDF et identifiant légal restent soumis à confirmation humaine.

## Clarifications Tranche 0.1

Les contrats canoniques sont :

- `BUL-PUB-01` : délibération persistée et versionnée obligatoire avant émission officielle ;
- `BUL-DOC-01` : PDF rendu depuis un snapshot immuable ;
- `BUL-COR-01` : remplacement par nouvelle version et statut `SUPERSEDED` pour l'ancienne ;
- `BUL-CALC-01` : politique versionnée et deux décimales comme défaut technique sous réserve réglementaire.

`SUPERSEDED` ne signifie pas révoqué. Une révocation doit disposer d'un contrat séparé avant d'être exposée par une API ou un écran. Le motif, l'autorité, le statut, la visibilité et la rétention de la version révoquée restent à décider.

La Tranche 1 des profils ne peut produire que des contrats de structure et de versionnement. Elle ne peut pas introduire de valeurs officielles pour les matières, maxima, coefficients, périodes, seuils, passages, mentions ou repêchages.
